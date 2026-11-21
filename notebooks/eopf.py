"""Project: Earth in the Browser; file: eopf.py; author: course contributors.
Email/organization: not supplied. Created/updated: 2026-11-21.
Purpose: shared, annotated EOPF lesson helpers. Inputs: data/eopf/* (real Sentinel-2).
Outputs: in-memory arrays, URLs and configuration objects. Python 3.12+, NumPy.
Notes: no automatic remote imagery requests; one 120 m overview snapshot.
Change log: 2026-11-21 initial helpers for lessons 31-36.
"""
import base64
import json
from pathlib import Path
from urllib.parse import urlencode
import numpy as np

DATA = Path(__file__).parent / 'data/eopf'
API = 'https://api.explorer.eopf.copernicus.eu'
SITE = 'https://jltobias.github.io/JupyterLite-zarr-sql-views'


def load_eopf() -> dict:
    """Return the recorded scene, metadata, physical reflectances and mask."""
    with np.load(DATA/'extract.npz') as archive:
        d = {key: archive[key] for key in archive.files}
    for name in ['item', 'collection', 'source-metadata', 'provenance']:
        d[name] = json.loads((DATA/f'{name}.json').read_text(encoding='utf-8'))
    return d


def normalized_difference(a: np.ndarray, b: np.ndarray, valid=None) -> np.ndarray:
    """Ratio with explicit finite, positive-reflectance and denominator rules.

    Negative physical reflectances are possible; this teaching index excludes
    them, retains missingness, and never clips invalid ratios into [-1, 1].
    """
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    keep = np.isfinite(a) & np.isfinite(b) & (a >= 0) & (b >= 0) & (a+b > 1e-8)
    if valid is not None: keep &= valid
    return np.divide(a-b, a+b, out=np.full_like(a, np.nan), where=keep)


def rgb(d: dict, bands=('b04', 'b03', 'b02'), maximum=0.4) -> np.ndarray:
    """Display stretch only; original reflectances remain unchanged."""
    return np.clip(np.stack([d[b] for b in bands], axis=-1)/maximum, 0, 1)**(1/1.5)


def search_url(bbox, dates=('2026-08-01','2026-11-20'), limit=5) -> str:
    """Build a bounded STAC GET request; west,south,east,north are degrees."""
    west,south,east,north = map(float,bbox)
    if not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
        raise ValueError('Invalid EPSG:4326 bbox order')
    if not 1 <= limit <= 20: raise ValueError('Use a page limit of 1-20')
    return API+'/stac/search?'+urlencode({'collections':'sentinel-2-l2a',
        'bbox':','.join(map(str,bbox)), 'datetime':dates[0]+'T00:00:00Z/'+dates[1]+'T23:59:59Z','limit':limit})


async def live_json(url: str) -> dict:
    """Optional public JSON retrieval, with explicit HTTP errors in both runtimes."""
    import sys
    if sys.platform == 'emscripten':
        from pyodide.http import pyfetch
        r = await pyfetch(url)
        if not r.ok: raise RuntimeError(f'HTTP {r.status}: {url}')
        return await r.json()
    import urllib.request
    with urllib.request.urlopen(url,timeout=30) as r: return json.load(r)


def tilejson_url(item: dict) -> str:
    """Current TiTiler STAC asset syntax, verified against /raster/api."""
    endpoint = f"{API}/raster/collections/{item['collection']}/items/{item['id']}/WebMercatorQuad/tilejson.json"
    return endpoint+'?'+urlencode({'assets':'reflectance|bands=b04,b03,b02',
        'rescale':'0,0.4','color_formula':'gamma rgb 1.5','tile_format':'png','tilesize':256})


def map_layers(url: str, bands=('b04','b03','b02')) -> list:
    """EOxElements declarative configuration; source values are reflectances."""
    color = ['color', *[['interpolate',['linear'],['band',i],0,0,0.4,255] for i in [1,2,3]],1]
    return [{'type':'WebGLTile','properties':{'id':'sentinel','title':'Sentinel-2 / 120 m overview'},
        'source':{'type':'GeoZarr','url':url,'bands':list(bands)},'style':{'gamma':1.5,'color':color}}]


def studio_sample() -> dict:
    """A reviewed prefill recipe; creating it does not authenticate or run a job."""
    return {'name':'EOPF teaching: southern Italy NDVI', 'collectionId':'sentinel-2-l2a',
        'temporalRange':['2026-09-22','2026-09-29'],
        'bands':['reflectance|bands=b04','reflectance|bands=b08'],
        'boundingBox':[13.9,41.0,14.2,41.2], 'cloudCover':20,
        'code':'''# Physical reflectances: do not apply DN scaling a second time.
def ndvi(data):
    red, nir = data[0], data[1]
    total = nir + red
    value = if_(total > 0, (nir - red) / total, None)
    return array_create([value, value, value])

index = reduced.apply_dimension(dimension="bands", process=ndvi)
grey = index.linear_scale_range(input_min=-1, input_max=1, output_min=0, output_max=255)
add_graph_to_map(grey.save_result("PNG"), "NDVI: first-valid composite")
'''}


def studio_link(sample: dict) -> str:
    encoded = base64.urlsafe_b64encode(json.dumps(sample).encode()).decode().rstrip('=')
    link = 'https://studio.explorer.eopf.copernicus.eu/editor?sample='+encoded
    if len(link) > 6000: raise ValueError('Use Studio sampleUrl for a large recipe')
    return link


async def install_widget() -> None:
    """Install the pinned pure-Python widget inside Pyodide; native uses requirements."""
    import sys
    if sys.platform == 'emscripten':
        import piplite, micropip
        # Match the anywidget frontend installed by requirements.txt at build time.
        await piplite.install(['ipywidgets','anywidget==0.9.21'])
        wheel=Path(__file__).parent/'wheels/ipyeoxelements-1.1.0-py3-none-any.whl'
        await micropip.install('emfs:'+str(wheel.resolve()),deps=False)


def qualify_widget_urls(widget):
    """Resolve GeoZarr paths against the notebook page, preserving Pages prefixes.

    Zarrita requires absolute store URLs. This small adapter adjusts the generated
    instance's layer assignments; the distributed ipyeoxelements wheel is unchanged.
    Only the simple GeoZarr layer dictionaries used in this lesson are supported.
    """
    # Some null optional traits arrive as undefined in the widget model. The
    # generated frontend must skip both values before calling component setters.
    esm = widget._esm.replace('!== null', '!= null')
    for expression in ["layers", "view.model.get('layers')"]:
        old = f"el['layers'] = {expression};"
        if old not in esm: raise RuntimeError('Upstream widget layer assignment changed')
        esm = esm.replace(old, f"el['layers'] = ({expression}).map(layer => ({{...layer, source: {{...layer.source, url: new URL(layer.source.url, document.baseURI).href}}}}));")
    widget._esm = esm
    return widget
