# QZBUILD exact checker (own code, independent of qz1): replays a C1-schema caller over Q(i)[D] at q in {1,-1,i,-i}
# (= Legal over Q(i)[q]/(q^4-1)[D] by CRT), symbolic D; counts Iota columns at q=1,D=1; computes cHat(.99).
import sys, json
from fractions import Fraction as Fr
class G:  # Gaussian rational
    __slots__ = ('r', 'i')
    def __init__(s, r, i=Fr(0)): s.r = Fr(r); s.i = Fr(i)
    def __add__(s, o): return G(s.r+o.r, s.i+o.i)
    def __sub__(s, o): return G(s.r-o.r, s.i-o.i)
    def __mul__(s, o): return G(s.r*o.r - s.i*o.i, s.r*o.i + s.i*o.r)
    def iszero(s): return s.r == 0 and s.i == 0
    def __eq__(s, o): return s.r == o.r and s.i == o.i
    def __repr__(s): return '%s+%si' % (s.r, s.i)
ONE = G(1); ZERO = G(0); IU = G(0, 1)
def qpow(q, e):
    x = ONE
    for _ in range(e % 4): x = x*q
    return x
def radd(A, B, c):  # A += c*B  (rows as dict (col, mono) -> G)
    for key, v in B.items():
        x = A.get(key, ZERO) + c*v
        if x.iszero(): A.pop(key, None)
        else: A[key] = x
def rscale(A, c):
    if c.iszero(): A.clear(); return
    for key in list(A): A[key] = A[key]*c
def rmono(A, S, k):
    out = {}
    for (col, mono), v in A.items():
        m = list(mono)
        for t in S: m[t] += 1
        out[(col, tuple(m))] = v
    return out
def replay(C, q):
    n, k = C['roles'], C['stages']; z = tuple([0]*k)
    R = [{(r, z): ONE} for r in range(n)]
    for e in C['events']:
        op = e[0]
        if op == 'ADD': radd(R[e[1]], R[e[2]], G(Fr(e[3])))
        elif op == 'SCALE': rscale(R[e[1]], G(Fr(e[2])))
        elif op == 'LAMBDA':
            s = e[2]; c = (G(1, s) + G(1, -s)*q*q)*G(Fr(1, 2)); rscale(R[e[1]], c)
        elif op == 'IDLE_ONE': R[e[1]] = rmono(R[e[1]], [x-1 for x in e[2]], k)
        elif op == 'HOST':
            t, s, d, a, b = e[1]-1, e[2], e[3], G(Fr(e[4])), G(Fr(e[5]))
            rs, rd = R[s], R[d]
            ns = dict(rs); radd(ns, rd, a*q)
            nd = {}; radd(nd, rs, b*qpow(q, 3)); radd(nd, rd, ONE + a*b)
            R[s] = rmono(ns, [t], k); R[d] = rmono(nd, [t], k)
        else: raise ValueError(op)
    return R
def target(C, q):
    k = C['stages']; out = []
    for r, dg in enumerate(C['diagonal']):
        mono = tuple(dg[2:2+k]); out.append({(r, mono): qpow(q, dg[0])})
    return out
def legal(C):
    ok = True
    for q in (ONE, G(-1), IU, G(0, -1)):
        R = replay(C, q); T = target(C, q)
        good = all(R[r] == T[r] for r in range(C['roles']))
        ok &= good
    hs = [e for e in C['events'] if e[0] == 'HOST']
    wf = all(e[2] != e[3] for e in hs) and all(Fr(e[4]) != 0 and Fr(e[5]) != 0 for e in hs)
    return ok, wf
S_ = 0.99
def chat(C):
    k = C['stages']
    masks = [sum(dg[2:2+k]) for dg in C['diagonal']]
    inv = sum((8*D+1)**S_ for D in masks) - sum((8*len(e[2]))**S_ for e in C['events'] if e[0] == 'IDLE_ONE') - 2*k*8**S_
    return 104*inv/k
def HP(k): return 208/k*((k-2)*(17**S_-16**S_) + (8*k+1)**S_ - 8**S_*k)
if __name__ == '__main__':
    for f in sys.argv[1:]:
        C = json.load(open(f)); ok, wf = legal(C)
        k = C['stages']; n = C['roles']
        print(f.split('/')[-1], 'n', n, 'k', k, 'events', len(C['events']), 'LEGAL(4 q, symbolic D):', ok, 'WF(hosts distinct, a,b!=0):', wf,
              'degrees', sorted(sum(dg[2:2+k]) for dg in C['diagonal']), 'cHat %.4f' % chat(C), 'HP %.4f' % HP(k), flush=True)
