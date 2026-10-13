"""Independent exact transport atlas for the PR589 bit word (seed 10, bit supplier).

With gate multiset, operands, scatter, start/final, D and rebuilt-C fixed,
enumerate every transport: relocate one elementary addition r += s to any
position in its exact commutation window at any legal catalogue frame (or the
closure frame of the slot bounds), singly and, for the shared-register coupling,
as every pair of movable transports sharing a register.  Scoring is exact: the
pinned moment engine gives outward rational bounds for d*(64/d)^c at the exact
saving c; the objective is the full per-register frame-chain cost plus scatter
tops, which reproduces the replay paid profile exactly.  No float decides a
comparison.
Prepared with an autonomous opencode research agent (Qwen3.8-Flash); Apache-2.0.
"""
import json, sys, time, importlib.util
from bisect import bisect_left
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path

from pathlib import Path as _P
ROOT = _P(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'research/e8-bit-p111-tuned/tune'))
import wlib

WORD = sys.argv[1] if len(sys.argv) > 1 else \
    str(ROOT / 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz')
C = Q(1733427039589844234749, 10**24)
T0 = time.time()
w = wlib.load(WORD)
V, R = w['v'], w['R']
N, NL = 2 * V + R, len(w['lines'])
ret = set(w['ret'])
lines = w['lines']

masks = [sum(1 << i for i in f) for f in w['frames']]
dim = [len(wlib.basis(lines[i] for i in f)) for f in w['frames']]
idx = {m: i for i, m in enumerate(masks)}
_cl = {}
def closure(mask):
    if mask in _cl:
        return _cl[mask]
    sel = [lines[i] for i in range(NL) if mask >> i & 1]
    rk = len(wlib.basis(sel))
    cl = mask
    for i in range(NL):
        if mask >> i & 1:
            continue
        if len(wlib.basis(sel + [lines[i]])) == rk:
            cl |= 1 << i
    if cl not in idx:
        idx[cl] = len(masks)
        masks.append(cl)
        dim.append(rk)
    _cl[mask] = idx[cl]
    return idx[cl]

ep = ROOT / 'research/complex-k492-owner-repair/vendor/multicold/engines/base_two_moment.py'
assert sha256(ep.read_bytes()).hexdigest() == 'aee70c242a2f1d225528fabe2002e1564d1dc884797c07d28a831c7878ee9098'
spec = importlib.util.spec_from_file_location('atlas_engine', ep)
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)
P = {0: (Q(0), Q(0))}
for d in range(1, 17):
    P[d] = tuple(64 * x for x in engine.moment(64, 1, [(d, 1)], C))

def chain_cost(seq):
    lo = hi = Q(0)
    for a, b in zip(seq, seq[1:]):
        da, db = dim[a], dim[b]
        if db < da or masks[a] & ~masks[b]:
            return None
        if db > da:
            lo += P[db - da][0]
            hi += P[db - da][1]
    return lo, hi

def dedup(seq):
    out = []
    for f in seq:
        if not out or out[-1] != f:
            out.append(f)
    return out

SEG = {r: {'D': [], 'A': [], 'B': [], 'C': []} for r in range(N)}
for sec in 'DABC':
    for f, t, ss in w[sec]:
        for r in [t, *ss]:
            s = SEG[r][sec]
            if not s or s[-1] != f:
                s.append(f)
def full_chain(r, sec=None, ev=None):
    segs = [SEG[r]['D']]
    if sec == 'A':
        segs += [ev, SEG[r]['B'], SEG[r]['C']]
    elif sec == 'B':
        segs += [SEG[r]['A'], ev, SEG[r]['C']]
    else:
        segs += [SEG[r]['A'], SEG[r]['B'], SEG[r]['C']]
    return [w['start'][r], *dedup(sum(segs, [])), w['final'][r]]
base_cost = {}
for r in range(N):
    c = chain_cost(full_chain(r))
    assert c is not None
    base_cost[r] = c
tops = Counter()
for q in ret:
    fa = w['start'][q]
    for sec in 'DA':
        for f, t, ss in w[sec]:
            if q in (t, *ss):
                fa = f
    tops[dim[fa]] += 1
assert dict(tops) == {7: 9}, tops

