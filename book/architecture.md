# How the browser workflow works

![STAC to Zarr to SQL to linked views](assets/pipeline.svg)

**Discover → read a bounded array → query local cells → inspect linked views.** These are distinct operations.

The browser lab loads small Zarr v2 stores using Zarrita, converts decoded cells to an Arrow table, and inserts the table into DuckDB-WASM. deck.gl renders a geographic grid, extruded values, an orbitable time cube, or a value surface. The time slider changes a map slice; a numeric SQL predicate selects cells across all times; clicking a cell changes the linked series to that location. Export retains every selected cell across times, even when a 2D view shows only one slice.

SQL filters the already loaded table. It does not automatically push a predicate into Zarr storage. Production remote-data work requires an earlier spatial and temporal window selection, chunk-aware fetching, coordinate handling, and memory budgeting. This course caps lab inputs at 100,000 cells, uses a 128 MB DuckDB memory setting, and bundles cubes below that limit.

The Python notebooks read the same stores inside ZIP containers so their files survive JupyterLite’s content transfer. A deliberately narrow reader handles only the course’s uncompressed float32 Zarr v2 layout; it validates the layout before reading. NumPy provides array operations. SQLite implements portable teaching SQL. **DuckDB-WASM is used in the JavaScript lab, not imported into Python.** The helper does not claim support for arbitrary remote Zarr stores, codecs, or Icechunk repositories.

## Relationship to the source project

Upstream `src/render/colors.ts` is preserved in `src/upstream-colors.ts`. Its palette interpolation drives the lab’s legends and cells. The DuckDB worker setup, bounded Arrow ingestion, and external-access setting in `src/engine.js` adapt upstream `src/analysis/runtime.ts`. The original ISC license is retained verbatim.

The teaching adaptation uses a smaller explicit data schema and a simpler query workflow. It does not vendor the full upstream viewer, forecast catalogs, custom volume shaders, or Mosaic state-management system. Refer to [upstream at the pinned commit](https://github.com/dzole0311/zarr-sql-views/tree/9c1bb2cb0320ae2f194f3f0fd1c36841f4b52dff) to study those implementations.

## Browser and network boundaries

GitHub Pages serves static files. Python runs through Pyodide; SQL runs in a Web Worker. No notebook server, application database, API secret, Mapbox token, or cloud-compute account is required. Initial downloads include about 36 MB of uncompressed DuckDB-WASM and the separate JupyterLite/Pyodide runtime. Compression and browser caching affect actual transfer size.

The lab data and boundaries are same-origin. JupyterLite runtime packages and fonts may come from CDNs on first use. Optional external STAC requests obey browser CORS. A service can allow metadata while blocking raster assets; neither catalog discoverability nor a desktop success guarantees browser access. The site is not advertised as fully offline.

## Adding a dataset

Create a reviewed small extract using the pattern in `scripts/prepare_data.py`. Preserve source URLs, identifiers, dates, native CRS, units, nodata, transformation method, quality masks, license, and scientific limitations. Use a `(time, latitude, longitude)` array with explicit monotonic coordinates and one time slice per chunk. Record whether each output is observed, modeled, or synthetic. Rebuild the catalog and notebook ZIP, run the data checks, and add a lesson that interprets the quantity correctly.
