"""Bounded native extraction from ESA's SeasFire v0.4 Zarr mirror.

Default rebuilds the browser cubes offline. --fetch downloads only the source
chunks intersecting two 16x16 windows (large source chunks, <= 1.5 GiB total).
Run with requirements-seasfire.txt; never run the refresh inside JupyterLite.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
import numpy as np
from prepare_data import cube, write_json, MANIFEST

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'notebooks/data'
BASE = 'https://s3.waw4-1.cloudferro.com/EarthCODE/OSCAssets/seasfire/seasfire_v0.4.zarr/'
VARIABLES = ['gwis_ba', 'tp', 'vpd', 't2m_mean', 'ndvi', 'area', 'lsm']
REGIONS = [('ghana', 'Northern Ghana and neighboring savannas', -3.0, 9.5),
           ('zambia', 'Central Zambia and neighboring savannas', 27.5, -13.5)]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def fetch():
    import truststore
    truststore.inject_into_ssl()
    import requests
    from numcodecs import get_codec
    session = requests.Session()
    cache = ROOT / '.work/seasfire-chunks'
    cache.mkdir(parents=True, exist_ok=True)
    objects = {}
    total = 0

    def read(path):
        nonlocal total
        if path in objects:
            return (cache / path.replace('/', '__')).read_bytes()
        url = BASE + path
        head = session.head(url, timeout=90)
        head.raise_for_status()
        size = int(head.headers['Content-Length'])
        assert size <= 256 * 1024**2, 'Per-object transfer budget exceeded'
        total += size
        assert total <= 1536 * 1024**2, 'Total source transfer budget exceeded'
        local = cache / path.replace('/', '__')
        sidecar = local.with_name(local.name + '.json')
        info = dict(url=url, bytes=size, etag=head.headers.get('ETag'),
                    last_modified=head.headers.get('Last-Modified'))
        cached = json.loads(sidecar.read_text()) if sidecar.exists() else {}
        if not (local.exists() and cached.get('etag') == info['etag'] and
                len(local.read_bytes()) == size and sha(local.read_bytes()) == cached.get('sha256')):
            print('Downloading', path, round(size / 1024**2, 2), 'MiB', flush=True)
            with session.get(url, headers={'If-Match': info['etag']}, stream=True, timeout=180) as response:
                response.raise_for_status()
                raw = response.raw.read(size + 1, decode_content=True)
            assert len(raw) == size
            local.write_bytes(raw)
        raw = local.read_bytes()
        info['sha256'] = sha(raw)
        write_json(sidecar, info)
        objects[path] = info
        return raw

    raw = read('.zmetadata')
    (DATA / 'seasfire-zmetadata.json').write_bytes(raw)
    metadata = json.loads(raw)['metadata']

    def chunk(name, indices):
        spec = metadata[name + '/.zarray']
        assert spec['order'] == 'C' and spec['filters'] is None
        raw = read(name + '/' + '.'.join(map(str, indices)))
        decoded = get_codec(spec['compressor']).decode(raw)
        return np.frombuffer(decoded, dtype=spec['dtype']).reshape(spec['chunks'])

    days = chunk('time', [0]).copy()
    lon = chunk('longitude', [0]).copy()
    lat = chunk('latitude', [0]).copy()
    valid = chunk('gwis_ba_valid_mask', [0]).copy()
    assert metadata['time/.zattrs']['units'] == 'days since 2001-01-01'
    dates = np.datetime64('2001-01-01') + days.astype('timedelta64[D]')
    regions = []
    for key, title, x, y in REGIONS:
        c = int(np.argmin(abs(lon - x))); r = int(np.argmin(abs(lat - y)))
        r0, r1, c0, c1 = r-8, r+8, c-8, c+8
        # All selected windows fit inside a single source spatial chunk.
        assert r0//180 == (r1-1)//180 and c0//360 == (c1-1)//360
        out = dict(lon=lon[c0:c1], lat=lat[r0:r1], days=days, gwis_ba_valid_mask=valid)
        for name in VARIABLES:
            indices = ([0] if name not in ['area', 'lsm'] else []) + [r0//180, c0//360]
            a = chunk(name, indices)
            out[name] = a[..., r0%180:r0%180+16, c0%360:c0%360+16].copy()
            del a
        filename = f'seasfire_{key}.npz'
        np.savez_compressed(DATA / filename, **out)
        regions.append(dict(id=key, title=title, file=filename, shape=list(out['gwis_ba'].shape),
                            source_rows=[r0,r1], source_columns=[c0,c1],
                            bounds=[float(lon[c0]-.125),float(lat[r1-1]-.125),
                                    float(lon[c1-1]+.125),float(lat[r0]+.125)]))
        print(key, str(dates[0]), str(dates[-1]), 'fire mask:',np.unique(valid,return_counts=True), flush=True)
    artifacts = [dict(file=name, sha256=sha((DATA/name).read_bytes()), bytes=(DATA/name).stat().st_size)
                 for name in ['seasfire-zmetadata.json'] + [r['file'] for r in regions]]
    provenance = dict(dataset='SeasFire Cube', version='0.4',
        source='https://opensciencedata.esa.int/products/seasfire-cube/item',
        doi='https://doi.org/10.5281/zenodo.13834057',
        paper='https://doi.org/10.1038/s41597-025-04546-3',
        license='CC-BY-4.0', license_url='https://creativecommons.org/licenses/by/4.0/',
        creators='Alonso, Gans, Karasante, Ahuja, Prapas, Kondylatos, Papoutsis, Panagiotou, Michail, Cremer, Weber and Carvalhais',
        inputs='GWIS burned area; ERA5 weather and land-sea mask; MODIS MOD13C1 v6 NDVI; derived vapor pressure deficit and cell area',
        retrieved_utc=datetime.now(timezone.utc).isoformat(), base=BASE,
        method='Contiguous 16x16 native 0.25 degree pixels, all 966 periods. No spatial resampling. Raw source values retained in NPZ; availability mask applied by lesson helpers and lab cube preparation.',
        temporal_support='Source timestamps start nominal 8-day bins, reset January 1 each year; final annual bins have 5 or 6 days. GWIS allocated by fire ignition date. 2001 unavailable, not zero fire.',
        limitations='Historical observations, reanalysis and derived variables, not forecasts or causal estimates. Selected cross-border windows are not country summaries. Interpolated/harmonized variables may leak information in predictive studies.',
        regions=regions, artifacts=artifacts, source_objects=list(objects.values()),
        source_object_bytes=total)
    write_json(DATA/'seasfire-provenance.json', provenance)


def build():
    p = json.loads((DATA/'seasfire-provenance.json').read_text(encoding='utf-8'))
    for artifact in p['artifacts']:
        assert sha((DATA/artifact['file']).read_bytes()) == artifact['sha256']
    for region in p['regions']:
        with np.load(DATA/region['file'], allow_pickle=False) as d:
            dates = np.datetime64('2001-01-01') + d['days'].astype('timedelta64[D]')
            selection = dates >= np.datetime64('2018-01-01')
            values = np.where(d['gwis_ba_valid_mask'][:,None,None] == 1, d['gwis_ba'], np.nan)[selection]
            cube('seasfire_'+region['id'], region['title']+' · SeasFire burned area', values,
                 d['lon'], d['lat'], [str(t) for t in dates[selection]],
                 'burned area (ha / grid cell / period)', 'historical',
                 'GWIS burned area allocated by ignition date, harmonized in SeasFire v0.4. Native 0.25 degree cells; final annual bins are shorter. Historical estimate, not active-fire alerts, a forecast, or terrain.',
                 'ember', dict(source='SeasFire / GWIS; ESA EarthCODE mirror', license=p['license'],
                    license_url=p['license_url'], provenance='seasfire-provenance.json',
                    citation=p['doi'], dataset_version='0.4', variable='gwis_ba',
                    sampling=p['method'], temporal_support=p['temporal_support']))
    catalog = json.loads((ROOT/'public/data/catalog.json').read_text(encoding='utf-8'))
    catalog = [r for r in catalog if not r['id'].startswith('seasfire_')] + MANIFEST
    for folder in [ROOT/'public/data', DATA]:
        write_json(folder/'catalog.json',catalog)
    for name in ['seasfire-provenance.json','seasfire-zmetadata.json']:
        shutil.copy2(DATA/name, ROOT/'public/data'/name)
    print('SeasFire classroom cubes ready')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true')
    if parser.parse_args().fetch:
        fetch()
    build()