def steps(seq):
    return Counter(dim[b] - dim[a] for a, b in zip(seq, seq[1:]) if dim[b] > dim[a])
H0 = Counter()
for r in range(N):
    H0.update(steps(full_chain(r)))
H0.update(tops)
assert dict(sorted(H0.items())) == wlib.paid(w)

def ops_of(sec):
    return [(f, t, s) for f, t, ss in w[sec] for s in ss]
A_ops, B_ops = ops_of('A'), ops_of('B')
lastA = list(w['start'])
for f, t, s in A_ops:
    lastA[t] = lastA[s] = f
firstB = list(w['final'])
seen = set()
for f, t, s in B_ops:
    for r in (t, s):
        if r not in seen:
            firstB[r] = f
            seen.add(r)
CTX = {'A': (list(w['start']), firstB), 'B': (lastA, list(w['final']))}
cp = {}
for r in ret:
    lf = w['start'][r]
    for f, t, s in A_ops:
        if r in (t, s):
            lf = f
    cp[r] = lf
commute = lambda a, b: a[1] != b[2] and b[1] != a[2]
_feas = {}
def feasible(low, high):
    if (low, high) in _feas:
        return _feas[(low, high)]
    out = [f for f in range(len(masks)) if masks[f] & ~high == 0 and low & ~masks[f] == 0]
    F0 = closure(low)
    if masks[F0] & ~high == 0 and F0 not in out:
        out.append(F0)
    _feas[(low, high)] = out
    return out

def options(sec):
    ops = A_ops if sec == 'A' else B_ops
    tl = [[] for _ in range(N)]
    for i, (f, t, s) in enumerate(ops):
        tl[t].append(i)
        tl[s].append(i)
    pre, post = CTX[sec]
    n = len(ops)
    res = []
    for i, (f0, t, s) in enumerate(ops):
        lo = i
        while lo > 0 and commute((f0, t, s), ops[lo - 1]):
            lo -= 1
        hi = i
        while hi < n - 1 and commute((f0, t, s), ops[hi + 1]):
            hi += 1
        tt = [j for j in tl[t] if j != i]
        ts = [j for j in tl[s] if j != i]
        starts = sorted({lo} | {e + 1 for e in tt + ts if lo <= e + 1 <= hi} | {i})
        opts = set()
        for k, st in enumerate(starts):
            en = (starts[k + 1] - 1) if k + 1 < len(starts) else hi
            q = min(max(i, st), en)
            ctx = []
            for r, lst in ((t, tt), (s, ts)):
                kk = bisect_left(lst, q)
                p = ops[lst[kk - 1]][0] if kk > 0 else pre[r]
                nx = ops[lst[kk]][0] if kk < len(lst) else post[r]
                ctx.append((p, nx, kk, lst))
            (pt, nt, kt, _), (ps, ns, ks, _) = ctx
            low = masks[pt] | masks[ps]
            high = masks[nt] & masks[ns]
            if low & ~high:
                continue
            for F in feasible(low, high):
                ok = True
                if sec == 'A':
                    for r, lst, kk in ((t, tt, kt), (s, ts, ks)):
                        if r in ret:
                            last = F if kk == len(lst) else (ops[lst[-1]][0] if lst else w['start'][r])
                            if last != cp[r]:
                                ok = False
                if ok:
                    opts.add((q, F))
        res.append(sorted(opts))
    return ops, tl, res

def score(sec, ops, tl, moves):
    regs = set()
    for i, q, F in moves:
        regs.add(ops[i][1])
        regs.add(ops[i][2])
    mv = {i: (q, F) for i, q, F in moves}
    lo = hi = Q(0)
    for r in regs:
        ev = []
        for j in tl[r]:
            if j in mv:
                ev.append((mv[j][0] - 0.5, j, mv[j][1]))
            else:
                ev.append((j, j, ops[j][0]))
        ev.sort()
        frames = [e[2] for e in ev]
        if sec == 'A':
            for r2 in ret:
                if r2 == r and frames:
                    if frames[-1] != cp[r]:
                        return None
        c = chain_cost(full_chain(r, sec, frames))
        if c is None:
            return None
        lo += c[0] - base_cost[r][1]
        hi += c[1] - base_cost[r][0]
    return lo, hi

