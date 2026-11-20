"""Recognise a quadratic Boolean indicator on Cantor-addressed operand bits."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Operand:
    m: int
    equations: tuple
    constant: int
    linear_mask: int
    cross_terms: tuple
    zero: bool

    def value(self, x):
        """Return the sparse defect at a binary site, including its support test."""
        if any((mask & x).bit_count() % 2 != rhs for mask, rhs in self.equations):
            return 0
        value = self.constant ^ ((self.linear_mask & x).bit_count() % 2)
        for mask in self.cross_terms:
            value ^= int((x & mask) == mask)
        return value


def cantor_flags(m):
    """Visit the complete ternary rectangle in little-endian address order."""
    # A frame has the next child number and the validity of its prefix.
    # The bottom and top tape marks give the depth tests on a sequential tape.
    stack = [[0, True]]
    while stack:
        child, valid = stack[-1]
        if len(stack) == m + 1:
            yield valid
            stack.pop()
        elif child == 3:
            stack.pop()
        else:
            stack[-1][0] += 1
            stack.append([0, valid and child != 2])


def _add_direction(basis, vector):
    # Keep a reduced binary basis. A pivot is its original site-bit position.
    for pivot in sorted(basis, reverse=True):
        if vector & (1 << pivot):
            vector ^= basis[pivot]
    if not vector:
        return
    pivot = vector.bit_length() - 1
    bit = 1 << pivot
    for prior in basis:
        if basis[prior] & bit:
            basis[prior] ^= vector
    basis[pivot] = vector


def _fit(values, m):
    origin = next((x for x, bit in enumerate(values) if bit), None)
    if origin is None:
        return Operand(m, (), 0, 0, (), True)
    basis = {}
    for x, bit in enumerate(values):
        if bit:
            _add_direction(basis, x ^ origin)
    pivots = sorted(basis)
    equations = []
    for j in range(m):
        if j in basis:
            continue
        mask = 1 << j
        for h in pivots:
            if (basis[h] >> j) & 1:
                mask ^= 1 << h
        equations.append((mask, (mask & origin).bit_count() % 2))

    # Read the small interpolation table during one compact-tape scan.
    probes = {origin, *(origin ^ basis[h] for h in pivots)}
    for index, i in enumerate(pivots):
        probes.update(origin ^ basis[i] ^ basis[j] for j in pivots[index + 1:])
    samples = {x: bit for x, bit in enumerate(values) if x in probes}
    q0 = samples[origin]
    constant = q0
    linear = 0
    cross = []
    singles = {h: samples[origin ^ basis[h]] for h in pivots}
    for index, i in enumerate(pivots):
        bi = 1 << i
        oi = int(bool(origin & bi))
        if singles[i] ^ q0:
            linear ^= bi
            constant ^= oi
        for j in pivots[index + 1:]:
            if not (q0 ^ singles[i] ^ singles[j] ^ samples[origin ^ basis[i] ^ basis[j]]):
                continue
            bj = 1 << j
            oj = int(bool(origin & bj))
            cross.append(bi | bj)
            linear ^= (bi if oj else 0) ^ (bj if oi else 0)
            constant ^= oi & oj
    result = Operand(m, tuple(equations), constant, linear, tuple(cross), False)
    if all(bit == result.value(x) for x, bit in enumerate(values)):
        return result
    return None


def recognise_sparse(bits, m):
    """Read literal bits in order. Return the affine-quadratic chart or None."""
    if m < 0:
        raise ValueError("The site count must be nonnegative")
    if len(bits) > 3 ** m:
        return None
    source = iter(bits)
    values = bytearray()
    valid_holes = True
    for valid in cantor_flags(m):
        bit = next(source, 0)
        if bit not in (0, 1):
            raise ValueError("A literal bit must have value zero or one")
        if valid:
            values.append(bit)
        elif bit:
            valid_holes = False
    return _fit(values, m) if valid_holes else None
