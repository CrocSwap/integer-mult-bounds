# Prepared by eumemic with substantial Anthropic Claude assistance; Apache-2.0.
"""CP-SAT plan for skeleton L3 (3 registers per cell, type-L targets that climb cell -> t^perp; every D6 (z,z)).
Needs ortools.  Not run by verify.sh.  The model is the skeleton-L model (text below, written for L2) plus the L3
host variables qh: every D6 is (z,z), each target's Q-delivery is the third register of one D6 of its triple (its
host), and the two D6s of a 4-frame without a host take a free keeper whose line goes to one recipient (rcv).

Per 4-frame Phi: every target t picks a partner x(t) in Phi - t.  It reads, in phase B, the keeper of the cell
C_t = Phi - {t, x(t)} at that cell (its single d-line l_t in C_t), then arrives at the D6 owned by {t, x(t)}.
The four arrival D6s of a 4-frame are distinct; the two D6s without an arriver are (z,z) and take a Q-delivery as
third register, whose needer goes to one recipient (each target gets exactly one Q-delivery: at its arrival D6 or as
a (z,z) recipient).  The four d-single keepers of a 4-frame hold four distinct lines; afterwards they climb to their
block frame and feed the block node, which makes the 12 Q-deliveries for the complementary block's targets.
Quad butterfly extras ext[q,H] in {D,Q,0} as in PR #493's discovery/plan.py (per quad and block pair the two owners differ;
the number of block pairs using '0' is even).  A_H = #D mod 2 (d-cell parity of D6 H), q_H = Q-cells with ext Q.
Constraints: d-line parity of every target exact; per 4-frame of every block the Q-extras X_u of its four targets
have a 2-dimensional difference space (so every node's Q-deliveries have rank >= 7 and need <= 5 extra inputs)."""
import itertools
import json
import os
import sys
from collections import defaultdict

from ortools.sat.python import cp_model

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "e8-bit-carrier-skeleton", "code",
                                "skeleton"))   # PR #493 on main
from geom import Geom  # noqa: E402


def build_model(G, rank_mode="strong", cycle_only=False, seed=0):
    M = cp_model.CpModel()
    TRUE = M.NewConstant(1)
    # ---- ext
    eD, eQ, e0 = {}, {}, {}
    for q in range(len(G.quads)):
        for H in G.qowners[q]:
            eD[q, H] = M.NewBoolVar("")
            eQ[q, H] = M.NewBoolVar("")
            e0[q, H] = M.NewBoolVar("")
            M.AddExactlyOne([eD[q, H], eQ[q, H], e0[q, H]])
    for q in range(len(G.quads)):
        zs = []
        for pi, (H1, H2) in G.qpairs[q].items():
            M.AddBoolOr([eQ[q, H1].Not(), eD[q, H2].Not()])
            M.AddBoolOr([eD[q, H1].Not(), eQ[q, H2].Not()])
            M.AddBoolOr([e0[q, H1].Not(), e0[q, H2].Not()])
            z = M.NewBoolVar("")
            M.AddBoolOr([e0[q, H1], e0[q, H2]]).OnlyEnforceIf(z)
            M.AddBoolAnd([e0[q, H1].Not(), e0[q, H2].Not()]).OnlyEnforceIf(z.Not())
            zs.append(z)
        k = M.NewIntVar(0, 1, "")
        M.Add(sum(zs) == 2 * k)
    # A_H literal lists and q_H per Psi line
    A_terms = {H: [eD[q, H] for q in G.d6quads[H]] for H in G.cells}
    qline_terms = {}          # (H, line) -> list of eQ literals contributing that Psi line
    for H in G.cells:
        for q in G.d6quads[H]:
            for l in G.qcell[(q, H)]:
                qline_terms.setdefault((H, l), []).append(eQ[q, H])
    # ---- per 4-frame choices
    part = {}                  # (t, x) -> bool
    lt = {}                    # (t, l) -> bool : keeper line of t's d-single cell is l
    arr = {}                   # D6 cell -> bool has arriver
    rcv = {}                   # (H, t) -> bool : t is the recipient of (z,z) H's Q-delivery
    qh = {}                    # (t, x) -> bool : the D6 owned by {t, x} hosts t's Q-delivery
    for f in G.frames4:
        cells = [tuple(sorted(p)) for p in itertools.combinations(f, 2)]
        for t in f:
            xs = [x for x in f if x != t]
            for x in xs:
                part[t, x] = M.NewBoolVar("")
            M.AddExactlyOne([part[t, x] for x in xs])
            # keeper line: in C_t = f - {t,x}
            for l in f:
                if l != t:
                    lt[t, l] = M.NewBoolVar("")
            # l must lie in C_t: l != x(t)
            for x in xs:
                M.AddImplication(part[t, x], lt[t, x].Not())
            M.AddExactlyOne([lt[t, l] for l in f if l != t])
        # distinct keeper lines (cover Phi): each line l is the keeper line of exactly one target
        for l in f:
            M.AddExactlyOne([lt[t, l] for t in f if t != l])
        # arrival D6s distinct
        for c in cells:
            a, b = c
            arr[c] = M.NewBoolVar("")
            M.Add(part[a, b] + part[b, a] == arr[c])
        M.Add(sum(arr[c] for c in cells) == 4)
        if cycle_only:
            # every target in exactly one (z,z) D6
            for t in f:
                M.Add(sum(arr[tuple(sorted((t, x)))] for x in f if x != t) == 2)
        # L3: every D6 is (z,z).  Each target's Q-delivery is the third register of one of its D6s (its "host", all
        # hosts of a 4-frame distinct); the two D6s without a host take a free keeper of the complementary block
        # whose line goes to a recipient (rcv).  qat[t] is the host indicator list (kept in the solution as 'qhost').
        host = {}
        for t in f:
            for x in f:
                if x != t:
                    qh[t, x] = M.NewBoolVar("")
            M.AddExactlyOne([qh[t, x] for x in f if x != t])
        for c in cells:
            a, b = c
            host[c] = M.NewBoolVar("")
            M.Add(qh[a, b] + qh[b, a] == host[c])
            for t in c:
                rcv[c, t] = M.NewBoolVar("")
            M.Add(rcv[c, c[0]] + rcv[c, c[1]] == 1).OnlyEnforceIf(host[c].Not())
            M.Add(rcv[c, c[0]] + rcv[c, c[1]] == 0).OnlyEnforceIf(host[c])
        M.Add(sum(host[c] for c in cells) == 4)
        # parity per target: for each d-line y of t: 1 + sum_{H ∋ t, y in dcell(H)} A_H + [lt[t,y]] even
        for t in f:
            for y in f:
                if y == t:
                    continue
                terms = []
                for x in f:
                    if x == t:
                        continue
                    H = tuple(sorted((t, x)))
                    if y in G.dcell[H]:
                        terms += A_terms[H]
                terms.append(lt[t, y])
                # XOR(terms) == 1
                M.AddBoolXOr(terms)
    # ---- Q-extras X_u per target (vector over Psi lines) and rank proxy
    X = {}
    for f in G.frames4:
        psi = G.psi[f]
        for t in f:
            for l in psi:
                v = M.NewBoolVar("")
                terms = []
                for x in f:
                    if x == t:
                        continue
                    H = tuple(sorted((t, x)))
                    terms += qline_terms.get((H, l), [])
                # v = XOR(terms)  <=> XOR(terms + [v]) = 0 <=> XOR(terms + [v, TRUE]) = 1
                M.AddBoolXOr(terms + [v, TRUE])
                X[t, l] = v
        if rank_mode == "strong":
            t0, t1, t2, t3 = f
            dif = {}
            for (a, b) in ((t1, t0), (t2, t0), (t1, t2)):
                nz = []
                for l in psi:
                    w = M.NewBoolVar("")
                    M.AddBoolXOr([X[a, l], X[b, l], w, TRUE])     # w = X_a + X_b
                    nz.append(w)
                M.AddBoolOr(nz)                                     # difference nonzero
    vars_ = dict(eD=eD, eQ=eQ, e0=e0, part=part, lt=lt, arr=arr, rcv=rcv, qh=qh, X=X)
    return M, vars_