def atlas(sec):
    ops, tl, opts = options(sec)
    stat = Counter()
    best_pos, ties, improving = None, 0, []
    examples = {'same_profile': [], 'strictly_worse': []}
    for i, (f0, t, s) in enumerate(ops):
        home = score(sec, ops, tl, [(i, i, f0)])
        assert abs(home[0]) < Q(1, 10**20) and abs(home[1]) < Q(1, 10**20), (sec, i, home)
        for q, F in opts[i]:
            if q == i and F == f0:
                continue
            stat['legal'] += 1
            d = score(sec, ops, tl, [(i, q, F)])
            if d is None:
                stat['illegal_chain'] += 1
                continue
            if d[1] < 0:
                improving.append((sec, i, q, F, float(d[0]), float(d[1])))
                stat['improving'] += 1
            elif d[0] > 0:
                stat['strictly_worse'] += 1
                if len(examples['strictly_worse']) < 2:
                    examples['strictly_worse'].append((i, q, F))
                if best_pos is None or d[0] < best_pos[0]:
                    best_pos = (d[0], sec, i, q, F)
            else:
                H = Counter()
                mv = {i: (q, F)}
                for r in (t, s):
                    ev = [(mv[j][0] - 0.5, j, mv[j][1]) if j in mv else (j, j, ops[j][0]) for j in tl[r]]
                    ev.sort()
                    H.update(steps(full_chain(r, sec, [e[2] for e in ev])))
                H0r = Counter()
                for r in (t, s):
                    H0r.update(steps(full_chain(r)))
                if H == H0r:
                    ties += 1
                    stat['same_profile'] += 1
                    if len(examples['same_profile']) < 2:
                        examples['same_profile'].append((i, q, F))
                else:
                    stat['unresolved'] += 1
    return ops, tl, opts, stat, improving, best_pos, ties, examples

out = {'word': WORD.rsplit('/', 1)[-1], 'c': str(C)}
all_opts = {}
for sec in 'AB':
    ops, tl, opts, stat, improving, best_pos, ties, examples = atlas(sec)
    all_opts[sec] = (ops, tl, opts)
    all_opts[sec + '_ex'] = examples
    out[sec] = dict(ops=len(ops), **dict(stat),
                    smallest_strict_loss=str(best_pos[0]) if best_pos else None,
                    improving=improving[:5])
# ------------------------------------------------- replay spot-check
# Apply sample single moves to the word, rebuild C, replay exactly, and
# compare the replayed paid profile with the chain-model prediction.
n0 = len(w['frames'])
def apply_and_replay(sec, i, q, F):
    import copy
    w2 = copy.deepcopy(w)
    ops = [(f, t, s) for f, t, ss in w2[sec] for s in ss]
    op = ops.pop(i)
    op = (F, op[1], op[2])
    ops.insert(q, op)
    w2[sec] = [[f, t, [s]] for f, t, s in ops]
    if F >= n0:
        w2['frames'].append([k for k in range(NL) if masks[F] >> k & 1])
    w2['C'] = wlib.rebuild_C(w2)
    return wlib.paid(w2)

def predicted(sec, i, q, F):
    ops, tl, opts = all_opts[sec]
    t, s = ops[i][1], ops[i][2]
    mv = {i: (q, F)}
    H = Counter(tops)
    for r in range(N):
        if r in (t, s):
            ev = [(mv[x][0] - 0.5, x, mv[x][1]) if x in mv else (x, x, ops[x][0]) for x in tl[r]]
            ev.sort()
            H.update(steps(full_chain(r, sec, [e[2] for e in ev])))
        else:
            H.update(steps(full_chain(r)))
    return dict(sorted(H.items()))

spot = []
for sec in 'AB':
    for kind in ('same_profile', 'strictly_worse'):
        for (i, q, F) in all_opts[sec + '_ex'][kind]:
            got = dict(sorted(apply_and_replay(sec, i, q, F).items()))
            pred = predicted(sec, i, q, F)
            assert got == pred, (sec, i, q, F, got, pred)
            spot.append(dict(section=sec, kind=kind, op=i, slot=q, frame=F, profile=got))
out['replay_spot_check'] = spot


