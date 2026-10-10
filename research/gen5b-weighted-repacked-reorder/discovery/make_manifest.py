"""Rewrite MANIFEST.json for the package (same rule as verify.integrity)."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
p=ROOT/'MANIFEST.json';old=json.loads(p.read_text());actual={}
for q in ROOT.rglob('*'):
    if '__pycache__' in q.parts:continue
    if q.is_file() and q.name!='MANIFEST.json':actual[q.relative_to(ROOT).as_posix()]=hashlib.sha256(q.read_bytes()).hexdigest()
for q in ROOT.rglob('MANIFEST.json'):
    if q!=p:actual[q.relative_to(ROOT).as_posix()]=hashlib.sha256(q.read_bytes()).hexdigest()
new=dict(old);new['files']=dict(sorted(actual.items()))
p.write_text(json.dumps(new,indent=1,sort_keys=True)+'\n');print('manifest files',len(actual))
