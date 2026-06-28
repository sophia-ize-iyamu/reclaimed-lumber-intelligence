# Data sources and coefficient provenance

Every coefficient in `config/` traces to a source below. Each row gives the
value, the source, a publication date (month and year, day where known), a
working URL, and notes. Links were web-verified in June 2026. Source PDFs that
are freely shareable are bundled in `docs/sources/`.

Corrections from the June 2026 source review are listed at the end.

## Supply coefficients (wood content, recovery, grading)

| Item | Value | Source | Date | URL | Notes |
|---|---|---|---|---|---|
| Framing lumber per floor area (post-war base) | 79 bf/m2 | McKeever & Phelps, "Wood products used in new single-family house construction," USDA Forest Products Lab | 1994 | https://www.fpl.fs.usda.gov/documnts/pdf1994/mckee94a.pdf | Newer series: McKeever & Elling 2015, https://research.fs.usda.gov/download/treesearch/48690.pdf |
| Framing lumber, pre-1946 uplift | 85 bf/m2 (75-100) | Falk, Cramer & Evans, "Framing lumber from building removal," Forest Products Journal 62(7/8), USDA FPL | 2013 | https://www.fpl.fs.usda.gov/documnts/pdf2013/fpl_2013_falk001.pdf | Landing: https://research.fs.usda.gov/treesearch/45113 |
| Dimensional share of total wood | 0.78 (0.65-0.85) | McKeever volume math; Oregon DEQ deconstruction study | 1994 / Mar 2019 | https://www.oregon.gov/deq/FilterDocs/DeconstructionReport.pdf | |
| Floor area by era | 115-205 m2 | MPAC Ontario press release | Dec 5, 2024 | https://www.mpac.ca/en/News/PressRelease/spacioushomescompactcondosMPACdatarevealsshiftinghousingtrendsacrossOntario | |
| recovery_method_factor (decon 0.55 / mixed 0.30 / demo 0.05) | fractions | Oregon DEQ, "Deconstruction vs Demolition" (Nunes, Palmeri & Love) | Mar 2019 | https://www.oregon.gov/deq/FilterDocs/DeconstructionReport.pdf | |
| denail_sort_yield | 0.70 (0.55-0.85) | Falk et al., FPL-RP-650, "Engineering properties of Douglas-fir lumber reclaimed from deconstructed buildings," USDA FPL | Jul 2008 | https://research.fs.usda.gov/download/treesearch/33418.pdf | |
| grading_pass_rate | 0.55 (0.35-0.70) | Arbelaez et al., "Evaluation of lumber from deconstructed Portland residential buildings," Wood & Fiber Science 51(4) | 2019 | https://www.swst.org/wp/wp-content/uploads/2019/10/wfs2879.pdf | |
| degradation_per_decade | 0.02 (0.00-0.05) | Cavalli et al., "A review of the mechanical properties of aged wood...," Construction & Building Materials 114 | Apr 2016 | https://doi.org/10.1016/j.conbuildmat.2016.04.001 | Weak coefficient; condition-driven. Use DOI (ScienceDirect blocks direct fetch). |
| condition_base | 0.85 (0.70-0.95) | Engineering placeholder; Oregon DEQ found no age-salvage correlation | Mar 2019 | https://www.oregon.gov/deq/FilterDocs/DeconstructionReport.pdf | |

## Demolition activity and housing stock

| Item | Value | Source | Date | URL | Notes |
|---|---|---|---|---|---|
| National residential demolition rate; per-CMA counts | 0.74 / 1,000 dwellings/yr | StatCan, "Boom goes the dynamite...and conversions" | Jun 20, 2023 (2022 data) | https://www.statcan.gc.ca/o1/en/plus/3896-boom-goes-dynamiteand-conversions | |
| Dwellings by period of construction | per-CMA distributions | StatCan 2021 Census, Table 98-10-0233-01 | released Sep 21, 2022 | https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=9810023301 | Corrected table id (was 98-10-0234-01, which is dwelling condition by tenure). |
| CMA population & private dwellings | per-CMA counts | StatCan 2021 Census, Table 98-10-0014-01 | released Feb 9, 2022 | https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=9810001401 | |
| Wood-frame share, single-detached | 0.98 | NRCan, "Back to basics: building with wood" | modified Apr 2026 | https://natural-resources.canada.ca/stories/simply-science/back-basics-building-wood-asknrcan | |
| Toronto demolition permits (live, by year) | ~1,277/yr, 77% single-detached | City of Toronto Open Data, Cleared Building Permits | dataset 2001-present | https://open.toronto.ca/dataset/building-permits-cleared-permits/ | Portal shows a "Retired" flag; confirm before relying. Active companion: Building Permits - Active Permits. |

## Ecosystem and companies (demand-side, two-sided circularity)

