"""Surface-normal flux glyphs, with a shared scale for case playback.

The arrows represent segment-averaged net flux or its signed relative deviation.
They are not radiation-ray trajectories. Their lengths are diagram lengths,
not physical transport distances.
"""

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize, TwoSlopeNorm
import numpy as np


def displayed_field(result, representation):
    if representation == "deviation":
        if result.metrics["max_deviation_percent"] is None:
            return np.zeros_like(result.inner_flux)
        mean = result.metrics["mean_inner_flux_w_m2"]
        values = 100 * (result.inner_flux - mean) / abs(mean)
        # Suppress roundoff in genuinely uniform numerical profiles.
        return np.where(np.abs(values) < 1e-8, 0.0, values)
    if representation != "net":
        raise ValueError("Representation must be 'net' or 'deviation'.")
    return result.inner_flux


def arrow_display_values(result, representation, length_contrast=1):
    """Optionally emphasize spatial differences without reversing flux signs.

    This changes glyph lengths only. The normal representation is recovered at
    power 1. For positive q and positive mean the mapping is
    mean * (q/mean)**power. It preserves order, uniformity and the flux sign;
    color and numerical charts always use the untransformed physical field.
    """
    values = displayed_field(result, representation)
    if not 1 <= length_contrast <= 10:
        raise ValueError("Length contrast must lie between 1 and 10.")
    if representation != "net" or length_contrast == 1 or result.metrics["max_deviation_percent"] is None:
        return values
    mean = abs(result.metrics["mean_inner_flux_w_m2"])
    return np.sign(values)*mean*(np.abs(values)/mean)**length_contrast


def arrow_length_scale(results, representation, detail, length_contrast=1):
    """One linear display scale; no individual arrows are clipped/rescaled.

    Fit every case so a shared scale can be used throughout playback. A global
    minimum-gap bound keeps enclosure glyphs within the outer wall. In detail
    view the absent outer wall does not limit the glyphs.
    """
    limits = []
    for result in results:
        g = result.view_factors.geometry
        values = arrow_display_values(result, representation, length_contrast)
        positive = max(float(values.max()), 0)
        negative = max(float(-values.min()), 0)
        if positive > 1e-10:
            space = 0.65*g.r if detail else 0.7*(g.R-g.r-g.d)
            limits.append(space/positive)
        if negative > 1e-10:
            limits.append(0.55*g.r/negative)
    return min(limits) if limits else 0.0


