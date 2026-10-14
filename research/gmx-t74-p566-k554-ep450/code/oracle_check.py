"""Independent exact oracle for the finer-constant engines (package stage).

Compares logarithm enclosures of code/fine_mercator.py and code/fine_moment.py with a separately written exact
2*atanh enclosure (N = 900 terms, width < 3^-1800) on every logarithm argument the pinned T74 complex and surcharge checks use
(73/t for t = 1..72 and 73) plus 43, 189 and 352 (the first integers on which a wrong-parity Mercator sum fails).
A valid enclosure [L, U] must satisfy L <= oracle_lower and U >= oracle_upper (so L <= ln <= U) and be tight (< 1e-200).
Also asserts the Mercator term count is even (an odd alternating partial sum lies above the log).
"""
import sys
from fractions import Fraction as F
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fine_mercator as FM, fine_moment as BF
assert (FM.LOGN - 1) % 2 == 0, 'fine_mercator must sum an even number of terms'
N = 900


def atanh2(z):
    s = 2*sum((z**(2*j+1)/(2*j+1) for j in range(N)), F(0))
    return s, s + 2*z**(2*N+1)/((2*N+1)*(1-z*z))


LN2 = atanh2(F(1, 3))


def oracle(x):
    assert x >= 1
    k = 0
    while x >= 2:
        x /= 2
        k += 1
    lo, hi = atanh2((x-1)/(x+1))
    return lo + k*LN2[0], hi + k*LN2[1]


# inner Mercator enclosures (before any outward rounding): the constants log(3/2), log(4/3) and sample reductions
for y in (F(3, 2), F(4, 3), F(5, 4), F(1), F(7, 6)):
    lo_o, hi_o = oracle(y) if y >= 1 else (None, None)
    L, U = FM.mercator(y)
    assert L <= lo_o and U >= hi_o, ('false inner Mercator enclosure', y)
inputs = [F(73, t) for t in range(1, 73)] + [F(73), F(43), F(189), F(352)]
checked = 0
for x in inputs:
    lo_o, hi_o = oracle(x)
    for name, (L, U) in (('fine_mercator', FM.logarithm(x)), ('fine_moment', BF.log_bounds(x))):
        assert L <= lo_o, ('false lower log bound', name, x)
        assert U >= hi_o, ('false upper log bound', name, x)
        assert U - L < F(1, 10**200), ('enclosure not tight', name, x)
        checked += 1
print('PASS_FINE_ENGINE_LOG_ORACLE inputs=%d enclosures=%d' % (len(inputs), checked))
