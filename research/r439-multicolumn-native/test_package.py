#!/usr/bin/env python3
"""Git-free source and receipt controls; native checks run separately."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def snapshot(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def run(root, rejected=None):
    env = dict(os.environ, PATH='', PYTHONDONTWRITEBYTECODE='1')
    p = subprocess.run([sys.executable, '-I', '-O', '-B',
                        root / HERE.relative_to(ROOT) / 'verify.py'], cwd=root,
                       env=env, capture_output=True, text=True, encoding='utf-8', timeout=180)
    if rejected is None:
        need(p.returncode == 0 and 'PYTHON_ONLY' in p.stdout, 'export replay: ' + p.stderr)
    else:
        need(p.returncode != 0 and rejected in p.stderr, 'wrong rejection: ' + p.stderr)


def main():
    with tempfile.TemporaryDirectory(prefix='r439-export-') as tmp:
        root = Path(tmp)
        package = root / HERE.relative_to(ROOT)
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        inputs = [p['path'] for p in json.loads((HERE / 'SOURCES.json').read_bytes())['files']
                  if p['usage'] == 'input']
        for name in inputs:
            dst = root / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes((ROOT / name).read_bytes())
        before = snapshot(root)
        run(root)
        need(snapshot(root) == before, 'default export replay wrote files')
        source = root / 'research/r439-bsection-stars-seed01/candidate.json.gz'
        original = source.read_bytes()
        source.write_bytes(original + b'corrupt')
        run(root, 'source SHA256')
        source.write_bytes(original)
        vendor = package / 'vendor/pr2440/WITNESS.json'
        original = vendor.read_bytes()
        vendor.write_bytes(original + b' ')
        run(root, 'predecessor SHA256')
        vendor.write_bytes(original)
        receipt = package / 'REPLAY.json'
        original = receipt.read_bytes()
        changed = json.loads(original)
        changed['native_executed'] = 0  # bool/int equality must not accept this.
        receipt.write_text(json.dumps(changed), encoding='utf-8')
        run(root, 'REPLAY.json receipt mismatch')
        receipt.write_bytes(original)
        need(snapshot(root) == before, 'mutation controls did not restore export')
    print('PASS_MULTICOLUMN_EXPORT_CONTROLS Git_free=1 read_only=1 corruptions=3')


if __name__ == '__main__':
    main()
