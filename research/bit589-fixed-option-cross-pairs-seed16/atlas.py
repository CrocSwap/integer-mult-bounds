"""Exact fixed-option cross-section transport-pair census for PR589 (seed 16).

With the PR589 gate multiset, operands, scatter, start/final frames, D and
rebuilt-C sections fixed, enumerate every pair consisting of one independently
legal A transport and one independently legal B transport sharing a register.
Recheck the combined A-to-B register chains, including boundary nesting, and
score with outward rational bounds from the pinned moment engine. No float
decides a comparison. Frame options are generated with the other section at
its base boundary; paired boundary-adaptive options are outside this scope.

Move generation and exact price construction adapt PR #1345 at head
b54a856aa79857d91cd5d65f8f7144e26c8c084f. Substantial OpenAI Codex
assistance; Apache-2.0.
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



# The within-section single/pair search in PR #1345 stops at the stage boundary.
# Here exactly one A move and one B move are combined whenever they share a register.
import itertools

def section_frames(sec, r, moved):
    ops, tl, opts = all_opts[sec]
    ev = []
    for j in tl[r]:
        if j in moved:
            q, F = moved[j]
            ev.append((q - 0.5, j, F))
        else:
            ev.append((j, j, ops[j][0]))
    ev.sort()
    return [e[2] for e in ev]

def mixed_chain(r, moved_a, moved_b):
    A = section_frames('A', r, moved_a)
    B = section_frames('B', r, moved_b)
    segs = [SEG[r]['D'], A, B, SEG[r]['C']]
    return [w['start'][r], *dedup(sum(segs, [])), w['final'][r]]

def cross_score(moved_a, moved_b):
    touched = set()
    for i in moved_a:
        touched.update((A_ops[i][1], A_ops[i][2]))
    for j in moved_b:
        touched.update((B_ops[j][1], B_ops[j][2]))
    lo = hi = Q(0)
    same_profile = True
    for r in touched:
        af = section_frames('A', r, moved_a)
        if r in ret and (af[-1] if af else w['start'][r]) != cp[r]:
            return None, False, 'copy'
        new_chain = mixed_chain(r, moved_a, moved_b)
        c = chain_cost(new_chain)
        if c is None:
            return None, False, 'frame_chain'
        base = chain_cost(full_chain(r))
        lo += c[0] - base[1]
        hi += c[1] - base[0]
        same_profile &= steps(new_chain) == steps(full_chain(r))
    return (lo, hi), same_profile, None

def paid_profile(moved_a, moved_b):
    h = Counter(tops)
    for r in range(N):
        h.update(steps(mixed_chain(r, moved_a, moved_b)))
    return dict(sorted(h.items()))

def apply_and_replay(moved_a, moved_b):
    import copy
    w2 = copy.deepcopy(w)
    n0 = len(w2['frames'])
    for sec, moved in (('A', moved_a), ('B', moved_b)):
        ops = [(f, t, s) for f, t, ss in w2[sec] for s in ss]
        for i, (q, F) in moved.items():
            op = ops.pop(i)
            ops.insert(q, (F, op[1], op[2]))
        w2[sec] = [[f, t, [s]] for f, t, s in ops]
    while len(w2['frames']) <= max((F for moved in (moved_a, moved_b) for _, F in moved.values()), default=n0-1):
        k = len(w2['frames'])
        w2['frames'].append([j for j in range(NL) if masks[k] >> j & 1])
    w2['C'] = wlib.rebuild_C(w2)
    return dict(sorted(wlib.paid(w2).items()))

all_opts = {}
for sec in 'AB':
    ops, tl, opts = options(sec)
    all_opts[sec] = (ops, tl, opts)
A_ops, A_tl, A_options = all_opts['A']
B_ops, B_tl, B_options = all_opts['B']

mov_a = [i for i, x in enumerate(A_options) if len(x) > 1]
mov_b = [j for j, x in enumerate(B_options) if len(x) > 1]
by_a, by_b = {}, {}
for i in mov_a:
    for r in (A_ops[i][1], A_ops[i][2]):
        by_a.setdefault(r, []).append(i)
for j in mov_b:
    for r in (B_ops[j][1], B_ops[j][2]):
        by_b.setdefault(r, []).append(j)
shared_registers = sorted(by_a.keys() & by_b.keys())
pairs = set()
for r in shared_registers:
    for i in by_a[r]:
        for j in by_b[r]:
            pairs.add((i, j))

stats = Counter()
examples = {'same_profile': [], 'worse': [], 'improving': [], 'illegal': []}
best = None
for i, j in sorted(pairs):
    for oa in A_options[i]:
        for ob in B_options[j]:
            if oa == (i, A_ops[i][0]) and ob == (j, B_ops[j][0]):
                continue
            stats['assignments'] += 1
            d, same, why = cross_score({i: oa}, {j: ob})
            if d is None:
                stats['illegal_' + why] += 1
                if len(examples['illegal']) < 5:
                    examples['illegal'].append([i, j, oa[0], oa[1], ob[0], ob[1], why])
                continue
            if same:
                stats['same_profile'] += 1
                if len(examples['same_profile']) < 5:
                    examples['same_profile'].append([i, j, oa[0], oa[1], ob[0], ob[1]])
            elif d[1] < 0:
                stats['improving'] += 1
                candidate = (d, (i, j, oa, ob))
                if best is None or d[0] < best[0][0]:
                    best = candidate
                if len(examples['improving']) < 5:
                    examples['improving'].append([i, j, oa[0], oa[1], ob[0], ob[1], str(d[0]), str(d[1])])
            elif d[0] > 0:
                stats['worse'] += 1
                if len(examples['worse']) < 5:
                    examples['worse'].append([i, j, oa[0], oa[1], ob[0], ob[1], str(d[0]), str(d[1])])
            else:
                stats['unresolved'] += 1

assert stats['assignments'] == sum(len(A_options[i]) * len(B_options[j]) - 1 for i, j in pairs)
assert len(shared_registers) == 336 and len(pairs) == 6151
assert stats['assignments'] == 88181
result = {
    'base_commit': 'bce54fb3f895cbe5cd4c0eb477c3afeed100190f',
    'predecessor_pr1345_head': 'b54a856aa79857d91cd5d65f8f7144e26c8c084f',
    'seed': 16,
    'track': 'bit supplier',
    'object': 'fixed PR589 word; one movable A and one movable B transport sharing a register',
    'c': str(C),
    'shared_registers': len(shared_registers),
    'movable_A': len(mov_a),
    'movable_B': len(mov_b),
    'cross_pairs': len(pairs),
    **dict(stats),
    'examples': examples,
    'best_improving': [str(best[0][0]), str(best[0][1]), list(best[1])] if best else None,
}

# Replay deterministic sample controls through the independent literal-word replayer.
replay = []
for kind in ('same_profile', 'worse', 'improving'):
    if not examples[kind]:
        continue
    row = examples[kind][0]
    i, j, qa, fa, qb, fb = row[:6]
    ma, mb = {i: (qa, fa)}, {j: (qb, fb)}
    observed = apply_and_replay(ma, mb)
    predicted = paid_profile(ma, mb)
    assert observed == predicted, (kind, row, observed, predicted)
    replay.append({'kind': kind, 'A': [i, qa, fa], 'B': [j, qb, fb], 'profile': observed})
result['replay_spot_checks'] = replay
# Home/home is the exact negative control for the delta scorer.
if pairs:
    i, j = sorted(pairs)[0]
    home_delta, home_profile, home_error = cross_score({i: (i, A_ops[i][0])}, {j: (j, B_ops[j][0])})
    # The outward moment intervals enclose zero; exact profile equality is the
    # proof that the home/home control has no paid change.
    assert home_error is None and home_profile and home_delta[0] <= 0 <= home_delta[1]
    result['home_control'] = [i, j, str(home_delta[0]), str(home_delta[1])]
print(json.dumps(result, sort_keys=True))
