#!/usr/bin/env python3
"""Checks for four rank-one frames plus one old projector.

PROOF.md is the argument. The checks below are exact arithmetic for that
case split, two declared sum-solutions, and an independent census of every
carrying-pair assignment. The census solves linear systems; it does not
search directions or scales.
"""

from fractions import Fraction
from itertools import permutations, product
from math import gcd


FOUR = (4, 4, 0)
A = (1, 0, 0)
B = (0, 1, 0)
P = (0, 0, 1)
Q = (1, 1, -1)
PROJECTORS = {"A": A, "B": B, "P": P, "Q": Q}
TARGET_NAMES = ("AP", "AQ", "BP", "BQ")
TARGETS = {
    "AP": (1, 0, 1),
    "AQ": (2, 1, -1),
    "BP": (0, 1, 1),
    "BQ": (1, 2, -1),
}
EDGES = (
    (0, 1), (0, 2), (0, 3), (0, 4),
    (1, 2), (1, 3), (1, 4),
    (2, 3), (2, 4),
    (3, 4),
)
EXPECTED_INCIDENT = {
    "A": (("AP", 0, P), ("AQ", 0, Q)),
    "B": (("BP", 0, P), ("BQ", 0, Q)),
    "P": (("AP", 0, A), ("BP", 0, B)),
    "Q": (("AQ", 0, A), ("BQ", 0, B)),
}


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def add(frames):
    total = [0, 0, 0]
    for frame in frames:
        for index in range(3):
            total[index] += frame[index]
    return tuple(total)


def sub(left, right):
    return tuple(left[index] - right[index] for index in range(3))


def trace(frame):
    return frame[0] + frame[1] + frame[2]


def determinant(frame):
    a, b, c = (Fraction(value) for value in frame)
    return a * b + c * (a + b) / 2


def rank_one_nonzero(frame):
    return frame != (0, 0, 0) and determinant(frame) == 0


def parity(frame):
    return ((frame[0] + frame[1]) % 2, frame[2] % 2)


def carrying(name, bit):
    target = TARGETS[name]
    if bit == 0:
        return target
    return sub(FOUR, target)


def matrix(frame):
    a, b, c = frame
    half = Fraction(c, 2)
    return ((a + half, half), (half, b + half))


def determinant_matrix(rows):
    return rows[0][0] * rows[1][1] - rows[0][1] * rows[1][0]


def coefficient(direction, scale):
    x, y = direction
    factor = Fraction(scale)
    return (factor * x * (x - y), factor * y * (y - x), factor * 2 * x * y)


def target_hits(labels):
    wanted = set(TARGETS.values())
    found = []
    width = len(labels)
    for mask in range(1, 1 << width):
        chosen = [labels[index] for index in range(width) if mask & (1 << index)]
        total = add(chosen)
        if total in wanted:
            found.append((mask, total, len(chosen)))
    return found


def target_identities():
    require(add(TARGETS.values()) == FOUR, "the four targets do not sum to 4I")
    for name in TARGET_NAMES:
        target = TARGETS[name]
        require(trace(target) == 2, name + " does not have trace 2")
        require(determinant(target) == Fraction(1, 2), name + " does not have determinant 1/2")
        require(parity(target) == (1, 1), name + " does not have parity (1,1)")
        complement = sub(FOUR, target)
        require(trace(complement) == 6, name + " complement does not have trace 6")
        require(determinant(complement) == Fraction(17, 2), name + " complement determinant changed")
        require(parity(complement) == (1, 1), name + " complement is not parity (1,1)")
        require(not rank_one_nonzero(complement), name + " complement was accepted as rank one")


