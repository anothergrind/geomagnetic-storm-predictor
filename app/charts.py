"""Altair chart builders.

Every builder takes the active mode's tokens and returns a finished chart, so a
chart can never be rendered with the wrong palette for the surface it lands on.
Charts are drawn on a transparent background and inherit the fill of whatever
card they sit in.

House rules, applied everywhere: one y-axis per chart (never two scales), 2px
lines, >=8px markers, rounded bar ends anchored to the baseline, recessive
grid and axis ink, a legend whenever there are two or more series, and a hover
layer on every chart.
"""
from __future__ import annotations

import altair as alt
import numpy as np
import pandas as pd

from app.theme import BODY_FONT, STATUS

_LINE_WIDTH = 2
_POINT_SIZE = 90


def _finish(chart: alt.Chart, t: dict, height: int) -> alt.Chart:
    """Shared chrome: typography, recessive axes, transparent surface."""
    return (
        chart.properties(height=height, width="container")
        .configure_view(stroke=None, fill=None)
        .configure(background="transparent", font=BODY_FONT)
        .configure_axis(
            labelColor=t["ink_muted"],
            titleColor=t["ink_secondary"],
            labelFontSize=11,
            titleFontSize=11,
            titleFontWeight=500,
            titlePadding=12,
            labelPadding=6,
            gridColor=t["grid"],
            gridWidth=1,
            domainColor=t["grid"],
            tickColor=t["grid"],
            tickSize=4,
        )
        .configure_legend(
            labelColor=t["ink_secondary"],
            titleColor=t["ink_muted"],
            labelFontSize=11,
            titleFontSize=10,
            symbolStrokeWidth=3,
            symbolSize=110,
            orient="top",
            direction="horizontal",
            offset=6,
            padding=0,
        )
        .configure_text(font=BODY_FONT)
    )


def _series_scale(t: dict, names: list[str]) -> alt.Scale:
    """Colour follows the model, never its rank — the domain is fixed."""
    return alt.Scale(domain=list(names), range=list(t["series"][: len(names)]))


# --------------------------------------------------------------- Ap timeline --
def ap_timeline(series: pd.DataFrame, t: dict, threshold: float, height: int = 320) -> alt.Chart:
    """Ap over time: the peak envelope shaded behind the typical level.

    Thirty years of daily values is 11,000 points in 900 pixels — a solid block
    of ink that hides the very spikes it is meant to show. Plotting the period
    maximum as an area with the mean as a line keeps both the storms and the
    baseline legible at any zoom, and both are the same measure on one axis.

    `series` needs columns: datetime, ap_max, ap_mean, storms, period.
    """
    ramp = t["sequential"]
    # Steps far apart in the ramp, so the band and the line stay distinguishable
    # for a reader who cannot separate two neighbouring blues.
    envelope, mean_line = (ramp[2], ramp[6]) if t["mode"] == "dark" else (ramp[1], ramp[5])

    base = alt.Chart(series)
    hover = alt.selection_point(
        fields=["datetime"], nearest=True, on="pointermove", empty=False, clear="pointerout"
    )
    x = alt.X("datetime:T", title=None, axis=alt.Axis(format="%Y", tickCount=8))

    # Both layers encode a constant series name so Vega-Lite builds one shared
    # legend — identity is never left to colour alone.
    series_scale = alt.Scale(
        domain=["Peak in period", "Typical level"], range=[envelope, mean_line]
    )
    area = base.transform_calculate(
        series='"Peak in period"'
    ).mark_area(opacity=0.45, interpolate="monotone").encode(
        x=x,
        y=alt.Y("ap_max:Q", title="Ap index", scale=alt.Scale(nice=True)),
        color=alt.Color("series:N", scale=series_scale, title=None),
    )
    line = base.transform_calculate(
        series='"Typical level"'
    ).mark_line(strokeWidth=_LINE_WIDTH, interpolate="monotone").encode(
        x=x,
        y="ap_mean:Q",
        color=alt.Color("series:N", scale=series_scale, title=None),
    )

    rule_thr = alt.Chart(pd.DataFrame({"y": [threshold]})).mark_rule(
        color=STATUS["critical"], strokeDash=[5, 4], strokeWidth=1.5, opacity=0.9
    ).encode(y="y:Q")

    label_thr = alt.Chart(
        pd.DataFrame({"y": [threshold], "label": [f"Storm threshold · Ap {threshold:.0f}"]})
    ).mark_text(
        align="left", baseline="bottom", dx=6, dy=-6, fontSize=10.5, fontWeight=600,
        color=STATUS["critical"],
    ).encode(y="y:Q", text="label:N", x=alt.value(4))

    crosshair = base.mark_rule(color=t["ink_muted"], strokeWidth=1).encode(
        x="datetime:T",
        opacity=alt.condition(hover, alt.value(0.7), alt.value(0)),
        tooltip=[
            alt.Tooltip("period:N", title="Period"),
            alt.Tooltip("ap_max:Q", title="Peak Ap", format=".0f"),
            alt.Tooltip("ap_mean:Q", title="Typical Ap", format=".1f"),
            alt.Tooltip("storms:Q", title="Storm bins", format="d"),
        ],
    ).add_params(hover)

    dot = base.mark_point(
        size=_POINT_SIZE, filled=True, color=mean_line,
        stroke=t["surface"], strokeWidth=2,
    ).encode(
        x="datetime:T", y="ap_mean:Q",
        opacity=alt.condition(hover, alt.value(1), alt.value(0)),
    )

    layered = alt.layer(area, line, rule_thr, label_thr, crosshair, dot).add_params(
        alt.selection_interval(bind="scales", encodings=["x"])
    )
    return _finish(layered, t, height)


