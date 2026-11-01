"""Offline integrity, spatial support, SQL and missing-data checks for FTW."""
from pathlib import Path
import hashlib
import json
import sys
import tempfile
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'notebooks'))
from ftw import load_ftw, field_connection, paired_difference, export_fields

DATA=ROOT/'notebooks/data'
p=json.loads((DATA/'ftw-provenance.json').read_text(encoding='utf-8'))
assert (DATA/'ftw-provenance.json').read_bytes()==(ROOT/'public/data/ftw-provenance.json').read_bytes()
assert p['license']=='CC-BY-4.0' and not p['catalog_commit_pins_data']
for item in p['artifacts']:
    raw=(DATA/item['file']).read_bytes()
    assert len(raw)==item['bytes'] and hashlib.sha256(raw).hexdigest()==item['sha256']
for obj in p['source_objects']:
    assert obj['etag'] and obj['bytes']>0 and obj['url'].startswith(p['physical_base'])
    if 'row_groups' in obj:
        assert obj['bytes_transferred']<=128*1024**2 and len(obj['row_groups'])<=8
        assert obj['bytes_transferred']<obj['bytes']
catalog=json.loads((ROOT/'public/data/catalog.json').read_text())
for key,counts in [('senegal',[20,24]),('kenya',[322,320])]:
    d=load_ftw(key,DATA); a=d['probability']; region=d['region']
    assert a.shape==(2,3,128,128) and a.dtype==np.float32
    finite=np.isfinite(a)
    assert np.array_equal(finite[:,0],finite[:,1]) and np.array_equal(finite[:,1],finite[:,2])
    assert a[finite].min()>=0 and a[finite].max()<=1
    np.testing.assert_allclose(a.sum(axis=1)[finite[:,0]],1,atol=2e-6)
    r0,r1,c0,c1=region['source_window']; dx,_,x0,_,negdy,y0=p['source_transform']
    np.testing.assert_allclose(d['lon'],x0+(np.arange(c0,c1)+.5)*dx,atol=1e-8)
    np.testing.assert_allclose(d['lat'],y0+(np.arange(r0,r1)+.5)*negdy,atol=1e-8)
    np.testing.assert_allclose(region['bounds'],[d['lon'][0]-dx/2,d['lat'][-1]+negdy/2,
                                                d['lon'][-1]+dx/2,d['lat'][0]-negdy/2],atol=1e-8)
    con=field_connection(d)
    assert [r[0] for r in con.execute('SELECT COUNT(*) FROM fields GROUP BY year ORDER BY year')]==counts
    assert len({(f['properties']['year'],f['properties']['id']) for f in d['fields']['features']})==sum(counts)
    west,south,east,north=region['bounds']
    for f in d['fields']['features']:
        props=f['properties']; geom=f['geometry']
        assert props['metrics:area']>0 and props['metrics:perimeter']>0
        assert props['confidence'] is None or 0<=props['confidence']<=100
        assert props['admin:country_code']==region['country']
        assert str(props['year'])==props['determination:datetime'][:4]
        polygons=[geom['coordinates']] if geom['type']=='Polygon' else geom['coordinates']
        coords=np.array([xy for polygon in polygons for ring in polygon for xy in ring])
        assert np.isfinite(coords).all()
        x,y=coords[:,0],coords[:,1]
        assert x.max()>=west and x.min()<=east and y.max()>=south and y.min()<=north
        edge=bool(x.min()<west or x.max()>east or y.min()<south or y.max()>north)
        assert edge==props['crosses_window_edge']
    delta,valid=paired_difference(a)
    np.testing.assert_allclose(delta[valid],a[1,1][valid]-a[0,1][valid])
    meta=next(m for m in catalog if m['id']=='ftw_'+key)
    assert meta['kind']=='prediction' and meta['model']=='PRUE' and meta['citation']==p['paper']
    for t in range(2):
        raw=(ROOT/'public/data'/meta['store']/f'value/{t}.0.0').read_bytes()
        np.testing.assert_array_equal(np.frombuffer(raw,dtype='<f4').reshape(128,128),a[t,1])
    with tempfile.TemporaryDirectory() as folder:
        path=Path(folder)/'selection.geojson'
        n=export_fields(d,path,2025,69); obj=json.loads(path.read_text())
        assert n==con.execute('SELECT COUNT(*) FROM fields WHERE year=2025 AND confidence>=69').fetchone()[0]
        assert n==len(obj['features']) and obj['license']=='CC-BY-4.0' and obj['citation']==p['paper']
        assert obj['geometry_clipped'] is False and obj['selection']['missing_confidence']=='excluded'
    print(key,'probability, polygons, coordinates, SQL and export OK')
# Missing at either time must not become change; zero is a valid probability.
example=np.zeros((2,3,2,2),dtype=np.float32)
example[0,1,0,0]=np.nan; example[1,1,1,0]=np.nan; example[1,1,0,1]=.5
delta,valid=paired_difference(example)
assert valid.tolist()==[[False,True],[False,True]] and delta[0,1]==.5 and delta[1,1]==0
assert np.isnan(delta[~valid]).all()
try: load_ftw('../outside',DATA)
except ValueError: pass
else: raise AssertionError('Unknown region must be rejected')
# Keep editable notebooks synchronized with their maintainable lesson source.
from ftw_lessons import add_lessons
def check_lesson(slug,title,minutes,objectives,cells,sources,challenge,answer):
    n=json.loads((ROOT/'notebooks'/f'{slug}.ipynb').read_text(encoding='utf-8'))
    actual=[(c['cell_type'],''.join(c['source'])) for c in n['cells'][2:-2]]
    assert actual==cells, f'Notebook/source drift: {slug}'
    assert n['metadata']['course']['minutes']==minutes
    for c in n['cells']:
        assert not any(ord(char)<32 and char not in '\n\t\r' for char in ''.join(c['source']))
add_lessons(check_lesson,lambda s:('markdown',s.strip()),lambda s:('code',s.strip()))
print('All FTW checks passed')
