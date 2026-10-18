"""C2: the shipped complex word is a dirty-borrow program, not a clean SLP.  Exact rational replay of the ck provider word of #626
(A + cut + B events; value = a register's exact row up to scale, frames by subspace inclusion), and the same dirt count on the #656 gauge44 word."""
import sys
from fractions import Fraction as Q
from collections import Counter, defaultdict
from common import *

def ap(e, rows):
    if e[0] == 'scale':
        _, t, a, b = e[:4]; q = Q(a, b); rows[t] = {j: q * x for j, x in rows[t].items()}
    else:
        _, t, s, a, b = e[:5]; q = Q(a, b)
        for j, x in list(rows[s].items()):
            z = rows[t].get(j, Q(0)) + q * x
            if z: rows[t][j] = z
            else: rows[t].pop(j, None)
def norm(r):
    if not r: return None
    k = min(r); c = r[k]; return tuple(sorted((j, x / c) for j, x in r.items()))

def cover_census(d):
    V = d['v']; n = len(d['start']); fr = d['frames']
    ss = []
    for f in fr:
        s = {0}
        for b in f: s |= {x ^ b for x in s}
        ss.append(frozenset(s))
    FULL = frozenset(range(1024))
    S = lambda f: FULL if f is None else ss[f]
    rows = [{r: Q(1)} for r in range(n)]
    cur = [norm(rows[r]) for r in range(n)]
    holders = defaultdict(set); readers = defaultdict(list)
    for r in range(n): holders[cur[r]].add(r)
    seq = d['A'] + d['cut'] + d['B']
    for T, e in enumerate(seq):
        if e[0] == 'add': readers[cur[e[2]]].append((T, e[-1]))
        ap(e, rows); t = e[1]; cur[t] = norm(rows[t]); holders[cur[t]].add(t)
    nvals = totH = totC = over = 0
    for val, hs in holders.items():
        rd = readers.get(val, [])
        if not rd or val is None: continue
        nvals += 1
        # min chain cover of the readers (order: time, then frame inclusion) = #readers - max bipartite matching (Dilworth/Fulkerson)
        adj = [[b for b in range(len(rd)) if b != a and (rd[a][0], a) < (rd[b][0], b) and S(rd[a][1]) <= S(rd[b][1])] for a in range(len(rd))]
        match = {}
        def aug(a, seen):
            for b in adj[a]:
                if b in seen: continue
                seen.add(b)
                if b not in match or aug(match[b], seen): match[b] = a; return True
            return False
        m = sum(1 for a in range(len(rd)) if aug(a, set()))
        totH += len(hs); totC += len(rd) - m
        if len(hs) > len(rd) - m: over += 1
    return nvals, totH, totC, over

def peak_redundant(d):
    V = d['v']; n = len(d['start'])
    rows = [{r: Q(1)} for r in range(n)]
    seq = d['A'] + d['cut'] + d['B']
    lastread = [-1] * n
    for T, e in enumerate(seq):
        if e[0] == 'add': lastread[e[2]] = T
    cur = [norm(rows[r]) for r in range(n)]; peak = 0
    for T, e in enumerate(seq):
        ap(e, rows); cur[e[1]] = norm(rows[e[1]])
        if T % 20 == 0:
            live = set(r for r in range(2 * V, n) if lastread[r] > T and cur[r] is not None)
            vals = {}
            for r in range(n):
                if r in live or r < V: vals.setdefault(cur[r], []).append(r)
            red = 0
            for v, rs in vals.items():
                hs = [r for r in rs if r >= 2 * V]
                if hs: red += len(hs) - (0 if [r for r in rs if r < V] else 1)
            peak = max(peak, red)
    return peak

def dirt(d):
    V = d['v']; n = len(d['start'])
    rows = [{r: Q(1)} for r in range(n)]
    for e in d['A'] + d['cut']: ap(e, rows)
    pre = [dict(r) for r in rows]
    readers = {e[2] for e in d['B'] if e[0] == 'add' and e[2] >= 2 * V}
    zero = {s for s in readers if not any(j < V for j in pre[s])}   # clean row = columns of the 112 source registers
    for e in d['B']: ap(e, rows)
    cl = lambda r: {j: x for j, x in r.items() if j < V}
    tclean = all(cl(rows[V + p]) == {p: Q(1)} for p in range(V))
    lens = [len(rows[t]) for t in range(V, 2 * V)]
    return readers, zero, tclean, min(lens), max(lens)

ck = load_json('derived', 'ck-CANONICAL-WORD.json.gz'); V = ck['v']
check('C2 ck word: v = 112, R = 492 helpers, 716 registers', V == 112 and ck['R'] == 492 and len(ck['start']) == 716)
nv, th, tc, ov = cover_census(ck)
check('C2 ck: 2056 distinct read values; every value\'s readers form ONE chain (min chain cover 2056)', nv == 2056 and tc == 2056, (nv, tc))
check('C2 ck: 2483 (value, holder) pairs, 259 values held by >1 register at some time (sequential reuse)', th == 2483 and ov == 259, (th, ov))
pk = peak_redundant(ck)
check('C2 ck: peak simultaneous redundant live helpers = 0 (sampled every 20 ops)', pk == 0, pk)
rd, zero, tclean, lo, hi = dirt(ck)
check('C2 ck: 422 helpers are read in B; 268 of them have an all-zero clean (source-column) row: pure dirt scratch', len(rd) == 422 and len(zero) == 268, (len(rd), len(zero)))
check('C2 ck: clean (zero-ancilla) map is t_p = s_p for all 112 targets; the real target rows have 36-97 terms over the 716 coordinates', tclean and lo == 36 and hi == 97, (lo, hi))

# the same dirt count on the #656 gauge44 word, and the join with C1's allocation sites
g = load_json('derived', 'g44-CANONICAL-WORD.json.gz')
rd, zero, tclean, lo, hi = dirt(g)
T = load_json('derived', 'g44-TAGS.json'); site = {int(k) - 16: x[0][0][:2] for k, x in T.items()}
s34 = {r for r, s in site.items() if s in ('S3', 'S4')}
check('C2 #656 gauge44 word: B-read helpers with an all-zero clean row (count, and equal as a SET to the S3 + S4 allocation sites of C1)',
      zero == s34 and len(s34) == 268, (len(rd), len(zero), len(zero & s34)))
finish()
