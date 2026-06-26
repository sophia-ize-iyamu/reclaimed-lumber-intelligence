"""
Canonical schema (Step 2 of the architecture).

Every city names its data differently (Toronto's "PERMIT_TYPE" vs another
city's "application_category"). The canonical table forces all of them into one
agreed shape so everything downstream measures the same thing.

This module is deliberately small: it defines the schema and a validator. The
heavy normalization lives in ingest.py, which is where raw-source quirks belong.
"""

import pandas as pd

# The canonical demolition record. One row = one cohort-bucket of residential
# demolition activity for a CMA in a given year.
DEMOLITION_COLUMNS = [
    "cma",              # metropolitan area name (matches config/cmas.py)
    "year",             # calendar year of the permit / estimate
    "cohort",           # housing age cohort (pre1946 ... post2010)
    "archetype",        # mapped building archetype
    "permits",          # number of residential demolition permits (float, can be fractional after allocation)
    "source",           # provenance label, e.g. "Toronto Open Data" or "synthetic"
    "coverage_tier",    # high / medium / low  -> confidence
]

# The canonical ecosystem-actor record (Step 4 supply chain mapping).
ACTOR_COLUMNS = [
    "cma",
    "actor_type",       # demolition, deconstruction, processor, warehouse, reuse_buyer
    "name",
    "capacity_bf_yr",   # rough annual throughput capacity in board feet
    "lat",
    "lon",
    "source",
]


def empty_demolition_table():
    return pd.DataFrame(columns=DEMOLITION_COLUMNS)


def validate(df, columns, name="table"):
    """Raise if a frame is missing canonical columns; reorder to canonical order."""
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"{name} missing canonical columns: {missing}")
    return df[columns].copy()


def validate_demolitions(df):
    return validate(df, DEMOLITION_COLUMNS, "demolition table")


def validate_actors(df):
    return validate(df, ACTOR_COLUMNS, "actor table")
