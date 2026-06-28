"""
The demand half of the reclaimed-wood ecosystem.

config/companies.py holds the supply half: the firms that generate, recover,
process, remake and resell wood. That left the ecosystem one-sided. This module
adds the buyers and channels that absorb reclaimed wood, the barriers that make
buyers default to new lumber, and the coordinators that connect the two sides.

Sourced and dated (see docs/SOURCES.md). Where a clean Canadian count was not
available (architects and designers), the figure is marked approximate.
"""

# Buyer-side and channel actors. kind groups them on the demand map.
# (name, kind, role, scale, source)
DEMAND_ACTORS = [
    ("Architects & interior designers", "Specifier",
     "Specify reclaimed wood into hospitality, retail and office interiors.",
     "Over 5,000 registered architects in Canada, plus interior designers (approximate).",
     "RAIC Vital Statistics; Interior Designers of Canada"),
    ("General contractors & homebuilders", "Builder",
     "Buy reclaimed where it is reliable, and default to new lumber where it is not.",
     "Sensitive to lead time and volume reliability.", "ECCC workshop report (2024)"),
    ("Habitat for Humanity ReStore", "Reuse retail",
     "The largest organized reseller of donated building materials in Canada.",
     "Over 100 stores, over 1 billion lbs diverted, about an $80M network.",
     "Habitat for Humanity Canada (2024); Retail-Insider (2022)"),
    ("Unbuilders & Heritage Lumber", "Reuse retail",
     "A deconstructor that channels salvaged structural wood into a reclaimed-lumber brokerage.",
     "99.2% single-family salvage rate, Vancouver's highest recorded.",
     "The Construction Source (2023)"),
    ("Furniture & millwork makers", "Maker",
     "The largest application for reclaimed wood by value.",
     "Furniture is about 31 to 41% of the market.",
     "Grand View Research; Market Research Future (2022-2025)"),
    ("Hospitality, retail & office fit-out", "Commercial",
     "Commercial fit-out is the largest end-use and a fast-growing one.",
     "Commercial is about 58% of end-use.", "Grand View Research (2022)"),
    ("Film, TV & set construction", "Niche",
     "Uses reclaimed wood for temporary sets and props.",
     "Qualitative; a small but visible channel.", "Industry sources (2024-2025)"),
    ("Mass-timber manufacturers", "Adjacent",
     "Buy new engineered feedstock, so a demand signal for wood but not for reclaimed today.",
     "5 Canadian CLT makers; the mass-timber market is targeted to reach $1.2B by 2030.",
     "Mass Timber Roadmap (2024); Wood Business (2024-2025)"),
]

# Material-exchange channels. These support the app's role: coordinate supply to
# buyers, rather than run a marketplace. (name, role, source)
EXCHANGES = [
    ("Building Material Exchange (BMEx)",
     "A free B2B material exchange run by Light House on the Rheaply platform across Vancouver "
     "Island, pairing an online marketplace with human matchmaking and a physical reuse hub.",
     "Light House; ConstructConnect (2024)"),
    ("Rheaply",
     "The marketplace software layer that Canadian regional exchanges run on. A coordinator "
     "builds on it rather than rebuilding a marketplace.", "Light House (2024)"),
    ("Informal channels (Kijiji, Facebook Marketplace)",
     "Hundreds of live building-material listings carry most peer-to-peer reuse, the unstructured "
     "slice that coordination could formalize.", "Kijiji Marketplaces (2025)"),
]

# Why buyers default to new lumber even when they want reclaimed.
# (barrier, detail, source)
DEMAND_BARRIERS = [
    ("No re-grading or certification path for structural reuse",
     "Salvaged lumber must be re-graded, and no Canadian code path exists for load-bearing reuse, "
     "so liability sits with the engineer of record.", "ECCC circularity-of-wood workshop (Feb 2024)"),
    ("Unknown service history and provenance",
     "Reused structural timber carries no documented load history, which blocks certification.",
     "Taylor and Francis, structural-timber reuse review (2025)"),
    ("Immature and fragmented supply chain",
     "Few established suppliers, so volume and lead time are unreliable.",
     "ECCC workshop report (2024)"),
    ("Processing cost",
     "De-nailing, metal-detecting and kiln-drying are labour-heavy and raise the price.",
     "Trade sources, Moruxo; The Green Mission (2025-2026)"),
    ("Supply unpredictability",
     "Buyers cannot commit to material they cannot see coming, the gap a forward signal closes.",
     "ECCC workshop report (2024)"),
]

# The coordinating layer that connects supply to demand. (org, role, source)
COORDINATORS = [
    ("Circular Construction Canada / Innovation Hub",
     "A national hub-and-spoke coordinator working to lift construction-waste diversion from "
     "about 16% toward 75 to 88%.", "Circular Economy Leadership Canada (2024)"),
    ("Light House",
     "A Vancouver nonprofit that runs BMEx and convenes building-material reuse, providing the "
     "human matchmaking layer between salvage supply and local buyers.", "Light House (2024)"),
]
