# Generalised joint edit at a main stop G (main P->G->N): main becomes P->N (drop) or P->X->N (re-stop, X != G).
# Every m-op at G is re-hosted at P, X or N (monotone along the main's time order), each optionally slid inside its
# exact commutation window; partners pay their path change.  Exact joint evaluation of all touched units.
import sys, pickle, jl, pricekit as pk
STAY = True
def nb(po, G):
    k = po.index(G); return (po[k - 1] if k > 0 else None, po[k + 1] if k + 1 < len(po) else None)
def opts_for(M, m, i, charts, mlist, cache):
    e = M.ev[i]
    if e[0] == 'SCALE': return [(M.key[i], C, 0.0, None, None) for C in charts]
    p = e[2] if e[1] == m else e[1]
    if p >= M.n: return []
    if i not in cache:
        lo, hi = M.window(i) if e[0] == 'ADD' else (i, i)
        keys = {M.key[i]}
        if e[0] == 'ADD':
            keys.add(lo + 0.5)
            for x in M.ops[p] + mlist:
                if lo < x < hi and x != i: keys.add(x + 0.5)
        cache[i] = (sorted(keys), M.cost(M.path(p)), {})
    keys, base, cc = cache[i]
    out = []
    G = M.tag[i]
    pst = [j for j in M.ops[p] if M.tag[j] == G and j != i]
    third = set()
    for j in pst:
        ej = M.ev[j]
        if ej[0] in ('ADD', 'COPY'):
            q = ej[2] if ej[1] == p else ej[1]
            third.add(q)
    stay_ok = STAY and pst and m not in third and all(q < M.n for q in third)
    for C in charts:
        if C not in cc:
            l = []
            for k in keys:
                c = M.cost(M.path(p, {i: (k, C)}))
                if c is not None: l.append((k, C, c - base, p, None))
                if stay_ok:
                    ov = {j: (M.key[j], C) for j in pst}; ov[i] = (k, C)
                    tot = 0.0
                    for u in {p} | third:
                        c1 = M.cost(M.path(u, ov))
                        if c1 is None: tot = None; break
                        tot += c1 - M.cost(M.path(u))
                    if tot is not None: l.append((k, C, tot, p, ov))
            cc[C] = l
        out += cc[C]
    return out
def scan_main(M, m, thresh=-1e-9, onlyG=None):
    o = M.path(m); mlist = M.ops[m]; sp = M.sp; res = []
    for gi in range(1, len(o) - 1):
        P, G, N = o[gi - 1], o[gi], o[gi + 1]
        if onlyG is not None and G != onlyG: continue
        Gops = [i for i in mlist if M.tag[i] == G]
        before = [i for i in mlist if i < Gops[0]]; after = [i for i in mlist if i > Gops[-1]]
        prevnonP = max([i for i in before if M.tag[i] != P], default=-1)
        lastP = before[-1] if before else -1
        firstN = after[0] if after else 10 ** 9
        nextnonN = min([i for i in after if M.tag[i] != N], default=10 ** 9)
        # necessary containment for X from partners' neighbours (blocked contacts)
        need_lo = sp[P]; need_hi = sp[N]; anyblocked = False; owned = False
        for i in Gops:
            e = M.ev[i]
            if e[0] == 'SCALE': continue
            p = e[2] if e[1] == m else e[1]
            if p >= M.n: owned = True; break
        if owned: continue
        Xs = [None] + [c for c in range(len(sp)) if c != G and M.legal(P, c) and M.legal(c, N)]
        cache = {}
        for X in Xs:
            charts = [P, N] if X is None else [P, X, N]
            rank = {P: 0, N: 2} if X is None else {P: 0, X: 1, N: 2}
            opts = []; ok = True
            for i in Gops:
                op = [x for x in opts_for(M, m, i, charts, mlist, cache)
                      if (x[1] == P and prevnonP < x[0] < firstN) or (x[1] != P and lastP < x[0] < nextnonN)]
                if not op: ok = False; break
                opts.append(op)
            if not ok: continue
            dmain = (jl.f(abs(M.dim[N] - M.dim[P])) if X is None else jl.f(M.dim[X] - M.dim[P]) + jl.f(M.dim[N] - M.dim[X])) \
                    - jl.f(M.dim[G] - M.dim[P]) - jl.f(M.dim[N] - M.dim[G])
            if dmain + sum(min(x[2] for x in op) for op in opts) >= thresh: continue
            ks = sorted(set(x[0] for op in opts for x in op))
            taus = [ks[0] - 1] + [(a + b) / 2 for a, b in zip(ks, ks[1:])] + [ks[-1] + 1]
            best = None
            for a in range(len(taus)):
                for b in (range(a, len(taus)) if X is not None else [a]):
                    t1, t2 = taus[a], taus[b]
                    tot = 0.0; ch = []
                    for op in opts:
                        c = [x for x in op if (rank[x[1]] == 0 and x[0] < t1) or (rank[x[1]] == 1 and t1 < x[0] < t2) or (rank[x[1]] == 2 and x[0] > t2)]
                        if not c: break
                        x = min(c, key=lambda x: x[2]); ch.append(x); tot += x[2]
                    else:
                        if X is not None and not any(x[1] == X for x in ch): continue
                        if best is None or tot < best[0]: best = (tot, ch)
            if best is None or dmain + best[0] >= thresh: continue
            ch = best[1]; ov = {}
            units = {m} | {x[3] for x in ch if x[3] is not None}
            for i, x in zip(Gops, ch):
                if x[4]:
                    for j, v in x[4].items():
                        if j in ov and ov[j] != v: ov = None; break
                        ov[j] = v
                        ej = M.ev[j]; units |= {ej[1]} | ({ej[2]} if ej[0] in ('ADD', 'COPY') else set())
                    if ov is None: break
                ov[i] = (x[0], x[1])
            if ov is None: continue
            d = 0.0; bad = False
            for r in units:
                c1 = M.cost(M.path(r, ov))
                if c1 is None: bad = True; break
                d += c1 - M.cost(M.path(r))
            if bad or d >= thresh: continue
            res.append(dict(m=m, G=G, P=P, N=N, X=X, dmain=dmain, d=d, ov=ov, units=sorted(units), nops=len(Gops),
                            slid=sum(1 for i, x in zip(Gops, ch) if x[0] != M.key[i])))
    return res
if __name__ == '__main__':
    W = pk.load(sys.argv[1]); M = jl.Word(W)
    allr = []
    for m in sorted(M.mains): allr += scan_main(M, m)
    allr.sort(key=lambda r: r['d'])
    print('candidates', len(allr), 'drops', sum(1 for r in allr if r['X'] is None), 'slid', sum(1 for r in allr if r['slid']))
    for r in allr[:25]: print(r['m'], 'G', r['G'], 'P/X/N', r['P'], r['X'], r['N'], 'dmain %.4f d %.4f nops %d slid %d units %s' % (r['dmain'], r['d'], r['nops'], r['slid'], r['units']))
    pickle.dump(allr, open(sys.argv[2], 'wb'))
