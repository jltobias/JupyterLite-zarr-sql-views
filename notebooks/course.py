"""Browser-friendly course helpers. Only NumPy, Matplotlib and Python's standard library.

The narrow Zarr reader intentionally handles this course's uncompressed v2 stores
only. Use Zarrita (JavaScript) or zarr-python for arbitrary production stores.
"""
from pathlib import Path
import csv
import io
import json
import sqlite3
import zipfile
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, HTML, IFrame, YouTubeVideo

SITE='https://jltobias.github.io/JupyterLite-zarr-sql-views'
DATA=Path('data')
plt.rcParams.update({'figure.figsize':(9,4.5),'axes.spines.top':False,'axes.spines.right':False,
                     'axes.grid':False,'font.size':11,'figure.dpi':110})

def load_cube(key):
    """Decode an actual Zarr store transported in a small ZIP for JupyterLite."""
    with zipfile.ZipFile(DATA/f'{key}.zip') as store:
        meta=json.loads(store.read('.zattrs'))
        spec=json.loads(store.read('value/.zarray'))
        assert spec['zarr_format']==2 and spec['compressor'] is None
        assert spec['order']=='C' and spec['dtype']=='<f4'
        assert spec['chunks']==[1,*spec['shape'][1:]], 'Unsupported chunk layout'
        arrays=[np.frombuffer(store.read(f'value/{t}.0.0'),dtype='<f4').reshape(spec['shape'][1:])
                for t in range(spec['shape'][0])]
    return meta,np.stack(arrays)

def sql_connection(meta,values):
    """SQLite in Python; the linked JavaScript lab uses DuckDB-WASM.

    The shared SELECT / WHERE / GROUP BY examples intentionally use portable SQL.
    """
    con=sqlite3.connect(':memory:')
    con.execute('CREATE TABLE cells(t INTEGER, row INTEGER, col INTEGER, lon REAL, lat REAL, value REAL)')
    con.executemany('INSERT INTO cells VALUES (?,?,?,?,?,?)',
        ((t,y,x,float(meta['lon'][x]),float(meta['lat'][y]),float(v) if np.isfinite(v) else None)
         for (t,y,x),v in np.ndenumerate(values)))
    return con

def map_slice(meta,values,t=0,title=None):
    fig,ax=plt.subplots()
    image=ax.pcolormesh(meta['lon'],meta['lat'],values[t],shading='nearest',cmap='viridis',
                       vmin=meta['range'][0],vmax=meta['range'][1])
    ax.set(xlabel='Longitude (degrees east)',ylabel='Latitude (degrees north)',
           title=title or f"{meta['title']} | {meta['times'][t]} | {meta['kind'].upper()}")
    ax.set_aspect(1 / max(.2, np.cos(np.deg2rad(np.mean(meta['lat'])))))
    fig.colorbar(image,ax=ax,label=meta['units'])
    fig.tight_layout()
    return fig,ax

def lab(key='ngami',mode='map'):
    url=f'{SITE}/lab/?dataset={key}&mode={mode}'
    display(HTML(f'<p><a href="{url}" target="_blank" rel="noopener">Open the linked SQL lab in a new tab ↗</a></p>'))
    display(IFrame(url,width='100%',height=670))

def export_geojson(meta,values,path='selection.geojson',threshold=0):
    features=[]
    for (t,y,x),v in np.ndenumerate(values):
        if np.isfinite(v) and v>=threshold:
            features.append({'type':'Feature','geometry':{'type':'Point','coordinates':[meta['lon'][x],meta['lat'][y]]},
               'properties':{'time':meta['times'][t],'value':float(v),'units':meta['units'],'kind':meta['kind']}})
    obj={'type':'FeatureCollection','source':meta['source'],'license':meta['license'],
         'description':meta['description'],'features':features}
    Path(path).write_text(json.dumps(obj,allow_nan=False),encoding='utf-8')
    return len(features)
