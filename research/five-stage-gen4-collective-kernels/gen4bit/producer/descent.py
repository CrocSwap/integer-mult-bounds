#!/usr/bin/env python3
"""Endpoint frame descent for a physical paired-cube bit word (PR200 physical-layer rules).

Moves equal-frame connected groups of operations to the join of their incoming frames and node value
spans, or to the meet of their outgoing frames (degenerate endpoints repaired by one row), accepting a move
only when the five-stage first-order cost  sum r*ln(120/r)  over all physical role chains decreases.
Gauge, root, source, target and full frames are fixed; alias splices (donor -> recipient gauge) are kept.

usage: descent.py PKGDIR OUTDIR   (PKGDIR = PR200-layout package whose selected/bit holds the word)
Prepared by DreamingOfClouds with Anthropic Claude assistance; Apache-2.0.
"""
import sys, json, gzip, math, time
from pathlib import Path
from collections import defaultdict, Counter

pkg = Path(sys.argv[1]); out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(pkg / 'bit'))
from word import Candidate

t0 = time.time()
W = Candidate(); C = W.C; mod = W.module; h = W.h
C.decoder(); C.geometry()
FULL = W.w['full_frame']
ops = W.ops; nops = len(ops)
opframe = list(W.opframe)

# ---------------------------------------------------------------- frame registry helpers
key_of = {}
def bkey(B): return tuple(sorted(map(tuple, B)))
for f, B in C.B.items():
    key_of.setdefault(bkey(B), f)

def register(rows):
    B, _ = mod.reduce_rows(rows, h)
    B = [tuple(r) for r in B]
    k = bkey(B)
    if k in key_of: return key_of[k]
    f = max(C.B) + 1
    A, _ = mod.kernel(B, h)
    C.B[f], C.A[f], C.dimf[f] = B, A, len(B)
    key_of[k] = f
    return f

join_cache = {}
def join(fs):
    fs = tuple(sorted(set(fs)))
    if len(fs) == 1: return fs[0]
    r = join_cache.get(fs)
    if r is None:
        rows = [b for f in fs for b in C.B[f]]
        r = join_cache[fs] = register(rows)
    return r

meet_cache = {}
def meet(fs):
    fs = tuple(sorted(set(fs)))
    if len(fs) == 1: return fs[0]
    r = meet_cache.get(fs)
    if r is None:
        ann = [a for f in fs for a in C.A[f]]
        B, _ = mod.kernel(ann, h) if ann else ([tuple(int(i == j) for j in range(h)) for i in range(h)], None)
        r = meet_cache[fs] = register(B)
    return r

nd_cache = {}
def nondeg(f):
    r = nd_cache.get(f)
    if r is None: r = nd_cache[f] = C.nondeg(f)
    return r

def sub(a, b): return C.sub(a, b)

# node value spans
span_cache = {}
def node_span(n):
    r = span_cache.get(n)
    if r is None:
        bits = C.sup[n]; rows = []
        while bits:
            low = bits & -bits; s = low.bit_length() - 1; bits -= low
            rows.append(C.chi[s])
        r = span_cache[n] = register(rows)
    return r

def repair_up(L, U):
    """smallest nondegenerate frame containing L inside U: L itself or L + one row of U."""
    if nondeg(L): return L
    for b in C.B[U]:
        f = register(list(C.B[L]) + [b])
        if C.dimf[f] == C.dimf[L] + 1 and nondeg(f): return f
    return None

def repair_down(L, U):
    """largest nondegenerate frame inside U containing L: U itself or U minus one row (kernel of A_U + 1 row)."""
    if nondeg(U): return U
    # hyperplanes of U containing L: add one annihilator row vanishing on L but not on U
    BL = C.B[L]
    cand = []
    for e in range(h):
        a = [int(i == e) for i in range(h)]
        cand.append(a)
    # project candidate covectors to vanish on L: use combinations orthogonal to B_L via kernel of B_L
    K, _ = mod.kernel(BL, h) if BL else ([tuple(int(i == j) for j in range(h)) for i in range(h)], None)
    for a in K:
        rows = list(C.A[U]) + [a]
        B, _ = mod.kernel(rows, h)
        f = register(B)
        if C.dimf[f] == C.dimf[U] - 1 and sub(L, f) and nondeg(f): return f
    return None

# ---------------------------------------------------------------- physical chains
recipient = {d: b for b, d in W.pairs}           # donor -> recipient
roots = defaultdict(list)
for j, s in enumerate(W.w['rootroles']): roots[s].append(W.w['root_frame'][j])
start = {b: W.w['source_frame'][x] for x, b in W.source.items()}
start.update({b: z['frame'] for b, z in W.gauge.items()})
seq = defaultdict(list)
for i, (a, b, x) in enumerate(ops):
    seq[a].append(i); seq[b].append(i)

chains = []   # list of element lists: ('f', frame) fixed or ('o', op)
for s in range(W.R):
    if s in W.donor: continue    # recipients are spliced into their donor's chain
    el = []
    st = start.get(s)
    el.append(('f', st) if st is not None else ('z', None))
    el += [('o', i) for i in seq[s]] + [('f', f) for f in roots[s]]
    if s in recipient:
        b = recipient[s]
        el += [('f', W.gauge[b]['frame'])] + [('o', i) for i in seq[b]] + [('f', f) for f in roots[b]]
    el.append(('f', FULL))
    chains.append(el)
