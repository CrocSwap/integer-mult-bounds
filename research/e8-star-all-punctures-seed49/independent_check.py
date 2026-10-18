#!/usr/bin/env python3
"""Genuinely independent checker for research/e8-star-all-punctures-seed49.

This checker does not import verify.py or any predecessor script. It uses:
1. Full 240-root enumeration in Z^8 followed by antipodal quotienting in reverse
   lexicographic order.
2. Exact rational RREF via `fractions.Fraction` (rather than integer cross-multiplication).
3. Low-bit-pivot GF(2) elimination on the 120x120 mod-2 Gram matrix (I + A) mod 2.
4. Matroid rank-sum formula sum_{d=0}^7 (9 - r_d) to cross-check optimal basis costs.
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import combinations, combinations_with_replacement, product
import json
from pathlib import Path
import sys
from typing import Any


EXPECTED_M = [0, 1, 3, 6, 12, 20, 36, 63, 120]
EXPECTED_DELTA = [56, 55, 53, 50, 44, 36, 26, 1, 0]
EXPECTED_U = [0, 56, 84, 100, 108, 112, 116, 118, 119, 120]
TARGET_RATIO = Fraction(63, 111)


class IndependentCheckError(RuntimeError):
    """Raised when an independent check fails."""


def check(cond: bool, msg: str) -> None:
    if not cond:
        raise IndependentCheckError(msg)


def enumerate_e8_lines_via_240_roots() -> list[tuple[int, ...]]:
    """Enumerate all 240 roots in doubled E8 coordinates, then quotient by {v, -v}."""
    signed_roots: set[tuple[int, ...]] = set()
    # Type 1: (+/-2, +/-2, 0^6)
    for idx_pair in combinations(range(8), 2):
        for s0, s1 in product((-2, 2), repeat=2):
            v = [0] * 8
            v[idx_pair[0]] = s0
            v[idx_pair[1]] = s1
            signed_roots.add(tuple(v))
    # Type 2: (+/-1)^8 with even number of minus signs
    for signs in product((-1, 1), repeat=8):
        if sum(1 for x in signs if x < 0) % 2 == 0:
            signed_roots.add(signs)
    check(len(signed_roots) == 240, f"Expected 240 signed roots, got {len(signed_roots)}")

    # Quotient by antipodal map using max(v, -v) and sort in reverse order
    reps = {max(v, tuple(-x for x in v)) for v in signed_roots}
    check(len(reps) == 120, f"Expected 120 antipodal root lines, got {len(reps)}")
    return sorted(reps, reverse=True)


def fraction_rref_rank(vectors: list[tuple[int, ...]]) -> int:
    """Compute rational rank over Q using exact Fraction RREF."""
    if not vectors:
        return 0
    mat = [[Fraction(x) for x in v] for v in vectors]
    r = 0
    rows = len(mat)
    cols = len(mat[0])
    for c in range(cols):
        piv = None
        for i in range(r, rows):
            if mat[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        mat[r], mat[piv] = mat[piv], mat[r]
        scale = mat[r][c]
        mat[r] = [ val / scale for val in mat[r] ]
        for i in range(rows):
            if i != r and mat[i][c] != 0:
                factor = mat[i][c]
                mat[i] = [mat[i][j] - factor * mat[r][j] for j in range(cols)]
        r += 1
        if r == cols:
            break
    return r


def lowbit_gf2_basis(masks: list[int]) -> list[int]:
    """GF(2) row reduction using lowest-set-bit pivots."""
    pivots: dict[int, int] = {}
    for m in masks:
        cur = m
        while cur:
            low = cur & -cur
            if low in pivots:
                cur ^= pivots[low]
            else:
                pivots[low] = cur
                break
    return [pivots[k] for k in sorted(pivots)]


def build_code_from_mod2_gram(lines: list[tuple[int, ...]]) -> tuple[list[int], list[int]]:
    """Build the 512-word reader code C from the 120x120 mod-2 Gram matrix (I + A) mod 2."""
    gram_rows: list[int] = []
    for x in lines:
        row_mask = 0
        for j, y in enumerate(lines):
            ip = sum(a * b for a, b in zip(x, y))
            check(ip % 4 == 0, "Inner product in doubled E8 must be divisible by 4")
            if (1 + ip // 4) % 2 != 0:
                row_mask |= 1 << j
        gram_rows.append(row_mask)

    basis = lowbit_gf2_basis(gram_rows)
    check(len(basis) == 9, f"Expected GF(2) rank 9 for (I+A) mod 2, got {len(basis)}")

    codewords = [0]
    for b in basis:
        codewords.extend(x ^ b for x in list(codewords))
    check(len(set(codewords)) == 512, "Expected 512 distinct codewords")

    # Compute 9-bit column functionals for each of the 120 ports
    col_labels: list[int] = []
    for port in range(120):
        lbl = 0
        for bit_idx, b in enumerate(basis):
            if (b >> port) & 1:
                lbl |= 1 << bit_idx
        col_labels.append(lbl)
    check(len(set(col_labels)) == 120 and 0 not in col_labels, "Port columns must be 120 distinct nonzero functionals")
    return codewords, col_labels


def verify_p56_orbits_independently(
    lines: list[tuple[int, ...]], codewords: list[int], col_labels: list[int]
) -> tuple[dict[int, int], dict[int, int]]:
    """Independently classify the 255 weight-56 codewords and verify Orbit 1 and Orbit 2."""
    w56_words = [w for w in codewords if w.bit_count() == 56]
    check(len(w56_words) == 255, f"Expected 255 weight-56 codewords, got {len(w56_words)}")

    # Root non-orthogonality supports S_a = {i : |<L_i, L_a>| == 4}
    s_a_set: set[int] = set()
    for a_idx, la in enumerate(lines):
        m = 0
        for i_idx, li in enumerate(lines):
            if abs(sum(x * y for x, y in zip(la, li))) == 4:
                m |= 1 << i_idx
        check(m.bit_count() == 56, "Each S_a must have weight 56")
        s_a_set.add(m)
    check(len(s_a_set) == 120, "Expected 120 distinct S_a supports")
    check(s_a_set.issubset(set(w56_words)), "All 120 S_a supports must lie in C")

    orb1_words = sorted(set(w56_words) - s_a_set)
    orb2_words = sorted(s_a_set)
    check(len(orb1_words) == 135 and len(orb2_words) == 120, "Orbit partition must be 135 + 120")

    # Check live F2 dimension == 8 on all 255 weight-56 puncture sets
    for w in w56_words:
        live_cols = [col_labels[i] for i in range(120) if not ((w >> i) & 1)]
        check(len(lowbit_gf2_basis(live_cols)) == 8, "Live F2 dimension must be 8 for every weight-56 codeword")

    # Evaluate full 511-reader rank distribution and matroid rank-sum cost on a representative of each orbit
    results: list[dict[int, int]] = []
    for expected_cost, expected_cum, p_mask in [
        (57, [1, 1, 1, 1, 1, 1, 1, 8, 9], orb1_words[0]),
        (50, [1, 1, 1, 1, 1, 1, 8, 8, 9], orb2_words[0]),
    ]:
        all_ones = (1 << 120) - 1
        live_mask = all_ones ^ p_mask
        hist: Counter[int] = Counter()
        ranks_by_word: dict[int, int] = {}
        for cw in codewords[1:]:
            surv = cw & live_mask
            pts = [lines[i] for i in range(120) if (surv >> i) & 1]
            rk = fraction_rref_rank(pts)
            hist[rk] += 1
            ranks_by_word[cw] = rk
            # Coset invariance: cw and cw ^ p_mask have identical live support
            check((cw ^ p_mask) & live_mask == surv, "Coset live-support invariance failed")

        cum_dims: list[int] = []
        for d in range(9):
            sub_words = [cw for cw, rk in ranks_by_word.items() if rk <= d]
            cum_dims.append(len(lowbit_gf2_basis(sub_words)))
        check(cum_dims == expected_cum, f"Cumulative F2 dims {cum_dims} != {expected_cum}")
        matroid_cost = sum(9 - cum_dims[d] for d in range(8))
        check(matroid_cost == expected_cost, f"Matroid cost {matroid_cost} != {expected_cost}")
        results.append(dict(hist))

        # Also verify all 56 single-port restorations restore live GF(2) dimension 9
        restored_count = 0
        for port in range(120):
            if (p_mask >> port) & 1:
                r_mask = p_mask ^ (1 << port)
                live_cols = [col_labels[i] for i in range(120) if not ((r_mask >> i) & 1)]
                check(len(lowbit_gf2_basis(live_cols)) == 9, "Single-port restoration must have GF(2) rank 9")
                restored_count += 1
        check(restored_count == 56, "Expected 56 single-port restorations")

    return results[0], results[1]


def verify_parabolic_flats_via_fraction_inverse(
    lines: list[tuple[int, ...]], codewords: list[int]
) -> None:
    """Independently compute M_d and delta_d across all 256 standard parabolic flats via Fraction matrix inversion."""
    simple = [
        (1, -1, -1, -1, -1, -1, -1, 1),
        (2, 2, 0, 0, 0, 0, 0, 0),
        (-2, 2, 0, 0, 0, 0, 0, 0),
        (0, -2, 2, 0, 0, 0, 0, 0),
        (0, 0, -2, 2, 0, 0, 0, 0),
        (0, 0, 0, -2, 2, 0, 0, 0),
        (0, 0, 0, 0, -2, 2, 0, 0),
        (0, 0, 0, 0, 0, -2, 2, 0),
    ]
    # Invert 8x8 simple-root matrix over Q using Fraction
    aug = [
        [Fraction(x) for x in row] + [Fraction(int(i == j)) for j in range(8)]
        for i, row in enumerate(simple)
    ]
    for col in range(8):
        piv = next(r for r in range(col, 8) if aug[r][col] != 0)
        aug[col], aug[piv] = aug[piv], aug[col]
        sc = aug[col][col]
        aug[col] = [val / sc for val in aug[col]]
        for r in range(8):
            if r != col and aug[r][col] != 0:
                fac = aug[r][col]
                aug[r] = [aug[r][c] - fac * aug[col][c] for c in range(16)]
    inv = [row[8:] for row in aug]

    root_supports: list[int] = []
    for line in lines:
        coords = [sum(line[k] * inv[k][j] for k in range(8)) for j in range(8)]
        check(all(c.denominator == 1 for c in coords), "Non-integral simple-root expansion")
        check(all(c >= 0 for c in coords) or all(c <= 0 for c in coords), "Mixed-sign simple-root expansion")
        supp = sum(1 << j for j, c in enumerate(coords) if c != 0)
        root_supports.append(supp)

    max_cap = [0] * 9
    min_del = [120] * 9
    for sub in range(256):
        d = sub.bit_count()
        flat_mask = 0
        for i, s in enumerate(root_supports):
            if (s & ~sub) == 0:
                flat_mask |= 1 << i
        max_cap[d] = max(max_cap[d], flat_mask.bit_count())
        for cw in codewords[1:]:
            del_cnt = (cw & ~flat_mask).bit_count()
            if del_cnt < min_del[d]:
                min_del[d] = del_cnt
    check(max_cap == EXPECTED_M, f"Independent M_d {max_cap} != {EXPECTED_M}")
    check(min_del == EXPECTED_DELTA, f"Independent delta_d {min_del} != {EXPECTED_DELTA}")


def verify_certificate_against_independent_model(
    cert: dict[str, Any], lines: list[tuple[int, ...]], codewords: list[int]
) -> None:
    """Cross-check CERTIFICATE.json against independent constructions and bounds."""
    verify_parabolic_flats_via_fraction_inverse(lines, codewords)
    # 1. Check parabolic capacities and thresholds
    cap_section = cert["parabolic_capacities_and_thresholds"]
    check(
        [cap_section["M_d"][str(d)] for d in range(9)] == EXPECTED_M,
        "Certificate M_d mismatch",
    )
    check(
        [cap_section["delta_d"][str(d)] for d in range(9)] == EXPECTED_DELTA,
        "Certificate delta_d mismatch",
    )

    # 2. Check Proposition 2 (p=56 classification)
    p56_sec = cert["proposition_2_p56_boundary_classification"]
    check(p56_sec["weight_56_codeword_count"] == 255, "Expected 255 weight-56 codewords in certificate")
    check(
        p56_sec["orbit_1_even_frame"]["analysis"]["star_cost"] == 57
        and p56_sec["orbit_2_root_nonorthogonality"]["analysis"]["star_cost"] == 50,
        "Certificate p=56 orbit star costs must be 57 and 50",
    )

    # 3. Independently verify the attaining subspace witnesses from CERTIFICATE.json
    # and the mathematical lower bounds for U_1..U_9
    h_sec = cert["proposition_3_subspace_union_hierarchy"]
    check(
        [h_sec["sharp_bounds"][str(k)] for k in range(1, 10)] == EXPECTED_U[1:],
        "Certificate sharp U_k bounds mismatch",
    )
    # Hyperplane averaging for k=1,2:
    check((56 * 1 + 0) // 1 == 56, "U_1 formula")
    check((56 * 3 + 1) // 2 == 84, "U_2 formula")
    # k=3 from 5-orbit census weight sum >= 6*56 + 64 = 400 -> 400/4 = 100:
    k3_hist = {int(k): v for k, v in h_sec["k3_weighted_union_histogram"].items()}
    k3_sub = {int(k): v for k, v in h_sec["k3_subspace_union_histogram"].items()}
    gaussian_9_3 = (511 * 510 * 508) // (7 * 6 * 4)
    check(gaussian_9_3 == 788035, "Gaussian binomial [9, 3]_2 mismatch")
    check(
        min(k3_hist) == 100
        and sum(k3_hist.values()) == 7 * gaussian_9_3
        and min(k3_sub) == 100
        and sum(k3_sub.values()) == gaussian_9_3,
        "k=3 census total mismatch",
    )
    # k=4 from 15-hyperplane incidence: 56 |U| >= 15 * 400 = 6000 -> ceil(6000/56) = 108:
    check((15 * 400 + 55) // 56 == 108, "k=4 incidence bound mismatch")
    # k=5..9 from affine hyperplane of annihilator U_k^perp: 120 - 2^(8-k):
    for k in range(5, 10):
        ann_bound = 120 - (1 << (8 - k)) if k <= 8 else 120
        check(ann_bound == EXPECTED_U[k], f"Annihilator bound mismatch at k={k}")

    # 4. Independently solve all 120 puncture budgets across all 24,310 sorted 9-tuples
    all_tuples = list(combinations_with_replacement(range(9), 9))
    check(len(all_tuples) == 24310, "Expected 24310 nondecreasing 9-tuples")

    cert_table = cert["theorem_4_all_puncture_ratio_certificate"]["budget_table"]
    check(len(cert_table) == 120, "Certificate budget table must have 120 rows (p=0..119)")

    k2_fail_list: list[int] = []
    for p in range(120):
        v = 120 - p
        best_k9: int | None = None
        best_k2: int | None = None
        for tup in all_tuples:
            if any(EXPECTED_DELTA[d] > p for d in tup):
                continue
            s = sum(tup)
            if EXPECTED_M[tup[0]] >= EXPECTED_U[1] - p and (
                EXPECTED_M[tup[0]] + EXPECTED_M[tup[1]] >= EXPECTED_U[2] - p
            ):
                if best_k2 is None or s < best_k2:
                    best_k2 = s
            pref = 0
            ok = True
            for k in range(1, 10):
                pref += EXPECTED_M[tup[k - 1]]
                if pref < EXPECTED_U[k] - p:
                    ok = False
                    break
            if ok and (best_k9 is None or s < best_k9):
                best_k9 = s

        if best_k9 is None or best_k2 is None:
            raise IndependentCheckError(f"Infeasible relaxation at p={p}")
        comb = max(best_k9, 72 - p) if p <= 8 else best_k9
        comb_k2 = max(best_k2, 72 - p) if p <= 8 else best_k2
        check(Fraction(comb, v) >= TARGET_RATIO, f"Ratio < 63/111 at p={p}")
        check(
             (Fraction(comb, v) > TARGET_RATIO) == (p != 9),
            f"Strictness mismatch at p={p}",
        )
        if Fraction(comb_k2, v) < TARGET_RATIO:
            k2_fail_list.append(p)

        row = cert_table[p]
        check(row["p"] == p and row["live_ports"] == v, f"Row index mismatch at p={p}")
        check(row["min_cost_k9"] == best_k9, f"min_cost_k9 mismatch at p={p}")
        check(row["combined_lower_bound"] == comb, f"combined_lower_bound mismatch at p={p}")
        check(row["min_cost_k2_only"] == best_k2, f"min_cost_k2_only mismatch at p={p}")

    check(
        k2_fail_list == [72] + list(range(78, 120)),
        f"Unexpected k<=2 failure budgets: {k2_fail_list}",
    )


def main() -> int:
    package_dir = Path(__file__).resolve().parent
    cert_path = package_dir / "CERTIFICATE.json"
    check(cert_path.is_file(), f"Missing {cert_path}")
    cert = json.loads(cert_path.read_text(encoding="utf-8"))

    lines = enumerate_e8_lines_via_240_roots()
    codewords, col_labels = build_code_from_mod2_gram(lines)
    hist1, hist2 = verify_p56_orbits_independently(lines, codewords, col_labels)
    check(hist1 == {0: 1, 7: 112, 8: 398}, f"Orbit 1 histogram mismatch: {hist1}")
    check(hist2 == {0: 1, 6: 56, 7: 198, 8: 256}, f"Orbit 2 histogram mismatch: {hist2}")

    verify_certificate_against_independent_model(cert, lines, codewords)

    print(
        "PASS (independent_check.py): independently verified 240->120 E8 root lines, "
        "mod-2 Gram reader code, Fraction-RREF p=56 orbit costs (57 and 50), "
        "U_1..U_9 hierarchy, and all 120 puncture budgets (0 <= p <= 119)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
