#!/usr/bin/env python3
"""Orchestrator: run Phase 1 or all 9 Assignment 2 EDA plots.

Usage
-----
    python src/run_all.py           # Phase 1 only (4 plots)
    python src/run_all.py --all     # Phase 1 + Phase 2 (9 plots)
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

# Ensure the src directory is importable
THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

import boundaries
import cdl
import weather


def main() -> int:
    parser = argparse.ArgumentParser(description="Assignment 2 Field EDA — all plots")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run Phase 2 plots in addition to Phase 1",
    )
    parser.add_argument(
        "--data-root",
        default=os.environ.get(
            "DATA_PIPELINE_DATA_ROOT",
            os.path.expanduser("~/my-farm-advisor-runtime"),
        ),
        help="Override DATA_PIPELINE_DATA_ROOT",
    )
    args = parser.parse_args()

    root = args.data_root
    out_dir = Path(root) / "data-pipeline" / "eda" / "assignment2" / "output"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Assignment 2 — Field-Level EDA")
    print(f"  Data root : {root}")
    print(f"  Output    : {out_dir}")
    print(f"  Mode      : {'Phase 1 + Phase 2' if args.all else 'Phase 1 only'}")
    print("=" * 60)

    # ------------------------------------------------------------------
    # Load data (once)
    # ------------------------------------------------------------------
    t0 = time.time()
    bdf = boundaries.load_boundaries(root)
    comp = cdl.load_composition(root)
    rot = cdl.load_rotation(root)
    wdf = weather.load_weather(root)
    load_s = time.time() - t0
    print(f"\nData loaded in {load_s:.1f}s:")
    print(f"  Boundaries  : {len(bdf)} features")
    print(f"  CDL comp.   : {len(comp)} rows")
    print(f"  Rotation    : {len(rot)} rows")
    print(f"  Weather     : {len(wdf)} rows ({wdf['field_id'].nunique()} fields)")

    # ------------------------------------------------------------------
    # Phase 1 plots
    # ------------------------------------------------------------------
    phase1: list[tuple] = [
        (boundaries.plot_size_boxplot, (bdf, out_dir), "field_size_boxplot"),
        (boundaries.plot_location_map, (bdf, out_dir, root), "field_locations_map"),
        (cdl.plot_2023_dominant_crop, (comp, out_dir), "cdl_2023_dominant_crop"),
        (weather.plot_regime_scatter, (wdf, out_dir), "weather_regime_scatter"),
    ]

    print("\n--- Phase 1 ---")
    for func, args_list, label in phase1:
        t1 = time.time()
        path = func(*args_list)
        elapsed = time.time() - t1
        print(f"  {label:40s} {elapsed:.1f}s  {path}")

    # ------------------------------------------------------------------
    # Phase 2 plots
    # ------------------------------------------------------------------
    if args.all:
        phase2: list[tuple] = [
            (boundaries.plot_size_rank, (bdf, out_dir), "field_size_rank"),
            (cdl.plot_corn_years, (rot, out_dir), "cdl_corn_years"),
            (
                cdl.plot_corn_proportion_trend,
                (comp, out_dir),
                "cdl_corn_proportion_trend",
            ),
            (
                weather.plot_example_timeseries,
                (wdf, out_dir),
                "weather_example_timeseries",
            ),
            (
                weather.plot_monthly_temperatures,
                (wdf, out_dir),
                "weather_monthly_temperature",
            ),
        ]

        print("\n--- Phase 2 ---")
        for func, args_list, label in phase2:
            t1 = time.time()
            path = func(*args_list)
            elapsed = time.time() - t1
            print(f"  {label:40s} {elapsed:.1f}s  {path}")
    else:
        print("\nSkipping Phase 2. Re-run with --all to generate all 9 plots.")

    total = time.time() - t0
    print(f"\nDone in {total:.1f}s")

    # List output files
    print(f"\nOutput directory listing ({out_dir}):")
    for p in sorted(out_dir.glob("*.png")):
        size_kb = p.stat().st_size / 1024
        print(f"  {p.name:45s} {size_kb:.1f} KB")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())