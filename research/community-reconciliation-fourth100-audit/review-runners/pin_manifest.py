import json,hashlib
from pathlib import Path
A=Path('/tmp/integer-mult-queue-20261013/research/community-reconciliation-fourth100-audit');files={p.relative_to(A).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(A.rglob('*'))if p.is_file() and p.name!='MANIFEST.json' and '__pycache__'not in p.parts};(A/'MANIFEST.json').write_text(json.dumps(dict(scope='Integrity and source provenance, not mathematical verification',files=files),indent=2)+'\n')
