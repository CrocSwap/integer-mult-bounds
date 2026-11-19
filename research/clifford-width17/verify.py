#!/usr/bin/env python3
"""Exact finite checks of the width-17 four-qubit Clifford interpolant."""

from collections import Counter
from itertools import combinations, product


def require(condition, message):
    if not condition:
        raise ValueError(message)


def mobius(rank):
    return (-1) ** rank * (1 << (rank * (rank - 1) // 2))


def subspaces(bits):
    """Enumerate unique reduced-row-echelon bases, with low-bit pivots."""
    for rank in range(bits + 1):
        for pivots in combinations(range(bits), rank):
            choices = []
            for pivot in pivots:
                row_options = [1 << pivot]
                for column in range(pivot + 1, bits):
                    if column not in pivots:
                        row_options += [row | (1 << column) for row in row_options]
                choices.append(row_options)
            yield from product(*choices)


def span(basis):
    values = [0]
    for row in basis:
        values += [value ^ row for value in values]
    return values


def affine_cube(x, y, z, offset):
    return (offset, offset ^ x, offset ^ y, offset ^ x ^ y,
            offset ^ z, offset ^ z ^ x, offset ^ z ^ y, offset ^ z ^ x ^ y)


def code_columns(basis):
    # Each block evaluates u1, u2, u3, 1 at all eight binary triples.
    rows = basis + (0,) * (8 - len(basis))
    return affine_cube(*rows[:4]) + affine_cube(*rows[4:])


def row_masks(columns, dim):
    return tuple(sum(((point >> j) & 1) << t for t, point in enumerate(columns))
                 for j in range(dim))


def verify_code():
    checked_pairs = 0
    for dim in range(9):
        units = tuple(1 << j for j in range(dim))
        columns = code_columns(units)
        masks = row_masks(columns, dim)
        words = span(masks)
        require(len(set(words)) == 1 << dim, "rank-deficient shortened generator")
        require(all(w.bit_count() % 4 == 0 for w in words), "quarter phase survives")
        for a, b in combinations(masks, 2):
            require((a & b).bit_count() % 2 == 0, "quadratic phase survives")
            checked_pairs += 1
        if dim < 8:
            require(0 in columns, "shortened generator lacks its zero column")
    return checked_pairs


# Gaussian integer pairs. Each test operator carries a common positive denominator.
ONE = (1, 0)
I = (0, 1)
ZERO = (0, 0)


def times(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def conjugate(a):
    return a[0], -a[1]


def kron(a, b):
    return [[times(x, y) for x in row_a for y in row_b]
            for row_a in a for row_b in b]


def tensor(factors):
    result = [[ONE]]
    for matrix in factors:
        result = kron(result, matrix)
    return result


def relative_matrix(a, b):
    """Literal matrix product a* b for Gaussian integer numerator matrices."""
    output = []
    for ca in zip(*a):
        row = []
        for cb in zip(*b):
            values = [times(conjugate(x), y) for x, y in zip(ca, cb)]
            row.append(tuple(map(sum, zip(*values))))
        output.append(row)
    return output


def bell(matrix):
    # Entry at (shift a, Fourier index b) of the unprepared normalized Choi state.
    # Suppress the common positive denominator 16 times the matrix denominator.
    result = []
    for b in range(16):
        for a in range(16):
            real = imag = 0
            for x in range(16):
                sign = (-1) ** ((b & x).bit_count() % 2)
                u, v = matrix[x ^ a][x]
                real += sign * u
                imag += sign * v
            result.append((real, imag))
    return result


def phase_profile(vector):
    """Return support and phase relative to its first nonzero amplitude."""
    first = next(z for z in vector if z != ZERO)
    rotations = [first]
    for _ in range(3):
        rotations.append(times(rotations[-1], I))
    lookup = {phase: k for k, phase in enumerate(rotations)}
    require(all(z == ZERO or z in lookup for z in vector), "unequal moduli/phase cosets")
    return [None if z == ZERO else lookup[z] for z in vector]


def basis_of_linear_support(support):
    require(0 in support, "linear support misses origin")
    reached = {0}
    basis = []
    for x in sorted(support):
        if x not in reached:
            basis.append(x)
            reached |= {y ^ x for y in reached}
    require(reached == support, "support through zero is not a flat")
    return tuple(basis)


def literal_detector(phase, check_full):
    # Skip K outside the support: their 16 evaluation points span K, so at
    # least one amplitude vanishes. Evaluate every surviving ordered monomial.
    if phase[0] is None:
        return (0, 0)
    support = {j for j, exponent in enumerate(phase) if exponent is not None}
    basis = basis_of_linear_support(support)
    images = span(basis)
    by_phase = [0] * 4
    for sub in subspaces(len(basis)):
        actual = tuple(images[combination] for combination in sub)
        columns = code_columns(actual)
        exponent = sum(phase[x] for x in columns) % 4
        require(exponent == 0, "nonzero phase on a supported code tuple")
        by_phase[exponent] += mobius(len(sub))
        if check_full is not None:
            check_full[len(sub)] += 1
    return by_phase[0] - by_phase[2], by_phase[1] - by_phase[3]


def actual_matrices():
    identity = [[ONE, ZERO], [ZERO, ONE]]
    x = [[ZERO, ONE], [ONE, ZERO]]
    s = [[ONE, ZERO], [ZERO, I]]
    # h = (1+i) H/sqrt(2), represented by its numerator over 2:
    # h = (1+i)[[1,1],[1,-1]]/2. Its global phase is immaterial.
    h = [[(1, 1), (1, 1)], [(1, 1), (-1, -1)]]
    hs = [[(1, 1), (-1, 1)], [(1, 1), (1, -1)]]
    cnot = [[ONE if row == (col ^ ((col >> 1) & 1)) else ZERO
             for col in range(16)] for row in range(16)]
    return [
        ("identity", tensor([identity] * 4), 1),
        ("Pauli X", tensor([identity] * 3 + [x]), 1),
        ("phase", tensor([identity] * 3 + [s]), 1),
        ("CNOT", cnot, 1),
        ("four Hadamards", tensor([h] * 4), 16),
        ("four HS gates", tensor([hs] * 4), 16),
        ("Hadamard and three HS gates", tensor([h, hs, hs, hs]), 16),
    ]


def verify_matrices():
    fixtures = actual_matrices()
    full_counts = Counter()
    support_sizes = []
    comparisons = 0
    for i, (source, a, da) in enumerate(fixtures):
        for j, (target, b, db) in enumerate(fixtures):
            vector = bell(relative_matrix(a, b))
            # Norm one including the suppressed common denominator.
            require(sum(u*u + v*v for u, v in vector) == (16 * da * db) ** 2,
                    f"normalization failed: {source}, {target}")
            phases = phase_profile(vector)
            support = {position for position, phase in enumerate(phases) if phase is not None}
            origin = min(support)
            basis_of_linear_support({x ^ origin for x in support})
            if i == 0:
                support_sizes.append(len(support))
            if i == j:
                require(vector[0] == (16 * da * db, 0) and support == {0},
                        "target maps to e0")
            counts = full_counts if (i, j) == (0, 5) else None
            result = literal_detector(phases, counts)
            require(result == (int(i == j), 0), f"decoder failed: {source}, {target}")
            comparisons += 1
    require(support_sizes == [1, 1, 2, 4, 16, 256, 128], "literal support sizes")
    require(sum(full_counts.values()) == 417199, "eight-axis subspace count")
    norm_squared = sum(count * mobius(k) ** 2 for k, count in full_counts.items())
    require(norm_squared == 73190789644335724, "ordered row squared norm")
    return comparisons, full_counts, norm_squared


def controls():
    # A shifted hyperplane containing all points of the full 16-word generator.
    # Shorter prefixes all include zero, which is outside this flat.
    plane = {x for x in range(256) if (x & 136).bit_count() % 2}
    _, matrix, _ = actual_matrices()[-1]
    phase = phase_profile(bell(matrix))
    require({x for x in range(256) if phase[x] is not None} == plane,
            "literal H tensor (HS)^3 does not give the anchor hyperplane")
    full_points = code_columns(tuple(1 << j for j in range(8)))
    require(all(phase[x] is not None for x in full_points),
            "full code tuple misses a nonzero literal amplitude")
    # Work relative to the first nonzero amplitude raised to the 16th power.
    # Ranks 0..7 contribute zero because their tuple has a zero coordinate.
    root = (ONE, I, (-1, 0), (0, -1))[sum(phase[x] for x in full_points) % 4]
    unanchored = times((mobius(8), 0), root)
    require(sum(t*t for t in unanchored) == 1 << 56
            and literal_detector(phase, None) == ZERO, "missing-anchor variant escaped")
    # One lost generator coordinate already leaks a linear quarter phase.
    full = code_columns(tuple(1 << j for j in range(8)))
    bad = list(full)
    bad[0] = 0
    require(sum((x >> 3) & 1 for x in bad) % 4 != 0, "bad weight escaped")
    # Two weight-four rows can share a single entry unless orthogonality is checked.
    pair = (0b00001111, 0b01110001)
    require(all(x.bit_count() == 4 for x in pair)
            and (2 * (pair[0] & pair[1]).bit_count()) % 4 == 2, "bad overlap escaped")
    # Evaluate the unsigned variant on the flat indicator for {0,1}.
    line = {0, 1}
    unsigned = sum(abs(mobius(len(sub))) for sub in subspaces(1)
                   if all(x in line for x in code_columns(sub)))
    line_profile = [0 if x in line else None for x in range(256)]
    require(unsigned == 2 and literal_detector(line_profile, None) == ZERO,
            "unsigned Möbius variant escaped")
    # A rank-deficient generator fails the span implication used to discard flats.
    require(len(set(span(row_masks((0,) * 16, 1)))) != 2, "zero-row variant escaped")
    return 5


def main():
    checked_pairs = verify_code()
    comparisons, counts, norm_squared = verify_matrices()
    rejected = controls()
    print(f"PASS_CLIFFORD_WIDTH17 code_pair_checks={checked_pairs}"
          f" literal_matrices=7 relative_matrices=49 decoder_checks={comparisons}"
          f" flats_by_dimension={','.join(str(counts[k]) for k in range(9))}"
          f" full_support_tuples={sum(counts.values())} row_norm_squared={norm_squared}"
          f" rejecting_controls={rejected}")


if __name__ == "__main__":
    main()
