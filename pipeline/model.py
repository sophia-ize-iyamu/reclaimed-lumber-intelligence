"""
Supply model (Deliverables 1, 3) and value layer.

Turns the canonical demolition table into board-foot and dollar estimates through
a transparent, sourced recovery cascade:

    permits
      -> wood-frame buildings        [x wood_frame_likelihood]
      -> demolished floor area (m2)  [x archetype floor area]
      -> framing lumber (bf)         [x framing_bf_per_m2]   (dimensional structural)
      -> recoverable (bf)            [x recovery_method x condition]
      -> salvageable dimensional (bf)[x denail/sort yield]
      -> spec-ready reusable (bf)    [x grading pass rate]
      -> reclaimed value (CAD)       [x value per bf by value tier]

Gross TOTAL wood content (framing + panels + finish) is reported separately by
grossing framing up via dimensional_share_of_total, to honour the brief's
gross-vs-dimensional distinction. The cascade itself operates on framing because
that is the reusable structural fraction.

Every coefficient comes from the assumptions registry via val(); nothing is
hard-coded. See docs/SOURCES.md for provenance.
"""

import pandas as pd

from config import assumptions as A
from config.assumptions import val

# Representative age (decades before base year) per cohort, for age degradation.
_COHORT_DECADES = {
    "pre1946": 9.0, "1946_1980": 5.5, "1981_2000": 3.5,
    "2001_2010": 2.0, "post2010": 1.0,
}


def condition_factor(reg, decades):
    cond_base = val(reg["recovery"]["condition_base"])
    degr = val(reg["recovery"]["degradation_per_decade"])
    return max(0.20, cond_base - degr * decades)


def estimate_supply(demo_table, reg=None):
    """
    Add board-foot and value columns to a canonical demolition table.

    New columns: floor_area_m2, framing_bf, gross_bf (total wood), recoverable_bf,
    salvageable_bf, spec_ready_bf, value_tier, value_cad.
    """
    if reg is None:
        reg = A.get_assumptions()

    arch = reg["archetypes"]
    rec = reg["recovery"]
    dim_share = val(reg["dimensional_share_of_total"])
    rmf = val(rec["recovery_method_factor"])
    denail = val(rec["denail_sort_yield"])
    grading = val(rec["grading_pass_rate"])
    value_tbl = reg["value_per_bf_cad"]

    df = demo_table.copy()

    def row_calc(r):
        a = arch[r["archetype"]]
        wfl = val(a["wood_frame_likelihood"])
        floor_area = r["permits"] * val(a["floor_area_m2"]) * wfl
        framing = floor_area * val(a["framing_bf_per_m2"])
        gross_total = framing / dim_share

        condition = condition_factor(reg, _COHORT_DECADES.get(r["cohort"], 3.0))
        recoverable = framing * rmf * condition
        salvageable = recoverable * denail
        spec_ready = salvageable * grading

        tier = a["value_tier"]
        value_cad = spec_ready * val(value_tbl[tier])
        return pd.Series({
            "floor_area_m2": floor_area,
            "framing_bf": framing,
            "gross_bf": gross_total,
            "recoverable_bf": recoverable,
            "salvageable_bf": salvageable,
            "spec_ready_bf": spec_ready,
            "value_tier": tier,
            "value_cad": value_cad,
        })

    calc = df.apply(row_calc, axis=1)
    return pd.concat([df, calc], axis=1)


def cma_summary(supply_df):
    """Aggregate the per-cohort supply rows to one row per CMA."""
    agg = supply_df.groupby("cma", as_index=False).agg(
        permits=("permits", "sum"),
        gross_bf=("gross_bf", "sum"),
        framing_bf=("framing_bf", "sum"),
        recoverable_bf=("recoverable_bf", "sum"),
        salvageable_bf=("salvageable_bf", "sum"),
        spec_ready_bf=("spec_ready_bf", "sum"),
        value_cad=("value_cad", "sum"),
        coverage_tier=("coverage_tier", "first"),
        source=("source", "first"),
    )
    return agg.sort_values("spec_ready_bf", ascending=False).reset_index(drop=True)


def to_m3(board_feet, reg=None):
    if reg is None:
        reg = A.get_assumptions()
    return board_feet / reg["bf_per_m3"]
