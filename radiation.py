"""Radiation between circular, infinitely long cylinders; SI units throughout.

Rows of F correspond to emitting segments; columns to receiving segments.
Outer segments precede inner segments. Arc-averaged radiosity is piecewise
constant. Receiver angular integration is exact at each source point, while
source arc integration uses adaptive quadrature. No row normalization is used.
"""

from dataclasses import dataclass
from numbers import Integral

import numpy as np
from scipy.integrate import quad_vec

SIGMA = 5.670374419e-8
TAU = 2 * np.pi


@dataclass(frozen=True)
class Geometry:
    r: float = 0.4
    d: float = 0.3
    n_outer: int = 48
    n_inner: int = 32
    R: float = 1.0
    side: str = "right"

    def __post_init__(self):
        if not np.all(np.isfinite([self.R, self.r, self.d])):
            raise ValueError("R, r and d must be finite.")
        if not (0 < self.r < self.R and 0 <= self.d < self.R - self.r):
            raise ValueError("Require 0 < r < R and 0 <= d < R - r.")
        if self.side not in ("left", "right"):
            raise ValueError("Side must be 'left' or 'right'.")
        for count in (self.n_outer, self.n_inner):
            if isinstance(count, bool) or not isinstance(count, Integral) or count < 4:
                raise ValueError("Each segment count must be an integer >= 4.")

    @property
    def center_x(self):
        """Signed horizontal position; d remains the nonnegative center distance."""
        return -self.d if self.side == "left" else self.d


@dataclass
class ViewFactors:
    geometry: Geometry
    factors: np.ndarray
    areas: np.ndarray  # m^2 per m of cylinder length, numerically arc lengths
    angles: np.ndarray  # segment midpoint angles in radians
    integration_tolerance: float
    estimated_integration_error: float

    @property
    def diagnostics(self):
        exchange = self.areas[:, None] * self.factors
        return {
            "closure_max": float(np.max(np.abs(self.factors.sum(axis=1) - 1))),
            "reciprocity_max_m": float(np.max(np.abs(exchange - exchange.T))),
            "reciprocity_relative_max": float(
                np.max(np.abs(exchange - exchange.T)) / np.max(self.areas)
            ),
            "minimum_factor": float(self.factors.min()),
            "source_integration_error_estimate": self.estimated_integration_error,
        }


def _wrap(angle):
    return (angle + np.pi) % TAU - np.pi


def calculate_view_factors(geometry: Geometry, integration_tolerance=1e-8) -> ViewFactors:
    """Calculate arc-to-arc factors including exact circular obstruction.

    The tolerance controls adaptive integration over source arcs, independently
    of the two surface segment counts. Accuracy estimates are not rigorous bounds
    on every matrix entry; reciprocity is an independent numerical diagnostic.
    """
    if not np.isfinite(integration_tolerance) or not 0 < integration_tolerance < 1:
        raise ValueError("Integration tolerance must lie between 0 and 1.")
    g = geometry
    edges_a = TAU * np.arange(g.n_outer) / g.n_outer
    edges_b = TAU * np.arange(g.n_inner) / g.n_inner
    endpoints = np.vstack([
        g.R * np.column_stack([np.cos(edges_a), np.sin(edges_a)]),
        np.array([g.center_x, 0]) + g.r * np.column_stack([np.cos(edges_b), np.sin(edges_b)]),
    ])
    total = g.n_outer + g.n_inner
    center_b = np.array([g.center_x, 0.0])

    def point_factors(theta, outer):
        radial = np.array([np.cos(theta), np.sin(theta)])
        p = g.R * radial if outer else center_b + g.r * radial
        normal = -radial if outer else radial
        bearing = np.arctan2(normal[1], normal[0])
        vectors = endpoints - p
        # Endpoint bearings delimit every possible change in receiving segment.
        angles = _wrap(np.arctan2(vectors[:, 1], vectors[:, 0]) - bearing)
        cuts = [-np.pi / 2, np.pi / 2]
        cuts.extend(angles[(angles > -np.pi / 2) & (angles < np.pi / 2)])
        if outer:
            v = center_b - p
            alpha = np.arctan2(v[1], v[0])
            beta = np.arcsin(np.clip(g.r / np.linalg.norm(v), 0, 1))
            tangents = _wrap(np.array([alpha - beta, alpha + beta]) - bearing)
            cuts.extend(tangents[(tangents > -np.pi / 2) & (tangents < np.pi / 2)])
        cuts = np.unique(cuts)
        phi = (cuts[:-1] + cuts[1:]) / 2
        directions = np.column_stack([np.cos(phi + bearing), np.sin(phi + bearing)])
        weights = (np.sin(cuts[1:]) - np.sin(cuts[:-1])) / 2
        # First positive intersection identifies the receiver. On A, the
        # nonzero outer-circle root is -2 p.v; on B use the positive exit root.
        dot_a = directions @ p
        if outer:
            distance_a = -2 * dot_a
        else:
            distance_a = -dot_a + np.sqrt(np.maximum(
                dot_a**2 + g.R**2 - p @ p, 0
            ))
        hits_b = np.zeros(len(phi), dtype=bool)
        distances = distance_a.copy()
        if outer:
            relative = p - center_b
            dot_b = directions @ relative
            discriminant = dot_b**2 - (relative @ relative - g.r**2)
            root_b = -dot_b - np.sqrt(np.maximum(discriminant, 0))
            hits_b = (discriminant > 0) & (root_b > 0) & (root_b < distance_a)
            distances[hits_b] = root_b[hits_b]
        hits = p + distances[:, None] * directions
        hit_angles = np.arctan2(hits[:, 1], hits[:, 0]) % TAU
        indices = np.floor(hit_angles / TAU * g.n_outer).astype(int)
        if np.any(hits_b):
            hits_relative = hits[hits_b] - center_b
            theta_b = np.arctan2(hits_relative[:, 1], hits_relative[:, 0]) % TAU
            indices[hits_b] = g.n_outer + np.floor(theta_b / TAU * g.n_inner).astype(int)
        return np.bincount(indices, weights=weights, minlength=total)

    factors = np.empty((total, total))
    errors = []
    angles = []
    areas = []
    for outer, count, radius, offset in (
        (True, g.n_outer, g.R, 0), (False, g.n_inner, g.r, g.n_outer)
    ):
        width = TAU / count
        for i in range(count):
            lower = i * width
            integral, error, info = quad_vec(
                lambda theta: point_factors(theta, outer), lower, lower + width,
                epsabs=integration_tolerance * width,
                epsrel=integration_tolerance, norm="max", limit=1000,
                full_output=True,
            )
            if not info.success:
                raise RuntimeError("Source-arc integration failed; relax tolerance or refine segments.")
            factors[offset + i] = integral / width
            errors.append(error / width)
            angles.append(lower + width / 2)
            areas.append(radius * width)
    return ViewFactors(g, factors, np.array(areas), np.array(angles),
                       integration_tolerance, float(max(errors)))


