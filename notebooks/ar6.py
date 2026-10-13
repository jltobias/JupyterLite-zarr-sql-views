"""AR6 teaching helpers: small local files, NumPy and Python standard library only."""
from pathlib import Path
import csv
import json
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

DATA=Path('data')
SITE='https://jltobias.github.io/JupyterLite-zarr-sql-views'

def load_ar6():
    provenance=json.loads((DATA/'ar6-provenance.json').read_text(encoding='utf-8'))
    with np.load(DATA/'ar6-gauge-samples.npz',allow_pickle=False) as archive:
        # float64 before unit conversion gives the same quantiles across runtimes.
        gauges=archive['sea_level_change_mm'].astype('float64')/1000
        years=archive['years']
    with np.load(DATA/'ar6-grid-city-samples.npz',allow_pickle=False) as archive:
        grid=archive['sea_level_change_mm'].astype('float64')/1000
    return provenance,years,gauges,grid

def coastline(ax):
    """Generalized Natural Earth country outlines: orientation, not port geometry."""
    boundaries=json.loads((DATA/'countries.geojson').read_text(encoding='utf-8'))
    lines=[]
    for f in boundaries['features']:
        g=f['geometry']
        polygons=[g['coordinates']] if g['type']=='Polygon' else g['coordinates']
        for polygon in polygons:
            lines.extend(polygon)
    ax.add_collection(LineCollection(lines,colors='#667c83',linewidths=.65,zorder=1))
    ax.set(xlabel='Longitude (degrees east)',ylabel='Latitude (degrees north)')

def coverage_map(p):
    fig,axes=plt.subplots(1,2,figsize=(13,5),constrained_layout=True)
    for ax,region,limits in zip(axes,[[0,1],[2,3,4]],[(-7,6,2,10),(97,124,7,18)]):
        coastline(ax)
        for i in region:
            c=p['cities'][i];g=p['gauges'][c['gauge_column']]
            ax.plot([c['lon'],g['lon']],[c['lat'],g['lat']],':',color='#b56b32')
            ax.scatter(c['lon'],c['lat'],marker='*',s=130,color='#207b91',zorder=3)
            ax.scatter(g['lon'],g['lat'],marker='^',s=45,color='#b56b32',zorder=3)
            ax.annotate(c['name']+'\n'+str(round(c['gauge_distance_km']))+' km to gauge',
                        (c['lon'],c['lat']),xytext=(4,7),textcoords='offset points',fontsize=8)
        ax.set(xlim=limits[:2],ylim=limits[2:])
        ax.set_aspect(1/np.cos(np.radians(np.mean(limits[2:]))))
    axes[0].set_title('West Africa: one shared proxy gauge')
    axes[1].set_title('Southeast Asia: coastal proxy locations')
    fig.suptitle('Stars: city references · triangles: nearest available AR6 gauge projections')
    return fig

def gauge_summary(p,years,samples):
    """One row per unique gauge/scenario/year, never count a shared proxy twice."""
    qs=np.quantile(samples,[.17,.5,.83],axis=1,method='linear')
    rows=[]
    for s,scenario in enumerate(p['gauge_scenarios']):
        for t,year in enumerate(years):
            for g,gauge in enumerate(p['gauges']):
                rows.append({'gauge_id':gauge['id'],'gauge_name':gauge['name'],'scenario':scenario,
                    'year':int(year),'lon':gauge['lon'],'lat':gauge['lat'],
                    'p17_m':float(qs[0,s,t,g]),'p50_m':float(qs[1,s,t,g]),
                    'p83_m':float(qs[2,s,t,g]),'n':samples.shape[1],
                    'workflow':p['workflow'],'baseline':p['baseline'],'version':p['version']})
    return rows

def summary_sql(rows):
    con=sqlite3.connect(':memory:')
    con.execute('CREATE TABLE projections (gauge_id INTEGER, gauge_name TEXT, scenario TEXT, year INTEGER, lon REAL, lat REAL, p17_m REAL, p50_m REAL, p83_m REAL, n INTEGER, workflow TEXT, baseline TEXT, version TEXT)')
    keys=['gauge_id','gauge_name','scenario','year','lon','lat','p17_m','p50_m','p83_m','n','workflow','baseline','version']
    con.executemany('INSERT INTO projections VALUES ('+','.join('?' for k in keys)+')',([r[k] for k in keys] for r in rows))
    return con

def export_summary(rows,path='ar6-projections.geojson'):
    obj={'type':'FeatureCollection','license':'CC-BY-4.0','license_url':'https://creativecommons.org/licenses/by/4.0/',
        'source':'Garner et al. (2021), IPCC AR6 Sea Level Projections v20210809, https://doi.org/10.5281/zenodo.5914709',
        'provenance_url':SITE+'/data/ar6-provenance.json',
        'description':'Single-workflow relative sea-level projection quantiles; not IPCC p-boxes or flood extents. Background land motion included.',
        'features':[{'type':'Feature','geometry':{'type':'Point','coordinates':[r['lon'],r['lat']]},
                     'properties':dict(r,kind='projected',units='m')} for r in rows]}
    Path(path).write_text(json.dumps(obj,indent=2,allow_nan=False),encoding='utf-8')
    return len(rows)