# --------------------------------------------------------- storms per year --
def storms_per_year(yearly: pd.DataFrame, t: dict, height: int = 260) -> alt.Chart:
    """Storm bins per calendar year. `yearly` needs columns: year, storms."""
    peaks = {2003, 2015, 2024}
    data = yearly.assign(peak=yearly["year"].isin(peaks))
    bar_color = t["sequential"][4]

    # One colour for every bar: the solar maxima are called out with dated
    # labels, so shading them a second blue would encode the same fact twice —
    # and two steps of one sequential ramp is not a categorical distinction.
    bars = alt.Chart(data).mark_bar(
        cornerRadiusTopLeft=4, cornerRadiusTopRight=4, color=bar_color,
    ).encode(
        x=alt.X(
            "year:O", title=None,
            scale=alt.Scale(paddingInner=0.28),
            axis=alt.Axis(labelAngle=0, values=list(range(1995, 2025, 5))),
        ),
        y=alt.Y("storms:Q", title="Storm bins", scale=alt.Scale(nice=True)),
        tooltip=[
            alt.Tooltip("year:O", title="Year"),
            alt.Tooltip("storms:Q", title="Storm bins", format="d"),
        ],
    )

    labels = alt.Chart(data[data["peak"]]).mark_text(
        dy=-9, fontSize=10.5, fontWeight=600, color=t["ink_secondary"],
    ).encode(x=alt.X("year:O", scale=alt.Scale(paddingInner=0.28)), y="storms:Q", text="year:O")

    return _finish(alt.layer(bars, labels), t, height)


