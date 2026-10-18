#!/usr/bin/env python3
"""Independent exact replay; no imports from the primary or predecessor code.

Uses lattice coordinates and an eight-dimensional quadratic form to exclude
nine pairwise-odd roots, instead of enumerating nonorthogonality cliques.
Standard library only; all proof checks remain active under python -O.
Prepared with substantial OpenAI Codex assistance. Apache-2.0.
"""

import argparse
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(left, right):
    return sum(x * y for x, y in zip(left, right))


def dense_basis(rows, width):
    """RREF using explicit binary coordinate lists (no bitset elimination)."""
    rows = [list(row) for row in rows]
    pivot = 0
    for column in range(width):
        selected = next((i for i in range(pivot, len(rows)) if rows[i][column]), None)
        if selected is None:
            continue
        rows[pivot], rows[selected] = rows[selected], rows[pivot]
        for i in range(len(rows)):
            if i != pivot and rows[i][column]:
                rows[i] = [x ^ y for x, y in zip(rows[i], rows[pivot])]
        pivot += 1
        if pivot == len(rows):
            break
    return rows[:pivot]


def inverse(matrix):
    size = len(matrix)
    rows = [[Fraction(x) for x in row] + [Fraction(i == j) for j in range(size)]
            for i, row in enumerate(matrix)]
    determinant = Fraction(1)
    for column in range(size):
        selected = next((i for i in range(column, size) if rows[i][column]), None)
        require(selected is not None, "singular lattice basis")
        if selected != column:
            rows[column], rows[selected] = rows[selected], rows[column]
            determinant = -determinant
        value = rows[column][column]
        determinant *= value
        rows[column] = [x / value for x in rows[column]]
        for i in range(size):
            if i != column:
                value = rows[i][column]
                rows[i] = [x - value * y for x, y in zip(rows[i], rows[column])]
    return [row[size:] for row in rows], determinant


