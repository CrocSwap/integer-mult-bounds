#!/usr/bin/env python3
"""Exact constructive geometry attempts and their independently checked bills."""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction as F
import importlib.util
from itertools import combinations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("local_exact_budget", HERE / "verify.py")
budget = importlib.util.module_from_spec(spec)
spec.loader.exec_module(budget)


def require(x: bool, text: str) -> None:
    if not x:
        raise ValueError(text)


def parity(x: int) -> int:
    return x.bit_count() % 2


def rank2(rows: list[int]) -> int:
    pivots = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = row
                break
            row ^= pivots[pivot]
    return len(pivots)


def indefinite_pentagon() -> dict:
    ports = [(1, 0, 0), (0, 1, 0), (4, 0, 3), (3, 3, 4), (0, 4, 3)]
    pairing = [[a[0]*b[0]+a[1]*b[1]-a[2]*b[2] for b in ports] for a in ports]
    require([pairing[i][i] for i in range(5)] == [1, 1, 7, 2, 7], "pentagon nondegeneracy")
    allowed = [(i, j) for i in range(5) for j in range(5) if i != j and pairing[i][j] == 0]
    require(set(allowed) == {(i, j) for i in range(5) for j in range(5)
                             if (i-j) % 5 in (1, 4)}, "pentagon free mask")
    counts = Counter()
    witness = None
    for mask in range(1 << len(allowed)):
        rows = [1 << i for i in range(5)]
        for bit, (i, j) in enumerate(allowed):
            if mask >> bit & 1:
                rows[i] |= 1 << j
        r = rank2(rows)
        counts[r] += 1
        if r == 3 and witness is None:
            witness = rows
    require(min(counts) == 3 and sum(counts.values()) == 1024, "pentagon minrank census")
    # Even the weaker size-two independent set already excludes this target
    # with scalar factors charged only one each.
    floor = budget.add(budget.scale(budget.power(F(2, 7), 8, 9), F(3)),
                       budget.scale(budget.power(F(1, 7), 8, 9), F(3, 5)))
    require(floor[0] > 1, "pentagon target floor")
    return {"form": [[1, 0, 0], [0, 1, 0], [0, 0, -1]], "ports": ports,
            "pairing": pairing, "binary_fitting_rank_counts": dict(sorted(counts.items())),
            "rank_three_fitting_rows_bitmask": witness,
            "independent_set_indices": [0, 2],
            "weak_unit_factor_target_floor": budget.record(floor)}


def apply(columns: tuple[int, ...], x: int) -> int:
    out = 0
    for i in range(5):
        if x >> i & 1:
            out ^= columns[i]
    return out


