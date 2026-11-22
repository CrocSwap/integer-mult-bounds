"""Run both native copies on independent nonzero stabilizer-product witnesses.

The changed-helper probe in #8030 supplies the role 1544. Here each of the
two actual copies has its own nonzero input, and each column can start at a
different basis vector. An exact tensor representation makes the 16-column
witness small enough to evaluate. Production data use the full field.
"""

from fractions import Fraction as F
from functools import cache
from upstream import HERE, install

_, _, _, source = install()
from strong_complex import artifacts, word
from raw48 import ComplexRaw
from periodic import Job


def rot(z, e):
    a, b = z
    return ((a, b), (-b, a), (-a, -b), (b, -a))[e % 4]


def times(z, w):
    a, b = z
    c, d = w
    return a * c - b * d, b * c + a * d


def plus(x, y):
    return x[0] + y[0], x[1] + y[1]


def normalize(v):
    """Remove one global phase. Minus one denotes a zero amplitude."""
    first = next(q for q in v if q >= 0)
    return tuple(-1 if q < 0 else (q - first) % 4 for q in v), first


@cache
def basis(i):
    return tuple(0 if j == i else -1 for j in range(512))


@cache
def affine(v, t, s):
    assert 0 <= t < 9 and (s is None or 0 <= s < 9)
    return normalize(tuple(v[j ^ ((1 if s is None else (j >> s) & 1) << t)] for j in range(512)))


@cache
def diagonal(v, q):
    return normalize(tuple(-1 if a < 0 else (a + b) % 4 for a, b in zip(v, q, strict=True)))


@cache
def kernel(v, t):
    assert 0 <= t < 9
    roots = {-1: (0, 0), 0: (1, 0), 1: (0, 1), 2: (-1, 0), 3: (0, -1)}
    values = tuple(
        plus(times((1, 1), roots[q]), times((1, -1), roots[v[j ^ (1 << t)]]))
        for j, q in enumerate(v)
    )
    pivot = next(x for x in values if x != (0, 0))
    identify = {rot(pivot, e): e for e in range(4)}
    # A Clifford image of a stabilizer basis state has equal nonzero magnitudes.
    return tuple(-1 if x == (0, 0) else identify[x] for x in values), pivot


@cache
def addresses(col, count):
    return tuple(sum(((j >> b) & 1) << (count * b + col) for b in range(9)) for j in range(512))


