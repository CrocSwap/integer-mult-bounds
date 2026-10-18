# SPDX-License-Identifier: Apache-2.0
"""Exact window-respecting optimum of k width-7 helpers per call on the PR589 nine-stage bit hosting.

Per replica: 9 idle children with 222 copies each, capacities and one-level windows from windows.py,
and per stage 439-k width-8 plus k width-7 residuals. The cost of a copy with r unused units is
F_a(r) = r (64/r)^a + 32*64^2*64^a/1e16 for r > 0 (the moment term plus the inherited bad-residue
surcharge) and 0 for r = 0. solve(k, a) returns an exact integer lower bound (units 2^-200, x5) of
the minimum total cost over all window-feasible placements, the minimising width-7 distribution and,
on request, an explicit plan attaining it. The proof steps (Lemma A, interval Hall reduction to two
nested chains, slack decomposition, DP relaxation) are written out in README.md; the code asserts the
checked facts for each k. Uses the merged PR1023 packing.py only for the pinned moment engine.
"""
import importlib.util
import sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import windows  # noqa: E402


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


P = _load('pr1023_packing', ROOT / 'research/bit589-width-packing/packing.py')
MOM = P.MOMENT
WIN = windows.checked_windows()
M, N, T, STG, R = 64, 222, 32, 9, 439
CAP = {i: WIN[i][0] for i in WIN}
SEVEN = [i for i in WIN if CAP[i] == 7]                      # 1, 3, 5
REST = [i for i in WIN if CAP[i] != 7]                       # 0, 2, 4, 6, 7, 8
SHIFT = 1 << 200

