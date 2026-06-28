"""
Reclaimed Lumber Intelligence Layer
Circular Construction Canada

A salvageable-lumber intelligence layer for Canada's 25 largest CMAs, organized
around the brief's five deliverables. Every coefficient is sourced (see
docs/SOURCES.md), uncertainty is propagated by Monte Carlo, and a sensitivity
tornado shows which assumption matters most.

Run locally:
    pip install -r requirements.txt
    streamlit run app.py
"""

import base64
import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from config import assumptions as A
from config import cmas as cma_cfg
from config import companies, demand, carbon, policy, demand_drivers, demand_ecosystem
from config.assumptions import val
from pipeline import ingest, model, forecast, ecosystem, projects, uncertainty

st.set_page_config(page_title="Reclaimed Lumber Intelligence | CCC",
                   layout="wide", page_icon="🪵")


# --------------------------------------------------------------------------- #
# Styling. The app follows the viewer's system light/dark setting: Streamlit's
# base theme tracks the OS, and all custom styling is driven by the CSS
# prefers-color-scheme media query (which reads the OS directly). Charts are
# theme-neutral so they read on either background, no detection needed.
# --------------------------------------------------------------------------- #
ACCENT = "#4DB779"  # CCC primary green


def style_chart(fig, height=340, **layout):
    """Transparent background and neutral text/grid that read on light or dark."""
    fig.update_layout(height=height, margin=dict(l=8, r=14, t=12, b=10),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(family="Inter, system-ui, sans-serif", color="#5F6368"),
                      template="none", **layout)
    # automargin reserves room for tick labels and axis titles so neither lands
    # on the plot; title_standoff keeps the axis title clear of the ticks.
    fig.update_xaxes(gridcolor="rgba(128,128,128,0.18)", zerolinecolor="rgba(128,128,128,0.25)",
                     linecolor="rgba(128,128,128,0.30)", automargin=True, title_standoff=10)
    fig.update_yaxes(gridcolor="rgba(128,128,128,0.18)", zerolinecolor="rgba(128,128,128,0.25)",
                     linecolor="rgba(128,128,128,0.30)", automargin=True, title_standoff=10)
    return fig


def style_geo(fig, height=460):
    """Transparent map with low-opacity gray land that tints either background."""
    fig.update_geos(fitbounds="locations", resolution=50, showcountries=True,
                    countrycolor="rgba(128,128,128,0.40)", showland=True,
                    landcolor="rgba(128,128,128,0.16)", showocean=False, showframe=False,
                    showcoastlines=True, coastlinecolor="rgba(128,128,128,0.40)",
                    bgcolor="rgba(0,0,0,0)", lakecolor="rgba(0,0,0,0)")
    fig.update_traces(marker=dict(line=dict(width=0.6, color="rgba(128,128,128,0.55)")),
                      selector=dict(type="scattergeo"))
    return style_chart(fig, height)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap');

/* Colours follow the operating system light/dark setting via prefers-color-scheme */
:root {
  --app-bg:#FFFFFF; --side-bg:#EEF2EC; --card-bg:#FFFFFF;
  --muted:#5C5C54; --rule:#E2E7DE; --head:#14532D;
  --gold:#4DB779; --gold-text:#2F7D4F;
}
@media (prefers-color-scheme: dark) {
  :root {
    --app-bg:#000000; --side-bg:#101310; --card-bg:rgba(77,183,121,0.08);
    --muted:#9A9A92; --rule:rgba(77,183,121,0.22); --head:#EAF3EC;
    --gold:#4DB779; --gold-text:#5CCF95;
  }
}

/* App surfaces matched to the walkthrough page */
.stApp, [data-testid="stAppViewContainer"] { background-color: var(--app-bg); }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { background-color: var(--side-bg); border-right: 1px solid var(--rule); }
[data-testid="stSidebar"] > div:first-child { border-top: 3px solid var(--gold); }

/* Inter for UI, JetBrains Mono for figures */
html, body, .stApp, [data-testid="stSidebar"], .stApp p, .stApp li, .stApp label, .stApp div {
  font-family: 'Inter', system-ui, 'Segoe UI', Roboto, sans-serif;
}
/* Editorial serif headings (brand: Source Serif 4) */
h1, h2, h3, h4 {
  font-family: 'Source Serif 4', Georgia, serif !important;
  font-weight: 600 !important; letter-spacing: -0.01em; color: var(--head);
}
/* Section subheaders get a gold lead bar */
.stApp [data-testid="stMarkdownContainer"] h3 { padding-left: 12px; border-left: 4px solid var(--gold); }

/* Metric cards: framed, gold accent, instrument-panel numerals */
div[data-testid="stMetric"] {
  background: var(--card-bg); border: 1px solid var(--rule); border-left: 3px solid var(--gold);
  border-radius: 12px; padding: 14px 16px;
}
div[data-testid="stMetric"] label p {
  font-family: 'JetBrains Mono', 'SFMono-Regular', monospace; white-space: normal;
  text-transform: uppercase; letter-spacing: 0.05em; font-size: 0.68rem; font-weight: 600; opacity: 0.9;
}
div[data-testid="stMetricValue"] {
  font-family: 'JetBrains Mono', 'SFMono-Regular', monospace; font-variant-numeric: tabular-nums;
  font-size: clamp(1.05rem, 1.7vw, 1.7rem); white-space: normal; line-height: 1.12; letter-spacing: -0.01em;
}
/* Tabs */
button[data-baseweb="tab"] { font-size: 0.95rem; padding-top: 6px; padding-bottom: 6px; }
/* Tables */
div[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; font-variant-numeric: tabular-nums; }
/* Captions: force the muted token (high specificity beats Streamlit's faded default) */
.stApp [data-testid="stCaptionContainer"],
.stApp [data-testid="stCaptionContainer"] p,
.stApp [data-testid="stCaptionContainer"] span,
.stApp small, .stApp [data-testid="stCaptionContainer"] div { color: var(--muted) !important; }

/* Hero header */
.hero { margin: 2px 0 4px; }
.hero-eyebrow { font-family: 'JetBrains Mono', monospace; text-transform: uppercase;
  letter-spacing: .16em; font-size: 11px; color: var(--gold-text); }
.hero-title { font-family: 'Source Serif 4', Georgia, serif; font-size: 2.4rem; line-height: 1.05;
  margin: 4px 0 8px; color: var(--head); font-weight: 600; }
.hero-sub { color: var(--muted); max-width: 840px; font-size: 1.02rem; line-height: 1.5; }
.hero-rule { height: 4px; width: 80px; background: var(--gold); border-radius: 3px; margin-top: 16px; }

