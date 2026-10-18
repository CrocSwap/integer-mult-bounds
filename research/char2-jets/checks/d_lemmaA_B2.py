"""Lemma A (T = 2) as a corollary of CR2, and spot checks of Theorem B2.
Lemma A: a configuration in P^1 (p(t), q(s) in Z^2, p(t).q(t) != 0).  The finitely many points p(t) and perp(q(s)) = (q2, -q1) of P^1(Q) are mapped injectively into P^1(GF(2^k)) fixing
[1:0] and [0:1]; the image vectors are a CR2 realisation (incidence <=> equality of points, preserved by injectivity; diagonal <=> inequality, preserved too).  Verified exactly for random
configurations (and for random admissible B: N = sum_j D(p~_j) B D(q~_j) is diagonal with non-zero diagonal).
B2: for random no-wild configurations, phi (phi(-1) = 1, phi(prime) = random element of GF(2^16)*) preserves every incidence of the blocks, its diagonal vanishes exactly on the harmonic
lines H, and the exhaustive minimum cost (C program enumall, f <= 20) is >= v - |H|."""
import random, collections, sys
from fractions import Fraction
from common import *
from kit import *; from phi import *; from gen import randcfg
from gr import mul
def gfmul(a, b, k, m):
    r = 0
    while b:
        if b & 1: r ^= a
        b >>= 1; a <<= 1
        if a >> k & 1: a ^= m
    return r
IR = {4: 0b10011, 6: 0b1000011}
random.seed(3); okA = 0; nA = 60
for it in range(nA):
    v = random.randint(3, 9); pts = [(1, 0), (0, 1)] + [(random.choice([1, 2, 3, -1, -2]), random.choice([1, 2, 3, -1, -2, 5])) for _ in range(5)]
    P = [list(random.choice(pts)) + [0] for _ in range(v)]; Q = []
    for t in range(v):
        while True:
            q = [random.randint(-3, 3), random.randint(-3, 3), 0]
            if (q[0] or q[1]) and P[t][0] * q[0] + P[t][1] * q[1] != 0: Q.append(q); break
    norm = lambda x, y: Fraction(y, x) if x else None      # P^1(Q) point [x:y] -> y/x, infinity -> None
    perp = lambda q: (q[1], -q[0])                         # p.q = 0 iff p ~ perp(q)
    used = {norm(*p[:2]) if p[0] else 'inf' for p in P} | {norm(*perp(q)) if perp(q)[0] else 'inf' for q in Q}
    k = 6; vals = [z for z in used if z not in ('inf', 0)]; assert len(vals) < (1 << k) - 1
    img = {'inf': None, 0: 0}; nxt = iter(range(1, 1 << k))
    for z in vals: img[z] = next(nxt)
    def vec(p):                                           # image of point p of P^1(Q) as a vector of GF(2^k)^2
        if p[0] == 0: return [0, 1]
        z = Fraction(p[1], p[0]); return [1, img[z]]       # z = 0 -> [1:0]
    Pt = [vec(p) + [0] for p in P]
    # line vector q~ = perp of the image point; in char 2 perp(x, y) = (y, x)
    Qt = [[vec(perp(q))[1], vec(perp(q))[0], 0] for q in Q]
    R, A, free = setup(P, Q); pi = [{j for j in range(3) if P[t][j]} for t in range(v)]; sig = [{j for j in range(3) if Q[t][j]} for t in range(v)]
    dotk = lambda a, b: gfmul(a[0], b[0], k, IR[k]) ^ gfmul(a[1], b[1], k, IR[k])
    s_ok = all(Pt[t][j] == 0 for t in range(v) for j in range(3) if j not in pi[t]) and all(Qt[t][j] == 0 for t in range(v) for j in range(3) if j not in sig[t])
    good = s_ok and all(dotk(Pt[t], Qt[s]) == 0 for (t, s) in free) and all(dotk(Pt[t], Qt[t]) != 0 for t in range(v))
    for _ in range(5):
        B = tomat(random.getrandbits(len(free)), free, v)
        N = [[(dotk(Pt[t], Qt[s]) if B[t][s] else 0) for s in range(v)] for t in range(v)]
        good = good and all((N[t][s] == 0) == (t != s) for t in range(v) for s in range(v)) and sum(blockranks(B, R, A)) >= v
    okA += good
report('A Lemma A (T=2): explicit injection P^1(Q) -> P^1(GF(2^6)) realises the full pattern; N diagonal; cost >= v', okA == nA, '%d/%d random T=2 configurations' % (okA, nA))
random.seed(5); st = collections.Counter(); nB = int(sys.argv[1]) if len(sys.argv) > 1 else 80
def nowild_cfg(v, R):
    while True:
        P, Q = randcfg(v, R=R)
        w, H = classify(P, Q)
        if w == 0: return P, Q
for it in range(nB):
    v = random.randint(5, 9); P, Q = nowild_cfg(v, random.choice([1, 2, 3]))
    w, H = classify(P, Q); R, A, free = setup(P, Q)
    phi = make_phi(random.Random(it)); Pt = [[phi(x) for x in p] for p in P]; Qt = [[phi(x) for x in q] for q in Q]
    st['inc'] += all(dot2(Pt[t], Qt[s]) == 0 for (t, s) in free)
    st['diag0==H'] += [t for t in range(v) if dot2(Pt[t], Qt[t]) == 0] == H
    if len(free) <= 20:
        best, ms = enum_raw(v, R, A, free, 0); st['n_exh'] += 1; st['cost>=v-|H|'] += best >= v - len(H)
        st['H>0'] += len(H) > 0
report('B2 phi preserves all incidences, zero diagonals = H exactly, on %d random no-wild configurations' % nB, st['inc'] == nB and st['diag0==H'] == nB, str(dict(st)))
report('B2 exhaustive min cost >= v - |H| on the %d of them with f <= 20 (%d with |H| > 0)' % (st['n_exh'], st['H>0']), st['n_exh'] > 0 and st['cost>=v-|H|'] == st['n_exh'])
done()
