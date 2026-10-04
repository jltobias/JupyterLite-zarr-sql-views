# Credits, citations, and reuse

This independent teaching project builds on the work of the following communities. No affiliation with or endorsement by any data provider or software project is implied.

## Upstream software

**dzole0311 and zarr-sql-views contributors (2026). Zarr SQL Views.** [Repository](https://github.com/dzole0311/zarr-sql-views), pinned commit `9c1bb2cb0320ae2f194f3f0fd1c36841f4b52dff`. ISC license, retained in `licenses/zarr-sql-views-ISC.txt`. Reuse includes the colour module, an adapted DuckDB/Arrow setup pattern, and the pedagogical geographic time-cube/linked-SQL approach. Changes add the course site, bounded teaching data, simplified query controls, Python lessons, book, exports, and deployment tooling. See `THIRD_PARTY_NOTICES.md` for a file-level description.

**C3S Atlas user tools (European Union, 2023 and contributors).** [Repository](https://github.com/ecmwf-projects/c3s-atlas), pinned commit `8d80d4e98053d96077ba67f29464b4f373ff4037`. The auxiliary CMIP6 warming-level CSV is redistributed unmodified under the source Apache 2.0 license, retained in `licenses/c3s-atlas-Apache-2.0.txt`. The source project’s figures and logos are not copied.

## Data sources

**Digital Earth Africa. Water Observations from Space annual summary.** [Specifications](https://docs.digitalearthafrica.org/en/latest/data_specs/Landsat_WOfS_specs.html) · [STAC collection](https://explorer.digitalearth.africa/stac/collections/wofs_ls_summary_annual) · [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Based on Landsat observations. Contains modified data: subset, nearest-neighbour geographic sampling, clear-observation mask, Zarr conversion. Exact item IDs and asset URLs are in the distributed provenance file.

**Copernicus Climate Change Service. Gridded dataset underpinning the Copernicus Interactive Climate Atlas.** [DOI 10.24381/cds.h35hb680](https://doi.org/10.24381/cds.h35hb680). Linked for guided exploration and future regional subsets; full CDS grids are not redistributed here. Check the selected CDS product’s current terms and acknowledgement instructions before reuse.

**Natural Earth. Country boundaries.** [About and public-domain terms](https://www.naturalearthdata.com/about/terms-of-use/). The generalized country GeoJSON is copied from upstream. Boundaries also inform the original conceptual splash illustration. They are not authoritative statements about borders.

**Synthetic data.** Original analytic teaching equations in `scripts/prepare_data.py`, dedicated under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/). The location names provide orientation; the fields are not observations at those locations.

## Scientific context

**IPCC (2022). Climate Change 2022: Impacts, Adaptation and Vulnerability, Chapter 9: Africa.** [Official chapter and citation information](https://www.ipcc.ch/report/ar6/wg2/chapter/chapter-9/). Use the chapter’s own evidence and confidence assessments when extending the course to climate-burden claims.

**IPCC (2021). Climate Change 2021: The Physical Science Basis, Chapter 9.** [Ocean, Cryosphere and Sea Level Change](https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-9/).

**Gutiérrez et al. (2024). The Copernicus Interactive Climate Atlas: a tool to explore regional climate change.** [ECMWF Newsletter 181, DOI 10.21957/ah52ufc369](https://doi.org/10.21957/ah52ufc369).

**Iturbide et al. (2022). Implementation of FAIR principles in the IPCC: the WGI AR6 Atlas repository.** [Scientific Data, DOI 10.1038/s41597-022-01739-y](https://doi.org/10.1038/s41597-022-01739-y).

## Software and media ecosystem

JupyterLite and Jupyter Book (BSD-3-Clause), Pyodide (MPL-2.0), NumPy (BSD-3-Clause), Matplotlib (Matplotlib license), DuckDB-WASM (MIT), Apache Arrow (Apache-2.0), Zarrita (MIT), deck.gl (MIT), Vite (MIT), and their contributors make the course possible. The locked JavaScript dependency inventory and bundled license texts are in `licenses/npm-notices.txt`. Python build dependencies retain their own licenses in the installed distributions.

[GeoLibre](https://github.com/opengeos/GeoLibre) (MIT) and [STAC Browser](https://github.com/radiantearth/stac-browser) (Apache-2.0) are linked external tools, not vendored applications. [STAC](https://stacspec.org/) is the discovery standard used in the metadata lesson.

Original SVG splash artwork, workflow infographic, lesson text, and notebook figures were created for this repository. Underlying data retain the licenses above. The Google Fonts services supply DM Sans and Space Grotesk (SIL Open Font License); system fonts provide a fallback. The embedded **Climate Atlas – Tutorial video** is by [Copernicus ECMWF](https://www.youtube.com/watch?v=o62IPhpvsAI), hosted by YouTube with all rights retained by its creator. It is linked/embedded, not downloaded or re-licensed.

Use the repository’s `CITATION.cff` to cite this teaching adaptation, and also cite upstream software and the specific datasets used in any derivative notebook or figure.
