#!/usr/bin/env python3
"""Exact Q(i) root-pair decoder and four-level tensor block climb.

The checker uses only the Python standard library. It verifies every matrix
entry, every binary support-pairing rank, both frame inverses, the nine-stage
average copy profile, and a rank-1 frame-slot tariff sensitivity.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction as Q
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
ZERO = (Q(0), Q(0))
ONE = (Q(1), Q(0))


def c(real=0, imag=0):
    return (Q(real), Q(imag))


def add(x, y):
    return (x[0] + y[0], x[1] + y[1])


def neg(x):
    return (-x[0], -x[1])


def sub(x, y):
    return add(x, neg(y))


def mul(x, y):
    return (x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0])


def inv(x):
    den = x[0] * x[0] + x[1] * x[1]
    if den == 0:
        raise ZeroDivisionError("zero Gaussian rational")
    return (x[0] / den, -x[1] / den)


def div(x, y):
    return mul(x, inv(y))


def conjugate(x):
    return (x[0], -x[1])


def scale(a, M):
    q = c(a)
    return [[mul(q, x) for x in row] for row in M]


def transpose(M):
    return [list(row) for row in zip(*M)]


def matmul(A, B):
    if not A or not B or len(A[0]) != len(B):
        raise ValueError("matrix dimensions")
    BT = transpose(B)
    return [[sumq(mul(x, y) for x, y in zip(row, col)) for col in BT] for row in A]


def sumq(values):
    out = ZERO
    for value in values:
        out = add(out, value)
    return out


def kron(A, B):
    return [[mul(A[i][j], B[r][k])
             for j in range(len(A[0])) for k in range(len(B[0]))]
            for i in range(len(A)) for r in range(len(B))]


def kron_int(A, B):
    return [[A[i][j] * B[r][k]
             for j in range(len(A[0])) for k in range(len(B[0]))]
            for i in range(len(A)) for r in range(len(B))]


def power_kron(A, exponent, integer=False):
    out = A
    op = kron_int if integer else kron
    for _ in range(exponent - 1):
        out = op(out, A)
    return out


def inverse_matrix(A):
    n = len(A)
    if any(len(row) != n for row in A):
        raise ValueError("inverse requires square matrix")
    aug = [row[:] + [ONE if i == j else ZERO for j in range(n)]
           for i, row in enumerate(A)]
    for col in range(n):
        pivot = next((r for r in range(col, n) if aug[r][col] != ZERO), None)
        if pivot is None:
            raise ValueError("singular frame")
        aug[col], aug[pivot] = aug[pivot], aug[col]
        p = inv(aug[col][col])
        aug[col] = [mul(p, x) for x in aug[col]]
        for row in range(n):
            if row == col or aug[row][col] == ZERO:
                continue
            q = aug[row][col]
            aug[row] = [sub(x, mul(q, y)) for x, y in zip(aug[row], aug[col])]
    return [row[n:] for row in aug]


def rank_f2(M):
    A = [[int(x) & 1 for x in row] for row in M]
    rows, cols = len(A), len(A[0]) if A else 0
    pivot_row = 0
    for col in range(cols):
        pivot = next((r for r in range(pivot_row, rows) if A[r][col]), None)
        if pivot is None:
            continue
        A[pivot_row], A[pivot] = A[pivot], A[pivot_row]
        for r in range(rows):
            if r != pivot_row and A[r][col]:
                A[r] = [x ^ y for x, y in zip(A[r], A[pivot_row])]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def eq(A, B):
    return len(A) == len(B) and all(len(a) == len(b) and a == b for a, b in zip(A, B))


def nnz(A):
    return sum(x != ZERO for row in A for x in row)


def fmt(x):
    a, b = x
    if b == 0:
        return str(a)
    if a == 0:
        return f"{b}*i"
    return f"{a}{'+' if b > 0 else ''}{b}*i"


def require(ok, why):
    if not ok:
        raise AssertionError(why)


def build_result():
    # Two actual E8 roots.  Their Gram matrix is [[2,1],[1,2]].
    roots = [
        [1, 1, 0, 0, 0, 0, 0, 0],
        [1, 0, 1, 0, 0, 0, 0, 0],
    ]
    R0 = [[c(x) for x in row] for row in roots]
    G0_int = [[2, 1], [1, 2]]
    G0 = [[c(x) for x in row] for row in G0_int]
    require([sum(x * x for x in row) for row in roots] == [2, 2], "root norms")
    require(sum(x * y for x, y in zip(*roots)) == 1, "root-pair dot product")
    require(eq(matmul(R0, transpose(R0)), G0), "root Gram reconstruction")

    # A dense complex two-term factorization over Q(i), using ordinary transpose.
    D0 = [[c(1), c(1)], [c(1), c(0, 1)]]
    T0 = [[c(3, -1), c(1, 1)], [c(3, 1), c(-1, -1)]]
    require(eq(matmul(D0, transpose(T0)), scale(2, G0)), "base decoder identity")
    require(nnz(D0) == 4 and nnz(T0) == 4, "base frames must have full support")
    T0_conj_transpose = transpose([[conjugate(x) for x in row] for row in T0])
    require(not eq(matmul(D0, T0_conj_transpose), scale(2, G0)),
            "conjugate transpose must be rejected as a negative control")

    B0 = [[(G0_int[i][j] + 1) & 1 for j in range(2)] for i in range(2)]
    require(B0 == [[1, 0], [0, 1]] and rank_f2(B0) == 2, "base support pairing")

    levels = []
    for s in range(1, 5):
        n = 2 ** s
        Rs = power_kron(R0, s)
        Gs = power_kron(G0, s)
        Ds = scale(Q(1, 2 ** (s - 1)), power_kron(D0, s))
        Ts = power_kron(T0, s)
        require(eq(matmul(Ds, transpose(Ts)), scale(2, Gs)), f"level {s} decoder identity")
        require(nnz(Ds) == n * n and nnz(Ts) == n * n, f"level {s} dense term supports")

        Gs_int = power_kron(G0_int, s, integer=True)
        require(all(Gs[i][j][1] == 0 and Gs[i][j][0].denominator == 1
                    and Gs_int[i][j] == Gs[i][j][0].numerator
                    for i in range(n) for j in range(n)), f"level {s} Gram consistency")
        Bs = [[(Gs_int[i][j] + 1) & 1 for j in range(n)] for i in range(n)]
        rank = rank_f2(Bs)
        require(rank == n, f"level {s} binary support pairing rank")
        require(all(Bs[i][j] == Bs[j][i] for i in range(n) for j in range(n)),
                f"level {s} symmetric label form")
        require(all(Bs[i][i] == 1 for i in range(n)), f"level {s} self-label pairing")

        Di = inverse_matrix(Ds)
        Ti = inverse_matrix(Ts)
        require(eq(matmul(Ds, Di), [[ONE if i == j else ZERO for j in range(n)] for i in range(n)]),
                f"level {s} decoder-frame inverse")
        require(eq(matmul(Ts, Ti), [[ONE if i == j else ZERO for j in range(n)] for i in range(n)]),
                f"level {s} reader-frame inverse")
        require(nnz(Di) == n * n and nnz(Ti) == n * n, f"level {s} inverse frame density")

        # Exact root-span embedding and left inverse: L_s R_s^T = I.
        L0 = [[c(0), c(1), c(0), c(0), c(0), c(0), c(0), c(0)],
              [c(0), c(0), c(1), c(0), c(0), c(0), c(0), c(0)]]
        Ls = power_kron(L0, s)
        require(eq(matmul(Ls, transpose(Rs)),
                   [[ONE if i == j else ZERO for j in range(n)] for i in range(n)]),
                f"level {s} root-span restoration")
        require(nnz(transpose(Rs)) == n * n and nnz(Ls) == n,
                f"level {s} embedding/extraction counts")

        # For each of the two dense tensor frames, s stages apply 2x2 maps to
        # n/2 pairs. D has an additional nontrivial global scale for s > 1.
        staged_const_mults = 4 * n * s + (n if s > 1 else 0)
        staged_adds = 2 * n * s
        levels.append({
            "tensor_factors": s,
            "ambient_dimension": 8 ** s,
            "line_count": n,
            "term_count": n,
            "child_rank_per_term": rank,
            "term_matrix_rank_over_Q_i": 1,
            "copied_information_per_term": rank,
            "copy_mass_per_block": n * rank,
            "support_pairing_rank": rank,
            "full_support_size_per_term_each_side": n,
            "D_frame_shape": [n, n],
            "T_frame_shape": [n, n],
            "forward_frame_nonzero_coefficients": nnz(Ds) + nnz(Ts),
            "inverse_frame_nonzero_coefficients_if_vector_restoration_is_needed": nnz(Di) + nnz(Ti),
            "root_embedding_nonzero_coefficients": nnz(transpose(Rs)),
            "root_span_extraction_reads": nnz(Ls),
            "staged_forward_constant_multiplication_slots_for_D_and_T": staged_const_mults,
            "staged_forward_additions_for_D_and_T": staged_adds,
            "term_products_for_scalar_bilinear_form": n,
            "scalar_accumulation_additions": n - 1,
            "binary_pairing_matrix": Bs,
        })

    # A nine-stage replica has 896 live families, so 56 rank-16 blocks cover
    # it.  Report the exact per-call average rather than charging the entire
    # replica to one call.
    blocks_per_replica = 896 // 16
    require(blocks_per_replica == 56, "selected live-family count must partition into 16-line blocks")
    blocks_per_call = Q(blocks_per_replica, 9)
    # Retain the selected centre path explicitly: eight rank-8 centre terms
    # cost 64.  This is the same centre operation represented by the parent's
    # coverage identity parameter, matching the selected profile.
    local_profile = {16: Q(896, 9), 8: 8}
    local_mass = sum(r * count for r, count in local_profile.items())
    decoder_copy_mass = Q(14336, 9)
    require(local_mass == Q(14912, 9), "per-call COPY mass including the retained centre")
    selected = json.loads((REPO / "certificates/selected-result.json").read_text())
    parent = json.loads((REPO / "research/complex-local-word-ceiling/RESULT.json").read_text())
    selected_local_mass = int(parent["selected"]["local_mass_per_call"])
    require(selected["decimal"] == "0.001672660197076918", "selected-result pin/value")
    require(selected_local_mass == 5586, "selected local mass")
    require(parent["model"]["live_families_per_call"] == "896/9", "selected coverage families")
    require(parent["model"]["centre_per_call"] == 64, "selected centre charge")

    # The parent's coverage law has (73-1)*(896/9)+64 = 7232 total
    # local+centre rank mass per call.  First screen exact decoder COPY rank
    # alone, then expose the unpriced linear frame/restoration bill separately.
    coverage_total = Q(72 * 896, 9) + 64
    require(coverage_total == 7232 and local_mass < coverage_total, "coverage profile fits")
    sys.path.insert(0, str(REPO / "research/complex-local-word-ceiling"))
    import ceiling  # noqa: E402
    local_model = ceiling.model(local_profile, 73, 896, 9, 64)
    ideal_ceiling = ceiling.ceiling(local_profile, 73, 896, 9, 64, grid=Q(1, 10 ** 12))
    selected_a = Q(parent["ceiling"]["a_ceiling"])
    five_percent_target = selected_a * Q(21, 20)
    require(ideal_ceiling[0] > five_percent_target, "COPY-only profile clears the five-percent screen")

    # Explicit tariff sensitivity: charge one rank-1 unit for each counted
    # forward-frame multiply/add, embedding coefficient, restoration read and
    # output accumulation add.  This is a screen, not an asserted physical tariff.
    rank1_proxy_per_block = 272 + 128 + 256 + 16 + 15
    rank1_proxy_per_call = Q(rank1_proxy_per_block * blocks_per_replica, 9)
    proxy_profile = {16: Q(896, 9), 8: 8, 1: rank1_proxy_per_call}
    proxy_ceiling = ceiling.ceiling(proxy_profile, 73, 896, 9, 64, grid=Q(1, 10 ** 12))
    require(proxy_ceiling[1] < selected_a, "one-unit-per-frame-slot proxy misses the selected endpoint")

    # Find the greatest integer number of additional rank-1 units per average
    # call that still clears the +5% target under the pinned parent relaxation.
    lo, hi = 0, 5639
    while hi - lo > 1:
        mid = (lo + hi) // 2
        v = ceiling.relax({16: Q(896, 9), 8: 8, 1: Q(mid)}, 73, 896, 9, 64,
                          five_percent_target)
        if v[1] < 1:
            lo = mid
        elif v[0] > 1:
            hi = mid
        else:
            raise AssertionError("exact threshold bracket did not separate an integer grid point")
    require(ceiling.relax({16: Q(896, 9), 8: 8, 1: Q(lo)}, 73, 896, 9, 64,
                          five_percent_target)[1] < 1, "rank-1 allowance lower endpoint")
    require(ceiling.relax({16: Q(896, 9), 8: 8, 1: Q(hi)}, 73, 896, 9, 64,
                          five_percent_target)[0] > 1, "rank-1 allowance upper endpoint")

    return {
        "status": "PASS_COMPLEX_E8_PAIR_BLOCK_CLIMB",
        "coefficient_field": "Q(i), ordinary transpose",
        "base_roots": roots,
        "base_gram": G0_int,
        "base_D": [[fmt(x) for x in row] for row in D0],
        "base_T": [[fmt(x) for x in row] for row in T0],
        "base_D_times_T_transpose": [[4, 2], [2, 4]],
        "levels": levels,
        "selected_per_call_comparison": {
            "direct_sum_blocks_per_nine_stage_replica": blocks_per_replica,
            "average_blocks_per_call": str(blocks_per_call),
            "live_families_per_nine_stage_replica": 896,
            "local_profile_by_rank_per_call": {"8": 8, "16": str(local_profile[16])},
            "candidate_rank16_child_count_per_call": str(local_profile[16]),
            "candidate_decoder_copy_mass_per_call": str(decoder_copy_mass),
            "retained_selected_centre_profile": {"8": 8},
            "candidate_local_copy_mass_per_call": str(local_mass),
            "idle_mass_per_call_under_parent_coverage": str(local_model["idle_mass"]),
            "selected_local_copy_mass_allowance": selected_local_mass,
            "candidate_to_selected_local_mass_ratio": str(Q(local_mass, selected_local_mass)),
            "parent_full_local_plus_centre_coverage_mass": str(coverage_total),
            "unchanged_selected_centre_charge_if_granted": 64,
            "forward_D_T_frame_nonzero_coefficients_per_call": str(Q(512 * blocks_per_replica, 9)),
            "inverse_D_T_frame_coefficients_per_call_if_vector_output": str(Q(512 * blocks_per_replica, 9)),
            "staged_D_T_constant_multiplications_per_call": str(Q(272 * blocks_per_replica, 9)),
            "staged_D_T_additions_per_call": str(Q(128 * blocks_per_replica, 9)),
            "root_embedding_coefficients_per_call": str(Q(256 * blocks_per_replica, 9)),
            "root_span_restoration_reads_per_call": str(Q(16 * blocks_per_replica, 9)),
            "scalar_accumulation_additions_per_call": str(Q(15 * blocks_per_replica, 9)),
            "COPY_plus_centre_a_ceiling_interval": [str(ideal_ceiling[0]), str(ideal_ceiling[1])],
            "five_percent_target_a": str(five_percent_target),
            "COPY_plus_centre_clears_five_percent": True,
            "frame_slot_rank1_proxy_units_per_call": str(rank1_proxy_per_call),
            "frame_slot_rank1_proxy_a_ceiling_interval": [str(proxy_ceiling[0]), str(proxy_ceiling[1])],
            "frame_slot_proxy_clears_selected_endpoint": False,
            "extra_rank1_allowance_at_five_percent_target": {
                "largest_integer_pass": lo,
                "next_integer_fails": hi,
            },
            "unpriced_physical_contract": "linear frame slots are listed exactly but the parent ceiling has no tariff converting them to copy rank; owner chronology, dirty-state consumer and outer hosting remain open",
        },
        "scope": {
            "exact": "a two-root E8 subalphabet at level 1 and its tensor-product root frames at levels 2 through 4",
            "label_pairing": "B_s=(G_0^tensor_s + all_ones) mod 2; represented by a new nondegenerate 2^s-bit form for s>=2",
            "not_established": [
                "embedding the product labels in the selected 9-bit, 112-port E8 alphabet",
                "an owner/dirty-state chronology or a selected-word consumer",
                "a selected supplier, a kappa improvement, or an all-size theorem",
            ],
        },
        "controls": [
            "ordinary-transpose base identity",
            "all four tensor-level identities entrywise",
            "all four support-pairing matrices have exact full F2 rank",
            "D and T frames and inverses are dense and mutually invertible",
            "root-span embedding and exact left-inverse restoration at every level",
            "per-call scaling uses 56 blocks over nine stages, not all 56 blocks in one call",
            "selected centre profile is retained explicitly as eight rank-8 terms",
            "COPY-only ceiling and one-rank1-unit-per-frame-slot sensitivity",
            "exact integer allowance for additional rank-1 units at the five-percent target",
        ],
    }


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write deterministic RESULT.json")
    args = parser.parse_args()
    result = build_result()
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    path = ROOT / "RESULT.json"
    if args.write:
        path.write_text(payload)
    elif not path.exists() or path.read_text() != payload:
        raise SystemExit("RESULT.json differs from the exact replay; use --write deliberately")
    screen = result["selected_per_call_comparison"]
    ideal_a = Q(screen["COPY_plus_centre_a_ceiling_interval"][1])
    proxy_a = Q(screen["frame_slot_rank1_proxy_a_ceiling_interval"][1])
    print(f"{result['status']} levels=4 rank16_block_copy_mass=256 "
          f"average_profile_mass={screen['candidate_local_copy_mass_per_call']} "
          f"ideal_a={float(ideal_a):.12f} frame_proxy_a={float(proxy_a):.12f}")


if __name__ == "__main__":
    main()
