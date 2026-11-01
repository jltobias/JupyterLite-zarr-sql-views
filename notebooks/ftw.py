"""FTW classroom helpers: NumPy, Matplotlib and standard-library SQLite only."""
from pathlib import Path
import json
import sqlite3
import numpy as np


def load_ftw(region='senegal', data_dir=Path('data')):
    data_dir=Path(data_dir)
    p=json.loads((data_dir/'ftw-provenance.json').read_text(encoding='utf-8'))
    if region not in {r['id'] for r in p['regions']}:
        raise ValueError('Choose senegal or kenya')
    with np.load(data_dir/f'ftw_{region}_probabilities.npz',allow_pickle=False) as z:
        arrays={k:z[k] for k in z.files}
    fields=json.loads((data_dir/f'ftw_{region}_fields.geojson').read_text(encoding='utf-8'))
    return dict(**arrays,fields=fields,provenance=p,years=p['years'],bands=p['bands'],
                region=next(r for r in p['regions'] if r['id']==region))


def raster_map(ax,d,values,title,cmap='viridis',vmin=0,vmax=1):
    from matplotlib.ticker import MaxNLocator
    image=ax.pcolormesh(d['lon'],d['lat'],values,shading='nearest',cmap=cmap,vmin=vmin,vmax=vmax)
    west,south,east,north=d['region']['bounds']
    ax.set(xlim=(west,east),ylim=(south,north),xlabel='Longitude',ylabel='Latitude',title=title)
    ax.set_aspect(1/np.cos(np.deg2rad(np.mean(d['lat']))))
    ax.ticklabel_format(useOffset=False,style='plain')
    ax.xaxis.set_major_locator(MaxNLocator(nbins=3))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=4))
    return image


def draw_fields(ax,d,year=2025,min_confidence=None,color='black'):
    """Draw all rings, including holes, as outlines; display extent clips the view only."""
    count=0
    for f in d['fields']['features']:
        p=f['properties']; confidence=p['confidence']
        if p['year']!=year: continue
        if min_confidence is not None and (confidence is None or confidence<min_confidence): continue
        g=f['geometry']; polygons=[g['coordinates']] if g['type']=='Polygon' else g['coordinates']
        for poly in polygons:
            for ring in poly:
                xy=np.asarray(ring); ax.plot(xy[:,0],xy[:,1],color=color,lw=.65)
        count+=1
    return count


def field_connection(d):
    con=sqlite3.connect(':memory:')
    con.execute('CREATE TABLE fields(id TEXT, year INTEGER, area_m2 REAL, perimeter_m REAL, confidence REAL, crosses_window_edge INTEGER)')
    con.executemany('INSERT INTO fields VALUES(?,?,?,?,?,?)',
        [(p['id'],p['year'],p['metrics:area'],p['metrics:perimeter'],p['confidence'],int(p['crosses_window_edge']))
         for f in d['fields']['features'] for p in [f['properties']]])
    return con


def paired_difference(probability,band=1):
    """A fixed common-support mask prevents missing values becoming false change."""
    a,b=np.asarray(probability)[:,band]
    valid=np.isfinite(a)&np.isfinite(b)
    return np.where(valid,b-a,np.nan),valid


def export_fields(d,path,year=2025,min_confidence=69):
    if year not in d['years'] or not 0<=min_confidence<=100:
        raise ValueError('Use a supplied year and a confidence threshold from 0 to 100')
    obj={k:v for k,v in d['fields'].items() if k!='features'}
    obj['selection']=dict(year=year,min_confidence=min_confidence,missing_confidence='excluded')
    obj['features']=[f for f in d['fields']['features'] if f['properties']['year']==year and
                     f['properties']['confidence'] is not None and f['properties']['confidence']>=min_confidence]
    obj['provenance_url']='https://jltobias.github.io/JupyterLite-zarr-sql-views/data/ftw-provenance.json'
    Path(path).write_text(json.dumps(obj,allow_nan=False),encoding='utf-8')
    return len(obj['features'])
