#!/usr/bin/env python3
"""Exact corroboration of the fixed positive-alphabet determinant obstruction."""

import argparse
from fractions import Fraction as F
from itertools import combinations_with_replacement
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Flattened symmetric 2-by-2 matrices, scaled by four. Order: A, B, P, Q, R.
FRAMES4 = ((4, 0, 0, 0), (0, 0, 0, 4), (2, 2, 2, 2),
           (2, -2, -2, 2), (4, 2, 2, 1))
# Exact integral coordinates in the independent basis (A, P, R).
LABELS = ((1, 0, 0), (2, 4, -4), (0, 1, 0), (3, 3, -4), (0, 0, 1))
TARGETS = ((1, 1, 0), (4, 3, -4), (2, 5, -4), (5, 7, -8))
EXPECTED_COUNTS = [[0, 0, 4, 4, 0], [1, 1, 3, 3, 0], [2, 2, 2, 2, 0],
                   [3, 3, 1, 1, 0], [4, 4, 0, 0, 0]]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def add(a, b):
    return tuple(x + y for x, y in zip(a, b, strict=True))


def matrix_product(a, b):
    """Binary matrices represented by tuples of packed rows, at most 7 rows."""
    size = len(a)
    require(1 <= size <= 7 and len(b) == size, "matrix size outside 1..7")
    result = []
    for row in a:
        value = 0
        for k in range(size):
            if row >> k & 1:
                value ^= b[k]
        result.append(value)
    return tuple(result)


def toggle(state, exponent, coefficient):
    previous = state.get(exponent, (0,) * len(coefficient))
    value = tuple(x ^ y for x, y in zip(previous, coefficient, strict=True))
    if any(value):
        state[exponent] = value
    else:
        state.pop(exponent, None)


def apply_factor(state, projector, frame):
    following = dict(state)
    for exponent, coefficient in state.items():
        correction = matrix_product(coefficient, projector)
        toggle(following, exponent, correction)
        toggle(following, add(exponent, frame), correction)
    return following


def formal_word(labels, roles, mixed=False):
    """Replay eight coordinate calls, optionally through free dirty mixing."""
    require(4 <= roles <= 7 and len(labels) <= 8, "word outside replay bounds")
    require(all(0 <= label < 5 for label in labels), "unknown positive label")
    identity = tuple(1 << i for i in range(roles))
    change = list(identity)
    if mixed:
        # An involution; for roles > 4 this mixes an active and a dirty role.
        change[0] ^= 1 << (roles - 1)
    change = tuple(change)
    require(matrix_product(change, change) == identity, "basis map not involutive")
    state = {(0, 0, 0): change}
    for position, label in enumerate(labels):
        owner = position // 2
        require(owner < 4, "coordinate owner outside target roles")
        projector = tuple((1 << owner) if i == owner else 0 for i in range(roles))
        projector = matrix_product(matrix_product(change, projector), change)
        state = apply_factor(state, projector, LABELS[label])
    return {exponent: matrix_product(coefficient, change)
            for exponent, coefficient in state.items()}


def endpoint(roles):
    state = {}
    for owner in range(roles):
        exponent = TARGETS[owner] if owner < 4 else (0, 0, 0)
        coefficient = tuple((1 << owner) if i == owner else 0 for i in range(roles))
        toggle(state, exponent, coefficient)
    return state


def verify_geometry():
    basis = (FRAMES4[0], FRAMES4[2], FRAMES4[4])
    for frame, coordinates in zip(FRAMES4, LABELS, strict=True):
        rebuilt = tuple(sum(coordinates[j] * basis[j][i] for j in range(3))
                        for i in range(4))
        require(frame == rebuilt, "lattice coordinate mismatch")
        a, b, c, d = frame
        require(a * d == b * c and frame != (0, 0, 0, 0), "frame not rank one")
        # For a symmetric 2-by-2 matrix these principal-minor tests prove PSD.
        require(b == c and a >= 0 and d >= 0, "frame not positive semidefinite")
    # In (00,01,11) entries the scaled basis determinant is nonzero.
    minor = basis[0][0] * (basis[1][1] * basis[2][3] - basis[1][3] * basis[2][1])
    require(minor == -8, "basis minor mismatch")
    pairs = ((0, 2), (0, 3), (1, 2), (1, 3))
    targets4 = [add(FRAMES4[i], FRAMES4[j]) for i, j in pairs]
    target_sum = tuple(map(sum, zip(*targets4, strict=True)))
    require(target_sum == (16, 0, 0, 16), "wrong target sum")
    require(all(t[0] * t[3] - t[1] * t[2] == 8 for t in targets4), "singular target")
    traces = [F(frame[0] + frame[3], 4) for frame in FRAMES4]
    energies = [F(4 * a + 2 * b + 2 * c + d, 4) for a, b, c, d in FRAMES4]
    require(traces == [1, 1, 1, 1, F(5, 4)], "trace control failed")
    require(energies == [4, 1, F(9, 2), F(1, 2), F(25, 4)], "energy control failed")
    require(F(20, 1) / energies[4] == F(16, 5) < 4, "R count bound failed")
    return traces, energies


