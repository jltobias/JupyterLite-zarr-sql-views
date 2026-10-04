"""Authoring source for the course; emits valid, editable Jupyter notebooks."""
from pathlib import Path
import shutil
import textwrap
import nbformat as nb

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'notebooks'; OUT.mkdir(exist_ok=True)
SITE='https://jltobias.github.io/JupyterLite-zarr-sql-views'
INDEX=[]
def md(s):return nb.v4.new_markdown_cell(textwrap.dedent(s).strip())
def code(s):return nb.v4.new_code_cell(textwrap.dedent(s).strip())
def lesson(slug,title,minutes,objectives,cells,sources,challenge,answer):
    n=nb.v4.new_notebook()
    n.metadata={'kernelspec':{'display_name':'Python (Pyodide)','language':'python','name':'python3'},
                'language_info':{'name':'python'},'license':'ISC', 'course':{'minutes':minutes,'sources':sources}}
    n.cells=[md(f'''# {title}

**Time:** {minutes} minutes · **Audience:** undergraduate / introductory graduate GIS and Earth science.

**By the end:** {objectives}

[Run in JupyterLite]({SITE}/lite/lab/index.html?path={slug}.ipynb) · [Earth lab]({SITE}/lab/) · [Sources and licenses]({SITE}/book/credits.html)

Run cells from top to bottom with **Shift+Enter**. The first kernel start downloads Python WebAssembly packages.
The bundled exercises need no data-service account. Save a copy with **File → Save and Export Notebook As** before clearing browser storage.

![Four-stage workflow: STAC discovery, Zarr reading, SQL selection, linked views](assets/pipeline.svg)
'''),code('''from course import *
import numpy as np
import matplotlib.pyplot as plt
print('Ready: Python + NumPy + local teaching data')''')]+cells+[md(f'''## Try it yourself

{challenge}

## Check your reasoning

{answer}

## Evidence journal

Write four sentences: **what I observed; how I calculated it; what this cannot establish; what evidence I need next**.
For any figure you reuse, retain its units, date or scenario, data origin, transformations, and attribution.

## Sources and credit

'''+ '\n'.join(f'- {s}' for s in sources)+'''

Teaching adaptation of [dzole0311/zarr-sql-views](https://github.com/dzole0311/zarr-sql-views), ISC.
Original teaching code and prose: JupyterLite-zarr-sql-views contributors, ISC. Data keep their separate licenses.
''')]
    # Stable IDs keep regeneration reviewable.
    for i,c in enumerate(n.cells):c.id=f'{slug}-{i:02d}'
    nb.write(n,OUT/f'{slug}.ipynb'); INDEX.append({'slug':slug,'title':title,'minutes':minutes})

UP='[zarr-sql-views, source architecture and ISC license](https://github.com/dzole0311/zarr-sql-views)'
DE='[Digital Earth Africa WOfS specifications and limitations](https://docs.digitalearthafrica.org/en/latest/data_specs/Landsat_WOfS_specs.html), CC BY 4.0 data.'
C3='[C3S Atlas user tools](https://github.com/ecmwf-projects/c3s-atlas), European Union, Apache 2.0; pinned auxiliary CMIP6 warming-level table.'
IPCC='[IPCC AR6 WGII, Chapter 9: Africa](https://www.ipcc.ch/report/ar6/wg2/chapter/chapter-9/). Linked context, not redistributed data.'

lesson('01_start_here','01 · A browser is a scientific workspace',25,
       'Read a real array, identify its axes, and distinguish data from a visual encoding.',[
md('''## 1. Predict before running

What could an array with shape `(3, 48, 48)` represent? Sketch three maps stacked on top of one another.
The source application treats a time-varying geographic field as a cube and links it to SQL selections.
Here, the browser lab uses **Zarrita + DuckDB-WASM + deck.gl**. Python notebooks use **NumPy + SQLite + Matplotlib** for portable exercises.
Both read the same Zarr values. This is a teaching adaptation, not a Python distribution of upstream.
'''),
code("meta, water = load_cube('ngami')\nprint(meta['title'])\nprint('Axes = time, latitude, longitude; shape =', water.shape)\nprint('Times:', meta['times'])\nprint('Units:', meta['units'])"),
md('''## 2. Look at one slice

Each number is the fraction of clear satellite observations classified as water during a year.
A value of 0.8 does **not** mean 80% of the pixel is water, nor water on 80% of calendar days.
White gaps are missing values after quality masking, not dry land.'''),
code("map_slice(meta, water, t=0);\nplt.show()"),
md('''## 3. Ask one small question

How many sampled cells had water detected in more than half of their clear observations?
Keep the denominator visible.'''),
code("valid = np.isfinite(water[0])\nselected = valid & (water[0] > 0.5)\nprint(f'{selected.sum()} selected / {valid.sum()} valid sampled cells')\nassert np.all((water[valid[None].repeat(3, axis=0)] >= 0) | np.isnan(water[valid[None].repeat(3, axis=0)]))"),
md('''## 4. Move the same question into the lab

Choose **Lake Ngami**, type `value > 0.5 AND t = 0`, and run the query. Compare the count with Python.
Switch between 2D and 3D. Extrusion adds a visual height; it does not turn water frequency into terrain elevation.
The iframe needs the deployed course site. Use the link above it if embedding is restricted.'''),
code("lab('ngami', 'map')")], [UP,DE],
'Change the year and threshold. Which changes the count more? Record both denominators.',
'A threshold count describes sampled pixels and observation conditions. It cannot establish water volume, access, or a climate trend from three dates.')

