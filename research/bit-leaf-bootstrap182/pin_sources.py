#!/usr/bin/env python3
"""Pin own files while requiring the immutable parent's existing pins to hold."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
p=ROOT/'research/paired-cube-local-bit-168/SOURCE.json'
parent=json.loads(p.read_text());repo=dict(parent['files'])
for path,digest in repo.items():
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,('Parent drift',path)
repo[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
own={str(f.relative_to(HERE)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(HERE.rglob('*'))
 if f.is_file() and f.name not in ('SOURCE.json','validation.json') and '__pycache__' not in f.parts}
(HERE/'SOURCE.json').write_text(json.dumps(dict(parent_commit='af90b94783f7d104a0be75c762ade758bec75855',
 repository_files=repo,package_files=own,scope='Immutable PR182 parent plus own finite-bootstrap sources; validation receipt excluded.'),indent=2,sort_keys=True)+'\n')
print(len(repo),'repository pins;',len(own),'own pins')
