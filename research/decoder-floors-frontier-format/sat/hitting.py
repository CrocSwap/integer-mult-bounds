"""C4.1 (NEWWORD c4): multi-unit puncture savings on the P112 coordinate term under ANY admissible B.  Standard library only.
R = N(f) (56 live lines non-orthogonal to a removed root f).  A kept clique C of pairwise non-orthogonal lines has B[C,C] = I for every admissible B,
so a puncture D of R (lines deleted from the support) with rank B[R\\D, R\\D] <= 8 - s keeps no (9 - s)-clique: D must hit every (9 - s)-clique of R.
f(s) = min |D| over hitting sets; 'z-1 infeasible' <=> UNSAT of 'hit all k-cliques with at most z-1 lines' (k = 9 - s), encoded with a sequential counter.
For k = 3 (s = 6) the dual form is used: no triangle-free kept set of size `keep`.   CNF text is a deterministic function of (k, z)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
from units import *

def region():
    L = sub(P112_IDX); f = F0[0]
    R = [t for t in range(len(L)) if dot(L[t], E8[f]) != 0]
    return L, R
def cliques(L, R, k):
    NO = lambda a, b: dot(L[a], L[b]) != 0
    out = []
    def ext(cur, cand):
        if len(cur) == k: out.append(cur); return
        for i, c in enumerate(cand): ext(cur + [c], [d for d in cand[i + 1:] if NO(c, d)])
    ext([], R); return out

def seqcounter_atmost(lits, bound, top):
    """Sinz sequential counter: at most `bound` of lits true; returns (clauses, new top)"""
    n = len(lits); s = [[0] * (bound + 1) for _ in range(n)]; cl = []
    for i in range(n):
        for j in range(1, bound + 1): top += 1; s[i][j] = top
    cl.append([-lits[0], s[0][1]])
    for j in range(2, bound + 1): cl.append([-s[0][j]])
    for i in range(1, n):
        cl.append([-lits[i], s[i][1]]); cl.append([-s[i - 1][1], s[i][1]])
        for j in range(2, bound + 1):
            cl.append([-lits[i], -s[i - 1][j - 1], s[i][j]]); cl.append([-s[i - 1][j], s[i][j]])
        cl.append([-lits[i], -s[i - 1][bound]])
    return cl, top

def hit_cnf(k, z):
    """UNSAT  <=>  no set of at most z lines of R meets every k-clique"""
    L, R = region(); idx = {t: i + 1 for i, t in enumerate(R)}
    C = cliques(L, R, k); cl = [[idx[t] for t in c] for c in C]
    card, top = seqcounter_atmost([idx[t] for t in R], z, len(R)); cl += card
    return top, cl, len(C)

def tri_cnf(keep):
    """UNSAT <=> no triangle-free subset of R (no three pairwise non-orthogonal lines) has `keep` lines"""
    L, R = region(); idx = {t: i + 1 for i, t in enumerate(R)}
    tris = cliques(L, R, 3); cl = [[-idx[a], -idx[b], -idx[c]] for a, b, c in tris]
    # at least `keep` kept = at most len(R)-keep dropped; encode on negated literals
    card, top = seqcounter_atmost([-idx[t] for t in R], len(R) - keep, len(R)); cl += card
    return top, cl, len(tris)

def dimacs(nv, cl): return "p cnf %d %d\n" % (nv, len(cl)) + "".join(" ".join(map(str, c)) + " 0\n" for c in cl)
