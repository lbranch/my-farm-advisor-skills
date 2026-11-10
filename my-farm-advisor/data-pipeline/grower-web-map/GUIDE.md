---
name: grower-web-map
description: Generate lightweight Leaflet interactive web maps for every grower in the data-pipeline runtime. Single-file HTML with field boundaries, satellite basemap, clickable metadata, and a field-list sidebar.
version: 1.0.0
author: Boreal Bytes (assignment-1)
tags: [web-map, visualization, leaflet, grower, fields, interactive]
---

# Workflow: grower-web-map

## Description

Generate a self-contained HTML interactive map for each grower in the pipeline runtime. Each map shows the grower's field polygons on an ESRI World Imagery satellite basemap with OpenStreetMap street toggle, clickable field popups with metadata, and a sidebar field list with "Zoom to" controls.

## When to Use

- **Visual review**: See all fields for a grower on a satellite basemap with metadata at a glance.
- **Sharing**: Email or host the single HTML file; no server or installation needed.
- **Field reference**: Load the map on a tablet during field visits.

## Output

A single HTML file per grower at:

```
${DATA_PIPELINE_DATA_ROOT}/data-pipeline/growers/<grower>/farms/<farm>/derived/reports/<grower>_<farm>_grower_map.html
```

Typical file size: 100-500 KB for 3-10 fields (geometry simplified).

## Map Features

- **ESRI World Imagery** satellite basemap (default)
- **OpenStreetMap** street basemap (toggle via layer control)
- Field polygons with colored fills per field
- Click popups showing: grower slug, farm name, field ID, area (acres), county, crop, source
- Sidebar list of all fields — click a field name to zoom to its bounds
- Full zoom, pan, and standard Leaflet interactivity

## Prerequisites

- `DATA_PIPELINE_DATA_ROOT` environment variable set
- Data pipeline installed and growers created at that root
- Python with `geopandas` and `shapely` (included in the pipeline venv)

## Usage

```bash
export DATA_PIPELINE_DATA_ROOT=/absolute/path/to/my-farm-advisor-runtime
cd "${DATA_PIPELINE_DATA_ROOT}/data-pipeline/src"
"${DATA_PIPELINE_DATA_ROOT}/data-pipeline/.venv/bin/python" \
  scripts/reporting/generate_grower_web_map.py
```

The script auto-discovers all growers with boundary files under the runtime root.

## Single-grower mode (optional)

For faster iteration on one grower:

```bash
"${DATA_PIPELINE_DATA_ROOT}/data-pipeline/.venv/bin/python" \
  scripts/reporting/generate_grower_web_map.py \
  --grower-slug il-grower
```

## Implementation Notes

- Geometry is simplified with `simplify(tolerance=0.0005)` to keep HTML output small.
- Leaflet CSS/JS are loaded from CDN; the map requires internet for basemap tiles and Leaflet library.
- Field metadata comes entirely from the boundary GeoJSON properties.
- No raster data, large CSVs, or binary assets are embedded.

## Resources

- [Leaflet](https://leafletjs.com/) — Open-source JavaScript library for interactive maps
- [ESRI World Imagery](https://www.esri.com/en-us/arcgis/products/arcgis-living-atlas) — Satellite tile layer