pos = defaultdict(list)    # op -> [(chain, index)]
for c, el in enumerate(chains):
    for k, (t, x) in enumerate(el):
        if t == 'o': pos[x].append((c, k))
assert all(len(v) == 2 for v in pos.values()) and len(pos) == nops

def fr(e):
    t, x = e
    if t == 'o': return opframe[x]
    return x

def dim(f): return 0 if f is None else C.dimf[f]

LN = [0.0] + [r * math.log(120 / r) for r in range(1, 121)]
def cost_pair(a, b):
    d = dim(b) - dim(a)
    assert d >= 0
    return LN[d]

def total_cost():
    tot = 0.0
    for el in chains:
        for k in range(len(el) - 1):
            tot += cost_pair(fr(el[k]), fr(el[k + 1]))
    return tot

def check_nested():
    for el in chains:
        for k in range(len(el) - 1):
            a, b = fr(el[k]), fr(el[k + 1])
            assert a is None or sub(a, b), ('nest', el[k], el[k + 1])

check_nested()
c0 = total_cost()
print('loaded', round(time.time() - t0, 1), 's; chains', len(chains), 'cost', round(c0, 1), flush=True)

# ---------------------------------------------------------------- group moves
def groups():
    parent = list(range(nops))
    def find(x):
        while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for el in chains:
        for k in range(len(el) - 1):
            if el[k][0] == 'o' and el[k + 1][0] == 'o' and opframe[el[k][1]] == opframe[el[k + 1][1]]:
                ra, rb = find(el[k][1]), find(el[k + 1][1])
                if ra != rb: parent[ra] = rb
    g = defaultdict(list)
    for i in range(nops): g[find(i)].append(i)
    return list(g.values())

def evaluate(G):
    Gs = set(G); F = opframe[G[0]]
    inc, outg = [], []
    for i in G:
        for c, k in pos[i]:
            el = chains[c]
            p = el[k - 1]
            if not (p[0] == 'o' and p[1] in Gs): inc.append(fr(p))
            q = el[k + 1]
            if not (q[0] == 'o' and q[1] in Gs): outg.append(fr(q))
    spans = {node_span(ops[i][2]) for i in G}
    L = join([f for f in inc if f is not None] + list(spans))
    U = meet(outg)
    if not sub(L, U): return None
    def delta(Fn):
        d = 0.0
        for f in inc: d += LN[dim(Fn) - dim(f)] - LN[dim(F) - dim(f)]
        for f in outg: d += LN[dim(f) - dim(Fn)] - LN[dim(f) - dim(F)]
        return d
    best = (0.0, None)
    cands = set()
    lo = repair_up(L, U)
    if lo is not None: cands.add(lo)
    hi = repair_down(L, U)
    if hi is not None: cands.add(hi)
    for f in inc + outg:
        if f is not None and sub(L, f) and sub(f, U) and nondeg(f): cands.add(f)
    for Fn in cands:
        if C.dimf[Fn] == C.dimf[F] and sub(Fn, F): continue
        d = delta(Fn)
        if d < best[0] - 1e-9: best = (d, Fn)
    return best

it = 0
while True:
    it += 1; moved = 0; gain = 0.0
    gs = groups()
    gs.sort(key=len, reverse=True)
    for G in gs:
        # frames may have changed for neighbours; G still has a common frame since only whole groups move
        if len({opframe[i] for i in G}) != 1: continue
        r = evaluate(G)
        if r is None or r[1] is None: continue
        d, Fn = r
        for i in G: opframe[i] = Fn
        moved += 1; gain += d
    c = total_cost()
    print('iter', it, 'groups', len(gs), 'moved', moved, 'gain', round(gain, 1), 'cost', round(c, 1), round(time.time() - t0, 1), 's', flush=True)
    if moved == 0 or it >= 40: break

check_nested()
for i in range(nops):
    f = opframe[i]
    assert nondeg(f)
    assert sub(node_span(ops[i][2]), f)
changed = sum(1 for i in range(nops) if opframe[i] != W.original_opframe[i])
print('changed op frames', changed, 'final cost', round(total_cost(), 1), 'from', round(c0, 1))

# ---------------------------------------------------------------- write outputs
w = dict(W.w); w['op_frame'] = opframe
w['descent'] = 'op_frame[i]: equal-frame connected groups moved to the join of incoming frames and node spans or the meet of outgoing frames (one-row repair), five-stage first-order cost decrease'
src = pkg / 'selected/bit'
frames = json.loads(gzip.decompress((src / 'frames_p12.json.gz').read_bytes()))
used = set(opframe)
for f in sorted(C.B):
    if str(f) in frames['frames'] or f not in used: continue
    B, A = C.B[f], C.A[f]
    frames['frames'][str(f)] = dict(dim=len(B), b=[list(r) for r in B]) if len(B) <= len(A) else dict(dim=len(B), a=[list(r) for r in A])
used = set(opframe)
print('frames now', len(frames['frames']))
for name in ('graph_p12.json', 'kchron_p12.json', 'profile_p12.json', 'sinks.json'):
    (out / name).write_bytes((src / name).read_bytes())
wj = json.dumps(w, sort_keys=True).encode(); fj = json.dumps(frames, sort_keys=True).encode()
(out / 'word_p12.json').write_bytes(wj); (out / 'word_p12.json.gz').write_bytes(gzip.compress(wj, mtime=0))
(out / 'frames_p12.json').write_bytes(fj); (out / 'frames_p12.json.gz').write_bytes(gzip.compress(fj, mtime=0))
print('wrote', out)