# ------------------------------------------- simultaneous transports
import itertools
comp_out = []
for sec in 'AB':
    ops, tl, opts = all_opts[sec]
    home = [(i, ops[i][0]) for i in range(len(ops))]
    movable = [i for i in range(len(ops)) if len(opts[i]) > 1]
    reg2op = {}
    par = {i: i for i in movable}
    def find(x):
        while par[x] != x:
            x = par[x]
        return x
    for i in movable:
        for r in (ops[i][1], ops[i][2]):
            if r in reg2op:
                a, b = find(reg2op[r]), find(i)
                if a != b:
                    par[a] = b
            else:
                reg2op[r] = i
    comps = {}
    for i in movable:
        comps.setdefault(find(i), []).append(i)
    stat = Counter()
    best = None
    for xs in comps.values():
        stat['components'] += 1
        stat['size_' + str(len(xs))] += 1
        ncombo = 1
        for i in xs:
            ncombo *= len(opts[i])
        stat['combos'] += ncombo
        if ncombo > 200000:
            stat['over_budget'] += 1
            stat['over_combos'] += ncombo
            continue
        for combo in itertools.product(*(opts[i] for i in xs)):
            moves = [(i, q, F) for i, (q, F) in zip(xs, combo)]
            if all((q, F) == (i, ops[i][0]) for i, (q, F) in zip(xs, combo)):
                continue
            stat['scored'] += 1
            d = score(sec, ops, tl, moves)
            if d is None:
                stat['illegal'] += 1
                continue
            if d[1] < 0:
                stat['improving'] += 1
                if best is None or d[0] < best[0]:
                    best = (d, moves)
            elif d[0] > 0:
                stat['worse'] += 1
            else:
                stat['undecided_or_tie'] += 1
    comp_out.append(dict(section=sec, movable=len(movable), **dict(stat),
                         best_improving=[str(best[0][0]), str(best[0][1]),
                                         [[i, q, F] for i, q, F in best[1]]] if best else None))
out['simultaneous'] = comp_out

# Full components are astronomically large; certify the first-order coupling:
# every pair of movable transports sharing a register, all frame/slot choices.
# Disjoint-register simultaneous moves decompose additively, so with no
# improving single transport they cannot improve either.
pair_out = []
for sec in 'AB':
    ops, tl, opts = all_opts[sec]
    movable = [i for i in range(len(ops)) if len(opts[i]) > 1]
    by_reg = {}
    for i in movable:
        for r in (ops[i][1], ops[i][2]):
            by_reg.setdefault(r, []).append(i)
    pairs = set()
    for r, xs in by_reg.items():
        for a in range(len(xs)):
            for b in range(a + 1, len(xs)):
                pairs.add((xs[a], xs[b]))
    stat = Counter()
    best = None
    for i, j in sorted(pairs):
        for qi, Fi in opts[i]:
            for qj, Fj in opts[j]:
                if (qi, Fi) == (i, ops[i][0]) and (qj, Fj) == (j, ops[j][0]):
                    continue
                stat['scored'] += 1
                d = score(sec, ops, tl, [(i, qi, Fi), (j, qj, Fj)])
                if d is None:
                    stat['illegal'] += 1
                elif d[1] < 0:
                    stat['improving'] += 1
                    if best is None or d[0] < best[0]:
                        best = (d, [(i, qi, Fi), (j, qj, Fj)])
                elif d[0] > 0:
                    stat['worse'] += 1
                else:
                    regs = {ops[i][1], ops[i][2], ops[j][1], ops[j][2]}
                    mv = {i: (qi, Fi), j: (qj, Fj)}
                    H = Counter()
                    H0r = Counter()
                    for r in regs:
                        ev = [(mv[x][0] - 0.5, x, mv[x][1]) if x in mv else (x, x, ops[x][0]) for x in tl[r]]
                        ev.sort()
                        H.update(steps(full_chain(r, sec, [e[2] for e in ev])))
                        H0r.update(steps(full_chain(r)))
                    if H == H0r:
                        stat['same_profile'] += 1
                    else:
                        stat['unresolved'] += 1
    pair_out.append(dict(section=sec, movable=len(movable), pairs=len(pairs), **dict(stat),
                         best_improving=[str(best[0][0]), str(best[0][1]), best[1]] if best else None))
out['simultaneous_pairs'] = pair_out
print(json.dumps(out))
