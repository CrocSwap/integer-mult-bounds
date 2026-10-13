"""Exact frame-only optimum of a bitE8/1+mut bit word with its gate sequence fixed.

Every gate g puts all its operands on one frame f_g; each register's frames must nest from its start to its final
frame. Targets stay at frame 0 until the scatter. Retained totals keep their scatter frames, so the COPY ranks and the
decoder constant do not change. Frames are closed sets of live lines. The paid profile counts each climb by its rank step.

1. Forward least frames lo_g and backward greatest frames hi_g bound every legal f_g. Every closed frame between
   them is enumerated.
2. Free gates (lo_g != hi_g) couple only through consecutive free gates on a register. A fixed gate in between pins
   the frame there, so the components are independent in both legality and cost.
3. At z = c the moment sum_d n_d (d/(mW)) (m/d)^z is linear in the profile. A frame change can raise c only if it
   lowers sum_d n_d d (m/d)^c. Each component is enumerated exhaustively and its best combination kept.

Usage: frameopt.py WORD.json.gz C [--degrade]
--degrade is the positive control: every free gate starts at its least frame.
"""
import gzip, itertools, json, sys
from collections import Counter
from fractions import Fraction
from functools import reduce
from operator import or_, and_

w = json.load(gzip.open(sys.argv[1], 'rt'))
c = float(Fraction(sys.argv[2]))
V, N, L = w['v'], 2 * w['v'] + w['R'], w['lines']
P = 2147483647


def rank(rows):
    rows, rk = [[x % P for x in r] for r in rows], 0
    for col in range(len(L[0])):
        p = next((i for i in range(rk, len(rows)) if rows[i][col]), None)
        if p is None:
            continue
        rows[rk], rows[p] = rows[p], rows[rk]
        inv = pow(rows[rk][col], P - 2, P)
        rows[rk] = [x * inv % P for x in rows[rk]]
        for i in range(len(rows)):
            if i != rk and rows[i][col]:
                f = rows[i][col]
                rows[i] = [(a - f * b) % P for a, b in zip(rows[i], rows[rk])]
        rk += 1
    return rk


bits = lambda m: [i for i in range(V) if m >> i & 1]
_close = {}


def close(m):
    """(closed line set spanned by mask m, its rank)"""
    if m not in _close:
        sel = [L[i] for i in bits(m)]
        rk = rank(sel) if sel else 0
        _close[m] = (sum(1 << i for i in range(V) if m >> i & 1 or (sel and rank(sel + [L[i]]) == rk)), rk)
    return _close[m]


dim = lambda m: close(m)[1]
FM = [sum(1 << i for i in f) for f in w['frames']]
assert all(close(m)[0] == m for m in FM), 'catalogue frame not closed'
SCATTER = ('S', 0, [], None)
gates = [(s, k, [g[1], *g[2]], FM[g[0]]) for s in 'DA' for k, g in enumerate(w[s])] + [SCATTER] + \
        [(s, k, [g[1], *g[2]], FM[g[0]]) for s in 'BC' for k, g in enumerate(w[s])]
start, final = [FM[f] for f in w['start']], [FM[f] for f in w['final']]
word = {(s, k): f for s, k, _, f in gates if s != 'S'}

cur = start.copy()
for s, k, regs, f in gates[:gates.index(SCATTER)]:
    for r in regs:
        cur[r] = f
pin = {q: cur[q] for q in w['ret']}

# 1. bounds
lo, cur = {}, start.copy()
for s, k, regs, f in gates:
    if s == 'S':
        assert all(cur[q] & ~pin[q] == 0 for q in pin)
        for q in pin:
            cur[q] = pin[q]
        continue
    lo[s, k] = m = close(reduce(or_, (cur[r] for r in regs)))[0]
    for r in regs:
        cur[r] = m
hi, ub = {}, final.copy()
for s, k, regs, f in reversed(gates):
    if s == 'S':
        for t in range(V, 2 * V):
            ub[t] = 0
        for q in pin:
            assert pin[q] & ~ub[q] == 0
            ub[q] = pin[q]
        continue
    hi[s, k] = m = reduce(and_, (ub[r] for r in regs))  # an intersection of closed sets is closed
    for r in regs:
        ub[r] = m
assert all(lo[x] & ~word[x] == 0 and word[x] & ~hi[x] == 0 for x in word), 'word frame outside its bounds'

opts = {}
for x in word:
    if lo[x] != hi[x]:
        seen, todo = {lo[x]}, [lo[x]]
        while todo:
            m = todo.pop()
            for i in bits(hi[x] & ~m):
                n = close(m | 1 << i)[0]
                if n & ~hi[x] == 0 and n not in seen:
                    seen.add(n)
                    todo.append(n)
        opts[x] = sorted(seen, key=dim)

# 2. components of free gates
parent = {x: x for x in opts}


def find(x):
    while parent[x] != x:
        x = parent[x]
    return x


last = {}
for s, k, regs, f in gates:
    for r in regs:
        if (s, k) in opts and last.get(r) in opts:
            parent[find(last[r])] = find((s, k))
        last[r] = (s, k)
members = {}
for x in opts:
    members.setdefault(find(x), []).append(x)


# 3. exact enumeration
def profile(fr):
    """paid profile (climbs plus COPY ranks) of a frame assignment, or None if some chain does not nest"""
    cur, H = start.copy(), Counter()
    for s, k, regs, _ in gates + [('F', 0, range(N), None)]:
        if s == 'S':
            H.update(dim(cur[q]) for q in pin)
            continue
        for r in regs:
            m = final[r] if s == 'F' else fr[s, k]
            if cur[r] != m:
                if cur[r] & ~m:
                    return None
                H[dim(m) - dim(cur[r])] += 1
                cur[r] = m
    return H


cost = lambda H: sum(n * d * (64 / d) ** c for d, n in H.items())
base = dict(word)
if '--degrade' in sys.argv:
    base.update({x: lo[x] for x in opts})
H0 = profile(base)
best, tried, illegal, ties, margins = dict(base), 0, 0, 0, []
for xs in members.values():
    deltas = []
    for combo in itertools.product(*(opts[x] for x in xs)):
        fr = dict(base)
        fr.update(zip(xs, combo))
        H = profile(fr)
        tried += 1
        if H is None:
            illegal += 1
        elif H == H0:
            ties += combo != tuple(base[x] for x in xs)
        else:
            deltas.append((cost(H) - cost(H0), combo))
    if deltas:
        d, combo = min(deltas)
        margins.append(d)
        if d < 0:
            best.update(zip(xs, combo))
H1 = profile(best)
result = dict(
    word=sys.argv[1].rsplit('/', 1)[-1], degraded_start='--degrade' in sys.argv, gates=len(word),
    free_gates=len(opts), components=len(members), component_sizes=dict(Counter(map(len, members.values()))),
    assignments_enumerated=tried, non_nesting_rejected=illegal, same_profile_alternatives=ties,
    start_profile=dict(sorted(H0.items())), optimum_profile=dict(sorted(H1.items())),
    improving_components=sum(d < 0 for d in margins),
    smallest_alternative_delta=min(margins) if margins else None, weighted_cost_delta=cost(H1) - cost(H0))
print(json.dumps(result))
