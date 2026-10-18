"""Relocation and effective live-integrity controls, without a Git dependency."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def check(ok, message):
    if not ok:
        raise ValueError(message)


def invoke(p, expect, phrase, quick=False):
    argv = [sys.executable, '-I', '-O', '-B', str(p/'verify.py')]
    if quick:
        argv.append('--quick')
    result = subprocess.run(argv, text=True, capture_output=True, timeout=120)
    combined = result.stdout+result.stderr
    check((result.returncode == 0) == expect and phrase in combined, combined)


def main():
    with tempfile.TemporaryDirectory(prefix='half-add-') as temp:
        root = Path(temp)
        package = root/'research/fixed-grid-half-add'
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        for row in json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8'))['files']:
            if row['usage'] == 'input':
                destination = root/row['path']
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT/row['path'], destination)
        invoke(package, True, 'PASS_FIXED_GRID_HALF_ADD')
        source_row = next(r for r in json.loads((HERE/'SOURCES.json').read_text())['files'] if r['usage']=='input')
        for path, error in [(root/source_row['path'], 'source drift'),
                            (package/'snapshots/Current1094Row2AddReference.lean', 'snapshot drift')]:
            raw=path.read_bytes(); path.write_bytes(raw+b'\nCORRUPTION\n')
            invoke(package, False, error, quick=True)
            path.write_bytes(raw)
        result_path=package/'RESULT.json'
        raw=result_path.read_bytes()
        value=json.loads(raw)
        check(value['schema_version']==1, 'fixture')
        value['schema_version']=True
        result_path.write_text(json.dumps(value), encoding='utf-8')
        invoke(package, False, 'typed receipt mismatch')
        result_path.write_bytes(raw)
    print('PASS_HALF_ADD_PACKAGE Git-free optimized full replay; 3 actual integrity corruptions rejected')


if __name__ == '__main__':
    main()
