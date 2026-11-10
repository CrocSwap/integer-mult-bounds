"""Check the exact sealed payload, excluding only FILES.json itself."""
from pathlib import Path
from hashlib import sha256
import json

HERE=Path(__file__).resolve().parent


def run():
    manifest=json.loads((HERE/'FILES.json').read_text())
    actual={str(p.relative_to(HERE)):{'bytes':p.stat().st_size,'sha256':sha256(p.read_bytes()).hexdigest()}
            for p in HERE.rglob('*') if p.is_file() and p != HERE/'FILES.json'}
    if actual!=manifest['files']:
        raise ValueError('exact sealed payload mismatch, missing/extra/changed files')
    print('PASS_EXACT_SEALED_NATIVE_DELTA_FILES',len(actual),sum(p['bytes'] for p in actual.values()))


if __name__=='__main__':run()
