#!/usr/bin/env python3
"""Run every test module in a fresh process to isolate research import paths.

Independent contributed research packages reuse names such as verify,
skip_graph and data_recovery. A shared unittest process can silently bind a
later package to an earlier package's module. Preserve full test discovery
within each file, but do not share those imports between files.

Modules are scheduled concurrently (one isolated interpreter per module,
--workers controls the width). Every module keeps the exact sequential
command and its captured stdout/stderr bytes are replayed in sorted module
order, so the combined receipts match a sequential run module for module.
For PR53 skip-clones, the unchanged module command runs in a temporary
copy with its authenticated frozen source instead of the optimized successor.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def module_command(python, tests_dir, name):
    """Default unchanged command for a test module."""
    return [python, '-m', 'unittest', 'discover', '-s', str(tests_dir), '-p', name, '-v']


def run_modules(files, python=None, tests_dir=None, cwd=None, workers=None):
    """Run each test module in its own interpreter; return (path, code, out, err).

    Results follow the input order regardless of scheduling. The per-module
    command and byte streams are those of a sequential run; only the
    scheduling is concurrent.
    """
    python = sys.executable if python is None else python
    tests_dir = ROOT / 'tests' if tests_dir is None else tests_dir
    cwd = ROOT if cwd is None else cwd
    if workers is None:
        workers = os.cpu_count() or 1
    workers = max(1, min(workers, len(files)))
    # A developer's optimized parent interpreter must not silently remove
    # assertions in research verifiers imported by the isolated tests.
    env = os.environ.copy()
    env.pop('PYTHONOPTIMIZE', None)

    def run_one(path):
        command = module_command(python, tests_dir, path.name)
        # Run this frozen package's original tests in its authenticated overlay.
        # Other test modules continue to exercise the live checkout unchanged.
        if (path.name == 'test_skip_clones.py'
                and Path(tests_dir).resolve() == (ROOT / 'tests').resolve()
                and Path(cwd).resolve() == ROOT.resolve()
                and (ROOT / 'research/skip-clones/SOURCE.json').is_file()
                and (ROOT / 'scripts/replay_historical_check.py').is_file()):
            command = [python, '-B', str(ROOT / 'scripts/replay_historical_check.py'),
                       'skip-clones-tests']
        result = subprocess.run(command,
                                cwd=cwd, env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return path, result.returncode, result.stdout, result.stderr

    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(run_one, files))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=None,
                        help='concurrent test-module processes (default: CPU count)')
    args = parser.parse_args(argv)
    files = sorted((ROOT / 'tests').glob('test*.py'))
    if not files:
        raise RuntimeError('No test modules discovered')
    failed = []
    for path, code, out, err in run_modules(files, workers=args.workers):
        print('Checking ' + path.name, flush=True)
        sys.stdout.buffer.write(out)
        sys.stdout.flush()
        sys.stderr.buffer.write(err)
        sys.stderr.flush()
        if code:
            failed.append(path.name)
    if failed:
        raise SystemExit('Failed modules: ' + ', '.join(failed))
    print(f'PASS all {len(files)} test modules in isolated interpreters')


if __name__ == '__main__':
    main()
