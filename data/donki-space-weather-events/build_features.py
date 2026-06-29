from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "data" / "donki-space-weather-events" / "donki_events.parquet"
OUT_DIR = ROOT / "data" / "clean-data"

CME_FEATURES = [
    "cme_speed_kms",
    "cme_half_angle_deg",
    "cme_latitude",
    "cme_longitude",
    "cme_type",
]


def build_storm_label_ids(df):
    """Return activity_ids linked to a GST via linked_events."""
    return set(
        df[df["event_type"] == "GST"]["linked_events"]
        .dropna()
        .str.split(r",\s*")
        .explode()
        .str.strip()
    )


def per_cme_table(df, caused_ids):
    cme = df[df["event_type"] == "CME"].copy()
    cme["leads_to_gst"] = cme["activity_id"].isin(caused_ids).astype(int)

    out = cme[["activity_id", "start_time"] + CME_FEATURES + ["leads_to_gst"]].copy()

    out["date"] = out["start_time"].dt.date
    out["year"] = out["start_time"].dt.year
    out["month"] = out["start_time"].dt.month

    # cme_longitude is ~14% null within CMEs; impute median and flag missingness.
    out["cme_longitude_missing"] = out["cme_longitude"].isna().astype(int)
    out["cme_longitude"] = out["cme_longitude"].fillna(out["cme_longitude"].median())

    # Drop the ~1% of CME rows still missing core physics columns.
    out = out.dropna(subset=["cme_speed_kms", "cme_half_angle_deg", "cme_latitude", "cme_type"])

    out = pd.get_dummies(out, columns=["cme_type"], prefix="type")
    return out


def per_day_table(df, caused_ids):
    """Aggregate all event types per day; storm label uses any-event-linked-to-GST."""
    d = df.copy()
    d["date"] = d["start_time"].dt.date
    d["is_cause"] = d["activity_id"].isin(caused_ids).astype(int)

    cme = d[d["event_type"] == "CME"]

    daily = pd.DataFrame(index=sorted(d["date"].unique()))
    daily.index.name = "date"

    g = cme.groupby("date")
    daily["cme_count"] = g.size()
    daily["cme_speed_max"] = g["cme_speed_kms"].max()
    daily["cme_speed_mean"] = g["cme_speed_kms"].mean()
    daily["cme_halfangle_max"] = g["cme_half_angle_deg"].max()
    # longitude closest to 0 = most Earth-directed
    daily["cme_longitude_absmin"] = g["cme_longitude"].apply(lambda s: s.abs().min())

    counts = d.groupby(["date", "event_type"]).size().unstack(fill_value=0)
    for col in ["IPS", "HSS", "SEP"]:
        daily[f"{col.lower()}_count"] = counts.get(col, 0)

    daily = daily.fillna({"cme_count": 0, "ips_count": 0, "hss_count": 0, "sep_count": 0})

    storm_days = d[d["is_cause"] == 1].groupby("date").size()
    daily["storm_day"] = daily.index.isin(storm_days.index).astype(int)

    return daily.reset_index()


if __name__ == "__main__":
    df = pd.read_parquet(INPUT)
    df["start_time"] = pd.to_datetime(df["start_time"], utc=True)
    caused = build_storm_label_ids(df)

    cme_tbl = per_cme_table(df, caused)
    cme_out = OUT_DIR / "donki-cme-features.parquet"
    cme_tbl.to_parquet(cme_out, index=False)
    print(f"per-CME : {cme_tbl.shape}  positives={cme_tbl['leads_to_gst'].sum()} "
          f"({cme_tbl['leads_to_gst'].mean() * 100:.1f}%)  -> {cme_out}")

    daily_tbl = per_day_table(df, caused)
    daily_out = OUT_DIR / "donki-daily-features.parquet"
    daily_tbl.to_parquet(daily_out, index=False)
    print(f"per-day : {daily_tbl.shape}  storm days={daily_tbl['storm_day'].sum()} "
          f"({daily_tbl['storm_day'].mean() * 100:.1f}%)  -> {daily_out}")
