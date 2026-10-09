"""Terminal elimination on #144's bit word (Swapnil Jain's round-seven PR97 word with #144's 9,543 selected gauges and
2,022 omitted reads at the zero frame).  Stdlib only.

Candidate u: an original deferred slot (selected or omitted) that is an output slot and never a source (never the
non-pivot of an addition, never the pivot of a fan).  Eliminating u deletes its read, its output read, its inverse
writes and V^-1, and applies each forward write into u (start copy or V gate, every addition it pivots) to its target
y_T at the same time and frame (SovereignSteak's PR122 operation, here on the bit word).  #144's charged target chain
of T is [0, sigma of the selected readouts on T in readout order (positive Z support), h-1]; after elimination it is
[0, remaining selected sigmas, redirected frames in time order, h-1].  A target's subset is legal iff that sequence
is nested exactly over Q (bases: sigma from the frozen data, node/late/output frames exact).
Usage: python3 research/bit-elim-144/elim144.py FRAMES_CACHE.json.gz OUT_PLAN.json [--omitted-only]"""
import gzip
import importlib.util
import json
import math
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from partial_gauge_bit import frozen_sources  # noqa: E402


def schedule144():
    record = json.loads((ROOT / 'certificates/paired-cube-bit-input.json').read_text())
    folder, _ = frozen_sources(record)
    sel = json.loads((ROOT / record['selection_file']).read_text())
    spec = importlib.util.spec_from_file_location('pr97_deferred', folder / 'deferred.py')
    dr = importlib.util.module_from_spec(spec); spec.loader.exec_module(dr)
    W = json.load(gzip.open(folder / 'witness_23.json.gz', 'rt')); D = json.load(gzip.open(folder / 'deferred_23.json.gz', 'rt'))
    S = dr.Schedule(W, D)
    return dr, W, D, S, sel['retained_readout_order'], sel['omitted_readout_order'], record


