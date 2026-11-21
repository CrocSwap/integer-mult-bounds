"""Run all 48 physical emitters on one exact spectator-constant input."""

from argparse import ArgumentParser
from fractions import Fraction
from pathlib import Path
import sys

from strong_complex import artifacts, word


class Field:
    def __init__(self, stock, data=None):
        self.stock, self.data = stock, data
        self.live = True
        stock[0] += 1
        stock[1] = max(stock[0], stock[1])

    def blank(self):
        return Field(self.stock)

    def copy(self):
        return Field(self.stock, None if self.data is None else self.data.copy())

    def clear(self):
        self.data = None

    def replace(self, other):
        self.data = other.data
        other.retire()

    def retire(self):
        assert self.live
        self.live = False
        self.data = None
        self.stock[0] -= 1

    @staticmethod
    def mul(x, c):
        c = Fraction(c)
        a, b = divmod(x, c.denominator)
        if b:
            raise ArithmeticError("The full native trace lost its exact grid")
        return a * c.numerator

    def scale(self, real, imag=0):
        if self.data is not None:
            self.data = [
                (self.mul(a, real) - self.mul(b, imag), self.mul(b, real) + self.mul(a, imag))
                for a, b in self.data
            ]
            if not any(a or b for a, b in self.data):
                self.data = None

    def scale_add(self, other, real=1, imag=0):
        if other.data is not None:
            value = other.copy()
            value.scale(real, imag)
            if value.data is not None:
                if self.data is None:
                    self.data = value.data
                else:
                    self.data = [
                        (a + c, b + d) for (a, b), (c, d) in zip(self.data, value.data, strict=True)
                    ]
                    if not any(a or b for a, b in self.data):
                        self.data = None
            value.retire()

    def phase(self, fn, suffix):
        from spool import quarter

        if self.data is not None:
            self.data = [quarter(v, fn(i)) for i, v in enumerate(self.data)]

    def swap(self, left, right, width, move):
        if self.data is not None:
            raise AssertionError("The selected witness requires a canonical external placement")


class Axes:
    offset = suffix = 0
    window = 1
    swap = None

    @staticmethod
    def row(field, targets, sources=None):
        if field.data is None:
            return
        for i, j in zip(targets, sources or [None] * len(targets), strict=True):
            if i >= 9 or (j is not None and j >= 9):
                raise AssertionError("A live field left the nine-coordinate evaluation space")
            field.data = [
                field.data[k ^ ((1 if j is None else (k >> j) & 1) << i)] for k in range(512)
            ]


def positive(values, bit):
    if not 0 <= bit < 9:
        raise ValueError("The nonzero job changed a spectator")
    out = []
    for j, (a, b) in enumerate(values):
        c, d = values[j ^ (1 << bit)]
        u, v = a - b + c + d, b + a + d - c
        if (u | v) & 1:
            raise ArithmeticError("The paid positive job lost its integer grid")
        out.append((u // 2, v // 2))
    return out


def run(grade, data):
    from periodic import Job
    from raw48 import ComplexRaw

    class WordRaw(ComplexRaw):
        def chart(self, field, tape, axes, cols, inverse=False):
            if field.data is not None:
                if any(j >= 9 for j in axes):
                    raise AssertionError("A nonzero crossed the pure helper/contact boundary")
                super().chart(field, tape, axes, cols, inverse)

    a = artifacts(grade, data)
    w = word(a.graph, a.layout)
    reg = a.layout["source_labels"].index(1544)
    assert reg not in a.main and reg == 1290
    clock, call = next((i, row[1]) for i, row in enumerate(a.instructions()) if row[0] == "NATIVE")
    chosen = ("helper", clock, call, 1544)
    jobs, fields, stock = [], {}, [0, 0]
    ordinary_slots = {}
    for (kind, root), visits in a.roots.items():
        for j, (sign, entries) in enumerate(a.words[kind][1]):
            tag = ("root", kind, root, a.offsets[kind, root] + j, sign)
            ordinary_slots[tag] = (0,) + tuple(
                9 + 8 * (visits[v][0] % 16) + k for v in entries for k in range(8)
            )
    for i, port in enumerate(w.targets):
        job = Job(i, ordinary_slots.get(port.tag, tuple(range(port.rank))))
        fields[i] = Field(stock)
        jobs.append((port.tag, job))
        if port.tag == chosen:
            owner, active = i, job.axes
    initial = [((19 * j - 5) << 128, (3 * j * j + 11) << 128) for j in range(512)]
    fields[owner].data = initial
    raw = WordRaw(a, fields, Axes(), low=0, bundle=1, slots=153)
    seen, nonzero, changed = 0, 0, 0
    iterator = raw.raw(jobs, 1)
    for port in w.paid:
        tag, job = next(iterator)
        assert tag == port.tag and len(job.axes) == port.rank
        field = raw.fields[job.owner]
        if field.data is not None:
            nonzero += 1
            changed += int(tag == ("return", clock, call, 95))
            for bit in job.axes:
                field.data = positive(field.data, bit)
        seen += 1
    assert next(iterator, None) is None
    expected = initial
    for bit in active:
        expected = positive(expected, bit)
    assert fields[owner].data == expected and all(
        f.data is None for i, f in fields.items() if i != owner
    )
    assert set(fields) == set(range(len(w.targets))) and stock[0] == len(fields)
    assert nonzero and changed == 1 and a.moves[95] == (34, 127)
    return dict(
        complete_raw_callers=48,
        external_roles=len(w.targets),
        actual_paid=seen,
        nonzero_paid=nonzero,
        changed_paid=changed,
        peak_test_fields=stock[1],
        owner=owner,
        helper_rank=len(active),
        returned_records=512,
    )


if __name__ == "__main__":
    p = ArgumentParser(description=__doc__)
    for key in ("grade", "native", "bounded", "data"):
        p.add_argument(key, type=Path)
    args = p.parse_args()
    sys.path.extend(str(path.resolve()) for path in (args.native, args.bounded))
    print(run(args.grade, args.data))
