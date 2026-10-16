#!/usr/bin/env python3
"""Git-free export and complete-receipt rejection controls."""
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def hashes(root):
    return {p.name: sha256(p.read_bytes()).hexdigest() for p in root.iterdir() if p.is_file()}


def run(root, succeeds, message=None, extra=()):
    p = subprocess.run([sys.executable, '-I', '-O', '-B', str(root/'verify.py'), *map(str, extra)],
                       cwd=root, text=True, capture_output=True, timeout=90)
    need((p.returncode == 0) == succeeds, 'unexpected exit: '+p.stdout+p.stderr)
    if message:
        need(message in p.stdout+p.stderr, 'wrong rejection reason: '+p.stdout+p.stderr)


def main():
    with tempfile.TemporaryDirectory(prefix='dn-pairing-spectrum-') as tmp:
        root = Path(tmp)/'export'
        shutil.copytree(HERE, root, ignore=shutil.ignore_patterns('__pycache__'))
        before = hashes(root)
        run(root, True)
        need(before == hashes(root), 'default export changed a file')
        receipt = root/'RESULT.json'
        original = receipt.read_bytes()
        data = json.loads(original)
        data['d5']['ties'] -= 1
        receipt.write_text(json.dumps(data))
        run(root, False, 'complete receipt mismatch')
        receipt.unlink()
        run(root, False, 'RESULT.json')
        receipt.write_bytes(original)
        out = root/'fresh.json'
        run(root, True, extra=('--out', out))
        need(json.loads(out.read_text()) == json.loads(original), 'regeneration changed receipt')
        run(root, False, 'FileExistsError', extra=('--out', out))
        out.unlink()
        need(before == hashes(root), 'boundary tests failed to restore export')
    print('PASS_DN_PAIRING_BOUNDARY git_free_unchanged=1 receipt_controls=2 exclusive_output=1')


if __name__ == '__main__':
    main()
