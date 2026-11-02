"""Assemble Vite, Jupyter Book, and JupyterLite under one relocatable Pages root."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'_site'
def run(*args):
    print('+',' '.join(map(str,args)),flush=True)
    subprocess.run(list(map(str,args)),cwd=ROOT,check=True)
def copytree(source,target):
    shutil.copytree(source,target,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','.ipynb_checkpoints','*.pyc','*-points.geojson','*-geolibre.geojson','optical-candidates.geojson','ar6-projections.geojson','ar6-lagos-grid.geojson','ftw-selected-fields.geojson','evidence-record.json','seasfire-selection.json'))

if not (ROOT/'dist/index.html').exists():
    raise SystemExit('Run npm run build first.')
# Only this generated directory may be removed; resolve before the recursive operation.
if SITE.exists():
    assert SITE.resolve().parent==ROOT.resolve() and SITE.name=='_site'
    shutil.rmtree(SITE)
copytree(ROOT/'dist',SITE)
copytree(ROOT/'public/assets',ROOT/'book/assets')
copytree(ROOT/'notebooks',ROOT/'book/notebooks')
# A static Book has no Python widget backend. Keep the executed reference plots,
# and link to JupyterLite instead of publishing disconnected widget models.
for path in (ROOT/'book/notebooks').glob('*.ipynb'):
    notebook=json.loads(path.read_text(encoding='utf-8'))
    notebook.get('metadata',{}).pop('widgets',None)
    for cell in notebook['cells']:
        if cell['cell_type']=='code':
            cell['outputs']=[o for o in cell.get('outputs',[])
                            if 'application/vnd.jupyter.widget-view+json' not in o.get('data',{})]
    path.write_text(json.dumps(notebook,ensure_ascii=False),encoding='utf-8')
run(sys.executable,'-c','from jupyter_book.cli.main import main; main()','build','book','--warningiserror','--keep-going')
copytree(ROOT/'book/_build/html',SITE/'book')
run(sys.executable,'-c','from jupyterlite_core.app import main; main()','build','--contents','notebooks',
    '--extra-ignore-contents',r'/(ftw-(probability-points|selected-fields)\.geojson|seasfire-selection\.json)$', '--output-dir',SITE/'lite')
copytree(ROOT/'notebooks',SITE/'downloads/notebooks')
copytree(ROOT/'licenses',SITE/'licenses')
for name in ['LICENSE','THIRD_PARTY_NOTICES.md','CITATION.cff']:
    shutil.copy2(ROOT/name,SITE/name)
(SITE/'.nojekyll').touch()
print('Site assembled at',SITE)
