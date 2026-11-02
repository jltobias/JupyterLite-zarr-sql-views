"""Fetch unmodified, hash-pinned LexCube 2.0.1 binary and corresponding source."""
from pathlib import Path
import hashlib
import tarfile
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'public/vendor/lexcube'
FILES=[
 ('lexcube-2.0.1-py3-none-any.whl','30/bd/c8d334d8b2fbcebff4ab93db47d4eb79d5ed349ae90110cd933f14f14014','9b4be927663d48139136260edfe4b7d6b3e78bf56fbc917881a47330f073ba5e'),
 ('lexcube-2.0.1.tar.gz','88/4d/f73cc04246b6ffd3a9bece5ad0c2cd375b0013f356e59d7341fbe6d2d1cb','6ffa67f254cbe5a99e40335a070ee248d9c0e6bb1994f5367c4392bc776d9f43')]
if __name__=='__main__':
    DEST.mkdir(parents=True,exist_ok=True)
    for name,path,digest in FILES:
        target=(ROOT/'notebooks/wheels'/name) if name.endswith('.whl') else DEST/name
        target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists():
            with urllib.request.urlopen('https://files.pythonhosted.org/packages/'+path+'/'+name,timeout=120) as r:
                raw=r.read(12*1024**2)
            assert hashlib.sha256(raw).hexdigest()==digest
            target.write_bytes(raw)
        assert hashlib.sha256(target.read_bytes()).hexdigest()==digest
    with tarfile.open(DEST/FILES[1][0]) as archive:
        names=archive.getnames()
        assert any('/src/' in n and n.endswith('.ts') for n in names), 'Require frontend source'
        license_name=next(n for n in names if n.endswith('/COPYING'))
        (ROOT/'licenses/lexcube-GPL-3.0.txt').write_bytes(archive.extractfile(license_name).read())
    print('LexCube wheel, corresponding source and GPL text verified')