lesson('02_zarr_sql','02 · From Zarr chunks to SQL rows',35,
       'Inspect Zarr metadata, reconstruct indices, and compare equivalent array and SQL filters.',[
md('''## 1. Inspect the storage contract

Zarr separates metadata from chunk bytes. Our deliberately small stores use Zarr v2, little-endian float32, C order,
no compression inside the store, and one time slice per chunk. The ZIP only packages files for JupyterLite.
The helper is an educational reader for this exact layout; it is not a general Zarr implementation.'''),
code("with zipfile.ZipFile('data/ngami.zip') as archive:\n    spec = json.loads(archive.read('value/.zarray'))\nprint(json.dumps(spec, indent=2))\nprint('Bytes per uncompressed chunk:', np.prod(spec['chunks']) * 4)"),
md('''## 2. Flatten without losing geography

For a C-order `(time, y, x)` array: `id = (time * ny + y) * nx + x`.
The latitude coordinates decrease down the array. Never assume row zero is the south edge.'''),
code("meta, values = load_cube('ngami')\nnt, ny, nx = values.shape\nt, y, x = 1, 12, 20\ncell_id = (t * ny + y) * nx + x\nassert values.ravel()[cell_id] == values[t, y, x] or np.isnan(values[t, y, x])\nprint('id:', cell_id, 'lon:', meta['lon'][x], 'lat:', meta['lat'][y])"),
md('''## 3. Make an explicit SQL view of the loaded window

SQL runs **after** this bounded cube is decoded. A `WHERE` expression does not automatically reduce remote Zarr reads.
NumPy stores missing values as NaN; the SQL table stores them as NULL. `COUNT(value)` excludes NULL.
SQLite is used in this Python cell. The companion browser lab uses real DuckDB-WASM.'''),
code("con = sql_connection(meta, values)\nquery = '''SELECT t, COUNT(value), AVG(value) FROM cells\n           WHERE value > 0.5 GROUP BY t ORDER BY t'''\nfor row in con.execute(query):\n    print(row)\nsql_n = con.execute('SELECT COUNT(*) FROM cells WHERE value > 0.5 AND t = 0').fetchone()[0]\nassert sql_n == np.count_nonzero(values[0] > 0.5)"),
md('''## 4. Experiment with the memory budget

This estimates only the raw float array. SQL tables, Arrow buffers, rendering buffers, and Python objects add overhead.
The lab imposes a 100,000-cell input limit. For remote large cubes, choose a bounding box, variable, resolution, and time window **before** decoding.'''),
code("for shape in [(3,48,48), (12,256,256), (365,2000,2000)]:\n    print(shape, 'raw float32 MiB:', round(np.prod(shape)*4/1024**2, 2))"),
code("lab('ngami','cube')")],[UP,'[Zarr v2 specification](https://zarr-specs.readthedocs.io/en/latest/v2/v2.0.html)'],
'Write SQL for a longitude window and two time slices. Verify the count with NumPy. Predict whether it changes bytes already fetched.',
'The filters should agree once NULL and NaN are handled consistently. Filtering an already-loaded table does not undo network transfer.')

