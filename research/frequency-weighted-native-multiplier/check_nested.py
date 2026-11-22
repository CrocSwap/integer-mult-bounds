"""Execute an actual weighted interior loan of a nonzero Raw48 field across both native types."""

from pathlib import Path
from collections import Counter
from functools import cache
from fractions import Fraction as Q
import sys

sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
from upstream import install

install()
from band_product import production_supplier
from periodic import Job
from raw48 import ComplexRaw
from check_nonzero_eight import Field, rot, times
from typed_raw import TypedRaw
from transport import Measure
from unpowered_price import certify
from installations import GAUSSIAN_C

lanes = 8
bits = 18
dim = 1 << bits
ALL = (1 << dim) - 1
# Each bit in a phase mask is one computational basis address.
ONES = tuple(ALL // ((1 << (1 << i)) + 1) << (1 << i) for i in range(bits))
unit = ((1, 0), (0, 1), (-1, 0), (0, -1), (0, 0))


@cache
def initial(x):
    return (1 << x, 0, 0, 0)


def norm(v):
    """Strip the phase of the first nonzero basis amplitude."""
    active = v[0] | v[1] | v[2] | v[3]
    first = active & -active
    pivot = next(j for j, s in enumerate(v) if s & first)
    return tuple(v[(j + pivot) % 4] for j in range(4)), pivot


def flip(s, t, ctrl):
    low = s & (ALL ^ ONES[t]) & ctrl
    high = s & ONES[t] & ctrl
    return (s ^ low ^ high) | (low << (1 << t)) | (high >> (1 << t))


@cache
def affine(v, target, control):
    ctrl = ALL if control < 0 else ONES[control]
    return norm(tuple(flip(s, target, ctrl) for s in v))


@cache
def diagonal_masks(alpha, cross):
    low = high = 0
    for i, g in enumerate(alpha):
        m = ONES[i]
        if g & 1:
            high ^= low & m
            low ^= m
        if g & 2:
            high ^= m
    for i, j in cross:
        high ^= ONES[i] & ONES[j]
    return ALL ^ (low | high), low & (ALL ^ high), high & (ALL ^ low), low & high


@cache
def phases(v, alpha, cross):
    masks = diagonal_masks(alpha, cross)
    return norm(
        tuple(
            (masks[0] & v[j])
            | (masks[1] & v[(j - 1) % 4])
            | (masks[2] & v[(j - 2) % 4])
            | (masks[3] & v[(j - 3) % 4])
            for j in range(4)
        )
    )


@cache
def kernel(v, target):
    """Apply the numerator (1+i)I+(1−i)X on one exact 18-bit factor."""
    masks = (*v, ALL ^ (v[0] | v[1] | v[2] | v[3]))
    others = tuple(flip(s, target, ALL) for s in masks)
    buckets = {}
    nz = 0
    for j, s in enumerate(masks):
        if not s:
            continue
        a, b = unit[j]
        for k, w in enumerate(others):
            v2 = s & w
            if not v2:
                continue
            c, d = unit[k]
            z = a - b + c + d, a + b + d - c
            if z == (0, 0):
                continue
            buckets[z] = buckets.get(z, 0) | v2
            nz |= v2
    first = nz & -nz
    pivot = next(z for z, s in buckets.items() if s & first)
    result = tuple(buckets.get(rot(pivot, i), 0) for i in range(4))
    assert sum(q.bit_count() for q in result) == nz.bit_count()
    return result, pivot


def axis(i):
    v, j = divmod(i, lanes)
    if v >= bits:
        raise ValueError(
            "The live stabilizer reached a qubit outside its declared group"
        )
    return v, j


class ProductField(Field):
    """A shared Gaussian scalar times eight independent 18-bit stabilizer factors."""

    def blank(self):
        return ProductField(self.stock)

    def affine(self, t, s):
        if self.data is None:
            return
        i, j = axis(t)
        v = -1
        if s is not None:
            v, k = axis(s)
            assert k == j
        z, vs = self.data
        w, h = affine(vs[j], i, v)
        self.data = rot(z, h), vs[:j] + (w,) + vs[j + 1 :]

    def paid(self, t):
        if self.data is None:
            return
        i, j = axis(t)
        z, vs = self.data
        w, h = kernel(vs[j], i)
        new = times(z, h)
        assert not (new[0] % 2 or new[1] % 2)
        self.data = (new[0] // 2, new[1] // 2), vs[:j] + (w,) + vs[j + 1 :]

    def phase(self, fn, suffix):
        if self.data is None:
            return
        z, vs = self.data
        base = fn(0) % 4
        z = rot(z, base)
        # Every literal I, S and CZ on a complete set of 8 or 16 columns is
        # diagonal quadratic and preserves the residue class modulo 8.
        loc = [1 << (i * lanes) for i in range(bits)]
        alpha = tuple((fn(x) - base) % 4 for x in loc)
        cross = []
        for i in range(bits):
            for j in range(i):
                coeff = (fn(loc[i] | loc[j]) - base - alpha[i] - alpha[j]) % 4
                assert coeff in (0, 2)
                if coeff:
                    cross.append((i, j))
        cross = tuple(cross)
        outs = []
        probe = 0
        measured = base
        for j, v in enumerate(vs):
            local = sum(loc[i] << j for i in range(bits) if (5 * i + j) % 7 < 3)
            assert (fn(local) - base) % 4 == (fn(local >> j) - base) % 4
            measured += fn(local) - base
            probe |= local
            w, h = phases(v, alpha, cross)
            outs.append(w)
            z = rot(z, h)
        assert fn(probe) % 4 == measured % 4
        self.data = z, tuple(outs)


class Axes:
    window = 1
    offset = suffix = 0
    swap = None

    def row(self, f, targets, sources=None):
        if f.data is None:
            return
        for j, t in enumerate(targets):
            f.affine(t, None if sources is None else sources[j])


def test():
    system = production_supplier(1024, 10**18)
    art, word = system.physical, system.word
    types = system.recipe.types()
    t, p = Counter(), Counter()
    n = 8192
    for v in types:
        for k in v.targets:
            t[k] += v.multiplicity
        for r in v.paid:
            p[r] += v.multiplicity
    C = GAUSSIAN_C
    _, cells = certify(C, (t, p))
    grant = (
        Measure(1 - C, 2**48, 64 * n.bit_length()).mass(24, 26)[0]
        * cells[1, 2]
        * 90
        / t[2]
    )
    child_count = system.recipe.targets.variants[1].histogram[2]
    share = system.recipe.typed_cells()[0, 1, 1, 2] / child_count
    assert (
        share == cells[1, 2] * 90 / t[2]
        and grant.numerator // grant.denominator == 899557645
    )
    assert cells[1, 2] > Q(99, 100) and 24 * 1 == 12 * 2
    clock, call = next(
        (i, row[1]) for i, row in enumerate(art.instructions()) if row[0] == "NATIVE"
    )
    pawn = next(
        i for i, k in enumerate(word.targets) if k.tag == ("helper", clock, call, 1544)
    )
    child = next(
        i
        for i, k in enumerate(word.targets)
        if k.rank == 1 and k.tag[:3] == ("helper", clock, call)
    )
    stock = [0, 0]
    fields = {i: ProductField(stock) for i in range(2 * len(word.targets))}
    big = types[0]
    small = types[1]
    P = 16
    S = 8
    rows = [Job(i, range(P * r)) for i, r in enumerate(big.targets)]
    x0 = 0
    for b in range(9):
        x0 |= ((11 >> b) & 1) << (2 * b)
        x0 |= ((73 >> b) & 1) << (2 * b + 1)
    z = (3 << 8192, 5 << 8192)
    fields[pawn].data = z, (initial(x0),) * lanes
    expected = fields[pawn].copy()
    for i in range(8 * P):
        expected.paid(i)
    physical = ComplexRaw(art, fields, Axes(), low=0, bundle=1, slots=n)
    method = TypedRaw(word, physical)
    op = method.native(rows, P)
    uses = [0, 0]
    for j, r in enumerate(big.paid):
        job = next(op)
        f = fields[job.owner]
        assert len(job.axes) == r * P
        if j != 3418:
            for axis_ in job.axes:
                f.paid(axis_)
            continue
        assert r == 1 and f.data is not None and tuple(job.axes) == tuple(range(P))
        # The actual parent pays every suffix axis before it lends its prefix.
        for axis_ in job.axes[S:]:
            f.paid(axis_)
        prefix = job.select(range(S))
        due = f.copy()
        for axis_ in prefix.axes:
            due.paid(axis_)
        cr = [
            Job(i + len(word.targets), range((S // 2) * k))
            for i, k in enumerate(small.targets)
        ]
        unused = cr[child].owner
        assert fields[unused].data is None
        cr[child] = prefix
        call2 = method.native(cr, S // 2 + 1)
        for grade in small.paid:
            loan = next(call2)
            owned = fields[loan.owner]
            assert len(loan.axes) == (S // 2) * grade
            if owned.data is not None:
                uses[1] += 1
            for axis_ in loan.axes:
                owned.paid(axis_)
            uses[0] += 1
        assert next(call2, None) is None and f.data == due.data
        due.retire()
        assert all(
            fields[i + len(word.targets)].data is None for i in range(len(word.targets))
        )
        print(
            "real nested transfer completed",
            j,
            word.targets[child].tag,
            uses,
            flush=True,
        )
    assert next(op, None) is None and fields[pawn].data == expected.data
    assert all(f.data is None for i, f in fields.items() if i != pawn)
    assert set(fields) == set(range(2 * len(word.targets)))
    expected.retire()
    for f in fields.values():
        f.retire()
    assert stock[0] == 0 and uses[1] > 0
    print(
        "PASS_NONZERO_INTERIOR",
        len(big.paid),
        len(small.paid),
        child,
        int(grant),
        uses[1],
        stock,
    )


if __name__ == "__main__":
    test()
