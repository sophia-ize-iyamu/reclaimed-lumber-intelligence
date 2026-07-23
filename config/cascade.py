"""
Cascade comparison (demand-side strategy).

Two ways to order wood-reuse pathways, compared for this project:

  - Functional (material) cascade: rank by remaining functionality, highest
    structural use first, to keep carbon in material form as long as possible.
    Source: Canadian Wood Council, "Expanding Secondary Market Opportunities for
    Recovered CRD Wood" (prepared for Environment and Climate Change Canada),
    March 2026, section 1.1 (internal draft, not yet public).

  - Constraint cascade: rank by how constrained each pathway is, least-constrained
    first ("easy market -> hard market"), so the easiest, highest-leverage markets
    are unlocked first. Source: B. Pelech, "From Material Cascades to Constraint
    Cascades" (executive-summary draft), 10 July 2026 (internal note).

Both organizing documents are dated but not yet public, so they carry no public
link. Underlying public sources are linked where they exist. Scores below are a
reasoned synthesis of those two documents; anything not lifted directly is an
estimate and labelled as such in the app.
"""

# Every source used on the cascade page: (label, date, url). url = "" when the
# document is an internal draft that cannot be publicly linked yet.
SOURCES = {
    "cwc": ("Canadian Wood Council, Expanding Secondary Market Opportunities for "
            "Recovered CRD Wood (for ECCC), section 1.1", "March 2026", ""),
    "prof": ("B. Pelech, From Material Cascades to Constraint Cascades "
             "(executive-summary draft)", "10 Jul 2026", ""),
    "waste_hierarchy": (
        "ECCC, Reducing municipal solid waste (the waste hierarchy)", "2024",
        "https://www.canada.ca/en/environment-climate-change/services/managing-reducing-waste/"
        "municipal-solid/reducing.html"),
    "eccc_circularity": (
        "ECCC, Opportunities for circularity of wood in construction, renovation and "
        "demolition (workshop report)", "Feb 2024",
        "https://www.canada.ca/en/services/environment/conservation/sustainability/circular-economy/"
        "workshop-report-opportunities-circularity-wood-construction-renovation-demolition.html"),
    "statcan_demo": (
        "Statistics Canada, Boom goes the dynamite...and conversions", "Jun 2023",
        "https://www.statcan.gc.ca/o1/en/plus/3896-boom-goes-dynamiteand-conversions"),
}

# The functional (material) cascade, highest structural use first (CWC 1.1.2, 1.1.5).
FUNCTIONAL_CASCADE = [
    ("Primary structural", "Mass timber (CLT / NLT / DLT), glulam, structural framing, bridge timbers"),
    ("Secondary structural", "Smaller framing, blocking and bracing, agricultural / utility buildings"),
    ("Engineered panels", "OSB, particleboard, MDF"),
    ("Fibre / composite", "Wood-fibre insulation, pulp and paper, bio-composites"),
    ("Energy / biochar", "Energy recovery, biochar, compost"),
]

# Reuse pathways scored on both lenses. functional_rank: 1 = highest structural,
# 5 = energy (CWC hierarchy). ease: 1 = easiest to unlock, 5 = hardest (per the
# professor's constraint framing plus CWC barriers). premium_x: reclaimed value as
# a multiple of commodity value (CWC 1.1.3-1.1.4: architectural 3-10x). market_now:
# rough share of the market that exists today (0-1). years: years to scale. tier:
# "A" = legal today (non-structural), "B" = code-gated (structural).
# columns: pathway, functional_rank, ease, premium_x, market_now, years, tier
PATHWAYS = [
    ("Architectural finishes & millwork",       2, 1, 6.0, 0.70, 0, "A"),
    ("High-end furniture stock",                2, 1, 8.0, 0.55, 0, "A"),
    ("Solid-wood flooring & cladding",          2, 2, 4.0, 0.60, 1, "A"),
    ("Specialty / artisanal products",          2, 1, 10.0, 0.40, 0, "A"),
    ("Non-structural / secondary framing",      3, 2, 1.2, 0.40, 1, "A"),
    ("Engineered flooring / remanufactured",    3, 3, 2.0, 0.30, 3, "A"),
    ("Panels (resaw / remill to OSB, MDF)",     4, 3, 0.8, 0.30, 3, "A"),
    ("Structural reuse / mass-timber feedstock", 1, 5, 1.0, 0.10, 8, "B"),
    ("Fibre / pulp / insulation",               4, 2, 0.5, 0.40, 1, "A"),
    ("Energy recovery / biochar",               5, 1, 0.2, 0.80, 0, "A"),
]
PATHWAY_COLS = ["pathway", "functional_rank", "ease", "premium_x", "market_now", "years", "tier"]

# The professor's constraint / leverage table (10 Jul 2026): which constraint, if
# removed, unlocks the most recovery. ease: 1 easy .. 4 very hard. impact: 1 .. 4.
CONSTRAINT_LEVERS = [
    ("Better supply visibility", 1, 4),
    ("Better buyer matching",    1, 4),
    ("Regional warehousing",     2, 3),
    ("Mobile de-nailing",        2, 3),
    ("Digital inventory",        2, 3),
    ("AI grading assistance",    2, 3),
    ("Structural certification", 3, 4),
    ("National code reform",     4, 4),
]

# Reframed, prediction-first feedback loop (professor's note, 10 Jul 2026).
FEEDBACK_LOOP = ["Permit issued", "Supply predicted", "Demand notified", "Capacity organized",
                 "Equipment deployed", "Material recovered", "Products already spoken for"]

# Reclamation timeline: when each lever / market realistically comes online, and a
# short justification. years is "years from now". (item, years, note)
RECLAMATION_TIMELINE = [
    ("Architectural, furniture, flooring markets", 0,
     "Exist today; pay 3-10x commodity value; need almost no regulatory change (CWC 1.1.3-1.1.4)."),
    ("Supply visibility & buyer matching", 0,
     "The coordination layer this tool provides; software, not regulation (Pelech note)."),
    ("Regional warehousing & mobile processing", 2,
     "Capital and siting; medium difficulty (CWC logistics/storage)."),
    ("Digital inventory & AI grading assistance", 3,
     "Tooling and data build-out; medium difficulty (Pelech note)."),
    ("Structural re-grading & certification", 6,
     "Grading standards, engineer acceptance, liability, insurance; hard (CWC 3.3; Pelech note)."),
    ("National code reform for structural reuse", 10,
     "Code change and CSA standards; very hard, transformational (Pelech note)."),
]
