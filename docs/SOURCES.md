# Data sources and coefficient provenance

Every coefficient in `config/` traces to a source below. Each row gives the
value, the source, a publication date (month and year, day where known), a
working URL, and notes. Source PDFs that
are freely shareable are bundled in `docs/sources/`.

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
| Demolition by structural type (Canada, 2022) | single-detached 77.1% of 11,988 units; rest semi-detached, row, apartment/multi | StatCan, "Boom goes the dynamite...and conversions" | Jun 2023 (2022 data) | https://www.statcan.gc.ca/o1/en/plus/3896-boom-goes-dynamiteand-conversions | National figure used on Hotspots; not Toronto-specific. CMA single-detached counts: Vancouver 1,451, Toronto 1,138, Montreal 575. |
| Dwellings by period of construction | per-CMA distributions | StatCan 2021 Census, Table 98-10-0233-01 | released Sep 21, 2022 | https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=9810023301 | Corrected table id (was 98-10-0234-01, which is dwelling condition by tenure). |
| CMA population & private dwellings | per-CMA counts | StatCan 2021 Census, Table 98-10-0014-01 | released Feb 9, 2022 | https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=9810001401 | |
| Wood-frame share, single-detached | 0.98 | NRCan, "Back to basics: building with wood" | modified Apr 2026 | https://natural-resources.canada.ca/stories/simply-science/back-basics-building-wood-asknrcan | |
| Toronto demolition permits (live, by year) | ~1,277 cleared demolition permits/yr | City of Toronto Open Data, Cleared Building Permits | dataset 2001-present | https://open.toronto.ca/dataset/building-permits-cleared-permits/ | The 77% single-detached share is the StatCan national figure above, not Toronto-specific. Portal shows a "Retired" flag; confirm before relying. |

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
| National C&D diversion vs deconstruction | ~16% national vs ~85% on deconstruction projects | Canadian Architect, "Reuse of Wood C&D Waste: Potentials for Canada" | 2023 | https://www.canadianarchitect.com/reuse-of-wood-construction-and-demolition-waste-potentials-for-canada/ | Deconstruction lifts diversion roughly 5x. |
| Federal C&D waste diversion target | 90% | Government of Canada, Greening Government Strategy | current | https://www.canada.ca/en/treasury-board-secretariat/services/innovation/greening-government/government-canada-progress-on-environmental-indicators/construction-renovation-demolition-waste.html | Federal operations target. |

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
| North American reclaimed lumber market (context) | ~US$12.4B (2024); flooring & furniture lead | Global Growth Insights; market.us, Reclaimed Lumber Market | 2024-2025 | https://market.us/report/global-reclaimed-lumber-market/ | Vendor estimates; used for regional/segment structure only. |
| Canadian value-retention economy (context) | ~C$56B (2019) | Constructive Voices; TheFutureEconomy.ca | 2023 | https://thefutureeconomy.ca/interviews/from-rubble-resource-building-canada-circular-construction-future/ | Reuse/repair/refurbishment macro scale. |

## Policy levers (scenarios)

| Item | Value | Source | Date | URL | Notes |
|---|---|---|---|---|---|
| Mandatory deconstruction uplift | recovery ~0.30 to 0.70 | City of Vancouver Green Demolition By-law | 2014 (amended 2016, 2018) | https://bylaws.vancouver.ca/11023c.pdf | 95%+ diversion for full deconstruction; 75-90% minimums for pre-1950. |
| C&D waste diversion (national) | scenarios to 90% | Delphi Group, "C&D Waste Diversion in Canada" (for ECCC) | Sep 2024 | https://delphi.ca/wp-content/uploads/2024/09/CD-Waste-Diversion-in-Canada-Exec-Summary-Report-Sep-2024.pdf | |

## Demand drivers and demand-side ecosystem

Market-research application shares and
reclaimed pricing disagree firm-to-firm and are shown as ranges. Government,
standards-body, and trade-press rows are firmer.

