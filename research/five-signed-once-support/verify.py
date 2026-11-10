#!/usr/bin/env python3
"""Checks for the five-call equation R+S+T+U+V = 4I.

PROOF.md holds the argument. This program checks the subset-size
identities, exhausts every ordered 4-tuple of distinct weight-2 and
weight-3 subsets, and checks one declared five-direction witness.
The tuple list is the whole support domain left by the size lemma.
The witness is one solution of the sum, not a census of solutions.
"""

from fractions import Fraction
from itertools import combinations, permutations


TARGETS = ((1, 0, 1), (2, 1, -1), (0, 1, 1), (1, 2, -1))
TOTAL = (4, 4, 0)
MASKS = tuple(mask for mask in range(32) if bin(mask).count("1") in (2, 3))
BAD_FROZEN = {
    (2, 2, 0),
    (-2, -2, 0),
    (1, -1, 0),
    (-1, 1, 0),
    (1, 1, -2),
    (-1, -1, 2),
}
HAND_MASKS = (3, 5, 6, 9)
HAND_FRAMES = (
    (Fraction(3, 2), Fraction(0), Fraction(-1, 2)),
    (Fraction(-1, 2), Fraction(0), Fraction(3, 2)),
    (Fraction(1, 2), Fraction(1), Fraction(-1, 2)),
    (Fraction(-1, 2), Fraction(2), Fraction(-1, 2)),
    (Fraction(3), Fraction(1), Fraction(0)),
)
SINGULAR_MASKS = (3, 5, 10, 12)
WITNESS_DIRECTIONS = ((-1, 1), (0, 1), (1, 0), (1, 1), (1, 3))
WITNESS_SCALES = (Fraction(1), Fraction(-1), Fraction(3), Fraction(-1, 2), Fraction(1, 2))
WITNESS_FRAMES = (
    (2, 2, -2),
    (0, -1, 0),
    (3, 0, 0),
    (0, 0, -1),
    (-1, 3, 3),
)

PERMS = []
for _perm in permutations(range(5)):
    inversions = sum(1 for i in range(5) for j in range(i + 1, 5) if _perm[i] > _perm[j])
    PERMS.append((_perm, 1 if inversions % 2 == 0 else -1))


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def coefficient(direction, scale):
    x, y = direction
    scale = Fraction(scale)
    return (scale * x * (x - y), scale * y * (y - x), 2 * scale * x * y)


def quad(frame):
    a, b, c = frame
    return 2 * a * b + c * (a + b)


def determinant(frame):
    a, b, c = frame
    return a * b + c * (a + b) / 2


def trace(frame):
    return frame[0] + frame[1] + frame[2]


def add(frames):
    return tuple(sum(frame[i] for frame in frames) for i in range(3))


def rank_one_nonzero(frame):
    return frame != (0, 0, 0) and quad(frame) == 0


def parity(frame):
    require(all(value.denominator == 1 for value in frame), "parity on a non-integral frame")
    return ((int(frame[0]) + int(frame[1])) % 2, int(frame[2]) % 2)


def det5(rows):
    total = 0
    for perm, sign in PERMS:
        total += (
            sign
            * rows[0][perm[0]]
            * rows[1][perm[1]]
            * rows[2][perm[2]]
            * rows[3][perm[3]]
            * rows[4][perm[4]]
        )
    return total


def incidence(masks, targets, total):
    rows = []
    rhs = [[], [], []]
    for index, mask in enumerate(masks):
        rows.append([(mask >> column) & 1 for column in range(5)])
        for coord in range(3):
            rhs[coord].append(targets[index][coord])
    rows.append([1, 1, 1, 1, 1])
    for coord in range(3):
        rhs[coord].append(total[coord])
    return rows, rhs


def cramer(rows, rhs):
    denominator = det5(rows)
    numerators = []
    for column in range(5):
        coords = []
        for coord in range(3):
            replaced = [row[:] for row in rows]
            for row_index in range(5):
                replaced[row_index][column] = rhs[coord][row_index]
            coords.append(det5(replaced))
        numerators.append(tuple(coords))
    return denominator, numerators


def residual_ok(rows, rhs, numerators, denominator):
    for row_index in range(5):
        for coord in range(3):
            got = sum(rows[row_index][column] * numerators[column][coord] for column in range(5))
            if got != denominator * rhs[coord][row_index]:
                return False
    return True


