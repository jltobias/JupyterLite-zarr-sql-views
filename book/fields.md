# Global FTW field studio

![From Sentinel-2 composites to probabilities, polygons and independently validated questions](assets/ftw-workflow.svg)

Explore real **Global Fields of the World (FTW)** predictions in Senegal and Kenya. Four independent browser notebooks connect the global catalog to three-class probability maps, Zarr/SQL queries, 3D score views, field polygons, regional confidence and annual differences. Each includes runnable Python, explanatory figures, an exercise and interpretation guidance. Start with lesson 22; lessons 23–25 also run on their own.

| Lesson | Focus | Run | Read |
|---|---|---|---|
| 22 · Discover Global FTW | Product identity, catalog, three classes, provenance | [JupyterLite](https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=22_ftw_discovery.ipynb) | [Chapter](notebooks/22_ftw_discovery.ipynb) |
| 23 · Probability cubes and SQL | Threshold sensitivity, maps, 3D, point export | [JupyterLite](https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=23_ftw_probability_sql.ipynb) | [Chapter](notebooks/23_ftw_probability_sql.ipynb) |
| 24 · Fields and confidence | Polygon geometry, SQL attributes, filtering, GeoLibre | [JupyterLite](https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=24_ftw_fields_confidence.ipynb) | [Chapter](notebooks/24_ftw_fields_confidence.ipynb) |
| 25 · Annual differences | Paired comparison, animation, food–water evidence plan | [JupyterLite](https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=25_ftw_change_food_water.ipynb) | [Chapter](notebooks/25_ftw_change_food_water.ipynb) |

## What is bundled?

The **alpha** global prediction store contains annual PRUE model outputs for 2024 and 2025. These are distinct from the FTW training benchmark. Two convenience windows each retain **128 × 128 contiguous native pixels × 3 classes × 2 years**, with original float32 values, ascending longitude and descending latitude centers in EPSG:4326. They are not representative regional samples. Pixel spacing is 0.0000898311982°, nominally about 10 m; east–west ground distance varies with latitude.

| Teaching window | Chosen center (longitude, latitude) | Intersecting polygons, 2024 / 2025 |
|---|---|---|
| Senegal River valley | −16.22°, 16.30° | 20 / 24 |
| Western Kenya | 34.95°, −0.10° | 322 / 320 |

The combined probability NPZ files are **0.64 MB**; the full-geometry GeoJSON extracts are **2.32 MB**. Metadata adds about 0.20 MB. Lab Zarr ZIPs hold the field-interior class alone. All numbers above refer to this retrieval, not a permanent census of fields.

Every selected polygon intersects the raster's pixel-edge extent. Geometry is **not clipped or simplified**. Provider area and perimeter describe the full polygon; an edge-crossing flag makes that explicit. A count of selected polygons is neither a farm count nor a count of landowners. Unknown confidence values remain null.

## Open the interactive labs

| Window | 2D map | 3D columns | Time cube | Score scene |
|---|---|---|---|---|
| Senegal | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ftw_senegal&mode=map) | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ftw_senegal&mode=columns) | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ftw_senegal&mode=cube) | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ftw_senegal&mode=scene) |
| Kenya | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ftw_kenya&mode=map) | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ftw_kenya&mode=columns) | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ftw_kenya&mode=cube) | [Open](https://jltobias.github.io/JupyterLite-zarr-sql-views/lab/?dataset=ftw_kenya&mode=scene) |

Try `value > 0.5 AND t = 1`. The query selects 2025 field-interior probabilities. Vertical height in columns/scenes is a score, not terrain; the cube's vertical axis is time index. Each lab uses its own full-data min–max color range; notebook maps use common 0–1 scales. Point exports retain the model, citation, license and provenance. Lesson 24 instead exports polygon geometries for [GeoLibre Web](https://web.geolibre.app/).

## Probability, confidence and change

- The three ~10 m softmax classes are `non_field_background`, `field`, and `field_boundaries`. Their sum is approximately one at each valid pixel. They are not calibrated crop-yield or impact probabilities.
- Polygon confidence is a separate **500 m** layer sampled upstream at the representative point. The score is `min(100, raw / 0.578178 × 100)`. A cutoff such as 69 can change which landscapes survive; test alternatives and independent labels.
- Annual layers are independent predictions. A difference in probability or polygon count does not establish land conversion, flood damage, abandonment or a climate trend. IDs are not longitudinal parcel identifiers.
- Field outlines do not supply legal boundaries, tenure, crop types, irrigation status, yields or household food security. They can help define candidate study units when paired with suitable independent evidence.

## Reproduce the extracts

[Machine-readable provenance](https://jltobias.github.io/JupyterLite-zarr-sql-views/data/ftw-provenance.json) records exact windows, source URLs, ETags, timestamps, selected Parquet row groups, metadata and artifact SHA256 checksums. The [catalog commit](https://github.com/fieldsoftheworld/ftw-data-catalog/tree/fd844c4c646af0f8e653fba774f79cc17b2af124/catalog) pins documentation, **not** the mutable cloud data. ETags are object identifiers, not assumed cryptographic checksums.

Default preparation is offline and checks the bundled extracts before rebuilding lab stores:

```bash
python scripts/prepare_ftw.py
python scripts/validate_ftw.py
```

An optional native refresh uses `requirements-ftw.txt` in a separate environment, followed by `python scripts/prepare_ftw.py --fetch`. It reads bounded source Zarr windows and range-reads intersecting GeoParquet row groups, with a 128 MiB per-country Parquet transfer budget. The initial extraction read about **38.6 MB** of Senegal Parquet ranges and **48.5 MB** of Kenya ranges, plus probability chunks and coordinates. Source shards are larger than the classroom extracts. A refresh deliberately updates the extract/provenance pair and must be reviewed and validated. The ordinary build and browser exercises do not contact Source Cooperative.

The official catalog documents an anonymous S3 backing prefix. Preparation uses its HTTPS path-style endpoint because the logical `data.source.coop` endpoint did not serve the requested objects during preparation. Both addresses are retained. Country files are never downloaded in full. Browser lessons use NumPy, Matplotlib and SQLite; GDAL, Shapely, PyArrow and native Zarr are not installed in Pyodide.

## Attribution and citation

**Global Fields of the World (FTW)**: Taylor Geospatial and collaborators, including Microsoft AI for Good Research Lab, Arizona State University, Washington University in St. Louis, Oregon State University and Clark University. PRUE predictions use **Copernicus Sentinel-2** inputs. Data are hosted by **Source Cooperative**, a Radiant Earth initiative. [Dataset](https://source.coop/ftw/global-data) · [Project](https://fieldsofthe.world/) · [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

**Robinson, C., Muhawenayo, G., Khanal, S., Fang, Z., Corley, I., Tárano, A. M., Estes, L., Marcus, J., Jacobs, N., Kerner, H., Becker-Reshef, I., & Lavista Ferres, J. M. (2026). *The first global agricultural field boundary map at 10 m resolution*. arXiv:2605.11055. [doi:10.48550/arXiv.2605.11055](https://doi.org/10.48550/arXiv.2605.11055).**

This atlas modifies the distribution through spatial subsetting, GeoJSON conversion, metadata annotations and scalar Zarr repackaging. Original probability values, full selected polygon geometries and provider attributes are retained. Lessons and the workflow infographic are original ISC-licensed material. Reuse must preserve data attribution, license links and an indication of changes. No affiliation or endorsement is implied.
