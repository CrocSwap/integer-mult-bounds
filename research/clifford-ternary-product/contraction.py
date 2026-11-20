"""Decode the three local product observations of two real stabilizer charts."""

from dataclasses import dataclass


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit
        mask ^= bit


def monomials(affine):
    # The low bit of an affine expression is its constant.
    if affine & 1:
        yield 0
    yield from bits(affine & ~1)


def reduce_rows(rows):
    """Return a basis of the affine equations, or None for empty support."""
    basis = {}
    for row in rows:
        while row > 1:
            pivot = row.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = row
                break
            row ^= basis[pivot]
        if row == 1:
            return None
    return tuple(basis.values())


@dataclass(frozen=True)
class Chart:
    # A monomial is the mask of its variables. The empty mask means one.
    rows: tuple
    phase: frozenset

    def substitute(self, variable, affine):
        rows = tuple(row ^ variable ^ affine if row & variable else row
                     for row in self.rows)
        phase = set()
        for term in self.phase:
            if term & variable:
                rest = term ^ variable
                for singleton in monomials(affine):
                    phase.symmetric_difference_update((rest | singleton,))
            else:
                phase.symmetric_difference_update((term,))
        return Chart(rows, frozenset(phase))

    def reduced(self):
        rows = reduce_rows(self.rows)
        return None if rows is None else Chart(rows, self.phase)


def embed(mask, side):
    result = 0
    for bit in bits(mask):
        index = bit.bit_length() - 1
        result |= 1 << (2 * index + 1 + side)
    return result


def joint(left, right, signed_left, signed_right):
    """Produce the joint chart on the interleaved operand site variables."""
    if left.m != right.m:
        raise ValueError("The operands must use the same site count")
    if left.zero or right.zero:
        return None
    rows = []
    phase = set()
    for side, operand, use_phase in ((0, left, signed_left), (1, right, signed_right)):
        rows.extend(embed(mask, side) | rhs for mask, rhs in operand.equations)
        if use_phase:
            if operand.constant:
                phase.symmetric_difference_update((0,))
            phase.update(embed(term, side) for term in bits(operand.linear_mask))
            phase.update(embed(term, side) for term in operand.cross_terms)
    return Chart(tuple(rows), frozenset(phase))


def project(chart, remaining, digit):
    """Return a chart with one fewer pair and its extra power of two."""
    if chart is None:
        return None, 0
    x = 1 << (2 * remaining - 1)
    y = x << 1
    if digit != 1:
        fixed = digit // 2
        return chart.substitute(y, fixed).substitute(x, fixed).reduced(), 0
    restricted = chart.substitute(y, 1 | x)
    pivot = next((row for row in restricted.rows if row & x), None)
    if pivot is not None:
        return restricted.substitute(x, pivot ^ x).reduced(), 0
    partial = set()
    derivative = 0
    for term in restricted.phase:
        if term & x:
            derivative ^= (term ^ x) or 1
        else:
            partial.add(term)
    reduced = Chart((*restricted.rows, derivative), frozenset(partial)).reduced()
    return reduced, int(reduced is not None)


@dataclass
class Frame:
    chart: Chart | None
    remaining: int
    offset: int
    next_child: int = 0


def events(chart, m, negative=False):
    """Emit unit head moves and signed unit deposits in one ternary traversal."""
    stack = [Frame(chart, m, 0)]
    while stack:
        frame = stack[-1]
        if frame.remaining == 0:
            if frame.chart is not None:
                yield "-" if (0 in frame.chart.phase) != negative else "+"
            yield ">"
        elif frame.next_child != 3:
            digit = frame.next_child
            frame.next_child += 1
            child, shift = project(frame.chart, frame.remaining, digit)
            if shift:
                yield ">"
            stack.append(Frame(child, frame.remaining - 1, shift))
            continue
        stack.pop()
        if frame.offset:
            yield "<"


def product_passes(left, right):
    for signed_right in (False, True):
        for signed_left in (False, True):
            chart = joint(left, right, signed_left, signed_right)
            yield events(chart, left.m, signed_left != signed_right)
