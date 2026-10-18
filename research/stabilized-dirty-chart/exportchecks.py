#!/usr/bin/env python3
"""Read-only, typed receipt and source checks on a Git-free export."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, why):
    if not ok:
        raise ValueError(why)


def snapshot(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def run(package, *args):
    return subprocess.run([sys.executable, '-I', '-O', '-B', str(package / 'verify.py'), *args],
                          capture_output=True, text=True, timeout=120)


def main():
    with tempfile.TemporaryDirectory(prefix='stabilized-chart-') as temp:
        root = Path(temp)
        package = root / 'research' / HERE.name
        shutil.copytree(HERE, package)
        sources = json.loads((HERE / 'SOURCES.json').read_bytes())
        for row in sources['files']:
            if row['usage'] == 'input':
                dest = root / row['path']
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / row['path'], dest)
        before = snapshot(root)
        result = run(package)
        require(result.returncode == 0, result.stdout + result.stderr)
        require(snapshot(root) == before, 'default replay writes files')
        result = run(package, '--out', str(package / 'RESULT.json'))
        require(result.returncode != 0 and 'output already exists' in result.stderr, 'overwrite control')
        source = root / next(row['path'] for row in sources['files'] if row['usage'] == 'input')
        saved = source.read_bytes()
        source.write_bytes(saved + b'\nchanged\n')
        result = run(package)
        require(result.returncode != 0 and 'source pin:' in result.stderr, 'source corruption control')
        source.write_bytes(saved)
        receipt = package / 'RESULT.json'
        saved = receipt.read_bytes()
        bad = json.loads(saved)
        bad['candidate_bill']['xors'] = float(bad['candidate_bill']['xors'])
        receipt.write_text(json.dumps(bad), encoding='utf-8')
        result = run(package)
        require(result.returncode != 0 and 'receipt differs' in result.stderr, 'typed receipt control')
        receipt.write_bytes(saved)
        require(snapshot(root) == before, 'export restoration')
    print('PASS_STABILIZED_EXPORT: optimized read-only replay; source, typed receipt and output controls')


if __name__ == '__main__':
    main()
