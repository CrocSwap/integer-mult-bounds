#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact character-rank charge gates for binary ports / complex queries."""
from __future__ import annotations

import argparse
from fractions import Fraction as F
import hashlib
import importlib.util
import json
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


def rational_rank(matrix):
    rows = [[F(x) for x in row] for row in matrix]
    rank = 0
    for col in range(len(rows[0]) if rows else 0):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        a = rows[rank][col]
        rows[rank] = [x/a for x in rows[rank]]
        for i in range(rank+1, len(rows)):
            if rows[i][col]:
                a = rows[i][col]
                rows[i] = [x-a*y for x, y in zip(rows[i], rows[rank])]
        rank += 1
    return rank


def character(a, b):
    return -1 if (a & b).bit_count() % 2 else 1


def span(basis):
    values = [0]
    for x in basis:
        values += [x ^ y for y in values]
    return values


def pairing_rank(left, right):
    return rank2([sum(((a & b).bit_count() % 2) << j
                     for j, b in enumerate(right)) for a in left])


def cancellation_control():
    ports = [span([1, 2, 4]), span([4, 8, 16])]
    queries = [([1, 1], [1, 1]), ([-1, 0], [0, 1]), ([0, -1], [1, 0])]
    K = [[sum(u[i]*v[j] for u, v in queries) for j in range(2)] for i in range(2)]
    require(K == [[1, 0], [0, 1]], "cancellation fitting identity")
    require(pairing_rank(ports[0], ports[1]) == 1, "partial nonzero pairing")
    index = [(i, x) for i, port in enumerate(ports) for x in port]
    lifted = [[K[i][j]*(character(x, y)-1) for j, y in index] for i, x in index]
    tariffs, term_ranks, terms = [], [], []
    for u, v in queries:
        readers = [x for i, port in enumerate(ports) if u[i] for x in port]
        sources = [x for j, port in enumerate(ports) if v[j] for x in port]
        r = pairing_rank(readers, sources)
        term = [[u[i]*v[j]*(character(x, y)-1) for j, y in index] for i, x in index]
        term_rank = rational_rank(term)
        require(term_rank <= 2**r-1, "query character-rank upper bound")
        tariffs.append(r)
        term_ranks.append(term_rank)
        terms.append(term)
    require(tariffs == [5, 1, 1], "complete asymmetric tariffs")
    require(all(lifted[a][b] == sum(t[a][b] for t in terms)
                for a in range(16) for b in range(16)), "lifted query identity")
    require(rational_rank(lifted) == 14, "two diagonal rank-seven blocks")
    require(all(u[0]*v[1] == 1 and u[1]*v[0] == 1 for u, v in queries[:1]),
            "deleting low-rank queries destroys fitting")
    return dict(port_bases=[[1, 2, 4], [4, 8, 16]], queries=queries,
                tariffs=tariffs, lifted_query_ranks=term_ranks,
                lifted_fitting_rank=14, total_charge=7, direct_diagonal_charge=6)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    manifest = json.loads((HERE / "WALSH-SOURCES.json").read_text())
    for item in manifest["local_files"]:
        require(hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"],
                "pinned dependency "+item["path"])
    spec = importlib.util.spec_from_file_location("walsh_exact_budget", HERE / "verify.py")
    budget = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(budget)

    character_checks = []
    for r in range(9):
        q = 2**r
        # Every pair of character rows has inner product equal to this sum
        # for the xor of its row indices. Thus H*H^T=q*I exactly.
        sums = [sum(character(x, y) for y in range(q)) for x in range(q)]
        require(sums == [q]+[0]*(q-1), "character orthogonality")
        if r <= 4:
            require(rational_rank([[character(x, y)-1 for y in range(q)] for x in range(q)]) == q-1,
                    "small exact H-minus-J rank")
        if r:
            require(F(r+1, r) <= 2 < F(2**(r+1)-1, 2**r-1), "decreasing capacity-to-cost ratio")
        character_checks.append(dict(binary_rank=r, character_order=q,
                                     nonconstant_character_rank=q-1))

    cases = [(3, 1, 3), (4, 2, 4), (5, 2, 5), (6, 2, 6),
             (6, 3, 5), (6, 3, 6), (7, 3, 6), (7, 3, 7),
             (8, 3, 6), (8, 3, 7), (8, 3, 8)]
    records = []
    for h, k, cap in cases:
        m = 3*h-2*k
        capacity_ratio = F(2**k-1, 2**cap-1)
        moment = budget.add(budget.data_bill(h, k),
                   budget.scale(budget.power(F(cap, m), 8, 9), F(3, 2)*capacity_ratio))
        fee = budget.copy_allowance(h, k)
        mass = cap*capacity_ratio
        excludes = (h, k, cap) not in ((6, 3, 6), (7, 3, 7), (8, 3, 7), (8, 3, 8))
        require(moment[0] > 1 if excludes else moment[1] < 1, "strict gate / open control")
        records.append(dict(h=h, k=k, query_rank_cap=cap, m=m,
                       character_mass_floor_C_over_V=str(mass),
                       mass_floor_C_over_Vk=str(mass/k),
                       necessary_copy_allowance_C_over_Vk=budget.record(fee),
                       target_moment_floor=budget.record(moment),
                       excluded_by_character_moment=excludes))
    for h, k in ((5, 2), (6, 2)):
        mass_per_vk = F(h*(2**k-1), k*(2**h-1))
        require(mass_per_vk > budget.copy_allowance(h, k)[1], "small dimension mass exclusion")
    require(62**9 < 15**9*5**8, "h5k2 dominates the all-stage query coefficient")
    require(F(8*7, 3*255) < budget.copy_allowance(8, 3)[0], "higher dimension remains open")
    odd_prime_controls = []
    for p in (3, 5):
        mass = F(3*(p-1), p**3-1)
        allowance = budget.copy_allowance(3, 1)
        require(mass > allowance[1], "conditional rational-bit mass exclusion")
        floor = budget.add(budget.data_bill(3, 1),
                    budget.scale(budget.power(F(3, 7), 8, 9), F(3*(p-1), 2*(p**3-1))))
        require(floor[0] > 1, "conditional rational-bit moment exclusion")
        odd_prime_controls.append(dict(reduction_prime=p,
                     full_good_reduction_mass_floor_C_over_V=str(mass),
                     target_moment_floor=budget.record(floor),
                     necessary_good_port_fraction_upper_bound=budget.record(budget.scale(allowance, 1/mass)),
                     hypothesis="fixed integral pairing and port bases; every counted port Gram determinant is a unit modulo p"))
    result = dict(status="NECESSARY_QUERY_CAPACITY_BOUND; NO_WORKING_SUPPLIER",
                  theorem="sum(2^query_pairing_rank-1)>=V*(2^port_rank-1)",
                  moment_normalization="displayed target_moment_floor is G for two data banks W=2V",
                  general_coverage_pressure_translation="P-D>=2*V*m*(G-1); M>=1+(2*V/W)*(G-1), so rejection sign is unchanged",
                  character_checks=character_checks,
                  asymmetric_cancellation_control=cancellation_control(),
                  exact_target_gates=records,
                  all_stage_h5k2_integer_witness={"left": 62**9, "right": 15**9*5**8},
                  conditional_rational_bit_good_reduction_gates=odd_prime_controls,
                  scope="binary nondegenerate ports, complex scalar fitting queries, full-orthogonality mask, complete support-pairing tariffs, separate query charges")
    path = HERE / "WALSH-RESULT.json"
    canonical = json.loads(json.dumps(result))
    if args.write:
        path.write_text(json.dumps(canonical, indent=2, sort_keys=True)+"\n")
    else:
        require(canonical == json.loads(path.read_text()), "character receipt changed")
    print("PASS_WALSH_QUERY_CAPACITY ranks=0..8 asymmetric_tariffs=5,1,1 target_gates=11 no_new_supplier")


if __name__ == "__main__":
    main()
