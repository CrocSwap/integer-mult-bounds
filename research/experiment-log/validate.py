from pathlib import Path
import json,hashlib,re
p=Path(__file__).resolve().parent
manifest=json.loads((p/'MANIFEST.json').read_text())
actual={f.relative_to(p).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in p.rglob('*') if f.is_file() and f.name!='MANIFEST.json' and '__pycache__' not in f.parts}
assert actual==manifest
ideas=json.loads((p/'campaign-100/results.json').read_text());assert sorted(x['id'] for x in ideas)==list(range(1,101))
for name in ['from-scratch','retain-and-repair']:
 x=json.loads((p/('kernel-search/'+name+'-100.json')).read_text());assert sorted(z['label']['trial'] for z in x['trials'])==list(range(100))
rows=json.loads((p/'kernel-search/factored-warm-ledger.json').read_text());assert len(rows)==101 and sorted(x['label']['trial'] for x in rows[1:])==list(range(100))
for f in p.rglob('*.md'):
 for link in re.findall(r'\]\(([^)]+)\)',f.read_text()):
  if '://' not in link:assert (f.parent/link.split('#')[0]).exists(),(f,link)
print('PASS archive integrity,100 original idea IDs,300 trial IDs and local links; no historical mathematical replay claimed')
