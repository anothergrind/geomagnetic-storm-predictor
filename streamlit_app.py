"""Geomagnetic Storm Predictor — Streamlit app.

Trains a gradient-boosting classifier on the team's time-binned dataset
(3-hour bins, 1995-2024) to predict geomagnetic storms (Ap-index threshold)
at a selectable forecast horizon, using the same time-based train/test split
as the modeling notebooks (train < 2022-01-01, test >= 2022-01-01).
"""
import json
from pathlib import Path
import joblib

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd
import streamlit as st
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)

DATA_PATH = "data/time_binned_dataset.csv"
SPLIT_DATE = "2022-01-01"
HORIZONS = [3]
XGB_MODEL_PATH = Path("time-series-modeling/xgboost_storm_3h_deployed.joblib")
XGB_METADATA_PATH = Path("time-series-modeling/xgboost_storm_3h_metadata.json")

# Palette (validated for CVD safety and contrast)
BLUE = "#2a78d6"
RED = "#e34948"
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
SURFACE = "#fcfcfb"
SEQ_BLUES = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]

st.set_page_config(page_title="Geomagnetic Storm Predictor", page_icon="🌌", layout="wide")


def style_axes(ax):
    ax.set_facecolor(SURFACE)
    ax.figure.set_facecolor(SURFACE)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


@st.cache_data(show_spinner="Loading dataset…")
def load_data():
    df = pd.read_csv(DATA_PATH, parse_dates=["datetime"])
    df = df.sort_values("datetime").reset_index(drop=True)
    float_cols = df.select_dtypes("float64").columns
    df[float_cols] = df[float_cols].astype("float32")
    return df

@st.cache_data(show_spinner="Loading XGBoost metadata…")
def load_xgb_metadata():
    with open(XGB_METADATA_PATH) as f:
        return json.load(f)


@st.cache_resource(show_spinner="Loading deployed XGBoost model…")
def load_xgb_model():
    return joblib.load(XGB_MODEL_PATH)


@st.cache_resource(show_spinner="Scoring test period…")
def train_model(horizon):
    if horizon != 3:
        raise ValueError("The deployed XGBoost model currently supports only the 3-hour horizon.")

    df = load_data()
    metadata = load_xgb_metadata()
    model = load_xgb_model()

    features = metadata["features"]
    target = metadata["target"]

    missing_features = [col for col in features if col not in df.columns]
    if missing_features:
        raise ValueError(f"Missing required XGBoost features: {missing_features}")

    test = df[df["datetime"] >= SPLIT_DATE].copy()
    proba = model.predict_proba(test[features])[:, 1]

    return model, test.reset_index(drop=True), proba


def storm_threshold(df, horizon):
    """Ap threshold implied by the storm labels."""
    return df.loc[df[f"storm_{horizon}h"] == 1, f"ap_target_{horizon}h"].min()


# ---------------------------------------------------------------- sidebar --
st.sidebar.title("🌌 Storm Predictor")
page = st.sidebar.radio("Page", ["Overview", "Model performance", "Forecast explorer"])
st.sidebar.markdown("---")
horizon = st.sidebar.select_slider("Forecast horizon (hours)", options=HORIZONS, value=3)
st.sidebar.caption(
    f"Predicting whether a geomagnetic storm occurs {horizon} hours ahead, "
    "from solar-wind, flare, and CME conditions in the current 3-hour bin."
)

df = load_data()
target = f"storm_{horizon}h"

