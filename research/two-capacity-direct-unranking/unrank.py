"""Direct two-capacity unranking with no prescribed injection.

Produced by Nick Petalas. Apache-2.0.
Uses Ali Romman's PR6539 quotient factors and classical Grassmann counts.
"""
from math import prod

from linear import (Field, add_vectors, basis, combine, complement, coordinates,
                    meet, need, standard)


def gaussian(m, k, q):
    if not 0 <= k <= m:
        return 0
    k = min(k, m - k)
    top = prod(q ** (m - j) - 1 for j in range(k))
    bottom = prod(q ** (k - j) - 1 for j in range(k))
    quotient, remainder = divmod(top, bottom)
    need(remainder == 0, "integral Gaussian coefficient")
    return quotient


def injections(m, k, q):
    return prod(q ** m - q ** j for j in range(k)) if 0 <= k <= m else 0


class Index:
    def __init__(self, value):
        need(type(value) is int and value >= 0, "nonnegative integer index")
        self.value = value

    def take(self, radix):
        need(radix > 0, "positive radix")
        self.value, digit = divmod(self.value, radix)
        return digit

    def finish(self):
        need(self.value == 0, "index fully consumed")


def digits(value, length, q):
    need(0 <= value < q ** length, "field digit range")
    cursor = Index(value)
    result = tuple(cursor.take(q) for _ in range(length))
    cursor.finish()
    return result


def subspace(m, k, value, field):
    """Unrank a Grassmannian by first-column RREF decomposition, iteratively."""
    need(0 <= value < gaussian(m, k, field.q), "subspace index")
    pending, left = [], k
    for col in range(m):
        remaining = m - col
        skip = gaussian(remaining - 1, left, field.q)
        if value < skip:
            continue
        value -= skip
        value, free = divmod(value, field.q ** (remaining - left))
        pending.append((col, digits(free, remaining - left, field.q)))
        left -= 1
    need(left == value == 0, "Grassmann index consumed")
    pivots = tuple(col for col, _ in pending)
    rows = []
    for col, free in pending:
        row = [int(j == col) for j in range(m)]
        slots = tuple(j for j in range(col + 1, m) if j not in pivots)
        need(len(slots) == len(free), "RREF free slots")
        for j, digit in zip(slots, free):
            row[j] = digit
        rows.append(tuple(row))
    return tuple(rows)


def outside(rows, n, value, field):
    """Unrank a vector outside span(rows) without scanning ambient vectors."""
    k = len(rows)
    need(0 <= value < field.q ** n - field.q ** k, "outside-span index")
    tail = complement(rows, standard(n), n, field)
    free, old = divmod(value, field.q ** k)
    coefficients = digits(old, k, field.q) + digits(free + 1, n - k, field.q)
    return combine(coefficients, rows + tail, n, field)


def injection(m, k, value, field):
    need(0 <= value < injections(m, k, field.q), "injection index")
    cursor, rows = Index(value), ()
    for j in range(k):
        row = outside(rows, m, cursor.take(field.q ** m - field.q ** j), field)
        rows += (row,)
    cursor.finish()
    return rows


def branch_weights(c, d, tau, j, alpha, beta, q):
    h = tau - j
    return tuple((i, gaussian(h, i, q) * gaussian(c - tau, alpha - i, q)
                  * q ** ((h - i) * (alpha - i)) * injections(alpha, alpha, q)
                  * injections(d - j - i, beta, q) * q ** (i * beta))
                 for i in range(max(0, alpha - c + tau), min(alpha, h) + 1))


