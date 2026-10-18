#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact controls for the source-derived C4-free field-line decoder bound."""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCALE = 10**40
ZERO = (Q(0), Q(0))
ONE = (Q(1), Q(0))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def add(a, b):
    return a[0]+b[0], a[1]+b[1]


def neg(a):
    return -a[0], -a[1]


def mul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def conjugate(a):
    return a[0], -a[1]


def norm(a):
    return a[0]**2+a[1]**2


def divide(a, b):
    t = mul(a, conjugate(b))
    q = norm(b)
    require(q > 0, "nonzero Gaussian divisor")
    return t[0]/q, t[1]/q


def rank_gaussian(A):
    rows = [list(row) for row in A]
    pivot = 0
    for col in range(len(rows[0])):
        index = next((i for i in range(pivot, len(rows)) if rows[i][col] != ZERO), None)
        if index is None:
            continue
        rows[pivot], rows[index] = rows[index], rows[pivot]
        p = rows[pivot][col]
        rows[pivot] = [divide(x, p) for x in rows[pivot]]
        for i in range(len(rows)):
            if i != pivot and rows[i][col] != ZERO:
                c = rows[i][col]
                rows[i] = [add(x, neg(mul(c, y))) for x, y in zip(rows[i], rows[pivot])]
        pivot += 1
        if pivot == len(rows):
            break
    return pivot


def graph_from_support(A):
    n = len(A)
    require(all(A[i][i] != ZERO for i in range(n)), "nonzero fitting diagonal")
    return [{j for j in range(n) if j != i and (A[i][j] != ZERO or A[j][i] != ZERO)}
            for i in range(n)]


def c4_free(graph):
    return all(len(graph[i] & graph[j]) <= 1
               for i in range(len(graph)) for j in range(i))


def trace_fixture(name, A, rho):
    """B=A/sqrt(rho), evaluated without introducing irrational coefficients."""
    n = len(A)
    graph = graph_from_support(A)
    require(c4_free(graph), "C4-free fixture required")
    require(all(sum(norm(x) for x in row) == rho for row in A), "scaled row norms")
    require(all(sum(norm(A[i][j]) for i in range(n)) == rho for j in range(n)), "scaled column norms")
    supports = [{j for j, x in enumerate(row) if x != ZERO} for row in A]
    require(all(len(supports[i] & supports[j]) <= 3
                for i in range(n) for j in range(i)), "three-column overlap")
    C = []
    for i in range(n):
        row = []
        for j in range(n):
            value = ZERO
            for k in range(n):
                value = add(value, mul(A[i][k], conjugate(A[j][k])))
            row.append((value[0]/rho, value[1]/rho))
        C.append(row)
    require(sum(C[i][i][0] for i in range(n)) == n
            and all(C[i][i][1] == 0 for i in range(n)), "trace n")
    frobenius = sum(norm(x) for row in C for x in row)
    fourth = sum(norm(x)**2 for row in A for x in row)/rho**2
    require(frobenius <= 4*n-3*fourth < 4*n, "strict trace inequality")
    rank = rank_gaussian(A)
    require(rank == rank_gaussian(C), "Gram rank")
    require(rank >= Q(n*n)/frobenius > Q(n, 4), "rank consequence")
    return dict(name=name, size=n, rank=rank, squared_modulus_fourth_sum=str(fourth),
                gram_trace_square=str(frobenius), trace_upper_bound=str(4*n-3*fourth))