| Item | Value | Source | Date | URL | Notes |
|---|---|---|---|---|---|
| Reclaimed-wood company directory (named) | 58 active companies | ECCC, "Companies working with reclaimed wood" (companion to Circularity of Wood) | Sep 2024 | bundled: docs/sources/ECCC Table Wood Reuse Companies Concise 12Sept EN.pdf | Year not printed in the file; companion to ECCC 2024-2025 circularity work. |
| National reclaimed-wood SME census | 252 SMEs; ON 37%, BC 25%, QC 16% | Light House, "Market Research on SMEs involved in Recovery and Reintegration of CRD Wood," for ECCC | Mar 2026 | no public URL; bundled: docs/sources/Light House Final Report - for distribution.pdf | Provided by advisor. No public link found as of Jun 2026. |
| CRD wood available for recovery (Canada) | ~3.6 Mt/yr; wood ~40% of CRD waste | FPInnovations Info Note 2023 No. 15 (Schorr & Boivin) | Sep 2023 | https://library.fpinnovations.ca/link/fpipub10712 | Most recent national supply ceiling. |
| ECCC material flow, sources to products | 11 source categories | ECCC / Canada.ca, Circularity of Wood | 2025 | https://www.canada.ca/en/services/environment/conservation/sustainability/circular-economy/sources-products-recovered-construction-renovation-demolition-wood.html | bundled chart: docs/sources/ECCC Circularity of Wood ... Chart 02_EN-v04.pdf |
| ECCC stakeholders (supply and demand) | stakeholder map | ECCC / Canada.ca | modified Jan 15, 2025 | https://www.canada.ca/en/services/environment/conservation/sustainability/circular-economy/construction-renovation-demolition-wood-supply-demand-stakeholders.html | bundled: docs/sources/ECCC Wood Stakeholders - Infographic ...EN-V02.pdf |
| Toronto C&D material flow | 366,300 t/yr C&D, 12% diverted | City of Toronto / Circle Economy / David Suzuki Foundation, "Baselining for a Circular Toronto," Tech Memo #3 | Jul 30, 2021 | https://www.toronto.ca/wp-content/uploads/2021/09/90e4-Technical-Memorandum-3Final-Report-09.09.2021FinalAODA.pdf | |
| Guelph-Wellington CRD material flow | wood inflow ~19.6 kt vs outflow ~2.75 kt (2021) | Dillon Consulting + Metabolic + Summit72 (Our Food Future) | 2021 data | https://www.dillon.ca/projects/material-flow-analysis-guelph-on/ | No public full-report PDF; bundled: docs/sources/Guelph-Wellington_MaterialFlowAnalysis_Report_FINAL.pdf |
| Residential construction waste rates | wood 21.8% by wt, 31.7% by vol | BC Housing / Light House, "Residential Construction Waste Analysis" | Apr 2021 (PDF May 27, 2021) | https://www.light-house.org/wp-content/uploads/2021/05/Residential-Construction-Waste-Analysis-May-27-2021.pdf | bundled in docs/sources/. |
| Per-house demolition wood yield | ~28.8 t wood per 1,300 sq ft SFD | Metro Vancouver, Demolition Waste Generation Rates Calculator (via Light House) | live tool | https://metrovancouver.org/services/solid-waste/demolition-waste-generation-rates-calculator | Coefficients computed in-tool, not displayed. |

## Demand and economics

