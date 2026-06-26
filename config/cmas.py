"""
CMA registry: Canada's 25 largest Census Metropolitan Areas.

Population and dwelling counts are real StatCan 2021 Census figures
(Table 98-10-0014). Housing-stock age distributions are real StatCan figures
(Table 98-10-0234) for the six largest CMAs; the rest use calibrated profiles
anchored to those real distributions. Demolition intensities are anchored to the
StatCan Building Permits Survey (national rate about 0.74 residential demolitions
per 1,000 dwellings per year, 2022), with real per-CMA figures for the six cities StatCan
publishes and regional estimates elsewhere. See docs/SOURCES.md.

Only Toronto is wired to a live open-data connector; coverage_tier records that.
"""

# Real StatCan 2021 period-of-construction distributions for the largest CMAs.
# Cohorts: pre1946, 1946_1980, 1981_2000, 2001_2010, post2010 (shares sum to about 1.0).
REAL_VINTAGE = {
    "Toronto":          {"pre1946": 0.086, "1946_1980": 0.339, "1981_2000": 0.256, "2001_2010": 0.164, "post2010": 0.155},
    "Montreal":         {"pre1946": 0.099, "1946_1980": 0.436, "1981_2000": 0.236, "2001_2010": 0.117, "post2010": 0.112},
    "Vancouver":        {"pre1946": 0.053, "1946_1980": 0.296, "1981_2000": 0.311, "2001_2010": 0.154, "post2010": 0.186},
    "Calgary":          {"pre1946": 0.022, "1946_1980": 0.306, "1981_2000": 0.266, "2001_2010": 0.206, "post2010": 0.201},
    "Edmonton":         {"pre1946": 0.023, "1946_1980": 0.358, "1981_2000": 0.223, "2001_2010": 0.185, "post2010": 0.211},
    "Ottawa-Gatineau":  {"pre1946": 0.069, "1946_1980": 0.353, "1981_2000": 0.277, "2001_2010": 0.149, "post2010": 0.151},
}

# Calibrated profiles for CMAs without an explicit real distribution, anchored to
# real StatCan patterns: old_east tracks Montreal, mature the Canada national mix,
# growth tracks Calgary and Edmonton, new_west tracks Vancouver.
VINTAGE_PROFILES = {
    "old_east": {"pre1946": 0.10, "1946_1980": 0.42, "1981_2000": 0.24, "2001_2010": 0.12, "post2010": 0.12},
    "mature":   {"pre1946": 0.096, "1946_1980": 0.385, "1981_2000": 0.253, "2001_2010": 0.133, "post2010": 0.133},
    "growth":   {"pre1946": 0.023, "1946_1980": 0.332, "1981_2000": 0.245, "2001_2010": 0.195, "post2010": 0.205},
    "new_west": {"pre1946": 0.053, "1946_1980": 0.296, "1981_2000": 0.311, "2001_2010": 0.154, "post2010": 0.186},
}

# (name, population, dwellings, lat, lon, vintage_profile, demolition_intensity, coverage_tier)
# population & dwellings: StatCan 2021 Census Table 98-10-0014 (total private dwellings).
# demolition_intensity: residential demolition permits per dwelling per year.
_CMA_ROWS = [
    ("Toronto",                      6202225, 2394205, 43.6532, -79.3832, "mature",   0.00060, "high"),
    ("Montreal",                     4291732, 1929263, 45.5019, -73.5674, "old_east", 0.00040, "medium"),
    ("Vancouver",                    2642825, 1104532, 49.2827, -123.1207, "new_west", 0.00131, "medium"),
    ("Ottawa-Gatineau",             1488307,  638013, 45.4215, -75.6972, "mature",   0.00022, "medium"),
    ("Calgary",                      1481806,  594513, 51.0447, -114.0719, "growth",  0.00090, "medium"),
    ("Edmonton",                     1418118,  589554, 53.5461, -113.4938, "growth",  0.00087, "medium"),
    ("Quebec City",                   839311,  411415, 46.8139, -71.2080, "old_east", 0.00035, "low"),
    ("Winnipeg",                      834678,  347144, 49.8951, -97.1384, "mature",   0.00050, "low"),
    ("Hamilton",                      785184,  320081, 43.2557, -79.8711, "old_east", 0.00070, "low"),
    ("Kitchener-Cambridge-Waterloo",  575847,  229809, 43.4516, -80.4925, "mature",   0.00065, "low"),
    ("London",                        543551,  235522, 42.9849, -81.2453, "mature",   0.00060, "low"),
    ("Halifax",                       465703,  211789, 44.6488, -63.5752, "old_east", 0.00060, "low"),
    ("St. Catharines-Niagara",        433604,  190878, 43.1594, -79.2469, "old_east", 0.00050, "low"),
    ("Windsor",                       422630,  174072, 42.3149, -83.0364, "old_east", 0.00055, "low"),
    ("Oshawa",                        415311,  153565, 43.8971, -78.8658, "mature",   0.00070, "low"),
    ("Victoria",                      397237,  186674, 48.4284, -123.3656, "mature",  0.00110, "low"),
    ("Saskatoon",                     317480,  134720, 52.1332, -106.6700, "growth",  0.00065, "low"),
    ("Regina",                        249217,  108120, 50.4452, -104.6189, "growth",  0.00060, "low"),
    ("Sherbrooke",                    227398,  113325, 45.4042, -71.8929, "old_east", 0.00035, "low"),
    ("St. John's",                    212579,   97429, 47.5615, -52.7126, "mature",   0.00045, "low"),
    ("Kelowna",                       222162,  102097, 49.8880, -119.4960, "new_west", 0.00120, "low"),
    ("Barrie",                        212856,   82649, 44.3894, -79.6903, "growth",   0.00075, "low"),
    ("Abbotsford-Mission",            195726,   70648, 49.0504, -122.3045, "new_west", 0.00095, "low"),
    ("Greater Sudbury",               170605,   78225, 46.4917, -80.9930, "mature",   0.00045, "low"),
    ("Kingston",                      172546,   80955, 44.2312, -76.4860, "old_east", 0.00055, "low"),
]


def vintage_for(name, profile):
    """Real StatCan distribution if available, else the calibrated profile."""
    if name in REAL_VINTAGE:
        return REAL_VINTAGE[name]
    return VINTAGE_PROFILES[profile]


def list_cmas():
    """Return the registry as a list of dicts with the resolved vintage mix."""
    out = []
    for name, pop, dw, lat, lon, profile, demo_int, tier in _CMA_ROWS:
        out.append({
            "cma": name,
            "population": pop,
            "dwellings": dw,
            "lat": lat,
            "lon": lon,
            "vintage_profile": profile,
            "vintage": vintage_for(name, profile),
            "vintage_is_real": name in REAL_VINTAGE,
            "demolition_intensity": demo_int,
            "coverage_tier": tier,
        })
    return out


def cma_names():
    return [r[0] for r in _CMA_ROWS]


def get_cma(name):
    for r in list_cmas():
        if r["cma"] == name:
            return r
    raise KeyError(name)