lesson('03_deafrica_water','03 · Lake Ngami: water observations and missing evidence',40,
       'Trace a measured extract to its STAC assets and test a water-detection threshold.',[
md('''## 1. Establish provenance before mapping

These observations come from **Digital Earth Africa WOfS annual summaries** for 2018, 2020, and 2022.
The preparation script reads frequency and clear-observation count, samples a 48 × 48 geographic grid with nearest-neighbour resampling,
and masks locations with fewer than five clear observations. Native COG pixels are 30 m in EPSG:6933.
Our coarse geographic sample is **not** an area-averaged raster and must not be summed into square kilometres.'''),
code("meta, water = load_cube('ngami')\nprovenance = json.loads(Path('data/deafrica-provenance.json').read_text())\nprint(provenance['method'])\nfor item in provenance['records']:\n    print(item['year'], item['item_id'], item['frequency_url'])"),
md('''## 2. Compare maps on the same colour scale

With independent colour scales, a small change can appear dramatic. Use the same zero-to-one scale for every year.'''),
code("fig, axes = plt.subplots(1, 3, figsize=(13, 4), constrained_layout=True)\nfor t, ax in enumerate(axes):\n    image = ax.pcolormesh(meta['lon'], meta['lat'], water[t], vmin=0, vmax=1, cmap='viridis', shading='nearest')\n    ax.set(title=meta['times'][t], xlabel='Longitude', ylabel='Latitude')\nfig.colorbar(image, ax=axes, label='Water detection / clear observations')\nplt.show()"),
md('''## 3. Hold the sample support constant

Comparing changing sets of valid pixels can change a mean even if the underlying water state is unchanged.
An intersection mask trades coverage for comparability. This still does not remove cloud-season sampling bias.'''),
code("common = np.all(np.isfinite(water), axis=0)\nprint('Common support:', common.sum(), 'sampled cells')\nthresholds = [0.2, 0.5, 0.8]\nfor threshold in thresholds:\n    print(threshold, [int(np.count_nonzero((water[t] > threshold) & common)) for t in range(3)])"),
code("con=sql_connection(meta, water)\nlist(con.execute('SELECT t, COUNT(value), ROUND(AVG(value), 3) FROM cells GROUP BY t'))"),
md('''## 4. Move between observation and interpretation

Try the time slider, click a cell, then compare its history with the selected-cell mean.
Three sparse annual snapshots cannot attribute changes to climate change. River inflows, antecedent rain,
evaporation, abstraction, and observation quality are candidate explanations requiring additional evidence.
Water presence is also different from household access to reliable, safe water.'''),
code("lab('ngami','map')")],[DE,IPCC],
'Compare thresholds on common support and each year’s own support. Explain why both tables are useful.',
'Changing quality masks affect denominators. A sound comparison states the mask, the resampling method, the threshold, and the available years.')

lesson('04_maps_and_cubes','04 · 2D maps, 3D maps, and a space–time cube',35,
       'Choose a visual encoding that answers a question without confusing time, value, and physical height.',[
md('''## 1. Three vertical axes, three meanings

In the **extruded map**, height encodes a scaled value. In the **time cube**, height encodes a time index.
In the **value surface**, height is a scaled measurement. Geographic coordinates remain horizontal.
The cube spaces available time indices equally; the selected WOfS dates happen to be two years apart.
Never interpret an index axis as elapsed time for irregular data.'''),
code("meta, water = load_cube('ngami')\nmap_slice(meta, water, 1); plt.show()"),
md('''## 2. Construct a small cube in Python

Reduce point density for a clear static figure. A viewer can otherwise confuse occlusion with missing data.
Points below a threshold are hidden by design; add that fact to the caption.'''),
code("fig = plt.figure(figsize=(9,6))\nax = fig.add_subplot(111, projection='3d')\nt, y, x = np.indices(water.shape)\nkeep = np.isfinite(water) & (water > 0.25) & (x % 2 == 0) & (y % 2 == 0)\npoints = ax.scatter(np.asarray(meta['lon'])[x[keep]], np.asarray(meta['lat'])[y[keep]], t[keep], c=water[keep], vmin=0, vmax=1, cmap='viridis', s=8)\nax.set(xlabel='Longitude', ylabel='Latitude', zlabel='Time index (not height)', title='Observed WOfS sample; frequency > 0.25')\nax.set_zticks(range(3), meta['times'])\nfig.colorbar(points, ax=ax, shrink=.6, label=meta['units'])\nplt.show()"),
md('''## 3. Use interaction to test your first impression

Rotate the cube, switch to 2D, and click a location. Is the apparently persistent feature present at every time?
Try `value > 0.75`. Compare what the 3D view reveals with what it hides.'''),
code("lab('ngami','cube')"),
md('''## 4. Make a shareable selection

This export records time, value, origin, and license. It exports sampled points, not polygons with valid area.
Download it from the JupyterLite file browser, or use the lab’s GeoJSON button.'''),
code("n = export_geojson(meta, water, 'ngami-water-points.geojson', threshold=.75)\nprint('Exported',n,'sample points')")],[UP,DE,'[deck.gl OrbitView](https://deck.gl/docs/api-reference/core/orbit-view)'],
'Write one question best served by 2D, one by a time series, and one by a cube. Provide an accessible text description of each.',
'2D supports location comparison; series supports temporal change at a point or region; a cube reveals patterns across location and time but introduces occlusion.')

