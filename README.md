# Geomagnetic Storm Predictor

### Forecasting 3-hour-ahead geomagnetic storms from OMNI solar-wind parameters, solar-flare activity, and CME activity.

This project was developed through the AI4ALL Ignite program and compares three deployed machine learning classifiers — XGBoost, LSTM, and TCN — through an interactive Streamlit dashboard.

### [Live Deployment](https://geomagnetic-storm-predictor-j2aajm6exxcsez34zesctv.streamlit.app/)

## Problem Statement

Geomagnetic storms can disrupt satellites, GPS, radio communication, aviation systems, and power infrastructure. Because strong storms are rare but high-impact events, prediction systems need to identify elevated storm risk while balancing two competing goals: catching true storms and reducing false alarms.

This project asks:

> Can solar-wind, flare, CME, and geomagnetic history data be used to predict whether a geomagnetic storm will occur in the next 3 hours?

Geomagnetic storms are a rare-event prediction problem. Most 3-hour intervals are non-storm intervals, while the events we care about are relatively infrequent but potentially disruptive.

This creates two challenges:

1. **Class imbalance:** a model can achieve high accuracy by predicting "no storm" most of the time, but this neglects true storm recognition.
2. **Temporal dependence:** solar-wind and magnetic-field conditions evolve over time, so randomly splitting observations can leak information between training and testing periods.


## Key Results

- Built a time-binned modeling dataset where each row represents a 3-hour space-weather interval.
- Trained and deployed three 3-hour storm classifiers: XGBoost, LSTM, and TCN.
- Used a chronological split to avoid time leakage: training on 2010–2021 and testing on 2022–2024.
- Compared models on the same held-out test period using ROC-AUC, PR-AUC, precision, recall, and F1.
- Developed a Streamlit dashboard for side-by-side model comparison and forecast exploration.


## Methodologies

We framed geomagnetic storm prediction as a rare-event binary classification task. The main target, `storm_3h`, indicates whether a geomagnetic storm occurs in the next 3-hour forecast window.

For each row at time `T`, features are built only from information available at or before `T`. Targets are created by shifting future Ap values forward by forecast horizon: `ap_target_{H}h` stores the future Ap value, and `storm_{H}h` marks whether that future Ap crosses the storm threshold. Rows with missing targets are dropped so all horizons share the same rows and can be compared directly.

Our workflow included:

- aggregating space-weather observations into 3-hour time bins
- engineering features from solar wind, magnetic-field, flare, CME, and recurrence variables
- using chronological train/test splits to prevent time leakage
- testing both tabular and sequence-modeling approaches
- handling severe class imbalance through oversampling, weighted losses, and focal loss
- tuning operating thresholds to balance precision and recall
- deploying final model artifacts and cached predictions in Streamlit

Final deployed models:

- **XGBoost:** tree-based classifier using engineered tabular features from the current 3-hour bin
- **LSTM:** recurrent sequence model using a rolling 48-hour history
- **TCN:** causal dilated convolutional sequence model using a rolling 48-hour solar-wind history

We selected three complementary model architectures to evaluate whether geomagnetic-storm prediction benefits from nonlinear tabular modeling, recurrent sequence modeling, or temporal convolution.

| Model | Why we selected it |
|---|---|
| **XGBoost** | Provides a strong tabular baseline and captures nonlinear relationships between engineered space-weather features. |
| **LSTM** | Tests whether recurrent modeling can learn temporal dependencies across the preceding 48 hours. |
| **TCN** | Tests whether causal dilated convolutions can capture temporal patterns while providing an alternative to recurrent architectures. |


## Data Sources

This project uses public space-weather datasets, including:

- OMNI-style solar-wind and interplanetary magnetic-field variables
- NASA DONKI space-weather event data, including CME activity
- solar flare event data
- space-weather index data, including Ap-index targets

These sources were combined into `data/time_binned_dataset.csv`, a 3-hour binned modeling dataset containing observations from 1995-2024 used for training and evaluation. For each forecast horizon — 3, 6, 12, and 24 hours — the dataset includes a future Ap target and a binary storm label. For example, `ap_target_3h` stores the future Ap value 3 hours ahead, and `storm_3h = 1` if that future Ap index is at least 50, approximately corresponding to Kp 5 geomagnetic storm conditions. The threshold was selected to represent elevated geomagnetic activity consistent with the project's storm definition. The final deployed models focus on the 3-hour-ahead prediction task (`storm_3h`).

Rather than randomly splitting the dataset, we trained on 2010–2021 and evaluated on the completely held-out 2022–2024 period. This better reflects the intended deployment setting: the model must predict future space-weather conditions using patterns learned from earlier observations.

A random split could place observations from the same evolving storm system in both training and testing, producing overly optimistic performance estimates.


## Model Evaluation

### Operating Thresholds
The default classification threshold of 0.50 was not assumed to be optimal. Instead, operating thresholds were selected using the validation process to balance precision and recall for the rare storm class.

The resulting thresholds differ across models because each model produces different probability distributions:

| Model | Threshold |
|---|---:|
| XGBoost | 0.90 |
| LSTM | 0.795 |
| TCN | 0.60 |

This illustrates why comparing models at an identical probability threshold can be misleading.

