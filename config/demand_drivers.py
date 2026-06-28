"""
Demand drivers: what pulls reclaimed wood through the market.

The supply side of this app is detailed (per-CMA demolition, archetypes, a Monte
Carlo forecast). The demand side was thinner, so this module adds the sourced
demand structure that was missing: where demand sits by application and buyer
channel, the macro and policy forces that pull it, the certification mechanisms
specifiers respond to, the competitive substitute, and indicative pricing.

Every row is dated and sourced (see docs/SOURCES.md). Application shares come from
market-research firms that disagree firm-to-firm, so they are shown as ranges with
indicative midpoints, not point estimates. Policy and substitute figures are from
government, standards bodies, and trade-press primary reporting and are firmer.
"""

# Demand by application (global reclaimed lumber). Vendors disagree on the exact
# split, so each row carries a reconciled midpoint for charting and the observed
# range for the table. (application, mid_pct, range_str, note, source)
APPLICATION_MIX = [
    ("Furniture & millwork", 35, "31 to 41%", "Largest application by value.",
     "Grand View Research (2022); Precedence Research (2024); Market Research Future (2024)"),
    ("Flooring", 22, "about 22%", "Fastest-growing large segment, about US$22.5B by 2030 at 3.7%/yr.",
     "Global Industry Analysts via Research and Markets (2025)"),
    ("Paneling & siding", 18, "about 18 to 21%", "Feature walls and exterior cladding.",
     "Global Growth Insights (2025)"),
    ("Beams & boards", 15, "about 15 to 18%", "Structural-look timber and dimensional stock.",
     "Global Growth Insights (2025)"),
    ("Other", 10, "about 10 to 13%", "Crafts, landscaping, sets and specialty uses.",
     "Global Growth Insights (2025)"),
]

# End-use split (where the wood goes). (end_use, share_str, note, source)
END_USE = [
    ("Commercial (retail, hospitality, office)", "about 58% (2022)",
     "Largest end-use today.", "Grand View Research (2022)"),
    ("Residential", "fast-growing", "The faster-growing end-use going forward.",
     "Grand View Research (2022)"),
    ("Construction", "about a quarter (vendor split)", "New-build and renovation.",
     "Global Growth Insights (2025)"),
]

# Macro demand drivers: the large, fast-growing markets reclaimed wood sits inside.
# (driver, value, note, source)
MACRO_DRIVERS = [
    ("North American green buildings market", "about US$204B (2024), about US$377B by 2030",
     "Growing about 10.6% per year, well above general construction.",
     "Mordor Intelligence (2025)"),
    ("Wellness real estate market", "about US$584B (2024), about US$1.1T by 2029",
     "Biophilic and natural-material interiors are a core driver; WELL v2 now requires them.",
     "Global Wellness Institute, Build Well to Live Well (2025)"),
    ("Wellness building price premium", "10 to 25% residential, 4.4 to 7.7% commercial rent",
     "Why developers absorb a reclaimed-material premium: the building earns it back.",
     "Global Wellness Institute (2025)"),
    ("Canada within North America", "fastest-growing reclaimed-lumber market in the region",
     "Vendor read; treat as directional.", "Market Research Future (2024-2025)"),
]

