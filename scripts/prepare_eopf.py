"""Project: Earth in the Browser. File: prepare_eopf.py.
Purpose: create a bounded, reproducible Sentinel-2 classroom extract and GeoZarr.
Author: course contributors; email/organization: not supplied.
Created/updated: 2026-11-21. Change log: initial EOPF teaching extract.
Inputs: pinned EOPF Sentinel-2 L2A item and public Zarr v3 objects (see provenance).
Outputs: public/data/eopf/*, notebooks/data/eopf/*; no full-resolution reflectance.
Dependencies: Python 3.12+, NumPy; --fetch also requests, truststore, numcodecs.
Notes: deterministic 128x128 window of upstream 120 m averaged overviews;
SCL is summarized from aligned 20 m pixels. No climate inference or resampling
to a latitude/longitude grid. Default builds from the checked-in NPZ offline.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'public/data/eopf'
ITEM = 'S2C_MSIL2A_20260928T095031_N0513_R079_T33TVF_20260928T130916'
COLLECTION = 'sentinel-2-l2a'
API = 'https://api.explorer.eopf.copernicus.eu'
ITEM_URL = f'{API}/stac/collections/{COLLECTION}/items/{ITEM}'
WINDOW = (340, 468, 120, 248)  # row start/stop, col start/stop, 120 m grid
BANDS = ['b02', 'b03', 'b04', 'b08']


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def fetch() -> None:
    """Fetch a fixed item with an enforced 32 MiB transfer budget and hashes."""
    import truststore
    truststore.inject_into_ssl()
    import requests
    from numcodecs import Blosc
    from google_crc32c import value as crc32c
    cache = ROOT / '.work/eopf-cache'
    cache.mkdir(parents=True, exist_ok=True)
    objects, total = [], 0

    def get(url: str) -> bytes:
        nonlocal total
        path = cache / hashlib.sha256(url.encode()).hexdigest()
        if path.exists():
            raw = path.read_bytes()
        else:
            with requests.get(url, timeout=90, stream=True) as r:
                r.raise_for_status()
                chunks = []
                size = 0
                for chunk in r.iter_content(65536):
                    size += len(chunk)
                    if size > 8 * 1024**2 or total + size > 32 * 1024**2:
                        raise ValueError('Transfer budget exceeded; no larger fetch attempted')
                    chunks.append(chunk)
                raw = b''.join(chunks)
            path.write_bytes(raw)
        total += len(raw)
        if len(raw) > 8 * 1024**2 or total > 32 * 1024**2:
            raise ValueError('Cached objects exceed transfer budget')
        objects.append({'url': url, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
        return raw

    item = json.loads(get(ITEM_URL))
    collection = json.loads(get(f'{API}/stac/collections/{COLLECTION}'))
    group = item['assets']['reflectance']['href'].rstrip('/')
    root = group.split('/measurements/')[0]
    metadata = json.loads(get(root + '/zarr.json'))
    specs = metadata['consolidated_metadata']['metadata']
    arrays = {}
    r0, r1, c0, c1 = WINDOW
    for band in BANDS:
        key = f'measurements/reflectance/r120m/{band}'
        spec = specs[key]
        shard = spec['codecs'][0]['configuration']
        # These assertions deliberately reject other codecs/layouts. This is a
        # small pinned-source decoder, not a general replacement for Zarr.
        assert spec['shape'] == [915, 915] and spec['data_type'] == 'float32'
        assert shard['chunk_shape'] == [183, 183] and shard['index_location'] == 'end'
        assert shard['codecs'][0] == {'name': 'scale_offset', 'configuration': {'offset': -0.1, 'scale': 10000.0}}
        assert shard['codecs'][1]['configuration'] == {'data_type': 'uint16', 'scalar_map': {'encode': [['NaN', 0]], 'decode': [[0, 'NaN']]}}
        assert [c['name'] for c in shard['codecs']] == ['scale_offset', 'cast_value', 'bytes', 'blosc']
        raw = get(root + '/' + key + '/c/0/0')
        # 5x5 inner chunks, two uint64 index fields and a four-byte CRC footer.
        assert crc32c(raw[-404:-4]) == int.from_bytes(raw[-4:], 'little'), 'Corrupt shard index'
        index = np.frombuffer(raw[-404:-4], dtype='<u8').reshape(5, 5, 2)
        full = np.full((915, 915), np.nan, dtype=np.float32)
        for y in range(r0 // 183, (r1 - 1) // 183 + 1):
            for x in range(c0 // 183, (c1 - 1) // 183 + 1):
                offset, length = map(int, index[y, x])
                if offset == 2**64 - 1:
                    continue
                assert 0 <= offset < offset + length <= len(raw) - 404
                dn = np.frombuffer(Blosc().decode(raw[offset:offset + length]), dtype='<u2').reshape(183, 183)
                values = dn.astype(np.float32) / 10000 - 0.1
                values[dn == 0] = np.nan  # Decode nodata before any ratio.
                full[y*183:(y+1)*183, x*183:(x+1)*183] = values
        arrays[band] = full[r0:r1, c0:c1].copy()

    # Decode the source's single SCL chunk (30 MB uncompressed). Keep the
    # fraction of 20 m children in accepted classes; never average class codes.
    key = 'conditions/mask/l2a_classification/r20m/scl'
    assert specs[key]['shape'] == [5490, 5490]
    assert [c['name'] for c in specs[key]['codecs']] == ['bytes', 'blosc']
    scl = np.frombuffer(Blosc().decode(get(root + '/' + key + '/c/0/0')), dtype='u1').reshape(5490, 5490)
    child = scl[r0*6:r1*6, c0*6:c1*6].reshape(128, 6, 128, 6)
    arrays['clear_fraction'] = np.isin(child, [4, 5, 6]).mean(axis=(1, 3)).astype('f4')
    # Read actual coordinates, not rounded STAC corner bounds.
    for axis, start, stop in [('x', c0, c1), ('y', r0, r1)]:
        raw = get(group + '/r120m/' + axis + '/c/0')
        arrays[axis] = np.frombuffer(raw, dtype='<f4')[start:stop].copy()
    OUT.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT / 'extract.npz', **arrays)
    for name, obj in [('item', item), ('collection', collection), ('source-metadata', metadata)]:
        write_json(OUT / f'{name}.json', obj)
    bounds = [float(arrays['x'][0]-60), float(arrays['y'][-1]-60), float(arrays['x'][-1]+60), float(arrays['y'][0]+60)]
    provenance = {
        'retrieved': '2026-11-21', 'collection': COLLECTION, 'item_id': ITEM,
        'item_url': ITEM_URL, 'group_url': group, 'shape': [128, 128],
        'window_r120m': list(WINDOW), 'crs': 'EPSG:32633', 'bounds': bounds,
        'date': item['properties']['datetime'], 'bands': BANDS,
        'attribution': 'Contains modified Copernicus Sentinel data (2026), processed by EOPF Sentinel Zarr Explorer; subset and GeoZarr repackaging by this course.',
        'license_url': next(x['href'] for x in collection['links'] if x['rel']=='license'),
        'transformations': ['Select 128x128 cells of upstream averaged 120 m overview', 'Decode uint16 packing: DN/10000 - 0.1; DN zero becomes NaN', 'Fraction of aligned 6x6 SCL children in classes 4, 5, 6', 'Repackage physical reflectance in an uncompressed single-resolution Zarr v3 group'],
        'limitations': ['One acquisition; no temporal trend', '120 m overviews contain mixed pixels and averaged reflectances', 'SCL 4/5/6 is a teaching mask, not validated local ground truth', 'A ratio of overview means is not the mean of native-pixel ratios'],
        'source_objects': objects, 'source_bytes': total,
        'extract_sha256': hashlib.sha256((OUT/'extract.npz').read_bytes()).hexdigest(),
    }
    write_json(OUT / 'provenance.json', provenance)
    print('Fetched', total, 'bytes; valid reflectances:', np.isfinite(arrays['b04']).sum())


def package() -> None:
    """Build same-origin GeoZarr for actual OpenLayers/EOxElements rendering."""
    p = json.loads((OUT/'provenance.json').read_text())
    assert hashlib.sha256((OUT/'extract.npz').read_bytes()).hexdigest() == p['extract_sha256']
    with np.load(OUT/'extract.npz') as d:
        attrs = {'proj:code': p['crs'], 'spatial:dimensions': ['y', 'x'],
                 'spatial:shape': [128,128], 'spatial:bbox': p['bounds'],
                 'spatial:registration': 'pixel', 'spatial:transform': [120,0,p['bounds'][0],0,-120,p['bounds'][3]],
                 'attribution': p['attribution']}
        store = OUT / 'classroom.zarr'
        entries = {}
        for key in BANDS + ['x','y']:
            data = np.asarray(d[key], dtype='<f4')
            spec = {'zarr_format': 3, 'node_type': 'array', 'shape': list(data.shape),
                    'data_type': 'float32', 'chunk_grid': {'name':'regular','configuration': {'chunk_shape':list(data.shape)}},
                    'chunk_key_encoding': {'name':'default','configuration':{'separator':'/'}},
                    'fill_value':'NaN', 'codecs':[{'name':'bytes','configuration':{'endian':'little'}}],
                    'dimension_names': ['y','x'] if data.ndim==2 else [key],
                    'attributes':{'units': '1' if key in BANDS else 'm'}}
            write_json(store/key/'zarr.json',spec)
            chunk = store/key/'c'/('0/0' if data.ndim==2 else '0')
            chunk.parent.mkdir(parents=True,exist_ok=True);chunk.write_bytes(data.tobytes())
            entries[key]=spec
        write_json(store/'zarr.json', {'zarr_format':3,'node_type':'group','attributes':attrs,
                   'consolidated_metadata': {'kind':'inline','must_understand':False,'metadata':entries}})
    target = ROOT/'notebooks/data/eopf';target.mkdir(parents=True,exist_ok=True)
    for name in ['extract.npz','item.json','collection.json','source-metadata.json','provenance.json',
                 'service-provenance.json','openeo-collection.json','eodash-config.json']:
        shutil.copy2(OUT/name,target/name)
    print('Packaged EOPF extract and GeoZarr')


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch',action='store_true')
    if parser.parse_args().fetch: fetch()
    package()
