"""Field boundary EDA — size distributions and location maps.

Phase 1
  - field_size_boxplot.png   horizontal box plot of acres per grower
  - field_locations_map.png  3-panel state/county maps (local geoadmin)

Phase 2
  - field_size_rank.png      sorted horizontal bar per grower
"""

from __future__ import annotations

import os
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# ---------------------------------------------------------------------------
# Grower lookup
# ---------------------------------------------------------------------------
GROWERS = {
    "IL": ("il-grower", "il-grower-illinois"),
    "IA": ("ia-grower", "ia-grower-iowa"),
    "NE": ("ne-grower", "ne-grower-nebraska"),
}


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
def load_boundaries(data_root: str) -> gpd.GeoDataFrame:
    """Load all 3 farm boundaries into a single GeoDataFrame.

    Adds ``grower`` (IL / IA / NE) and a numeric ``field_num`` column.
    """
    parts: list[gpd.GeoDataFrame] = []
    for state, (grower, farm) in GROWERS.items():
        path = (
            Path(data_root)
            / "data-pipeline"
            / "growers"
            / grower
            / "farms"
            / farm
            / "boundary"
            / "field_boundaries.geojson"
        )
        gdf = gpd.read_file(path)
        gdf["grower"] = state
        gdf["field_num"] = gdf["field_id"].str.extract(r"(\d+)").astype(int)
        parts.append(gdf)
    result = pd.concat(parts, ignore_index=True)
    return result