lesson('05_c3s_atlas','05 · C3S Atlas: scenarios, warming levels, and model spread',45,
       'Use real C3S Atlas auxiliary data, preserve missing categories, and compare global warming levels with regional change.',[
md('''## 1. Start in the official Atlas

Open the [Copernicus C3S Atlas](https://atlas.climate.copernicus.eu/). Select an African region, a temperature variable,
CMIP6, a scenario, a baseline, and a future period. Record these choices before comparing maps.
The original request’s “C32” is interpreted here as **C3S**.

The bundled CSV is the actual CMIP6 global-warming-level table from the official C3S Atlas user-tools repository,
pinned at `8d80d4e98053d96077ba67f29464b4f373ff4037`. It lists model-member averaging periods,
not local African temperature values. A global warming level and a local anomaly are different quantities.'''),
code("rows = list(csv.reader(Path('data/CMIP6_WarmingLevels.csv').open(encoding='utf-8')))\nlevels, scenarios = rows[0][1:], rows[1][1:]\nprint('Columns:', list(zip(levels, scenarios)))\nprint('Model-member rows:', len(rows)-2)"),
md('''## 2. Parse periods and preserve sentinels

The upstream selection code uses entries that contain a year range. Here `9999`, `NA`, blanks, and other text remain explicit categories.
We do **not** turn either sentinel into a year, zero warming, or a probability. Their precise semantics should be checked against the chosen dataset version.'''),
code("import re\nfrom collections import Counter\ndef periods_for(level='2', scenario='ssp245'):\n    j = next(i for i,pair in enumerate(zip(levels, scenarios)) if pair == (level, scenario)) + 1\n    periods=[]; excluded=Counter()\n    for row in rows[2:]:\n        value=row[j]\n        if re.fullmatch(r'\\d{4}-\\d{4}', value):\n            start,end=map(int,value.split('-')); periods.append((row[0],start,end))\n        else: excluded[value]+=1\n    return periods, excluded\nperiods, excluded = periods_for()\nprint('Valid windows:',len(periods),'Excluded codes:',dict(excluded))\nprint(periods[:4])"),
md('''## 3. Visualise model-member spread

The midpoint labels the supplied averaging window. It is not a prediction of a particular year’s temperature.
These model-member entries are not independent draws from a probability distribution; models may share structure.'''),
code("fig,ax=plt.subplots(figsize=(9,5))\nfor k,scenario in enumerate(['ssp126','ssp245','ssp370','ssp585']):\n    p, missing=periods_for('2',scenario)\n    mids=[(start+end)/2 for _,start,end in p]\n    ax.scatter(mids, np.full(len(mids),k), alpha=.55, label=f'{scenario}: n={len(mids)}')\n    print(scenario,'excluded:',dict(missing))\nax.set_yticks(range(4),['ssp126','ssp245','ssp370','ssp585'])\nax.set(xlabel='Midpoint of supplied 2°C global-warming-level window',title='C3S Atlas auxiliary CMIP6 table · model-member spread')\nax.legend(loc='best'); plt.show()"),
md('''## 4. Bridge to regional climate evidence

In the Atlas compare the same African region at 1.5°C and 2°C global warming. Record regional change and ensemble spread,
the variable’s units, the baseline, and the Atlas export citation. Repeat for a second African region and one region outside Africa.
Do not reuse the synthetic temperature cube as Atlas data.

For gridded downloads, use the [C3S Atlas dataset](https://cds.climate.copernicus.eu/datasets/multi-origin-c3s-atlas).
CDS requests can require an account and accepted terms. Prepare an approved regional subset outside JupyterLite;
retain the selected product’s license and acknowledgement. The [official user-tools book](https://ecmwf-projects.github.io/c3s-atlas/intro.html)
provides the full xarray/CDS workflow. This course does not embed credentials or redistribute arbitrary CDS data.'''),
code("display(YouTubeVideo('o62IPhpvsAI', width=720, height=405))"),
md('''Video: **Climate Atlas – Tutorial video**, Copernicus ECMWF. Hosted by the creator on YouTube; may require network access and captions are controlled by the provider.
[Open video directly](https://www.youtube.com/watch?v=o62IPhpvsAI). Reading alternative: [official Atlas guide](https://climate.copernicus.eu/copernicus-interactive-climate-atlas-guide-powerful-new-c3s-tool).''')],[C3,'[C3S Atlas dataset, DOI 10.24381/cds.h35hb680](https://doi.org/10.24381/cds.h35hb680)',IPCC],
'Change the warming level to 3°C. Report valid windows and excluded categories for each scenario. Explain why a histogram is not a calibrated likelihood.',
'Availability changes the ensemble. Always report the included sample size; global warming levels do not directly specify local impacts.')

