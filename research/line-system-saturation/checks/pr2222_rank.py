"""Maintainer correction (PR2222 classification): on the norm-six shell the 48 linear
features are combinations of the cubic ones, x_i = (1/6) * sum_j x_i * x_j**2, so the
cubic-plus-linear feature matrix has rank <= binom(50, 3) = 19,600 < 19,648 terms.

Exact checks (stdlib only):
  1. binom(50,3) = 19,600 and binom(50,3) + 48 = 19,648.
  2. The identity holds symbolically: sum_j x_i x_j^2 = x_i * N(x), with N(x) = sum_j x_j^2 = 6
     on the shell (checked as a polynomial identity on random integer vectors of every norm,
     and as the stated identity on vectors of norm 6 in Z^48 and in (1/2)Z^48 of the D-type form).
  3. Consequence: each linear feature lies in the span of the cubic monomial features
     x_i x_j^2 (j = 1..48), which are among the binom(50,3) degree-3 monomials in 48 variables.
"""
import math, random
from fractions import Fraction as F

assert math.comb(50, 3) == 19600 and math.comb(50, 3) + 48 == 19648
assert math.comb(48 + 2, 3) == 19600          # degree-3 monomials in 48 variables

rng = random.Random(2222)
for _ in range(2000):                          # polynomial identity sum_j x_i x_j^2 = x_i N(x)
    x = [rng.randint(-5, 5) for _ in range(48)]
    N = sum(v * v for v in x)
    for i in range(48):
        assert sum(x[i] * v * v for v in x) == x[i] * N

def norm6_vectors(k):
    """Random vectors of squared norm 6 in Z^48 (patterns 2,1,1 / 1^6) and half-integral (±1/2)^24."""
    out = []
    for _ in range(k):
        x = [F(0)] * 48
        kind = rng.randrange(3)
        if kind == 0:
            idx = rng.sample(range(48), 3); x[idx[0]] = F(rng.choice([-2, 2]))
            for j in idx[1:]: x[j] = F(rng.choice([-1, 1]))
        elif kind == 1:
            for j in rng.sample(range(48), 6): x[j] = F(rng.choice([-1, 1]))
        else:
            for j in rng.sample(range(48), 24): x[j] = F(rng.choice([-1, 1]), 2)
        assert sum(v * v for v in x) == 6
        out.append(x)
    return out

for x in norm6_vectors(3000):
    for i in range(48):
        assert x[i] == F(1, 6) * sum(x[i] * v * v for v in x)

print("PASS pr2222_rank: binom(50,3)=19600 < 19648; x_i = (1/6) sum_j x_i x_j^2 on norm-6 vectors (exact)")