def determinant_profiles():
    """Independent enumeration from matrix entries, not the lattice equations."""
    accepted = []
    tested = 0
    for size in range(9):
        for multiset in combinations_with_replacement(range(5), size):
            tested += 1
            total = tuple(sum(FRAMES4[label][i] for label in multiset)
                          for i in range(4))
            if total == (16, 0, 0, 16):
                accepted.append([multiset.count(label) for label in range(5)])
    require(tested == 1287, "incomplete bounded count enumeration")
    require(sorted(accepted) == EXPECTED_COUNTS,
            "determinant count classification failed")
    return tested, sorted(accepted)


def compute_receipt():
    traces, energies = verify_geometry()
    tested, profiles = determinant_profiles()
    direct = [0, 2, 0, 3, 1, 2, 1, 3]
    positive = 0
    negative = 0
    for roles in (4, 5, 7):
        for mixed in (False, True):
            require(formal_word(direct, roles, mixed) == endpoint(roles),
                    "direct word failed")
            positive += 1
            for position in range(8):
                changed = direct.copy()
                changed[position] = 4
                require(formal_word(changed, roles, mixed) != endpoint(roles),
                        "R mutation accepted")
                negative += 1
    # All six-call equality candidates in PR2112 have this label multiset.
    six_trace = 2 * traces[2] + 2 * traces[3] + 2 * traces[4]
    require(six_trace == F(13, 2) != 8, "six-call determinant control failed")
    # Boundary: the no-R conclusion is specific to the original target sum.
    scaled = tuple(3 * FRAMES4[1][i] + 4 * FRAMES4[3][i] + 4 * FRAMES4[4][i]
                   for i in range(4))
    require(scaled == (24, 0, 0, 24), "scaled determinant-positive control failed")
    # Allowing inverse labels permits an R,-R identity pair after the direct word.
    identity = {(0, 0, 0): (1, 2, 4, 8)}
    dirty_projector = (9, 0, 0, 0)
    with_R = apply_factor(identity, dirty_projector, LABELS[4])
    restored = apply_factor(with_R, dirty_projector, tuple(-x for x in LABELS[4]))
    require(with_R != identity and restored == identity,
            "inverse boundary control failed")
    return {
        "status": "PASS_FIFTH_FRAME_DETERMINANT_OBSTRUCTION",
        "minimum_calls": 8,
        "R_calls_in_any_exact_word": 0,
        "all_exact_words_have_calls": 8,
        "determinant_profiles": profiles,
        "enumerated_multisets": tested,
        "formal_positive_fixtures": positive,
        "formal_R_mutation_controls": negative,
        "traces": list(map(str, traces)),
        "energies_at_2_1": list(map(str, energies)),
        "R_upper_bound": "16/5",
        "six_call_candidate_trace": str(six_trace),
        "scaled_target_sum_boundary": [3, 4, 4],
        "scope": ("Fixed positive alphabet; arbitrary finite restored dirty workspace. "
                  "No supplier or kappa."),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, default=HERE / "RESULT.json")
    args = parser.parse_args()
    actual = compute_receipt()
    with args.receipt.open("rb") as source:
        raw = source.read(65537)
    require(len(raw) <= 65536, "receipt exceeds 64 KiB")
    expected = json.loads(raw)
    require(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
            "receipt mismatch")
    print(json.dumps(actual, sort_keys=True))


if __name__ == "__main__":
    main()
