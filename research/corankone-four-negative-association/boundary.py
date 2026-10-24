#!/usr/bin/env python3
# Copyright 2026 Krzysztof Wojt.
# Created with substantial assistance from OpenAI Codex and Luna.
# SPDX-License-Identifier: Apache-2.0

"""Independent exact enumeration of a four-indicator GL_4(F_2) law.

Each 4x4 matrix is stored as four row bitmasks.  The four indicators are
X_i = 1 exactly when all three leading principal minors of orders 1, 2, and 3
of G (I - e_i e_i^T) G^{-1} are nonzero.  All arithmetic is over F_2.

This is a bounded finite check for this specified distribution.  It does not
establish a claim in other dimensions or over other fields.
"""

from collections import Counter
from itertools import combinations, product


N = 4
FIELD_MATRIX_BITS = 1 << (N * N)
IDENTITY = tuple(1 << r for r in range(N))
SPLIT_SIZES = ((1, 1), (1, 2), (1, 3), (2, 2))


def require(condition, message):
    """A check that remains active when Python is run with -O."""
    if not condition:
        raise RuntimeError(message)


def columns(matrix):
    return tuple(
        sum(((matrix[r] >> c) & 1) << r for r in range(N))
        for c in range(N)
    )


def matmul(left, right):
    right_columns = columns(right)
    return tuple(
        sum(((row & col).bit_count() & 1) << c for c, col in enumerate(right_columns))
        for row in left
    )


def inverse(matrix):
    """Return the literal GF(2) inverse, or None if matrix is singular."""
    augmented = [matrix[r] | (1 << (N + r)) for r in range(N)]
    for c in range(N):
        pivot = next((r for r in range(c, N) if (augmented[r] >> c) & 1), None)
        if pivot is None:
            return None
        augmented[c], augmented[pivot] = augmented[pivot], augmented[c]
        for r in range(N):
            if r != c and ((augmented[r] >> c) & 1):
                augmented[r] ^= augmented[c]
    result = tuple((augmented[r] >> N) & ((1 << N) - 1) for r in range(N))
    require(matmul(matrix, result) == IDENTITY, "computed right inverse failed")
    require(matmul(result, matrix) == IDENTITY, "computed left inverse failed")
    return result


def leading_minor_nonzero(matrix, order):
    """Compute the determinant of the top-left order x order block over F_2."""
    block = [matrix[r] & ((1 << order) - 1) for r in range(order)]
    rank = 0
    for c in range(order):
        pivot = next((r for r in range(rank, order) if (block[r] >> c) & 1), None)
        if pivot is None:
            return False
        block[rank], block[pivot] = block[pivot], block[rank]
        for r in range(rank + 1, order):
            if (block[r] >> c) & 1:
                block[r] ^= block[rank]
        rank += 1
    return True


PROJECTORS = tuple(
    tuple((1 << r) ^ ((1 << r) if r == i else 0) for r in range(N))
    for i in range(N)
)


def indicators_for(matrix, inv, use_inverse=True):
    values = []
    for projector in PROJECTORS:
        if use_inverse:
            conjugate = matmul(matmul(matrix, projector), inv)
        else:
            # Deliberately incorrect control: use G on both sides.
            conjugate = matmul(matmul(matrix, projector), matrix)
        minors = tuple(leading_minor_nonzero(conjugate, k) for k in (1, 2, 3))
        values.append(int(all(minors)))
    return tuple(values)


def all_gl4():
    """Yield every invertible 4x4 GF(2) matrix exactly once."""
    for encoding in range(FIELD_MATRIX_BITS):
        matrix = tuple((encoding >> (N * r)) & ((1 << N) - 1) for r in range(N))
        inv = inverse(matrix)
        if inv is not None:
            yield matrix, inv


def atom_label(bits):
    return "".join(str(bit) for bit in bits)


def monotone_event_masks(width):
    """Enumerate event truth tables of all increasing Boolean functions."""
    assignment_count = 1 << width
    for event in range(1 << assignment_count):
        increasing = True
        for x in range(assignment_count):
            if (event >> x) & 1:
                for y in range(assignment_count):
                    if (x & y) == x and not ((event >> y) & 1):
                        increasing = False
                        break
                if not increasing:
                    break
        if increasing:
            yield event