def automorphism_checks():
    basis = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    samples = list(basis) + list(PROJECTORS.values()) + list(TARGETS.values())
    samples.append((2, 2, 0))
    for frame in samples:
        swapped = (frame[1], frame[0], frame[2])
        reflected = (frame[0] + frame[2], frame[1] + frame[2], -frame[2])
        require(determinant(swapped) == determinant(frame), "coordinate swap changed a determinant")
        require(determinant(reflected) == determinant(frame), "sign flip changed a determinant")
        require(matrix(swapped) == (
            (matrix(frame)[1][1], matrix(frame)[1][0]),
            (matrix(frame)[0][1], matrix(frame)[0][0]),
        ), "coordinate swap is not conjugation by the exchange matrix")
        raw = matrix(frame)
        reflected_matrix = ((raw[0][0], -raw[0][1]), (-raw[1][0], raw[1][1]))
        require(matrix(reflected) == reflected_matrix, "sign flip is not conjugation by diag(1,-1)")
        require(determinant_matrix(reflected_matrix) == determinant_matrix(raw),
                "sign flip failed to preserve the matrix determinant")
    require((B[1], B[0], B[2]) == A, "swap does not exchange A and B")
    require((P[0] + P[2], P[1] + P[2], -P[2]) == Q, "sign flip does not exchange P and Q")
    require((Q[0] + Q[2], Q[1] + Q[2], -Q[2]) == P, "sign flip does not exchange Q and P")
    for name, image in (("AP", "BP"), ("AQ", "BQ"), ("BP", "AP"), ("BQ", "AQ")):
        frame = TARGETS[name]
        require((frame[1], frame[0], frame[2]) == TARGETS[image], "swap moved " + name + " incorrectly")


def star_obstruction():
    # 3 tr(C) = 4k. The center trace is 1, or one more or less than an edge trace.
    require(3 * 1 % 4 != 0, "three times the projector trace became divisible by 4")
    for edge_trace in (2, 6):
        center_trace = edge_trace - 1
        require(3 * center_trace % 4 != 0, "a leaf placement made the star trace equation possible")


def path_and_fork_identities():
    def matrices():
        yield ((0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0))
        for slot in range(4):
            for axis in range(3):
                rows = [(0, 0, 0)] * 4
                value = [0, 0, 0]
                value[axis] = 1
                rows[slot] = tuple(value)
                yield tuple(rows)

    for row in matrices():
        m0, m1, m2, m3 = row
        f0 = sub(sub(FOUR, m1), m3)
        f1 = sub(m0, f0)
        f2 = sub(m1, f1)
        f3 = sub(m2, f2)
        f4 = sub(m3, f3)
        require(add((f0, f1, f2, f3, f4)) == FOUR, "path propagation missed 4I")
        require(add((f0, f1)) == m0 and add((f1, f2)) == m1, "path edge equation failed")
        require(add((f2, f3)) == m2 and add((f3, f4)) == m3, "path edge equation failed")
        center = sub(add((m0, m1, m2)), FOUR)
        branch = sub(m3, center)
        leaves = (sub(m0, center), sub(m1, center), sub(m2, branch))
        require(add((center, branch, leaves[0], leaves[1], leaves[2])) == FOUR, "fork sum failed")
    for bits in range(16):
        edge_traces = [2 if (bits >> index) & 1 else 6 for index in range(4)]
        path_traces = (
            8 - edge_traces[1] - edge_traces[3],
            edge_traces[0] + edge_traces[1] + edge_traces[3] - 8,
            8 - edge_traces[0] - edge_traces[3],
            edge_traces[0] + edge_traces[2] + edge_traces[3] - 8,
            8 - edge_traces[0] - edge_traces[2],
        )
        fork_center = edge_traces[0] + edge_traces[1] + edge_traces[2] - 8
        fork_branch = edge_traces[3] - fork_center
        fork_traces = (
            fork_center,
            fork_branch,
            edge_traces[0] - fork_center,
            edge_traces[1] - fork_center,
            edge_traces[2] - fork_branch,
        )
        for value in path_traces + fork_traces:
            require(value % 2 == 0, "a tree vertex trace became odd")
            require(value != 1, "a tree vertex had the projector trace")


def isolated_projector_trace():
    for old in PROJECTORS.values():
        require(trace(sub(FOUR, old)) == 7, "4I-E does not have trace 7")
        for left in (2, 6):
            for right in (2, 6):
                require(left + right != 7, "two edge traces summed to the odd residual")


def incident_edges(name):
    old = PROJECTORS[name]
    found = []
    for target_name in TARGET_NAMES:
        for bit in (0, 1):
            value = carrying(target_name, bit)
            frame = sub(value, old)
            if rank_one_nonzero(frame):
                found.append((target_name, bit, frame))
    found.sort()
    expected = tuple(sorted(EXPECTED_INCIDENT[name]))
    require(tuple(found) == expected, name + " incident edges changed: " + str(found))
    return found


