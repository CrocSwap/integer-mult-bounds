# EIGENCAP ec1 (own code): exact check of the eigen-capacity laws on built Q=0 words (QZBUILD chain/ML recipes, rebuilt exactly).
# Laws checked: (a) d_j = dim ker(P_j+I) = 2(j-1) for j>=1; (b) R_j = Im(P_j - I) = W_j (span of contact planes of first j hosts), dim 2j for j<k;
# (c) IDLE LAW: every middle stage has nu_t >= 2 non-invariant non-contact events, H_t contains Pi_t + P_j^{-1} Pi_t (dim 4);
# (d) no P_j-fixed vector in Pi_t (middle); (e) COVER-CAP p(S) <= 2(k-|S|-1) for every S that is a union... (all S met by events).
import sys, os, itertools
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'qzbuild'))
from fractions import Fraction as Fr
from qzchain import eye, T, add, rank, mm, Z, O
from qzword import mat_inv
def twist(vi, wi, vj, wj, a, b, n):
    return [[(O if r == c else Z) + 2*a*b*(vi[r]*wi[c] + vj[r]*wj[c]) - 2*a*vi[r]*wj[c] - 2*b*(1+a*b)*vj[r]*wi[c] for c in range(n)] for r in range(n)]
def outer(v, w): return [[x*y for y in w] for x in v]
def analyse(d, Vv, Ww, AB, name):
    n, k, m = d.n, d.k, d.m
    # time index of each incidence = number of hosts at/before it (contacts: own host)
    Ps = [eye(n)]; Vt = {}
    for h, (i, j) in enumerate(d.hostinc):
        a, b = AB[h]; X = twist(Vv[i], Ww[i], Vv[j], Ww[j], a, b, n)
        Vt[d.hosts[h]] = X; Ps.append(mm(X, Ps[-1], Z))
    I = eye(n)
    assert Ps[-1] == [[-x for x in r] for r in I], 'prod V != -I'
    ok = True; rep = []
    # (a)
    dj = [n - rank(add(Ps[j], I)) for j in range(k+1)]
    ok &= all(dj[j] == 2*(j-1) for j in range(1, k+1)) and dj[0] == 0
    rep.append('d_j=%s' % dj)
    # (b)
    cont = {}  # stage -> (v1, v2, w1, w2)
    for h, (i, j) in enumerate(d.hostinc): cont[d.hosts[h]] = (Vv[i], Vv[j], Ww[i], Ww[j])
    Wd = []
    for j in range(k+1):
        Wv = [x for h in range(j) for x in cont[d.hosts[h]][:2]]
        R = T(add(Ps[j], I, -O))  # columns of P_j - I as rows
        rW = rank(Wv) if Wv else 0; rR = rank(R) if j else 0
        rWR = rank(Wv + R) if Wv else 0
        Wd.append((rW, rR, rWR))
        if j < k: ok &= (rW == 2*j and rR == 2*j and rWR == 2*j)
    rep.append('dimW,R,W+R=%s' % Wd)
    # invariance of each non-contact event
    inv = []
    for e in range(m):
        Le = Ps[d.nh[e]]; Li = mat_inv(Le, Z, O)
        vm = [sum(Li[r][c]*Vv[e][c] for c in range(n)) for r in range(n)]
        wm = [sum(Le[c][r]*Ww[e][c] for c in range(n)) for r in range(n)]
        inv.append(outer(vm, wm) == outer(Vv[e], Ww[e]))
    contacts = set(x for p in d.hostinc for x in p)
    # (c),(d) per stage
    for pos, t in enumerate(d.hosts):
        j = pos  # hosts before t
        evs = [e for e in range(m) if t in d.inc[e][0]]
        nu = sum(1 for e in evs if e not in contacts and not inv[e])
        Hn = [Vv[e] for e in evs if e in contacts or not inv[e]]
        v1, v2 = cont[t][:2]
        Pi = mat_inv(Ps[j], Z, O)
        pv = [[sum(Pi[r][c]*v[c] for c in range(n)) for r in range(n)] for v in (v1, v2)]
        core = rank([v1, v2] + pv)
        inH = rank(Hn + pv) == rank(Hn)
        fixed = 2 - rank([[sum(Ps[j][r][c]*v[c] for c in range(n)) - v[r] for r in range(n)] for v in (v1, v2)])
        middle = 0 < pos < k-1
        if middle: ok &= (nu >= 2 and core == 4 and fixed == 0 and inH)
        rep.append('stage %d pos %d nu %d core %d fixed %d inH %s %s' % (t, pos, nu, core, fixed, inH, 'MID' if middle else ''))
    # (e) cover cap over all S that are intersections of event sets
    Ssets = set()
    for e in range(m):
        if e in contacts: continue
        S = d.inc[e][0]
        for r in range(1, len(S)+1):
            for sub in itertools.combinations(sorted(S), r): Ssets.add(frozenset(sub))
    worst = None
    for S in Ssets:
        p = sum(1 for e in range(m) if e not in contacts and S <= d.inc[e][0])
        cap = 2*max(k - len(S) - 1, 0)
        ok &= p <= cap
        sl = cap - p
        if worst is None or sl < worst[0]: worst = (sl, sorted(S), p, cap)
    rep.append('COVER-CAP min slack %s' % (worst,))
    rep.append('invariant non-contact events: %d / %d' % (sum(1 for e in range(m) if e not in contacts and inv[e]), m - len(contacts)))
    print(name, 'ALL LAWS', ok); [print('   ', x) for x in rep]
    return ok
if __name__ == '__main__':
    from qzml import build_ml
    from qzchain import build_chain, chain_frames
    import qzchain
    for k in range(3, 10):
        d, C, taus = build_ml(k); Vv, Ww, AB = build_ml.data
        analyse(d, Vv, Ww, AB, 'ML k%d' % k)
