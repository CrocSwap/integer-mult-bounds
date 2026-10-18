"""Generalised label decoders on a 9-line puncture P whose labels are a basis D: Binv = B_D^{-1} = sum_j x_j y_j^T over F2
(p_j = D x_j readers, q_j = D y_j sources... in D-coordinates).  Term cost (pairing rank, Theorem C):
  8 generic; 7 if x_j or y_j is a unit vector; 6 if x_j = e_a, y_j = e_b, a != b, y_a orth y_b (lines).
Star cost: 7 if y_j unit else 8.  Modes: 'thmc' (free), 'chain' (all x-unit terms share one a), 'star'."""
import sys, numpy as np, sympy, itertools
from ortools.sat.python import cp_model
from geo import *
def binv(P):
    BD = sympy.Matrix(B0[np.ix_(P, P)].tolist())
    if BD.det() % 2 == 0: return None
    return np.array(BD.inv_mod(2).tolist(), dtype=int)
def solve(P, n=9, mode='thmc', tl=60):
    Bi = binv(P); k = len(P)
    orth = [[G[P[a], P[b]] == 0 and a != b for b in range(k)] for a in range(k)]
    m = cp_model.CpModel()
    X = [[m.NewBoolVar('') for j in range(n)] for r in range(k)]
    Y = [[m.NewBoolVar('') for j in range(n)] for r in range(k)]
    A = {}
    for r in range(k):
        for c in range(k):
            ands = []
            for j in range(n):
                a = m.NewBoolVar(''); m.AddMultiplicationEquality(a, [X[r][j], Y[c][j]]); ands.append(a)
            if Bi[r, c]: m.AddBoolXOr(ands)
            else:
                t = m.NewBoolVar(''); m.AddBoolXOr(ands + [t])   # xor(ands) xor t = 1 -> xor(ands) = not t ; force t = 1
                m.Add(t == 1)
    cost = []
    unitx_a = {}
    for j in range(n):
        sx = sum(X[r][j] for r in range(k)); sy = sum(Y[r][j] for r in range(k))
        used = m.NewBoolVar(''); m.Add(sx >= 1).OnlyEnforceIf(used); m.Add(sx == 0).OnlyEnforceIf(used.Not())
        m.Add(sy >= 1).OnlyEnforceIf(used); m.Add(sy == 0).OnlyEnforceIf(used.Not())
        ux = m.NewBoolVar(''); m.Add(sx == 1).OnlyEnforceIf(ux); m.Add(sx != 1).OnlyEnforceIf(ux.Not())
        uy = m.NewBoolVar(''); m.Add(sy == 1).OnlyEnforceIf(uy); m.Add(sy != 1).OnlyEnforceIf(uy.Not())
        disc = m.NewBoolVar('')
        pairs = []
        for a in range(k):
            for b in range(k):
                if orth[a][b]:
                    pv = m.NewBoolVar(''); m.AddBoolAnd([X[a][j], Y[b][j], ux, uy]).OnlyEnforceIf(pv)
                    m.AddBoolOr([X[a][j].Not(), Y[b][j].Not(), ux.Not(), uy.Not()]).OnlyEnforceIf(pv.Not())
                    pairs.append(pv)
        m.AddMaxEquality(disc, pairs) if pairs else m.Add(disc == 0)
        if mode == 'star':
            # star cost: 7 if y unit else 8
            c = m.NewIntVar(0, 8, ''); m.Add(c == 8 * used - uy)
        else:
            one = m.NewBoolVar(''); m.AddMaxEquality(one, [ux, uy])
            c = m.NewIntVar(0, 8, ''); m.Add(c == 8 * used - one - disc)
        cost.append(c)
        for a in range(k):
            v = m.NewBoolVar(''); m.AddBoolAnd([ux, X[a][j]]).OnlyEnforceIf(v)
            m.AddBoolOr([ux.Not(), X[a][j].Not()]).OnlyEnforceIf(v.Not())
            unitx_a.setdefault(a, []).append((v, uy))
    if mode == 'chain':
        # x-unit terms are read at <y_a> unless they are also y-unit with cost 7 read at 0 (column terms, star).  Require:
        # non-star x-unit terms (not y-unit) and discounted terms all share one a.
        sel = [m.NewBoolVar('') for a in range(k)]
        m.Add(sum(sel) <= 1)
        for a in range(k):
            for (v, uy) in unitx_a[a]:
                # v and not(uy) -> sel[a]  ;  discount also implies uy and v -> require sel[a] when the term is discounted
                m.AddImplication(v, sel[a]).OnlyEnforceIf(uy.Not())
        # discounted terms: force their a selected
        # (approximation: any x-unit & y-unit term with cost 6 needs sel; enforce via cost bookkeeping below)
    m.Minimize(sum(cost))
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = tl; s.parameters.num_workers = 4
    r = s.Solve(m)
    return s.StatusName(r), s.ObjectiveValue(), s.BestObjectiveBound()
if __name__ == '__main__':
    P = [39, 52, 57, 71, 76, 78, 103, 109, 114]
    for mode in ('star', 'thmc'):
        for n in (9, 10, 11):
            print(mode, n, solve(P, n, mode, tl=60), flush=True)
