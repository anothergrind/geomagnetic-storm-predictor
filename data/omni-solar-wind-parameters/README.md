---
license: cc-by-4.0
pretty_name: "OMNI Hourly Solar Wind Parameters"
language:
  - en
description: "Merged hourly near-Earth solar wind magnetic field, plasma, energetic particle parameters combined with geomagnetic and solar activity indices from NASA's OMNI dataset. The master bridge dataset for s"
task_categories:
  - tabular-regression
  - time-series-forecasting
tags:
  - space
  - solar-wind
  - imf
  - magnetic-field
  - space-weather
  - nasa
  - open-data
  - tabular-data
  - parquet
size_categories:
  - 100K<n<1M
configs:
  - config_name: default
    data_files:
      - split: train
        path: data/omni_solar_wind_parameters.parquet
    default: true
---

# OMNI Hourly Solar Wind Parameters


<div align="center">
  <img src="banner.jpg" alt="Aurora borealis blankets the Earth, seen from the ISS" width="400">
  <p><em>Credit: NASA</em></p>
</div>


*Part of a [dataset collection](https://huggingface.co/collections/juliensimon/space-weather-datasets-69c24cae98f1666f2101ca70) on Hugging Face.*

## Dataset description

Merged hourly near-Earth solar wind magnetic field, plasma, energetic particle parameters combined with geomagnetic and solar activity indices from NASA's OMNI dataset. The master bridge dataset for space weather analysis -- it time-aligns IMF, solar wind, and geomagnetic response in a single file.

The OMNI dataset from NASA's Goddard Space Flight Center merges solar wind observations from multiple spacecraft (IMP 8, ACE, Wind, DSCOVR, and others) into a single consistent hourly time series at Earth's bow shock nose. It combines interplanetary magnetic field (IMF) components, solar wind plasma parameters, energetic particle fluxes, and geomagnetic activity indices. Key parameter groups include IMF (field magnitude, Bx/By/Bz in GSE and GSM), solar wind plasma (proton density, temperature, bulk flow speed), derived quantities (flow pressure, plasma beta, electric field, Alfven and magnetosonic Mach numbers), geomagnetic indices (Kp, Dst, AE, AL, AU, ap, PC(N)), solar indices (F10.7, sunspot number), and energetic particles (proton fluxes at >1 to >60 MeV).

A key feature of the OMNI processing is the time-shifting of upstream spacecraft data to the Earth's bow shock nose. Observations from monitors at the L1 Lagrange point (ACE, Wind, DSCOVR -- roughly 1.5 million km upstream) are propagated to the bow shock using the measured solar wind speed, ensuring temporal alignment with the geomagnetic indices they drive.

The derived quantities encode important plasma physics. Plasma beta distinguishes magnetically dominated structures such as magnetic clouds (beta << 1) from the ambient solar wind (beta ~ 1). The Alfven Mach number characterizes how supersonic the flow is relative to the Alfven wave speed. The convective electric field (-V x B) quantifies magnetic flux transport toward the magnetopause and is a key input to empirical geomagnetic activity models.


This dataset is suitable for **tabular regression, time-series forecasting** tasks.

## Schema

| Column | Type | Description | Sample | Null % |
|--------|------|-------------|--------|--------|
| `datetime` | datetime64[us] | Observation timestamp (UTC, hourly cadence). OMNI data begins 1963 and is updated daily. | 1963-01-01 00:00:00 | 0.0% |
| `bartels_rotation_number` | float64 | Bartels solar rotation number: sequential count of 27-day rotation periods; used to align data with the solar rotation cycle. | 1771.0 | 0.9% |
| `b_magnitude_avg_nt` | float64 | Average IMF magnitude 1/N SUM \|B\| (nT); scalar average of field magnitude over the hour. | 4.5 | 23.0% |
| `b_magnitude_vector_nt` | float64 | Magnitude of the hourly-averaged field vector (nT); differs from b_magnitude_avg_nt when the field direction varies within the hour. | 3.4 | 23.0% |
| `b_lat_angle_gse_deg` | float64 | Latitude angle of the average IMF vector in GSE coordinates (degrees); +90 = northward, -90 = southward. | 3.4 | 23.0% |
| `b_lon_angle_gse_deg` | float64 | Longitude angle of the average IMF vector in GSE coordinates (degrees); 0 = sunward, 180 = anti-sunward. | 154.0 | 23.0% |
| `bx_gse_nt` | float64 | IMF Bx component in GSE/GSM coordinates (nT); positive sunward along the Sun-Earth line. Bx is identical in GSE and GSM. | -3.0 | 23.0% |
| `by_gse_nt` | float64 | IMF By component in GSE coordinates (nT); positive dawnward (opposite to Earth's orbital motion). | 1.5 | 23.0% |
| `bz_gse_nt` | float64 | IMF Bz component in GSE coordinates (nT); positive northward (perpendicular to ecliptic). | 0.2 | 23.0% |
| `by_gsm_nt` | float64 | IMF By component in GSM coordinates (nT); GSM rotates with Earth's dipole tilt, important for magnetospheric coupling. | 1.5 | 23.0% |
| `bz_gsm_nt` | float64 | IMF Bz component in GSM coordinates (nT); negative (southward) Bz drives magnetic reconnection and geomagnetic storms. | -0.2 | 23.0% |
| `sigma_b_magnitude_nt` | float64 | RMS standard deviation of \|B\| within the averaging hour (nT); measures IMF variability. | 0.7 | 26.0% |
| `sigma_b_vector_nt` | float64 | RMS standard deviation of the field vector magnitude within the hour (nT). | 3.1 | 23.0% |
| `sigma_bx_nt` | float64 | RMS standard deviation of Bx component, GSE (nT). | 1.4 | 23.1% |
| `sigma_by_nt` | float64 | RMS standard deviation of By component, GSE (nT). | 2.1 | 23.1% |
| `sigma_bz_nt` | float64 | RMS standard deviation of Bz component, GSE (nT). | 1.8 | 23.1% |
| `proton_temperature_k` | float64 | Solar wind proton temperature (K); typical range 10^4-5x10^5 K; elevated in fast streams, depressed in ICMEs. | 55488.0 | 29.7% |
| `proton_density_cm3` | float64 | Solar wind proton number density (cm^-3); typical 5-10 cm^-3 at 1 AU; spikes during CME sheaths. | 10.5 | 26.7% |
| `flow_speed_kms` | float64 | Solar wind bulk plasma speed (km/s); slow wind: 350-450 km/s, fast streams: 600-800 km/s. | 285.0 | 23.8% |
| `flow_lon_angle_deg` | float64 | Flow longitude angle in quasi-GSE coordinates (degrees); small departures from 180 deg indicate non-radial flow. | -2.5 | 29.4% |
| `flow_lat_angle_deg` | float64 | Flow latitude angle in GSE coordinates (degrees); small departures from 0 deg indicate north/south deflections. | 3.7 | 35.7% |
| `alpha_proton_ratio` | float64 | He2+/H+ number density ratio (Na/Np); typical 0.02-0.08; elevated in fast streams and CMEs. | 0.04 | 41.7% |
| `flow_pressure_npa` | float64 | Solar wind dynamic (ram) pressure 0.5*rho*v^2 (nPa); typical 1-10 nPa; high values compress the dayside magnetopause. | 1.71 | 26.7% |
| `sigma_t_k` | float64 | Intra-hour standard deviation of proton temperature (K); reflects solar wind variability within the averaging window. | 10200.0 | 30.4% |
| `sigma_n_cm3` | float64 | Intra-hour standard deviation of proton density (cm^-3). | 1.7 | 30.5% |
| `sigma_v_kms` | float64 | Intra-hour standard deviation of flow speed (km/s). | 10.0 | 29.5% |
| `sigma_phi_v_deg` | float64 | Intra-hour standard deviation of flow longitude angle (degrees). | 1.5 | 32.1% |
| `sigma_theta_v_deg` | float64 | Intra-hour standard deviation of flow latitude angle (degrees). | 1.3 | 38.2% |
| `sigma_alpha_proton_ratio` | float64 | Intra-hour standard deviation of the He2+/H+ density ratio. | 0.018 | 41.7% |
| `electric_field_mvpm` | float64 | Interplanetary electric field component -V x Bz (mV/m); negative (southward Bz) drives magnetospheric energy input; typical range -10 to +10 mV/m. | 0.06 | 28.0% |
| `plasma_beta` | float64 | Ratio of thermal pressure to magnetic pressure (nkT / B^2/8pi); beta < 1 = magnetically dominated, beta > 1 = thermally dominated. | 3.93 | 32.5% |
| `alfven_mach_number` | float64 | Solar wind speed divided by Alfven speed; typical ~8-10 at 1 AU; determines bow shock and magnetopause standoff. | 10.3 | 29.6% |
| `kp_index` | float64 | Planetary geomagnetic 3-hourly Kp index stored as integer x 10 (e.g. 27 = Kp 2.7); scale 0-90; Kp >= 50 = geomagnetic storm. | 7.0 | 0.9% |
| `sunspot_number` | float64 | International sunspot number (SILSO v2); tracks the 11-year solar cycle; range ~0-300. | 33.0 | 0.9% |
| `dst_index_nt` | float64 | Disturbance Storm Time ring-current index (nT); 0 = quiet; -30 to -50 nT = minor storm; < -100 nT = intense storm. | -6.0 | 0.9% |
| `ae_index_nt` | float64 | Auroral Electrojet AE index (nT) = AU - AL; measures substorm and auroral zone current intensity; 0-2000+ nT. | 119.0 | 6.3% |
| `proton_flux_gt1mev` | float64 | Energetic proton flux for particles > 1 MeV (1/cm^2 s sr); elevated during solar proton events (SPEs). | 415.56 | 58.3% |
| `proton_flux_gt2mev` | float64 | Energetic proton flux for particles > 2 MeV (1/cm^2 s sr). | 0.3 | 64.8% |
| `proton_flux_gt4mev` | float64 | Energetic proton flux for particles > 4 MeV (1/cm^2 s sr). | 0.29 | 64.8% |
| `proton_flux_gt10mev` | float64 | Energetic proton flux for particles > 10 MeV (1/cm^2 s sr); NOAA SPE threshold: 10 pfu at this energy. | 4.39 | 34.9% |
| `proton_flux_gt30mev` | float64 | Energetic proton flux for particles > 30 MeV (1/cm^2 s sr). | 1.51 | 34.9% |
| `proton_flux_gt60mev` | float64 | Energetic proton flux for particles > 60 MeV (1/cm^2 s sr). | 0.93 | 34.9% |
| `ap_index_nt` | float64 | Linear equivalent of Kp index (nT); 3-hourly; range 0-400 nT; ap >= 100 = major geomagnetic storm. | 3.0 | 0.9% |
| `f107_index_sfu` | float64 | Solar 10.7 cm radio flux index (SFU, 1 SFU = 10^-22 W/m^2/Hz); solar cycle range ~65-300 SFU; proxy for EUV output. | 77.0 | 1.0% |
| `pc_n_index` | float64 | Polar Cap (North) magnetic activity index from Thule/Qaanaaq magnetometer; tracks cross-polar-cap potential and substorm precursors. | 0.5 | 21.9% |
| `al_index_nt` | float64 | Auroral Electrojet lower (AL) index (nT); measures westward electrojet intensity; negative excursions indicate substorm onset. | -19.0 | 11.0% |
| `au_index_nt` | float64 | Auroral Electrojet upper (AU) index (nT); measures eastward electrojet intensity; AE = AU - AL. | -2.0 | 11.0% |
| `magnetosonic_mach_number` | float64 | Solar wind speed divided by the fast magnetosonic wave speed; determines bow shock geometry; typical ~6-8 at 1 AU. | 6.6 | 32.5% |

## Quick stats

- **561,024** hourly records (1963-01-01 to 2026-12-31)
- **48** parameters spanning IMF, solar wind, geomagnetic indices, and energetic particles
- Bz coverage: **77.0%**, flow speed: **76.2%**, Dst: **99.1%**
- Standard reference dataset for solar wind-magnetosphere coupling studies

## Usage

```python
from datasets import load_dataset

ds = load_dataset("juliensimon/omni-solar-wind-parameters", split="train")
df = ds.to_pandas()
```

```python
from datasets import load_dataset

ds = load_dataset("juliensimon/omni-solar-wind-parameters", split="train")
df = ds.to_pandas()

# Southward IMF (Bz < 0) and geomagnetic storms (Dst < -50)
storms = df[(df["bz_gsm_nt"] < -5) & (df["dst_index_nt"] < -50)]
print(f"Storm hours with strong southward IMF: {len(storms):,}")

# Solar wind speed distribution
print(df["flow_speed_kms"].describe())

# Plasma beta vs Alfven Mach number
import matplotlib.pyplot as plt
sub = df[["plasma_beta", "alfven_mach_number"]].dropna()
plt.scatter(sub["plasma_beta"], sub["alfven_mach_number"], s=0.1, alpha=0.1)
plt.xlabel("Plasma Beta")
plt.ylabel("Alfven Mach Number")
plt.xscale("log")
plt.yscale("log")
plt.title("OMNI: Plasma Beta vs Alfven Mach Number")
plt.show()
```

## Data source

https://omniweb.gsfc.nasa.gov/

## Related datasets

- [juliensimon/solar-wind](https://huggingface.co/datasets/juliensimon/solar-wind)

- [juliensimon/dst-index](https://huggingface.co/datasets/juliensimon/dst-index)

- [juliensimon/geomagnetic-kp-index](https://huggingface.co/datasets/juliensimon/geomagnetic-kp-index)

- [juliensimon/auroral-electrojet-index](https://huggingface.co/datasets/juliensimon/auroral-electrojet-index)

- [juliensimon/f107-solar-flux](https://huggingface.co/datasets/juliensimon/f107-solar-flux)

> If you find this dataset useful, please consider [giving it a like](https://huggingface.co/datasets/juliensimon/omni-solar-wind-parameters) on Hugging Face. It helps others discover it.

## About the author

Created by [Julien Simon](https://julien.org) — AI Operating Partner at Fortino Capital. Part of the [Space Datasets](https://julien.org/datasets) collection.

## Citation

```bibtex
@dataset{omni_solar_wind_parameters,
  title = {OMNI Hourly Solar Wind Parameters},
  author = {juliensimon},
  year = {2026},
  url = {https://huggingface.co/datasets/juliensimon/omni-solar-wind-parameters},
  publisher = {Hugging Face}
}
```

## License

[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/)
