# Local Instructions

## Purpose

This folder owns the grower-level interactive web map subskill. It generates a lightweight Leaflet HTML map for each existing grower in the data-pipeline runtime, showing field polygons on a satellite basemap with clickable metadata and a field-list sidebar.

## Safe edit scope

Edits should stay in this folder and its children unless the user explicitly asks for a broader skill change. Do not change parent `SKILL.md`, sibling workflows, or root policy from a subskill task unless explicitly requested.

## Read nearby docs first

Read `GUIDE.md` first, then `src/generate_grower_map.py` before changing map generation behavior. Read `../../../admin/interactive-web-map/GUIDE.md` for the parent interactive map pattern. For runtime contract details (DATA_PIPELINE_DATA_ROOT, grower tree layout), read `../../AGENTS.md`.

## Runtime contract

- `DATA_PIPELINE_DATA_ROOT` must be set and point to the runtime root.
- Grower data lives under `${DATA_PIPELINE_DATA_ROOT}/data-pipeline/growers/<grower-slug>/`.
- The script discovers growers from `${DATA_PIPELINE_DATA_ROOT}/data-pipeline/growers/`, not the bare root.
- Farm boundary GeoJSON is at `farms/<farm-slug>/boundary/field_boundaries.geojson`.
- Output HTML goes to `farms/<farm-slug>/derived/reports/<grower>_<farm>_grower_map.html`.

## Local validation

Run from the runtime source copy:

```bash
export DATA_PIPELINE_DATA_ROOT=/absolute/path/to/my-farm-advisor-runtime
cd "${DATA_PIPELINE_DATA_ROOT}/data-pipeline/src"
"${DATA_PIPELINE_DATA_ROOT}/data-pipeline/.venv/bin/python" \
  scripts/reporting/generate_grower_web_map.py
```

## Local-delta-only reminder

This nested AGENTS.md only records instructions that differ from the parent or root files. Do not duplicate root-wide asset, vendor, or validation policy here except this pointer to `../../../AGENTS.md`.