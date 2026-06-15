---
license: cc-by-4.0
pretty_name: "NASA DONKI Space Weather Events"
language:
  - en
description: "Space weather events from NASA's DONKI (Database Of Notifications, Knowledge, Information) at the Community Coordinated Modeling Center. Covers coronal mass ejections, geomagnetic storms, interplaneta"
task_categories:
  - tabular-classification
  - time-series-forecasting
tags:
  - space
  - space-weather
  - cme
  - geomagnetic-storm
  - solar
  - nasa
  - open-data
  - coronal-mass-ejection
  - ccmc
  - donki
  - solar-wind
  - tabular-data
  - parquet
size_categories:
  - 10K<n<100K
configs:
  - config_name: default
    data_files:
      - split: train
        path: data/donki_events.parquet
    default: true
---

# NASA DONKI Space Weather Events


<div align="center">
  <img src="banner.jpg" alt="Aurora borealis blankets the Earth, seen from the ISS" width="400">
  <p><em>Credit: NASA</em></p>
</div>


*Part of a [dataset collection](https://huggingface.co/collections/juliensimon/space-weather-datasets-69c24cae98f1666f2101ca70) on Hugging Face.*

## Dataset description

Space weather events from NASA's DONKI (Database Of Notifications, Knowledge, Information) at the Community Coordinated Modeling Center. Covers coronal mass ejections, geomagnetic storms, interplanetary shocks, high-speed streams, and solar energetic particles from 2010 to present.

DONKI tracks the chain of space weather events from Sun to Earth. A CME erupts from the solar corona at speeds ranging from 250 to over 3,000 km/s, driving an interplanetary shock (IPS) ahead of it. When the shock and CME arrive at Earth, they compress the magnetosphere and produce a geomagnetic storm (GST) measurable via the Kp and Dst indices. High-speed streams (HSS) from coronal holes produce recurring disturbances on a ~27-day cadence, while solar energetic particle (SEP) events deliver MeV-range protons within minutes to hours of the initiating flare or CME.

DONKI is uniquely valuable because it preserves the causal linkages between these phenomena via the linked_events field. Unlike raw index time series, DONKI records which specific CME triggered which geomagnetic storm, making it possible to study transit times, geoeffectiveness as a function of CME speed and direction, and the statistical reliability of CME arrival forecasts.

This dataset is suitable for **tabular classification, time-series forecasting** tasks.

## Schema

| Column | Type | Description | Sample | Null % |
|--------|------|-------------|--------|--------|
| `event_type` | str | Event category: CME (coronal mass ejection), GST (geomagnetic storm), IPS (interplanetary shock), HSS (high-speed stream), or SEP (solar energetic particle) | IPS | 0.0% |
| `activity_id` | str | Unique DONKI event identifier (e.g. '2024-05-08T22:09:00-CME-001'); primary key for cross-referencing | 2010-01-20T20:20:00-IPS-001 | 0.0% |
| `start_time` | datetime64[us, UTC] | Event start time in UTC; for CMEs this is the first coronagraph appearance, for GSTs the storm onset | 2010-01-20 20:20:00+00:00 | 0.0% |
| `source_location` | str | Solar source location in heliographic coordinates (e.g. 'N23W45'); CME-only, null for other event types | S20E05 | 75.5% |
| `active_region` | Int64 | NOAA active region number associated with the event (e.g. 13664); CME-only, null for other types | 11123 | 85.8% |
| `note` | str | Analyst notes from CCMC space weather forecasters; may contain event details or IPS location info | STEREO B | 13.3% |
| `link` | str | URL to the DONKI web page for this specific event; useful for accessing additional details and linked analyses | https://kauai.ccmc.gsfc.nasa.gov/DONK... | 0.0% |
| `cme_speed_kms` | float64 | CME speed in km/s from coronagraph analysis (SOHO/LASCO or STEREO/COR); ranges from ~250 to >3000 km/s; CME-only | 620.0 | 26.5% |
| `cme_half_angle_deg` | float64 | CME angular half-width in degrees from coronagraph imagery; halo CMEs have half-angle near 90 degrees; CME-only | 26.0 | 26.5% |
| `cme_latitude` | float64 | CME source latitude in degrees from coronagraph analysis; CME-only | 7.0 | 26.6% |
| `cme_longitude` | float64 | CME source longitude in degrees from coronagraph analysis; CME-only | 8.0 | 36.1% |
| `cme_type` | str | CME morphological type: S (slow), C (common), O (occasional), R (rare), ER (extremely rare); CME-only | C | 26.5% |
| `cme_time_21_5` | datetime64[us, UTC] | Estimated time the CME reaches 21.5 solar radii (roughly 0.1 AU); used for transit-time modeling; CME-only | 2010-04-03 17:16:00+00:00 | 26.5% |
| `cme_measurement` | str | Coronagraph measurement technique used for CME parameter estimation; CME-only | null | 26.5% |
| `linked_events` | str | Comma-separated activity IDs of causally linked events; enables Sun-to-Earth chain analysis (e.g. CME -> IPS -> GST) | 2010-04-03T09:04:00-FLR-001, 2010-04-... | 66.5% |
| `gst_max_kp` | float64 | Maximum Kp index recorded during the geomagnetic storm (0-9 scale); Kp >= 5 is a minor storm, >= 7 strong, 9 extreme; GST-only | 7.0 | 98.2% |
| `gst_kp_count` | float64 | Number of 3-hour Kp index readings during the storm duration; GST-only | 1.0 | 98.2% |

## Quick stats

- **10,907** events (2010-01-20 to 2026-06-15)
- **8,095** CMEs, **197** geomagnetic storms, **1,363** interplanetary shocks
- **775** high speed streams, **477** solar energetic particle events
- Fastest CME: **3529 km/s** on 2024-02-12

## Usage

```python
from datasets import load_dataset

ds = load_dataset("juliensimon/donki-space-weather-events", split="train")
df = ds.to_pandas()
```

```python
from datasets import load_dataset

ds = load_dataset("juliensimon/donki-space-weather-events", split="train")
df = ds.to_pandas()

# Fast CMEs (potential Earth-directed storms)
fast_cmes = df[(df["event_type"] == "CME") & (df["cme_speed_kms"] > 1000)]

# Geomagnetic storms with linked CMEs
storms = df[df["event_type"] == "GST"]
storms_with_cme = storms[storms["linked_events"].str.contains("CME", na=False)]

# CME speed distribution
import matplotlib.pyplot as plt
cmes = df[df["event_type"] == "CME"]
cmes["cme_speed_kms"].hist(bins=50)
plt.xlabel("CME Speed (km/s)")
plt.ylabel("Count")
plt.title("DONKI CME Speed Distribution")
plt.show()

# Event frequency by type and year
df["year"] = df["start_time"].dt.year
df.groupby(["year", "event_type"]).size().unstack().plot()
plt.title("DONKI Events by Type and Year")
plt.show()
```

## Data source

https://ccmc.gsfc.nasa.gov/tools/DONKI/

## Update schedule

Daily at 14:00 UTC via GitHub Actions

## Related datasets

- [juliensimon/solar-flare-events](https://huggingface.co/datasets/juliensimon/solar-flare-events)

- [juliensimon/space-weather-indices](https://huggingface.co/datasets/juliensimon/space-weather-indices)

- [juliensimon/dst-index](https://huggingface.co/datasets/juliensimon/dst-index)

- [juliensimon/neo-close-approaches](https://huggingface.co/datasets/juliensimon/neo-close-approaches)

> If you find this dataset useful, please consider [giving it a like](https://huggingface.co/datasets/juliensimon/donki-space-weather-events) on Hugging Face. It helps others discover it.

## About the author

Created by [Julien Simon](https://julien.org) — AI Operating Partner at Fortino Capital. Part of the [Space Datasets](https://julien.org/datasets) collection.

## Citation

```bibtex
@dataset{donki_space_weather_events,
  title = {NASA DONKI Space Weather Events},
  author = {juliensimon},
  year = {2026},
  url = {https://huggingface.co/datasets/juliensimon/donki-space-weather-events},
  publisher = {Hugging Face}
}
```

## License

[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/)
