"""Exact arithmetic helpers (standard library only): rank / row-reduction over Q (Fractions), ranks over F2 (ints as bit rows),
p-adic valuation at 2, deterministic output.  Used by every check."""
from fractions import Fraction as Fr


def rank_f2(rows):
    """Rank over F2 of a list of ints (each int = a bit row)."""
    basis = {}
    r = 0
    for x in rows:
        while x:
            h = x.bit_length() - 1
            if h in basis:
                x ^= basis[h]
            else:
                basis[h] = x
                r += 1
                break
    return r


def rref(rows):
    """Reduced row echelon form over Q of a list of vectors; returns a tuple of tuples of Fractions (canonical)."""
    M = [[Fr(x) for x in r] for r in rows]
    piv = []
    r = 0
    ncol = len(M[0]) if M else 0
    for c in range(ncol):
        p = next((i for i in range(r, len(M)) if M[i][c] != 0), None)
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        inv = 1 / M[r][c]
        M[r] = [x * inv for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        piv.append(c)
        r += 1
        if r == len(M):
            break
    return tuple(tuple(row) for row in M[:r])


def rank_q(rows):
    return len(rref(rows)) if rows else 0


def in_span(basis_rref, v):
    """Is v in the row space of the (reduced) basis? basis_rref from rref()."""
    v = [Fr(x) for x in v]
    for row in basis_rref:
        c = next(i for i, x in enumerate(row) if x != 0)
        if v[c] != 0:
            f = v[c]
            v = [a - f * b for a, b in zip(v, row)]
    return all(x == 0 for x in v)


def nullspace(rows, ncols):
    """Basis (list of tuples of Fractions) of {x : rows . x = 0} over Q."""
    R = rref(rows) if rows else ()
    pivs = [next(i for i, x in enumerate(r) if x != 0) for r in R]
    free = [c for c in range(ncols) if c not in pivs]
    out = []
    for f in free:
        x = [Fr(0)] * ncols
        x[f] = Fr(1)
        for r, p in zip(R, pivs):
            x[p] = -r[f]
        out.append(tuple(x))
    return out


def v2(x):
    """2-adic valuation of a nonzero rational (None for 0)."""
    x = Fr(x)
    if x == 0:
        return None
    n, d, k = x.numerator, x.denominator, 0
    while n % 2 == 0:
        n //= 2
        k += 1
    while d % 2 == 0:
        d //= 2
        k -= 1
    return k


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))
