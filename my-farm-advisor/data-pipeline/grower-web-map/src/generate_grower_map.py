#!/usr/bin/env python3
"""Generate lightweight Leaflet interactive web maps for every grower.

Reads each grower's field_boundaries.geojson from the pipeline runtime,
generates a self-contained HTML file with a satellite basemap, clickable
field popups, and a field-list sidebar with "Zoom to" controls.

Output goes to each farm's ``derived/reports/`` directory alongside existing
reports.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import geopandas as gpd


# ---------------------------------------------------------------------------
# HTML template (Leaflet-based, no folium dependency)
# ---------------------------------------------------------------------------
def _html_template(
    geojson_str: str,
    title: str,
    center_lat: float,
    center_lon: float,
    fields_meta: list[dict[str, Any]],
) -> str:
    """Return a self-contained Leaflet HTML page with embedded GeoJSON."""
    fields_json = json.dumps(fields_meta)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; display: flex; height: 100vh; }}
    #sidebar {{
      width: 280px; min-width: 280px;
      background: #ffffff; border-right: 1px solid #ccc;
      display: flex; flex-direction: column; overflow: hidden;
    }}
    #sidebar h2 {{
      font-size: 1.1rem; padding: 14px 12px 8px; color: #1B5E20;
      border-bottom: 1px solid #eee;
    }}
    #sidebar .grower-info {{
      padding: 4px 12px 10px; font-size: 0.85rem; color: #555;
      border-bottom: 1px solid #eee;
    }}
    #field-list {{
      flex: 1; overflow-y: auto; padding: 6px 0;
    }}
    .field-item {{
      display: flex; align-items: center; justify-content: space-between;
      padding: 8px 12px; cursor: pointer; border-bottom: 1px solid #f0f0f0;
      transition: background 0.15s;
    }}
    .field-item:hover {{ background: #e8f5e9; }}
    .field-item .name {{ font-weight: 500; font-size: 0.9rem; }}
    .field-item .area {{ font-size: 0.75rem; color: #888; margin-left: 8px; }}
    .field-item .zoom-btn {{
      font-size: 0.7rem; padding: 2px 8px; border: 1px solid #4CAF50;
      background: white; border-radius: 3px; cursor: pointer; color: #2E7D32;
    }}
    .field-item .zoom-btn:hover {{ background: #4CAF50; color: white; }}
    #map {{ flex: 1; }}
    .leaflet-popup-content {{ font-size: 0.85rem; line-height: 1.5; }}
    .leaflet-popup-content strong {{ color: #1B5E20; }}
    #video-container {{
      flex-shrink: 0;
      border-top: 1px solid #ddd;
      background: #000;
      max-height: 160px;
      overflow: hidden;
    }}
    #video-container video {{
      display: block;
      width: 100%;
      height: auto;
      max-height: 160px;
    }}
  </style>
</head>
<body>
  <div id="sidebar">
    <h2>🌾 {title}</h2>
    <div class="grower-info" id="grower-info"></div>
    <div id="field-list"></div>
    <div id="video-container">
      <video src="https://restless-fog-c79d.lonnellbranch.workers.dev/agintro.mp4" autoplay muted loop playsinline></video>
    </div>
  </div>
  <div id="map"></div>

  <script>
    // ---- embedded field data ----
    const fieldData = {geojson_str};
    const fieldsMeta = {fields_json};

    // ---- basemap layers ----
    const satellite = L.tileLayer(
      'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}',
      {{ attribution: '&copy; Esri, Maxar, Earthstar Geographics', maxZoom: 19 }}
    );
    const streets = L.tileLayer(
      'https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
      {{ attribution: '&copy; OpenStreetMap contributors', maxZoom: 19 }}
    );

    // ---- init map ----
    const map = L.map('map', {{
      layers: [satellite],
      center: [{center_lat}, {center_lon}],
      zoom: 9,
    }});

    // ---- layer control ----
    L.control.layers({{ 'Satellite': satellite, 'Street': streets }}).addTo(map);

    // ---- colour palette for fields ----
    const palette = [
      '#e6194b','#3cb44b','#ffe119','#4363d8','#f58231',
      '#911eb4','#42d4f4','#f032e6','#bfef45','#fabed4',
    ];

    // ---- render fields ----
    const fieldLayer = L.geoJSON(fieldData, {{
      style: function (feature) {{
        const idx = (feature.properties.field_id) ? feature.properties.field_id.length % palette.length : 0;
        return {{
          color: '#333', weight: 1.5, opacity: 0.8,
          fillColor: palette[idx], fillOpacity: 0.45,
        }};
      }},
      onEachFeature: function (feature, layer) {{
        const p = feature.properties || {{}};
        const html = `
          <strong>Field:</strong> ${{p.field_id || '?'}}<br>
          <strong>Grower:</strong> ${{p.grower_slug || '?'}}<br>
          <strong>Farm:</strong> ${{p.farm_name || p.farm_slug || '?'}}<br>
          ${{p.area_acres ? '<strong>Area:</strong> ' + Number(p.area_acres).toLocaleString() + ' ac<br>' : ''}}
          ${{p.county ? '<strong>County:</strong> ' + p.county + '<br>' : ''}}
          ${{p.crop && p.crop !== '?' ? '<strong>Crop:</strong> ' + p.crop + '<br>' : ''}}
          ${{p.source ? '<strong>Source:</strong> ' + p.source + '<br>' : ''}}
        `.trim();
        layer.bindPopup(html);
        layer.on('mouseover', function () {{ this.setStyle({{ weight: 3, color: '#222' }}); }});
        layer.on('mouseout', function () {{ this.setStyle({{ weight: 1.5, color: '#333' }}); }});
      }}
    }}).addTo(map);

    // ---- fit to bounds ----
    const allBounds = fieldLayer.getBounds();
    if (allBounds.isValid()) {{
      map.fitBounds(allBounds.pad(0.08));
    }}

    // ---- populate sidebar ----
    const growerInfo = document.getElementById('grower-info');
    if (fieldsMeta.length > 0) {{
      const first = fieldsMeta[0];
      growerInfo.innerHTML =
        '<strong>Grower:</strong> ' + (first.grower_slug || '?') + '<br>' +
        '<strong>Farm:</strong> ' + (first.farm_name || first.farm_slug || '?') + '<br>' +
        '<strong>Fields:</strong> ' + fieldsMeta.length;
    }}

    const listEl = document.getElementById('field-list');
    const fieldLayers = {{}};
    fieldLayer.eachLayer(function (layer) {{
      const fid = layer.feature.properties.field_id;
      if (fid) fieldLayers[fid] = layer;
    }});

    fieldsMeta.forEach(function (m, i) {{
      const div = document.createElement('div');
      div.className = 'field-item';
      div.innerHTML = `
        <div>
          <div class="name">${{m.field_id || 'Field ' + (i+1)}}</div>
          <div class="area">${{m.county || ''}}${{m.area_acres ? ' \\u00b7 ' + Number(m.area_acres).toLocaleString() + ' ac' : ''}}${{m.crop && m.crop !== '?' ? ' \\u00b7 ' + m.crop : ''}}</div>
        </div>
        <button class="zoom-btn" data-fid="${{m.field_id || ''}}">Zoom</button>
      `;
      div.querySelector('.zoom-btn').addEventListener('click', function (e) {{
        e.stopPropagation();
        const fid = this.dataset.fid;
        const layer = fieldLayers[fid];
        if (layer) {{ map.fitBounds(layer.getBounds().pad(0.3)); }}
      }});
      div.addEventListener('click', function () {{
        const fid = m.field_id;
        const layer = fieldLayers[fid];
        if (layer) {{ map.fitBounds(layer.getBounds().pad(0.3)); }}
      }});
      listEl.appendChild(div);
    }});
  </script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_all_growers(data_root: Path) -> list[dict[str, Any]]:
    """Discover every grower with a farm that has a field boundaries file.

    Grower data lives under ``data_root / "data-pipeline" / "growers"``
    (the canonical data-pipeline runtime layout).
    """
    growers: list[dict[str, Any]] = []
    growers_dir = data_root / "data-pipeline" / "growers"
    if not growers_dir.is_dir():
        return growers

    for grower_dir in sorted(growers_dir.iterdir()):
        if not grower_dir.is_dir():
            continue
        grower_slug = grower_dir.name
        farms_dir = grower_dir / "farms"
        if not farms_dir.is_dir():
            continue
        for farm_dir in sorted(farms_dir.iterdir()):
            if not farm_dir.is_dir():
                continue
            bounds_file = farm_dir / "boundary" / "field_boundaries.geojson"
            if not bounds_file.is_file():
                continue
            farm_slug = farm_dir.name
            growers.append({
                "grower_slug": grower_slug,
                "farm_slug": farm_slug,
                "farm_dir": farm_dir,
                "bounds_file": bounds_file,
            })
    return growers


def _load_farm_json(farm_dir: Path) -> dict[str, Any]:
    """Read farm.json for display name, or return empty dict."""
    fj = farm_dir / "manifests" / "farm.json"
    if fj.is_file():
        try:
            return json.loads(fj.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def generate_grower_map(data_root: str | Path) -> list[Path]:
    """Generate a web map for every grower in the pipeline runtime.

    Returns a list of output HTML paths.
    """
    data_root = Path(data_root).expanduser().resolve()
    growers = _find_all_growers(data_root)
    if not growers:
        print("No growers with boundaries found under", data_root / "data-pipeline" / "growers")
        return []

    outputs: list[Path] = []

    for info in growers:
        gsl = info["grower_slug"]
        fsl = info["farm_slug"]
        bounds_file = info["bounds_file"]
        farm_dir = info["farm_dir"]

        farm_meta = _load_farm_json(farm_dir)
        farm_name = farm_meta.get("farm_name", fsl)

        # ---- load boundaries ----
        gdf: gpd.GeoDataFrame = gpd.read_file(bounds_file)
        if gdf.empty:
            print(f"  {gsl}/{fsl}: empty boundary file, skipping")
            continue
        if gdf.crs is not None and gdf.crs.is_geographic is False:
            gdf = gdf.to_crs("EPSG:4326")

        # ---- add grower/farm metadata to properties ----
        gdf["grower_slug"] = gsl
        gdf["farm_slug"] = fsl
        gdf["farm_name"] = farm_name

        # ---- simplify geometry ---- (keep output small)
        gdf["geometry"] = gdf["geometry"].simplify(tolerance=0.0005)

        # ---- centre point ----
        # Project to a continental CRS for an accurate centroid, then back to WGS84.
        gdf_proj = gdf.to_crs("EPSG:5070")  # NAD83 Conus Albers
        cx_proj = float(gdf_proj.geometry.centroid.x.mean())
        cy_proj = float(gdf_proj.geometry.centroid.y.mean())
        from pyproj import Transformer  # noqa: PLC0415
        t = Transformer.from_crs("EPSG:5070", "EPSG:4326", always_xy=True)
        cx, cy = t.transform(cx_proj, cy_proj)

        # ---- build fields_meta for sidebar ----
        fields_meta: list[dict[str, Any]] = []
        for _, row in gdf.iterrows():
            meta: dict[str, Any] = {}
            for col in gdf.columns:
                if col != "geometry":
                    val = row[col]
                    if isinstance(val, (float, int)):
                        val = round(float(val), 2) if isinstance(val, float) else int(val)
                    meta[col] = val
            fields_meta.append(meta)

        # ---- serialise GeoJSON ----
        geojson_str = gdf.to_json()

        # ---- title ----
        title = f"{farm_name} – {gsl}"

        # ---- render HTML ----
        html = _html_template(
            geojson_str=geojson_str,
            title=title,
            center_lat=cy,
            center_lon=cx,
            fields_meta=fields_meta,
        )

        # ---- output path ----
        reports_dir = farm_dir / "derived" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        out_path = reports_dir / f"{gsl}_{fsl}_grower_map.html"
        out_path.write_text(html, encoding="utf-8")
        size_kb = round(out_path.stat().st_size / 1024, 1)
        print(f"  {gsl}/{fsl}: {out_path.relative_to(data_root)}  ({size_kb} KB, {len(gdf)} fields)")
        outputs.append(out_path)

    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Leaflet interactive web maps for every grower."
    )
    parser.add_argument(
        "--data-root",
        default=os.environ.get("DATA_PIPELINE_DATA_ROOT"),
        help="Pipeline runtime root (default: $DATA_PIPELINE_DATA_ROOT)",
    )
    parser.add_argument(
        "--grower-slug",
        default=None,
        help="Optional: only process this grower slug",
    )
    args = parser.parse_args()

    data_root = args.data_root
    if not data_root:
        print("ERROR: DATA_PIPELINE_DATA_ROOT is not set.", file=sys.stderr)
        sys.exit(1)

    data_root_path = Path(data_root).expanduser().resolve()
    outputs = generate_grower_map(data_root_path)

    if not outputs:
        print("No maps generated.")
        sys.exit(1)

    print(f"\nDone — {len(outputs)} map(s) generated.")


if __name__ == "__main__":
    main()