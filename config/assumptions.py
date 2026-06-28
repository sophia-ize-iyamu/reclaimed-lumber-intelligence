"""
Assumptions registry (sourced).

Every coefficient the model uses, in one place, each with a value, a plausible
low/high range (fed to the Monte Carlo uncertainty model), a unit, and a
citation. See docs/SOURCES.md for the full provenance and caveats.

The model never hard-codes a coefficient. It reads through val()/rng(), and the
dashboard can override any editable value at runtime. Ranges are what make the
confidence bands honest: they propagate coefficient uncertainty, not just data
coverage.

Key reconciliation note: the wood literature (McKeever & Phelps, FPL 1994)
measures FRAMING (dimensional) lumber per unit floor area directly. So
`framing_bf_per_m2` already is the structural dimensional lumber in the building.
The recovery cascade operates on that. `dimensional_share_of_total` is used only
to gross framing back up to a TOTAL wood-content headline (framing + panels +
finish), to satisfy the brief's gross-vs-dimensional distinction.
"""

import copy


def C(value, low, high, unit, source, url, basis, editable=True):
    """Construct a coefficient record."""
    return {"value": value, "low": low, "high": high, "unit": unit,
            "source": source, "url": url, "basis": basis, "editable": editable}


def val(x):
    """Read the point value of a coefficient record or a bare scalar."""
    return x["value"] if isinstance(x, dict) else x


def rng(x):
    """Read (low, point, high) for Monte Carlo. Bare scalars get a zero-width range."""
    if isinstance(x, dict):
        return x.get("low", x["value"]), x["value"], x.get("high", x["value"])
    return x, x, x


# --------------------------------------------------------------------------- #
# Building archetypes (physical parameters, sourced)
# --------------------------------------------------------------------------- #
# framing_bf_per_m2 : dimensional framing lumber per m2 of floor area
# floor_area_m2     : typical floor area of the archetype
# wood_frame_likelihood : probability the demolished building is light wood-frame
# value_tier        : reclaimed-market value class -> see VALUE_PER_BF_CAD
ARCHETYPES = {
    "sfd_prewar": {
        "label": "Single-family detached, pre-1946",
        "framing_bf_per_m2": C(85, 75, 100, "bf/m2", "Falk FPL 2013 + McKeever 1994",
                               "https://www.fpl.fs.usda.gov/documnts/pdf2013/fpl_2013_falk001.pdf",
                               "Older homes use heavier full-dimension solid-sawn members."),
        "floor_area_m2": C(115, 95, 140, "m2", "MPAC Ontario 2024",
                           "https://www.mpac.ca", "<=1960 single-detached about 1,200 ft2."),
        "wood_frame_likelihood": C(0.98, 0.95, 0.99, "fraction", "NRCan; NBC Part 9",
                                   "https://natural-resources.canada.ca/stories/simply-science/back-basics-building-wood-asknrcan",
                                   "Single-detached homes are almost entirely wood-frame."),
        "value_tier": "high",
    },
    "sfd_postwar": {
        "label": "Single-family detached, 1946-1980",
        "framing_bf_per_m2": C(79, 75, 86, "bf/m2", "McKeever & Phelps FPL 1994",
                               "https://www.fpl.fs.usda.gov/documnts/pdf1994/mckee94a.pdf",
                               "Measured 7.28-7.51 bf/ft2 of finished floor area."),
        "floor_area_m2": C(120, 110, 135, "m2", "MPAC Ontario 2024",
                           "https://www.mpac.ca", "1970s median 1,317 ft2."),
        "wood_frame_likelihood": C(0.98, 0.95, 0.99, "fraction", "NRCan; NBC Part 9",
                                   "https://natural-resources.canada.ca", "Stick-frame dominant."),
        "value_tier": "medium",
    },
    "sfd_modern": {
        "label": "Single-family detached, 1981-2000",
        "framing_bf_per_m2": C(80, 72, 85, "bf/m2", "McKeever & Phelps FPL 1994",
                               "https://www.fpl.fs.usda.gov/documnts/pdf1994/mckee94a.pdf",
                               "Lumber/ft2 roughly flat to 1990 before engineered substitution."),
        "floor_area_m2": C(175, 150, 195, "m2", "MPAC Ontario 2024",
                           "https://www.mpac.ca", "1980s about 44% above 1970s."),
        "wood_frame_likelihood": C(0.97, 0.93, 0.99, "fraction", "NRCan; NBC Part 9",
                                   "https://natural-resources.canada.ca", "Wood-frame dominant."),
        "value_tier": "medium",
    },
    "sfd_recent": {
        "label": "Single-family detached, 2001 and later",
        "framing_bf_per_m2": C(70, 60, 80, "bf/m2", "Reasoned; NAHB/Home Innovation mix",
                               "https://www.nahb.org",
                               "Engineered wood (I-joists, LVL, trusses) and OSB displace dimensional lumber."),
        "floor_area_m2": C(205, 170, 240, "m2", "MPAC Ontario 2024",
                           "https://www.mpac.ca", "2020s median 2,383 ft2."),
        "wood_frame_likelihood": C(0.95, 0.90, 0.99, "fraction", "NRCan; NBC Part 9",
                                   "https://natural-resources.canada.ca", "Wood-frame dominant."),
        "value_tier": "low",
    },
    "low_rise_multi": {
        "label": "Low-rise multi-unit",
        "framing_bf_per_m2": C(55, 45, 70, "bf/m2", "Reasoned (shared walls, more concrete/steel)",
                               "https://www.fpl.fs.usda.gov", "Lower wood intensity per floor area."),
        "floor_area_m2": C(520, 350, 800, "m2", "Reasoned", "https://www150.statcan.gc.ca",
                           "Building-level floor area for a low-rise multi."),
        "wood_frame_likelihood": C(0.80, 0.65, 0.90, "fraction", "BC Gov 2019; reasoned",
                                   "https://news.gov.bc.ca/releases/2019FLNR0033-000571",
                                   "Mix of wood-frame and concrete/steel; widest uncertainty."),
        "value_tier": "medium",
    },
}

