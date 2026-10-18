"""Independent, exact tensor-character oracle for the synthetic transform.

This file deliberately contains no butterfly recursion, simulated slot moves,
chunk exchanges, or imports from any other implementation.  Axis zero is the
most significant coordinate of a record address.  Polynomial coefficients are
in increasing powers of y in Z[y]/(y**r + 1), with r = 2**ell.

Arithmetic API convention: ``direct_basis`` and ``direct_transform`` return
INTEGER NUMERATORS with common denominator M = product(axis lengths).  Thus
their returned matrix is M times the normalized operator, in either direction.
The forward operator is L B F^-; the opposite operator is F^+ B^-1 L^-1.
In particular, an opposite input record number is a PHYSICAL address.
"""

from __future__ import annotations

from collections.abc import Sequence


def _exponents(ell: int, K: int, long_axes: Sequence[bool]) -> tuple[int, ...]:
    if type(ell) is not int or ell < 2:
        raise ValueError("ell must be an integer at least 2")
    if type(K) is not int or not 1 <= K < ell:
        raise ValueError("K must satisfy 1 <= K <= ell - 1")
    if not long_axes or any(type(flag) is not bool for flag in long_axes):
        raise ValueError("long_axes must be a nonempty sequence of booleans")
    return tuple(ell if flag else ell - 1 for flag in long_axes)


def _coordinates(index: int, exponents: Sequence[int]) -> tuple[int, ...]:
    if type(index) is not int or not 0 <= index < (1 << sum(exponents)):
        raise ValueError("record address is outside the tensor array")
    result = []
    for exponent in reversed(exponents):
        result.append(index & ((1 << exponent) - 1))
        index >>= exponent
    return tuple(reversed(result))


def closed_form_slots(
    ell: int, K: int, long_axes: Sequence[bool]
) -> list[tuple[int, int]]:
    """Return final L slot order as (zero-based axis, named bit h).

    This is a direct expression for the target order, not the paper's sequence
    of prefix insertions and chunk swaps.  Bits are listed most significant
    first; the polynomial suffix is not part of the address permutation.
    """
    _exponents(ell, K, long_axes)
    D = len(long_axes)
    q, b = divmod(ell - 1, K)
    return (
        [(axis, ell - 1) for axis in range(D) if long_axes[axis]]
        + [(axis, h) for h in range(b - 1, -1, -1) for axis in range(D)]
        + [
            (axis, ell - 2 - chunk * K - offset)
            for chunk in range(q)
            for axis in range(D)
            for offset in range(K)
        ]
    )


def address_from_logical(
    index: int, ell: int, K: int, long_axes: Sequence[bool]
) -> int:
    """Return L(index), using integer fields rather than simulated moves.

    The input is an ordinary axis-major address.  This function applies L
    alone: pass reverse_axis_bits(index, exponents) first to obtain L(B(index)).
    """
    exponents = _exponents(ell, K, long_axes)
    coordinates = _coordinates(index, exponents)
    q, b = divmod(ell - 1, K)
    result = 0
    for axis, flag in enumerate(long_axes):
        if flag:
            result = (result << 1) | (coordinates[axis] >> (ell - 1))
    for h in range(b - 1, -1, -1):
        for coordinate in coordinates:
            result = (result << 1) | ((coordinate >> h) & 1)
    mask = (1 << K) - 1
    for chunk in range(q):
        shift = ell - 1 - K * (chunk + 1)
        for coordinate in coordinates:
            result = (result << K) | ((coordinate >> shift) & mask)
    return result


def logical_from_address(
    index: int, ell: int, K: int, long_axes: Sequence[bool]
) -> int:
    """Return L^-1(index) by assigning named bits from the final slot formula."""
    exponents = _exponents(ell, K, long_axes)
    _coordinates(index, exponents)  # validates the total address width
    coordinates = [0] * len(exponents)
    slots = closed_form_slots(ell, K, long_axes)
    for position, (axis, h) in enumerate(slots):
        coordinates[axis] |= ((index >> (len(slots) - 1 - position)) & 1) << h
    result = 0
    for exponent, coordinate in zip(exponents, coordinates):
        result = (result << exponent) | coordinate
    return result


