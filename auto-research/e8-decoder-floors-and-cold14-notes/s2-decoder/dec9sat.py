"""Exact: on a 9-line puncture P whose labels form a basis D, is there a generalised label decoder
(I_9 = sum_j p_j q_j^T, i.e. Binv = sum_j x_j y_j^T in D-coordinates) with pairing-rank (Theorem C) cost <= budget?
Term types: '6' x=e_a, y=e_b (a != b, y_a orth y_b); '7r' x=e_a, y free; '7c' y=e_b, x free; '8' free.
For cost <= 62 only n=9 (a6 >= 1 + a8) and n=10 (a6 - a8 >= 8) are possible."""
import sys, itertools, numpy as np, sympy, time
from pysat.solvers import Cadical153
from geo import *
class F:
    def __init__(s): s.n = 0; s.cl = []
    def new(s): s.n += 1; return s.n
    def AND(s, a, b):
        z = s.new(); s.cl += [[-z, a], [-z, b], [z, -a, -b]]; return z
    def XOR(s, a, b):
        z = s.new(); s.cl += [[-z, a, b], [-z, -a, -b], [z, -a, b], [z, a, -b]]; return z
    def onehot(s, lits):
        s.cl.append(list(lits))
        for i in range(len(lits)):
            for j in range(i + 1, len(lits)): s.cl.append([-lits[i], -lits[j]])
def binv(P):
    BD = sympy.Matrix(B0[np.ix_(P, P)].tolist())
    if BD.det() % 2 == 0: return None
    return np.array(BD.inv_mod(2).tolist(), dtype=int)
def feasible(Bi, orth, types):
    k = len(Bi); f = F(); X = []; Y = []
    for t in types:
        if t == '6':
            sel = {(a, b): f.new() for a in range(k) for b in range(k) if orth[a][b]}
            f.onehot(list(sel.values()))
            x = [f.new() for _ in range(k)]; y = [f.new() for _ in range(k)]
            for (a, b), s_ in sel.items():
                for r in range(k):
                    f.cl.append([-s_, x[r]] if r == a else [-s_, -x[r]])
                    f.cl.append([-s_, y[r]] if r == b else [-s_, -y[r]])
        elif t in ('7r', '7c'):
            u = [f.new() for _ in range(k)]; f.onehot(u)
            v = [f.new() for _ in range(k)]; f.cl.append(v)
            x, y = (u, v) if t == '7r' else (v, u)
        else:
            x = [f.new() for _ in range(k)]; y = [f.new() for _ in range(k)]
            f.cl.append(x); f.cl.append(y)
        X.append(x); Y.append(y)
    for r in range(k):
        for c in range(k):
            ands = [f.AND(X[j][r], Y[j][c]) for j in range(len(types))]
            acc = ands[0]
            for a in ands[1:]: acc = f.XOR(acc, a)
            f.cl.append([acc] if Bi[r, c] else [-acc])
    s = Cadical153(bootstrap_with=f.cl); r = s.solve()
    return r
def combos(budget):
    out = []
    for n in (9, 10):
        for a6 in range(n + 1):
            for a8 in range(n + 1 - a6):
                a7 = n - a6 - a8
                if 6 * a6 + 7 * a7 + 8 * a8 <= budget:
                    for a7r in range(a7 + 1):
                        out.append(['6'] * a6 + ['7r'] * a7r + ['7c'] * (a7 - a7r) + ['8'] * a8)
    return out
def min_cost(P, budget=62):
    Bi = binv(P)
    if Bi is None: return None
    k = len(P); orth = [[G[P[a], P[b]] == 0 and a != b for b in range(k)] for a in range(k)]
    for ty in combos(budget):
        if feasible(Bi, orth, ty): return ty
    return 'none<=%d' % budget
if __name__ == '__main__':
    P = [int(x) for x in sys.argv[1].split(',')]
    t = time.time(); print(min_cost(P), round(time.time() - t, 1))
def combos_exact(budget):
    cost = {'6': 6, '7r': 7, '7c': 7, '8': 8}
    return [t for t in combos(budget) if sum(cost[x] for x in t) == budget]
def check_budget(P, budget=62, verbose=True):
    Bi = binv(P)
    k = len(P); orth = [[G[P[a], P[b]] == 0 and a != b for b in range(k)] for a in range(k)]
    for ty in combos_exact(budget):
        t = time.time(); r = feasible(Bi, orth, ty)
        if verbose: print(''.join(x[0] + (x[1] if len(x) > 1 else '') + ' ' for x in ty), r, round(time.time() - t, 1), flush=True)
        if r: return ty
    return None
