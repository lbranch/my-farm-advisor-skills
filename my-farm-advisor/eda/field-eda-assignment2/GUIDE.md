---
name: field-eda-assignment2
description: >
  Assignment 2 field-level EDA comparing boundaries, CDL/cropland, and
  weather across 3 growers (IL, IA, NE) with 10 fields each.  Generates
  9 static PNGs — first build Phase 1 (4 plots), then all 9 with --all.
version: 1.0.0
author: Boreal Bytes
tags: [eda, assignment2, boundaries, cdl, weather, visualization]
---

# Workflow: field-eda-assignment2

## Description

Produce static exploratory data analysis outputs for a 3-grower, 30-field
dataset spanning Illinois, Iowa, and Nebraska.  The workflow loads field
boundaries, CDL composition and rotation tables, and daily weather from
the runtime data pipeline, then generates publication-ready PNGs.

## When to Use This Workflow

- **Assignement 2 deliverables:** you need the approved plot set for
  the field-level EDA milestone.
- **Cross-state field comparison:** compare field sizes, crop composition,
  and weather regimes across IL, IA, and NE.
- **Phase 1 review:** run just Phase 1 (4 plots) to check output quality
  and data integrity before investing in the full 9-plot set.

## Prerequisites

```bash
# Venv from the data pipeline has everything needed.
export DATA_PIPELINE_DATA_ROOT="$HOME/my-farm-advisor-runtime"
source "${DATA_PIPELINE_DATA_ROOT}/data-pipeline/.venv/bin/activate"
```

## Plot Catalog

All outputs land in:
`${DATA_PIPELINE_DATA_ROOT}/data-pipeline/eda/assignment2/output/`

### Phase 1 — 4 plots

| # | File | Module | Story |
|---|---|---|---|
| 1 | `field_size_boxplot.png` | boundaries.py | IL fields (~950 ac) are smaller and more variable than IA (~1,000–1,650); NE is uniformly compact (~435–520 ac). Reflects different farm structures and the center-pivot context. |
| 2 | `field_locations_map.png` | boundaries.py | Spatial distribution: IL spans central/northern counties, IA ranges from Cass to Emmet, NE is concentrated in York. The "farm" is a CSB sample, not contiguous block. |
| 3 | `cdl_2023_dominant_crop.png` | cdl.py | Dominant 2023 crop composition: IL soy-heavy (8/10), IA mixed (6 corn / 4 soy), NE corn-heavy (8/10). |
| 4 | `weather_regime_scatter.png` | weather.py | Annual mean T2M vs total precip per field-year. Three tight clusters: IL (cool, wet), IA (mid), NE (hot, dry). Trend lines quantify the climate gradient. |

### Phase 2 — 5 more plots

| # | File | Module | Story |
|---|---|---|---|
| 5 | `field_size_rank.png` | boundaries.py | Sorted bar per grower shows the within-state range spread and the rank ordering of fields. |
| 6 | `cdl_corn_years.png` | cdl.py | Histogram of corn years (0–5): NE fields 4+ years corn, IA 2–3, IL 1–2. Rotation intensity varies by state. |
| 7 | `cdl_corn_proportion_trend.png` | cdl.py | Corn pixel % 2019–2023 per grower line. Highlights the NE 2020 anomaly (90 % corn vs ~70 % other years). |
| 8 | `weather_example_timeseries.png` | weather.py | Dual-axis T2M + precip for one field per grower, 2021–2025. Within-field seasonal patterns and data quality check. |
| 9 | `weather_monthly_temperature.png` | weather.py | Box plots of T2M per month by grower. Frost season length visible in shoulder-month tails. |

## Quick Start

```bash
cd /home/coder/my-farm-advisor-skills/my-farm-advisor/eda/field-eda-assignment2
export DATA_PIPELINE_DATA_ROOT="$HOME/my-farm-advisor-runtime"

# Phase 1
python src/run_all.py

# All 9 plots
python src/run_all.py --all
```

## Interpreting the Outputs

### Boundaries

- **Field size boxplot:** IL has the widest range (945–1,360 ac); IA
  includes the largest single field (ia-f1, 1,654 ac) but also the
  smallest (ia-f6, 1,001 ac); NE is uniformly around 435–522 ac.
  Consider the center-pivot irrigation context for NE's uniformity.
- **Location map:** Every IL field is in a different county; IA fields
  span from Cass in the south-west to Emmet in the north — these
  are state-wide CSB samples, not contiguous farms.
- **Size rank (Phase 2):** Compare the sorted slope within each state.
  IL and IA have gradual slopes; NE is a steep cliff — all fields nearly
  the same size.

### CDL / Cropland

- **Dominant crop (2023):** IL is soybean country (8/10 fields); NE is
  corn country (8/10); IA splits nearly evenly. This matches the
  Corn Belt gradient.
- **Corn years (Phase 2):** Out of 5 CDL years (2019–2023), NE fields
  average 4+ years in corn. Several IL fields are in corn only 1 or 2
  years, confirming a soybean-dominant rotation.
- **Corn proportion trend (Phase 2):** The NE 2020 spike (90 % corn)
  stands out. Investigate whether this is a genuine year effect or
  a sampling artifact of the 10 fields.

### Weather

- **Regime scatter:** The three groups are non-overlapping. The IL
  cluster (lower right — cooler, wetter) and NE cluster (upper left —
  hotter, drier) define the climate range. Trend slopes are similar,
  confirming that within each state warmer years are also drier.
- **Example time series (Phase 2):** NE shows a more concentrated
  summer precipitation pattern; IL winter/spring precipitation is more
  persistent. Validates that the NASA POWER weather data has no gaps.
- **Monthly temperature (Phase 2):** The 0 °C line crossing in April
  (IL/IA) vs March (NE) reflects the latitudinal frost gradient.
  Summer months (Jun–Aug) show the warmest NE medians.

## Design Decisions

- **Static PNGs only.** No interactive dashboards — the deliverable is
  images for a report.
- **Report assembly is outside this subskill.** Use these individual PNGs
  as building blocks for a one-time report notebook or markdown document.
- **Not tracking generated outputs.** PNGs go under the runtime tree,
  never into git. Only the scripts and docs are committed.
- **EPSG:4326 source data.** Maps are reprojected to EPSG:3857 for
  Contextily basemap compatibility. Other plots use the raw projection.
- **`crop` on boundaries is the 2025 CSB label**, not the historic CDL.
  Year-over-year crop comparisons use CDL exclusively.
- **Weather data** comes from NASA POWER at the field centroid.
  Fields in the same grid cell share identical weather values — treat
  field-to-field differences within a grower as grid-cell effects.