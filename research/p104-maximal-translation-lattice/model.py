"""Separate finite model of the literal Gaussian lifting word. Apache-2.0.

Public vector boundaries accept ranks 0..7 and signed components of at most
4096 magnitude bits. Exhaustive tables are limited separately to ranks 1..2.
The all-rank mathematical theorem is in PROOF.md, not inferred from these caps.
"""

from itertools import product


def need(condition, message):
    if not condition:
        raise ValueError(message)


def checked(value, rank):
    need(type(rank) is int and 0 <= rank <= 7, "rank must be in 0..7")
    need(len(value) == 2 << rank, "interleaved real dimension")
    need(
        all(type(x) is int and x.bit_length() <= 4096 for x in value),
        "signed integer component limit",
    )
    return list(value)


def pair(a, b, inverse=False):
    """Internal pair on two Gaussian integer tuples, with Euclidean floors."""
    real, imag = a[0] - b[0], a[1] - b[1]
    mid_real, mid_imag = b[0] + real // 2, b[1] + imag // 2
    real, imag = (imag, -real) if inverse else (-imag, real)
    out_b = mid_real - real // 2, mid_imag - imag // 2
    return (out_b[0] + real, out_b[1] + imag), out_b


def lift(value, rank, inverse=False):
    rows = checked(value, rank)
    stages = reversed(range(rank)) if inverse else range(rank)
    for bit in stages:
        for first in range(1 << rank):
            if first & (1 << bit):
                continue
            second = first ^ (1 << bit)
            a, b = pair(
                rows[2 * first : 2 * first + 2],
                rows[2 * second : 2 * second + 2],
                inverse,
            )
            rows[2 * first : 2 * first + 2] = a
            rows[2 * second : 2 * second + 2] = b
    return rows


def linear_stage(rows, bit):
    """Integer numerator of one ideal stage, deliberately without division."""
    result = list(rows)
    for first in range(len(rows) // 2):
        if first & (1 << bit):
            continue
        second = first ^ (1 << bit)
        ar, ai = rows[2 * first : 2 * first + 2]
        br, bi = rows[2 * second : 2 * second + 2]
        result[2 * first : 2 * first + 2] = ar - ai + br + bi, ar + ai - br + bi
        result[2 * second : 2 * second + 2] = ar + ai + br - bi, -ar + ai + br + bi
    return result


def ideal_numerator(value, rank):
    rows = checked(value, rank)
    for bit in range(rank):
        rows = linear_stage(rows, bit)
    return rows


def member(value, rank):
    """Direct prefix conditions on one vector, with exact integer divisions."""
    rows = checked(value, rank)
    for bit in range(rank):
        for first in range(1 << rank):
            if first & (1 << bit):
                continue
            second = first ^ (1 << bit)
            if any((rows[2 * first + c] - rows[2 * second + c]) % 2 for c in range(2)):
                return False
        following = linear_stage(rows, bit)
        need(all(x % 2 == 0 for x in following), "prefix ideal integrality")
        rows = [x // 2 for x in following]
    return True


def error(value, rank):
    """Return 2**rank times the nonlinear error, including nonintegral U(x)."""
    return tuple(
        (y << rank) - u
        for y, u in zip(lift(value, rank), ideal_numerator(value, rank), strict=True)
    )


def encode(value, modulus):
    result = 0
    for component in value:
        result = result * modulus + component % modulus
    return result


def census(rank):
    """Reject every nonperiod at rank <=2 using three explicit base points."""
    need(type(rank) is int and 1 <= rank <= 2, "census rank must be 1 or 2")
    dimension, modulus = 2 << rank, 1 << (rank // 2 + 1)
    vectors = list(product(range(modulus), repeat=dimension))
    errors = [error(x, rank) for x in vectors]
    candidates = list(range(len(vectors)))
    counts = []
    # IDs 1 and modulus are the last two real coordinate unit vectors.
    for probe in (0, 1, modulus):
        x = vectors[probe]
        candidates = [
            z
            for z in candidates
            if errors[
                encode([a + b for a, b in zip(x, vectors[z], strict=True)], modulus)
            ]
            == errors[probe]
        ]
        counts.append(len(candidates))
    actual = [i for i, z in enumerate(vectors) if member(z, rank)]
    need(candidates == actual, "period probes do not force every prefix condition")
    # These scalar generators justify the modular wrap in the table lookup.
    for j in range(dimension):
        z = [int(i == j) * modulus for i in range(dimension)]
        need(member(z, rank), "table modulus is not a sufficient translation")
    return dict(
        rank=rank,
        modulus=modulus,
        shifts=len(vectors),
        probe_ids=[0, 1, modulus],
        survivor_counts=counts,
        periods=len(actual),
        nonperiods_rejected=len(vectors) - len(actual),
    )
