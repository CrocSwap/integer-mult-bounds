"""Read-only package entry point; exact byte guards and bounded scientific checks."""
from pathlib import Path
import hashlib,json,runpy
P=Path(__file__).resolve().parent
for name,digest in json.loads((P/'INTEGRITY.json').read_bytes()).items():
 if hashlib.sha256((P/name).read_bytes()).hexdigest()!=digest:raise ValueError('Source/artifact drift: '+name)
for name in ('involution_verify.py','unit_transfer_variant.py','verify_dilation.py','independent.py','phase_audit.py'):
 runpy.run_path(str(P/name),run_name='__main__')
print('PASS_NATIVE_INVOLUTIVE_PORT_TRANSFER_SCOPED_ONLY')
