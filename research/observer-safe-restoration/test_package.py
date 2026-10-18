#!/usr/bin/env python3
# Copyright 2026 Adam Gall. SPDX-License-Identifier: Apache-2.0
"""One full relocated replay plus an actual source-corruption rejection."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def main():
    with tempfile.TemporaryDirectory(prefix='observer-restoration-') as temp:
        copy = Path(temp) / 'standalone'
        shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns('__pycache__'))
        command = [sys.executable, '-I', '-O', '-B', str(copy / 'verify.py')]
        good = subprocess.run(command, cwd=temp, text=True, capture_output=True)
        if good.returncode:
            raise RuntimeError(good.stdout + good.stderr)
        print(good.stdout, end='')
        source = copy / 'context/pr1155-README.md'
        source.write_bytes(source.read_bytes() + b'\ncorruption-control\n')
        bad = subprocess.run(command, cwd=temp, text=True, capture_output=True)
        if bad.returncode == 0 or 'source pin: context/pr1155-README.md' not in bad.stderr:
            raise RuntimeError('source corruption was not rejected at its pin')
        print('PASS_OBSERVER_RESTORATION_PACKAGE relocation=1 source_corruption=1')


if __name__ == '__main__':
    main()
