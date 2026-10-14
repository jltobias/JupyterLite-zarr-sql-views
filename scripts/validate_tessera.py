"""Source integrity, geographic alignment, numerical contracts and metric exports."""
from pathlib import Path
import hashlib
import json
import sys
import tempfile
import zipfile
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'notebooks'))
from tessera import (load_tessera,unit_vectors,fit_pca,project,spherical_kmeans,
                     assign_clusters,adjusted_rand,export_points)
DATA=ROOT/'notebooks/data'
p=json.loads((DATA/'tessera-provenance.json').read_text())
assert (DATA/'tessera-provenance.json').read_bytes()==(ROOT/'public/data/tessera-provenance.json').read_bytes()
assert p['snapshot_id']=='B6AFRJGX5XQC0A716PA0'
assert (p['dataset_version'],p['dataset_variant'])==('1.1','dclimate')
assert p['root_attributes']['checkpoint_id']=='tessera_v1_1_aws_encoder.pt'
assert len(p['artifacts'])==6 and len(p['cities'])==2
for item in p['artifacts']:
    path=DATA/item['file']
    assert path.stat().st_size==item['bytes']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256']

# Known analytical cases, including absent and zero vectors.
x=np.array([[3.,4.,0.],[0.,0.,2.],[0.,0.,0.],[np.nan,1,2]])
u=unit_vectors(x)
np.testing.assert_allclose(u[:2],[[.6,.8,0],[0,0,1]])
assert np.isnan(u[2:]).all()
assert np.dot(u[0],u[1])==0
np.testing.assert_allclose(unit_vectors(x[:2]*7),u[:2])
# A centered rank-two cloud has an exact two-component reconstruction.
cloud=np.array([[3,1,7],[-3,1,7],[3,-1,7],[-3,-1,7]],dtype=float)
model=fit_pca(cloud,2)
np.testing.assert_allclose(project(cloud,model)@model['components'].T+model['mean'],cloud,atol=1e-12)
np.testing.assert_allclose(model['explained'],[.9,.1],atol=1e-12)
np.testing.assert_allclose(model['components'].T@model['components'],np.eye(2),atol=1e-12)
assert adjusted_rand([0,0,1,1],[1,1,0,0])==1
assert np.isclose(adjusted_rand([0,0,1,1],[0,1,0,1]),-.5)
centers=spherical_kmeans(np.array([[1.,0],[1,.01],[0,1],[.01,1]]),k=2)
labels,_=assign_clusters(np.array([[1.,0],[1,.01],[0,1],[.01,1]]),centers)
assert labels[0]==labels[1] and labels[2]==labels[3] and labels[0]!=labels[2]
assert assign_clusters(np.array([[np.nan,0],[0,0]]),centers)[0].tolist()==[-1,-1]

for city in ['lagos','abidjan']:
    d=load_tessera(city,DATA); x=d['embedding']; u=unit_vectors(x)
    assert x.shape==(3,64,64,128) and d['quantized'].dtype==np.int8
    assert d['years'].tolist()==[2018,2021,2025]
    assert d['valid'].sum()>10000
    assert np.isnan(x[~d['valid']]).all()
    assert (d['s2_obs_count'][d['valid']]>=15).all()
    assert np.all(np.diff(d['lon'])>0) and np.all(np.diff(d['lat'])<0)
    # Independent approximate ground distance to the stored native centers.
    lon,lat=np.meshgrid(d['lon'],d['lat'])
    offset=np.hypot((d['native_lon']-lon)*111320*np.cos(np.deg2rad(lat)),
                    (d['native_lat']-lat)*110574)
    assert offset.max()<7.2
    assert np.all(np.diff(d['native_lon'],axis=1)>0)
    assert np.all(np.diff(d['native_lat'],axis=0)<0)
    score=np.clip(np.sum(u*u[-1,32,32],axis=-1),-1,1)
    assert np.isclose(score[-1,32,32],1)
    # Cross-check scalar arithmetic independently of the vectorized computation.
    a,b=x[0,16,16].astype(float),x[-1,32,32].astype(float)
    expected=sum(a*b)/(sum(a*a)**.5*sum(b*b)**.5)
    np.testing.assert_allclose(score[0,16,16],expected,atol=1e-12)
    with zipfile.ZipFile(DATA/f'tessera_{city}.zip') as archive:
        z=np.stack([np.frombuffer(archive.read(f'value/{i}.0.0'),dtype='<f4').reshape(64,64) for i in range(3)])
        np.testing.assert_allclose(z,score,atol=1e-6,equal_nan=True)
        meta=json.loads(archive.read('.zattrs'))
        assert meta['reference']['year']==2025 and meta['snapshot_id']==p['snapshot_id']
    with tempfile.TemporaryDirectory() as folder:
        export=export_points(d,score,Path(folder)/'points.geojson',threshold=.999999)
        assert export['license']=='CC0-1.0'
        feature=next(f for f in export['features'] if f['properties']==dict(
            year=2025,row=32,col=32,cosine_similarity=float(score[-1,32,32]),
            query_lon=float(d['lon'][32]),query_lat=float(d['lat'][32])))
        assert feature['geometry']['coordinates']==[d['native_lon'][32,32],d['native_lat'][32,32]]
        try:
            export_points(d,score,Path(folder)/'wrong.geojson',reference=(2,16,16))
        except ValueError:
            pass
        else:
            raise AssertionError('Mismatched metric metadata was accepted')
    print(city,'source checksums, masks, alignment, cosine, Zarr and export OK')
print('GeoTessera numerical and provenance checks passed')

# Optional live audit. Needs requirements-tessera.txt; never run by normal CI.
# Read one pixel from each of the six source window-years using raw hemisphere
# arrays, independently of the preparation adapter's merged-zone indexing.
if '--source' in sys.argv:
    from geotessera.icechunk import IcechunkStore
    from pyproj import Transformer
    store=IcechunkStore(p['store'],snapshot_id=p['snapshot_id'])
    for city in p['cities']:
        group=store.root[city['source_zone']]
        xs,ys=group['easting'][:],group['northing'][:]
        forward=Transformer.from_crs('EPSG:4326',city['source_crs'],always_xy=True)
        inverse=Transformer.from_crs(city['source_crs'],'EPSG:4326',always_xy=True)
        for year,index in zip(p['years'],[0,32,63]):
            with np.load(DATA/f"tessera_{city['id']}_{year}.npz") as z:
                east,north=forward.transform(float(z['lon'][index]),float(z['lat'][index]))
                col,row=int(np.argmin(abs(xs-east))),int(np.argmin(abs(ys-north)))
                ti=store.years.index(year)
                np.testing.assert_array_equal(group['embeddings'][ti,row,col,:],z['quantized'][index,index])
                for name in ['scales','s2_obs_count','s1_asc_obs_count','s1_desc_obs_count']:
                    np.testing.assert_array_equal(group[name][ti,row,col],z[name][index,index])
                np.testing.assert_allclose(inverse.transform(xs[col],ys[row]),
                    [z['native_lon'][index,index],z['native_lat'][index,index]],atol=1e-10,rtol=0)
            print('Raw source verified:',city['id'],year,'query row/col',index)
