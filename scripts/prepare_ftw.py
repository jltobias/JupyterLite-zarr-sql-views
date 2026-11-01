"""Prepare small, real FTW prediction windows; native Python, never in JupyterLite.

Default: rebuild lab Zarr stores from the verified, checked-in extracts (offline).
--fetch: read two 128 x 128 windows and intersecting GeoParquet row groups using
anonymous HTTP ranges. No country file or global raster is downloaded in full.
The catalog commit pins documentation, NOT the mutable source data. ETags,
metadata, selected source windows and extract SHA256s record what was used.
"""
from pathlib import Path
import argparse
import hashlib
import io
import json
from datetime import datetime, timezone
import numpy as np
from prepare_data import cube, write_json, MANIFEST

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'notebooks/data'
PROVENANCE = DATA / 'ftw-provenance.json'
BASE = 'https://s3.us-west-2.amazonaws.com/us-west-2.opendata.source.coop/tge-labs/ftw-global-data/'
LOGICAL = 'https://data.source.coop/ftw/global-data/'
COMMIT = 'fd844c4c646af0f8e653fba774f79cc17b2af124'
CATALOG = f'https://raw.githubusercontent.com/fieldsoftheworld/ftw-data-catalog/{COMMIT}/catalog/'
STORE = 'predictions/zarr/alpha/global.zarr'
REGIONS = [('senegal', 'Senegal River valley teaching window', 'SN', 'Senegal', -16.22, 16.30),
           ('kenya', 'Western Kenya teaching window', 'KE', 'Kenya', 34.95, -0.10)]
