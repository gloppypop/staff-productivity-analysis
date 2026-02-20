# src/kpi_metrics.py
# Basic KPI calculations + a few plots.
# Kept simple on purpose.

from __future__ import annotations

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# seaborn styling
sns.set_theme(style="whitegrid")


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

    # Drop rows with bad dates (shouldn't happen much after cleaning)
    df = df.dropna(subset=["encounter_date"])

    # Month bucket for grouping
    df["month"] = df["encounter_date"].dt.to_period("M").dt.to_timestamp()

    # Monthly totals
    monthly = (
        df.groupby("month", as_index=False)
        .agg(
            encounters=("revenue", "size"),
            client_hours=("duration_min", lambda x: x.sum() / 60.0),
            revenue=("revenue", "sum"),
        )
        .sort_values("month")
    )

    # Extra KPIs
    monthly["revenue_per_hour"] = monthly["revenue"] / monthly["client_hours"]
    monthly["revenue_per_encounter"] = monthly["revenue"] / monthly["encounters"]

    # Utilization rate (simple baseline)
    # Assumption: 160 working hours per month for a full-time baseline
    monthly["utilization_rate"] = monthly["client_hours"] / 160

    return monthly


def save_plots(
    monthly_kpis: pd.DataFrame,
    out_dir: str | Path = "outputs",
    revenue_goal: float | None = None,
    utilization_goal: float | None = None,
) -> None:
    """
    Saves plots into outputs/.
    Optional:
    - revenue_goal (float): horizontal goal line for revenue
    - utilization_goal (float): horizontal goal line for utilization
    """
    from matplotlib.ticker import FuncFormatter
    import matplotlib.dates as mdates

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = monthly_kpis.copy()

    currency_fmt = FuncFormatter(lambda x, pos: f"${x:,.0f}")
    month_locator = mdates.MonthLocator(interval=1)
    month_fmt = mdates.DateFormatter("%Y-%m")

    def prettify(ax, y_is_currency=False):
        # Force grid on
        ax.grid(True, which="major", linestyle="--", linewidth=0.6, alpha=0.5)
        ax.set_axisbelow(True)  # grid stays behind lines

        # Improve x-axis formatting
        ax.xaxis.set_major_locator(month_locator)
        ax.xaxis.set_major_formatter(month_fmt)
        ax.tick_params(axis="x", rotation=45)

        # Currency formatting
        if y_is_currency:
            ax.yaxis.set_major_formatter(currency_fmt)

    # 1) Revenue Trend
    fig, ax = plt.subplots()
    ax.plot(df["month"], df["revenue"], marker="o", linewidth=1.8)
    ax.set_title("Monthly Revenue")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue")
    prettify(ax, y_is_currency=True)

    if revenue_goal is not None:
        ax.axhline(
            revenue_goal,
            linestyle="--",
            linewidth=1.5,
            label="Revenue Goal",
        )
        ax.legend()

    fig.tight_layout()
    fig.savefig(out_dir / "revenue_trends.png", dpi=220)
    plt.close(fig)

    # 2) Client Hours
    fig, ax = plt.subplots()
    ax.plot(df["month"], df["client_hours"], marker="o", linewidth=1.8)
    ax.set_title("Monthly Client Hours")
    ax.set_xlabel("Month")
    ax.set_ylabel("Client Hours")
    prettify(ax)
    fig.tight_layout()
    fig.savefig(out_dir / "client_hours_trends.png", dpi=220)
    plt.close(fig)

    # 3) Utilization Rate
    fig, ax = plt.subplots()
    ax.plot(df["month"], df["utilization_rate"], marker="o", linewidth=1.8)
    ax.set_title("Utilization Rate")
    ax.set_xlabel("Month")
    ax.set_ylabel("Utilization (Client Hours / 160)")
    prettify(ax)

    if utilization_goal is not None:
        ax.axhline(
            utilization_goal,
            linestyle="--",
            linewidth=1.5,
            label="Utilization Goal",
        )
        ax.legend()

    fig.tight_layout()
    fig.savefig(out_dir / "utilization_rate.png", dpi=220)
    plt.close(fig)

    # 4) Encounter Volume
    fig, ax = plt.subplots()
    ax.plot(df["month"], df["encounters"], marker="o", linewidth=1.8)
    ax.set_title("Monthly Encounter Volume")
    ax.set_xlabel("Month")
    ax.set_ylabel("Encounters")
    prettify(ax)
    fig.tight_layout()
    fig.savefig(out_dir / "encounter_volume.png", dpi=220)
    plt.close(fig)