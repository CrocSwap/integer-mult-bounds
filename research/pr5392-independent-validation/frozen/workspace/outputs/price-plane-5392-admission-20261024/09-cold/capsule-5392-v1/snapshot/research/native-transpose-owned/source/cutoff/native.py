"""Canonical affine maps with quadratic Gaussian phases."""
from dataclasses import dataclass
from exact import need


def parity(x):
    return x.bit_count() & 1


def act(rows, x):
    return sum(parity(row & x) << j for j, row in enumerate(rows))


def inverse(rows):
    n = len(rows)
    work = [row | (1 << (n + i)) for i, row in enumerate(rows)]
    for j in range(n):
        p = next((k for k in range(j, n) if work[k] >> j & 1), None)
        need(p is not None, 'invertible binary matrix required')
        work[j], work[p] = work[p], work[j]
        for k in range(n):
            if k != j and work[k] >> j & 1:
                work[k] ^= work[j]
    return tuple(x >> n for x in work)


def matrix_product(left, right):
    result = []
    for row in left:
        value = 0
        for j, other in enumerate(right):
            if row >> j & 1:
                value ^= other
        result.append(value)
    return tuple(result)


@dataclass(frozen=True)
class Native:
    rows: tuple
    offset: int
    phase: int
    linear: tuple
    quadratic: tuple

    @property
    def n(self):
        return len(self.rows)

    @classmethod
    def identity(cls, n):
        return cls(tuple(1 << j for j in range(n)), 0, 0, (0,) * n, (0,) * n)

    @classmethod
    def parse(cls, data, n):
        need(isinstance(data, dict), 'native recipe object required')
        need(set(data) == {'matrix_rows', 'offset', 'phase', 'linear_Z4', 'quadratic_rows'},
             'exact native recipe fields required')
        rows, linear, quadratic = (data[k] for k in ('matrix_rows', 'linear_Z4', 'quadratic_rows'))
        need(all(isinstance(x, list) and len(x) == n for x in (rows, linear, quadratic)),
             'native recipe dimension')
        need(all(type(x) is int and 0 <= x < 1 << n for x in rows + quadratic),
             'binary row extent')
        need(all(type(x) is int and 0 <= x < 4 for x in linear), 'linear phase extent')
        need(type(data['offset']) is int and 0 <= data['offset'] < 1 << n, 'offset extent')
        need(type(data['phase']) is int and 0 <= data['phase'] < 4, 'constant phase extent')
        inverse(rows)
        # The source convention ignores diagonal and lower quadratic entries.
        quadratic = tuple(row & ~((1 << (j + 1)) - 1) for j, row in enumerate(quadratic))
        return cls(tuple(rows), data['offset'], data['phase'], tuple(linear), quadratic)

    def json(self):
        return {'matrix_rows': list(self.rows), 'offset': self.offset, 'phase': self.phase,
                'linear_Z4': list(self.linear), 'quadratic_rows': list(self.quadratic)}

    def image(self, x):
        return act(self.rows, x) ^ self.offset

    def exponent(self, x):
        return (self.phase + sum(self.linear[i] for i in range(self.n) if x >> i & 1)
                + 2 * sum(parity(self.quadratic[i] & x) for i in range(self.n) if x >> i & 1)) % 4

    @classmethod
    def from_function(cls, rows, offset, phase_function):
        n = len(rows)
        c = phase_function(0) % 4
        a = tuple((phase_function(1 << i) - c) % 4 for i in range(n))
        quadratic = []
        for i in range(n):
            row = 0
            for j in range(i + 1, n):
                delta = (phase_function((1 << i) | (1 << j)) - c - a[i] - a[j]) % 4
                need(delta in (0, 2), 'quadratic phase parity')
                row |= (delta // 2) << j
            quadratic.append(row)
        return cls(tuple(rows), offset, c, a, tuple(quadratic))

    def compose(self, right):
        """Apply right first, then this map. Scalars stay outside this operation."""
        need(self.n == right.n, 'composition dimension')
        return Native.from_function(matrix_product(self.rows, right.rows),
                                    act(self.rows, right.offset) ^ self.offset,
                                    lambda x: right.exponent(x) + self.exponent(right.image(x)))

    def inv(self):
        rows = inverse(self.rows)
        offset = act(rows, self.offset)
        return Native.from_function(rows, offset, lambda x: -self.exponent(act(rows, x) ^ offset))

    def phase_key(self):
        return ((self.phase,) + self.linear +
                tuple((self.quadratic[i] >> j) & 1 for i in range(self.n) for j in range(i + 1, self.n)))


def gram_factor(rows):
    """Return at most n+1 columns whose binary outer products sum to rows."""
    n = len(rows)
    need(all(0 <= r < 1 << n for r in rows), 'Gram row extent')
    need(all(((rows[i] >> j) & 1) == ((rows[j] >> i) & 1)
             for i in range(n) for j in range(n)), 'symmetric Gram matrix')

    def pair(x, y):
        return parity(x & act(rows, y))

    pending = [1 << i for i in range(n)]
    singles, pairs = [], []
    while pending:
        p = next((i for i, v in enumerate(pending) if pair(v, v)), None)
        if p is not None:
            v = pending.pop(p)
            singles.append(v)
            pending = [w ^ (v if pair(v, w) else 0) for w in pending]
            continue
        hit = next(((i, j) for i in range(len(pending)) for j in range(i + 1, len(pending))
                    if pair(pending[i], pending[j])), None)
        if hit is None:
            break
        i, j = hit
        v, w = pending[i], pending[j]
        pairs.append((v, w))
        pending = [u ^ (v if pair(u, w) else 0) ^ (w if pair(u, v) else 0)
                   for k, u in enumerate(pending) if k not in (i, j)]

    basis = singles + [v for pair_ in pairs for v in pair_] + pending
    a, b = len(singles), len(pairs)
    rank = a + 2 * b
    width = rank + bool(b)
    # Even-weight vectors in odd dimension have a nonsingular alternating form.
    even = [(1 << i) | (1 << (2 * b)) for i in range(2 * b)]
    hyperbolic = []
    while even:
        v = even.pop(0)
        j = next(j for j, w in enumerate(even) if parity(v & w))
        w = even.pop(j)
        hyperbolic.extend((v, w))
        even = [u ^ (v if parity(u & w) else 0) ^ (w if parity(u & v) else 0) for u in even]
    canonical = ([1 << i for i in range(a)] + [v << a for v in hyperbolic]
                 + [0] * len(pending))
    undo = inverse(basis)
    vectors = []
    for row in undo:
        value = 0
        for j in range(n):
            if row >> j & 1:
                value ^= canonical[j]
        vectors.append(value)
    return [sum(((vectors[i] >> j) & 1) << i for i in range(n)) for j in range(width)]


def character_tuple(n, character, floor=None):
    """Realize one phase character on an affinely spanning tuple."""
    need(len(character) == 1 + n + n * (n - 1) // 2, 'phase character dimension')
    need(all(type(x) is int and 0 <= x < 4 for x in character[:n + 1]) and
         all(type(x) is int and x in (0, 1) for x in character[n + 1:]), 'phase character extent')
    floor = 2 * n + 4 if floor is None else floor
    need(type(floor) is int and floor >= 2 * n + 4, 'tensor window floor')
    c, a = character[0], character[1:n + 1]
    rows = [((a[i] & 1) ^ 1) << i for i in range(n)]
    k = n + 1
    for i in range(n):
        for j in range(i + 1, n):
            rows[i] |= character[k] << j
            rows[j] |= character[k] << i
            k += 1
    points = [0] + [1 << i for i in range(n)] + gram_factor(rows)
    counts = [sum((x >> i) & 1 for x in points) % 4 for i in range(n)]
    need(all((a[i] - counts[i]) % 2 == 0 for i in range(n)), 'Gram parity invariant')
    z = sum((((a[i] - counts[i]) % 4) // 2) << i for i in range(n))
    if z:
        points.extend((z, z))
    f = floor + (c - floor) % 4
    need(len(points) <= f, 'proved tensor cutoff')
    return points + [0] * (f - len(points))
