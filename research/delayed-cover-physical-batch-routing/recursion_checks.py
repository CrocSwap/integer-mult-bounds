"""Authenticate and replay the two frozen recursive physical programs.

This driver is verification orchestration, outside the literal runtime.
The pre-existing independent router walkers do not cover the new recursion.
"""
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def authenticate(directory, expected):
    manifest = directory / 'FILES.json'
    require(sha256(manifest.read_bytes()).hexdigest() == expected,
            'exact frozen recursion manifest')
    rows = json.loads(manifest.read_text())['files']
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob('*')
              if p.is_file() and p != manifest}
    require(actual == set(rows), 'complete frozen recursion file inventory')
    for name, row in rows.items():
        path = PurePosixPath(name)
        require(not path.is_absolute() and '..' not in path.parts,
                'scoped frozen file path')
        raw = (directory / name).read_bytes()
        require(len(raw) == row['bytes'] and sha256(raw).hexdigest() == row['sha256'],
                'exact frozen recursion bytes: ' + name)
    return rows


custody = json.loads((HERE / 'recursion/CUSTODY.json').read_text())
core = HERE / 'recursion/core'
root = HERE / 'recursion/root'
core_rows = authenticate(core, custody['core_FILES_sha256'])
authenticate(root, custody['root_FILES_sha256'])
for name in (*core_rows, 'FILES.json'):
    require((core / name).read_bytes() == (root / 'inputs/core' / name).read_bytes(),
            'root prefix retains the complete exact recursive core: ' + name)

flags = ['-I', '-B'] + (['-O'] if sys.flags.optimize else [])
for script in (core / 'check.py', root / 'check.py'):
    result = subprocess.run([sys.executable, *flags, str(script)],
                            cwd=HERE, timeout=60)
    if result.returncode:
        raise SystemExit(result.returncode)
print(json.dumps({'status': 'PASS_FROZEN_CORE_AND_NATURAL_ROOT_RECURSION',
                  'optimized': bool(sys.flags.optimize),
                  'scientific_replays': 2}))
