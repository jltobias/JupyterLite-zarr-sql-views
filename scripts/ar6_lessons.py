"""Authoring source for the four port-city lessons, called by make_notebooks.py."""

def add_lessons(lesson,md,code):
    sources=[
        '[Fox-Kemper et al. (2021), IPCC AR6 WG1 Chapter 9: Ocean, Cryosphere and Sea Level Change](https://doi.org/10.1017/9781009157896.011).',
        '[Kopp et al. (2023), FACTS v1.0, Geoscientific Model Development 16, 7461–7489](https://doi.org/10.5194/gmd-16-7461-2023).',
        '[Garner et al. (2021), IPCC AR6 Sea Level Projections, version 20210809](https://doi.org/10.5281/zenodo.5914709), accessed 2026-10-13. Modified extracts under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).',
        '[Rutgers-ESSP source guide and workflow FAQ](https://github.com/Rutgers-ESSP/IPCC-AR6-Sea-Level-Projections/tree/8ee75128d8f6d9a8ba9825f47c92d11955d0651e).',
        '[Exact source objects, checksums, transformations and location distances](https://jltobias.github.io/JupyterLite-zarr-sql-views/data/ar6-provenance.json).',
        'We thank the projection authors for developing and making the sea-level rise projections available, multiple funding agencies for supporting the development of the projections, and the NASA Sea Level Change Team for developing and hosting the IPCC AR6 Sea Level Projection Tool.'
    ]
    intro=md('''> **Data identity:** real modeled projections, not observations. AR6 v20210809; workflow `wf_1e`; 20,000 Monte Carlo samples at each decade from 2020 to 2100. Source values are millimetres of relative sea-level change from the 1995–2014 reference period; plots convert them to metres. Background land motion is included.

> **Interpretation:** a workflow distribution is not the assessed IPCC probability box (p-box). The source FAQ says `wf_1e` does not preserve time correlations: do not calculate rates, sample trajectories, or first-crossing dates. The exercise compares distributions at specified years. These data alone cannot map inundation or rank port vulnerability.

![From archive chunks to projection distributions, with flood-risk evidence kept separate](assets/ar6-workflow.svg)
''')
    setup=code("from ar6 import load_ar6, coverage_map, coastline, gauge_summary, summary_sql, export_summary\np, years, gauge_m, grid_m = load_ar6()\nprint('Samples: scenario, sample, year, unique gauge =', gauge_m.shape)\nprint('Nearest defined grid samples: sample, year, city =', grid_m.shape)")

    lesson('13_ar6_archive','13 · Open the AR6 archive without downloading the world',35,
        'Inspect actual metadata, estimate chunk costs, and distinguish samples, scenarios, workflows, and locations.',[
        intro,
        md('''## 1. Ask a small question first

We will study **Abidjan, Lagos, Bangkok, Ho Chi Minh City, and Manila**. Begin with a particular location, year, scenario, and statistic. The source's 38.42 GB gauge archive and 1.65 TB gridded archive describe many stores, not a single download needed for this lesson.

`gs://bucket/path` becomes `https://storage.googleapis.com/bucket/path` for public HTTP access. A readable URL in desktop Python still needs CORS permission for browser fetch. No Google account is needed for the bundled extracts.'''),
        setup,
        code("for source in p['stores']:\n    m=source['metadata']; a=m['sea_level_change/.zarray']\n    print(source['partition'], source['scenario'])\n    print(source['url'])\n    print('Axes:',m['sea_level_change/.zattrs']['_ARRAY_DIMENSIONS'])\n    print('Shape:',a['shape'],'chunks:',a['chunks'],'codec:',a['compressor'])\n    print('Decoded chunk MiB:',round(np.prod(a['chunks'])*np.dtype(a['dtype']).itemsize/1024**2,2))"),
        md('''## 2. Calculate the cost before reading values

One gauge chunk spans **5,000 samples × 5 years × 1,012 locations**. A point selection does not make its compressed chunk smaller. The gridded store instead has `(sample, year, latitude, longitude)` axes, with **30 × 30** spatial chunks. Inspect axes: do not substitute a sample axis for time.

Selecting all 20,000 samples and nine years touches eight chunks per gauge store. The five small gridded windows intersect four spatial tiles, each with eight sample/year chunks. These chunks were downloaded once during preparation. Students read only the derivative files.'''),
        code("objects=p['source_objects']\nchunks=[r for r in objects if '/sea_level_change/' in r['url']]\nprint('Value chunks actually fetched:',len(chunks))\nprint('One-time source transfer MB:',round(p['unique_source_bytes']/1e6,1))\nprint('Bundled statistical artifacts MB:',round(sum(a['bytes'] for a in p['artifacts'].values())/1e6,2))\nprint('Source data retained:',p['samples'],'samples per selected location/year')"),
        md('''## 3. Trace a byte to a source

The provenance records source URLs, object generation IDs where supplied, retrieval timestamps, SHA-256 hashes, coordinate choices, and transformations. A full refresh is an **instructor/desktop** operation using `python scripts/prepare_ar6.py --download`. It limits each decoded chunk to 128 MiB and new downloads to 2 GiB per run, and reuses verified cached objects. Normal builds and notebooks never fetch that archive.

The browser-facing cubes contain per-year medians, converted to uncompressed Zarr v2. The NPZ files preserve all samples for the selected locations. Reducing samples to quantiles and selecting locations are stated modifications under the data license.'''),
        code("record=chunks[0]\nprint(json.dumps(record,indent=2))\nprint('A source variable:',p['stores'][0]['metadata']['sea_level_change/.zattrs'])"),
        md('''## 4. Optional live metadata experiment

This requests only one `.zmetadata` file (about 8 KB), never a value chunk. Leave `LIVE=False` for the recorded, reproducible lesson. Public Google Storage responses inspected during preparation did not provide an `Access-Control-Allow-Origin` header for the course origin. A browser failure therefore does not establish that a store is absent. The code reports the failure explicitly; it never substitutes fabricated values.'''),
        code("LIVE=False\nurl=p['stores'][0]['url']+'/.zmetadata'\nif LIVE:\n    try:\n        if __import__('sys').platform=='emscripten':\n            from pyodide.http import pyfetch\n            response=await pyfetch(url)\n            if not response.ok: raise RuntimeError(f'HTTP {response.status}')\n            live=await response.json()\n        else:\n            import urllib.request\n            with urllib.request.urlopen(url,timeout=30) as response: live=json.load(response)\n        print('LIVE metadata axes:',live['metadata']['sea_level_change/.zattrs']['_ARRAY_DIMENSIONS'])\n    except Exception as exc:\n        print('LIVE METADATA UNAVAILABLE:',type(exc).__name__,str(exc))\n        print('The recorded metadata above remains usable; no live sample values were requested.')\nelse:\n    print('RECORDED METADATA MODE: no archive network requests.')"),
        md('''## 5. Find the question's proper dataset

| Question | Suitable evidence |
|---|---|
| Distribution at one location/year under one workflow | The supplied Monte Carlo samples |
| Assessed IPCC range across workflows | Authors' confidence/p-box products or [NASA's projection tool](https://sealevel.nasa.gov/ipcc-ar6-sea-level-projection-tool) |
| Rate or first-crossing date | Appropriate time-correlated workflow or supplied milestone products, not `wf_1e` paths |
| Which port assets flood? | Datum-aligned elevation, tides/surge/waves, hydraulic connectivity, defenses and asset exposure |

The free public **totals** used here include background land motion. No requester-pays bucket or no-VLM product is used.''')],sources,
        'Estimate chunks needed for one gauge in 2050 versus one gauge at all nine years. Explain why SQL filtering after loading does not change this cost.',
        'With all samples, 2050 touches four chunks; nine years touch eight. Both include all gauge locations within each fetched chunk. Source selection precedes decoding; SQL acts on the extracted table.')

    lesson('14_ar6_port_cities','14 · Five port cities, four tide-gauge proxies',50,
        'Audit city-to-gauge distances, compare scenario distributions, and preserve uncertainty in a map narrative.',[
        intro,setup,
        md('''## 1. Locate the evidence before plotting a projection

City reference points are rounded geographic anchors, not surveyed ports or administrative boundaries. The preparation script finds the nearest available gauge **projection location**, using great-circle distance; it does not retrieve an observed tide-gauge time series.

Both Abidjan and Lagos map to **Takoradi, Ghana** in this archive. Displaying that series twice does not provide two independent local projections. Do not label it “measured Lagos sea level.” Bangkok uses Fort Phrachula Chomklao, Ho Chi Minh City uses Vung Tau, and Manila uses the Manila site. The next lesson uses grid windows to expose the proxy problem.'''),
        code("for c in p['cities']:\n    g=p['gauges'][c['gauge_column']]\n    print(f\"{c['name']:18} -> {g['name']:24} ID {g['id']:4} | {c['gauge_distance_km']:.1f} km\")\ncoverage_map(p);plt.show()"),
        md('''## 2. Read scenario spread and sample spread separately

Choose SSP1-2.6 (lower emissions) and SSP5-8.5 (higher emissions) **conditional scenarios**, not assigned likelihoods. At each decade compute the 17th, 50th, and 83rd percentiles of all 20,000 samples. The shaded interval is this workflow's central 66% sample interval; it is not a confidence interval on the median and not the IPCC assessed likely p-box range.

Lines connect per-year medians as visual guides. They do not track any one Monte Carlo realization. All panels share the same vertical scale; African panels deliberately reveal the shared gauge.'''),
        code("fig,axes=plt.subplots(2,3,figsize=(14,8),sharex=True,sharey=True,constrained_layout=True)\nq=np.quantile(gauge_m,[.17,.5,.83],axis=1,method='linear')\nfor ax,c in zip(axes.flat,p['cities']):\n    g=c['gauge_column']\n    for s,(label,color) in enumerate([('SSP1-2.6','#237c97'),('SSP5-8.5','#b34b3c')]):\n        ax.fill_between(years,q[0,s,:,g],q[2,s,:,g],color=color,alpha=.16)\n        ax.plot(years,q[1,s,:,g],color=color,label=label)\n    ax.set(title=c['name']+' — '+p['gauges'][g]['name'].replace('_',' '),xlabel='Year',ylabel='Relative sea-level change (m)')\n    ax.grid(alpha=.2);ax.legend(fontsize=8)\naxes.flat[-1].axis('off')\nfig.suptitle('wf_1e gauge proxies · median and p17–p83 · relative to 1995–2014',fontsize=14)\nplt.show()"),
        md('''## 3. Verify one statistic independently

The source is in millimetres. Conversion to metres divides by 1,000; do it exactly once. Each year is a distribution of possible levels. Inspect an empirical cumulative distribution at 2100 for the Manila gauge.'''),
        code("city=p['cities'][-1]; g=city['gauge_column']; t=int(np.where(years==2100)[0][0])\nfig,ax=plt.subplots()\nfor s,label in enumerate(p['gauge_scenarios']):\n    v=np.sort(gauge_m[s,:,t,g])\n    ax.plot(v,np.arange(1,len(v)+1)/len(v),label=label)\nax.set(xlabel='Relative sea-level change (m; 1995–2014 baseline)',ylabel='Empirical cumulative fraction',title='Manila gauge · 2100 · wf_1e')\nax.legend();plt.show()\nassert np.isclose(np.median(gauge_m[1,:,t,g]),q[1,1,t,g])"),
        md('''## 4. Turn the distributions into a SQL view

The 72 rows below represent **four unique gauges × two scenarios × nine years**. City names belong in a separate geographic mapping. SQL in this notebook is SQLite; the map lab uses DuckDB-WASM. Both operate after bounded source extraction.'''),
        code("summary=gauge_summary(p,years,gauge_m)\ncon=summary_sql(summary)\nprint('Unique rows:',con.execute('SELECT COUNT(*) FROM projections').fetchone()[0])\nfor row in con.execute(\"SELECT gauge_name, scenario, ROUND(p50_m,3), ROUND(p83_m-p17_m,3) FROM projections WHERE year=2100 ORDER BY gauge_id,scenario\"):\n    print(row)\ncon.close()"),
        md('''## 5. Ask what would change a port decision

These totals already include an AR6 background land-motion component. Adding a published subsidence rate directly could double-count part of that term. Local, time-varying subsidence, groundwater extraction, estuarine water levels, storm tides, wave setup, drainage and protection require additional evidence and a consistent reference datum. A higher projected level alone does not establish greater population vulnerability or greater port losses.''')],sources,
        'Compare the scenario medians and within-scenario p17–p83 widths in 2050 and 2100. Explain why Abidjan and Lagos have identical proxy curves.',
        'Their shared Takoradi location creates identical gauge results. Differences between scenario medians are conditional contrasts, not probabilities or paired-sample treatment effects. Validate any local interpretation against closer spatial and observational evidence.')

    lesson('15_ar6_grid_maps','15 · Regional grids, 3D maps, and sea-level time cubes',50,
        'Map actual gridded projections, compare spatial support with gauges, and interpret the vertical axis correctly.',[
        intro,setup,
        md('''## 1. Change spatial support explicitly

For each city, we extracted a **5 × 5 one-degree window**, with no interpolation, for SSP5-8.5 / `wf_1e`. Each map value is the median of all 20,000 samples at one location and year. Missing locations remain NaN.

The authors explain that some projections are defined over apparent land because of differing model land/ocean masks. No additional coastline mask is applied here. Coloured cells indicate regional projection locations and their display footprint; they do not delineate water, flooded land, or a one-degree asset polygon. Natural Earth outlines are only geographic orientation.'''),
        code("for c in p['cities']:\n    print(c['name'],c['grid'])\nfig,axes=plt.subplots(2,3,figsize=(14,8),constrained_layout=True)\nfor ax,c in zip(axes.flat,p['cities']):\n    meta,values=load_cube('ar6_'+c['id'])\n    image=ax.pcolormesh(meta['lon'],meta['lat'],values[-1],vmin=0,vmax=2,cmap='viridis',shading='nearest')\n    coastline(ax); ax.scatter(c['lon'],c['lat'],marker='*',s=100,c='tomato',edgecolors='white',zorder=4)\n    ax.set(xlim=(min(meta['lon'])-.5,max(meta['lon'])+.5),ylim=(min(meta['lat'])-.5,max(meta['lat'])+.5),title=c['name'])\n    ax.set_aspect(1/np.cos(np.radians(c['lat'])))\naxes.flat[-1].axis('off')\nfig.colorbar(image,ax=list(axes.flat[:5]),label='Median relative sea-level change (m; 1995–2014 baseline)',extend='both',shrink=.8)\nfig.suptitle('2100 · SSP5-8.5 · wf_1e · 1-degree projection locations (not inundation)')\nplt.show()"),
        md('''## 2. Compare the nearest defined grid location and the proxy gauge

The nearest defined grid location is selected within the stated window using great-circle distance, requiring complete samples at all nine years. It is not automatically an offshore or hydraulically connected location. The scatter chart uses the **same workflow, scenario and year** for both products. A difference can reflect spatial support and model background processes; it cannot isolate local subsidence.'''),
        code("t=-1\nfig,ax=plt.subplots()\nfor i,c in enumerate(p['cities']):\n    gm=np.median(gauge_m[1,:,t,c['gauge_column']]); xm=np.median(grid_m[:,t,i])\n    ax.scatter(gm,xm,s=65);ax.annotate(c['name'],(gm,xm),xytext=(5,5),textcoords='offset points',fontsize=9)\nlimits=[min(ax.get_xlim()[0],ax.get_ylim()[0]),max(ax.get_xlim()[1],ax.get_ylim()[1])]\nax.plot(limits,limits,'--',c='grey',label='Equal medians')\nax.set(xlabel='Nearest gauge median (m)',ylabel='Nearest defined grid median (m)',title='2100 · SSP5-8.5 · wf_1e · 1995–2014 baseline')\nax.legend();plt.show()"),
        md('''## 3. Use SQL to select regional cell-years

Change the city and threshold. `t=8` means 2100; this is an index, not a year literal. The 3D lab reads the same real Zarr median values and identifies them as **PROJECTIONS**. The default includes every finite value, including a negative value if one exists.'''),
        code("city_id='lagos'\nmeta,values=load_cube('ar6_'+city_id)\ncon=sql_connection(meta,values)\nrows=list(con.execute('SELECT t, COUNT(value), MIN(value), MAX(value) FROM cells GROUP BY t ORDER BY t'))\nfor row in rows: print(meta['times'][row[0]],*row[1:])\ncon.close()\nlab('ar6_'+city_id,'columns')"),
        md('''## 4. Rotate a time cube, then return to a 2D map

Use the lab's dataset menu for all five cities. In **3D map**, height is a visual scaling of median sea-level change, not terrain or water depth. In **time cube**, vertical position is decade index. **Value surface** is another scaled-value view, not a surveyed coastal scene. The animation steps between available decades; it does not simulate floods or storm dynamics.

Click one location to inspect its median sequence. Per-year medians form a summary curve, not a time-correlated realization. Separate city datasets have their own fixed colour ranges; use the common scale in the Python maps for cross-city magnitude comparisons.'''),
        code("lab('ar6_manila','cube')"),
        md('''## 5. Export for GeoLibre

Export the projection locations as GeoJSON points. Open the file in [GeoLibre Web](https://web.geolibre.app/) and style by value, with a year filter. Retain workflow, scenario, baseline and provenance. The exported geometry is a point sample; making a polygon or extruding it does not create an inundation model.

For African context, revisit [Digital Earth Africa's STAC catalog](https://explorer.digitalearth.africa/stac) and investigate coastal water observations. A WOfS frequency is not a terrain height, and its time support and observation masks differ from AR6 projections. Treat an overlay as a question to investigate, not validation of future flood extent.'''),
        code("print('Exported finite nonnegative cell-years:',export_geojson(meta,values,'ar6-lagos-grid.geojson',threshold=0))")],sources+['[Natural Earth boundary data, public domain](https://www.naturalearthdata.com/about/terms-of-use/).'],
        'Switch from Lagos to Abidjan and inspect the 2050/2100 maps. Which differences come from spatial support, scenario, statistic, or visual scale?',
        'Only spatial support and time change within these SSP5-8.5 median maps. Compare values on a shared colour scale and retain each location’s coordinates. Neither the source grid nor the extruded view resolves a port flood boundary.')

    lesson('16_ar6_uncertainty','16 · Threshold questions without false flood probabilities',45,
        'Calculate fixed-year conditional exceedance, export a documented SQL result, and design a port evidence study.',[
        intro,setup,
        md('''## 1. Define the event precisely

“Relative sea-level change exceeds 0.5 m in 2100 at this projection location, conditional on SSP5-8.5 and `wf_1e`” is answerable here. “Lagos port will flood with probability X” is not. The threshold is relative to the **1995–2014 mean sea-level baseline**, not the elevation of a building, quay, road, or levee.

The fraction of finite samples above a threshold is an empirical estimate within this one workflow. It omits structural uncertainty across workflows and does not assign probabilities to emissions scenarios. Do not label it the overall probability of sea-level rise or of climate harm.'''),
        code("year=2100; threshold_m=.5\nt=int(np.where(years==year)[0][0])\nfor c in p['cities']:\n    g=c['gauge_column']\n    fractions=[]\n    for s in range(2):\n        v=gauge_m[s,:,t,g];valid=np.isfinite(v)\n        fractions.append(float(np.count_nonzero(v[valid]>threshold_m)/valid.sum()))\n    print(c['name'],p['gauges'][g]['name'],dict(zip(p['gauge_scenarios'],fractions)))"),
        md('''## 2. Inspect threshold sensitivity at grid locations

Use the five nearest defined gridded locations for a second view. The curve is an exceedance fraction at a **fixed year**, not a survival curve through time. A threshold sweep communicates more than one chosen threshold. At large thresholds the empirical tail has fewer samples; apparent numerical precision does not resolve structural model uncertainty.'''),
        code("thresholds=np.linspace(0,2,101)\nfig,ax=plt.subplots()\nfor i,c in enumerate(p['cities']):\n    v=grid_m[:,t,i]\n    fraction=np.array([np.mean(v>h) for h in thresholds])\n    assert np.all(np.diff(fraction)<=0)\n    ax.plot(thresholds,fraction,label=c['name'])\nax.set(xlabel='Relative sea-level-change threshold (m; 1995–2014 baseline)',ylabel='Fraction of samples exceeding threshold',ylim=(0,1),title=f'{year} · nearest defined grid locations · SSP5-8.5 · wf_1e')\nax.legend();plt.show()"),
        md('''## 3. Export a small, auditable selection

Summarise unique gauge locations before joining city labels. The query selects 2100 SSP5-8.5 records whose **median**, not every sample, exceeds 0.5 m. Every output point retains quantiles, units, baseline, workflow, scenario, data version, sample count and a link to exact provenance.'''),
        code("summary=gauge_summary(p,years,gauge_m)\ncon=summary_sql(summary)\nids={r[0] for r in con.execute(\"SELECT gauge_id FROM projections WHERE year=2100 AND scenario='ssp585' AND p50_m>0.5\")}\nselected=[r for r in summary if r['gauge_id'] in ids and r['year']==2100 and r['scenario']=='ssp585']\nprint('Unique gauges exported:',export_summary(selected))\ncon.close()\nprint('Download ar6-projections.geojson from the file browser; retain its attribution.')"),
        md('''## 4. Avoid a tempting but invalid calculation

Do **not** subtract consecutive `wf_1e` samples to estimate rates, identify each sample's first threshold crossing, or use the same sample number as a paired counterfactual across scenarios. This workflow's time correlations are not valid for those tasks. Use the authors' appropriately constructed rate or milestone products, following their documentation. Connecting medians in a plot is a display device; it does not fix that limitation.

## 5. Design a five-city evidence clinic

Divide into teams for Abidjan, Lagos, Bangkok, Ho Chi Minh City and Manila. Each team should document:

| Evidence needed | Why it matters | A test before using it |
|---|---|---|
| Port/transport asset geometry and critical services | Establishes exposure, not assumed from a city point | Verify coordinates, date, ownership and reuse terms |
| Local elevation/bathymetry and vertical datum | Links land and water heights | Reconcile datum, resolution, error and survey epoch |
| Tide, storm-surge, wave and river levels | Describes coastal and compound flood drivers | Check time support, joint events and hydraulic connectivity |
| InSAR/GNSS and local subsidence interpretation | Evaluates changing ground levels | Resolve overlap with AR6 background land motion before combining |
| Defenses, drainage and maintenance | Changes the pathway from hazard to impact | Validate crest levels, operations and plausible failure assumptions |
| Population, livelihoods and community knowledge | Supports an equitable vulnerability assessment | Protect privacy; validate representativeness and local relevance |

Use [NASA's IPCC tool](https://sealevel.nasa.gov/ipcc-ar6-sea-level-projection-tool) to inspect assessed products. Use STAC/browser GIS to discover additional Earth observation evidence. Check each source's license; no proprietary port or asset data is bundled here.

**Submission:** one reproducible figure, one source table, the selected GeoJSON, and a short statement separating the modeled hazard from exposure, vulnerability and potential impacts. Cite the three required AR6 works listed below.''')],sources,
        'Repeat the fixed-year threshold question for 2050 and 2100, then write a sentence that avoids implying a first-crossing time or flood probability.',
        'Report each year’s conditional sample fraction separately, with scenario, workflow, location and baseline. A change between these two fractions does not identify individual trajectories or a time-to-flood distribution.')
