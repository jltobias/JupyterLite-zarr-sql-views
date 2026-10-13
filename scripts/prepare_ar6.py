"""Prepare bounded AR6 full-sample extracts; never run during normal site builds.

Run with --download to fetch only the enumerated objects, then reuse .work/ar6-cache.
The source is Zarr v2/Blosc. Browser lessons use small NPZ and uncompressed Zarr
derivatives, preserving all 20,000 samples for selected locations and each year.
"""
from pathlib import Path
import argparse
import hashlib
import io
import json
import math
import urllib.request
import zipfile
from datetime import datetime, timezone
import numpy as np
import numcodecs
from prepare_data import cube, MANIFEST, write_json

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / '.work/ar6-cache'
OUT = ROOT / 'notebooks/data'
PUBLIC = ROOT / 'public/data'
COMMIT = '8ee75128d8f6d9a8ba9825f47c92d11955d0651e'
GUIDE = 'https://raw.githubusercontent.com/Rutgers-ESSP/IPCC-AR6-Sea-Level-Projections/' + COMMIT
BASE = 'https://storage.googleapis.com/ar6-lsl-simulations-public-standard'
WORKFLOW = 'wf_1e'
SCENARIOS = ['ssp126', 'ssp585']
# Rounded city reference points for geographic orientation, not port assets or boundaries.
CITIES = [dict(id=k, name=n, lat=y, lon=x) for k,n,y,x in [
    ('abidjan','Abidjan',5.32,-4.02), ('lagos','Lagos',6.45,3.39),
    ('bangkok','Bangkok',13.76,100.50), ('ho_chi_minh','Ho Chi Minh City',10.78,106.70),
    ('manila','Manila',14.60,120.98)]]
MAX_DOWNLOAD = 2 * 1024**3
MAX_OBJECT = 128 * 1024**2
OBJECTS = {}
downloaded = 0
allow_download = False

def fetch(url):
    """Bound compressed object size and total transfer; atomic, persistent cache."""
    global downloaded
    key = hashlib.sha256(url.encode()).hexdigest()
    path = CACHE / key
    record_path = CACHE / (key + '.json')
    CACHE.mkdir(parents=True, exist_ok=True)
    if path.exists() and record_path.exists():
        raw = path.read_bytes()
        record = json.loads(record_path.read_text())
        if hashlib.sha256(raw).hexdigest() != record['sha256']:
            raise ValueError(f'Cache checksum mismatch: {url}')
    else:
        if not allow_download:
            raise RuntimeError('Missing cached object. Run --download to allow bounded source retrieval: ' + url)
        request = urllib.request.Request(url, headers={'Origin':'https://jltobias.github.io'})
        with urllib.request.urlopen(request, timeout=120) as response:
            size = int(response.headers.get('Content-Length', 0))
            if size > MAX_OBJECT or downloaded + size > MAX_DOWNLOAD:
                raise ValueError('Download budget exceeded before reading ' + url)
            raw = response.read(min(MAX_OBJECT, MAX_DOWNLOAD-downloaded)+1)
            if len(raw)>MAX_OBJECT or downloaded+len(raw)>MAX_DOWNLOAD:
                raise ValueError('Download budget exceeded: ' + url)
            record = {'url':url, 'bytes':len(raw), 'sha256':hashlib.sha256(raw).hexdigest(),
                      'retrieved_utc':datetime.now(timezone.utc).isoformat(),
                      'etag':response.headers.get('ETag'),
                      'generation':response.headers.get('x-goog-generation'),
                      'cors_allow_origin':response.headers.get('Access-Control-Allow-Origin')}
        downloaded += len(raw)
        temporary = path.with_suffix('.part')
        temporary.write_bytes(raw); temporary.replace(path)
        write_json(record_path, record)
        print(f'{downloaded/1e6:.1f} MB fetched: {url.rsplit("/",2)[-2:]}', flush=True)
    OBJECTS[url] = record
    return raw