def c4_survivors(name):
    found = incident_edges(name)
    old = PROJECTORS[name]
    names = [item[0] for item in found]
    rest = [target_name for target_name in TARGET_NAMES if target_name not in names]
    require(len(rest) == 2, name + " did not leave two opposite targets")
    survivors = []
    for orient in (0, 1):
        edge_x, edge_y = (names[0], names[1]) if orient == 0 else (names[1], names[0])
        for bit_x in (0, 1):
            for bit_y in (0, 1):
                for swap in (0, 1):
                    opposite_x, opposite_y = (rest[0], rest[1]) if swap == 0 else (rest[1], rest[0])
                    mx = carrying(edge_x, 0)
                    my = carrying(edge_y, 0)
                    rx = carrying(opposite_x, bit_x)
                    ry = carrying(opposite_y, bit_y)
                    if add((mx, ry)) != add((my, rx)):
                        continue
                    frames = (
                        sub(mx, old),
                        sub(my, old),
                        add((sub(rx, mx), old)),
                        sub(sub(FOUR, my), rx),
                    )
                    require(not all(rank_one_nonzero(frame) for frame in frames),
                            name + " C4 survivor was rank one")
                    survivors.append(tuple(sorted(frames)))
    require(len(survivors) == 4, name + " had " + str(len(survivors)) + " C4 survivors")
    kinds = set(survivors)
    require(len(kinds) == 2, name + " survivor patterns changed")
    flat = [determinant(frame) for frames in kinds for frame in frames]
    require(Fraction(4) in flat and Fraction(6) in flat and Fraction(-1) in flat,
            name + " survivor determinants changed: " + str(flat))
    two_i = (2, 2, 0)
    require(any(two_i in frames for frames in kinds), name + " lost the 2I near-miss")
    return survivors


def declared_solutions():
    axial = [
        coefficient(direction, scale)
        for direction, scale in (((1, 0), 4), ((0, 1), 2), ((1, 1), -2), ((1, 2), 1))
    ]
    diagonal = [
        coefficient(direction, scale)
        for direction, scale in (
            ((1, 0), 1),
            ((0, 1), 1),
            ((1, 1), 1),
            ((1, -1), Fraction(3, 2)),
        )
    ]
    require(add(axial) == sub(FOUR, A), "axial solution does not sum to 4I-A")
    require(add(diagonal) == sub(FOUR, P), "diagonal solution does not sum to 4I-P")
    for frame in axial + diagonal:
        require(rank_one_nonzero(frame), "declared frame is not rank one")
    axial_hits = target_hits(axial + [A])
    diagonal_hits = target_hits(diagonal + [P])
    require(axial_hits == [], "axial solution gained a target subset: " + str(axial_hits))
    pair_hits = [hit for hit in diagonal_hits if hit[2] == 2]
    require(len(pair_hits) == 2, "diagonal solution did not keep exactly two pair hits")
    require(len({hit[1] for hit in diagonal_hits}) == 2, "diagonal solution meets more than two targets")
    covered = {hit[1] for hit in diagonal_hits}
    require(covered == {TARGETS["AP"], TARGETS["BP"]}, "diagonal pair hits are not A+P and B+P")
    positive = target_hits([A, B, P, Q, (2, 2, 0)])
    require(len({hit[1] for hit in positive}) == 4, "positive control missed a target")
    require(not rank_one_nonzero((2, 2, 0)), "2I was accepted as rank one")
    broken = (add((axial[0], (1, 0, 0))),) + tuple(axial[1:])
    require(add(broken) != sub(FOUR, A), "tampered solution still sums to 4I-A")
    require(determinant((1, 1, 0)) == 1, "det I changed")
    require(not rank_one_nonzero((1, 1, 0)), "I was accepted as rank one")
    require(rank_one_nonzero((0, 0, 0)) is False, "zero was accepted as rank one")


def pair_rows(left, right, rhs, old):
    rows = []
    for axis in range(3):
        row = [0] * 13
        for vertex, sign in ((left, 1), (right, 1)):
            if vertex < 4:
                row[3 * vertex + axis] += sign
            else:
                row[12] -= old[axis]
        row[12] += rhs[axis]
        rows.append(row)
    return rows


def total_rows(old):
    residual = sub(FOUR, old)
    rows = []
    for axis in range(3):
        row = [0] * 13
        for vertex in range(4):
            row[3 * vertex + axis] = 1
        row[12] = residual[axis]
        rows.append(row)
    return rows


