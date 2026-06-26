"""
Ingest layer (Step 1) and void / coverage analysis.

Two jobs:
  1. Produce a canonical demolition table for all 25 CMAs.
       - Toronto pulls REAL demolition permits from Toronto Open Data (CKAN):
         it counts WORK = "Demolition" permits by year, drops the trailing
         incomplete years (the dataset holds "cleared" permits, so recent years
         lag), and takes a stable-window mean plus a real growth trend. Falls
         back to a cached real figure if the network is unavailable.
       - The other 24 CMAs are generated from real StatCan dwelling counts x
         each CMA's real/calibrated vintage mix x a sourced demolition intensity.
  2. Produce a void / coverage report: per CMA, what is real, what is modelled,
     and the resulting confidence tier.

Synthetic counts are deterministic (no random noise) so results are stable.
"""

import numpy as np
import pandas as pd

from config import cmas as cma_cfg
from config import assumptions as A
from config.assumptions import val
from pipeline import canonical

CKAN = "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action/datastore_search"
TORONTO_RESOURCE_ID = "a96c0ba4-3026-402b-b09d-5b1268b8f810"  # Cleared Building Permits since 2017

COHORTS = ["pre1946", "1946_1980", "1981_2000", "2001_2010", "post2010"]

# Cached real Toronto figures (stable window 2017-2022 mean from a prior live
# pull) used when the network is unavailable. Provenance stays honest.
TORONTO_CACHED = {"annual": 1277, "growth": 0.015,
                  "source": "Toronto Open Data (cached 2017-2022 mean)", "tier": "high"}


# --------------------------------------------------------------------------- #
# Source registry
# --------------------------------------------------------------------------- #
def source_registry():
    return pd.DataFrame([
        {"source": "Toronto Open Data - Cleared Building Permits", "type": "Demolition permits",
         "coverage": "Toronto", "status": "live connector (by-year), offline fallback",
         "license": "Open Government Licence - Toronto", "cadence": "daily"},
        {"source": "StatCan 98-10-0014 - Population & dwellings", "type": "Population / dwellings",
         "coverage": "All 25 CMAs", "status": "embedded (real)", "license": "StatCan Open Licence",
         "cadence": "5-year"},
        {"source": "StatCan 98-10-0234 - Dwellings by period of construction", "type": "Housing stock age",
         "coverage": "6 CMAs real, 19 calibrated", "status": "embedded (real for 6)",
         "license": "StatCan Open Licence", "cadence": "5-year"},
        {"source": "StatCan Building Permits Survey - demolitions 2022", "type": "Demolition rate",
         "coverage": "6 CMAs real, rest national rate", "status": "embedded",
         "license": "StatCan Open Licence", "cadence": "annual"},
        {"source": "Municipal demolition permit portals", "type": "Demolition permits",
         "coverage": "24 CMAs", "status": "not yet connected", "license": "varies", "cadence": "varies"},
        {"source": "Reuse / salvage directories", "type": "Ecosystem actors",
         "coverage": "All 25 CMAs", "status": "synthetic placeholder", "license": "n/a", "cadence": "n/a"},
    ])


# --------------------------------------------------------------------------- #
# Toronto live connector
# --------------------------------------------------------------------------- #
def _fetch_toronto_by_year(timeout=20, max_pages=4):
    """Return {year:int -> count} for WORK='Demolition', or None on failure."""
    try:
        import requests
    except Exception:
        return None
    try:
        counts = {}
        offset = 0
        for _ in range(max_pages):
            params = {"resource_id": TORONTO_RESOURCE_ID, "limit": 10000,
                      "offset": offset, "q": '{"WORK":"Demolition"}'}
            r = requests.get(CKAN, params=params, timeout=timeout)
            if r.status_code != 200:
                return None
            res = r.json().get("result", {})
            recs = res.get("records", [])
            if not recs:
                break
            for rec in recs:
                d = (rec.get("APPLICATION_DATE") or "")[:4]
                if d.isdigit():
                    counts[int(d)] = counts.get(int(d), 0) + 1
            offset += len(recs)
            if offset >= res.get("total", 0):
                break
        return counts or None
    except Exception:
        return None


