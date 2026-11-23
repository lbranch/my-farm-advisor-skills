---
name: field-eda-assignment2
description: >
  Assignment 2 field-level EDA comparing field boundaries, CDL/cropland,
  and weather across 3 growers (IL, IA, NE) with 10 fields each.
  Generates static PNGs for review.
license: Apache-2.0
metadata:
  author: Clayton Young / Superior Byte Works, LLC (@borealBytes)
  skill-author: Boreal Bytes
  skill-version: "1.0.0"
  assignment: "2"
  dataset: my-farm-advisor-assignment2
  runtime-data-root: DATA_PIPELINE_DATA_ROOT
---

# field-eda-assignment2

**Assignment 2 — Field-Level EDA Subskill**  
**Dataset:** 3 growers × 10 fields (IL, IA, NE)  
**Outputs:** static PNGs under `${DATA_PIPELINE_DATA_ROOT}/data-pipeline/eda/assignment2/output/`

## Start Here

Open the [GUIDE.md](GUIDE.md) for the full workflow walkthrough, then use
`src/run_all.py` to generate all plots.

### Plot Modules

- [Boundaries](src/boundaries.py) — field size distributions and location maps
- [CDL](src/cdl.py) — crop domination and rotation intensity
- [Weather](src/weather.py) — seasonal cycles and climate regime comparisons

### Routing

This is a subskill of the **EDA** subtree within My Farm Advisor. Load the
umbrella skill first, then open this guide when the task is "run the
Assignment 2 field-level EDA".

## Outputs

All 9 plots land in `${DATA_PIPELINE_DATA_ROOT}/data-pipeline/eda/assignment2/output/`.
See [GUIDE.md](GUIDE.md#plot-catalog) for the full catalog.