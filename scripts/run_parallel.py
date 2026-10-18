#!/usr/bin/env python3
"""Run independent Python scripts concurrently, one fresh interpreter each.

Each script's combined output is printed as one block when it finishes, so
concurrent logs stay readable. Only list scripts that do not read a file that
another listed script writes. JOBS limits the number of concurrent processes
(default: one per CPU and per 3 GiB of memory); JOBS=1 runs them in order.
"""
# Adapted from eumemic, PR #154 (f571bcbd6e06618aeae0b8279da48060032dc74b).
# Apache-2.0; strict worker validation added during integration.
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import signal
import threading
import subprocess
import sys
import time


def available_cpus():
    if hasattr(os, 'sched_getaffinity'):
        return len(os.sched_getaffinity(0))
    return os.cpu_count() or 1


def memory_gib():
    """Physical memory in GiB, or None where the platform does not report it."""
    if sys.platform == 'win32':
        import ctypes

        class MemoryStatusEx(ctypes.Structure):
            _fields_ = [
                ('dwLength', ctypes.c_uint32),
                ('dwMemoryLoad', ctypes.c_uint32),
                ('ullTotalPhys', ctypes.c_uint64),
                ('ullAvailPhys', ctypes.c_uint64),
                ('ullTotalPageFile', ctypes.c_uint64),
                ('ullAvailPageFile', ctypes.c_uint64),
                ('ullTotalVirtual', ctypes.c_uint64),
                ('ullAvailVirtual', ctypes.c_uint64),
                ('ullAvailExtendedVirtual', ctypes.c_uint64),
            ]

        status = MemoryStatusEx()
        status.dwLength = ctypes.sizeof(status)
        try:
            query = ctypes.WinDLL('kernel32', use_last_error=True).GlobalMemoryStatusEx
            query.argtypes = [ctypes.POINTER(MemoryStatusEx)]
            query.restype = ctypes.c_int
            # Match sysconf's total physical memory, not currently free memory.
            if query(ctypes.byref(status)) and status.ullTotalPhys:
                return status.ullTotalPhys / 2**30
        except (AttributeError, OSError):
            pass
        return None
    try:
        return os.sysconf('SC_PAGE_SIZE')*os.sysconf('SC_PHYS_PAGES')/2**30
    except (AttributeError, ValueError, OSError):
        return None


def positive_jobs(value):
    """Reject invalid worker counts instead of silently clamping or hanging."""
    try:
        count = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError('worker count must be a positive integer') from exc
    if count < 1:
        raise ValueError('worker count must be a positive integer')
    return count


def jobs():
    """JOBS if set, else one process per CPU and per 3 GiB (the largest audits use 3 GiB)."""
    if 'JOBS' in os.environ:
        return positive_jobs(os.environ['JOBS'])
    memory = memory_gib()
    return max(1, min(available_cpus(), int(memory//3) if memory else available_cpus()))


# Process-registration and bounded-stop pattern adapted from PR2625
# (ywz65, OpenAI Codex), exact source head in the accompanying audit note.
def stop_script(process):
    """Stop the owned active script and its ordinary child processes."""
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
        raise RuntimeError(f'script {process.pid}: ' + '; '.join(problems))

def run_all(commands, cwd=None):
    """Run (label, argv) pairs concurrently and return the failed labels.

    Controlling exceptions stop active ordinary process trees and prevent
    queued launches. Normal completion retains one output block per script.
    """
    # Inherited optimization must not erase assertions in verification scripts
    # or their Python children. Deliberate -O/-OO argv controls remain explicit.
    env = os.environ.copy()
    env.pop('PYTHONOPTIMIZE', None)
    active = set()
    lock = threading.Lock()
    stopping = False

    def run(label, argv):
        start = time.monotonic()
        with lock:
            if stopping:
                return label, -1, '', 0
            process = subprocess.Popen(argv, cwd=cwd, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, text=True,
                                       errors='replace', start_new_session=True, env=env)
            active.add(process)
        finished = False
        try:
            while True:
                try:
                    output, _ = process.communicate(timeout=0.2)
                    finished = True
                    return label, process.returncode, output, time.monotonic()-start
                except subprocess.TimeoutExpired:
                    with lock:
                        if stopping:
                            # A failed stop or already orphaned child can keep
                            # stdout open. Cancellation must not wait for EOF.
                            finished = True
                            return label, -1, '', time.monotonic()-start
        finally:
            with lock:
                # Unexpected output errors leave the process owned by the
                # controlling cleanup path, even after this worker returns.
                if finished:
                    active.discard(process)

    failed = []
    pool = ThreadPoolExecutor(max_workers=jobs())
    try:
        futures = [pool.submit(run, label, argv) for label, argv in commands]
        for future in as_completed(futures):
            label, code, output, seconds = future.result()
            print(f'{"FAIL" if code else "Checked"} {label} ({seconds:.1f}s)', flush=True)
            print(output, end='' if output.endswith('\n') else '\n', flush=True)
            if code:
                failed.append(label)
        return failed
    except BaseException as error:
        with lock:
            stopping = True
            processes = tuple(active)
        problems = []
        for process in processes:
            try:
                stop_script(process)
            except Exception as cleanup_error:
                problems.append(str(cleanup_error))
        if problems:
            note = 'Parallel script cleanup failed: ' + '; '.join(problems)
            if hasattr(error, 'add_note'):
                error.add_note(note)
            else:
                print(note, file=sys.stderr)
        raise
    finally:
        pool.shutdown(wait=True, cancel_futures=stopping)


if __name__ == '__main__':
    scripts = sys.argv[1:]
    if not scripts:
        raise SystemExit('usage: run_parallel.py SCRIPT.py [SCRIPT.py ...]')
    failed = run_all([(script, [sys.executable, script]) for script in scripts])
    if failed:
        raise SystemExit('Failed: '+', '.join(failed))
    print(f'PASS all {len(scripts)} scripts')
