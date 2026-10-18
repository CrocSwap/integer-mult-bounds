"""Intermediate-permutation descriptors for a complete mixed fallback word.

Covariance and diagonal-pair descriptors: source527, PR2159 and PR2188.
This continuation binds every shear, inverse chronology and physical index.
Jose Manuel, with substantial OpenAI Codex assistance; Apache-2.0.
"""
from dataclasses import dataclass
from math import gcd, prod

from descriptor import (Root, Good, FallbackPair, elimination, good_pivots,
                        projector, residual, require, identity)
from controlled_normalizer import Arithmetic


@dataclass(frozen=True)
class Header:
    q: int
    width: int
    low: tuple
    high: tuple
    axes: tuple

    @property
    def dimension(self):
        return len(self.low)

    def read(self, arithmetic, low_only=False):
        m = self.dimension
        require(1 <= len(self.axes) < m <= 64, "header projector dimension")
        require(len(set(self.axes)) == len(self.axes) and
                all(0 <= i < m for i in self.axes), "header projector axes")
        require(len(self.high) == m and
                all(len(row) == m for row in self.low + self.high), "header extent")
        cap = self.q ** (self.width - 1)
        out = []
        for a, b in zip(self.low, self.high):
            row = []
            for x, y in zip(a, b):
                require(0 <= x < self.q and 0 <= y < cap, "header digit range")
                arithmetic.prefix_cells += 2
                row.append(x + (0 if low_only else self.q * y))
            out.append(row)
        return out


@dataclass(frozen=True)
class Ancestor:
    kind: str
    header: Header
    field: int = 0
    reverse: bool = False


@dataclass(frozen=True)
class Prefix:
    root_size: int
    root_unit: int
    ancestors: tuple
    current: Header


@dataclass(frozen=True)
class Coefficient:
    kind: str
    first: int = 0
    second: int = 0
    scalar: int = 1
    permutation: tuple = ()
    reduction_index: int = -1


@dataclass(frozen=True)
class Instruction:
    kind: str
    target: int
    source: int
    coefficient: Coefficient


@dataclass
class Prepared:
    prefix: Prefix
    weights: object
    matrix: list
    plan: object
    columns: int
    operations: tuple
    arithmetic: Arithmetic
    matrix_preparations: int

    @property
    def dimension(self):
        return self.prefix.current.dimension

    @property
    def modulus(self):
        return self.plan.modulus


def annotated_reductions(plan):
    pi = list(range(len(plan.diagonal)))
    out = []
    for index, (kind, i, k, c) in enumerate(plan.operations):
        out.append((kind, i, k, c, tuple(pi), index))
        if kind == "swap":
            pi[i], pi[k] = pi[k], pi[i]
    require(tuple(pi) == plan.permutation, "complete original-row permutation")
    return out


def compile_program(plan):
    n, modulus = len(plan.diagonal), plan.modulus
    unit = Coefficient("unit")
    out = []
    for i, diagonal in enumerate(plan.diagonal[:-1]):
        out.append(Instruction("swap", i, n-1, unit))
        out.append(Instruction("swap", i, n-1,
                   Coefficient("pair", i, n-1, diagonal, plan.permutation)))
    sign = prod(plan.diagonal) % modulus
    require(sign in (1, modulus-1), "fallback determinant sign")
    if sign != 1:
        out.append(Instruction("sign", n-1, -1, Coefficient("fixed", scalar=-1)))
    for kind, i, k, c, pi, index in reversed(annotated_reductions(plan)):
        if kind == "swap":
            out.append(Instruction("swap", i, k, unit))
            continue
        coefficient = Coefficient("shear", i, k, -c % modulus, pi, index)
        if i > k:
            out.append(Instruction("lower", i, k, coefficient))
        else:
            out.extend((Instruction("swap", i, k, unit),
                        Instruction("lower", k, i, coefficient),
                        Instruction("swap", i, k, unit)))
    require(all(op.target > op.source for op in out if op.kind == "lower"),
            "ordered physical ADD fields")
    return tuple(out)