def store(partition, scenario):
    base = f'{BASE}/{partition}/full_sample_workflows/{WORKFLOW}/{scenario}/total-workflow.zarr'
    metadata = json.loads(fetch(base+'/.zmetadata'))['metadata']
    spec = metadata['sea_level_change/.zarray']
    expected = ['samples','years','locations'] if partition=='tide-gauges' else ['samples','years','lat','lon']
    if metadata['sea_level_change/.zattrs']['_ARRAY_DIMENSIONS'] != expected:
        raise ValueError('Unexpected axis order')
    if metadata['sea_level_change/.zattrs']['units'] != 'mm' or spec['shape'][:2] != [20000,9]:
        raise ValueError('Unexpected source units or sample/year count')
    coords = {k:read_chunk(base, metadata[k+'/.zarray'], k+'/0').reshape(-1)
              for k in ['lat','lon','years'] + (['locations'] if partition=='tide-gauges' else [])}
    if coords['years'].tolist()!=list(range(2020,2101,10)):
        raise ValueError('Unexpected time coordinates')
    return base, metadata, coords

def read_chunk(base, spec, key):
    if (spec['zarr_format']!=2 or spec['order']!='C' or spec['filters'] is not None
        or spec['compressor']['id']!='blosc'):
        raise ValueError('Unsupported source storage encoding')
    size = math.prod(spec['chunks'])*np.dtype(spec['dtype']).itemsize
    if size > MAX_OBJECT:
        raise ValueError('Decoded chunk exceeds memory budget')
    raw = numcodecs.get_codec(spec['compressor']).decode(fetch(base+'/'+key))
    if len(raw)!=size:
        raise ValueError('Decoded chunk size mismatch')
    return np.frombuffer(raw,dtype=spec['dtype']).reshape(spec['chunks'])

def distances(city, lat, lon):
    phi = np.radians(lat)
    a = np.sin((phi-np.radians(city['lat']))/2)**2 + np.cos(phi)*np.cos(np.radians(city['lat']))*np.sin(np.radians(lon-city['lon'])/2)**2
    return 6371.0088 * 2*np.arcsin(np.sqrt(np.clip(a,0,1)))

