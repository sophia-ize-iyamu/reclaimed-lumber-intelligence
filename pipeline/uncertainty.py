"""
Monte Carlo uncertainty and sensitivity (the defensibility engine).

The old confidence bands reflected only data coverage. That understated the real
uncertainty, which is dominated by the SIX recovery coefficients multiplied
together. This module propagates that properly:

  - Coefficient uncertainty (recovery method, condition, degradation, denailing,
    grading, framing content) is SHARED across all CMAs in each Monte Carlo
    draw, because these are national physical coefficients. Correlated error does
    not diversify away, so the national band stays honest.
  - Data-coverage uncertainty (the demolition COUNT) is idiosyncratic per CMA and
    is drawn independently, scaled by each CMA's coverage-tier band.

Outputs: P10 / P50 / P90 for spec-ready and recoverable lumber, per CMA and
nationally, plus a one-at-a-time tornado sensitivity on national spec-ready.
"""

import numpy as np
import pandas as pd

from config import assumptions as A
from config.assumptions import val, rng

# Representative building age (decades) used for condition sensitivity.
_REP_DECADES = 5.0


def _tri(rand, rec, size):
    """Triangular samples from a coefficient record; degenerate -> constant."""
    lo, pt, hi = rng(rec)
    if hi <= lo:
        return np.full(size, pt, dtype=float)
    pt = min(max(pt, lo), hi)
    return rand.triangular(lo, pt, hi, size=size)


def _condition(base, degr, decades=_REP_DECADES):
    return np.maximum(0.20, base - degr * decades)


def monte_carlo(summary_df, reg=None, n=4000, seed=42):
    """
    Returns (per_cma_df, national) where per_cma_df has p10/p50/p90 for
    spec_ready_bf and recoverable_bf, and national is a dict of the same.
    """
    if reg is None:
        reg = A.get_assumptions()
    rec = reg["recovery"]
    rand = np.random.default_rng(seed)

    # Point values the deterministic summary already used.
    rmf0 = val(rec["recovery_method_factor"])
    denail0 = val(rec["denail_sort_yield"])
    grading0 = val(rec["grading_pass_rate"])
    cbase0 = val(rec["condition_base"])
    degr0 = val(rec["degradation_per_decade"])
    cond0 = _condition(cbase0, degr0)

    # Shared coefficient draws (correlated across CMAs).
    rmf = _tri(rand, rec["recovery_method_factor"], n)
    denail = _tri(rand, rec["denail_sort_yield"], n)
    grading = _tri(rand, rec["grading_pass_rate"], n)
    cbase = _tri(rand, rec["condition_base"], n)
    degr = _tri(rand, rec["degradation_per_decade"], n)
    cond = _condition(cbase, degr)
    # Framing-content multiplier, proxied from the post-war archetype range.
    fr = reg["archetypes"]["sfd_postwar"]["framing_bf_per_m2"]
    flo, fpt, fhi = rng(fr)
    gross_mult = _tri(rand, {"low": flo / fpt, "value": 1.0, "high": fhi / fpt}, n)

    spec_coef = (rmf / rmf0) * (denail / denail0) * (grading / grading0) * (cond / cond0) * gross_mult
    recov_coef = (rmf / rmf0) * (cond / cond0) * gross_mult

    bands = reg["confidence_band"]
    rows = []
    nat_spec = np.zeros(n)
    nat_recov = np.zeros(n)
    for _, r in summary_df.iterrows():
        band = val(bands[r["coverage_tier"]])
        count_mult = rand.triangular(1 - band, 1.0, 1 + band, size=n)
        spec = r["spec_ready_bf"] * spec_coef * count_mult
        recov = r["recoverable_bf"] * recov_coef * count_mult
        nat_spec += spec
        nat_recov += recov
        rows.append({
            "cma": r["cma"], "coverage_tier": r["coverage_tier"],
            "spec_ready_p50": np.percentile(spec, 50),
            "spec_ready_p10": np.percentile(spec, 10),
            "spec_ready_p90": np.percentile(spec, 90),
            "recoverable_p50": np.percentile(recov, 50),
            "recoverable_p10": np.percentile(recov, 10),
            "recoverable_p90": np.percentile(recov, 90),
        })

    def pct(a):
        return {"p10": float(np.percentile(a, 10)), "p50": float(np.percentile(a, 50)),
                "p90": float(np.percentile(a, 90)), "mean": float(a.mean())}

    national = {"spec_ready": pct(nat_spec), "recoverable": pct(nat_recov)}
    return pd.DataFrame(rows), national


# --------------------------------------------------------------------------- #
# Tornado sensitivity on national spec-ready (one-at-a-time low/high)
# --------------------------------------------------------------------------- #
def tornado(summary_df, reg=None):
    """
    For each coefficient, swing it to its low and high (others at point) and
    measure the multiplicative effect on national spec-ready supply. Returns a
    DataFrame sorted by absolute swing, with the national point total.
    """
    if reg is None:
        reg = A.get_assumptions()
    rec = reg["recovery"]
    base = float(summary_df["spec_ready_bf"].sum())

    rmf0 = val(rec["recovery_method_factor"])
    denail0 = val(rec["denail_sort_yield"])
    grading0 = val(rec["grading_pass_rate"])
    cbase0 = val(rec["condition_base"])
    degr0 = val(rec["degradation_per_decade"])
    cond0 = _condition(cbase0, degr0)

    rows = []

    def add(label, lo_mult, hi_mult, lo_v, hi_v, unit):
        rows.append({"parameter": label,
                     "low_total": base * lo_mult, "high_total": base * hi_mult,
                     "low_value": lo_v, "high_value": hi_v, "unit": unit,
                     "swing": base * abs(hi_mult - lo_mult)})

    def ratios(record):
        lo, pt, hi = rng(record)
        return lo / pt, hi / pt, lo, hi

    for key, label in [("recovery_method_factor", "Recovery method factor"),
                       ("denail_sort_yield", "Denail / sort yield"),
                       ("grading_pass_rate", "Grading pass rate")]:
        lm, hm, lo, hi = ratios(rec[key])
        add(label, lm, hm, lo, hi, "fraction")

    # condition_base
    lo, pt, hi = rng(rec["condition_base"])
    add("Condition base",
        _condition(lo, degr0) / cond0, _condition(hi, degr0) / cond0, lo, hi, "fraction")
    # degradation_per_decade (higher degradation -> lower supply)
    lo, pt, hi = rng(rec["degradation_per_decade"])
    add("Degradation per decade",
        _condition(cbase0, hi) / cond0, _condition(cbase0, lo) / cond0, hi, lo, "fraction/decade")
    # framing content (post-war proxy)
    fr = reg["archetypes"]["sfd_postwar"]["framing_bf_per_m2"]
    lo, pt, hi = rng(fr)
    add("Framing lumber content", lo / pt, hi / pt, lo, hi, "bf/m2")

    df = pd.DataFrame(rows).sort_values("swing", ascending=False).reset_index(drop=True)
    df.attrs["base_total"] = base
    return df
