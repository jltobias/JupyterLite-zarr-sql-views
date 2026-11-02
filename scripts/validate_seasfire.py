"""Numerical and provenance checks for real SeasFire subsets and LexCube delivery."""
from pathlib import Path
import hashlib
import json
import os
import sys
import tarfile
import zipfile
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'notebooks'))
os.chdir(ROOT/'notebooks')
from seasfire import load_seasfire,spatial_series,seasonal_anomaly,lag_correlation
from course import load_cube,sql_connection

p=json.loads(Path('data/seasfire-provenance.json').read_text(encoding='utf-8'))
for item in p['artifacts']:
    assert hashlib.sha256(Path('data',item['file']).read_bytes()).hexdigest()==item['sha256']
assert Path('data/seasfire-provenance.json').read_bytes()==(ROOT/'public/data/seasfire-provenance.json').read_bytes()
assert p['source_object_bytes']==sum(x['bytes'] for x in p['source_objects'])<=1536*1024**2
assert all(len(x['sha256'])==64 and x['etag'] and x['url'].startswith(p['base']) for x in p['source_objects'])
for key in ['ghana','zambia']:
    d=load_seasfire(key)
    assert d['gwis_ba'].shape==(966,16,16)
    assert d['dates'][0]==np.datetime64('2001-01-01') and d['dates'][-1]==np.datetime64('2021-12-27')
    np.testing.assert_array_equal(np.unique(d['year'],return_counts=True)[1],np.full(21,46))
    assert set(d['duration_days'])=={5,6,8}
    assert np.all(d['duration_days'][d['bin']<45]==8)
    np.testing.assert_allclose(np.diff(d['lon']),.25);np.testing.assert_allclose(np.diff(d['lat']),-.25)
    assert np.isnan(d['gwis_ba'][d['year']==2001]).all()
    assert np.isfinite(d['gwis_ba'][d['year']>2001]).all()
    assert np.nanmin(d['gwis_ba'])>=0 and np.nanmax(d['gwis_ba'])>0
    assert (d['area']>0).all() and d['metadata']['area/.zattrs']['units']=='m2'
    series=spatial_series(d,'gwis_ba')
    assert np.isnan(series[:46]).all()
    np.testing.assert_allclose(series[46:],d['gwis_ba'][46:].astype(float).sum(axis=(1,2)))
    weights=d['area'].astype(float)
    np.testing.assert_allclose(spatial_series(d,'vpd')[100],np.average(d['vpd'][100],weights=weights))
    meta,values=load_cube('seasfire_'+key)
    assert meta['shape']==[184,16,16] and meta['kind']=='historical'
    np.testing.assert_array_equal(values,d['gwis_ba'][d['year']>=2018])
    con=sql_connection(meta,values)
    assert con.execute('SELECT COUNT(*) FROM cells WHERE t=0 AND value>500').fetchone()[0]==int(np.sum(values[0]>500))
    con.close()
    print(key,'dates, coverage, units, source support and SQL agree')

# A held-out perturbation must not change the fitted seasonal baseline.
bins=np.tile(np.arange(46),3);train=np.arange(138)<92
values=np.arange(138,dtype=float)
_,a=seasonal_anomaly(values,bins,train)
values[~train]+=10000
_,b=seasonal_anomaly(values,bins,train)
np.testing.assert_array_equal(a,b)
# Known delayed signal verifies lag direction and split-boundary exclusion.
signal=np.random.default_rng(7).normal(size=138)
response=np.r_[np.nan,signal[:-1]]
r,n=lag_correlation(signal,response,1,~train)
assert np.isclose(r,1) and n==45

wheel=Path('wheels/lexcube-2.0.1-py3-none-any.whl')
assert hashlib.sha256(wheel.read_bytes()).hexdigest()=='9b4be927663d48139136260edfe4b7d6b3e78bf56fbc917881a47330f073ba5e'
source=ROOT/'public/vendor/lexcube/lexcube-2.0.1.tar.gz'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='6ffa67f254cbe5a99e40335a070ee248d9c0e6bb1994f5367c4392bc776d9f43'
with tarfile.open(source) as archive:
    assert any('/src/' in n and n.endswith('.ts') for n in archive.getnames())
with zipfile.ZipFile(wheel) as archive:
    module=archive.read('lexcube/lexcube_server/src/tile_server.py').decode().replace('\r\n','\n')
    assert module.count('import psutil\n')==1
    assert module.count('def get_current_memory_usage(s: str = ""):\n')==1
print('SeasFire and LexCube integrity checks passed')
