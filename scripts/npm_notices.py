"""Collect installed dependency license/notice texts for static bundle distribution."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
lock=json.loads((ROOT/'package-lock.json').read_text())
parts=['JavaScript dependency attribution inventory\nGenerated from package-lock.json. Includes build/test tools as well as runtime dependencies.\n']
missing=[]
for rel,details in sorted(lock['packages'].items()):
    if not rel:continue
    folder=ROOT/rel
    if not folder.exists():continue # Optional packages for other operating systems.
    package=folder/'package.json'
    if not package.exists():continue
    p=json.loads(package.read_text(encoding='utf8'))
    parts.append(f"\n{'='*72}\n{p.get('name',rel)} {p.get('version','')}\nDeclared license: {p.get('license','See source')}\n")
    matches=[f for f in folder.iterdir() if f.is_file() and f.name.lower().startswith(('license','licence','notice','copying','copyright'))]
    if p.get('name')=='@duckdb/duckdb-wasm':matches=[ROOT/'licenses/duckdb-wasm-MIT.txt']
    if not matches:missing.append(p.get('name',rel))
    for f in sorted(matches):parts.append(f'\n--- {f.name} ---\n'+f.read_text(encoding='utf8',errors='replace'))
(ROOT/'licenses/npm-notices.txt').write_text('\n'.join(parts),encoding='utf8')
print('Wrote dependency notices; no root license file for:',', '.join(missing) or 'none')
