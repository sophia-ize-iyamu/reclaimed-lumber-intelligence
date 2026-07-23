# Maintainer hand-off

How the Reclaimed Lumber Intelligence Layer is put together, where every input
lives, how to change it, and how a future team can extend it. Written for CCC or
a follow-on team taking the model forward.

## What runs where

```
app/
  app.py                  the Streamlit app: sidebar nav, one block per page, and the
                          run_pipeline() that assembles everything (cached)
  config/                 all inputs and coefficients (this is what you edit)
    assumptions.py        every model coefficient, each with value + low/high range + source
    cmas.py               the 25 CMA registry: population, dwellings, vintage mix,
                          demolition intensity, data-quality tier
    carbon.py             carbon coefficients (avoided manufacturing, biogenic stored)
    policy.py             municipal policy scores and by-laws
    demand*.py            demand-side inputs (supporting layer this phase)
  pipeline/               the calculation, kept separate from the inputs
    ingest.py             live Toronto & Vancouver connectors, StatCan-derived counts,
                          the era split, and the void / coverage report
    model.py              the supply cascade (permits -> board feet -> value)
    forecast.py           the projection to the horizon year
    uncertainty.py        Monte Carlo bands and the sensitivity tornado
  docs/SOURCES.md         the full provenance table with URLs
```

## The model in one line

`permits -> wood-frame floor area -> framing lumber -> recoverable -> salvageable
-> spec-ready -> reclaimed value`, with carbon computed from spec-ready volume.
Every arrow is a coefficient in `config/assumptions.py`. Nothing is hard-coded in
the pipeline; `model.py` reads coefficients through `val()` / `rng()`.

## How to change an assumption

- **At runtime:** open the **Assumptions** page and move a slider. Every figure in
  the app updates live. Good for what-if checks; changes are not saved.
- **Permanently:** edit the coefficient's `C(...)` record in `config/assumptions.py`.
  Each record is `C(value, low, high, unit, source, url, basis)`. Change the value
  and the range, and update the source and URL so the provenance stays honest.

## How the demolition era mix is built

`pipeline/ingest.py` splits each city's annual demolitions across building eras.
The era mix of demolitions is **not** the era mix of the standing stock, so the
standing-stock age (StatCan) is weighted by `TEARDOWN_PROPENSITY` in
`assumptions.py` (older homes are torn down at higher rates) and renormalised.
That curve is an editable estimate; replace it if a vintage-of-demolitions series
becomes available.

## How to add a live city feed

1. Write a connector in `pipeline/ingest.py` that returns `{year: count}` for that
   city's demolition permits, mirroring `vancouver_demolitions()` (Opendatasoft) or
   `toronto_demolitions()` (CKAN). Include an offline cached fallback.
2. Wire it into `build_demolition_table()` next to the Toronto/Vancouver branches
   and set its tier to `"high"`.
3. Add a row to `source_registry()` and to `docs/SOURCES.md`, and update
   `config/cmas.py` (that city's `coverage_tier`).

Clean next targets (all publish an open demolition work-type): Calgary and Edmonton
(Socrata), Montreal (CKAN), then Winnipeg. Ottawa publishes Excel only.

## How outputs are calculated

`model.estimate_supply()` applies the cascade per (CMA, era) row; `cma_summary()`
rolls it up per CMA; the Overview rolls up to province and national. Carbon is in
`config/carbon.py`. The confidence band comes from the data-quality tier
(`CONFIDENCE_BAND`) plus Monte Carlo sampling of the coefficients
(`pipeline/uncertainty.py`). Per-CMA percentiles are not additive, so the band is
reported at the national level only.

## How to update over time

The model is structure plus swappable data. As better data arrives (municipal
open data, a Canadian wood-content study, expert-validated recovery rates), swap
the coefficient or connect the feed behind the same canonical schema
(`pipeline/canonical.py`); the rest of the model stays put. Log the change in
`docs/SOURCES.md`.

## Run and deploy

```
pip install -r requirements.txt
streamlit run app.py
```

Live open-data feeds are off by default (the sidebar toggle turns them on).
Deployed on Streamlit Cloud, which redeploys on a push to the connected repo.
