#!/usr/bin/env python3
"""Source corruption and Git-free optimized complete replay.
Tekalign / OpenAI Codex, Apache-2.0.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import types

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def main():
    manifest = json.loads((PACKAGE / 'SOURCES.json').read_bytes())
    with tempfile.TemporaryDirectory(prefix='r2 mutation export ') as directory:
        root = Path(directory)
        target = root / PACKAGE.relative_to(ROOT)
        shutil.copytree(PACKAGE, target, ignore=shutil.ignore_patterns('__pycache__'))
        for row in manifest['files']:
            if row['usage'] == 'input':
                path = root / row['path']
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / row['path'], path)
        R = types.ModuleType('exported_path_replay')
        R.__file__ = str(target / 'replay.py')
        exec(compile((target / 'replay.py').read_bytes(), R.__file__, 'exec'), R.__dict__)
        original = R.capture()
        for file in (target / 'vendor/pr3218/vendor/pr3202/verify.py',
                     target / 'vendor/pr3218/engine.py',
                     root / 'research/frontier1094-recipes-exact-seed76/clifford.py'):
            raw = file.read_bytes()
            file.write_bytes(raw + b'\n')
            try:
                R.capture()
            except ValueError as error:
                if 'source drift:' not in str(error):
                    raise
            else:
                raise ValueError('source corruption accepted')
            file.write_bytes(raw)
        if R.capture() != original or (root / '.git').exists():
            raise ValueError('clean restored export')
        output = root / 'fresh.json'
        commands = [
            [sys.executable, '-I', '-O', '-B', str(target / 'replay.py'), '--output', str(output)],
            [sys.executable, '-I', '-O', '-B', str(target / 'controls.py')],
        ]
        for command in commands:
            process = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=120)
            if process.returncode:
                raise ValueError(process.stdout + process.stderr)
        actual, expected = json.loads(output.read_bytes()), json.loads((target / 'RESULT.json').read_bytes())
        for key in ('reference_result_sha256', 'call_multiset_sha256', 'decisions', 'providers', 'source_sha256'):
            if actual[key] != expected[key]:
                raise ValueError('optimized export result mismatch: ' + key)
    print('PASS_R2_PATH_COPY_EXPORT source_corruptions=3 optimized_full_replay=1')


if __name__ == '__main__':
    main()
