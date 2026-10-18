#!/usr/bin/env python3
"""Equality audit and same-process before/after timing of the null_exact/prim kernels on the pinned h=23 input.

thakrarsagar, with substantial AI assistance from Claude (Anthropic, Claude Opus 5.5). Apache-2.0.
Usage: python3 -B research/recycled-bit-nesting-reuse/bench.py [STOP_UTC_ISO]   (about 13 min, about 1.3 GB RSS; not part
of the bounded check). Builds Exact once with both kernels on every call (init audit). It then times a deterministic
400-move sample with each kernel in turn, and audits the basis of every distinct ledger-move key and the annihilator
of every distinct target. An optional STOP time ends the full-key audit early, and the output reports PARTIAL.
"""
import sys, time, random, json, hashlib, resource
from datetime import datetime, timezone
from pathlib import Path
ROOT = str(Path(__file__).resolve().parents[2])
sys.path.insert(0, ROOT + '/research/bit-reuse-147'); sys.path.insert(0, ROOT + '/research/recycled-bit-integration')
import verify as V, word147, frames147
assert V.__file__.startswith(ROOT + "/research/recycled-bit-integration"), V.__file__
STOP = datetime.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else None
t0 = time.time()
_, W, _, S, record, folder = word147.load_schedule()
plan = json.load(open(ROOT + '/research/recycled-bit-integration/plan.json'))
word = word147.Word(S, plan['elim'], plan['retained'], plan['pairs']); led = word.ledger(); fresh = word.new_moves(led)
moves = led['moves']; print('ledger', len(moves), 'fresh', len(fresh), flush=True)
sys.path.insert(0, str(folder)); import linalg, check_lifted as cl
ref_null, ref_prim = linalg.null_exact, frames147.prim
V.install_null_kernel(folder, 'fast'); fast_null, fast_prim = linalg.null_exact, frames147.prim
st = dict(nc=0, nref=0.0, nfast=0.0, pc=0, pref=0.0, pfast=0.0)
def null_a(A, k):
    a = time.perf_counter(); o = ref_null(A, k); b = time.perf_counter(); f = fast_null(A, k); c = time.perf_counter()
    assert f == o, ('MISMATCH', A, k)
    st['nc'] += 1; st['nref'] += b - a; st['nfast'] += c - b; return o
def prim_a(r):
    a = time.perf_counter(); o = ref_prim(r); b = time.perf_counter(); f = fast_prim(r); c = time.perf_counter()
    assert f == o and all(type(x) is int for x in f), ('MISMATCH prim', r)
    st['pc'] += 1; st['pref'] += b - a; st['pfast'] += c - b; return o
def set_kernels(n, p): linalg.null_exact = cl.null_exact = n; frames147.prim = p
set_kernels(null_a, prim_a)
t = time.time(); E = frames147.Exact(S, W, folder); print('init (audit both kernels)', round(time.time() - t, 1), 's', dict(st), flush=True)
init_st = dict(st)
# deterministic 400-move sample (seed 1), end-to-end before/after in this process
rng = random.Random(1); samp = rng.sample(sorted(moves, key=str), 400)
keys = sorted({a for _, a, b in samp} | {b for _, a, b in samp}, key=str)
def run_sample():
    E._basis.clear(); E._null.clear(); E.null_exact = linalg.null_exact
    t = time.perf_counter()
    for k in keys: E.basis(k)
    tb = time.perf_counter() - t; t = time.perf_counter()
    for _, a, b in samp:
        B = E.basis(b)
        if B and len(B) < E.h: E.null(b)
    tn = time.perf_counter() - t; t = time.perf_counter()
    ok = all(E.inside(a, b) for _, a, b in samp); ti = time.perf_counter() - t
    return tb, tn, ti, ok, dict(E._basis), dict(E._null)
res = {}
for rep in range(2):
    for name, nk, pk in (('reference', ref_null, ref_prim), ('fast', fast_null, fast_prim)):
        set_kernels(nk, pk); tb, tn, ti, ok, Bd, Nd = run_sample()
        res.setdefault(name, []).append((round(tb, 3), round(tn, 3), round(ti, 3)))
        assert ok; res[name + '_maps'] = (Bd, Nd)
        print('sample', name, 'basis', round(tb, 3), 'null', round(tn, 3), 'inside', round(ti, 3), flush=True)
assert res['reference_maps'] == res['fast_maps']; print('sample maps identical: keys', len(keys), 'nulls', len(res['fast_maps'][1]), flush=True)
del res['reference_maps'], res['fast_maps']
# full-key audit: every distinct basis key and every distinct target annihilator of the 202,190 ledger moves
set_kernels(null_a, prim_a); E.null_exact = null_a; E._basis.clear(); E._null.clear()
for k in st: st[k] = 0 if isinstance(st[k], int) else 0.0
allkeys = sorted({a for _, a, b in moves} | {b for _, a, b in moves}, key=str)
targets = sorted({b for _, a, b in moves}, key=str)
done_b = done_n = 0; complete = False
for k in allkeys:
    if STOP and datetime.now(timezone.utc) >= STOP: break
    E.basis(k); done_b += 1
    if done_b % 10000 == 0: print('basis audited', done_b, dict(st), flush=True)
else:
    for b in targets:
        if STOP and datetime.now(timezone.utc) >= STOP: break
        B = E.basis(b)
        if B and len(B) < E.h: E.null(b)
        done_n += 1
    else: complete = True
print('FULL-KEY AUDIT', 'complete' if complete else 'PARTIAL (time stop)', 'basis keys', done_b, '/', len(allkeys),
      'targets', done_n, '/', len(targets), 'calls', dict(st), flush=True)
print('summary', json.dumps(dict(init=init_st, sample=res, keys=len(allkeys), targets=len(targets),
      maxrss_mb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024, total_s=round(time.time() - t0, 1))), flush=True)
