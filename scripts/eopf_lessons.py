"""Project: Earth in the Browser. File: eopf_lessons.py.
Purpose: author six EOPF notebooks. Author: course contributors; contact/agency: not supplied.
Created/updated: 2026-11-21; change log: initial lessons 31-36.
Inputs: pinned Copernicus Sentinel-2 extract and metadata. Output: notebooks + index.
Dependencies: make_notebooks.py / nbformat. Runtime lessons: NumPy, Matplotlib,
SQLite; lesson 34 additionally ipyeoxelements/anywidget/ipywidgets.
Notes: descriptive teaching, one convenience scene; no impacts or climate trend.
"""
SOURCES = [
 '[EOPF Sentinel Zarr Explorer](https://explorer.eopf.copernicus.eu/), funded by ESA through the Copernicus Space Component programme; EOX, Development Seed and project contributors.',
 '[Copernicus Sentinel data legal notice](https://sentinels.copernicus.eu/documents/247904/690755/Sentinel_Data_Legal_Notice): contains modified Copernicus Sentinel data (2026). EOPF processing; course subset and repackaging.',
 '[Recorded source objects, checksums and transformations](https://jltobias.github.io/JupyterLite-zarr-sql-views/data/eopf/provenance.json). One 128 × 128 window of the upstream 120 m averaged overview, acquired 2026-09-28.',
]
HEADER = '''**Reproducibility record.** Project: Earth in the Browser; author: course contributors;
email/organization: not supplied. Created/updated: 2026-11-21. Input: `data/eopf/`;
outputs: the figures and objects below (exports are named explicitly). Python, NumPy and
Matplotlib; SQLite where used. Initial EOPF teaching release. The acquisition is a
convenience example, not a representative sample. Missing values remain missing.

![EOPF workflow from discovery to direct maps, quality-aware analysis and server processing](assets/eopf-workflow.svg)
'''