def make_model():
    roots = set()
    for i, j in combinations(range(8), 2):
        for signs in product((-2, 2), repeat=2):
            vector = [0] * 8
            vector[i], vector[j] = signs
            roots.add(tuple(vector))
    roots.update(signs for signs in product((-1, 1), repeat=8) if sum(x < 0 for x in signs) % 2 == 0)
    # The sign and sorted order are deliberately independent of PR717's order.
    lines = sorted({min(root, tuple(-x for x in root)) for root in roots})
    require(len(roots) == 240 and len(lines) == 120, "E8 root enumeration")
    inner = [[dot(left, right) // 4 for right in lines] for left in lines]
    require(all(dot(left, right) % 4 == 0 for left in lines for right in lines), "integral inner products")
    require(all(inner[i][i] == 2 for i in range(120)), "root norms")
    puncture = []
    for i in range(0, 8, 2):
        for sign in (-2, 2):
            vector = [0] * 8
            vector[i], vector[i + 1] = -2, sign
            puncture.append(lines.index(tuple(vector)))
    puncture.sort()
    live = sorted(set(range(120)) - set(puncture))
    require(all(inner[i][j] == 0 for i, j in combinations(puncture, 2)), "punctured frame")
    return lines, inner, puncture, live


def quadratic_coordinates(lines, inner):
    simple = [
        [1, -1, -1, -1, -1, -1, -1, 1],
        [2, 2, 0, 0, 0, 0, 0, 0],
        [-2, 2, 0, 0, 0, 0, 0, 0],
    ]
    for i in range(1, 6):
        root = [0] * 8
        root[i], root[i + 1] = -2, 2
        simple.append(root)
    # Root vectors are columns in this lattice basis.
    inverse_basis, determinant = inverse([list(column) for column in zip(*simple)])
    require(abs(determinant) == 256, "doubled lattice determinant")
    gram = [[dot(a, b) // 4 for b in simple] for a in simple]
    _, gram_determinant = inverse(gram)
    require(gram_determinant == 1, "unimodular Gram matrix")
    reduced = [[value % 2 for value in row] for row in gram]
    require(len(dense_basis(reduced, 8)) == 8, "nondegenerate mod-two form")
    coordinates = []
    for root in lines:
        vector = [dot(row, root) for row in inverse_basis]
        require(all(x.denominator == 1 for x in vector), "root outside integral lattice")
        require([sum(int(vector[j]) * simple[j][i] for j in range(8)) for i in range(8)] == list(root),
                "coordinate reconstruction")
        coordinates.append([int(x) % 2 for x in vector])

    def bilinear(left, right):
        return sum(left[i] * reduced[i][j] * right[j] for i in range(8) for j in range(8)) % 2

    def quadratic(vector):
        return (sum(vector) + sum(gram[i][j] * vector[i] * vector[j]
                                  for i, j in combinations(range(8), 2))) % 2

    require(len({tuple(row) for row in coordinates}) == 120, "distinct root residues")
    require(all(quadratic(row) == 1 for row in coordinates), "root quadratic values")
    require(all(bilinear(coordinates[i], coordinates[j]) == inner[i][j] % 2
                for i in range(120) for j in range(120)), "polar form versus root inner products")
    vectors = list(product((0, 1), repeat=8))
    require(sum(quadratic(vector) for vector in vectors) == 120, "nonsingular quadratic vectors")
    # Exhaustive polarization check is inexpensive and independent of root pairs.
    require(all(quadratic([a ^ b for a, b in zip(left, right)]) ==
                quadratic(left) ^ quadratic(right) ^ bilinear(left, right)
                for left in vectors for right in vectors), "quadratic polarization")
    nine_gram = [[int(i != j) for j in range(9)] for i in range(9)]
    require(len(dense_basis(nine_gram, 9)) == 8, "nine-clique polar Gram rank")
    require(all(sum(row) % 2 == 0 for row in nine_gram), "nine-clique all-ones kernel")
    require((9 + 9 * 8 // 2) % 2 == 1 and quadratic([0] * 8) == 0,
            "nine-clique quadratic contradiction")
    labels = [row + [1] for row in coordinates]
    label_form = [row + [0] for row in reduced] + [[0] * 8 + [1]]
    return labels, label_form, {
        "simple_roots_doubled": simple,
        "gram_matrix": gram,
        "gram_determinant": int(gram_determinant),
        "polar_rank": 8,
        "root_residues": 120,
        "quadratic_one_vectors": 120,
        "polarization_pairs": 65536,
        "hypothetical_nine_clique_gram_rank": 8,
        "hypothetical_sum_quadratic_value": 1,
        "zero_quadratic_value": 0,
    }


def frames_and_extension(inner, live):
    orthogonal = {i: {j for j in live if i != j and inner[i][j] == 0} for i in live}
    frames = []

    def extend(prefix, candidates):
        if len(prefix) == 8:
            frames.append(tuple(prefix))
            return
        if len(prefix) + len(candidates) < 8:
            return
        remaining = set(candidates)
        for chosen in sorted(candidates):
            remaining.remove(chosen)
            extend(prefix + [chosen], remaining.intersection(orthogonal[chosen]))

    extend([], set(live))
    require(len(frames) == 1260 and len(set(frames)) == 1260, "live frame enumeration")
    pair_counts = Counter(pair for frame in frames for pair in combinations(frame, 2))
    orthogonal_pairs = {pair for pair in combinations(live, 2) if inner[pair[0]][pair[1]] == 0}
    require(set(pair_counts) == orthogonal_pairs, "every live orthogonal pair extends to a frame")
    occurrence = Counter(point for frame in frames for point in frame)
    require(set(occurrence) == set(live) and set(occurrence.values()) == {90}, "frame incidence")
    return frames, pair_counts


def pair_cost(left_basis, right_basis, form):
    transformed = [[sum(row[i] * form[i][j] for i in range(9)) % 2 for j in range(9)]
                   for row in left_basis]
    restricted = [[dot(row, column) % 2 for column in right_basis] for row in transformed]
    return len(dense_basis(restricted, len(right_basis)))


def run():
    lines, inner, puncture, live = make_model()
    labels, form, quadratic_receipt = quadratic_coordinates(lines, inner)
    require(all(sum(labels[i][a] * form[a][b] * labels[j][b]
                    for a in range(9) for b in range(9)) % 2 == (inner[i][j] + 1) % 2
                for i in range(120) for j in range(120)), "nine-dimensional label pairing")
    frames, pair_counts = frames_and_extension(inner, live)
    supports = []
    for normal in range(120):
        for trimmed in (False, True):
            support = {i for i in live if inner[i][normal] != 0 and (not trimmed or i != normal)}
            basis = dense_basis([labels[i] for i in sorted(support)], 9)
            self_removed = trimmed or normal in puncture
            require(len(basis) == (8 if self_removed else 9), "star support dimension")
            if self_removed:
                require(all((inner[i][normal] + 1) % 2 == 0 for i in support), "trimmed support hyperplane")
            missed = {k for k, frame in enumerate(frames) if not support.intersection(frame)}
            expected = {k for k, frame in enumerate(frames) if trimmed and normal in frame}
            require(missed == expected, "trimmed-star missed-frame characterization")
            supports.append((normal, trimmed, self_removed, support, basis, missed))
    costs = Counter()
    rank_seven_miss_sizes = Counter()
    for left in supports:
        for right in supports:
            normal_a, _, removed_a, _, basis_a, missed_a = left
            normal_b, _, removed_b, _, basis_b, missed_b = right
            actual = pair_cost(basis_a, basis_b, form)
            expected = (7 if inner[normal_a][normal_b] % 2 else 8) if removed_a and removed_b else (
                8 if removed_a or removed_b else 9)
            require(actual == expected, "ordered support-pair rank classification")
            costs[actual] += 1
            if actual == 7:
                require(normal_a in live or normal_b in live, "rank-seven live endpoint")
                require(len(missed_a | missed_b) in (90, 180), "rank-seven missed frames")
                rank_seven_miss_sizes[len(missed_a | missed_b)] += 1
    require(dict(costs) == {7: 7616, 8: 37440, 9: 12544}, "support-pair histogram")
    require(all((inner[i][j] + 1) % 2 == 1 for frame in frames for i in frame for j in frame),
            "zero-cost terms vanish on every frame block")
    # A separate exact construction establishes sharpness, not merely a bound.
    decoder = [[inner[i][normal] for normal in puncture] for i in live]
    target = [[2 * inner[i][j] for j in live] for i in live]
    require(all(dot(decoder[i], decoder[j]) == target[i][j]
                for i in range(112) for j in range(112)), "coordinate decoder identity")
    coordinate_costs = []
    for normal in puncture:
        support = [labels[i] for i in live if inner[i][normal]]
        basis = dense_basis(support, 9)
        coordinate_costs.append(pair_cost(basis, basis, form))
    require(coordinate_costs == [8] * 8, "coordinate decoder cost 64")

    controls = []
    changed = [row[:] for row in decoder]
    changed[0][0] += 1
    require(any(dot(changed[i], decoder[j]) != target[i][j]
                for i in range(112) for j in range(112)), "mutated decoder was accepted")
    controls.append("changed coordinate coefficient breaks exactness")
    chosen_pair = next(iter(pair_counts))
    remaining = [frame for frame in frames if not set(chosen_pair).issubset(frame)]
    observed = {pair for frame in remaining for pair in combinations(frame, 2)}
    require(chosen_pair not in observed, "missing extension fixture was accepted")
    controls.append("deleting all witnesses breaks orthogonal-pair coverage")
    singleton = {live[0]}
    require(all(singleton != entry[3] for entry in supports), "singleton unexpectedly a star support")
    singleton_basis = dense_basis([labels[live[0]]], 9)
    require(pair_cost(singleton_basis, singleton_basis, form) == 1, "singleton scope control")
    controls.append("arbitrary deeper trimming admits cost-one terms outside the theorem")
    # Nine pairwise-one vectors DO exist if q=1 is omitted: the eight basis
    # vectors and their sum for the nondegenerate alternating form J+I.
    alternative_form = [[int(i != j) for j in range(8)] for i in range(8)]
    alternative_vectors = [[int(i == j) for j in range(8)] for i in range(8)] + [[1] * 8]
    require(all(sum(left[i] * alternative_form[i][j] * right[j] for i in range(8) for j in range(8)) % 2 == 1
                for left, right in combinations(alternative_vectors, 2)), "polar-only nine-clique control")
    require((8 + 28) % 2 == 0, "ninth vector quadratic value control")
    controls.append("bilinear dimension alone permits nine vectors; quadratic condition is essential")
    wrong_form = [row[:] for row in form]
    wrong_form[8][8] = 0
    require(pair_cost(singleton_basis, singleton_basis, wrong_form) == 0,
            "omitted affine label coordinate control")
    controls.append("dropping affine label coordinate falsely makes a diagonal singleton free")

    return {
        "schema": "masked-root-star-assembly-independent-v1",
        "method": "dense binary elimination, integral lattice coordinates, quadratic obstruction",
        "root_lines": len(lines),
        "punctured_root_vectors_doubled": [lines[i] for i in puncture],
        "live_lines": len(live),
        "quadratic_certificate": quadratic_receipt,
        "frames": len(frames),
        "orthogonal_pair_count": len(pair_counts),
        "orthogonal_pair_frame_multiplicities": dict(sorted(Counter(pair_counts.values()).items())),
        "support_count": len(supports),
        "ordered_support_pair_rank_histogram": dict(sorted(costs.items())),
        "rank_seven_missed_frame_histogram": dict(sorted(rank_seven_miss_sizes.items())),
        "coordinate_identity_entries": 112 * 112,
        "coordinate_costs": coordinate_costs,
        "lower_bound": 64,
        "controls": controls,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate this checker's own receipt")
    args = parser.parse_args()
    result = run()
    path = Path(__file__).with_name("INDEPENDENT.json")
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        path.write_text(encoded, encoding="utf-8")
    else:
        require(json.loads(path.read_text(encoding="utf-8")) == json.loads(encoded), "independent receipt mismatch")
    print("PASS_MASKED_ROOT_STAR_INDEPENDENT frames=1260 pairs=57600 quadratic_dimension=8 floor=64 controls=5")


if __name__ == "__main__":
    main()
