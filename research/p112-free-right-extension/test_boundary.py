#!/usr/bin/env python3
"""Behavioral evidence boundary: Git-free, unchanged files, failed drift controls."""
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REL = HERE.relative_to(ROOT)
INPUT = Path('research/direct-delivery504-global/inputs/hamming/PROTOTYPE.json')


def need(ok, message):
    if not ok:
        raise ValueError(message)


def hashes(root):
    return {str(p.relative_to(root)): sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def run(root, succeeds, message=None, extra=()):
    p = subprocess.run([sys.executable, '-I', '-O', '-B', str(root/REL/'verify.py'), *map(str, extra)],
                       cwd=root, text=True, capture_output=True, timeout=90)
    need((p.returncode == 0) == succeeds, 'unexpected exit: '+p.stdout+p.stderr)
    if message:
        need(message in p.stdout+p.stderr, 'wrong rejection reason: '+p.stdout+p.stderr)


def main():
    with tempfile.TemporaryDirectory(prefix='p112-free-extension-') as tmp:
        root = Path(tmp)
        shutil.copytree(HERE, root/REL, ignore=shutil.ignore_patterns('__pycache__'))
        (root/INPUT).parent.mkdir(parents=True)
        shutil.copyfile(ROOT/INPUT, root/INPUT)
        before = hashes(root)
        run(root, True)
        need(before == hashes(root), 'default export changed a file')
        receipt = root/REL/'RESULT.json'
        original = receipt.read_bytes()
        data = json.loads(original)
        data['sharp_profile'][0] = 7
        receipt.write_text(json.dumps(data))
        run(root, False, 'complete receipt mismatch')
        receipt.unlink()
        run(root, False, 'RESULT.json')
        receipt.write_bytes(original)
        raw = (root/INPUT).read_bytes()
        (root/INPUT).write_bytes(raw+b' ')
        run(root, False, 'source hash mismatch')
        (root/INPUT).write_bytes(raw)
        out = root/'fresh.json'
        run(root, True, extra=('--out', out))
        need(json.loads(out.read_text()) == json.loads(original), 'regeneration changed receipt')
        run(root, False, 'FileExistsError', extra=('--out', out))
        out.unlink()
        need(before == hashes(root), 'boundary tests failed to restore exported inputs')
    print('PASS_P112_FREE_EXTENSION_BOUNDARY git_free_unchanged=1 drift_controls=3 exclusive_output=1')


if __name__ == '__main__':
    main()
