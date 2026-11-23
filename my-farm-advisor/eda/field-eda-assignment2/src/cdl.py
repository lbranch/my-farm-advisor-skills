"""CDL / cropland EDA — crop domination, rotation intensity, time trends.

Phase 1
  - cdl_2023_dominant_crop.png   stacked bar of dominant crop per grower

Phase 2
  - cdl_corn_years.png           histogram of corn-years per field
  - cdl_corn_proportion_trend.png  line plot of corn % per year per grower
"""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# ---------------------------------------------------------------------------
# Grower lookup
# ---------------------------------------------------------------------------
GROWERS = {
    "IL": ("il-grower", "il-grower-illinois", "il_grower_illinois"),
    "IA": ("ia-grower", "ia-grower-iowa", "ia_grower_iowa"),
    "NE": ("ne-grower", "ne-grower-nebraska", "ne_grower_nebraska"),
}


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
def load_composition(data_root: str) -> pd.DataFrame:
    """Load all 3 full-composition CSVs.

    Returns a single DataFrame with an extra ``grower`` column.
    """
    parts: list[pd.DataFrame] = []
    for state, (grower, farm, slug) in GROWERS.items():
        path = (
            Path(data_root)
            / "data-pipeline"
            / "growers"
            / grower
            / "farms"
            / farm
            / "derived"
            / "tables"
            / f"{slug}_cdl_2019_2023_full_composition.csv"
        )
        df = pd.read_csv(path)
        df["grower"] = state
        parts.append(df)
    return pd.concat(parts, ignore_index=True)


def load_rotation(data_root: str) -> pd.DataFrame:
    """Load all 3 crop-rotation CSVs.

    Returns a single DataFrame with a ``grower`` column.
    """
    parts: list[pd.DataFrame] = []
    for state, (grower, farm, slug) in GROWERS.items():
        path = (
            Path(data_root)
            / "data-pipeline"
            / "growers"
            / grower
            / "farms"
            / farm
            / "derived"
            / "tables"
            / f"{slug}_crop_rotation.csv"
        )
        df = pd.read_csv(path)
        df["grower"] = state
        parts.append(df)
    return pd.concat(parts, ignore_index=True)


# ---------------------------------------------------------------------------
# Phase 1 — 2023 dominant crop
# ---------------------------------------------------------------------------
def plot_2023_dominant_crop(
    comp: pd.DataFrame, output_dir: str | os.PathLike
) -> str:
    """Stacked / grouped bar of dominant crop per field for 2023.

    Dominant = the crop category with the highest ``pct`` for each
    field × year.
    """
    df = comp[comp["year"] == 2023].copy()
    # Find dominant crop per field
    idx = df.groupby(["grower", "field_id"])["pct"].idxmax()
    dom = df.loc[idx, ["grower", "field_id", "crop_name"]]

    # Count fields by (grower, crop_name)
    tally = dom.groupby(["grower", "crop_name"]).size().reset_index(name="count")

    palette = {"IL": "#4c72b0", "IA": "#55a868", "NE": "#d55e00"}

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=tally,
        x="grower",
        y="count",
        hue="crop_name",
        order=["IL", "IA", "NE"],
        ax=ax,
    )
    ax.set_xlabel("")
    ax.set_ylabel("Number of Fields (dominant crop)", fontsize=12)
    ax.set_title(
        "2023 Dominant Crop per Field by Grower", fontsize=14, fontweight="bold"
    )
    ax.legend(title="Crop", fontsize=9, title_fontsize=10)
    sns.despine()

    out = Path(output_dir) / "cdl_2023_dominant_crop.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return str(out)


# ---------------------------------------------------------------------------
# Phase 2 — corn years histogram
# ---------------------------------------------------------------------------
def plot_corn_years(
    rotation: pd.DataFrame, output_dir: str | os.PathLike
) -> str:
    """Histogram of *corn_years* per field, faceted by grower."""
    palette = {"IL": "#4c72b0", "IA": "#55a868", "NE": "#d55e00"}

    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
    fig.suptitle("Corn Years (out of 5) per Field", fontsize=14, fontweight="bold")

    for idx, state in enumerate(["IL", "IA", "NE"]):
        ax = axes[idx]
        subset = rotation[rotation["grower"] == state]
        vals = subset["corn_years"].value_counts().sort_index()
        ax.bar(
            vals.index,
            vals.values,
            width=0.6,
            color=palette[state],
            edgecolor="black",
            linewidth=0.8,
        )
        ax.set_title(f"{state}  (n={len(subset)})")
        ax.set_xlabel("Corn Years")
        ax.set_ylabel("Field Count")
        ax.set_xticks(range(0, 6))
        sns.despine()

    plt.tight_layout()

    out = Path(output_dir) / "cdl_corn_years.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return str(out)


# ---------------------------------------------------------------------------
# Phase 2 — corn proportion over time
# ---------------------------------------------------------------------------
def plot_corn_proportion_trend(
    comp: pd.DataFrame, output_dir: str | os.PathLike
) -> str:
    """Line: corn pixel % per year per grower, 2019–2023.

    Calculated as (corn pixel_count / total classified pixel_count)
    for each grower × year.
    """
    # Classify corn (crop_code == 1)
    comp["is_corn"] = comp["crop_code"] == 1

    yearly = (
        comp.groupby(["grower", "year"])
        .apply(
            lambda grp: grp[grp["is_corn"]]["pixel_count"].sum()
            / grp["pixel_count"].sum()
            * 100,
            include_groups=False,
        )
        .reset_index(name="corn_pct")
    )

    colors = {"IL": "#4c72b0", "IA": "#55a868", "NE": "#d55e00"}

    fig, ax = plt.subplots(figsize=(10, 6))
    for state in ["IL", "IA", "NE"]:
        subset = yearly[yearly["grower"] == state].sort_values("year")
        ax.plot(
            subset["year"],
            subset["corn_pct"],
            marker="o",
            linewidth=2.5,
            label=state,
            color=colors[state],
        )
        # Annotate points
        for _, row in subset.iterrows():
            ax.annotate(
                f"{row['corn_pct']:.1f}%",
                (row["year"], row["corn_pct"]),
                textcoords="offset points",
                xytext=(0, 12),
                fontsize=9,
                ha="center",
            )

    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Corn Share of Classified Pixels (%)", fontsize=12)
    ax.set_title(
        "Corn Proportion Over Time (2019–2023)", fontsize=14, fontweight="bold"
    )
    ax.set_xticks(range(2019, 2024))
    ax.legend(title="Grower", fontsize=10)
    sns.despine()

    out = Path(output_dir) / "cdl_corn_proportion_trend.png"
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

    comp = load_composition(root)
    rot = load_rotation(root)
    print("CDL composition loaded:", len(comp), "rows")
    print("Rotation loaded:", len(rot), "rows")

    for fn, phase in [
        (plot_2023_dominant_crop, 1),
        (plot_corn_years, 2),
        (plot_corn_proportion_trend, 2),
    ]:
        if fn == plot_2023_dominant_crop:
            p = fn(comp, out_dir)
        elif fn == plot_corn_years:
            p = fn(rot, out_dir)
        else:
            p = fn(comp, out_dir)
        print(f"  Phase {phase}: {p}")