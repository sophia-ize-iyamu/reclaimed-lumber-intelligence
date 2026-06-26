"""
Project store (Deliverable / architecture Step 3): incremental, persistent
addition of specific demolition projects analyzed against the baseline model.

A user adds one real project (address, CMA, archetype, floor area, recovery
method). It is scored with the same recovery cascade as the city-wide model and
written to a JSON store that persists across runs. This is what moves the layer
from a point-in-time estimate to a continuously growing intelligence asset.

The store is a plain JSON file so it has zero infrastructure dependencies and is
trivially inspectable. A real deployment swaps this for a database behind the
same add_project / load_projects interface.
"""

import json
import os

import pandas as pd

from config import assumptions as A
from config.assumptions import val

_STORE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "store", "projects.json")

# Intake schema: the fields a new project needs to be analyzable.
INTAKE_FIELDS = [
    ("name", "Project / site name"),
    ("cma", "CMA"),
    ("archetype", "Building archetype"),
    ("floor_area_m2", "Floor area (m2)"),
    ("year_built", "Year built"),
    ("recovery_method", "Recovery method (deconstruction / mixed / demolition)"),
]

# Recovery method overrides the blended recovery_method_factor assumption.
# Values match config/assumptions.METHOD_FACTOR (sourced: Oregon DEQ, Delta).
METHOD_FACTOR = {"deconstruction": 0.70, "mixed": 0.30, "demolition": 0.05}


def _ensure_store():
    os.makedirs(os.path.dirname(_STORE_PATH), exist_ok=True)
    if not os.path.exists(_STORE_PATH):
        with open(_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)


def load_projects():
    _ensure_store()
    with open(_STORE_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _save(projects):
    _ensure_store()
    with open(_STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(projects, f, indent=2)


def analyze_project(project, reg=None):
    """
    Score a single project through the recovery cascade. The project's chosen
    recovery method overrides the global blended method factor; everything else
    follows the shared assumptions, so a project is always comparable to the
    baseline model.
    """
    if reg is None:
        reg = A.get_assumptions()

    arch = reg["archetypes"][project["archetype"]]
    rec = reg["recovery"]

    base_year = val(reg["forecast"]["base_year"])
    decades = max(0.0, (base_year - float(project["year_built"]))) / 10.0

    wfl = val(arch["wood_frame_likelihood"])
    floor_area = float(project["floor_area_m2"]) * wfl
    framing = floor_area * val(arch["framing_bf_per_m2"])
    gross_total = framing / val(reg["dimensional_share_of_total"])

    rmf = METHOD_FACTOR.get(project.get("recovery_method", "mixed"),
                            val(rec["recovery_method_factor"]))
    cond_base = val(rec["condition_base"])
    degr = val(rec["degradation_per_decade"])
    denail = val(rec["denail_sort_yield"])
    grading = val(rec["grading_pass_rate"])

    condition = max(0.20, cond_base - degr * decades)
    recoverable = framing * rmf * condition
    salvageable = recoverable * denail
    spec_ready = salvageable * grading
    tier = arch["value_tier"]
    value_cad = spec_ready * val(reg["value_per_bf_cad"][tier])

    return {
        "gross_bf": round(gross_total, 1),
        "framing_bf": round(framing, 1),
        "recoverable_bf": round(recoverable, 1),
        "salvageable_bf": round(salvageable, 1),
        "spec_ready_bf": round(spec_ready, 1),
        "value_tier": tier,
        "value_cad": round(value_cad, 0),
        "condition_factor": round(condition, 3),
    }


def add_project(project, reg=None):
    """Analyze and persist a project. Returns the stored record."""
    result = analyze_project(project, reg)
    record = dict(project)
    record["analysis"] = result
    projects = load_projects()
    record["id"] = len(projects) + 1
    projects.append(record)
    _save(projects)
    return record


def projects_dataframe():
    """Flatten the project store into a DataFrame for display."""
    projects = load_projects()
    if not projects:
        return pd.DataFrame()
    rows = []
    for p in projects:
        a = p.get("analysis", {})
        rows.append({
            "id": p.get("id"),
            "name": p.get("name"),
            "cma": p.get("cma"),
            "archetype": p.get("archetype"),
            "floor_area_m2": p.get("floor_area_m2"),
            "year_built": p.get("year_built"),
            "recovery_method": p.get("recovery_method"),
            "spec_ready_bf": a.get("spec_ready_bf"),
            "recoverable_bf": a.get("recoverable_bf"),
            "gross_bf": a.get("gross_bf"),
            "value_tier": a.get("value_tier"),
            "value_cad": a.get("value_cad"),
        })
    return pd.DataFrame(rows)


def clear_projects():
    _save([])
