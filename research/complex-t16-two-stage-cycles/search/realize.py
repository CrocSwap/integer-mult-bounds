"""Turn a min-diff class solution (triples (bin, call, width)) into an owner map closest to the selected map A:
keep A's helper label wherever A's (bin, call, width) placement is kept, assign the rest of each class arbitrarily
(deterministically), then choose each bin's serialization order to maximise rows whose offset equals A's
(contiguous offsets from 0, R6), then audits (seed67 rules) and prices the result.
argv: LIBDIR SOL_JSON OUT_OWNERS. Standard library only."""
import sys, json, gzip, itertools
sys.path.insert(0, sys.argv[1]); import lib
from collections import Counter, defaultdict
A = lib.selroles; sol = json.load(open(sys.argv[2]))
B = lambda z: (z['owner_replica'], z['child'], z['port'])
trip = {(tuple(k), t, w) for k, t, w in sol['triples']}
assert len(trip) == len(A)
rows = [dict(z) for z in A]
left = defaultdict(list)   # class -> unplaced row indices
used = set()
for i, z in enumerate(A):
    c = (B(z), z['time'], z['width'])
    if c in trip: used.add(c)
    else: left[z['time'], z['width']].append(i)
free = defaultdict(list)
for c in sorted(trip - used): free[c[1], c[2]].append(c[0])
for tw, idx in left.items():
    assert len(idx) == len(free[tw])
    for i, k in zip(sorted(idx), free[tw]): rows[i] = lib.relocate(rows[i], *k)
# per-bin order: maximise rows at A's offset
bybin = defaultdict(list)
for i, z in enumerate(rows): bybin[B(z)].append(i)
def tiles(gaps, ws):
    """Can the multiset ws exactly tile the gap lengths? (small: brute force via DP over assignment)"""
    ws = sorted(ws, reverse=True)
    def rec(j, g):
        if j == len(ws): return all(x == 0 for x in g)
        seen = set()
        for a in range(len(g)):
            if g[a] >= ws[j] and g[a] not in seen:
                seen.add(g[a]); g2 = list(g); g2[a] -= ws[j]
                if rec(j + 1, g2): return True
        return False
    return rec(0, list(gaps))
def layout(fixed, rest, fill):
    """fixed: list of (offset, width, i) kept at A offsets; rest: (width, i). Return {i: offset} or None."""
    fixed = sorted(fixed); pos = 0; gaps = []
    for o, w, i in fixed:
        if o < pos: return None
        gaps.append((pos, o - pos)); pos = o + w
    if pos > fill: return None
    gaps.append((pos, fill - pos))
    if not tiles([g for _, g in gaps], [w for w, _ in rest]): return None
    # realise the tiling greedily with backtracking
    rest = sorted(rest, reverse=True); out = {i: o for o, w, i in fixed}
    def rec(j, g):
        if j == len(rest): return all(x[1] == 0 for x in g)
        w, i = rest[j]
        for a in range(len(g)):
            if g[a][1] >= w:
                g2 = list(g); g2[a] = (g[a][0] + w, g[a][1] - w); out[i] = g[a][0]
                if rec(j + 1, g2): return True
        return False
    assert rec(0, gaps); return out
stat = Counter()
for k, idx in bybin.items():
    fill = sum(rows[i]['width'] for i in idx)
    cand = [i for i in idx if B(A[i]) == k]          # kept placements, candidates to keep A's offset
    other = [i for i in idx if B(A[i]) != k]
    best = None
    for r in range(len(cand), -1, -1):
        for S in itertools.combinations(cand, r):
            L = layout([(A[i]['offset'], A[i]['width'], i) for i in S],
                       [(rows[i]['width'], i) for i in idx if i not in S], fill)
            if L is not None: best = L; break
        if best is not None: break
        if len(cand) > 14 and r < len(cand) - 3: raise SystemExit(f'bin {k} too hard')
    for i, o in best.items(): rows[i]['offset'] = o
for z, a in zip(rows, A):
    assert all(z[f] == a[f] for f in ('stage', 'replica', 'time', 'helper', 'width'))
au = lib.audit(rows)
pr = lib.price(au['profile'])
ch = sum(a != z for a, z in zip(A, rows)); rel = sum(B(a) != B(z) for a, z in zip(A, rows))
print('changed', ch, 'relocated', rel, 'offset_only', ch - rel, 'idle', dict(sorted(au['idle'].items())), 'kappa', pr['kappa_decimal'])
open(sys.argv[3], 'wb').write(gzip.compress(json.dumps(rows).encode(), mtime=0))