lesson('06_heat_stress','06 · Global heat questions, African heat laboratory',40,
       'Map temperature exceedance while distinguishing air temperature, thermal stress, exposure, and vulnerability.',[
md('''## 1. State the evidence type

This cube is an **analytic synthetic field**, spanning an Africa-centred rectangle including ocean cells.
The twelve labels are fictional months in 2000, not a reanalysis. We use it to learn aggregation and threshold sensitivity.
Air temperature alone cannot calculate wet-bulb temperature or UTCI. Humidity, wind, radiation, and context matter.
For real global comparison, use the C3S Atlas or a documented thermal-stress product with its own definitions.'''),
code("meta,heat=load_cube('heat')\nprint(meta['description'])\nmap_slice(meta,heat,6);plt.show()"),
md('''## 2. Compare a chosen threshold across latitude bands

The 32°C threshold here is a teaching parameter, not a health recommendation. A count of monthly synthetic means above it
is not a count of hot days. Label the temporal aggregation honestly.'''),
code("threshold=32.0\ncon=sql_connection(meta,heat)\nfor row in con.execute('SELECT t, COUNT(*) FROM cells WHERE value > ? GROUP BY t ORDER BY t',(threshold,)):\n    print(meta['times'][row[0]],row[1])\nfig,ax=plt.subplots()\nfor low,high,label in [(10,25,'10–25°N'),(-25,-10,'10–25°S')]:\n    keep=(np.asarray(meta['lat'])>=low)&(np.asarray(meta['lat'])<=high)\n    ax.plot(range(1,13),heat[:,keep,:].mean(axis=(1,2)),label=label)\nax.set(xlabel='Fictional month',ylabel='Synthetic air temperature (°C)',title='Illustrative seasonality; unweighted rectangle means');ax.legend();plt.show()"),
md('''## 3. Test weighting

On a regular latitude-longitude grid, cell areas vary with latitude. Cosine-latitude weighting approximates an area mean.
It does not make a land-only mean or a population-exposure mean. Those need masks and an appropriately aligned population dataset.'''),
code("weights=np.broadcast_to(np.cos(np.deg2rad(meta['lat']))[:,None],heat.shape[1:])\nweighted=np.array([np.average(v,weights=weights) for v in heat])\nprint('Unweighted:',np.round(heat.mean(axis=(1,2)),2))\nprint('Area-weighted approximation:',np.round(weighted,2))"),
code("lab('heat','cube')"),
md('''## 4. Design a global comparison

Compare Lagos, Delhi, and São Paulo using a common real dataset, time interval, UTCI definition, and spatial support in a follow-on project.
Explain the difference between hazard (thermal conditions), exposure (people and activities), and vulnerability (ability to cope).
Do not rank cities from the synthetic Africa-only grid.''')], [IPCC,'[Copernicus: data and methods, including UTCI](https://climate.copernicus.eu/GCH2025-about-data-and-methods)'],
'Try thresholds of 30, 32, and 34°C. Then explain what additional inputs are needed to discuss worker heat stress.',
'Threshold choice changes the result. Temperature-only monthly fields cannot identify daily dangerous conditions or personal health risk.')

lesson('07_coastal_scenes','07 · Sea-level rise and the meaning of a 3D scene',40,
       'Build a terrain-like scene, test height thresholds, and identify missing physical processes.',[
md('''## 1. Read the synthetic terrain

Coordinates place an invented grid near Durban for geographic orientation only. Elevations are analytic, not a measured DEM.
The vertical zero has no surveyed datum. A threshold at 1 m is an experiment, not a sea-level projection.
Real inundation requires connected water pathways, defensible elevation and water-level datums, tides, waves, and local defenses.'''),
code("meta,terrain=load_cube('coast')\nz=terrain[0]\nlon,lat=np.meshgrid(meta['lon'],meta['lat'])\nfig=plt.figure(figsize=(9,6));ax=fig.add_subplot(111,projection='3d')\nsurface=ax.plot_surface(lon,lat,z,cmap='terrain',linewidth=0)\nax.set(xlabel='Longitude',ylabel='Latitude',zlabel='Invented elevation (m)',title='Synthetic coastal scene · vertical scale exaggerated')\nfig.colorbar(surface,ax=ax,shrink=.6,label='Invented elevation (m)');plt.show()"),
md('''## 2. Separate low cells from connected low cells

A flood-fill from the grid’s left edge illustrates connectivity. The edge is stipulated to be water-connected for this toy exercise.
This still omits flow dynamics and all real-world coastal forcing.'''),
code("from collections import deque\nlevel=1.0\nlow=z<level\nconnected=np.zeros_like(low)\nqueue=deque((y,0) for y in range(z.shape[0]) if low[y,0])\nwhile queue:\n    y,x=queue.popleft()\n    if connected[y,x]: continue\n    connected[y,x]=True\n    for yy,xx in [(y-1,x),(y+1,x),(y,x-1),(y,x+1)]:\n        if 0<=yy<z.shape[0] and 0<=xx<z.shape[1] and low[yy,xx] and not connected[yy,xx]:\n            queue.append((yy,xx))\nprint('Below threshold:',low.sum(),'Connected to assumed boundary:',connected.sum())\nassert np.all(~connected | low)"),
code("fig,axes=plt.subplots(1,2,figsize=(10,4))\nfor ax,grid,title in zip(axes,[low,connected],['Below 1 m (toy)','Connected below 1 m (toy)']):\n    ax.pcolormesh(meta['lon'],meta['lat'],grid,cmap='Blues',shading='nearest',vmin=0,vmax=1)\n    ax.set(title=title,xlabel='Longitude',ylabel='Latitude')\nplt.show()"),
md('''## 3. Explore uncertainty before telling a story

Add ±0.5 m as an arbitrary perturbation to illustrate sensitivity. It is not an estimated DEM error distribution.
If a small perturbation changes many classifications, a precise-looking 3D picture can conceal substantial uncertainty.'''),
code("for offset in [-.5,0,.5]:\n    print('Invented offset:',offset,'m; cells below level:',np.count_nonzero(z+offset<level))\nlab('coast','scene')")],[IPCC,'[IPCC AR6 WGI, Chapter 9: Ocean, Cryosphere and Sea Level Change](https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-9/)'],
'Increase the height threshold, then specify the minimum metadata needed to replace this scene with a real coastal DEM.',
'Document vertical and horizontal datums, resolution, acquisition date, terrain versus surface height, uncertainty, and water connectivity. None is established by a smooth rendering.')

