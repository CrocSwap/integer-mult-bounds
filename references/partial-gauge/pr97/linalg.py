"""Stdlib exact linear algebra used by the release checks (no numpy).

Ranks over Q are computed in one of two rigorous ways:
  * modulo a prime p with a Hadamard certificate: if every row of an integer matrix has squared norm n_i and
    prod_i max(1, n_i) < p^2, every minor has absolute value < p, so a minor is nonzero over Q iff it is nonzero
    mod p, and the rank mod p equals the rank over Q (hadamard_ok);
  * exactly, by fraction-free (Bareiss) elimination over Z (rank_exact) or Fraction elimination (null_exact).
Everything else is plain arithmetic modulo a prime."""
from fractions import Fraction
from math import gcd

Q31 = 2**31 - 1          # prime used for the point evaluation and frame reductions
M127 = 2**127 - 1        # Mersenne prime
M521 = 2**521 - 1        # Mersenne prime


def hadamard_ok(rows, p):
    """True if prod of max(1, |row|^2) < p^2, i.e. every minor of the integer matrix is below p in absolute value."""
    b = 1; p2 = p * p
    for r in rows:
        b *= max(1, sum(x * x for x in r))
        if b >= p2: return False
    return True


class Echelon:
    """Row echelon basis mod p, built by insertion. Each stored row has a pivot (first nonzero, normalised to 1)
    and zeros in the pivot columns of all earlier rows, so reducing a new row against the rows in order is exact."""
    __slots__ = ('p', 'rows', 'piv')

    def __init__(self, p):
        self.p = p; self.rows = []; self.piv = []

    def reduce(self, r):
        p = self.p; r = [x % p for x in r]
        for pc, b in zip(self.piv, self.rows):
            c = r[pc]
            if c: r = [(x - c * y) % p for x, y in zip(r, b)]
        return r

    def insert(self, r):
        """insert row; returns True if it was independent."""
        r = self.reduce(r)
        for i, x in enumerate(r):
            if x:
                inv = pow(x, self.p - 2, self.p)
                self.rows.append([(y * inv) % self.p for y in r]); self.piv.append(i); return True
        return False

    def contains(self, r):
        return not any(self.reduce(r))

    def __len__(self): return len(self.rows)


def rank_mod(rows, p):
    E = Echelon(p)
    for r in rows: E.insert(r)
    return len(E)


def rank_exact(rows):
    """exact rank over Q of an integer matrix (Bareiss fraction-free elimination)."""
    M = [list(r) for r in rows if any(r)]
    if not M: return 0
    n = len(M); k = len(M[0]); r = 0; prev = 1
    for c in range(k):
        i = next((i for i in range(r, n) if M[i][c]), None)
        if i is None: continue
        M[r], M[i] = M[i], M[r]
        pr = M[r]; a = pr[c]
        for t in range(r + 1, n):
            row = M[t]; b = row[c]
            M[t] = [(a * x - b * y) // prev for x, y in zip(row, pr)]
        prev = a; r += 1
        if r == n: break
    return r


def null_mod(A, k, p):
    """basis of {x in F_p^k : A x = 0} (A: list of rows of length k)."""
    rows = [[x % p for x in r] for r in A]; piv = []; R = []
    for r in rows:
        for pc, b in zip(piv, R):
            c = r[pc]
            if c: r = [(x - c * y) % p for x, y in zip(r, b)]
        i = next((i for i, x in enumerate(r) if x), None)
        if i is None: continue
        inv = pow(r[i], p - 2, p); r = [(y * inv) % p for y in r]
        R = [[(x - b[i] * y) % p for x, y in zip(b, r)] if b[i] else b for b in R]   # keep fully reduced
        R.append(r); piv.append(i)
    free = [c for c in range(k) if c not in piv]; out = []
    for f in free:
        x = [0] * k; x[f] = 1
        for pc, b in zip(piv, R): x[pc] = (-b[f]) % p
        out.append(x)
    return out


def null_exact(A, k):
    """basis (integer vectors) of {x in Q^k : A x = 0}, by Fraction reduced row echelon form."""
    R = []; piv = []
    for r0 in A:
        r = [Fraction(x) for x in r0]
        for pc, b in zip(piv, R):
            c = r[pc]
            if c: r = [x - c * y for x, y in zip(r, b)]
        i = next((i for i, x in enumerate(r) if x), None)
        if i is None: continue
        inv = 1 / r[i]; r = [y * inv for y in r]
        R = [[x - b[i] * y for x, y in zip(b, r)] if b[i] else b for b in R]
        R.append(r); piv.append(i)
    free = [c for c in range(k) if c not in piv]; out = []
    for f in free:
        x = [Fraction(0)] * k; x[f] = Fraction(1)
        for pc, b in zip(piv, R): x[pc] = -b[f]
        out.append(primitive(x))
    return out


def primitive(x):
    """scale a rational vector to a primitive integer vector."""
    den = 1
    for v in x: den = den * v.denominator // gcd(den, v.denominator)
    y = [int(v * den) for v in x]; g = 0
    for v in y: g = gcd(g, v)
    return [v // g for v in y] if g else y


def inv_mod_matrix(A, p):
    """inverse of a square matrix mod p, or None if singular."""
    n = len(A); M = [[x % p for x in A[i]] + [int(i == j) for j in range(n)] for i in range(n)]
    for c in range(n):
        i = next((i for i in range(c, n) if M[i][c]), None)
        if i is None: return None
        M[c], M[i] = M[i], M[c]
        inv = pow(M[c][c], p - 2, p); M[c] = [(x * inv) % p for x in M[c]]
        rc = M[c]
        for t in range(n):
            if t != c and M[t][c]:
                f = M[t][c]; M[t] = [(x - f * y) % p for x, y in zip(M[t], rc)]
    return [r[n:] for r in M]


def matmul(A, B, p):
    Bt = list(zip(*B))
    return [[sum(x * y for x, y in zip(r, c)) % p for c in Bt] for r in A]


def rightmost_pivots(Q, p):
    """rows top to bottom: the rightmost nonzero column of the reduced row, then eliminate it below."""
    M = [list(r) for r in Q]; n = len(M); out = [-1] * n
    for i in range(n):
        row = M[i]; c = next((j for j in range(len(row) - 1, -1, -1) if row[j]), -1)
        out[i] = c
        if c < 0: continue
        inv = pow(row[c], p - 2, p)
        for t in range(i + 1, n):
            f = M[t][c]
            if f:
                f = f * inv % p; M[t] = [(x - f * y) % p for x, y in zip(M[t], row)]
    return out


def predicted(h):
    """pivot column per row of the generic north-east rank function f_r of a rank-r idempotent."""
    pr = {}
    for r in range(1, h + 1):
        s = h - r
        f = lambda i, j: 0 if i < 0 or j >= h else min(i + 1, h - j, r, max(0, i - j + 1) + s)
        pc = [-1] * h
        for i in range(h):
            for j in range(h):
                if f(i, j) - f(i - 1, j) - f(i, j + 1) + f(i - 1, j + 1) == 1: pc[i] = j
        pr[r] = pc
    return pr