# --------------------------------------------------------------- overview --
if page == "Overview":
    st.title("Geomagnetic Storm Predictor")
    st.write(
        "Forecasting geomagnetic storms from OMNI solar-wind parameters, "
        "solar-flare and CME activity, aggregated into 3-hour bins. "
        f"A storm is a bin where the Ap index exceeds "
        f"**{storm_threshold(df, horizon):.0f}** (horizon: {horizon} h)."
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Time bins", f"{len(df):,}")
    c2.metric(
        "Date range",
        f"{df['datetime'].min():%Y}–{df['datetime'].max():%Y}",
    )
    c3.metric("Storm bins", f"{int(df[target].sum()):,}")
    c4.metric("Storm rate", f"{df[target].mean() * 100:.2f}%")

    st.subheader("Ap index over time")
    daily = df.set_index("datetime")["ap_now"].resample("D").mean()
    fig, ax = plt.subplots(figsize=(11, 3))
    ax.plot(daily.index, daily.values, color=BLUE, linewidth=0.8)
    ax.set_ylabel("Ap (daily mean)", color=INK_SECONDARY, fontsize=9)
    style_axes(ax)
    st.pyplot(fig, width='stretch')
    plt.close(fig)

    st.subheader(f"Storm bins per year ({horizon} h horizon)")
    yearly = df.groupby(df["datetime"].dt.year)[target].sum()
    fig, ax = plt.subplots(figsize=(11, 3))
    ax.bar(yearly.index, yearly.values, color=BLUE, width=0.7)
    ax.set_ylabel("Storm bins", color=INK_SECONDARY, fontsize=9)
    style_axes(ax)
    st.pyplot(fig, width='stretch')
    plt.close(fig)
    st.caption(
        "Storm counts track the ~11-year solar cycle: maxima around 2003, "
        "2015, and 2024, quiet minima around 2009 and 2019."
    )

    with st.expander("Browse the dataset"):
        st.dataframe(df.tail(500), width='stretch')

# -------------------------------------------------------------- model page --
elif page == "Model performance":
    st.title("Model performance")
    metadata = load_xgb_metadata()

    st.write(
        f"Deployed **Candidate A XGBoost** model for 3-hour geomagnetic storm prediction. "
        f"The model uses the no-current-Ap feature set, Random Oversampling during training, "
        f"and a median-imputation + XGBoost pipeline. It was trained on 2010–2021 and "
        f"evaluated on 2022–2024. The selected operating threshold is "
        f"**{metadata['operating_threshold']:.2f}**."
    )

    model, test, proba = train_model(horizon)
    y_true = test[target].values

    threshold = st.slider(
        "Decision threshold (storm probability)",
        min_value=0.05,
        max_value=0.99,
        value=float(metadata["operating_threshold"]),
        step=0.01,
    )
    y_pred = (proba >= threshold).astype(int)

    # Persistence baseline: predict a storm if the current bin is already at
    # storm level (the standard no-skill reference for space-weather models).
    ap_storm_level = storm_threshold(df, horizon)
    baseline_pred = (test["ap_now"] >= ap_storm_level).astype(int)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Precision", f"{precision_score(y_true, y_pred, zero_division=0):.2f}")
    c2.metric("Recall", f"{recall_score(y_true, y_pred, zero_division=0):.2f}")
    c3.metric("F1", f"{f1_score(y_true, y_pred, zero_division=0):.2f}")
    c4.metric("ROC AUC", f"{roc_auc_score(y_true, proba):.3f}")

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Confusion matrix")
        cm = confusion_matrix(y_true, y_pred)
        fig, ax = plt.subplots(figsize=(4.4, 3.6))
        cmap = LinearSegmentedColormap.from_list("seq_blue", SEQ_BLUES)
        ax.imshow(cm, cmap=cmap)
        for (i, j), v in np.ndenumerate(cm):
            frac = cm[i, j] / cm.max()
            ax.text(
                j, i, f"{v:,}",
                ha="center", va="center", fontsize=11,
                color="white" if frac > 0.5 else INK,
            )
        ax.set_xticks([0, 1], ["No storm", "Storm"], fontsize=9, color=INK_SECONDARY)
        ax.set_yticks([0, 1], ["No storm", "Storm"], fontsize=9, color=INK_SECONDARY)
        ax.set_xlabel("Predicted", color=INK_SECONDARY, fontsize=9)
        ax.set_ylabel("Actual", color=INK_SECONDARY, fontsize=9)
        fig.set_facecolor(SURFACE)
        st.pyplot(fig, width='stretch')
        plt.close(fig)

    with col_right:
        st.subheader("Precision–recall curve")
        prec, rec, _ = precision_recall_curve(y_true, proba)
        ap_model = average_precision_score(y_true, proba)
        base_prec = precision_score(y_true, baseline_pred, zero_division=0)
        base_rec = recall_score(y_true, baseline_pred, zero_division=0)

        fig, ax = plt.subplots(figsize=(4.8, 3.6))
        ax.plot(rec, prec, color=BLUE, linewidth=2, label=f"Model (AP {ap_model:.2f})")
        ax.scatter(
            [base_rec], [base_prec], color=MUTED, s=60, zorder=3,
            label="Persistence baseline",
        )
        ax.set_xlabel("Recall", color=INK_SECONDARY, fontsize=9)
        ax.set_ylabel("Precision", color=INK_SECONDARY, fontsize=9)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1.02)
        ax.legend(fontsize=8, frameon=False, labelcolor=INK_SECONDARY)
        style_axes(ax)
        st.pyplot(fig, width='stretch')
        plt.close(fig)

    tn, fp, fn, tp = cm.ravel()
    st.write(
        f"At this threshold the model catches **{tp} of {tp + fn}** storms in the "
        f"test period ({df['datetime'].max():%Y-%m-%d} back to {SPLIT_DATE}) with "
        f"**{fp}** false alarms. The persistence baseline (assume storm continues "
        f"if Ap is already ≥ {ap_storm_level:.0f}) reaches precision "
        f"{base_prec:.2f} / recall {base_rec:.2f}."
    )

