"""
Ecosystem mapping (Deliverable 4, expanded for the June 2026 feedback).

The earlier version generated synthetic actors. This version uses the real
reclaimed-wood ecosystem: a named company directory (ECCC, September 2024) and
the national SME census (Light House for ECCC, March 2026). It maps the full
circular value chain (generate, recover, process, remake, resell), ties the
ecosystem to each CMA through its province, and flags where supply outruns the
recovery and processing base.

This treats circularity as two-sided, as the feedback asked: the buildings that
generate waste wood, and the companies that recover, process, remanufacture,
retail, recycle, downcycle and upcycle it.
"""

from collections import Counter

import pandas as pd

from config import companies as C

# Live ecosystem feed. The named directory is a dated snapshot (ECCC, September
# 2024). The one public, changing number is the Habitat ReStore count, so the
# connector refreshes that with a graceful fallback to the cached census figure,
# mirroring how the Toronto permit connector works.
RESTORE_SOURCE = "https://www.habitat.ca/en/restore"


def refresh_restores(allow_network=True, timeout=8):
    """Return (restore_count, source_label, is_live). Falls back to cached."""
    if allow_network:
        try:
            import re
            import requests
            r = requests.get(RESTORE_SOURCE, timeout=timeout,
                             headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200:
                m = re.search(r"(\d{2,3})\s*(?:\+\s*)?ReStore", r.text)
                if m:
                    return int(m.group(1)), "Habitat Canada (live)", True
        except Exception:
            pass
    return C.RESTORE_COUNT, "Light House census (cached, March 2026)", False

# Each of the 25 CMAs sits in a province, which is how the named ecosystem and
# the national SME census attach to a market.
CMA_PROVINCE = {
    "Toronto": "ON", "Montreal": "QC", "Vancouver": "BC", "Ottawa-Gatineau": "ON",
    "Calgary": "AB", "Edmonton": "AB", "Quebec City": "QC", "Winnipeg": "MB",
    "Hamilton": "ON", "Kitchener-Cambridge-Waterloo": "ON", "London": "ON",
    "Halifax": "NS", "St. Catharines-Niagara": "ON", "Windsor": "ON", "Oshawa": "ON",
    "Victoria": "BC", "Saskatoon": "SK", "Regina": "SK", "Sherbrooke": "QC",
    "St. John's": "NL", "Kelowna": "BC", "Barrie": "ON", "Abbotsford-Mission": "BC",
    "Greater Sudbury": "ON", "Kingston": "ON",
}

# Stages that represent recovery and processing capacity (the infrastructure that
# turns demolition supply into reusable material).
INFRA_STAGES = {"Recover", "Process", "Remake"}


def company_table():
    """The named reclaimed-wood company directory as a DataFrame."""
    return pd.DataFrame(C.list_companies())


def stage_counts_named():
    """Count named-directory companies active at each value-chain stage."""
    counts = {s: 0 for s in C.VALUE_CHAIN}
    for comp in C.list_companies():
        for s in comp["stages"]:
            counts[s] += 1
    return counts


def stage_counts_national():
    """National SME census by value-chain step (Light House, March 2026)."""
    return dict(C.NATIONAL_SME_BY_STEP)


def activity_counts():
    """Companies by activity (recycling, downcycling, upcycling, etc.)."""
    c = Counter()
    for comp in C.list_companies():
        for a in comp["activities"]:
            c[a] += 1
    return pd.DataFrame(sorted(c.items(), key=lambda x: -x[1]), columns=["activity", "companies"])


def province_company_estimate():
    """
    Estimated reclaimed-wood SMEs per province, from the national census of 252
    scaled by the Light House provincial distribution. Used for gap analysis so
    the ecosystem size reflects the full census, not just the named sample.
    """
    return {p: round(C.NATIONAL_SME_TOTAL * share)
            for p, share in C.NATIONAL_SME_BY_PROVINCE.items()}


def gap_analysis(cma_summary_df):
    """
    Join each CMA's spec-ready supply to its province's reclaimed-wood ecosystem
    size, and flag where supply outruns the recovery and processing base.

    Returns one row per CMA: province, spec_ready_bf, province SME estimate,
    board feet of spec-ready supply per SME, and a plain-language gap flag.
    """
    import numpy as np

    prov_smes = province_company_estimate()
    df = cma_summary_df.loc[:, ["cma", "spec_ready_bf"]].copy()
    df["province"] = df["cma"].map(CMA_PROVINCE).fillna("")
    df["province_smes"] = df["province"].map(prov_smes).fillna(0).astype(int)
    # Coerce supply to numeric so a None or object-dtype cell cannot break the
    # arithmetic on any pandas build (the cloud and local versions differ).
    df["spec_ready_bf"] = pd.to_numeric(df["spec_ready_bf"], errors="coerce").fillna(0.0)

    smes = df["province_smes"].to_numpy()
    spec = df["spec_ready_bf"].to_numpy(dtype=float)
    safe_smes = np.where(smes == 0, 1, smes)
    df["bf_per_sme"] = np.where(smes > 0, spec / safe_smes, np.inf)

    def flag(sm, per):
        if sm <= 8:
            return "Thin ecosystem: few recovery/processing firms in-province"
        if per > 60_000:
            return "Under-served: high supply per firm"
        return "Workable base"

    df["gap_flag"] = [flag(int(sm), float(p)) for sm, p in zip(smes, df["bf_per_sme"].to_numpy())]
    cols = ["cma", "province", "spec_ready_bf", "province_smes", "bf_per_sme", "gap_flag"]
    return df.sort_values("spec_ready_bf", ascending=False).reset_index(drop=True)[cols]
