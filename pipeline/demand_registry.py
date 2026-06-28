"""
Demand registry: the buyer-side mirror of the project store.

pipeline/projects.py logs supply (specific demolition sites). This logs demand:
buyers posting standing wants (grade, volume, location, timeline, and the premium
they will pay). Matchmaking needs both sides. A teardown is only a real match when
a buyer wants that material, in that place, on that timeline.

Where no buyer has registered for a metro yet, predicted_demand() synthesizes
demand from the market model: national legal-today (Tier A) demand allocated to the
metro by population share and split across the largest applications, each tagged
with a grade preference. Predicted rows are labelled, so a match can run on
predicted pull before the registry fills, and the labels keep it honest.

Plain JSON store, same pattern as projects.py: zero infrastructure, swappable for a
database behind the same add/load interface.
"""

import json
import os

import pandas as pd

from config import cmas as cma_cfg
from config import demand

_STORE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "store", "demand.json")

# Buyer types, aligned to the demand-side ecosystem actors.
BUYER_TYPES = [
    "Specifier (architect/designer)", "Maker (furniture/millwork)", "Reuse retailer",
    "Commercial fit-out", "Builder / GC", "Mass-timber maker",
]

# Grade preference maps to the model's value tiers.
GRADE_LABEL = {"high": "feature / old-growth", "medium": "general dimensional",
               "low": "utility / structural-look"}

TIMELINES = ["within 3 months", "3 to 12 months", "ongoing"]

# Intake schema: the fields a buyer want needs to be matchable.
INTAKE_FIELDS = [
    ("buyer", "Buyer / organization"),
    ("buyer_type", "Buyer type"),
    ("cma", "Metro (CMA)"),
    ("grade_pref", "Grade wanted"),
    ("volume_bf", "Annual volume wanted (board feet)"),
    ("timeline", "Timeline"),
    ("max_premium_pct", "Max premium over virgin (%)"),
]

_TIER_RANK = {"high": 0, "medium": 1, "low": 2}


def _ensure_store():
    os.makedirs(os.path.dirname(_STORE_PATH), exist_ok=True)
    if not os.path.exists(_STORE_PATH):
        with open(_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)


def load_demand():
    _ensure_store()
    with open(_STORE_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _save(items):
    _ensure_store()
    with open(_STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)


def add_demand(want):
    """Persist a buyer want. Returns the stored record."""
    items = load_demand()
    rec = dict(want)
    rec["id"] = len(items) + 1
    rec["source"] = "registered"
    items.append(rec)
    _save(items)
    return rec


def demand_dataframe():
    """Registered buyer wants as a DataFrame for display."""
    items = load_demand()
    if not items:
        return pd.DataFrame()
    return pd.DataFrame([{
        "id": d.get("id"), "buyer": d.get("buyer"), "buyer_type": d.get("buyer_type"),
        "cma": d.get("cma"), "grade_pref": d.get("grade_pref"),
        "volume_bf": d.get("volume_bf"), "timeline": d.get("timeline"),
        "max_premium_pct": d.get("max_premium_pct"),
    } for d in items])


def clear_demand():
    _save([])


def predicted_demand(cma):
    """Synthesize predicted buyer wants for a metro from the market model.

    National Tier A (legal-today) demand is allocated to the metro by population
    share, then split across the largest applications, each tagged with a grade
    preference. Returns a list of want dicts labelled source='predicted'.
    """
    pop = {r["cma"]: r["population"] for r in cma_cfg.list_cmas()}
    total = sum(pop.values()) or 1
    share = pop.get(cma, 0) / total
    local = demand.tier_a_total() * share  # board feet per year, legal-today demand
    # (application label, buyer type, grade preference, share of local Tier A)
    split = [
        ("Furniture & millwork demand", "Maker (furniture/millwork)", "high", 0.30),
        ("Flooring & feature demand", "Specifier (architect/designer)", "high", 0.22),
        ("Commercial fit-out demand", "Commercial fit-out", "medium", 0.20),
        ("Cladding & landscaping demand", "Builder / GC", "low", 0.16),
        ("Residential renovation demand", "Reuse retailer", "medium", 0.12),
    ]
    out = []
    for label, btype, grade, frac in split:
        out.append({"buyer": f"Predicted {label}", "buyer_type": btype, "cma": cma,
                    "grade_pref": grade, "volume_bf": local * frac,
                    "timeline": "ongoing", "max_premium_pct": None, "source": "predicted"})
    return out


def buyer_matches(cma, site_grade, top=12):
    """Two-sided match: buyers wanting this grade in this metro.

    Combines registered wants for the metro with predicted demand, then ranks by
    grade fit (distance from the teardown's grade), with registered buyers ahead of
    predicted ones at equal fit. Returns a display DataFrame.
    """
    registered = [dict(d, source="registered") for d in load_demand() if d.get("cma") == cma]
    pool = registered + predicted_demand(cma)
    if not pool:
        return pd.DataFrame()
    site_rank = _TIER_RANK.get(site_grade, 1)
    rows = []
    for b in pool:
        fit = abs(_TIER_RANK.get(b.get("grade_pref", "medium"), 1) - site_rank)
        rows.append({
            "buyer": b.get("buyer"), "type": b.get("buyer_type"),
            "grade wanted": GRADE_LABEL.get(b.get("grade_pref", "medium"), b.get("grade_pref")),
            "annual want (bf)": b.get("volume_bf", 0.0),
            "timeline": b.get("timeline", "ongoing"), "source": b.get("source"),
            "_fit": fit, "_srank": 0 if b.get("source") == "registered" else 1,
        })
    df = pd.DataFrame(rows).sort_values(["_fit", "_srank"]).drop(columns=["_fit", "_srank"])
    return df.head(top)
