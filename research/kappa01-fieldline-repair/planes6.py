#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact overlap gate for distinct nondegenerate binary planes in dimension six."""
from __future__ import annotations

from collections import Counter
from fractions import Fraction as Q
import hashlib
import importlib.util
from itertools import combinations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, what):
    if not ok:
        raise ValueError(what)


def geometry(name, rows):
    def pairing(a, b):
        out = sum(((row & b).bit_count() & 1) << i for i, row in enumerate(rows))
        return (a & out).bit_count() & 1

    require(len(rows) == 6, "six-dimensional form")
    require(all(pairing(1 << i, 1 << j) == pairing(1 << j, 1 << i)
                for i in range(6) for j in range(6)), "symmetric form")
    require(all(any(pairing(a, 1 << i) for i in range(6)) for a in range(1, 64)),
            "nondegenerate ambient form")
    planes = sorted({tuple(sorted((a, b, a ^ b)))
                     for a, b in combinations(range(1, 64), 2)
                     if (pairing(a, a)*pairing(b, b)) ^ pairing(a, b)})
    require(len(planes) == 336, "exact nondegenerate plane count")
    for plane in planes:
        require(plane[0] ^ plane[1] ^ plane[2] == 0, "closed binary plane")
        require(all((pairing(a, a)*pairing(b, b)) ^ pairing(a, b)
                    for a, b in combinations(plane, 2)), "every plane basis nondegenerate")
    adjacency = [sum(1 << j for j, V in enumerate(planes)
                     if all(pairing(a, b) == 0 for a in U for b in V)) for U in planes]
    require(all(x.bit_count() == 20 for x in adjacency), "degree twenty")
    require(all(not (adjacency[i] >> i & 1) for i in range(336)), "zero diagonal")
    require(all((adjacency[i] >> j & 1) == (adjacency[j] >> i & 1)
                for i in range(336) for j in range(i)), "undirected permission mask")
    closed = [mask | (1 << i) for i, mask in enumerate(adjacency)]
    overlaps, adjacent_overlaps = Counter(), Counter()
    witness = None
    for i in range(336):
        for j in range(i):
            overlap = (closed[i] & closed[j]).bit_count()
            overlaps[overlap] += 1
            if adjacency[i] >> j & 1:
                adjacent_overlaps[overlap] += 1
            if overlap == 4 and witness is None:
                witness = [i, j]
    require(overlaps == Counter({0:15120, 1:30240, 3:3360, 4:7560}), "closed-overlap census")
    require(adjacent_overlaps == Counter({3:3360}), "adjacent overlap census")
    require(sum(overlaps.values()) == 336*335//2, "complete pair census")
    require(witness is not None and max(overlaps) == 4, "attaining overlap bound")
    return dict(form=name, matrix_rows=rows, planes=planes, adjacency_bitmasks=adjacency,
                vertices=336, degree=20, edges=3360,
                closed_row_overlap_counts=dict(sorted(overlaps.items())),
                adjacent_overlap_counts=dict(sorted(adjacent_overlaps.items())),
                overlap_four_witness=witness)


def trace_fixture(exact, name, A, rho, mu):
    n = len(A)
    require(mu > 0, "positive overlap cap")
    require(all(A[i][i] != exact.ZERO for i in range(n)), "nonzero fixture diagonal")
    supports = [{j for j, x in enumerate(row) if x != exact.ZERO} for row in A]
    require(all(len(supports[i] & supports[j]) <= mu for i in range(n) for j in range(i)),
            "fixture overlap hypothesis")
    require(all(sum(exact.norm(x) for x in row) == rho for row in A), "fixture row norms")
    require(all(sum(exact.norm(A[i][j]) for i in range(n)) == rho for j in range(n)),
            "fixture column norms")
    gram = []
    for i in range(n):
        row = []
        for j in range(n):
            value = exact.ZERO
            for t in range(n):
                value = exact.add(value, exact.mul(A[i][t], exact.conjugate(A[j][t])))
            row.append((value[0]/rho, value[1]/rho))
        gram.append(row)
    trace_square = sum(exact.norm(x) for row in gram for x in row)
    fourth = sum(exact.norm(x)**2 for row in A for x in row)/rho**2
    require(trace_square <= (mu+1)*n-mu*fourth < (mu+1)*n, "strict overlap trace gate")
    rank = exact.rank_gaussian(A)
    require(rank >= Q(n*n)/trace_square > Q(n, mu+1), "fixture fitting rank")
    return dict(name=name, order=n, rank=rank, overlap_cap=mu,
                gram_trace_square=str(trace_square), fourth_sum=str(fourth))


def main():
    manifest = json.loads((HERE / "PLANES6-SOURCES.json").read_text())
    for source in manifest["local_files"]:
        require(hashlib.sha256((ROOT / source["path"]).read_bytes()).hexdigest() == source["sha256"],
                "pinned proof or exact arithmetic dependency")
    spec = importlib.util.spec_from_file_location("fieldline_exact", HERE / "verify.py")
    exact = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(exact)
    geometries = [geometry("standard_dot", [1, 2, 4, 8, 16, 32]),
                  geometry("alternating_H_plus_H_plus_H", [2, 1, 8, 4, 32, 16])]
    fixtures = [trace_fixture(exact, "rank_one_K4", [[exact.ONE]*4 for _ in range(4)], Q(4), 4)]
    phased = [[exact.ZERO for _ in range(5)] for _ in range(5)]
    for i in range(5):
        phased[i][i] = (Q(3, 5), Q(0))
        phased[i][(i+1) % 5] = (Q(0), Q(4, 5))
    fixtures.append(trace_fixture(exact, "asymmetric_complex_cycle", phased, Q(1), 4))
    rejected = False
    try:
        trace_fixture(exact, "invalid_K5", [[exact.ONE]*5 for _ in range(5)], Q(5), 4)
    except ValueError as err:
        require(str(err) == "fixture overlap hypothesis", "K5 rejects at the intended hypothesis")
        rejected = True
    require(rejected, "invalid overlap-cap negative control")
    data = tuple(3*x for x in exact.power89(Q(2, 7)))
    unit = exact.power89(Q(1, 14))
    floor = exact.combine(data, Q(3, 10), unit)
    conservative = exact.combine(data, Q(3, 14), unit)
    require(data[1] < 1 < floor[0], "data-only passes but complete query floor fails")
    require(conservative[0] > 1, "even a weaker V/7 rank bound would suffice")
    result = dict(status="DISTINCT_BINARY_PLANES6_SCALAR_QUERY_TARGET_OBSTRUCTION",
                  source_manifest=manifest,
                  geometries=geometries, trace_fixtures=fixtures,
                  strict_complex_fitting_rank_ratio="1/5", positive_query_minimum_rank=1,
                  h=6, k=2, m=14, stage_count=3,
                  data_only_moment=exact.interval_record(data),
                  strict_target_floor=exact.interval_record(floor),
                  weaker_V_over_7_control_floor=exact.interval_record(conservative),
                  controls=["reject_K5_for_overlap_cap4", "do_not_price_every_query_rank2",
                            "data_only_pass_does_not_admit_query_decoder"],
                  scope="distinct ports or induced subsets; scalar query factors; complete support pairing tariff; separate public legs")
    encoded = json.dumps(result, indent=2, sort_keys=True)+"\n"
    out = HERE / "PLANES6-RESULT.json"
    if out.exists():
        require(out.read_text() == encoded, "existing plane receipt differs; inspect before replacing")
    else:
        with out.open("x") as handle:
            handle.write(encoded)
    print("PASS_KAPPA01_PLANES6 forms=2 planes_each=336 max_closed_overlap=4 moment>"
          +exact.show(floor[0])+" distinct_ports_scalar_contract_only")


if __name__ == "__main__":
    main()