def geometry_chart(result, color_domain=None, *, representation="net", detail=False,
                   arrow_count=16, uniform_reference=True, scale_results=None,
                   length_contrast=1):
    g = result.view_factors.geometry
    cases = [result] if scale_results is None else scale_results
    values = displayed_field(result, representation)
    lengths = arrow_display_values(result, representation, length_contrast)
    scale = arrow_length_scale(cases, representation, detail, length_contrast)
    arcs = []
    for i in range(g.n_inner):
        angles = np.linspace(i*2*np.pi/g.n_inner, (i+1)*2*np.pi/g.n_inner, 8)
        arcs.append(np.column_stack([g.d+g.r*np.cos(angles), g.r*np.sin(angles)]))
    fig, ax = plt.subplots(figsize=(6.2, 5.6), layout="constrained")
    theta = np.linspace(0, 2*np.pi, 361)
    if not detail:
        ax.plot(g.R*np.cos(theta), g.R*np.sin(theta), color="#64748b", linewidth=1.5)

    if representation == "deviation":
        limit = max(max(float(np.max(np.abs(displayed_field(c, representation)))) for c in cases), 1e-3)
        norm = TwoSlopeNorm(vmin=-limit, vcenter=0, vmax=limit)
        cmap, color_label = "coolwarm", "Deviation from mean (%)"
    else:
        lower, upper = (float(values.min()), float(values.max())) if color_domain is None else color_domain
        # Avoid a spurious rainbow when only floating-point roundoff varies.
        if upper-lower < 1e-8*max(abs(lower), abs(upper), 1):
            padding = 0.01*max(abs(lower), abs(upper), 1)
            center = (lower+upper)/2
            lower, upper = center-padding, center+padding
        norm, cmap, color_label = Normalize(lower, upper), "inferno", "Net outward flux (W/m²)"
    collection = LineCollection(arcs, cmap=cmap, norm=norm, linewidths=6, zorder=3)
    collection.set_array(values)
    ax.add_collection(collection)

    indices = np.floor(np.linspace(0, g.n_inner, min(arrow_count, g.n_inner), endpoint=False)).astype(int)
    angles = result.view_factors.angles[g.n_outer:][indices]
    normals = np.column_stack([np.cos(angles), np.sin(angles)])
    sources = np.array([g.d, 0]) + g.r*normals
    vectors = scale*lengths[indices, None]*normals
    arrows = ax.quiver(sources[:, 0], sources[:, 1], vectors[:, 0], vectors[:, 1],
                       angles="xy", scale_units="xy", scale=1, pivot="tail",
                       color="#334155", width=0.005, headwidth=3.8,
                       headlength=4.5, minlength=0, zorder=4)
    maximum = max(float(np.max(np.abs(displayed_field(c, representation)))) for c in cases)
    if representation == "net" and length_contrast != 1:
        ax.text(0.5, 0.98, f"Length contrast {length_contrast:g}: not proportional to q",
                transform=ax.transAxes, ha="center", va="top", fontsize=9,
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.9, "pad": 2})
    elif maximum > 1e-8 and scale > 0:
        target = maximum/2
        decade = 10**np.floor(np.log10(target))
        reference = max(x for x in [decade, 2*decade, 5*decade, 10*decade] if x <= target)
        label = f"{reference:g}% of mean" if representation == "deviation" else f"{reference:,.0f} W/m²"
        ax.quiverkey(arrows, X=0.04, Y=0.97, U=reference*scale, label=label,
                     labelpos="E", coordinates="axes", fontproperties={"size": 9})
    elif representation == "deviation":
        message = "Relative deviation undefined at zero mean flux" if result.metrics["max_deviation_percent"] is None else "Uniform flux: deviation arrows are zero"
        ax.text(0.5, 0.98, message, transform=ax.transAxes,
                ha="center", va="top", fontsize=9)

    mean = result.metrics["mean_inner_flux_w_m2"]
    if representation == "net" and uniform_reference and scale > 0:
        radius = g.r+scale*mean
        ax.plot(g.d+radius*np.cos(theta), radius*np.sin(theta), "--",
                color="#64748b", linewidth=1, label="Uniform mean-flux tips", zorder=2)
        ax.legend(loc="lower center", fontsize=8, framealpha=0.9)
    if representation == "net":
        ax.text(0.035, 0.075,
                f"q_min = {result.inner_flux.min():,.1f} W/m²\nq_max = {result.inner_flux.max():,.1f} W/m²",
                transform=ax.transAxes, ha="left", va="bottom", fontsize=8,
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.85, "pad": 2})
    if not detail:
        ax.plot([0, g.d], [0, 0], ":", color="#64748b", linewidth=1)
        ax.scatter([0], [0], color="#64748b", s=15)
        ax.annotate("A", (0, 0), xytext=(-12, 9), textcoords="offset points")
    ax.scatter([g.d], [0], color="#64748b", s=15)
    ax.annotate("B", (g.d, 0), xytext=(3, 9), textcoords="offset points")
    if detail:
        # Common physical extent across frames, with the origin following B.
        extent = 1.15*max(c.view_factors.geometry.r + scale*float(np.max(np.abs(arrow_display_values(c, representation, length_contrast)))) for c in cases)
        ax.set(xlim=(g.d-extent, g.d+extent), ylim=(-extent, extent))
    else:
        ax.set(xlim=(-1.12*g.R, 1.12*g.R), ylim=(-1.12*g.R, 1.12*g.R))
    ax.set(xlabel="x (m)", ylabel="y (m)")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(alpha=0.15)
    fig.colorbar(collection, ax=ax, shrink=0.75, label=color_label)
    return fig
