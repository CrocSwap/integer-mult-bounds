#!/usr/bin/env python3
"""Relocated optimized replay and source/certificate corruption controls."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def run(path, expected_error=None):
    result = subprocess.run([sys.executable, '-I', '-O', '-B', str(path / 'verify.py')],
                            cwd=path.parent, text=True, capture_output=True)
    if expected_error is None:
        if result.returncode or 'PASS_TWO_CLEAN_CHECKPOINTS' not in result.stdout:
            raise ValueError(result.stdout + result.stderr)
    elif result.returncode == 0 or expected_error not in result.stderr:
        raise ValueError('wrong corruption result: ' + result.stdout + result.stderr)


def main():
    with tempfile.TemporaryDirectory(prefix='two-clean-checkpoints-') as tmp:
        root = Path(tmp)
        package = root / 'relocated'
        shutil.copytree(ROOT, package, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        run(package)
        expected = package / 'EXPECTED.json'
        original = expected.read_bytes()
        for mutation in ('cost', 'boolean'):
            data = json.loads(original)
            if mutation == 'cost':
                data['primary'][2]['cost'] = 1249
            else:
                # Python equality treats True == 1; canonical JSON must not.
                data['primary'][1]['clean'] = True
            expected.write_text(json.dumps(data))
            changed = expected.read_bytes()
            run(package, 'certificate mismatch')
            if expected.read_bytes() != changed:
                raise ValueError('verification overwrote a corrupt certificate')
        expected.write_bytes(original)
        source = package / 'vendor/pr628/DIRTY-PROOF.md'
        source.write_bytes(source.read_bytes() + b'\nsource mutation\n')
        run(package, 'source drift')
    print('PASS_TWO_CLEAN_PACKAGE: relocated optimized replay; 3 corruptions rejected without overwrite')


if __name__ == '__main__':
    main()
