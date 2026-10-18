"""Re-price a gauge44 global profile with mpmath interval arithmetic (no shared moment engine).

Usage: price.py PLAN.json LOCAL-PROFILE-JSON BIT-C B-LOWER KAPPA
Checks: PLAN profile = 72 * local + idle remainder, rank deficit, the moment sign at both
certificate endpoints, and the closed-form kappa grid step from (b, c).
"""
import json, sys
from fractions import Fraction as Q
from mpmath import iv, mpf

iv.prec = 400
plan, local, c, b, kappa = json.load(open(sys.argv[1])), json.loads(sys.argv[2]), Q(sys.argv[3]), Q(sys.argv[4]), Q(sys.argv[5])
H = {int(r): n for r, n in plan['profile'].items()}
m, W = plan['M'], plan['live']
idle = {r: H.get(r, 0) - 72 * local.get(str(r), 0) for r in H}
assert all(x >= 0 for x in idle.values()), idle
assert m * W - sum(r * n for r, n in H.items()) == plan['deficit'], 'rank deficit'
print('idle remainder', {r: x for r, x in idle.items() if x})


def moment(z):  # sum_r (r n / (m W)) (m / r)^z, enclosed
    z = iv.mpf(z.numerator) / z.denominator
    return sum(iv.mpf(r * n) / (m * W) * iv.exp(z * iv.log(iv.mpf(m) / r)) for r, n in H.items())


lo, hi = moment(b), moment(b + Q(1, 10**24))
assert lo.b < 1 < hi.a, (lo, hi)
print('moment(b) - 1 <', float(lo.b - 1), '; moment(b + 1e-24) - 1 >', float(hi.a - 1))

# Closed-form kappa from (b, c): common saving s, seven bootstrap steps, eta margin, floor to 1e-18.
eta = beta = Q(1, 10**24)
s = min(c, (1 - beta) * b) - Q(1, 10**27)
a = Q(384599, 10**10)
for _ in range(7):
    a = (1 - s) * s + s * a
q = a * (1 - 2 * eta)
ticks = (1 - eta) * q / (1 + q) * 10**18
k = Q((ticks.numerator - 1) // ticks.denominator, 10**18)
assert k == kappa, (k, kappa)
print('binding', 'bit' if c < (1 - beta) * b else 'complex', 'kappa', k, float(k))
print('PASS')
