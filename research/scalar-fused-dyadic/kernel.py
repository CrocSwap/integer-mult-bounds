"""Fuse exact dyadic sparse-row multiply-adds without changing row values.

Gareth Davidson (@bitplane), substantial OpenAI Codex assistance; Apache-2.0.
The scalar interface is icekylinx's independent audit, retained by Jeremy
Kothe's PR799. See README.md and SOURCES.json for exact provenance.
"""

from fractions import Fraction as F


def fused(q, x, y):
    """Return y+q*x as Fraction, with one normalization on dyadic inputs.

    None denotes a missing destination entry (zero). Non-dyadic existing
    entries use the original rational operations; no domain is silently
    rounded or enlarged by the acceleration.
    """
    numerator = q.numerator * x.numerator
    denominator = q.denominator * x.denominator
    if y is None or not y:
        return F(numerator, denominator)
    dy = y.denominator
    if denominator & (denominator - 1) or dy & (dy - 1):
        return y + q * x
    if dy >= denominator:
        numerator = y.numerator + numerator * (dy // denominator)
        denominator = dy
    else:
        numerator += y.numerator * (denominator // dy)
    return F(numerator, denominator)


def apply(e, rows, dual=False):
    """Same add/scale contract and guards as the pinned reference apply()."""
    if e[0] == "add":
        t, s = e[1:3]
        q = F(e[3], e[4])
        if t == s:
            raise RuntimeError("self add")
        if dual:
            t, s, q = s, t, -q
        dst = rows[t]
        # Snapshot matches the original even if a caller aliases row objects.
        for k, x in list(rows[s].items()):
            a = fused(q, x, dst.get(k))
            if a:
                dst[k] = a
            else:
                dst.pop(k, None)
    elif e[0] == "scale":
        t = e[1]
        q = F(e[2], e[3])
        if not q:
            raise RuntimeError("zero scale")
        if dual:
            q = 1 / q
        rows[t] = {k: q*x for k, x in rows[t].items()}
    else:
        raise RuntimeError("unknown scalar primitive")
