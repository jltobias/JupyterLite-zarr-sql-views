# Port cities and AR6 sea-level futures

![Archive, locations, conditional distributions, local evidence](assets/ar6-workflow.svg)

This four-lesson studio studies **Abidjan, Lagos, Bangkok, Ho Chi Minh City, and Manila** using real IPCC AR6 modeled sea-level projections. It complements the earlier synthetic coastal scene with source-derived distributions, maps, and explicit geographic coverage checks.

## Start the studio

| Lesson | Learn | Open |
|---|---|---|
| 13 · Archive access | Axes, chunk budgets, units, CORS, provenance | [Read](notebooks/13_ar6_archive.ipynb) · [Run](https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=13_ar6_archive.ipynb) |
| 14 · Port-city proxies | Gauge matching, scenario bands, empirical distributions and SQL | [Read](notebooks/14_ar6_port_cities.ipynb) · [Run](https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=14_ar6_port_cities.ipynb) |
| 15 · Gridded maps | Common-scale maps, gauge/grid comparisons, 3D and time cubes | [Read](notebooks/15_ar6_grid_maps.ipynb) · [Run](https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=15_ar6_grid_maps.ipynb) |
| 16 · Uncertainty | Fixed-year exceedance, documented exports, port evidence clinic | [Read](notebooks/16_ar6_uncertainty.ipynb) · [Run](https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=16_ar6_uncertainty.ipynb) |

Suggested teaching sequence: complete lessons 01–02, then run the studio in two 90-minute sessions. Assign one city per group. Require each group to identify its projection location and explain one limitation before comparing numbers. The book contains executed outputs; students can inspect figures without starting Python.

## Where is the evidence?

Distances below are great-circle distances from rounded teaching reference points. The source's available projection locations determine the match. They are not evidence of local gauge data completeness, port footprint, or hydraulic connectivity.

| City | Nearest available gauge projection | Gauge distance | Nearest defined grid location (lat, lon) | Grid distance |
|---|---|---:|---|---:|
| Abidjan | Takoradi, ID 331 | 256.1 km | 5°, −4° | 35.7 km |
| Lagos | Takoradi, ID 331 | 594.9 km | 6°, 3° | 66.0 km |
| Bangkok | Fort Phrachula Chomklao, ID 444 | 24.9 km | 14°, 100° | 60.2 km |
| Ho Chi Minh City | Vung Tau, ID 1495 | 64.3 km | 11°, 107° | 40.9 km |
| Manila | Manila, ID 145 | 2.5 km | 15°, 121° | 44.5 km |

The African cities share one distant gauge proxy. Their gauge curves therefore coincide. The regional grids provide a separate spatial comparison; neither product resolves the ports. “Nearest defined grid” means complete samples at all nine years inside the 5 × 5 window, not necessarily an ocean-only cell.

## Explore the actual gridded medians

All five lab datasets use **SSP5-8.5 / wf_1e**, decades 2020–2100, and the median of all 20,000 samples at each location/year. The one-degree windows are deliberately small. They have no added ocean mask, spatial interpolation, DEM, or flood model.

| City | 2D map | 3D map | Time cube |
|---|---|---|---|
| Abidjan | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ar6_abidjan&mode=map) | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ar6_abidjan&mode=columns) | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ar6_abidjan&mode=cube) |
| Lagos | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ar6_lagos&mode=map) | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ar6_lagos&mode=columns) | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ar6_lagos&mode=cube) |
| Bangkok | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ar6_bangkok&mode=map) | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ar6_bangkok&mode=columns) | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ar6_bangkok&mode=cube) |
| Ho Chi Minh City | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ar6_ho_chi_minh&mode=map) | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ar6_ho_chi_minh&mode=columns) | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ar6_ho_chi_minh&mode=cube) |
| Manila | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ar6_manila&mode=map) | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ar6_manila&mode=columns) | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ar6_manila&mode=cube) |

Try `t = 8 AND value > 0.8` to select 2100 locations with median relative sea-level change above 0.8 m. The query operates on medians already loaded from the derived Zarr window. The 3D height is a visual scaling, not water depth. Per-city colour scales differ; lesson 15 supplies common-scale maps for comparison.

## Source and preparation

- **Dataset:** Garner et al. (2021), *IPCC AR6 Sea Level Projections*, version **20210809**, accessed **2026-10-13**, [DOI 10.5281/zenodo.5914709](https://doi.org/10.5281/zenodo.5914709).
- **Guide/catalog/license:** [Rutgers-ESSP repository, pinned commit 8ee7512](https://github.com/Rutgers-ESSP/IPCC-AR6-Sea-Level-Projections/tree/8ee75128d8f6d9a8ba9825f47c92d11955d0651e).
- **Gauge subset:** four unique locations, both SSP1-2.6 and SSP5-8.5, workflow `wf_1e`, all 20,000 samples, nine decades.
- **Grid subset:** five 5 × 5 windows at one-degree spacing, SSP5-8.5 / `wf_1e`; 122 of 125 selected locations contain complete samples. Nine per-year p17/p50/p83 summaries; full samples also retained at each city's nearest defined grid location.
- **Units:** source millimetres → display metres relative to the **1995–2014 baseline**. The source totals include background land motion.
- **Transformations:** location selection, independent per-year NumPy linear quantiles, unit conversion and latitude reversal for north-up map stores. No temporal interpolation or sample reduction.
- **Transfer:** the one-time preparation read 48 value chunks and small source metadata/coordinates, about **1.34 GB**, then cached the verified objects. Students use about **4.5 MB** of statistical artifacts plus small map stores and browser runtimes. Normal builds make no archive requests.
- **Audit:** [Exact provenance](https://jltobias.github.io/JupyterLite-zarr-sql-views/data/ar6-provenance.json) records source URLs, dates, checksums, object generations where supplied, source metadata and city choices. `scripts/prepare_ar6.py` rebuilds from cache; `--download` permits bounded retrieval of missing public objects.

## Interpretation limits to retain in every presentation

These are projections, not tide-gauge observations. One workflow's percentiles are not the IPCC assessed p-box. Scenarios are conditional pathways without probabilities assigned here. The [source FAQ](https://github.com/Rutgers-ESSP/IPCC-AR6-Sea-Level-Projections/blob/main/FAQ.md) says emulator workflows such as `wf_1e` should not be used for rates because time correlations are not captured. Accordingly the lessons do not calculate individual trajectories, rates or first-crossing dates.

A fixed-year sample fraction above a sea-level-change threshold is not a flood probability. Port vulnerability requires exposure, local elevation and datums, storm/river/wave levels, defenses, drainage, land-motion evidence and social context. Adding an independent subsidence estimate to these totals without separating the existing background component could double-count land motion. The lessons identify these missing inputs without claiming to quantify them.

For assessed IPCC results, use the authors' confidence products or the [NASA IPCC AR6 Sea Level Projection Tool](https://sealevel.nasa.gov/ipcc-ar6-sea-level-projection-tool). Follow the [full required citations and acknowledgement](credits.md) when reusing these extracts or figures.
