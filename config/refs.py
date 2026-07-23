"""
Curated citation registry for the app's superscript footnotes.

Every source is defined once here, with a label, a working URL, and a date, so a
page cites it by key and the footnote is always consistent, dated and linked. URLs
are link-checked; see tools/check_refs. Do not hand-edit a URL without re-checking.
"""

# key: (label, url, date)
REFS = {
    # --- Demolition and dwelling data ---
    "statcan_boom": (
        "Statistics Canada, Boom goes the dynamite and conversions (demolitions)",
        "https://www.statcan.gc.ca/o1/en/plus/3896-boom-goes-dynamiteand-conversions", "Jun 2023"),
    "statcan_demo_type": (
        "Statistics Canada, Building Permits: demolitions by structure type (Table 34-10-0285-01)",
        "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3410028501", "2022"),
    "statcan_vintage": (
        "Statistics Canada, dwellings by period of construction (Table 98-10-0234-01)",
        "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=9810023401", "2021 Census"),
    "statcan_pop": (
        "Statistics Canada, population and dwellings (Table 98-10-0014-01)",
        "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=9810001401", "2021 Census"),
    "toronto_permits": (
        "City of Toronto Open Data, Cleared Building Permits (live demolition feed)",
        "https://open.toronto.ca/dataset/building-permits-cleared-permits/", "2017-present"),
    "vancouver_permits": (
        "City of Vancouver Open Data, Issued building permits (live demolition feed)",
        "https://opendata.vancouver.ca/explore/dataset/issued-building-permits/", "2017-present"),
    # --- Wood content and recovery ---
    "mckeever94": (
        "McKeever & Phelps, wood used in new single-family houses (USDA Forest Products Lab)",
        "https://www.fpl.fs.usda.gov/documnts/pdf1994/mckee94a.pdf", "1994"),
    "falk13": (
        "Falk, single-family framing lumber per floor area (USDA Forest Products Lab)",
        "https://www.fpl.fs.usda.gov/documnts/pdf2013/fpl_2013_falk001.pdf", "2013"),
    "elling15": (
        "Elling & McKeever, wood products in Canadian residential construction (APA / USDA FS)",
        "https://research.fs.usda.gov/download/treesearch/53618.pdf", "2015"),
    "oregon_deq": (
        "Oregon DEQ, deconstruction and building material reuse (recovery rates)",
        "https://www.oregon.gov/deq/FilterDocs/DeconstructionReport.pdf", "2019"),
    "swst_grading": (
        "Arbelaez et al., lumber from deconstructed buildings, grade pass rate (Wood and Fiber Science)",
        "https://www.swst.org/wp/wp-content/uploads/2019/10/wfs2879.pdf", "2019"),
    "ijoist": (
        "APA / engineered-wood adoption in framing (I-joist overview)",
        "https://en.wikipedia.org/wiki/I-joist", "accessed 2026"),
    # --- Carbon ---
    "bergman13": (
        "USDA Forest Service, Bergman et al., life cycle of reclaimed lumber (FPL-RP-676)",
        "https://research.fs.usda.gov/download/treesearch/43547.pdf", "2013"),
    "athena": (
        "Athena Sustainable Materials Institute, cradle-to-gate LCA of Canadian softwood lumber",
        "https://www.athenasmi.org/", "2018"),
    # --- Value ---
    "reclaimed_price": (
        "Reclaimed lumber dealer price review (Green Mission)",
        "https://thegreenmissioninc.com/the-lumber-market-in-2026/", "2026"),
    "placemakers": (
        "PlaceMakers, old-growth reclaimed Douglas fir dimensional price",
        "https://placemakersinc.com/product/old-growth-doug-fir/", "2026"),
    # --- Policy ---
    "van_bylaw": (
        "City of Vancouver Green Demolition By-law (deconstruction and recycling), via REMI Network",
        "https://www.reminetwork.com/articles/vancouver-green-demolition-bylaw/", "2014, amended 2019"),
    "waste_hierarchy": (
        "Environment and Climate Change Canada, reducing municipal solid waste (waste hierarchy)",
        "https://www.canada.ca/en/environment-climate-change/services/managing-reducing-waste/"
        "municipal-solid/reducing.html", "2024"),
    "eccc_circularity": (
        "Environment and Climate Change Canada, circularity of wood in construction (workshop report)",
        "https://www.canada.ca/en/services/environment/conservation/sustainability/circular-economy/"
        "workshop-report-opportunities-circularity-wood-construction-renovation-demolition.html", "Feb 2024"),
    "calrecycle": (
        "CalRecycle, model deconstruction and reuse ordinance",
        "https://calrecycle.ca.gov/lgcentral/library/canddmodel/", "2022"),
    # --- Ecosystem and market ---
    "habitat_restore": (
        "Habitat for Humanity Canada, ReStore",
        "https://habitat.ca/en/restore", "2024"),
    "nrcan_woodframe": (
        "Natural Resources Canada, back to basics: building with wood",
        "https://natural-resources.canada.ca/stories/simply-science/back-basics-building-wood-asknrcan",
        "2026"),
    # --- Documents that are dated but not publicly linkable (internal drafts) ---
    "cwc_markets": (
        "Canadian Wood Council, Expanding Secondary Market Opportunities for Recovered CRD Wood "
        "(for ECCC; internal draft, not public)", "", "Mar 2026"),
    "prof_note": (
        "B. Pelech, From Material Cascades to Constraint Cascades (draft; internal note, not public)",
        "", "10 Jul 2026"),
}
