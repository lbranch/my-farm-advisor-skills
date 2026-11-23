# Provenance — field-eda-assignment2

| Field | Value |
|---|---|
| **Skill** | `field-eda-assignment2` |
| **Author** | Boreal Bytes |
| **Source** | My Farm Advisor umbrella skill, EDA subtree `(my-farm-advisor/eda/)` |
| **Assignment** | 2 |
| **Created** | 2026-11-21 |
| **Dataset** | 3 growers × 10 fields under `my-farm-advisor-runtime/data-pipeline/growers/` |

## Dependencies

No new PyPI packages. Uses the existing `.venv` at
`${DATA_PIPELINE_DATA_ROOT}/data-pipeline/.venv` which provides:

- pandas, numpy, matplotlib, seaborn, scipy
- geopandas, contextily, pyproj, shapely

## Output Scope

Generated PNGs are **not committed** — they live under
`${DATA_PIPELINE_DATA_ROOT}/data-pipeline/eda/assignment2/output/`.

## Attribution

Based on the Assignment 2 expansion produced by the runtime data pipeline,
accessed via `DATA_PIPELINE_DATA_ROOT` convention.