# ---------------------------------------------------------------------------
# Phase 1 — field size box plot
# ---------------------------------------------------------------------------
def plot_size_boxplot(
    gdf: gpd.GeoDataFrame, output_dir: str | os.PathLike
) -> str:
    """Horizontal box plot of field *area_acres* per grower.

    Returns the path of the saved PNG.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    palette = {"IL": "#4c72b0", "IA": "#55a868", "NE": "#d55e00"}

    sns.boxplot(
        data=gdf,
        x="area_acres",
        y="grower",
        hue="grower",
        palette=palette,
        order=["IL", "IA", "NE"],
        linewidth=1.5,
        width=0.5,
        ax=ax,
    )

    # Overlay strip plot for individual points
    sns.stripplot(
        data=gdf,
        x="area_acres",
        y="grower",
        hue="grower",
        palette=palette,
        order=["IL", "IA", "NE"],
        size=7,
        alpha=0.6,
        jitter=True,
        legend=False,
        ax=ax,
    )

    ax.set_xlabel("Field Area (acres)", fontsize=12)
    ax.set_ylabel("")
    ax.set_title("Field Size Distribution by Grower", fontsize=14, fontweight="bold")
    sns.despine()

    out = Path(output_dir) / "field_size_boxplot.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return str(out)


# ---------------------------------------------------------------------------
# Phase 1 — location map (local geoadmin, no tile server)
# ---------------------------------------------------------------------------
def plot_location_map(
    gdf: gpd.GeoDataFrame, output_dir: str | os.PathLike, data_root: str | None = None
) -> str:
    """3-panel map with local state + county background outlines.

    Each panel shows the 10 fields for that state overlaid on a geographic
    frame of the surrounding states with county lines.  No external tile
    servers — uses the runtime's geoadmin vector boundaries.
    """
    colors = {"IL": "#4c72b0", "IA": "#55a868", "NE": "#d55e00"}

    # Locate geoadmin data
    geoadmin_root = (
        Path(data_root) / "data-pipeline" / "shared" / "geoadmin"
        if data_root
        else Path(output_dir).parents[4] / "shared" / "geoadmin"
    )
    states_all = gpd.read_file(geoadmin_root / "l1_states" / "states_usa.geojson")
    counties_all = gpd.read_file(
        geoadmin_root / "l2_counties" / "counties_usa.geojson"
    )

    # Focal states (IL, IA, NE)
    focal_fips = ["17", "19", "31"]
    focal_states = states_all[states_all["state_fips"].isin(focal_fips)].copy()

    # Gather neighbouring states for visual context
    neighbour_fips: set[str] = set()
    for fips in focal_fips:
        fs = focal_states[focal_states["state_fips"] == fips]
        if not fs.empty:
            touches = states_all[
                states_all.intersects(fs.union_all())
            ]["state_fips"].tolist()
            neighbour_fips.update(touches)
    context_fips = [f for f in neighbour_fips if f not in focal_fips]
    context_states = states_all[states_all["state_fips"].isin(context_fips)]

    # Counties in focal states
    focal_counties = counties_all[counties_all["state_fips"].isin(focal_fips)]

    fig, axes = plt.subplots(1, 3, figsize=(18, 7))
    fig.suptitle("Field Locations by Grower", fontsize=15, fontweight="bold", y=0.96)

    fips_map = {"IL": "17", "IA": "19", "NE": "31"}

    for idx, state in enumerate(["IL", "IA", "NE"]):
        ax = axes[idx]
        fips = fips_map[state]
        subset = gdf[gdf["grower"] == state].copy()

        # Determine geographic extent from the focal state boundary
        state_poly = focal_states[focal_states["state_fips"] == fips]
        if not state_poly.empty:
            bounds = state_poly.total_bounds  # [minx, miny, maxx, maxy]
            ax.set_xlim(bounds[0] - 0.3, bounds[2] + 0.3)
            ax.set_ylim(bounds[1] - 0.3, bounds[3] + 0.3)

        # Context states (very light grey)
        if not context_states.empty:
            context_states.plot(
                ax=ax, facecolor="#f0f0f0", edgecolor="#cccccc", linewidth=0.5
            )

        # Focal state (light fill, prominent outline)
        focal_states[focal_states["state_fips"] == fips].plot(
            ax=ax, facecolor="#e8e8e8", edgecolor="black", linewidth=1.0
        )

        # County lines within the focal state
        counties_here = focal_counties[focal_counties["state_fips"] == fips]
        counties_here.plot(
            ax=ax, facecolor="none", edgecolor="#aaaaaa", linewidth=0.4
        )

        # Field polygons
        subset.plot(
            ax=ax,
            facecolor=colors[state],
            edgecolor="black",
            linewidth=0.6,
            alpha=0.75,
        )

        # Label each polygon with the field number
        for _, row in subset.iterrows():
            centroid = row.geometry.centroid
            ax.text(
                centroid.x,
                centroid.y,
                row["field_id"].split("-")[-1],
                fontsize=8,
                ha="center",
                va="center",
                color="white",
                fontweight="bold",
            )

        ax.set_title(f"{state} ({len(subset)} fields)", fontsize=12)
        ax.set_axis_off()

    plt.tight_layout()

    out = Path(output_dir) / "field_locations_map.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return str(out)


# ---------------------------------------------------------------------------
# Phase 2 — field size rank (horizontal bar)
# ---------------------------------------------------------------------------
def plot_size_rank(
    gdf: gpd.GeoDataFrame, output_dir: str | os.PathLike
) -> str:
    """Sorted horizontal bar of field area per grower (Phase 2).

    Returns path of the saved PNG.
    """
    colors = {"IL": "#4c72b0", "IA": "#55a868", "NE": "#d55e00"}

    fig, axes = plt.subplots(1, 3, figsize=(16, 7))
    fig.suptitle(
        "Field Size Ranking by Grower", fontsize=15, fontweight="bold", y=0.97
    )

    for idx, state in enumerate(["IL", "IA", "NE"]):
        ax = axes[idx]
        subset = gdf[gdf["grower"] == state].sort_values("area_acres", ascending=True)
        labels = subset["field_id"].tolist()
        sizes = subset["area_acres"].tolist()

        bars = ax.barh(
            labels, sizes, color=colors[state], edgecolor="black", linewidth=0.5
        )
        for bar, val in zip(bars, sizes):
            ax.text(
                bar.get_width() + 10,
                bar.get_y() + bar.get_height() / 2,
                f"{val:.0f}",
                va="center",
                fontsize=8,
            )

        ax.set_xlabel("Acres")
        ax.set_title(f"{state}")
        sns.despine()

    plt.tight_layout()

    out = Path(output_dir) / "field_size_rank.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return str(out)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    root = os.environ.get(
        "DATA_PIPELINE_DATA_ROOT",
        os.path.expanduser("~/my-farm-advisor-runtime"),
    )
    out_dir = Path(root) / "data-pipeline" / "eda" / "assignment2" / "output"

    bdf = load_boundaries(root)
    print("Boundaries loaded:", len(bdf), "features")

    for fn, phase in [
        (plot_size_boxplot, 1),
        (plot_location_map, 1),
        (plot_size_rank, 2),
    ]:
        p = fn(bdf, out_dir) if fn != plot_location_map else fn(bdf, out_dir, data_root=root)
        print(f"  Phase {phase}: {p}")