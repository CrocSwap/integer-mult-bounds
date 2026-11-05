"""Read-only exact natural-root payload seal, including nested FILES.json."""
from pathlib import Path
from hashlib import sha256
import json

HERE=Path(__file__).resolve().parent


def run():
    expected=json.loads((HERE/'FILES.json').read_text())['files']
    actual={str(p.relative_to(HERE)):{'bytes':p.stat().st_size,'sha256':sha256(p.read_bytes()).hexdigest()}
            for p in HERE.rglob('*')if p.is_file()and p!=HERE/'FILES.json'}
    if actual!=expected:raise ValueError('natural-root payload changed or has missing/extra files')
    print('PASS_EXACT_NATURAL_ROOT_FILES',len(actual))


if __name__=='__main__':run()
