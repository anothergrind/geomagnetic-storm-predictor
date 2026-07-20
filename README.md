# Geomagnetic Storm Predictor

Forecasting geomagnetic storms from OMNI solar-wind parameters, solar-flare
and CME activity. The modeling dataset (`data/time_binned_dataset.csv`) bins
1995–2024 into 3-hour windows with storm labels (Ap ≥ 56) at 3/6/12/24-hour
forecast horizons.

## Streamlit app

An interactive dashboard (`streamlit_app.py`) trains a gradient-boosting
classifier on the time-binned dataset and lets you explore storm history,
model performance on the held-out 2022+ test period, and per-event forecasts.

Run locally:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

To deploy on [Streamlit Community Cloud](https://share.streamlit.io), point a
new app at this repo with `streamlit_app.py` as the entrypoint.

## Repository layout

- `data/` — raw and cleaned source datasets plus the combined time-binned dataset
- `exploratory-data-analysis/` — EDA notebooks per data source
- `notebooks/` — dataset assembly and baseline models (logistic regression, random forest, SVM, XGBoost)
- `time-series-modeling/` — time-aware models (XGBoost, TCN, decision tree) across forecast horizons
