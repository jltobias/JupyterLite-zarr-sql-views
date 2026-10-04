# Data catalog and provenance

One observed water cube, one official auxiliary climate table, five synthetic method cubes, and generalized boundaries are distributed. The origin is visible in the lab, each lesson, and exports.

| Resource | Origin | Coverage | License | Interpretation |
|---|---|---|---|---|
| Lake Ngami WOfS | Digital Earth Africa / Landsat | 2018, 2020, 2022; 48 × 48 sample | CC BY 4.0 | Fraction of clear observations classified as water |
| CMIP6 warming windows | C3S Atlas user-tools auxiliary table | Model-members, scenarios, global warming levels | Apache 2.0 in source repository | Supplied averaging windows, not local anomalies |
| Heat laboratory | Analytic equation | Africa-centred rectangle; 12 fictional months | CC0 1.0 | Air temperature teaching field, not thermal stress |
| Air laboratory | Analytic equation | Africa-centred rectangle; 12 fictional months | CC0 1.0 | Illustrative PM2.5, not CAMS or station observations |
| Food & water laboratory | Analytic equation | Africa-centred rectangle; 12 fictional months | CC0 1.0 | Illustrative rainfall, not an insecurity index |
| Coastal scene | Analytic terrain | Near Durban coordinates; one fictional surface | CC0 1.0 | Height-threshold exercise, not inundation |
| Optical water laboratory | Analytic plume | Lake Victoria-area coordinates; 12 fictional months | CC0 1.0 | Reflectance proxy, not water safety |
| Country outlines | Natural Earth, bundled by upstream | World, generalized | Public domain | Orientation only, not authoritative boundaries |

## Reproduce the observed extract

The checked-in [machine-readable provenance](https://jltobias.github.io/JupyterLite-zarr-sql-views/data/deafrica-provenance.json) records STAC item IDs, URLs, retrieval date, bounding box, and transformations. The preparation script obtains both `frequency` and `count_clear` for DE Africa tile x203/y050.

The native data are 30 m EPSG:6933 COGs. A 48 × 48 EPSG:4326 grid samples the bounding box `[22.60, -20.60, 22.88, -20.35]` with nearest-neighbour reprojection. Pixels with `count_clear < 5` become NaN. The output values are point samples, not averages over enlarged pixel footprints. Pixel counts do not estimate surface-water area or volume. Because the sampling grid is geographic, equal cell counts are not equal areas.

```bash
python -m pip install -r requirements-data.txt
python scripts/prepare_data.py --refresh-deafrica
```

Raw COGs are cached under ignored `.work/`. Without `--refresh-deafrica`, the script uses the checked-in extract to reproduce the teaching Zarr stores and ZIPs without contacting DE Africa. Refresh can change results if source products change; review provenance and differences before publishing.

**Attribution:** Contains modified Digital Earth Africa Water Observations from Space annual summary data, based on Landsat. Modifications: spatial subset, nearest-neighbour reprojection/sampling, clear-observation mask, and conversion to uncompressed Zarr v2. Source: [Digital Earth Africa WOfS](https://docs.digitalearthafrica.org/en/latest/data_specs/Landsat_WOfS_specs.html). License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). No endorsement is implied.

## C3S Atlas scope

The original request’s “Copernicus C32 Atlas” is interpreted as C3S Atlas. The bundled `CMIP6_WarmingLevels.csv` is copied unmodified from the [official user-tools repository](https://github.com/ecmwf-projects/c3s-atlas/blob/8d80d4e98053d96077ba67f29464b4f373ff4037/auxiliar/GWLs/CMIP6_WarmingLevels.csv), copyright 2023 European Union, under that repository’s Apache 2.0 license. It supports a real analysis of model-member averaging-window spread. Non-period codes remain explicit; the lesson does not invent missing years or infer that model frequencies are calibrated probabilities.

The [C3S Atlas gridded dataset](https://doi.org/10.24381/cds.h35hb680) and the [interactive Atlas](https://atlas.climate.copernicus.eu/) are guided external activities. Full gridded C3S products are not bundled here. Their product-specific terms and acknowledgement requirements must be checked when obtaining additional data. Do not attribute the synthetic heat cube to Copernicus.

## Climate-burden interpretation

Use [IPCC AR6 WGII Chapter 9](https://www.ipcc.ch/report/ar6/wg2/chapter/chapter-9/) for regional context and its evidence and confidence assessments. The course illustrates analytic methods; it does not derive operational heat alerts, flood-risk estimates, drinking-water assessments, or food-security classifications. The capstone explicitly separates physical observations, inference, exposure, vulnerability, and the evidence needed next.
