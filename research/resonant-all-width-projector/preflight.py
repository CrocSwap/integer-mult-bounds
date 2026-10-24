from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent
m=json.loads((P/'MANIFEST.json').read_text(encoding='utf8'))
a={f.relative_to(P).as_posix() for f in P.rglob('*') if f.is_file() and '__pycache__' not in f.parts and f.name!='MANIFEST.json'}
if a!=set(m):raise ValueError('Manifest inventory mismatch')
for n,h in m.items():
 if hashlib.sha256((P/n).read_bytes()).hexdigest()!=h:raise ValueError('Source drift: '+n)
print('PASS_RESONANT_PACKAGE_BYTES')
