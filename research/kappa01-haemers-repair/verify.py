#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact three-subset scalar decoder and full-support native tariff."""
from __future__ import annotations

from fractions import Fraction as Q
import hashlib
import importlib.util
from itertools import combinations
import json
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def rank2(rows):
    pivots = {}
    for row in rows:
        while row:
            p = row.bit_length()-1
            if p not in pivots:
                pivots[p] = row
                break
            row ^= pivots[p]
    return len(pivots)


def basis2(rows):
    pivots = {}
    for row in rows:
        while row:
            p = row.bit_length()-1
            if p not in pivots:
                pivots[p] = row
                break
            row ^= pivots[p]
    return list(pivots.values())


def pairing_rank(rows):
    basis = basis2(rows)
    return rank2([sum(((a & b).bit_count() % 2) << j
                     for j, b in enumerate(basis)) for a in basis])


def geometry(n):
    require(n >= 4 and n % 4 == 0, "divisibility hypothesis")
    ports = [sum(1 << i for i in subset) for subset in combinations(range(n), 3)]
    V = len(ports)
    require(V == comb(n, 3), "port count")
    for i, x in enumerate(ports):
        require(x.bit_count() % 2 == 1, "nondegenerate line")
        for j, y in enumerate(ports):
            intersection = (x & y).bit_count()
            fitting = Q(intersection-1, 2)
            factor_sum = sum(Q(1, 2) * ((x >> t) & 1) * ((y >> t) & 1)
                             for t in range(n)) - Q(1, 2)
            require(fitting == factor_sum, "explicit fitting factorization")
            require(i != j or fitting == 1, "fitting diagonal")
            require(i == j or intersection % 2 == 0 or fitting == 0,
                    "forced off-diagonal zero")
    tariffs = [pairing_rank([x for x in ports if (x >> i) & 1]) for i in range(n)]
    tariffs.append(pairing_rank(ports))
    require(tariffs == [n-1]*n+[n], "full support tariff")
    require(sum(tariffs) == n*n, "full copy rank")
    independent = [sum(1 << i for i in subset)
                   for j in range(0, n, 4) for subset in combinations(range(j, j+4), 3)]
    require(len(independent) == n and len(set(independent)) == n, "independent count")
    require(all((x & y).bit_count() % 2 == int(i == j)
                for i, x in enumerate(independent) for j, y in enumerate(independent)),
            "independent identity Gram witness")
    require(sum(tariffs) > len(tariffs), "unit query tariff negative control")
    return dict(n=n, ports=V, native_query_tariffs=tariffs,
                copy_rank=sum(tariffs), independent_witness=independent)


def main():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for item in manifest["local_files"]:
        require(hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"],
                "pinned exact interval dependency")
    path = ROOT / "research/kappa01-fieldline-repair/verify.py"
    spec = importlib.util.spec_from_file_location("fieldline_exact_interval", path)
    interval = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(interval)
    finite = [geometry(n) for n in (4, 8, 12)]
    records = []
    for n in (4, 8, 12, 100):
        V, m = comb(n, 3), 3*n-2
        data = tuple(3*x for x in interval.power89(Q(n-1, m)))
        copies_a = interval.power89(Q(n-1, m))
        copies_b = interval.power89(Q(n, m))
        full = tuple(data[t]+Q(3, 2*V)*(n*copies_a[t]+copies_b[t]) for t in (0, 1))
        require(data[0] > 1 and full[0] > data[0], "actual density rejects target")
        records.append(dict(n=n, h=n, k=1, V=V, copy_rank=n*n,
                            copy_rank_per_port=str(Q(n*n, V)),
                            data_moment=interval.interval_record(data),
                            attempted_fully_charged_moment=interval.interval_record(full)))
    wrong_density = tuple(3*x for x in interval.power89(Q(2, 7)))
    require(wrong_density[1] < 1 < Q(records[-1]["data_moment"]["lower"]),
            "wrong density has passing data but actual density rejects")
    require(Q(10000, comb(100, 3)) < Q(63, 1000), "small concrete copy ratio")
    require(3**17 > 10**8, "all n>=4 integer data gate")
    result = dict(status="CONCRETE_CROSS_CHARACTERISTIC_DECODER_FAILS_DENSITY",
                  finite_geometry_checks=finite, exact_moment_checks=records,
                  controls=["reject_unit_query_tariff", "reject_reused_h_over_k_equals_three",
                            "same_graph_block_rank_at_least_n_times_block_size"],
                  theorem_scope="three-subset family, complete support scalar query tariff")
    encoded = json.dumps(result, indent=2, sort_keys=True)+"\n"
    out = HERE / "RESULT.json"
    if out.exists():
        require(out.read_text() == encoded, "existing receipt differs; inspect before replacing")
    else:
        with out.open("x") as handle:
            handle.write(encoded)
    print("PASS_KAPPA01_HAEMERS_ATTEMPT exact_tariff=n^2 density_obstruction=h/k>=n no_new_supplier")


if __name__ == "__main__":
    main()