# --------------------------------------------------------------- explorer --
else:
    st.title("Forecast explorer")
    st.write(
        "Step through the held-out test period (2022 onward) and compare the "
        "model's storm probability with what actually happened."
    )

    model, test, proba = train_model(horizon)
    test = test.assign(storm_probability=proba)

    min_d, max_d = test["datetime"].min().date(), test["datetime"].max().date()
    window = st.slider(
        "Test-period window",
        min_value=min_d, max_value=max_d,
        value=(pd.Timestamp("2024-05-01").date(), pd.Timestamp("2024-06-01").date()),
        format="YYYY-MM-DD",
    )
    mask = (test["datetime"].dt.date >= window[0]) & (test["datetime"].dt.date <= window[1])
    view = test[mask]

    if view.empty:
        st.info("No bins in the selected window.")
    else:
        storms = view[view[target] == 1]
        fig, ax = plt.subplots(figsize=(11, 3.4))
        ax.plot(
            view["datetime"], view["storm_probability"],
            color=BLUE, linewidth=1.4, label="Predicted storm probability",
        )
        if not storms.empty:
            ax.scatter(
                storms["datetime"], np.full(len(storms), 1.02),
                color=RED, marker="v", s=36, label="Actual storm bin", zorder=3,
            )
        ax.set_ylim(0, 1.08)
        ax.set_ylabel("P(storm)", color=INK_SECONDARY, fontsize=9)
        ax.legend(fontsize=8, frameon=False, loc="upper left", labelcolor=INK_SECONDARY)
        style_axes(ax)
        st.pyplot(fig, width='stretch')
        plt.close(fig)

        st.caption(
            f"{len(view):,} bins shown · {len(storms)} actual storm bins in window. "
            "Try May 2024 — the Gannon storm, the strongest in two decades."
        )

        st.subheader("Conditions at the highest-risk bin")
        peak = view.loc[view["storm_probability"].idxmax()]
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("When", f"{peak['datetime']:%Y-%m-%d %H:%M}")
        c2.metric("P(storm)", f"{peak['storm_probability']:.2f}")
        c3.metric("Bz GSM (nT)", f"{peak['bz_gsm_nt_last']:.1f}")
        c4.metric("Flow speed (km/s)", f"{peak['flow_speed_kms_last']:.0f}")
        c5.metric("Actual outcome", "Storm" if peak[target] == 1 else "No storm")
