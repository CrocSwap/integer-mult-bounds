"""Exact reciprocal-boundary census for one PR589 A/B move pair (seed 5).

Enumerate canonical commutation slots and catalogue/closure frames for
A[2071] and B[820] at shared register 659. Recompute both stage boundaries,
preserve COPY frames, check complete touched-register chains, and price with
outward rational bounds from the pinned moment engine. Every legal candidate
is replayed through the literal word builder. No float decides a comparison.

Move and price methods adapt PR #1345 at b54a856aa79857d91cd5d65f8f7144e26c8c084f;
this narrow extension addresses the joint-boundary question left open by PR #1382.
Substantial OpenAI Codex assistance; Apache-2.0.
"""
import json, sys, importlib.util
from bisect import bisect_left
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'research/e8-bit-p111-tuned/tune'))
import wlib

WORD = sys.argv[1] if len(sys.argv) > 1 else \
    str(ROOT / 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz')
C = Q(1733427039589844234749, 10**24)
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

# Seed-5 scope: jointly move only A[2071] and B[820] on their shared
# boundary register r=659. Slot regions are exact commutation-equivalence
# classes; opposite-stage bounds are relaxed for candidate generation and
# restored jointly below.
AI, BI = 2071, 820
assert A_ops[AI] == (501, 290, 659), A_ops[AI]
assert B_ops[BI] == (598, 184, 659), B_ops[BI]
FULL = (1 << NL) - 1

def slot_regions(sec, i):
    ops = A_ops if sec == 'A' else B_ops
    tl = [[] for _ in range(N)]
    for k, (_, t, s) in enumerate(ops):
        tl[t].append(k)
        tl[s].append(k)
    f0, t, s = ops[i]
    lo = i
    while lo > 0 and commute((f0, t, s), ops[lo - 1]):
        lo -= 1
    hi = i
    while hi < len(ops) - 1 and commute((f0, t, s), ops[hi + 1]):
        hi += 1
    touches = [k for r in (t, s) for k in tl[r] if k != i]
    starts = sorted({lo, i} | {k + 1 for k in touches if lo <= k + 1 <= hi})
    out = []
    for p, st in enumerate(starts):
        en = starts[p + 1] - 1 if p + 1 < len(starts) else hi
        out.append((min(max(i, st), en), st, en))
    return ops, tl, out

A_ops2, A_tl2, A_slots = slot_regions('A', AI)
B_ops2, B_tl2, B_slots = slot_regions('B', BI)
assert [q for q, _, _ in A_slots] == [2070, 2071], A_slots
assert [q for q, _, _ in B_slots] == [65, 819, 820, 822, 823], B_slots

def local_bounds(sec, i, q, tl):
    ops = A_ops if sec == 'A' else B_ops
    pre, post = CTX[sec]
    _, t, s = ops[i]
    ctx = []
    for r in (t, s):
        lst = [k for k in tl[r] if k != i]
        kk = bisect_left(lst, q)
        before = ops[lst[kk - 1]][0] if kk else pre[r]
        after = ops[lst[kk]][0] if kk < len(lst) else post[r]
        ctx.append((r, before, after, kk, lst))
    low = masks[ctx[0][1]] | masks[ctx[1][1]]
    high = masks[ctx[0][2]] & masks[ctx[1][2]]
    if sec == 'A':
        # Only remove the B-stage cap where this moved event is last in A.
        for z, (r, _, _, kk, lst) in enumerate(ctx):
            if kk == len(lst):
                ctx[z] = (r, ctx[z][1], None, kk, lst)
                high &= FULL
    else:
        # Only remove the A-stage floor where this moved event is first in B.
        for z, (r, _, _, kk, lst) in enumerate(ctx):
            if kk == 0:
                ctx[z] = (r, None, ctx[z][2], kk, lst)
                low &= FULL
    return low, high, ctx

def section_frames(sec, r, i, q, frame):
    ops = A_ops if sec == 'A' else B_ops
    tl = A_tl2 if sec == 'A' else B_tl2
    ev = []
    for k in tl[r]:
        if k == i:
            ev.append((q - 0.5, k, frame))
        else:
            ev.append((k, k, ops[k][0]))
    ev.sort()
    return [x[2] for x in ev]

def stage_edge(sec, r, moved_i, q, frame, first):
    ops = A_ops if sec == 'A' else B_ops
    tl = A_tl2 if sec == 'A' else B_tl2
    ev = []
    for k in tl[r]:
        ev.append((q - 0.5, k, frame) if k == moved_i else (k, k, ops[k][0]))
    if not ev:
        return w['start'][r] if sec == 'A' else w['final'][r]
    ev.sort()
    return ev[0][2] if first else ev[-1][2]

def local_low_high(sec, i, q):
    ops, tl, _ = (A_ops2, A_tl2, A_slots) if sec == 'A' else (B_ops2, B_tl2, B_slots)
    _, _, ctx = local_bounds(sec, i, q, tl)
    low = 0
    high = FULL
    for r, before, after, kk, lst in ctx:
        if sec == 'A':
            low |= masks[before]
            if after is not None:
                high &= masks[after]
        else:
            if before is not None:
                low |= masks[before]
            if after is not None:
                high &= masks[after]
    return low, high, ctx

def candidate_frames(sec, i, q):
    low, high, _ = local_low_high(sec, i, q)
    return feasible(low, high)

def chain_for(r, fa, qa, fb, qb):
    af = section_frames('A', r, AI, qa, fa)
    bf = section_frames('B', r, BI, qb, fb)
    segs = [SEG[r]['D'], af, bf, SEG[r]['C']]
    return [w['start'][r], *dedup(sum(segs, [])), w['final'][r]]

def pair_score(qa, fa, qb, fb):
    moved_a = {AI: (qa, fa)}
    moved_b = {BI: (qb, fb)}
    touched = {A_ops[AI][1], A_ops[AI][2], B_ops[BI][1], B_ops[BI][2]}
    # COPY outputs retain the selected A access frame.
    for r in (A_ops[AI][1], A_ops[AI][2]):
        af = section_frames('A', r, AI, qa, fa)
        if r in ret and (af[-1] if af else w['start'][r]) != cp[r]:
            return None, None, 'copy'
    # Check both dynamically updated stage boundaries, including the
    # reciprocal B-first/A-last dependency for each operand.
    for r in (A_ops[AI][1], A_ops[AI][2]):
        _, _, ctx = local_low_high('A', AI, qa)
        slot = next(x for x in ctx if x[0] == r)
        if slot[2] is None:
            bfirst = stage_edge('B', r, BI, qb, fb, True)
            if masks[fa] & ~masks[bfirst]:
                return None, None, 'A_upper_boundary'
    for r in (B_ops[BI][1], B_ops[BI][2]):
        _, _, ctx = local_low_high('B', BI, qb)
        slot = next(x for x in ctx if x[0] == r)
        if slot[1] is None:
            alast = stage_edge('A', r, AI, qa, fa, False)
            if masks[alast] & ~masks[fb]:
                return None, None, 'B_lower_boundary'
    low = high = Q(0)
    same = True
    for r in touched:
        now = chain_for(r, fa, qa, fb, qb)
        c = chain_cost(now)
        if c is None:
            return None, None, 'frame_chain'
        old = chain_cost(full_chain(r))
        low += c[0] - old[1]
        high += c[1] - old[0]
        same &= steps(now) == steps(full_chain(r))
    return (low, high), same, None

def literal_replay(qa, fa, qb, fb):
    import copy
    w2 = copy.deepcopy(w)
    for sec, index, q, frame in (('A', AI, qa, fa), ('B', BI, qb, fb)):
        ops = [(f, t, s) for f, t, ss in w2[sec] for s in ss]
        op = ops.pop(index)
        # q is a gap before original operation q. Removal shifts that gap
        # left by one precisely when the destination is later than the source.
        ops.insert(q if q <= index else q - 1, (frame, op[1], op[2]))
        w2[sec] = [[f, t, [s]] for f, t, s in ops]
    while len(w2['frames']) < len(masks):
        w2['frames'].append([j for j in range(NL) if masks[len(w2['frames'])] >> j & 1])
    w2['C'] = wlib.rebuild_C(w2)
    return dict(sorted(wlib.paid(w2).items()))

stats = Counter()
examples = {'tie': [], 'worse': [], 'better': [], 'unresolved': [], 'illegal': []}
valid_rows = []
all_assignments = 0
for qa, _, _ in A_slots:
    a_low, a_high, actx = local_low_high('A', AI, qa)
    a_frames = feasible(a_low, a_high)
    for qb, _, _ in B_slots:
        b_low0, b_high, bctx = local_low_high('B', BI, qb)
        # For each candidate A frame, rebuild B's lower bound from the
        # actual last-A frames; the closure is recomputed at that exact bound.
        for fa in a_frames:
            dyn_low = b_low0
            for r, before, _, _, _ in bctx:
                if before is None:
                    dyn_low |= masks[stage_edge('A', r, AI, qa, fa, False)]
            for fb in feasible(dyn_low, b_high):
                all_assignments += 1
                delta, same, why = pair_score(qa, fa, qb, fb)
                if why:
                    stats['illegal_' + why] += 1
                    if len(examples['illegal']) < 8:
                        examples['illegal'].append([qa, fa, qb, fb, why])
                    continue
                valid_rows.append((qa, fa, qb, fb, delta, same))
                if same:
                    label = 'tie'
                elif delta[1] < 0:
                    label = 'better'
                elif delta[0] > 0:
                    label = 'worse'
                else:
                    label = 'unresolved'
                stats[label] += 1
                if len(examples[label]) < 8:
                    examples[label].append([qa, fa, qb, fb, str(delta[0]), str(delta[1])])

# The base/base assignment must be legal, profile-identical, and replay exactly.
base_row = next((x for x in valid_rows if x[:4] == (AI, A_ops[AI][0], BI, B_ops[BI][0])), None)
assert base_row is not None and base_row[5] and base_row[4][0] <= 0 <= base_row[4][1]
base_literal = literal_replay(AI, A_ops[AI][0], BI, B_ops[BI][0])
assert base_literal == dict(sorted(wlib.paid(w).items()))

# Replay every legal joint assignment, including destinations after the
# original operation index. The latter checks the pop/insert gap adjustment.
replay = []
for qa, fa, qb, fb, _, _ in valid_rows:
    predicted = Counter(tops)
    for r in range(N):
        predicted.update(steps(chain_for(r, fa, qa, fb, qb)))
    observed = literal_replay(qa, fa, qb, fb)
    assert observed == dict(sorted(predicted.items())), (qa, fa, qb, fb, observed, predicted)
    if len(replay) < 3:
        replay.append({'A': [qa, fa], 'B': [qb, fb], 'profile': observed})

# Boundary negative control: at least one candidate drawn from the relaxed
# superset must fail when the actual opposing frame is restored.
relaxed_invalid = None
for qa, _, _ in A_slots:
    af = candidate_frames('A', AI, qa)
    for qb, _, _ in B_slots:
        bl, bh, _ = local_low_high('B', BI, qb)
        for fa in af:
            for fb in feasible(bl, bh):
                _, _, why = pair_score(qa, fa, qb, fb)
                if why in ('A_upper_boundary', 'B_lower_boundary'):
                    relaxed_invalid = [qa, fa, qb, fb, why]
                    break
            if relaxed_invalid:
                break
        if relaxed_invalid:
            break
    if relaxed_invalid:
        break
assert relaxed_invalid is not None

# Fixed-option negative control: enforce the original external A/B bounds and
# confirm the resulting domain is a subset of the joint dynamic domain.
static_rows = []
for qa, _, _ in A_slots:
    al, ah, actx = local_low_high('A', AI, qa)
    for r, before, after, _, _ in actx:
        if after is None:
            ah &= masks[firstB[r]]
    afs = feasible(al, ah)
    for qb, _, _ in B_slots:
        bl, bh, bctx = local_low_high('B', BI, qb)
        for r, before, _, _, _ in bctx:
            if before is None:
                bl |= masks[lastA[r]]
        bfs = feasible(bl, bh)
        for fa in afs:
            for fb in bfs:
                _, _, why = pair_score(qa, fa, qb, fb)
                if why is None:
                    static_rows.append((qa, fa, qb, fb))
valid_set = {x[:4] for x in valid_rows}
static_set = set(static_rows)
assert static_set <= valid_set, (static_set - valid_set)

result = {
    'base_commit': 'bce54fb3f895cbe5cd4c0eb477c3afeed100190f',
    'predecessor_pr1345_head': 'b54a856aa79857d91cd5d65f8f7144e26c8c084f',
    'predecessor_fixed_pair_pr1382_head': 'cf17b06c00c50a22315f210c5f6b5197c860abdd',
    'seed': 5,
    'track': 'bit supplier',
    'object': 'PR589 fixed word; jointly boundary-adaptive A[2071] and B[820] at r=659',
    'c': str(C),
    'registers_touched': sorted({A_ops[AI][1], A_ops[AI][2], B_ops[BI][1], B_ops[BI][2]}),
    'A_slots': [q for q, _, _ in A_slots],
    'B_slots': [q for q, _, _ in B_slots],
    'candidate_assignments': all_assignments,
    'valid_assignments': len(valid_rows),
    'static_fixed_boundary_assignments': len(static_rows),
    'joint_only_assignments': len(valid_set - static_set),
    **dict(stats),
    'examples': examples,
    'home_control_profile': base_literal,
    'literal_replay': replay,
    'literal_replay_count': len(valid_rows),
    'relaxed_boundary_negative_control': relaxed_invalid,
    'relaxed_boundary_negative_control_frames': [
        {'index': relaxed_invalid[1], 'mask_hex': hex(masks[relaxed_invalid[1]]), 'rank': dim[relaxed_invalid[1]]},
        {'index': relaxed_invalid[3], 'mask_hex': hex(masks[relaxed_invalid[3]]), 'rank': dim[relaxed_invalid[3]]},
    ],
}
if __name__ == '__main__':
    print(json.dumps(result, sort_keys=True))