# Maps each housing age cohort to the archetype its demolitions resemble.
COHORT_TO_ARCHETYPE = {
    "pre1946": "sfd_prewar",
    "1946_1980": "sfd_postwar",
    "1981_2000": "sfd_modern",
    "2001_2010": "sfd_recent",
    "post2010": "sfd_recent",
}

# Fraction of total wood content that is dimensional framing (framing -> total).
DIMENSIONAL_SHARE_OF_TOTAL = C(
    0.78, 0.65, 0.85, "fraction", "McKeever 1994 volume math; Oregon DEQ 2019",
    "https://www.oregon.gov/deq/FilterDocs/DeconstructionReport.pdf",
    "Used to gross framing lumber up to total wood content for the headline.",
    editable=False)

# --------------------------------------------------------------------------- #
# Recovery cascade (sourced): framing -> recoverable -> salvageable -> spec-ready
# --------------------------------------------------------------------------- #
RECOVERY = {
    "recovery_method_factor": C(
        0.30, 0.15, 0.50, "fraction", "Oregon DEQ 2019; Delta Institute",
        "https://www.oregon.gov/deq/FilterDocs/DeconstructionReport.pdf",
        "Blended (mixed-practice) share of structural wood recovered intact. "
        "Deconstruction about 0.55, mechanical demolition about 0.05."),
    "condition_base": C(
        0.85, 0.70, 0.95, "fraction", "Engineering placeholder; Oregon DEQ 2019",
        "https://www.oregon.gov/deq/FilterDocs/DeconstructionReport.pdf",
        "Baseline reusable-condition share before age degradation."),
    "degradation_per_decade": C(
        0.020, 0.000, 0.050, "fraction/decade", "Cavalli et al. 2016",
        "https://www.sciencedirect.com/science/article/abs/pii/S0950061816305335",
        "Weak: sound aged wood loses little intrinsic strength; condition-driven."),
    "denail_sort_yield": C(
        0.70, 0.55, 0.85, "fraction", "Falk FPL-RP-650 2008 (inferred)",
        "https://research.fs.usda.gov/download/treesearch/33418.pdf",
        "Yield surviving denailing, sorting and trimming to clean stock."),
    "grading_pass_rate": C(
        0.55, 0.35, 0.70, "fraction", "Falk FPL-RP-650; Arbelaez et al. 2019",
        "https://www.swst.org/wp/wp-content/uploads/2019/10/wfs2879.pdf",
        "Share of clean salvaged dimensional lumber passing >= No.2 structural regrade."),
}

# Recovery-method presets (override recovery_method_factor for a project or scenario).
METHOD_FACTOR = {"deconstruction": 0.70, "mixed": 0.30, "demolition": 0.05}

# --------------------------------------------------------------------------- #
# Forecast
# --------------------------------------------------------------------------- #
FORECAST = {
    "base_year": C(2026, 2026, 2026, "year", "Anchor", "", "Projection anchor year.",
                   editable=False),
    "demolition_growth_rate": C(
        0.020, -0.010, 0.050, "fraction/year", "StatCan Building Permits Survey",
        "https://www.statcan.gc.ca/o1/en/plus/3896-boom-goes-dynamiteand-conversions",
        "Default annual growth in residential demolition (infill redevelopment). "
        "Toronto derives a real trend from live data when available."),
    "horizon_years": C(10, 5, 15, "years", "Brief (5-10 yr)", "", "Forecast horizon."),
}

