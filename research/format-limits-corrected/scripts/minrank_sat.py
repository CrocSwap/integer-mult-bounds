"""SAT encodings for the F_2 pairing of a decoder pattern.

A pattern is a set of unordered 'off-cap' pairs {S, T} of ports and the question is whether there are words
u_T (and, in the asymmetric case, v_T) in F_2^c with
    <u_T, v_T> = 1                                (unit diagonal)
    <u_S, v_T> = <u_T, v_S> = 0   for every off-cap pair {S, T}
(symmetric case v = u).  Such words exist iff the pairing matrix B = V U^T (B_TS = <v_T, u_S>) has unit diagonal,
vanishes on the pattern, and has F_2 rank at most c; the smallest c is the F_2 'minrank' of the pattern.

Symmetry breaking.  A set K of pairwise off-cap ports has B[K,K] = I forced, so U_K and V_K are invertible; the action
(U, V) -> (U P, V P^-T) of GL(c, F_2) leaves B fixed and can bring U_K to [I_|K| | 0] and V_K to [I_|K| | 0]
(for |K| = c this is U_K = V_K = I; for |K| < c the last columns of V_K are cleared with the remaining freedom of P).
In the symmetric case O(c, F_2) is transitive on orthonormal bases, so U_K = V_K = [I | 0] as well.

solve_minrank() is the plain minrank question (gauge only when |K| = c).  solve_asym() adds the gauge for any
|K| <= c and the extra constraints 'B is not symmetric' (some free pair has B_TS != B_ST) or 'B differs from B0 =
(J + G) mod 2' (some free pair), and optionally fixes U to given labels.  The solver is Cadical 1.5.3 through pysat.
"""
import time

import numpy as np
from pysat.solvers import Cadical153


class CNF:
    def __init__(self):
        self.n = 0
        self.cl = []

    def new(self):
        self.n += 1
        return self.n

    def AND(self, a, b):
        z = self.new()
        self.cl += [[-z, a], [-z, b], [z, -a, -b]]
        return z

    def XOR(self, a, b):
        z = self.new()
        self.cl += [[-z, a, b], [-z, -a, -b], [z, -a, b], [z, a, -b]]
        return z

    def xorlist(self, lits):
        acc = lits[0]
        for l in lits[1:]:
            acc = self.XOR(acc, l)
        return acc

    def parity(self, lits, val):
        """add the constraint  xor(lits) = val."""
        if not lits:
            if val:
                self.cl.append([])
            return
        acc = self.xorlist(lits)
        self.cl.append([acc] if val else [-acc])


def build(v, offpairs, c, sym, clique):
    f = CNF()
    U = [[f.new() for _ in range(c)] for _ in range(v)]
    V = U if sym else [[f.new() for _ in range(c)] for _ in range(v)]
    for T in range(v):
        f.parity([f.AND(U[T][j], V[T][j]) for j in range(c)], 1)
    for (S, T) in offpairs:
        f.parity([f.AND(U[S][j], V[T][j]) for j in range(c)], 0)
        if not sym:
            f.parity([f.AND(U[T][j], V[S][j]) for j in range(c)], 0)
    if clique and len(clique) == c:                  # U_K V_K^T = I  =>  WLOG U_K = V_K = I
        for i, T in enumerate(clique):
            for j in range(c):
                f.cl.append([U[T][j]] if j == i else [-U[T][j]])
                if not sym:
                    f.cl.append([V[T][j]] if j == i else [-V[T][j]])
    return f


def solve_minrank(v, offpairs, c, sym, clique):
    """('SAT'|'UNSAT', seconds, variables, clauses) for words in F_2^c on the pattern."""
    f = build(v, offpairs, c, sym, clique)
    s = Cadical153(bootstrap_with=f.cl)
    t = time.time()
    r = s.solve()
    return ('SAT' if r else 'UNSAT'), round(time.time() - t, 1), f.n, len(f.cl)


def solve_asym(v, pattern, B0, c, mode, K, U_fixed=None):
    """Existence of source labels U and sink labels W (v x c over F_2), B = W U^T, with B_TT = 1, B_TS = 0 on the
    ordered pairs of `pattern`, gauge U_K = W_K = [I | 0] on the pairwise off-cap set K, and
      mode 'none'   : no further condition,
      mode 'nonsym' : B_TS != B_ST for some free pair (T, S),
      mode 'neB0'   : B_TS != B0_TS for some free pair.
    U_fixed (v x c 0/1 array) additionally fixes U (then K's gauge is dropped).  Returns a dict with the result and,
    when satisfiable, the pairing B = W U^T and its F_2 rank."""
    f = CNF()
    U = [[f.new() for _ in range(c)] for _ in range(v)]
    W = [[f.new() for _ in range(c)] for _ in range(v)]
    Bvar = {}

    def B(T, S):
        if (T, S) not in Bvar:
            Bvar[(T, S)] = f.xorlist([f.AND(W[T][j], U[S][j]) for j in range(c)])
        return Bvar[(T, S)]
    for T in range(v):
        f.cl.append([B(T, T)])
    for (T, S) in pattern:
        f.cl.append([-B(T, S)])
    if U_fixed is not None:
        for T in range(v):
            for j in range(c):
                f.cl.append([U[T][j]] if U_fixed[T][j] else [-U[T][j]])
    else:
        for i, T in enumerate(K):
            for j in range(c):
                f.cl.append([U[T][j]] if j == i else [-U[T][j]])
                f.cl.append([W[T][j]] if j == i else [-W[T][j]])
    free = [(T, S) for T in range(v) for S in range(v) if T != S and (T, S) not in pattern]
    if mode == 'nonsym':
        f.cl.append([f.XOR(B(T, S), B(S, T)) for (T, S) in free if T < S])
    elif mode == 'neB0':
        f.cl.append([B(T, S) if B0[T][S] == 0 else -B(T, S) for (T, S) in free])
    s = Cadical153(bootstrap_with=f.cl)
    t = time.time()
    r = s.solve()
    out = dict(c=c, mode=mode, result='SAT' if r else 'UNSAT', sec=round(time.time() - t, 1), vars=f.n, clauses=len(f.cl))
    if r:
        m = set(x for x in s.get_model() if x > 0)
        Uv = np.array([[1 if U[T][j] in m else 0 for j in range(c)] for T in range(v)], dtype=np.int64)
        Wv = np.array([[1 if W[T][j] in m else 0 for j in range(c)] for T in range(v)], dtype=np.int64)
        out['B'] = (Wv @ Uv.T) % 2
        out['U'], out['W'] = Uv, Wv
    return out
