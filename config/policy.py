"""
Municipal circular-construction policy signal, by CMA (addresses the problem
statement's third gap: "municipalities with ambitious circular goals but limited
operational capacity," and adds municipalities and policy to the ecosystem map).

Each metro carries a 0-3 policy-ambition score from documented, construction-
specific programs. Most Canadian municipalities have limited deconstruction or
embodied-carbon policy; Vancouver and Toronto lead. Scores are explicit and
sourced; where no construction-specific by-law is documented, the entry says so
rather than inventing one.

Federal backdrop for every metro: the Canada Green Buildings Strategy (2024)
commits to addressing embodied carbon in construction.
"""

# Cities with documented, construction-specific circular policy (override).
# (score, label, initiative, source-with-date)
LEADERS = {
    "Vancouver": (3, "Leading",
                  "Green Demolition By-law: pre-1950 houses must reuse/recycle 75% by weight "
                  "(90% for character houses) and pre-1910/heritage homes require deconstruction",
                  "City of Vancouver By-law 11023 (2014, expanded 2019)"),
    "Toronto": (3, "Leading",
                "Toronto Green Standard v4 embodied-carbon caps (350/250 kg CO2e/m2); reused "
                "components count as zero upfront carbon; circular-economy review underway",
                "City of Toronto, TGS v4 (2022, tightened 2025)"),
    "Victoria": (2, "Active",
                 "Provincial CleanBC waste plan plus regional C&D diversion; follows Vancouver's "
                 "deconstruction lead in the capital region",
                 "CleanBC (2022); Capital Regional District"),
    "Montreal": (2, "Active",
                 "Quebec circular-economy roadmap and construction/renovation/demolition (CRD) "
                 "diversion targets",
                 "RECYC-QUEBEC; Quebec circular-economy plan (2022)"),
    "Ottawa-Gatineau": (2, "Active",
                        "Ottawa Climate Change Master Plan and Solid Waste Master Plan with C&D "
                        "diversion goals",
                        "City of Ottawa Solid Waste Master Plan (2023)"),
}

# Province-level default where no city-specific construction by-law is documented.
PROVINCE_DEFAULT = {
    "BC": (2, "Active", "CleanBC waste plan and regional C&D diversion",
           "CleanBC (2022)"),
    "QC": (2, "Active", "Quebec circular-economy roadmap and CRD diversion",
           "RECYC-QUEBEC (2022)"),
    "ON": (1, "Emerging", "Provincial diversion framework and municipal climate plans; "
           "no local deconstruction by-law documented", "Ontario; municipal climate plans"),
    "AB": (1, "Emerging", "Municipal climate plans; no deconstruction by-law documented",
           "Municipal climate plans"),
    "MB": (1, "Emerging", "Municipal waste diversion; no deconstruction by-law documented",
           "Municipal waste plans"),
    "SK": (1, "Emerging", "Municipal waste diversion; no deconstruction by-law documented",
           "Municipal waste plans"),
    "NS": (1, "Emerging", "Provincial diversion leadership; no deconstruction by-law documented",
           "Nova Scotia Environment"),
    "NL": (1, "Emerging", "Municipal waste diversion; no deconstruction by-law documented",
           "Municipal waste plans"),
    "NB": (1, "Emerging", "Municipal waste diversion; no deconstruction by-law documented",
           "Municipal waste plans"),
    "PE": (1, "Emerging", "Municipal waste diversion; no deconstruction by-law documented",
           "Municipal waste plans"),
}

SCORE_LABEL = {3: "Leading", 2: "Active", 1: "Emerging", 0: "None documented"}


def policy_for(cma, province):
    """Return (score, label, initiative, source) for a CMA."""
    if cma in LEADERS:
        return LEADERS[cma]
    return PROVINCE_DEFAULT.get(
        province,
        (1, "Emerging", "Municipal waste plans; no construction-specific deconstruction "
         "by-law documented", "Municipal climate/waste plans"))
