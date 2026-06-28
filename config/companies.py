"""
Reclaimed-wood ecosystem: real Canadian companies.

This replaces the earlier synthetic actor placeholders with a real directory.
Two sources sit behind it (see docs/SOURCES.md, both dated):

  - Environment and Climate Change Canada (ECCC), "Companies working with
    reclaimed wood" directory (companion to the Circularity of Wood in
    Construction material-flow work), September 2024. The named companies below
    are transcribed from that directory.
  - Light House, "Market Research on SMEs involved in Recovery and Reintegration
    of CRD Wood," for ECCC, March 2026. This gives the national census the named
    list is a sample of: 252 confirmed SMEs, and the distributions used in
    NATIONAL_SME_* below.

The professor's June 2026 feedback asked for the demand side and the full
two-sided ecosystem (waste generators and the firms that recover, process,
remanufacture, retail, recycle, downcycle, and upcycle wood). Each company is
tagged on the circular value chain so the app can show that ecosystem.
"""

# Province centroids for the ecosystem map.
PROVINCE_CENTROID = {
    "AB": (53.93, -116.58), "BC": (53.73, -127.65), "MB": (53.76, -98.81),
    "NB": (46.57, -66.46), "NL": (53.14, -57.66), "NS": (44.68, -63.74),
    "ON": (50.00, -85.32), "PE": (46.51, -63.42), "QC": (52.94, -73.55),
    "SK": (52.94, -106.45), "CA": (56.13, -106.35),
}

# Each activity maps to a stage on the circular value chain.
ACTIVITY_STAGE = {
    "demolition": "Generate", "salvage": "Recover", "warehouse": "Recover",
    "processing": "Process", "recycling": "Process", "downcycling": "Process",
    "manufacturer": "Remake", "upcycling": "Remake",
    "retail": "Resell", "marketplace": "Resell",
}
VALUE_CHAIN = ["Generate", "Recover", "Process", "Remake", "Resell"]

# (name, province, [activities], website)  -- transcribed from the ECCC directory.
_COMPANIES = [
    ("Backroads Reclamation", "AB", ["salvage", "processing", "manufacturer", "retail"], ""),
    ("Urban Timber Co", "AB", ["salvage", "manufacturer", "processing"], ""),
    ("Rural Creative", "AB", ["upcycling", "manufacturer", "salvage"], ""),
    ("Lonestar Lumber", "AB", ["processing", "recycling", "downcycling", "salvage"], ""),
    ("Taitlin Studio", "AB", ["manufacturer"], ""),
    ("Wall Theory", "AB", ["retail", "marketplace", "salvage"], ""),
    ("Vema Deconstruction", "BC", ["demolition", "salvage", "upcycling", "retail"], ""),
    ("Urban Jacks", "BC", ["salvage", "processing", "manufacturer", "recycling"], "https://www.urbanjacks.ca"),
    ("Blue Planet Recycling", "BC", ["processing", "recycling", "downcycling"], ""),
    ("I Used to be a Pallet", "BC", ["upcycling", "manufacturer", "salvage"], ""),
    ("Structurecraft", "BC", ["manufacturer", "processing"], ""),
    ("Salvaged Vancouver", "BC", ["salvage", "processing", "retail"], ""),
    ("Hall it Up - Recycled Floors", "BC", ["processing", "manufacturer", "salvage"], ""),
    ("Syd's Demo & Salvage", "BC", ["demolition", "salvage", "recycling", "retail", "warehouse"], ""),
    ("Rewood", "BC", ["salvage", "manufacturer"], ""),
    ("First Growth Reclaimed Design", "BC", ["salvage", "upcycling", "manufacturer"], ""),
    ("A Light Studio", "BC", ["salvage", "manufacturer", "retail"], ""),
    ("Island Woodwork", "BC", ["manufacturer", "recycling"], ""),
    ("Maple Ridge New and Used", "BC", ["salvage", "demolition", "retail", "warehouse"], ""),
    ("The BarnHouse Company", "BC", ["manufacturer", "processing"], ""),
    ("The Den Authentic Barnwood", "MB", ["salvage", "retail"], ""),
    ("Halifax C&D Recycling (Goodwood)", "NS", ["recycling", "processing", "downcycling"], ""),
    ("Creative Urban Timber", "NS", ["manufacturer", "salvage"], ""),
    ("Timberhart Woodworks", "NS", ["salvage", "retail"], ""),
    ("Onslow Historic Lumber", "NS", ["salvage", "manufacturer"], ""),
    ("City Pallets", "ON", ["processing"], ""),
    ("Timbercraft", "ON", ["demolition", "salvage", "manufacturer", "retail"], ""),
    ("HD Threshing", "ON", ["manufacturer"], ""),
    ("Ouroboros Deconstruction", "ON", ["demolition", "salvage", "retail", "manufacturer"], ""),
    ("The WoodSource", "ON", ["processing", "retail", "salvage"], ""),
    ("Revival Flooring", "ON", ["salvage", "processing"], ""),
    ("Old Wood Salvage", "ON", ["salvage", "manufacturer"], ""),
    ("Re4m Design and Fabrication", "ON", ["manufacturer", "salvage"], ""),
    ("Forever Interiors", "ON", ["manufacturer", "retail"], ""),
    ("Lubo Design", "ON", ["manufacturer", "upcycling"], ""),
    ("Timeless Material Co", "ON", ["demolition", "salvage", "manufacturer"], ""),
    ("Barnboardstore", "ON", ["manufacturer"], ""),
    ("Junk Whisperer", "ON", ["upcycling", "manufacturer", "salvage"], ""),
    ("Tomlinson", "ON", ["recycling", "salvage", "processing", "downcycling"], ""),
    ("Logsend", "ON", ["upcycling", "manufacturer"], ""),
    ("The Woodshed Lumber", "ON", ["processing", "retail"], ""),
    ("Brothers Dressler", "ON", ["manufacturer", "salvage"], ""),
    ("Northern Wide Plank", "ON", ["manufacturer", "processing"], ""),
    ("Danzer Canada", "ON", ["processing", "manufacturer"], ""),
    ("Century Wood Products", "ON", ["manufacturer", "processing", "retail"], ""),
    ("Timberware Custom Cabinets", "ON", ["manufacturer"], ""),
    ("TRY Recycling", "ON", ["recycling", "processing"], ""),
    ("Biomass Recycle", "ON", ["recycling", "downcycling", "salvage"], ""),
    ("Robias Wood", "PE", ["manufacturer"], ""),
    ("Reclaimed PEI", "PE", ["manufacturer"], ""),
    ("Birdmouse", "PE", ["manufacturer", "upcycling"], ""),
    ("Veser Antique Woods", "QC", ["manufacturer", "processing"], ""),
    ("Mr. Barn Wood", "QC", ["manufacturer"], ""),
    ("Tafisa: Rewood", "QC", ["recycling", "processing", "manufacturer"], ""),
    ("MSL Fibre", "QC", ["recycling", "processing", "manufacturer"], ""),
    ("Timber Wood Innovations", "SK", ["manufacturer", "processing", "retail", "salvage"], ""),
    ("Last Mountain Timber", "SK", ["manufacturer", "processing", "salvage"], ""),
    ("Habitat for Humanity ReStore (network)", "CA", ["retail", "warehouse", "salvage", "demolition"], "https://www.habitat.ca/en/restore"),
]