lesson('08_air_quality','08 · Air quality: a map is not an exposure estimate',35,
       'Inspect spatial gradients and distinguish surface pollution, atmospheric columns, and human exposure.',[
md('''## 1. Identify the quantity

Our synthetic field is labeled illustrative surface PM2.5 in µg/m³. It is not CAMS output or station data.
Satellite aerosol optical depth is a column optical quantity; it cannot be renamed surface PM2.5 without a justified retrieval or model.
For a real extension, inspect the [Copernicus Atmosphere Data Store](https://ads.atmosphere.copernicus.eu/) and the selected product documentation.'''),
code("meta,air=load_cube('air')\nmap_slice(meta,air,0);plt.show()"),
md('''## 2. Compare regions with explicit spatial support

These boxes are latitude bands, not administrative regions. Their means include ocean cells.
Neither is population weighted. A visually tall column in the lab only encodes scaled value.'''),
code("con=sql_connection(meta,air)\nfor label,lo,hi in [('Northern band',10,25),('Equatorial band',-5,5)]:\n    result=list(con.execute('SELECT t, AVG(value) FROM cells WHERE lat BETWEEN ? AND ? GROUP BY t ORDER BY t',(lo,hi)))\n    plt.plot([r[0]+1 for r in result],[r[1] for r in result],label=label)\nplt.xlabel('Fictional month');plt.ylabel('Illustrative PM2.5 (µg/m³)');plt.title('Synthetic band means');plt.legend();plt.show()"),
md('''## 3. Ask what an exposure model needs

Explore changes under a chosen threshold without attaching regulatory or health meanings to it.
Actual exposure depends on where and when people are present, indoor conditions, and many other factors.
Spatial alignment, units, averaging period, and missing-data handling must be checked before joining population and pollution grids.'''),
code("threshold=35\nprint('Synthetic cell-months above chosen threshold:',np.count_nonzero(air>threshold))\nlab('air','columns')")],[IPCC,'[Copernicus Atmosphere Monitoring Service](https://atmosphere.copernicus.eu/)'],
'Explain why “largest average concentration” and “largest total population exposure” could identify different regions.',
'A concentration map weights location; an exposure estimate weights people and time. Both require transparent assumptions and appropriate observations.')

lesson('09_water_quality','09 · Water quality: from optical signal to a testable hypothesis',35,
       'Follow a moving reflectance feature and identify what calibration is needed to discuss water quality.',[
md('''## 1. Follow a synthetic plume

The grid uses Lake Victoria-area coordinates but invented red-band reflectance. It is not a satellite scene.
Reflectance is dimensionless. Sediment, algae, bottom reflectance, atmosphere, and viewing conditions can all influence optical signals.
A high value is not a pathogen measurement and cannot establish drinking-water safety.'''),
code("meta,red=load_cube('water')\nmap_slice(meta,red,5);plt.show()"),
md('''## 2. Make a space–time section

A transect sacrifices one spatial dimension to make temporal movement easier to inspect.
Unlike a 3D cube it has no occlusion, but a different row could show a different story.'''),
code("row=15\nfig,ax=plt.subplots()\nimage=ax.pcolormesh(meta['lon'],range(1,13),red[:,row,:],shading='nearest',cmap='viridis')\nax.set(xlabel='Longitude along selected row',ylabel='Fictional month',title='Synthetic optical plume · a Hovmöller-style section')\nfig.colorbar(image,ax=ax,label='Red reflectance (dimensionless)');plt.show()"),
md('''## 3. Export candidate locations for validation

Treat a threshold as a screening hypothesis. Plan paired in-situ sampling and quality control to evaluate the hypothesis.
For real Earth observation practice, discover Sentinel-2 surface-reflectance assets through DE Africa STAC and inspect masks and scaling.
The WOfS dataset used elsewhere in this course measures water presence, not water quality.'''),
code("print('Exported candidate cell-months:',export_geojson(meta,red,'optical-candidates.geojson',threshold=.06))\nlab('water','cube')")],[DE,'[Digital Earth Africa direct data access](https://docs.digitalearthafrica.org/en/latest/platform_tools/index_direct_access.html)'],
'Move the transect and threshold. Propose a calibration study with a response variable, paired samples, and an independent validation set.',
'A defensible model needs field measurements and uncertainty estimates. A bright plume alone cannot diagnose its cause or safety consequences.')

