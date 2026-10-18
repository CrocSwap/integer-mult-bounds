"""census.py: exact two-shock helper-donor relations for EVERY helper pivot read in B before its first write.
Independent re-implementation of the #1274/#1297 rule (rohanarun's search_relations.py): delete the early reads of a
pivot q, then compensate the exact rational output difference d with one helper cut (h += a*q after an output read of h,
restored h -= a*q at the end of early cleanup) and one donor pair (x += c*q / x -= c*q around an output read of x),
all coefficients dyadic and both nonzero.  Adds pivots never written in B (first write = len(B)).
--restore first: the helper cut is restored just before the pivot's first B write instead of at the end of early cleanup
(exact by construction, since the pivot still holds its initial value there).  Output records carry no timing fields, so a
rerun is byte-identical.  Credit: rule and edit format from rohanarun's #1297 search_relations.py and Jeremy Kothe's #1274.
usage: python3 -B census.py WORD.json.gz OUT.json [--workers 12] [--pivots ...] [--restore tail|first]"""
import argparse, gzip, json, os, resource, signal, sys, time, multiprocessing as mp
from fractions import Fraction as Q
W = None
RESTORE = 'tail'
def coef(g): return Q(g[3], g[4]) if g[0] == 'add' else Q(g[2], g[3])
def dyadic(c): return c.denominator & (c.denominator - 1) == 0
def addv(a, b, c):
    d = dict(a)
    for k, v in b.items():
        x = d.get(k, 0) + c * v
        if x: d[k] = x
        else: d.pop(k, None)
    return d
def col(seq, q):
    r = {q: Q(1)}
    for g in seq:
        t = g[1]
        if g[0] == 'add':
            if g[2] in r:
                x = r.get(t, 0) + coef(g) * r[g[2]]
                if x: r[t] = x
                else: r.pop(t, None)
        elif t in r:
            r[t] = r[t] * coef(g)
    return r
def mask(v):
    m = 0
    for k in v: m |= 1 << k
    return m
def solve(u, v, d):
    keys = sorted(set(u) | set(v) | set(d)); i = keys[0]; ui, vi, di = u.get(i, 0), v.get(i, 0), d.get(i, 0)
    for j in keys:
        uj, vj, dj = u.get(j, 0), v.get(j, 0), d.get(j, 0); det = ui * vj - uj * vi
        if det:
            a = (di * vj - dj * vi) / det; b = (ui * dj - uj * di) / det
            if not a or not b or not dyadic(a) or not dyadic(b): return None
            return (a, b) if all(a * u.get(k, 0) + b * v.get(k, 0) == d.get(k, 0) for k in keys) else None
    return None
def init(path, restore='tail'):
    global W, RESTORE; W = json.loads(gzip.decompress(open(path, 'rb').read())); RESTORE = restore
def relations(q):
    signal.alarm(900)
    t0 = time.monotonic(); w = W; B = w['B']; ne = len(w['early_cleanup']); tail = [w['cleanup'][i] for i, U in w['early_cleanup']]
    seq = B + tail
    first = next((i for i, g in enumerate(B) if g[1] == q), len(B))
    dele = {i for i in range(first) if B[i][0] == 'add' and B[i][2] == q}
    if not dele: return dict(pivot=q, early=0, matches=[])
    new = [g for i, g in enumerate(seq) if i not in dele]
    d = addv(col(seq, q), col(new, q), -1)
    cols = {}; hs = []; ts = []; snap = None
    for i in range(len(seq) - 1, -1, -1):
        g = seq[i]
        if i == first - 1 and RESTORE == 'first': snap = {k: dict(v) for k, v in cols.items()}
        if i < first and g[0] == 'add' and 112 <= g[1] < 224 and g[2] >= 224 and g[2] != q and i not in dele:
            h = g[2]
            base_h = (snap.get(h, {h: Q(1)}) if snap is not None else {h: Q(1)}) if RESTORE == 'first' else {h: Q(1)}
            eff = addv(cols.get(h, {h: Q(1)}), base_h, -1)
            if eff: hs.append((i + 1, h, eff))
            ts.append((i, g, dict(cols.get(g[1], {g[1]: Q(1)}))))
        if i in dele: continue
        if g[0] == 'add':
            t, s = g[1], g[2]; cols[s] = addv(cols.get(s, {s: Q(1)}), cols.get(t, {t: Q(1)}), coef(g))
        else:
            t = g[1]; c = coef(g); cols[t] = {k: x * c for k, x in cols.get(t, {t: Q(1)}).items()}
    md = mask(d); tm = [mask(v) for _, _, v in ts]; out = []; tried = 0
    for cut, h, u in hs:
        need = md & ~mask(u)
        for (i, g, v), mv in zip(ts, tm):
            if h == g[2] or need & ~mv: continue
            tried += 1; sol = solve(u, v, d)
            if not sol: continue
            a, b = sol; c = b / coef(g)
            if not dyadic(c): continue
            ins = [[i, ['add', g[2], q, c.numerator, c.denominator, []]], [i + 1, ['add', g[2], q, -c.numerator, c.denominator, []]], [cut, ['add', h, q, a.numerator, a.denominator, []]]]
            if RESTORE == 'first':
                ed = dict(delete=sorted(dele), insert=ins + [[first, ['add', h, q, -a.numerator, a.denominator, []]]], tail=[], prepend=[])
            else:
                ed = dict(delete=sorted(dele), insert=ins, tail=[[ne, ['add', h, q, -a.numerator, a.denominator, []]]], prepend=[])
            out.append(dict(pivot=q, helper=h, cut=cut, output=g[1], hook=i, donor=g[2], amount=str(a), correction=str(b), ed=ed))
    signal.alarm(0)
    return dict(pivot=q, early=len(dele), first=first, d_support=len(d), hs=len(hs), ts=len(ts), solved=tried, matches=out)
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('word'); ap.add_argument('out'); ap.add_argument('--workers', type=int, default=12)
    ap.add_argument('--pivots', nargs='*', type=int); ap.add_argument('--restore', choices=('tail', 'first'), default='tail'); a = ap.parse_args()
    RESTORE = a.restore
    init(a.word, a.restore); B = W['B']; first = {}
    for i, g in enumerate(B): first.setdefault(g[1], i)
    piv = a.pivots or sorted({g[2] for i, g in enumerate(B) if g[0] == 'add' and g[2] >= 224 and i < first.get(g[2], len(B))})
    print('pivots', len(piv), flush=True); res = []; t0 = time.time()
    with mp.get_context('fork').Pool(a.workers, initializer=init, initargs=(a.word, a.restore), maxtasksperchild=8) as pool:
        for n, r in enumerate(pool.imap_unordered(relations, piv), 1):
            res.append(r)
            if r['matches']: print(f"  {n}/{len(piv)} {time.time()-t0:.0f}s pivot {r['pivot']} early {r['early']} matches {len(r['matches'])}", flush=True)
    res.sort(key=lambda r: r['pivot'])
    json.dump(res, open(a.out, 'w'), sort_keys=True)
    print('done', len(res), 'pivots with matches', sum(1 for r in res if r['matches']), 'matches', sum(len(r['matches']) for r in res), f'{time.time()-t0:.0f}s')
