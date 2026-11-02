"""Exact 8-by-8 Gaussian numerator multiplication. Apache-2.0."""

SIZE = 8


def raw_product(a, b):
    """Multiply trusted immutable source triples, before canonical normalization.

    A triple is (nonnegative exponent, 64 real ints, 64 imaginary ints).
    The source-bound loader and fixed fixtures supply this internal contract.
    No coefficient or product is cached here.
    """
    ea, ar, ai = a
    eb, br, bi = b
    rows = [tuple((j, br[8*k+j], bi[8*k+j]) for j in range(SIZE)
                  if br[8*k+j] or bi[8*k+j]) for k in range(SIZE)]
    real, imag = [0]*64, [0]*64
    for i in range(SIZE):
        for k in range(SIZE):
            x, y = ar[8*i+k], ai[8*i+k]
            if x == y == 0:
                continue
            for j, u, v in rows[k]:
                real[8*i+j] += x*u-y*v
                imag[8*i+j] += x*v+y*u
    return ea+eb, real, imag
