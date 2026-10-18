#!/usr/bin/env python3
"""Source corruption and clean export controls; no Git/network needed.
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


def load_replay(path):
    module = types.ModuleType('exported_anchor_replay')
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def main():
    manifest = json.loads((PACKAGE / 'SOURCES.json').read_bytes())
    with tempfile.TemporaryDirectory(prefix='anchor export ') as directory:
        root = Path(directory)
        target = root / PACKAGE.relative_to(ROOT)
        shutil.copytree(PACKAGE, target, ignore=shutil.ignore_patterns('__pycache__'))
        for row in manifest['files']:
            if row['usage'] == 'input':
                destination = root / row['path']
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / row['path'], destination)
        replay = load_replay(target / 'replay.py')
        captured = replay.capture()
        if len(captured) != 25 or (root / '.git').exists():
            raise ValueError('clean complete source export')
        # Mutate a live engine, a retained recipe and retained checker independently.
        mutants = [root / replay.KERNEL, target / 'vendor/pr3202/data/base/CLIFFORD-RECIPES.json.gz',
                   target / 'vendor/pr3202/verify.py']
        for file in mutants:
            original = file.read_bytes()
            file.write_bytes(original + b'\n')
            try:
                replay.capture()
            except ValueError as error:
                if 'source drift:' not in str(error):
                    raise
            else:
                raise ValueError('source corruption accepted')
            file.write_bytes(original)
        if replay.capture() != captured:
            raise ValueError('export restoration')
        command = [sys.executable, '-I', '-O', '-B', str(target / 'verify.py')]
        process = subprocess.run(command, cwd=root, text=True, capture_output=True, timeout=120)
        if process.returncode or 'PASS_CLIFFORD_PAULI_ANCHOR' not in process.stdout:
            raise ValueError(process.stdout + process.stderr)
    print('PASS_ANCHOR_EXPORT source_mutants=3 optimized_full_replay=1')


if __name__ == '__main__':
    main()
