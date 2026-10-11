"""Reorder screen on a PR249 snapshot (discovery only; the frozen result is applied and checked by code/stages.py).
usage: reorder_screen.py SNAPDIR OUT.json   (writes the kept moves; then wrap them as stages/<name>-selection.json)
Chafik Boukhalfa (chafreaky) with substantial Anthropic Claude assistance; Apache-2.0."""
import sys, json, math, bisect
from collections import defaultdict
sys.path.insert(0, __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', 'code'))
import stagelib as w3t


def screen(snap):
    s, rec = snap['s'], snap['rec']; n = s['n']; Fm = w3t.Frames(snap['fr']); dim = Fm.dim
    init = {r: s['initial'][str(r)] for r in range(n)}; final = {r: s['final'][str(r)] for r in range(n)}
    ev = [tuple(x) for x in rec.tolist()]
    phi = lambda r: r * math.log(100 / r) if r else 0.0
    incf = defaultdict(list); reads = defaultdict(list); writes = defaultdict(list)
    for i, (op, a, b, c, f, z) in enumerate(ev):
        if op == 1:
            incf[a].append((i, f, True)); writes[a].append(i)
            if b != n: incf[b].append((i, f, True)); reads[b].append(i)
        elif op == 2: incf[a].append((i, c, False)); reads[a].append(i)
        elif op == 3: reads[a].append(i)
    inct = {r: [t for t, f, x in L] for r, L in incf.items()}
    cost = lambda fs: sum(phi(dim[b] - dim[a]) for a, b in zip(fs, fs[1:]) if a != b)
    legal = lambda fs: all(Fm.sub(a, b) for a, b in zip(fs, fs[1:]))
    def path(r, dele=None, add=None):
        L = [(t, f) for t, f, x in incf[r] if t != dele] + ([add] if add else []); L.sort()
        return [init[r]] + [f for t, f in L] + [final[r]]
    count = lambda L, lo, hi: bisect.bisect_left(L, hi) - bisect.bisect_left(L, lo)
    cands = []
    for i, (op, a, b, c, f, z) in enumerate(ev):
        if op != 1 or b == n: continue
        def bp(r):
            L = inct[r]; k = bisect.bisect_left(L, i); pf = incf[r][k - 1][1] if k else init[r]; nf = incf[r][k + 1][1] if k + 1 < len(L) else final[r]
            return pf != f and nf != f
        if not (bp(a) or bp(b)): continue
        base = cost(path(a)) + cost(path(b)); best = None
        for r in (a, b):
            L = inct[r]; k = bisect.bisect_left(L, i)
            for j in range(1, 7):
                for kk, side in ((k + j, 'before'), (k - j, 'after')):
                    if not (0 <= kk < len(L)) or not incf[r][kk][2]: continue
                    T, F, _ = incf[r][kk]; lo, hi = (i + 1, T) if side == 'before' else (T + 1, i)
                    if count(reads[a], lo, hi) or count(writes[b], lo, hi): continue
                    pos = T + (-.5 if side == 'before' else .5)
                    pa = path(a, i, (pos, F)); pb = path(b, i, (pos, F))
                    if not (legal(pa) and legal(pb)): continue
                    d = cost(pa) + cost(pb) - base
                    if d < -1e-9 and (best is None or (d, T) < (best[0], best[1])): best = (d, T, side, F)
        if best: cands.append((best[0], i, best[1], best[2], best[3]))
    cands.sort(key=lambda x: (round(x[0], 9), x[1])); used = set(); keep = []
    for d, i, T, side, F in cands:
        op, a, b, c, f, z = ev[i]
        if {a, b} & used: continue
        used |= {a, b}
        keep.append(dict(record=i, anchor=T, side=side, incidence=[a, b, c], frame_basis=Fm.mats(F)[0], phi=round(d, 6)))
    print('reorder screen: candidates', len(cands), 'kept', len(keep), 'phi %.3f' % sum(e['phi'] for e in keep), flush=True)
    return keep


if __name__ == '__main__':
    keep = screen(w3t.load_snapshot(sys.argv[1]))
    json.dump(dict(moves=keep), open(sys.argv[2], 'w'))
