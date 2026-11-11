#!/usr/bin/env python3
"""Checks for one length-6 support witness with two old projectors.

PROOF.md is the argument. This program checks that one declared six-label
solution sums to 4I, that every pair of old projectors leaves four rank-one
added frames, that every target is a two-label subset sum, and that the
odd-c count on this same solution is two calls against four targets.
The witness is one solution, not a census.
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


def rank_one_nonzero(frame):
    return frame != (0, 0, 0) and determinant(frame) == 0


def coefficient(direction, scale):
    x, y = direction
    scale = Fraction(scale)
    return (scale * x * (x - y), scale * y * (y - x), scale * 2 * x * y)


def parity_c(frame):
    require(all(value.denominator == 1 for value in frame), "odd-c test on a non-integral frame")
    return int(frame[2]) % 2


A = (1, 0, 0)
B = (0, 1, 0)
P = (0, 0, 1)
Q = (1, 1, -1)
TWO_A = (2, 0, 0)
TWO_B = (0, 2, 0)
FOUR = (4, 4, 0)
PROJECTORS = (A, B, P, Q)
LABELS = (A, B, P, Q, TWO_A, TWO_B)
NAMES = ("A", "B", "P", "Q", "2A", "2B")


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
        require(row[0] + row[1] + row[2] == 2, name + " does not have trace 2")
        require(determinant(row) == Fraction(1, 2), name + " does not have determinant 1/2")
        complement = add((FOUR, tuple(-value for value in row)))
        require(determinant(complement) == Fraction(17, 2), name + " complement determinant changed")
        require(parity_c(row) == 1, name + " does not have odd c")


def witness_parameterization():
    require(coefficient((1, 0), 1) == A, "A is not the scale-1 axis frame")
    require(coefficient((0, 1), 1) == B, "B is not the scale-1 axis frame")
    require(coefficient((1, 1), Fraction(1, 2)) == P, "P is not the declared uu^T frame")
    require(coefficient((1, -1), Fraction(1, 2)) == Q, "Q is not the declared uu^T frame")
    require(coefficient((1, 0), 2) == TWO_A, "2A is not scale 2 on (1,0)")
    require(coefficient((0, 1), 2) == TWO_B, "2B is not scale 2 on (0,1)")
    require(add((P, Q)) == add((A, B)) == (1, 1, 0), "P+Q and A+B are not both I")


def witness_sum():
    for frame, name in zip(LABELS, NAMES):
        require(rank_one_nonzero(frame), name + " is not nonzero rank one")
    require(add(LABELS) == FOUR, "the six labels do not sum to 4I")
    # 3(A+B) + (P+Q) = 3I + I = 4I, using P+Q = A+B = I.
    require(add((A, B, P, Q, TWO_A, TWO_B)) == add((
        add((A, A, A)), add((B, B, B)), add((A, B)),
    )), "the written sum identity does not match the six labels")


def support_scan(rows):
    found = {name: [] for name in rows}
    for mask in range(1, 1 << 6):
        chosen = [LABELS[index] for index in range(6) if mask & (1 << index)]
        total = add(chosen)
        for name, row in rows.items():
            if total == row:
                found[name].append((mask, len(chosen)))
    expected = {
        "AP": (1 << 0) | (1 << 2),  # A+P
        "AQ": (1 << 0) | (1 << 3),  # A+Q
        "BP": (1 << 1) | (1 << 2),  # B+P
        "BQ": (1 << 1) | (1 << 3),  # B+Q
    }
    for name, mask in expected.items():
        hits = found[name]
        require(hits == [(mask, 2)], name + " is not exactly the declared projector pair: " + str(hits))


def every_old_pair():
    rows = targets()
    for left, right in combinations(range(4), 2):
        old = {left, right}
        added = [LABELS[index] for index in range(6) if index not in old]
        require(len(added) == 4, "an old pair did not leave four added frames")
        for frame in added:
            require(rank_one_nonzero(frame), "an added frame is not rank one")
        residual = add((FOUR, tuple(-LABELS[left][i] for i in range(3)),
                         tuple(-LABELS[right][i] for i in range(3))))
        require(add(added) == residual, NAMES[left] + "+" + NAMES[right] + " residual mismatch")
        # The six-label scan already hits every target; recheck on this designation.
        labels = [LABELS[left], LABELS[right], *added]
        seen = set()
        for mask in range(1, 1 << 6):
            total = add(labels[index] for index in range(6) if mask & (1 << index))
            if total in rows.values():
                seen.add(total)
        require(seen == set(rows.values()), NAMES[left] + "+" + NAMES[right] + " misses a target")


def character_count():
    detected_calls = sum(parity_c(frame) for frame in LABELS)
    detected_targets = sum(parity_c(row) for row in targets().values())
    require(detected_calls == 2, "odd c detects something other than P and Q")
    require(parity_c(P) == 1 and parity_c(Q) == 1, "P or Q lost its odd c")
    require(parity_c(A) == parity_c(B) == parity_c(TWO_A) == parity_c(TWO_B) == 0,
            "an even label became odd")
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
    tampered = (A, B, P, Q, add((TWO_A, (1, 0, 0))), TWO_B)
    require(add(tampered) != FOUR, "tampered 2A still sums to 4I")
    require(determinant((1, 1, 0)) == 1, "det I changed")
    require(not rank_one_nonzero((1, 1, 0)), "I was accepted as rank one")
    require(rank_one_nonzero((0, 0, 0)) is False, "the zero matrix was accepted")


def main():
    rows = targets()
    target_identities(rows)
    witness_parameterization()
    witness_sum()
    support_scan(rows)
    every_old_pair()
    character_count()
    failure_controls(rows)
    print("PASS four-signed-two-old-support checks")


if __name__ == "__main__":
    main()
