"""Check teaching data integrity, native-source ranges, and notebook packaging."""
from pathlib import Path
import hashlib
import json
import zipfile
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
catalog=json.loads((ROOT/'public/data/catalog.json').read_text())
assert len(catalog)==6
for meta in catalog:
    key=meta['id']; folder=ROOT/'public/data'/meta['store']
    spec=json.loads((folder/'value/.zarray').read_text())
    assert spec['shape']==meta['shape'] and spec['chunks']==[1,*meta['shape'][1:]]
    assert meta['kind'] in ['observed','synthetic'] and meta['units'] and meta['license']
    assert len(meta['lon'])==meta['shape'][2] and len(meta['lat'])==meta['shape'][1]
    assert np.all(np.diff(meta['lon'])>0) and np.all(np.diff(meta['lat'])<0)
    zipped=ROOT/'notebooks/data'/f'{key}.zip'
    assert hashlib.sha256(zipped.read_bytes()).hexdigest()==meta['sha256_notebook_zip']
    with zipfile.ZipFile(zipped) as archive:
        arrays=[]
        for t in range(meta['shape'][0]):
            path=f'value/{t}.0.0'; raw=(folder/path).read_bytes()
            assert raw==archive.read(path)
            a=np.frombuffer(raw,dtype='<f4').reshape(meta['shape'][1:]); arrays.append(a)
        values=np.stack(arrays)
        assert np.isclose(np.nanmin(values),meta['range'][0]) and np.isclose(np.nanmax(values),meta['range'][1])
        if key=='ngami':
            assert np.isfinite(values).sum()>0
            assert np.nanmin(values)>=0 and np.nanmax(values)<=1
            cached=np.load(ROOT/'public/data/deafrica-extract.npz')['value']
            np.testing.assert_allclose(values,cached,equal_nan=True)
    print(key,meta['kind'],meta['shape'],'OK')
assert (ROOT/'notebooks/data/CMIP6_WarmingLevels.csv').exists()
assert len(list((ROOT/'notebooks').glob('*.ipynb')))==12
print('All data checks passed')