def local_assignment(atom, coordinates):
    return sum(atom[c] << j for j, c in enumerate(coordinates))


def event_true(event_mask, atom, coordinates):
    assignment = local_assignment(atom, coordinates)
    return (event_mask >> assignment) & 1


def split_covariances(atom_counts):
    """Return exact covariance numerators for every monotone event pair.

    For a distribution with total mass M, the numerator is
    M * count(A and B) - count(A) * count(B), so its sign is the covariance
    sign and the exact covariance equals numerator / M**2.
    """
    total = sum(atom_counts.values())
    reports = {}
    for sizes in SPLIT_SIZES:
        left_size, right_size = sizes
        pairs = []
        if left_size == right_size:
            for left in combinations(range(N), left_size):
                remaining = tuple(c for c in range(N) if c not in left)
                for right in combinations(remaining, right_size):
                    if left < right:
                        pairs.append((left, right))
        else:
            for left in combinations(range(N), left_size):
                remaining = tuple(c for c in range(N) if c not in left)
                for right in combinations(remaining, right_size):
                    pairs.append((left, right))

        left_events = tuple(monotone_event_masks(left_size))
        right_events = tuple(monotone_event_masks(right_size))
        values = []
        strict_values = []
        constant_involved = 0
        witness = None
        strict_witness = None
        for left, right in pairs:
            for event_left in left_events:
                count_left = sum(
                    mass for atom, mass in atom_counts.items()
                    if event_true(event_left, atom, left)
                )
                for event_right in right_events:
                    count_right = sum(
                        mass for atom, mass in atom_counts.items()
                        if event_true(event_right, atom, right)
                    )
                    count_both = sum(
                        mass for atom, mass in atom_counts.items()
                        if event_true(event_left, atom, left)
                        and event_true(event_right, atom, right)
                    )
                    covariance_numerator = total * count_both - count_left * count_right
                    values.append(covariance_numerator)
                    left_constant = event_left in (0, (1 << (1 << left_size)) - 1)
                    right_constant = event_right in (0, (1 << (1 << right_size)) - 1)
                    if left_constant or right_constant:
                        require(covariance_numerator == 0,
                                f"constant event has nonzero covariance for split {sizes}")
                        constant_involved += 1
                    else:
                        strict_values.append(covariance_numerator)
                    if witness is None or covariance_numerator > witness[0]:
                        witness = (
                            covariance_numerator,
                            left,
                            right,
                            event_left,
                            event_right,
                            count_left,
                            count_right,
                            count_both,
                        )
                    if not (left_constant or right_constant):
                        if strict_witness is None or covariance_numerator > strict_witness[0]:
                            strict_witness = (
                                covariance_numerator,
                                left,
                                right,
                                event_left,
                                event_right,
                                count_left,
                                count_right,
                                count_both,
                            )
        reports[sizes] = (
            min(values), max(values), len(values), witness,
            min(strict_values), max(strict_values), len(strict_values), strict_witness,
            constant_involved,
        )
    return reports


def law_for_header(predicate):
    """Enumerate a restricted family with prescribed first-row predicate."""
    law = Counter()
    count = 0
    for matrix, inv in all_gl4():
        if predicate(matrix[0]):
            count += 1
            law[indicators_for(matrix, inv)] += 1
    return count, law


