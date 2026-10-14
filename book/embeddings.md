# GeoTessera embedding studio

![A year becomes a vector: observe, represent, explore, validate](assets/tessera-workflow.svg)

Five lessons use **real TESSERA v1.1 / dclimate annual embeddings** near Lagos and Abidjan. They connect vector mathematics to geographic maps, three-dimensional feature space, Zarr/SQL selection and a coastal evidence study. All calculations run in JupyterLite with NumPy and Matplotlib; the rendered chapters contain executed figures for reading without a kernel.

| Lesson | Explore | Run Python | Read with outputs |
|---|---|---|---|
| 17 · Embedding foundations | Quantization, dimensions, coverage and provenance | [JupyterLite](https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=17_tessera_embeddings.ipynb) | [Chapter](notebooks/17_tessera_embeddings.ipynb) |
| 18 · Similarity search | Cosine similarity, threshold sensitivity, SQL and GeoJSON | [JupyterLite](https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=18_tessera_similarity.ipynb) | [Chapter](notebooks/18_tessera_similarity.ipynb) |
| 19 · PCA and 3D | Shared-basis false-color maps, reconstruction loss, 3D scatter and animation | [JupyterLite](https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=19_tessera_pca.ipynb) | [Chapter](notebooks/19_tessera_pca.ipynb) |
| 20 · Clusters and transfer | Spherical k-means, stability, Lagos-to-Abidjan transfer and validation design | [JupyterLite](https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=20_tessera_clusters.ipynb) | [Chapter](notebooks/20_tessera_clusters.ipynb) |
| 21 · Annual differences | Aligned vectors, optical/radar support and coastal research questions | [JupyterLite](https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=21_tessera_change.ipynb) | [Chapter](notebooks/21_tessera_change.ipynb) |

## Open the linked maps

| Teaching window | 2D similarity | 3D score columns | Annual time cube |
|---|---|---|---|
| Lagos / Apapa vicinity | [Map](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=tessera_lagos&mode=map) | [Columns](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=tessera_lagos&mode=columns) | [Time cube](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=tessera_lagos&mode=cube) |
| Abidjan / Treichville vicinity | [Map](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=tessera_abidjan&mode=map) | [Columns](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=tessera_abidjan&mode=columns) | [Time cube](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=tessera_abidjan&mode=cube) |

Each city uses its **own fixed 2025 reference pixel**, query row 32 / column 32. Similarity values between cities therefore refer to different reference vectors. Compare both using the same reference explicitly if that is your research question. Lab colors span each dataset's observed range; the notebook maps use the common theoretical −1 to 1 range. Vertical columns show similarity scores, never terrain. Time-cube spacing represents a year index, with unequal calendar intervals.

## What is bundled

The six NPZ files total **3.33 MB**. Each holds a 64 × 64 sample grid, 128 original int8 components, float32 per-pixel scales, optical and ascending/descending radar counts, and query plus native coordinates. There are 4,096 query locations per city, sampled in 2018, 2021 and 2025. The windows cover 0.024° × 0.024° around these manually selected centers:

| Window | Longitude | Latitude | Source grid |
|---|---:|---:|---|
| Lagos / Apapa vicinity | 3.363 | 6.439 | EPSG:32631 |
| Abidjan / Treichville vicinity | −4.005 | 5.295 | EPSG:32630 |

These are convenience windows, not official port boundaries or citywide samples. Query points are spaced 0.000375°, approximately 42 m. Each selects the containing **10 m native UTM pixel**, without averaging, interpolation, or a nearest-valid replacement. The geographic map paints those point-sampled values on the query grid. Exact native centers are retained; their offsets from query centers are at most half a source-pixel diagonal, about 7.1 m. Missing vectors remain missing, and missing is not a water classification.

