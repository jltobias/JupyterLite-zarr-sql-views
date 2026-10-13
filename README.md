# Earth in the Browser

![Earth in the Browser — a changing Earth, a new perspective](public/assets/splash.svg)

**A JupyterLite + Jupyter Book teaching atlas for Zarr, SQL, and Earth observation in the browser.** Sixteen executable Python lessons connect small data cubes to 2D maps, 3D extruded maps, orbitable space–time cubes, coastal scenes, and linked time series. The new **AR6 port-city studio** studies Abidjan, Lagos, Bangkok, Ho Chi Minh City, and Manila.

Inspired by and adapted from **[dzole0311/zarr-sql-views](https://github.com/dzole0311/zarr-sql-views)**. This independent teaching adaptation preserves upstream attribution and its ISC license.

[![Build and publish](https://github.com/jltobias/JupyterLite-zarr-sql-views/actions/workflows/pages.yml/badge.svg)](https://github.com/jltobias/JupyterLite-zarr-sql-views/actions/workflows/pages.yml)

## Open the teaching site

- **[Splash page and course home](https://jltobias.github.io/JupyterLite-zarr-sql-views/)**
- **[Interactive Earth lab](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/)**
- **[JupyterLite notebooks](https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html)**
- **[Jupyter Book](https://jltobias.github.io/JupyterLite-zarr-sql-views/book/intro.html)**
- [Instructor guide](https://jltobias.github.io/JupyterLite-zarr-sql-views/book/teaching.html) · [Data provenance](https://jltobias.github.io/JupyterLite-zarr-sql-views/book/data.html) · [Credits](https://jltobias.github.io/JupyterLite-zarr-sql-views/book/credits.html) · [Troubleshooting](https://jltobias.github.io/JupyterLite-zarr-sql-views/book/accessibility.html)

These URLs are served by the repository’s GitHub Pages deployment. The Actions badge above reports the build/deployment state. No data-service account or notebook server is required for the bundled lessons. Initial runtime downloads require internet access; some optional external services have separate accounts and terms.

## Explore the lab demos

### New: AR6 port-city studio

![From sea-level archive chunks to a defensible port-city question](public/assets/ar6-workflow.svg)

**[Open the studio guide](https://jltobias.github.io/JupyterLite-zarr-sql-views/book/sea-level.html).** Real IPCC AR6 v20210809 projections from the [Rutgers-ESSP source archive](https://github.com/Rutgers-ESSP/IPCC-AR6-Sea-Level-Projections), with all **20,000 samples** retained at selected locations. Gauge lessons compare SSP1-2.6 and SSP5-8.5; five one-degree grid windows show SSP5-8.5 medians through 2100. All use workflow `wf_1e` and a 1995–2014 baseline. Statistical files total about **4.5 MB**; students never download the full archives.

| City | 2D map | 3D map | Time cube |
|---|---|---|---|
| Abidjan | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ar6_abidjan&mode=map) | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ar6_abidjan&mode=columns) | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ar6_abidjan&mode=cube) |
| Lagos | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ar6_lagos&mode=map) | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ar6_lagos&mode=columns) | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ar6_lagos&mode=cube) |
| Bangkok | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ar6_bangkok&mode=map) | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ar6_bangkok&mode=columns) | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ar6_bangkok&mode=cube) |
| Ho Chi Minh City | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ar6_ho_chi_minh&mode=map) | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ar6_ho_chi_minh&mode=columns) | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ar6_ho_chi_minh&mode=cube) |
| Manila | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ar6_manila&mode=map) | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ar6_manila&mode=columns) | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ar6_manila&mode=cube) |

The nearest available gauge projection for both **Abidjan and Lagos is Takoradi**, about **256 km and 595 km** away respectively. The lessons make that proxy limitation explicit and compare nearby gridded locations. These are modeled regional sea-level changes, not port flood extents or observations. `wf_1e` cannot support rates or first-crossing dates; a single workflow's quantiles are not the assessed IPCC p-box. [Exact provenance and source checksums](public/data/ar6-provenance.json) · [Required citations and credits](https://jltobias.github.io/JupyterLite-zarr-sql-views/book/credits.html#ipcc-ar6-sea-level-projections).

### Earth observation and method laboratories

