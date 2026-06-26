# Reclaimed Lumber Intelligence Layer

A salvageable-lumber intelligence layer for Circular Construction Canada (CCC),
covering Canada's 25 largest Census Metropolitan Areas (CMAs). Built for the UofT
Rotman RSM2700 project brief.

It answers four questions the brief poses: where salvageable lumber will emerge,
what it's worth, what recovery capacity exists, and where the bottlenecks are.
Every coefficient traces to a credible source (see `docs/SOURCES.md`), and the
uncertainty in those coefficients flows through to every number on screen.

## What makes it defensible

- **Sourced coefficients.** Wood content from McKee & McKeever (USDA FPL, 1994)
  and Falk (FPL, 2012); recovery and grading yields from Oregon DEQ (2019) and
  Falk FPL-RP-650 (2008); demolition rates and housing stock from StatCan 2021
  Census and the Building Permits Survey; reclaimed value from dealer price guides.
  Full provenance with ranges sits in `docs/SOURCES.md`.
- **Real data where it exists.** Toronto demolition permits are pulled live from
  Toronto Open Data (counted by year, with the incomplete recent years dropped).
  CMA populations, dwelling counts, and (for the six largest CMAs) housing-stock
  age distributions are real StatCan figures. Everything modelled is labelled as
  such.
- **Monte Carlo uncertainty.** The old fixed bands implied a precision the data
  can't support. Now 4,000 draws sample every coefficient across its sourced range,
  kept correlated across CMAs so national error doesn't falsely diversify away, and
  layered with per-CMA data-coverage noise. Results come as P10/P50/P90 rather than
  a single point.
- **Sensitivity tornado.** Shows which assumption moves the national answer most.
  Recovery method (deconstruction against demolition) dominates, which points CCC
  straight at its highest-leverage policy lever.

## The five deliverables (tabs)

1. **Municipal baseline.** City-wide estimate per market from demolition activity,
   real housing-stock age, and building archetype, with a recovery cascade and value.
2. **Hotspots & archetypes.** Neighbourhood demolition clusters; Toronto worked
   example, where real data confirms single-family detached at about 77% of
   demolitions.
3. **Forecast & uncertainty.** 5-10 year projection, Monte Carlo P10/P50/P90, and the
   sensitivity tornado.
4. **Ecosystem & gaps.** Supply chain mapped against supply, flagging weak-capacity
   markets.
5. **Platform roadmap.** Build-versus-partner blueprint (`docs/platform_roadmap.md`).

It also carries an editable **assumptions registry** (with ranges and sources), a
persistent **project store**, a **sources & void** view, and **scenario toggles**
(baseline, mandatory-deconstruction bylaw, high-redevelopment, downturn).

## Run it locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL Streamlit prints (usually http://localhost:8501). Running
locally needs no GitHub or cloud account. The live Toronto pull is off by default;
turn it on with the sidebar toggle, and it falls back to a cached real figure if
Toronto Open Data is unreachable.

## Project structure

```
app/
  app.py                  Streamlit dashboard, one tab per deliverable and uncertainty
  requirements.txt
  config/
    cmas.py               25 CMA registry (real StatCan dwellings, vintage, demo rate)
    assumptions.py        sourced coefficient registry with low/high ranges and scenarios
  pipeline/
    canonical.py          canonical schema and validators
    ingest.py             live Toronto connector, StatCan-derived counts, void report
    model.py              framing-based recovery cascade and value layer
    forecast.py           5-10 yr forecast with coverage bands
    uncertainty.py        Monte Carlo and tornado sensitivity
    ecosystem.py          actor map and gap analysis
    projects.py           persistent project store
  data/store/             persisted project JSON (created on first save)
  docs/
    platform_roadmap.md   Deliverable 5 strategy document
    SOURCES.md            every coefficient, its range, and its citation
```

## Limitations

- Wood-content and recovery coefficients are US-anchored (FPL, Oregon DEQ) applied
  to Canadian SPF-heavy stock. Ranges are widened to reflect that, and the Monte
  Carlo propagates it.
- `degradation_per_decade` is the weakest coefficient. The aged-wood literature
  finds sound wood loses little intrinsic strength with age, since real loss is
  condition-driven. It's kept small with a wide low bound (0).
- Demolition figures outside Toronto come from StatCan 2022 single-year data
  (single-detached at CMA scale, grossed up) or national-rate estimates. Toronto
  alone runs on live by-year data.
- Reclaimed value figures are indicative dealer prices rather than transaction-grade,
  and they carry a unit caveat (reclaimed is full-dimension rough sawn, new is dressed).
- Ecosystem actors are synthetic placeholders. The gap logic is real and runs
  unchanged on a verified actor directory.
