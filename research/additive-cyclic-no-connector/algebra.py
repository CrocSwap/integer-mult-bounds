"""Small polynomial arithmetic for the exact additive Bezout identity."""
from gaussian import G


def product(a, b):
    out = [G()]*(len(a)+len(b)-1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] += x*y
    return out
