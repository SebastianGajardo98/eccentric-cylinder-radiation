"""Surface-normal net-flux arrows on cylinder B for the interactive simulation.

The arrows interpolate segment-averaged flux onto evenly spaced directions.
They are not radiation-ray trajectories. Their lengths are diagram lengths,
not physical transport distances.
"""

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize
import numpy as np


def arrow_samples(result, arrow_count):
    """Interpolate the net flux at fixed directions, including all four axes.

    Interpolation is periodic and bounded by the adjacent segment averages.
    Drawing more arrows does not improve the solver's spatial resolution.
    """
    if arrow_count < 4 or arrow_count % 4:
        raise ValueError("Arrow count must be a positive multiple of four.")
    angles = np.linspace(0, 2*np.pi, arrow_count, endpoint=False)
    centers = result.view_factors.angles[result.view_factors.geometry.n_outer:]
    return angles, np.interp(angles, centers, result.inner_flux, period=2*np.pi)


def arrow_length_scale(result):
    """One linear display scale; outward arrows fit the gap, inward ones fit inside B."""
    g = result.view_factors.geometry
    positive = max(float(result.inner_flux.max()), 0)
    negative = max(float(-result.inner_flux.min()), 0)
    limits = []
    if positive > 1e-10:
        limits.append(0.7*(g.R-g.r-g.d)/positive)
    if negative > 1e-10:
        limits.append(0.55*g.r/negative)
    return min(limits) if limits else 0.0


def geometry_chart(result, arrow_count=8):
    g = result.view_factors.geometry
    center_x = g.center_x
    values = result.inner_flux
    scale = arrow_length_scale(result)
    arcs = []
    for i in range(g.n_inner):
        angles = np.linspace(i*2*np.pi/g.n_inner, (i+1)*2*np.pi/g.n_inner, 8)
        arcs.append(np.column_stack([center_x+g.r*np.cos(angles), g.r*np.sin(angles)]))
    fig, ax = plt.subplots(figsize=(9, 7.2), layout="constrained")
    theta = np.linspace(0, 2*np.pi, 361)
    ax.plot(g.R*np.cos(theta), g.R*np.sin(theta), color="#475569", linewidth=2.5)
    ax.annotate(f"A: outer cylinder, R = {g.R:g} m", (0, g.R),
                xytext=(0, 1.07*g.R), ha="center", va="bottom", fontsize=11)
    ax.fill(center_x+g.r*np.cos(theta), g.r*np.sin(theta), facecolor="#f8fafc", zorder=1)

    lower, upper = float(values.min()), float(values.max())
    # Avoid a spurious rainbow when only floating-point roundoff varies.
    if upper-lower < 1e-8*max(abs(lower), abs(upper), 1):
        padding = 0.01*max(abs(lower), abs(upper), 1)
        center = (lower+upper)/2
        lower, upper = center-padding, center+padding
    collection = LineCollection(arcs, cmap="inferno", norm=Normalize(lower, upper), linewidths=8, zorder=3)
    collection.set_array(values)
    ax.add_collection(collection)

    angles, sampled_values = arrow_samples(result, arrow_count)
    normals = np.column_stack([np.cos(angles), np.sin(angles)])
    sources = np.array([center_x, 0]) + g.r*normals
    vectors = scale*sampled_values[:, None]*normals
    arrows = ax.quiver(sources[:, 0], sources[:, 1], vectors[:, 0], vectors[:, 1],
                       angles="xy", scale_units="xy", scale=1, pivot="tail",
                       color="#334155", width=0.0045, headwidth=3.8,
                       headlength=4.5, minlength=0, zorder=4)
    maximum = float(np.max(np.abs(values)))
    if maximum > 1e-8 and scale > 0:
        target = maximum/2
        decade = 10**np.floor(np.log10(target))
        reference = max(x for x in [decade, 2*decade, 5*decade, 10*decade] if x <= target)
        ax.quiverkey(arrows, X=0.04, Y=0.97, U=reference*scale, label=f"{reference:,.0f} W/m²",
                     labelpos="E", coordinates="axes", fontproperties={"size": 9})

    ax.plot([0, center_x], [0, 0], ":", color="#64748b", linewidth=1)
    ax.scatter([0, center_x], [0, 0], color="#64748b", s=15)
    if g.d > 1e-10:
        ax.annotate("$O_A$", (0, 0), xytext=(-9, -16), textcoords="offset points", fontsize=9)
        ax.annotate("$O_B$", (center_x, 0), xytext=(4, -16), textcoords="offset points", fontsize=9)
    else:
        ax.annotate("$O_A = O_B$", (0, 0), xytext=(4, -16), textcoords="offset points", fontsize=9)
    ax.text(center_x, 0.35*g.r, f"B\nr = {g.r:g} m", ha="center", va="center", fontsize=11)
    ax.text(0.04, 0.08, f"Center distance d = {g.d:.3f} m", transform=ax.transAxes,
            fontsize=10, bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.9, "pad": 3})
    ax.set(xlim=(-1.15*g.R, 1.15*g.R), ylim=(-1.15*g.R, 1.15*g.R))
    ax.text(0.5, 0.02, "Arrow scale fitted to gap; compare q on the fixed-scale chart",
            transform=ax.transAxes, ha="center", va="bottom", fontsize=9,
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.9, "pad": 2})
    ax.set_aspect("equal", adjustable="box")
    ax.set(xlabel="x (m)", ylabel="y (m)")
    ax.grid(alpha=0.15)
    fig.colorbar(collection, ax=ax, shrink=0.75, label="Net outward flux (W/m²)")
    return fig