def save_npz(path, **arrays):
    """Stable ZIP timestamps and no pickled objects."""
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as archive:
        for key,value in arrays.items():
            buf=io.BytesIO(); np.save(buf,value,allow_pickle=False)
            info=zipfile.ZipInfo(key+'.npy',date_time=(2026,1,1,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED
            archive.writestr(info,buf.getvalue())

def prepare():
    OUT.mkdir(exist_ok=True,parents=True)
    names_raw=fetch(GUIDE+'/location_list.txt').decode()
    names={int(row.split('\t')[1]):row.split('\t')[0] for row in names_raw.splitlines()}
    # Confirm every selected store is in the authors' pinned catalog.
    catalog=json.loads(fetch(GUIDE+'/google_zarr_stores.json'))['full_sample_workflows']
    for part,scenarios in [('tide-gauges',SCENARIOS),('gridded',['ssp585'])]:
        for scenario in scenarios:
            uri=f'gs://ar6-lsl-simulations-public-standard/{part}/full_sample_workflows/{WORKFLOW}/{scenario}/total-workflow.zarr'
            if uri not in catalog[part]: raise ValueError('Store absent from pinned source catalog')
    license_raw=fetch(GUIDE+'/LICENSE.md')
    (ROOT/'licenses/ipcc-ar6-sea-level-CC-BY-4.0.md').write_bytes(license_raw)
    gauges=[]; samples=[]; stores=[]
    previous=None
    for scenario in SCENARIOS:
        base,metadata,coord=store('tide-gauges',scenario)
        if previous is not None:
            for k in coord: np.testing.assert_array_equal(coord[k],previous[k])
        previous=coord
        selected=[int(np.argmin(distances(c,coord['lat'],coord['lon']))) for c in CITIES]
        indices=sorted(set(selected))
        if not gauges:
            for c,idx in zip(CITIES,selected):
                c['gauge_column']=indices.index(idx)
                c['gauge_distance_km']=float(distances(c,coord['lat'][idx],coord['lon'][idx]))
            gauges=[dict(id=int(coord['locations'][i]), name=names[int(coord['locations'][i])],
                         lat=float(coord['lat'][i]),lon=float(coord['lon'][i])) for i in indices]
        spec=metadata['sea_level_change/.zarray']
        if spec['chunks']!=[5000,5,1012]: raise ValueError('Unexpected tide-gauge chunks')
        subset=np.empty((20000,9,len(indices)),dtype='<f4')
        for s in range(4):
            for t in range(2):
                chunk=read_chunk(base,spec,f'sea_level_change/{s}.{t}.0')
                n=min(5,9-t*5)
                subset[s*5000:(s+1)*5000,t*5:t*5+n]=chunk[:,:n,indices]
        if not np.isfinite(subset).all(): raise ValueError('Missing tide-gauge samples')
        samples.append(subset)
        stores.append({'partition':'tide-gauges','scenario':scenario,'url':base,'metadata':metadata})
    gauge_samples=np.stack(samples)
    save_npz(OUT/'ar6-gauge-samples.npz',sea_level_change_mm=gauge_samples,years=coord['years'])
    del samples, subset, chunk

    base,metadata,coord=store('gridded','ssp585')
    spec=metadata['sea_level_change/.zarray']
    if spec['chunks']!=[5000,5,30,30]: raise ValueError('Unexpected gridded chunks')
    points=[]; windows=[]
    for c in CITIES:
        yi=int(np.argmin(abs(coord['lat']-c['lat'])))
        xi=int(np.argmin(abs(coord['lon']-c['lon'])))
        cells=[(y,x) for y in range(yi-2,yi+3) for x in range(xi-2,xi+3)]
        windows.append(cells); points.extend(cells)
    points=sorted(set(points)); lookup={p:i for i,p in enumerate(points)}
    grid=np.full((20000,9,len(points)),np.nan,dtype='<f4')
    tiles=sorted(set((y//30,x//30) for y,x in points))
    for ty,tx in tiles:
        ids=[i for i,(y,x) in enumerate(points) if (y//30,x//30)==(ty,tx)]
        yy=np.array([points[i][0]%30 for i in ids]); xx=np.array([points[i][1]%30 for i in ids])
        for s in range(4):
            for t in range(2):
                chunk=read_chunk(base,spec,f'sea_level_change/{s}.{t}.{ty}.{tx}')
                n=min(5,9-t*5)
                grid[s*5000:(s+1)*5000,t*5:t*5+n,np.asarray(ids)]=chunk[:,:n,yy,xx]
    count=np.isfinite(grid).sum(axis=0)
    if not np.all((count==0)|(count==20000)): raise ValueError('Partially missing samples require an explicit policy')
    defined=np.all(count==20000,axis=0)
    quantiles=np.full((3,9,len(points)),np.nan)
    quantiles[:,:,defined]=np.quantile(grid[:,:,defined].astype('float64')/1000,[.17,.5,.83],axis=0,method='linear')
    nearest=[]; summaries=[]
    for c,cells in zip(CITIES,windows):
        ids=[lookup[p] for p in cells]
        lat=np.array([coord['lat'][y] for y,x in cells]); lon=np.array([coord['lon'][x] for y,x in cells])
        d=distances(c,lat,lon); valid=np.array([defined[i] for i in ids])
        if not valid.any(): raise ValueError('No defined grid location in city window')
        index=int(np.argmin(np.where(valid,d,np.inf))); p=ids[index]; nearest.append(p)
        c['grid']={'lat':float(lat[index]),'lon':float(lon[index]),'distance_km':float(d[index]),
                   'window_defined_locations':int(valid.sum()),'window_locations':len(cells)}
        vals=quantiles[1,:,ids].T.reshape(9,5,5)[:,::-1,:]
        # Advanced indexing above yields (points, years); transpose restores year first.
        cube('ar6_'+c['id'],c['name']+' · AR6 sea-level projection',vals,
             sorted(set(lon)),sorted(set(lat),reverse=True),[str(int(y)) for y in coord['years']],
             'relative sea-level change (m; 1995–2014 baseline)','projected',
             'AR6 v20210809, wf_1e / SSP5-8.5, median of all 20,000 samples per year. '
             'One-degree regional projection locations; no additional land/ocean mask. '
             'Background land motion included. Not a flood map or canonical IPCC p-box. '
             'Extruded height is a visual scale, not terrain.', 'ocean',
             {'source':'Garner et al. (2021), doi:10.5281/zenodo.5914709; FACTS; IPCC AR6 WG1 Ch9',
              'license':'CC-BY-4.0','workflow':WORKFLOW,'scenario':'ssp585','statistic':'p50',
              'baseline':'1995–2014','sample_count':20000,'data_version':'20210809',
              'provenance':'ar6-provenance.json'})
        for i in ids:
            if not defined[i]: continue
            y,x=points[i]
            for t,year in enumerate(coord['years']):
                summaries.append({'city':c['name'],'year':int(year),'lat':float(coord['lat'][y]),
                    'lon':float(coord['lon'][x]),'p17_m':float(quantiles[0,t,i]),
                    'p50_m':float(quantiles[1,t,i]),'p83_m':float(quantiles[2,t,i]),'n':20000})
    save_npz(OUT/'ar6-grid-city-samples.npz',sea_level_change_mm=grid[:,:,nearest],years=coord['years'])
    stores.append({'partition':'gridded','scenario':'ssp585','url':base,'metadata':metadata})
    write_json(OUT/'ar6-grid-summary.json',summaries)
    provenance={'dataset':'IPCC AR6 Sea Level Projections','version':'20210809','license':'CC-BY-4.0',
        'source_repository_commit':COMMIT,'workflow':WORKFLOW,'gauge_scenarios':SCENARIOS,'grid_scenario':'ssp585',
        'years':coord['years'].tolist(),'samples':20000,'source_units':'mm','display_units':'m',
        'baseline':'1995–2014','baseline_reference':'https://doi.org/10.5194/gmd-16-7461-2023',
        'cities':CITIES,'gauges':gauges,'city_coordinates':'Rounded reference points chosen for teaching; not port boundaries or surveyed infrastructure.',
        'method':'Nearest gauge by great-circle distance among available locations. Gridded 5x5 one-degree windows centered on nearest coordinate. All 20,000 samples retained for selected gauges and nearest grid locations with complete samples; p17/p50/p83 computed independently at each year by NumPy linear quantiles after mm-to-m conversion. No spatial interpolation, ocean mask, DEM, or inundation calculation. Gridded latitude reversed for north-up lab stores.',
        'limitations':['wf_1e samples do not preserve time correlations: no rates, trajectories, or first-crossing dates.',
          'A single workflow is not the assessed IPCC p-box. Scenarios have no assigned probabilities.',
          'Background land motion is included; no additional subsidence term has been added.',
          'Regional projection locations do not resolve port assets, estuarine hydrodynamics, defenses or exposure.'],
        'stores':stores,'source_objects':list(OBJECTS.values()),'unique_source_bytes':sum(o['bytes'] for o in OBJECTS.values())}
    artifacts=['ar6-gauge-samples.npz','ar6-grid-city-samples.npz','ar6-grid-summary.json']
    provenance['artifacts']={f:{'bytes':(OUT/f).stat().st_size,'sha256':hashlib.sha256((OUT/f).read_bytes()).hexdigest()} for f in artifacts}
    write_json(OUT/'ar6-provenance.json',provenance)
    write_json(PUBLIC/'ar6-provenance.json',provenance)
    current=json.loads((PUBLIC/'catalog.json').read_text())
    write_json(PUBLIC/'catalog.json',[m for m in current if not m['id'].startswith('ar6_')]+MANIFEST)
    write_json(OUT/'catalog.json',[m for m in current if not m['id'].startswith('ar6_')]+MANIFEST)
    print('Prepared five city windows, four unique gauges, and all selected Monte Carlo samples.')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--download',action='store_true',help='Allow missing public source objects, capped at 2 GiB per run')
    allow_download=parser.parse_args().download
    prepare()
