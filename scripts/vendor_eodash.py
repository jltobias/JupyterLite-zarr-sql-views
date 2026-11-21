"""Project: Earth in the Browser; vendor_eodash.py; course contributors.
Created/updated: 2026-11-21. Contact/agency: not supplied.
Purpose: produce a documented, Git-free eodash frontend package for npm ci.
Input: official npm eodash 5.10.0 tarball, verified against registry integrity.
Output: vendor/eodash/eodash-5.10.0-classroom.tgz and provenance.
Dependencies: Python 3.12+, requests, truststore. Native-only maintenance utility.
Notes: remove optional animated-details import/attribute and its Git dependency;
native HTML details controls remain. Fix STAC dependency to the API used by 5.10.
Change log: 2026-11-21 initial narrowly modified MIT package.
"""
from pathlib import Path
import base64, gzip, hashlib, io, json, tarfile
import truststore
truststore.inject_into_ssl()
import requests

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'vendor/eodash';OUT.mkdir(parents=True,exist_ok=True)
metadata=requests.get('https://registry.npmjs.org/@eodash/eodash/5.10.0',timeout=30)
metadata.raise_for_status();dist=metadata.json()['dist']
response=requests.get(dist['tarball'],timeout=60);response.raise_for_status()
assert 'sha512-'+base64.b64encode(hashlib.sha512(response.content).digest()).decode()==dist['integrity']
changed=[]
buffer=io.BytesIO()
with tarfile.open(fileobj=io.BytesIO(response.content),mode='r:gz') as source, tarfile.open(fileobj=buffer,mode='w') as target:
    for member in source.getmembers():
        if not member.isfile(): continue
        assert member.name.startswith('package/') and '..' not in Path(member.name).parts
        raw=source.extractfile(member).read()
        if member.name=='package/package.json':
            package=json.loads(raw)
            assert package['dependencies'].pop('animated-details').startswith('gist:')
            package['dependencies']['@eodash/stac']='0.2.0'
            # The archive already contains built artifacts. Do not run upstream
            # monorepo build commands when consumers install this local tarball.
            package.get('scripts',{}).pop('prepare',None)
            raw=(json.dumps(package,indent=2)+'\n').encode();changed.append(member.name)
        elif member.name.endswith(('.js','.vue')):
            text=raw.decode('utf-8')
            if 'import "animated-details";' in text:
                text=text.replace('import "animated-details";','// Classroom adaptation: use native HTML details, without optional animation.')
                text=text.replace('is="animated-details"','').replace('is: "animated-details",','')
                raw=text.encode('utf-8');changed.append(member.name)
        # Fixed metadata makes the adapted archive reproducible.
        info=tarfile.TarInfo(member.name);info.size=len(raw);info.mode=0o644;info.mtime=0
        target.addfile(info,io.BytesIO(raw))
assert len(changed)==3,changed
output=OUT/'eodash-5.10.0-classroom.tgz'
output.write_bytes(gzip.compress(buffer.getvalue(),mtime=0))
# npm can otherwise reuse a cached local tarball after this file is regenerated.
# Keep its content integrity synchronized before any subsequent npm ci.
lock_path=ROOT/'package-lock.json'
if lock_path.exists():
    lock=json.loads(lock_path.read_text())
    entry=lock['packages'].get('node_modules/@eodash/eodash')
    if entry and entry.get('resolved')=='file:vendor/eodash/eodash-5.10.0-classroom.tgz':
        entry['integrity']='sha512-'+base64.b64encode(hashlib.sha512(output.read_bytes()).digest()).decode()
        lock_path.write_text(json.dumps(lock,indent=2)+'\n',encoding='utf-8')
(OUT/'provenance.json').write_text(json.dumps({'version':'5.10.0','retrieved':'2026-11-21',
    'source':dist['tarball'],'source_integrity':dist['integrity'],
    'source_sha256':hashlib.sha256(response.content).hexdigest(),
    'adapted_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
    'changed_files':changed,'changes':['Remove optional animated-details import and customized built-in attribute; retain native HTML details','Remove Git-only animated-details dependency','Pin @eodash/stac 0.2.0 to match imported exports','Omit monorepo prepare lifecycle script from the already-built archive']},indent=2)+'\n')
print('Adapted',len(changed),'files;',output.stat().st_size,'bytes; no Git dependency')