lesson('10_food_water','10 · Food and water insecurity: separate the signal from the claim',40,
       'Analyse seasonality and distinguish a physical proxy from a social outcome.',[
md('''## 1. Begin with a causal question

The rainfall field is synthetic. It can demonstrate dry-month selection; it cannot estimate crop yields, hunger, or access to water.
Food insecurity also involves markets, livelihoods, conflict, institutions, and access. Water insecurity is not equivalent to low rainfall.
Use the IPCC Africa chapter as context, and center local expertise when formulating follow-on questions.'''),
code("meta,rain=load_cube('rain')\nmap_slice(meta,rain,2);plt.show()"),
md('''## 2. Use a reference with the same seasonal definition

Only one fictional year is present, so a climatological anomaly or SPI cannot be calculated.
Subtracting this field’s own annual mean produces a seasonal departure, not a climate anomaly or drought index.'''),
code("departures=rain-rain.mean(axis=0,keepdims=True)\nfig,ax=plt.subplots()\nimage=ax.pcolormesh(meta['lon'],meta['lat'],departures[2],cmap='BrBG',vmin=-85,vmax=85,shading='nearest')\nax.set(xlabel='Longitude',ylabel='Latitude',title='Synthetic March departure from this fictional annual mean')\nfig.colorbar(image,ax=ax,label='mm/month departure');plt.show()"),
md('''## 3. Ask a portable SQL question

Count low-rainfall cell-months by latitude band. Explain the chosen threshold and the rectangle’s spatial support.
For a real extension, DE Africa provides access to rainfall and vegetation data; check each product’s native units, time axis, and license before use.'''),
code("con=sql_connection(meta,rain)\nquery='SELECT t, COUNT(*) FROM cells WHERE value < 40 AND lat BETWEEN -15 AND 0 GROUP BY t ORDER BY t'\nprint(list(con.execute(query)))\nlab('rain','cube')"),
md('''## 4. Construct an evidence ladder

**Observed physical variable → validated agronomic relationship → exposure and livelihoods → food-security assessment.**
At each arrow write down one missing dataset and one assumption. Include an adaptation option that local partners can evaluate,
such as forecast communication or water management, without claiming this notebook establishes its effectiveness.''')],[IPCC,'[Digital Earth Africa datasets](https://docs.digitalearthafrica.org/en/latest/data_specs/index.html)'],
'Design a follow-on experiment joining real seasonal rainfall and vegetation. Specify a multi-year baseline and a validation strategy.',
'Match spatial support and time intervals first. A correlation is not a causal effect, and a physical proxy alone is not a social vulnerability measure.')

lesson('11_stac_geolibre','11 · STAC discovery and GeoLibre handoff',40,
       'Inspect STAC assets, understand CORS and formats, and transfer a documented selection to a browser GIS.',[
md('''## 1. Separate metadata from pixels

STAC catalogs describe collections and items; asset links point to data. A COG asset is not a Zarr store.
The observed lesson’s source COGs were prepared outside the browser into a small Zarr extract using a reproducible script.
Catalog access does not guarantee cross-origin permission for every asset.'''),
code("provenance=json.loads(Path('data/deafrica-provenance.json').read_text())\nitem=provenance['records'][-1]\nprint('Search:',item['search'])\nprint('Raster:',item['frequency_url'])\nprint('Source CRS:',provenance['source_crs'],'Teaching CRS:',provenance['output_crs'])"),
md('''## 2. Make an optional live STAC request

Set `LIVE = True` to request a small metadata response. The default uses the recorded provenance so the lesson can finish
when a service is unavailable. The fallback is explicitly labeled and never silently substitutes invented observations.
Pyodide uses browser fetch, which obeys CORS; desktop Python uses urllib.'''),
code("LIVE=False\nif LIVE:\n    try:\n        if __import__('sys').platform == 'emscripten':\n            from pyodide.http import pyfetch\n            response=await pyfetch(item['search'])\n            if not response.ok: raise RuntimeError(f'HTTP {response.status}')\n            stac=await response.json()\n        else:\n            import urllib.request\n            with urllib.request.urlopen(item['search'],timeout=30) as response: stac=json.load(response)\n        print('LIVE STAC items:',len(stac['features']))\n        print('Asset names:',list(stac['features'][0]['assets']))\n    except Exception as exc:\n        print('LIVE REQUEST FAILED:',str(exc),'Use the recorded metadata above; no new observation was obtained.')\nelse:\n    print('RECORDED METADATA MODE:',item['item_id'])"),
md('''## 3. Inspect in a STAC browser

Open [DE Africa Explorer](https://explorer.digitalearth.africa/products/wofs_ls_summary_annual),
or paste `https://explorer.digitalearth.africa/stac` into [STAC Browser](https://radiantearth.github.io/stac-browser/).
Record the item ID, collection, date interval, bounding box, CRS, asset media type, nodata, units, and license.
When a viewer cannot load an asset, inspect the network response and format before assuming the dataset is empty.'''),
code("meta,water=load_cube('ngami')\nprint('Exported',export_geojson(meta,water,'ngami-for-geolibre.geojson',.5),'sampled points')"),
md('''## 4. Handoff to GeoLibre

1. Download `ngami-for-geolibre.geojson` from the JupyterLite file browser (or use the lab export button).
2. Open [GeoLibre Web](https://web.geolibre.app/) and add the local GeoJSON file using its data import controls.
3. Style points by `value`, retain `time`, and inspect the `kind` field.
4. Compare its 2D or 3D presentation with the course lab. Read GeoLibre’s current tool documentation before using analyses.
5. Save your project with a caption stating that these are sampled locations rather than areal flood polygons.

No GeoLibre Python installation or credential is required for this file-based handoff.
Other useful browser tools include [EO Browser](https://apps.sentinel-hub.com/eo-browser/),
[Copernicus Browser](https://browser.dataspace.copernicus.eu/), and [NASA Worldview](https://worldview.earthdata.nasa.gov/).
Some tools or downloads require their own accounts. Their availability and terms remain external to this course.''')],[DE,'[STAC specification](https://stacspec.org/en/about/stac-spec/)','[GeoLibre source and documentation](https://github.com/opengeos/GeoLibre)'],
'Inspect one additional DE Africa collection. Explain why its source asset can or cannot be opened directly by the lab’s Zarr reader.',
'The current lab accepts the bundled schema, not arbitrary STAC items. COGs, compressed Zarr variants, coordinate systems, and authentication each need an explicit adapter.')

