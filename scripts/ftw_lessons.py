"""Four Global Fields of the World lessons, independently runnable in Pyodide."""
SOURCES=[
    '[Global Fields of the World on Source Cooperative](https://source.coop/ftw/global-data), Taylor Geospatial and collaborators, CC-BY-4.0.',
    '[Robinson et al. (2026), The first global agricultural field boundary map at 10 m resolution](https://doi.org/10.48550/arXiv.2605.11055).',
    '[Pinned official FTW catalog and product documentation](https://github.com/fieldsoftheworld/ftw-data-catalog/tree/fd844c4c646af0f8e653fba774f79cc17b2af124/catalog). PRUE model predictions use Copernicus Sentinel-2 composites.',
    '[Exact extracts, source ETags, spatial selection and SHA256 checksums](https://jltobias.github.io/JupyterLite-zarr-sql-views/data/ftw-provenance.json). Local modifications: spatial subsets, GeoJSON conversion and scalar Zarr repackaging; original class values and full selected polygon geometries retained.',
]


def add_lessons(lesson,md,code):
    lesson('22_ftw_discovery','22 · Global FTW: discover fields, probabilities and confidence',35,
           'find the correct FTW product; inspect the three model classes; explain what a field prediction means.',[
    md('''## 1. What kind of field is this?

**Global Fields of the World (FTW)** maps predicted agricultural field boundaries for 2024 and 2025.
The PRUE model uses Sentinel-2 planting and harvest composites. A connected predicted field interior is a
remote-sensing unit: it is **not a legal parcel, ownership record, crop label, or yield measurement**.
The earlier *Fields of the World training benchmark* is a separate dataset; these global predictions are not ground truth.

![Sentinel-2 composites lead to three probabilities, predicted polygons, and a separate confidence layer; independent evidence is required for impacts](assets/ftw-workflow.svg)

This studio uses two small African windows: the Senegal River valley and western Kenya. Each contains
128 × 128 contiguous native pixels, with all three probability classes and both years. These chosen windows
do not represent either country's farming systems. A roughly 10 m pixel is a model grid cell, not a promise of 10 m boundary accuracy.

**Predict:** can a sharp outline establish who farms the land? Name the independent evidence you would need.'''),
    code('''from ftw import load_ftw, raster_map
d=load_ftw('senegal')  # repeat with 'kenya'
p=d['probability']
print(d['region']['title'])
print('Axes: year, class, row, column:',p.shape)
print('Years:',d['years'],'| classes:',d['bands'])
print('Pixel-edge bounding box:',d['region']['bounds'])
print('License:',d['provenance']['license'])
print('Source catalog commit:',d['provenance']['catalog_commit'])'''),
    md('''## 2. Read a catalog before reading a planet

The bundled metadata is a pinned copy of the official STAC catalog. Catalogs describe assets; they do not
make every format directly readable in every browser. Inspect the Zarr array's dimensions and codecs.
Its full-resolution array uses sharded Zarr v3. Native preparation reads only the needed chunks;
our browser receives small NPZ extracts and uncompressed Zarr v2 teaching cubes.

| Product | Meaning | Useful question |
|---|---|---|
| Three ~10 m probability classes | Model softmax outputs | Which class is favored here? |
| Field polygons | Predicted field units | What sizes and shapes were delineated? |
| 500 m confidence / polygon score | Separate regional reliability model | How sensitive is a result to a quality filter? |

The metadata commit pins documentation. It does **not** freeze cloud data. Source ETags and extract checksums
record the retrieved objects and the exact classroom files.'''),
    code('''catalog=json.loads((DATA/'ftw-catalog.json').read_text())
metadata=json.loads((DATA/'ftw-zarr-metadata.json').read_text())
a=metadata['consolidated_metadata']['metadata']['variables']
print('Catalog:',catalog['id'])
print('Global shape:',a['shape'],'| dtype:',a['data_type'])
print('Shard shape:',a['chunk_grid']['configuration']['chunk_shape'])
print('Codec:',a['codecs'][0]['name'])
global_bytes=int(np.prod(a['shape'],dtype=np.int64))*4
print(f'Uncompressed logical probability array: {global_bytes/1e12:.1f} TB')
print(f'This window, decoded probabilities: {p.nbytes/1e6:.2f} MB')
print('Transfer size also depends on source chunks, compression and request overhead.')'''),
    md('''## 3. Three classes, one probability budget

At each valid pixel the three probabilities sum approximately to one. A high boundary score can coexist
with a low field-interior score in a small field. These are model scores; they have not become calibrated
probabilities of ownership, productivity, or food insecurity. Missing predictions remain missing.'''),
    code('''valid=np.isfinite(p).all(axis=1)
np.testing.assert_allclose(p.sum(axis=1)[valid],1,atol=2e-6)
fig,axes=plt.subplots(1,3,figsize=(13,4),layout='constrained')
for b,ax in enumerate(axes):
    image=raster_map(ax,d,p[1,b],f"2025: {d['bands'][b].replace('_',' ')}")
fig.colorbar(image,ax=axes,label='Model class probability (0–1)',shrink=.7)
plt.show()
print('Valid pixel-years:',int(valid.sum()),'of',valid.size)
print('Mean class scores:',np.round(np.nanmean(p,axis=(0,2,3)),3))'''),
    md('''## 4. Browse beyond this sample

Open [FTW on Source Cooperative](https://source.coop/ftw/global-data) or the
[Portolan STAC browser](https://browser.portolan-sdi.org/#/external/data.source.coop/ftw/global-data/catalog.json).
Find the vector collection, a country partition, its GeoParquet asset, PMTiles map and style.
Record the year, license and product type before comparing it with this sample. External browsers need network access;
the numerical exercises run from bundled files after JupyterLite loads.

The optional native refresh command is `python scripts/prepare_ftw.py --fetch`, after installing
`requirements-ftw.txt` in a separate native Python environment. It is not a JupyterLite cell.
The source country files can be large: the script requires HTTP ranges, spatial row-group statistics and a byte budget.''')],SOURCES,
    'Repeat with Kenya. Compare the three class distributions and explain why boundary-heavy pixels do not prove poor farming conditions.',
    'A model output describes a learned image pattern. Field identity, land rights, agricultural performance and household welfare require other evidence.')

    lesson('23_ftw_probability_sql','23 · FTW probability cubes: maps, SQL and 3D',40,
           'query a real FTW Zarr extract; quantify threshold sensitivity; interpret 3D probability views.',[
    md('''## 1. Carry one class from Zarr into SQL

The lab cube keeps the **field-interior** class for both years. The three-class NPZ from lesson 22 remains
available for comparisons. We copy native probability values without resampling. Rows run north to south,
columns west to east; coordinates are pixel centers. The display shows the pixel footprints.

Python uses SQLite in this notebook. The linked JavaScript lab uses **Zarrita → Arrow → DuckDB-WASM → deck.gl**,
following the zarr-sql-views approach. Neither path needs a server-side database.'''),
    code('''from ftw import load_ftw, raster_map
d=load_ftw('senegal')
meta,value=load_cube('ftw_'+d['region']['id'])
np.testing.assert_array_equal(value,d['probability'][:,1])
con=sql_connection(meta,value)
summary=list(con.execute('SELECT t, COUNT(value), AVG(value), MIN(value), MAX(value) FROM cells GROUP BY t ORDER BY t'))
for t,n,mean,low,high in summary:
    print(meta['times'][t],n,'pixels; mean:',round(mean,4),'range:',round(low,4),round(high,4))
map_slice(meta,value,1);plt.show()'''),
    md('''## 2. A threshold changes the question

Counting pixels with `value > 0.5` asks how many pixel centers pass that model-score cutoff.
It does not count fields. A pixel fraction on this small geographic grid is also not a geodesic crop-area estimate.
Boundary pixels, excluded missing values, partial fields and model error all affect interpretation.

**Predict:** should raising the threshold ever increase the selected count? Check both SQL and NumPy.'''),
    code('''thresholds=np.linspace(.1,.9,9)
fig,ax=plt.subplots(figsize=(8,4))
for t,year in enumerate(d['years']):
    counts=[]
    for threshold in thresholds:
        n=con.execute('SELECT COUNT(*) FROM cells WHERE t=? AND value>?',(t,float(threshold))).fetchone()[0]
        assert n==int(np.count_nonzero(value[t]>threshold))
        counts.append(n)
    assert np.all(np.diff(counts)<=0)
    ax.plot(thresholds,counts,marker='o',label=str(year))
ax.set(xlabel='Field-interior probability threshold',ylabel='Selected native pixels',title='Threshold sensitivity / one teaching window')
ax.legend();plt.show()'''),
    md('''## 3. Give height an honest meaning

In this surface plot, height is a probability. It is not terrain, crop height, flood depth, or agricultural output.
We show every fourth pixel to keep the 3D figure legible; this is display subsampling, not a new analytical grid.
Read the 2D map beside it: perspective and occlusion can hide detail.'''),
    code('''from matplotlib.ticker import MaxNLocator
fig=plt.figure(figsize=(10,5));ax=fig.add_subplot(111,projection='3d')
xx,yy=np.meshgrid(d['lon'][::4],d['lat'][::4])
ax.plot_surface(xx,yy,value[1,::4,::4],cmap='viridis',vmin=0,vmax=1,linewidth=0)
ax.set(xlabel='Longitude',ylabel='Latitude',zlabel='Field probability',zlim=(0,1),title='2025 model-score surface / every fourth pixel')
ax.xaxis.set_major_locator(MaxNLocator(3));ax.yaxis.set_major_locator(MaxNLocator(3))
ax.ticklabel_format(useOffset=False,style='plain',axis='both')
plt.show()'''),
    code("lab('ftw_'+d['region']['id'],'cube')"),
    md('''## 4. Experiment in the linked lab

Use `value > 0.5 AND t = 1` for 2025, then remove `t = 1` to compare both years.
Switch between the 2D map, 3D columns, scene and time cube. The time cube separates the two annual snapshots;
it does not show crop growth between them. Click a cell for its two-point series.

Exported lab GeoJSON contains **pixel-center points**. Lesson 24 exports **field polygons**.
Both carry attribution and provenance, but they answer different questions.'''),
    code("n=export_geojson(meta,value,'ftw-probability-points.geojson',.8)\nprint('Exported pixel-year points at probability >= 0.8:',n)")],SOURCES+[
    '[zarr-sql-views by dzole0311](https://github.com/dzole0311/zarr-sql-views), ISC; inspiration for the browser Zarr/SQL/graphics architecture.'
],
    'Switch to Kenya. Run a 2025 threshold of 0.7, compare SQL with NumPy, and explain why the number of selected pixels is not the number of farms.',
    'A cutoff selects model scores on a grid. Polygonization, field validation and a definition of farm would each add information that the count does not contain.')

    lesson('24_ftw_fields_confidence','24 · Field polygons, confidence and selection bias',45,
           'map real FTW polygons; query their attributes; distinguish class probability from regional confidence.',[
    md('''## 1. Move from pixels to predicted field units

We selected all provider polygons that intersect the raster window. Their geometries are **not clipped**;
the map viewport hides portions outside the window. `metrics:area` and `metrics:perimeter` describe the
provider's full polygons, in square metres and metres. We retain an edge-crossing flag so those areas cannot
silently be presented as area within this window. Selection is by intersection, not a random field sample.

The catalog describes polygons derived from thresholded field interiors. Their separate delivery and processing
mean a local contour of this probability array is not guaranteed to reproduce the published polygons exactly.'''),
    code('''from ftw import load_ftw, raster_map, draw_fields, field_connection, export_fields
d=load_ftw('senegal')
fig,axes=plt.subplots(1,2,figsize=(12,5),layout='constrained')
for t,ax in enumerate(axes):
    image=raster_map(ax,d,d['probability'][t,1],str(d['years'][t]))
    n=draw_fields(ax,d,d['years'][t])
    ax.set_title(f"{d['years'][t]} / {n} intersecting polygons")
fig.colorbar(image,ax=axes,label='Field probability (0–1); black outlines = polygons',shrink=.7)
plt.show()
con=field_connection(d)
for row in con.execute('SELECT year, COUNT(*), SUM(crosses_window_edge), COUNT(confidence), AVG(confidence) FROM fields GROUP BY year ORDER BY year'):
    print('year, polygons, edge-crossing, with confidence, mean confidence:',row)'''),
    md('''## 2. Two scores with different spatial support

The field-interior probability belongs to a ~10 m pixel and is one of three softmax classes.
The polygon `confidence` attribute comes from a **separate 500 m confidence raster**, sampled upstream at
the polygon's representative point (a point on its surface). It is scaled as `raw / 0.578178 × 100`, capped at 100.
It is **not** the mean pixel probability and **not** the probability that every boundary vertex is correct.
Neighboring fields may share the same confidence cell.

The upstream guidance discusses a score around **69** as a possible quality filter. Treat it as a sensitivity
experiment: conservative scores outside the training distribution can remove real fields, particularly in
smallholder landscapes. Missing confidence is unknown, not zero.'''),
    code('''thresholds=[0,30,50,69,80,90]
print('year | minimum confidence | retained | sum of full polygon areas (ha)')
fig,ax=plt.subplots(figsize=(8,4))
for year in d['years']:
    retained=[]
    for cutoff in thresholds:
        n,area=con.execute('SELECT COUNT(*), COALESCE(SUM(area_m2),0)/10000 FROM fields WHERE year=? AND confidence>=?',(year,cutoff)).fetchone()
        retained.append(n)
        print(year,cutoff,n,round(area,2))
    ax.plot(thresholds,retained,marker='o',label=str(year))
ax.set(xlabel='Minimum regional confidence score',ylabel='Retained polygon records',title='Who disappears when the filter becomes stricter?')
ax.legend();plt.show()'''),
    md('''## 3. Inspect the polygons that survive

For a simple full-polygon size distribution, restrict to polygons wholly inside the window. This avoids
using outside area but introduces an additional size-selection bias: large fields are more likely to cross
an edge. Do not present this as the country-wide field-size distribution. Counts and area sums from
different annual layers are not longitudinal tracking of the same fields.'''),
    code('''fig,ax=plt.subplots(figsize=(8,4))
for year in d['years']:
    areas=np.array([r[0]/10000 for r in con.execute('SELECT area_m2 FROM fields WHERE year=? AND crosses_window_edge=0 AND area_m2>0',(year,))])
    if len(areas):
        ax.hist(np.log10(areas),bins=12,alpha=.5,label=f'{year}, n={len(areas)}')
ax.set(xlabel='log10(full predicted polygon area / hectares)',ylabel='Polygon count',title='Fully contained predictions / no confidence filter')
ax.legend();plt.show()
fig,ax=plt.subplots(figsize=(7,5))
image=raster_map(ax,d,d['probability'][1,1],'2025 / outlines with confidence >= 69')
fig.colorbar(image,ax=ax,label='Field probability (0–1)')
print('Outlined polygons:',draw_fields(ax,d,2025,69))
plt.show()'''),
    md('''## 4. Export a traceable selection to browser GIS

Download the GeoJSON produced below from JupyterLite's file browser and import it into
[GeoLibre Web](https://web.geolibre.app/), or another GeoJSON-capable GIS. Style by `confidence` and inspect
`crosses_window_edge`. The file retains full geometries, the filter, source citation and CC-BY attribution.
It contains no ownership information. External tools have their own availability and terms.'''),
    code("count=export_fields(d,'ftw-selected-fields.geojson',year=2025,min_confidence=69)\nprint('Exported polygon records:',count)")],SOURCES,
    'Repeat with Kenya. Compare retention at 50, 69 and 90, then write two possible explanations for the difference that do not assume farming quality.',
    'Different imagery, field geometry, training coverage and confidence-model behavior can change retention. A quality filter changes the population being described and needs independent validation.')

    lesson('25_ftw_change_food_water','25 · Annual field predictions and food–water questions',50,
           'compare annual predictions on common support; make a temporal visualization; design a defensible climate-impact study.',[
    md('''## 1. Difference is a calculation; change is an interpretation

Subtract 2024 probabilities from 2025 probabilities at the same pixels. This produces **a difference between
model outputs**, not a verified map of field creation, abandonment, drought or flood damage. Annual input
composites, crop cycles, clouds, model errors and real land changes can all contribute. Two annual layers
cannot establish a climate trend. Polygon IDs are not stable field identities across years.

Use a fixed paired-valid mask. If one year were missing, replacing it with zero would invent a difference.'''),
    code('''from ftw import load_ftw, raster_map, paired_difference
d=load_ftw('kenya')
delta,paired=paired_difference(d['probability'])
fig,axes=plt.subplots(1,3,figsize=(14,4),layout='constrained')
for t in range(2):
    annual=raster_map(axes[t],d,d['probability'][t,1],str(d['years'][t]))
fig.colorbar(annual,ax=axes[:2],label='Field probability (0–1)',shrink=.65)
image=raster_map(axes[2],d,delta,'2025 minus 2024',cmap='RdBu_r',vmin=-1,vmax=1)
fig.colorbar(image,ax=axes[2],label='Difference in model probability',shrink=.75)
plt.show()
print('Paired valid pixels:',paired.sum(),'of',paired.size)
print('Mean paired difference:',round(float(np.nanmean(delta)),5))
for cutoff in [.1,.25,.5]:
    print('|difference| >',cutoff,':',int(np.count_nonzero(np.abs(delta)>cutoff)),'pixels')'''),
    md('''## 2. Animate the two snapshots without inventing intermediate years

The player alternates the two annual arrays with a fixed 0–1 color scale. There is no interpolation.
It is a teaching animation of predictions, not satellite video. Stop on each frame and read the year.
The static panels above carry the same evidence if animation is unavailable.'''),
    code('''from matplotlib.animation import FuncAnimation
fig,ax=plt.subplots(figsize=(7,5))
image=raster_map(ax,d,d['probability'][0,1],'2024 / field probability')
fig.colorbar(image,ax=ax,label='Model class probability (0–1)')
def frame(i):
    image.set_array(d['probability'][i,1].ravel())
    ax.set_title(f"{d['years'][i]} / field probability / annual model output")
    return (image,)
animation=FuncAnimation(fig,frame,frames=2,interval=1200,repeat=True)
display(HTML(animation.to_jshtml(default_mode='once')))
plt.close(fig)'''),
    md('''## 3. Compare representations before making a claim

Even if field probability changes little, a threshold can split or merge connected areas and alter polygon counts.
Try several pixel thresholds and compare annual selected-pixel counts. These are model sensitivities, not a
validation against independent field observations.'''),
    code('''fig,ax=plt.subplots(figsize=(6,5))
a=d['probability'][0,1][paired];b=d['probability'][1,1][paired]
image=ax.hexbin(a,b,gridsize=35,extent=(0,1,0,1),mincnt=1,cmap='magma')
ax.plot([0,1],[0,1],'--',color='cyan',lw=1)
ax.set(xlabel='2024 field probability',ylabel='2025 field probability',title='Same native pixels / common support',aspect='equal')
fig.colorbar(image,ax=ax,label='Pixel pairs per bin');plt.show()
for threshold in [.3,.5,.7]:
    print('threshold',threshold,'2024 / 2025:',int((a>threshold).sum()),int((b>threshold).sum()))'''),
    md('''## 4. Connect fields to climate and food–water questions

FTW can provide candidate spatial units for a study. It does not supply the hazard, exposure, yields, irrigation,
markets, access to food, or adaptation capacity needed to assess impacts. For example:

| Question | Evidence to add | Matching / validation task |
|---|---|---|
| Were predicted fields exposed to flooding? | Event-dated water maps and local flood observations | Intersect contemporaneous fields and water; test cloud/missing-data masks |
| Did water stress affect crops? | Rainfall, soil moisture, crop calendar, irrigation and measured yields | Match seasons and spatial support; check field data and alternative causes |
| Could rising seas affect delta agriculture? | Local elevation/datum, salinity, defenses, drainage and sea-level projections | Use hydraulic/salinity evidence; a sea-level offset is not an inundation map |
| Is a household food insecure? | Consented socioeconomic and food-access evidence | A field outline cannot identify household circumstances |

The course's Digital Earth Africa water example is at Lake Ngami, **not these FTW windows**. Do not spatially
join it here. Retrieve compatible, dated coverage for the actual study area and preserve its license and uncertainty.
The Lagos and Abidjan GeoTessera extracts likewise do not overlap these windows. Embedding similarity is not
a substitute for a validated crop or hazard classifier. Country-level comparisons require a sampling design.

## 5. Instructor exercise: an evidence plan

Write one bounded question, the unit of analysis, dates, a spatial selection rule, a missing-data policy,
a confidence-sensitivity analysis, independent validation, and an attribution statement.
Peer review using five criteria (4 points each): scope, reproducibility, provenance, visual reasoning and interpretation.'''),
    code('''plan={
 'question':'Where do these two annual FTW model outputs differ?',
 'region':d['region']['title'], 'years':d['years'],
 'method':'2025 minus 2024 field probability, paired finite native pixels',
 'claim_limit':'Differences are not independently verified land change or climate attribution',
 'next_evidence':['Dated Sentinel-2 imagery','Independent field boundaries and local interpretation','Seasonally matched hazard observations'],
 'citation':d['provenance']['paper'], 'license':d['provenance']['license']
}
print(json.dumps(plan,indent=2))''')],SOURCES+[
    '[Digital Earth Africa Water Observations from Space specifications](https://docs.digitalearthafrica.org/en/latest/data_specs/Landsat_WOfS_specs.html).',
    '[IPCC AR6 WGII Chapter 9: Africa](https://www.ipcc.ch/report/ar6/wg2/chapter/chapter-9/), context for climate impacts, vulnerability and adaptation.'
],
    'Repeat for Senegal. Draft a flood-exposure study with compatible observations; state why a change in polygon count alone would not validate its conclusion.',
    'A defensible study aligns dates, support and meaning across data sources, tests selection effects and validates with independent evidence. Model differences alone cannot establish a climate burden.')
