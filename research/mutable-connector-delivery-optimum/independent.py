#!/usr/bin/env python3
"""Separate all-word oracle and bit interpreter; imports no primary verifier.

Ross Richardson with OpenAI Codex assistance. Apache-2.0. Independent here
means implementation/method, not an independent author or human review.
"""
from fractions import Fraction
import hashlib
import heapq
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def demand(ok, message):
    if not ok:
        raise ValueError(message)


def shortest(b, d, a, delayed=False):
    """Dijkstra on actual scalar-identity query states, with unbounded loops.

    Stage 2i is request i; 2i+1 is its mutation cut. z stores source
    coefficients (its dirty coefficient is always one), y also stores the
    current output's dirty-connector coefficient. Completed outputs are fixed.
    No connector parity DP, paired-readout assumption or source-count bound.
    """
    k = len(b)
    origin = (0, 0, 0)
    distance, queue = {origin: 0}, [(0, origin)]
    settled = 0
    while queue:
        price, state = heapq.heappop(queue)
        if distance[state] != price:
            continue
        settled += 1
        stage, z, y = state
        i = stage // 2
        edges = []
        if stage % 2:
            edges.append(((stage, z ^ (1 << (i + 1)), 0), d[i]))
            edges.append(((stage + 1, z, 0), 0))
        else:
            source = (1 << (i + 1)) - 1
            if i == k - 1 and y == source and z == 0:
                return price, settled
            edges.append(((stage, z ^ source, y), b[i]))
            edges.append(((stage, z, y ^ z ^ (1 << k)), a[i]))
            if i < k - 1 and y == source:
                edges.append(((stage + 1, z, 0), 0))
        if delayed:
            # Relaxation: any previous correction remains available, even
            # inside later output intervals. The same lower bound must hold.
            for j in range(i):
                edges.append(((stage, z ^ (1 << (j + 1)), y), d[j]))
        for endpoint, charge in edges:
            proposed = price + charge
            if endpoint not in distance or proposed < distance[endpoint]:
                distance[endpoint] = proposed
                heapq.heappush(queue, (proposed, endpoint))
    raise ValueError("finite quotient has no accepting path")


def all_tariffs():
    rows, states, relaxed_states = [], 0, 0
    for k in range(1, 5):
        readers = [1 + i % 2 for i in range(k)]
        for b in itertools.product([1, 3], repeat=k):
            for d in itertools.product([1, 2, 5], repeat=k - 1):
                cost, visited = shortest(b, d, readers)
                relaxed, visited_relaxed = shortest(b, d, readers, delayed=True)
                demand(cost == relaxed, "delayed adapter lowers claimed optimum")
                rows.append([list(b), list(d), readers[:], str(cost)])
                states += visited
                relaxed_states += visited_relaxed
    encoded = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    return len(rows), hashlib.sha256(encoded).hexdigest(), states, relaxed_states


def apply_matrix(matrix, values):
    out = []
    for mask in matrix:
        value = 0
        for j, entry in enumerate(values):
            if mask & (1 << j):
                value ^= entry
        out.append(value)
    return out


def xor_vectors(left, right):
    return [x ^ y for x, y in zip(left, right)]


def small_maps():
    """All 4096 triples B,C0,C1 of 2x2 maps, all four boundary paths.

    Fixed distinct readers include singular and noncommuting maps. Every
    state entry is a formal bit-row on all 14 arbitrary input coordinates.
    """
    matrices = list(itertools.product(range(4), repeat=2))
    readers = [(2, 1), (1, 0), (3, 2)]
    cases = 0
    for B, C0, C1 in itertools.product(matrices, repeat=3):
        for p, q in itertools.product((0, 1), repeat=2):
            vectors = [[1 << (2 * i), 1 << (2 * i + 1)] for i in range(7)]
            x, u0, u1, z, y0, y1, y2 = vectors
            initial_z = z[:]
            ys, us, cs = [y0, y1, y2], [u0, u1], [C0, C1]
            expected, phase = [], 0
            for i, following in enumerate((p, q, 0)):
                expected.append(xor_vectors(ys[i], apply_matrix(readers[i], apply_matrix(B, x))))
                # Read/query/read; the optional extra B returns to the same type.
                ys[i] = xor_vectors(ys[i], apply_matrix(readers[i], z))
                z = xor_vectors(z, apply_matrix(B, x))
                ys[i] = xor_vectors(ys[i], apply_matrix(readers[i], z))
                if phase == following:
                    z = xor_vectors(z, apply_matrix(B, x))
                demand(ys[i] == expected[i], "noncommuting-map delivery")
                if i < 2:
                    delta = apply_matrix(cs[i], us[i])
                    x = xor_vectors(x, delta)
                    if following:
                        z = xor_vectors(z, apply_matrix(B, delta))
                phase = following
            demand(z == initial_z and ys == expected, "noncommuting-map restoration")
            target_x = xor_vectors(vectors[0], xor_vectors(apply_matrix(C0, u0), apply_matrix(C1, u1)))
            demand(x == target_x, "noncommuting source endpoint")
            cases += 1
    return cases


