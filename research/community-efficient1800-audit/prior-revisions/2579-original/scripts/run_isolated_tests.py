#!/usr/bin/env python3
"""Run every test module in a fresh process to isolate research import paths.

Independent contributed research packages reuse names such as verify,
skip_graph and data_recovery. A shared unittest process can silently bind a
later package to an earlier package's module. Preserve full test discovery
within each file, but do not share those imports between files.

Modules are scheduled concurrently (one isolated interpreter per module,
--workers controls the width). Every module uses the same unittest discovery
arguments and its captured stdout/stderr bytes are replayed in sorted module
order. A successful exit counts only after unittest has returned a result.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
COMPLETED = b'unittest completed successfully\n'
BOOTSTRAP = '''from pathlib import Path
import sys
import unittest
tests_dir, pattern, receipt = sys.argv[1:]
sys.argv = [str(Path(unittest.__file__).with_name('__main__.py')),
            'discover', '-s', tests_dir, '-p', pattern, '-v']
program = unittest.main(module=None, exit=False)
if not program.result.wasSuccessful():
    raise SystemExit(1)
Path(receipt).write_bytes(b'unittest completed successfully\\n')
'''


def module_command(python, tests_dir, name, receipt):
    """Run discovery normally, then attest that the suite returned successfully."""
    return [python, '-c', BOOTSTRAP, str(tests_dir), name, str(receipt)]


def run_modules(files, python=None, tests_dir=None, cwd=None, workers=None):
    """Run each test module in its own interpreter; return (path, code, out, err).

    Results follow the input order regardless of scheduling. Each child must
    return from unittest successfully, not merely terminate with exit code 0.
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

    def run_one(indexed):
        index, path = indexed
        receipt = Path(completion_dir) / str(index)
        result = subprocess.run(module_command(python, tests_dir, path.name, receipt),
                                cwd=cwd, env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0 and (
                not receipt.is_file() or receipt.read_bytes() != COMPLETED):
            return path, 1, result.stdout, result.stderr + (
                b'Incomplete unittest run: child exited successfully before '
                b'discovery and execution completed\n')
        return path, result.returncode, result.stdout, result.stderr

    with tempfile.TemporaryDirectory(prefix='isolated-test-completion-') as completion_dir:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            return list(pool.map(run_one, enumerate(files)))


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