def rref_family(rows, rhs, reverse):
    columns = list(range(4, -1, -1)) if reverse else list(range(5))
    matrix = [
        [Fraction(rows[row][column]) for column in range(5)] + [Fraction(rhs[coord][row]) for coord in range(3)]
        for row in range(5)
    ]
    pivot_of = {}
    rank = 0
    for column in columns:
        pivot = None
        for row in range(rank, 5):
            if matrix[row][column] != 0:
                pivot = row
                break
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        pivot_value = matrix[rank][column]
        for entry in range(8):
            matrix[rank][entry] /= pivot_value
        for row in range(5):
            if row == rank or matrix[row][column] == 0:
                continue
            factor = matrix[row][column]
            for entry in range(0, 8):
                matrix[row][entry] -= factor * matrix[rank][entry]
        pivot_of[column] = rank
        rank += 1
    for row in range(rank, 5):
        if any(matrix[row][5 + coord] != 0 for coord in range(3)):
            return ("inconsistent",)
    if rank != 4:
        return ("unhandled", rank)
    free = [column for column in range(5) if column not in pivot_of]
    if len(free) != 1:
        return ("unhandled", rank)
    free = free[0]
    kernel = [Fraction(0)] * 5
    kernel[free] = Fraction(1)
    for column, row in pivot_of.items():
        kernel[column] = -matrix[row][free]
    zeros = [column for column in range(5) if kernel[column] == 0]
    if zeros == []:
        return ("unhandled", "no frozen frame")
    frozen = []
    for column in zeros:
        row = pivot_of[column]
        frozen.append(tuple(matrix[row][5 + coord] for coord in range(3)))
    return ("family", tuple(frozen), tuple(kernel))


def target_identities():
    require(len(PERMS) == 120, "the symmetric group on five letters has 120 elements")
    require(sum(sign for _, sign in PERMS) == 0, "permutation signs are not balanced")
    identity = [[1 if i == j else 0 for j in range(5)] for i in range(5)]
    require(det5(identity) == 1, "Leibniz determinant of the identity is not 1")
    require(len(MASKS) == 20, "weight-2 and weight-3 subsets are not the 20 masks")
    require(len(set(TARGETS)) == 4, "the four targets are not distinct")
    require(add(TARGETS) == TOTAL, "the four targets do not sum to 4I")
    for target in TARGETS:
        require(trace(target) == 2, "a target trace is not 2")
        require(determinant(target) == Fraction(1, 2), "a target determinant is not 1/2")
        require(quad(target) == 1, "twice a target determinant is not 1")
        complement = (4 - target[0], 4 - target[1], -target[2])
        require(determinant(complement) == Fraction(17, 2), "det(4I-H) is not 17/2")
        matrix_expansion = 16 - 4 * trace(target) + determinant(target)
        require(matrix_expansion == Fraction(17, 2), "the complement expansion is not 17/2")
    require(determinant(TOTAL) == 16, "det(4I) is not 16")
    require(trace(TOTAL) == 8, "the trace of 4I is not 8")


def support_census():
    invertible = 0
    inconsistent = 0
    families = 0
    frozen_seen = {}
    for chosen in combinations(MASKS, 4):
        for masks in permutations(chosen):
            rows, rhs = incidence(masks, TARGETS, TOTAL)
            denominator = det5(rows)
            if denominator != 0:
                invertible += 1
                _, numerators = cramer(rows, rhs)
                require(
                    residual_ok(rows, rhs, numerators, denominator),
                    "Cramer residual failed for " + str(masks),
                )
                off_cone = False
                for coords in numerators:
                    if quad(coords) != 0 or coords == (0, 0, 0):
                        off_cone = True
                        break
                require(off_cone, "invertible system met the rank-one cone at " + str(masks))
                continue
            forward = rref_family(rows, rhs, False)
            backward = rref_family(rows, rhs, True)
            require(forward[0] == backward[0], "elimination order disagreed on " + str(masks))
            if forward[0] == "inconsistent":
                inconsistent += 1
                continue
            require(forward[0] == "family", "singular system was not discharged: " + str(forward))
            require(forward[1] == backward[1], "frozen frames depended on elimination order")
            families += 1
            killed = False
            for frame in forward[1]:
                require(all(value.denominator == 1 for value in frame), "a frozen frame is not integral")
                key = tuple(int(value) for value in frame)
                frozen_seen[key] = frozen_seen.get(key, 0) + 1
                if not rank_one_nonzero(frame):
                    killed = True
            require(killed, "a rank-4 family kept every frozen frame on the cone")
    require(invertible == 71040, "invertible count changed: " + str(invertible))
    require(inconsistent == 44520, "inconsistent count changed: " + str(inconsistent))
    require(families == 720, "rank-4 family count changed: " + str(families))
    require(invertible + inconsistent + families == 116280, "the support domain was not fully counted")
    require(set(frozen_seen) == BAD_FROZEN, "frozen frames changed: " + str(sorted(frozen_seen)))
    for frame in BAD_FROZEN:
        require(determinant(frame) in (Fraction(4), Fraction(-1)), "a named frozen frame is rank one")
        require(frozen_seen[frame] == 120, "frozen frame " + str(frame) + " is not seen 120 times")


