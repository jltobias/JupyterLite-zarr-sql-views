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
    shutil.copytree(source,target,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','.ipynb_checkpoints','*.pyc','*-points.geojson','*-geolibre.geojson','optical-candidates.geojson','evidence-record.json'))

if not (ROOT/'dist/index.html').exists():
    raise SystemExit('Run npm run build first.')
# Only this generated directory may be removed; resolve before the recursive operation.
if SITE.exists():
    assert SITE.resolve().parent==ROOT.resolve() and SITE.name=='_site'
    shutil.rmtree(SITE)
copytree(ROOT/'dist',SITE)
copytree(ROOT/'public/assets',ROOT/'book/assets')
copytree(ROOT/'notebooks',ROOT/'book/notebooks')
run(sys.executable,'-c','from jupyter_book.cli.main import main; main()','build','book','--warningiserror','--keep-going')
copytree(ROOT/'book/_build/html',SITE/'book')
run(sys.executable,'-c','from jupyterlite_core.app import main; main()','build','--contents','notebooks','--output-dir',SITE/'lite')
copytree(ROOT/'notebooks',SITE/'downloads/notebooks')
copytree(ROOT/'licenses',SITE/'licenses')
for name in ['LICENSE','THIRD_PARTY_NOTICES.md','CITATION.cff']:
    shutil.copy2(ROOT/name,SITE/name)
(SITE/'.nojekyll').touch()
print('Site assembled at',SITE)
