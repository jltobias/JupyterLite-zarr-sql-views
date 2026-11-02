# SeasFire and LexCube: seasons in three dimensions

Explore historical fire, weather and vegetation in two small African windows using **SeasFire Cube v0.4**. Five executable notebooks connect Zarr metadata, maps, SQL, animation, seasonal analysis and the actual **LexCube 2.0.1** Jupyter widget.

![Discover, check, explore and ask a bounded question](assets/seasfire-workflow.svg)

## Start a lesson

| Lesson | Main question | Minutes |
|---|---|---:|
| [26 · Discover the cube](notebooks/26_seasfire_discovery.ipynb) | What do the variables, masks and intervals mean? | 35 |
| [27 · Maps, SQL and animation](notebooks/27_seasfire_maps_sql.ipynb) | How do totals and area-normalized values differ? | 45 |
| [28 · Seasons and lags](notebooks/28_seasfire_seasons_lags.ipynb) | Does an association persist after removing seasonality? | 50 |
| [29 · LexCube slicing](notebooks/29_seasfire_lexcube.ipynb) | Which exact cell-periods are visible? | 45 |
| [30 · Linked LexCube comparison](notebooks/30_seasfire_lexcube_compare.ipynb) | How can two different variables share a selection? | 50 |

Each chapter has a **Run in JupyterLite** link. Run from the top. Initial LexCube setup downloads WebAssembly-compatible dependencies and can take a minute. Use a modern WebGL2 browser. The Book contains static maps and charts; live LexCube controls require the running JupyterLite kernel. There is no data-service login or Python server for these exercises.

## What is bundled?

Two contiguous **16 × 16 native 0.25° windows**, one covering northern Ghana and neighboring savannas and one covering central Zambia and neighboring savannas. These are cross-border selections, not administrative summaries or representative regional samples. Both retain all **966 period starts, 2001–2021**, for five time-varying variables: `gwis_ba`, `tp`, `t2m_mean`, `vpd` and `ndvi`. We also retain `gwis_ba_valid_mask`, `area`, `lsm`, and the original coordinates.

The public SQL lab receives **2018–2021**, 184 periods × 16 × 16 = **47,104 cells per cube**. Its origin label is **HISTORICAL · SEASFIRE / GWIS**. The longer multivariate NPZ files support the notebook analyses.

- [West African fire map](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=seasfire_ghana&mode=map) · [time cube](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=seasfire_ghana&mode=cube)
- [Southern African fire map](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=seasfire_zambia&mode=map) · [time cube](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=seasfire_zambia&mode=cube)
- [Provenance, exact windows, source-object hashes and extract checksums](https://jltobias.github.io/JupyterLite-zarr-sql-views/data/seasfire-provenance.json)
- [Original consolidated Zarr metadata](https://jltobias.github.io/JupyterLite-zarr-sql-views/data/seasfire-zmetadata.json)

## Interpret the support

GWIS burned area is measured in **hectares per cell per period**, allocated using fire ignition dates. It is not a video of active fire fronts. Its temporal mask marks **2001 unavailable**; missing values are not replaced by zero. The mask describes source time coverage, not local detection quality.

Every year has 46 bins; the last has five or six days. The actual final timestamp is **2021-12-27**, and the last interval closes on 2022-01-01. Durations are derived from the array rather than copied from the catalog's display dates. Sums over successive bins can count repeatedly burned land; they are not automatically unique burned footprints.

Precipitation is a depth in mm per interval, temperature is in kelvin, VPD is in hPa, and NDVI is dimensionless. MODIS NDVI originally has 16-day support; harmonization does not create independent eight-day observations. The source `area` is in m² for the whole cell. A normalized burned-area ratio uses this whole-cell denominator, not land-only area. Source variable attributes are preserved in full.

SeasFire combines observations, reanalysis and derived quantities. These lessons are descriptive. They do not provide operational fire forecasts, causal estimates, smoke exposure, crop loss, food-security outcomes or climate attribution. Time dependence, seasonal confounding, interpolation and data availability matter in any predictive follow-up.

## Reproduce the extracts and browser integration

Normal builds use checked-in artifacts and do not contact ESA's data store. Run `python scripts/prepare_seasfire.py` to verify NPZ hashes and rebuild the two scalar Zarr stores offline. For a source refresh, install `requirements-seasfire.txt` in a native Python environment, then run `python scripts/prepare_seasfire.py --fetch`.

The source chunks are much larger than the requested windows: one dynamic chunk decodes to about 239 MiB. The refresh script limits each compressed object to 256 MiB and the total requested source bytes to 1.5 GiB. It caches verified objects, uses conditional requests, and records SHA256 hashes and ETags. This intentionally avoids the approximately 44 GB Zenodo ZIP. Neither the version label nor an ETag alone guarantees immutable cloud contents; saved object hashes identify the retrieved bytes.

LexCube uses the unmodified upstream wheel and frontend. `notebooks/lexcube_lite.py` selects Pyodide-compatible dependencies and applies a small, explicitly documented patch to disable the native `psutil` memory diagnostic inside WebAssembly. It does not substitute a renderer or change the data algorithm. The wheel, complete matching source archive, license and adaptation instructions are distributed with the course; see [LexCube source and build notes](https://jltobias.github.io/JupyterLite-zarr-sql-views/vendor/lexcube/README.md). No standalone native server, Dask cluster or arbitrary remote-store support is claimed for this adaptation.

## Citations and attribution

**Data:** Alonso, L., Gans, F., Karasante, I., Ahuja, A., Prapas, I., Kondylatos, S., Papoutsis, I., Panagiotou, E., Michail, D., Cremer, F., Weber, U., & Carvalhais, N. (2024). *SeasFire Cube: A Global Dataset for Seasonal Fire Modeling in the Earth System* (v0.4). Zenodo. [doi:10.5281/zenodo.13834057](https://doi.org/10.5281/zenodo.13834057). **CC BY 4.0**. Modified here by spatial subsetting, mask application, metadata annotation and browser packaging; no spatial resampling.

**Dataset paper:** Karasante, I., Alonso, L., Prapas, I., Ahuja, A., Carvalhais, N., & Papoutsis, I. (2025). *SeasFire cube — a multivariate dataset for global wildfire modeling*. Scientific Data **12**, 368. [doi:10.1038/s41597-025-04546-3](https://doi.org/10.1038/s41597-025-04546-3).

**Visualization:** Söchting, M., Scheuermann, G., Montero, D., & Mahecha, M. D. (2025). *Interactive Earth system data cube visualization in Jupyter notebooks*. Big Earth Data, 1–15. [doi:10.1080/20964471.2025.2471646](https://doi.org/10.1080/20964471.2025.2471646). [LexCube](https://github.com/msoechting/lexcube), Maximilian Söchting and contributors, **GPL-3.0-or-later**.

Credit the SeasFire consortium and ESA support, ESA EarthCODE and CloudFerro for the mirror, the European Commission Joint Research Centre's [GWIS](https://gwis.jrc.ec.europa.eu/), ECMWF/Copernicus [ERA5](https://doi.org/10.24381/cds.adbb2d47), and NASA [MOD13C1 v6](https://doi.org/10.5067/MODIS/MOD13C1.006). The source paper documents the harmonization and derived variables. Credit LexCube's RSC4Earth/Leipzig contributors and its ESA DeepESDL and DFG NFDI4Earth support. Original lesson code, prose and workflow artwork retain ISC; redistributed data and LexCube retain their separate licenses. No affiliation or endorsement is implied.
