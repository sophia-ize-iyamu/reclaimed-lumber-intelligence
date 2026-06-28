## From intelligence layer to coordination platform

This app already answers the brief's core questions about where salvageable
lumber will emerge, what recovery capacity exists, and where the bottlenecks sit.
Deliverable 5 asks how Circular Construction Canada (CCC) turns that analytical
layer into a live coordination and decision-support platform. What follows is the
blueprint, with a build-versus-partner view and an integration pathway.

### The destination

A live platform adds what the static layer can't deliver on its own:

1. **Real-time permit monitoring.** Ingest demolition permits as they're issued,
   so the forward supply signal updates continuously rather than once per study.
2. **Supply-to-demand matchmaking.** Connect a known incoming demolition to nearby
   processors, warehouses, and reuse buyers before the material is landfilled.
3. **Dynamic recovery forecasting.** Recompute the forecast as new permits,
   projects, and ecosystem actors enter the system.

### Demand and the two-sided ecosystem

The supply estimate is only half the picture; the platform has to model the demand
side and the full two-sided ecosystem. That is built into the app: a real
reclaimed-wood company directory, the national SME census, the circular value
chain, demand segments, the economics, and a ranked diagnosis of why recoverable
wood still isn't reclaimed.

The strategic read that follows from it: this is a coordination gap rather than a
supply problem. Latent demand already exceeds current spec-ready supply. What's
missing is a forward supply signal, so buyers can commit to material before it
physically exists. Shared advance information lets independent operators coordinate,
without running a marketplace. A predictable supply signal is what makes those
commitments possible.

The deconstructor is the real customer, because the recover-versus-downcycle
decision is theirs, and demand assurance is what tips it toward recovery.

### Machine vision and the yield-prediction problem

A permit gives an address and a date. Turning that into a usable forecast means
predicting what the building contains: species, dimensions, condition, and board
footage. Machine vision is the path to closing that inference gap at scale:

- Estimate recoverable yield from building imagery (street view, listing photos,
  permit drawings) keyed to the building archetype.
- Map defects (checks, knots, fastener holes) to grade reclaimed boards for
  mass-timber feedstock without shredding.
- Build a digital twin of irregular stock and match cut plans against it.

This is a Phase 2 to Phase 3 capability. The attributes-and-archetypes model
already in the app is the schema it would feed.

### Phased roadmap

**Phase 0 (now): defensible intelligence layer.** This app. One real connector
(Toronto), modelled coverage for the other 24 CMAs, a transparent assumptions
registry, and an honest void report. What this phase buys is credibility: numbers
CCC can defend in front of municipalities and funders.

**Phase 1 (0 to 6 months): widen real coverage.** Connect the next tier of
machine-readable permit feeds (Vancouver, Ottawa, Calgary, Hamilton). Each new
connector lands behind the same canonical schema, so the model stays put. Coverage
tiers climb from low to medium to high as feeds come online, and the confidence
bands tighten on their own. The void report becomes the public scorecard of
national data readiness.

**Phase 2 (6 to 18 months): project intake at scale and the actor registry.**
Open the project store to demolition and deconstruction contractors so they can
register upcoming sites. Extend the reclaimed-wood company directory into a
verified, per-site registry of processors, warehouses, and reuse buyers. At that
point the gap analysis runs on audited capacity rather than a province-level estimate.

**Phase 3 (18 months and beyond): live matchmaking.** With real supply signals and
a real actor registry in place, add matchmaking: notify the nearest processor and
buyer when a high-yield demolition is permitted, and let them claim the material.
That's the coordination platform the brief envisions.

### Build versus partner

The platform isn't one system. It's several capabilities, and the right answer
differs for each.

| Capability | Recommendation | Why |
|---|---|---|
| Canonical data model and assumptions registry | **Build** | This is CCC's proprietary asset and the source of its credibility. It can't be outsourced. |
| Permit ingestion connectors | **Build thin, partner where feeds exist** | Where a municipality already publishes open permit data, write a connector. Don't rebuild the municipal system. |
| Forecasting and gap-analysis engine | **Build** | The method is the differentiator. Keep it in house and transparent. |
| Matchmaking marketplace | **Partner or integrate** | Material-exchange marketplaces already exist. CCC should feed them supply signals instead of rebuilding a marketplace from zero. |
| Hosting and identity | **Partner (managed cloud)** | Commodity. No reason to operate infrastructure. |

The guiding rule is simple. CCC builds the data asset and the analysis it depends
on, and it partners for commodity infrastructure and for marketplaces that already
have buyers.

### Integration pathway

The canonical schema is the integration contract. Data crosses it in a few
directions:

1. **Inbound:** municipal open-data portals and provincial assessment data feed the
   canonical demolition and housing tables.
2. **Internal:** the assumptions registry and project store let CCC and its partners
   correct and extend the model without touching code.
3. **Outbound:** a read API over the forecast and gap tables lets municipalities,
   funders, and marketplaces consume CCC intelligence inside their own tools.

### What makes this durable

The lasting advantage comes from the canonical dataset and the network of
corrections that builds up as municipalities, contractors, and reuse buyers use it.
The layer grows harder to replicate as more connectors, registered projects, and
expert corrections accumulate inside it. The same methodology then extends from
lumber to other reclaimed materials, and the data and network asset grow more
valuable as they accumulate.

### Limitations

- Base-year demolition figures outside Toronto rely on StatCan 2022 CMA figures or
  a national-rate estimate rather than live feeds. Toronto alone draws live by-year
  data. Monte Carlo confidence bands reflect this by coverage tier.
- The recovery cascade uses sourced coefficients from US deconstruction literature
  (USDA FPL, Oregon DEQ) applied to Canadian stock. The sensitivity tornado shows
  recovery method as the dominant uncertainty, so Phase 1 should validate it against
  real Canadian deconstruction projects through the project store.
- `degradation_per_decade` is weakly supported and reads better as a condition
  factor than a calendar-age factor, so it's kept small with a wide low bound.
- Reclaimed value figures are indicative dealer prices rather than transaction-grade.
- The ecosystem uses the real ECCC company directory (September 2024) and the
  national SME census (Light House, March 2026). Capacity is estimated at the
  province level, so the gap analysis is not yet a verified per-site infrastructure audit.