def reverse_axis_bits(index: int, exponents: Sequence[int]) -> int:
    """Return B(index), reversing each axis's bits separately.

    ``exponents`` contains log2(axis length), not the axis lengths themselves.
    This is an involution and therefore also computes B^-1.
    """
    if not exponents or any(type(a) is not int or a < 0 for a in exponents):
        raise ValueError("exponents must be a nonempty sequence of nonnegative integers")
    coordinates = _coordinates(index, exponents)
    result = 0
    for exponent, coordinate in zip(exponents, coordinates):
        for h in range(exponent):
            result = (result << 1) | ((coordinate >> h) & 1)
    return result


def _direction_sign(direction: str) -> int:
    if direction == "forward":
        return -1
    if direction == "opposite":
        return 1
    raise ValueError("direction must be 'forward' or 'opposite'")


def direct_basis(
    ell: int,
    K: int,
    long_axes: Sequence[bool],
    input_record: int,
    input_coefficient: int = 0,
    direction: str = "forward",
) -> list[list[int]]:
    """Compute M times a normalized basis column by the tensor character.

    Input has the single value y**input_coefficient at input_record.  Return
    M rows, each containing r integer coefficients.  Every row has precisely
    one coefficient equal to +1 or -1; all others vanish.  In the forward
    direction input_record is axis-major and outputs are physical L B order.
    In the opposite direction input_record is physical L B order and outputs
    are axis-major.  No division or floating-point arithmetic is performed.
    """
    exponents = _exponents(ell, K, long_axes)
    r = 1 << ell
    M = 1 << sum(exponents)
    if type(input_coefficient) is not int or not 0 <= input_coefficient < r:
        raise ValueError("input coefficient must be in range(r)")
    _coordinates(input_record, exponents)
    sign = _direction_sign(direction)
    logical_input = input_record
    if sign == 1:
        logical_input = reverse_axis_bits(
            logical_from_address(input_record, ell, K, long_axes), exponents
        )
    source = _coordinates(logical_input, exponents)
    root_steps = tuple((2 * r) >> a for a in exponents)
    result = [[0] * r for _ in range(M)]
    for logical_output in range(M):
        target = _coordinates(logical_output, exponents)
        power = (
            input_coefficient
            + sign * sum(step * j * k for step, j, k in zip(root_steps, target, source))
        ) % (2 * r)
        output_record = logical_output
        if sign == -1:
            output_record = address_from_logical(
                reverse_axis_bits(logical_output, exponents), ell, K, long_axes
            )
        result[output_record][power % r] = 1 if power < r else -1
    return result


def direct_transform(
    ell: int,
    K: int,
    long_axes: Sequence[bool],
    values: Sequence[Sequence[int]],
    direction: str = "forward",
) -> list[list[int]]:
    """Return M times the normalized transform of an integer coefficient array.

    Uses the direct double tensor sum, without any factorization into rounds.
    This intentionally quadratic oracle is intended for small exact checks.
    Its output has the same common denominator M as ``direct_basis``.
    """
    exponents = _exponents(ell, K, long_axes)
    r = 1 << ell
    M = 1 << sum(exponents)
    sign = _direction_sign(direction)
    if len(values) != M or any(len(row) != r for row in values):
        raise ValueError("values must have shape M by r")
    if any(type(value) is not int for row in values for value in row):
        raise ValueError("values must contain integer coefficients")
    coordinates = [_coordinates(index, exponents) for index in range(M)]
    retained = [
        address_from_logical(reverse_axis_bits(index, exponents), ell, K, long_axes)
        for index in range(M)
    ]
    root_steps = tuple((2 * r) >> a for a in exponents)
    result = [[0] * r for _ in range(M)]
    for logical_output, target in enumerate(coordinates):
        output_record = retained[logical_output] if sign == -1 else logical_output
        output = result[output_record]
        for logical_input, source in enumerate(coordinates):
            input_record = logical_input if sign == -1 else retained[logical_input]
            power = sign * sum(
                step * j * k for step, j, k in zip(root_steps, target, source)
            )
            for coefficient, value in enumerate(values[input_record]):
                if value:
                    reduced = (power + coefficient) % (2 * r)
                    output[reduced % r] += value if reduced < r else -value
    return result
