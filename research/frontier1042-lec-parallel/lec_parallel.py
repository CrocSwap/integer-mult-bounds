# SPDX-License-Identifier: Apache-2.0
"""Opt-in parallel runner for the pinned layer-end controls (frontier1042 leaver chain and T37).

Usage: lec_parallel.py WORD ROUTING OUTDIR [ENTERING] [--jobs N] [--script PINNED_SCRIPT]
       (environment PR635_CODE, and LEC_REASON_PINS for the leaver variant, exactly as for the step)

Drop-in for the step

    python -B <multicold>/code/run_portable.py PINNED_SCRIPT WORD ROUTING OUTDIR

where PINNED_SCRIPT is any byte-identical copy of one of the two signed variants in PINNED_SCRIPTS:
layer_end_controls_leaver.py v2 (the default; run five times by reproduce_leaver_chain.py's lec()
in the frontier1042 leaver chain, the cold baseline of selected frontier1094) or
layers_p6n/layer_end_controls.py (run by the T37 u8-native stage, complex741's p6n stage and the
#799 native stage). The pinned script audits the unmutated word and 95 mutated words with
PR635's hpe_audit_and_transport.run; every mutant must be rejected for its pinned reason. The 96
audits are independent pure computations. The pinned launcher and script are never edited and
never re-implemented:

1. record:   the pinned launcher runs the pinned script with a stand-in hpe_audit_and_transport
             whose run() records the exact gzip bytes of each trial word. It answers the first
             (unmutated) word with success and every other word with a placeholder rejection
             that satisfies any reason check. Its receipt goes to a scratch directory and is
             discarded. As each word is recorded, the real audit of it starts in a worker.
2. evaluate: every distinct word is audited by the real, digest-checked PR635 run() in a worker
             process, giving exactly the outcome (and printed output) trial() would see.
3. replay:   the pinned launcher runs the pinned script again with a stand-in that prints the
             captured output and returns or raises the real outcome for the identical bytes. The
             script's own assertions accept or reject every control, check every pinned reason
             and write COLD-END-CONTROLS.json. The sequence of trial words must equal the
             recorded one.

Outcomes are keyed by the sha256 of the exact trial bytes, the absolute (unresolved) routing path
and the routing file's sha256, so a Runner shared across steps (chain_lec.py) audits a word only
once even if two steps build it. A worker that dies fails the run instead of losing its task.
"""
import argparse
import gzip
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

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from audit_worker import evaluate, init_worker, load_audit  # noqa: E402

