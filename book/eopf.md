# EOPF Sentinel Zarr studio

![Trace a catalog item through quality-aware analysis and browser or server processing](assets/eopf-workflow.svg)

**[Open the interactive two-map studio](https://jltobias.github.io/JupyterLite-zarr-sql-views/eopf/)** · **[Open the eodash explorer](https://jltobias.github.io/JupyterLite-zarr-sql-views/eopf-dashboard.html)**

Six lessons connect the [EOPF Sentinel Zarr Explorer](https://explorer.eopf.copernicus.eu/) to practical Python and browser GIS. Work through discovery, physical reflectance, quality masks, SQL, real OpenLayers and EOxElements maps, a Python-controlled widget, and inspectable server-processing recipes.

## Start with a bounded observation

The recorded scene is **Sentinel-2C L2A, 2026-09-28, tile T33TVF**, southern Italy. The classroom extract contains **128 × 128 cells** from the upstream **120 m averaged overview**, with blue, green, red and NIR reflectances. It covers a 15.36 km square in **UTM zone 33N (EPSG:32633)**. It is one convenience window, not a representative regional sample. The preparation downloaded 7.23 MB of source objects, including a 20 m Scene Classification mask; the full archive is not downloaded in JupyterLite.

The array packing was decoded once: DN/10000 − 0.1, with zero DN missing. The notebook arrays and classroom GeoZarr already contain physical reflectance. Each overview cell also carries the fraction of its aligned 36 SCL children in classes 4, 5 or 6. The strict exercise accepts all 36; it does not claim local ground-truth validation. A ratio of overview means differs from a mean of native-pixel ratios.

The [provenance record](https://jltobias.github.io/JupyterLite-zarr-sql-views/data/eopf/provenance.json) contains item and object URLs, checksums, coordinates, window indices, transformations and attribution. Normal builds use these checked-in data. A native source refresh is `python scripts/prepare_eopf.py --fetch` after installing `requirements-eopf.txt`; it enforces a 32 MiB transfer budget.

## Teaching sequence

| Lesson | Activity | Evidence produced |
|---|---|---|
| [31: Catalog and GeoZarr](notebooks/31_eopf_discovery.ipynb) | Inspect STAC assets, resolution levels and codecs; construct African city searches | Product and storage audit |
| [32: Reflectance, masks and SQL](notebooks/32_eopf_reflectance_sql.ipynb) | Map RGB, NDVI and green–NIR NDWI; compare mask thresholds; query pixels | Figures, retained counts and SQL/NumPy agreement |
| [33: OpenLayers](notebooks/33_eopf_openlayers.ipynb) | Change actual GeoZarr bands in the two-map studio | Source/style configuration and network observations |
| [34: EOxElements Jupyter](notebooks/34_eopf_eox_widgets.ipynb) | Operate EOxMap with Python dropdown and linked layer control | Actual widget plus static reference plot |
| [35: TiTiler](notebooks/35_eopf_titiler.ipynb) | Construct a request and diagnose the recorded service response | Reproducible HTTP 400, optional live retry |
| [36: Studio and eodash](notebooks/36_eopf_studio_eodash.ipynb) | Export an openEO Studio prefill recipe and dashboard configuration | Reviewed local JSON exports and external handoffs |

Allow approximately 35, 50, 40, 45, 40 and 50 minutes respectively. Each notebook includes prediction prompts, annotated Python, exercises and reasoning checks.

## The eight requested resources

| Official resource | How this course uses it |
|---|---|
| [Explorer](https://explorer.eopf.copernicus.eu/) | Entry point, ecosystem and processing provenance |
| [STAC Browser](https://api.explorer.eopf.copernicus.eu/browser/) | Item/asset discovery and coverage audit |
| [OpenLayers](https://explorer.eopf.copernicus.eu/software-services/ol/) | Actual direct GeoZarr renderer with RGB, false color and NDVI |
| [EOxElements](https://explorer.eopf.copernicus.eu/software-services/eoxelements/) | Actual map and layer-control components; official globe/storytelling extensions |
| [EOxElements-Jupyter](https://explorer.eopf.copernicus.eu/software-services/EOxElements-Jupyter/) | Pinned `ipyeoxelements` widget in lesson 34 |
| [Studio](https://studio.explorer.eopf.copernicus.eu/) | Inspectable Python recipe and prefill link; authenticated execution remains optional |
| [eodash](https://explorer.eopf.copernicus.eu/software-services/eodash/) | Actual web component loaded on demand with a shared configuration |
| [TiTiler](https://explorer.eopf.copernicus.eu/software-services/titiler/) | Current request syntax and service-boundary troubleshooting |

## What works locally, and what depends on services

The six notebooks default to bundled data and metadata. The map studio's default GeoZarr is served from this site. JupyterLite's first start and the widget's CDN JavaScript need internet. The optional full-scene map and eodash query external EOPF services. A blank map must be diagnosed, not interpreted as absent observations.

On **2026-11-21**, TiTiler returned HTTP 400 for the pinned item because it treated an SCL array asset as a GeoZarr group. Lesson 35 records that response rather than claiming a successful tile render. Direct source arrays and both browser map implementations are separate paths. Studio recipe syntax and metadata can be checked locally; authenticated remote execution is not claimed.

The bounded Lagos and Cape Town searches returned zero items for 2026-08-01 through 2026-11-20 in `sentinel-2-l2a` when checked. Students can vary dates and collections, preserving actual empty responses. The southern Italy example is not presented as African imagery. Connect future African observations to the AR6, FTW or SeasFire studios only after auditing geographic coverage, temporal support and the claims each product can support.

## Attribution

**Contains modified Copernicus Sentinel data (2026)**, processed by EOPF Sentinel Zarr Explorer; spatial subset, packing decode, quality summary and classroom GeoZarr repackaging by this course. Use the [Copernicus Sentinel legal notice](https://sentinels.copernicus.eu/documents/247904/690755/Sentinel_Data_Legal_Notice); the catalog's `proprietary` identifier links those terms and is not a software license.

Credit **ESA / Copernicus**, **EOX**, **Development Seed** and the **EOPF Explorer contributors**. The Explorer is funded by ESA through the Copernicus Space Component programme. OpenLayers is BSD-2-Clause; EOxElements, EOxElements-Jupyter, anywidget, eodash and openEO Studio are MIT; TiTiler-EOPF is Apache-2.0. Original course lessons, adapter code and workflow artwork are ISC. Separate upstream notices are retained in `licenses/`; no endorsement is implied. See [full credits](credits.md).
