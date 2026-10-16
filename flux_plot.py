"""Surface-normal flux glyphs, with a shared scale for case playback.

The arrows interpolate segment-averaged flux onto evenly spaced directions.
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


def arrow_display_values(result, representation, length_contrast=1, *, values=None):
    """Optionally emphasize spatial differences without reversing flux signs.

    This changes glyph lengths only. The normal representation is recovered at
    power 1. For positive q and positive mean the mapping is
    mean * (q/mean)**power. It preserves order, uniformity and the flux sign;
    color and numerical charts always use the untransformed physical field.
    """
    if values is None:
        values = displayed_field(result, representation)
    if not 1 <= length_contrast <= 10:
        raise ValueError("Length contrast must lie between 1 and 10.")
    if representation != "net" or length_contrast == 1 or result.metrics["max_deviation_percent"] is None:
        return values
    mean = abs(result.metrics["mean_inner_flux_w_m2"])
    return np.sign(values)*mean*(np.abs(values)/mean)**length_contrast


def arrow_samples(result, representation, arrow_count):
    """Reconstruct display values at fixed directions, including all four axes.

    Interpolation is periodic and bounded by the adjacent segment averages.
    Drawing more arrows does not improve the solver's spatial resolution.
    """
    if arrow_count < 4 or arrow_count % 4:
        raise ValueError("Arrow count must be a positive multiple of four.")
    angles = np.linspace(0, 2*np.pi, arrow_count, endpoint=False)
    centers = result.view_factors.angles[result.view_factors.geometry.n_outer:]
    values = np.interp(angles, centers, displayed_field(result, representation), period=2*np.pi)
    return angles, values


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
    center_x = g.center_x
    cases = [result] if scale_results is None else scale_results
    values = displayed_field(result, representation)
    scale = arrow_length_scale(cases, representation, detail, length_contrast)
    arcs = []
    for i in range(g.n_inner):
        angles = np.linspace(i*2*np.pi/g.n_inner, (i+1)*2*np.pi/g.n_inner, 8)
        arcs.append(np.column_stack([center_x+g.r*np.cos(angles), g.r*np.sin(angles)]))
    fig, ax = plt.subplots(figsize=(9, 6.6 if detail else 7.2), layout="constrained")
    theta = np.linspace(0, 2*np.pi, 361)
    if not detail:
        ax.plot(g.R*np.cos(theta), g.R*np.sin(theta), color="#475569", linewidth=2.5)
        ax.annotate(f"A: outer cylinder, R = {g.R:g} m", (0, g.R),
                    xytext=(0, 1.07*g.R), ha="center", va="bottom", fontsize=11)
    ax.fill(center_x+g.r*np.cos(theta), g.r*np.sin(theta), facecolor="#f8fafc", zorder=1)

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
    collection = LineCollection(arcs, cmap=cmap, norm=norm, linewidths=8, zorder=3)
    collection.set_array(values)
    ax.add_collection(collection)

    angles, sampled_values = arrow_samples(result, representation, arrow_count)
    lengths = arrow_display_values(result, representation, length_contrast, values=sampled_values)
    normals = np.column_stack([np.cos(angles), np.sin(angles)])
    sources = np.array([center_x, 0]) + g.r*normals
    vectors = scale*lengths[:, None]*normals
    arrows = ax.quiver(sources[:, 0], sources[:, 1], vectors[:, 0], vectors[:, 1],
                       angles="xy", scale_units="xy", scale=1, pivot="tail",
                       color="#334155", width=0.009 if detail and arrow_count <= 8 else 0.0045, headwidth=3.8,
                       headlength=4.5, minlength=0, zorder=4)
    maximum = max(float(np.max(np.abs(displayed_field(c, representation)))) for c in cases)
    if representation == "net" and length_contrast != 1:
        ax.text(0.5, 0.98, f"Length contrast {length_contrast:g}: not proportional to q",
                transform=ax.transAxes, ha="center", va="top", fontsize=11,
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
        ax.plot(center_x+radius*np.cos(theta), radius*np.sin(theta), "--",
                color="#64748b", linewidth=1, label="Uniform mean-flux tips", zorder=2)
        ax.legend(loc="lower center", fontsize=9, framealpha=0.9)
    if detail:
        # Cardinal labels stay legible regardless of the number of extra arrows.
        positions = [(0.98, 0.60, "right", "center"), (0.5, 0.89, "center", "top"),
                     (0.02, 0.60, "left", "center"), (0.5, 0.11, "center", "bottom")]
        for index, (x, y, ha, va) in zip(range(0, arrow_count, arrow_count//4), positions):
            value = sampled_values[index]
            if representation == "net":
                deviation = 100*(value-mean)/abs(mean) if result.metrics["max_deviation_percent"] is not None else None
                label = f"q ≈ {value:,.0f} W/m²"
                if deviation is not None:
                    label += f"\n{deviation:+.1f}% from mean"
            else:
                label = f"{value:+.1f}% from mean" if result.metrics["max_deviation_percent"] is not None else "Undefined"
            ax.text(x, y, label, transform=ax.transAxes, ha=ha, va=va, fontsize=12,
                    color="#1e293b", zorder=6,
                    bbox={"facecolor": "white", "edgecolor": "#e2e8f0", "alpha": 0.95, "pad": 5})
    if not detail:
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
    else:
        ax.scatter([center_x], [0], color="#64748b", s=15)
        ax.annotate("B", (center_x, 0), xytext=(3, 9), textcoords="offset points")
    if detail:
        # Common physical extent across frames, with the origin following B.
        extent = 1.5*max(c.view_factors.geometry.r + scale*float(np.max(np.abs(arrow_display_values(c, representation, length_contrast)))) for c in cases)
        ax.set(xlim=(center_x-extent, center_x+extent), ylim=(-extent, extent))
    else:
        ax.set(xlim=(-1.15*g.R, 1.15*g.R), ylim=(-1.15*g.R, 1.15*g.R))
    ax.set_aspect("equal", adjustable="box")
    if detail:
        ax.set_axis_off()
    else:
        ax.set(xlabel="x (m)", ylabel="y (m)")
        ax.grid(alpha=0.15)
    fig.colorbar(collection, ax=ax, shrink=0.75, label=color_label)
    return fig
