"""Weather EDA — regime comparison, seasonal cycles, example time series.

Phase 1
  - weather_regime_scatter.png   annual T2M vs PRECTOTCORR per field-year

Phase 2
  - weather_example_timeseries.png   dual-axis T2M + precip, 1 field/grower
  - weather_monthly_temperature.png   box plot per month × grower
"""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

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
def load_weather(data_root: str) -> pd.DataFrame:
    """Load all 3 farm weather CSVs.

    Returns a single DataFrame with ``grower`` and ``date`` (datetime).
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
            / f"{slug}_weather_2021_2025.csv"
        )
        df = pd.read_csv(path, parse_dates=["date"])
        df["grower"] = state
        parts.append(df)
    return pd.concat(parts, ignore_index=True)


def _annual_aggregates(weather: pd.DataFrame) -> pd.DataFrame:
    """Compute annual T2M mean and PRECTOTCORR sum per field per year."""
    weather["year"] = weather["date"].dt.year
    agg = (
        weather.groupby(["grower", "field_id", "year"])
        .agg(
            mean_temp=("T2M", "mean"),
            total_precip=("PRECTOTCORR", "sum"),
        )
        .reset_index()
    )
    return agg


# ---------------------------------------------------------------------------
# Phase 1 — regime scatter
# ---------------------------------------------------------------------------
def plot_regime_scatter(
    weather: pd.DataFrame, output_dir: str | os.PathLike
) -> str:
    """Scatter of annual mean T2M vs annual total PRECTOTCORR.

    One point per field-year.  Coloured by grower with linear trend lines.
    """
    agg = _annual_aggregates(weather)
    colors = {"IL": "#4c72b0", "IA": "#55a868", "NE": "#d55e00"}
    markers = {"IL": "o", "IA": "s", "NE": "^"}

    fig, ax = plt.subplots(figsize=(10, 7))

    for state in ["IL", "IA", "NE"]:
        subset = agg[agg["grower"] == state]
        ax.scatter(
            subset["mean_temp"],
            subset["total_precip"],
            c=colors[state],
            marker=markers[state],
            label=state,
            s=50,
            alpha=0.7,
            edgecolors="black",
            linewidths=0.4,
        )
        # Linear trend line
        slope, intercept, r_val, p_val, std_err = stats.linregress(
            subset["mean_temp"], subset["total_precip"]
        )
        x_vals = np.linspace(subset["mean_temp"].min(), subset["mean_temp"].max(), 50)
        y_vals = slope * x_vals + intercept
        ax.plot(
            x_vals,
            y_vals,
            color=colors[state],
            linestyle="--",
            linewidth=1.5,
            alpha=0.6,
            label=f"{state} trend (r²={r_val**2:.2f})",
        )

    ax.set_xlabel("Mean Annual Temperature (°C)", fontsize=12)
    ax.set_ylabel("Total Annual Precipitation (mm)", fontsize=12)
    ax.set_title(
        "Weather Regimes: Temperature vs Precipitation", fontsize=14, fontweight="bold"
    )
    ax.legend(fontsize=9, loc="upper left")
    sns.despine()

    out = Path(output_dir) / "weather_regime_scatter.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return str(out)


# ---------------------------------------------------------------------------
# Phase 2 — example field time series
# ---------------------------------------------------------------------------
def plot_example_timeseries(
    weather: pd.DataFrame, output_dir: str | os.PathLike
) -> str:
    """Dual-axis time series for one representative field per grower.

    Chooses the field with the median total area  (approximated by the
    median row count — all fields have 1826 rows so the first field per
    grower is used as a simple proxy).
    """
    colors = {"IL": "#4c72b0", "IA": "#55a868", "NE": "#d55e00"}

    fig, axes = plt.subplots(3, 1, figsize=(14, 12), sharex=True)
    fig.suptitle(
        "Daily Temperature and Precipitation — One Field per Grower",
        fontsize=14,
        fontweight="bold",
        y=1.01,
    )

    for idx, state in enumerate(["IL", "IA", "NE"]):
        ax = axes[idx]
        # Pick the first field for this grower
        field = weather[weather["grower"] == state]["field_id"].iloc[0]
        subset = (
            weather[(weather["grower"] == state) & (weather["field_id"] == field)]
            .sort_values("date")
            .copy()
        )

        ax.fill_between(
            subset["date"],
            subset["T2M_MIN"],
            subset["T2M_MAX"],
            alpha=0.2,
            color=colors[state],
            label="T2M range",
        )
        ax.plot(
            subset["date"],
            subset["T2M"],
            color=colors[state],
            linewidth=0.7,
            label="T2M mean",
        )
        ax.set_ylabel("Temperature (°C)", color=colors[state], fontsize=10)
        ax.tick_params(axis="y", labelcolor=colors[state])

        # Precip on secondary axis
        ax2 = ax.twinx()
        ax2.bar(
            subset["date"],
            subset["PRECTOTCORR"],
            color="#2ca02c",
            alpha=0.25,
            width=1.5,
            label="Precip",
        )
        ax2.set_ylabel("Precipitation (mm/day)", color="#2ca02c", fontsize=10)
        ax2.tick_params(axis="y", labelcolor="#2ca02c")

        ax.set_title(f"{state} — {field}", fontsize=12, loc="left")
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

    plt.tight_layout()

    out = Path(output_dir) / "weather_example_timeseries.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return str(out)


# ---------------------------------------------------------------------------
# Phase 2 — monthly temperature box plots
# ---------------------------------------------------------------------------
def plot_monthly_temperatures(
    weather: pd.DataFrame, output_dir: str | os.PathLike
) -> str:
    """Box plots of T2M per month, faceted by grower.

    Uses all fields and all years pooled.
    """
    weather["month"] = weather["date"].dt.month
    month_labels = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]

    colors = {"IL": "#4c72b0", "IA": "#55a868", "NE": "#d55e00"}

    fig, axes = plt.subplots(3, 1, figsize=(12, 12), sharex=True)
    fig.suptitle(
        "Monthly Temperature Distributions", fontsize=14, fontweight="bold", y=1.01
    )

    for idx, state in enumerate(["IL", "IA", "NE"]):
        ax = axes[idx]
        subset = weather[weather["grower"] == state]
        sns.boxplot(
            data=subset,
            x="month",
            y="T2M",
            color=colors[state],
            width=0.6,
            linewidth=0.8,
            ax=ax,
        )
        ax.set_title(f"{state}  (n={len(subset):,} daily records)", fontsize=12)
        ax.set_ylabel("T2M (°C)", fontsize=10)
        if idx == 2:
            ax.set_xlabel("Month", fontsize=11)
            ax.set_xticks(range(12))
            ax.set_xticklabels(month_labels)
        else:
            ax.set_xlabel("")
        sns.despine()

    plt.tight_layout()

    out = Path(output_dir) / "weather_monthly_temperature.png"
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

    wdf = load_weather(root)
    print("Weather loaded:", len(wdf), "rows across", wdf["field_id"].nunique(), "fields")

    for fn, phase in [
        (plot_regime_scatter, 1),
        (plot_example_timeseries, 2),
        (plot_monthly_temperatures, 2),
    ]:
        p = fn(wdf, out_dir)
        print(f"  Phase {phase}: {p}")