lesson('12_capstone','12 · Capstone: an evidence-led climate story',60,
       'Produce a reproducible map narrative that states uncertainty, provenance, and a responsible interpretation.',[
md('''## 1. Choose a question with a bounded claim

Choose observed Lake Ngami water change, C3S model-member spread, or a clearly labeled synthetic method experiment.
Frame a claim the available data can answer. For an African climate-burden discussion, pair the result with the IPCC Africa chapter
and local knowledge; neither the notebook nor an attractive map establishes impacts on its own.'''),
code("meta,values=load_cube('ngami')\ncon=sql_connection(meta,values)\nresult=list(con.execute('SELECT t, COUNT(value), AVG(value) FROM cells GROUP BY t ORDER BY t'))\nfor row in result: print(row)\nmap_slice(meta,values,2);plt.show()"),
md('''## 2. Record your method as structured evidence

Fill this record with your own choices. Cite both upstream software and actual data used.
When sharing, include a screenshot or static figure, the notebook, a GeoJSON if relevant, and the record below.'''),
code("record={\n 'question':'How does sampled water detection differ across the three supplied years?',\n 'dataset':meta['title'], 'origin':meta['kind'], 'units':meta['units'],\n 'method':'Mean across available sampled cells; quality mask in provenance',\n 'limitations':['Three snapshots cannot establish a climate trend','Sampled cells are not equal-area flood extent'],\n 'next_evidence':['Longer water and rainfall record','Local hydrological interpretation'],\n 'source':meta['source'], 'license':meta['license']\n}\nPath('evidence-record.json').write_text(json.dumps(record,indent=2),encoding='utf-8')\nprint(json.dumps(record,indent=2))"),
md('''## 3. Peer review with a 20-point rubric

| Criterion | Points | What to check |
|---|---:|---|
| Question and scope | 4 | Claim fits spatial and temporal support |
| Reproducibility | 4 | Code runs; transformations and filters are stated |
| Provenance | 4 | Data origin, version, license, and software credits |
| Visual reasoning | 4 | Units, scale, uncertainty, text alternative |
| Interpretation | 4 | Distinguishes observation, inference, and missing evidence |

Ask a peer to change a threshold or mask. Does your conclusion survive? If not, revise the claim instead of hiding the sensitivity.

## 4. Plan the next version

For a real climate-impact project: co-design the question with affected communities; select an appropriate observed or modeled product;
create a bounded, licensed subset; test coordinate and unit handling; validate against independent evidence; then communicate the uncertainty.
The digital method is only one part of that work.''')],[UP,DE,C3,IPCC],
'Submit a notebook, evidence record, and a two-minute explanation of what the visualization cannot establish.',
'A strong submission makes a modest, reproducible claim and identifies the next evidence needed. A synthetic exercise is valid when its data origin remains unmistakable.')

if __name__=='__main__':
    (OUT/'assets').mkdir(exist_ok=True)
    shutil.copy2(ROOT/'public/assets/pipeline.svg',OUT/'assets/pipeline.svg')
    shutil.copy2(ROOT/'public/data/deafrica-provenance.json',OUT/'data/deafrica-provenance.json')
    (ROOT/'course-index.json').write_text(__import__('json').dumps(INDEX,indent=2)+'\n',encoding='utf-8')
    print('Wrote',len(INDEX),'notebooks')
