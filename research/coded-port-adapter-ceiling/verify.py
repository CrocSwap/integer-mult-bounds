#!/usr/bin/env python3
"""Read-only portable verifier for the scoped coded-port adapter ceiling.
Apache-2.0; substantial OpenAI Codex assistance, source credit in ATTRIBUTION.md.
"""
from hashlib import sha256
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True


def authenticate():
    manifest = json.loads((HERE / 'SCIENCE.json').read_text())
    for row in manifest['files']:
        path = HERE / row['path']
        if path.is_symlink() or sha256(path.read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('Frozen science bytes differ: ' + row['path'])


def main():
    authenticate()
    scope = {'__name__': 'coded_port_scoped_core', '__file__': str(HERE/'check_core.py')}
    # Compile authenticated bytes directly: no ambient source or stale pyc import.
    exec(compile((HERE/'check_core.py').read_bytes(), str(HERE/'check_core.py'), 'exec'), scope)
    result = json.loads(json.dumps(scope['run'](HERE)))
    if result != json.loads((HERE/'RESULT.json').read_text()):
        raise ValueError('Fixed scientific receipt differs')
    authenticate()
    print('PASS_CODED_PORT_ADAPTER_CEILING 5824supported_grade2 '
          '112grade2channels_one_bank 4semantic_controls exact_intervals no_new_kappa')


if __name__ == '__main__':
    main()