BANDS = ['non_field_background', 'field', 'field_boundaries']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fetch():
    import requests
    import zarr
    import pyarrow.parquet as pq
    from obstore.store import HTTPStore
    from shapely import from_wkb
    from shapely.geometry import box, mapping

    session = requests.Session()
    def head(url):
        r = session.head(url, timeout=60); r.raise_for_status()
        return dict(url=url, etag=r.headers['ETag'], bytes=int(r.headers['Content-Length']),
                    last_modified=r.headers.get('Last-Modified'))

    class RangeFile(io.RawIOBase):
        """Seekable, byte-budgeted HTTP reader; rejects silent full-file responses."""
        def __init__(self, source):
            self.source = source; self.pos = 0; self.transferred = 0
        def readable(self): return True
        def seekable(self): return True
        def tell(self): return self.pos
        def seek(self, offset, whence=0):
            self.pos = offset + (0 if whence == 0 else self.pos if whence == 1 else self.source['bytes'])
            if self.pos < 0: raise ValueError('Negative seek')
            return self.pos
        def read(self, size=-1):
            end = self.source['bytes'] if size < 0 else min(self.pos + size, self.source['bytes'])
            if end <= self.pos: return b''
            assert self.transferred + end-self.pos <= 128*1024**2, 'Stop: 128 MiB per-country request budget'
            with session.get(self.source['url'], headers={'Range':f'bytes={self.pos}-{end-1}',
                            'If-Match':self.source['etag']}, stream=True, timeout=90) as r:
                r.raise_for_status()
                assert r.status_code == 206, 'Server must honor byte ranges'
                assert r.headers['Content-Range'] == f'bytes {self.pos}-{end-1}/{self.source["bytes"]}'
                raw=r.raw.read(end-self.pos+1)
            assert len(raw)==end-self.pos
            self.transferred += len(raw); self.pos=end
            return raw

    p = dict(dataset='Global Fields of the World (FTW)', variant='alpha', years=[2024,2025],
             provider='Taylor Geospatial and collaborators; Microsoft AI for Good Research Lab',
             inputs='Copernicus Sentinel-2 planting and harvest composites', model='PRUE',
             source='https://source.coop/ftw/global-data', physical_base=BASE, logical_base=LOGICAL,
             catalog_commit=COMMIT, catalog_commit_pins_data=False,
             license='CC-BY-4.0', license_url='https://creativecommons.org/licenses/by/4.0/',
             citation='Robinson et al. (2026), The first global agricultural field boundary map at 10 m resolution',
             paper='https://doi.org/10.48550/arXiv.2605.11055',
             retrieved_utc=datetime.now(timezone.utc).isoformat(), bands=BANDS,
             sampling='Contiguous 128 x 128 native pixels, no resampling. Full polygons intersecting the pixel-edge extent; polygons are not clipped. Geometry and provider area/perimeter are retained.',
             confidence='Separate 500 m confidence raster sampled upstream at each polygon representative point; raw / 0.578178 * 100, capped at 100; not the field softmax probability.',
             limitations='Teaching windows selected by location, not representative country samples. Independent annual predictions are not tracked parcels. Not legal boundaries, crop yields, or food-security estimates.',
             regions=[], source_objects=[], artifacts=[])
    def artifact(path):
        p['artifacts'].append(dict(file=path.name, bytes=path.stat().st_size, sha256=sha(path)))
    # Preserve the exact root metadata and STAC collection descriptions with the extracts.
    for name,url in [('ftw-zarr-metadata.json',BASE+STORE+'/zarr.json'),
                     ('ftw-catalog.json',CATALOG+'catalog.json'),
                     ('ftw-zarr-collection.json',CATALOG+'predictions/zarr/collection.json'),
                     ('ftw-vector-collection.json',CATALOG+'predictions/vectors/collection.json')]:
        r=session.get(url,timeout=60); r.raise_for_status(); assert len(r.content)<250000
        path=DATA/name; path.write_bytes(r.content); artifact(path)
    root=zarr.open_group(zarr.storage.ObjectStore(HTTPStore(BASE+STORE),read_only=True),mode='r',use_consolidated=True)
    np.testing.assert_array_equal(root['band'][:],BANDS)
    np.testing.assert_array_equal(root['time'][:],[0,366])
    assert root['time'].attrs['units']=='days since 2024-01-01'
    assert root['variables'].shape==(2,3,1566049,4007517)
    for path in ['zarr.json','x/c/0','y/c/0','time/c/0','band/c/0']:
        p['source_objects'].append(head(BASE+STORE+'/'+path))
    xs,ys=root['x'][:],root['y'][:]
    transform=root.attrs['spatial:transform']; dx,dy=transform[0],-transform[4]
    np.testing.assert_allclose(xs,transform[2]+(np.arange(len(xs))+.5)*dx,atol=1e-8)
    np.testing.assert_allclose(ys,transform[5]-(np.arange(len(ys))+.5)*dy,atol=1e-8)
    p['source_transform']=transform
    for key,title,country,name,lon,lat in REGIONS:
        c=int(np.argmin(abs(xs-lon))); r=int(np.argmin(abs(ys-lat)))
        r0,r1,c0,c1=r-64,r+64,c-64,c+64
        shards=[head(BASE+STORE+f'/variables/c/{t}/0/{sr}/{sc}') for t in range(2)
                for sr in range(r0//8192,(r1-1)//8192+1) for sc in range(c0//8192,(c1-1)//8192+1)]
        print('Reading native probability pixels:',key,flush=True)
        a=root['variables'][:,:,r0:r1,c0:c1]
        for obj in shards:
            assert head(obj['url'])['etag']==obj['etag'], 'Source shard changed during read'
        p['source_objects']+=shards
        bounds=[float(xs[c0]-dx/2),float(ys[r1-1]-dy/2),float(xs[c1-1]+dx/2),float(ys[r0]+dy/2)]
        path=DATA/f'ftw_{key}_probabilities.npz'
        np.savez_compressed(path,probability=a,lon=xs[c0:c1],lat=ys[r0:r1])
        artifact(path)
        prefix=f'predictions/vectors/alpha/results-by-admin-conf/admin:country_code={country}/{name}'
        source=head(BASE+prefix+'.parquet')
        features=[]; selected=[]
        with RangeFile(source) as f:
            pf=pq.ParquetFile(f)
            geo=json.loads(pf.metadata.metadata[b'geo'])
            crs=geo['columns']['geometry'].get('crs')
            assert crs is None or crs.get('id',{}).get('code') in [4326,'CRS84']
            names=[pf.schema.column(i).path for i in range(len(pf.schema))]
            for i in range(pf.num_row_groups):
                rg=pf.metadata.row_group(i)
                stats={axis:rg.column(names.index('bbox.'+axis)).statistics for axis in ['xmin','ymin','xmax','ymax']}
                assert all(s and s.has_min_max for s in stats.values()), 'Require spatial row-group statistics'
                if (stats['xmin'].min>bounds[2] or stats['xmax'].max<bounds[0] or
                    stats['ymin'].min>bounds[3] or stats['ymax'].max<bounds[1]): continue
                selected.append(i)
                assert len(selected)<=8, 'Stop: unexpected number of spatial row groups'
                table=pf.read_row_group(i)
                # Bbox prefilter before decoding WKB geometries.
                for row in table.to_pylist():
                    b=row['bbox']
                    if b['xmin']>bounds[2] or b['xmax']<bounds[0] or b['ymin']>bounds[3] or b['ymax']<bounds[1]: continue
                    geometry=from_wkb(row['geometry'])
                    if not geometry.intersects(box(*bounds)): continue
                    assert geometry.is_valid and geometry.geom_type in ['Polygon','MultiPolygon']
                    props={k:v for k,v in row.items() if k not in ['geometry','bbox']}
                    props['year']=props['determination:datetime'].year
                    props['determination:datetime']=props['determination:datetime'].isoformat()
                    props['crosses_window_edge']=not box(*bounds).covers(geometry)
                    features.append(dict(type='Feature',geometry=mapping(geometry),properties=props))
            source.update(row_groups=selected,total_row_groups=pf.num_row_groups,bytes_transferred=f.transferred,
                          geo_metadata=geo)
        p['source_objects'].append(source)
        features.sort(key=lambda f:(f['properties']['year'],f['properties']['id']))
        assert features and {f['properties']['year'] for f in features}=={2024,2025}
        path=DATA/f'ftw_{key}_fields.geojson'
        write_json(path,dict(type='FeatureCollection',source=LOGICAL+prefix+'.parquet',
                            attribution=p['provider'],license=p['license'],license_url=p['license_url'],
                            citation=p['paper'],selection_bounds=bounds,geometry_clipped=False,features=features))
        artifact(path)
        p['regions'].append(dict(id=key,title=title,country=country,center=[lon,lat],bounds=bounds,
                                 source_window=[r0,r1,c0,c1],shape=[2,3,128,128],crs='EPSG:4326',
                                 field_count_by_year={str(y):sum(f['properties']['year']==y for f in features) for y in [2024,2025]}))
        print(key,'fields:',len(features),'groups:',selected,'range bytes:',source['bytes_transferred'],flush=True)
    # Metadata/coordinate identifiers must also still match at the end.
    for obj in p['source_objects']:
        assert head(obj['url'])['etag']==obj['etag'], 'Source changed during extraction'
    write_json(PROVENANCE,p)


def derive():
    p=json.loads(PROVENANCE.read_text(encoding='utf-8'))
    for item in p['artifacts']:
        assert sha(DATA/item['file'])==item['sha256'], 'FTW extract checksum mismatch'
    for region in p['regions']:
        key=region['id']
        with np.load(DATA/f'ftw_{key}_probabilities.npz',allow_pickle=False) as d:
            cube('ftw_'+key,region['title']+' / FTW field probability',d['probability'][:,1],d['lon'],d['lat'],
                 ['2024','2025'],'field class probability (0-1)','prediction',
                 'FTW / PRUE model predictions from Sentinel-2. Native ~10 m geographic pixels; '+
                 'not legal parcels, calibrated confidence, crop yield or a verified change map. '+
                 '3D height encodes probability, not terrain.', 'ocean',
                 dict(source=p['provider']+'; Copernicus Sentinel-2; Source Cooperative',license=p['license'],
                      provenance='ftw-provenance.json',dataset_version='alpha',model='PRUE',
                      statistic='field softmax class probability',sampling=p['sampling'],citation=p['paper']))
    previous=json.loads((ROOT/'public/data/catalog.json').read_text())
    combined=[m for m in previous if not m['id'].startswith('ftw_')]+MANIFEST
    write_json(ROOT/'public/data/catalog.json',combined); write_json(DATA/'catalog.json',combined)
    write_json(ROOT/'public/data/ftw-provenance.json',p)
    print('Prepared',len(MANIFEST),'FTW probability cubes')


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--fetch',action='store_true'); args=parser.parse_args()
    if args.fetch: fetch()
    derive()
