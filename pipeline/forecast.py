"""
Forecast (Deliverable 3): project recoverable supply over a 5-10 year horizon
with confidence bands.

The forecast is intentionally simple and defensible: base-year supply grown at a
per-year demolition growth rate, with a confidence band whose half-width comes
from each CMA's data coverage tier. The band is the quantitative expression of
the void analysis. A low-coverage city does not get a falsely precise number; it
gets a wide, honestly-labelled range.
"""

import pandas as pd

from config import assumptions as A
from config.assumptions import val


def project_supply(cma_summary_df, reg=None):
    """
    Given the per-CMA base-year summary, return a long-form forecast table:
    one row per (cma, year) with central / low / high estimates of each
    recovery tier in board feet.
    """
    if reg is None:
        reg = A.get_assumptions()

    base_year = val(reg["forecast"]["base_year"])
    growth = val(reg["forecast"]["demolition_growth_rate"])
    horizon = int(val(reg["forecast"]["horizon_years"]))
    bands = reg["confidence_band"]

    metrics = ["gross_bf", "recoverable_bf", "salvageable_bf", "spec_ready_bf", "value_cad"]
    rows = []
    for _, r in cma_summary_df.iterrows():
        band = val(bands[r["coverage_tier"]])
        for h in range(0, horizon + 1):
            year = base_year + h
            factor = (1.0 + growth) ** h
            row = {"cma": r["cma"], "year": year,
                   "coverage_tier": r["coverage_tier"], "band_pm": band}
            for m in metrics:
                central = r[m] * factor
                row[m] = central
                row[f"{m}_low"] = central * (1 - band)
                row[f"{m}_high"] = central * (1 + band)
            rows.append(row)
    return pd.DataFrame(rows)


def cumulative_horizon(forecast_df, metric="spec_ready_bf"):
    """
    Total board feet over the full forecast horizon per CMA (sum of yearly
    central estimates), with low/high cumulative bounds. Useful for ranking the
    multi-year opportunity rather than a single year.
    """
    g = forecast_df.groupby("cma", as_index=False).agg(
        central=(metric, "sum"),
        low=(f"{metric}_low", "sum"),
        high=(f"{metric}_high", "sum"),
        coverage_tier=("coverage_tier", "first"),
    )
    return g.sort_values("central", ascending=False).reset_index(drop=True)
