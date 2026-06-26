"""
Reclaimed Lumber Intelligence Layer
Circular Construction Canada  |  UofT Rotman RSM2700

A salvageable-lumber intelligence layer for Canada's 25 largest CMAs, organized
around the brief's five deliverables. Every coefficient is sourced (see
docs/SOURCES.md), uncertainty is propagated by Monte Carlo, and a sensitivity
tornado shows which assumption matters most.

Run locally:
    pip install -r requirements.txt
    streamlit run app.py
"""

import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from config import assumptions as A
from config import cmas as cma_cfg
from config.assumptions import val
from pipeline import ingest, model, forecast, ecosystem, projects, uncertainty

st.set_page_config(page_title="Reclaimed Lumber Intelligence | CCC",
                   layout="wide", page_icon="🪵")


# --------------------------------------------------------------------------- #
# Theme-aware styling. The app theme follows the viewer's system / browser
# setting (Streamlit does this when no theme is pinned), so reading it here lets
# every chart match light or dark automatically.
# --------------------------------------------------------------------------- #
def active_theme():
    try:
        t = st.context.theme
        if t and getattr(t, "type", None):
            return t.type
    except Exception:
        pass
    return "dark"


THEME = active_theme()
DARK = THEME == "dark"
_FONT = "#E6E6E6" if DARK else "#1F2421"
_PLOT_TEMPLATE = "plotly_dark" if DARK else "plotly_white"
_LAND = "#23262C" if DARK else "#EFEFE9"
_COUNTRY = "#444954" if DARK else "#CBCBC4"
_MARKER_LINE = "rgba(255,255,255,0.55)" if DARK else "rgba(40,40,40,0.45)"
ACCENT = "#3FA06A"


def style_chart(fig, height=340, **layout):
    """Transparent background, theme font, theme template. Inherits page theme."""
    fig.update_layout(height=height, margin=dict(l=0, r=0, t=10, b=0),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font_color=_FONT, template=_PLOT_TEMPLATE, **layout)
    return fig


def style_geo(fig, height=460):
    """Theme-aware map: transparent ocean/background, themed land and borders."""
    fig.update_geos(fitbounds="locations", resolution=50, showcountries=True,
                    countrycolor=_COUNTRY, showland=True, landcolor=_LAND,
                    showocean=False, showframe=False, showcoastlines=True,
                    coastlinecolor=_COUNTRY, bgcolor="rgba(0,0,0,0)",
                    lakecolor="rgba(0,0,0,0)")
    fig.update_traces(marker=dict(line=dict(width=0.6, color=_MARKER_LINE)),
                      selector=dict(type="scattergeo"))
    return style_chart(fig, height)


