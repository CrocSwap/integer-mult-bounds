#!/usr/bin/env python3
"""Run every test module in a fresh process to isolate research import paths.

Independent contributed research packages reuse names such as verify,
skip_graph and data_recovery. A shared unittest process can silently bind a
later package to an earlier package's module. Preserve full test discovery
within each file, but do not share those imports between files.

Modules are scheduled concurrently (one isolated interpreter per module,
--workers controls the width). Every module retains unittest discovery arguments and its captured stdout/stderr bytes are replayed in sorted module
order, so the combined receipts match a sequential run module for module.
For PR53 skip-clones, the completion-checked module command runs in a temporary
copy with its authenticated frozen source instead of the optimized successor.
Each module and historical wrapper uses a private bytecode-cache namespace.
The owned temporary directory is removed after workers finish or are stopped.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading
import tempfile
import time

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


def isolated_python(python, cache):
    # -B prevents writes, not reads. An explicit fresh prefix also overrides
    # inherited PYTHONPYCACHEPREFIX without changing the caller's environment.
    return [python, '-B', '-X', 'pycache_prefix=' + str(cache)]


def module_command(python, tests_dir, name, receipt):
    """Run discovery normally, then attest that the suite returned successfully."""
    cache = Path(str(receipt) + '-pycache')
    return isolated_python(python, cache) + ['-c', BOOTSTRAP, str(tests_dir), name, str(receipt)]


def stop_module(process):
    """Stop the owned active module and its ordinary child processes."""
    problems = []
    if os.name == 'nt':
        if process.poll() is None:
            try:
                result = subprocess.run(['taskkill', '/F', '/T', '/PID', str(process.pid)],
                                        capture_output=True, timeout=5)
                if result.returncode:
                    problems.append('taskkill exited ' + str(result.returncode))
            except (OSError, subprocess.TimeoutExpired) as error:
                problems.append(str(error))
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        except OSError as error:
            problems.append(str(error))
    if process.poll() is None:
        try:
            process.kill()
        except OSError as error:
            problems.append(str(error))
    try:
        process.wait(timeout=2)
    except (OSError, subprocess.TimeoutExpired) as error:
        problems.append(str(error))
    if problems:
        raise RuntimeError(f'module {process.pid}: ' + '; '.join(problems))


def module_budget(value):
    """Reject NaN/infinity as well as nonpositive deadline budgets."""
    seconds = float(value)
    if not math.isfinite(seconds) or seconds <= 0:
        raise ValueError('module timeout must be finite and positive')
    return seconds


def run_modules(files, python=None, tests_dir=None, cwd=None, workers=None,
                module_timeout=None):
    """Run each test module in its own interpreter; return (path, code, out, err).

    Results follow the input order regardless of scheduling. Each child must return a successful unittest result; a zero process exit
    alone is insufficient. Completion receipts are private to this invocation.
    """
    python = sys.executable if python is None else python
    tests_dir = ROOT / 'tests' if tests_dir is None else tests_dir
    cwd = ROOT if cwd is None else cwd
    if module_timeout is not None:
        module_timeout = module_budget(module_timeout)
    if workers is None:
        workers = os.cpu_count() or 1
    workers = max(1, min(workers, len(files)))
    # A developer's optimized parent interpreter must not silently remove
    # assertions in research verifiers imported by the isolated tests.
    env = os.environ.copy()
    env.pop('PYTHONOPTIMIZE', None)
    active = set()
    lock = threading.Lock()
    stopping = False

    completion = tempfile.TemporaryDirectory(prefix="isolated-test-completion-")

    def run_one(indexed):
        index, path = indexed
        receipt = Path(completion.name) / str(index)
        command = module_command(python, tests_dir, path.name, receipt)
        # Run this frozen package's original tests in its authenticated overlay.
        # Other test modules continue to exercise the live checkout unchanged.
        legacy = {'test_skip_clones.py': 'skip-clones-tests',
                  **{'test_' + slug.replace('-', '_') + '.py': 'legacy-test-' + slug
                     for slug in ('copied-fixed', 'copied-fixed-reversed', 'skip-strips',
                                  'skip-suffix', 'pair-assembly', 'split-skip')}}
        if (path.name in legacy
                and Path(tests_dir).resolve() == (ROOT / 'tests').resolve()
                and Path(cwd).resolve() == ROOT.resolve()
                and (ROOT / 'research/skip-clones/SOURCE.json').is_file()
                and (ROOT / 'scripts/replay_historical_check.py').is_file()):
            cache = Path(str(receipt) + '-wrapper-pycache')
            command = isolated_python(python, cache) + [
                str(ROOT / 'scripts/replay_historical_check.py'),
                legacy[path.name], '--completion-receipt', str(receipt)]
        # Serialize launch/registration with cancellation: no worker may start
        # an unregistered module after the controlling thread takes its snapshot.
        with lock:
            if stopping:
                return path, -1, b'', b''
            process = subprocess.Popen(command,
                                       cwd=cwd, env=env, start_new_session=True,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            active.add(process)
            deadline = None if module_timeout is None else time.monotonic() + module_timeout
        finished = False
        cleaned = False
        try:
            while True:
                try:
                    remaining = 0.2 if deadline is None else max(0, deadline - time.monotonic())
                    out, err = process.communicate(timeout=min(0.2, remaining))
                    finished = True
                    code = process.returncode
                    if code == 0 and (not receipt.is_file() or receipt.read_bytes() != COMPLETED):
                        code = 1
                        err += b"Incomplete unittest run: child exited successfully before discovery and execution completed\n"
                    return path, code, out, err
                except subprocess.TimeoutExpired:
                    with lock:
                        if stopping:
                            # Failed native cleanup or an orphan can retain the
                            # pipes. Do not make cancellation wait for their EOF.
                            finished = True
                            return path, -1, b'', b''
                    if deadline is not None and time.monotonic() >= deadline:
                        stop_module(process)
                        cleaned = True
                        try:
                            out, err = process.communicate(timeout=2)
                        except subprocess.TimeoutExpired as error:
                            # A deliberately detached child may retain a pipe.
                            # Preserve captured bytes without waiting for its EOF.
                            out, err = error.output or b'', error.stderr or b''
                            process.stdout.close()
                            process.stderr.close()
                        finished = True
                        err += (f'Module timeout after {module_timeout:g}s: {path.name}; '
                                'unittest completion is not accepted\n').encode('utf-8')
                        return path, 124, out, err
        finally:
            # An unexpected worker exception must leave a live child visible
            # to the controlling thread's cleanup snapshot.
            if finished:
                # Pipe EOF and leader exit do not imply solver completion: a
                # descendant may have closed its inherited capture streams.
                # Keep ownership until POSIX group cleanup succeeds, including
                # ordinary success/failure. Windows exited leaders need a Job
                # Object; the existing taskkill cancellation contract is unchanged.
                if os.name != 'nt' and not cleaned:
                    stop_module(process)
                with lock:
                    active.discard(process)

    pool = ThreadPoolExecutor(max_workers=workers)
    try:
        return list(pool.map(run_one, enumerate(files)))
    except BaseException as error:
        with lock:
            stopping = True
            processes = tuple(active)
        problems = []
        for process in processes:
            try:
                stop_module(process)
            except Exception as cleanup_error:
                problems.append(str(cleanup_error))
        if problems:
            note = 'Isolated test cleanup failed: ' + '; '.join(problems)
            if hasattr(error, 'add_note'):
                error.add_note(note)
            else:
                print(note, file=sys.stderr)
        raise
    finally:
        try:
            pool.shutdown(wait=True, cancel_futures=stopping)
        finally:
            completion.cleanup()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=None,
                        help='concurrent test-module processes (default: CPU count)')
    parser.add_argument('--module-timeout', type=module_budget, default=None,
                        help='positive seconds per launched module; timeout fails (default: unlimited)')
    args = parser.parse_args(argv)
    files = sorted((ROOT / 'tests').glob('test*.py'))
    if not files:
        raise RuntimeError('No test modules discovered')
    failed = []
    for path, code, out, err in run_modules(files, workers=args.workers,
                                          module_timeout=args.module_timeout):
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