if __name__ == '__main__':
    CACHE, OUT = [a for a in sys.argv[1:] if not a.startswith('--')]
    dr, W, D, S, selected, omitted, record = schedule144()
    orig_sel = set(S.sel); chosen = set(selected)
    h = S.h; m = 3 * h
    def norm(k): return tuple(tuple(x) if isinstance(x, list) else x for x in k)
    cache = {norm(json.loads(k)): B for k, B in json.load(gzip.open(CACHE, 'rt')).items()}
    cache_out = {tuple(k[2]): B for k, B in cache.items() if k[0] == 'out'}
    FULL = [[int(i == j) for j in range(h)] for i in range(h)]
    def basis(k):
        if k[0] == 'sigma': return S.sigma[k[1]]
        if k[0] == 'v': return S.vstart[k[1]]
        if k[0] == '0': return []
        if k[0] == 'F': return FULL
        if k[0] == 'out': return cache_out[tuple(k[2])]
        return cache[k]
    _nz = {}
    def null(B):
        kb = tuple(map(tuple, B))
        if kb in _nz: return _nz[kb]
        rows = [[Fraction(x) for x in r] for r in B]; piv = []; Rr = []
        for r in rows:
            for pc, b in zip(piv, Rr):
                c = r[pc]
                if c: r = [x - c * y for x, y in zip(r, b)]
            i = next((i for i, x in enumerate(r) if x), None)
            if i is None: continue
            inv = 1 / r[i]; r = [y * inv for y in r]
            Rr = [[x - b[i] * y for x, y in zip(b, r)] if b[i] else b for b in Rr]
            Rr.append(r); piv.append(i)
        out = []
        for f in [c for c in range(h) if c not in piv]:
            x = [Fraction(0)] * h; x[f] = Fraction(1)
            for pc, b in zip(piv, Rr): x[pc] = -b[f]
            den = 1
            for q in x: den = den * q.denominator // math.gcd(den, q.denominator)
            out.append([int(q * den) for q in x])
        _nz[kb] = out
        return out
    def inside(a, b):
        Ab, Bb = basis(a), basis(b)
        if not Ab or len(Bb) == h: return True
        return all(sum(x * z for x, z in zip(ra, rz)) == 0 for ra in Ab for rz in null(Bb))
    src = Counter()
    for op in S.ops:
        if op[0] == 'add': src[op[2]] += 1
        elif op[0] == 'fan': src[op[1]] += 1
    cands = [u for u in S.out if u in orig_sel and src[u] == 0]
    if '--omitted-only' in sys.argv: cands = [u for u in cands if u not in chosen]
    S.sel = chosen                                   # #144's chains: selected slots start at sigma, others at 0
    adj = S.adjoint()
    # redirected update frames of each candidate, in time order (late V gates precede the rest phase)
    prev = {}; pred = defaultdict(list); last = {}
    for i, op in enumerate(S.ops):
        for s in S.touch(op):
            if s in prev: pred[i].append(prev[s])
            prev[s] = i; last[s] = i
    Anc = set(); st = [last[s] for s in S.ret]
    while st:
        i = st.pop()
        if i in Anc: continue
        Anc.add(i); st.extend(pred[i])
    late_pos = {s: i for i, s in enumerate(S.late_v)}
    upd = defaultdict(list)
    for i, op in enumerate(S.ops):
        if op[0] == 'add' and op[1] in S.out:
            upd[op[1]].append(((2, i, 0), ('n', op[3])))
        elif op[0] == 'fan':
            for j, f in enumerate(sorted(op[2], key=lambda s: S.dim(S.start_key(s)))):
                if f in S.out: upd[f].append(((2, i, j), S.start_key(f)))
    for u in cands:
        if u in S.srcop: upd[u].append(((1, late_pos[u], 0), ('v', u)))
        assert all(t[1] not in Anc for t, _ in upd[u] if t[0] == 2), 'deferred slot untouched by phase 1'
        upd[u].sort()
        assert [k for _, k in upd[u]] == S.chain_keys(u)[1:-2]
    levels = defaultdict(list)
    for s in selected:
        for t, c in adj[s].items():
            if c > 0: levels[t].append(s)
    def tpath(t, U):
        seq = [('0',)] + [('sigma', s) for s in levels[t] if s not in U] + \
              [k for _, k in sorted(e for u in U for e in upd[u])] + [('out', 0, S.trip[t])]
        out = []
        for k in seq:
            if not out or out[-1] != k: out.append(k)
        return out
    xl = lambda t: t * math.log(m / t) if t > 0 else 0.0
    def steps(p):
        ds = [S.dim(k) for k in p]
        return [b - a for a, b in zip(ds, ds[1:]) if b > a]
    def role_children(u):
        ds = [S.dim(k) for k in S.chain_keys(u)]
        ch = [b - a for a, b in zip(ds, ds[1:]) if b > a]
        return ch + ([3 * S.f[u] / 3] if u in chosen else [])
    byT = defaultdict(list)
    for u in cands: byT[S.tid[S.out[u][1]]].append(u)
    elim = set(); stat = Counter(); total = 0.0
    for t in sorted(byT):
        U = byT[t]; base = sum(xl(d) for d in steps(tpath(t, [])))
        best = (0.0, ())
        for r in range(1, len(U) + 1):
            for sub in combinations(U, r):
                p = tpath(t, sub)
                if not all(S.dim(a) <= S.dim(b) and inside(a, b) for a, b in zip(p, p[1:])): continue
                g = base - sum(xl(d) for d in steps(p))
                for u in sub:
                    ds = [S.dim(k) for k in S.chain_keys(u)]
                    g += sum(xl(b - a) for a, b in zip(ds, ds[1:]) if b > a)
                    if u in chosen: g += xl(3 * S.f[u]) / 3
                if g > best[0] + 1e-12: best = (g, sub)
        stat[len(best[1])] += 1; elim.update(best[1]); total += best[0]
    print('candidates', len(cands), '(selected %d, omitted %d)' % (sum(u in chosen for u in cands), sum(u not in chosen for u in cands)),
          'eliminated', len(elim), '(selected %d)' % sum(u in chosen for u in elim), dict(stat), 'gain %.0f' % total)
    Path(OUT).write_text(json.dumps(dict(elim=sorted(elim)), indent=0) + '\n')
