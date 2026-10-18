# Prepared by eumemic with substantial Anthropic Claude assistance; Apache-2.0.
"""CP-SAT plan for the quad skeleton (skeleton B: every quad content delivered to its 6 owner D6s).

Choices
  match[f]      perfect matching of each 4-frame into two y-pairs; a D6 owned by a y-pair is (y,y), else (z,z)
  ext[q,H]      extra pi-cell carried by the butterfly output of quad q for owner H: 'D' (its d-cell), 'Q' (its Q-cell)
                or '0'; per quad and block pair the two owners' outputs must be independent, and the number of
                block pairs using u = a + a' (ext '0') must be even (the six outputs S + u are then independent)
  plus[H]       for each (z,z) D6: the single line (from its d-cell) carried by its third register, and which of its
                two targets receives it
Constraints: every target's d-line parity is exactly sigma(Phi - t) (no single-line fix-ups at (y,y) D6s); the two
targets of a (y,y) D6 need the same Q-delivery.
"""
import json
import os
import sys
from collections import defaultdict

from ortools.sat.python import cp_model

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "code", "skeleton"))
from geom import Geom  # noqa: E402


def solve(G, fixed_match=None, seed=0, time_limit=60.0, extra_cuts=(), use_q=True, use_d=True):
    M = cp_model.CpModel()
    # matchings
    match = {}
    for f in G.frames4:
        if fixed_match is not None:
            match[f] = None
        else:
            match[f] = [M.NewBoolVar("m%s_%d" % (f, k)) for k in range(3)]
            M.AddExactlyOne(match[f])
    mpairs = {}
    for f in G.frames4:
        a, b, c, d = f
        mpairs[f] = [((a, b), (c, d)), ((a, c), (b, d)), ((a, d), (b, c))]
    isyy = {}
    for f in G.frames4:
        for k, (p1, p2) in enumerate(mpairs[f]):
            for p in (p1, p2):
                if fixed_match is not None:
                    isyy[p] = 1 if fixed_match[f] == k else isyy.get(p, 0)
                else:
                    isyy.setdefault(p, []).append(match[f][k])
    if fixed_match is None:
        isyy = {p: (v[0] if len(v) == 1 else v) for p, v in isyy.items()}
    # ext variables
    eD, eQ, e0 = {}, {}, {}
    for q in range(len(G.quads)):
        for H in G.qowners[q]:
            eD[q, H] = M.NewBoolVar("eD%d_%s" % (q, H))
            eQ[q, H] = M.NewBoolVar("eQ%d_%s" % (q, H))
            e0[q, H] = M.NewBoolVar("e0%d_%s" % (q, H))
            M.AddExactlyOne([eD[q, H], eQ[q, H], e0[q, H]])
    for q in range(len(G.quads)):
        zs = []
        for pi, (H1, H2) in G.qpairs[q].items():
            assert G.comp[G.cblk[H1]] == G.cblk[H2]
            M.AddBoolOr([eQ[q, H1].Not(), eD[q, H2].Not()])
            M.AddBoolOr([eD[q, H1].Not(), eQ[q, H2].Not()])
            M.AddBoolOr([e0[q, H1].Not(), e0[q, H2].Not()])
            z = M.NewBoolVar("z%d_%s" % (q, pi))
            M.AddBoolOr([e0[q, H1], e0[q, H2]]).OnlyEnforceIf(z)
            M.AddBoolAnd([e0[q, H1].Not(), e0[q, H2].Not()]).OnlyEnforceIf(z.Not())
            zs.append(z)
        k = M.NewIntVar(0, 1, "k%d" % q)
        M.Add(sum(zs) == 2 * k)
    # A_H parity of D extras
    # plus variables for each D6 (used only if (z,z)): line choice (0/1 index in dcell) and recipient (0/1 in owner)
    pl, pr = {}, {}
    for H in G.cells:
        pl[H] = M.NewBoolVar("pl%s" % (H,))
        pr[H] = M.NewBoolVar("pr%s" % (H,))
    # helpers: product booleans
    def AND(*xs):
        v = M.NewBoolVar("")
        M.AddBoolAnd(list(xs)).OnlyEnforceIf(v)
        M.AddBoolOr([x.Not() for x in xs]).OnlyEnforceIf(v.Not())
        return v

    def lit(x):
        return x
    zz = {}
    for H in G.cells:
        y = isyy[H]
        if isinstance(y, int):
            zz[H] = 1 - y
        else:
            zv = M.NewBoolVar("zz%s" % (H,))
            M.Add(zv == 1 - y)
            zz[H] = zv
    # per target constraints
    for t in range(G.blocks and 120):
        f = G.phi[t]
        partners = [x for x in f if x != t]
        myD6 = [tuple(sorted((t, e))) for e in partners]
        for l in partners:
            terms = []
            for H in myD6:
                if l in G.dcell[H]:
                    for q in G.d6quads[H]:
                        terms.append(eD[q, H])
                # plus single received by t from (z,z) H
                dc = G.dcell[H]
                if l in dc:
                    idx = dc.index(l)
                    tidx = H.index(t)
                    linev = pl[H] if idx == 1 else pl[H].Not()
                    recv = pr[H] if tidx == 1 else pr[H].Not()
                    z = zz[H]
                    if isinstance(z, int):
                        if z:
                            terms.append(AND(linev, recv))
                    else:
                        terms.append(AND(linev, recv, z))
            # 1 + sum(terms) even
            if use_d:
                n = M.NewIntVar(0, 20, "n%d_%d" % (t, l))
                M.Add(1 + sum(terms) == 2 * n)
    # Q equality for y-partners: for each 4-frame and each matching pair (t,m): the Q-cell extras from t's z-D6s and
    # m's z-D6s agree line by line on Psi
    for f in (G.frames4 if use_q else []):
        psi = G.psi[f]
        for k, (p1, p2) in enumerate(mpairs[f]):
            act = None if fixed_match is not None else match[f][k]
            if fixed_match is not None and fixed_match[f] != k:
                continue
            for (t, m) in (p1, p2):
                zt = [tuple(sorted((t, e))) for e in f if e not in (t, m)]
                zm = [tuple(sorted((m, e))) for e in f if e not in (t, m)]
                for l in psi:
                    terms = []
                    for H in zt + zm:
                        for q in G.d6quads[H]:
                            if l in G.qcell[(q, H)]:
                                terms.append(eQ[q, H])
                    n = M.NewIntVar(0, 20, "")
                    if act is None:
                        M.Add(sum(terms) == 2 * n)
                    else:
                        M.Add(sum(terms) == 2 * n).OnlyEnforceIf(act)
    # Q-node independence (fixed matching only): the six Q-deliveries of each block's node must be independent
    if use_q and fixed_match is not None:
        TRUE = M.NewConstant(1)
        yys = []
        for f in G.frames4:
            yys += list(mpairs[f][fixed_match[f]])
        for bi in range(len(G.blocks)):
            cb = G.comp[bi]
            Hs = sorted(H for H in yys if G.cblk[H] == cb)
            assert len(Hs) == 6
            vterms = []     # per H: dict line -> list of eQ literals
            for Hy in Hs:
                t, m = Hy
                f = G.phi[t]
                zt = [tuple(sorted((t, e))) for e in f if e not in (t, m)]
                dl = defaultdict(list)
                for H in [Hy] + zt:
                    for q in G.d6quads[H]:
                        for l in G.qcell[(q, H)]:
                            dl[l].append(eQ[q, H])
                vterms.append(dl)
            qlines = sorted(set(l for f in G.frames4 if G.blk[f[0]] == bi for l in f))
            for C in range(1, 64):
                idx = [i for i in range(6) if C >> i & 1]
                ors = []
                for l in qlines:
                    terms = []
                    for i in idx:
                        terms += vterms[i].get(l, [])
                    c0 = len(idx) & 1
                    p = M.NewBoolVar("")
                    # p = c0 xor XOR(terms)  <=>  XOR(terms + [p]) = c0  <=> XOR(terms + [p] + [TRUE]*(1-c0)) = 1
                    M.AddBoolXOr(terms + [p] + ([TRUE] if c0 == 0 else []))
                    ors.append(p)
                M.AddBoolOr(ors)
    for cut in extra_cuts:
        cut(M, dict(eD=eD, eQ=eQ, e0=e0, pl=pl, pr=pr, match=match))
    S = cp_model.CpSolver()
    S.parameters.max_time_in_seconds = time_limit
    S.parameters.num_workers = 4
    S.parameters.random_seed = seed
    r = S.Solve(M)
    status = S.StatusName(r)
    if r not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return status, None
    sol = dict(match={}, ext={}, plus={})
    for f in G.frames4:
        if fixed_match is not None:
            sol["match"][f] = fixed_match[f]
        else:
            sol["match"][f] = [k for k in range(3) if S.Value(match[f][k])][0]
    for (q, H) in eD:
        sol["ext"][(q, H)] = "D" if S.Value(eD[q, H]) else ("Q" if S.Value(eQ[q, H]) else "0")
    for H in G.cells:
        sol["plus"][H] = (G.dcell[H][S.Value(pl[H])], H[S.Value(pr[H])])
    return status, sol


if __name__ == "__main__":
    G = Geom()
    fm = {f: 0 for f in G.frames4} if (len(sys.argv) > 1 and sys.argv[1] == "fixed") else None
    for uq, ud in ((False, True), (True, False), (True, True)):
        st, sol = solve(G, fixed_match=fm, use_q=uq, use_d=ud)
        print("use_q", uq, "use_d", ud, "status", st)
    if sol:
        from collections import Counter
        print("ext counts", Counter(sol["ext"].values()), "matchings", Counter(sol["match"].values()))
