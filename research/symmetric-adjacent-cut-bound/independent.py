#!/usr/bin/env python3
"""Independent exact checks; no imports from the producer or its certificates.

Ross Richardson, with substantial OpenAI Codex assistance. Apache-2.0.

Breadth-first search measures adjacent word distance without an inversion
formula. Separate bitset arithmetic checks complete F2[S_4] boundary operators,
including dirty input columns, while an ordered-pair image checks cut ranks.
This finite replay supports, and does not replace, the all-parameter proof.
"""

from collections import deque
from itertools import permutations, product
import json
from math import factorial


class Rejected(ValueError):
    """An exact mathematical contract was violated."""


def require(condition, message):
    if not condition:
        raise Rejected(message)


def xor_sum(values):
    answer = 0
    for value in values:
        answer ^= value
    return answer


def bits(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def rank(rows):
    pivots = {}
    for value in rows:
        while value:
            lead = value.bit_length() - 1
            if lead in pivots:
                value ^= pivots[lead]
            else:
                pivots[lead] = value
                break
    return len(pivots)


def identity(size):
    return tuple(1 << j for j in range(size))


def multiply(left, right):
    return tuple(xor_sum(right[k] for k in bits(row)) for row in left)


def inverse(matrix):
    size = len(matrix)
    rows = [row | (1 << (size + j)) for j, row in enumerate(matrix)]
    for column in range(size):
        pivot = next((j for j in range(column, size)
                      if (rows[j] >> column) & 1), None)
        require(pivot is not None, "singular scalar matrix")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        for j in range(size):
            if j != column and (rows[j] >> column) & 1:
                rows[j] ^= rows[column]
    result = tuple(row >> size for row in rows)
    require(multiply(matrix, result) == identity(size), "incorrect inverse")
    return result


def general_linear(size):
    return [rows for rows in product(range(1 << size), repeat=size)
            if rank(rows) == size]


def rank_one_idempotents(size):
    result = set()
    for u in range(1, 1 << size):
        for v in range(1, 1 << size):
            if (u & v).bit_count() % 2:
                result.add(tuple(v if (u >> j) & 1 else 0
                                 for j in range(size)))
    require(len(result) == ((1 << size) - 1) * (1 << (size - 1)),
            "rank-one idempotent enumeration")
    return sorted(result)


def adjacent(size, i):
    value = list(range(size))
    value[i], value[i + 1] = value[i + 1], value[i]
    return tuple(value)


def cayley_bfs(size):
    """Edges are left multiplication by adjacent swaps of VALUES."""
    unit = tuple(range(size))
    distance = {unit: 0}
    parent = {}
    queue = deque([unit])
    edges = 0
    while queue:
        value = queue.popleft()
        for i in range(size - 1):
            following = tuple(i + 1 if x == i else i if x == i + 1 else x
                              for x in value)
            edges += 1
            if following not in distance:
                distance[following] = distance[value] + 1
                parent[following] = (value, i)
                queue.append(following)
    require(len(distance) == factorial(size), "incomplete Cayley graph")
    words = {}
    for value in distance:
        current, backward = value, []
        while current != unit:
            current, generator = parent[current]
            backward.append(generator)
        words[value] = tuple(reversed(backward))
    return distance, words, edges


def permutation_crossing_rows(value):
    size = len(value)
    positive = [(a, b) for a in range(size) for b in range(a + 1, size)]
    negative_index = {(b, a): k for k, (a, b) in enumerate(positive)}
    rows = [0] * len(positive)
    for column, (a, b) in enumerate(positive):
        image = (value[a], value[b])
        if image in negative_index:
            rows[negative_index[image]] |= 1 << column
    return rows


class GroupAlgebra:
    """Complete group-algebra coefficients as XOR bitsets of permutations."""

    def __init__(self, size):
        self.size = size
        self.elements = list(permutations(range(size)))
        self.index = {g: j for j, g in enumerate(self.elements)}
        self.unit = 1 << self.index[tuple(range(size))]
        self.generators = [adjacent(size, j) for j in range(size - 1)]
        self.pairs = [(a, b) for a in range(size) for b in range(size) if a != b]
        self.pair_index = {pair: j for j, pair in enumerate(self.pairs)}
        self.images = [[self.pair_index[g[a], g[b]] for a, b in self.pairs]
                       for g in self.elements]
        self.left_images = {
            g: [self.index[tuple(g[h[j]] for j in range(size))]
                for h in self.elements]
            for g in self.generators
        }

    def left(self, generator, polynomial):
        return xor_sum(1 << self.left_images[generator][j] for j in bits(polynomial))

    def endpoint(self, targets, roles):
        rows = [[0] * roles for _ in range(roles)]
        for j in range(roles):
            rows[j][j] = (1 << self.index[targets[j]]) if j < len(targets) else self.unit
        return rows

    def scalar(self, scalar, operator):
        return [[xor_sum(operator[k][c] for k in bits(scalar[r]))
                 for c in range(len(scalar))] for r in range(len(scalar))]

    def paid(self, idempotent, generator, operator):
        roles = len(idempotent)
        differences = [[self.left(generator, item) ^ item for item in row]
                       for row in operator]
        return [[operator[r][c] ^ xor_sum(differences[k][c]
                 for k in bits(idempotent[r])) for c in range(roles)]
                for r in range(roles)]

    def represented(self, operator):
        roles, dimension = len(operator), len(self.pairs)
        rows = [0] * (roles * dimension)
        for r in range(roles):
            for c in range(roles):
                for g in bits(operator[r][c]):
                    for input_pair, output_pair in enumerate(self.images[g]):
                        rows[r * dimension + output_pair] ^= 1 << (c * dimension + input_pair)
        return tuple(rows)

    def crossing_rank(self, represented):
        dimension = len(self.pairs)
        positive = [j for j in range(len(represented))
                    if self.pairs[j % dimension][0] < self.pairs[j % dimension][1]]
        negative = [j for j in range(len(represented))
                    if self.pairs[j % dimension][0] > self.pairs[j % dimension][1]]
        mask = xor_sum(1 << j for j in positive)
        return rank([represented[j] & mask for j in negative])

    def admit_scalar(self, operator):
        require(all(item in (0, self.unit) for row in operator for item in row),
                "free scalar cannot change the address")
        scalar = tuple(xor_sum(1 << j for j, item in enumerate(row) if item)
                       for row in operator)
        require(rank(scalar) == len(scalar), "free scalar must be invertible")

    def admit_paid(self, idempotent, generator):
        require(generator in self.generators, "paid address must be adjacent")
        require(rank(idempotent) == 1, "paid scalar coefficient must have rank one")
        require(multiply(idempotent, idempotent) == idempotent,
                "paid scalar coefficient must be idempotent")


def equal_boundary(actual, expected):
    require(actual == expected, "complete formal dirty boundary differs")


def must_reject(operation, name, reason):
    try:
        operation()
    except Rejected as error:
        if str(error) != reason:
            raise RuntimeError("wrong rejection reason for " + name + ": " + str(error)) from error
        return name
    raise RuntimeError("negative control unexpectedly accepted: " + name)


def conjugated_run(algebra, words, targets, scalar, check_prefixes=False):
    roles = len(scalar)
    undo = inverse(scalar)
    operator = algebra.scalar(scalar, algebra.endpoint([], roles))
    calls = 0
    for role, target in enumerate(targets):
        projector = tuple((1 << role) if j == role else 0 for j in range(roles))
        projector = multiply(multiply(scalar, projector), undo)
        for generator_index in words[target]:
            generator = algebra.generators[generator_index]
            algebra.admit_paid(projector, generator)
            operator = algebra.paid(projector, generator, operator)
            calls += 1
            if check_prefixes:
                require(algebra.crossing_rank(algebra.represented(operator)) <= calls,
                        "prefix cut exceeds paid calls")
    operator = algebra.scalar(undo, operator)
    equal_boundary(operator, algebra.endpoint(targets, roles))
    return calls


def verify():
    census, bfs, total_vertices, total_edges = [], {}, 0, 0
    for size in range(2, 8):
        distances, words, edges = cayley_bfs(size)
        bfs[size] = (distances, words)
        for value, distance in distances.items():
            crossing = permutation_crossing_rows(value)
            require(rank(crossing) == distance, "BFS distance differs from cut rank")
            require(sum(row.bit_count() for row in crossing) == distance,
                    "BFS distance differs from inversion crossings")
        total_vertices += len(distances)
        total_edges += edges
        census.append({"n": size, "permutations": len(distances), "edges": edges,
                       "diameter": max(distances.values())})

    gate_checks = 0
    for size in range(2, 6):
        algebra = GroupAlgebra(size)
        for roles in range(1, 4):
            for coefficient in rank_one_idempotents(roles):
                for generator in algebra.generators:
                    algebra.admit_paid(coefficient, generator)
                    formal = algebra.paid(coefficient, generator, algebra.endpoint([], roles))
                    equal_boundary(algebra.paid(coefficient, generator, formal),
                                   algebra.endpoint([], roles))
                    represented = algebra.represented(formal)
                    require(algebra.crossing_rank(represented) == 1, "paid gate cut rank")
                    require(multiply(represented, represented) == identity(len(represented)),
                            "paid gate involution")
                    gate_checks += 1

    algebra = GroupAlgebra(4)
    scalar_checks, conjugacy_checks = 0, 0
    for roles in range(1, 4):
        projector = (1,) + (0,) * (roles - 1)
        conjugates = set()
        for scalar in general_linear(roles):
            formal = algebra.scalar(scalar, algebra.endpoint([], roles))
            algebra.admit_scalar(formal)
            require(algebra.crossing_rank(algebra.represented(formal)) == 0,
                    "free scalar cut rank")
            conjugates.add(multiply(multiply(scalar, projector), inverse(scalar)))
            scalar_checks += 1
        require(conjugates == set(rank_one_idempotents(roles)),
                "conjugacy misses a rank-one idempotent")
        conjugacy_checks += len(conjugates)

    scalar = (3, 6, 7)
    distances, words = bfs[4]
    endpoint_checks = 0
    for left, right in product(algebra.elements, repeat=2):
        calls = conjugated_run(algebra, words, (left, right), scalar)
        require(calls == distances[left] + distances[right], "incorrect attaining cost")
        endpoint_checks += 1
    fixed_targets = ((3, 2, 1, 0), (1, 2, 3, 0))
    prefix_circuit_checks = 0
    for scalar in general_linear(3):
        calls = conjugated_run(algebra, words, fixed_targets, scalar, check_prefixes=True)
        require(calls == 9, "fixed target attaining cost")
        endpoint_checks += 1
        prefix_circuit_checks += 1

    rejected = []
    nonadjacent = (2, 1, 0, 3)
    coefficient = (1, 0, 0)
    rejected.append(must_reject(lambda: algebra.admit_paid(coefficient, nonadjacent),
                                "unit-cost nonadjacent transposition",
                                "paid address must be adjacent"))
    require(rank(permutation_crossing_rows(nonadjacent)) == 3,
            "nonadjacent countermodel should cross three pairs")
    rejected.append(must_reject(lambda: algebra.admit_paid(identity(3), algebra.generators[0]),
                                "unit-cost higher-rank coefficient",
                                "paid scalar coefficient must have rank one"))
    high_rank = algebra.paid(identity(3), algebra.generators[0], algebra.endpoint([], 3))
    require(algebra.crossing_rank(algebra.represented(high_rank)) == 3,
            "higher-rank countermodel should cross three pairs")

    free_address = algebra.endpoint((algebra.generators[0],) * 3, 3)
    rejected.append(must_reject(lambda: algebra.admit_scalar(free_address),
                                "free address-changing map",
                                "free scalar cannot change the address"))
    require(algebra.crossing_rank(algebra.represented(free_address)) == 3,
            "free address countermodel should have positive cut rank")

    expected = algebra.endpoint(fixed_targets, 3)
    unreturned = algebra.endpoint(fixed_targets + (algebra.generators[0],), 3)
    require(unreturned[:2] == expected[:2], "visible-row-only check should miss restoration")
    rejected.append(must_reject(lambda: equal_boundary(unreturned, expected),
                                "spectator not restored", "complete formal dirty boundary differs"))
    contaminated = [row[:] for row in expected]
    contaminated[0][2] ^= algebra.unit
    require([row[:2] for row in contaminated] == [row[:2] for row in expected],
            "clean-spectator input check should miss contamination")
    rejected.append(must_reject(lambda: equal_boundary(contaminated, expected),
                                "dirty spectator leaks into target", "complete formal dirty boundary differs"))

    norm = (1 << len(algebra.elements)) - 1
    hidden = [row[:] for row in expected]
    hidden[0][2] ^= norm
    require(hidden != expected and norm.bit_count() == 24, "formal kernel witness nonzero")
    require(algebra.represented(hidden) == algebra.represented(expected),
            "S4 group norm should vanish in ordered-pair action")
    rejected.append(must_reject(lambda: equal_boundary(hidden, expected),
                                "representation equality substituted for formal equality",
                                "complete formal dirty boundary differs"))

    return {
        "status": "PASS_SYMMETRIC_ADJACENT_INDEPENDENT",
        "scope": "finite evidence for the written theorem; no new kappa; not a formal-kernel proof",
        "cayley_bfs": census,
        "permutation_vertices": total_vertices,
        "directed_adjacent_edges": total_edges,
        "paid_full_matrix_checks_n2_through5_R1_through3": gate_checks,
        "free_GL_scalar_matrices_R1_through3": scalar_checks,
        "distinct_rank_one_idempotent_conjugates_R1_through3": conjugacy_checks,
        "formal_S4_endpoints_R3_with_one_dirty_spectator": endpoint_checks,
        "all_GL3_gauges_with_full_prefix_cut_checks": prefix_circuit_checks,
        "negative_controls": rejected,
        "representation_kernel_witness": "nonzero sum of all 24 S4 basis elements; ordered-pair image zero",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