| Item | Value | Source | Date | URL | Notes |
|---|---|---|---|---|---|
| Salvaged-wood value, Metro Vancouver | $342M/yr | BCIT / Unbuilders / Vancouver Economic Commission, "The Business Case for Deconstruction" | Jul 2020 | https://vemadeconstruction.com/wp-content/uploads/2024/files/387304d5-demolition_metrovancouver_industrywhitepaper_web_july2020.pdf | Original VEC URL dead; working mirror linked. |
| Reclaimed price premium (aesthetic) | 20-50% over virgin | Light House SME report; ECCC workshop report | Mar 2026 / Feb 2024 | https://www.canada.ca/en/services/environment/conservation/sustainability/circular-economy/workshop-report-opportunities-circularity-wood-construction-renovation-demolition.html | See unit caveat below. |
| Reclaimed vs new lumber prices (current) | reclaimed 2x4 $3.50-4.20/lin ft; hand-hewn +50-70% | The Green Mission Inc., "The Lumber Market in 2026" (J. Marschall, CPA) | Feb 14, 2026 | https://thegreenmissioninc.com/the-lumber-market-in-2026/ | North American; full-dimension vs dressed is a unit trap. |
| New softwood reference price | ~$468/MBF (Mar 2026) | NAHB framing lumber prices (now Madison's Lumber Price Index) | updated Jun 2026 | https://www.nahb.org/news-and-economics/housing-economics/national-statistics/framing-lumber-prices | Page shows % change, not absolute. |
| Deconstruction cost premium | 17-25% over demolition | Light House SME; Delta Institute Go Guide | Mar 2026 / May 2018 | https://delta-institute.org/wp-content/uploads/2018/05/Deconstruction-Go-Guide-6-13-18-.pdf | |
| Canadian secondary market state | "limited... in its infancy" | ECCC, "Opportunities for Circularity of Wood in CRD in Canada" (workshop report) | Feb 2024 | https://www.canada.ca/en/services/environment/conservation/sustainability/circular-economy/workshop-report-opportunities-circularity-wood-construction-renovation-demolition.html | Strongest Canadian demand-dynamics source. |
| Recycling vs downcycling vs upcycling framing | 4R principle | Owusu-Akyaw et al., "A review of the circular economy approach to CRD wood waste," Cleaner Waste Systems | Jun 2025 | https://doi.org/10.1016/j.clwas.2025.100248 | |
| Mass timber / DLT from reclaimed boards | glue-free DLT pilot | InnoRenew CoE, EcoDLT project | Sep 2024 - Feb 2027 | https://innorenew.eu/project/lifecycle-extension-salvaged-wooden-materials-reuse-dowel-laminated-timber-ecodlt/ | EU. Canadian movers: Urban Machine, All Bay Lumber. |
| Housing starts (demand anchor) | 259,028 in 2025 (+5.6%) | CMHC, "Housing starts up 5.6% in 2025" | Jan 16, 2026 | https://www.cmhc-schl.gc.ca/media-newsroom/news-releases/2026/housing-starts-december-2025 | |
| Global reclaimed lumber market (context) | USD 59.9B (2025) | Mordor Intelligence, Reclaimed Lumber Market | updated May 14, 2026 | https://www.mordorintelligence.com/industry-reports/reclaimed-lumber-market | Global only; vendor estimate. |

## Policy levers (scenarios)

| Item | Value | Source | Date | URL | Notes |
|---|---|---|---|---|---|
| Mandatory deconstruction uplift | recovery ~0.30 to 0.70 | City of Vancouver Green Demolition By-law | 2014 (amended 2016, 2018) | https://bylaws.vancouver.ca/11023c.pdf | 95%+ diversion for full deconstruction; 75-90% minimums for pre-1950. |
| C&D waste diversion (national) | scenarios to 90% | Delphi Group, "C&D Waste Diversion in Canada" (for ECCC) | Sep 2024 | https://delphi.ca/wp-content/uploads/2024/09/CD-Waste-Diversion-in-Canada-Exec-Summary-Report-Sep-2024.pdf | |

## Corrections applied in this revision (June 2026 review)

- Author fix: the 1994 FPL single-family-construction source is **McKeever & Phelps**, not "McKee & McKeever."
- Year fix: Falk, Cramer & Evans is **2013** (FPJ 62(7/8)), not 2012.
- Year fix: StatCan "Boom goes the dynamite" was published **June 2023** (it analyzes 2022 data), not 2022.
- Table fix: period-of-construction is StatCan **98-10-0233-01**; 98-10-0234-01 is "dwelling condition by tenure."
- Link fix: Cavalli et al. now cited by **DOI** because the ScienceDirect page blocks direct access.
- Outdated-price fix: the WoodWeb antique-beam figure is from **2010**; current prices now come from Green Mission (Feb 2026); Aurora Mills (Jan 2023) retained but flagged as aging.
- Note: NAHB now sources **Madison's Lumber Price Index** (not Random Lengths) and publishes percentage change only.

## Bundled source PDFs (docs/sources/)

ECCC company directory; ECCC material-flow chart; ECCC stakeholders infographic;
Light House SME report; BC Housing/Light House residential waste analysis;
Guelph-Wellington material flow analysis; the MBA project brief. The Woodloop
thesis (Rashmi Sirkar, Toronto wood salvage) is ~310 MB and is referenced rather
than bundled: https://drive.google.com/file/d/1wXTFSXguiWjHS90OVRuzLCpoUnG_1SPQ/view

## Caveats

- The Light House SME report and the Guelph-Wellington full report have no public
  URLs found as of June 2026; both are bundled or linked via project pages.
- ECCC circularity pages block automated fetching; titles, dates, and content were
  confirmed by index and by the bundled PDFs.
- Reclaimed price comparisons carry a unit trap: reclaimed is often quoted
  full-dimension and per lineal foot, while new lumber is dressed and per MBF.
- The national "16% diversion" and "4 Mt CRD" figures rest on 2010-2015 data and
  are treated as a dated floor; the 3.6 Mt/yr wood figure (FPInnovations, 2023) is
  the current supply anchor.
