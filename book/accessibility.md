# Access, troubleshooting, and reproducibility

All lab controls have text labels, visible keyboard focus, and keyboard-operable inputs. A status message reports load and query failures. The visible-cell table provides numeric access to map values; GeoJSON exports contain the complete selection. Static notebook maps include units and titles, and each lesson provides prose interpretation. This project has not undergone a formal accessibility conformance audit.

## If a map is blank

Check the status message. The lab requires WebGL2 and WebAssembly. Try an updated browser with hardware acceleration or use the Python map and values table. SQL queries that match no cells deliberately draw an empty selection. Press **Reset view** if you have moved the camera away. In 2D, the time slider may point to a slice with no selected cells while other times still match.

## If Python is slow or does not start

The first launch downloads Pyodide and scientific packages. Wait for the kernel to become idle, then run the first import cell. School network filtering of CDNs can prevent startup. Reload once after checking network access. For repeat failures, download the repository and use native Python with `requirements.txt`. Python examples use the local `course.py` helper and `data/` folder; run from the `notebooks/` directory.

## Save and recover work

JupyterLite stores edits in browser storage. Download notebooks and exports before switching devices, using private browsing, or clearing site data. A later deployment may not replace your previously edited local notebook; use a fresh browser profile or rename your copy to compare with the new bundled version.

## External services and video

Optional STAC requests can fail because of CORS, network policy, or provider availability. The STAC lesson explicitly distinguishes recorded provenance from a live response. No failure is silently replaced by synthetic observations. YouTube playback and captions depend on the provider; a direct creator link and official text tutorial are provided. GeoLibre and the C3S Atlas open as separate websites and have their own accessibility, privacy, account, and license policies.

## Reproduce the complete site

```bash
npm ci
python -m pip install -r requirements.txt
python scripts/validate_data.py
python scripts/execute_notebooks.py
npm test
npm run build
python scripts/build_site.py
python -m http.server 8000 --directory _site
```

Open `http://localhost:8000/`. `npm run dev` previews the landing page and browser lab only; the assembled `_site` contains the book and JupyterLite. GitHub Actions runs the checks, builds the site, and deploys to Pages on the main branch. Pull requests build and test without deploying.
