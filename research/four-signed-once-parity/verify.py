#!/usr/bin/env python3
"""Checks for the four-call signed-frame equation R+S+T+U = 4I.

PROOF.md holds the argument. This program checks the determinant
identities, exhausts the 15 pair graphs, and checks one declared
parity-image witness. The graph list is the whole set of 4-edge
patterns on four calls. The witness is one solution, not a census.
"""

from fractions import Fraction
from itertools import combinations


EDGES = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))

WITNESS_DIRECTIONS = ((0, 1), (1, -1), (1, 1), (1, 2))
WITNESS_SCALES = (Fraction(-3), Fraction(5, 2), Fraction(1, 2), Fraction(1))


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def coefficient(direction, scale):
    x, y = direction
    return tuple(scale * value for value in (x * (x - y), y * (y - x), 2 * x * y))


def determinant(frame):
    a, b, c = frame
    return a * b + c * (a + b) / 2


def trace(frame):
    return frame[0] + frame[1] + frame[2]


def add(frames):
    return tuple(sum(frame[i] for frame in frames) for i in range(3))


def scale(frame, factor):
    return tuple(factor * value for value in frame)


def rank_one_nonzero(frame):
    return frame != (0, 0, 0) and determinant(frame) == 0


def targets():
    a = (1, 0, 0)
    b = (0, 1, 0)
    p = (0, 0, 1)
    q = (1, 1, -1)
    return (
        add((a, p)),
        add((a, q)),
        add((b, p)),
        add((b, q)),
    )


def parity(frame):
    require(all(value.denominator == 1 for value in frame), "parity on a non-integral frame")
    return ((int(frame[0]) + int(frame[1])) % 2, int(frame[2]) % 2)


def degrees(graph):
    counts = [0, 0, 0, 0]
    for i, j in graph:
        counts[i] += 1
        counts[j] += 1
    return tuple(sorted(counts, reverse=True))


def formal_edge_sum(graph):
    total = [0, 0, 0, 0]
    for i, j in graph:
        total[i] += 1
        total[j] += 1
    return tuple(total)


def target_identities():
    rows = targets()
    require(add(rows) == (4, 4, 0), "the four targets do not sum to 4I")
    for row in rows:
        require(trace(row) == 2, "a target trace is not 2")
        require(determinant(row) == Fraction(1, 2), "a target determinant is not 1/2")
        complement = add(((4, 4, 0), scale(row, -1)))
        require(determinant(complement) == Fraction(17, 2), "det(4I-H) is not 17/2")
        require(determinant(scale(row, Fraction(-1, 2))) == Fraction(1, 8), "det(-H/2) is not 1/8")


def pair_patterns():
    graphs = list(combinations(EDGES, 4))
    require(len(graphs) == 15, "pair patterns are not the 15 four-edge graphs")
    seen = {}
    for graph in graphs:
        kind = degrees(graph)
        seen[kind] = seen.get(kind, 0) + 1
        edge_sum = formal_edge_sum(graph)
        if kind == (2, 2, 2, 2):
            require(edge_sum == (2, 2, 2, 2), "a 2-regular edge sum is not twice the total")
        elif kind == (3, 2, 2, 1):
            counts = [0, 0, 0, 0]
            for i, j in graph:
                counts[i] += 1
                counts[j] += 1
            hub = counts.index(3)
            leaf_edge = next(edge for edge in graph if hub not in edge)
            difference = [edge_sum[i] - 1 for i in range(4)]
            expected = [0, 0, 0, 0]
            expected[hub] = 2
            expected[leaf_edge[0]] += 1
            expected[leaf_edge[1]] += 1
            require(tuple(difference) == tuple(expected), "leaf reduction failed for " + str(graph))
        else:
            raise SystemExit("FAIL: unexpected degree sequence " + str(kind))
    require(seen == {(2, 2, 2, 2): 3, (3, 2, 2, 1): 12}, "degree census changed: " + str(seen))


def witness_frames():
    frames = [
        coefficient(direction, scale)
        for direction, scale in zip(WITNESS_DIRECTIONS, WITNESS_SCALES)
    ]
    require(add(frames) == (4, 4, 0), "witness does not sum to 4I")
    for frame in frames:
        require(rank_one_nonzero(frame), "witness frame is not rank one")
    return tuple(frames)


def witness_parity(frames):
    images = {
        (0, 0): parity((0, 0, 0)),
        (1, 0): parity(frames[0]),
        (0, 1): parity(frames[1]),
        (1, 1): parity(add((frames[1], frames[3]))),
    }
    require(images[(1, 0)] == (1, 0), "R does not have parity (1,0)")
    require(images[(0, 1)] == (0, 1), "S does not have parity (0,1)")
    require(images[(1, 1)] == (1, 1), "S+U does not have parity (1,1)")
    require(set(images.values()) == {(0, 0), (1, 0), (0, 1), (1, 1)}, "parity image is not full")
    # An AB form reduces to a+b mod 2, and a PQ form reduces to c mod 2.
    require(images[(1, 0)][0] == 1, "AB shape would kill every frame")
    require(images[(0, 1)][1] == 1, "PQ shape would kill every frame")


def witness_character(frames):
    detected_calls = sum(parity(frame)[1] for frame in frames)
    detected_targets = sum(parity(row)[1] for row in targets())
    require(detected_calls == 2, "P-coefficient detects something other than two calls")
    require(detected_targets == 4, "P-coefficient does not detect every target")
    require(detected_calls < detected_targets, "witness is not a direct character obstruction")


def witness_support(frames):
    rows = set(targets())
    hits = []
    for mask in range(1, 16):
        chosen = [frames[i] for i in range(4) if mask & (1 << i)]
        if add(chosen) in rows:
            hits.append(mask)
    require(hits == [], "witness subset sums hit a target: " + str(hits))


def failure_controls(frames):
    broken = (frames[0], frames[1], frames[2], add((frames[3], (1, 0, 0))))
    require(add(broken) != (4, 4, 0), "tampered witness still sums to 4I")
    # I has coefficient (1,1,0) and determinant 1, so it is not rank one.
    require(determinant((1, 1, 0)) == 1, "det I changed")
    require(not rank_one_nonzero((1, 1, 0)), "I was accepted as rank one")
    require(rank_one_nonzero((0, 0, 0)) is False, "the zero matrix was accepted")


def main():
    target_identities()
    pair_patterns()
    frames = witness_frames()
    witness_parity(frames)
    witness_character(frames)
    witness_support(frames)
    failure_controls(frames)
    print("PASS four-signed-once-parity checks")


if __name__ == "__main__":
    main()