The pinned Icechunk snapshot is `B6AFRJGX5XQC0A716PA0`. The checkpoint is `tessera_v1_1_aws_encoder.pt`. The [machine-readable provenance](https://jltobias.github.io/JupyterLite-zarr-sql-views/data/tessera-provenance.json) records the store URI, model attributes, extraction windows, timestamps and SHA-256 checksums. [Preparation code](https://github.com/jltobias/JupyterLite-zarr-sql-views/blob/main/scripts/prepare_tessera.py) uses the pinned GeoTessera adapter. It slices before reading array values; it does not download the global archive. Native cloud reads can transfer more than the extracted output because they operate on chunks.

## How to teach the sequence

Allow 35–45 minutes per lesson, or split it into two sessions: foundations/similarity/PCA, then clusters/change/evidence. Start with a prediction, run the calculation, change one parameter, and write an evidence journal. The first three lessons work without machine-learning prerequisites; the cluster lesson introduces the extra assumptions explicitly.

For an assessment, ask students for one geographic map, one sensitivity result, the exact source snapshot and a plan for independent validation. Award credit for identifying an unsupported claim. No independent land-cover labels are supplied, so the notebooks report no classification accuracy. Clustering stability is not an accuracy score.

PCA axes are feature-space coordinates, not physical coordinates. RGB colors are stretched component scores. A shared basis and stretch keep comparisons interpretable; the display still loses information. The animation cycles through three annual summaries and has static map alternatives. It does not show event timing.

## Connect to climate and coastal questions

Embedding retrieval can identify locations for follow-up interpretation or help design sampling strata. It does not measure sea level, heat stress, water contamination, food insecurity or social vulnerability. Pair candidate patterns with dated independent imagery, reference labels and relevant physical measurements. Observation counts help examine coverage differences; they do not establish model confidence or causes of change.

Use the [AR6 port-city studio](sea-level.md) for conditional regional sea-level projections, [Digital Earth Africa lesson](notebooks/03_deafrica_water.ipynb) for a distinct observed water product at Lake Ngami, and [C3S Atlas lesson](notebooks/05_c3s_atlas.ipynb) for climate context. These differ in location, time and spatial support. None is automatic ground truth for these embedding windows. The [STAC and GeoLibre lesson](notebooks/11_stac_geolibre.ipynb) explains discovery and browser GIS handoffs.

## Source and license

Credit **TESSERA / University of Cambridge and collaborators**, **dClimate** for this global inference run and hosting, and the **GeoTessera** contributors for data access. The root metadata identifies Sentinel-2 inputs from `s3://sentinel-cogs` and OPERA Sentinel-1 RTC from the Alaska Satellite Facility archive. Credit the Copernicus Sentinel missions, the input-processing and hosting teams, and the open Zarr/Icechunk ecosystem. We redistribute derived embeddings and counts, not raw satellite images or model weights.

Feng, Z., Atzberger, C., Jaffer, S., Knezevic, J., Sormunen, S., Young, R., Lisaius, M. C., Immitzer, M., Jackson, T., Ball, J., Coomes, D. A., Madhavapeddy, A., Blake, A., and Keshav, S. (2025; revised 2026). *TESSERA: Temporal Embeddings of Surface Spectra for Earth Representation and Analysis*. [doi:10.48550/arXiv.2506.20380](https://doi.org/10.48550/arXiv.2506.20380).

The [TESSERA terms](https://github.com/ucam-eo/tessera/blob/master/aup.md) explicitly release data under CC0 and describe ethical guidelines as advisory. A retained copy includes upstream's inconsistent legacy CC-BY wording; we identify the data using its explicit CC0 declaration, also stated on the project website. GeoTessera code is MIT. This repository's original lessons, helper code and infographic are ISC. See [all credits](credits.md), the [MIT notice](https://jltobias.github.io/JupyterLite-zarr-sql-views/licenses/geotessera-MIT.txt), [CC0 text](https://jltobias.github.io/JupyterLite-zarr-sql-views/licenses/tessera-CC0-1.0.txt) and [retained terms](https://jltobias.github.io/JupyterLite-zarr-sql-views/licenses/tessera-terms.md). No institutional endorsement is implied.