# Policy and regulation that pulls demand for reused and low-carbon material in
# Canada. This is the structural demand engine the app was missing.
# (driver, jurisdiction, status, when, detail, source)
POLICY_DEMAND = [
    ("Standard on Embodied Carbon in Construction", "Federal procurement", "In force", "Dec 2022",
     "10% embodied-carbon cut on concrete for federal projects of $10M or more using over 100 m3.",
     "Treasury Board of Canada Secretariat (2022)"),
    ("Embodied-carbon standard expanded", "Federal procurement", "In force", "Sept 2025",
     "Adds structural steel and a mandatory whole-building life-cycle assessment.",
     "Treasury Board, Contracting Policy Notice 2025-6 (2025)"),
    ("Federal building embodied-carbon target", "Federal", "In force", "2024",
     "New federal buildings over 2,000 m2 must show a 30% cut, or the most achievable within a 2% cost premium.",
     "NRCan, Canada Green Buildings Strategy (2024)"),
    ("Toronto Green Standard v4", "Toronto", "In force, tightening", "2022 to 2028",
     "Embodied-carbon caps of 350 and 250 kg CO2e/m2; reused components count as zero upfront carbon; "
     "the top tier becomes mandatory for all new development by 2028.",
     "City of Toronto (2022)"),
    ("Building By-law embodied-carbon limits", "Vancouver", "In force", "Jan 2025",
     "Whole-building LCA showing a 10% cut, rising to 20% for 1 to 6 storey wood and mass-timber buildings.",
     "City of Vancouver; Carbon Leadership Forum BC (2025)"),
    ("National Building Code GHG objective", "National", "Direction-setting", "2025",
     "The 2025 code adds a greenhouse-gas-emissions objective, the precursor to embodied-carbon provisions.",
     "NRC Codes Canada (2025)"),
    ("Landfill Methane Regulations", "Federal", "Finalized", "Dec 2025",
     "Aim to cut landfill methane 50% below 2019 levels by 2030, which raises the value of diverting wood from landfill.",
     "Canada Gazette, SOR/2025-279 (2025)"),
    ("Zero Carbon Building Design Standard v4", "National (CaGBC)", "In force", "June 2024",
     "The leading Canadian green standard now scores embodied carbon, not only operations.",
     "Canada Green Building Council (2024)"),
    ("Mass timber to 18 storeys and wood-first", "Quebec", "In force", "2025",
     "Mass timber allowed to 18 storeys, and public projects must consider a wood solution first.",
     "Quebec MRNF; Regie du batiment du Quebec (2025)"),
]

# Certification mechanisms that make specifiers choose reclaimed wood.
# (lever, mechanism, source)
CERT_LEVERS = [
    ("LEED v4.1", "Reused materials count at 200% of their cost toward the Sourcing of Raw "
     "Materials credit, and salvaged materials can earn up to 5 points for building and material reuse.",
     "USGBC, LEED v4.1 Materials and Resources credits (current)"),
    ("Toronto Green Standard v4", "Reused and salvaged components count as zero upfront embodied carbon.",
     "City of Toronto (2022)"),
    ("Zero Carbon Building v4", "Requires projects to cut both operational and embodied carbon.",
     "Canada Green Building Council (2024)"),
]

# The competitive substitute. (label, value, note, source)
SUBSTITUTE = [
    ("Hardwood share of US hard-surface sales", "23.4% (2015) to 12.6% (2024)",
     "Real wood is ceding share to wood-look alternatives.", "Floor Covering News (2025)"),
    ("Industry naming vinyl the top threat", "69% of respondents (2024)",
     "The threat to real wood is wood-look LVT, not virgin lumber.", "Floor Covering News (2025)"),
    ("Where reclaimed sits", "premium-aesthetic niche",
     "Reclaimed holds a provenance and character position the look-alikes cannot copy.",
     "Floor Covering News (2025)"),
]

# Indicative pricing and willingness to pay. (item, value, note, source)
PRICE_POINTS = [
    ("Reclaimed flooring, raw material", "about US$10 to 20 per sq ft",
     "Against about US$3 to 7 per sq ft for new hardwood.",
     "Supplier estimates, Really Cheap Floors; Appalachian Woods (2025-2026)"),
    ("Processing uplift on raw timber", "about 2 to 10 times",
     "De-nailing and kiln-drying take raw stock from about US$1 to 5 per bf to US$10 to 15 processed.",
     "Trade sources, Moruxo; The Green Mission (2025-2026)"),
    ("Reclaimed and certified furniture", "about 15 to 30% retail premium",
     "End-buyers pay more for provenance and sustainability.", "IndexBox (2024-2025)"),
]
