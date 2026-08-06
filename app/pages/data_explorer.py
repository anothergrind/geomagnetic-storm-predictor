"""
Space Weather Explorer — interactively explore the dataset used to train the
geomagnetic storm prediction models.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app import charts, ui
from app.data import TARGET, load_data
from app.theme import tokens

# ==========================================================
# Feature metadata
# ==========================================================

PHENOMENA = {
    "🌬 Solar Wind": {
        "description": (
            "Solar wind carries plasma from the Sun toward Earth. "
            "Its speed, density, pressure and electric field strongly "
            "influence geomagnetic activity."
        ),

        "features": {
            "Solar Wind Speed": "flow_speed_kms_last",
            "Dynamic Pressure": "flow_pressure_npa_last",
            "Proton Density": "proton_density_cm3_last",
            "Electric Field": "electric_field_mvpm_last",
        },
    },

    "🧲 Magnetic Field": {
        "description": (
            "The interplanetary magnetic field determines how efficiently "
            "solar wind energy couples into Earth's magnetic field. "
            "A strongly southward Bz often precedes geomagnetic storms."
        ),

        "features": {
            "Southward Bz": "bz_gsm_nt_last",
            "By Component": "by_gsm_nt_last",
            "Total Field Bt": "bt_nt_last",
        },
    },

    "🌍 Geomagnetic Response": {
        "description": (
            "Indices measuring Earth's geomagnetic disturbance."
        ),

        "features": {
            "Ap Index": "ap_now",
        },
    },

    "☀ Solar Activity": {
        "description": (
            "Solar flares and coronal mass ejections provide the eruptive "
            "events that ultimately drive geomagnetic storms."
        ),

        "features": {
            "Largest Flare": "flare_max_class_now",
            "CMEs (72 h)": "cme_count_72h",
            "Maximum CME Speed": "cme_max_speed_72h",
        },
    },
}

# caching functions for reducing load time

@st.cache_data(show_spinner=False)
def filter_dataset(df, start_date, end_date):
    return df.loc[
        (df["datetime"].dt.date >= start_date)
        & (df["datetime"].dt.date <= end_date)
    ].copy()

@st.cache_data(show_spinner=False)
def compute_correlation(df, columns):
    return df[list(columns)].corr()

@st.cache_data(show_spinner=False)
def sample_data(df, n):

    return df.sample(
        min(len(df), n),
        random_state=42,
    )

@st.cache_data(show_spinner=False)
def storm_frequency(df, frequency):

    return (
        df
        .set_index("datetime")
        .resample(frequency)[TARGET]
        .sum()
        .reset_index()
    )

# ----------------------------------------------------------
# Helpers
# ----------------------------------------------------------

EXCLUDED_COLUMNS = {
    TARGET,
    "storm_6h",
    "storm_12h",
    "storm_24h",
}


def _numeric_features(df: pd.DataFrame) -> list[str]:
    """Return numeric features that may be explored."""

    cols = df.select_dtypes("number").columns.tolist()

    return sorted(
        c
        for c in cols
        if c not in EXCLUDED_COLUMNS
    )


def _dataset_metrics(df: pd.DataFrame):

    storms = int(df[TARGET].sum())

    ui.stat_row(
        [
            (
                "Observations",
                f"{len(df):,}",
                "3-hour measurements",
            ),
            (
                "Storm bins",
                f"{storms:,}",
                "positive training labels",
            ),
            (
                "Storm rate",
                f"{100 * storms / len(df):.2f}%",
                "dataset imbalance",
            ),
            (
                "Coverage",
                f"{df.datetime.min():%Y}–{df.datetime.max():%Y}",
                "years included",
            ),
        ]
    )


# ----------------------------------------------------------
# Page
# ----------------------------------------------------------

def render():

    t = tokens()

    df = load_data()

    ui.page_header(
        "Space Weather Explorer",
        (
            "Explore the solar-wind measurements, geomagnetic indices, "
            "flare activity and engineered features used to train all "
            "three forecasting models."
        ),
    )

    _dataset_metrics(df)

    ui.section(
        "Explore a Feature",
        (
            "Choose any feature used by the models and inspect how it evolves "
            "through time. Storm observations can be highlighted to reveal "
            "patterns preceding geomagnetic disturbances."
        ),
    )

    numeric = _numeric_features(df)

    c1, c2 = st.columns([2, 1])

    with c1:

        phenomenon = st.selectbox(
            "Physical Phenomenon",
            list(PHENOMENA),
        )

        selection = PHENOMENA[phenomenon]

        st.info(
            selection["description"],
            icon="ℹ️",
        )

        label = st.selectbox(
            "Feature",
            list(selection["features"]),
        )

        feature = selection["features"][label]

    with c2:

        highlight = st.toggle(
            "Highlight storm bins",
            value=True,
        )

    # ------------------------------------------------------
    # Date filter
    # ------------------------------------------------------

    minimum = df["datetime"].min().date()
    maximum = df["datetime"].max().date()

    start_date, end_date = st.slider(
        "Date range",
        minimum,
        maximum,
        (minimum, maximum),
    )

    data = filter_dataset(
        df,
        start_date,
        end_date,
    )

    rolling = st.toggle(
        "Show rolling average",
        value=False,
    )

    if rolling:

        window = st.slider(
            "Rolling window (observations)",
            3,
            96,
            24,
        )

        data[feature] = (
            data[feature]
            .rolling(window)
            .mean()
        )

    with st.container(border=True):

        st.altair_chart(
            charts.feature_timeseries(
                data,
                feature,
                t,
                show_storms=highlight,
            ),
            theme=None,
            use_container_width=True,
        )

    st.caption(
        "Zoom using the mouse wheel, drag to pan, and double-click to reset."
    )

    st.divider()

        # ==========================================================
    # Feature Analysis
    # ==========================================================

    ui.section(
        f"{phenomenon} Analysis",
        selection["description"],
    )

    left, right = st.columns(2, gap="medium")

    # ----------------------------------------------------------
    # Histogram
    # ----------------------------------------------------------

    with left, st.container(border=True):

        st.altair_chart(
            charts.feature_distribution(
                data,
                feature,
                t,
            ),
        )

    # ----------------------------------------------------------
    # Storm vs Quiet
    # ----------------------------------------------------------

    with right, st.container(border=True):

        st.altair_chart(
            charts.storm_distribution(
                data,
                feature,
                t,
            ),
        )

    st.divider()

    # ==========================================================
    # Summary Statistics
    # ==========================================================

    ui.section(
        f"{label} Statistics",
        f"Summary statistics for {label.lower()} over the selected time period.",
    )

    stats = charts.feature_statistics(
        data,
        feature,
    )

    values = data[feature].dropna()

    ui.stat_row(
        [
            (
                "Mean",
                f"{values.mean():.2f}",
                "average",
            ),
            (
                "Median",
                f"{values.median():.2f}",
                "50th percentile",
            ),
            (
                "Std Dev",
                f"{values.std():.2f}",
                "variation",
            ),
            (
                "Missing",
                f"{data[feature].isna().sum():,}",
                "observations",
            ),
        ]
    )

    with st.expander("Full descriptive statistics"):

        st.dataframe(
            stats,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Statistic": st.column_config.TextColumn(
                    width="medium",
                ),
                "Value": st.column_config.NumberColumn(
                    format="%.4f",
                ),
            },
        )

    st.divider()

    # ==========================================================
    # Storm Frequency
    # ==========================================================

    ui.section(
        "Storm Frequency",
        (
            "Observe how often geomagnetic storms occur throughout the "
            "dataset."
        ),
    )

    frequency = st.radio(
        "Aggregation",
        [
            "Monthly",
            "Yearly",
        ],
        horizontal=True,
    )

    if frequency == "Monthly":

        monthly = storm_frequency(
            data,
            "ME",
        )

        with st.container(border=True):

            st.altair_chart(
                charts.monthly_storms(
                    monthly,
                    t,
                ),
                theme=None,
                use_container_width=True,
            )

    else:

        yearly = storm_frequency(
            data,
            "YE",
        )

        yearly.columns = [
            "Year",
            "Storms",
        ]

        with st.container(border=True):

            st.altair_chart(
                charts.yearly_storms(
                    yearly,
                    t,
                ),
                theme=None,
                use_container_width=True,
            )

    st.divider()

    # ==========================================================
    # Correlation Explorer
    # ==========================================================

    ui.section(
        "Feature Relationships",
        (
            "Inspect correlations between selected variables. Highly "
            "correlated features often describe related physical "
            "measurements."
        ),
    )

    group_columns = list(selection["features"].values())

    selected = group_columns.copy()

    # Add Ap Index if it's not already included
    if "ap_now" in numeric and "ap_now" not in selected:
        selected.append("ap_now")

    if len(selected) >= 2:

        corr = compute_correlation(
            data,
            tuple(selected),
        )

        with st.container(border=True):

            st.altair_chart(
                charts.correlation_heatmap(
                    corr,
                ),
                theme=None,
                use_container_width=True,
            )

    else:

        st.info(
            "Select at least two features to compute a correlation matrix."
        )

    st.divider()

        # ==========================================================
    # Feature Relationship Explorer
    # ==========================================================

    comparison_group = st.selectbox(
        "Compare With",
        list(PHENOMENA),
        index=list(PHENOMENA).index("🌍 Geomagnetic Response"),
    )

    comparison_selection = PHENOMENA[comparison_group]

    comparison_label = st.selectbox(
        "Comparison Feature",
        list(comparison_selection["features"]),
    )

    comparison = comparison_selection["features"][comparison_label]

    ui.section(
            f"{label} Relationships",
            (
                f"Compare {label.lower()} with measurements from "
                f"{comparison_group.lower()}."
            ),
        )

    sample = st.slider(
        "Maximum observations",
        min_value=1000,
        max_value=min(len(data), 25000),
        value=min(len(data), 8000),
        step=1000,
    )

    scatter = sample_data(
        data,
        sample,
    )

    with st.container(border=True):

        st.altair_chart(
            charts.feature_scatter(
            scatter,
            feature,
            comparison,
            t,
        ),
            theme=None,
            use_container_width=True,
        )

    st.divider()

    # ==========================================================
    # Raw Dataset
    # ==========================================================

    ui.section(
        "Raw Dataset",
        (
            "Inspect the filtered observations that were used during model "
            "training and evaluation."
        ),
    )

    with st.expander("Filters", expanded=True):

        storms_only = st.checkbox(
            "Show only storm observations",
            value=False,
        )

        selected_columns = st.multiselect(
            "Displayed columns",
            data.columns.tolist(),
            default=[
                c
                for c in [
                    "datetime",
                    "ap_now",
                    TARGET,
                    "bz_gsm_nt_last",
                    "flow_speed_kms_last",
                    "proton_density_cm3_last",
                    "flow_pressure_npa_last",
                ]
                if c in data.columns
            ],
        )

        rows = st.slider(
            "Rows",
            min_value=25,
            max_value=500,
            value=100,
            step=25,
        )

    table = data.copy()

    if storms_only:
        table = table[
            table[TARGET] == 1
        ]

    if selected_columns:

        st.dataframe(
            table[selected_columns].head(rows),
            hide_index=True,
            width="stretch",
            column_config={
                "datetime": st.column_config.DatetimeColumn(
                    "Datetime",
                    format="DD MMM YYYY HH:mm",
                ),
                TARGET: st.column_config.CheckboxColumn(
                    "Storm"
                ),
            },
        )

    else:

        st.info("Select at least one column.")

    st.download_button(
        "Download filtered data (CSV)",
        table.to_csv(index=False).encode("utf-8"),
        file_name="space_weather_filtered.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.divider()

    # ==========================================================
    # Dataset Summary
    # ==========================================================

    ui.section(
        "About This Dataset",
        (
            "A summary of the observations used to train the deployed "
            "geomagnetic storm prediction models."
        ),
    )

    with st.container(border=True):

        st.markdown(
            f"""
**Coverage**

- **Time span:** {df.datetime.min():%d %B %Y} → {df.datetime.max():%d %B %Y}
- **Temporal resolution:** One observation every **3 hours**
- **Prediction target:** **{TARGET}**

**Measurements Included**

- Solar wind properties
- Interplanetary magnetic field (IMF)
- Geomagnetic indices
- Solar flare information
- Coronal Mass Ejection (CME) activity
- Engineered rolling statistics
- Time-derived features

**Purpose**

These measurements form the input feature set used by the
XGBoost, LSTM, and TCN models deployed within this application.
"""
        )

    ui.footer()