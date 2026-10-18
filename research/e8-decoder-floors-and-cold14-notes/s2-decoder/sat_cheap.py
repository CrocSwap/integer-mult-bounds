"""SAT: is there an F2 decoder of the bit E8 pattern on the live lines with n totals, of which at least n - nfull have
their sources (or readers) inside an E7 hyperplane ell^perp (pairing rank <= 7)?"""
import sys, time, itertools
import numpy as np
from pysat.solvers import Cadical153
from pysat.card import CardEnc, EncType
from geo import *
class F:
    def __init__(s): s.n = 0; s.cl = []
    def new(s): s.n += 1; return s.n
    def AND(s, a, b):
        z = s.new(); s.cl += [[-z, a], [-z, b], [z, -a, -b]]; return z
    def XOR(s, a, b):
        z = s.new(); s.cl += [[-z, a, b], [-z, -a, -b], [z, -a, b], [z, a, -b]]; return z
    def xorlist(s, l):
        acc = l[0]
        for x in l[1:]: acc = s.XOR(acc, x)
        return acc
def build(live, n, nfull, hyper='E7', fix0=True):
    v = len(live); f = F()
    al = [[f.new() for _ in range(v)] for _ in range(n)]
    be = [[f.new() for _ in range(v)] for _ in range(n)]
    for T in range(v):
        for S in range(v):
            if T == S or G[live[T], live[S]] != 0:
                acc = f.xorlist([f.AND(al[j][T], be[j][S]) for j in range(n)])
                f.cl.append([acc] if T == S else [-acc])
    # hyperplanes: E7 type, normal = root line ell; members = live lines orthogonal to ell
    Hs = [[k for k in range(v) if G[live[k], l] == 0] for l in range(NL)]
    cheap = []
    for j in range(n):
        sels = []
        for h, mem in enumerate(Hs):
            memset = set(mem)
            for side, vec in (('A', be[j]), ('R', al[j])):
                if fix0 and j == 0 and not (side == 'A' and h == 0): continue
                x = f.new(); sels.append(x)
                for k in range(v):
                    if k not in memset: f.cl.append([-x, -vec[k]])
        c = f.new(); cheap.append(c)
        f.cl.append([-c] + sels)
    if fix0: f.cl.append([cheap[0]])
    enc = CardEnc.atleast(lits=cheap, bound=n - nfull, top_id=f.n, encoding=EncType.seqcounter)
    f.n = max(f.n, enc.nv); f.cl += enc.clauses
    return f, al, be
if __name__ == '__main__':
    n, nfull = int(sys.argv[1]), int(sys.argv[2])
    P = [int(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 and sys.argv[3] else []
    live = [i for i in range(NL) if i not in P]
    f, al, be = build(live, n, nfull)
    print('vars', f.n, 'clauses', len(f.cl), flush=True)
    s = Cadical153(bootstrap_with=f.cl); t = time.time(); r = s.solve()
    print('n', n, 'nfull', nfull, 'live', len(live), 'SAT' if r else 'UNSAT', round(time.time() - t, 1), flush=True)
    if r:
        m = set(x for x in s.get_model() if x > 0)
        for j in range(n):
            R = [live[T] for T in range(len(live)) if al[j][T] in m]; A = [live[S] for S in range(len(live)) if be[j][S] in m]
            print(j, len(R), len(A), rankG_exact(R, A))