def solve(rows):
    working = [row[:] for row in rows]
    width = 12
    height = len(working)
    cursor = 0
    pivots = []
    for column in range(width):
        selected = None
        best = None
        for index in range(cursor, height):
            value = working[index][column]
            if value and (best is None or abs(value) < best):
                best = abs(value)
                selected = index
        if selected is None:
            continue
        working[cursor], working[selected] = working[selected], working[cursor]
        divisor = 0
        for index in range(column, width + 1):
            divisor = gcd(divisor, working[cursor][index])
        if working[cursor][column] < 0:
            divisor = -divisor
        if divisor not in (0, 1):
            for index in range(column, width + 1):
                working[cursor][index] //= divisor
        pivot = working[cursor][column]
        for index in range(height):
            if index == cursor or working[index][column] == 0:
                continue
            factor = working[index][column]
            reduced = gcd(pivot, factor)
            pivot_scale = pivot // reduced
            factor_scale = factor // reduced
            for entry in range(column, width + 1):
                working[index][entry] = (
                    pivot_scale * working[index][entry] - factor_scale * working[cursor][entry]
                )
        pivots.append(column)
        cursor += 1
        if cursor == height:
            break
    for index in range(cursor, height):
        if working[index][width]:
            return None
    free = [column for column in range(width) if column not in pivots]
    if free:
        return ("free", len(free))
    solution = [0] * width
    for index, column in enumerate(pivots):
        for other in range(width):
            if other != column and working[index][other]:
                return ("dirty", column)
        pivot = working[index][column]
        rhs = working[index][width]
        if rhs % pivot:
            return ("nonint", column)
        solution[column] = rhs // pivot
    return solution


def frames_of(solution):
    return tuple(tuple(solution[3 * index:3 * index + 3]) for index in range(4))


def integer_determinant(frame):
    a, b, c = frame
    return 2 * a * b + c * (a + b)


def census():
    options = [(TARGETS[name], sub(FOUR, TARGETS[name])) for name in TARGET_NAMES]
    for name, old in PROJECTORS.items():
        base_rows = total_rows(old)
        inconsistent = solved = free = nonint = dirty = hits = 0
        checked = 0
        for chosen in permutations(range(10), 4):
            edges = [EDGES[index] for index in chosen]
            for bits in product((0, 1), repeat=4):
                checked += 1
                rows = [row[:] for row in base_rows]
                for edge, bit, choices in zip(edges, bits, options):
                    rows.extend(pair_rows(edge[0], edge[1], choices[bit], old))
                answer = solve(rows)
                if answer is None:
                    inconsistent += 1
                    continue
                if isinstance(answer, tuple) and answer[0] == "free":
                    free += 1
                    continue
                if isinstance(answer, tuple) and answer[0] == "nonint":
                    nonint += 1
                    continue
                if isinstance(answer, tuple):
                    dirty += 1
                    continue
                solved += 1
                degrees = [0, 0, 0, 0, 0]
                for edge in edges:
                    degrees[edge[0]] += 1
                    degrees[edge[1]] += 1
                require(degrees[4] == 2, name + " consistent graph did not put E on the cycle")
                require(sorted(degrees) == [0, 2, 2, 2, 2], name + " consistent degree sequence changed")
                frames = frames_of(answer)
                if all(frame != (0, 0, 0) and integer_determinant(frame) == 0 for frame in frames):
                    hits += 1
        require(checked == 80640, name + " census missed an assignment")
        require(inconsistent == 80064 and solved == 576, name + " census counts changed")
        require(free == nonint == dirty == hits == 0, name + " census accepted a non-rigid or rank-one solution")
    near = solve(
        total_rows(A)
        + pair_rows(0, 4, TARGETS["AP"], A)
        + pair_rows(2, 4, TARGETS["AQ"], A)
        + pair_rows(0, 1, TARGETS["BP"], A)
        + pair_rows(1, 2, TARGETS["BQ"], A)
    )
    require(frames_of(near) == (P, B, Q, (2, 2, 0)), "near-miss round trip changed")
    tampered = solve(
        total_rows(A)
        + pair_rows(0, 4, add((TARGETS["AP"], (1, 0, 0))), A)
        + pair_rows(2, 4, TARGETS["AQ"], A)
        + pair_rows(0, 1, TARGETS["BP"], A)
        + pair_rows(1, 2, TARGETS["BQ"], A)
    )
    require(tampered is None, "tampered near-miss stayed consistent")


def main():
    target_identities()
    automorphism_checks()
    star_obstruction()
    path_and_fork_identities()
    isolated_projector_trace()
    for name in PROJECTORS:
        c4_survivors(name)
    declared_solutions()
    census()
    print("PASS four-signed-one-old checks")


if __name__ == "__main__":
    main()
