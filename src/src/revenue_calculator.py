# ================================
# src/revenue_calculator.py
# ================================
# This file takes cleaned encounter data and computes:
# - units (for time-based codes)
# - revenue per row
# - monthly rollups (by code + totals)

from __future__ import annotations

import numpy as np
import pandas as pd


# ================================
# Billing rates
# ================================
# NOTE: These rates come from the original analysis notebook.
# FY23 rates are lower than FY24/FY25 (rates increased).
# FY25 matches FY24 (no increase).

# FY23
RATES_FY23 = {
    # Psychotherapy (per encounter)
    "90832": 65.00,
    "90834": 100.00,
    "90837": 129.00,

    # Other per-encounter
    "H0001": 176.00,
    "H0006": 45.50,

    # Group vs individual rates (fake codes)
    "T1012": 47.50,     # individual
    "T1012G": 19.00,    # group

    # Time-based codes (15-min units)
    "H0004": 26.50,     # 15-min units
    "H0038": 24.00,     # individual, 15-min units
    "H0038G": 5.50,     # group, treated as per-encounter in this repo
}

# FY24
RATES_FY24 = {
    "90832": 71.50,
    "90834": 110.00,
    "90837": 142.00,

    "H0001": 194.00,
    "H0006": 50.50,

    "T1012": 52.50,
    "T1012G": 21.00,

    "H0004": 29.50,
    "H0038": 26.50,
    "H0038G": 6.50,
}

# FY25 matches FY24 - no increase in billing rates
RATES_FY25 = dict(RATES_FY24)

# Put all the rate tables in one place so we can select by fiscal year
RATE_TABLES = {
    "FY23": RATES_FY23,
    "FY24": RATES_FY24,
    "FY25": RATES_FY25,
}

# Codes billed in 15-minute increments using duration_min
# NOTE: H0038G is treated as "per encounter" in this simplified setup
TIME_BASED_CODES = {"H0038", "H0004"}


def get_rates(fiscal_year: str = "FY24") -> dict[str, float]:
    """Return the billing rates for FY23, FY24, or FY25."""
    # Basic input check so we don't silently pick the wrong thing
    if fiscal_year not in RATE_TABLES:
        raise ValueError(f"Unknown fiscal_year={fiscal_year}. Use one of: {sorted(RATE_TABLES.keys())}")
    return RATE_TABLES[fiscal_year]


def _month_start(date_series: pd.Series) -> pd.Series:
    """Convert dates into month-start timestamps (e.g., 2024-02-01)."""
    # This makes grouping by month easy/consistent
    return pd.to_datetime(date_series).dt.to_period("M").dt.to_timestamp()


def add_units(df: pd.DataFrame, time_based_codes: set[str] = TIME_BASED_CODES) -> pd.DataFrame:
    """
    Add a 'units' column.
    - Time-based codes: units = floor(duration_min / 15)
    - Per-encounter codes: units = 1
    """
    out = df.copy()

    # Make sure duration is numeric (bad values become NaN, then we fill with 0)
    out["duration_min"] = pd.to_numeric(out["duration_min"], errors="coerce").fillna(0)

    # Default: per encounter = 1 unit
    out["units"] = 1

    # For time-based codes, compute 15-min units
    is_time_based = out["cpt_code"].isin(time_based_codes)
    out.loc[is_time_based, "units"] = np.floor(out.loc[is_time_based, "duration_min"] / 15).astype(int)

    # Guardrail: units should never be negative
    out["units"] = out["units"].clip(lower=0)

    return out


def compute_revenue(
    df: pd.DataFrame,
    fiscal_year: str = "FY24",
    rates: dict[str, float] | None = None,
    time_based_codes: set[str] = TIME_BASED_CODES,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Compute revenue at the encounter level and return:
    1) encounter-level df with units + revenue columns
    2) monthly revenue by code
    3) monthly total revenue

    Required columns:
    - encounter_date
    - cpt_code
    - duration_min
    """
    # If rates aren't provided, pull them from the fiscal year
    if rates is None:
        rates = get_rates(fiscal_year)

    # Make sure the dataframe has what we need
    required_cols = {"encounter_date", "cpt_code", "duration_min"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    out = df.copy()

    # Parse dates + drop rows where the date is missing/bad
    out["encounter_date"] = pd.to_datetime(out["encounter_date"], errors="coerce")
    out = out.dropna(subset=["encounter_date"])

    # Add month column for grouping
    out["month"] = _month_start(out["encounter_date"])

    # Add units column (time-based vs per-encounter)
    out = add_units(out, time_based_codes=time_based_codes)

    # Map rates and compute revenue
    # If a code isn't found, rate becomes 0 so it doesn't crash
    out["rate"] = out["cpt_code"].map(rates).fillna(0.0)
    out["revenue"] = out["units"] * out["rate"]

    # Monthly by code (helps see service mix)
    monthly_by_code = (
        out.groupby(["month", "cpt_code"], as_index=False)
        .agg(
            encounters=("cpt_code", "size"),
            total_units=("units", "sum"),
            revenue=("revenue", "sum"),
        )
        .sort_values(["month", "cpt_code"])
    )

    # Monthly total (main trend line)
    monthly_total = (
        out.groupby("month", as_index=False)
        .agg(
            encounters=("cpt_code", "size"),
            total_units=("units", "sum"),
            revenue=("revenue", "sum"),
        )
        .sort_values("month")
    )

    return out, monthly_by_code, monthly_total
