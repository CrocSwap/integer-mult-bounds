"""Independent exact oracle for the finer-constant engines (package stage).

Compares logarithm enclosures of code/fine_mercator.py and code/fine_moment.py with a separately written exact
2*atanh enclosure (integer fixed point 128 bits finer than the engines, directed rounding) on every logarithm argument the pinned T74 complex and surcharge checks use
(73/t for t = 1..72 and 73) plus 43, 189 and 352 (the first integers on which a wrong-parity Mercator sum fails).
A valid enclosure [L, U] must satisfy L <= oracle_lower and U >= oracle_upper (so L <= ln <= U) and be tight (width below 2^-(bits-40) resp. 2^-(grid bits-40)).
Also asserts the Mercator term count is even (an odd alternating partial sum lies above the log).
"""
import sys
from fractions import Fraction as F
try:
    from gmpy2 import mpz   # optional accelerator, identical results
except ImportError:
    mpz = int
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fine_mercator as FM, fine_moment as BF
assert (FM.LOGN - 1) % 2 == 0, 'fine_mercator must sum an even number of terms'
# Exact 2*atanh enclosure in directed-rounding integer fixed point on a 2^-OB grid (OB = max engine bits + 128, strictly finer than both engines);
# N terms with 3^-2N below 2^-OB, tail bounded by the geometric series. Written separately from both engines.
OB = max(FM.DYAD.bit_length(), BF.GRID.bit_length()) - 1 + 128
N = int(OB / 3.1699) + 20
ONE = 1 << OB


def atanh2(z):
    p, q = mpz(z.numerator), mpz(z.denominator)
    p2, q2 = p*p, q*q
    pl = ONE*p//q
    ph = -((-ONE*p)//q)
    sl = sh = mpz(0)
    for j in range(N):
        sl += pl//(2*j+1)
        sh += -((-ph)//(2*j+1))
        pl = pl*p2//q2
        ph = -((-ph*p2)//q2)
    tail = -((-2*ph*q2)//((2*N+1)*(q2-p2)))
    return F(int(2*sl), ONE), F(int(2*sh + tail), ONE)


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
tight = {'fine_mercator': F(1, 2**(FM.DYAD.bit_length() - 1 - 40)), 'fine_moment': F(1, 2**(BF.GRID.bit_length() - 1 - 40))}
inputs = [F(73, t) for t in range(1, 73)] + [F(73), F(43), F(189), F(352)]
checked = 0
for x in inputs:
    lo_o, hi_o = oracle(x)
    for name, (L, U) in (('fine_mercator', FM.logarithm(x)), ('fine_moment', BF.log_bounds(x))):
        assert L <= lo_o, ('false lower log bound', name, x)
        assert U >= hi_o, ('false upper log bound', name, x)
        assert U - L < tight[name], ('enclosure not tight', name, x)
        checked += 1
print('PASS_FINE_ENGINE_LOG_ORACLE inputs=%d enclosures=%d' % (len(inputs), checked))
