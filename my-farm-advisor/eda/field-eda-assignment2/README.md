# Field EDA — Assignment 2

**Skill:** `field-eda-assignment2`  
**Location:** `my-farm-advisor/eda/field-eda-assignment2/`  
**Dataset:** 3 growers (IL, IA, NE) × 10 fields = 30 fields  
**Generates:** 9 static PNGs  
**Outputs:** `${DATA_PIPELINE_DATA_ROOT}/data-pipeline/eda/assignment2/output/`  
**Report PDF:** `my-farm-advisor/eda/field-eda-assignment2/report/assignment-2-eda-report.pdf`

| Module | Files |
|---|---|
| Boundaries | `field_size_boxplot.png`, `field_size_rank.png`, `field_locations_map.png` |
| CDL / Cropland | `cdl_2023_dominant_crop.png`, `cdl_corn_years.png`, `cdl_corn_proportion_trend.png` |
| Weather | `weather_regime_scatter.png`, `weather_example_timeseries.png`, `weather_monthly_temperature.png` |

## Quick Start

```bash
export DATA_PIPELINE_DATA_ROOT="$HOME/my-farm-advisor-runtime"

cd /home/coder/my-farm-advisor-skills/my-farm-advisor/eda/field-eda-assignment2

# Run Phase 1 (4 plots):
python src/run_all.py

# Run all 9 plots (Phase 1 + Phase 2):
python src/run_all.py --all
```

Output directory:
```bash
ls -la "${DATA_PIPELINE_DATA_ROOT}/data-pipeline/eda/assignment2/output/"
```

## Plot Catalog

| Module | Plot | Phase |
|---|---|---|
| `boundaries.py` | `field_size_boxplot.png` | 1 |
| `boundaries.py` | `field_locations_map.png` | 1 |
| `boundaries.py` | `field_size_rank.png` | 2 |
| `cdl.py` | `cdl_2023_dominant_crop.png` | 1 |
| `cdl.py` | `cdl_corn_years.png` | 2 |
| `cdl.py` | `cdl_corn_proportion_trend.png` | 2 |
| `weather.py` | `weather_regime_scatter.png` | 1 |
| `weather.py` | `weather_example_timeseries.png` | 2 |
| `weather.py` | `weather_monthly_temperature.png` | 2 |

## Runtime Data

All data paths resolve from `$DATA_PIPELINE_DATA_ROOT/data-pipeline/growers/…`.
The `.venv` from the data pipeline provides all dependencies.