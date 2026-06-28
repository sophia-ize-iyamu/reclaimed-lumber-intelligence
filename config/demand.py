"""
Demand side and economics.

The June 2026 feedback was that the supply side is solid and the project now
needs the demand side, the economics, and a clear answer to one question: if
recoverable wood exists, why isn't it reclaimed, and is the binding constraint
demand or supply?

This module holds the demand segments, the economics, and the ranked bottleneck
diagnosis. Figures are order-of-magnitude planning estimates drawn from the
June 2026 research set (Light House SME report March 2026; the project's own
bottom-up demand build; ECCC and municipal material-flow analyses). They are
ranges on purpose. See docs/SOURCES.md for provenance and dates.

All volumes are board feet per year.
"""

M = 1_000_000

# Demand segments. tier "A" is legal today (non-structural / aesthetic); tier "B"
# needs a building-code change to allow structural reuse. code_gated flags B.
# (segment, tier, low_bf, point_bf, high_bf, code_gated, note)
DEMAND_SEGMENTS = [
    ("Hospitality & restaurant fit-out", "A", 3.0, 3.5, 4.0, False, "Feature walls, bars, tables."),
    ("Residential feature & renovation", "A", 3.0, 3.5, 4.0, False, "Accent walls, mantels, built-ins."),
    ("Retail fit-out & display", "A", 2.5, 2.75, 3.0, False, "Fixtures, millwork, displays."),
    ("Office / commercial tenant improvement", "A", 2.0, 2.5, 3.0, False, "Interiors and finishes."),
    ("Furniture & millwork", "A", 2.0, 2.5, 3.0, False, "Tables, casework, cabinetry."),
    ("Flooring", "A", 2.0, 2.5, 3.0, False, "Reclaimed plank and engineered."),
    ("Cladding & siding", "A", 1.0, 1.5, 2.0, False, "Interior and exterior cladding."),
    ("Landscaping & public realm", "A", 1.0, 1.5, 2.0, False, "Decking, planters, structures."),
    ("Film, TV & events", "A", 0.5, 0.75, 1.0, False, "Sets and temporary builds."),
    ("Acoustic & architectural panels", "A", 0.5, 0.75, 1.0, False, "Finger-jointed and panel stock."),
    ("Crafts & artisan", "A", 0.3, 0.4, 0.5, False, "Small-batch makers."),
    ("Residential structural framing reuse", "B", 30.0, 45.0, 70.0, True, "Needs code path for structural reuse."),
    ("Mass timber / NLT / DLT feedstock", "B", 10.0, 18.0, 30.0, True, "Engineered wood from reclaimed boards."),
    ("Industrial / dunnage / non-spec structural", "B", 10.0, 15.0, 20.0, True, "Pallets, blocking, temporary works."),
    ("Modular / panelized / ADU", "B", 5.0, 10.0, 15.0, True, "Off-site construction."),
]

# Economics. Each is (label, low, point, high, unit, basis).
ECONOMICS = {
    "reclaimed_premium": (0.20, 0.35, 0.50, "fraction over virgin",
                          "Reclaimed dimensional and feature lumber commands 20-50% over virgin "
                          "in aesthetic applications (Light House SME report, March 2026)."),
    "deconstruction_premium": (0.17, 0.21, 0.25, "fraction over demolition",
                               "Full deconstruction of a wood-frame house costs ~17-25% more than "
                               "mechanical demolition (Light House / Delta Institute)."),
    "metro_van_salvage_value": (342 * M, 342 * M, 342 * M, "CAD/yr, raw salvage value, Metro Vancouver",
                                "Vancouver Economic Commission, Unbuilders & BCIT, Business Case for "
                                "Deconstruction, July 2020."),
}

# The ranked diagnosis: why recoverable wood is not reclaimed. side = where the
# constraint binds. The order is the project's read of severity.
BOTTLENECKS = [
    {"rank": 1, "name": "Structural-reuse code wall", "side": "Demand (rules)",
     "note": "Salvaged lumber must be re-graded; no code provisions for structural reuse in "
             "Canadian provinces, so the liability sits with the engineer of record. This caps "
             "the largest demand tier (structural) before economics even enter."},
    {"rank": 2, "name": "No forward supply signal", "side": "Coordination",
     "note": "Buyers discover supply only after demolition begins, so latent demand cannot "
             "commit to material it cannot see. This is the gap this app targets."},
    {"rank": 3, "name": "Processing / de-nailing labour cost", "side": "Supply",
     "note": "De-nailing, sorting, metal-detecting and drying are labour-intensive, which "
             "erodes the price advantage over virgin lumber."},
    {"rank": 4, "name": "Deconstruction vs demolition cost gap", "side": "Supply",
     "note": "Deconstruction costs ~17-25% more and takes days rather than hours, so recovery "
             "loses to the excavator unless a buyer or policy closes the gap."},
    {"rank": 5, "name": "Storage, logistics & standards", "side": "Supply",
     "note": "Lumpy, unpredictable supply needs storage and grading infrastructure that barely "
             "exists, so material is downcycled or landfilled before it can be matched."},
]

# The project's framing funnel (illustrative, national, board feet per year).
# Flagged as plausible but not yet tied to a single published source.
FRAMING_FUNNEL = {
    "generated": 100 * M, "recoverable": 27 * M, "spec_ready": 10 * M,
    "moving_today": 30 * M,
}


def demand_table():
    """Demand segments as a list of dicts in board feet."""
    out = []
    for seg, tier, lo, pt, hi, gated, note in DEMAND_SEGMENTS:
        out.append({"segment": seg, "tier": tier, "low_bf": lo * M, "point_bf": pt * M,
                    "high_bf": hi * M, "code_gated": gated, "note": note})
    return out


def tier_a_total():
    """Point-estimate demand that is legal today (board feet/yr)."""
    return sum(s["point_bf"] for s in demand_table() if s["tier"] == "A")


def tier_b_total():
    """Point-estimate demand that needs a code change (board feet/yr)."""
    return sum(s["point_bf"] for s in demand_table() if s["tier"] == "B")
