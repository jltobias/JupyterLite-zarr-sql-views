"""Check provenance, all per-year quantiles, orientation, city matching and exports."""
from pathlib import Path
import hashlib
import json
import sys
import zipfile
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'notebooks'))
import ar6
ar6.DATA=ROOT/'notebooks/data'
p,years,gauge,grid=ar6.load_ar6()
assert gauge.shape==(2,20000,9,4) and grid.shape==(20000,9,5)
assert np.isfinite(gauge).all() and np.isfinite(grid).all()
assert years.tolist()==list(range(2020,2101,10))
assert p['cities'][0]['gauge_column']==p['cities'][1]['gauge_column']==1
assert p['gauges'][1]['name']=='TAKORADI'
assert round(p['cities'][0]['gauge_distance_km'])==256
assert round(p['cities'][1]['gauge_distance_km'])==595
assert p['workflow']=='wf_1e' and p['baseline']=='1995–2014'
for name,info in p['artifacts'].items():
    raw=(ar6.DATA/name).read_bytes()
    assert len(raw)==info['bytes'] and hashlib.sha256(raw).hexdigest()==info['sha256']
assert (ar6.DATA/'ar6-provenance.json').read_bytes()==(ROOT/'public/data/ar6-provenance.json').read_bytes()
assert len([r for r in p['source_objects'] if '/sea_level_change/' in r['url']])==48
assert all('requesterpays' not in r['url'] for r in p['source_objects'])
# Source-derived regression references, in mm before conversion.
np.testing.assert_allclose(np.median(gauge[:,:,8,:],axis=1),[[.957,.508,1.524,.442],[1.281,.848,1.848,.764]],atol=1e-9)
summary=ar6.gauge_summary(p,years,gauge)
assert len(summary)==72 and len({(r['gauge_id'],r['scenario'],r['year']) for r in summary})==72
con=ar6.summary_sql(summary)
assert con.execute('SELECT COUNT(DISTINCT gauge_id) FROM projections').fetchone()[0]==4
assert con.execute("SELECT p50_m FROM projections WHERE gauge_id=331 AND year=2100 AND scenario='ssp585'").fetchone()[0]==.848
con.close()
records=json.loads((ar6.DATA/'ar6-grid-summary.json').read_text())
for ci,city in enumerate(p['cities']):
    with zipfile.ZipFile(ar6.DATA/('ar6_'+city['id']+'.zip')) as z:
        meta=json.loads(z.read('.zattrs'))
        values=np.stack([np.frombuffer(z.read(f'value/{t}.0.0'),dtype='<f4').reshape(5,5) for t in range(9)])
    assert np.all(np.diff(meta['lat'])<0) and np.all(np.diff(meta['lon'])>0)
    rows=[r for r in records if r['city']==city['name']]
    for r in rows:
        y=meta['lat'].index(r['lat']);x=meta['lon'].index(r['lon']);t=meta['times'].index(str(r['year']))
        np.testing.assert_allclose(values[t,y,x],r['p50_m'],rtol=1e-6)
        assert r['p17_m']<=r['p50_m']<=r['p83_m'] and r['n']==20000
    assert np.isfinite(values).sum()==len(rows)
    point=city['grid']; near=[r for r in rows if r['lat']==point['lat'] and r['lon']==point['lon']]
    q=np.quantile(grid[:,:,ci],[.17,.5,.83],axis=0,method='linear')
    for r in near:
        t=list(years).index(r['year'])
        np.testing.assert_allclose(q[:,t],[r['p17_m'],r['p50_m'],r['p83_m']],rtol=1e-12)
    distance=6371.0088*2*np.arcsin(np.sqrt(np.sin(np.radians(point['lat']-city['lat'])/2)**2+np.cos(np.radians(city['lat']))*np.cos(np.radians(point['lat']))*np.sin(np.radians(point['lon']-city['lon'])/2)**2))
    np.testing.assert_allclose(distance,point['distance_km'])
print('AR6 source hashes, 72 gauge summaries, 5 grid windows, units, quantiles, and geographic orientation verified')