# Inject a small CSS polish layer (cards, metric wrapping, tab styling).
st.markdown("""
<style>
/* Metric cards: framed, and wrap instead of truncating on narrow screens */
div[data-testid="stMetric"] {
  background: rgba(128,128,128,0.08);
  border: 1px solid rgba(128,128,128,0.20);
  border-radius: 14px;
  padding: 14px 16px;
}
div[data-testid="stMetric"] label p { white-space: normal; font-size: 0.80rem; opacity: 0.85; }
div[data-testid="stMetricValue"] {
  font-size: clamp(1.05rem, 1.7vw, 1.75rem);
  white-space: normal; line-height: 1.12;
}
/* Tabs: a touch more breathing room and a clearer active state */
button[data-baseweb="tab"] { font-size: 0.95rem; padding-top: 6px; padding-bottom: 6px; }
/* Rounded dataframes */
div[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }
/* Tighten heading tracking */
h1, h2, h3 { letter-spacing: -0.015em; }
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
    actors = ecosystem.build_actor_table()
    gaps = ecosystem.gap_analysis(summary, actors)
    void = ingest.void_report(demo)
    mc_cma, mc_nat = uncertainty.monte_carlo(summary, reg)
    tor = uncertainty.tornado(summary, reg)
    return {"demo": demo, "supply": supply, "summary": summary, "forecast": fcast,
            "actors": actors, "gaps": gaps, "void": void,
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


TIER_COLOR = {"high": "#2e7d32", "medium": "#f9a825", "low": "#c62828"}


# --------------------------------------------------------------------------- #
# Sidebar
# --------------------------------------------------------------------------- #
st.sidebar.title("Reclaimed Lumber Intelligence")
st.sidebar.caption("Circular Construction Canada | RSM2700")

_scenarios = A.get_assumptions()["scenarios"]
scenario_key = st.sidebar.selectbox(
    "Scenario", list(_scenarios.keys()),
    format_func=lambda k: _scenarios[k]["label"])
st.sidebar.caption(_scenarios[scenario_key]["note"])

allow_network = st.sidebar.toggle(
    "Use live Toronto Open Data", value=False,
    help="Pull real Toronto demolition permits by year (offline fallback if unreachable).")
st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Deliverables**\n\n1. Municipal baseline\n2. Hotspots & archetypes\n"
    "3. Forecast & uncertainty\n4. Ecosystem & gaps\n5. Platform roadmap")
st.sidebar.caption("Every coefficient is sourced. See the Sources & void tab.")

reg = build_registry(scenario_key)
overrides_sig = tuple(sorted(
    (str(k), v) for k, v in st.session_state.get("assumption_overrides", {}).items()))
data = run_pipeline(overrides_sig, allow_network, scenario_key)
summary = data["summary"]


# --------------------------------------------------------------------------- #
# Header
# --------------------------------------------------------------------------- #
st.title("Reclaimed Lumber Intelligence Layer")
st.markdown(
    "Where will salvageable lumber emerge across Canada's 25 largest metro regions, "
    "what it's worth, what recovery capacity exists, and where the bottlenecks are. "
    "Coefficients are sourced, and the uncertainty in them carries through to every number.")
if scenario_key != "baseline":
    st.info(f"Scenario active: **{_scenarios[scenario_key]['label']}**. "
            "All figures below reflect this scenario.")

tabs = st.tabs([
    "Overview", "1. Municipal baseline", "2. Hotspots & archetypes",
    "3. Forecast & uncertainty", "4. Ecosystem & gaps", "5. Platform roadmap",
    "Projects", "Assumptions", "Sources & void"])


# --------------------------------------------------------------------------- #
# Overview
# --------------------------------------------------------------------------- #
with tabs[0]:
    nat = data["mc_nat"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Gross wood content", fmt_bf(summary["gross_bf"].sum()))
    c2.metric("Recoverable", fmt_bf(summary["recoverable_bf"].sum()))
    c3.metric("Spec-ready reusable", fmt_bf(summary["spec_ready_bf"].sum()))
    c4.metric("Reclaimed value (CAD/yr)", fmt_cad(summary["value_cad"].sum()))

    st.caption(f"National spec-ready, Monte Carlo P10-P50-P90: "
               f"{fmt_bf(nat['spec_ready']['p10'])}  ->  "
               f"{fmt_bf(nat['spec_ready']['p50'])}  ->  "
               f"{fmt_bf(nat['spec_ready']['p90'])} per base year. "
               "The range propagates coefficient and data-coverage uncertainty.")

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
        st.dataframe(top[["cma", "coverage_tier", "spec_ready", "value/yr"]],
                     width="stretch", hide_index=True)
    with colB:
        st.markdown("**Top markets by reclaimed value**")
        byval = summary.sort_values("value_cad", ascending=False).head(10)
        fig = px.bar(byval, x="value_cad", y="cma", orientation="h",
                     labels={"value_cad": "CAD / yr", "cma": ""})
        style_chart(fig, 320, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, width="stretch")
    st.caption("Marker size = spec-ready lumber. Colour = data coverage (green high, "
               "amber medium, red low). Only Toronto uses a live permit feed.")


# --------------------------------------------------------------------------- #
# 1. Municipal baseline
# --------------------------------------------------------------------------- #
with tabs[1]:
    st.subheader("Deliverable 1: Municipal demolition & housing-stock baseline")
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
    st.caption(("Housing-stock age: real StatCan distribution." if rec["vintage_is_real"]
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
with tabs[2]:
    st.subheader("Deliverable 2: Neighbourhood hotspots & archetype refinement")
    st.markdown("Demolition clusters in specific neighbourhoods and repeatable building "
                "types. Toronto is the worked example. Its real permit data shows "
                "single-family detached is about 77% of demolitions, confirming the brief.")
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
        fig = px.scatter_geo(hotspots, lat="lat", lon="lon", size="annual_permits",
                             color="dominant_archetype", hover_name="neighbourhood",
                             hover_data={"annual_permits": True, "lat": False, "lon": False},
                             scope="north america", size_max=45)
        style_geo(fig, 420)
        fig.update_layout(legend_title_text="Dominant archetype")
        st.plotly_chart(fig, width="stretch")
    with colB:
        st.markdown("**Toronto demolition hotspots**")
        st.dataframe(hotspots[["neighbourhood", "annual_permits", "archetype_label"]],
                     width="stretch", hide_index=True)
        st.caption("Neighbourhood splits are illustrative of the method; the city total "
                   "and archetype mix are anchored to real Toronto Open Data.")
    st.info("Post-war stick-frame homes dominate the demolition stream and carry the most "
            "reusable dimensional lumber; pre-war homes are fewer but carry higher-value "
            "old-growth members. Targeting these archetypes raises realized yield and value.")


# --------------------------------------------------------------------------- #
# 3. Forecast + uncertainty
# --------------------------------------------------------------------------- #
with tabs[3]:
    st.subheader("Deliverable 3: Material flow forecast with propagated uncertainty")
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
    st.caption("4,000 draws. Recovery coefficients are sampled jointly across all CMAs "
               "(correlated national error that doesn't diversify away), and the demolition "
               "count is sampled per CMA by coverage tier.")

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
    fig.add_vline(x=base_total, line_dash="dash", line_color=_FONT,
                  annotation_text="central", annotation_position="top")
    style_chart(fig, 340, xaxis_title="national spec-ready bf if parameter swings low to high")
    fig.update_layout(margin=dict(l=0, r=0, t=28, b=0))
    st.plotly_chart(fig, width="stretch")
    st.caption("Recovery method factor (deconstruction vs demolition) dominates. That's "
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


# --------------------------------------------------------------------------- #
# 4. Ecosystem & gaps
# --------------------------------------------------------------------------- #
with tabs[4]:
    st.subheader("Deliverable 4: Ecosystem actor map & gap analysis")
    st.markdown("The circular lumber supply chain mapped against supply. Flags markets "
                "with strong supply but weak recovery or storage capacity.")
    gaps = data["gaps"]
    actors = data["actors"]
    n_gap = (~gaps["gap_flag"].isin(["Adequate", "No modelled supply"])).sum()
    g1, g2, g3 = st.columns(3)
    g1.metric("CMAs analyzed", len(gaps))
    g2.metric("Markets with a flagged gap", int(n_gap))
    g3.metric("Total mapped actors", len(actors))
    gshow = gaps.copy()
    gshow["recoverable"] = gshow["recoverable_bf"].map(fmt_bf)
    gshow["processing_cap"] = gshow["processing_capacity_bf_yr"].map(fmt_bf)
    gshow["capacity_ratio"] = gshow["capacity_ratio"].map(lambda x: f"{x:.2f}")
    st.dataframe(gshow[["cma", "coverage_tier", "recoverable", "processing_cap",
                        "capacity_ratio", "deconstruction", "processor", "warehouse",
                        "reuse_buyer", "gap_flag"]], width="stretch", hide_index=True)
    st.caption("capacity_ratio = (processing and storage throughput) / recoverable supply. "
               "Actor counts are synthetic placeholders demonstrating the method; the gap "
               "logic runs unchanged on a real actor directory.")
    cma_pick = st.selectbox("Actor map for CMA", cma_cfg.cma_names(), key="actor_cma")
    asub = actors[actors["cma"] == cma_pick]
    if len(asub):
        fig = px.scatter_geo(asub, lat="lat", lon="lon", color="actor_type",
                             hover_name="name", scope="north america")
        style_geo(fig, 360)
        st.plotly_chart(fig, width="stretch")


# --------------------------------------------------------------------------- #
# 5. Platform roadmap
# --------------------------------------------------------------------------- #
with tabs[5]:
    st.subheader("Deliverable 5: Coordination platform architecture & roadmap")
    path = os.path.join(os.path.dirname(__file__), "docs", "platform_roadmap.md")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            st.markdown(f.read())


# --------------------------------------------------------------------------- #
# Projects
# --------------------------------------------------------------------------- #
with tabs[6]:
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
# Assumptions
# --------------------------------------------------------------------------- #
with tabs[7]:
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
            st.caption(f"range {meta['low']}-{meta['high']} | {meta['source']}")
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
    st.caption("Editing a slider clears the pipeline cache on next run. Full provenance "
               "and caveats are in docs/SOURCES.md.")


# --------------------------------------------------------------------------- #
# Sources & void
# --------------------------------------------------------------------------- #
with tabs[8]:
    st.subheader("Sources registry & void / coverage analysis")
    st.markdown("What data is real, what is modelled, and where the gaps are. Coverage "
                "tier drives the demolition-count uncertainty in the Monte Carlo model.")
    st.markdown("**Source registry**")
    st.dataframe(ingest.source_registry(), width="stretch", hide_index=True)
    st.markdown("**Void / coverage report (per CMA)**")
    void = data["void"].copy()
    void["confidence_band_pm"] = void["confidence_band_pm"].map(lambda x: f"+/- {x*100:.0f}%")
    st.dataframe(void, width="stretch", hide_index=True)
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