# Technology / innovation entrants named in the June 2026 materials. These are
# the demand-side and processing-economics movers the feedback flagged.
_INNOVATORS = [
    ("Urban Machine", "CA", ["processing"], "Robotic de-nailing of reclaimed lumber (machine vision + robotics)."),
    ("All Bay Lumber", "CA", ["manufacturer"], "Dowel-laminated timber (DLT) from reclaimed boards."),
]

# National census from the Light House SME report (March 2026), n = 252 SMEs.
NATIONAL_SME_TOTAL = 252
NATIONAL_SME_BY_PROVINCE = {  # share of 252
    "ON": 0.37, "BC": 0.25, "QC": 0.16, "AB": 0.07, "NS": 0.04,
    "MB": 0.03, "SK": 0.03, "NB": 0.02, "PE": 0.02, "NL": 0.005,
}
NATIONAL_SME_BY_STEP = {  # entities active at each value-chain step (sums > total: integrated firms)
    "Generate": 32, "Recover": 31, "Process": 71, "Remake": 71, "Resell": 177,
}
RESTORE_COUNT = 102  # Habitat for Humanity ReStores, the dominant reuse-retail channel

# Real sector-capacity context for the ecosystem and gap analyses, from dated
# Canadian sources. (label, value, source with date)
SECTOR_CONTEXT = [
    ("Wood share of construction/renovation/demolition waste", "about 40%",
     "City of Vancouver; ECCC CRD wood workshop (Feb 2024)"),
    ("CRD wood available, Canada", "about 3.6 Mt per year",
     "FPInnovations Info Note 15 (Sep 2023)"),
    ("National construction and demolition diversion rate", "about 16%",
     "Greening Government; Canadian Architect (2023)"),
    ("Diversion achieved on deconstruction projects", "about 85%",
     "Canadian Architect, Reuse of Wood C&D Waste (2023)"),
    ("Federal C&D waste diversion target", "90%",
     "Government of Canada, Greening Government Strategy"),
    ("Habitat ReStores nationwide (reuse-retail)", "over 100",
     "Habitat for Humanity Canada (2026)"),
]


def list_companies():
    """Return the named company directory as a list of dicts with stages."""
    out = []
    for name, prov, acts, web in _COMPANIES:
        stages = sorted({ACTIVITY_STAGE[a] for a in acts}, key=VALUE_CHAIN.index)
        out.append({"name": name, "province": prov, "activities": acts,
                    "stages": stages, "website": web,
                    "lat": PROVINCE_CENTROID[prov][0], "lon": PROVINCE_CENTROID[prov][1]})
    return out


def innovators():
    return [{"name": n, "scope": s, "activities": a, "note": note}
            for n, s, a, note in _INNOVATORS]
