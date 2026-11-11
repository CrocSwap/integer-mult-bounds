#!/usr/bin/env python3
"""Checks for one length-7 support witness with three old projectors.

PROOF.md is the argument. This program checks that one declared seven-label
solution sums to 4I, that every triple of old projectors leaves four
positive-semidefinite rank-one added frames, that each target is exactly the
declared projector pair, and that the odd-c count on this same solution is
two calls against four targets. The witness is one solution, not a census.
"""

from fractions import Fraction
from itertools import combinations


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def add(frames):
    rows = tuple(frames)
    return tuple(sum(frame[index] for frame in rows) for index in range(3))


def determinant(frame):
    a, b, c = frame
    return a * b + c * (a + b) / 2


def trace(frame):
    return frame[0] + frame[1] + frame[2]


def rank_one_nonzero(frame):
    return frame != (0, 0, 0) and determinant(frame) == 0


def positive_semidefinite_rank_one(frame):
    # A symmetric rank-one matrix has trace equal to its nonzero eigenvalue.
    return rank_one_nonzero(frame) and trace(frame) > 0


def coefficient(direction, scale):
    x, y = direction
    scale = Fraction(scale)
    return (scale * x * (x - y), scale * y * (y - x), scale * 2 * x * y)


def integer_c(frame):
    require(frame[2].denominator == 1, "odd-c test on a frame whose c-coordinate is not integral")
    return int(frame[2])


A = coefficient((1, 0), 1)
B = coefficient((0, 1), 1)
P = coefficient((1, 1), Fraction(1, 2))
Q = coefficient((1, -1), Fraction(1, 2))
HALF_A = coefficient((1, 0), Fraction(1, 2))
THREE_HALVES_A = coefficient((1, 0), Fraction(3, 2))
TWO_A = coefficient((1, 0), 2)
TWO_B = coefficient((0, 1), 2)
FOUR = (Fraction(4), Fraction(4), Fraction(0))
IDENTITY = (Fraction(1), Fraction(1), Fraction(0))

PROJECTORS = (A, B, P, Q)
LABELS = (A, B, P, Q, HALF_A, THREE_HALVES_A, TWO_B)
NAMES = ("A", "B", "P", "Q", "(1/2)A", "(3/2)A", "2B")
EXTRAS = (HALF_A, THREE_HALVES_A, TWO_B)
SIX = (A, B, P, Q, TWO_A, TWO_B)


def targets():
    return {
        "AP": add((A, P)),
        "AQ": add((A, Q)),
        "BP": add((B, P)),
        "BQ": add((B, Q)),
    }


def target_identities(rows):
    require(add(rows.values()) == FOUR, "the four targets do not sum to 4I")
    for name, row in rows.items():
        require(trace(row) == 2, name + " does not have trace 2")
        require(determinant(row) == Fraction(1, 2), name + " does not have determinant 1/2")
        complement = add((FOUR, tuple(-value for value in row)))
        require(determinant(complement) == Fraction(17, 2), name + " complement determinant changed")
        require(integer_c(row) % 2 == 1, name + " does not have odd c")


def witness_parameterization():
    require(coefficient((1, 0), 1) == (1, 0, 0), "A is not the scale-1 axis frame")
    require(coefficient((0, 1), 1) == (0, 1, 0), "B is not the scale-1 axis frame")
    require(P == (0, 0, 1), "P is not the declared uu^T frame")
    require(Q == (1, 1, -1), "Q is not the declared uu^T frame")
    require(HALF_A == (Fraction(1, 2), 0, 0), "(1/2)A is not scale 1/2 on (1,0)")
    require(THREE_HALVES_A == (Fraction(3, 2), 0, 0), "(3/2)A is not scale 3/2 on (1,0)")
    require(TWO_A == (2, 0, 0), "2A is not scale 2 on (1,0)")
    require(TWO_B == (0, 2, 0), "2B is not scale 2 on (0,1)")
    require(add((P, Q)) == add((A, B)) == IDENTITY, "P+Q and A+B are not both I")
    require(add((HALF_A, THREE_HALVES_A)) == TWO_A, "(1/2)A + (3/2)A is not 2A")
    require(len(set(LABELS)) == 7, "the seven labels are not distinct matrices")


def witness_sum():
    for frame, name in zip(LABELS, NAMES):
        require(positive_semidefinite_rank_one(frame), name + " is not positive-semidefinite rank one")
    require(add(LABELS) == FOUR, "the seven labels do not sum to 4I")
    # (1/2)A+(3/2)A = 2A, and A+B+P+Q+2A+2B = 3(A+B)+(P+Q) = 4I.
    require(add(LABELS) == add(SIX), "splitting 2A changed the six-label sum")
    require(add(SIX) == add((
        add((A, A, A)), add((B, B, B)), add((A, B)),
    )), "the written sum identity does not match the six labels")