| Experiment | Open a view | Data origin |
|---|---|---|
| Lake Ngami surface water, Botswana | [2D map](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ngami&mode=map) · [3D map](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ngami&mode=columns) · [time cube](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ngami&mode=cube) | **Observed** DE Africa WOfS extract, 2018/2020/2022 |
| African heat seasonality | [Space–time cube](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=heat&mode=cube) | **Synthetic**, not ERA5 or thermal-stress observations |
| Coastal height and sea-level reasoning | [3D scene](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=coast&mode=scene) | **Synthetic** terrain; not an inundation forecast |
| Air quality and exposure reasoning | [3D extruded map](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=air&mode=columns) | **Synthetic**, not CAMS or station data |
| Water-quality optical proxies | [Animated map](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=water&mode=map) | **Synthetic** reflectance; not drinking-water safety |
| Rainfall, food and water insecurity | [Time cube](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=rain&mode=cube) | **Synthetic**, not crop yield or food-security estimates |

Try `value > 0.5 AND t = 0` in the Lake Ngami lab. Switch perspective, move through time, click a cell for its history, and export your selection to GeoJSON. Export includes selected cells across **all** times; the map’s slider chooses one displayed slice. Open the result in [GeoLibre Web](https://web.geolibre.app/).

![Discover with STAC, read Zarr, query with SQL, inspect linked views](public/assets/pipeline.svg)

## Run the lessons

Each notebook includes learning objectives, short Python cells, explanatory Markdown, an infographic, generated visualizations, a linked interactive lab where relevant, exercises, interpretation guidance, and source credits. The C3S lesson includes an official creator-hosted tutorial video and a text alternative. The rendered book includes executed outputs for reading without a running kernel.

| Lesson | JupyterLite | Jupyter Book |
|---|---|---|
| 01 · A browser is a scientific workspace | [Run](https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=01_start_here.ipynb) | [Read](https://jltobias.github.io/JupyterLite-zarr-sql-views/book/notebooks/01_start_here.html) |
| 02 · From Zarr chunks to SQL rows | [Run](https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=02_zarr_sql.ipynb) | [Read](https://jltobias.github.io/JupyterLite-zarr-sql-views/book/notebooks/02_zarr_sql.html) |
| 03 · Lake Ngami: water observations and missing evidence | [Run](https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=03_deafrica_water.ipynb) | [Read](https://jltobias.github.io/JupyterLite-zarr-sql-views/book/notebooks/03_deafrica_water.html) |
| 04 · 2D maps, 3D maps, and a space–time cube | [Run](https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=04_maps_and_cubes.ipynb) | [Read](https://jltobias.github.io/JupyterLite-zarr-sql-views/book/notebooks/04_maps_and_cubes.html) |
| 05 · C3S Atlas: scenarios, warming levels, and model spread | [Run](https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=05_c3s_atlas.ipynb) | [Read](https://jltobias.github.io/JupyterLite-zarr-sql-views/book/notebooks/05_c3s_atlas.html) |
| 06 · Global heat questions, African heat laboratory | [Run](https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=06_heat_stress.ipynb) | [Read](https://jltobias.github.io/JupyterLite-zarr-sql-views/book/notebooks/06_heat_stress.html) |
| 07 · Sea-level rise and the meaning of a 3D scene | [Run](https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=07_coastal_scenes.ipynb) | [Read](https://jltobias.github.io/JupyterLite-zarr-sql-views/book/notebooks/07_coastal_scenes.html) |
| 08 · Air quality: a map is not an exposure estimate | [Run](https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=08_air_quality.ipynb) | [Read](https://jltobias.github.io/JupyterLite-zarr-sql-views/book/notebooks/08_air_quality.html) |
| 09 · Water quality: from optical signal to a testable hypothesis | [Run](https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=09_water_quality.ipynb) | [Read](https://jltobias.github.io/JupyterLite-zarr-sql-views/book/notebooks/09_water_quality.html) |
| 10 · Food and water insecurity | [Run](https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=10_food_water.ipynb) | [Read](https://jltobias.github.io/JupyterLite-zarr-sql-views/book/notebooks/10_food_water.html) |
| 11 · STAC discovery and GeoLibre handoff | [Run](https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=11_stac_geolibre.ipynb) | [Read](https://jltobias.github.io/JupyterLite-zarr-sql-views/book/notebooks/11_stac_geolibre.html) |
| 12 · Capstone: an evidence-led climate story | [Run](https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=12_capstone.ipynb) | [Read](https://jltobias.github.io/JupyterLite-zarr-sql-views/book/notebooks/12_capstone.html) |
| 13 · Open the AR6 archive without downloading the world | [Run](https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=13_ar6_archive.ipynb) | [Read](https://jltobias.github.io/JupyterLite-zarr-sql-views/book/notebooks/13_ar6_archive.html) |
| 14 · Five port cities, four tide-gauge proxies | [Run](https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=14_ar6_port_cities.ipynb) | [Read](https://jltobias.github.io/JupyterLite-zarr-sql-views/book/notebooks/14_ar6_port_cities.html) |
| 15 · Regional grids, 3D maps, and sea-level time cubes | [Run](https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=15_ar6_grid_maps.ipynb) | [Read](https://jltobias.github.io/JupyterLite-zarr-sql-views/book/notebooks/15_ar6_grid_maps.html) |
| 16 · Threshold questions without false flood probabilities | [Run](https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=16_ar6_uncertainty.ipynb) | [Read](https://jltobias.github.io/JupyterLite-zarr-sql-views/book/notebooks/16_ar6_uncertainty.html) |

Save your work by downloading notebooks and exports. JupyterLite browser storage is local to your device and browser profile.

## Copernicus, Digital Earth Africa, and browser GIS

“C32 Atlas” is interpreted as the **[Copernicus C3S Atlas](https://atlas.climate.copernicus.eu/)**. Lesson 05 analyses the actual CMIP6 warming-level auxiliary table from the [official C3S Atlas user-tools repository](https://github.com/ecmwf-projects/c3s-atlas), then guides regional comparison in the Atlas. Full CDS grids are not bundled; their download may require credentials and accepted product terms. The synthetic heat cube is never labeled as Copernicus data.

The **[DE Africa WOfS extract](public/data/deafrica-provenance.json)** includes exact STAC item IDs, source COG URLs, CRS, transformations, quality mask, and retrieval date. It is a nearest-neighbour sample on a coarse grid, not an area-averaged flood product. Three selected years cannot establish a climate trend or attribute change.

Additional tools: [DE Africa Explorer](https://explorer.digitalearth.africa/) · [DE Africa STAC](https://explorer.digitalearth.africa/stac) · [STAC Browser](https://radiantearth.github.io/stac-browser/) · [GeoLibre](https://web.geolibre.app/) · [Copernicus Browser](https://browser.dataspace.copernicus.eu/) · [EO Browser](https://apps.sentinel-hub.com/eo-browser/) · [NASA Worldview](https://worldview.earthdata.nasa.gov/).

Climate-burden discussions use [IPCC AR6 WGII Chapter 9: Africa](https://www.ipcc.ch/report/ar6/wg2/chapter/chapter-9/) as scientific context. Exercises separate environmental hazards, exposure, vulnerability, and social outcomes. Synthetic laboratory outputs are learning tools, not operational assessments.

## Build and test locally

Requirements: Node.js 22.13+ (Node 24 used in CI), Python 3.12 or 3.13, and a modern WebGL2 browser for the 3D lab.

```bash
python -m venv .venv
# Activate your environment: .venv\Scripts\Activate.ps1 (PowerShell)
# or source .venv/bin/activate (macOS/Linux)
python -m pip install -r requirements.txt
npm ci
python scripts/validate_data.py
python scripts/validate_ar6.py
python scripts/execute_notebooks.py
npm test
npm run build
python scripts/build_site.py
python -m http.server 8000 --directory _site
```

Open `http://localhost:8000/`. To test the served site in a second terminal:

```bash
npx playwright install chromium
npm run test:browser
```

`npm run dev` previews the landing page and lab only. `scripts/build_site.py` assembles the book and JupyterLite alongside the Vite build. GitHub Actions builds and tests pull requests and publishes `main` through Pages. Repository Settings → Pages must use **GitHub Actions** as its source.

To regenerate authored notebooks, run `python scripts/make_notebooks.py`, then execute them again. To refresh real raster sources, install `requirements-data.txt` and run `python scripts/prepare_data.py --refresh-deafrica`; raw COGs are cached in ignored `.work/`. Without that flag, the checked-in extract reproduces the six teaching stores. The core build does not request fresh environmental data.

AR6 preparation is separate: install `requirements-data.txt`, then run `python scripts/prepare_ar6.py --download` once. It retrieves about 1.34 GB of explicitly selected public source objects, enforces a 2 GiB transfer budget per run, and caches verified objects in `.work/ar6-cache/`. Run without `--download` to rebuild from that cache. It preserves all selected samples, writes quantile summaries and five small Zarr stores, and records exact provenance. The regular build uses checked-in derivatives and requires neither Numcodecs nor archive access. Do not run bulk bucket-copy commands for these lessons.

## Architecture and limits

- **Lab:** Zarrita reads real Zarr chunks; Arrow transfers decoded cells; DuckDB-WASM applies numeric SQL predicates; deck.gl renders linked views. SQL operates on the loaded window, not automatic remote predicate pushdown.
- **Notebooks:** NumPy, Matplotlib, and SQLite run in Pyodide. A documented narrow reader handles the course’s uncompressed Zarr v2 stores in ZIP containers. The notebooks do not require native DuckDB, rasterio, GDAL, or Open Data Cube in the browser.
- **Scope:** eleven bounded cubes (one observed, five synthetic, five projected), maximum 100,000 cells per lab dataset, explicit missing-value handling, fixed dataset colour scales, and transparent origins. Generic remote Zarr/COG adapters and the full upstream forecast application are outside this teaching implementation.
- **Network:** first launch downloads the browser runtimes. Optional live metadata, external video, fonts, and GIS applications require network access. No API secrets or tokens are committed.

## Credits, citations, and licenses

**Upstream:** dzole0311 and zarr-sql-views contributors, *Zarr SQL Views*, commit [`9c1bb2c`](https://github.com/dzole0311/zarr-sql-views/tree/9c1bb2cb0320ae2f194f3f0fd1c36841f4b52dff), ISC. The original colour module is retained; the DuckDB/Arrow setup is adapted. [Original license](licenses/zarr-sql-views-ISC.txt).

**Digital Earth Africa:** *Water Observations from Space annual summary*, based on Landsat, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Contains modified data: spatial subset, nearest-neighbour reprojection/sampling, observation-quality mask, Zarr conversion. [Product documentation](https://docs.digitalearthafrica.org/en/latest/data_specs/Landsat_WOfS_specs.html) · [Exact provenance](public/data/deafrica-provenance.json).

**C3S Atlas:** European Union, *C3S Atlas user tools*, commit [`8d80d4e`](https://github.com/ecmwf-projects/c3s-atlas/tree/8d80d4e98053d96077ba67f29464b4f373ff4037). Unmodified auxiliary CSV under [Apache 2.0](licenses/c3s-atlas-Apache-2.0.txt). Related dataset: [DOI 10.24381/cds.h35hb680](https://doi.org/10.24381/cds.h35hb680); overview: [Gutiérrez et al., 2024](https://doi.org/10.21957/ah52ufc369); FAIR principles: [Iturbide et al., 2022](https://doi.org/10.1038/s41597-022-01739-y).

**Natural Earth:** generalized boundaries, [public domain](https://www.naturalearthdata.com/about/terms-of-use/). **Synthetic data:** original analytic examples, [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/). **Original code, prose, and SVG artwork:** [ISC](LICENSE). **Embedded video:** Copernicus ECMWF, creator-hosted, all rights retained.

**IPCC AR6 sea-level projections:** modified subsets under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), source guide pinned to [`8ee7512`](https://github.com/Rutgers-ESSP/IPCC-AR6-Sea-Level-Projections/tree/8ee75128d8f6d9a8ba9825f47c92d11955d0651e). Required citations: **Fox-Kemper et al. (2021), WG1 Chapter 9**, [DOI 10.1017/9781009157896.011](https://doi.org/10.1017/9781009157896.011); **Kopp et al. (2023), FACTS v1.0**, [DOI 10.5194/gmd-16-7461-2023](https://doi.org/10.5194/gmd-16-7461-2023); **Garner et al. (2021), IPCC AR6 Sea Level Projections, version 20210809**, accessed 2026-10-13, [DOI 10.5281/zenodo.5914709](https://doi.org/10.5281/zenodo.5914709). [Full required citations and original license text](licenses/ipcc-ar6-sea-level-CC-BY-4.0.md).

We thank the projection authors for developing and making the sea-level rise projections available, multiple funding agencies for supporting the development of the projections, and the NASA Sea Level Change Team for developing and hosting the IPCC AR6 Sea Level Projection Tool.

Thanks to JupyterLite, Jupyter Book, Pyodide, NumPy, Matplotlib, DuckDB-WASM, Apache Arrow, Zarrita, deck.gl, GeoLibre, STAC, and their contributors. [Complete third-party notices](THIRD_PARTY_NOTICES.md) · [Bundled JavaScript license texts](licenses/npm-notices.txt) · [Citation metadata](CITATION.cff). Cite this course **and** its upstream software and actual data sources. No institutional endorsement is implied.

## Repository review

[Review findings and resolutions, 13 October 2026](docs/review-2026-10-13.md) ? [Machine-readable findings](docs/review-2026-10-13.json). The AR6 update also fixes failed-load metadata mixing, negative synthetic rainfall, omitted negative terrain, preparation provenance, and verification gaps.
