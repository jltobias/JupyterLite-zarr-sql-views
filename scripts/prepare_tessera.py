"""Extract six bounded GeoTessera windows, then build browser teaching artifacts.

Native Python only: install requirements-tessera.txt in a separate environment.
Default rebuilds from checked-in extracts without contacting the data service.
--fetch reads the pinned Icechunk snapshot (or pins the first snapshot on first use).
--fetch reuses verified local extracts; remove an extract explicitly to refetch it.
The 64x64 geographic sample grid selects individual 10 m source pixels, not averages.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
import numpy as np
from prepare_data import cube, write_json, MANIFEST

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'notebooks/data'
PROVENANCE = DATA / 'tessera-provenance.json'
STORE = 's3://tessera-embeddings/v1.1/dclimate.icechunk'
COMMIT = '2814c5b3d967e0247f50e7b8d825efdf4fd606a6'
YEARS = [2018, 2021, 2025]
CITIES = [('lagos', 'Lagos / Apapa vicinity', 3.363, 6.439),
          ('abidjan', 'Abidjan / Treichville vicinity', -4.005, 5.295)]
COUNTS = ['s2_obs_count', 's1_asc_obs_count', 's1_desc_obs_count']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fetch():
    # Import only in the optional native fetch path.
    from geotessera.icechunk import IcechunkStore
    from pyproj import Transformer
    old = json.loads(PROVENANCE.read_text()) if PROVENANCE.exists() else {}
    store = IcechunkStore(STORE, snapshot_id=old.get('snapshot_id'))
    snapshot = store.session.snapshot_id
    root_attrs = dict(store.root.attrs)
    assert root_attrs['geoemb:dimensions'] == 128
    record = dict(provider='TESSERA / University of Cambridge; dClimate global inference and hosting',
                  dataset_version='1.1', dataset_variant='dclimate', store=STORE,
                  snapshot_id=snapshot, geotessera_commit=COMMIT, root_attributes=root_attrs,
                  years=YEARS, license='CC0-1.0', license_url='https://creativecommons.org/publicdomain/zero/1.0/',
                  paper='https://doi.org/10.48550/arXiv.2506.20380',
                  source_docs='https://github.com/dClimate/tessera-embeddings/blob/main/docs/global-store.md',
                  method='64 x 64 regular WGS84 query points per city. Each selects the containing native 10 m UTM pixel; no averaging or nearest-valid fill. Native pixel centers retained. Missing/invalid scales remain missing.',
                  coverage_note='Missing is not a water mask. Annual optical/radar observation counts are retained; counts are not confidence scores.',
                  cities=[], artifacts=[])
    for key, title, lon, lat in CITIES:
        zone = int((lon + 180) // 6) + 1
        ds = store.open_zone(zone)
        crs = ds.attrs['proj:code']
        xs, ys = ds.x.values, ds.y.values
        lons = lon + (np.arange(64) + .5 - 32) * .024 / 64
        lats = lat - (np.arange(64) + .5 - 32) * .024 / 64
        xx, yy = np.meshgrid(lons, lats)
        east, north = Transformer.from_crs('EPSG:4326', crs, always_xy=True).transform(xx, yy)
        cols = np.floor((east - (xs[0]-5)) / 10).astype(int)
        rows = np.floor(((ys[0]+5) - north) / 10).astype(int)
        r0, r1, c0, c1 = int(rows.min()), int(rows.max()+1), int(cols.min()), int(cols.max()+1)
        assert 0 <= r0 < r1 <= len(ys) and 0 <= c0 < c1 <= len(xs)
        assert r1-r0 <= 280 and c1-c0 <= 280, 'Stop: unexpected source window size'
        native_lon, native_lat = Transformer.from_crs(crs, 'EPSG:4326', always_xy=True).transform(xs[cols], ys[rows])
        offset = np.hypot(xs[cols]-east, ys[rows]-north)
        assert offset.max() <= np.sqrt(50)+1e-6
        city = dict(id=key, title=title, center=[lon, lat], query_bounds=[lon-.012,lat-.012,lon+.012,lat+.012],
                    source_crs=crs, source_zone=f'{zone:02d}N', source_window=[r0,r1,c0,c1],
                    query_grid_shape=[64,64], query_spacing_degrees=.000375,
                    source_pixel_size_m=10, max_query_to_pixel_center_m=float(offset.max()))
        assert all(y in store.root[city['source_zone']].attrs['years_complete'] for y in YEARS)
        record['cities'].append(city)
        for year in YEARS:
            path = DATA / f'tessera_{key}_{year}.npz'
            previous = next((a for a in old.get('artifacts',[]) if a['file']==path.name), None)
            if path.exists() and previous and sha(path)==previous['sha256']:
                record['artifacts'].append(previous)
                print('Verified cache', path.name, flush=True)
                continue
            print('Reading', key, year, (r1-r0,c1-c0), 'native pixels', flush=True)
            window = ds.sel(time=year).isel(y=slice(r0,r1),x=slice(c0,c1))
            q = window.embeddings.values[:, rows-r0, cols-c0].transpose(1,2,0).copy()
            scales = window.scales.values[rows-r0, cols-c0].copy()
            assert q.shape == (64,64,128) and q.dtype == np.int8
            counts = {name:window[name].values[rows-r0,cols-c0].copy() for name in COUNTS}
            np.savez_compressed(path, quantized=q, scales=scales, lon=lons, lat=lats,
                                native_lon=native_lon, native_lat=native_lat, **counts)
            record['artifacts'].append(dict(file=path.name, sha256=sha(path), bytes=path.stat().st_size,
                                            retrieved_utc=datetime.now(timezone.utc).isoformat()))
            # Persist after each fetch so interruption does not discard completed work.
            write_json(PROVENANCE, record)
    write_json(PROVENANCE, record)


def derive():
    sys.path.insert(0, str(ROOT/'notebooks'))
    from tessera import load_tessera, unit_vectors
    p = json.loads(PROVENANCE.read_text())
    for a in p['artifacts']:
        assert sha(DATA/a['file']) == a['sha256'], 'Source extract checksum mismatch'
    for key, title, _, _ in CITIES:
        d = load_tessera(key, data_dir=DATA)
        vectors = unit_vectors(d['embedding'])
        reference_row, reference_col = 32, 32
        reference = vectors[-1, reference_row, reference_col]
        assert np.isfinite(reference).all(), 'Choose and document a valid reference'
        similarity = np.clip(np.sum(vectors * reference, axis=-1), -1, 1)
        extra = dict(source='TESSERA v1.1 / dClimate; Sentinel-1 and Sentinel-2', license='CC0-1.0',
                     provenance='tessera-provenance.json', dataset_version='1.1', dataset_variant='dclimate',
                     snapshot_id=p['snapshot_id'], statistic='cosine similarity to one fixed 2025 reference vector',
                     reference=dict(year=2025,row=32,col=32,query_lon=float(d['lon'][32]),query_lat=float(d['lat'][32]),
                                    native_lon=float(d['native_lon'][32,32]),native_lat=float(d['native_lat'][32,32])),
                     sampling='Individual 10 m source pixels at geographic query centers spaced about 42 m; not area averages.')
        cube(f'tessera_{key}', title+' / embedding similarity', similarity, d['lon'],d['lat'],
             list(map(str,YEARS)), 'cosine similarity (dimensionless)', 'embedding',
             'TESSERA v1.1 dClimate annual embeddings, compared with a fixed 2025 center-pixel vector. '+
             'Similarity is not a class probability, flood depth, or climate trend. Query spacing about 42 m; '+
             'values come from individual 10 m pixels. Vertical height is a score, not terrain.', 'ocean',extra)
    previous = json.loads((ROOT/'public/data/catalog.json').read_text())
    combined = [m for m in previous if not m['id'].startswith('tessera_')] + MANIFEST
    write_json(ROOT/'public/data/catalog.json',combined)
    write_json(DATA/'catalog.json',combined)
    write_json(ROOT/'public/data/tessera-provenance.json',p)
    print('Prepared',len(MANIFEST),'embedding similarity cubes')


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--fetch', action='store_true')
    args=parser.parse_args()
    if args.fetch:
        fetch()
    derive()
