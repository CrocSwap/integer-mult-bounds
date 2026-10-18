#!/usr/bin/env python3
"""Relocation and proof-relevant corruption checks. Apache-2.0."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def run(folder):
    return subprocess.run([sys.executable, '-I', '-O', '-B', str(folder/'verify.py')],
                          cwd='/', capture_output=True, text=True, timeout=60)


def main():
    with tempfile.TemporaryDirectory(prefix='connector-package-') as temp:
        relocated = Path(temp)/'relocated'
        shutil.copytree(HERE, relocated, ignore=shutil.ignore_patterns('__pycache__'))
        for item in relocated.rglob('*'):
            item.chmod(0o555 if item.is_dir() else 0o444)
        relocated.chmod(0o555)
        try:
            result = run(relocated)
            if result.returncode or 'PASS_SIGNED_CONNECTOR_FOUR_TRANSFERS' not in result.stdout:
                raise ValueError('read-only relocation: ' + result.stdout + result.stderr)
        finally:
            relocated.chmod(0o755)
            for item in relocated.rglob('*'):
                item.chmod(0o755 if item.is_dir() else 0o644)
        mutations = [
            ('source', 'sources/PR1637-README.md', lambda text: text + '\ncorrupted source\n', 'source pin sources/PR1637-README.md'),
            ('word', 'CERTIFICATE.json', lambda text: mutate(text, 'word'), 'complete certificate equality'),
            ('coverage', 'CERTIFICATE.json', lambda text: mutate(text, 'coverage'), 'complete certificate equality'),
            ('cost', 'CERTIFICATE.json', lambda text: mutate(text, 'cost'), 'complete certificate equality'),
            ('dense', 'INDEPENDENT.json', lambda text: mutate(text, 'dense'), 'independent full receipt equality'),
        ]
        for label, name, change, expected in mutations:
            target = relocated/name
            before = target.read_text()
            target.write_text(change(before))
            result = run(relocated)
            target.write_text(before)
            if result.returncode == 0:
                raise ValueError('corruption accepted: ' + label)
            if 'ValueError' not in result.stderr or expected not in result.stderr:
                raise ValueError('wrong failure class for ' + label + ': ' + result.stderr)
    print('PASS_CONNECTOR_PACKAGE relocation=1 corruptions=5')


def mutate(text, kind):
    data = json.loads(text)
    if kind == 'word':
        data['word'][0][2] *= -1
    elif kind == 'coverage':
        data['one_root_census']['cover_masks']['7'] = 1
    elif kind == 'cost':
        data['candidate']['root_transfers'] -= 1
    elif kind == 'dense':
        data['basis_columns_per_direction'] -= 1
    return json.dumps(data)


if __name__ == '__main__':
    main()
