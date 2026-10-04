# Third-party notices

Original source: **dzole0311 / zarr-sql-views**, https://github.com/dzole0311/zarr-sql-views,
commit `9c1bb2cb0320ae2f194f3f0fd1c36841f4b52dff` (retrieved 2026-10-04).

Copyright (c) 2026 zarr-sql-views contributors. ISC license reproduced verbatim in
[licenses/zarr-sql-views-ISC.txt](licenses/zarr-sql-views-ISC.txt).

- `src/upstream-colors.ts`: upstream `src/render/colors.ts`, unmodified.
- `src/engine.js`: adapted worker initialization, bounded Arrow ingestion, and external SQL access restriction from `src/analysis/runtime.ts`; replaced Mosaic and forecast-specific logic with a small teaching table and explicit numeric predicates.
- Geographic time cubes and SQL-linked views are based on the upstream approach; the teaching app is an independent implementation, not the full upstream viewer.
- `public/data/countries.geojson`: copied from the upstream public directory; Natural Earth generalized boundaries, public domain. See https://www.naturalearthdata.com/about/terms-of-use/.

**C3S Atlas user tools**, https://github.com/ecmwf-projects/c3s-atlas,
commit `8d80d4e98053d96077ba67f29464b4f373ff4037` (retrieved 2026-10-04).
Copyright 2023, European Union. Licensed under Apache 2.0, retained in
[licenses/c3s-atlas-Apache-2.0.txt](licenses/c3s-atlas-Apache-2.0.txt).
`notebooks/data/CMIP6_WarmingLevels.csv` is copied unmodified from
`auxiliar/GWLs/CMIP6_WarmingLevels.csv`. No C3S logo or source figure is redistributed.
The distributed auxiliary table is distinct from full CDS gridded products and their terms.

**Digital Earth Africa WOfS annual summaries**, CC BY 4.0.
Contains modified Digital Earth Africa data based on Landsat observations.
Changes: Lake Ngami subset, nearest-neighbour EPSG:4326 sampling, count-clear quality mask,
conversion to uncompressed Zarr v2 and ZIP. Product and exact assets:
[provenance](public/data/deafrica-provenance.json). License:
https://creativecommons.org/licenses/by/4.0/. Source:
https://docs.digitalearthafrica.org/en/latest/data_specs/Landsat_WOfS_specs.html.
Attribution must follow these data into derivative maps and exports. No endorsement is implied.

**Synthetic cubes** (`heat`, `air`, `rain`, `coast`, `water`) are original analytic examples,
dedicated under CC0 1.0: https://creativecommons.org/publicdomain/zero/1.0/.
They are not Copernicus, DE Africa, or measured local environmental data.

**Bundled JavaScript dependencies:** versions are locked in `package-lock.json`; full
available license and NOTICE texts are collected in [licenses/npm-notices.txt](licenses/npm-notices.txt).
The generated site includes this license directory. Python/JupyterLite runtime components
retain upstream distribution notices; installed Python build packages carry their own licenses.

**Linked external applications:** GeoLibre (MIT), STAC Browser (Apache-2.0), C3S Atlas,
Copernicus Browser, EO Browser, and NASA Worldview. These are external links, not copied applications.

**Media and fonts:** original vector splash and infographic, ISC; Natural Earth geometry,
public domain. The Copernicus ECMWF Climate Atlas tutorial is embedded from its creator's
YouTube page (https://www.youtube.com/watch?v=o62IPhpvsAI); all rights remain with the creator.
DM Sans and Space Grotesk are delivered by Google Fonts under SIL OFL; neither font file
is checked into this repository. All external services have independent terms.
