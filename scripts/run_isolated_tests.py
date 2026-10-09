#!/usr/bin/env python3
"""Run every test module in a fresh process to isolate research import paths.

Independent contributed research packages reuse names such as verify,
skip_graph and data_recovery. A shared unittest process can silently bind a
later package to an earlier package's module. Preserve full test discovery
within each file, but do not share those imports between files. Modules run
concurrently (JOBS; see run_parallel.py); each writes only temporary files.
"""
from pathlib import Path
import sys

from run_parallel import run_all

ROOT = Path(__file__).resolve().parents[1]
files = sorted((ROOT/'tests').glob('test*.py'))
if not files:
    raise RuntimeError('No test modules discovered')
failed = run_all([(path.name, [sys.executable, '-m', 'unittest', 'discover', '-s', str(ROOT/'tests'),
                               '-p', path.name, '-v']) for path in files], cwd=ROOT)
if failed:
    raise SystemExit('Failed modules: '+', '.join(sorted(failed)))
print(f'PASS all {len(files)} test modules in isolated interpreters')