def Ftilde(a):
    """integer lower bounds of F_a(r) = r (64/r)^a + 32*64^2*64^a/1e16 (r>0), F(0)=0, in units 2^-200"""
    out = [0]
    l, _ = MOM.logarithm(Q(M)); e64, _ = MOM.exponential(a * l, a * MOM.logarithm(Q(M))[1])
    lam = Q(32 * M * M, 10 ** 16) * e64
    for r in range(1, 43):
        lo, hi = MOM.logarithm(Q(M, r)); e, _ = MOM.exponential(a * lo, a * hi)
        x = (r * e + lam) * SHIFT
        out.append(x.numerator // x.denominator)
    return out

def types(c):
    m, f = c % 8, c // 8
    w7 = [(l, b, m + 8 * l - 7 * b) for l in range(f + 1) for b in range(1, 7) if m + 8 * l - 7 * b >= 0]
    p8 = [(l, m + 8 * l) for l in range(1, f + 1)]
    return m, f, w7, p8

def V_table(F, Smax):
    INF = None; V = [0] + [INF] * Smax; bp = [None] * (Smax + 1)
    moves = [(c, l, F[r] - F[c % 8]) for c in (14, 28, 42) for (l, r) in types(c)[3]]
    for S in range(1, Smax + 1):
        for c, l, d in moves:
            if l <= S and V[S - l] is not None:
                v = V[S - l] + d
                if V[S] is None or v < V[S]: V[S] = v; bp[S] = (c, l)
    return V, bp

def knap(F, c, A, Bmax):
    m, f, w7, _ = types(c)
    E = [[None] * 5 for _ in range(Bmax + 1)]; bp = [[None] * 5 for _ in range(Bmax + 1)]
    E[0][0] = 0
    for B in range(1, Bmax + 1):
        for (l, b, r) in w7:
            if b > B: continue
            cost = 5 * (F[r] - F[m]) - l * A
            for rho in range(5):
                prev = E[B - b][(rho - l) % 5]
                if prev is None: continue
                v = prev + cost
                if E[B][rho] is None or v < E[B][rho]: E[B][rho] = v; bp[B][rho] = (l, b, r)
    return E, bp

def chain_constraints(k):
    """all 45 interval Hall constraints for the width-7 roles of children REST after the 7-slots take stages 2,4,6"""
    supply = {s: (0 if s in (2, 4, 6) else k) for s in range(STG)}
    cons = []
    for lo in range(STG):
        for hi in range(lo, STG):
            C = frozenset(i for i in REST if set(WIN[i][1]) <= set(range(lo, hi + 1)))
            cons.append((C, sum(supply[s] for s in range(lo, hi + 1))))
    return cons

LEFT, RIGHT = (0, 2, 4), (8, 7, 6)
def check_chain_reduction(k):
    cons = chain_constraints(k)
    best = {}
    for C, s in cons:
        best[C] = min(s, best.get(C, s))
    lb = [best.get(frozenset(LEFT[:j]), None) for j in range(4)]
    rb = [best.get(frozenset(RIGHT[:j]), None) for j in range(4)]
    assert lb[1:] == [2 * k, 3 * k, 4 * k] and rb[1:] == [2 * k, 3 * k, 4 * k], (lb, rb)
    assert best[frozenset(REST)] == 6 * k
    for C, s in best.items():
        jl = max(j for j in range(4) if frozenset(LEFT[:j]) <= C); jr = max(j for j in range(4) if frozenset(RIGHT[:j]) <= C)
        assert C == frozenset(LEFT[:jl]) | frozenset(RIGHT[:jr]), C
        bl = 0 if jl == 0 else lb[jl]; br = 0 if jr == 0 else rb[jr]
        assert bl + br <= s or s >= 6 * k, (C, s)
    return True

def solve(k, a, want_plan=False):
    F = Ftilde(a)
    S0 = 45 + 9 * k
    V, vbp = V_table(F, max(S0, 10))
    A = F[42] - F[2]
    for S in range(S0 + 1):
        assert V[S] == (S // 5) * A + V[S % 5], ('V not periodic', S)
    R5 = [5 * V[t] - t * A for t in range(5)]
    check_chain_reduction(k)
    E = {c: knap(F, c, A, 4 * k) for c in (14, 28, 42)}
    bound = {0: 2 * k, 2: 3 * k, 4: 4 * k, 8: 2 * k, 7: 3 * k, 6: 4 * k}
    def chain(order):
        tab = {(0, 0): (0, ())}
        for i in order:
            Ec = E[CAP[i]][0]; new = {}
            for (Pp, rp), (v, hist) in tab.items():
                for B in range(0, bound[i] - Pp + 1):
                    for rho in range(5):
                        e = Ec[B][rho]
                        if e is None: continue
                        key = (Pp + B, (rp + rho) % 5); val = v + e
                        if key not in new or val < new[key][0]: new[key] = (val, hist + ((i, B, rho),))
            tab = new
        return tab
    Lt, Rt = chain(LEFT), chain(RIGHT)
    best = None
    for (pl, rl), (vl, hl) in Lt.items():
        for rr in range(5):
            if (6 * k - pl, rr) not in Rt: continue
            vr, hr = Rt[(6 * k - pl, rr)]
            t = (S0 - rl - rr) % 5
            v = vl + vr + R5[t]
            if best is None or v < best[0]: best = (v, hl + hr, t)
    const5 = 5 * N * sum(F[CAP[i] % 8] for i in WIN) + 15 * k * (F[0] - F[7]) + S0 * A
    total5 = const5 + best[0]
    plan = None
    if want_plan:
        copies = {i: [] for i in WIN}
        for i in SEVEN: copies[i] = [(0, 1, 0)] * k
        lam = 0
        for i, B, rho in best[1]:
            bp = E[CAP[i]][1]; b_, r_ = B, rho
            while b_:
                l, b, r = bp[b_][r_]; copies[i].append((l, b, r)); b_ -= b; r_ = (r_ - l) % 5; lam += l
            assert r_ == 0
        S = S0 - lam
        assert S >= 0 and S % 5 == best[2]
        moves = [(42, 5)] * (S // 5); t = S % 5
        while t:
            c, l = vbp[t]; moves.append((c, l)); t -= l
        plan = dict(copies=copies, pure8=moves, S=S, lam=lam)
    return total5, best, plan, F