class Field:
    """Store an exact Gaussian scalar times normalized disjoint column rays."""

    def __init__(self, stock):
        self.stock = stock
        self.data = None
        self.live = True
        self.writes = 0
        stock[0] += 1
        stock[1] = max(stock[1], stock[0])

    def blank(self):
        return Field(self.stock)

    def clear(self):
        self.data = None

    def copy(self):
        x = self.blank()
        x.data = self.data
        return x

    def retire(self):
        assert self.live
        self.live = False
        self.data = None
        self.stock[0] -= 1

    def replace(self, other):
        self.data = other.data
        self.writes += 1
        other.retire()

    def scaled(self, real, imag):
        if self.data is None:
            return None
        real, imag = F(real), F(imag)
        z, v = self.data
        for s in (real, imag):
            assert all(a % s.denominator == 0 for a in z)
        a, b = times(z, (real, imag))
        assert a.denominator == b.denominator == 1
        return None if not a and not b else ((int(a), int(b)), v)

    def scale(self, real, imag=0):
        self.data = self.scaled(real, imag)

    def scale_add(self, other, real=1, imag=0):
        d = other.scaled(real, imag)
        if d is None:
            return
        if self.data is None:
            self.data = d
            return
        a, v = self.data
        b, w = d
        assert v == w, "Two live donor states do not have the same exact ray."
        s = plus(a, b)
        self.data = None if s == (0, 0) else (s, v)

    def swap(self, *args):
        assert self.data is None, "The nonzero witness left the external canonical placement."

    def phase(self, fn, suffix):
        if self.data is None:
            return
        z, ray = self.data
        count = len(ray)
        base = fn(0) % 4
        z = rot(z, base)
        after = []
        sums = base
        check = 0
        for i, v in enumerate(ray):
            addr = addresses(i, count)
            phases = tuple((fn(x) - base) % 4 for x in addr)
            j = (71 * i + 93) % 512
            check |= addr[j]
            sums += phases[j]
            v2, phase = diagonal(v, phases)
            after.append(v2)
            z = rot(z, phase)
        assert fn(check) % 4 == sums % 4
        self.data = z, tuple(after)

    def paid(self, index):
        z, vs = self.data
        c = index % len(vs)
        t = index // len(vs)
        v, p = kernel(vs[c], t)
        u = times(z, p)
        assert u[0] % 2 == 0 and u[1] % 2 == 0
        self.data = (u[0] // 2, u[1] // 2), vs[:c] + (v,) + vs[c + 1 :]


class Axes:
    window = 1
    offset = suffix = 0
    swap = None

    def row(self, field, targets, sources=None):
        if field.data is None:
            return
        z, vs = field.data
        n = len(vs)
        after = []
        assert len(targets) == n and (sources is None or len(sources) == n)
        for c, i in enumerate(targets):
            assert i % n == c and (sources is None or sources[c] % n == c)
            v, phase = affine(vs[c], i // n, None if sources is None else sources[c] // n)
            after.append(v)
            z = rot(z, phase)
        field.data = z, tuple(after)


class WitnessRaw(ComplexRaw):
    def chart(self, field, tape, axes, cols, inverse=False):
        if field.data is not None and any(axis >= 9 for axis in axes):
            raise ValueError("A live chart reached a coordinate outside the nine-axis witness.")
        return super().chart(field, tape, axes, cols, inverse)


def final_ray(origin):
    """Evaluate the closed eight-axis product on one basis column."""
    vals = [-1 if (j ^ origin) & 256 else (-(j ^ origin).bit_count()) % 4 for j in range(512)]
    return normalize(tuple(vals))


def check():
    a = artifacts(source / "research/grade14-native-realization", HERE / "inputs")
    w = word(a.graph, a.layout)
    from retimed_supplier import Raw, source_ranks, SCALES, SMALL_SPLITS

    assert SCALES == (1, 8) and SMALL_SPLITS == 1008
    sizes, paid = source_ranks(w)
    stock = [0, 0]
    fields = {i: Field(stock) for i in range(len(sizes))}
    jobs = [Job(i, range(2 * k)) for i, k in enumerate(sizes)]
    clock, call = next((i, row[1]) for i, row in enumerate(a.instructions()) if row[0] == "NATIVE")
    key = ("helper", clock, call, 1544)
    pawn = next(i for i, p in enumerate(w.targets) if p.tag == key)
    assert w.targets[pawn].rank == 8
    expected = {}
    for copy, cols in enumerate((2, 16)):
        owner = pawn + copy * len(w.targets)
        origins = tuple((37 * i + 11 + 17 * copy) % 512 for i in range(cols))
        initial = ((3 if not copy else -7) << 512, (5 if not copy else 2) << 512)
        fields[owner].data = initial, tuple(basis(i) for i in origins)
        exact = tuple(final_ray(i) for i in origins)
        z = rot(initial, sum(p for _, p in exact))
        assert all(a % 16**cols == 0 for a in z)
        expected[owner] = (z[0] // 16**cols, z[1] // 16**cols), tuple(v for v, _ in exact)
    physical = WitnessRaw(a, fields, Axes(), low=0, bundle=1, slots=2 * 1224)
    it = Raw(w, physical).native(jobs, 2)
    cnt = 0
    nonzero = {2: 0, 16: 0}
    for g in paid:
        j = next(it)
        f = fields[j.owner]
        cnt += 1
        assert len(j.axes) == 2 * g
        if f.data is not None:
            nonzero[len(f.data[1])] += 1
            for axis in j.axes:
                f.paid(axis)
    assert next(it, None) is None
    assert set(fields) == set(range(len(sizes))) and all(
        f.live and f.writes >= 1 for f in fields.values()
    )
    assert {k: f.data for k, f in fields.items() if f.data is not None} == expected
    assert all(nonzero.values())
    for f in fields.values():
        f.retire()
    assert stock[0] == 0
    print("independent columns", 2, 16, "nonzero paid cuts by copy", nonzero, "all cuts", cnt)
    print(
        "returned owners",
        len(fields),
        "active output axes",
        2 * sum(sizes),
        "nonzero Hilbert dimensions",
        2**18,
        2**144,
        "peak handles",
        stock[1],
    )
    print(
        "all other outputs retained zero; both nonzero states match the independent closed H-kernel formula"
    )


if __name__ == "__main__":
    check()