# --------------------------------------------------------------------------- #
# Confidence band half-width by data coverage tier. This now governs only the
# uncertainty on the demolition-COUNT input (data availability). Coefficient
# uncertainty is handled separately by the Monte Carlo model.
# --------------------------------------------------------------------------- #
CONFIDENCE_BAND = {
    "high":   C(0.10, 0.05, 0.15, "fraction", "Toronto Open Data (live by-year)",
                "https://open.toronto.ca/dataset/building-permits-cleared-permits/",
                "Live machine-readable permit feed; count well constrained."),
    "medium": C(0.25, 0.15, 0.35, "fraction", "StatCan CMA demolition 2022",
                "https://www.statcan.gc.ca/o1/en/plus/3896-boom-goes-dynamiteand-conversions",
                "Single-year StatCan CMA figure grossed to all-residential."),
    "low":    C(0.45, 0.30, 0.60, "fraction", "Inferred from housing stock",
                "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=9810023401",
                "No machine-readable permit feed; demolition count inferred."),
}

# --------------------------------------------------------------------------- #
# Reclaimed lumber value (CAD per board foot). USD to CAD about 1.37 (mid-2025/26).
# --------------------------------------------------------------------------- #
VALUE_PER_BF_CAD = {
    "low":    C(3.70, 3.30, 4.80, "CAD/bf", "Aurora Mills price guide 2023",
                "https://www.auroramills.com", "Common reclaimed 2x dimensional."),
    "medium": C(4.80, 4.10, 5.65, "CAD/bf", "Aurora Mills; WoodWeb",
                "https://www.woodweb.com", "Resawn fir, small timber."),
    "high":   C(12.00, 10.30, 16.50, "CAD/bf", "WoodWeb antique Douglas fir beams",
                "https://www.woodweb.com", "Old-growth large-section beams."),
}
NEW_LUMBER_CAD_PER_BF = C(4.45, 3.40, 5.50, "CAD/bf", "NAHB framing composite; retail",
                          "https://www.nahb.org", "New softwood retail reference.")

# --------------------------------------------------------------------------- #
# Scenarios (policy levers). Each can override recovery and growth parameters.
# --------------------------------------------------------------------------- #
SCENARIOS = {
    "baseline": {
        "label": "Baseline (mixed practice)",
        "overrides": {},
        "note": "Current mixed demolition/deconstruction practice.",
    },
    "mandatory_deconstruction": {
        "label": "Mandatory deconstruction bylaw",
        "overrides": {("recovery", "recovery_method_factor"): 0.70},
        "note": "Pre-war and older homes must be deconstructed. Recovery climbs from "
                "about 0.30 to 0.70 (Portland and Vancouver bylaw evidence; about 2.3x uplift).",
    },
    "high_redevelopment": {
        "label": "High redevelopment pressure",
        "overrides": {("forecast", "demolition_growth_rate"): 0.045},
        "note": "Sustained infill boom lifts demolition growth to about 4.5%/yr.",
    },
    "downturn": {
        "label": "Construction downturn",
        "overrides": {("forecast", "demolition_growth_rate"): -0.010},
        "note": "Demolition activity declines about 1%/yr.",
    },
}

# Board feet to cubic metres (nominal lumber). 1 m3 is about 424 board feet.
BF_PER_M3 = 424.0


def get_assumptions():
    """Return a fresh, mutable copy of the full registry."""
    return {
        "archetypes": copy.deepcopy(ARCHETYPES),
        "cohort_to_archetype": dict(COHORT_TO_ARCHETYPE),
        "dimensional_share_of_total": copy.deepcopy(DIMENSIONAL_SHARE_OF_TOTAL),
        "recovery": copy.deepcopy(RECOVERY),
        "method_factor": dict(METHOD_FACTOR),
        "forecast": copy.deepcopy(FORECAST),
        "confidence_band": copy.deepcopy(CONFIDENCE_BAND),
        "value_per_bf_cad": copy.deepcopy(VALUE_PER_BF_CAD),
        "new_lumber_cad_per_bf": copy.deepcopy(NEW_LUMBER_CAD_PER_BF),
        "scenarios": copy.deepcopy(SCENARIOS),
        "bf_per_m3": BF_PER_M3,
    }


def apply_scenario(reg, scenario_key):
    """Apply a scenario's parameter overrides onto a registry in place; return it."""
    sc = reg["scenarios"].get(scenario_key)
    if not sc:
        return reg
    for (group, key), v in sc["overrides"].items():
        if isinstance(reg[group][key], dict):
            reg[group][key]["value"] = v
        else:
            reg[group][key] = v
    return reg


def flat_editable_rows(reg):
    """Yield (group, key, meta) for every editable scalar coefficient, for the UI."""
    for group in ("recovery", "forecast", "confidence_band"):
        for key, meta in reg[group].items():
            if isinstance(meta, dict) and meta.get("editable", True):
                yield group, key, meta