def axis_subset_tables():
    """The a-sums of subsets of {A,(1/2)A,(3/2)A} and the b-sums of {B,2B}."""
    a_parts = (A, HALF_A, THREE_HALVES_A)
    b_parts = (B, TWO_B)
    alpha = {}
    for mask in range(1 << 3):
        chosen = [a_parts[index] for index in range(3) if mask & (1 << index)]
        value = add(chosen)[0] if chosen else 0
        alpha.setdefault(value, []).append(mask)
    beta = {}
    for mask in range(1 << 2):
        chosen = [b_parts[index] for index in range(2) if mask & (1 << index)]
        value = add(chosen)[1] if chosen else 0
        beta.setdefault(value, []).append(mask)
    expected_alpha = {
        0: [0],
        Fraction(1, 2): [0b010],
        1: [0b001],
        Fraction(3, 2): [0b011, 0b100],
        2: [0b110],
        Fraction(5, 2): [0b101],
        3: [0b111],
    }
    expected_beta = {0: [0], 1: [0b01], 2: [0b10], 3: [0b11]}
    normalized = {key: sorted(value) for key, value in alpha.items()}
    require(normalized == expected_alpha, "a-subset table changed: " + str(normalized))
    require({key: sorted(value) for key, value in beta.items()} == expected_beta,
            "b-subset table changed: " + str(beta))
    require(alpha[0] == [0] and alpha[1] == [0b001], "a in {0,1} is not unique")
    require(beta[0] == [0] and beta[1] == [0b01], "b in {0,1} is not unique")


def support_scan(rows):
    found = {name: [] for name in rows}
    examined = 0
    for mask in range(1, 1 << 7):
        examined += 1
        chosen = [LABELS[index] for index in range(7) if mask & (1 << index)]
        total = add(chosen)
        for name, row in rows.items():
            if total == row:
                found[name].append((mask, len(chosen), tuple(
                    NAMES[index] for index in range(7) if mask & (1 << index)
                )))
    require(examined == 127, "the subset scan missed a nonempty subset")
    expected = {
        "AP": ((1 << 0) | (1 << 2), ("A", "P")),
        "AQ": ((1 << 0) | (1 << 3), ("A", "Q")),
        "BP": ((1 << 1) | (1 << 2), ("B", "P")),
        "BQ": ((1 << 1) | (1 << 3), ("B", "Q")),
    }
    for name, (mask, names) in expected.items():
        hits = found[name]
        require(hits == [(mask, 2, names)], name + " is not exactly the declared projector pair: " + str(hits))


def every_old_triple(rows):
    for chosen in combinations(range(4), 3):
        old = set(chosen)
        missing = next(index for index in range(4) if index not in old)
        added = (PROJECTORS[missing],) + EXTRAS
        require(len(added) == 4, "an old triple did not leave four added frames")
        require(len(set(added)) == 4, "an old triple repeated an added frame")
        for frame in added:
            require(positive_semidefinite_rank_one(frame), "an added frame is not positive-semidefinite rank one")
        old_frames = [PROJECTORS[index] for index in chosen]
        residual = tuple(FOUR[index] - sum(frame[index] for frame in old_frames) for index in range(3))
        require(add(added) == residual, NAMES[missing] + " omitted: residual mismatch")
        require(residual == add((IDENTITY, IDENTITY, PROJECTORS[missing])),
                NAMES[missing] + " omitted: residual is not 2I plus the omitted projector")
        labels = [PROJECTORS[index] for index in chosen] + list(added)
        require(sorted(names_of(labels)) == sorted(NAMES), "an old triple changed the seven-label set")
        seen = set()
        for mask in range(1, 1 << 7):
            total = add(labels[index] for index in range(7) if mask & (1 << index))
            if total in rows.values():
                seen.add(total)
        require(seen == set(rows.values()), "old triple " + str(tuple(NAMES[index] for index in chosen)) + " misses a target")


def names_of(frames):
    positions = {frame: name for frame, name in zip(LABELS, NAMES)}
    return [positions[frame] for frame in frames]


def character_count():
    detected_calls = 0
    for frame, name in zip(LABELS, NAMES):
        parity = integer_c(frame) % 2
        if name in ("P", "Q"):
            require(parity == 1, name + " lost its odd c")
        else:
            require(parity == 0, name + " has odd c")
        detected_calls += parity
    detected_targets = sum(integer_c(row) % 2 for row in targets().values())
    require(detected_calls == 2, "odd c detects something other than P and Q")
    require(detected_targets == 4, "odd c does not detect every target")
    require(detected_calls < detected_targets, "the witness is not a direct character obstruction")


def failure_controls(rows):
    without_q = [frame for frame in LABELS if frame != Q]
    hits = set()
    for mask in range(1, 1 << len(without_q)):
        total = add(without_q[index] for index in range(len(without_q)) if mask & (1 << index))
        if total in rows.values():
            hits.add(total)
    require(rows["AQ"] not in hits and rows["BQ"] not in hits, "dropping Q still realizes an AQ or BQ target")
    require(rows["AP"] in hits and rows["BP"] in hits, "dropping Q lost a target that does not use Q")
    tampered = (A, B, P, Q, HALF_A, add((THREE_HALVES_A, A)), TWO_B)
    require(add(tampered) != FOUR, "tampered (3/2)A still sums to 4I")
    require(add(SIX) == FOUR, "the six-label set no longer sums to 4I")
    require(add(SIX + (HALF_A,)) != FOUR, "adjoining (1/2)A to the six-label set still sums to 4I")
    require(determinant(IDENTITY) == 1, "det I changed")
    require(not rank_one_nonzero(IDENTITY), "I was accepted as rank one")
    require(rank_one_nonzero((0, 0, 0)) is False, "the zero matrix was accepted")
    require(trace(HALF_A) == Fraction(1, 2) and trace(THREE_HALVES_A) == Fraction(3, 2),
            "a split frame lost its positive trace")


def main():
    rows = targets()
    target_identities(rows)
    witness_parameterization()
    witness_sum()
    axis_subset_tables()
    support_scan(rows)
    every_old_triple(rows)
    character_count()
    failure_controls(rows)
    print("PASS four-signed-three-old-support checks")


if __name__ == "__main__":
    main()