LAUNCHER = ROOT / 'research/complex-k492-owner-repair/vendor/multicold/code/run_portable.py'
LAUNCHER_SHA256 = '322d29d43dbee8130cde15d4bf05396698b5e3dfe3735813899db91cc0ba7955'
SCRIPT = ROOT / 'research/gauge44-leaver8/construction/leaver/layer_end_controls_leaver.py'
SCRIPT_SHA256 = '4ba676f1ea326b739a64c3477f64eeb295f8151514f78fa7e62b71e4373a6206'
T37_SCRIPT = ROOT / 'research/complex-t21-owners/vendor/pr870/construction/layers_p6n/layer_end_controls.py'
T37_SCRIPT_SHA256 = 'fc58c5699ba6191c1163a3041241f6f0b619626c4462cd99bcf88210bac9e81e'
# The runner accepts a script only by digest: these two signed variants call the audit the same way.
PINNED_SCRIPTS = {SCRIPT_SHA256: 'layer_end_controls_leaver.py v2', T37_SCRIPT_SHA256: 'layers_p6n/layer_end_controls.py'}
# Interpreter settings of every chain step (reproduce_leaver_chain.py run(): env and -B).
CHAIN_ENV = dict(PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0')


class AnyReason(str):
    """Placeholder message for the record pass: every reason substring is 'in' it."""

    def __contains__(self, item):
        return True


class Placeholder:
    def __repr__(self):
        return AnyReason('placeholder rejection (record pass only)')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def ensure_chain_interpreter(argv):
    """Re-execute under the chain's interpreter settings (UTF-8 mode, no int digit limit, -B)."""
    if not __debug__:
        raise RuntimeError('assertions must remain enabled')
    if sys.flags.utf8_mode and sys.get_int_max_str_digits() == 0 and sys.dont_write_bytecode:
        return
    env = dict(os.environ, **CHAIN_ENV)
    env.pop('PYTHONOPTIMIZE', None)
    os.execve(sys.executable, [sys.executable, '-B', *argv], env)


def check_digest(path, expected, what):
    if sha(Path(path).read_bytes()) != expected:
        raise RuntimeError('pinned %s digest mismatch: %s' % (what, path))


def routing_key(routing_arg, cache):
    """(path, digest) of the routing file exactly as trial() hands it to the audit.

    The path is made absolute but not resolved: PR635's reader picks gzip or JSON from the
    suffix of the path it is given, so symlinks must not be followed here. The digest makes an
    outcome table shared across steps safe even if the file at that path changes.
    """
    path = str(Path(routing_arg).absolute())
    if path not in cache:
        cache[path] = sha(Path(path).read_bytes())
    return path, cache[path]


def run_pinned(argv, stub_run, script=SCRIPT, stdout=None):
    """One run of the pinned launcher on the pinned script, with a stand-in audit module.

    Global state touched by the launcher and the script (sys.argv, sys.path, the stand-in module,
    Path.write_text, gzip.compress, sys.stdout) is restored afterwards, so every pass behaves
    like a fresh `python -B run_portable.py SCRIPT ARGS`.
    """
    check_digest(LAUNCHER, LAUNCHER_SHA256, 'run_portable.py')
    if sha(Path(script).read_bytes()) not in PINNED_SCRIPTS:
        raise RuntimeError('pinned layer-end-controls digest mismatch: %s' % script)
    stub = types.ModuleType('hpe_audit_and_transport')
    stub.run = stub_run
    saved = (sys.argv, list(sys.path), sys.modules.get('hpe_audit_and_transport'), sys.stdout,
             Path.write_text, gzip.compress)
    sys.modules['hpe_audit_and_transport'] = stub
    sys.argv = [str(LAUNCHER), str(script), *map(str, argv)]
    if stdout is not None:
        sys.stdout = stdout
    try:
        runpy.run_path(str(LAUNCHER), run_name='__main__')
    finally:
        sys.stdout.flush()
        sys.argv, sys.path[:] = saved[0], saved[1]
        if saved[2] is None:
            sys.modules.pop('hpe_audit_and_transport', None)
        else:
            sys.modules['hpe_audit_and_transport'] = saved[2]
        sys.stdout, Path.write_text, gzip.compress = saved[3], saved[4], saved[5]


class Runner:
    """A worker pool and an outcome table shared by any number of control steps."""

    def __init__(self, code_dir, jobs):
        self.code_dir, self.jobs = str(code_dir), jobs
        load_audit(self.code_dir)                      # digest check before any work starts
        self.table = {}
        self.pool, self.workers = None, []
        if jobs > 1:
            self.pool = mp.get_context('spawn').Pool(jobs, initializer=init_worker, initargs=(self.code_dir,))
            self.workers = list(self.pool._pool)       # the pool never retires workers: any exit is a loss
        else:
            init_worker(self.code_dir)

    def close(self):
        if self.pool is not None:
            self.pool.close()
            self.pool.join()
            self.pool = None

    def terminate(self):
        if self.pool is not None:
            self.pool.terminate()
            self.pool.join()
            self.pool = None

    def __enter__(self):
        return self

    def __exit__(self, kind, value, tb):
        self.close() if kind is None else self.terminate()

    def wait(self, result):
        """result.get(), failing closed if a worker died: Pool would respawn it and lose its task."""
        while True:
            if any(p.exitcode is not None for p in self.workers):
                raise RuntimeError('an audit worker process exited; refusing to wait for a lost task')
            if result.ready():
                return result.get()
            result.wait(0.5)

    def step(self, word, routing, outdir, entering=None, stdout=None, script=SCRIPT, tamper=None):
        """Run the pinned controls on WORD; returns timing and reuse statistics.

        `tamper(table, recorded)` is a test hook used only by verify.py's controls: it edits a
        private copy of the outcome table before the replay.
        """
        start = time.monotonic()
        tail = [] if entering is None else [str(entering)]
        recorded, fresh, digests = [], 0, {}

        def record(p, routing_arg, out):
            nonlocal fresh
            data = Path(p).read_bytes()
            key = (sha(data), *routing_key(routing_arg, digests))
            recorded.append(key)
            if key not in self.table:
                fresh += 1
                task = (data, key[1])
                self.table[key] = (self.pool.apply_async(evaluate, (task,)) if self.pool is not None
                                   else evaluate(task))
            if len(recorded) == 1:
                return None                              # the pinned script's first trial is the unmutated word
            raise AssertionError(Placeholder())

        sink = tempfile.mkdtemp()
        try:
            with open(os.devnull, 'w') as devnull:
                run_pinned([word, routing, sink, *tail], record, script, devnull)
        finally:
            shutil.rmtree(sink, ignore_errors=True)
        recorded_at = time.monotonic()
        for key in set(recorded):
            if not isinstance(self.table[key], tuple):
                self.table[key] = self.wait(self.table[key])
        evaluated_at = time.monotonic()

        table = dict(self.table)
        if tamper is not None:
            tamper(table, recorded)
        seen = []

        def replay(p, routing_arg, out):
            data = Path(p).read_bytes()
            key = (sha(data), *routing_key(routing_arg, digests))
            seen.append(key)
            if key not in table:
                raise RuntimeError('the replay built a trial word that the record pass did not')
            kind, args, text = table[key]
            if text:
                sys.stdout.write(text)
                sys.stdout.flush()
            if kind == 'pass':
                return None
            if kind == 'assert':
                raise AssertionError(*args)
            raise RuntimeError('audit raised a non-assertion error: ' + args[0])

        run_pinned([word, routing, outdir, *tail], replay, script, stdout)
        if seen != recorded:
            raise RuntimeError('the replay produced a different sequence of trial words')
        done = time.monotonic()
        return dict(trials=len(recorded), distinct=len(set(recorded)), audited_now=fresh,
                    routing=sorted(digests), record_seconds=round(recorded_at - start, 1),
                    evaluate_wait_seconds=round(evaluated_at - recorded_at, 1),
                    replay_seconds=round(done - evaluated_at, 1), runner_seconds=round(done - start, 1))


def main():
    ensure_chain_interpreter([str(Path(__file__).resolve()), *sys.argv[1:]])
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('word')
    ap.add_argument('routing')
    ap.add_argument('outdir')
    ap.add_argument('entering', nargs='?')
    ap.add_argument('--jobs', type=int, default=os.cpu_count() or 1)
    ap.add_argument('--script', default=str(SCRIPT), help='a byte-identical copy of a pinned variant (default: leaver v2)')
    a = ap.parse_args()
    with Runner(os.environ['PR635_CODE'], a.jobs) as runner:   # prints exactly what the pinned step prints
        runner.step(a.word, a.routing, a.outdir, a.entering, script=a.script)


if __name__ == '__main__':
    main()
