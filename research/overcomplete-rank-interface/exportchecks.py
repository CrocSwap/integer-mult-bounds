#!/usr/bin/env python3
"""Git-free finite-replay controls; no implicit formal-toolchain download."""
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def require(ok, why):
    if not ok:
        raise ValueError(why)


def run(path, *args):
    return subprocess.run([sys.executable, '-I', '-O', '-B', str(path / 'verify.py'), *args],
                          capture_output=True, text=True, timeout=90)


def snapshot(path):
    return {p.relative_to(path).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in path.rglob('*') if p.is_file()}


def main():
    with tempfile.TemporaryDirectory(prefix='oc-export-') as temp:
        dest = Path(temp) / 'package'
        shutil.copytree(HERE, dest)
        before = snapshot(dest)
        result = run(dest)
        require(result.returncode == 0, result.stdout + result.stderr)
        require(snapshot(dest) == before, 'default replay writes files')
        result = run(dest, '--out', str(dest / 'RESULT.json'))
        require(result.returncode != 0 and 'output already exists' in result.stderr, 'overwrite control')
        for name, marker in [('vendor/pr2277/lean/Overcomplete.lean', 'predecessor source pin'),
                             ('Coupling.lean', 'formal source receipt pin')]:
            path = dest / name
            original = path.read_bytes()
            path.write_bytes(original + b'\n-- altered\n')
            result = run(dest)
            require(result.returncode != 0 and marker in result.stderr, name + ' corruption control')
            path.write_bytes(original)
        require(snapshot(dest) == before, 'export content not restored')
    print('PASS_OC_EXPORT: optimized Git-free read-only replay; three failure controls')


if __name__ == '__main__':
    main()
