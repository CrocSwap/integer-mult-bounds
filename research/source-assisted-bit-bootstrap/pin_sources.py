#!/usr/bin/env python3
"""Pin this package and require all immutable PR185 ancestry pins to hold."""
if not __debug__: raise RuntimeError('Do not run source pinning with -O')
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
parent_dir=ROOT/'research/bit-leaf-bootstrap182';p=parent_dir/'SOURCE.json';parent=json.loads(p.read_text())
digest=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
repo=dict(parent['repository_files'])
for name,sha in parent['package_files'].items():repo[str((parent_dir/name).relative_to(ROOT))]=sha
for name,sha in repo.items():assert digest(ROOT/name)==sha,('Immutable ancestry drift',name)
repo[str(p.relative_to(ROOT))]=digest(p)
workflow=ROOT/'.github/workflows/source-assisted-bit-bootstrap.yml'
if workflow.exists():repo[str(workflow.relative_to(ROOT))]=digest(workflow)
for row in json.loads((HERE/'baseline-185-equality.json').read_text()):
 assert digest(ROOT/row['path'])==row['sha256'];repo[row['path']]=row['sha256']
own={str(f.relative_to(HERE)):digest(f) for f in sorted(HERE.rglob('*')) if f.is_file() and f.name not in ('SOURCE.json','validation.json') and '__pycache__' not in f.parts}
(HERE/'SOURCE.json').write_text(json.dumps(dict(parent_commit='32daefe471e1e41926971747bb901e2839938b43',source_assisted_reference='4b5fc7fb45a77b6c7b9d886d30ad5b57eae553fa',bit_input_commit='2c4a380126640abfcdce398ced255d1dd5d1d007',repository_files=repo,package_files=own,scope='Immutable PR185 ancestry, exact newer PR168 BIT inputs, new complete source-assisted word compiler and audits. Own validation receipt excluded.'),sort_keys=True,indent=2)+'\n')
print(len(repo),'repository pins;',len(own),'own pins')