# ------------------------------------------------------- confusion matrix --
def confusion_matrix(cm: np.ndarray, t: dict, height: int = 210) -> alt.Chart:
    """2x2 outcome grid on the sequential ramp.

    The ramp runs light->dark on the light surface and dark->light on the dark
    one, so the cell that needs inverted ink is the opposite end in each mode.
    """
    labels = ["No storm", "Storm"]
    rows = [
        {
            "actual": labels[i],
            "predicted": labels[j],
            "count": int(cm[i, j]),
            "share": float(cm[i, j] / cm.max()),
            "outcome": _outcome_name(i, j),
        }
        for i in range(2)
        for j in range(2)
    ]
    data = pd.DataFrame(rows)

    cells = alt.Chart(data).mark_rect(cornerRadius=4, stroke=t["surface"], strokeWidth=2).encode(
        x=alt.X("predicted:N", title="Predicted", sort=labels, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("actual:N", title="Actual", sort=labels),
        color=alt.Color(
            "share:Q",
            scale=alt.Scale(range=t["sequential"], domain=[0, 1]),
            legend=None,
        ),
        tooltip=[
            alt.Tooltip("outcome:N", title="Outcome"),
            alt.Tooltip("count:Q", title="Bins", format=","),
        ],
    )

    if t["mode"] == "dark":
        # High share = pale cell, so its ink must go dark.
        heavy_ink, light_ink = "#0b0b0b", t["ink"]
    else:
        # High share = deep blue cell, so its ink must go white.
        heavy_ink, light_ink = "#ffffff", t["ink"]

    text = alt.Chart(data).mark_text(fontSize=13, fontWeight=600).encode(
        x=alt.X("predicted:N", sort=labels),
        y=alt.Y("actual:N", sort=labels),
        text=alt.Text("count:Q", format=","),
        color=alt.condition(
            alt.datum.share > 0.55, alt.value(heavy_ink), alt.value(light_ink)
        ),
    )

    return _finish(alt.layer(cells, text), t, height)


def _outcome_name(actual: int, predicted: int) -> str:
    return {
        (0, 0): "Correct quiet call",
        (0, 1): "False alarm",
        (1, 0): "Missed storm",
        (1, 1): "Caught storm",
    }[(actual, predicted)]


# ----------------------------------------------------- precision–recall --
def pr_curves(curves: pd.DataFrame, points: pd.DataFrame, t: dict, height: int = 320) -> alt.Chart:
    """Overlaid PR curves. `curves`: model, recall, precision. `points`: model,
    recall, precision, kind ("tuned" | "selected")."""
    names = list(dict.fromkeys(curves["model"]))
    scale = _series_scale(t, names)

    lines = alt.Chart(curves).mark_line(strokeWidth=_LINE_WIDTH).encode(
        x=alt.X("recall:Q", title="Recall", scale=alt.Scale(domain=[0, 1])),
        y=alt.Y("precision:Q", title="Precision", scale=alt.Scale(domain=[0, 1.02])),
        color=alt.Color("model:N", scale=scale, title=None),
    )

    # Note: none of these layers may set legend=None. Vega-Lite resolves the
    # colour scale across layers, and a single null legend suppresses the shared
    # one — which would leave three series identified by colour alone.
    marker_tooltip = [
        alt.Tooltip("model:N", title="Model"),
        alt.Tooltip("label:N", title="Point"),
        alt.Tooltip("recall:Q", title="Recall", format=".2f"),
        alt.Tooltip("precision:Q", title="Precision", format=".2f"),
    ]

    # A ring rather than a filled shape: at the default slider position the tuned
    # and selected points sit on top of each other, and a ring around the dot
    # still reads as two things.
    tuned = alt.Chart(points[points["kind"] == "tuned"]).mark_point(
        size=300, filled=False, strokeWidth=2,
    ).encode(
        x="recall:Q", y="precision:Q",
        color=alt.Color("model:N", scale=scale, title=None),
        tooltip=marker_tooltip,
    )

    selected = alt.Chart(points[points["kind"] == "selected"]).mark_point(
        size=130, filled=True, stroke=t["surface"], strokeWidth=2,
    ).encode(
        x="recall:Q", y="precision:Q",
        color=alt.Color("model:N", scale=scale, title=None),
        tooltip=marker_tooltip,
    )

    return _finish(alt.layer(lines, tuned, selected), t, height)


# ------------------------------------------------------ forecast timeline --
def forecast_timeline(
    view: pd.DataFrame, t: dict, threshold: float, series_color: str, height: int = 300
) -> alt.Chart:
    """Predicted storm probability through a window, with real storms marked.

    `view` needs columns: datetime, storm_probability, is_storm, ap_now.
    """
    fill = alt.Gradient(
        gradient="linear",
        stops=[
            alt.GradientStop(color=series_color, offset=1),
            alt.GradientStop(color=series_color + "00", offset=0),
        ],
        x1=1, x2=1, y1=1, y2=0,
    )

    base = alt.Chart(view)
    hover = alt.selection_point(
        fields=["datetime"], nearest=True, on="pointermove", empty=False, clear="pointerout"
    )

    storms = view[view["is_storm"]]
    storm_rules = alt.Chart(storms).mark_rule(
        color=STATUS["critical"], strokeWidth=2, opacity=0.34,
    ).encode(x="datetime:T")

    area = base.mark_area(
        line={"color": series_color, "strokeWidth": _LINE_WIDTH},
        color=fill,
        interpolate="monotone",
    ).encode(
        x=alt.X(
            "datetime:T", title=None,
            axis=alt.Axis(format="%d %b", labelOverlap="greedy", tickCount=8),
        ),
        y=alt.Y(
            "storm_probability:Q",
            title="Predicted P(storm)",
            scale=alt.Scale(domain=[0, 1]),
            axis=alt.Axis(format=".1f"),
        ),
    )

    thr_rule = alt.Chart(pd.DataFrame({"y": [threshold]})).mark_rule(
        color=t["ink_muted"], strokeDash=[5, 4], strokeWidth=1.5,
    ).encode(y="y:Q")

    thr_label = alt.Chart(
        pd.DataFrame({"y": [threshold], "label": [f"Decision threshold {threshold:.2f}"]})
    ).mark_text(
        align="left", baseline="bottom", dy=-4, fontSize=10.5, color=t["ink_muted"],
    ).encode(y="y:Q", text="label:N", x=alt.value(6))

    crosshair = base.mark_rule(color=t["ink_muted"], strokeWidth=1).encode(
        x="datetime:T",
        opacity=alt.condition(hover, alt.value(0.7), alt.value(0)),
        tooltip=[
            alt.Tooltip("datetime:T", title="Bin", format="%d %b %Y %H:%M"),
            alt.Tooltip("storm_probability:Q", title="P(storm)", format=".2f"),
            alt.Tooltip("ap_now:Q", title="Ap (now)", format=".0f"),
            alt.Tooltip("outcome:N", title="Actual"),
        ],
    ).add_params(hover)

    dot = base.mark_point(
        size=_POINT_SIZE, filled=True, color=series_color,
        stroke=t["surface"], strokeWidth=2,
    ).encode(
        x="datetime:T", y="storm_probability:Q",
        opacity=alt.condition(hover, alt.value(1), alt.value(0)),
    )

    layered = alt.layer(storm_rules, area, thr_rule, thr_label, crosshair, dot).add_params(
        alt.selection_interval(bind="scales", encodings=["x"])
    )
    return _finish(layered, t, height)


# ------------------------------------------------------ event conditions --
def event_conditions(event: pd.DataFrame, t: dict, height: int = 220) -> alt.Chart:
    """Ap through a storm event, with each model's probability alongside.

    Two measures share one 0-1 axis by plotting Ap as a share of the event peak,
    which keeps this to a single y-scale rather than a dual axis.
    """
    long = event.melt(
        id_vars=["datetime"],
        value_vars=["proba_XGBoost", "proba_LSTM", "proba_TCN"],
        var_name="model",
        value_name="probability",
    )
    long["model"] = long["model"].str.replace("proba_", "", regex=False)
    names = ["XGBoost", "LSTM", "TCN"]

    # The observed-Ap band joins the same colour scale in neutral grey, so it
    # gets a legend entry without pretending to be a fourth model.
    band_label = "Observed Ap (share of peak)"
    scale = alt.Scale(
        domain=[*names, band_label],
        range=[*t["series"][:3], t["ink_muted"]],
    )
    x = alt.X(
        "datetime:T", title=None,
        axis=alt.Axis(format="%d %b %H:%M", labelOverlap="greedy", tickCount=6),
    )

    ap = alt.Chart(event).transform_calculate(
        band=f'"{band_label}"'
    ).mark_area(opacity=0.22).encode(
        x=x,
        y=alt.Y("ap_share:Q", title="0–1 scale", scale=alt.Scale(domain=[0, 1])),
        color=alt.Color("band:N", scale=scale, title=None),
        tooltip=[
            alt.Tooltip("datetime:T", title="Bin", format="%d %b %Y %H:%M"),
            alt.Tooltip("ap_now:Q", title="Ap (now)", format=".0f"),
        ],
    )

    lines = alt.Chart(long).mark_line(
        strokeWidth=_LINE_WIDTH, point=alt.OverlayMarkDef(size=45, filled=True),
    ).encode(
        x=x,
        y=alt.Y("probability:Q", scale=alt.Scale(domain=[0, 1])),
        color=alt.Color("model:N", scale=scale, title=None),
        tooltip=[
            alt.Tooltip("datetime:T", title="Bin", format="%d %b %Y %H:%M"),
            alt.Tooltip("model:N", title="Model"),
            alt.Tooltip("probability:Q", title="P(storm)", format=".2f"),
        ],
    )

    return _finish(alt.layer(ap, lines), t, height)

# ==========================================================
# Data Explorer Charts
# ==========================================================

import altair as alt
import pandas as pd


def feature_timeseries(
    data: pd.DataFrame,
    feature: str,
    theme: dict,
    show_storms: bool = True,
):
    """
    Interactive time-series for any feature.

    Mouse wheel:
        zoom

    Drag:
        pan

    Double click:
        reset
    """

    zoom = alt.selection_interval(bind="scales")

    base = (
        alt.Chart(data)
        .encode(
            x=alt.X(
                "datetime:T",
                title="Date",
            )
        )
    )

    line = (
        base
        .mark_line(
            color=theme["series"][0],
            strokeWidth=2,
        )
        .encode(
            y=alt.Y(
                f"{feature}:Q",
                title=feature.replace("_", " "),
            ),
            tooltip=[
                alt.Tooltip(
                    "datetime:T",
                    title="Time",
                ),
                alt.Tooltip(
                    f"{feature}:Q",
                    format=".3f",
                ),
            ],
        )
    )

    if not show_storms:
        return (
            line
            .properties(height=420)
            .add_params(zoom)
        )

    storms = (
        alt.Chart(
            data[data["storm_3h"] == 1]
        )
        .mark_circle(
            color=STATUS["critical"],
            size=55,
        )
        .encode(
            x="datetime:T",
            y=f"{feature}:Q",
            tooltip=[
                alt.Tooltip("datetime:T"),
                alt.Tooltip(f"{feature}:Q"),
            ],
        )
    )

    return (
        (line + storms)
        .properties(height=420)
        .add_params(zoom)
    )


# ----------------------------------------------------------


def feature_distribution(
    data: pd.DataFrame,
    feature: str,
    theme: dict,
):

    return (
        alt.Chart(data)
        .mark_bar(
            color=theme["series"][0],
            opacity=0.85,
        )
        .encode(
            alt.X(
                f"{feature}:Q",
                bin=alt.Bin(maxbins=50),
                title=feature.replace("_", " "),
            ),
            alt.Y(
                "count()",
                title="Observations",
            ),
            tooltip=[
                alt.Tooltip("count()"),
            ],
        )
        .properties(
            height=350,
        )
    )


# ----------------------------------------------------------


def storm_distribution(
    data: pd.DataFrame,
    feature: str,
    theme: dict,
):

    df = data.copy()

    df["Condition"] = (
        df["storm_3h"]
        .map(
            {
                0: "Quiet",
                1: "Storm",
            }
        )
    )

    return (
        alt.Chart(df)
        .transform_density(
            feature,
            groupby=["Condition"],
            as_=[feature, "Density"],
        )
        .mark_area(
            opacity=0.45,
        )
        .encode(
            x=alt.X(
                f"{feature}:Q",
                title=feature.replace("_", " "),
            ),
            y="Density:Q",
            color=alt.Color(
                "Condition:N",
                scale=alt.Scale(
                    range=[
                        theme["series"][0],
                        STATUS["critical"],
                    ]
                ),
            ),
            tooltip=[
                "Condition:N",
                alt.Tooltip(
                    "Density:Q",
                    format=".3f",
                ),
            ],
        )
        .properties(
            height=350,
        )
    )


# ----------------------------------------------------------


def monthly_storms(
    monthly: pd.DataFrame,
    theme: dict,
):

    return (
        alt.Chart(monthly)
        .mark_bar(
            color=theme["series"][2],
        )
        .encode(
            x=alt.X(
                "datetime:T",
                title="Month",
            ),
            y=alt.Y(
                "storm_3h:Q",
                title="Storm Bins",
            ),
            tooltip=[
                alt.Tooltip(
                    "datetime:T",
                    title="Month",
                ),
                alt.Tooltip(
                    "storm_3h:Q",
                    title="Storms",
                ),
            ],
        )
        .properties(
            height=350,
        )
    )

# ----------------------------------------------------------


def feature_scatter(
    data: pd.DataFrame,
    x_feature: str,
    y_feature: str,
    theme: dict,
):
    """
    Interactive scatter plot comparing two selected features.
    Storm observations are highlighted in a contrasting color.
    """

    df = data.copy()

    df["Condition"] = df["storm_3h"].map(
        {
            0: "Quiet",
            1: "Storm",
        }
    )

    brush = alt.selection_interval()

    points = (
        alt.Chart(df)
        .mark_circle(size=42, opacity=0.65)
        .encode(
            x=alt.X(
                f"{x_feature}:Q",
                title=x_feature.replace("_", " "),
            ),
            y=alt.Y(
                f"{y_feature}:Q",
                title=y_feature.replace("_", " "),
            ),
            color=alt.Color(
                "Condition:N",
                scale=alt.Scale(
                    domain=["Quiet", "Storm"],
                    range=[
                        theme["series"][0],
                        STATUS["critical"],
                    ],
                ),
            ),
            tooltip=[
                alt.Tooltip("datetime:T"),
                alt.Tooltip(f"{x_feature}:Q", format=".3f"),
                alt.Tooltip(f"{y_feature}:Q", format=".3f"),
                "Condition:N",
            ],
        )
        .add_params(brush)
    )

    return points.properties(height=420)


# ----------------------------------------------------------


def correlation_heatmap(
    corr: pd.DataFrame,
):
    """
    Correlation matrix heatmap.
    """

    heat = (
        alt.Chart(
            corr.reset_index()
            .melt(
                id_vars="index",
                var_name="Feature 2",
                value_name="Correlation",
            )
            .rename(columns={"index": "Feature 1"})
        )
        .mark_rect()
        .encode(
            x=alt.X(
                "Feature 1:N",
                sort=None,
                title=None,
            ),
            y=alt.Y(
                "Feature 2:N",
                sort=None,
                title=None,
            ),
            color=alt.Color(
                "Correlation:Q",
                scale=alt.Scale(
                    scheme="redblue",
                    domain=(-1, 1),
                ),
            ),
            tooltip=[
                "Feature 1",
                "Feature 2",
                alt.Tooltip(
                    "Correlation:Q",
                    format=".3f",
                ),
            ],
        )
    )

    text = (
        alt.Chart(
            corr.reset_index()
            .melt(
                id_vars="index",
                var_name="Feature 2",
                value_name="Correlation",
            )
            .rename(columns={"index": "Feature 1"})
        )
        .mark_text(fontSize=10)
        .encode(
            x="Feature 1:N",
            y="Feature 2:N",
            text=alt.Text(
                "Correlation:Q",
                format=".2f",
            ),
            color=alt.condition(
                "abs(datum.Correlation) > 0.6",
                alt.value("white"),
                alt.value("black"),
            ),
        )
    )

    return (
        heat + text
    ).properties(
        height=520,
        width=520,
    )


# ----------------------------------------------------------


def rolling_feature(
    data: pd.DataFrame,
    feature: str,
    theme: dict,
):
    """
    Overlay raw observations with a rolling mean.
    """

    base = alt.Chart(data)

    raw = (
        base
        .mark_line(
            color="#BBBBBB",
            opacity=0.45,
        )
        .encode(
            x="datetime:T",
            y=f"{feature}:Q",
        )
    )

    smooth = (
        base
        .transform_window(
            rolling_mean=f"mean({feature})",
            frame=[-12, 12],
        )
        .mark_line(
            color=theme["series"][1],
            strokeWidth=3,
        )
        .encode(
            x="datetime:T",
            y="rolling_mean:Q",
            tooltip=[
                alt.Tooltip(
                    "rolling_mean:Q",
                    format=".3f",
                    title="Rolling Mean",
                )
            ],
        )
    )

    return (
        raw + smooth
    ).properties(
        height=420,
    )


# ----------------------------------------------------------


def yearly_storms(
    yearly: pd.DataFrame,
    theme: dict,
):
    """
    Number of storm bins observed each year.
    """

    return (
        alt.Chart(yearly)
        .mark_bar(
            color=theme["series"][2],
        )
        .encode(
            x=alt.X(
                "Year:O",
                title="Year",
            ),
            y=alt.Y(
                "Storms:Q",
                title="Storm Bins",
            ),
            tooltip=[
                "Year",
                "Storms",
            ],
        )
        .properties(
            height=340,
        )
    )


# ----------------------------------------------------------


def feature_statistics(
    data: pd.DataFrame,
    feature: str,
):
    """
    Returns descriptive statistics as a DataFrame.
    """

    s = data[feature].dropna()

    return pd.DataFrame(
        {
            "Statistic": [
                "Mean",
                "Median",
                "Std Dev",
                "Minimum",
                "25%",
                "75%",
                "Maximum",
            ],
            "Value": [
                s.mean(),
                s.median(),
                s.std(),
                s.min(),
                s.quantile(0.25),
                s.quantile(0.75),
                s.max(),
            ],
        }
    )