def prepare(prefix, low_only_ancestors=False, low_only_current=False):
    header = prefix.current
    require(header.q >= 3 and header.q % 2 and header.width >= 1, "odd ring domain")
    modulus = header.q ** header.width
    arithmetic = Arithmetic(modulus)
    weights = Root(prefix.root_size, modulus, prefix.root_unit)
    preparations = 0
    for ancestor in prefix.ancestors:
        h = ancestor.header
        require((h.q, h.width) == (header.q, header.width), "fixed radix and atom width")
        f = weights.size // h.dimension
        require(f >= 1, "proper ancestor block extent")
        p = projector(h.read(arithmetic, low_only_ancestors), h.axes, modulus)
        preparations += 1
        if ancestor.kind == "good":
            pivots = good_pivots(p, len(h.axes), modulus)
            weights = Good(weights, h.dimension, f, pivots)
        elif ancestor.kind == "pair":
            plan = elimination(residual(p, modulus), modulus)
            weights = FallbackPair(weights, h.dimension, f, plan,
                                   ancestor.field, ancestor.reverse)
        else:
            raise ValueError("unknown ancestor descriptor")
    f = weights.size // header.dimension
    require(f >= 1, "current fallback block extent")
    p = projector(header.read(arithmetic, low_only_current), header.axes, modulus)
    matrix = residual(p, modulus)
    plan = elimination(matrix, modulus)
    return Prepared(prefix, weights, matrix, plan, f, compile_program(plan),
                    arithmetic, preparations + 1)


def bank_weight(prepared, row, column):
    m, f = prepared.dimension, prepared.columns
    require(0 <= row < 2*m and 0 <= column < f, "bank weight index")
    if row >= m:
        return 1
    prepared.arithmetic.counts["descriptor_value_requests"] += 1
    value = prepared.weights.value(row*f + column)
    require(gcd(value, prepared.modulus) == 1, "generated ancestor unit")
    return value


def coefficient(prepared, descriptor, column, final_permutation=False):
    if descriptor.kind == "unit":
        return 1
    if descriptor.kind == "fixed":
        return descriptor.scalar % prepared.modulus
    if descriptor.kind == "pair":
        numerator_row = descriptor.permutation[descriptor.first]
        denominator_row = descriptor.first
    elif descriptor.kind == "shear":
        pi = prepared.plan.permutation if final_permutation else descriptor.permutation
        numerator_row, denominator_row = pi[descriptor.first], pi[descriptor.second]
    else:
        raise ValueError("unknown coefficient descriptor")
    a = bank_weight(prepared, numerator_row, column)
    b = bank_weight(prepared, denominator_row, column)
    return prepared.arithmetic.mul(descriptor.scalar,
           prepared.arithmetic.mul(a, prepared.arithmetic.inv(b)))


def physical_atom(field, column, m, f):
    return field*f + (column if field < m else f-1-column)


def child_descriptor(prepared, operation):
    require(operation.kind == "swap", "weighted child operation")
    if operation.coefficient.kind == "unit":
        return Root(prepared.columns, prepared.modulus)
    require(operation.coefficient.kind == "pair" and
            operation.target == operation.coefficient.first and
            operation.source == 2*prepared.dimension-1, "fallback pair child binding")
    return FallbackPair(prepared.weights, prepared.dimension, prepared.columns,
                        prepared.plan, operation.target,
                        operation.target >= prepared.dimension)


def logical_column(field, atom, m, f):
    require(0 <= atom < f, "physical atom extent")
    return atom if field < m else f-1-atom


def shape(operations):
    return tuple((x.kind, x.target, x.source, x.coefficient.kind,
                  x.coefficient.reduction_index) for x in operations)


def reconstruct(prepared, column, final_permutation=False):
    """Full ADDRESS operator; payload execution uses the separate stream code."""
    n, modulus = 2*prepared.dimension, prepared.modulus
    out = identity(n)
    for op in prepared.operations:
        i, k = op.target, op.source
        c = coefficient(prepared, op.coefficient, column, final_permutation)
        if op.kind == "lower":
            if c:
                out[i] = [(x+c*y) % modulus for x, y in zip(out[i], out[k])]
        elif op.kind == "swap":
            a, b = out[i], out[k]
            out[i] = [c*x % modulus for x in b]
            inverse = pow(c, -1, modulus)
            out[k] = [inverse*x % modulus for x in a]
        else:
            out[i] = [c*x % modulus for x in out[i]]
    return out


def paid_children(prepared):
    f, m = prepared.columns, prepared.dimension
    widths = []
    for op in prepared.operations:
        if op.kind != "swap":
            continue
        same_orientation = (op.target < m) == (op.source < m)
        if same_orientation and f//2:
            widths.append(f//2)
        widths.append(f)
        if same_orientation and f//2:
            widths.append(f//2)
    return widths
