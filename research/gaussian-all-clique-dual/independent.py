#!/usr/bin/env python3
"""Independent finite replay of the Gaussian E8 all-clique dual.

Only Python's standard library is used. No primary or predecessor executable
code is imported. Geometry is reconstructed from the doubled real E8 roots;
Gaussian ranks are checked by direct Gaussian-rational Fraction elimination.
All nonempty cliques are obtained as deduplicated subsets of Bron--Kerbosch
maximal cliques, rather than by the primary replay's ordered clique recursion.

Prepared for William Lawyer with substantial OpenAI Codex assistance. Separate
AI implementation is not independent human review or a formal proof assistant.
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import struct
import time


Gaussian = tuple[int, int]
Vector = tuple[Gaussian, ...]


def require(condition: bool, message: str) -> None:
    # Deliberately not an assert: optimized Python must retain failure detection.
    if not condition:
        raise ValueError(message)


def e8_root_valid(root: tuple[int, ...]) -> bool:
    """Membership in the *doubled* E8 root system, not just its norm shell."""
    if len(root) != 8:
        return False
    if all(x in (-1, 1) for x in root):
        return sum(x < 0 for x in root) % 2 == 0
    return (sum(x != 0 for x in root) == 2
            and all(x in (-2, 0, 2) for x in root))


def doubled_roots() -> set[tuple[int, ...]]:
    roots: set[tuple[int, ...]] = set()
    for support in combinations(range(8), 2):
        for signs in product((-2, 2), repeat=2):
            row = [0] * 8
            for position, value in zip(support, signs):
                row[position] = value
            roots.add(tuple(row))
    for row in product((-1, 1), repeat=8):
        if sum(x == -1 for x in row) % 2 == 0:
            roots.add(row)
    require(len(roots) == 240, "Doubled E8 root count changed")
    require(all(e8_root_valid(row) for row in roots), "Invalid E8 root")
    return roots


def rotate_i(root: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(value for j in range(0, 8, 2)
                 for value in (-root[j + 1], root[j]))


def line_representative(root: tuple[int, ...]) -> tuple[int, ...]:
    phase_i = rotate_i(root)
    return min(root, phase_i, tuple(-x for x in root),
               tuple(-x for x in phase_i))


def hermitian(left: Vector, right: Vector) -> Gaussian:
    require(len(left) == len(right), "Mismatched vector lengths")
    # conj(a+ib)(c+id) = ac+bd + i(ad-bc).
    return (sum(a * c + b * d for (a, b), (c, d) in zip(left, right)),
            sum(a * d - b * c for (a, b), (c, d) in zip(left, right)))


def indices(mask: int):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def gaussian_rank(matrix: list[list[Gaussian]]) -> int:
    """Exact rank over Q(i), using direct pairs of rational components.

    This does not realify the matrix or use the primary replay's real RREF.
    Every elimination quotient is evaluated in the Gaussian rational field.
    """
    if not matrix:
        return 0
    width = len(matrix[0])
    require(all(len(row) == width for row in matrix), "Ragged Gaussian matrix")
    rows = [[(Fraction(real), Fraction(imaginary)) for real, imaginary in row]
            for row in matrix]
    pivot_row = 0
    for column in range(width):
        pivot = next((j for j in range(pivot_row, len(rows))
                      if rows[j][column] != (0, 0)), None)
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        row = rows[pivot_row]
        for j in range(pivot_row + 1, len(rows)):
            if rows[j][column] != (0, 0):
                a, b = rows[j][column]
                c, d = row[column]
                denominator = c * c + d * d
                factor = ((a * c + b * d) / denominator,
                          (b * c - a * d) / denominator)
                rows[j][column] = (Fraction(0), Fraction(0))
                f, g = factor
                for k in range(column + 1, width):
                    c, d = row[k]
                    a, b = rows[j][k]
                    rows[j][k] = (a - (f * c - g * d),
                                  b - (f * d + g * c))
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return pivot_row


def build_geometry() -> tuple[list[Vector], list[int], list[int]]:
    roots = doubled_roots()
    representatives = sorted({line_representative(row) for row in roots})
    require(len(representatives) == 60, "Gaussian line count changed")
    for row in representatives:
        orbit = {row, rotate_i(row), tuple(-x for x in row),
                 tuple(-x for x in rotate_i(row))}
        require(len(orbit) == 4 and orbit <= roots,
                "Gaussian phase orbit does not consist of four E8 roots")
    lines = [tuple((row[j], row[j + 1]) for j in range(0, 8, 2))
             for row in representatives]
    perpendiculars = [sum(1 << j for j, right in enumerate(lines)
                          if hermitian(left, right) == (0, 0))
                      for left in lines]
    universe = (1 << len(lines)) - 1
    nonorthogonal = [universe ^ perpendiculars[i] ^ (1 << i)
                     for i in range(len(lines))]
    verify_geometry(lines, perpendiculars, nonorthogonal)
    return lines, perpendiculars, nonorthogonal


def verify_geometry(lines: list[Vector], perpendiculars: list[int],
                    nonorthogonal: list[int]) -> None:
    require(len(lines) == len(perpendiculars) == len(nonorthogonal) == 60,
            "Geometry arrays must contain 60 lines")
    universe = (1 << 60) - 1
    for i, left in enumerate(lines):
        require(hermitian(left, left) == (8, 0), "Invalid root norm")
        require(perpendiculars[i].bit_count() == 15,
                "Hyperplane does not contain 15 line indices")
        require(perpendiculars[i] & (1 << i) == 0, "Self orthogonality")
        require(nonorthogonal[i] == universe ^ perpendiculars[i] ^ (1 << i),
                "Nonorthogonality graph complement is incorrect")
        for j, right in enumerate(lines):
            if i < j:
                real, imaginary = hermitian(left, right)
                require(64 - real * real - imaginary * imaginary > 0,
                        "Two representatives are the same Gaussian line")
            expected = hermitian(left, right) == (0, 0)
            require(bool(perpendiculars[i] & (1 << j)) == expected,
                    "Orthogonality edge does not match exact Hermitian form")
            require(bool(perpendiculars[j] & (1 << i)) == expected,
                    "Orthogonality graph is not symmetric")


def ordered_dual_pairs(perpendiculars: list[int]) -> list[tuple[int, int]]:
    return [(i, j) for i, neighbors in enumerate(perpendiculars)
            for j in indices(neighbors)
            if (neighbors & perpendiculars[j]).bit_count() == 6]


def geometry_ranks(lines: list[Vector], perpendiculars: list[int],
                   dual_pairs: list[tuple[int, int]]) -> dict[str, int]:
    spans = [list(indices(mask)) for mask in perpendiculars]
    source_rank = Counter(gaussian_rank([list(lines[i]) for i in support])
                          for support in spans)
    require(source_rank == {3: 60}, "Hyperplane source span is not dimension3")
    pairing_rank = Counter()
    for first, second in dual_pairs:
        gram = [[hermitian(lines[i], lines[j]) for j in spans[second]]
                for i in spans[first]]
        pairing_rank[gaussian_rank(gram)] += 1
    require(pairing_rank == {2: 180}, "Selected hyperplane pairing rank changed")
    return {"source_spans_rank3": source_rank[3],
            "ordered_gram_blocks_rank2": pairing_rank[2]}


def maximal_cliques(adjacency: list[int]) -> list[int]:
    """Bron--Kerbosch pivot recursion; every returned clique is maximal."""
    found: list[int] = []

    def visit(chosen: int, possible: int, excluded: int) -> None:
        if not possible and not excluded:
            found.append(chosen)
            return
        candidates = possible | excluded
        pivot = max(indices(candidates),
                    key=lambda i: (possible & adjacency[i]).bit_count())
        branch = possible & ~adjacency[pivot]
        while branch:
            bit = branch & -branch
            vertex = bit.bit_length() - 1
            visit(chosen | bit, possible & adjacency[vertex],
                  excluded & adjacency[vertex])
            possible ^= bit
            excluded |= bit
            branch ^= bit

    visit(0, (1 << len(adjacency)) - 1, 0)
    require(len(found) == len(set(found)), "Duplicate maximal cliques")
    for mask in found:
        require(is_clique(mask, adjacency), "Malformed maximal clique")
        common = (1 << len(adjacency)) - 1
        for i in indices(mask):
            common &= adjacency[i]
        require(common == 0, "Returned clique is extendible")
    return sorted(found)


def is_clique(mask: int, adjacency: list[int]) -> bool:
    if mask < 0 or mask >> len(adjacency):
        return False
    for i in indices(mask):
        if (mask ^ (1 << i)) & ~adjacency[i]:
            return False
    return True


def all_cliques(maximals: list[int]) -> set[int]:
    """A finite graph clique extends to a maximal one: enumerate all subsets."""
    result: set[int] = set()
    for mask in maximals:
        subset = mask
        while subset:
            result.add(subset)
            subset = (subset - 1) & mask
    return result


def dual_incidence(perpendiculars: list[int],
                   pairs: list[tuple[int, int]]) -> tuple[list[int], list[int]]:
    first = [0] * len(perpendiculars)
    second = [0] * len(perpendiculars)
    for index, (u, v) in enumerate(pairs):
        for i in indices(perpendiculars[u]):
            first[i] |= 1 << index
        for i in indices(perpendiculars[v]):
            second[i] |= 1 << index
    return first, second


def hit_count(mask: int, incidence: tuple[list[int], list[int]]) -> int:
    left = right = 0
    first, second = incidence
    for i in indices(mask):
        left |= first[i]
        right |= second[i]
    return (left & right).bit_count()


def expected_failure(action, message: str) -> None:
    try:
        action()
    except ValueError:
        return
    raise ValueError("Negative control was accepted: " + message)


def small_graph_domain_controls() -> int:
    """Compare BK/subsets with brute force for all labelled graphs of order1..5."""
    checked = 0
    for order in range(1, 6):
        edges = list(combinations(range(order), 2))
        for edge_mask in range(1 << len(edges)):
            adjacency = [0] * order
            for position, (i, j) in enumerate(edges):
                if edge_mask & (1 << position):
                    adjacency[i] |= 1 << j
                    adjacency[j] |= 1 << i
            brute_force = {mask for mask in range(1, 1 << order)
                           if is_clique(mask, adjacency)}
            reconstructed = all_cliques(maximal_cliques(adjacency))
            require(reconstructed == brute_force,
                    f"Small graph domain mismatch: n={order}, edges={edge_mask}")
            checked += 1
    return checked


def controls(lines: list[Vector], perpendiculars: list[int],
             adjacency: list[int], pairs: list[tuple[int, int]],
             maximum_clique: int) -> dict[str, object]:
    require(hermitian(((1, 0), (0, 1)), ((0, 1), (1, 0))) == (0, 0),
            "Hermitian conjugation control failed")
    require(hermitian(((1, 0),), ((0, 1),)) == (0, 1),
            "Hermitian imaginary-sign control failed")
    require(gaussian_rank([[(1, 0), (0, 1)], [(0, 1), (-1, 0)]]) == 1,
            "Gaussian-dependent rank control failed")
    require(gaussian_rank([[(1, 0), (0, 1)], [(0, 1), (1, 0)]]) == 2,
            "Gaussian-independent rank control failed")
    root = (1,) * 8
    corrupt_root = (-1,) + root[1:]
    require(e8_root_valid(root) and not e8_root_valid(corrupt_root),
            "Odd root-sign corruption was not rejected")
    orthogonal = (0, next(indices(perpendiculars[0])))
    require(not is_clique((1 << orthogonal[0]) | (1 << orthogonal[1]),
                          adjacency), "Orthogonal pair admitted as clique")
    bad_perps = perpendiculars.copy()
    bad_perps[0] ^= 1 << orthogonal[1]
    expected_failure(lambda: verify_geometry(lines, bad_perps, adjacency),
                     "deleted orthogonality edge")
    original = [(i, j) for i, mask in enumerate(perpendiculars)
                for j in indices(mask)]
    old_singleton_hits = hit_count(1, dual_incidence(perpendiculars, original))
    require(old_singleton_hits == 42 and old_singleton_hits < 45,
            "Original 900-pair singleton counterexample disappeared")
    hits = hit_count(maximum_clique, dual_incidence(perpendiculars, pairs))
    require(hits < 10 * maximum_clique.bit_count(),
            "Stronger multiplier 1/10 negative control did not fail")
    # Removing a contributing pair invalidates a tight size12 dual inequality.
    contributing = next(k for k, (u, v) in enumerate(pairs)
                        if maximum_clique & perpendiculars[u]
                        and maximum_clique & perpendiculars[v])
    reduced = pairs[:contributing] + pairs[contributing + 1:]
    reduced_hits = hit_count(maximum_clique,
                            dual_incidence(perpendiculars, reduced))
    require(hits == 9 * maximum_clique.bit_count()
            and reduced_hits < 9 * maximum_clique.bit_count(),
            "Dropped-dual-pair negative control did not fail")
    return {"orthogonal_pair_rejected": list(orthogonal),
            "deleted_edge_rejected": True,
            "odd_root_sign_rejected": True,
            "hermitian_sign_controls": 2,
            "gaussian_rank_controls": 2,
            "all_labelled_graphs_order1_through5": small_graph_domain_controls(),
            "original900_singleton_hits": old_singleton_hits,
            "original900_required_singleton_hits": 45,
            "multiplier1_over10_rejected": True,
            "dropped_dual_pair_rejected": True,
            "dropped_pair_hits": reduced_hits}


MATHEMATICAL_FIELDS = ("line_count", "orthogonal_ordered_pair_count",
                       "dual_pair_count", "clique_counts", "minimum_dual_hits",
                       "all_cliques_sha256", "dual_pairs", "dual_multiplier", "ceiling")


def compare_certificate(result: dict, certificate: dict) -> None:
    for field in MATHEMATICAL_FIELDS:
        require(field in certificate, "Missing certificate field: " + field)
        require(certificate[field] == result[field],
                "Independent certificate mismatch: " + field)


def replay() -> dict:
    lines, perpendiculars, adjacency = build_geometry()
    pairs = ordered_dual_pairs(perpendiculars)
    require(len(pairs) == 180, "Selected dual is not 180 ordered pairs")
    ranks = geometry_ranks(lines, perpendiculars, pairs)
    maximals = maximal_cliques(adjacency)
    cliques = all_cliques(maximals)
    incidence = dual_incidence(perpendiculars, pairs)
    counts: Counter[int] = Counter()
    minima: dict[int, int] = {}
    digest = hashlib.sha256()
    for mask in sorted(cliques):
        size = mask.bit_count()
        hits = hit_count(mask, incidence)
        require(hits >= 9 * size,
                f"All-clique dual fails: mask={mask}, size={size}, hits={hits}")
        counts[size] += 1
        minima[size] = min(minima.get(size, len(pairs) + 1), hits)
        digest.update(struct.pack("<Q", mask))
    require(max(counts) == 12, "Maximum clique size changed")
    maximum_clique = next(mask for mask in maximals if mask.bit_count() == 12)
    report = {"line_count": len(lines),
              "orthogonal_ordered_pair_count": sum(mask.bit_count()
                                                     for mask in perpendiculars),
              "dual_pair_count": len(pairs),
              "dual_multiplier": "1/9", "ceiling": "40",
              "dual_pairs": [list(pair) for pair in pairs],
              "clique_counts": {str(k): counts[k] for k in sorted(counts)},
              "minimum_dual_hits": {str(k): minima[k] for k in sorted(minima)},
              "all_cliques_sha256": digest.hexdigest(),
              "nonempty_cliques": len(cliques),
              "maximal_clique_counts": {str(k): v for k, v in sorted(
                  Counter(mask.bit_count() for mask in maximals).items())},
              "exact_rank_checks": ranks,
              "controls": controls(lines, perpendiculars, adjacency, pairs,
                                   maximum_clique)}
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path,
                        default=Path(__file__).with_name("CERTIFICATE.json"))
    parser.add_argument("--compute-only", action="store_true",
                        help="emit recomputed evidence without comparing a fixture")
    parser.add_argument("--show-report", action="store_true",
                        help="print the complete independent evidence")
    arguments = parser.parse_args()
    started = time.perf_counter()
    result = replay()
    if not arguments.compute_only:
        certificate = json.loads(arguments.certificate.read_text(encoding="utf-8"))
        compare_certificate(result, certificate)
        result["certificate_mathematical_fields_match"] = True
        # A replayed claim must reject changed published evidence.
        changed = dict(certificate)
        changed["all_cliques_sha256"] = "0" * 64
        expected_failure(lambda: compare_certificate(result, changed),
                         "corrupted clique-set digest")
        result["controls"]["corrupted_certificate_digest_rejected"] = True
    result["verification"] = "PASS"
    result["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    if arguments.show_report or arguments.compute_only:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("PASS_INDEPENDENT_GAUSSIAN_ALL_CLIQUE_DUAL cliques="
              + str(result["nonempty_cliques"])
              + " ordered_pairs=180 ceiling=40 graphs=1099 no_new_kappa")


if __name__ == "__main__":
    main()