def add_lessons(lesson, md, code):
    lesson('31_eopf_discovery','31 · EOPF: from STAC catalog to GeoZarr',35,
      'trace an item to its arrays; distinguish resolution levels, storage shards and browser services.',[
    md(HEADER+'''## 1. Find the product before loading its pixels

Open the [Explorer](https://explorer.eopf.copernicus.eu/) and its
[STAC Browser](https://api.explorer.eopf.copernicus.eu/browser/). A catalog describes
products; it does not contain every pixel. This recorded item covers southern Italy.
The official tutorial's older item was absent when checked; this course pins a current
2026-09-28 item and keeps its metadata so class does not depend on catalog retention.

**Predict:** will the GeoZarr asset point to a single array, a group, or a file?'''),
    code('''from eopf import load_eopf, search_url, live_json
d=load_eopf(); item=d['item']; p=d['provenance']
asset=item['assets']['reflectance']
print('Item:',item['id'])
print('Acquired:',p['date'],'| cloud cover (% of product):',item['properties']['eo:cloud_cover'])
print('Asset:',asset['href'])
print('Media type:',asset['type'],'| CRS:',asset['proj:code'])
print('Band names:',[b['name'] for b in asset['bands']])
print('License field:',d['collection']['license'])
print('Read the actual linked terms:',p['license_url'])'''),
    md('''## 2. Inspect groups, overview levels and codecs

The collection uses `proprietary` as its STAC license identifier and links the
Copernicus Sentinel legal notice. Do not relabel the data MIT or CC0 because a
viewer is open source. Preserve the linked terms and the modified-data attribution.

The source is **Zarr v3** with multiscales, projected coordinates and sharded arrays.
Our classroom store is a single-resolution, uncompressed GeoZarr v3 group. The older
SQL lab's Zarr v2 scalar schema is a different adapter; arbitrary source products
cannot be pasted into it unchanged.'''),
    code('''specs=d['source-metadata']['consolidated_metadata']['metadata']
layout=specs['measurements/reflectance']['attributes']['multiscales']['layout']
for level in layout: print(level['asset'],level['spatial:shape'])
spec=specs['measurements/reflectance/r120m/b04']
print('Logical dtype:',spec['data_type'],'| source shard:',spec['chunk_grid'])
print('Inner codecs:',spec['codecs'][0]['configuration']['codecs'])
print('Source bytes retrieved:',p['source_bytes'],'| classroom pixels:',np.prod(p['shape']))'''),
    md('''## 3. Search African cities without inventing coverage

The bounded Lagos and Cape Town searches returned zero items for the selected dates
on 2026-11-21. Catalog extent is not a guarantee of coverage. Try Abidjan, Lagos or
another collection/date interval and report the returned count before analysis.
The next cell defaults to URL construction; change `LIVE` to send one request.
A page limit is not the total matching count; follow `rel=next` deliberately if needed.'''),
    code('''cities={'Lagos':[3.3,6.4,3.5,6.6],'Abidjan':[-4.1,5.2,-3.9,5.4],
        'Cape Town':[18.3,-34.1,18.6,-33.8]}
url=search_url(cities['Lagos'])
print(url)
LIVE=False
if LIVE:
    try:
        response=await live_json(url)
        print('Returned this page:',len(response['features']))
        print('Next links:',[x['href'] for x in response.get('links',[]) if x['rel']=='next'])
    except Exception as exc:
        print('LIVE REQUEST FAILED:',exc,'No fresh observations were obtained.')
else:
    print('RECORDED MODE: no live query was sent.')''')],SOURCES,
    'Inspect Sentinel-1 or Sentinel-3 metadata in STAC Browser. Explain which measurement, units and quality rules would change.',
    'Radar backscatter, optical reflectance and radiance need different processing. Shared Zarr storage does not make their physical meaning interchangeable.')

    lesson('32_eopf_reflectance_sql','32 · Sentinel reflectance, quality masks and SQL',50,
      'calculate NDVI and a water-related spectral index; audit missingness; query pixels with explicit units.',[
    md(HEADER+'''## 1. Read physical reflectance once

The source codec represents reflectance as packed integers with scale and offset.
The preparation script decodes `DN / 10000 - 0.1`, with zero DN missing. The bundled
arrays already contain **physical reflectance**: do not scale them again.
Four source bands are retained: blue B02, green B03, red B04 and NIR B08.
The overview averages source reflectance to 120 m; a ratio of means is not the mean
of all native-pixel ratios. A 120 m cell can mix vegetation, buildings and water.'''),
    code('''from eopf import load_eopf, rgb, normalized_difference
d=load_eopf(); b=d['provenance']['bounds']; extent=[b[0],b[2],b[1],b[3]]
fig,axes=plt.subplots(1,2,figsize=(11,5),layout='constrained')
for ax,bands,title in zip(axes,[('b04','b03','b02'),('b08','b04','b03')],['True color','False color: NIR/red/green']):
    ax.imshow(rgb(d,bands),extent=extent,origin='upper')
    ax.set(title=title+' / 2026-09-28',xlabel='UTM 33N easting (m)',ylabel='Northing (m)')
    ax.ticklabel_format(axis='x',style='sci',scilimits=(0,0))
plt.show()'''),
    md('''## 2. Mask quality; retain the denominator

`clear_fraction` records the fraction of each aligned 6 × 6 block of source 20 m SCL
pixels in vegetation (4), bare/not-vegetated (5), or water (6). We require **all 36**
children accepted. This deliberately conservative teaching rule excludes clouds,
shadows and other classes; it is not a validated local quality model. No class codes
were averaged. Pixel quality is distinct from the product's cloud percentage.

NDVI = (NIR − red)/(NIR + red). Here NDWI means the **green–NIR** ratio, not the
NIR–SWIR moisture index. Neither is a measured pollution concentration or crop yield.
We also exclude negative reflectances and near-zero denominators, without clipping.'''),
    code('''clear=d['clear_fraction']==1
ndvi=normalized_difference(d['b08'],d['b04'],clear)
ndwi=normalized_difference(d['b03'],d['b08'],clear)
print('All cells:',clear.size,'| accepted SCL:',int(clear.sum()),'| finite NDVI:',int(np.isfinite(ndvi).sum()))
fig,axes=plt.subplots(1,2,figsize=(11,5),layout='constrained')
for ax,value,title in zip(axes,[ndvi,ndwi],['NDVI','Green–NIR NDWI']):
    im=ax.imshow(value,extent=extent,origin='upper',vmin=-1,vmax=1,cmap='BrBG')
    ax.set(title=title+' / accepted SCL children',xlabel='Easting (m)',ylabel='Northing (m)')
    ax.ticklabel_format(axis='x',style='sci',scilimits=(0,0))
    fig.colorbar(im,ax=ax,label='Dimensionless ratio')
plt.show()'''),
    md('''## 3. Flatten only the bounded window

Create one row per 120 m cell with a stable row/column key. Python uses SQLite;
the main course lab teaches the related Zarrita → Arrow → DuckDB-WASM pattern.
`NULL` means an excluded index, not zero vegetation. COUNT(*) and COUNT(ndvi)
therefore answer different questions. UTM coordinates below are meters, not degrees.'''),
    code('''import sqlite3
con=sqlite3.connect(':memory:')
con.execute('CREATE TABLE pixels(row INTEGER,col INTEGER,x REAL,y REAL,clear REAL,ndvi REAL,PRIMARY KEY(row,col))')
records=[(r,c,float(d['x'][c]),float(d['y'][r]),float(d['clear_fraction'][r,c]),
          float(ndvi[r,c]) if np.isfinite(ndvi[r,c]) else None)
         for r in range(128) for c in range(128)]
con.executemany('INSERT INTO pixels VALUES(?,?,?,?,?,?)',records)
summary=con.execute('SELECT COUNT(*),COUNT(ndvi),AVG(ndvi) FROM pixels').fetchone()
print('Total, finite, mean NDVI:',summary)
assert summary[1]==np.isfinite(ndvi).sum()
np.testing.assert_allclose(summary[2],np.nanmean(ndvi))
print('Illustrative NDVI > 0.5 count:',con.execute('SELECT COUNT(*) FROM pixels WHERE ndvi > 0.5').fetchone()[0])'''),
    code('''# Sensitivity: always report retained counts with the descriptive mean.
thresholds=np.array([0.5,0.75,1.0])
counts=[];means=[]
for threshold in thresholds:
    values=normalized_difference(d['b08'],d['b04'],d['clear_fraction']>=threshold)
    counts.append(np.isfinite(values).sum()); means.append(np.nanmean(values))
fig,ax=plt.subplots(figsize=(7,4),layout='constrained')
ax.plot(thresholds,means,'o-');ax.set(xlabel='Minimum accepted SCL fraction',ylabel='Mean finite NDVI',title='Mask sensitivity in this window')
for x,y,n in zip(thresholds,means,counts): ax.annotate(f'n={n}',(x,y),xytext=(0,8),textcoords='offset points',ha='center')
ax.margins(y=.3);plt.show()''')],SOURCES+[
 '[Sentinel-2 Level-2A processing and Scene Classification](https://sentiwiki.copernicus.eu/web/s2-processing)',
 '[zarr-sql-views, dzole0311](https://github.com/dzole0311/zarr-sql-views): inspiration for the course query-to-view architecture; this lesson uses Python SQLite.'],
    'Change the SCL rule and NDVI threshold. Report excluded cells and explain why a large green area is not a food-security estimate.',
    'Spectral response depends on surface cover, atmosphere, mixtures and acquisition date. Food-security claims need crop calendars, yield validation, access and socioeconomic evidence.')

    lesson('33_eopf_openlayers','33 · OpenLayers: direct GeoZarr and band expressions',40,
      'inspect actual browser GeoZarr rendering; compare band order and display transforms.',[
    md(HEADER+'''## 1. Open the direct browser laboratory

[Open the two-map studio](https://jltobias.github.io/JupyterLite-zarr-sql-views/eopf/).
It uses actual **OpenLayers 10.11.0** and **EOxElements 2.10.0**, adapting the
[official OpenLayers examples](https://explorer.eopf.copernicus.eu/software-services/ol/).
GeoZarr support is evolving. The default reads the checked-in small window from the
same site. Choose **Live EOPF full scene** to request external source chunks; choose
the bundled window again if service access or CORS fails.

The Python cells inspect and reproduce the configuration; the linked page runs JavaScript.
This is not a Python OpenLayers binding. The static figures remain readable in the Book.'''),
    code('''from eopf import load_eopf, map_layers, SITE, rgb
d=load_eopf()
layers=map_layers(SITE+'/data/eopf/classroom.zarr/')
print(json.dumps(layers,indent=2))
display(HTML(f'<a href="{SITE}/eopf/" target="_blank" rel="noopener">Open interactive OpenLayers and EOxElements maps</a>'))'''),
    md('''## 2. Observe the network and change the view

1. Open browser developer tools → Network and filter for `zarr.json`, then `/c/`.
2. Reload the bundled window. Metadata is followed by array chunks.
3. Switch true color to false color; B08 now supplies the red display channel.
4. Switch to NDVI; compare with notebook 32. The map has **no SCL mask**.
5. Use keyboard focus and zoom controls. Reset extents after panning.

In OpenLayers, `band` expressions use **one-based** loaded-band indices. For NDVI,
this demo loads `[b08, b04]`, so band 1 is NIR and band 2 is red. It guards invalid
denominators and negative reflectances. Gamma and RGB stretching change appearance,
not the stored numbers. Map pixels are reprojected for display.'''),
    code('''# Reproduce the RGB stretch with numerical data, not screen colors.
fig,axes=plt.subplots(1,3,figsize=(12,4),layout='constrained')
for ax,maximum in zip(axes,[0.2,0.4,0.6]):
    ax.imshow(rgb(d,maximum=maximum));ax.set_title(f'Reflectance maximum {maximum}');ax.axis('off')
plt.show()
print('Unchanged red reflectance range:',float(d['b04'].min()),float(d['b04'].max()))'''),
    md('''## 3. Compare approaches

| Route | Where pixels are processed | What is delivered |
|---|---|---|
| OpenLayers GeoZarr | Browser JavaScript/WebGL | Metadata and numeric chunks |
| EOxElements GeoZarr | Browser, using OpenLayers | Same arrays plus declarative controls |
| TiTiler | External server | Rendered image tiles |
| Python lesson | Browser Pyodide or native Python | Bundled numeric arrays and plots |

Do not count downloaded array bytes as all network traffic: runtimes, scripts and
metadata also have costs. The source's multiscale hierarchy reduces detailed reads
when zoomed out, while the classroom store contains only one resolution.''')],SOURCES+[
 '[OpenLayers GeoZarr API](https://openlayers.org/en/latest/apidoc/module-ol_source_GeoZarr-GeoZarr.html), OpenLayers contributors, BSD-2-Clause.',
 '[EOxElements guide](https://explorer.eopf.copernicus.eu/software-services/eoxelements/), EOX, MIT.'],
    'Explain one visible difference caused by band order, one by display stretch, and one by a quality mask.',
    'Band order changes channel meaning; stretch changes display brightness; masking changes which observations contribute. These operations must not be conflated.')

    lesson('34_eopf_eox_widgets','34 · EOxElements Jupyter: Python-controlled maps',45,
      'create a real EOxMap widget in JupyterLite; link layer controls; change bands from Python.',[
    md(HEADER+'''## 1. Connect Python traits to a real map component

The [EOxElements-Jupyter guide](https://explorer.eopf.copernicus.eu/software-services/EOxElements-Jupyter/)
maps Python classes to EOxElements web components through **anywidget**. This lesson
uses `ipyeoxelements==1.1.0` with pinned map and layer-control releases. JupyterLite
installs the bundled pure-Python wheel; its JavaScript components load from jsDelivr.
The first widget start needs internet and WebGL. The Book strips live widget state
and retains the reference plot. Re-run in JupyterLite for the actual controls.'''),
    code('''from eopf import install_widget, load_eopf, map_layers, SITE, rgb, qualify_widget_urls
await install_widget()
from ipyeoxelements import EOxMap, EOxLayercontrol
from ipywidgets import HBox, VBox, Layout, Dropdown
import sys
d=load_eopf()
# Browser-relative URL also works when Pages is served below a project path.
url='../../data/eopf/classroom.zarr/' if sys.platform=='emscripten' else SITE+'/data/eopf/classroom.zarr/'
eo_map=EOxMap(version='2.10.0',id='classroom-eopf-map',
    layers=map_layers(url),center=[14.08,41.07],zoom=11,
    layout=Layout(width='100%',height='450px'))
qualify_widget_urls(eo_map)  # Convert relative URLs in the frontend document context.
control=EOxLayercontrol(version='1.10.1',for_='#classroom-eopf-map')
control._esm=control._esm.replace('!== null','!= null')  # Skip unset optional traits.
choice=Dropdown(options=['True color','False color'],description='Bands:')
def set_bands(change):
    bands=('b04','b03','b02') if change['new']=='True color' else ('b08','b04','b03')
    eo_map.layers=map_layers(url,bands)
choice.observe(set_bands,names='value')
display(VBox([choice,eo_map,control]))'''),
    md('''## 2. Trace a Python → widget update

Use the dropdown. The observer replaces the layer configuration, anywidget sends
the changed trait, and `<eox-map>` updates its WebGL layer. The layer-control targets
the map's unique ID. Do not reuse that ID for several displayed widgets.
The following change is visible in the map; the assert checks Python state only.
Browser tests additionally inspect the rendered component and its canvas.'''),
    code('''choice.value='False color'
assert eo_map.layers[0]['source']['bands']==['b08','b04','b03']
print('Python source configuration:',eo_map.layers[0]['source'])
# Independent static reference for readers of the Book.
fig,ax=plt.subplots(figsize=(6,5),layout='constrained')
ax.imshow(rgb(d,('b08','b04','b03')),extent=[d['provenance']['bounds'][i] for i in [0,2,1,3]])
ax.set(title='False-color reference / 120 m overview',xlabel='UTM 33N easting (m)',ylabel='Northing (m)')
plt.show()'''),
    md('''## 3. Extend to a globe and a story

The official [3D globe tutorial](https://explorer.eopf.copernicus.eu/software-services/eoxelements/globe)
and [EOxElements examples](https://explorer.eopf.copernicus.eu/software-services/eoxelements/)
show the globe plugin, terrain and storytelling components. Try the official globe
with its documented mosaic source; the small classroom window alone is not global
terrain. Distinguish a 3D camera from measured height, and distinguish a story's
annotations from observations. Compare with the course's existing LexCube lessons
for a genuinely time-indexed 3D data volume.

**Troubleshooting:** a blank widget can be a CDN/WebGL failure even when the Python
cell succeeds. Use notebook 33's separate map page or the static reference while
checking browser errors. Do not interpret a blank canvas as missing satellite data.''')],SOURCES+[
 '[EOxElements-Jupyter source](https://github.com/EOX-A/EOxElements-Jupyter), EOX and contributors; MIT notice bundled with the unmodified wheel.',
 '[anywidget documentation](https://anywidget.dev/), MIT.'],
    'Create a second independent map with a different ID and compare true and false color. Explain which state is shared and which is independent.',
    'Each map has its own layer configuration and ID. Reusing a layer-control selector may control the wrong map; copying arrays does not create a second acquisition.')

    lesson('35_eopf_titiler','35 · TiTiler: requests, tiles and processing boundaries',40,
      'construct a current TiTiler request; diagnose a recorded service failure; distinguish numeric pixels from rendered imagery.',[
    md(HEADER+'''## 1. Build the request from the actual item

The [TiTiler guide](https://explorer.eopf.copernicus.eu/software-services/titiler/)
illustrates server-rendered RGB, indices and cropping. APIs evolve: older tutorial
band-path syntax differs from the current service's STAC asset syntax. This lesson
uses `reflectance|bands=b04,b03,b02`, checked against the service's `/raster/api`.
URL-encode the asset selection rather than manually concatenating pipe/comma escapes.'''),
    code('''from eopf import load_eopf, tilejson_url, live_json, DATA
d=load_eopf(); url=tilejson_url(d['item'])
print('TileJSON request:',url)
record=json.loads((DATA/'service-provenance.json').read_text())
print('RECORDED HTTP status:',record['status'])
print('RECORDED response:',record['response'])
print('Recorded request date:',record['retrieved'])'''),
    md('''## 2. Run one optional metadata request

TileJSON describes a tile service; constructing a URL does not prove imagery was
rendered. On 2026-11-21 this request returned **HTTP 400**: the service attempted to
open the item's SCL array as a GeoZarr group. The successful STAC and direct-array
reads in earlier lessons establish that this is not proof of missing Sentinel data.
No TiTiler preview was obtained. The next cell retries only when you choose `LIVE=True`;
it does not silently substitute another scene or a fabricated server result.'''),
    code('''LIVE=False
if LIVE:
    try:
        current=await live_json(url)
        print('LIVE response:',current['tiles'][0])
    except Exception as exc:
        print('LIVE REQUEST FAILED:',exc,'The recorded response remains available.')
else:
    print('RECORDED MODE: no request sent; the saved HTTP 400 is the observed result.')'''),
    md('''## 3. Do not analyze display colors as reflectance

When a tile request succeeds, its PNG contains display colors. Its pixel grid can differ
from the UTM extract; it is not an independent validation dataset. Reprojection,
resampling, color enhancement and quantization can all change screen colors.
Use numeric GeoZarr arrays and documented masks for scientific calculations.

For an external map, open the current TiTiler Swagger UI from the guide, inspect
`assets`, `expression`, `rescale` and `reproject`, then request one small tile.
Avoid submitting an unbounded global crop. The Python kernel and map may run in a
browser while the numerical work still happens on the TiTiler server.'''),
    code('''from urllib.parse import urlsplit, parse_qs
request=parse_qs(urlsplit(url).query)
assert request['assets']==['reflectance|bands=b04,b03,b02']
assert request['rescale']==['0,0.4']
print('Display request:',request)
print('Numeric extract red mean:',float(np.mean(d['b04'])))
print('No server-rendered image is used in this lesson.')''')],SOURCES+[
 '[TiTiler-EOPF source](https://github.com/EOPF-Explorer/titiler-eopf), Apache-2.0; Development Seed, EOPF Explorer and contributors.',
 '[Current raster OpenAPI](https://api.explorer.eopf.copernicus.eu/raster/api).'],
    'Change the RGB stretch in a request and explain why the vegetation did not physically change. Record processing location, acquisition time and request time separately.',
    'Rendering time and acquisition time are different. Brightness adjustments are display choices; underlying reflectance and quality evidence must support physical interpretations.')

    lesson('36_eopf_studio_eodash','36 · openEO Studio and eodash: a reproducible handoff',50,
      'generate an inspectable Studio recipe and an eodash configuration; explain credentials, processing and evidence.',[
    md(HEADER+'''## 1. Build a recipe before opening Studio

[openEO Studio](https://studio.explorer.eopf.copernicus.eu/) is a browser editor for
Python that creates process graphs for a remote backend. Its
[script contract](https://studio.explorer.eopf.copernicus.eu/agents/script-contract.md)
provides `datacube`, `reduced` and `add_graph_to_map`; these names are not standard
standalone Python globals. `reduced` selects the first valid pixel, not a temporal
mean. The backend supplies physical reflectance, so applying DN scaling again is wrong.

We generate a small NDVI recipe and a prefill link. This does **not** submit a job or
save to an account. Studio requires login, then review and Save to execute/persist
the recipe. That external authenticated step is an optional instructor activity.'''),
    code('''from eopf import studio_sample, studio_link, DATA, SITE
sample=studio_sample()
backend=json.loads((DATA/'openeo-collection.json').read_text())
available=backend['cube:dimensions']['bands']['values']
assert all(b in available for b in sample['bands'])
assert backend['cube:dimensions']['bands']['type']=='bands'
print(json.dumps(sample,indent=2))
# Export locally for inspection; no server job is created.
Path('eopf-studio-sample.json').write_text(json.dumps(sample,indent=2),encoding='utf-8')
display(HTML(f'<a href="{studio_link(sample)}" target="_blank" rel="noopener">Open reviewed recipe in Studio (login required)</a>'))'''),
    md('''## 2. Verify the process before interpreting the map

Inspect the date interval, bbox, ordered band names and first-valid reduction.
The sample is a grayscale NDVI display recipe with a denominator guard; it does not
reproduce notebook 32's SCL-fraction mask. A scene-level cloud filter is not that mask.
Studio graph generation and server execution are separate verification steps.
This course validates recipe fields against recorded backend metadata and Python
syntax; it does not claim to have run your authenticated project.

For an African port or agricultural area, first repeat lesson 31's coverage search.
Then alter bbox, dates and the research question. Sea-level rise needs projections
and vertical datums; water safety needs calibrated retrievals and field samples;
food security needs much more than an NDVI snapshot.'''),
    code('''# Syntax validation is useful but is not remote process execution.
compile(sample['code'],'studio-recipe','exec')
print('Recipe syntax and ordered backend band names checked.')
print('Area:',sample['boundingBox'],'| dates:',sample['temporalRange'])'''),
    md('''## 3. Use eodash to coordinate a catalog, map and controls

The [eodash integration](https://explorer.eopf.copernicus.eu/software-services/eodash/)
uses a shared state store and configuration for linked views. Our
[eodash page](https://jltobias.github.io/JupyterLite-zarr-sql-views/eopf-dashboard.html)
loads the actual pinned web component **on button click** and points it at the EOPF
STAC API. It is an external-service explorer, not an offline replica of the course.
The configuration below is the same one used by that page.'''),
    code('''config=json.loads((DATA/'eodash-config.json').read_text())
assert config['stacEndpoint']['endpoint'].endswith('/stac')
assert config['stacEndpoint']['api'] is True
print(json.dumps(config,indent=2))
Path('eopf-dashboard-config.json').write_text(json.dumps(config,indent=2),encoding='utf-8')
display(HTML(f'<a href="{SITE}/eopf-dashboard.html" target="_blank" rel="noopener">Open actual eodash component</a>'))'''),
    md('''## 4. Publish an evidence-led story

Choose an item in eodash, adjust its date/filter controls and compare the visible
product ID with STAC Browser. A blank view may mean coverage, filter, service or
rendering failure. Record which one you established. In your evidence journal,
include item ID, acquisition date, CRS, resolution, quality rule, processing location,
rendering recipe and source credits. Connect to the existing AR6, FTW and SeasFire
studios only after aligning what each dataset can support.''')],SOURCES+[
 '[Studio prefill documentation](https://studio.explorer.eopf.copernicus.eu/agents/prefill.md) and [Studio source](https://github.com/developmentseed/openeo-studio), Development Seed, MIT.',
 '[eodash source](https://github.com/eodash/eodash), EOX and contributors, MIT.'],
    'Design a two-date follow-up for Lagos or Abidjan. Specify coverage checks, masks and additional evidence before changing any climate-impact claim.',
    'Two dates can show a difference, but seasonal timing, cloud/shadow errors, alignment and land management may explain it. A climate attribution requires a substantially stronger design.')
