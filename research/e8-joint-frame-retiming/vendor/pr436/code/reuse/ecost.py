"""Integer step-cost tables for the search heuristics of reuse.py and retime.py.

cost(r) = r ln(m / r) (the per-child term of the linearised moment equation), scaled by 10^12 and rounded half-even
with Python's decimal module (correctly rounded natural logarithm), so every comparison made by the two stages is an
integer comparison and gives the same word on every platform.  The tables only steer the deterministic choices of the
stages; the word they produce is checked and priced exactly elsewhere.
Prepared by eumemic with Anthropic Claude assistance; Apache-2.0."""
from decimal import Decimal, localcontext, ROUND_HALF_EVEN

SCALE = 10 ** 12


def table(m, rmax):
    out = [0] * (rmax + 1)
    with localcontext() as ctx:
        ctx.prec = 60
        for r in range(1, rmax + 1):
            x = Decimal(r) * (Decimal(m) / Decimal(r)).ln() * SCALE
            out[r] = int(x.to_integral_value(rounding=ROUND_HALF_EVEN))
    return out
