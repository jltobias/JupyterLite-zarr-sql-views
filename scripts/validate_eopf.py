"""Project: Earth in the Browser; validate_eopf.py; course contributors.
Created/updated: 2026-11-21. Contact/agency: not supplied.
Purpose: check EOPF extraction, repackaging, ratios, URLs and provenance.
Input: public and notebook EOPF data. Output: assertions and summary.
Dependencies: Python 3.12+, NumPy. No network. Change log: initial checks.
"""
from pathlib import Path
import hashlib
import json
import sys
from urllib.parse import parse_qs, urlsplit
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'notebooks'))
from eopf import load_eopf, normalized_difference, search_url, studio_sample, studio_link, tilejson_url

d=load_eopf();p=d['provenance'];folder=ROOT/'public/data/eopf'
assert p['shape']==[128,128] and p['crs']=='EPSG:32633'
assert p['source_bytes']==sum(o['bytes'] for o in p['source_objects'])<32*1024**2
assert hashlib.sha256((folder/'extract.npz').read_bytes()).hexdigest()==p['extract_sha256']
for file in (ROOT/'notebooks/data/eopf').iterdir():
    assert file.read_bytes()==(folder/file.name).read_bytes(),file.name
assert np.all(np.diff(d['x'])==120) and np.all(np.diff(d['y'])==-120)
assert d['clear_fraction'].min()>=0 and d['clear_fraction'].max()<=1
np.testing.assert_allclose(d['clear_fraction']*36,np.round(d['clear_fraction']*36),atol=2e-6)
# Check exported bytes independently of the preparation writer and notebook loader.
for band in ['b02','b03','b04','b08']:
    raw=np.frombuffer((folder/f'classroom.zarr/{band}/c/0/0').read_bytes(),dtype='<f4').reshape(128,128)
    np.testing.assert_array_equal(raw,d[band])
    assert np.isfinite(raw).all() and -0.1<=raw.min()<raw.max()<2
spec=json.loads((folder/'classroom.zarr/zarr.json').read_text())
assert spec['attributes']['spatial:bbox']==p['bounds']
# Small analytical edge cases catch nodata, zero denominator and double scaling.
actual=normalized_difference(np.array([.6,0,np.nan,-.1,.5]),np.array([.2,0,.1,.2,.25]),[True]*4+[False])
np.testing.assert_allclose(actual,[.5,np.nan,np.nan,np.nan,np.nan],equal_nan=True)
ndvi=normalized_difference(d['b08'],d['b04'],d['clear_fraction']==1)
assert 0<np.isfinite(ndvi).sum()<=ndvi.size
assert -1<=np.nanmin(ndvi)<=np.nanmax(ndvi)<=1
try: search_url([20,10,-20,30])
except ValueError: pass
else: raise AssertionError('Reversed bbox accepted')
assert parse_qs(urlsplit(tilejson_url(d['item'])).query)['assets']==['reflectance|bands=b04,b03,b02']
sample=studio_sample();compile(sample['code'],'studio-recipe','exec')
backend=json.loads((folder/'openeo-collection.json').read_text())
assert set(sample['bands'])<=set(backend['cube:dimensions']['bands']['values'])
import base64
encoded=parse_qs(urlsplit(studio_link(sample)).query)['sample'][0]
assert json.loads(base64.urlsafe_b64decode(encoded+'='*(-len(encoded)%4)))==sample
record=json.loads((folder/'service-provenance.json').read_text())
assert record['status']==400 and 'GeoZarr group' in record['response']['detail']
assert record['tilejson_request']==tilejson_url(d['item'])
assert len(list((ROOT/'notebooks').glob('*eopf*.ipynb')))==6
import tarfile
vendor=ROOT/'vendor/eodash'
v=json.loads((vendor/'provenance.json').read_text())
archive=vendor/'eodash-5.10.0-classroom.tgz'
assert hashlib.sha256(archive.read_bytes()).hexdigest()==v['adapted_sha256']
with tarfile.open(archive,'r:gz') as tar:
    package=json.load(tar.extractfile('package/package.json'))
    assert 'animated-details' not in package['dependencies']
    assert package['dependencies']['@eodash/stac']=='0.2.0'
    assert 'prepare' not in package['scripts']
lock=(ROOT/'package-lock.json').read_text()
assert 'git+' not in lock and 'gist:' not in lock
print('EOPF data, GeoZarr bytes, quality fractions, numerical edge cases and recipes passed')
