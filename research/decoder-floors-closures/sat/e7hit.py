"""E7 (the 63 lines orthogonal to line 0) : the orthogonal 7-frames and 'hit every frame with at most z lines'.  PUNCTTHEORY (D5): min hitting set = 10.
CNF text is a deterministic function of z.  UNSAT(z = 9) <=> no 9 lines of E7 meet all 135 orthogonal 7-frames; SAT(z = 10).  Standard library only."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
from units import *
def seqcounter_atmost(lits, bound, top):
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
def frames7():
    E = E7_IDX; adj = [sum(1 << j for j, s in enumerate(E) if s != t and orth(t, s)) for t in E]
    out = []
    def ext(cur, cand, last):
        if len(cur) == 7: out.append(tuple(cur)); return
        m = cand >> (last + 1) << (last + 1)
        while m:
            low = m & -m; i = low.bit_length() - 1; m ^= low
            ext(cur + [i], cand & adj[i], i)
    ext([], (1 << len(E)) - 1, -1)
    return out
def cnf(z):
    F = frames7(); cl = [[i + 1 for i in f] for f in F]
    card, top = seqcounter_atmost(list(range(1, 64)), z, 63)
    return top, cl + card, len(F)
def dimacs(nv, cl): return "p cnf %d %d\n" % (nv, len(cl)) + "".join(" ".join(map(str, c)) + " 0\n" for c in cl)