def scalar_program(closed):
    """Independent fixed three-request lowering, including delivery markers."""
    # Bit positions: x 0..2, u 3..4, z 5..7, y0 8..10, y1 11..13, y2 14..16.
    # The canonical optimal tie choice closes request 0, then pairs 1 and 2.
    after = [0, 0, 0] if closed else [0, 1, 0]
    previous, program = 0, []
    B, A = (3, 6, 7), [(2, 4, 1), (3, 2, 4), (2, 4, 1)]
    def emit(matrix, src0, dst0):
        for row in range(3):
            for col in range(3):
                if matrix[row] & (1 << col):
                    program.append((src0 + col, dst0 + row))
    for i, following in enumerate(after):
        emit(A[i], 5, 8 + 3 * i)
        emit(B, 0, 5)
        emit(A[i], 5, 8 + 3 * i)
        if previous == following:
            emit(B, 0, 5)
        program.append(("deliver", i))
        if i < 2:
            program.append((3 + i, 0))
            if following:
                program.extend([(3 + i, 5), (3 + i, 7)])
        previous = following
    return program


def literal_program(receipt):
    p = receipt["three_output_pilot"]
    demand(p["k"] == 3 and p["bits"] == 17, "pilot domain")
    demand(p["x"] == [0, 1, 2] and p["u"] == [3, 4] and p["z"] == [5, 6, 7], "pilot addresses")
    demand(p["B"] == [3, 6, 7] and p["C"] == [1, 0, 0], "pilot maps")
    cuts = {count: i for i, count in p["deliveries"]}
    program = []
    for j, gate in enumerate(p["gates"], 1):
        demand(len(gate) == 2 and all(type(x) is int and 0 <= x < 17 for x in gate)
               and gate[0] != gate[1], "literal gate")
        program.append(tuple(gate))
        if j in cuts:
            program.append(("deliver", cuts[j]))
    demand(program == scalar_program(False), "independent literal lowering")
    return program


def exhaustive_pilot(program):
    readers = [[2, 4, 1], [3, 2, 4], [2, 4, 1]]
    for original in range(1 << 17):
        state, expected, x = original, original, original & 7
        target_outputs = []
        for i in range(3):
            bx = sum(((x & mask).bit_count() % 2) << j for j, mask in enumerate((3, 6, 7)))
            result = sum(((bx & mask).bit_count() % 2) << j for j, mask in enumerate(readers[i]))
            expected ^= result << (8 + 3 * i)
            target_outputs.append((expected >> (8 + 3 * i)) & 7)
            if i < 2:
                x ^= (original >> (3 + i)) & 1
        expected = (expected & ~7) | x
        delivered = 0
        for src, dst in program:
            if src == "deliver":
                demand(dst == delivered, "literal delivery order")
                demand((state >> (8 + 3 * dst)) & 7 == target_outputs[dst], "literal delivered value")
                delivered += 1
            else:
                if dst >= 8:
                    demand((dst - 8) // 3 == delivered, "literal output cut")
                state ^= ((state >> src) & 1) << dst
        demand(delivered == 3 and state == expected, "literal full dirty endpoint")
    return 1 << 17


def main():
    receipt = json.loads((HERE / "RESULT.json").read_text())
    count, digest, states, relaxed_states = all_tariffs()
    demand(type(receipt["tariff_cases"]) is int and receipt["tariff_cases"] == count, "tariff count")
    demand(receipt["tariff_digest"] == digest, "all-word quotient disagrees with DP")
    demand(shortest([10, 1, 10], [2, 2], [1, 1, 1])[0] == 32, "nonadjacent optimum")
    demand(shortest([Fraction(10, 3), Fraction(1, 3), Fraction(10, 3)],
                    [Fraction(2, 3)] * 2, [Fraction(1, 3)] * 3)[0] == Fraction(32, 3),
           "rational optimum")
    maps = small_maps()
    assignments = exhaustive_pilot(literal_program(receipt))
    demand(exhaustive_pilot(scalar_program(True)) == assignments, "closed pilot coverage")
    print("PASS_INDEPENDENT_MUTABLE_DELIVERY", "tariffs=" + str(count),
          "settled_states=" + str(states), "relaxed_states=" + str(relaxed_states),
          "map_paths=" + str(maps),
          "dirty_assignments_per_schedule=" + str(assignments), "schedules=2 no_new_kappa")


if __name__ == "__main__":
    main()
