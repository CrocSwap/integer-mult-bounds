#!/usr/bin/env python3
"""Run independent Python scripts concurrently, one fresh interpreter each.

Each script's combined output is printed as one block when it finishes, so
concurrent logs stay readable. Only list scripts that do not read a file that
another listed script writes. JOBS limits the number of concurrent processes
(default: one per CPU and per 3 GiB of memory); JOBS=1 runs them in order.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import subprocess
import sys
import time


def available_cpus():
    if hasattr(os, 'sched_getaffinity'):
        return len(os.sched_getaffinity(0))
    return os.cpu_count() or 1


def memory_gib():
    """Physical memory in GiB, or None where the platform does not report it."""
    try:
        return os.sysconf('SC_PAGE_SIZE')*os.sysconf('SC_PHYS_PAGES')/2**30
    except (AttributeError, ValueError, OSError):
        return None


def jobs():
    """JOBS if set, else one process per CPU and per 3 GiB (the largest audits use 3 GiB)."""
    if os.environ.get('JOBS'):
        return max(1, int(os.environ['JOBS']))
    memory = memory_gib()
    return max(1, min(available_cpus(), int(memory//3) if memory else available_cpus()))


def run_all(commands, cwd=None):
    """Run (label, argv) pairs concurrently and return the failed labels."""
    def run(label, argv):
        start = time.monotonic()
        result = subprocess.run(argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, errors='replace')
        return label, result.returncode, result.stdout, time.monotonic()-start
    failed = []
    with ThreadPoolExecutor(max_workers=jobs()) as pool:
        futures = [pool.submit(run, label, argv) for label, argv in commands]
        for future in as_completed(futures):
            label, code, output, seconds = future.result()
            print(f'{"FAIL" if code else "Checked"} {label} ({seconds:.1f}s)', flush=True)
            print(output, end='' if output.endswith('\n') else '\n', flush=True)
            if code:
                failed.append(label)
    return failed


if __name__ == '__main__':
    scripts = sys.argv[1:]
    if not scripts:
        raise SystemExit('usage: run_parallel.py SCRIPT.py [SCRIPT.py ...]')
    failed = run_all([(script, [sys.executable, script]) for script in scripts])
    if failed:
        raise SystemExit('Failed: '+', '.join(failed))
    print(f'PASS all {len(scripts)} scripts')
