from pathlib import Path
import hashlib,json
p=Path(__file__).resolve().parent
m=json.loads((p/'MANIFEST.json').read_text())
a={x.relative_to(p).as_posix():hashlib.sha256(x.read_bytes()).hexdigest() for x in p.rglob('*') if x.is_file() and x.name!='MANIFEST.json' and '__pycache__' not in x.parts}
if a!=m['files']:raise ValueError('Package inventory or source hash mismatch')
print('PASS_NATIVE_CYCLIC_RECOVERY_BYTES')