@dataclass
class RadiationResult:
    view_factors: ViewFactors
    radiosity: np.ndarray
    irradiation: np.ndarray
    flux: np.ndarray  # W/m^2, positive from surface into the vacuum

    @property
    def inner_flux(self):
        return self.flux[self.view_factors.geometry.n_outer:]

    @property
    def metrics(self):
        model = self.view_factors
        n = model.geometry.n_outer
        mean = float(np.average(self.inner_flux, weights=model.areas[n:]))
        heat_b = float(model.areas[n:] @ self.inner_flux)
        heat_a = float(model.areas[:n] @ self.flux[:n])
        # Relative nonuniformity is undefined when the net flux is effectively
        # zero compared with the absolute radiation field.
        zero_flux = abs(mean) <= 1e-10 * max(float(np.max(np.abs(self.radiosity))), 1)
        delta = self.inner_flux - mean
        return {
            "mean_inner_flux_w_m2": mean,
            "min_inner_flux_w_m2": float(self.inner_flux.min()),
            "max_inner_flux_w_m2": float(self.inner_flux.max()),
            "max_deviation_percent": None if zero_flux else float(100 * np.max(np.abs(delta)) / abs(mean)),
            "peak_to_peak_percent": None if zero_flux else float(100 * np.ptp(self.inner_flux) / abs(mean)),
            "heat_inner_w_m": heat_b,
            "heat_outer_w_m": heat_a,
            "energy_imbalance_w_m": heat_a + heat_b,
            "energy_imbalance_relative": None if zero_flux else abs(heat_a + heat_b) / max(abs(heat_a), abs(heat_b)),
        }


def solve_radiation(view_factors: ViewFactors, temperature_outer_k=303.15,
                    temperature_inner_k=473.15, emissivity_outer=0.6,
                    emissivity_inner=0.8) -> RadiationResult:
    """Solve diffuse-gray radiosity with uniform temperature/emissivity per body.

    Temperatures are in kelvin. Equal and reversed temperatures are accepted for
    verification, although the assignment uses a hotter inner cylinder.
    """
    temperatures = [temperature_outer_k, temperature_inner_k]
    emissivities = [emissivity_outer, emissivity_inner]
    if not np.all(np.isfinite(temperatures)) or min(temperatures) <= 0:
        raise ValueError("Temperatures must be finite and positive in kelvin.")
    if not np.all(np.isfinite(emissivities)) or not all(0 < e <= 1 for e in emissivities):
        raise ValueError("Emissivities must satisfy 0 < epsilon <= 1.")
    g = view_factors.geometry
    eps = np.repeat(emissivities, [g.n_outer, g.n_inner])
    temp = np.repeat(temperatures, [g.n_outer, g.n_inner])
    factors = view_factors.factors
    matrix = np.eye(len(eps)) - (1 - eps[:, None]) * factors
    radiosity = np.linalg.solve(matrix, eps * SIGMA * temp**4)
    irradiation = factors @ radiosity
    return RadiationResult(view_factors, radiosity, irradiation, radiosity - irradiation)
