"""Exact test: does the n = 10 relaxation (see sav10.py: M = I + v w^T, |V n W| odd) admit total savings >= need on
effective puncture P'?  Terms: p 'pair' terms (both sides reduced, x _|_ y, x != y, saving 2; never in V n W) and
q = 10 - p other terms (any type in {00,10,01,11}, reader line or none, source line or none; saving = #reduced sides,
minus 1 if both).  Conditions for j != k: B0[x_j, y_k] = [k in V][j in W]; same term: B0[x_j, y_j] = 1 xor [j in V n W].
Reader lines repeat only as a pair {j, j'} with V = {j, j'} (then exactly one of them is in W); same for sources and W.
Exhaustive DFS (pair terms in canonical order, then the q other terms in canonical order)."""
import core
from itertools import product


def exists_need(Pp, need, return_witness=False):
    Pp = list(Pp); B = core.B0; G = core.G
    opts = Pp + [None]
    pairc = [((v, w), x, y) for (v, w) in ((0, 0), (1, 0), (0, 1)) for x in Pp for y in Pp if x != y and G[x][y] == 0]
    pairc.sort(key=lambda c: (c[0], Pp.index(c[1]), Pp.index(c[2])))
    other = []
    for (v, w) in ((0, 0), (1, 0), (0, 1), (1, 1)):
        for x in opts:
            for y in opts:
                if x is not None and y is not None:
                    same = B[x][y]
                    if same != (1 ^ (v & w)): continue          # same-term condition
                    if (v & w) == 0 and x != y and G[x][y] == 0: continue   # that would be a pair term
                sav = (x is not None) + (y is not None) - (1 if (x is not None and y is not None) else 0)
                other.append(((v, w), x, y, sav))
    def cross_ok(p, q):
        (vp, wp), xp, yp = p[:3]; (vq, wq), xq, yq = q[:3]
        if xp is not None and yq is not None and B[xp][yq] != (vq & wp): return False
        if xq is not None and yp is not None and B[xq][yp] != (vp & wq): return False
        return True
    def dup_ok(terms):
        V = [t for t in terms if t[0][0]]; W = [t for t in terms if t[0][1]]
        for idx in (1, 2):
            seen = {}
            for t in terms:
                l = t[idx]
                if l is None: continue
                seen.setdefault(l, []).append(t)
            for l, ts in seen.items():
                if len(ts) > 2: return False
                if len(ts) == 2:
                    if idx == 1:   # repeated reader: V = these two, exactly one in W
                        if not (len(V) == 2 and all(t[0][0] for t in ts) and (ts[0][0][1] + ts[1][0][1]) == 1): return False
                    else:          # repeated source: W = these two, exactly one in V
                        if not (len(W) == 2 and all(t[0][1] for t in ts) and (ts[0][0][0] + ts[1][0][0]) == 1): return False
        return True
    pmin = max(0, need - 10)
    found = []
    def finish(pairs_chosen):
        p = len(pairs_chosen); q = 10 - p
        base = 2 * p
        if base + q < need: return False
        # choose q other terms (multiset in canonical order), at least one of type 11, odd count of type 11
        def rec2(start, chosen, sav):
            if len(chosen) == q:
                n11 = sum(1 for t in chosen if t[0] == (1, 1))
                if n11 % 2 == 1 and base + sav >= need and dup_ok(pairs_chosen + chosen):
                    found.append(pairs_chosen + chosen); return True
                return False
            if base + sav + 1 * (q - len(chosen)) < need: return False
            for i in range(start, len(other)):
                t = other[i]
                if all(cross_ok(t, c) for c in pairs_chosen) and all(cross_ok(t, c) for c in chosen):
                    chosen.append(t)
                    if rec2(i, chosen, sav + t[3]): return True
                    chosen.pop()
            return False
        return rec2(0, [], 0)
    comp = {}
    def rec(start, chosen):
        p = len(chosen)
        if p >= pmin and finish(chosen): return True
        if p == 9: return False          # ten pair terms impossible (V n W needs a non-pair term)
        for i in range(start, len(pairc)):
            c = pairc[i]
            if any(c[1] == d[1] or c[2] == d[2] for d in chosen): continue   # repeats among pair terms excluded (they would need v or w = e_j + e_j' with one of them in V n W)
            if all(cross_ok(c, d) for d in chosen):
                chosen.append(c)
                if rec(i + 1, chosen): return True
                chosen.pop()
        return False
    ok = rec(0, [])
    return (ok, found[0] if found else None) if return_witness else ok


if __name__ == '__main__':
    import sys, time
    P = list(range(111, 120))
    for need in (11, 12):
        t = time.time(); print('P111 need', need, exists_need(P, need), round(time.time() - t, 1), flush=True)
