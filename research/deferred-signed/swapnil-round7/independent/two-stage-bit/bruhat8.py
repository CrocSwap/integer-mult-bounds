"""Exact Bruhat profile of S_p for data stage-2 entrance projectors p = Q_a1 (x) Q_a2 at h=8 after one S0."""
import sys, random
sys.path.insert(0, __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', 'partial-swap'))
from fractions import Fraction as Q
from factor import inv, mul, bruhat, swapmat, predicted
import corners as C
h = 8; m = h*h; trip, G, I, P, Qc = C.setup(h); v = len(trip); rng = random.Random(5)
Lw = [[Q(rng.randint(-2, 2)) if j < i else Q(int(i == j)) for j in range(m)] for i in range(m)]
Up = [[Q(rng.randint(-2, 2)) if j > i else Q(int(i == j)) for j in range(m)] for i in range(m)]
S = mul(Lw, Up); Si = inv(S); ok = 0; n = int(sys.argv[1])
for _ in range(n):
    a1, a2 = rng.randrange(v), rng.randrange(v); p = mul(mul(S, C.kron(Qc[a1], Qc[a2])), Si); k = 2*h-1
    piv, L1, Mon, L2 = bruhat(swapmat(p)); assert mul(mul(L1, Mon), L2) == swapmat(p)
    cp, *_ = bruhat([r[m-k:] for r in p[:k]], track=False)
    good = piv == predicted({l: m-k+cp[l] for l in range(k)}, m, k); ok += good
    print('pair', a1, a2, 'profile ok', good, flush=True)
print('h=8 data entrance exact Bruhat profile matches lemma: %d/%d' % (ok, n))
