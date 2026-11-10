# Grower Web Map Examples

## Generated Output

After running the script, output maps land at:

```
${DATA_PIPELINE_DATA_ROOT}/data-pipeline/growers/<grower>/farms/<farm>/derived/reports/<grower>_<farm>_grower_map.html
```

## How to Generate

```bash
export DATA_PIPELINE_DATA_ROOT=/absolute/path/to/my-farm-advisor-runtime
cd "${DATA_PIPELINE_DATA_ROOT}/data-pipeline/src"
"${DATA_PIPELINE_DATA_ROOT}/data-pipeline/.venv/bin/python" \
  scripts/reporting/generate_grower_web_map.py
```

## Usage

Open the generated `.html` file in any modern web browser. Features:

- Satellite basemap (ESRI World Imagery)
- Toggle to OpenStreetMap street view via the layer control
- Colour-coded field polygons — click a field for metadata (grower, farm, field ID, area, county, crop, source)
- Sidebar with a list of all fields — click a field name or its "Zoom" button to zoom directly to that field
- Standard zoom/pan Leaflet controls

## Data Source

- **Input**: `${DATA_PIPELINE_DATA_ROOT}/data-pipeline/growers/<grower>/farms/<farm>/boundary/field_boundaries.geojson`
- **Fields**: Real USDA CSB polygons downloaded during pipeline setup
- **Library**: Pure Leaflet.js (loaded from CDN), no folium dependency