def main():
    law = Counter()
    wrong_law = Counter()
    total = 0
    identity_atom = None
    noninvolution_witness = None

    for matrix, inv in all_gl4():
        total += 1
        atom = indicators_for(matrix, inv)
        law[atom] += 1
        if matrix == IDENTITY:
            identity_atom = atom
        if noninvolution_witness is None and matmul(matrix, matrix) != IDENTITY:
            wrong_atom = indicators_for(matrix, inv, use_inverse=False)
            if wrong_atom != atom:
                noninvolution_witness = (matrix, atom, wrong_atom)
        wrong_law[indicators_for(matrix, inv, use_inverse=False)] += 1

    require(total == 20160, f"expected |GL_4(F_2)|=20160, got {total}")
    require(sum(law.values()) == total, "atom masses do not sum to group size")
    expected_by_weight = (3480, 3816, 228, 12, 0)
    require(all(law[atom] == expected_by_weight[sum(atom)]
                for atom in product((0, 1), repeat=N)), "complete atom fixture differs")
    require(identity_atom == (0, 0, 0, 1), f"identity control changed: {identity_atom}")
    require(noninvolution_witness is not None, "no forward-only witness found")
    require(law != wrong_law, "forward-only mutation unexpectedly has the same atom law")

    moments = {}
    for size in range(1, N + 1):
        for subset in combinations(range(N), size):
            moments[subset] = sum(
                mass for atom, mass in law.items()
                if all(atom[i] for i in subset)
            )

    print(f"GL4_F2_count={total}")
    print("indicator_definition=Xi iff all leading principal minors of orders 1,2,3 of G P_i G^-1 are nonzero")
    print("atom_counts (bits in i=0,1,2,3 order):")
    for atom in product((0, 1), repeat=N):
        print(f"  {atom_label(atom)}: {law[atom]}")
    print("product_moment_counts (subset -> count where all selected Xi=1):")
    for subset, count in sorted(moments.items(), key=lambda item: (len(item[0]), item[0])):
        print(f"  {''.join(str(i) for i in subset)}: {count}")

    reports = split_covariances(law)
    print("monotone_event_covariance_numerator_ranges (covariance = numerator / 20160^2):")
    for sizes in SPLIT_SIZES:
        report = reports[sizes]
        minimum, maximum, tested = report[:3]
        strict_minimum, strict_maximum, strict_tested = report[4:7]
        constants_tested = report[8]
        print(f"  {sizes[0]}+{sizes[1]}: all_min={minimum} all_max={maximum} all_pairs={tested}")
        print(f"    constants_zero_pairs={constants_tested}; strict_nonconstant_pairs={strict_tested}; strict_min={strict_minimum} strict_max={strict_maximum}")
        require(maximum == 0, f"constants or nonconstant events gave positive covariance for split {sizes}: {report[3]}")
        require(strict_maximum < 0, f"nonconstant events were not strictly negative for split {sizes}: {report[7]}")

    # A fixed first-row header slice. This is a reproducible restriction of
    # GL_4(F_2), not the full uniform law; it deliberately supplies a positive
    # covariance control showing that the full-law conclusion is not automatic
    # for arbitrary restricted families.
    header_count, header_law = law_for_header(lambda row: row == 0b1110)
    header_reports = split_covariances(header_law)
    header_violations = [
        (sizes, report[3])
        for sizes, report in header_reports.items()
        if report[1] > 0
    ]
    require(header_count == 1344, f"unexpected fixed-row header size: {header_count}")
    require(header_violations, "fixed-row header control did not violate negative association")
    print(f"header_control=first row [0,1,1,1] (columns 0,1,2,3); matrices={header_count}")
    print(f"header_control_positive_covariance_splits={len(header_violations)}")
    if header_violations:
        sizes, witness = header_violations[0]
        numerator, left, right, event_left, event_right, count_left, count_right, count_both = witness
        left_table = ''.join(str((event_left >> x) & 1) for x in range(1 << len(left)))
        right_table = ''.join(str((event_right >> x) & 1) for x in range(1 << len(right)))
        require((numerator, count_left, count_right, count_both) == (960, 432, 4, 2),
                "fixed-row positive-covariance witness changed")
        print(f"  witness_split={sizes}; left_coordinates={left}; right_coordinates={right}")
        print(f"  left_event_truth_table={left_table}; right_event_truth_table={right_table}")
        print(f"  counts: total={header_count}, left={count_left}, right={count_right}, joint={count_both}")
        print(f"  covariance_numerator={numerator}; covariance={numerator}/{header_count**2} > 0")

    matrix, correct_atom, forward_atom = noninvolution_witness
    print("forward_only_control=G P_i G instead of G P_i G^-1")
    print(f"  sample_G_rows={[[(row >> c) & 1 for c in range(N)] for row in matrix]}")
    print(f"  correct_atom={atom_label(correct_atom)} forward_only_atom={atom_label(forward_atom)}")
    print(f"  full_forward_only_law_differs={law != wrong_law}")
    print("PASS_GL4_FOUR_GUARD_BOUNDARY")


if __name__ == "__main__":
    main()
