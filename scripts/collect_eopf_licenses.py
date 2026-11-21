"""Project: Earth in the Browser; collect_eopf_licenses.py; course contributors.
Created/updated: 2026-11-21. Contact/agency: not supplied.
Purpose: preserve installed runtime dependency legal notices with the site.
Input: package-lock.json and node_modules (npm ci). Output: public/vendor/eopf/npm-licenses.txt.
Dependencies: Python 3.12+ standard library. No network or package mutations.
Notes: includes runtime dependencies shared by the lab and EOPF frontend;
metadata is reported separately when a package supplies no top-level notice.
Change log: initial runtime notice bundle.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
lock=json.loads((ROOT/'package-lock.json').read_text())
parts=['Runtime dependency notices for Earth in the Browser 0.6.0\nGenerated from the pinned npm lockfile. Source packages retain their own licenses.\n']
for key, entry in sorted(lock['packages'].items()):
    if not key or entry.get('dev') or entry.get('devOptional'): continue
    folder=ROOT/key
    if not (folder/'package.json').exists(): continue
    metadata=json.loads((folder/'package.json').read_text(encoding='utf-8'))
    parts.append('\n'+'='*78+'\n'+metadata['name']+' '+metadata['version']+'\n')
    parts.append('Declared license: '+str(metadata.get('license','not declared'))+'\n')
    parts.append('Repository: '+json.dumps(metadata.get('repository',{}))+'\n')
    files=[p for p in sorted(folder.iterdir()) if p.is_file() and p.name.lower().split('.')[0] in ['license','licence','notice','copying','copyright']]
    if not files: parts.append('No top-level legal text was included in this package; consult its declared license and source.\n')
    for file in files:
        parts.extend(['\n--- '+file.name+' ---\n',file.read_text(encoding='utf-8',errors='replace'),'\n'])
out=ROOT/'public/vendor/eopf/npm-licenses.txt';out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(''.join(parts),encoding='utf-8')
print('Preserved npm runtime notices:',out.stat().st_size,'bytes')
