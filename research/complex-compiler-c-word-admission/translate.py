"""Finite source-record lowering; compilation operates on owner labels, not data.

The source native callback and its all-column endpoint remain premises.
Product/schedule below are imported byte-for-byte from the exact #7828 head.
"""
from dataclasses import dataclass
from fractions import Fraction


def require(ok, message):
    if not ok:
        raise ValueError(message)


@dataclass(frozen=True)
class Monomial:
    rows: tuple
    offset: int
    constant: int
    linear: tuple
    quadratic: tuple

    def gates(self):
        n = len(self.rows)
        require(n > 0 and len(self.linear) == n, "finite square monomial")
        require(all(type(r) is int and 0 <= r < 1 << n for r in self.rows), "binary matrix")
        require(0 <= self.offset < 1 << n and 0 <= self.constant < 4, "absolute affine phase")
        require(all(type(a) is int and 0 <= a < 4 for a in self.linear), "Z4 linear phase")
        require(len(set(self.quadratic)) == len(self.quadratic)
                and all(0 <= a < b < n for a, b in self.quadratic), "off-diagonal quadratic phase")
        matrix = list(self.rows)
        reduction = []

        def add(a, b):
            matrix[b] ^= matrix[a]
            reduction.append(("cx", a, b))

        for col in range(n):
            pivot = next((i for i in range(col, n) if matrix[i] >> col & 1), None)
            require(pivot is not None, "singular monomial")
            if pivot != col:
                add(col, pivot); add(pivot, col); add(col, pivot)
            for row in range(n):
                if row != col and matrix[row] >> col & 1:
                    add(col, row)
        require(matrix == [1 << i for i in range(n)], "elimination identity")
        gates = [("s", i) for i, a in enumerate(self.linear) for _ in range(a)]
        gates += [("cz", a, b) for a, b in self.quadratic]
        gates += list(reversed(reduction))
        gates += [("x", i) for i in range(n) if self.offset >> i & 1]
        gates += [("unit",)] * self.constant
        require(len(gates) <= 4 * (n + 1) ** 2, "source monomial record allowance")
        return tuple(gates)


class Emitter:
    """One fixed expanded word: public owners first, fresh private lifetime tags.

    All loops here are compile-time. Lift f is absent from compilation.
    """
    def __init__(self, dimension, productive):
        require(dimension >= 2 and productive >= 2, "target header")
        self.n, self.productive = dimension, productive
        self.next_owner = productive
        self.ops, self.paid_sites, self.moves, self.retired = [], [], [], []

    def zero(self):
        owner = self.next_owner
        self.next_owner += 1
        self.ops.append(("clear", owner))
        return owner

    def retire_zero(self, owner):
        require(self.productive <= owner < self.next_owner, "retire actual private owner")
        self.ops.append(("clear", owner))
        self.retired.append(owner)

    def scale(self, owner, real, imag=0):
        a, b = Fraction(real), Fraction(imag)
        from math import lcm
        q = lcm(a.denominator, b.denominator)
        self.ops.append(("scale", owner, int(a * q), int(b * q), q))

    def copy(self, target, source):
        if target != source:
            self.ops.extend((("clear", target), ("add", target, source)))

    def accumulate(self, target, source, real=1, imag=0):
        # Staging also preserves the old value when target and source alias.
        temp = self.zero()
        self.copy(temp, source)
        self.scale(temp, real, imag)
        self.ops.append(("add", target, temp))
        self.retire_zero(temp)

    def swap(self, left, right):
        if left == right:
            return
        temp = self.zero()
        self.copy(temp, left)
        self.copy(left, right)
        self.copy(right, temp)
        self.retire_zero(temp)

    def global_lambda(self, owner, direction, dimensions, columns, sign):
        require(sign in (-1, 1) and 0 < direction < 1 << dimensions, "selected global LAMBDA")
        temp = self.zero()
        self.copy(temp, owner)
        self.monomial(temp, Monomial(tuple(1 << i for i in range(dimensions)),
                                     direction, 0, (0,) * dimensions, ()), columns)
        half = Fraction(1, 2)
        self.scale(owner, half, sign * half)
        self.scale(temp, half, -sign * half)
        self.ops.append(("add", owner, temp))
        self.retire_zero(temp)

    def monomial(self, owner, mono, columns=1, start=0):
        require(type(columns) is int and columns > 0
                and start >= 0 and start + len(mono.rows) * columns <= self.n, "whole-column placement")
        # unit is the columnwise i gate. A source multiplicity c contributes c
        # copies, hence i^(a*c*f) after the later external lift f.
        for op, *axes in mono.gates():
            if op == "unit":
                self.ops.extend(("unit", owner) for _ in range(columns))
            else:
                for j in range(columns):
                    self.ops.append((op, owner, *(start + i * columns + j for i in axes)))

    def move(self, owner, order, inverse):
        require(sorted(order) == list(range(self.n)), "complete whole-job permutation")
        # Output coordinate j receives input coordinate order[j].
        rows = tuple(1 << i for i in order)
        if inverse:
            rows = tuple(1 << order.index(i) for i in range(self.n))
        self.monomial(owner, Monomial(rows, 0, 0, (0,) * self.n, ()))
        self.moves.append((owner, tuple(order), inverse))

    def leaf(self, owner, axis):
        require(0 <= owner < self.next_owner and 0 <= axis < self.n, "positive rank-one leaf")
        self.ops.append(("paid", owner, axis))
        self.paid_sites.append((owner, axis))

    def finish(self):
        # Charge a complete final clear even for an already zero private owner.
        for owner in range(self.productive, self.next_owner):
            self.ops.append(("clear", owner))
        return {"dimension": self.n, "productive": self.productive,
                "owned": self.next_owner - self.productive, "ops": tuple(self.ops),
                "paid": len(self.paid_sites), "instructions": len(self.ops)}