### Model Outcomes
| Model | Input style | Test PR-AUC | Precision | Recall | F1 | Operating threshold |
|---|---|---:|---:|---:|---:|---:|
| XGBoost | Single 3-hour bin, no current Ap features | 0.575 | 0.375 | 0.684 | 0.485 | 0.90 |
| LSTM | 48-hour sequence with solar-wind + Ap history | 0.610 | 0.729 | 0.448 | 0.555 | 0.795 |
| TCN | 48-hour sequence of solar-wind features, no current Ap | 0.602 | 0.611 | 0.552 | 0.580 | 0.60 |

The models exhibit different precision-recall tradeoffs:

- **TCN**: achieved the highest F1 score (0.580), indicating the strongest balance between identifying storms and limiting false alarms.
- **LSTM**: achieved the highest PR-AUC (0.610) and precision (0.729), suggesting that its positive predictions were the most reliable overall, although it missed more storms than XGBoost.
- **XGBoost**: achieved the highest recall (0.684), identifying more of the observed storms but producing substantially more false positives.

The dataset contains substantially more non-storm intervals than storm intervals. Consequently, accuracy alone would provide a misleading assessment of model quality. Therefore, we emphasize PR-AUC, precision, recall, and F1 when comparing models. The results also demonstrate that there is no single model that dominates every operating objective.


## [Streamlit App](https://geomagnetic-storm-predictor-j2aajm6exxcsez34zesctv.streamlit.app/)
The Streamlit dashboard turns the modeling pipeline into an interactive space-weather exploration tool.

- **[Forecast Explorer:](https://geomagnetic-storm-predictor-j2aajm6exxcsez34zesctv.streamlit.app/forecast)** Users can select a test-period window from the held-out test set and inspect predicted probabilities alongside observed storm activity.
- **[Model Comparison:](https://geomagnetic-storm-predictor-j2aajm6exxcsez34zesctv.streamlit.app/performance)** Users can compare XGBoost, LSTM, and TCN performance using precision, recall, F1, PR-AUC, confusion matrices, and precision-recall curves, using the same held-out 2022–2024 test period.
- **[Storm Explorer:](https://geomagnetic-storm-predictor-j2aajm6exxcsez34zesctv.streamlit.app/storms)** Individual storm events can be inspected to examine the solar-wind, magnetic-field, flare, and CME conditions surrounding the event.


## Limitations

Several limitations should be considered when interpreting these results:

- **Rare-event prediction:** Even the best model produces false alarms and misses some storms.
- **Historical distribution:** The models are evaluated on 2022–2024 observations and may behave differently under future space-weather conditions.
- **Feature availability:** The models depend on measurements being available and correctly processed before the prediction time.
- **Forecast horizon:** The deployed system focuses specifically on the 3-hour horizon; performance may differ at 6-, 12-, or 24-hour horizons.
- **Model interpretability:** XGBoost provides a more interpretable feature-based baseline, while LSTM and TCN predictions are more difficult to explain directly.
- **Not an operational warning system:** The dashboard is a research and educational demonstration rather than an operational replacement for official space-weather forecasts.


## Technologies Used

- Python
- pandas, NumPy
- scikit-learn
- XGBoost
- PyTorch
- imbalanced-learn
- matplotlib
- Streamlit
- joblib
- parquet
- Git/GitHub


## Repository Structure

```
geomagnetic-storm-predictor/
├── app/
│   ├── pages/
│   │   ├── overview.py
│   │   ├── model_comparison.py
│   │   ├── forecast.py
│   │   ├── storm_explorer.py
│   │   └── data_explorer.py
│   ├── charts.py
│   ├── data.py
│   ├── theme.py
│   ├── ui.py
│   └── nav.py
│
├── data/
│   └── time_binned_dataset.csv
│
├── exploratory-data-analysis/
├── notebooks/
├── time-series-modeling/
├── streamlit_app.py
└── requirements.txt
```

- `data/` — raw, cleaned, and combined time-binned datasets
- `exploratory-data-analysis/` — EDA notebooks for individual data sources
- `notebooks/` — dataset assembly and baseline modeling notebooks
- `time-series-modeling/` — final time-aware models, deployed artifacts, metadata files, and cached predictions
- `streamlit_app.py` — Streamlit dashboard for model comparison and forecast exploration
- `requirements.txt` — Python dependencies


## Future Work

Potential next steps include:

- evaluating additional forecast horizons using the same time-aware
  methodology
- calibrating predicted probabilities for more meaningful risk estimates
- adding model explainability methods such as SHAP for the XGBoost model
- evaluating performance across individual storm events rather than only
  aggregate test-set metrics
- testing robustness on future observations outside the current
  2022–2024 test period
- incorporating additional physical features or longer temporal histories
  into the sequence models


## Authors

This project was completed in collaboration with: 

- Nithila Sadheesh
- Kamsi Ozorji
- Nancy Nakyung Kwak
- Chan Li
- Hafsah Khan
- Nana Oppong Ampofo


## AI4ALL Ignite

This project was developed as part of AI4ALL Ignite, applying machine learning, responsible AI thinking, technical communication, and deployment skills to a real-world space-weather prediction problem.