/* Sidebar vertical navigation (replaces the horizontal tab strip) */
[data-testid="stSidebar"] [role="radiogroup"] { gap: 2px; }
[data-testid="stSidebar"] [role="radiogroup"] > label {
  display: flex; align-items: center; width: 100%; margin: 0;
  padding: 8px 12px; border-radius: 8px; cursor: pointer;
  border-left: 3px solid transparent;
}
[data-testid="stSidebar"] [role="radiogroup"] > label:hover { background: rgba(77,183,121,0.10); }
[data-testid="stSidebar"] [role="radiogroup"] > label:has(input:checked) {
  background: rgba(77,183,121,0.16); border-left-color: var(--gold);
}
[data-testid="stSidebar"] [role="radiogroup"] > label:has(input:checked) p {
  color: var(--gold-text); font-weight: 600;
}
[data-testid="stSidebar"] [role="radiogroup"] > label > div:first-child { display: none; }
[data-testid="stSidebar"] [role="radiogroup"] label p { font-size: 0.95rem; }
[data-testid="stSidebar"] .navhdr {
  font-size: 0.72rem; letter-spacing: 0.09em; font-weight: 700; text-transform: uppercase;
  color: var(--muted); margin: 14px 0 2px; padding-left: 12px;
}
/* Section "tabs": color the expander headers even when collapsed */
[data-testid="stSidebar"] details { border: none !important; background: transparent !important; }
[data-testid="stSidebar"] details summary {
  background: rgba(77,183,121,0.12); border-left: 3px solid var(--gold);
  border-radius: 8px; padding: 8px 12px; margin: 3px 0; list-style: none;
}
[data-testid="stSidebar"] details summary:hover { background: rgba(77,183,121,0.22); }
[data-testid="stSidebar"] details[open] summary { background: rgba(77,183,121,0.22); }
[data-testid="stSidebar"] details summary p,
[data-testid="stSidebar"] details summary span,
[data-testid="stSidebar"] details summary div { color: var(--gold-text); font-weight: 700; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
[data-baseweb="tab-highlight"] { background-color: var(--gold) !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: var(--gold-text) !important; }
button[data-baseweb="tab"][aria-selected="true"] p { color: var(--gold-text) !important; font-weight: 600; }
button[data-baseweb="tab"]:hover { color: var(--gold-text) !important; }
</style>
""", unsafe_allow_html=True)


def build_registry(scenario_key="baseline"):
    """Defaults -> scenario overrides -> live slider overrides."""
    reg = A.get_assumptions()
    A.apply_scenario(reg, scenario_key)
    for (group, key), v in st.session_state.get("assumption_overrides", {}).items():
        if isinstance(reg[group][key], dict):
            reg[group][key]["value"] = v
        else:
            reg[group][key] = v
    return reg


@st.cache_data(show_spinner=True)
def run_pipeline(overrides_signature, allow_network, scenario_key):
    reg = build_registry(scenario_key)
    demo = ingest.build_demolition_table(allow_network=allow_network)
    supply = model.estimate_supply(demo, reg)
    summary = model.cma_summary(supply)
    fcast = forecast.project_supply(summary, reg)
    gaps = ecosystem.gap_analysis(summary)
    void = ingest.void_report(demo)
    mc_cma, mc_nat = uncertainty.monte_carlo(summary, reg)
    tor = uncertainty.tornado(summary, reg)
    restores = ecosystem.refresh_restores(allow_network)
    return {"demo": demo, "supply": supply, "summary": summary, "forecast": fcast,
            "gaps": gaps, "void": void, "restores": restores,
            "mc_cma": mc_cma, "mc_nat": mc_nat, "tornado": tor}


def fmt_bf(x):
    if x >= 1e6:
        return f"{x/1e6:,.2f}M bf"
    if x >= 1e3:
        return f"{x/1e3:,.0f}k bf"
    return f"{x:,.0f} bf"


def fmt_cad(x):
    if x >= 1e6:
        return f"${x/1e6:,.1f}M"
    if x >= 1e3:
        return f"${x/1e3:,.0f}k"
    return f"${x:,.0f}"


def fmt_m3(x, reg):
    return f"{x/reg['bf_per_m3']:,.0f} m3"


def cap(text):
    """A caption with explicit, readable contrast (does not rely on Streamlit's
    faded caption colour, which is too light on the cream background)."""
    st.markdown(
        f"<p style='color:var(--muted);font-size:0.84rem;line-height:1.45;"
        f"margin:0.1rem 0 0.5rem'>{text}</p>", unsafe_allow_html=True)


TIER_COLOR = {"high": "#2e7d32", "medium": "#f9a825", "low": "#c62828"}
# Confidence score per market, derived from data-coverage tier (mirrors the
# Monte Carlo bands: high +/-15%, medium +/-25%, low +/-45%).
TIER_CONFIDENCE = {"high": 85, "medium": 75, "low": 55}


# --------------------------------------------------------------------------- #
# Sidebar
# --------------------------------------------------------------------------- #
st.sidebar.title("Reclaimed Lumber Intelligence")
st.sidebar.caption("Circular Construction Canada")

NAV = [
    ("", ["Overview"]),
    ("Supply", ["Municipal baseline", "Hotspots & archetypes", "Forecast & uncertainty"]),
    ("Demand", ["Demand segments", "Demand drivers", "Economics"]),
    ("Ecosystem", ["Ecosystem", "Supply gaps", "Demand gaps"]),
    ("Policy & carbon", ["Policy & capacity", "Embodied carbon"]),
    ("Platform", ["Platform roadmap", "Projects", "Matchmaking"]),
    ("Reference", ["Assumptions", "Sources & void", "How it works"]),
]
PAGES = [p for _, items in NAV for p in items]
if "page" not in st.session_state or st.session_state.page not in PAGES:
    st.session_state.page = "Overview"


def _nav_pick(gid):
    val = st.session_state.get(gid)
    if not val:
        return
    st.session_state.page = val
    for k in list(st.session_state.keys()):
        if k.startswith("navgrp_") and k != gid:
            st.session_state[k] = None


for _gi, (_header, _items) in enumerate(NAV):
    _gid = f"navgrp_{_gi}"
    if _gid not in st.session_state:
        st.session_state[_gid] = st.session_state.page if st.session_state.page in _items else None
    if _header:
        _active = st.session_state.page in _items
        with st.sidebar.expander(_header, expanded=_active):
            st.radio(f"nav {_gi}", _items, key=_gid, label_visibility="collapsed",
                     on_change=_nav_pick, args=(_gid,))
    else:
        st.sidebar.radio(f"nav {_gi}", _items, key=_gid, label_visibility="collapsed",
                         on_change=_nav_pick, args=(_gid,))
page = st.session_state.page

st.sidebar.markdown("---")
_scenarios = A.get_assumptions()["scenarios"]
scenario_key = st.sidebar.selectbox(
    "Scenario", list(_scenarios.keys()),
    format_func=lambda k: _scenarios[k]["label"])
st.sidebar.caption(_scenarios[scenario_key]["note"])

allow_network = st.sidebar.toggle(
    "Use live open-data feeds", value=False,
    help="Pull real Toronto demolition permits by year (offline fallback if unreachable).")
st.sidebar.caption("Every coefficient is sourced. See the Sources & void section.")

st.sidebar.markdown("---")
with st.sidebar.expander("Glossary"):
    st.markdown(
        "**Units**\n"
        "- **Board foot (bf)**: a measure of lumber volume, not length. 1 bf = a piece "
        "12 in x 12 in x 1 in (144 cubic inches). M bf = millions of board feet.\n"
        "- **CO2e (t)**: carbon dioxide equivalent, in tonnes. All greenhouse gases expressed "
        "as the equivalent weight of CO2.\n\n"
        "**Places**\n"
        "- **CMA (Census Metropolitan Area)**: Statistics Canada's term for a large urban area "
        "plus its commuter zone. The app covers Canada's 25 largest.\n\n"
        "**Buildings and materials**\n"
        "- **Single-family detached**: a standalone house for one household, no shared walls.\n"
        "- **Spec-ready**: lumber recovered in good enough condition and grade to be reused to "
        "specification (the usable end of the supply).\n"
        "- **Deconstruction**: taking a building apart by hand to salvage materials, as opposed to "
        "demolition (machine teardown).\n"
        "- **NLT / DLT**: nail-laminated / dowel-laminated timber. Mass-timber panels made by "
        "stacking boards, a reuse path for reclaimed lumber.\n"
        "- **ADU**: accessory dwelling unit. A small secondary home on a lot, such as a laneway "
        "house or basement suite.\n"
        "- **CRD**: construction, renovation and demolition, the waste stream this app draws from.\n\n"
        "**Model terms**\n"
        "- **Monte Carlo**: running the model thousands of times with the inputs varied, to produce "
        "a range instead of a single number.\n"
        "- **P10 / P50 / P90**: the 10th, 50th and 90th percentiles of those runs, a conservative, "
        "central and optimistic estimate.\n"
        "- **Coverage tier (high / medium / low)**: how much real data backs a metro's estimate, "
        "which sets its confidence band.\n"
        "- **Tier A / Tier B demand**: Tier A is legal today (non-structural uses); Tier B needs a "
        "building-code change for structural reuse.\n\n"
        "**Organizations and standards**\n"
        "- **SME**: small and medium-sized enterprise, here the reclaimed-wood firms in the census.\n"
        "- **ECCC**: Environment and Climate Change Canada.\n"
        "- **StatCan**: Statistics Canada.\n"
        "- **TGS**: Toronto Green Standard, the city's green-building rules, including embodied-carbon "
        "caps.")

reg = build_registry(scenario_key)
overrides_sig = tuple(sorted(
    (str(k), v) for k, v in st.session_state.get("assumption_overrides", {}).items()))
data = run_pipeline(overrides_sig, allow_network, scenario_key)
summary = data["summary"]


# --------------------------------------------------------------------------- #
# Global scenario banner (shown on every page)
# --------------------------------------------------------------------------- #
if scenario_key != "baseline":
    st.info(f"Scenario active: **{_scenarios[scenario_key]['label']}**. "
            "All figures below reflect this scenario.")

# Sections render one at a time based on the sidebar nav selection (`page`).


# --------------------------------------------------------------------------- #
# Overview
# --------------------------------------------------------------------------- #
if page == "Overview":
    st.markdown("""
    <div class="hero">
      <div class="hero-eyebrow">Circular Construction Canada</div>
      <div class="hero-title">Reclaimed Lumber Intelligence Layer</div>
      <div class="hero-sub">Where salvageable lumber will emerge across Canada's 25 largest metro
      regions, what it's worth, what recovery capacity exists, and where the bottlenecks are.
      Every coefficient is sourced, and the uncertainty carries through to every number.</div>
      <div class="hero-rule"></div>
    </div>
    """, unsafe_allow_html=True)
    nat = data["mc_nat"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Gross wood content", fmt_bf(summary["gross_bf"].sum()))
    c2.metric("Recoverable", fmt_bf(summary["recoverable_bf"].sum()))
    c3.metric("Spec-ready reusable", fmt_bf(summary["spec_ready_bf"].sum()))
    c4.metric("Reclaimed value (CAD/yr)", fmt_cad(summary["value_cad"].sum()))

    cap(f"National spec-ready, Monte Carlo P10-P50-P90: "
               f"{fmt_bf(nat['spec_ready']['p10'])}  ->  "
               f"{fmt_bf(nat['spec_ready']['p50'])}  ->  "
               f"{fmt_bf(nat['spec_ready']['p90'])} per base year. "
               "The range propagates coefficient and data-coverage uncertainty.")
    _ta = demand.tier_a_total(); _spec = summary["spec_ready_bf"].sum()
    cap(f"Demand side: buyers legal today want about {fmt_bf(_ta)}, roughly "
               f"{_ta / _spec:.0f}x current spec-ready supply, so across markets the binding "
               "constraint is supply, not appetite. See Demand for the buyer breakdown and "
               "Demand gaps for the per-market balance.")
    _av = carbon.avoided_production_t(_spec); _bio = carbon.biogenic_stored_t(_spec)
    cap(f"Embodied carbon: reusing the spec-ready supply avoids about {_av:,.0f} t CO2e "
               f"of new-lumber manufacturing a year and keeps about {_bio:,.0f} t CO2e of "
               "biogenic carbon in use. Reused components count as zero upfront carbon under "
               "Toronto Green Standard v4. See Policy & carbon.")

    st.markdown("#### National view: spec-ready reusable lumber by CMA (base year)")
    map_df = summary.merge(
        pd.DataFrame(cma_cfg.list_cmas())[["cma", "lat", "lon"]], on="cma", how="left")
    fig = px.scatter_geo(
        map_df, lat="lat", lon="lon", size="spec_ready_bf",
        color="coverage_tier", color_discrete_map=TIER_COLOR, hover_name="cma",
        hover_data={"spec_ready_bf": ":,.0f", "value_cad": ":,.0f",
                    "lat": False, "lon": False},
        scope="north america", size_max=40, labels={"coverage_tier": "Data coverage"})
    style_geo(fig, 460)
    st.plotly_chart(fig, width="stretch")

    colA, colB = st.columns(2)
    with colA:
        st.markdown("**Top markets by spec-ready supply**")
        top = summary.head(10).copy()
        top["spec_ready"] = top["spec_ready_bf"].map(fmt_bf)
        top["value/yr"] = top["value_cad"].map(fmt_cad)
        top["confidence"] = top["coverage_tier"].map(TIER_CONFIDENCE).map(lambda v: f"{v}/100")
        st.dataframe(top[["cma", "coverage_tier", "confidence", "spec_ready", "value/yr"]],
                     width="stretch", hide_index=True)
    with colB:
        st.markdown("**Top markets by reclaimed value**")
        byval = summary.sort_values("value_cad", ascending=False).head(10)
        fig = px.bar(byval, x="value_cad", y="cma", orientation="h",
                     labels={"value_cad": "CAD / yr", "cma": ""})
        style_chart(fig, 320, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, width="stretch")
    cap("Marker size = spec-ready lumber. Colour = data coverage, a confidence class based on how "
        "each metro's demolition count is known: "
        "<b>high</b> (green) = live permit feed, about +/-10% (Toronto only); "
        "<b>medium</b> (amber) = real StatCan demolition figure with the cohort split modelled, "
        "about +/-25% (5 metros); "
        "<b>low</b> (red) = inferred from dwellings x a sourced rate, about +/-45% (the other 19).")


# --------------------------------------------------------------------------- #
# 1. Municipal baseline
# --------------------------------------------------------------------------- #
if page == "Municipal baseline":
    st.subheader("Municipal demolition & housing-stock baseline")
    st.markdown("First-order, city-wide estimate of salvageable wood per market, "
                "built from demolition activity, real StatCan housing-stock age, and "
                "building archetype.")
    supply = data["supply"]
    sel = st.selectbox("CMA", cma_cfg.cma_names())
    rec = cma_cfg.get_cma(sel)
    sub = supply[supply["cma"] == sel].copy()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Dwellings (StatCan 2021)", f"{rec['dwellings']:,}")
    m2.metric("Annual demolition permits", f"{sub['permits'].sum():,.0f}")
    m3.metric("Spec-ready", fmt_bf(sub["spec_ready_bf"].sum()))
    m4.metric("Reclaimed value/yr", fmt_cad(sub["value_cad"].sum()))
    cap(("Housing-stock age: real StatCan distribution." if rec["vintage_is_real"]
                else "Housing-stock age: calibrated profile (no CMA-specific StatCan row).")
               + f" Demolition source: {sub['source'].iloc[0]}.")

    colA, colB = st.columns(2)
    with colA:
        st.markdown("**Recovery cascade (base year)**")
        funnel = pd.DataFrame({
            "stage": ["Framing lumber", "Recoverable", "Salvageable dimensional", "Spec-ready"],
            "bf": [sub["framing_bf"].sum(), sub["recoverable_bf"].sum(),
                   sub["salvageable_bf"].sum(), sub["spec_ready_bf"].sum()]})
        fig = go.Figure(go.Funnel(y=funnel["stage"], x=funnel["bf"],
                                  texttemplate="%{x:,.0f} bf"))
        style_chart(fig, 340)
        st.plotly_chart(fig, width="stretch")
    with colB:
        st.markdown("**Spec-ready by building archetype**")
        by_arch = sub.groupby("archetype", as_index=False)["spec_ready_bf"].sum()
        by_arch["label"] = by_arch["archetype"].map(lambda a: reg["archetypes"][a]["label"])
        fig = px.bar(by_arch, x="spec_ready_bf", y="label", orientation="h",
                     labels={"spec_ready_bf": "Spec-ready (bf)", "label": ""})
        style_chart(fig, 340)
        st.plotly_chart(fig, width="stretch")

    st.markdown("**Cohort detail**")
    st.dataframe(sub[["cohort", "archetype", "permits", "framing_bf", "recoverable_bf",
                      "salvageable_bf", "spec_ready_bf", "value_tier", "value_cad"]],
                 width="stretch", hide_index=True)


# --------------------------------------------------------------------------- #
# 2. Hotspots & archetypes
# --------------------------------------------------------------------------- #
if page == "Hotspots & archetypes":
    st.subheader("Neighbourhood hotspots & archetype refinement")
    st.markdown("Demolition clusters in specific neighbourhoods and repeatable building "
                "types. Across Canada in 2022, single-detached houses were 77% of the 11,988 "
                "dwellings permitted for demolition (StatCan); the other 23% were semi-detached, "
                "row, and apartment or multi-unit dwellings, which yield less dimensional lumber "
                "per teardown. Toronto, shown here with real permit data, is the worked example.")
    hotspots = pd.DataFrame([
        ("Etobicoke (Central)", 43.6435, -79.5660, 210, "sfd_postwar"),
        ("Willowdale / North York", 43.7700, -79.4100, 265, "sfd_postwar"),
        ("Scarborough (Birch Cliff)", 43.6920, -79.2600, 120, "sfd_postwar"),
        ("Leaside / East York", 43.7050, -79.3660, 145, "sfd_prewar"),
        ("The Beaches", 43.6710, -79.2960, 85, "sfd_prewar"),
        ("Don Mills", 43.7330, -79.3460, 95, "sfd_modern"),
        ("Long Branch", 43.5910, -79.5390, 110, "sfd_postwar"),
    ], columns=["neighbourhood", "lat", "lon", "annual_permits", "dominant_archetype"])
    hotspots["archetype_label"] = hotspots["dominant_archetype"].map(
        lambda a: reg["archetypes"][a]["label"])
    colA, colB = st.columns([3, 2])
    with colA:
        st.markdown("**Demolition hotspots (Toronto worked example)**")
        fig = px.scatter_geo(hotspots, lat="lat", lon="lon", size="annual_permits",
                             color="archetype_label", hover_name="neighbourhood",
                             hover_data={"annual_permits": True, "lat": False, "lon": False},
                             scope="north america", size_max=45)
        style_geo(fig, 420)
        fig.update_layout(legend_title_text="Dominant archetype")
        st.plotly_chart(fig, width="stretch")
    with colB:
        st.markdown("**Toronto demolition hotspots**")
        st.dataframe(hotspots[["neighbourhood", "annual_permits", "archetype_label"]],
                     width="stretch", hide_index=True)
        cap("Neighbourhood splits are illustrative of the method; the city total "
                   "and archetype mix are anchored to real Toronto Open Data.")
    st.info("Post-war stick-frame homes dominate the demolition stream and carry the most "
            "reusable dimensional lumber; pre-war homes are fewer but carry higher-value "
            "old-growth members; modern and low-rise multi-unit buildings yield less reclaimable "
            "lumber. Targeting the first two archetypes raises realized yield and value.")


# --------------------------------------------------------------------------- #
# 3. Forecast + uncertainty
# --------------------------------------------------------------------------- #
if page == "Forecast & uncertainty":
    st.subheader("Material flow forecast with propagated uncertainty")
    fcast = data["forecast"]
    metric = st.selectbox(
        "Metric", ["spec_ready_bf", "salvageable_bf", "recoverable_bf", "gross_bf", "value_cad"],
        format_func=lambda m: {"spec_ready_bf": "Spec-ready reusable (bf)",
                               "salvageable_bf": "Salvageable dimensional (bf)",
                               "recoverable_bf": "Recoverable (bf)",
                               "gross_bf": "Gross wood content (bf)",
                               "value_cad": "Reclaimed value (CAD)"}[m])
    sel = st.multiselect("CMAs to chart", cma_cfg.cma_names(),
                         default=["Toronto", "Vancouver", "Montreal", "Calgary"])
    if sel:
        st.markdown("**Forecast to 2036: central line with P10-P90 band**")
        sub = fcast[fcast["cma"].isin(sel)]
        fig = go.Figure()
        palette = px.colors.qualitative.Safe
        for i, cma in enumerate(sel):
            d = sub[sub["cma"] == cma]
            color = palette[i % len(palette)]
            fig.add_trace(go.Scatter(x=d["year"], y=d[metric], mode="lines+markers",
                                     name=cma, line=dict(color=color)))
            fig.add_trace(go.Scatter(
                x=list(d["year"]) + list(d["year"][::-1]),
                y=list(d[f"{metric}_high"]) + list(d[f"{metric}_low"][::-1]),
                fill="toself", fillcolor=color, opacity=0.12, line=dict(width=0),
                hoverinfo="skip", showlegend=False))
        style_chart(fig, 420, yaxis_title=metric, xaxis_title="year")
        st.plotly_chart(fig, width="stretch")

    st.markdown("### Monte Carlo uncertainty (base year)")
    nat = data["mc_nat"]
    u1, u2, u3 = st.columns(3)
    u1.metric("Spec-ready P10 (conservative)", fmt_bf(nat["spec_ready"]["p10"]))
    u2.metric("Spec-ready P50 (central)", fmt_bf(nat["spec_ready"]["p50"]))
    u3.metric("Spec-ready P90 (optimistic)", fmt_bf(nat["spec_ready"]["p90"]))
    cap("4,000 draws. Recovery coefficients are sampled jointly across all CMAs "
               "(correlated national error that doesn't diversify away), and the demolition "
               "count is sampled per CMA by coverage tier.")

    st.markdown("**Per-CMA spec-ready, P50 with P10-P90 (top 12)**")
    mc = data["mc_cma"].head(12).copy()
    fig = go.Figure(go.Bar(
        x=mc["cma"], y=mc["spec_ready_p50"],
        error_y=dict(type="data", symmetric=False,
                     array=mc["spec_ready_p90"] - mc["spec_ready_p50"],
                     arrayminus=mc["spec_ready_p50"] - mc["spec_ready_p10"]),
        marker_color=ACCENT))
    style_chart(fig, 380, yaxis_title="spec-ready bf (P50 with P10-P90)")
    st.plotly_chart(fig, width="stretch")

    st.markdown("### Sensitivity: which assumption moves the answer most")
    tor = data["tornado"]
    base_total = tor.attrs.get("base_total", summary["spec_ready_bf"].sum())
    fig = go.Figure()
    for _, r in tor.iloc[::-1].iterrows():
        lo, hi = sorted([r["low_total"], r["high_total"]])
        fig.add_trace(go.Bar(y=[r["parameter"]], x=[hi - lo], base=lo, orientation="h",
                             marker_color="#ef6c00", showlegend=False,
                             hovertemplate=f"{r['parameter']}<br>%{{base:,.0f}} to "
                                           f"{hi:,.0f} bf<extra></extra>"))
    fig.add_vline(x=base_total, line_dash="dash", line_color="rgba(128,128,128,0.7)",
                  annotation_text="central", annotation_position="top")
    style_chart(fig, 340, xaxis_title="national spec-ready bf if parameter swings low to high")
    fig.update_layout(margin=dict(l=0, r=0, t=28, b=0))
    st.plotly_chart(fig, width="stretch")
    cap("Recovery method factor (deconstruction vs demolition) dominates. That's "
               "the single highest-leverage place for CCC to act and to cut uncertainty. "
               "Policy that shifts demolition toward deconstruction moves the national "
               "number more than any other lever.")

    st.markdown("**Cumulative opportunity over the full horizon**")
    cum = forecast.cumulative_horizon(fcast, metric if metric != "value_cad" else "spec_ready_bf")
    cum_show = cum.copy()
    for c in ["central", "low", "high"]:
        cum_show[c] = cum_show[c].map(fmt_bf)
    st.dataframe(cum_show.rename(columns={"central": "central (sum)", "coverage_tier": "coverage"}),
                 width="stretch", hide_index=True)
    cap("Demand is forecast too: see Demand drivers for the demand outlook to 2036 and the "
        "supply-demand balance over time.")


# --------------------------------------------------------------------------- #
# 4. Ecosystem & gaps
# --------------------------------------------------------------------------- #
if page == "Ecosystem":
    st.subheader("The reclaimed-wood ecosystem")
    st.markdown("Circularity is two-sided: the buildings that generate waste wood, and the firms "
                "that recover, process, remake, retail, recycle, downcycle and upcycle it. This maps "
                "the real ecosystem from the ECCC company directory (September 2024) and the national "
                "SME census (Light House for ECCC, March 2026).")

    comp = ecosystem.company_table()
    restore_count, restore_src, restore_live = data["restores"]
    e1, e2, e3, e4 = st.columns(4)
    e1.metric("Named companies", f"{len(comp)}")
    e2.metric("National SMEs (census)", f"{companies.NATIONAL_SME_TOTAL}")
    e3.metric("Habitat ReStores", f"{restore_count}")
    e4.metric("Provinces covered", f"{comp['province'].nunique()}")
    cap(f"ReStore count source: {restore_src}. Turn on the sidebar feed toggle to refresh "
               "it live; the named directory falls back to the dated ECCC snapshot either way.")

    st.markdown("#### The circular value chain")
    sc = ecosystem.stage_counts_national()
    xs = [16, 160, 304, 448, 592]
    nodes = ""
    for i, stg in enumerate(companies.VALUE_CHAIN):
        x = xs[i]
        nodes += (f'<rect x="{x}" y="70" width="120" height="58" rx="11" class="vnode"/>'
                  f'<text x="{x+60}" y="95" text-anchor="middle" class="vtext" font-size="13" font-weight="700">{stg}</text>'
                  f'<text x="{x+60}" y="116" text-anchor="middle" class="vcount" font-family="JetBrains Mono, monospace" font-size="12">{sc[stg]} firms</text>')
        if i < 4:
            nodes += f'<path d="M{x+120},99 L{xs[i+1]},99" class="vedge" marker-end="url(#vh)"/>'
    vsvg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 728 165" font-family="Inter, Segoe UI, Arial, sans-serif">
  <style>
    .vnode{{fill:#FFFFFF;stroke:#E2E7DE;stroke-width:1.5}} .vtext{{fill:#14532D}} .vcount{{fill:#2F7D4F}}
    .vedge{{stroke:#2F7D4F;stroke-width:2;fill:none}} .vacc{{fill:#2F7D4F}} .vloop{{stroke:#2F7D4F;stroke-width:1.6;fill:none;stroke-dasharray:5 4}} .vlbl{{fill:#2F7D4F}}
    @media (prefers-color-scheme: dark){{
      .vnode{{fill:#15151B;stroke:#2A2A31}} .vtext{{fill:#EAF3EC}} .vcount{{fill:#5CCF95}}
      .vedge{{stroke:#4DB779}} .vacc{{fill:#4DB779}} .vloop{{stroke:#4DB779}} .vlbl{{fill:#5CCF95}}
    }}
  </style>
  <defs><marker id="vh" markerWidth="9" markerHeight="9" refX="7.5" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" class="vacc"/></marker></defs>
  <path d="M652,70 L652,26 L76,26 L76,70" class="vloop" marker-end="url(#vh)"/>
  <text x="364" y="20" text-anchor="middle" class="vlbl" font-family="JetBrains Mono, monospace" font-size="11">reuse closes the loop</text>
  {nodes}
</svg>'''
    _b = base64.b64encode(vsvg.encode("utf-8")).decode()
    st.markdown(f'<div style="max-width:760px;margin:2px auto 6px">'
                f'<img alt="circular value chain" style="width:100%" '
                f'src="data:image/svg+xml;base64,{_b}"/></div>', unsafe_allow_html=True)
    cap("Firm counts are the national SME census by value-chain step (Light House, March "
               "2026). Retail dominates because it includes 102 Habitat for Humanity ReStores.")

    st.markdown("#### Company directory")
    all_acts = sorted({a for c in companies.list_companies() for a in c["activities"]})
    f1, f2 = st.columns(2)
    prov_pick = f1.multiselect("Province", sorted(comp["province"].unique()))
    act_pick = f2.multiselect("Activity", all_acts)
    view = comp.copy()
    if prov_pick:
        view = view[view["province"].isin(prov_pick)]
    if act_pick:
        view = view[view["activities"].apply(lambda acts: any(a in acts for a in act_pick))]
    show = view.copy()
    show["activities"] = show["activities"].apply(lambda a: ", ".join(a))
    show["stages"] = show["stages"].apply(lambda a: ", ".join(a))
    colA, colB = st.columns([3, 2])
    with colA:
        st.dataframe(show[["name", "province", "activities", "stages", "website"]],
                     width="stretch", hide_index=True, height=360)
    with colB:
        st.markdown("**Companies by province**")
        prov_counts = comp.groupby("province").size().reset_index(name="companies")
        prov_counts["lat"] = prov_counts["province"].map(lambda p: companies.PROVINCE_CENTROID[p][0])
        prov_counts["lon"] = prov_counts["province"].map(lambda p: companies.PROVINCE_CENTROID[p][1])
        fig = px.scatter_geo(prov_counts, lat="lat", lon="lon", size="companies",
                             color="companies", color_continuous_scale="Greens",
                             hover_name="province", scope="north america", size_max=34)
        style_geo(fig, 360)
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(fig, width="stretch")

    st.markdown("#### Recovery pathways (recycling, downcycling, upcycling and more)")
    ac = ecosystem.activity_counts()
    fig = px.bar(ac, x="companies", y="activity", orientation="h",
                 labels={"companies": "named companies", "activity": ""})
    fig.update_traces(marker_color=ACCENT)
    fig.update_layout(yaxis=dict(autorange="reversed"))
    style_chart(fig, 320)
    st.plotly_chart(fig, width="stretch")

    st.markdown("#### Storage and warehousing")
    st.markdown("Warehousing is the connective layer between recovery and reuse, and it is the "
                "thinnest part of the map. The clearest physical nodes today are the "
                f"{restore_count} Habitat ReStores that hold and resell salvaged material; dedicated "
                "reclaimed-lumber warehousing is sparse, which is why storage and standards rank "
                "among the bottlenecks. A verified warehouse and capacity registry is a Phase-2 build.")

    st.markdown("#### The demand side of the ecosystem")
    st.markdown("The value chain above is the supply half. The buyers and channels that absorb "
                "reclaimed wood are the demand half, and they were missing from the map. This is who "
                "pulls material through, how it reaches them, and what holds demand back.")
    da = pd.DataFrame(demand_ecosystem.DEMAND_ACTORS,
                      columns=["actor", "kind", "role", "scale", "source"])
    st.markdown("**Who buys, and the channels that reach them**")
    st.dataframe(da.rename(columns={"actor": "buyer / channel"}),
                 width="stretch", hide_index=True)
    cap("Mass-timber manufacturers are marked adjacent: they buy new engineered feedstock, so they "
        "are a demand signal for wood but not for reclaimed today.")

    cda, cdb = st.columns(2)
    with cda:
        st.markdown("**Material-exchange channels**")
        st.dataframe(pd.DataFrame(demand_ecosystem.EXCHANGES, columns=["Channel", "Role", "Source"]),
                     width="stretch", hide_index=True)
        cap("These are why the app coordinates supply to buyers rather than running a marketplace: "
            "the marketplaces already exist.")
    with cdb:
        st.markdown("**Coordinators connecting the two sides**")
        st.dataframe(pd.DataFrame(demand_ecosystem.COORDINATORS,
                                  columns=["Organization", "Role", "Source"]),
                     width="stretch", hide_index=True)
        cap("The connective layer between salvage supply and local buyers.")

    st.markdown("**Why buyers default to new lumber**")
    st.dataframe(pd.DataFrame(demand_ecosystem.DEMAND_BARRIERS,
                              columns=["Barrier", "Detail", "Source"]),
                 width="stretch", hide_index=True)
    cap("The top barrier is the missing re-grading and certification path for structural reuse, "
        "which caps the largest demand tier before economics apply.")

    st.markdown("#### Sector capacity context")
    st.dataframe(pd.DataFrame(companies.SECTOR_CONTEXT, columns=["Indicator", "Value", "Source"]),
                 width="stretch", hide_index=True)
    cap("Confidence and limits: the supply-side firm directory and the national SME census are "
               "real and dated, so that half of the map is solid. The demand-side actors are real "
               "organizations and sourced market structure; some scale figures are approximate. "
               "Per-market capacity in the gap analyses is the census allocated to provinces, so it "
               "is directional, not a verified per-site audit.")



# --------------------------------------------------------------------------- #
# Supply gaps
# --------------------------------------------------------------------------- #
if page == "Supply gaps":
    st.subheader("Where supply outruns the in-province ecosystem")
    st.markdown("Each CMA's spec-ready supply is set against the recovery and processing capacity "
                "in its province, flagging markets where supply is high relative to the firms that "
                "can handle it.")
    st.markdown("#### Gap analysis: supply against the in-province ecosystem")
    gaps = data["gaps"]
    n_gap = (gaps["gap_flag"] != "Workable base").sum()
    g1, g2 = st.columns(2)
    g1.metric("CMAs analyzed", len(gaps))
    g2.metric("Markets flagged thin or under-served", int(n_gap))
    gshow = gaps.copy()
    gshow["spec_ready"] = gshow["spec_ready_bf"].map(fmt_bf)
    gshow["bf per SME"] = gshow["bf_per_sme"].map(lambda x: fmt_bf(x) if x != float("inf") else "n/a")
    st.dataframe(gshow[["cma", "province", "spec_ready", "province_smes", "bf per SME", "gap_flag"]],
                 width="stretch", hide_index=True)
    cap("Province SME counts come from the national census of 252 scaled by the Light House "
               "provincial distribution. A market is flagged where supply is high relative to the "
               "recovery and processing firms operating in its province.")
    cap("Confidence and limits: capacity is the national census allocated to provinces, so "
               "this flags directional pressure, not audited per-firm capacity.")


# --------------------------------------------------------------------------- #
# Demand & economics
# --------------------------------------------------------------------------- #
if page == "Demand segments":
    st.subheader("Demand side: who buys reclaimed wood")
    st.markdown("The supply model says how much reusable lumber appears. This answers the harder "
                "question the feedback raised: who buys it, what it's worth, and why so much "
                "recoverable wood still isn't reclaimed.")

    dem = pd.DataFrame(demand.demand_table())
    spec_ready = data["summary"]["spec_ready_bf"].sum()
    ta, tb = demand.tier_a_total(), demand.tier_b_total()
    d1, d2, d3 = st.columns(3)
    ta_lo, ta_hi = demand.tier_a_range()
    tb_lo, tb_hi = demand.tier_b_range()
    d1.metric("Spec-ready supply (model, base yr)", fmt_bf(spec_ready))
    d2.metric("Demand legal today (Tier A)", fmt_bf(ta),
              f"{fmt_bf(ta_lo)}-{fmt_bf(ta_hi)} band", delta_color="off")
    d3.metric("Demand if code allows reuse (Tier B)", fmt_bf(tb),
              f"{fmt_bf(tb_lo)}-{fmt_bf(tb_hi)} band", delta_color="off")
    st.info("Latent demand dwarfs current spec-ready supply, so the binding constraint is supply "
            "and coordination, not appetite. Visible demand stays small because buyers cannot "
            "commit to material they cannot see coming. That is the gap this layer targets.")

    st.markdown("#### Demand by segment")
    dshow = dem.copy()
    dshow["tier"] = dshow["tier"].map({"A": "A: legal today", "B": "B: needs code change"})
    dshow["point"] = dshow["point_bf"]
    fig = px.bar(dshow, x="point", y="segment", orientation="h", color="tier",
                 color_discrete_map={"A: legal today": ACCENT, "B: needs code change": "#9A9A92"},
                 labels={"point": "demand absorption (bf/yr)", "segment": "", "tier": ""})
    fig.update_layout(yaxis=dict(autorange="reversed"), legend=dict(orientation="h", y=1.08))
    style_chart(fig, 460)
    st.plotly_chart(fig, width="stretch")
    st.markdown("**Segment detail**")
    seg_tbl = dem.copy()
    seg_tbl["absorption"] = seg_tbl.apply(lambda r: f"{fmt_bf(r['low_bf'])} - {fmt_bf(r['high_bf'])}", axis=1)
    seg_tbl["tier"] = seg_tbl["tier"].map({"A": "legal today", "B": "needs code change"})
    st.dataframe(seg_tbl[["segment", "tier", "absorption", "note"]],
                 width="stretch", hide_index=True)

    st.markdown("#### Market context")
    st.dataframe(pd.DataFrame(demand.MARKET_CONTEXT, columns=["Indicator", "Value", "Source"]),
                 width="stretch", hide_index=True)
    cap("Confidence and limits: these segment volumes are bottom-up board-foot estimates shown as "
               "ranges, calibrated to the market structure above. The forces around them, the "
               "application mix, macro and policy drivers, certification levers and the buyer "
               "ecosystem, are separately sourced. See Demand drivers and Ecosystem.")


# --------------------------------------------------------------------------- #
# Demand drivers
# --------------------------------------------------------------------------- #
if page == "Demand drivers":
    st.subheader("Demand drivers: what pulls reclaimed wood through the market")
    st.markdown("The segments page sizes demand from the bottom up. This page gives it the same "
                "depth the supply side has: where demand sits by application, the macro and policy "
                "forces pulling it, the certification mechanisms specifiers respond to, the "
                "competitive substitute, and what buyers pay.")

    st.markdown("#### Macro drivers")
    md = demand_drivers.MACRO_DRIVERS
    g1, g2, g3 = st.columns(3)
    g1.metric("NA green buildings", "US$204B", "to US$377B by 2030", delta_color="off")
    g2.metric("Wellness real estate", "US$584B", "to US$1.1T by 2029", delta_color="off")
    g3.metric("Green-building growth", "10.6%/yr", "vs general construction", delta_color="off")
    st.dataframe(pd.DataFrame(md, columns=["Driver", "Value", "Why it matters", "Source"]),
                 width="stretch", hide_index=True)
    cap("Reclaimed wood rides demand-pull from large, fast-growing green and wellness building "
        "markets, not just from its own niche.")

    st.markdown("#### Demand by application")
    am = demand_drivers.APPLICATION_MIX
    amdf = pd.DataFrame(am, columns=["application", "mid", "range", "note", "source"])
    fig = px.bar(amdf, x="mid", y="application", orientation="h",
                 labels={"mid": "indicative share of demand (%)", "application": ""})
    fig.update_traces(marker_color=ACCENT)
    fig.update_layout(yaxis=dict(autorange="reversed"))
    style_chart(fig, 300)
    st.plotly_chart(fig, width="stretch")
    st.dataframe(amdf[["application", "range", "note", "source"]].rename(
        columns={"range": "observed range"}), width="stretch", hide_index=True)
    cap("Furniture and flooring lead. Shares come from market-research firms that disagree "
        "firm-to-firm, so the bars are reconciled midpoints and the table shows the observed range. "
        "End-use skews commercial today (about 58%), with residential growing faster (Grand View, 2022).")

    st.markdown("#### Demand outlook and the supply-demand balance to 2036")
    base_year = int(val(reg["forecast"]["base_year"]))
    horizon = int(val(reg["forecast"]["horizon_years"]))
    ta = demand.tier_a_total()
    tb_tot = demand.tier_b_total()
    code_path = st.checkbox(
        "Scenario: a structural-reuse code path opens in 2030 (unlocks Tier B)", value=False)
    dfc = pd.DataFrame(demand_drivers.demand_forecast(
        ta, base_year=base_year, horizon=horizon,
        code_year=2030 if code_path else None, base_tier_b=tb_tot))
    sup = data["forecast"].groupby("year", as_index=False).agg(
        s=("spec_ready_bf", "sum"), s_lo=("spec_ready_bf_low", "sum"),
        s_hi=("spec_ready_bf_high", "sum"))
    MM = 1e6
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(dfc["year"]) + list(dfc["year"][::-1]),
        y=list(dfc["high"] / MM) + list(dfc["low"][::-1] / MM),
        fill="toself", fillcolor="#9A9A92", opacity=0.12, line=dict(width=0),
        hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=dfc["year"], y=dfc["central"] / MM, mode="lines+markers",
                             name="Demand (legal today)", line=dict(color="#5C5C54")))
    fig.add_trace(go.Scatter(
        x=list(sup["year"]) + list(sup["year"][::-1]),
        y=list(sup["s_hi"] / MM) + list(sup["s_lo"][::-1] / MM),
        fill="toself", fillcolor=ACCENT, opacity=0.14, line=dict(width=0),
        hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=sup["year"], y=sup["s"] / MM, mode="lines+markers",
                             name="Spec-ready supply", line=dict(color=ACCENT)))
    style_chart(fig, 430, xaxis_title="year", yaxis_title="M board feet per year",
                legend=dict(orientation="h", y=1.08))
    st.plotly_chart(fig, width="stretch")
    g = demand_drivers.DEMAND_GROWTH
    end = dfc.iloc[-1]
    sup_end = sup.iloc[-1]
    o1, o2, o3 = st.columns(3)
    o1.metric(f"Demand {base_year}", fmt_bf(ta))
    o2.metric(f"Demand {base_year + horizon} (central)", fmt_bf(end["central"]))
    o3.metric(f"Supply {base_year + horizon} (central)", fmt_bf(sup_end["s"]))
    cap(f"Demand grows at about {g['central'] * 100:.0f}% a year (band {g['low'] * 100:.0f} to "
        f"{g['high'] * 100:.0f}%); supply is the national spec-ready forecast. The gap persists "
        "across the horizon: demand stays well above spec-ready supply. The code-path scenario "
        "steps demand far higher by unlocking structural reuse.")
    cap("Confidence and limits: this is a growth-rate projection from sourced market rates, not a "
        "bottom-up yearly demand model, and the band reflects the growth range rather than full "
        "Monte Carlo. " + demand_drivers.DEMAND_FORECAST_SOURCE)

    st.markdown("#### Policy and procurement pull (Canada)")
    st.markdown("The structural demand engine. Embodied-carbon procurement and codes increasingly "
                "favour reused material, which counts as zero or low upfront carbon.")
    pol = pd.DataFrame(demand_drivers.POLICY_DEMAND,
                       columns=["Driver", "Jurisdiction", "Status", "When", "Detail", "Source"])
    st.dataframe(pol, width="stretch", hide_index=True)
    cap("In force items create demand today; direction-setting items signal where it is heading. "
        "Toronto's top tier becomes mandatory for all new development by 2028.")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Why specifiers choose it")
        st.dataframe(pd.DataFrame(demand_drivers.CERT_LEVERS,
                                  columns=["Lever", "Mechanism", "Source"]),
                     width="stretch", hide_index=True)
        cap("LEED v4.1 counts reused material at 200% of its cost, a concrete reason architects "
            "specify reclaimed wood.")
    with c2:
        st.markdown("#### The competitive substitute")
        st.dataframe(pd.DataFrame(demand_drivers.SUBSTITUTE,
                                  columns=["Indicator", "Value", "Note", "Source"]),
                     width="stretch", hide_index=True)
        cap("The threat to real wood is wood-look vinyl, not virgin lumber. Reclaimed defends a "
            "premium-aesthetic position the look-alikes cannot copy.")

    st.markdown("#### What buyers pay")
    st.dataframe(pd.DataFrame(demand_drivers.PRICE_POINTS,
                              columns=["Item", "Value", "Note", "Source"]),
                 width="stretch", hide_index=True)
    cap("Confidence and limits: macro, policy, certification and substitute figures are from "
        "government, standards bodies and trade-press primary reporting and are firm. Application "
        "shares and reclaimed pricing are market-research and supplier estimates, so they read as "
        "ranges, not precise values.")


# --------------------------------------------------------------------------- #
# Economics
# --------------------------------------------------------------------------- #
if page == "Economics":
    st.subheader("Economics and why reuse stalls")
    st.markdown("Reclaimed lumber sells at a premium, yet recovery costs more and takes longer. "
                "This is the economics behind the supply leak, and the constraints that hold it back.")
    st.markdown("#### Economics")
    ec = demand.ECONOMICS
    rp = ec["reclaimed_premium"]; dp = ec["deconstruction_premium"]
    m1, m2, m3 = st.columns(3)
    m1.metric("Reclaimed price premium", f"{int(rp[0]*100)}-{int(rp[2]*100)}%", "over virgin", delta_color="off")
    m2.metric("Deconstruction cost premium", f"{int(dp[0]*100)}-{int(dp[2]*100)}%", "over demolition", delta_color="off")
    m3.metric("Salvage value, Metro Vancouver", "$342M/yr", "2020", delta_color="off")
    cap("Reclaimed lumber sells at a premium, yet recovery costs more and takes longer. "
               "Sources: Light House SME report (March 2026); Vancouver Economic Commission, "
               "Unbuilders & BCIT, Business Case for Deconstruction (July 2020).")

    st.markdown("#### Why recoverable wood is not reclaimed")
    bt = pd.DataFrame(demand.BOTTLENECKS)
    bt = bt.rename(columns={"rank": "#", "name": "bottleneck", "side": "binds on", "note": "explanation"})
    st.dataframe(bt[["#", "bottleneck", "binds on", "explanation"]],
                 width="stretch", hide_index=True)
    cap("Ranked by severity. The largest demand tier (structural reuse) is capped by code "
               "before economics even apply, and the next constraint is the missing forward supply "
               "signal, which is exactly what a predictive layer supplies.")


# --------------------------------------------------------------------------- #
# Demand gaps (mirror of Supply gaps)
# --------------------------------------------------------------------------- #
if page == "Demand gaps":
    st.subheader("Where demand outruns local supply")
    st.markdown("The mirror of supply gaps. National legal-today demand (Tier A) is allocated "
                "across the 25 CMAs by population share, then set against each market's spec-ready "
                "supply. It shows where buyers want more reclaimed wood than the local market can "
                "currently deliver.")

    pop = {r["cma"]: r["population"] for r in cma_cfg.list_cmas()}
    total_pop = sum(pop.values()) or 1
    tier_a = demand.tier_a_total()
    dg = data["summary"][["cma", "spec_ready_bf"]].copy()
    dg["spec_ready_bf"] = pd.to_numeric(dg["spec_ready_bf"], errors="coerce").fillna(0.0)
    dg["population"] = dg["cma"].map(pop).fillna(0)
    dg["demand_bf"] = tier_a * (dg["population"] / total_pop)
    dg["gap_bf"] = dg["demand_bf"] - dg["spec_ready_bf"]
    dg["coverage"] = (dg["spec_ready_bf"] / dg["demand_bf"].where(dg["demand_bf"] > 0)).fillna(0.0)
    dg = dg.sort_values("gap_bf", ascending=False).reset_index(drop=True)

    unmet = int((dg["coverage"] < 1).sum())
    dm1, dm2, dm3 = st.columns(3)
    dm1.metric("Demand legal today (Tier A)", fmt_bf(tier_a))
    dm2.metric("Spec-ready supply (base yr)", fmt_bf(dg["spec_ready_bf"].sum()))
    dm3.metric("Markets with unmet demand", f"{unmet} of {len(dg)}")

    st.markdown("**Demand vs supply by market (top 12)**")
    top = dg.head(12).melt(id_vars="cma", value_vars=["demand_bf", "spec_ready_bf"],
                           var_name="series", value_name="bf")
    top["series"] = top["series"].map({"demand_bf": "allocated demand",
                                       "spec_ready_bf": "spec-ready supply"})
    fig = px.bar(top, x="bf", y="cma", color="series", orientation="h", barmode="group",
                 color_discrete_map={"allocated demand": "#9A9A92", "spec-ready supply": ACCENT},
                 labels={"bf": "board feet per year", "cma": "", "series": ""})
    fig.update_layout(yaxis=dict(autorange="reversed"), legend=dict(orientation="h", y=1.06))
    style_chart(fig, 460)
    st.plotly_chart(fig, width="stretch")

    st.markdown("**All 25 markets**")
    show = dg.copy()
    show["allocated demand"] = show["demand_bf"].map(fmt_bf)
    show["spec-ready supply"] = show["spec_ready_bf"].map(fmt_bf)
    show["demand gap"] = show["gap_bf"].map(fmt_bf)
    show["coverage"] = (show["coverage"] * 100).round(0).astype(int).astype(str) + "%"
    st.dataframe(show[["cma", "allocated demand", "spec-ready supply", "demand gap", "coverage"]],
                 width="stretch", hide_index=True)
    cap("Allocation assumption: national Tier A demand split by each CMA's share of "
               "population (StatCan 2021 Census, Table 98-10-0014). Coverage is local spec-ready "
               "supply divided by allocated local demand. Demand exceeds supply in nearly every "
               "market, which is the core finding: the binding constraint is supply, not appetite.")
    cap("Confidence and limits: demand is allocated to metros by population share and supply "
               "is the model estimate, so this is a directional balance, not measured local demand.")


# --------------------------------------------------------------------------- #
# Policy & capacity (third named gap)
# --------------------------------------------------------------------------- #
if page == "Policy & capacity":
    st.subheader("Policy ambition against recovery capacity")
    st.markdown("The third gap the brief names: municipalities with ambitious circular goals but "
                "limited operational capacity. Each metro's construction-specific policy ambition "
                "is scored 0-3 from documented programs, then set against the recovery and "
                "processing firms in its province and its spec-ready supply.")

    prov_smes = ecosystem.province_company_estimate()
    med_supply = data["summary"]["spec_ready_bf"].median()
    rows = []
    for _, r in data["summary"].iterrows():
        cma = r["cma"]; prov = ecosystem.CMA_PROVINCE.get(cma, "")
        score, label, initiative, src = policy.policy_for(cma, prov)
        smes = prov_smes.get(prov, 0)
        per_firm = r["spec_ready_bf"] / smes if smes else float("inf")
        if score >= 2 and per_firm > 60_000:
            flag = "Ambition ahead of capacity"
        elif score >= 2:
            flag = "Aligned: policy and capacity"
        elif r["spec_ready_bf"] >= med_supply:
            flag = "Policy opportunity: supply, weak policy"
        else:
            flag = "Early: low policy, low supply"
        rows.append({"cma": cma, "province": prov, "score": score,
                     "policy": f"{score}/3 {label}", "province_firms": smes,
                     "spec_ready_bf": r["spec_ready_bf"], "flag": flag,
                     "initiative": initiative, "source": src})
    pol = pd.DataFrame(rows)

    p1, p2, p3 = st.columns(3)
    p1.metric("Aligned leaders", int((pol["flag"].str.startswith("Aligned")).sum()))
    p2.metric("Policy opportunities", int((pol["flag"].str.startswith("Policy opportunity")).sum()))
    p3.metric("Ambition ahead of capacity", int((pol["flag"] == "Ambition ahead of capacity").sum()))

    st.markdown("**Policy ambition vs in-province capacity**")
    fig = px.scatter(pol, x="score", y="province_firms", size="spec_ready_bf", color="flag",
                     hover_name="cma", size_max=34,
                     labels={"score": "policy ambition (0-3)  ->",
                             "province_firms": "in-province recovery firms  ->", "flag": ""})
    xmid = 1.5; ymid = pol["province_firms"].median(); ymax = pol["province_firms"].max()
    fig.add_vline(x=xmid, line_dash="dot", line_color="rgba(128,128,128,0.45)")
    fig.add_hline(y=ymid, line_dash="dot", line_color="rgba(128,128,128,0.45)")
    for qx, qy, txt in [(0.4, ymax, "Policy opportunity"),
                        (2.6, ymax, "Aligned: policy + capacity"),
                        (0.4, 0, "Early"),
                        (2.6, 0, "Ambition ahead of capacity")]:
        fig.add_annotation(x=qx, y=qy, text=txt, showarrow=False,
                           font=dict(size=10, color="#5F6368"))
    fig.update_xaxes(range=[-0.3, 3.3], tickvals=[0, 1, 2, 3])
    fig.update_layout(legend=dict(orientation="h", y=1.18))
    style_chart(fig, 400)
    st.plotly_chart(fig, width="stretch")

    st.markdown("**All metros**")
    show = pol.sort_values(["score", "spec_ready_bf"], ascending=[False, False]).copy()
    show["spec-ready"] = show["spec_ready_bf"].map(fmt_bf)
    st.dataframe(show[["cma", "policy", "province_firms", "spec-ready", "flag"]],
                 width="stretch", hide_index=True)

    st.markdown("#### Documented initiatives (leaders)")
    lead = pol[pol["score"] >= 2].sort_values("score", ascending=False)
    st.dataframe(lead[["cma", "policy", "initiative", "source"]].drop_duplicates("cma"),
                 width="stretch", hide_index=True)
    cap("Most metros sit in 'policy opportunity': real recoverable supply with little "
               "construction-specific circular policy. The leaders (Vancouver, Toronto) pair policy "
               "with capacity. Scores come from documented programs; where no local by-law is "
               "documented a metro defaults to its provincial signal. Federal backdrop: Canada "
               "Green Buildings Strategy (2024) addresses embodied carbon.")


# --------------------------------------------------------------------------- #
# Embodied carbon
# --------------------------------------------------------------------------- #
if page == "Embodied carbon":
    st.subheader("Embodied carbon avoided by reuse")
    st.markdown("Reusing reclaimed lumber instead of buying new avoids manufacturing emissions and "
                "keeps biogenic carbon locked in service. This ties the supply estimate to "
                "municipal embodied-carbon goals.")

    spec = data["summary"]["spec_ready_bf"].sum()
    av = carbon.avoided_production_t(spec); bio = carbon.biogenic_stored_t(spec)
    c1, c2, c3 = st.columns(3)
    c1.metric("Avoided manufacturing", f"{av:,.0f} t CO2e/yr", "not making new lumber", delta_color="off")
    c2.metric("Biogenic carbon kept in use", f"{bio:,.0f} t CO2e/yr", "vs landfill or burning", delta_color="off")
    c3.metric("Total climate benefit", f"{av + bio:,.0f} t CO2e/yr", delta_color="off")
    st.info(f"Toronto Green Standard v4 lets reused or salvaged components count as zero upfront "
            f"embodied carbon against its {carbon.TGS_TIER2_CAP} (Tier 2) and {carbon.TGS_TIER3_CAP} "
            "(Tier 3) kg CO2e/m2 caps, so reclaimed lumber directly helps projects meet the cap.")
    cars = (av + bio) / 4.6
    st.success(f"In plain terms, that total climate benefit is roughly {cars:,.0f} passenger cars "
               "off the road for a year (US EPA: 4.6 t CO2e per vehicle per year), combining "
               "avoided manufacturing and biogenic carbon kept in use.")

    st.markdown("#### Carbon benefit by market")
    cb = data["summary"][["cma", "spec_ready_bf"]].copy()
    cb["avoided_t"] = cb["spec_ready_bf"].map(carbon.avoided_production_t)
    cb["stored_t"] = cb["spec_ready_bf"].map(carbon.biogenic_stored_t)
    cb = cb.sort_values("avoided_t", ascending=False)
    fig = px.bar(cb.head(12), x="avoided_t", y="cma", orientation="h",
                 labels={"avoided_t": "t CO2e/yr avoided (manufacturing)", "cma": ""})
    fig.update_traces(marker_color=ACCENT)
    fig.update_layout(yaxis=dict(autorange="reversed"))
    style_chart(fig, 420)
    st.plotly_chart(fig, width="stretch")

    st.markdown("**Detail by market**")
    show = cb.copy()
    show["spec-ready"] = show["spec_ready_bf"].map(fmt_bf)
    show["avoided (t CO2e/yr)"] = show["avoided_t"].map(lambda x: f"{x:,.0f}")
    show["biogenic kept (t CO2e/yr)"] = show["stored_t"].map(lambda x: f"{x:,.0f}")
    st.dataframe(show[["cma", "spec-ready", "avoided (t CO2e/yr)", "biogenic kept (t CO2e/yr)"]],
                 width="stretch", hide_index=True)
    cap("Coefficients: avoided manufacturing 62 kg CO2e/m3 and biogenic carbon 785 kg "
               "CO2e/m3 of softwood lumber (Athena Institute CtoG LCA, 2018; Review of Canadian "
               "harvested-wood-product emission factors, 2024), at 0.00236 m3 per board foot. "
               "Displacement check: about 280 kg CO2e/tonne avoided by reuse (UK Forest Research, "
               "2025).")


# --------------------------------------------------------------------------- #
# 5. Platform roadmap
# --------------------------------------------------------------------------- #
if page == "Platform roadmap":
    st.subheader("From intelligence layer to coordination platform")
    st.markdown("This app is the defensible intelligence layer. This section is how Circular "
                "Construction Canada turns it into a live coordination platform: a phased build, a "
                "build-versus-partner split, and a clean integration contract.")

    phases = [
        ("Phase 0", "now", "Defensible intelligence layer",
         "This app. One live connector (Toronto), modelled coverage for 24 metros, a transparent "
         "assumptions registry, and an honest void report. Buys credibility CCC can defend."),
        ("Phase 1", "0 to 6 months", "Widen real coverage",
         "Add machine-readable permit feeds (Vancouver, Ottawa, Calgary, Hamilton) behind the same "
         "schema. Coverage tiers climb and confidence bands tighten on their own."),
        ("Phase 2", "6 to 18 months", "Project intake and verified actors",
         "Open the project store to contractors to register sites; verify the processor, warehouse "
         "and buyer directory. Gap analysis runs on real infrastructure data."),
        ("Phase 3", "18 months and beyond", "Live matchmaking",
         "Notify the nearest processor and buyer when a high-yield demolition is permitted, and let "
         "them claim the material. The coordination platform the brief envisions."),
    ]
    xs = [16, 196, 376, 556]
    nodes = ""
    for i, (ph, when, _t, _d) in enumerate(phases):
        x = xs[i]
        nodes += (f'<rect x="{x}" y="60" width="156" height="62" rx="11" class="vnode"/>'
                  f'<text x="{x+78}" y="86" text-anchor="middle" class="vtext" font-size="14" font-weight="700">{ph}</text>'
                  f'<text x="{x+78}" y="107" text-anchor="middle" class="vcount" font-family="JetBrains Mono, monospace" font-size="11">{when}</text>')
        if i < 3:
            nodes += f'<path d="M{x+156},91 L{xs[i+1]},91" class="vedge" marker-end="url(#ph)"/>'
    rsvg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 728 150" font-family="Inter, Segoe UI, Arial, sans-serif">
  <style>
    .vnode{{fill:#FFFFFF;stroke:#E2E7DE;stroke-width:1.5}} .vtext{{fill:#14532D}} .vcount{{fill:#2F7D4F}}
    .vedge{{stroke:#2F7D4F;stroke-width:2;fill:none}} .vacc{{fill:#2F7D4F}} .vlbl{{fill:#2F7D4F}}
    @media (prefers-color-scheme: dark){{
      .vnode{{fill:#15151B;stroke:#2A2A31}} .vtext{{fill:#EAF3EC}} .vcount{{fill:#5CCF95}}
      .vedge{{stroke:#4DB779}} .vacc{{fill:#4DB779}} .vlbl{{fill:#5CCF95}}
    }}
  </style>
  <defs><marker id="ph" markerWidth="9" markerHeight="9" refX="7.5" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" class="vacc"/></marker></defs>
  <text x="364" y="28" text-anchor="middle" class="vlbl" font-family="JetBrains Mono, monospace" font-size="11">each connector lands behind one canonical schema, so the model stays put</text>
  {nodes}
</svg>'''
    _b = base64.b64encode(rsvg.encode("utf-8")).decode()
    st.markdown(f'<div style="max-width:820px;margin:2px auto 8px">'
                f'<img alt="phased roadmap" style="width:100%" '
                f'src="data:image/svg+xml;base64,{_b}"/></div>', unsafe_allow_html=True)

    pc = st.columns(4)
    for col, (ph, when, title, desc) in zip(pc, phases):
        with col:
            st.markdown(f"**{ph}**  \n*{when}*")
            st.markdown(f"**{title}**")
            cap(desc)

    st.markdown("#### Build versus partner")
    st.dataframe(pd.DataFrame([
        {"Capability": "Canonical data model and assumptions registry", "Call": "Build",
         "Why": "CCC's proprietary asset and the source of its credibility. Cannot be outsourced."},
        {"Capability": "Permit ingestion connectors", "Call": "Build thin",
         "Why": "Write a connector where a municipality publishes open data. Do not rebuild the municipal system."},
        {"Capability": "Forecasting and gap-analysis engine", "Call": "Build",
         "Why": "The method is the differentiator. Keep it in house and transparent."},
        {"Capability": "Matchmaking marketplace", "Call": "Partner",
         "Why": "Material-exchange marketplaces exist. Send them supply signals instead of rebuilding a marketplace."},
        {"Capability": "Hosting and identity", "Call": "Partner",
         "Why": "Commodity managed cloud. No reason to operate infrastructure."},
    ]), width="stretch", hide_index=True)

    st.markdown("#### Integration: the canonical schema is the contract")
    i1, i2, i3 = st.columns(3)
    with i1:
        st.markdown("**Inbound**")
        cap("Municipal open-data portals and provincial assessment data feed the canonical "
                   "demolition and housing tables.")
    with i2:
        st.markdown("**Internal**")
        cap("The assumptions registry and project store let CCC and partners correct and "
                   "extend the model without touching code.")
    with i3:
        st.markdown("**Outbound**")
        cap("A read API over the forecast and gap tables lets municipalities, funders and "
                   "marketplaces consume the intelligence in their own tools.")

    st.markdown("#### Two capabilities worth calling out")
    j1, j2 = st.columns(2)
    with j1:
        st.markdown("**Predictable supply lets buyers commit**")
        cap("This is a coordination gap rather than a supply shortage. Latent demand already "
                   "exceeds spec-ready supply. What's missing is a forward signal so buyers can "
                   "commit before the material physically exists. The layer shares that advance "
                   "information so independent operators can coordinate, without running a marketplace.")
    with j2:
        st.markdown("**Machine vision for yield prediction**")
        cap("A permit gives an address and a date. Machine vision turns building imagery and "
                   "the archetype schema into predicted species, dimensions, condition and board "
                   "footage, closing the inference gap at scale. A Phase 2 to 3 capability.")

    st.info("What makes it durable: the lasting asset is the canonical dataset and the network of "
            "corrections that accumulates as municipalities, contractors and buyers use it. The "
            "same method extends from lumber to other reclaimed materials, and the data and "
            "network grow more valuable as they accumulate.")


# --------------------------------------------------------------------------- #
# Projects
# --------------------------------------------------------------------------- #
if page == "Projects":
    st.subheader("Project store: add a specific demolition project")
    st.markdown("Layer real projects onto the baseline. Each is scored with the same "
                "sourced cascade and saved persistently.")
    with st.form("add_project"):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("Project / site name", "Sample infill site")
        cma = c2.selectbox("CMA", cma_cfg.cma_names())
        archetype = c3.selectbox("Archetype", list(reg["archetypes"].keys()),
                                 format_func=lambda a: reg["archetypes"][a]["label"])
        c4, c5, c6 = st.columns(3)
        floor_area = c4.number_input("Floor area (m2)", 20.0, 5000.0, 140.0, 10.0)
        year_built = c5.number_input("Year built", 1850, 2026, 1958, 1)
        method = c6.selectbox("Recovery method",
                              ["deconstruction", "mixed", "demolition"], index=1)
        submitted = st.form_submit_button("Analyze & save project")
    if submitted:
        record = projects.add_project({
            "name": name, "cma": cma, "archetype": archetype,
            "floor_area_m2": floor_area, "year_built": year_built,
            "recovery_method": method}, reg)
        a = record["analysis"]
        st.success(f"Saved project #{record['id']}: {name}")
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Framing lumber", fmt_bf(a["framing_bf"]))
        p2.metric("Spec-ready", fmt_bf(a["spec_ready_bf"]))
        p3.metric("Reclaimed value", fmt_cad(a["value_cad"]))
        p4.metric("Condition factor", f"{a['condition_factor']:.2f}")
    pdf = projects.projects_dataframe()
    if len(pdf):
        st.markdown("**Stored projects**")
        st.dataframe(pdf, width="stretch", hide_index=True)
        if st.button("Clear all stored projects"):
            projects.clear_projects()
            st.rerun()
    else:
        st.info("No projects stored yet. Add one above.")


# --------------------------------------------------------------------------- #
# Matchmaking (Phase-2 demonstrator)
# --------------------------------------------------------------------------- #
if page == "Matchmaking":
    st.subheader("Matchmaking (prototype)")
    cap("Phase-2 demonstrator. It shows how a specific demolition routes to nearby recovery "
               "and reuse firms, a working proof of the mechanic on the real ECCC directory, not a "
               "live commercial exchange. CCC's role is to send this signal to operators and partner "
               "marketplaces, rather than to run a marketplace.")

    stored = projects.projects_dataframe()
    opts = ["Quick entry"] + (["From the project store"] if not stored.empty else [])
    mode = st.radio("Material source", opts, horizontal=True)
    if mode == "From the project store" and not stored.empty:
        pick = st.selectbox("Project", stored["name"].tolist())
        prow = stored[stored["name"] == pick].iloc[0]
        site = {"name": pick, "cma": prow["cma"], "archetype": prow["archetype"],
                "floor_area_m2": prow["floor_area_m2"], "year_built": prow["year_built"],
                "recovery_method": prow["recovery_method"]}
    else:
        c1, c2, c3 = st.columns(3)
        cma = c1.selectbox("CMA", cma_cfg.cma_names())
        archetype = c2.selectbox("Archetype", list(reg["archetypes"].keys()),
                                 format_func=lambda a: reg["archetypes"][a]["label"])
        method = c3.selectbox("Recovery method", ["deconstruction", "mixed", "demolition"], index=1)
        c4, c5 = st.columns(2)
        floor_area = c4.number_input("Floor area (m2)", 20.0, 5000.0, 160.0, 10.0)
        year_built = c5.number_input("Year built", 1850, 2026, 1955, 1)
        site = {"name": "Quick entry", "cma": cma, "archetype": archetype,
                "floor_area_m2": floor_area, "year_built": year_built, "recovery_method": method}

    res = projects.analyze_project(site, reg)
    prov = ecosystem.CMA_PROVINCE.get(site["cma"], "")
    s1, s2, s3 = st.columns(3)
    s1.metric("Predicted spec-ready", fmt_bf(res["spec_ready_bf"]))
    s2.metric("Reclaimed value", fmt_cad(res["value_cad"]))
    s3.metric("Carbon benefit", f"{carbon.total_benefit_t(res['spec_ready_bf']):,.1f} t CO2e")

    st.markdown(f"#### Matched firms in {prov or 'province'}")
    comp = ecosystem.company_table()
    matches = comp[comp["province"] == prov].copy()
    if matches.empty:
        st.warning("No directory firms recorded in this province yet. The signal would route to the "
                   "nearest out-of-province firms or a partner marketplace.")
    else:
        order = {"Recover": 0, "Process": 1, "Remake": 2, "Resell": 3, "Generate": 4}
        matches["fit"] = matches["stages"].apply(lambda s: min((order.get(x, 9) for x in s), default=9))
        matches["role"] = matches["stages"].apply(lambda s: ", ".join(s))
        matches["activities"] = matches["activities"].apply(lambda a: ", ".join(a))
        matches = matches.sort_values("fit")
        st.dataframe(matches[["name", "role", "activities", "website"]].head(12),
                     width="stretch", hide_index=True)
        cap("Ranked by value-chain fit: recovery and processing first, since they can take "
                   "the material, then remanufacture and resale. Province match from the ECCC "
                   "directory (September 2024).")

    if st.button("Register interest (prototype)"):
        rec = projects.add_project(site, reg)
        st.success(f"Logged to the project store as entry #{rec['id']}. On a persistent backend this "
                   "would notify the matched firms; on the shared cloud demo the store is "
                   "session-only.")


# --------------------------------------------------------------------------- #
# Assumptions
# --------------------------------------------------------------------------- #
if page == "Assumptions":
    st.subheader("Assumptions registry (sourced)")
    st.markdown("Every coefficient, its plausible range, and its source. Move a slider and "
                "every figure across the app updates. Ranges feed the Monte Carlo model.")
    if "assumption_overrides" not in st.session_state:
        st.session_state["assumption_overrides"] = {}
    defaults = A.get_assumptions()
    cols = st.columns(2)
    i = 0
    for group, key, meta in A.flat_editable_rows(defaults):
        if meta["unit"] == "year":
            continue
        col = cols[i % 2]
        i += 1
        cur = st.session_state["assumption_overrides"].get((group, key), meta["value"])
        with col:
            if "fraction" in meta["unit"]:
                newv = st.slider(f"{group}.{key}", 0.0, 1.0, float(cur), 0.01, help=meta["basis"])
            elif meta["unit"] == "years":
                newv = st.slider(f"{group}.{key}", 1, 15, int(cur), 1, help=meta["basis"])
            else:
                newv = st.number_input(f"{group}.{key}", value=float(cur), help=meta["basis"])
            cap(f"range {meta['low']}-{meta['high']} | {meta['source']}")
            if newv != meta["value"]:
                st.session_state["assumption_overrides"][(group, key)] = newv
            elif (group, key) in st.session_state["assumption_overrides"]:
                del st.session_state["assumption_overrides"][(group, key)]
    if st.button("Reset to defaults"):
        st.session_state["assumption_overrides"] = {}
        st.cache_data.clear()
        st.rerun()

    st.markdown("**Building archetypes (sourced physical parameters)**")
    arch_rows = []
    for k, v in defaults["archetypes"].items():
        arch_rows.append({
            "archetype": k, "label": v["label"],
            "framing_bf_per_m2": val(v["framing_bf_per_m2"]),
            "floor_area_m2": val(v["floor_area_m2"]),
            "wood_frame_likelihood": val(v["wood_frame_likelihood"]),
            "value_tier": v["value_tier"]})
    st.dataframe(pd.DataFrame(arch_rows), width="stretch", hide_index=True)
    cap("Editing a slider clears the pipeline cache on next run. Full provenance "
               "and caveats are in docs/SOURCES.md.")


# --------------------------------------------------------------------------- #
# Sources & void
# --------------------------------------------------------------------------- #
if page == "Sources & void":
    st.subheader("Sources registry & void / coverage analysis")
    st.markdown("What data is real, what is modelled, and where the gaps are. Coverage "
                "tier drives the demolition-count uncertainty in the Monte Carlo model.")
    st.markdown("**Source registry**")
    st.dataframe(ingest.source_registry(), width="stretch", hide_index=True)
    st.markdown("**Void / coverage report (per CMA)**")
    void = data["void"].copy()
    void["confidence_band_pm"] = void["confidence_band_pm"].map(lambda x: f"+/- {x*100:.0f}%")
    st.dataframe(void, width="stretch", hide_index=True)
    st.markdown("**Coverage tiers across the 25 CMAs**")
    tier_counts = data["void"]["coverage_tier"].value_counts().reset_index()
    tier_counts.columns = ["coverage_tier", "cma_count"]
    fig = px.bar(tier_counts, x="coverage_tier", y="cma_count", color="coverage_tier",
                 color_discrete_map=TIER_COLOR,
                 labels={"cma_count": "number of CMAs", "coverage_tier": "coverage tier"})
    style_chart(fig, 300, showlegend=False)
    st.plotly_chart(fig, width="stretch")
    src = os.path.join(os.path.dirname(__file__), "docs", "SOURCES.md")
    if os.path.exists(src):
        with st.expander("Full source list and coefficient provenance (docs/SOURCES.md)"):
            with open(src, "r", encoding="utf-8") as f:
                st.markdown(f.read())


# --------------------------------------------------------------------------- #
# How it works (native walkthrough)
# --------------------------------------------------------------------------- #
if page == "How it works":
    st.subheader("How it works: sourcing to output")
    st.markdown("How the app turns open data and sourced coefficients into a "
                "confidence-scored estimate of salvageable lumber across Canada's 25 "
                "largest metro regions.")

    st.markdown("#### The pipeline, end to end")
    stages = [
        ("01", "Sourcing & inputs", ["Toronto Open Data (live permits, daily)",
            "StatCan 2021 Census (dwellings, housing age)",
            "StatCan Building Permits (demolition rates)",
            "Coefficients (USDA FPL, Oregon DEQ, MPAC)"]),
        ("02", "Canonical table", ["One agreed schema for every city",
            "Void / coverage flags", "Marks real versus modelled"]),
        ("03", "Recovery cascade", ["Framing lumber in the building",
            "Recoverable, then salvageable", "Spec-ready, then dollar value",
            "One sourced coefficient per step"]),
        ("04", "Uncertainty", ["Monte Carlo over every range",
            "P10 / P50 / P90 bands", "Tornado: the lever that matters"]),
        ("05", "Outputs", ["5 to 10 year forecast", "Maps and gap analysis",
            "Value and scenarios", "Platform roadmap"]),
        ("06", "Demand & ecosystem", ["Real reclaimed-wood company directory",
            "Demand segments and economics", "Why recoverable wood is not reclaimed"]),
    ]
    _badge = ("font-family:'JetBrains Mono',monospace;background:var(--gold);color:#fff;"
              "border-radius:6px;padding:2px 9px;font-size:12px;font-weight:600")
    for n, title, items in stages:
        with st.container(border=True):
            st.markdown(f"<span style=\"{_badge}\">{n}</span> "
                        f"<b style=\"font-size:1.03rem\">{title}</b>", unsafe_allow_html=True)
            st.markdown("\n".join(f"- {it}" for it in items))

    st.markdown("#### Inside the recovery cascade")
    cap("One typical post-war single-detached home: 120 m2 floor area, built around "
               "1965, mixed demolition practice. Each step multiplies by a sourced coefficient.")
    casc = [("Floor area", "120 m2"), ("Framing lumber", "9,290 bf"), ("Recoverable", "2,029 bf"),
            ("Salvageable", "1,420 bf"), ("Spec-ready", "781 bf"), ("Reclaimed value", "$3,750")]
    for c, (lab, v) in zip(st.columns(3), casc[:3]):
        c.metric(lab, v)
    for c, (lab, v) in zip(st.columns(3), casc[3:]):
        c.metric(lab, v)
    cap("Coefficients applied in order: framing 79 bf/m2; structural recovery x0.30 and "
               "age-adjusted condition x0.73; denailing and sort x0.70; grading x0.55; "
               "value $4.80/bf. Sources: McKeever & Phelps FPL 1994; Oregon DEQ 2019; "
               "Falk FPL-RP-650. Gross wood content including panels and finish is 11,911 bf.")

    st.markdown("#### The two-sided picture: supply meets demand")
    cap("The supply model is half the story. The Ecosystem and Demand pages add the firms "
               "that recover and remake wood, and the markets that buy it.")
    w1, w2, w3, w4 = st.columns(4)
    w1.metric("Named companies", f"{len(companies.list_companies())}")
    w2.metric("National SMEs", f"{companies.NATIONAL_SME_TOTAL}")
    w3.metric("Demand legal today", fmt_bf(demand.tier_a_total()))
    w4.metric("Demand if reuse is allowed", fmt_bf(demand.tier_b_total()))
    cap("Latent demand runs well above current spec-ready supply, so the binding constraint "
               "is supply and coordination. The top blocker is the structural-reuse code wall, and "
               "the next is the missing forward supply signal that this layer provides.")
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 680 690" font-family="Inter, Segoe UI, Arial, sans-serif">
  <style>
    .term{fill:#14532D} .termtx{fill:#ffffff} .dia{fill:none;stroke:#CBD5C9;stroke-width:1.5}
    .dtext{fill:#14532D} .card{fill:#FFFFFF;stroke:#E2E7DE;stroke-width:1.5}
    .cach{fill:#E9F5EE;stroke:#BFE3CD;stroke-width:1.5} .ctitle{fill:#1F2421}
    .edge{stroke:#2F7D4F;stroke-width:2;fill:none} .accf{fill:#2F7D4F}
    .mono{fill:#2F7D4F} .lbl{fill:#2F7D4F}
    @media (prefers-color-scheme: dark){
      .term{fill:#1E5B3A} .dia{stroke:#3A4A40} .dtext{fill:#EAF3EC}
      .card{fill:#15151B;stroke:#2A2A31} .cach{fill:#16241B;stroke:#2E5A3E} .ctitle{fill:#ECECE6}
      .edge{stroke:#4DB779} .accf{fill:#4DB779} .mono{fill:#5CCF95} .lbl{fill:#5CCF95}
    }
  </style>
  <defs><marker id="dh" markerWidth="9" markerHeight="9" refX="7.5" refY="4.5" orient="auto">
    <path d="M0,0 L9,4.5 L0,9 Z" class="accf"/></marker></defs>
  <g class="edge">
    <path d="M380,78 L380,116" marker-end="url(#dh)"/>
    <path d="M380,232 L380,268" marker-end="url(#dh)"/>
    <path d="M380,390 L380,453" marker-end="url(#dh)"/>
    <path d="M380,525 L380,598" marker-end="url(#dh)"/>
    <path d="M250,175 L150,175 L150,374" marker-end="url(#dh)"/>
    <path d="M240,330 L150,330"/>
    <path d="M150,452 L150,628 L279,628" marker-end="url(#dh)"/>
  </g>
  <g class="lbl" font-family="JetBrains Mono, monospace" font-size="12">
    <text x="392" y="255">yes</text><text x="392" y="420">yes</text>
    <text x="158" y="166">no</text><text x="158" y="321">no</text>
  </g>
  <rect x="290" y="30" width="180" height="48" rx="11" class="term"/>
  <text x="380" y="60" text-anchor="middle" class="termtx" font-size="15" font-weight="700">Run pipeline</text>
  <polygon points="380,116 510,175 380,234 250,175" class="dia"/>
  <text x="380" y="171" text-anchor="middle" class="dtext" font-size="13">Live Toronto</text>
  <text x="380" y="189" text-anchor="middle" class="dtext" font-size="13">toggle on?</text>
  <polygon points="380,268 520,330 380,392 240,330" class="dia"/>
  <text x="380" y="323" text-anchor="middle" class="dtext" font-size="13">Fetch OK?</text>
  <text x="380" y="340" text-anchor="middle" class="dtext" font-size="13">200 + records,</text>
  <text x="380" y="357" text-anchor="middle" class="dtext" font-size="13">under 20s?</text>
  <rect x="263" y="455" width="234" height="70" rx="11" class="card"/>
  <text x="380" y="483" text-anchor="middle" class="ctitle" font-size="13.5" font-weight="600">Live by-year counts</text>
  <text x="380" y="505" text-anchor="middle" class="mono" font-family="JetBrains Mono, monospace" font-size="12">2017-2022 stable mean</text>
  <rect x="52" y="374" width="196" height="74" rx="13" class="cach"/>
  <text x="150" y="404" text-anchor="middle" class="ctitle" font-size="13.5" font-weight="600">Cached figure</text>
  <text x="150" y="426" text-anchor="middle" class="mono" font-family="JetBrains Mono, monospace" font-size="12">"cached" label</text>
  <rect x="279" y="602" width="202" height="52" rx="13" class="term"/>
  <text x="380" y="625" text-anchor="middle" class="termtx" font-size="14" font-weight="700">Assign coverage</text>
  <text x="380" y="643" text-anchor="middle" class="termtx" font-size="14" font-weight="700">tier</text>
</svg>'''
    b64 = base64.b64encode(svg.encode("utf-8")).decode()
    st.markdown(f'<div style="max-width:680px;margin:4px auto 0">'
                f'<img alt="Live-data decision flow" style="width:100%" '
                f'src="data:image/svg+xml;base64,{b64}"/></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Coverage tier sets the band")
        st.dataframe(pd.DataFrame([
            {"Coverage": "HIGH", "Markets": "Toronto (live permit feed)", "Band": "+/- 10%"},
            {"Coverage": "MEDIUM", "Markets": "Vancouver, Montreal, Calgary, Edmonton, Ottawa-Gatineau", "Band": "+/- 25%"},
            {"Coverage": "LOW", "Markets": "The other 19 CMAs (inferred)", "Band": "+/- 45%"},
        ]), width="stretch", hide_index=True)
    with c2:
        st.markdown("#### What comes out")
        st.dataframe(pd.DataFrame([
            {"Output": "National & per-CMA supply, value", "Where": "Overview, Municipal baseline"},
            {"Output": "Forecast with P10/P50/P90", "Where": "Forecast & uncertainty"},
            {"Output": "Sensitivity tornado", "Where": "Forecast & uncertainty"},
            {"Output": "Ecosystem gaps", "Where": "Ecosystem > Supply gaps"},
            {"Output": "Scenario testing", "Where": "Sidebar scenario selector"},
        ]), width="stretch", hide_index=True)

    ppath = os.path.join(os.path.dirname(__file__), "docs", "Reclaimed_Lumber_How_It_Works.pdf")
    if os.path.exists(ppath):
        with open(ppath, "rb") as pf:
            st.download_button("Download as PDF", pf.read(),
                               file_name="Reclaimed_Lumber_How_It_Works.pdf",
                               mime="application/pdf")