def plane_geometry() -> dict:
    planes = sorted({tuple(sorted((a, b, a ^ b)))
                     for a, b in combinations(range(1, 32), 2)
                     if parity(a)*parity(b) ^ parity(a & b)})
    require(len(planes) == 80, "nondegenerate plane count")
    lookup = {plane: i for i, plane in enumerate(planes)}
    adjacency = [sum(1 << j for j, v in enumerate(planes)
                     if all(parity(a & b) == 0 for a in u for b in v)) for u in planes]
    require(all(x.bit_count() == 4 for x in adjacency), "plane degree four")
    require(all(not (adjacency[i] >> i & 1) for i in range(80)), "no self adjacency")
    require(all(((adjacency[i] >> j) & 1) == ((adjacency[j] >> i) & 1)
                for i in range(80) for j in range(80)), "symmetric graph")

    def independent(s: tuple[int, ...]) -> bool:
        bits = sum(1 << i for i in s)
        return len(set(s)) == len(s) and all(not (adjacency[i] & bits) for i in s)

    # Discovered by a small optimization, accepted only by exact checks here.
    # No optimizer, optimality claim, or floating point is used in this replay.
    seed = (2, 5, 9, 12, 16, 19, 22, 25, 28, 31, 34, 41, 42, 43, 44, 45, 48,
            51, 52, 53, 54, 55, 56, 57, 58, 59, 63, 64, 65, 66, 67, 71, 75, 79)
    require(independent(seed), "independent seed")
    generators = []
    for i in range(4):
        g = [1 << j for j in range(5)]
        g[i], g[i+1] = g[i+1], g[i]
        generators.append(tuple(g))
    generators.append(tuple((1 << i) ^ (15 if parity(15 & (1 << i)) else 0)
                            for i in range(5)))
    identity = (1, 2, 4, 8, 16)
    matrices, seen = [identity], {identity}
    for g in matrices:
        for h in generators:
            gh = tuple(apply(g, x) for x in h)
            if gh not in seen:
                seen.add(gh)
                matrices.append(gh)
    require(len(matrices) == 720, "generated maps")
    family = set()
    for g in matrices:
        require(all(parity(g[i] & g[j]) == (i == j)
                    for i in range(5) for j in range(5)), "dot-preserving map")
        image = tuple(sorted(lookup[tuple(sorted(apply(g, x) for x in planes[i]))]
                             for i in seed))
        require(independent(image), "independent image")
        family.add(image)
    family = sorted(family)
    counts = [sum(i in s for s in family) for i in range(80)]
    require(len(family) == 30, "independent-set cover size")
    require(Counter(counts) == Counter({12: 60, 15: 20}), "cover multiplicities")
    require(all(counts[i] == (15 if not any(parity(x) for x in u) else 12)
                for i, u in enumerate(planes)), "cover by geometric type")

    # A complete scalar fitting factorization has at least alpha positive-cost
    # factors after removing zero-pairing factors. Price each one at only rank1.
    floor = budget.add(budget.scale(budget.power(F(3, 11), 8, 9), F(3)),
                       budget.scale(budget.power(F(1, 11), 8, 9), F(3, 5)))
    require(floor[0] > F(1016, 1000), "strict plane target floor")
    # With the source coverage law and separate active/query charges,
    # (P-D)/(s*V) >= A*(2+3*s)^(1/9)-8+2/s.  Its derivative is
    # A/(3*(2+3*s)^(8/9))-2/s**2, positive for all s>=3 once positive at3.
    coefficient = budget.add(budget.scale(budget.power(F(3), 8, 9), F(2)),
                             (F(2, 5), F(2, 5)))
    width_power = budget.power(F(11), 1, 9)
    pressure_margin = budget.add((coefficient[0] * width_power[0],
                                  coefficient[1] * width_power[1]),
                                 (F(-22, 3), F(-22, 3)))
    derivative = budget.add(budget.divide(coefficient,
                               budget.scale(budget.power(F(11), 8, 9), F(3))),
                            (F(-2, 9), F(-2, 9)))
    require(pressure_margin[0] > 0, "all-stage pressure base")
    require(derivative[0] > F(3655, 10**6), "all-stage derivative base")
    require(not independent((0, next(i for i in range(80) if adjacency[0] >> i & 1))),
            "orthogonal pair must not be independent")
    return {"ambient_dimension": 5, "port_dimension": 2, "plane_count": 80,
            "planes_nonzero_vector_bitmasks": planes,
            "orthogonality_adjacency_bitmasks": adjacency,
            "degree": 4, "edges": 160,
            "generators_as_column_bitmasks": generators, "generated_maps": 720,
            "independent_seed": seed, "independent_set_cover": family,
            "cover_multiplicities": counts,
            "universal_induced_subset_independence_fraction": "2/5",
            "also_valid_with_nonnegative_port_multiplicities": True,
            "unit_factor_target_floor": budget.record(floor),
            "all_stage_pressure_margin_at_s3": budget.record(pressure_margin),
            "all_stage_pressure_derivative_at_s3": budget.record(derivative),
            "all_stage_extension_hypotheses": "source coverage law, active children rank at most3, separate per-query support-pairing tariff, all other children rank at most m",
            "scope": "nondegenerate rank2 planes, full-orthogonality free mask, scalar outer-product decoding and full support-pairing tariffs"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = {"indefinite_bit_pentagon": indefinite_pentagon(),
              "binary_five_dimensional_planes": plane_geometry(),
              "status": "two concrete repair geometries checked; neither supplies kappa0.1"}
    path = HERE / "PLANE_RESULT.json"
    canonical = json.loads(json.dumps(result))
    if args.write:
        path.write_text(json.dumps(canonical, indent=2, sort_keys=True) + "\n")
    else:
        require(canonical == json.loads(path.read_text()), "geometry receipt changed")
    print("PASS_KAPPA01_GEOMETRY_REPAIRS indefinite_c5=1024 binary_planes=80 cover_sets=30 subset_fraction=2/5 no_new_kappa")


if __name__ == "__main__":
    main()
