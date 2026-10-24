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
Ordinary Python descendants inherit a private namespace and suppress cache writes;
children that ignore or override their environment need their own cache policy.
The owned temporary directory is removed after workers finish or are stopped.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
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
                # The supervisor may finish job cleanup between poll and
                # taskkill. An already-exited owner needs no further kill.
                if result.returncode and process.poll() is None:
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


def close_captures(process):
    """Bound CPython Windows reader completion before acquiring stream locks."""
    problems = []
    deadline = time.monotonic() + 2
    for name in ('stdout', 'stderr'):
        try:
            reader = getattr(process, name + '_thread', None)
            if reader is not None:
                reader.join(max(0, deadline - time.monotonic()))
                if reader.is_alive():
                    problems.append(name + ' capture reader did not stop')
                    continue
            getattr(process, name).close()
        except Exception as error:
            problems.append(str(error))
    return problems


def module_budget(value):
    """Reject NaN/infinity as well as nonpositive deadline budgets."""
    seconds = float(value)
    if not math.isfinite(seconds) or seconds <= 0:
        raise ValueError('module timeout must be finite and positive')
    return seconds


WINDOWS_OWNER = '''import json, os, sys
sys.path.insert(0, sys.argv[1])
from research_package import run_windows_command
sys.exit(run_windows_command(json.loads(sys.argv[2]), os.getcwd(), None, dict(os.environ)))
'''


def windows_module_command(command, python, cache):
    """Keep a live owner until its gated module's whole Job Object is empty.

    Reuse the registered replay runner's native ownership implementation. This
    supervisor inherits the capture pipes and preserves the module's exit code;
    closing its non-inherited job handle also kills descendants on cancellation.
    Isolate supervisor startup and bytecode without changing the test environment.
    """
    return isolated_python(python, cache) + [
        # Preserve Unicode at this outer layer as well as inside the job gate;
        # ASCII escapes would consume the Windows command-line budget again.
        '-I', '-S', '-c', WINDOWS_OWNER, str(ROOT / 'scripts'),
        json.dumps(command, ensure_ascii=False)]


def run_modules(files, python=None, tests_dir=None, cwd=None, workers=None,
                module_timeout=None):
    """Run each test module in its own interpreter; return (path, code, out, err).

    Results follow the input order regardless of scheduling. Each child must return a successful unittest result; a zero process exit
    alone is insufficient. Completion receipts are private to this invocation.
    """
    previous_handler = None
    termination = {'requested': False, 'waiting': False}

    def terminate(signum, frame):
        if not termination['requested']:
            termination['requested'] = True
            if termination['waiting']:
                raise SystemExit(128 + signum)

    try:
        if (os.name != 'nt' and threading.current_thread() is threading.main_thread()
                and signal.getsignal(signal.SIGTERM) == signal.SIG_DFL):
            previous_handler = signal.SIG_DFL
            signal.signal(signal.SIGTERM, terminate)
        # Popen runs only in workers. The existing registration lock makes the
        # cancellation snapshot wait for every in-progress launch to be owned.
        result = _run_modules(files, python, tests_dir, cwd, workers, module_timeout, termination)
    finally:
        if previous_handler is not None:
            signal.signal(signal.SIGTERM, previous_handler)
    if termination['requested']:
        raise SystemExit(143)
    return result


def _run_modules(files, python, tests_dir, cwd, workers, module_timeout, termination):
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
        # -X options do not propagate to Python processes launched by tests.
        # Keep their inherited cache policy private to this module as well.
        module_env = dict(env, PYTHONPYCACHEPREFIX=str(receipt) + '-descendant-pycache',
                          PYTHONDONTWRITEBYTECODE='1')
        if os.name == 'nt':
            command = windows_module_command(command, python, Path(str(receipt) + '-owner-pycache'))
        # Serialize launch/registration with cancellation: no worker may start
        # an unregistered module after the controlling thread takes its snapshot.
        with lock:
            if stopping:
                return path, -1, b'', b''
            process = subprocess.Popen(command,
                                       cwd=cwd, env=module_env, start_new_session=True,
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
                except subprocess.TimeoutExpired:
                    with lock:
                        if stopping:
                            # Failed native cleanup or an orphan can retain the
                            # pipes. Do not make cancellation wait for their EOF.
                            finished = True
                            return path, -1, b'', b''
                    exited = os.name != 'nt' and process.poll() is not None
                    if deadline is not None and time.monotonic() >= deadline:
                        stop_module(process)
                        cleaned = True
                        try:
                            out, err = process.communicate(timeout=2)
                        except subprocess.TimeoutExpired as error:
                            # A deliberately detached child may retain a pipe.
                            # Preserve captured bytes without waiting for its EOF.
                            out, err = error.output or b'', error.stderr or b''
                            capture_problems = close_captures(process)
                            if capture_problems:
                                err += ('Capture cleanup failed: ' + '; '.join(capture_problems)
                                        + '\n').encode('utf-8')
                        finished = True
                        err += (f'Module timeout after {module_timeout:g}s: {path.name}; '
                                'unittest completion is not accepted\n').encode('utf-8')
                        return path, 124, out, err
                    if exited:
                        # Owned descendants may retain pipes after the module exits.
                        # Check the deadline after observing exit, including poll time.
                        stop_module(process)
                        cleaned = True
                        out, err = process.communicate(timeout=2)
                    else:
                        continue
                finished = True
                code = process.returncode
                if code == 0 and (not receipt.is_file() or receipt.read_bytes() != COMPLETED):
                    code = 1
                    err += b"Incomplete unittest run: child exited successfully before discovery and execution completed\n"
                return path, code, out, err
        finally:
            # An unexpected worker exception must leave a live child visible
            # to the controlling thread's cleanup snapshot.
            if finished:
                # Pipe EOF and leader exit do not imply solver completion: a
                # descendant may have closed its inherited capture streams.
                # Keep ownership until POSIX group cleanup succeeds, including
                # ordinary success/failure. On Windows the supervisor empties
                # its Job Object before exit; taskkill targets that live owner
                # on timeout/cancellation, and handle closure kills its job.
                if os.name != 'nt' and not cleaned:
                    stop_module(process)
                with lock:
                    active.discard(process)

    captures, problems = [], []
    failure = None
    pool = ThreadPoolExecutor(max_workers=workers)
    try:
        if termination['requested']:
            raise SystemExit(143)
        futures = [pool.submit(run_one, indexed) for indexed in enumerate(files)]
        # A later worker exception must not hide behind an earlier hung module.
        pending = iter(as_completed(futures))
        while True:
            try:
                termination['waiting'] = True
                if termination['requested']:
                    raise SystemExit(143)
                completed = next(pending, None)
                if completed is None:
                    return [future.result() for future in futures]
                completed.result()
            finally:
                # Disable asynchronous raises before any exceptional cleanup,
                # including a first SIGTERM during an unrelated worker failure.
                termination['waiting'] = False
    except BaseException as error:
        failure = error
        with lock:
            stopping = True
            processes = tuple(active)
        for process in processes:
            try:
                stop_module(process)
                captures.append(process)
            except Exception as cleanup_error:
                problems.append(str(cleanup_error))
        raise
    finally:
        try:
            pool.shutdown(wait=True, cancel_futures=stopping)
            # Workers must release communicate before we close stopped owners' pipes.
            for process in captures:
                problems.extend(close_captures(process))
            if problems:
                note = 'Isolated test cleanup failed: ' + '; '.join(problems)
                if hasattr(failure, 'add_note'):
                    failure.add_note(note)
                else:
                    print(note, file=sys.stderr)
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