def extract(S, V):
    sol = dict(ext={}, partner={}, kline={}, rcv={}, qhost={})
    for (q, H) in V["eD"]:
        sol["ext"][(q, H)] = "D" if S.Value(V["eD"][q, H]) else ("Q" if S.Value(V["eQ"][q, H]) else "0")
    for (t, x), b in V["part"].items():
        if S.Value(b):
            sol["partner"][t] = x
    for (t, l), b in V["lt"].items():
        if S.Value(b):
            sol["kline"][t] = l
    for (c, t), b in V["rcv"].items():
        if S.Value(b):
            sol["rcv"][c] = t
    for (t, x), b in V["qh"].items():
        if S.Value(b):
            sol["qhost"][t] = x
    return sol


def solve(G, time_limit=120.0, seed=0, **kw):
    M, V = build_model(G, **kw)
    S = cp_model.CpSolver()
    S.parameters.max_time_in_seconds = time_limit
    S.parameters.num_workers = 4
    S.parameters.random_seed = seed
    r = S.Solve(M)
    st = S.StatusName(r)
    if r not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return st, None
    return st, extract(S, V)


def save_plan(sol, path):
    out = dict(ext=[[q, list(H), e] for (q, H), e in sorted(sol["ext"].items())],
               partner=sorted(sol["partner"].items()), kline=sorted(sol["kline"].items()),
               rcv=[[list(c), t] for c, t in sorted(sol["rcv"].items())], qhost=sorted(sol["qhost"].items()))
    json.dump(out, open(path, "w"), sort_keys=True)


def load_plan(path):
    d = json.load(open(path))
    return dict(ext={(q, tuple(H)): e for q, H, e in d["ext"]}, partner={t: x for t, x in d["partner"]},
                kline={t: l for t, l in d["kline"]}, rcv={tuple(c): t for c, t in d["rcv"]},
                qhost={t: x for t, x in d["qhost"]})


if __name__ == "__main__":
    G = Geom()
    mode = sys.argv[1] if len(sys.argv) > 1 else "strong"
    cyc = len(sys.argv) > 2 and sys.argv[2] == "cycle"
    st, sol = solve(G, rank_mode=mode, cycle_only=cyc)
    print("status", st)
    if sol:
        from collections import Counter
        print("ext counts", Counter(sol["ext"].values()))
        if len(sys.argv) > 3:
            save_plan(sol, sys.argv[3])
            print("saved", sys.argv[3])
