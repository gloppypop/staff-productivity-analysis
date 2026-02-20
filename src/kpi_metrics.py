# src/kpi_metrics.py
# Basic KPI calculations + a couple plots.
# Nothing fancy — just clean and readable.

from __future__ import annotations

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def compute_monthly_kpis(encounters_with_revenue: pd.DataFrame) -> pd.DataFrame:
    """
    Input: encounter-level dataframe that includes:
    - encounter_date
    - duration_min
    - revenue
    Output: monthly KPI table.
    """
    df = encounters_with_revenue.copy()

    # Make sure types are right
    df["encounter_date"] = pd.to_datetime(df["encounter_date"], errors="coerce")
    df["duration_min"] = pd.to_numeric(df["duration_min"], errors="coerce")

    df = df.dropna(subset=["encounter_date"])
    df["month"] = df["encounter_date"].dt.to_period("M").dt.to_timestamp()

    monthly = (
        df.groupby("month", as_index=False)
        .agg(
            encounters=("revenue", "size"),
            client_hours=("duration_min", lambda x: x.sum() / 60.0),
            revenue=("revenue", "sum"),
        )
        .sort_values("month")
    )

    # Simple extra metrics
    monthly["revenue_per_hour"] = monthly["revenue"] / monthly["client_hours"]
    monthly["revenue_per_encounter"] = monthly["revenue"] / monthly["encounters"]

    return monthly


def save_plots(monthly_kpis: pd.DataFrame, out_dir: str | Path = "outputs") -> None:
    """
    Saves a few plots to outputs/.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = monthly_kpis.copy()

    # 1) Revenue trend
    plt.figure()
    plt.plot(df["month"], df["revenue"], marker="o")
    plt.title("Monthly Revenue")
    plt.xlabel("Month")
    plt.ylabel("Revenue")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(out_dir / "revenue_trends.png", dpi=200)
    plt.close()

    # 2) Client hours trend
    plt.figure()
    plt.plot(df["month"], df["client_hours"], marker="o")
    plt.title("Monthly Client Hours")
    plt.xlabel("Month")
    plt.ylabel("Client Hours")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(out_dir / "client_hours_trends.png", dpi=200)
    plt.close()

    # 3) Revenue per hour
    plt.figure()
    plt.plot(df["month"], df["revenue_per_hour"], marker="o")
    plt.title("Revenue per Client Hour")
    plt.xlabel("Month")
    plt.ylabel("Revenue / Hour")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(out_dir / "revenue_per_hour.png", dpi=200)
    plt.close()