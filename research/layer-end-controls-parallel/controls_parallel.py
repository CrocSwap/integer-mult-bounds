# SPDX-License-Identifier: Apache-2.0
"""Opt-in parallel runner for the pinned U8 layer-end controls, with identical receipts.

Usage: controls_parallel.py LAYERED-WORD.json.gz ROUTING OUTDIR [ENTERING] [--jobs N]
       (environment PR635_CODE exactly as for the pinned script)

The pinned script research/complex-t21-owners/vendor/pr870/construction/layers_p6n/
layer_end_controls.py builds 95 mutated words and audits each one, plus the unmutated
word, with PR635's hpe_audit_and_transport.run. Every trial is independent. The pinned
script is never edited and never re-implemented:

1. record:   the pinned script runs with a stand-in hpe_audit_and_transport whose run()
             records the exact gzip bytes of each trial word. It answers the unmutated
             word with success and every other word with a placeholder rejection that
             satisfies any reason check. No receipt is written in this pass.
2. evaluate: every distinct recorded word is audited by the real, pinned
             hpe_audit_and_transport.run in a worker process, giving exactly the outcome
             trial() would see (the AssertionError arguments, or success).
3. replay:   the pinned script runs again with a stand-in that returns or raises the
             precomputed real outcome for the identical bytes. Its own assertions accept
             or reject every control and write COLD-END-CONTROLS.json. The sequence of
             trial words must equal the recorded one.
"""
import argparse
import hashlib
import multiprocessing as mp
import os
import runpy
import shutil
import sys
import tempfile
import time
import types
from pathlib import Path

from audit_worker import evaluate, init_worker

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'research/complex-t21-owners/vendor/pr870/construction/layers_p6n/layer_end_controls.py'
SCRIPT_SHA256 = 'fc58c5699ba6191c1163a3041241f6f0b619626c4462cd99bcf88210bac9e81e'


class AnyReason(str):
    """Placeholder message for the record pass: every reason substring is 'in' it."""

    def __contains__(self, item):
        return True


class Placeholder:
    def __repr__(self):
        return AnyReason('placeholder rejection (record pass only)')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def run_pinned(argv, stub_run):
    stub = types.ModuleType('hpe_audit_and_transport')
    stub.run = stub_run
    saved_argv, saved_mod = sys.argv, sys.modules.get('hpe_audit_and_transport')
    sys.modules['hpe_audit_and_transport'] = stub
    sys.argv = [str(SCRIPT), *argv]
    try:
        runpy.run_path(str(SCRIPT), run_name='__main__')
    finally:
        sys.argv = saved_argv
        if saved_mod is None:
            sys.modules.pop('hpe_audit_and_transport', None)
        else:
            sys.modules['hpe_audit_and_transport'] = saved_mod


def main():
    if not __debug__:
        raise RuntimeError('assertions must remain enabled')
    ap = argparse.ArgumentParser()
    ap.add_argument('word')
    ap.add_argument('routing')
    ap.add_argument('outdir')
    ap.add_argument('entering', nargs='?')
    ap.add_argument('--jobs', type=int, default=os.cpu_count() or 1)
    a = ap.parse_args()
    if sha(SCRIPT.read_bytes()) != SCRIPT_SHA256:
        raise RuntimeError('pinned layer_end_controls.py digest mismatch')
    code_dir = os.environ['PR635_CODE']
    argv = [a.word, a.routing, a.outdir] + ([a.entering] if a.entering else [])
    start = time.monotonic()

    # 1. record, while 2. the real audits already run in the pool as each word is recorded
    recorded = []
    pending = {}
    routing_abs = str(Path(a.routing).resolve())
    pool = None if a.jobs == 1 else mp.get_context('spawn').Pool(a.jobs, initializer=init_worker, initargs=(code_dir,))
    if pool is None:
        init_worker(code_dir)

    def record(p, routing, out):
        data = Path(p).read_bytes()
        key = sha(data)
        recorded.append(key)
        if key not in pending:
            pending[key] = (pool.apply_async(evaluate, ((data, routing_abs),)) if pool is not None
                            else evaluate((data, routing_abs)))
        if len(recorded) == 1:
            return None                      # the pinned script's first trial is the unmutated word
        raise AssertionError(Placeholder())
    sink = tempfile.mkdtemp()
    try:
        devnull = open(os.devnull, 'w')
        saved = sys.stdout
        sys.stdout = devnull
        try:
            run_pinned([a.word, a.routing, sink] + argv[3:], record)
        finally:
            sys.stdout = saved
            devnull.close()
        print('recorded', len(recorded), 'trial words', len(pending), 'distinct', 'seconds',
              round(time.monotonic() - start, 1), flush=True)
        table = {k: (v.get() if pool is not None else v) for k, v in pending.items()}
    finally:
        shutil.rmtree(sink, ignore_errors=True)
        if pool is not None:
            pool.close()
            pool.join()
    print('evaluated', len(table), 'words with', a.jobs, 'jobs', 'seconds', round(time.monotonic() - start, 1), flush=True)

    # 3. replay
    seen = []

    def replay(p, routing, out):
        data = Path(p).read_bytes()
        key = sha(data)
        seen.append(key)
        kind, args = table[key] if key in table else evaluate_here(data, routing)
        if kind == 'pass':
            return None
        if kind == 'assert':
            raise AssertionError(*args)
        raise RuntimeError('audit raised a non-assertion error: ' + args[0])

    def evaluate_here(data, routing):
        init_worker(code_dir)
        return evaluate((data, str(routing)))
    run_pinned(argv, replay)
    if seen != recorded:
        raise RuntimeError('the replay produced a different sequence of trial words')
    print('replayed', len(seen), 'trials; total seconds', round(time.monotonic() - start, 1), flush=True)


if __name__ == '__main__':
    main()
