# Data sources and coefficient provenance

Every coefficient in `config/assumptions.py` and `config/cmas.py` traces to a
source below. Each entry lists the value used, the plausible low/high range fed
to the Monte Carlo uncertainty model, and the citation. Where a number is
reasoned rather than directly measured, it's flagged.

## Wood content (framing lumber per floor area)

| Parameter | Value | Low | High | Source |
|---|---|---|---|---|
| Framing lumber, post-war base | 79 bf/m2 | 75 | 86 | McKee & McKeever, "Wood products used in new single-family house construction: 1950-1992," Forest Products Journal 44(11/12), USDA FPL, 1994 |
| Framing lumber, pre-1946 | 85 bf/m2 | 75 | 100 | Reasoned uplift on McKee and Falk, Cramer & Evans, FPJ 62(7/8), FPL, 2012 (full-dimension solid-sawn members) |
| Framing lumber, 1981-2000 | 80 bf/m2 | 72 | 85 | McKee & McKeever, 1994 |
| Framing lumber, 2001 on | 70 bf/m2 | 60 | 80 | Reasoned downshift (engineered wood / OSB substitution); NAHB / Home Innovation new-construction mix |
| Dimensional share of total wood | 0.78 | 0.65 | 0.85 | McKee volume math; Oregon DEQ deconstruction (85% of salvage weight is softwood lumber) |

Sources:
- McKee & McKeever, FPL, 1994: https://www.fpl.fs.usda.gov/documnts/pdf1994/mckee94a.pdf
- Falk, Cramer & Evans, FPL, 2012: https://www.fpl.fs.usda.gov/documnts/pdf2013/fpl_2013_falk001.pdf
- Oregon DEQ, Deconstruction vs Demolition, 2019: https://www.oregon.gov/deq/FilterDocs/DeconstructionReport.pdf

## Floor area by era (single-detached)

| Era | Value (m2) | Low | High | Source |
|---|---|---|---|---|
| pre-1946 | 115 | 95 | 140 | MPAC Ontario, 2024 (<=1960 homes about 1,200 ft2) |
| 1946-1980 | 120 | 110 | 135 | MPAC Ontario, 2024 (1970s median 1,317 ft2) |
| 1981-2000 | 175 | 150 | 195 | MPAC Ontario, 2024 (1980s +44% over 1970s) |
| 2001 on | 205 | 170 | 240 | MPAC Ontario, 2024 (2020s median 2,383 ft2) |

MPAC: https://www.mpac.ca/en/News/PressRelease/spacioushomescompactcondosMPACdatarevealsshiftinghousingtrendsacrossOntario

## Recovery cascade

| Parameter | Value | Low | High | Source |
|---|---|---|---|---|
| recovery_method_factor, deconstruction | 0.55 | 0.40 | 0.75 | Oregon DEQ 2019 (27% of home weight salvaged, 37% best crews; structural-wood basis) |
| recovery_method_factor, mixed | 0.30 | 0.15 | 0.50 | Interpolated DEQ / Delta Institute |
| recovery_method_factor, demolition | 0.05 | 0.00 | 0.15 | Oregon DEQ (mechanical demo modelled at about 0% intact reuse); Bowyer/Falk national about 10-11% mostly recycle |
| denail_sort_yield | 0.70 | 0.55 | 0.85 | Inferred from Falk et al. FPL-RP-650, 2008 (deconstruction damage about one grade) |
| grading_pass_rate (>= No.2) | 0.55 | 0.35 | 0.70 | Falk et al. FPL-RP-650; Arbelaez et al., Wood & Fiber Science 51(4), 2019 |
| degradation_per_decade | 0.02 | 0.00 | 0.05 | Cavalli et al., Construction & Building Materials, 2016 (weak; aged sound wood shows little intrinsic strength loss; condition-driven) |
| condition_base | 0.85 | 0.70 | 0.95 | Engineering placeholder; Oregon DEQ found no age-salvage correlation |

