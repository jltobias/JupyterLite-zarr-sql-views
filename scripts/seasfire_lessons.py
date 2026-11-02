"""Five SeasFire/LexCube lessons; generated notebooks remain independently runnable."""
SOURCES=[
 '[SeasFire Cube v0.4, Alonso et al. (2024)](https://doi.org/10.5281/zenodo.13834057), CC-BY-4.0. Spatial subsets and browser repackaging by this course; no spatial resampling.',
 '[Karasante, Alonso, Prapas, Ahuja, Carvalhais & Papoutsis (2025), SeasFire cube — a multivariate dataset for global wildfire modeling](https://doi.org/10.1038/s41597-025-04546-3), Scientific Data 12, 368.',
 '[ESA Open Science Catalog / EarthCODE](https://opensciencedata.esa.int/products/seasfire-cube/item), public SeasFire v0.4 mirror. Inputs used: GWIS burned area, ECMWF/Copernicus ERA5, NASA MODIS MOD13C1 v6 NDVI, and SeasFire derived VPD/cell area.',
 '[Exact source objects, SHA256 checksums, extraction windows and transformations](https://jltobias.github.io/JupyterLite-zarr-sql-views/data/seasfire-provenance.json).',
 '[Söchting, Scheuermann, Montero & Mahecha (2025), Interactive Earth system data cube visualization in Jupyter notebooks](https://doi.org/10.1080/20964471.2025.2471646), Big Earth Data, 1–15. [LexCube 2.0.1](https://github.com/msoechting/lexcube), Maximilian Söchting and contributors, GPL-3.0-or-later.',
]


