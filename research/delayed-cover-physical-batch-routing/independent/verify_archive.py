"""Read-only exact transport check for this internal review. Apache-2.0."""
from pathlib import Path
from hashlib import sha256
import json
here=Path(__file__).resolve().parent
manifest=json.loads((here/'FILES.json').read_text())
expected={x['path'] for x in manifest['files']}
actual={str(x.relative_to(here)) for x in here.rglob('*') if x.is_file() and x.name!='FILES.json'}
if expected!=actual:raise ValueError('Exact payload set differs')
for x in manifest['files']:
    raw=(here/x['path']).read_bytes()
    if len(raw)!=x['bytes'] or sha256(raw).hexdigest()!=x['sha256']:raise ValueError(x['path'])
print('PASS_INDEPENDENT_PHYSICAL_ROUTER_ARCHIVE',len(expected))
