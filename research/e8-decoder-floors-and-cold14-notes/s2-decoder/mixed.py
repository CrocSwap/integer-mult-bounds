"""General bit-unit evaluator: ports with Q-vectors lam (rows), F2 labels u (ints, c bits).  Checks the label decoder
pattern (<u_T,u_S>=0 when <lam_T,lam_S>!=0, <u_T,u_T>=1) and returns the min star cost over label decoders
(min-weight basis of the label space under s(q) = dim span{lam_S : <u_S,q>=1}), and window h."""
import numpy as np
def dot(a, b): return bin(a & b).count('1') & 1
def check_pattern(lam, u):
    Gm = lam @ lam.T
    n = len(u)
    for i in range(n):
        if dot(u[i], u[i]) != 1: return False, ('diag', i)
        for j in range(i + 1, n):
            if Gm[i, j] != 0 and dot(u[i], u[j]) != 0: return False, ('pair', i, j)
    return True, None
def star_cost(lam, u, cbits=9):
    lamf = lam.astype(float)
    s = {}
    for q in range(1, 1 << cbits):
        idx = [i for i in range(len(u)) if dot(u[i], q)]
        s[q] = int(np.linalg.matrix_rank(lamf[idx])) if idx else 0
    # min weight basis of the span of the labels' dual... decoder: I_c = sum p_j q_j^T requires q's to span F2^c;
    # but only the label span matters: restrict to q modulo span(u)^perp -> use greedy on all q, need rank = dim span(u)
    span_dim = len(basis_of(u))
    order = sorted(s, key=lambda q: (s[q], q))
    # the decoder needs q_1..q_r whose restrictions to span(u) are a basis of its dual: i.e. the matrix [<u_T,q_j>]
    # has F2 rank r = dim span(u).  Greedy on the vectors (<u_T,q>)_T.
    basis, chosen = [], []
    for q in order:
        vec = sum(dot(u[i], q) << i for i in range(len(u)))
        x = vec
        for b in sorted(basis, reverse=True):
            x = min(x, x ^ b)
        if x:
            basis.append(x); chosen.append(q)
            if len(chosen) == span_dim: break
    return sum(s[q] for q in chosen), chosen, span_dim
def basis_of(vs):
    b = []
    for x in vs:
        for y in sorted(b, reverse=True): x = min(x, x ^ y)
        if x: b.append(x)
    return b