Sources:
- Falk et al. FPL-RP-650, 2008: https://research.fs.usda.gov/download/treesearch/33418.pdf
- Arbelaez et al., 2019: https://www.swst.org/wp/wp-content/uploads/2019/10/wfs2879.pdf
- Cavalli et al., 2016: https://www.sciencedirect.com/science/article/abs/pii/S0950061816305335
- Delta Institute deconstruction: https://delta-institute.org/program-area/deconstruction/

## Demolition rates and housing stock

| Parameter | Value | Source |
|---|---|---|
| National residential demolition rate | 0.74 / 1,000 dwellings / yr (77% single-detached) | StatCan Building Permits Survey, "Boom goes the dynamite...and conversions," 2022 |
| Per-CMA demolition (2022, single-detached) | Toronto 1,138; Vancouver 1,451; Montreal 575; Calgary 389; Edmonton 393; Ottawa-Gatineau 100 | StatCan (same) |
| Wood-frame share, single-detached | 0.98 | NRCan ("over 90% of residential homes constructed in wood"); NBC Part 9 |
| Dwellings by period of construction | per-CMA real distributions | StatCan 2021 Census, Table 98-10-0234-01 |
| CMA population & private dwellings | per-CMA real counts | StatCan 2021 Census, Table 98-10-0014 |
| Toronto demolition permits | live, by year | Toronto Open Data, Cleared Building Permits (resource a96c0ba4-3026-402b-b09d-5b1268b8f810) |

Sources:
- StatCan demolition writeup: https://www.statcan.gc.ca/o1/en/plus/3896-boom-goes-dynamiteand-conversions
- StatCan 98-10-0234 (period of construction): https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=9810023401
- StatCan 98-10-0014 (population/dwellings): https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=9810001401
- NRCan wood construction: https://natural-resources.canada.ca/stories/simply-science/back-basics-building-wood-asknrcan
- Toronto Open Data: https://open.toronto.ca/dataset/building-permits-cleared-permits/

## Reclaimed lumber value (CAD per board foot, USD->CAD about 1.37)

| Tier | Value | Low | High | Source |
|---|---|---|---|---|
| low (common reclaimed 2x) | 3.70 | 3.30 | 4.80 | Aurora Mills price guide, 2023 |
| medium (resawn fir / small timber) | 4.80 | 4.10 | 5.65 | Aurora Mills; WoodWeb |
| high (old-growth beams) | 12.00 | 10.30 | 16.50 | WoodWeb antique Douglas fir beams |
| new softwood retail (reference) | 4.45 | 3.40 | 5.50 | NAHB framing composite; retail surveys |

## Policy lever (scenario)

| Scenario | Effect | Source |
|---|---|---|
| Mandatory deconstruction bylaw | recovery_method_factor 0.30 -> 0.70 (about 2.3x) | Oregon DEQ (Portland); Delta Institute; City of Vancouver deconstruction bylaw (best projects 95-99% salvage); ECCC/Delphi 2024 |

- Delphi/ECCC C&D waste diversion, 2024: https://delphi.ca/wp-content/uploads/2024/09/CD-Waste-Diversion-in-Canada-Exec-Summary-Report-Sep-2024.pdf
- Portland deconstruction ordinance (Oregon DEQ report above)

## Caveats

- US-anchored recovery and wood-content data applied to Canadian SPF-heavy stock;
  ranges widened to reflect species/era differences.
- `degradation_per_decade` is the weakest coefficient and is better understood as
  a condition/exposure factor than a calendar-age factor. Kept small with a wide
  low bound (0).
- Demolition figures outside Toronto are StatCan 2022 single-year, single-detached
  at CMA scale, grossed up to all-residential. Toronto alone is live by-year data.
- Reclaimed price comparison has a unit trap (reclaimed is full-dimension rough
  sawn; new is dressed). Value figures are indicative rather than transaction-grade.