def hand_examples():
    rows, rhs = incidence(HAND_MASKS, TARGETS, TOTAL)
    denominator, numerators = cramer(rows, rhs)
    require(denominator == -2, "the worked incidence determinant is not -2")
    frames = tuple(tuple(Fraction(numerators[column][coord], denominator) for coord in range(3)) for column in range(5))
    require(frames == HAND_FRAMES, "the worked five frames moved")
    for frame in frames:
        require(quad(frame) != 0, "the worked example met the rank-one cone")
    singular_rows, singular_rhs = incidence(SINGULAR_MASKS, TARGETS, TOTAL)
    require(det5(singular_rows) == 0, "the singular fixture is invertible")
    # One explicit point on this affine line. The third frame vanishes only at
    # this parameter value; the fifth frame is the frozen one.
    point = ((2, 1, -1), (-1, -1, 2), (0, 0, 0), (1, 2, -1), (2, 2, 0))
    for row in range(5):
        for coord in range(3):
            got = sum(singular_rows[row][column] * point[column][coord] for column in range(5))
            require(got == singular_rhs[coord][row], "singular point misses an equation")
    require(quad(point[4]) == 8, "twice det(2I) is not 8")
    family = rref_family(singular_rows, singular_rhs, False)
    require(family[0] == "family", "the singular fixture is not a rank-4 family")
    require(family[1] == ((Fraction(2), Fraction(2), Fraction(0)),), "the singular fixture does not freeze 2I")


def positive_control():
    witness = tuple(coefficient(direction, scale) for direction, scale in zip(WITNESS_DIRECTIONS, WITNESS_SCALES))
    require(witness == tuple(tuple(Fraction(value) for value in frame) for frame in WITNESS_FRAMES), "witness frames moved")
    require(add(witness) == tuple(Fraction(value) for value in TOTAL), "witness does not sum to 4I")
    for frame in witness:
        require(rank_one_nonzero(frame), "witness frame is not rank one")
    fake_targets = []
    for mask in HAND_MASKS:
        chosen = [witness[index] for index in range(5) if mask & (1 << index)]
        fake_targets.append(add(chosen))
    rows, rhs = incidence(HAND_MASKS, fake_targets, add(witness))
    denominator, numerators = cramer(rows, rhs)
    require(denominator != 0, "the positive-control incidence is singular")
    recovered = tuple(
        tuple(Fraction(numerators[column][coord], denominator) for coord in range(3)) for column in range(5)
    )
    require(recovered == witness, "the solver did not recover the declared rank-one frames")
    tampered = (fake_targets[0], fake_targets[1], fake_targets[2], add((fake_targets[3], (1, 0, 0))))
    tampered_rows, tampered_rhs = incidence(HAND_MASKS, tampered, add(witness))
    _, tampered_nums = cramer(tampered_rows, tampered_rhs)
    tampered_frames = tuple(
        tuple(Fraction(tampered_nums[column][coord], denominator) for coord in range(3)) for column in range(5)
    )
    require(tampered_frames != witness, "tampered targets still recovered the witness")


def witness_parity(frames):
    images = {
        (0, 0): parity((0, 0, 0)),
        (1, 0): parity(frames[1]),
        (0, 1): parity(frames[3]),
        (1, 1): parity(add((frames[1], frames[3]))),
    }
    require(images[(1, 0)] == (1, 0), "(0,1) at scale -1 does not have parity (1,0)")
    require(images[(0, 1)] == (0, 1), "(1,1) at scale -1/2 does not have parity (0,1)")
    require(images[(1, 1)] == (1, 1), "the sum of those two frames does not have parity (1,1)")
    require(set(images.values()) == {(0, 0), (1, 0), (0, 1), (1, 1)}, "parity image is not full")
    require(images[(1, 0)][0] == 1, "an AB shape would kill every frame")
    require(images[(0, 1)][1] == 1, "a PQ shape would kill every frame")


def witness_character(frames):
    detected_calls = sum(parity(frame)[1] for frame in frames)
    detected_targets = sum(parity(tuple(Fraction(value) for value in target))[1] for target in TARGETS)
    require(detected_calls == 2, "P-coefficient detects something other than two calls")
    require(detected_targets == 4, "P-coefficient does not detect every target")
    require(detected_calls < detected_targets, "witness is not a direct character obstruction")


def witness_support(frames):
    rows = {tuple(Fraction(value) for value in target) for target in TARGETS}
    hits = []
    for mask in range(1, 32):
        chosen = [frames[index] for index in range(5) if mask & (1 << index)]
        if add(chosen) in rows:
            hits.append(mask)
    require(hits == [], "witness subset sums hit a target: " + str(hits))


def failure_controls():
    require(determinant((1, 1, 0)) == 1, "det I changed")
    require(not rank_one_nonzero((1, 1, 0)), "I was accepted as rank one")
    require(rank_one_nonzero((0, 0, 0)) is False, "the zero matrix was accepted")
    broken = add((WITNESS_FRAMES[0], (1, 0, 0)))
    require(quad(broken) != 0, "tampering the witness by A kept it rank one")


def main():
    target_identities()
    hand_examples()
    positive_control()
    witness = tuple(coefficient(direction, scale) for direction, scale in zip(WITNESS_DIRECTIONS, WITNESS_SCALES))
    witness_parity(witness)
    witness_character(witness)
    witness_support(witness)
    failure_controls()
    support_census()
    print("PASS five-signed-once-support checks")


if __name__ == "__main__":
    main()
