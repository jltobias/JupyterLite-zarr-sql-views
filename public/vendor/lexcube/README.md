# LexCube 2.0.1: source, license and JupyterLite adaptation

Copyright (C) 2022 Maximilian Söchting and LexCube contributors.
LexCube is distributed under **GNU GPL version 3 or, at your option, any later version**,
without any warranty. Retain the upstream copyright notices and component licenses.

- Upstream: https://github.com/msoechting/lexcube
- Full GPL text: [lexcube-GPL-3.0.txt](https://jltobias.github.io/JupyterLite-zarr-sql-views/licenses/lexcube-GPL-3.0.txt)
- Complete corresponding source, including TypeScript, Python and build configuration:
  [lexcube-2.0.1.tar.gz](lexcube-2.0.1.tar.gz)
- Unmodified upstream wheel (also supplies the prebuilt frontend):
  [lexcube-2.0.1-py3-none-any.whl](https://jltobias.github.io/JupyterLite-zarr-sql-views/downloads/notebooks/wheels/lexcube-2.0.1-py3-none-any.whl)
- Course adaptation source:
  [lexcube_lite.py](https://jltobias.github.io/JupyterLite-zarr-sql-views/downloads/notebooks/lexcube_lite.py)
- Reproducible download / hash verification script:
  https://github.com/jltobias/JupyterLite-zarr-sql-views/blob/main/scripts/vendor_lexcube.py

SHA256:

```
9b4be927663d48139136260edfe4b7d6b3e78bf56fbc917881a47330f073ba5e  lexcube-2.0.1-py3-none-any.whl
6ffa67f254cbe5a99e40335a070ee248d9c0e6bb1994f5367c4392bc776d9f43  lexcube-2.0.1.tar.gz
```

## Modification, 2026-11-01

The wheel and frontend are redistributed unchanged. In a JupyterLite kernel only,
`setup_lexcube()` installs compatible Pyodide packages and the wheel with dependency
resolution disabled. Native package requirements such as `opencv-python-headless`
cannot be installed verbatim in WebAssembly; Pyodide supplies `opencv-python` instead.

Before importing LexCube, the helper changes two places in its installed
`lexcube/lexcube_server/src/tile_server.py`: it replaces `import psutil` with
`psutil = None`, and adds a guard to `get_current_memory_usage` that returns a clear
“diagnostics unavailable” message. It does not fabricate memory measurements.
The modified module remains **GPL-3.0-or-later**, with original notices preserved.
The exact patch instructions are executable in the linked helper; applying them to
the corresponding source reproduces the browser backend modification.

No rendering, tiling, compression, geographic-coordinate or numerical algorithms
are modified. Browser lessons use bounded in-memory float32 xarray arrays, the
upstream lossless widget tile protocol, and explicit float32 voxel mode. Native
Jupyter uses the unmodified installed LexCube package. We do not claim that native
server mode, process diagnostics, arbitrary remote stores or multiprocessing work
in Pyodide.

The independent course `cube_sliders` helper supplies ipywidgets controls linked
to the upstream widget's bounds. Their maximum stop index is the dimension size.
This avoids an endpoint mismatch in upstream 2.0.1's `Sliders` control, whose
maximum is size-1 although `get_current_cube_selection` uses a stop-exclusive
slice. The course controls therefore preserve the final native cell. The
upstream slider code is neither copied nor modified.

To rebuild upstream from source, unpack the source archive and follow its
`README.md` development instructions and `pyproject.toml` build configuration.
These include the JavaScript/TypeScript sources, package lock and Jupyter extension
build scripts. To reproduce this site's frontend, install `lexcube==2.0.1` and
`ipywidgets==8.1.9` using the root `requirements.txt`, then run the repository build.
The unchanged prebuilt extension and all its bundled third-party notices are copied
by JupyterLite. The corresponding source and these instructions are served alongside it.

Citation: Söchting, M., Scheuermann, G., Montero, D., & Mahecha, M. D. (2025).
*Interactive Earth system data cube visualization in Jupyter notebooks*.
Big Earth Data, 1–15. https://doi.org/10.1080/20964471.2025.2471646.
Credit Maximilian Söchting, RSC4Earth/Leipzig University and contributors;
acknowledge ESA DeepESDL and DFG NFDI4Earth support as described upstream.