| Item | Value | Source | Date | URL | Notes |
|---|---|---|---|---|---|
| NA green buildings market | US$204B (2024) to US$377B (2030), 10.6%/yr | Mordor Intelligence, North America Green Buildings Market | 2025 | https://www.mordorintelligence.com/industry-reports/north-america-green-buildings-market | Macro demand driver |
| Wellness real estate market | US$584B (2024) to US$1.1T (2029) | Global Wellness Institute, Build Well to Live Well | 2025 | https://globalwellnessinstitute.org/press-room/press-releases/build-well-to-live-well-2025/ | Biophilic demand; WELL v2 |
| Wellness building premium | 10-25% residential, 4.4-7.7% commercial rent | Global Wellness Institute | 2025 | https://globalwellnessinstitute.org/press-room/press-releases/build-well-to-live-well-2025/ | Willingness to pay |
| Reclaimed application mix | Furniture 31-41% (largest); flooring fastest-growing | Grand View Research; Precedence Research; Market Research Future | 2022-2025 | https://www.grandviewresearch.com/industry-analysis/reclaimed-lumber-market | Vendor estimates; ranges |
| End-use split | Commercial about 58% (2022) | Grand View Research | 2022 | https://www.grandviewresearch.com/industry-analysis/reclaimed-lumber-market | Residential faster-growing |
| Flooring segment growth | about US$22.5B by 2030 at 3.7%/yr | Global Industry Analysts via Research and Markets | Feb 2025 | https://www.globenewswire.com/news-release/2025/02/28/3034812/28124/en/Reclaimed-Lumber-Industry-Business-Report-2025.html | |
| Federal Standard on Embodied Carbon | 10% cut on concrete, federal projects >=$10M and >100 m3 | Treasury Board of Canada Secretariat | Dec 2022 | https://www.tbs-sct.canada.ca/pol/doc-eng.aspx?id=32814 | In force |
| Standard expanded to steel and whole-building LCA | Effective Sept 1, 2025 | Treasury Board, Contracting Policy Notice 2025-6 | 2025 | https://www.canada.ca/en/treasury-board-secretariat/services/policy-notice/2025-6.html | In force |
| Federal building embodied-carbon target | 30% cut or max within 2% cost premium, buildings >2,000 m2 | NRCan, Canada Green Buildings Strategy | Jul 2024 | https://natural-resources.canada.ca/energy-efficiency/building-energy-efficiency/canada-green-buildings-strategy | Verify verbatim |
| Toronto Green Standard v4 | Caps 350/250 kg CO2e/m2; reused = zero upfront; top tier mandatory by 2028 | City of Toronto; Daily Commercial News | 2022-2023 | https://canada.constructconnect.com/dcn/news/resource/2023/07/climate-and-construction-toronto-green-standard-v4-tackles-embodied-carbon-in-materials | |
| Vancouver Building By-law embodied carbon | 10% cut (Jan 1, 2025); 20% for 1-6 storey wood | City of Vancouver; Carbon Leadership Forum BC | 2025 | https://clfbritishcolumbia.com/embodied-carbon-in-vancouver-building-bylaw-2025/ | Partial delay for smaller buildings |
| National Building Code 2025 GHG objective | Adds a GHG-emissions objective | NRC Codes Canada | 2025 | https://nrc-publications.canada.ca/eng/view/object/?id=adf1ad94-7ea8-4b08-a19f-653ebb7f45f6 | Direction-setting |
| Landfill Methane Regulations | 50% cut below 2019 by 2030 | Canada Gazette Part 2, SOR/2025-279 | Dec 2025 | https://gazette.gc.ca/rp-pr/p2/2025/2025-12-31/html/sor-dors279-eng.html | Raises landfill-diversion value |
| Zero Carbon Building Design Standard v4 | Scores embodied carbon, not only operations | Canada Green Building Council | Jun 2024 | https://www.cagbc.org/news-resources/technical-documents/zcb-design-standard-v4/ | |
| LEED v4.1 reused-material incentive | Reused counted at 200% of cost; up to 5 pts reuse | USGBC, LEED v4.1 Materials and Resources | current | https://leeduser.buildinggreen.com/ | Specifier mechanism |
| Quebec mass timber and wood-first | 18 storeys (2025); consider wood first | Quebec MRNF; Regie du batiment du Quebec | 2025 | https://mechanicalbusiness.com/2025/07/25/quebec-authorizes-mass-timber-buildings-to-18-storeys/ | |
| Canadian mass-timber market | $379M (2023) to $1.2B (2030) to $2.4B (2035) | Mass Timber Roadmap (Transition Accelerator, FPAC, CWC) | Jun 2024 | https://transitionaccelerator.ca/wp-content/uploads/2024/06/MT_Roadmap_Digital_vf.pdf | Adjacent demand signal |
| Competitive substitute (wood-look LVT) | Hardwood share 23.4% (2015) to 12.6% (2024); 69% name vinyl top threat | Floor Covering News | 2025 | https://www.fcnews.net/2025/07/hardwood-stats-segment-cedes-share-but-high-end-hangs-tough/ | |
| Reclaimed pricing | Flooring about US$10-20/sq ft raw vs $3-7 new; processing 2-10x; furniture 15-30% premium | Supplier and trade estimates; IndexBox | 2024-2026 | https://www.reallycheapfloors.com/blog/reclaimed-hardwood-flooring-cost/ | Indicative |
| Habitat ReStore scale | 100+ stores, over 1B lbs diverted, about $80M network | Habitat for Humanity Canada; Retail-Insider | 2022-2024 | https://habitat.ca/en/restore | Demand-side retail |
| Unbuilders and Heritage Lumber | 99.2% single-family salvage rate | The Construction Source | 2023 | https://www.theconstructionsource.ca/2023/06/01/unbuilders/ | Broker archetype |
| BMEx / Light House / Rheaply | Free B2B material exchange on Rheaply | Light House; ConstructConnect | 2024 | https://www.light-house.org/bmex/ | Coordinate, not run a marketplace |
| Structural reuse barrier | Salvaged lumber must be re-graded; no Canadian code path | ECCC circularity-of-wood workshop report | Feb 2024 | https://www.canada.ca/en/services/environment/conservation/sustainability/circular-economy/workshop-report-opportunities-circularity-wood-construction-renovation-demolition.html | Top demand barrier |
| Structural-timber reuse barriers | Certification gap, unknown provenance | Taylor and Francis review | 2025 | https://www.tandfonline.com/doi/full/10.1080/17480272.2025.2517186 | Peer-reviewed |
| Architect and designer count | Over 5,000 registered architects (approximate) | RAIC Vital Statistics; Interior Designers of Canada | 2024-2025 | https://chop.raic.ca/appendix-c-vital-statistics-provincial-and-territorial-associations-of-architects | Specifier channel; approximate |

