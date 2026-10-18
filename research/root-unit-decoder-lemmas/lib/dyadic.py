"""The dyadic exact decoder of a root unit: M = G = P Q^T with n = rank_Q G totals, P = coordinates of the lines in a basis of n lines,
Q = P C (C the Gram matrix of the basis).  Entries are exact Fractions with denominators dividing 4."""
import numpy as np
from fractions import Fraction as F
def dyadic_decoder(L):
    G = np.rint(L @ L.T).astype(int); v = len(L); idx = []
    for i in range(v):
        if np.linalg.matrix_rank(L[idx + [i]]) > len(idx): idx.append(i)
    X = np.linalg.lstsq(L[idx].T, L.T, rcond=None)[0].T
    C = np.rint(L[idx] @ L[idx].T).astype(int)
    P = [[F(round(x * 4), 4) for x in row] for row in X]
    Q = [[sum(P[t][k] * int(C[k][j]) for k in range(len(idx))) for j in range(len(idx))] for t in range(v)]
    return G, idx, P, Q