def matrix_controls():
    tri = [[ONE for _ in range(3)] for _ in range(3)]
    fixtures = [trace_fixture("rank_one_triangle", tri, Q(3))]
    directed = [[ZERO for _ in range(5)] for _ in range(5)]
    for i in range(5):
        directed[i][i] = (Q(3, 5), Q(0))
        directed[i][(i+1) % 5] = (Q(0), Q(4, 5))
    fixtures.append(trace_fixture("asymmetric_complex_cycle", directed, Q(1)))
    double = [[ONE if i//3 == j//3 else ZERO for j in range(6)] for i in range(6)]
    fixtures.append(trace_fixture("two_triangle_blocks", double, Q(3)))

    # Reducible support: three singleton SCC blocks, positive off-diagonal
    # edges that cannot belong to any full permutation diagonal.
    triangular = [[ONE, ONE, ZERO], [ZERO, ONE, ONE], [ZERO, ZERO, ONE]]
    require(c4_free(graph_from_support(triangular)), "reducible support graph")
    require(rank_gaussian(triangular) >= sum(rank_gaussian([[triangular[i][i]]]) for i in range(3)),
            "block triangular rank inequality")

    # Removing the graph hypothesis really breaks the alleged n/4 bound.
    K4 = [[ONE for _ in range(4)] for _ in range(4)]
    require(not c4_free(graph_from_support(K4)), "K4 hypothesis control")
    require(rank_gaussian(K4) == Q(len(K4), 4), "K4 defeats strict n/4 conclusion")
    rejected = False
    try:
        trace_fixture("invalid_K4", K4, Q(4))
    except ValueError:
        rejected = True
    require(rejected, "invalid C4 fixture accepted")
    return fixtures


def power89(x):
    a, b = x.numerator**8*SCALE**9, x.denominator**8
    lo, hi = 0, 1
    while hi**9*b <= a:
        hi *= 2
    while hi-lo > 1:
        mid = (lo+hi)//2
        if mid**9*b <= a:
            lo = mid
        else:
            hi = mid
    require(lo**9*b <= a < hi**9*b, "outward ninth-root witnesses")
    return Q(lo, SCALE), Q(hi, SCALE)


def combine(x, multiplier, y):
    return x[0]+multiplier*y[0], x[1]+multiplier*y[1]


def show(value):
    n = value.numerator*10**18//value.denominator
    return f"{n//10**18}.{n%10**18:018d}"


def interval_record(x):
    return dict(lower=str(x[0]), upper=str(x[1]), lower_decimal=show(x[0]), upper_decimal=show(x[1]))


def build():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for source in manifest["local_files"]:
        require(hashlib.sha256((ROOT/source["path"]).read_bytes()).hexdigest() == source["sha256"],
                "source hash: "+source["path"])
    data = tuple(3*x for x in power89(Q(2, 7)))
    min_child, max_child = power89(Q(1, 7)), power89(Q(3, 7))
    gates = {
        "complex_n_over_4_query_count": combine(data, Q(3, 8), min_child),
        "complex_n_over_4_mass_only": combine(data, Q(1, 8), max_child),
        "published_real_n_over_6_via_complex_n_over_12_query_count": combine(data, Q(1, 8), min_child),
        "published_real_n_over_6_via_complex_n_over_12_mass_only": combine(data, Q(1, 24), max_child),
    }
    require(data[1] < 1, "data-only relaxation passes")
    require(all(bounds[0] > 1 for bounds in gates.values()), "each fully charged gate fails")
    # Simple rational corroboration of the stronger count gate.
    require(Q(41, 125)**9 < Q(2, 7)**8, "data rational lower bound")
    require(Q(7, 40)**9 < Q(1, 7)**8, "copy rational lower bound")
    rational_gate = 3*Q(41, 125)+Q(3, 8)*Q(7, 40)
    require(rational_gate > 1, "independent rational gate")
    return dict(
        status="PASS_KAPPA01_FIELDLINE_SCALAR_DECODER_OBSTRUCTION",
        source_base=manifest["base"],
        target_primitive_saving="1/9", target_kappa="1/10",
        complex_fitting_rank_bound="rank_C M > n/4 for undirected C4-free masks",
        scalar_total_query_bound="paid_queries > V/4; each nonzero complete-support tariff >= k",
        data_only_moment=interval_record(data),
        necessary_moment_lower_bounds={key: interval_record(value) for key,value in gates.items()},
        independent_rational_count_gate=str(rational_gate),
        exact_matrix_fixtures=matrix_controls(),
        controls={"asymmetric_complex_allowed":True, "reducible_support_allowed":True,
                  "K4_hypothesis_violation_rejected":True, "K4_rank_conclusion_fails":True,
                  "data_only_relaxation_passes":True, "conservative_published_theorem_alone_suffices":True},
        proof_dependencies=["positive diagonal scaling for nonnegative total-support matrices (Sinkhorn-Knopp)",
                            "spectral and scalar Cauchy-Schwarz", "finite-field trace pairing nondegeneracy"],
        scope="Scalar outer-product totals, complete plane-support tariff and separate public data legs; no universal supplier or kappa theorem."
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = build()
    if args.output:
        with args.output.open("x") as output:
            output.write(json.dumps(result, indent=2, sort_keys=True)+"\n")
    else:
        require(result == json.loads((HERE / "RESULT.json").read_text()), "receipt mismatch")
    print(result["status"], "moment>" + result["necessary_moment_lower_bounds"]["complex_n_over_4_query_count"]["lower_decimal"],
          "scalar_contract_only")


if __name__ == "__main__":
    main()
