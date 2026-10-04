"""Execute every lesson with a fresh native kernel; preserve outputs for the Book."""
from pathlib import Path
import nbformat
from nbclient import NotebookClient
ROOT=Path(__file__).resolve().parents[1]
for path in sorted((ROOT/'notebooks').glob('*.ipynb')):
    print('Executing',path.name,flush=True)
    book=nbformat.read(path,as_version=4)
    NotebookClient(book,timeout=180,kernel_name='python3',resources={'metadata':{'path':str(path.parent)}}).execute()
    nbformat.write(book,path)
print('All lessons executed successfully')
