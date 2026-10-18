#!/usr/bin/env python3
"""Relocated optimized replay and real on-disk failure controls.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.
"""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


HERE = Path(__file__).resolve().parent


def run(package, expected_error=None):
    result = subprocess.run([sys.executable, '-I', '-O', '-B', str(package / 'verify.py')],
                            cwd=package.parent, text=True, capture_output=True, timeout=90)
    if expected_error is None:
        if result.returncode or not result.stdout.startswith('PASS_PAID_READER_DEFECT '):
            raise RuntimeError('relocated replay failed: ' + result.stdout + result.stderr)
        print(result.stdout.strip())
    elif result.returncode == 0 or expected_error not in result.stderr:
        raise RuntimeError('corruption was not rejected as expected: ' + result.stdout + result.stderr)


def main():
    with tempfile.TemporaryDirectory(prefix='paid-reader-defect-') as directory:
        package = Path(directory) / 'standalone'
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        run(package)

        note = package / 'context/pr1205-README.md'
        original = note.read_bytes()
        note.write_bytes(original + b'\ncorrupt source\n')
        run(package, 'source SHA256 mismatch')
        note.write_bytes(original)

        source = package / 'SOURCE-PINS.json'
        original = source.read_bytes()
        changed = json.loads(original)
        changed['sources'][0]['commit'] = '0' * 40
        source.write_text(json.dumps(changed))
        run(package, 'certificate mismatch')
        source.write_bytes(original)

        receipt = package / 'CERTIFICATE.json'
        original = receipt.read_bytes()
        changed = json.loads(original)
        changed['selected']['repair_plan'][0] -= 1
        receipt.write_text(json.dumps(changed))
        run(package, 'certificate mismatch')
        receipt.write_bytes(original)

        program = package / 'model.py'
        original = program.read_text()
        old = '+ add_word(tuple(-a for a in e), registers, output)'
        if original.count(old) != 1:
            raise RuntimeError('correction mutation anchor drifted')
        program.write_text(original.replace(old, '+ ()'))
        run(package, 'selected partition map')
        program.write_text(original)

        old = 'range(abs(a))'
        if original.count(old) != 1:
            raise RuntimeError('coefficient mutation anchor drifted')
        program.write_text(original.replace(old, 'range(min(abs(a), 1))'))
        run(package, 'selected partition map')
        program.write_text(original)

    print('PASS_PAID_READER_PACKAGE relocation=1 corruptions=5')


if __name__ == '__main__':
    main()
