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

## IPCC AR6 sea-level projections

The port-city studio uses modified extracts of AR6 version **20210809**, accessed **2026-10-13**. [Preparation and exact provenance](sea-level.md) document location selection, mm-to-m conversion, per-year quantiles and storage conversion. The source guide is pinned to commit `8ee75128d8f6d9a8ba9825f47c92d11955d0651e`. Full source licensing, required citations and acknowledgement follow, reproduced from the authors' LICENSE.md.

### Source license

The IPCC AR6 Sea-Level Rise Projections are licensed by the authors under a [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/). The data producers and data providers make no warranty, either express or implied, including, but not limited to, warranties of merchantability and fitness for a particular purpose. All liabilities arising from the supply of the information (including any liability arising in negligence) are excluded to the fullest extent permitted by law.

### Required acknowledgements and citations

In order to document the impact of these sea-level rise projections, users of the projections are obligated to cite chapter 9 of Working Group 1 contribution to the the IPCC Sixth Assessment Report, the Framework for Assessment of Changes To Sea-level (FACTS) model description paper, and the version of the data set used:

> Fox-Kemper, B., H.T. Hewitt, C. Xiao, G. Aðalgeirsdóttir, S.S. Drijfhout, T.L. Edwards, N.R. Golledge, M. Hemer, R.E. Kopp, G. Krinner, A. Mix, D. Notz, S. Nowicki, I.S. Nurhati, L. Ruiz, J.-B. Sallée, A.B.A. Slangen, and Y. Yu, 2021: Ocean, Cryosphere and Sea Level Change. In Climate Change 2021: The Physical Science Basis. Contribution of Working Group I to the Sixth Assessment Report of the Intergovernmental Panel on Climate Change \[Masson-Delmotte, V., P. Zhai, A. Pirani, S.L. Connors, C. Péan, S. Berger, N. Caud, Y. Chen, L. Goldfarb, M.I. Gomis, M. Huang, K. Leitzell, E. Lonnoy, J.B.R. Matthews, T.K. Maycock, T. Waterfield, O. Yelekçi, R. Yu, and B. Zhou (eds.)\]. Cambridge University Press, Cambridge, United Kingdom and New York, NY, USA, pp. 1211–1362, [doi:10.1017/9781009157896.011](https://doi.org/10.1017/9781009157896.011).

> Kopp, R. E., Garner, G. G., Hermans, T. H. J., Jha, S., Kumar, P., Reedy, A., Slangen, A. B. A., Turilli, M., Edwards, T. L., Gregory, J. M., Koubbe, G., Levermann, A., Merzky, A., Nowicki, S., Palmer, M. D., & Smith, C. (2023). The Framework for Assessing Changes To Sea-Level (FACTS) v1.0: A platform for characterizing parametric and structural uncertainty in future global, relative, and extreme sea-level change. Geoscientific Model Development, 16, 7461–7489. https://doi.org/10.5194/gmd-16-7461-2023

> Garner, G. G., T. Hermans, R. E. Kopp, A. B. A. Slangen, T. L. Edwards, A. Levermann, S. Nowikci, M. D. Palmer, C. Smith, B. Fox-Kemper, H. T. Hewitt, C. Xiao, G. Aðalgeirsdóttir, S. S. Drijfhout, T. L. Edwards, N. R. Golledge, M. Hemer, G. Krinner, A. Mix, D. Notz, S. Nowicki, I. S. Nurhati, L. Ruiz, J-B. Sallée, Y. Yu, L. Hua, T. Palmer, B. Pearson, 2021. IPCC AR6 Sea Level Projections. Version 20210809. Dataset accessed 2026-10-13 at https://doi.org/10.5281/zenodo.5914709.

Please also include in the acknowledgements of works citing these projections:

> We thank the projection authors for developing and making the sea-level rise projections available, multiple funding agencies for supporting the development of the projections, and the NASA Sea Level Change Team for developing and hosting the IPCC AR6 Sea Level Projection Tool.

## GeoTessera annual embeddings

The [embedding studio](embeddings.md) gives the full dataset specification and citation to Feng et al. (2025; revised 2026), [TESSERA](https://doi.org/10.48550/arXiv.2506.20380). Credit TESSERA / University of Cambridge and collaborators, dClimate for global inference and hosting, and GeoTessera contributors for access software. Source inputs are Copernicus Sentinel-2 and OPERA Sentinel-1 RTC through the source archives recorded in the provenance. The six data extracts and two similarity cubes use CC0-1.0; GeoTessera preparation software is MIT; original lessons, helper code and infographic are ISC. Exact source snapshot, dates, native coordinates, transformations and hashes are retained in [provenance](https://jltobias.github.io/JupyterLite-zarr-sql-views/data/tessera-provenance.json). See the studio guide for full notices and the retained upstream terms. These are learned representations, not verified land-cover labels or physical hazard measurements.