class Contract:
    """Canonical finite input; maps are returned as standard-domain columns."""

    def __init__(self, n, q, a, b, c, d):
        need(type(n) is int and 0 <= n <= 12, "dimension limit")
        self.n, self.field = n, Field(q)
        spaces = []
        for rows in (a, b, c, d):
            need(len(rows) <= n, "input basis length")
            need(all(len(v) == n and all(type(x) is int and 0 <= x < q for x in v)
                     for v in rows), "canonical vectors")
            spaces.append(basis(rows, n, self.field))
        self.a, self.b, self.c, self.d = spaces
        self.j = meet(self.a, self.b, n, self.field)
        self.t = meet(self.c, self.d, n, self.field)
        self.aa = complement(self.j, self.a, n, self.field)
        self.bb = complement(self.j, self.b, n, self.field)
        self.cc = complement(self.t, self.c, n, self.field)
        self.dd = complement(self.t, self.d, n, self.field)
        self.source = self.j + self.aa + self.bb
        self.source += complement(self.source, standard(n), n, self.field)
        self.weights = ()
        if len(self.j) <= len(self.t):
            self.weights = branch_weights(len(self.c), len(self.d), len(self.t),
                                          len(self.j), len(self.aa), len(self.bb), q)
        self.total = (injections(len(self.t), len(self.j), q)
                      * sum(w for _, w in self.weights)
                      * q ** (len(self.j) * (len(self.aa) + len(self.bb)))
                      * prod(q ** n - q ** k
                             for k in range(len(self.j + self.aa + self.bb), n)))

    def decode(self, value):
        need(type(value) is int and 0 <= value < self.total, "completion index")
        f, n, q = self.field, self.n, self.field.q
        j, alpha, beta = len(self.j), len(self.aa), len(self.bb)
        cursor = Index(value)
        common = injection(len(self.t), j,
                           cursor.take(injections(len(self.t), j, q)), f)
        images = tuple(combine(v, self.t, n, f) for v in common)
        h = complement(images, self.t, n, f)
        branch = cursor.take(sum(w for _, w in self.weights))
        selected = None
        for i, weight in self.weights:
            if branch < weight:
                selected = i
                break
            branch -= weight
        need(selected is not None, "nonempty intersection branch")
        left, right = self._quotient(images, h, selected, Index(branch))
        for v in left + right:
            coeff = digits(cursor.take(q ** j), j, q)
            images += (add_vectors(v, combine(coeff, images[:j], n, f), f),)
        for k in range(len(images), n):
            images += (outside(images, n, cursor.take(q ** n - q ** k), f),)
        cursor.finish()
        need(len(images) == n, "complete image basis")
        return tuple(combine(coordinates(self.source, v, n, f), images, n, f)
                     for v in standard(n))

    def sample(self, blocks):
        """Supplied independent uniform b-bit blocks; report bounded exhaustion."""
        need(self.total > 0, "nonempty sampling contract")
        width = (self.total - 1).bit_length()
        need(len(blocks) <= 64, "sampling attempt limit")
        need(all(type(x) is int and 0 <= x < 2 ** width for x in blocks),
             "canonical entropy blocks")
        for attempt, value in enumerate(blocks):
            if value < self.total:
                return self.decode(value), (attempt + 1) * width
        return None, len(blocks) * width

    def _quotient(self, common, h, i, cursor):
        f, n, q = self.field, self.n, self.field.q
        alpha, beta = len(self.aa), len(self.bb)
        ib = subspace(len(h), i, cursor.take(gaussian(len(h), i, q)), f)
        intersection = tuple(combine(v, h, n, f) for v in ib)
        hc = complement(intersection, h, n, f)
        kb = subspace(len(self.cc), alpha - i,
                      cursor.take(gaussian(len(self.cc), alpha - i, q)), f)
        graph = tuple(combine(v, self.cc, n, f) for v in kb)
        graph = tuple(add_vectors(v, combine(digits(cursor.take(q ** len(hc)),
                                                   len(hc), q), hc, n, f), f)
                      for v in graph)
        p = intersection + graph
        gl = injection(alpha, alpha, cursor.take(injections(alpha, alpha, q)), f)
        left = tuple(combine(v, p, n, f) for v in gl)
        target = hc + self.dd
        inj = injection(len(target), beta,
                        cursor.take(injections(len(target), beta, q)), f)
        right = tuple(combine(v, target, n, f) for v in inj)
        right = tuple(add_vectors(v, combine(digits(cursor.take(q ** i), i, q),
                                             intersection, n, f), f) for v in right)
        cursor.finish()
        need(len(common) + len(h) == len(self.t), "common quotient dimensions")
        return left, right