def add_lessons(lesson,md,code):
    lesson('26_seasfire_discovery','26 · SeasFire: read the cube before reading the fire',35,
      'inspect source Zarr metadata; distinguish observations, reanalysis and derived quantities; preserve missing coverage.',[
    md('''## 1. One grid, several kinds of evidence

SeasFire harmonizes historical Earth-system variables for fire research. This studio uses the **v0.4**
release on ESA EarthCODE: **2001–2021**, nominal **8-day** intervals and **0.25°** grid cells.
Harmonization makes arrays align; it does not make their original sensors, accuracy or temporal support identical.

![SeasFire teaching workflow: catalog, bounded windows, masks and units, SQL and LexCube, cautious interpretation](assets/seasfire-workflow.svg)

| Variable | What it represents | Unit / aggregation |
|---|---|---|
| `gwis_ba` | Historical GWIS burned-area estimates, allocated by ignition date | hectares per cell and period; summed |
| `tp` | ERA5 total precipitation | mm per period; summed |
| `t2m_mean` | ERA5 2 m air temperature | kelvin; mean |
| `vpd` | SeasFire-derived vapor pressure deficit | hPa; mean |
| `ndvi` | Harmonized MODIS MOD13C1 v6 vegetation index | dimensionless; mean |

**Predict:** which variable can be summed across cells, and which should be area-weighted?
Our windows include northern Ghana and neighboring countries, and central Zambia and neighboring areas.
They are selected teaching windows, not country statistics.'''),
    code('''from seasfire import load_seasfire, raster
d=load_seasfire('ghana')
print(d['region']['title'])
print('Axes: time, latitude, longitude:',d['gwis_ba'].shape)
print('First / last starts:',d['dates'][[0,-1]])
print('Interval lengths and counts:',np.unique(d['duration_days'],return_counts=True))
print('Pixel-edge bounds:',d['region']['bounds'])
print('Source version:',d['provenance']['version'],'|',d['provenance']['license'])'''),
    md('''## 2. A small selection can require a large source chunk

Read the real Zarr v2 metadata before opening a remote array. The source stores an entire time axis in
each spatial chunk. A 16 × 16 request may still decode a 966 × 180 × 360 chunk. The native preparation
script caps source requests at 1.5 GiB in total, caches the necessary objects, and records their hashes.
The notebook reads a small local NPZ; the linked SQL lab reads an uncompressed Zarr v2 repackaging.
Both retain native grid values. No full global archive is loaded into your browser.'''),
    code('''spec=d['metadata']['gwis_ba/.zarray']
print('Global shape:',spec['shape'],'| chunks:',spec['chunks'],'| codec:',spec['compressor'])
print('One decoded source chunk: %.1f MiB' % (np.prod(spec['chunks'])*4/1024**2))
print('Selected raw fire array: %.2f MiB' % (d['gwis_ba'].nbytes/1024**2))
print('Latitude descends:',bool(np.all(np.diff(d['lat'])<0)))
print('Raw source description:',d['metadata']['gwis_ba/.zattrs']['creator_notes'])'''),
    md('''## 3. Missing is not zero

The GWIS temporal availability mask marks 2001 unavailable. It is a **global time-coverage mask**,
not a pixel-level quality score. The helper keeps those values missing. A finite zero later in the record
means zero burned area in this harmonized product, not proof that no small fire occurred.

The final annual interval has only 5 or 6 days. Derive durations from the actual timestamps and the
2022-01-01 closing boundary; do not assume 966 identical intervals or replace gaps with zero.'''),
    code('''available=d['gwis_ba_valid_mask']==1
assert np.isnan(d['gwis_ba'][~available]).all()
print('Unavailable bins:',int((~available).sum()))
print('Finite zero-fire cells:',int(np.sum(d['gwis_ba']==0)))
t=int(np.nanargmax(np.nansum(d['gwis_ba'],axis=(1,2))))
fig,ax=plt.subplots(figsize=(7,5),layout='constrained')
im=raster(ax,d,d['gwis_ba'][t],f"GWIS / SeasFire: {d['dates'][t]}")
fig.colorbar(im,ax=ax,label='Burned area (ha / cell / period)')
plt.show()'''),
    md('''## 4. Follow the catalog trail

Open the [ESA catalog item](https://opensciencedata.esa.int/products/seasfire-cube/item), then inspect its
Zarr asset, license and time coverage. Compare with the [versioned Zenodo record](https://doi.org/10.5281/zenodo.13834057).
The catalog and the mirror may evolve; this course records the exact retrieved object hashes.
An optional native refresh is `python scripts/prepare_seasfire.py --fetch` with `requirements-seasfire.txt`.
Do not run that command in JupyterLite.''')],SOURCES,
    'Open the Zambia window. Compare its grid bounds and units. Explain why the same grid resolution does not imply the same accuracy for fire and precipitation.',
    'Resampling and harmonization align coordinates; uncertainty remains specific to the underlying product. Missing coverage must stay missing.')

    lesson('27_seasfire_maps_sql','27 · Burned area: maps, SQL and a moving season',45,
      'query historical fire values; distinguish extensive totals from area-normalized quantities; animate a season.',[
    md('''## 1. Use the same values in Python and the SQL lab

The lab carries **2018–2021** to keep its 184 × 16 × 16 cube below the browser's cell budget.
The NPZ retains all 21 years for time-series analysis. Python uses SQLite; the linked lab follows
the zarr-sql-views approach with Zarrita, Arrow, DuckDB-WASM and deck.gl.
Both operate on the same burned-area values, with explicit dates and units.'''),
    code('''from seasfire import load_seasfire, raster
d=load_seasfire('ghana')
meta,fire=load_cube('seasfire_ghana')
np.testing.assert_array_equal(fire,d['gwis_ba'][d['dates']>=np.datetime64('2018-01-01')])
con=sql_connection(meta,fire)
rows=list(con.execute('SELECT t, COUNT(value), SUM(value) FROM cells GROUP BY t ORDER BY t'))
totals=np.array([r[2] for r in rows])
np.testing.assert_allclose(totals,np.sum(fire,axis=(1,2),dtype=float))
peak=int(np.argmax(totals))
print('Largest period total in this window:',meta['times'][peak],round(totals[peak]),'ha')
print('Contributing cells:',rows[peak][1])'''),
    md('''## 2. Compare a total with a normalized map

Burned area is extensive: add hectares over disjoint cells. ERA5 precipitation is a depth, so summing
millimeters over cells is not a regional rainfall statistic. Normalize fire area with SeasFire's `area`
in m²: `100 × burned_ha × 10,000 / cell_area`. This uses the **whole grid cell**, not its land-only area.
It is a product-derived area ratio; repeated burning and product errors can complicate an annual ratio.
Do not clip unexpected values silently.'''),
    code('''percent=100*fire[peak]*10000/d['area']
fig,axes=plt.subplots(1,2,figsize=(11,5),layout='constrained')
a=raster(axes[0],d,fire[peak],meta['times'][peak]+' | area')
b=raster(axes[1],d,percent,'Same period | whole-cell area ratio')
fig.colorbar(a,ax=axes[0],label='Burned area (ha / cell / period)',shrink=.7)
fig.colorbar(b,ax=axes[1],label='Burned area / cell area (%)',shrink=.7)
plt.show()
threshold=500
count=con.execute('SELECT COUNT(*) FROM cells WHERE t=? AND value>?',(peak,threshold)).fetchone()[0]
assert count==int(np.sum(fire[peak]>threshold))
print(count,'cells exceed',threshold,'ha in that period; not a count of fires.')'''),
    md('''## 3. Watch a year without changing the color scale

The animation uses all 46 bins in 2019, a fixed color range, and labels each interval duration.
Playback advances by bin, so short year-end intervals take the same screen time as eight-day bins.
GWIS assigns burned areas using ignition dates; the animation is not an active-fire video.'''),
    code('''from matplotlib.animation import FuncAnimation
keep=d['year']==2019
frames=d['gwis_ba'][keep]; dates=d['dates'][keep]; durations=d['duration_days'][keep]
fig,ax=plt.subplots(figsize=(7,5),layout='constrained')
image=raster(ax,d,frames[0],'',vmax=float(np.nanmax(frames)))
fig.colorbar(image,ax=ax,label='Burned area (ha / cell / period)')
def update(i):
    image.set_array(frames[i].ravel())
    ax.set_title(f"GWIS / SeasFire | {dates[i]} | {durations[i]} days")
    return image,
animation=FuncAnimation(fig,update,frames=len(frames),interval=180)
display(HTML(animation.to_jshtml(default_mode='loop')))
plt.close(fig)'''),
    md('''## 4. Move from map to space–time cube

Open the lab, filter `value > 500 AND t < 46`, then change between map, columns, cube and scene.
Columns encode burned-area magnitude. In the time cube the vertical axis is the **period index**.
Neither display represents terrain height. Exported points retain source, license and temporal support.'''),
    code("lab('seasfire_ghana','cube')")],SOURCES,
    'Repeat with Zambia. Compare the 2019 peaks using dates, totals and contributing area. Explain what a country comparison would require.',
    'These equal-sized angular windows cross administrative boundaries and differ in area and ecology. Country totals require boundaries, support-aware aggregation and coverage checks.')

    lesson('28_seasfire_seasons_lags','28 · Seasons, anomalies and lagged relationships',50,
      'build support-aware regional series; remove a training-period seasonal baseline; interpret lag correlations cautiously.',[
    md('''## 1. Compare two seasonal calendars

Fire seasons can differ across hemispheres. Compute a strict spatial sum of burned hectares (any missing
cell makes that period unavailable), and area-weighted means of intensive weather variables.
The baseline below uses **2002–2015**. The later **2016–2021** years are held out.
Nominal bins are indexed 0–45 within each year; their timestamps and durations remain available.'''),
    code('''from seasfire import load_seasfire, spatial_series, seasonal_anomaly, lag_correlation
fig,axes=plt.subplots(2,1,figsize=(10,7),layout='constrained')
for key in ['ghana','zambia']:
    d=load_seasfire(key)
    train=(d['year']>=2002)&(d['year']<=2015)
    for ax,var in zip(axes,['gwis_ba','tp']):
        values=spatial_series(d,var)
        _,baseline=seasonal_anomaly(values,d['bin'],train)
        ax.plot(np.arange(1,47),baseline,label=key.title())
axes[0].set(ylabel='Burned area (ha / window / period)',title='2002–2015 mean seasonal cycle')
axes[1].set(xlabel='Period within year (1–46)',ylabel='Area-weighted precipitation (mm / period)')
for ax in axes:ax.legend()
plt.show()'''),
    md('''## 2. Separate seasonality from anomalies

An association between dry weather and fire can largely reflect their common seasonal calendar.
Subtract the training-period average for each bin. Positive lag here pairs **driver[t−lag] with fire[t]**.
A lag of one is a source-bin step, not exactly eight days when crossing a year boundary.
The split is chronological, and a pair is used only if both its times are in the same split.'''),
    code('''d=load_seasfire('zambia')
train=(d['year']>=2002)&(d['year']<=2015)
test=d['year']>=2016
fire=spatial_series(d,'gwis_ba'); vpd=spatial_series(d,'vpd')
fire_anom,_=seasonal_anomaly(fire,d['bin'],train)
vpd_anom,_=seasonal_anomaly(vpd,d['bin'],train)
lags=np.arange(7)
fig,ax=plt.subplots(figsize=(9,4),layout='constrained')
for title,x,y,split in [('Raw, train',vpd,fire,train),('Anomaly, train',vpd_anom,fire_anom,train),
                        ('Anomaly, held out',vpd_anom,fire_anom,test)]:
    results=[lag_correlation(x,y,int(lag),split) for lag in lags]
    ax.plot(lags,[r[0] for r in results],marker='o',label=title)
    print(title,'valid pairs by lag:',[r[1] for r in results])
ax.axhline(0,color='grey',linewidth=.8)
ax.set(xlabel='VPD leads fire by this many bins',ylabel='Pearson correlation r',ylim=(-1,1))
ax.legend();plt.show()'''),
    md('''## 3. A descriptive calculation is not a forecast

These correlations have no independent-sample significance claim: adjacent periods and neighboring cells
are dependent, multiple lags were inspected, and omitted drivers remain. Shared seasonality, fuel growth,
land use, ignition and fire management can all matter. Harmonized variables can incorporate interpolation;
a real forecast must audit when each input was actually available. A chronological split alone cannot fix that.

For a forecast study, choose the lag and model on training data, reserve a final untouched test period,
compare with a seasonal baseline, and use dependence-aware uncertainty estimates.
Do not select the best held-out lag and report it as an unbiased final score.'''),
    code('''years=np.unique(d['year'])
annual=np.array([np.sum(fire[d['year']==y]) if np.isfinite(fire[d['year']==y]).all() else np.nan for y in years])
fig,ax=plt.subplots(figsize=(10,4),layout='constrained')
ax.bar(years,annual)
ax.set(xlabel='Year',ylabel='Sum of reported burned area (ha)',title='Zambia window: complete-year totals; 2001 unavailable')
plt.show()
print('Missing annual totals:',years[~np.isfinite(annual)])'''),
    md('''## 4. Connect to an impact question responsibly

SeasFire helps describe environmental conditions. Smoke exposure needs emissions, transport, population
and measurements; water-quality impacts need catchments, runoff and observations; food-security impacts
need crop calendars, yields, livelihoods and local knowledge. These cubes do not directly measure those outcomes.
Use [IPCC Africa context](https://www.ipcc.ch/report/ar6/wg2/chapter/chapter-9/) and local expertise when framing a project.''')],SOURCES,
    'Repeat the lag plot with precipitation or NDVI. Record the sign convention, baseline, valid-pair counts and two alternative explanations.',
    'A lagged correlation is a descriptive association. It does not establish a causal mechanism, climate attribution or operational forecast skill.')

    lesson('29_seasfire_lexcube','29 · LexCube: slice a real fire cube in the browser',45,
      'render the upstream LexCube widget; navigate time–latitude–longitude; reconcile a visual slice with exact Python values.',[
    md('''## 1. Load the browser widget

This is **LexCube 2.0.1**, not the deck.gl lab. Its Python backend runs in Pyodide and communicates
with its Jupyter widget frontend. The first setup downloads compatible packages and can take a minute.
Keep this tab open until the cell finishes. WebGL2 is required for the interactive view.

The helper installs the hash-pinned upstream wheel and disables its optional native process-memory diagnostic
inside the browser. Tile compression, values and rendering remain upstream code. LexCube retains
**GPL-3.0-or-later**; [source and adaptation notes](https://jltobias.github.io/JupyterLite-zarr-sql-views/vendor/lexcube/README.md)
are distributed with the site. Native Jupyter uses the regular installed package.
The Jupyter Book supplies a static reference map; use **Run in JupyterLite** for live interaction.'''),
    code('''from lexcube_lite import setup_lexcube, cube_sliders
lexcube=await setup_lexcube()
from seasfire import load_seasfire, data_array, raster
d=load_seasfire('ghana')
a=data_array(d,'gwis_ba')
print('LexCube',lexcube.__version__,'| dimensions:',a.dims,'| shape:',a.shape)
print('Data:',a.attrs['source'],'|',a.attrs['units'])'''),
    md('''## 2. Read the axes before rotating

The array order is **time, latitude, longitude**. LexCube displays time on Z, latitude on Y and longitude on X.
Time is not altitude, and voxels are not three-dimensional vegetation or smoke measurements.
The fixed color limits encode hectares per cell per period. Missing cells stay missing.

Drag to rotate, use the controls to switch between surface and voxel views, and adjust the clipping sliders.
Left-click the displayed data to explore a time series. The time axis advances by index, including shorter
year-end bins. Float32 voxel transfers are requested to avoid extra float16 rounding.

**Read the voxel-mode label:** volume controls can show raw values or seasonal anomalies and can filter
by a threshold or quantile. Switch the target to **values** for a raw-hectare comparison. LexCube's own
anomaly display is not the training-only baseline from lesson 28. A thresholded voxel view does not show
every value in the selection; the summary button below always reports the full selected array.'''),
    code('''w=lexcube.Cube3DWidget(a,cmap='inferno',vmin=0,vmax=float(a.max()),
                         widget_size=(10,7),force_float32_for_voxel_mode=True)
w.xlim=(0,16);w.ylim=(0,16);w.zlim=(0,len(a.time))
display(w)
display(cube_sliders(w,a))'''),
    md('''## 3. Make the visual selection auditable

The initial view shows all of 2018–2021. Limits use **start-inclusive, stop-exclusive indices**.
The button reads the current widget limits after your edits, reports exact values from the selected array,
and states the full denominator. It does not sum colors or infer values from a screenshot.
Click it after changing sliders; keyboard users can tab to and edit the range controls.
For 2018 alone, set time limits to `(0,46)`. Switching surface/volume modes can reset the clip;
read the displayed bounds and refresh the summary after changing mode.'''),
    code('''import ipywidgets as widgets
result=widgets.Output()
button=widgets.Button(description='Summarize selection',layout=widgets.Layout(width='200px'))
def summarize(_=None):
    with result:
        result.clear_output(wait=True)
        selected=w.get_current_cube_selection()
        values=selected.values
        print('Selection shape:',values.shape,'| finite cells:',int(np.isfinite(values).sum()),'/',values.size)
        if values.size:
            print('First / last starts:',str(selected.time.values[0])[:10],str(selected.time.values[-1])[:10])
            print('Sum of reported burned area:',round(float(np.nansum(values)),2),'ha across the selected cell-periods')
            print('This sum is not unique burned land area; repeated burning can be counted across periods.')
button.on_click(summarize)
display(button,result)
summarize()'''),
    md('''## 4. Keep a static view with the same units

A 2D map is easier to print, compare and describe in text. Below is the highest-total period in the
2018 reference year, with the same color range as the interactive cube. It remains readable in the Book
without a widget connection. Record the dates and limits with any screenshot.'''),
    code('''peak=int(np.argmax(a.values[:46].sum(axis=(1,2))))
fig,ax=plt.subplots(figsize=(7,5),layout='constrained')
image=raster(ax,d,a.values[peak],str(a.time.values[peak])[:10]+' | 2018 peak',vmax=float(a.max()))
fig.colorbar(image,ax=ax,label='Burned area (ha / cell / period)')
plt.show()
print('Full cube:',a.shape,'| 2018 reference:',a.values[:46].shape)''')],SOURCES,
    'Clip a quarter-year and a smaller spatial window. Use the summary button, then change a bound and explain why the denominator changed.',
    'Clipping selects original cell-periods. It does not increase spatial resolution or turn historical values into predictions. Report start/stop indices and dates.')

    lesson('30_seasfire_lexcube_compare','30 · LexCube comparisons: fire, dryness and evidence',50,
      'link two genuine LexCube selections; retain different units and color scales; compare a selected region as time series.',[
    md('''## 1. Compare the same support, not the same colors

We compare historical burned area and vapor pressure deficit in the Zambia window, 2018–2021.
VPD describes atmospheric drying demand in hPa; it is not soil moisture or a direct measure of crop stress.
Fire is an extensive amount in hectares. Each cube therefore has its own fixed color scale.
Matching spatial and temporal limits makes comparison meaningful without making the variables equivalent.'''),
    code('''from lexcube_lite import setup_lexcube, cube_sliders
lexcube=await setup_lexcube()
from seasfire import load_seasfire, data_array
import ipywidgets as widgets
d=load_seasfire('zambia')
fire=data_array(d,'gwis_ba'); dryness=data_array(d,'vpd')
np.testing.assert_array_equal(fire.time.values,dryness.time.values)
left=lexcube.Cube3DWidget(fire,cmap='inferno',vmin=0,vmax=float(fire.max()),widget_size=(8,6),force_float32_for_voxel_mode=True)
right=lexcube.Cube3DWidget(dryness,cmap='viridis',vmin=0,vmax=float(dryness.max()),widget_size=(8,6),force_float32_for_voxel_mode=True)
left.xlim=(0,16);left.ylim=(0,16);left.zlim=(0,len(fire.time))
links=[widgets.link((left,name),(right,name)) for name in ['xlim','ylim','zlim']]
display(HTML('<p><b>Burned area — hectares per cell per period</b></p>'))
display(left)
display(HTML('<p><b>Vapor pressure deficit — hPa</b></p>'))
display(right)
display(cube_sliders(left,fire))'''),
    md('''## 2. One selection, two summaries

The linked bounds start with all of 2018–2021. Change the first cube's sliders and both selections follow.
For 2019 alone, use time bounds `(46,92)`. Read the bounds again after switching visualization modes.
The button below reads those bounds and draws a shared calendar axis. Fire is summed over the selected
cells; VPD is weighted by their grid-cell areas. Both curves use separate axes and labeled units.
The initial static chart is stored in the Book; the button and linked cubes require a live kernel.'''),
    code('''out=widgets.Output()
compare=widgets.Button(description='Plot selected series',layout=widgets.Layout(width='200px'))
def plot_selection():
    f=left.get_current_cube_selection()
    v=right.get_current_cube_selection()
    if not f.size:
        print('Choose a nonempty selection.');return
    np.testing.assert_array_equal(f.time.values,v.time.values)
    # Coordinates index the original area array, preserving the exact selected support.
    import xarray as xr
    area=xr.DataArray(d['area'],dims=['latitude','longitude'],coords={'latitude':d['lat'],'longitude':d['lon']})
    area=area.sel(latitude=f.latitude,longitude=f.longitude)
    fire_total=f.sum(('latitude','longitude'),skipna=False)
    vpd_mean=v.weighted(area).mean(('latitude','longitude'))
    fig,axes=plt.subplots(2,1,figsize=(10,6),sharex=True,layout='constrained')
    axes[0].plot(f.time.values,fire_total.values,color='firebrick')
    axes[1].plot(v.time.values,vpd_mean.values,color='teal')
    axes[0].set(ylabel='Burned area (ha)',title='Selected native cells; periods labeled by start date')
    axes[1].set(ylabel='Area-weighted VPD (hPa)',xlabel='Period start')
    plt.show()
    print('Shape:',f.shape,'| sum of selected cell areas:',round(float(area.sum()/1e6),1),'km²')
def compare_selection(_=None):
    with out:
        out.clear_output(wait=True)
        plot_selection()
compare.on_click(compare_selection)
display(compare,out)
plot_selection()'''),
    md('''## 3. Save the selection as an evidence record

The record below captures the initial selection during Run All. After exploring, rerun this cell to
capture your own bounds. A record stores a reproducible selection, not an explanation of its cause.
Retain data and software citations when exporting screenshots or using these lessons in class.'''),
    code('''selection=left.get_current_cube_selection()
record={'dataset':d['provenance']['doi'],'version':'0.4','region':d['region']['id'],
        'variables':['gwis_ba','vpd'],'software':'LexCube 2.0.1',
        'xlim':list(left.xlim),'ylim':list(left.ylim),'zlim':list(left.zlim),
        'bounds_convention':'start inclusive, stop exclusive',
        'period_starts':[str(t)[:10] for t in selection.time.values],
        'data_license':'CC-BY-4.0','software_license':'GPL-3.0-or-later',
        'interpretation':'Descriptive historical comparison; not a causal or impact estimate'}
Path('seasfire-selection.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps(record,indent=2))'''),
    md('''## 4. Design the next investigation

Use lesson 28 to quantify lagged associations after removing a training-period seasonal cycle.
Propose one additional source for a question about smoke, catchment water quality, or agricultural impacts.
Explain its resolution, observation timing, independent validation and licensing. Do not overlay the tiny
FTW or Tessera windows as though they cover this same location or observation period.

For a teaching demonstration of LexCube controls, consult the
[creator's illustrated documentation and animations](https://github.com/msoechting/lexcube#readme).
The text equivalent is: rotate to inspect faces; clip dimensions with start/stop bounds; inspect values
with the time-series interaction; return to exact array statistics to support a claim.''')],SOURCES,
    'Make one comparison for each region. Retain the units and exact support, and propose a falsifiable explanation plus the independent evidence needed to test it.',
    'Linked views coordinate a question. They do not supply a causal design, observed impacts, operational warning skill or climate-change attribution.')