def _stable_window(by_year):
    """
    From raw year counts, pick the stable window for a representative annual rate.

    The dataset holds "cleared" permits, and demolition permits take about 2-3 years to
    clear, so the most recent calendar years undercount. We drop the trailing 3
    years, then trim any remaining trailing years that are still incomplete
    (below 60% of the candidate peak), then keep the last 6 years above 40% of
    peak (excludes the early ramp-up). Return (annual_mean, growth_rate, window).
    """
    if not by_year:
        return None
    years = sorted(by_year)
    max_year = years[-1]
    candidate = [y for y in years if y <= max_year - 3]
    if len(candidate) < 2:
        candidate = years[:-1] or years
    peak = max(by_year[y] for y in candidate)
    # Trim incomplete trailing years (clearing lag leaves them well below peak).
    while len(candidate) > 2 and by_year[candidate[-1]] < 0.60 * peak:
        candidate.pop()
    window = [y for y in candidate if by_year[y] >= 0.40 * peak][-6:]
    if len(window) < 2:
        window = candidate[-6:]
    vals = np.array([by_year[y] for y in window], dtype=float)
    annual = float(vals.mean())
    xs = np.arange(len(window), dtype=float)
    slope = np.polyfit(xs, vals, 1)[0] if len(window) >= 2 else 0.0
    growth = float(np.clip(slope / annual, -0.03, 0.05)) if annual > 0 else 0.0
    return annual, growth, window


def toronto_demolitions(allow_network=True):
    """Return (annual_count, growth_rate, source_label, tier, by_year_or_None)."""
    if allow_network:
        by_year = _fetch_toronto_by_year()
        sw = _stable_window(by_year)
        if sw:
            annual, growth, window = sw
            label = f"Toronto Open Data (live, {window[0]}-{window[-1]} mean)"
            return annual, growth, label, "high", by_year
    c = TORONTO_CACHED
    return c["annual"], c["growth"], c["source"], c["tier"], None


# --------------------------------------------------------------------------- #
# Demolition table
# --------------------------------------------------------------------------- #
def build_demolition_table(base_year=None, allow_network=True):
    """Canonical demolition table for the base year across all 25 CMAs."""
    reg = A.get_assumptions()
    if base_year is None:
        base_year = val(reg["forecast"]["base_year"])

    tor_annual, _, tor_source, tor_tier, _ = toronto_demolitions(allow_network)

    rows = []
    for rec in cma_cfg.list_cmas():
        name = rec["cma"]
        vintage = rec["vintage"]
        if name == "Toronto":
            annual, source, tier = tor_annual, tor_source, tor_tier
        else:
            annual = rec["dwellings"] * rec["demolition_intensity"]
            source = "StatCan-derived (real dwellings x sourced rate)"
            tier = rec["coverage_tier"]

        for cohort in COHORTS:
            rows.append({
                "cma": name, "year": base_year, "cohort": cohort,
                "archetype": reg["cohort_to_archetype"][cohort],
                "permits": annual * vintage[cohort],
                "source": source, "coverage_tier": tier,
            })
    return canonical.validate_demolitions(pd.DataFrame(rows))


# --------------------------------------------------------------------------- #
# Void / coverage report
# --------------------------------------------------------------------------- #
def void_report(demo_table):
    """Per-CMA coverage summary: provenance, tier, band, and a gap note."""
    reg = A.get_assumptions()
    bands = reg["confidence_band"]
    gap_text = {
        "high": "Live machine-readable permit feed. Highest confidence.",
        "medium": "Real StatCan CMA demolition figure; cohort split modelled.",
        "low": "No machine-readable permit feed. Count inferred from dwellings x sourced rate.",
    }
    out = []
    for rec in cma_cfg.list_cmas():
        name = rec["cma"]
        sub = demo_table[demo_table["cma"] == name]
        tier = sub["coverage_tier"].iloc[0] if len(sub) else rec["coverage_tier"]
        source = sub["source"].iloc[0] if len(sub) else "modelled"
        out.append({
            "cma": name,
            "coverage_tier": tier,
            "source": source,
            "vintage_real": rec["vintage_is_real"],
            "confidence_band_pm": val(bands[tier]),
            "permit_feed": "yes" if tier == "high" else ("statcan" if tier == "medium" else "no"),
            "gap_note": gap_text[tier],
        })
    return pd.DataFrame(out)
