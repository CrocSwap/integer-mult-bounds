#!/usr/bin/env python3
"""Optional third implementation (about 4-5 minutes): Python's decimal ln/exp at 10,060 digits.

Checks that decimal's ln(73/r) lies inside each verify.py log enclosure at the
PR1928 precision, and that decimal gives the same four moment signs. decimal
rounds to nearest, so this is corroboration, not a certificate; verify.py is
the certificate. Aaron Wang, with help from opencode. Apache-2.0.
"""
from decimal import Decimal, getcontext
from fractions import Fraction as Q
import verify as V

getcontext().prec = 10060
src = V.load_inputs()['sources']['pr1928']
bits = V.default_bits(10000)
scale = Decimal(2) ** bits
for r, (lo, hi) in V.log_table(73, (1, 2, 3, 4, 5, 8, 48), bits).items():
    ln = (Decimal(73) / Decimal(r)).ln()
    assert Decimal(lo) / scale <= ln <= Decimal(hi) / scale, r
prof = {int(r): int(n) for r, n in src['global_profile'].items()}
W, N = int(src['live']), sum(prof.values())


def moment_minus_one(x, surcharge):
    x = Decimal(x.numerator) / Decimal(x.denominator)
    s = sum(Decimal(r * n) / Decimal(73 * W) * (x * (Decimal(73) / Decimal(r)).ln()).exp() for r, n in prof.items())
    if surcharge:
        s += Decimal(32 * 73 * N) / (Decimal(10) ** 16 * W) * (x * Decimal(73).ln()).exp()
    return s - 1


g = Q(1, 10 ** 10000)
for field, surcharge in (('complex_lower', False), ('conservative_complex_lower', True)):
    e = Q(src[field])
    assert moment_minus_one(e, surcharge) < 0 < moment_minus_one(e + g, surcharge), field
print('PASS_DECIMAL_CROSSCHECK | 7 log enclosures | 4 moment signs agree')
