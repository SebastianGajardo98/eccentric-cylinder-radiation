"""Charts use recorded segment averages; display interpolation is identified."""

import altair as alt


def angular_chart(frame, quantity="deviation_percent", group=None, order=None):
    title = "Deviation from own mean (%)" if quantity == "deviation_percent" else "Net outward flux (W/m²)"
    chart = alt.Chart(frame).mark_line().encode(
        x=alt.X("angle_deg:Q", title="Angle on B (degrees)", scale=alt.Scale(domain=[0, 360])),
        y=alt.Y(f"{quantity}:Q", title=title, scale=alt.Scale(zero=False)),
        tooltip=[alt.Tooltip("angle_deg:Q", title="Angle (°)", format=".2f"),
                 alt.Tooltip(f"{quantity}:Q", title=title, format=".5f")],
    )
    if group:
        if group == "mesh":
            mesh_order = frame[group].drop_duplicates().tolist()
            legend = alt.Legend(orient="bottom", direction="horizontal")
            chart = chart.encode(
                color=alt.Color(f"{group}:N", title="Segments A/B", sort=mesh_order,
                                scale=alt.Scale(domain=mesh_order, scheme="tableau10"), legend=legend),
                strokeDash=alt.StrokeDash(f"{group}:N", title="Segments A/B", sort=mesh_order,
                    scale=alt.Scale(domain=mesh_order, range=[[1, 0], [8, 4], [2, 3], [8, 3, 2, 3]]), legend=legend),
                tooltip=[alt.Tooltip(f"{group}:N", title="Segments A/B"),
                         alt.Tooltip("angle_deg:Q", title="Angle (°)", format=".2f"),
                         alt.Tooltip(f"{quantity}:Q", title=title, format=".5f")],
            )
        else:
            chart = chart.encode(color=alt.Color(f"{group}:N", title="Case", sort=order))
    return chart.properties(height=320)


def trend_chart(frame, x, xlabel, y, ylabel):
    return alt.Chart(frame).mark_line(point=True).encode(
        x=alt.X(f"{x}:Q", title=xlabel, scale=alt.Scale(zero=False)),
        y=alt.Y(f"{y}:Q", title=ylabel, scale=alt.Scale(zero=True)),
        tooltip=[alt.Tooltip(f"{x}:Q", title=xlabel, format=".4g"),
                 alt.Tooltip(f"{y}:Q", title=ylabel, format=".6f")],
    ).properties(height=280)
