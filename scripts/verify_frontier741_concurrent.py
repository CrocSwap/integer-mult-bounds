#!/usr/bin/env python3
"""Cold replay of PR589 + PR741 with the bit and complex suppliers overlapped.

Sibling of scripts/verify_frontier741.py, which stays unchanged because its hash
is pinned by the selected record and checkpoint certificates. It executes the same
two supplier commands, in the same environment, into the same output layout
(bit/, complex/, bit589.log, complex741.log, STEPS.json, RESULT.json), then runs
the same scripts/verify_frontier741_bindings.py. The only change is that the two
supplier commands run at the same time: neither reads anything the other writes
(bit589 writes only under <work>/bit, complex741 only under <work>/complex).
If either supplier fails, the other is stopped and nothing is bound.

The output is a valid --ancestor for scripts/verify_frontier799.py (which then
records it as reused ancestry, as for any externally produced ancestor).
Optional --complex-jobs N (>1) additionally uses the dependency-scheduled
complex replay of scripts/verify_complex741_parallel.py.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[1]


def supplier_commands(work, complex_jobs=1):
    """The commands scripts/verify_frontier741.py runs, as (name, argv) in its order."""
    if complex_jobs > 1:
        complex_command = [sys.executable, '-B', ROOT / 'scripts/verify_complex741_parallel.py',
                           '--work', work / 'complex', '--jobs', complex_jobs]
    else:
        complex_command = [sys.executable, '-B', ROOT / 'research/complex-sw4-frame8/verify.py',
                           '--work', work / 'complex']
    return [('bit589', ['bash', ROOT / 'research/e8-bit-p111-tuned/tune/verify.sh', work / 'bit']),
            ('complex741', complex_command)]


def binding_command(work):
    return [sys.executable, '-B', ROOT / 'scripts/verify_frontier741_bindings.py',
            '--bit', work / 'bit', '--complex', work / 'complex', '--out', work / 'RESULT.json']


def supplier_env():
    env = dict(os.environ, PYTHON=sys.executable, PYTHONDONTWRITEBYTECODE='1',
               SW4_FRAME8_PYTHON=sys.executable)
    for name in ('PYTHONOPTIMIZE', 'WITNESS_DISCOVER', 'WITNESS_RECORD', 'SW4_PIN'):
        env.pop(name, None)
    return env


def _stop(process):
    if process.poll() is not None:
        return
    try:
        if hasattr(os, 'killpg'):
            os.killpg(process.pid, signal.SIGTERM)
        else:
            process.terminate()
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=20)
    except subprocess.TimeoutExpired:
        if hasattr(os, 'killpg'):
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
        process.wait()


def run_concurrent(jobs, work, env, cwd=ROOT):
    """Run [(name, argv)] at once, one log per job under work. Returns step records
    in the given order. On the first non-zero exit the others are stopped and
    RuntimeError names the failing job; stopped jobs record their negative exit code.
    """
    state = {}
    first_failure = []
    lock = threading.Lock()
    start = time.monotonic()
    for name, command in jobs:
        log_path = work / (name + '.log')
        stream = log_path.open('w')
        print('RUN', name, flush=True)
        process = subprocess.Popen(list(map(str, command)), cwd=cwd, env=env, stdout=stream,
                                   stderr=subprocess.STDOUT,
                                   start_new_session=hasattr(os, 'killpg'))
        state[name] = dict(process=process, stream=stream, log=log_path, started=time.monotonic())

    def watch(name):
        item = state[name]
        code = item['process'].wait()
        item['seconds'] = time.monotonic() - item['started']
        with lock:
            if code != 0 and not first_failure:
                first_failure.append(name)
                for other, other_item in state.items():
                    if other != name:
                        _stop(other_item['process'])
        if code == 0:
            print('PASS', name, flush=True)

    threads = [threading.Thread(target=watch, args=(name,)) for name, _ in jobs]
    for thread in threads:
        thread.start()
    try:
        for thread in threads:
            thread.join()
    except BaseException:
        for item in state.values():
            _stop(item['process'])
        raise
    finally:
        for item in state.values():
            item['stream'].close()
    records = [dict(name=name, exit_code=state[name]['process'].returncode,
                    seconds=state[name]['seconds'],
                    log_sha256=hashlib.sha256(state[name]['log'].read_bytes()).hexdigest())
               for name, _ in jobs]
    (work / 'CONCURRENCY.json').write_text(json.dumps(dict(
        jobs=[name for name, _ in jobs], wall_seconds=time.monotonic() - start,
        sequential_seconds=sum(r['seconds'] for r in records)), indent=2) + '\n')
    if first_failure:
        raise RuntimeError(f"{first_failure[0]} failed; inspect {state[first_failure[0]]['log']}",
                           records)
    return records


def replay(work, complex_jobs=1):
    steps = []
    def dump():
        (work / 'STEPS.json').write_text(json.dumps(steps, indent=2) + '\n')
    env = supplier_env()
    try:
        steps.extend(run_concurrent(supplier_commands(work, complex_jobs), work, env))
    except RuntimeError as error:
        steps.extend(error.args[1])
        dump()
        raise SystemExit(error.args[0])
    dump()
    name, command = 'bindings', binding_command(work)
    start = time.monotonic()
    log = work / (name + '.log')
    print('RUN', name, flush=True)
    with log.open('w') as stream:
        result = subprocess.run(list(map(str, command)), cwd=ROOT, env=env,
                                stdout=stream, stderr=subprocess.STDOUT)
    steps.append(dict(name=name, exit_code=result.returncode, seconds=time.monotonic() - start,
                      log_sha256=hashlib.sha256(log.read_bytes()).hexdigest()))
    dump()
    if result.returncode:
        raise SystemExit(f'{name} failed; inspect {log}')
    print('PASS', name, flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--complex-jobs', type=int, default=1,
                   help='>1 uses the dependency-scheduled complex replay with this many workers')
    a = p.parse_args()
    work = a.work.resolve()
    if sys.flags.optimize or work.exists() or work.is_relative_to(ROOT) or a.complex_jobs < 1:
        raise SystemExit('Use enabled assertions, positive jobs, and a fresh directory outside the repository')
    work.mkdir(parents=True)
    replay(work, a.complex_jobs)
    print('PASS selected finite composition; inherited hypotheses remain')


if __name__ == '__main__':
    main()
