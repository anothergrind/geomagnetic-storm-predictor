---
license: other
license_name: "celestrak-usage-policy"
license_link: "https://celestrak.org/usage-policy.php"
pretty_name: "Space Weather Indices (Kp, Ap, F10.7)"
language:
  - en
description: "Daily geomagnetic and solar activity indices since 1957 from NOAA SWPC via CelesTrak. Includes Kp/Ap geomagnetic indices, F10.7 solar radio flux, and international sunspot numbers.  These indices toge"
task_categories:
  - tabular-regression
  - time-series-forecasting
tags:
  - space
  - space-weather
  - geomagnetic
  - solar
  - noaa
  - celestrak
  - open-data
  - kp-index
  - f10.7
  - sunspot
  - solar-cycle
  - swpc
  - tabular-data
  - parquet
size_categories:
  - 10K<n<100K
configs:
  - config_name: default
    data_files:
      - split: train
        path: data/space_weather_indices.parquet
    default: true
---

# Space Weather Indices (Kp, Ap, F10.7)


<div align="center">
  <img src="banner.jpg" alt="Aurora borealis blankets the Earth, seen from the ISS" width="400">
  <p><em>Credit: NASA</em></p>
</div>


*Part of a [dataset collection](https://huggingface.co/collections/juliensimon/space-weather-datasets-69c24cae98f1666f2101ca70) on Hugging Face.*

## Dataset description

Daily geomagnetic and solar activity indices since 1957 from NOAA SWPC via CelesTrak. Includes Kp/Ap geomagnetic indices, F10.7 solar radio flux, and international sunspot numbers.

These indices together form the essential parameter set for characterizing the state of the heliosphere and its coupling to the terrestrial environment. The Kp index (quasi-logarithmic, 0-9 scale, 3-hourly) captures planetary-scale geomagnetic disturbances driven by solar wind-magnetosphere interactions, while the Ap index (its linearized daily equivalent in nanotesla) serves as the standard geomagnetic input to atmospheric density models. The F10.7 solar radio flux (measured daily at 2800 MHz in Penticton, Canada) is the primary proxy for solar extreme ultraviolet (EUV) radiation that heats the thermosphere -- the atmospheric layer where most satellites experience drag.

For operational space weather applications, this dataset provides the complete set of inputs required by the major atmospheric density models: NRLMSISE-00 (F10.7, F10.7bar, Ap), JB2008 (F10.7 plus supplementary indices), and DTM (F10.7, Kp). The storm classification (G1-G5) derived from Kp thresholds is the same scale used in NOAA space weather alerts.


This dataset is suitable for **tabular regression, time-series forecasting** tasks.

## Schema

| Column | Type | Description | Sample | Null % |
|--------|------|-------------|--------|--------|
| `date` | datetime64[us] | Observation date in UTC | 1957-10-01 00:00:00 | 0.0% |
| `bartels_rotation` | int64 | Bartels Solar Rotation Number -- a 27-day cycle count since 1832, used to align solar data with the Sun's synodic rotation period as seen from Earth | 1700 | 0.0% |
| `bartels_day` | int64 | Day within the current Bartels rotation cycle (1-27) | 19 | 0.0% |
| `kp_0000` | float64 | 3-hourly Kp geomagnetic index for the 00:00-03:00 UT interval (quasi-logarithmic, 0-9 scale); measures planetary-scale magnetic field disturbances | 43.0 | 0.7% |
| `kp_0300` | float64 | 3-hourly Kp geomagnetic index for the 03:00-06:00 UT interval | 40.0 | 0.7% |
| `kp_0600` | float64 | 3-hourly Kp geomagnetic index for the 06:00-09:00 UT interval | 30.0 | 0.7% |
| `kp_0900` | float64 | 3-hourly Kp geomagnetic index for the 09:00-12:00 UT interval | 20.0 | 0.7% |
| `kp_1200` | float64 | 3-hourly Kp geomagnetic index for the 12:00-15:00 UT interval | 37.0 | 0.7% |
| `kp_1500` | float64 | 3-hourly Kp geomagnetic index for the 15:00-18:00 UT interval | 23.0 | 0.7% |
| `kp_1800` | float64 | 3-hourly Kp geomagnetic index for the 18:00-21:00 UT interval | 43.0 | 0.7% |
| `kp_2100` | float64 | 3-hourly Kp geomagnetic index for the 21:00-24:00 UT interval | 37.0 | 0.7% |
| `kp_sum` | float64 | Sum of the eight daily 3-hourly Kp values (0-72); daily aggregate measure of geomagnetic activity | 273.0 | 0.7% |
| `ap_0000` | float64 | 3-hourly Ap index for the 00:00-03:00 UT interval -- linearized equivalent of Kp in nanotesla units; used as input to atmospheric density models (NRLMSISE-00, JB2008) | 32.0 | 0.7% |
| `ap_0300` | float64 | 3-hourly Ap index for the 03:00-06:00 UT interval | 27.0 | 0.7% |
| `ap_0600` | float64 | 3-hourly Ap index for the 06:00-09:00 UT interval | 15.0 | 0.7% |
| `ap_0900` | float64 | 3-hourly Ap index for the 09:00-12:00 UT interval | 7.0 | 0.7% |
| `ap_1200` | float64 | 3-hourly Ap index for the 12:00-15:00 UT interval | 22.0 | 0.7% |
| `ap_1500` | float64 | 3-hourly Ap index for the 15:00-18:00 UT interval | 9.0 | 0.7% |
| `ap_1800` | float64 | 3-hourly Ap index for the 18:00-21:00 UT interval | 32.0 | 0.7% |
| `ap_2100` | float64 | 3-hourly Ap index for the 21:00-24:00 UT interval | 22.0 | 0.7% |
| `ap_avg` | float64 | Daily average Ap index; geomagnetic storm threshold at Ap >= 50; key input for satellite drag models | 21.0 | 0.7% |
| `cp` | float64 | Daily Character Figure Cp (0.0-2.5) -- a qualitative measure of the overall level of geomagnetic disturbance for the day | 1.1 | 0.7% |
| `c9` | float64 | Converted Cp on a 0-9 integer scale; derived from Cp for easier comparison with Kp | 5.0 | 0.7% |
| `sunspot_number` | int64 | International Sunspot Number (ISN) -- daily count of sunspot groups and individual spots; primary indicator of the ~11-year solar activity cycle | 334 | 0.0% |
| `f107_obs` | float64 | Observed 10.7 cm (2800 MHz) solar radio flux in solar flux units (SFU, 1 SFU = 10^-22 W/m2/Hz); measured at Penticton, Canada; primary proxy for solar EUV radiation that heats the thermosphere | 269.3 | 0.0% |
| `f107_adj` | float64 | F10.7 solar radio flux adjusted to 1 AU distance; removes the effect of Earth's orbital eccentricity for physical comparisons | 269.8 | 0.0% |
| `f107_data_type` | str | Data source flag: OBS (observed), INT (interpolated from observations), PRD (predicted), PRM (predicted monthly mean) | OBS | 0.0% |
| `f107_obs_center81` | float64 | 81-day centered running average of observed F10.7; smooths the 27-day solar rotation modulation to represent background EUV irradiance level | 266.6 | 0.0% |
| `f107_obs_last81` | float64 | 81-day trailing (last 81 days) running average of observed F10.7; available in near-real-time unlike the centered average | 230.9 | 0.0% |
| `f107_adj_center81` | float64 | 81-day centered running average of 1-AU-adjusted F10.7 | 266.8 | 0.0% |
| `f107_adj_last81` | float64 | 81-day trailing running average of 1-AU-adjusted F10.7 | 235.5 | 0.0% |
| `is_storm` | bool | True when daily average Ap >= 50, indicating a geomagnetic storm day; storms cause elevated satellite drag, GPS errors, and power grid disturbances | False | 0.0% |
| `storm_level` | str | NOAA G-scale classification based on maximum 3-hourly Kp: G1 (Kp=5, minor), G2 (Kp=6, moderate), G3 (Kp=7, strong), G4 (Kp=8, severe), G5 (Kp=9, extreme); null for non-storm days | G5 | 1.4% |
| `data_type` | str | Simplified data type: 'observed' (OBS/INT -- based on measurements) or 'predicted' (PRD/PRM -- forecast values) | observed | 0.0% |

## Quick stats

- **25,094** observed days (1957-10-01 to 2026-06-14)
- **613** geomagnetic storm days (Ap >= 50)
- **24,975** severe storms (G3+)
- Strongest storm: Ap=280 on 1960-11-13

## Usage

```python
from datasets import load_dataset

ds = load_dataset("juliensimon/space-weather-indices", split="train")
df = ds.to_pandas()
```

```python
from datasets import load_dataset

ds = load_dataset("juliensimon/space-weather-indices", split="train")
df = ds.to_pandas()

# Only observed data (exclude predictions)
observed = df[df["data_type"] == "observed"]

# Geomagnetic storms
storms = df[df["is_storm"] == True].sort_values("ap_avg", ascending=False)

# Solar cycle visualization
import matplotlib.pyplot as plt
df["year"] = df["date"].dt.year
yearly_ssn = df.groupby("year")["sunspot_number"].mean()
yearly_ssn.plot(figsize=(12, 4))
plt.ylabel("Mean Sunspot Number")
plt.title("Solar Cycle from Daily Sunspot Numbers")
plt.show()

# F10.7 flux trend (drives atmospheric drag)
df.set_index("date")[["f107_adj"]].rolling(81).mean().plot()
plt.ylabel("F10.7 (SFU)")
plt.title("81-day Running Mean F10.7 Solar Flux")
plt.show()
```

## Data source

https://celestrak.org/SpaceData/

## Update schedule

Daily at 11:00 UTC via GitHub Actions

## Related datasets

- [juliensimon/solar-flare-events](https://huggingface.co/datasets/juliensimon/solar-flare-events)

- [juliensimon/space-track-satcat](https://huggingface.co/datasets/juliensimon/space-track-satcat)

- [juliensimon/space-track-tle-history](https://huggingface.co/datasets/juliensimon/space-track-tle-history)

- [juliensimon/neo-close-approaches](https://huggingface.co/datasets/juliensimon/neo-close-approaches)

> If you find this dataset useful, please consider [giving it a like](https://huggingface.co/datasets/juliensimon/space-weather-indices) on Hugging Face. It helps others discover it.

## About the author

Created by [Julien Simon](https://julien.org) — AI Operating Partner at Fortino Capital. Part of the [Space Datasets](https://julien.org/datasets) collection.

## Citation

```bibtex
@dataset{space_weather_indices,
  title = {Space Weather Indices (Kp, Ap, F10.7)},
  author = {juliensimon},
  year = {2026},
  url = {https://huggingface.co/datasets/juliensimon/space-weather-indices},
  publisher = {Hugging Face}
}
```

## License

[celestrak-usage-policy](https://celestrak.org/usage-policy.php)
