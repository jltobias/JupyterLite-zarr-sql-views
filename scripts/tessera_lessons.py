"""GeoTessera embedding studio: five independent browser-executable lessons."""
SOURCES=[
    '[TESSERA project](https://geotessera.org/) and [model repository](https://github.com/ucam-eo/tessera), University of Cambridge and collaborators.',
    '[Feng et al., TESSERA: Temporal Embeddings of Surface Spectra for Earth Representation and Analysis](https://doi.org/10.48550/arXiv.2506.20380), 2025, revised 2026.',
    '[GeoTessera Python client](https://github.com/ucam-eo/geotessera), MIT; pinned preparation commit in the provenance.',
    '[dClimate global-store documentation](https://github.com/dClimate/tessera-embeddings/blob/main/docs/global-store.md): annual v1.1-dclimate embeddings and observation counts.',
    '[Bundled source snapshot, coordinates, transformations and checksums](https://jltobias.github.io/JupyterLite-zarr-sql-views/data/tessera-provenance.json). Embedding data: CC0-1.0; [upstream terms and advisory guidelines](https://github.com/ucam-eo/tessera/blob/master/aup.md).',
]


def add_lessons(lesson,md,code):
    lesson('17_tessera_embeddings','17 · GeoTessera: from satellite years to embedding vectors',35,
        'explain an embedding; decode quantized vectors; inspect coverage and distinguish data support from meaning.',[
    md('''## 1. A different kind of Earth observation layer

A temperature layer gives a physical quantity at a location. An **embedding** gives a vector of learned features.
TESSERA summarizes an annual sequence of optical and radar inputs. Its dimensions are useful together; dimension 7 is
not automatically vegetation, heat, poverty, or water quality. A downstream task needs evidence connecting vectors to a target.

![Satellite observations become annual vectors; compare patterns, then validate with independent evidence](assets/tessera-workflow.svg)

Our real samples come from the **v1.1 / dclimate** inference run, with 128 dimensions for each selected pixel-year.
The two small windows lie near Apapa in Lagos and Treichville in Abidjan. These are teaching windows, not port boundaries
or representative samples of either city. We retain 2018, 2021 and 2025. We do not mix model versions or inference variants.

**Predict:** would a vector by itself tell you the date of a flood? Explain why an annual summary cannot resolve that event.'''),
    code('''from tessera import load_tessera, unit_vectors, scalar_map
d=load_tessera('lagos')  # try 'abidjan'
X=d['embedding']
print(d['city']['title'])
print('Axes: year, row, column, embedding dimension:', X.shape)
print('Years:', d['years'])
print('Snapshot:', d['provenance']['snapshot_id'])
print('Source grid:', d['city']['source_crs'], '| source pixel: 10 m')
print('Query spacing: 0.000375 degrees (about 42 m), individual source pixels; no averaging.')
print('Largest query-to-native-center offset (m):',round(d['city']['max_query_to_pixel_center_m'],3))'''),
    md('''## 2. Decode the compact representation

The extract preserves the provider's signed 8-bit integers `q` and one positive scale `s` per pixel.
Decode using `x = q * s`. This recovers the published quantized representation, with its quantization error;
it does not reconstruct the original satellite images. Missing scales and zero-length vectors remain missing.

This library runs on native Python during preparation. JupyterLite needs only NumPy to analyze the verified extracts,
so the classroom does not depend on a live cloud request or a native Icechunk/GDAL installation.'''),
    code('''t,r,c=2,32,32
q=d['quantized'][t,r,c]; s=d['scales'][t,r,c]
decoded=q.astype(np.float32)*s
np.testing.assert_allclose(decoded,X[t,r,c])
print('Integer dtype:',q.dtype,'| scale:',s)
print('First eight decoded components:',np.round(decoded[:8],4))
fig,ax=plt.subplots(figsize=(10,3.5))
ax.plot(np.arange(128),decoded,lw=1.2)
ax.set(xlabel='Embedding dimension (index, not wavelength)',ylabel='Learned component value',
       title='One Lagos pixel / 2025 / TESSERA v1.1-dclimate')
plt.show()'''),
    md('''## 3. Ask what the model was able to see

Inspect missing vectors and the number of usable optical and radar observations. These counts describe input support;
they are not confidence intervals. A valid vector may exist with no radar observations. Missing pixels are not a water mask.
All figures in this studio show values sampled from individual 10 m native pixels at a coarser geographic query grid.
The displayed squares do not mean every point in that square was measured.'''),
    code('''fig,axes=plt.subplots(1,3,figsize=(13,4),layout='constrained')
for ax,year,valid in zip(axes,d['years'],d['valid']):
    scalar_map(ax,d,valid.astype(float),f'{year}: {valid.mean():.1%} valid',cmap='gray_r',vmin=0,vmax=1)
plt.show()
for i,year in enumerate(d['years']):
    valid=d['valid'][i]
    radar=d['s1_asc_obs_count'][i]+d['s1_desc_obs_count'][i]
    print(year,'valid pixels:',valid.sum(),
          'median optical count:',float(np.median(d['s2_obs_count'][i][valid])),
          'valid pixels with zero radar:',int((valid&(radar==0)).sum()))'''),
    md('''## 4. Inspect the evidence trail

The public source is a Zarr store in an Icechunk repository. An Icechunk snapshot identifies a consistent state of that store.
The checksums identify the exact local extracts. These solve different reproducibility problems.

The optional native preparation command, run from a checkout outside JupyterLite, is:

```bash
python -m pip install -r requirements-tessera.txt
python scripts/prepare_tessera.py --fetch
```

It reads six bounded spatial windows and reuses verified extracts. The checked-in provenance pins the snapshot.
Cloud chunk sizes make network transfer larger than the final samples; do not extrapolate output size to download cost.'''),
    code('''for item in d['provenance']['artifacts']:
    print(item['file'], f"{item['bytes']/1e6:.2f} MB", item['sha256'][:16]+'...')
raw_bytes=d['quantized'].nbytes+d['scales'].nbytes
print('This city, q + scales:',raw_bytes,'bytes; decoded float32:',X.nbytes,'bytes')''')],SOURCES,
    'Switch to Abidjan. Compare valid coverage and observation counts, then explain why different counts alone do not prove different model accuracy.',
    'An embedding is a learned description, not a measured hazard. A missing vector, a low observation count, and an inaccurate prediction are three different things.')

    lesson('18_tessera_similarity','18 · Similarity search: vectors, maps, Zarr and SQL',40,
        'calculate cosine similarity; test a reference and threshold; export a traceable geographic query.',[
    md(r'''## 1. Turn “looks similar” into a reproducible calculation

Choose one reference vector and compare all vectors to it. Cosine similarity is the dot product divided by the two vector lengths:

$$s(x,r)=\frac{x\cdot r}{\|x\|\|r\|}.$$

Scores range from −1 to 1. They are not probabilities. A score of 0.9 does not mean 90% confidence in a land-cover label.
Our reference is the native pixel selected by query row 32, column 32 in **2025**. The same vector is used for every year.
Its location is a demonstration choice with no supplied land-cover label.'''),
    code('''from tessera import load_tessera, unit_vectors, scalar_map, export_points
d=load_tessera('lagos')
U=unit_vectors(d['embedding'])
reference=U[-1,32,32]
similarity=np.clip(np.sum(U*reference,axis=-1),-1,1)
print('Reference native pixel:',d['native_lon'][32,32],d['native_lat'][32,32])
print('Reference self similarity:',similarity[-1,32,32])
fig,axes=plt.subplots(1,3,figsize=(13,4),layout='constrained')
for i,ax in enumerate(axes):
    im=scalar_map(ax,d,similarity[i],f'{d["years"][i]} / fixed 2025 reference',cmap='viridis',vmin=-1,vmax=1)
    ax.plot(d['lon'][32],d['lat'][32],marker='+',color='red',ms=10)
fig.colorbar(im,ax=axes,label='Cosine similarity (dimensionless)')
plt.show()'''),
    md('''## 2. A threshold is an analyst choice

The red cross marks the query reference. Similar pixels may have multiple explanations. Repeat the experiment with another
valid reference or threshold before describing a pattern. A self-match is a useful mathematical check, not a validation result.

The next chart measures the fraction of valid **sampled pixels**, not the fraction of the city's area or population.'''),
    code('''thresholds=np.array([.70,.80,.85,.90,.95])
fig,ax=plt.subplots()
for i,year in enumerate(d['years']):
    valid=np.isfinite(similarity[i])
    fractions=[np.count_nonzero(valid&(similarity[i]>=v))/valid.sum() for v in thresholds]
    ax.plot(thresholds,fractions,'o-',label=str(year))
ax.set(xlabel='Chosen cosine threshold',ylabel='Fraction of valid sampled pixels',ylim=(0,1),
       title='Threshold sensitivity / fixed 2025 Lagos reference')
ax.legend();plt.show()'''),
    md('''## 3. Query the same scalar field with SQL

The original 128 dimensions stay in the notebook extracts. The linked lab stores the derived scalar similarity field
as a small uncompressed Zarr cube. Python uses SQLite; the lab uses DuckDB-WASM and Zarrita. SQL selects cells after the
metric is calculated: it does not invent a semantic label or train the foundation model.'''),
    code('''meta,values=load_cube('tessera_lagos')
np.testing.assert_allclose(values,similarity,atol=1e-6,equal_nan=True)
con=sql_connection(meta,values)
rows=con.execute("""SELECT t, COUNT(*) AS selected, AVG(value) AS mean_similarity
 FROM cells WHERE value >= 0.85 GROUP BY t ORDER BY t""").fetchall()
print('Year index, selected count, selected mean:',rows)
con.close()
lab('tessera_lagos','cube')'''),
    md('''Use the time slider, change the SQL predicate to `value >= 0.9`, and switch between 2D, columns and the time cube.
The time cube's layer spacing is an index of the three sampled years; it is not proportional to elapsed years.
Column height represents similarity, never terrain height or flood depth.

## 4. Carry the meaning with the exported points

This notebook exports actual native pixel centers and retains query coordinates, version, snapshot, reference and method.
The lab exports query-grid centers and explicitly describes its sampling in the dataset metadata.
Open the result in [GeoLibre](https://web.geolibre.app/) or another GeoJSON viewer that supports local file import.
Use a [STAC Browser](https://radiantearth.github.io/stac-browser/) with a suitable catalog to discover independent imagery.
Compare dates and provenance before interpreting a visual match.'''),
    code('''result=export_points(d,similarity,'tessera-lagos-similarity.geojson',threshold=.9)
print('Exported',len(result['features']),'native-center points')
print('Reference:',result['method'])
print('A next-evidence question: do independently labeled surfaces explain these matches?')''')],SOURCES,
    'Try row 16, column 16 as the reference if valid; recalculate maps and threshold curves. Pass `reference=(2,16,16)` to the export helper so its metadata matches. The bundled lab retains its documented center reference; its equality check will correctly fail for your new derivative.',
    'High similarity supports retrieval within a chosen representation. A class label needs independent evidence. Changing the reference changes the selected set even when all calculations are correct.')

    lesson('19_tessera_pca','19 · PCA colors and a three-dimensional embedding space',45,
        'fit a shared PCA basis; quantify information loss; distinguish a geographic map from a feature-space visualization.',[
    md('''## 1. Why reduce 128 dimensions?

We can plot two or three coordinates, but our vectors have 128. Principal component analysis (PCA) chooses directions
with high variance after centering. Here we first normalize vectors so their direction, rather than magnitude, drives the display.
PCA colors are **false colors of learned features**, not a satellite RGB photograph or a classification.

Fit the PCA once on valid 2025 Lagos vectors. Apply that same mean, basis and color stretch to every year. Independently fitted
PCA maps can rotate or flip axes and change colors even when the underlying surface is unchanged.'''),
    code('''from tessera import load_tessera, unit_vectors, fit_pca, project, rgb_limits, rgb
d=load_tessera('lagos'); U=unit_vectors(d['embedding'])
model=fit_pca(U[-1],n=3)
scores=project(U,model)
limits=rgb_limits(scores[-1])  # one 2nd-to-98th percentile display stretch
colors=rgb(scores,limits)
print('Valid training vectors:',model['count'])
print('Explained variance per component:',np.round(model['explained'],4))
print('Total retained in this 3D display:',f"{model['explained'].sum():.1%}")
fig,axes=plt.subplots(1,3,figsize=(13,4),layout='constrained')
half=.000375/2
extent=[d['lon'][0]-half,d['lon'][-1]+half,d['lat'][-1]-half,d['lat'][0]+half]
for i,ax in enumerate(axes):
    ax.imshow(colors[i],extent=extent,origin='upper')
    ax.set(title=f'{d["years"][i]} / shared PCA + stretch',xlabel='Longitude',ylabel='Latitude')
    ax.set_aspect(1/np.cos(np.deg2rad(d['city']['center'][1])))
plt.show()'''),
    md('''Gray pixels have missing vectors. Each RGB channel is one stretched principal component. Saturated colors can hide
differences outside the display range. Similar colors only mean proximity in the three displayed components, which omit the rest.

## 2. Rotate the question: geography versus feature space

This 3D scatter places points by principal-component scores. **None of its axes is longitude, latitude, or altitude.**
We use the same colors as the geographic map to connect the views. The plotted sample is every fourth valid point for readability.'''),
    code('''valid=np.isfinite(scores[-1]).all(axis=-1)
points=scores[-1][valid][::4]; point_colors=colors[-1][valid][::4]
fig=plt.figure(figsize=(9,6));ax=fig.add_subplot(111,projection='3d')
ax.scatter(points[:,0],points[:,1],points[:,2],c=point_colors,s=9,alpha=.65)
ax.set(xlabel='PC1 score',ylabel='PC2 score',zlabel='PC3 score',
       title='Lagos 2025 / feature space, not geographic space')
ax.view_init(elev=24,azim=35);plt.show()'''),
    md('''## 3. Measure the information discarded

Reconstruct the normalized vectors using three components and compare with the originals. The residual norm measures
projection loss in this representation; it is not uncertainty in land cover or a physical measurement error.'''),
    code('''reconstructed=scores[-1]@model['components'].T+model['mean']
residual=np.linalg.norm(U[-1]-reconstructed,axis=-1)
print('Median reconstruction residual:',float(np.nanmedian(residual)))
fig,ax=plt.subplots();ax.hist(residual[np.isfinite(residual)],bins=35)
ax.set(xlabel='L2 reconstruction residual (unit-vector space)',ylabel='Sampled pixels',
       title='What the three-component display leaves out');plt.show()'''),
    md('''## 4. Make a small animation without video software

The following player cycles through annual embedding displays using the fixed basis and stretch. It is not a movie of events
between the sampled years. Read the year labels: the intervals are unequal, and no intermediate years are interpolated.
The static maps above provide the same information when animation is unavailable.'''),
    code('''from matplotlib.animation import FuncAnimation
fig,ax=plt.subplots(figsize=(5,5))
im=ax.imshow(colors[0],origin='upper');ax.set_axis_off()
def frame(i):
    im.set_data(colors[i]);ax.set_title(f'Lagos {d["years"][i]} | annual PCA display')
    return (im,)
animation=FuncAnimation(fig,frame,frames=len(d['years']),interval=1200,blit=False)
player=animation.to_jshtml(default_mode='once')
plt.close(fig)
display(HTML(player))''')],SOURCES,
    'Fit 2, 8 and 16 components and compare retained variance and reconstruction residuals. Then apply the Lagos model to Abidjan with the same color limits; explain why that is a transfer experiment.',
    'PCA optimizes variance in its training sample. More components retain more information, but a visually clear plot does not establish semantic accuracy or transferability.')

    lesson('20_tessera_clusters','20 · Clusters, transfer and the need for independent labels',45,
        'cluster embeddings; test stability without confusing label IDs; design a defensible validation study.',[
    md('''## 1. Group vectors without pretending to know their classes

Spherical k-means groups normalized vectors by direction. Choose `k=4` as an experiment, not a claim that there are four
land-cover types. We fit on valid 2025 Lagos pixels. Cluster IDs are arbitrary; neither the algorithm nor this lesson supplies
verified labels such as “wetland,” “informal settlement,” or “flood-vulnerable.”

**Predict:** could two runs find the same groups but assign them different ID numbers?'''),
    code('''from tessera import load_tessera, unit_vectors, spherical_kmeans, assign_clusters, adjusted_rand, scalar_map
d=load_tessera('lagos'); other=load_tessera('abidjan')
U=unit_vectors(d['embedding'][-1]); V=unit_vectors(other['embedding'][-1])
centers=spherical_kmeans(U,k=4,seed=7)
labels,distance=assign_clusters(U,centers)
other_labels,other_distance=assign_clusters(V,centers)
from matplotlib.colors import ListedColormap, BoundaryNorm
cluster_colors=ListedColormap(plt.get_cmap('tab10').colors[:4])
cluster_norm=BoundaryNorm(np.arange(-.5,4.5),4)
fig,axes=plt.subplots(1,2,figsize=(11,4.5),layout='constrained')
for ax,item,ids in [(axes[0],d,labels),(axes[1],other,other_labels)]:
    im=scalar_map(ax,item,np.ma.masked_less(ids,0),item['city']['title']+' / 2025',
                  cmap=cluster_colors,norm=cluster_norm)
fig.colorbar(im,ax=axes,ticks=range(4),label='Cluster ID (arbitrary, no semantic labels)')
plt.show()'''),
    md('''## 2. Measure stability with a label-invariant comparison

Adjusted Rand index compares pairs of points grouped together. It does not require matching cluster numbers.
One means the partitions agree; a value near zero is the chance-adjusted reference, and negative values are possible.
Agreement is a reproducibility diagnostic, not accuracy against reality.'''),
    code('''for seed in [7,19,41]:
    alternative=spherical_kmeans(U,k=4,seed=seed)
    alt_labels,_=assign_clusters(U,alternative)
    print('Seed',seed,'adjusted Rand agreement:',round(adjusted_rand(labels,alt_labels),4))
print('ID-renaming check:',adjusted_rand(labels,np.where(labels>=0,3-labels,-1)))'''),
    md('''## 3. Transfer asks a different question

Assigning Abidjan vectors to Lagos centers demonstrates transfer of a fixed partition. It does not validate the same
land-cover meanings in both places. Compare distances to the assigned centers; larger distances can motivate investigation
of distribution differences, but they are not calibrated out-of-distribution probabilities.'''),
    code('''fig,ax=plt.subplots()
for title,dist in [('Lagos training window',distance),('Abidjan transfer window',other_distance)]:
    ax.hist(dist[np.isfinite(dist)],bins=np.linspace(0,2,41),density=True,alpha=.55,label=title)
ax.set(xlabel='1 - cosine similarity to assigned center',ylabel='Density',title='Representation distance / 2025')
ax.legend();plt.show()
for title,dist in [('Lagos',distance),('Abidjan',other_distance)]:
    print(title,'median distance:',round(float(np.nanmedian(dist)),4))'''),
    md('''## 4. Design the study that these clusters cannot replace

For a coastal vegetation or impervious-surface question, obtain independent, dated reference labels. Use a shared class
definition with local expertise. Separate spatial blocks before training and tuning: neighboring pixels can share conditions
and make random train/test splits overly optimistic. Keep a city or year held out to test transfer explicitly.

This map proposes four geographic blocks. It does not claim a valid buffer distance; select separation using spatial
dependence and the intended use. No accuracy score is reported because this package contains no independent class labels.'''),
    code('''rows,cols=np.indices((64,64))
blocks=(rows>=32).astype(int)*2+(cols>=32).astype(int)
fig,ax=plt.subplots();im=scalar_map(ax,d,blocks,'Candidate geographic blocks / not validated classes',
                                  cmap=ListedColormap(plt.get_cmap('Set2').colors[:4]),norm=cluster_norm)
fig.colorbar(im,ax=ax,ticks=range(4),label='Proposed block ID');plt.show()
validation_plan={
 'target':'Independently defined coastal vegetation class',
 'labels_needed':'Dated field or expert interpretation, with uncertainty and permissions',
 'split':'Separated geographic blocks; untouched city/year transfer set',
 'checks':['Class confusion matrix','Per-class recall and precision','Calibration if probabilities are used'],
 'limitations':['Tiny convenience windows','No reference labels bundled','No social vulnerability inferred from imagery']}
print(json.dumps(validation_plan,indent=2))''')],SOURCES,
    'Repeat with k=3 and k=6. Which geographic boundaries persist? Write a label-collection plan that could distinguish an interesting cluster from a validated land-cover class.',
    'Cluster stability, geographical coherence, and predictive accuracy answer different questions. Never use the cluster IDs as ground truth for reporting model accuracy.')

    lesson('21_tessera_change','21 · Annual embedding differences and coastal evidence',45,
        'compare aligned annual vectors; check observation support; connect candidate changes to a cautious climate study.',[
    md('''## 1. Compare the same native pixel, using the same representation

For each sampled location, calculate `1 - cosine(x_2018, x_2025)`. The result lies between 0 and 2.
It measures an annual **representation difference**. It does not identify when a change occurred or its cause.
The notebook checks coordinate alignment and uses the same model version, variant and source snapshot for all years.

Potential explanations include surface change, observation availability, preprocessing, phenology and model behavior.
Three annual samples cannot establish a climate trend or attribute change to sea-level rise.'''),
    code('''from tessera import load_tessera, unit_vectors, scalar_map
d=load_tessera('lagos'); U=unit_vectors(d['embedding'])
paired=d['valid'][0]&d['valid'][-1]
delta=np.where(paired,np.clip(1-np.sum(U[0]*U[-1],axis=-1),0,2),np.nan)
print('Paired valid native pixels:',paired.sum(),'of',paired.size)
fig,ax=plt.subplots();im=scalar_map(ax,d,delta,'Lagos: 2018 to 2025 embedding difference',
                                  cmap='magma',vmin=0,vmax=2)
fig.colorbar(im,ax=ax,label='1 - cosine similarity (dimensionless)');plt.show()'''),
    md('''## 2. Put observation support beside the apparent change

Compare radar and optical counts before interpreting high scores. The dClimate run permits an embedding without radar
observations, provided its optical requirements are met. Counts can reveal a reason to investigate; they cannot isolate a cause.
We retain valid pixels in both years and never silently treat a missing vector as “no change.”'''),
    code('''radar=d['s1_asc_obs_count'].astype(np.int32)+d['s1_desc_obs_count'].astype(np.int32)
fig,axes=plt.subplots(1,3,figsize=(13,4),layout='constrained')
vmax=max(1,int(radar.max()))
for i,ax in enumerate(axes):
    im=scalar_map(ax,d,radar[i],f'{d["years"][i]} radar support',cmap='cividis',vmin=0,vmax=vmax)
fig.colorbar(im,ax=axes,label='Usable ascending + descending radar observations');plt.show()
optical_min=np.minimum(d['s2_obs_count'][0],d['s2_obs_count'][-1])
for minimum in [15,30,60]:
    selected=paired&(optical_min>=minimum)&(radar[0]>0)&(radar[-1]>0)
    print('Both years: optical >=',minimum,'and radar > 0; n =',selected.sum(),
          'median difference =',round(float(np.median(delta[selected])),4) if selected.any() else 'no supported pixels')'''),
    md('''## 3. Watch individual locations without inventing observations between years

Here the three annual vectors at each location are compared with that location's 2018 vector. Symbols show the sampled years;
there are no interpolated observations. Compare with the fixed-reference maps from lesson 18: those answer a different question.'''),
    code('''fig,ax=plt.subplots()
for row,col in [(16,16),(32,32),(48,48)]:
    series=np.clip(1-np.sum(U[:,row,col]*U[0,row,col],axis=-1),0,2)
    ax.scatter(d['years'],series,label=f'row {row}, col {col}')
ax.set(xticks=d['years'],xlabel='Year of annual embedding',ylabel='1 - cosine to this pixel in 2018',
       title='Three sampled annual representations / no event timing inferred',ylim=(0,2))
ax.legend();plt.show()'''),
    md('''## 4. Build a coastal research question with independent evidence

| Candidate question | Embeddings can help with | Evidence still needed |
|---|---|---|
| Is coastal vegetation changing? | Candidate locations and sampling strata | Dated imagery, independent labels, field ecology |
| Is new construction exposed to flooding? | Candidate surface-pattern changes | Validated building footprints, terrain and datum, tides, drainage, defenses |
| Is water becoming unsafe? | Identifying places for follow-up imagery | Calibrated optical retrievals and water samples; embeddings do not measure pathogens |
| Who bears the burden? | Environmental context | Community knowledge and appropriate social data; no inferred vulnerability from appearance |

The [AR6 port-city studio](https://jltobias.github.io/JupyterLite-zarr-sql-views/book/sea-level.html) supplies conditional regional
sea-level projections. Its one-degree grid support differs enormously from these sampled 10 m pixels. Do not subtract an
embedding score from an AR6 projection or use either as an inundation map. The DE Africa lesson illustrates a separate,
observed water product at Lake Ngami; it is not co-located validation for these port windows.

Use the [C3S Atlas](https://atlas.climate.copernicus.eu/) for regional climate context and a STAC catalog for dated imagery.
Record spatial support, time, provenance, license and the proposed causal link for each layer.'''),
    code('''evidence={
 'question':'Which sampled coastal locations merit independent surface-change investigation?',
 'city':d['city']['title'],'years':[int(d['years'][0]),int(d['years'][-1])],
 'metric':'1 - cosine, same native pixel, full 128-dimensional annual v1.1-dclimate vectors',
 'paired_pixels':int(paired.sum()),'median_difference':float(np.nanmedian(delta)),
 'source_snapshot':d['provenance']['snapshot_id'],
 'next_step':'Inspect dated independent imagery and observation counts before labeling any change',
 'not_established':['Climate attribution','Flood extent','Event dates','Water safety','Social vulnerability']}
print(json.dumps(evidence,indent=2))''')],SOURCES,
    'Repeat for Abidjan and for 2018–2021 versus 2021–2025. Keep map limits fixed. Identify what additional data would distinguish physical surface change from changing observation support.',
    'A large vector difference is a candidate for investigation. It becomes a defensible environmental claim only with independent validation and an explanation consistent with temporal and spatial support.')
