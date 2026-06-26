"""
Ecosystem actor map and gap analysis (Deliverable 4).

Maps the circular lumber supply chain (demolition contractors, deconstruction
specialists, processors, warehouses, reuse buyers) against the supply forecast,
then finds the gaps the brief cares about:

  - high supply but weak recovery / processing infrastructure
  - supply nodes with no visible downstream buyer
  - geographic whitespace in warehousing / storage capacity

Actors are synthetic placeholders generated from each CMA's scale. Their purpose
is to demonstrate the gap-analysis method; real actor directories slot in behind
the same canonical ACTOR_COLUMNS schema with no model change.
"""

import numpy as np
import pandas as pd

from config import cmas as cma_cfg
from pipeline import canonical

ACTOR_TYPES = ["demolition", "deconstruction", "processor", "warehouse", "reuse_buyer"]

# Expected actors per 100k population, by type, in today's nascent ecosystem.
# Demolition contractors are common; deconstruction specialists, salvage
# processors, and reuse warehousing are genuinely scarce. That scarcity is what
# creates the recovery bottleneck the brief describes, so it is modelled
# deliberately rather than smoothed away.
_DENSITY_PER_100K = {
    "demolition": 2.5,
    "deconstruction": 0.18,
    "processor": 0.15,
    "warehouse": 0.25,
    "reuse_buyer": 0.8,
}


def _seed_for(name):
    return abs(hash("actors:" + name)) % (2**31)


def build_actor_table():
    """Generate a synthetic ecosystem actor table for all 25 CMAs."""
    rows = []
    for rec in cma_cfg.list_cmas():
        rng = np.random.default_rng(_seed_for(rec["cma"]))
        per100k = rec["population"] / 100_000.0
        for atype in ACTOR_TYPES:
            expected = per100k * _DENSITY_PER_100K[atype]
            # Smaller / lower-coverage markets under-index on scarce infrastructure.
            if rec["coverage_tier"] == "low" and atype in ("deconstruction", "processor", "warehouse"):
                expected *= 0.5
            count = int(max(0, round(rng.poisson(max(0.05, expected)))))
            for i in range(count):
                jitter_lat = rng.normal(0, 0.05)
                jitter_lon = rng.normal(0, 0.05)
                rows.append({
                    "cma": rec["cma"],
                    "actor_type": atype,
                    "name": f"{rec['cma']} {atype} {i+1}",
                    # Annual reclaimed-lumber throughput per facility. Modest by
                    # design: reuse processing/storage is small-scale today.
                    "capacity_bf_yr": float(rng.integers(4_000, 30_000)),
                    "lat": rec["lat"] + jitter_lat,
                    "lon": rec["lon"] + jitter_lon,
                    "source": "synthetic",
                })
    df = pd.DataFrame(rows)
    return canonical.validate_actors(df)


def actor_counts(actor_table):
    """Pivot to one row per CMA with a column per actor type."""
    counts = (actor_table.groupby(["cma", "actor_type"]).size()
              .unstack(fill_value=0).reset_index())
    for t in ACTOR_TYPES:
        if t not in counts.columns:
            counts[t] = 0
    return counts


def processing_capacity(actor_table):
    """Annual processing + warehouse throughput capacity (bf/yr) per CMA."""
    cap = actor_table[actor_table["actor_type"].isin(["processor", "warehouse"])]
    return (cap.groupby("cma", as_index=False)["capacity_bf_yr"].sum()
            .rename(columns={"capacity_bf_yr": "processing_capacity_bf_yr"}))


def gap_analysis(cma_summary_df, actor_table):
    """
    Join supply against ecosystem capacity and flag the gaps.

    Returns one row per CMA with:
      spec_ready_bf            base-year spec-ready supply
      processing_capacity_bf_yr  processor + warehouse throughput
      capacity_ratio           capacity / supply (under 1.0 = under-capacity)
      has_buyers               any reuse_buyer present
      gap_flag                 plain-language headline gap
    """
    counts = actor_counts(actor_table)
    cap = processing_capacity(actor_table)

    df = cma_summary_df.merge(counts, on="cma", how="left").merge(cap, on="cma", how="left")
    df["processing_capacity_bf_yr"] = df["processing_capacity_bf_yr"].fillna(0.0)
    for t in ACTOR_TYPES:
        if t not in df.columns:
            df[t] = 0
        df[t] = df[t].fillna(0)

    df["capacity_ratio"] = df.apply(
        lambda r: (r["processing_capacity_bf_yr"] / r["recoverable_bf"])
        if r["recoverable_bf"] > 0 else 0.0, axis=1)
    df["has_buyers"] = df["reuse_buyer"] > 0

    def flag(r):
        if r["recoverable_bf"] <= 0:
            return "No modelled supply"
        if r["capacity_ratio"] < 0.25:
            return "Severe gap: supply far exceeds processing/storage"
        if r["capacity_ratio"] < 0.75:
            return "Under-capacity: processing/storage gap"
        if not r["has_buyers"]:
            return "No visible reuse buyer"
        if r["deconstruction"] == 0:
            return "No deconstruction specialist (recovery bottleneck)"
        return "Adequate"

    df["gap_flag"] = df.apply(flag, axis=1)
    cols = ["cma", "coverage_tier", "recoverable_bf", "spec_ready_bf",
            "processing_capacity_bf_yr", "capacity_ratio", "has_buyers",
            "deconstruction", "processor", "warehouse", "reuse_buyer", "gap_flag"]
    return df[cols].sort_values("recoverable_bf", ascending=False).reset_index(drop=True)
