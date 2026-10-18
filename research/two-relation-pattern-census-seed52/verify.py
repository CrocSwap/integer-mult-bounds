#!/usr/bin/env python3
"""Exact four-register two-relation pattern census and fixed-word screen."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
NREG = 4
MATRIX_SIZE = NREG * NREG
EDGE_ORDER = tuple((i, j) for i in range(NREG) for j in range(NREG) if i != j)


def unit(i: int, j: int) -> tuple[int, ...]:
    return tuple(int((r, c) == (i, j)) for r in range(NREG) for c in range(NREG))


def vadd(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(x + y for x, y in zip(a, b))


def vsub(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(x - y for x, y in zip(a, b))


def matrix_rank_f2(rows: list[list[int]]) -> int:
    if not rows:
        return 0
    a = [row[:] for row in rows]
    m, n = len(a), len(a[0])
    pivot_row = 0
    for col in range(n):
        pivot = next((r for r in range(pivot_row, m) if a[r][col] & 1), None)
        if pivot is None:
            continue
        a[pivot_row], a[pivot] = a[pivot], a[pivot_row]
        for r in range(m):
            if r != pivot_row and (a[r][col] & 1):
                a[r] = [x ^ y for x, y in zip(a[r], a[pivot_row])]
        pivot_row += 1
        if pivot_row == m:
            break
    return pivot_row


def matrix_rank_q(rows: list[list[int]]) -> int:
    a = [[Fraction(x) for x in row] for row in rows]
    if not a:
        return 0
    m, n = len(a), len(a[0])
    pivot_row = 0
    for col in range(n):
        pivot = next((r for r in range(pivot_row, m) if a[r][col]), None)
        if pivot is None:
            continue
        a[pivot_row], a[pivot] = a[pivot], a[pivot_row]
        scale = a[pivot_row][col]
        a[pivot_row] = [x / scale for x in a[pivot_row]]
        for r in range(m):
            if r != pivot_row and a[r][col]:
                scale = a[r][col]
                a[r] = [x - scale * y for x, y in zip(a[r], a[pivot_row])]
        pivot_row += 1
        if pivot_row == m:
            break
    return pivot_row


def offdiag_pattern(x: int, y: int) -> int:
    bits = 0
    for bit, (i, j) in enumerate(EDGE_ORDER):
        if ((x >> i) & 1) and ((y >> j) & 1):
            bits |= 1 << bit
    return bits


def pattern_edges(pattern: int) -> tuple[tuple[int, int], ...]:
    return tuple(edge for bit, edge in enumerate(EDGE_ORDER) if (pattern >> bit) & 1)


def is_acyclic(patterns: tuple[int, ...] | list[int]) -> bool:
    adjacency = [set() for _ in range(NREG)]
    for pattern in patterns:
        for i, j in pattern_edges(pattern):
            adjacency[i].add(j)
    indegree = [0] * NREG
    for i in range(NREG):
        for j in adjacency[i]:
            indegree[j] += 1
    queue = [i for i, degree in enumerate(indegree) if degree == 0]
    seen = 0
    while queue:
        i = queue.pop()
        seen += 1
        for j in adjacency[i]:
            indegree[j] -= 1
            if indegree[j] == 0:
                queue.append(j)
    return seen == NREG


def enumerate_projectors() -> dict[int, list[tuple[int, int]]]:
    pools: dict[int, list[tuple[int, int]]] = {}
    for x in range(1, 1 << NREG):
        for y in range(1, 1 << NREG):
            if (x & y).bit_count() % 2 == 1:
                pools.setdefault(offdiag_pattern(x, y), []).append((x, y))
    return pools


def pattern_planes(pools: dict[int, list[tuple[int, int]]]) -> list[tuple[int, int, int]]:
    nonzero = sorted(p for p in pools if p)
    planes = set()
    for p, q in itertools.combinations(nonzero, 2):
        r = p ^ q
        if r in pools and r not in (p, q):
            planes.add(tuple(sorted((p, q, r))))
    return sorted(planes)


def independent_census() -> tuple[dict[int, list[tuple[int, int]]], set[tuple[int, int, int]],
                                 set[tuple[int, int, int]]]:
    """Second census: build matrices first and detect cycles by transitive closure."""
    groups: dict[int, list[tuple[int, int]]] = {}
    for x in range(1, 1 << NREG):
        for y in range(1, 1 << NREG):
            rows = tuple(sum((((x >> i) & 1) * ((y >> j) & 1)) << j
                             for j in range(NREG)) for i in range(NREG))
            if sum((rows[i] >> i) & 1 for i in range(NREG)) % 2 != 1:
                continue
            pattern = 0
            for bit, (i, j) in enumerate(EDGE_ORDER):
                pattern |= ((rows[i] >> j) & 1) << bit
            groups.setdefault(pattern, []).append((x, y))

    nonzero = sorted(pattern for pattern in groups if pattern)
    planes = set()
    for i, p in enumerate(nonzero):
        for q in nonzero[i + 1:]:
            r = p ^ q
            if r in groups and r not in (p, q):
                planes.add(tuple(sorted((p, q, r))))

    def has_cycle(plane: tuple[int, ...]) -> bool:
        reach = [[False] * NREG for _ in range(NREG)]
        for pattern in plane:
            for i, j in pattern_edges(pattern):
                reach[i][j] = True
        for k in range(NREG):
            for i in range(NREG):
                for j in range(NREG):
                    reach[i][j] = reach[i][j] or (reach[i][k] and reach[k][j])
        return any(reach[i][i] for i in range(NREG))

    exceptional = {plane for plane in planes if has_cycle(plane)}
    return groups, planes, exceptional


def mat_times_projector(rows: tuple[int, ...], xy: tuple[int, int]) -> tuple[int, ...]:
    x, y = xy
    return tuple(y if ((row & x).bit_count() & 1) else 0 for row in rows)


def add_coeff(poly: dict[tuple[int, ...], tuple[int, ...]],
              exponent: tuple[int, ...], coefficient: tuple[int, ...]) -> None:
    old = poly.get(exponent, (0,) * NREG)
    new = tuple(a ^ b for a, b in zip(old, coefficient))
    if any(new):
        poly[exponent] = new
    else:
        poly.pop(exponent, None)


def formal_product(word: list[tuple[tuple[int, ...], tuple[int, int]]]
                   ) -> dict[tuple[int, ...], tuple[int, ...]]:
    """Multiply I+([A]+1)N factors in F2[Q^(4x4)] exactly."""
    zero = (0,) * MATRIX_SIZE
    identity = tuple(1 << i for i in range(NREG))
    poly = {zero: identity}
    for address, projector in word:
        following: dict[tuple[int, ...], tuple[int, ...]] = {}
        for exponent, coefficient in poly.items():
            product_n = mat_times_projector(coefficient, projector)
            add_coeff(following, exponent,
                      tuple(a ^ b for a, b in zip(coefficient, product_n)))
            add_coeff(following, vadd(exponent, address), product_n)
        poly = following
    return poly


def expected_endpoint(targets: list[tuple[int, ...]]) -> dict[tuple[int, ...], tuple[int, ...]]:
    endpoint = {}
    for role, target in enumerate(targets):
        rows = tuple((1 << role) if row == role else 0 for row in range(NREG))
        endpoint[target] = rows
    return endpoint


def row_decomposition(target: tuple[int, ...], role: int
                     ) -> list[tuple[tuple[int, ...], tuple[int, int]]]:
    factors = []
    for row in range(NREG):
        source = tuple(target[row * NREG + col] for col in range(NREG))
        if any(source):
            frame = tuple((1 if r == row else 0) * source[c]
                          for r in range(NREG) for c in range(NREG))
            factors.append((frame, (1 << role, 1 << role)))
    return factors


def candidate_addresses() -> list[tuple[int, ...]]:
    e = unit
    return [
        e(0, 0), e(1, 1), vadd(e(0, 0), e(1, 0)), vsub(e(1, 1), e(1, 0)),
        e(2, 2), vadd(e(0, 0), e(2, 0)), vsub(e(2, 2), e(2, 0)),
        e(3, 3), e(0, 1), e(0, 2), e(0, 3), e(1, 2), e(1, 3), e(2, 1), e(2, 3),
    ]


def targets() -> list[tuple[int, ...]]:
    identity = tuple(int(i == j) for i in range(NREG) for j in range(NREG))
    return [identity] + [vadd(identity, unit(i - 1, i)) for i in range(1, 4)]


def first_seven_diagonal(poly: dict[tuple[int, ...], tuple[int, ...]]
                         ) -> tuple[tuple[int, ...], ...] | None:
    supports = [[] for _ in range(NREG)]
    for exponent, rows in poly.items():
        for i, row in enumerate(rows):
            if row & ~(1 << i):
                return None
            if row & (1 << i):
                supports[i].append(exponent)
    if any(len(support) != 1 for support in supports):
        return None
    return tuple(support[0] for support in supports)


def residual_diagonal_assignment(base: tuple[tuple[int, ...], ...],
                                 target: list[tuple[int, ...]],
                                 independent_frames: list[tuple[int, ...]]) -> tuple[int, ...] | None:
    """Solve all 4^8 coordinate-projector choices by their exact exponents."""
    deltas = [tuple(c - b for c, b in zip(t, old)) for t, old in zip(target, base)]
    unit_positions = {frame.index(1): idx for idx, frame in enumerate(independent_frames)}
    if len(unit_positions) != len(independent_frames):
        return None
    owners = [-1] * len(independent_frames)
    for role, delta in enumerate(deltas):
        for pos, coefficient in enumerate(delta):
            if pos not in unit_positions and coefficient != 0:
                return None
            if pos in unit_positions:
                if coefficient not in (0, 1):
                    return None
                idx = unit_positions[pos]
                if coefficient:
                    if owners[idx] != -1:
                        return None
                    owners[idx] = role
    if any(owner < 0 for owner in owners):
        return None
    return tuple(owners)


def exact_candidate_screen(pools: dict[int, list[tuple[int, int]]],
                           exceptional: list[tuple[int, int, int]],
                           addresses: list[tuple[int, ...]],
                           target: list[tuple[int, ...]]) -> dict:
    mappings = 0
    diagonal_singleton = 0
    residual_matches = 0
    witness = None
    for plane in exceptional:
        lifts = [pools[p][0] for p in plane]
        for relation_lifts in itertools.permutations(lifts):
            mappings += 1
            word = [
                (addresses[0], relation_lifts[0]),
                (addresses[1], relation_lifts[1]),
                (addresses[2], relation_lifts[1]),
                (addresses[3], relation_lifts[1]),
                (addresses[4], relation_lifts[2]),
                (addresses[5], relation_lifts[2]),
                (addresses[6], relation_lifts[2]),
            ]
            diagonal = first_seven_diagonal(formal_product(word))
            if diagonal is None:
                continue
            diagonal_singleton += 1
            assignment = residual_diagonal_assignment(diagonal, target, addresses[7:])
            if assignment is None:
                continue
            residual_matches += 1
            complete = word + [
                (address, (1 << owner, 1 << owner))
                for address, owner in zip(addresses[7:], assignment)
            ]
            if formal_product(complete) == expected_endpoint(target):
                witness = {
                    "plane": list(plane),
                    "relation_lifts_xy": [list(xy) for xy in relation_lifts],
                    "zero_pattern_role_assignment": list(assignment),
                }
                break
        if witness:
            break
    return {
        "exceptional_pattern_planes": len(exceptional),
        "signature_bijections_checked": mappings,
        "first_seven_diagonal_singleton_endpoints": diagonal_singleton,
        "residual_role_assignments": residual_matches,
        "construction_found": witness is not None,
        "witness": witness,
        "domain": "fixed ordered 15-address set; nontriangular two-plane pattern ansatz; all six signature bijections; the first-seven prefix test rules out all 4^8 trailing coordinate-projector choices",
    }


def build_certificate() -> dict:
    pools = enumerate_projectors()
    planes = pattern_planes(pools)
    independent_pools, independent_planes, independent_exceptional = independent_census()
    assert pools == independent_pools
    assert set(planes) == independent_planes
    cycle_counts = {}
    for plane in planes:
        cycles = sum(not is_acyclic([pattern]) for pattern in plane)
        cycle_counts[str(cycles)] = cycle_counts.get(str(cycles), 0) + 1
    exceptional = [plane for plane in planes if not is_acyclic(plane)]
    acyclic = [plane for plane in planes if is_acyclic(plane)]
    assert set(exceptional) == independent_exceptional
    assert len(EDGE_ORDER) == 12
    assert sum(len(group) for group in pools.values()) == 120
    assert len(pools) == 105 and len(pools.get(0, [])) == 4
    assert len(planes) == 196
    assert len(acyclic) == 176 and len(exceptional) == 20
    assert cycle_counts == {"0": 176, "1": 12, "2": 8}
    assert all(all(len(pools[p]) == 1 for p in plane) for plane in exceptional)

    addresses = candidate_addresses()
    target = targets()
    assert all(matrix_rank_q([list(address[i * NREG:(i + 1) * NREG])
                              for i in range(NREG)]) == 1 for address in addresses)
    assert vadd(addresses[0], addresses[1]) == vadd(addresses[2], addresses[3])
    assert vadd(addresses[0], addresses[4]) == vadd(addresses[5], addresses[6])
    address_rows = [[addresses[j][i] for j in range(len(addresses))]
                    for i in range(MATRIX_SIZE)]
    assert matrix_rank_q(address_rows) == 13
    address_span_dimension_f2 = matrix_rank_f2([[x & 1 for x in row] for row in address_rows])
    assert address_span_dimension_f2 == 13
    relation_vectors = [
        [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    ]
    assert all(sum(row[j] * relation[j] for j in range(len(addresses))) % 2 == 0
               for relation in relation_vectors for row in address_rows)
    assert matrix_rank_f2(relation_vectors) == 2
    assert [matrix_rank_q([list(t[i * NREG:(i + 1) * NREG]) for i in range(NREG)])
                          for t in target] == [4, 4, 4, 4]
    # Each target is in the integer span of the fixed address list.
    assert target[0] == vadd(vadd(addresses[0], addresses[1]),
                             vadd(addresses[4], addresses[7]))
    assert target[1] == vadd(target[0], addresses[8])
    assert target[2] == vadd(target[0], addresses[11])
    assert target[3] == vadd(target[0], addresses[14])

    baseline = []
    for role, matrix in enumerate(target):
        baseline.extend(row_decomposition(matrix, role))
    assert len(baseline) == 16
    expected = expected_endpoint(target)
    assert formal_product(baseline) == expected
    assert formal_product(baseline[:-1]) != expected
    corrupt = list(baseline)
    corrupt[-1] = (vadd(corrupt[-1][0], unit(0, 0)), corrupt[-1][1])
    assert formal_product(corrupt) != expected

    screen = exact_candidate_screen(pools, exceptional, addresses, target)
    return {
        "format": "four-register-two-relation-pattern-census-v1",
        "base_commit": "0b1cccf86e2f5132ed286a26ef0a681a495740ea",
        "assignment_seed": "52ca0472d6f3968cc45d208c3914ca12",
        "pattern_census": {
            "registers": 4,
            "rank_one_idempotents": 120,
            "distinct_offdiagonal_patterns_including_zero": 105,
            "acyclic_patterns": sum(1 for p in pools if is_acyclic([p])),
            "cyclic_patterns": sum(1 for p in pools if not is_acyclic([p])),
            "realizable_two_dimensional_pattern_planes": len(planes),
            "common_topological_order_planes": len(acyclic),
            "nontriangular_planes": len(exceptional),
            "nonzero_cyclic_pattern_count_per_plane": cycle_counts,
            "all_nontriangular_plane_fibers_singleton": True,
            "all_plane_patterns_sha256": value_sha256([list(p) for p in planes]),
            "common_order_plane_patterns_sha256": value_sha256([list(p) for p in acyclic]),
            "nontriangular_planes": [
                {"patterns": list(plane),
                 "unique_xy_lifts": [list(pools[p][0]) for p in plane]}
                for plane in exceptional
            ],
            "edge_encoding": "12 directed off-diagonal coordinates in lexicographic (row,column) order; bit 0 is the first edge",
        },
        "fixed_candidate": {
            "addresses": [list(a) for a in addresses],
            "targets": [list(t) for t in target],
            "address_span_dimension_over_q": 13,
            "address_span_dimension_over_f2": address_span_dimension_f2,
            "two_relation_generators_complete_over_f2": True,
            "independent_frame_relations": [
                "A1+A2=A3+A4",
                "A1+A5=A6+A7",
            ],
            "full_rank_target_sum": 16,
            "direct_baseline_paid_rank_one_calls": len(baseline),
            "candidate_calls": 15,
            "first_seven_pattern_assignment": "For each exceptional plane, choose one of the six permutations (a,b,c) of its three unique projector lifts; assign N1=a, N2=N3=N4=b, and N5=N6=N7=c.",
            "best_case_local_reduction": "1/16 (6.25 percent)",
            "baseline_formal_endpoint": "PASS",
            "dropped_call_control": "REJECTED",
            "corrupt_address_control": "REJECTED",
            "candidate_screen": screen,
        },
        "scope": "Exact finite pattern-space census and one fixed chronological candidate ansatz. No universal two-relation lower bound, physical supplier admission, or new kappa is claimed.",
    }


def canonical_sha256(value: dict) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def value_sha256(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-certificate", action="store_true")
    args = parser.parse_args()
    result = build_certificate()
    certificate = {**result, "sha256": canonical_sha256(result)}
    path = HERE / "CERTIFICATE.json"
    if args.write_certificate:
        path.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads(path.read_text())
        if certificate != expected:
            raise SystemExit("FAIL_CERTIFICATE_MISMATCH")
    census = certificate["pattern_census"]
    screen = certificate["fixed_candidate"]["candidate_screen"]
    print("PASS_TWO_RELATION_PATTERN_CENSUS")
    print(json.dumps({"pattern_census": census, "candidate_screen": screen,
                      "certificate_sha256": certificate["sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
