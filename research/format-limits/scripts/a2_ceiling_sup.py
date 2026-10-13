"""A. Format ceiling, rev. 2: the supremum over the stage count s is attained at s = 5 on both realised units.

For every odd s the root obeys X(s) <= D_s / Cost_s, Cost_s = sum over the skeleton slots of mass * ln(m / cap)
(because e^y - 1 >= y).  This script certifies D_s/Cost_s < X(5) for every odd s = 7 .. 401 with rational-interval
logarithms (cost_iv's lower end, so D/Cost is an upper bound), on the bit unit 111/63 and the complex unit 112/64.
For s >= 403 the README (section A.3) gives the analytic tail Cost_s/v >= 4a(K^2/4 - K/e - K/2), K = (s-1)/2; the
value of that bound at s = 403 is printed, and the elementary inequality sum_{p<K} p ln(K/p) >= K^2/4 - K/e - K/2
that it uses is checked numerically for K = 2 .. 5000 (its proof is in the README).
"""
import math
from fractions import Fraction as Fr

from cert import cost_iv
from report import check, finish, near
from skel import X, profile

UNITS = {'bit-111/63': (8, 63, 111), 'cx-112/64': (9, 64, 112)}
EXPECTED_WORST = {'bit-111/63': (5.231066e-3, 7), 'cx-112/64': (4.529190e-3, 7)}   # max D/Cost over s = 7..401
EXPECTED_TAIL = {'bit-111/63': 6.270e-4, 'cx-112/64': 5.438e-4}                    # analytic tail value at s = 403

for name, (h, cst, v) in UNITS.items():
    x = Fr(cst, v)
    x5 = X(5, h, 1, x)['hi']
    worst, sworst, allbelow = Fr(0), None, True
    for s in range(7, 402, 2):
        prof, m, D = profile(s, h, 1, x)
        clo, _ = cost_iv(prof, m)
        ub = D / clo
        allbelow &= ub < x5
        if ub > worst:
            worst, sworst = ub, s
    ew, es = EXPECTED_WORST[name]
    check('A2.sup.' + name, allbelow and sworst == es and abs(float(worst) / ew - 1) < 1e-6,
          'D/Cost < X(5) = %.6e for all odd s in 7..401; largest %.6e at s = %d' % (float(x5), float(worst), sworst))
    a = h - 1
    K = 201
    s = 2 * K + 1
    tail = float(1 - x) * s / (4 * a * (K * K / 4 - K / math.e - K / 2))
    check('A2.tail.' + name, tail < float(x5) and near(tail, EXPECTED_TAIL[name], 7),
          'analytic tail bound at s = 403: %.3e (decreasing in s)' % tail)
bad = [K for K in range(2, 5001) if sum(p * math.log(K / p) for p in range(1, K)) < K * K / 4 - K / math.e - K / 2]
check('A2.tail-inequality', not bad, 'sum_{p<K} p ln(K/p) >= K^2/4 - K/e - K/2 for K = 2..5000')
finish()
