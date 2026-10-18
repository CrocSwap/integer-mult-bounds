"""DIMACS generators for the F2 low-rank (fitting-minrank) instances.  Standard library only.
A matrix  X = U V^T  over F2 of rank <= r is encoded with U[t][i], V[s][i] variables,  X_ts = XOR_i (U[t][i] AND V[s][i])  (Tseitin chain).
Symmetry breaking: if C is a set of rows/columns with X[C,C] = I (a clique of non-orthogonal lines for the fitting problem B, a clique of
orthogonal lines for the Gamma problem), then U[C] has rank |C|, and applying a change of basis of F2^r we may fix U[C] = [I_|C| | 0]
(and V[C] = [I | 0] too when r = |C|).  Any choice of C is valid."""
import itertools
from roots import *

class CNF:
    def __init__(self): self.nv = 0; self.cls = []
    def new(self): self.nv += 1; return self.nv
    def lowrank_entry(self, Urow, Vrow, val):
        """add: XOR_i (Urow[i] AND Vrow[i]) == val  (val in {0,1}), or, if val is a variable index, == that variable"""
        r = len(Urow); ands = []
        for i in range(r):
            a = self.new(); self.cls.extend([[-a, Urow[i]], [-a, Vrow[i]], [a, -Urow[i], -Vrow[i]]]); ands.append(a)
        cur = ands[0]
        for l in ands[1:]:
            y = self.new(); self.cls.extend([[-y, cur, l], [-y, -cur, -l], [y, -cur, l], [y, cur, -l]]); cur = y
        if val in (0, 1): self.cls.append([cur] if val else [-cur])
        else: self.cls.extend([[-cur, val], [cur, -val]])
    def dimacs(self):
        return "p cnf %d %d\n" % (self.nv, len(self.cls)) + "".join(" ".join(map(str, c)) + " 0\n" for c in self.cls)

def clique_in(adj, universe):
    """a (deterministic) large clique of the graph adj inside the bitmask `universe`, as a sorted list (any clique is a valid symmetry-breaking choice)"""
    adj2 = [a & universe for a in adj]; best = 0; bs = -1
    for c in maximal_cliques(adj2):
        if not (c & universe) == c: continue
        k = popcount(c)
        if k > bs or (k == bs and c < best): best, bs = c, k
    return bits(best)

def nonorth_graph(L):
    G = gram(L); v = len(L)
    return [sum(1 << s for s in range(v) if s != t and G[t][s] != 0) for t in range(v)]

def fitting_cnf(L, R, A, r, clique, fixV=False):
    """exists X = U V^T over F2 of rank <= r on rows R, columns A with X_tt = 1, X_ts = 0 for non-orthogonal t != s, entries on orthogonal
    pairs free?  (the fitting minrank of the block B[R,A] over all admissible B).  clique: list of lines in R cap A, pairwise non-orthogonal."""
    G = gram(L); c = CNF()
    U = {t: [c.new() for _ in range(r)] for t in R}; V = {s: [c.new() for _ in range(r)] for s in A}
    for t in R:
        for s in A:
            if t != s and G[t][s] == 0: continue
            c.lowrank_entry(U[t], V[s], 1 if t == s else 0)
    for k, t in enumerate(clique[:r]):
        for i in range(r): c.cls.append([U[t][i]] if i == k else [-U[t][i]])
        if fixV:                         # only valid when r == |clique|: X[C,C] = I = U[C] V[C]^T with U[C] = I forces V[C] = I
            assert r == len(clique)
            for i in range(r): c.cls.append([V[t][i]] if i == k else [-V[t][i]])
    c.U, c.V = U, V
    return c

def gamma_cnf(L, r, clique):
    """exists N = U V^T over F2 of rank <= r on all lines with N_tt = 1 and N_ts = 0 for ORTHOGONAL t != s (entries on non-orthogonal pairs free);
    clique: pairwise orthogonal lines (N[C,C] = I)."""
    G = gram(L); v = len(L); c = CNF()
    U = [[c.new() for _ in range(r)] for _ in range(v)]; V = [[c.new() for _ in range(r)] for _ in range(v)]
    for t in range(v):
        for s in range(v):
            if t != s and G[t][s] != 0: continue
            c.lowrank_entry(U[t], V[s], 1 if t == s else 0)
    for k, t in enumerate(clique[:r]):
        for i in range(r): c.cls.append([U[t][i]] if i == k else [-U[t][i]])
    c.U, c.V = U, V
    return c

def joint_cnf(L, terms, caps):
    """exists an admissible B (B_tt = 1, B_ts = 0 on non-orthogonal pairs, free variables on orthogonal pairs, SHARED by all terms) with
    rank B[R_j, A_j] <= caps[j] for every j.  Returns (cnf, bvars)."""
    G = gram(L); v = len(L); c = CNF(); bvar = {}
    nog = nonorth_graph(L)
    for (R, A), r in zip(terms, caps):
        D = sorted(set(R) & set(A)); C = clique_in(nog, sum(1 << t for t in D)) if D else []
        U = {t: [c.new() for _ in range(r)] for t in R}; V = {s: [c.new() for _ in range(r)] for s in A}
        for k, t in enumerate(C[:r]):
            for i in range(r): c.cls.append([U[t][i]] if i == k else [-U[t][i]])
        for t in R:
            for s in A:
                if t == s: c.lowrank_entry(U[t], V[s], 1)
                elif G[t][s] != 0: c.lowrank_entry(U[t], V[s], 0)
                else:
                    if (t, s) not in bvar: bvar[t, s] = c.new()
                    c.lowrank_entry(U[t], V[s], bvar[t, s])
    return c, bvar