## Cost economics, jobs, and provincial diversion

Cost-per-area and per-house figures are contractor and single-firm estimates shown
as ranges or illustrative cases; government and StatCan rows are firmer.

| Item | Value | Source | Date | URL | Notes |
|---|---|---|---|---|---|
| Deconstruction vs demolition cost | demo about US$4-10/sq ft; deconstruction about US$8-16/sq ft | Angi, cost-to-demolish-a-house | 2026 | https://www.angi.com/articles/how-much-does-it-cost-demolish-house.htm | Contractor aggregator; ranges |
| Deconstruction vs demolition time | demo 1-4 days; deconstruction 2 or more weeks | DemoPros; Journal of Commerce | 2021-2025 | https://canada.constructconnect.com/joc/news/projects/2021/05/deconstruction-a-new-way-to-make-old-buildings-disappear | |
| Kiln drying cost | about US$0.70-2.00/bf | SW Wood Dryer | 2024-2025 | https://swwooddryer.com/how-much-does-it-cost-to-kiln-dry-lumber/ | Processing component |
| De-nailing and inspection | adds about US$3-8/sq ft, manual | Moruxo | 2024 | https://moruxo.com/blog/cost-of-reclaimed-vs-new-wood-slabs | |
| Net cost after donation tax credits (Canadian case) | demolition about $26,500; deconstruction net about $14,595 after about $18,850 federal and $9,555 provincial credits | Unbuilders / Habitat via The Construction Source; CBC | 2020-2023 | https://www.theconstructionsource.ca/2023/06/01/unbuilders/ | Illustrative single-firm case |
| Jobs, deconstruction vs demolition | about 6 jobs per project vs 1 | Journal of Commerce / ConstructConnect | 2021 | https://canada.constructconnect.com/joc/news/projects/2021/05/deconstruction-a-new-way-to-make-old-buildings-disappear | |
| Jobs per 10,000 tons by end-of-life path | landfill about 1, recycling about 10, reuse far higher | Institute for Local Self-Reliance | current | https://ilsr.org/articles/recycling-means-business/ | |
| Per-house recovery (Unbuilders) | about 70 t diverted, about 10 t lumber, under 10% waste | Journal of Commerce | 2021 | https://canada.constructconnect.com/joc/news/projects/2021/05/deconstruction-a-new-way-to-make-old-buildings-disappear | |
| Salvage rate and carbon (36-home study) | about 27% by weight salvaged; about 7.6 t CO2e/house benefit; softwood framing about 85% of salvage | Oregon DEQ, Deconstruction vs Demolition | 2019 | https://www.oregon.gov/deq/FilterDocs/DeconstructionReport.pdf | Primary study |
| Provincial all-waste diversion | national 27%; NS 43%, BC 38%, NL 11% (2022) | ECCC CESI; StatCan Table 38-10-0138 | 2022 / Nov 2024 | https://www.canada.ca/en/environment-climate-change/services/environmental-indicators/solid-waste-diversion-disposal.html | QC, ON, AB, MB approximate |
| Diverted tonnage by province | Ontario 3.4 Mt, Quebec 2.7 Mt (2022) | StatCan, The Daily | Apr 2024 | https://www150.statcan.gc.ca/n1/daily-quotidien/240408/dq240408b-eng.htm | |
| Victoria deconstruction by-law | salvage 40 kg wood per m2; $19,500 deposit | City of Victoria; CTV | 2022 | https://victoria.ca/EN/main/residents/waste-reduction/construction-waste.html | |
| North Vancouver salvage by-law | about 3.5 kg lumber per sq ft, pre-1950; $15,000 deposit | District of North Vancouver; CBC | 2023 | https://www.dnv.org/business-development/demolition-waste-reduction-bylaw | |
| BC municipalities with demolition recycling by-laws | Port Moody and Burnaby 70%; plus Richmond, Surrey, Coquitlam, West Vancouver, Squamish | Coast Waste Management Association | 2024 | https://cwma.ca/knowledge-base-2/deconstruction-by-laws/ | |
| Quebec building-sector CRD | about 1.675 Mt (2023), 53% to sorting centres | RECYC-QUEBEC, Bilan 2023 | 2023 | https://www.recyc-quebec.gouv.qc.ca/sites/default/files/documents/bilan-gmr-2023-crd.pdf | |
| Metro Vancouver tipping fees | clean wood $118/t, C&D processing residual $185/t (2025) | Metro Vancouver, Bylaw 383 | 2025 | https://metrovancouver.org/services/solid-waste/Documents/sws-tipping-fee-updates-2025.pdf | |

## Bundled source PDFs (docs/sources/)

ECCC company directory; ECCC material-flow chart; ECCC stakeholders infographic;
Light House SME report; BC Housing/Light House residential waste analysis;
Guelph-Wellington material flow analysis; the MBA project brief. The Woodloop
thesis (Rashmi Sirkar, Toronto wood salvage) is ~310 MB and is referenced rather
than bundled: https://drive.google.com/file/d/1wXTFSXguiWjHS90OVRuzLCpoUnG_1SPQ/view

## Caveats

- The Light House SME report and the Guelph-Wellington full report have no public
  URLs; both are bundled or linked via project pages.
- ECCC circularity pages block automated fetching; titles, dates, and content were
  confirmed by index and by the bundled PDFs.
- Reclaimed price comparisons carry a unit trap: reclaimed is often quoted
  full-dimension and per lineal foot, while new lumber is dressed and per MBF.
- The national "16% diversion" and "4 Mt CRD" figures rest on 2010-2015 data and
  are treated as a dated floor; the 3.6 Mt/yr wood figure (FPInnovations, 2023) is
  the current supply anchor.
