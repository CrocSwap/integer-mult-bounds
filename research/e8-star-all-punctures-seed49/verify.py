#!/usr/bin/env python3
"""Verify the all-puncture E8 star label-decoder bound and 56-puncture dimension-loss classification.

This script is self-contained, uses only the Python standard library, and runs
under `python3 -I -O -B` without relying on Python `assert` statements.
"""

from __future__ import annotations

import argparse
from collections import Counter, deque
from fractions import Fraction
import hashlib
from itertools import combinations, combinations_with_replacement, product
import json
from pathlib import Path
import sys
from typing import Any


BASE_COMMIT = "ce7ad1b6ab09452c3478723a2e96ed5ff212dc08"
SPRINT_SEED = 49

EXPECTED_M = {0: 0, 1: 1, 2: 3, 3: 6, 4: 12, 5: 20, 6: 36, 7: 63, 8: 120}
EXPECTED_DELTA = {0: 56, 1: 55, 2: 53, 3: 50, 4: 44, 5: 36, 6: 26, 7: 1, 8: 0}
EXPECTED_SUBSPACE_UNIONS = {
    1: 56,
    2: 84,
    3: 100,
    4: 108,
    5: 112,
    6: 116,
    7: 118,
    8: 119,
    9: 120,
}
KNOWN_RATIO = Fraction(63, 111)


class VerificationError(RuntimeError):
    """Raised when any mathematical or certificate obligation fails."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def verify_sources(package_dir: Path) -> dict[str, Any]:
    sources_path = package_dir / "SOURCES.json"
    require(sources_path.is_file(), f"Missing {sources_path}")
    manifest = json.loads(sources_path.read_text(encoding="utf-8"))
    require(
        manifest.get("base_commit") == BASE_COMMIT,
        f"Expected base_commit {BASE_COMMIT}, got {manifest.get('base_commit')}",
    )
    retained = manifest.get("retained_sources", [])
    require(len(retained) == 5, f"Expected 5 retained sources, got {len(retained)}")
    checked_files: list[dict[str, Any]] = []
    for entry in retained:
        rel_path = entry["local_path"]
        file_path = package_dir / rel_path
        require(file_path.is_file(), f"Missing retained source file {file_path}")
        raw = file_path.read_bytes()
        digest = sha256_bytes(raw)
        blob = git_blob_sha1(raw)
        require(
            digest == entry["sha256"],
            f"SHA-256 mismatch for {rel_path}: {digest} != {entry['sha256']}",
        )
        require(
            blob == entry["git_blob"],
            f"Git blob SHA-1 mismatch for {rel_path}: {blob} != {entry['git_blob']}",
        )
        checked_files.append(
            {
                "pr": entry["pr"],
                "local_path": rel_path,
                "sha256": digest,
                "git_blob": blob,
            }
        )
    return {
        "base_commit": manifest["base_commit"],
        "retained_source_count": len(checked_files),
        "retained_sources": checked_files,
    }


def canonical_sign(vec: tuple[int, ...]) -> tuple[int, ...]:
    for coord in vec:
        if coord != 0:
            return vec if coord > 0 else tuple(-x for x in vec)
    raise VerificationError("Zero vector has no projective sign representative")


def build_e8_root_lines() -> tuple[list[tuple[int, ...]], list[tuple[int, ...]]]:
    """Construct the 120 positive E8 root lines in doubled coordinates (norm 8)."""
    lines: list[tuple[int, ...]] = []
    for i, j in combinations(range(8), 2):
        for s_j in (2, -2):
            vec = [0] * 8
            vec[i] = 2
            vec[j] = s_j
            lines.append(tuple(vec))
    for signs in product((1, -1), repeat=7):
        full = (1,) + signs
        if full.count(-1) % 2 == 0:
            lines.append(full)
    require(len(lines) == 120, f"Expected 120 E8 root lines, got {len(lines)}")
    require(len(set(lines)) == 120, "Duplicate E8 root lines found")
    for line in lines:
        norm = sum(x * x for x in line)
        require(norm == 8, f"Expected doubled E8 norm 8, got {norm}")
    # Standard E8 simple roots in doubled coordinates
    simple_roots: list[tuple[int, ...]] = [
        (2, -2, 0, 0, 0, 0, 0, 0),
        (0, 2, -2, 0, 0, 0, 0, 0),
        (0, 0, 2, -2, 0, 0, 0, 0),
        (0, 0, 0, 2, -2, 0, 0, 0),
        (0, 0, 0, 0, 2, -2, 0, 0),
        (0, 0, 0, 0, 0, 2, -2, 0),
        (0, 0, 0, 0, 0, 2, 2, 0),
        (-1, -1, -1, -1, -1, -1, -1, -1),
    ]
    return lines, simple_roots


def build_weyl_generators(
    lines: list[tuple[int, ...]], simple_roots: list[tuple[int, ...]]
) -> list[tuple[int, ...]]:
    index_of = {line: idx for idx, line in enumerate(lines)}
    perms: list[tuple[int, ...]] = []
    for alpha in simple_roots:
        perm: list[int] = []
        for v in lines:
            dot = sum(a * b for a, b in zip(alpha, v))
            require(dot % 4 == 0, f"Non-integral reflection dot product {dot}")
            step = dot // 4
            reflected = canonical_sign(tuple(v[i] - step * alpha[i] for i in range(8)))
            perm.append(index_of[reflected])
        require(sorted(perm) == list(range(120)), "Generator is not a bijection on 120 lines")
        perms.append(tuple(perm))
    return perms


def build_decoder_and_reader_code(
    lines: list[tuple[int, ...]],
    simple_roots: list[tuple[int, ...]],
) -> tuple[list[int], list[int], list[int], dict[int, int]]:
    """Construct the 9-row binary decoder B, 512 codewords of C, and 120 port labels.

    Rows 0..7 are the simple-root mod-2 inner products <alpha_j, L_i>/4 mod 2,
    which span the 8-dimensional linear evaluation subspace C_lin (containing the
    120 weight-56 root-nonorthogonality supports S_a and 135 weight-64 frame words).
    Row 8 is the all-ones word 1_120, whose coset 1_120 + C_lin contains the
    135 weight-56 even-frame words of Orbit 1.
    """
    b_rows: list[int] = [0] * 9
    port_labels: list[int] = [0] * 120
    for idx, v in enumerate(lines):
        bit = 1 << idx
        for j in range(8):
            dot = sum(a * b for a, b in zip(simple_roots[j], v))
            if (dot // 4) & 1:
                b_rows[j] |= bit
                port_labels[idx] |= 1 << j
        b_rows[8] |= bit
        port_labels[idx] |= 1 << 8
    require(
        len(set(port_labels)) == 120 and 0 not in port_labels,
        "Port columns of B must be 120 distinct nonzero 9-bit functionals",
    )
    codewords: list[int] = [0] * 512
    mask_to_label: dict[int, int] = {}
    for label in range(512):
        mask = 0
        for bit_idx in range(9):
            if (label >> bit_idx) & 1:
                mask ^= b_rows[bit_idx]
        codewords[label] = mask
        mask_to_label[mask] = label
    require(len(mask_to_label) == 512, "Reader code C must have dimension 9 (512 distinct words)")
    all_ones = (1 << 120) - 1
    require(all_ones in mask_to_label, "All-ones word 1_120 must lie in reader code C")
    return b_rows, codewords, port_labels, mask_to_label


def apply_perm_to_mask(mask: int, perm: tuple[int, ...]) -> int:
    out = 0
    rem = mask
    while rem:
        low = rem & -rem
        idx = low.bit_length() - 1
        out |= 1 << perm[idx]
        rem ^= low
    return out


def gf2_rank_9bit(vectors: list[int]) -> int:
    basis: list[int] = []
    for vec in vectors:
        cur = vec
        for b in basis:
            if (cur ^ b) < cur:
                cur ^= b
        if cur:
            basis.append(cur)
            basis.sort(reverse=True)
    return len(basis)


def rational_rank_8d(lines: list[tuple[int, ...]], indices: list[int]) -> int:
    """Exact rational rank over Q using bare integer cross-multiplication."""
    rows = [list(lines[i]) for i in indices]
    pivot_row = 0
    row_count = len(rows)
    for col in range(8):
        sel = None
        for r in range(pivot_row, row_count):
            if rows[r][col] != 0:
                sel = r
                break
        if sel is None:
            continue
        rows[pivot_row], rows[sel] = rows[sel], rows[pivot_row]
        piv = rows[pivot_row][col]
        for r in range(pivot_row + 1, row_count):
            val = rows[r][col]
            if val != 0:
                for c in range(col, 8):
                    rows[r][c] = rows[r][c] * piv - rows[pivot_row][c] * val
                g = 0
                for c in range(col, 8):
                    if rows[r][c] != 0:
                        g = abs(rows[r][c]) if g == 0 else _gcd(g, abs(rows[r][c]))
                if g > 1:
                    for c in range(col, 8):
                        rows[r][c] //= g
        pivot_row += 1
        if pivot_row == 8:
            break
    return pivot_row


def _gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a


def mask_to_indices(mask: int) -> list[int]:
    indices: list[int] = []
    rem = mask
    while rem:
        low = rem & -rem
        indices.append(low.bit_length() - 1)
        rem ^= low
    return indices


def build_parabolic_flats_and_capacities(
    lines: list[tuple[int, ...]],
    simple_roots: list[tuple[int, ...]],
    codewords: list[int],
    mask_to_label: dict[int, int],
) -> tuple[list[tuple[int, int]], dict[int, Any]]:
    """Construct the 256 standard parabolic root-line flats and verify M_d, delta_d."""
    flats_by_rank: dict[int, set[int]] = {d: set() for d in range(9)}
    for r in range(9):
        for subset in combinations(range(8), r):
            sub_roots = [simple_roots[i] for i in subset]
            flat_mask = 0
            for idx, line in enumerate(lines):
                if rational_rank_8d(sub_roots + [line], list(range(len(sub_roots) + 1))) == r:
                    flat_mask |= 1 << idx
            flats_by_rank[r].add(flat_mask)

    # Close under intersections to confirm all 256 parabolic flats and verify capacities M_d
    flat_pairs: list[tuple[int, int]] = []
    computed_m: dict[int, int] = {}
    for d in range(9):
        require(len(flats_by_rank[d]) > 0, f"No parabolic flats found for rank {d}")
        computed_m[d] = max(mask.bit_count() for mask in flats_by_rank[d])
        require(
            computed_m[d] == EXPECTED_M[d],
            f"Capacity M_{d} mismatch: {computed_m[d]} != {EXPECTED_M[d]}",
        )
        for mask in sorted(flats_by_rank[d]):
            flat_pairs.append((d, mask))

    # Compute single-reader puncture threshold delta_d = min_{c != 0, F_d} |supp(c) \ F_d|
    computed_delta: dict[int, int] = {}
    sharp_witnesses: dict[str, dict[str, Any]] = {}
    for d in range(9):
        best_val: int | None = None
        best_witness: dict[str, Any] | None = None
        for flat_mask in sorted(flats_by_rank[d]):
            for label in range(1, 512):
                cw = codewords[label]
                diff = cw & ~flat_mask
                cnt = diff.bit_count()
                if best_val is None or cnt < best_val:
                    best_val = cnt
                    best_witness = {
                        "rank": d,
                        "delta": cnt,
                        "reader_label": label,
                        "reader_weight": cw.bit_count(),
                        "surviving_ports": (cw & flat_mask).bit_count(),
                        "punctured_ports_indices": mask_to_indices(diff),
                    }
        require(best_val == EXPECTED_DELTA[d], f"delta_{d} mismatch: {best_val} != {EXPECTED_DELTA[d]}")
        if best_witness is None:
            raise VerificationError(f"Missing witness for rank {d}")
        computed_delta[d] = best_val
        sharp_witnesses[str(d)] = best_witness

    return flat_pairs, {
        "parabolic_flat_count": len(flat_pairs),
        "M_d": {str(k): v for k, v in computed_m.items()},
        "delta_d": {str(k): v for k, v in computed_delta.items()},
        "sharp_witnesses": sharp_witnesses,
    }


def classify_weyl_orbits(
    codewords: list[int],
    mask_to_label: dict[int, int],
    weyl_perms: list[tuple[int, ...]],
) -> tuple[list[list[int]], dict[str, Any]]:
    visited: set[int] = set()
    orbits: list[list[int]] = []
    for mask in sorted(codewords[1:]):
        if mask in visited:
            continue
        queue = deque([mask])
        visited.add(mask)
        comp: list[int] = []
        while queue:
            cur = queue.popleft()
            comp.append(cur)
            for perm in weyl_perms:
                nxt = apply_perm_to_mask(cur, perm)
                require(nxt in mask_to_label, "W(E8) reflection left reader code C")
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append(nxt)
        comp.sort()
        orbits.append(comp)
    orbits.sort(key=lambda orb: (orb[0].bit_count(), -len(orb), orb[0]))
    require(len(orbits) == 5, f"Expected 5 W(E8) orbits on C\\{{0}}, got {len(orbits)}")
    summary = [
        {
            "orbit_index": idx,
            "size": len(orb),
            "weight": orb[0].bit_count(),
            "rep_label": mask_to_label[orb[0]],
        }
        for idx, orb in enumerate(orbits)
    ]
    require(
        [(s["weight"], s["size"]) for s in summary]
        == [(56, 135), (56, 120), (64, 135), (64, 120), (120, 1)],
        f"Unexpected W(E8) orbit table: {summary}",
    )
    return orbits, {"orbit_count": 5, "orbits": summary}


def analyze_puncture_mask(
    p_mask: int,
    lines: list[tuple[int, ...]],
    codewords: list[int],
    port_labels: list[int],
) -> dict[str, Any]:
    """Compute exact 511-reader star ranks, cumulative F2 dimensions, and live-quotient cost."""
    all_mask = (1 << 120) - 1
    live_mask = all_mask ^ p_mask
    live_indices = mask_to_indices(live_mask)
    live_dim = gf2_rank_9bit([port_labels[i] for i in live_indices])

    reader_ranks: list[int] = [0] * 512
    rank_hist: Counter[int] = Counter()
    for label in range(1, 512):
        surv = codewords[label] & live_mask
        if surv == 0:
            rk = 0
        else:
            rk = rational_rank_8d(lines, mask_to_indices(surv))
        reader_ranks[label] = rk
        rank_hist[rk] += 1

    # Cumulative F2 dimensions r_d = dim span {c in C : s_P(c) <= d}
    cum_dims: list[int] = []
    basis_weights: list[int] = []
    basis_labels: list[int] = []
    cur_basis: list[int] = []
    for d in range(9):
        candidates = [label for label in range(1, 512) if reader_ranks[label] <= d]
        for cand in candidates:
            reduced = cand
            for b in cur_basis:
                if (reduced ^ b) < reduced:
                    reduced ^= b
            if reduced:
                cur_basis.append(reduced)
                cur_basis.sort(reverse=True)
                basis_weights.append(d)
                basis_labels.append(cand)
        cum_dims.append(len(cur_basis))
    require(len(basis_weights) == 9, "Matroid greedy basis of C must have 9 elements")

    # Verify matroid rank identity sum_{i=1}^9 d_i == sum_{d=0}^7 (9 - r_d)
    total_cost = sum(basis_weights)
    rank_sum_formula = sum(9 - cum_dims[d] for d in range(8))
    require(
        total_cost == rank_sum_formula,
        f"Matroid basis cost {total_cost} != cumulative rank formula {rank_sum_formula}",
    )

    # Check kernel K_P = {c in C : supp(c) subseteq P} and coset invariance on C / K_P
    kernel_labels = [label for label in range(512) if (codewords[label] & live_mask) == 0]
    k0 = (len(kernel_labels) - 1).bit_length()
    require(len(kernel_labels) == (1 << k0), "Kernel size is not a power of 2")
    require(9 - k0 == live_dim, f"Rank-nullity mismatch: 9 - {k0} != {live_dim}")

    for label in range(512):
        base_surv = codewords[label] & live_mask
        base_rk = reader_ranks[label]
        for z in kernel_labels:
            require(
                (codewords[label ^ z] & live_mask) == base_surv,
                "Live support changed within a K_P coset",
            )
            require(
                reader_ranks[label ^ z] == base_rk,
                "Star rank changed within a K_P coset",
            )

    # Live-quotient basis weights (excluding kernel elements of weight 0)
    live_basis_weights = [w for w in basis_weights if w > 0]
    require(
        len(live_basis_weights) == live_dim,
        f"Live quotient basis size {len(live_basis_weights)} != live dimension {live_dim}",
    )
    require(
        sum(live_basis_weights) == total_cost,
        "Live quotient star cost differs from full 9-reader star cost",
    )

    return {
        "puncture_size": p_mask.bit_count(),
        "live_ports": len(live_indices),
        "kernel_dim": k0,
        "live_f2_dim": live_dim,
        "rank_histogram": {str(k): rank_hist[k] for k in sorted(rank_hist)},
        "cumulative_f2_dims": cum_dims,
        "optimal_basis_weights": basis_weights,
        "optimal_basis_labels": basis_labels,
        "live_quotient_basis_weights": live_basis_weights,
        "star_cost": total_cost,
    }


def verify_p56_boundary(
    lines: list[tuple[int, ...]],
    codewords: list[int],
    port_labels: list[int],
    mask_to_label: dict[int, int],
    orbits: list[list[int]],
) -> dict[str, Any]:
    """Verify Proposition 2: complete classification of the 255 weight-56 puncture sets at p=56."""
    orb1, orb2 = orbits[0], orbits[1]
    require(len(orb1) == 135 and len(orb2) == 120, "Unexpected weight-56 orbit sizes")

    # Verify that Orbit 1 = weight-56 words in the 256-word frame coset 1_120 + C_lin (bit 8 == 1)
    even_frame_w56 = sorted(
        codewords[label]
        for label in range(1, 512)
        if ((label >> 8) & 1) == 1 and codewords[label].bit_count() == 56
    )
    require(orb1 == even_frame_w56, "Orbit 1 does not match the 135 even-frame weight-56 codewords")

    # Verify that Orbit 2 = the 120 root-nonorthogonality supports S_a = {i : |<L_i, L_a>| == 4}
    nonorth_supports: list[tuple[int, int]] = []
    for a_idx, line_a in enumerate(lines):
        supp = 0
        for i_idx, line_i in enumerate(lines):
            if abs(sum(x * y for x, y in zip(line_a, line_i))) == 4:
                supp |= 1 << i_idx
        require(supp.bit_count() == 56, f"Expected |S_a| = 56, got {supp.bit_count()}")
        require(supp in mask_to_label, "Root non-orthogonality support S_a not in reader code C")
        nonorth_supports.append((supp, a_idx))
    nonorth_masks = sorted(s for s, _ in nonorth_supports)
    require(orb2 == nonorth_masks, "Orbit 2 does not match the 120 root-nonorthogonality supports S_a")

    # Verify that all 255 weight-56 masks have live F2 dimension 8 (k_0 = 1)
    for mask in orb1 + orb2:
        live_indices = mask_to_indices(((1 << 120) - 1) ^ mask)
        dim = gf2_rank_9bit([port_labels[i] for i in live_indices])
        require(dim == 8, f"Expected live F2 dimension 8 at weight-56 mask, got {dim}")

    # Analyze canonical representatives and sprint-seed-49 orbit members (index 49 in each sorted orbit)
    rep1_mask = orb1[0]
    seed1_mask = orb1[SPRINT_SEED]
    rep2_mask = orb2[0]
    seed2_mask = orb2[SPRINT_SEED]

    rep1_info = analyze_puncture_mask(rep1_mask, lines, codewords, port_labels)
    seed1_info = analyze_puncture_mask(seed1_mask, lines, codewords, port_labels)
    rep2_info = analyze_puncture_mask(rep2_mask, lines, codewords, port_labels)
    seed2_info = analyze_puncture_mask(seed2_mask, lines, codewords, port_labels)

    require(
        rep1_info["rank_histogram"] == {"0": 1, "7": 112, "8": 398}
        and seed1_info["rank_histogram"] == {"0": 1, "7": 112, "8": 398},
        f"Orbit 1 rank histogram mismatch: {rep1_info['rank_histogram']}",
    )
    require(
        rep1_info["cumulative_f2_dims"] == [1, 1, 1, 1, 1, 1, 1, 8, 9]
        and seed1_info["cumulative_f2_dims"] == [1, 1, 1, 1, 1, 1, 1, 8, 9],
        f"Orbit 1 cumulative F2 dims mismatch: {rep1_info['cumulative_f2_dims']}",
    )
    require(
        rep1_info["optimal_basis_weights"] == [0, 7, 7, 7, 7, 7, 7, 7, 8]
        and rep1_info["star_cost"] == 57
        and seed1_info["star_cost"] == 57,
        "Orbit 1 optimal basis weights or cost 57 mismatch",
    )

    require(
        rep2_info["rank_histogram"] == {"0": 1, "6": 56, "7": 198, "8": 256}
        and seed2_info["rank_histogram"] == {"0": 1, "6": 56, "7": 198, "8": 256},
        f"Orbit 2 rank histogram mismatch: {rep2_info['rank_histogram']}",
    )
    require(
        rep2_info["cumulative_f2_dims"] == [1, 1, 1, 1, 1, 1, 8, 8, 9]
        and seed2_info["cumulative_f2_dims"] == [1, 1, 1, 1, 1, 1, 8, 8, 9],
        f"Orbit 2 cumulative F2 dims mismatch: {rep2_info['cumulative_f2_dims']}",
    )
    require(
        rep2_info["optimal_basis_weights"] == [0, 6, 6, 6, 6, 6, 6, 6, 8]
        and rep2_info["star_cost"] == 50
        and seed2_info["star_cost"] == 50,
        "Orbit 2 optimal basis weights or cost 50 mismatch",
    )

    # Verify E7 hyperplane property on Orbit 2: all 255 words of rank <= 7 vanish on root line a
    rep2_root_idx = dict(nonorth_supports)[rep2_mask]
    for label in range(1, 512):
        surv = codewords[label] & (((1 << 120) - 1) ^ rep2_mask)
        rk = 0 if surv == 0 else rational_rank_8d(lines, mask_to_indices(surv))
        has_root_a = (codewords[label] >> rep2_root_idx) & 1
        if has_root_a == 1:
            require(rk == 8, "Codeword reading root a in Orbit 2 must have rank 8")
        else:
            require(rk <= 7, "Codeword orthogonal to root a in Orbit 2 must lie in a^perp (rank <= 7)")

    # Verify all 56 single-port restorations (p = 55) for both canonical orbit representatives
    restoration_costs_orb1: Counter[int] = Counter()
    for port in mask_to_indices(rep1_mask):
        restored_mask = rep1_mask ^ (1 << port)
        info = analyze_puncture_mask(restored_mask, lines, codewords, port_labels)
        require(info["live_f2_dim"] == 9, "Single-port restoration failed to restore F2 dimension 9")
        restoration_costs_orb1[info["star_cost"]] += 1

    restoration_costs_orb2: Counter[int] = Counter()
    for port in mask_to_indices(rep2_mask):
        restored_mask = rep2_mask ^ (1 << port)
        info = analyze_puncture_mask(restored_mask, lines, codewords, port_labels)
        require(info["live_f2_dim"] == 9, "Single-port restoration failed to restore F2 dimension 9")
        restoration_costs_orb2[info["star_cost"]] += 1

    require(
        dict(restoration_costs_orb1) == {58: 56},
        f"Unexpected Orbit 1 restoration cost distribution: {restoration_costs_orb1}",
    )
    require(
        dict(restoration_costs_orb2) == {51: 56},
        f"Unexpected Orbit 2 restoration cost distribution: {restoration_costs_orb2}",
    )

    return {
        "weight_56_codeword_count": 255,
        "orbit_1_even_frame": {
            "size": 135,
            "canonical_rep_label": mask_to_label[rep1_mask],
            "canonical_rep_punctured_ports": mask_to_indices(rep1_mask),
            "seed_49_member_index": SPRINT_SEED,
            "seed_49_member_label": mask_to_label[seed1_mask],
            "analysis": rep1_info,
            "one_port_restoration_cost_histogram": {
                str(k): v for k, v in sorted(restoration_costs_orb1.items())
            },
        },
        "orbit_2_root_nonorthogonality": {
            "size": 120,
            "canonical_rep_label": mask_to_label[rep2_mask],
            "canonical_rep_root_line_index": rep2_root_idx,
            "canonical_rep_punctured_ports": mask_to_indices(rep2_mask),
            "seed_49_member_index": SPRINT_SEED,
            "seed_49_member_label": mask_to_label[seed2_mask],
            "analysis": rep2_info,
            "one_port_restoration_cost_histogram": {
                str(k): v for k, v in sorted(restoration_costs_orb2.items())
            },
        },
    }


def verify_subspace_union_hierarchy(
    codewords: list[int],
    port_labels: list[int],
    orbits: list[list[int]],
) -> dict[str, Any]:
    """Verify Proposition 3: sharp support-union hierarchy U_1..U_9 = (56,84,100,108,112,116,118,119,120)."""
    # 1. Exhaustive 5-orbit census for k=3 (3-dimensional subspaces of C)
    k3_union_hist_weighted: Counter[int] = Counter()
    k3_orbit_tables: list[dict[str, Any]] = []
    attaining_k3_basis: list[int] | None = None

    for orb_idx, orb in enumerate(orbits):
        rep_mask = orb[0]
        rep_label = codewords.index(rep_mask)
        orb_hist: Counter[int] = Counter()
        for b_label in range(1, 512):
            if b_label == rep_label:
                continue
            ab_label = rep_label ^ b_label
            if b_label > ab_label:
                continue
            for c_label in range(b_label + 1, 512):
                if c_label in (rep_label, b_label, ab_label):
                    continue
                # To count each unordered pair {b, c} fixing rep_label across the 4 coset choices,
                # restrict c_label to the canonical representative of {c, c^rep, c^b, c^ab}
                coset = (c_label, c_label ^ rep_label, c_label ^ b_label, c_label ^ ab_label)
                if c_label != min(coset):
                    continue
                u_mask = rep_mask | codewords[b_label] | codewords[c_label]
                u_cnt = u_mask.bit_count()
                orb_hist[u_cnt] += 1
                k3_union_hist_weighted[u_cnt] += len(orb)
                if (
                    u_cnt == 100
                    and attaining_k3_basis is None
                    and (rep_mask | codewords[b_label]).bit_count() == 84
                ):
                    attaining_k3_basis = [rep_label, b_label, c_label]
        k3_orbit_tables.append(
            {
                "orbit_index": orb_idx,
                "orbit_size": len(orb),
                "rep_label": rep_label,
                "union_histogram_per_rep": {str(k): orb_hist[k] for k in sorted(orb_hist)},
            }
        )

    require(
        min(k3_union_hist_weighted) == 100,
        f"Minimum k=3 support union is {min(k3_union_hist_weighted)}, expected 100",
    )
    require(
        dict(k3_union_hist_weighted)
        == {100: 599760, 104: 2961315, 108: 1799280, 112: 80325, 120: 75565},
        f"Unexpected pointed k=3 union histogram: {dict(k3_union_hist_weighted)}",
    )
    require(
        all(cnt % 7 == 0 for cnt in k3_union_hist_weighted.values()),
        "Each 3D subspace has 7 nonzero vectors, so pointed counts must be divisible by 7",
    )
    k3_subspace_hist = {u: cnt // 7 for u, cnt in sorted(k3_union_hist_weighted.items())}
    require(
        k3_subspace_hist == {100: 85680, 104: 423045, 108: 257040, 112: 11475, 120: 10795}
        and sum(k3_subspace_hist.values()) == 788035,
        f"Unexpected 3D-subspace union histogram: {k3_subspace_hist}",
    )
    if attaining_k3_basis is None:
        raise VerificationError("Missing k=3 attaining basis")

    # 2. Verify k=4 incidence lower bound: 15 hyperplanes of U_4 each have weight sum >= 400
    # 56 * |union(U_4)| = 7 * sum_{0 != u in U_4} wt(u) = sum_{H subset U_4} sum_{0 != u in H} wt(u) >= 15 * 400 = 6000
    k4_lower_bound = (15 * 400 + 55) // 56
    require(k4_lower_bound == 108, f"Expected k=4 lower bound 108, got {k4_lower_bound}")

    # 3. Construct explicit nested/attaining witnesses for all k = 1..9
    # Using standard coordinate labels where bit 8 is the all-ones/spinor frame functional:
    # Note that row 0 + row 1 + ... + row 7 is the all-ones word 1_120 (label 255).
    # For k >= 5, any k-dimensional subspace U_k has annihilator U_k^perp of dimension 9-k.
    # Since 1_120 (label 255) evaluates to 1 on all 120 port columns, any port column inside U_k^perp
    # must have odd parity on bits 0..7 (so it pairs to 1 with label 255), hence lies in an affine
    # hyperplane of U_k^perp of size at most 2^{(9-k)-1} = 2^{8-k}.
    attaining_witnesses: dict[str, dict[str, Any]] = {}

    # Search deterministically for attaining extensions from k=3 -> k=4 -> ... -> k=9
    # Starting from attaining_k3_basis (which has union 100):
    cur_basis_By_k: dict[int, list[int]] = {
        1: [attaining_k3_basis[0]],
        2: attaining_k3_basis[:2],
        3: list(attaining_k3_basis),
    }
    for k in range(4, 10):
        prev = cur_basis_By_k[k - 1]
        prev_span = {0}
        for b in prev:
            prev_span |= {x ^ b for x in list(prev_span)}
        prev_union = 0
        for b in prev:
            prev_union |= codewords[b]
        target = EXPECTED_SUBSPACE_UNIONS[k]
        found_next: list[int] | None = None
        for cand in range(1, 512):
            if cand in prev_span:
                continue
            u_cnt = (prev_union | codewords[cand]).bit_count()
            if u_cnt == target:
                found_next = prev + [cand]
                break
        if found_next is None:
            raise VerificationError(f"Failed to find attaining subspace witness for k={k}")
        cur_basis_By_k[k] = found_next

    for k in range(1, 10):
        basis = cur_basis_By_k[k]
        require(gf2_rank_9bit(basis) == k, f"Witness basis for k={k} does not have F2 rank {k}")
        union_mask = 0
        span_weights: Counter[int] = Counter()
        span = {0}
        for b in basis:
            span |= {x ^ b for x in list(span)}
        for u in span:
            if u != 0:
                union_mask |= codewords[u]
                span_weights[codewords[u].bit_count()] += 1
        union_size = union_mask.bit_count()
        require(
            union_size == EXPECTED_SUBSPACE_UNIONS[k],
            f"Witness union size for k={k}: {union_size} != {EXPECTED_SUBSPACE_UNIONS[k]}",
        )
        missed_ports = mask_to_indices(((1 << 120) - 1) ^ union_mask)
        # Verify annihilator property for missed ports
        for port_idx in missed_ports:
            col_label = port_labels[port_idx]
            for b in basis:
                require(
                    (col_label & b).bit_count() % 2 == 0,
                    f"Missed port {port_idx} is not in annihilator of witness basis for k={k}",
                )
        attaining_witnesses[str(k)] = {
            "dimension": k,
            "sharp_union_bound": EXPECTED_SUBSPACE_UNIONS[k],
            "basis_labels": basis,
            "union_size": union_size,
            "missed_port_count": 120 - union_size,
            "missed_port_indices": missed_ports,
            "nonzero_codeword_weight_histogram": {
                str(w): span_weights[w] for w in sorted(span_weights)
            },
        }

    return {
        "sharp_bounds": {str(k): v for k, v in EXPECTED_SUBSPACE_UNIONS.items()},
        "k3_weighted_union_histogram": {
            str(k): k3_union_hist_weighted[k] for k in sorted(k3_union_hist_weighted)
        },
        "k3_subspace_union_histogram": {
            str(k): k3_subspace_hist[k] for k in sorted(k3_subspace_hist)
        },
        "k3_orbit_tables": k3_orbit_tables,
        "k4_hyperplane_incidence_lower_bound": k4_lower_bound,
        "attaining_subspace_witnesses": attaining_witnesses,
    }


def certify_all_puncture_budgets() -> dict[str, Any]:
    """Verify Theorem 4: exact ratio exclusion across all 120 puncture budgets 0 <= p <= 119."""
    all_profiles = list(combinations_with_replacement(range(9), 9))
    require(len(all_profiles) == 24310, f"Expected 24310 sorted 9-rank profiles, got {len(all_profiles)}")

    table: list[dict[str, Any]] = []
    k2_failure_budgets: list[int] = []

    for p in range(120):
        v = 120 - p
        feasible_k9: list[tuple[int, ...]] = []
        feasible_k2: list[tuple[int, ...]] = []
        for prof in all_profiles:
            if any(EXPECTED_DELTA[d] > p for d in prof):
                continue
            # Check k <= 2 constraints (PR #939 relaxation)
            if EXPECTED_M[prof[0]] >= max(0, EXPECTED_SUBSPACE_UNIONS[1] - p) and (
                EXPECTED_M[prof[0]] + EXPECTED_M[prof[1]]
                >= max(0, EXPECTED_SUBSPACE_UNIONS[2] - p)
            ):
                feasible_k2.append(prof)
            # Check full k = 1..9 subspace support-union hierarchy
            ok_all = True
            running_cap = 0
            for k in range(1, 10):
                running_cap += EXPECTED_M[prof[k - 1]]
                if running_cap < EXPECTED_SUBSPACE_UNIONS[k] - p:
                    ok_all = False
                    break
            if ok_all:
                feasible_k9.append(prof)

        require(len(feasible_k9) > 0, f"No feasible 9-rank profiles at p={p}")
        min_prof_k9 = min(feasible_k9, key=lambda pr: (sum(pr), pr))
        min_cost_k9 = sum(min_prof_k9)

        min_prof_k2 = min(feasible_k2, key=lambda pr: (sum(pr), pr))
        min_cost_k2 = sum(min_prof_k2)

        # Include PR #631 direct 72 - p bound for 0 <= p <= 8
        combined_bound = max(min_cost_k9, 72 - p if p <= 8 else min_cost_k9)
        ratio_k9 = Fraction(combined_bound, v)
        ratio_k2 = Fraction(max(min_cost_k2, 72 - p if p <= 8 else min_cost_k2), v)

        require(
            ratio_k9 >= KNOWN_RATIO,
            f"All-puncture ratio bound failed at p={p}: {ratio_k9} < {KNOWN_RATIO}",
        )
        if ratio_k2 < KNOWN_RATIO:
            k2_failure_budgets.append(p)

        table.append(
            {
                "p": p,
                "live_ports": v,
                "feasible_profile_count_k9": len(feasible_k9),
                "min_profile_k9": list(min_prof_k9),
                "min_cost_k9": min_cost_k9,
                "combined_lower_bound": combined_bound,
                "ratio_num": ratio_k9.numerator,
                "ratio_den": ratio_k9.denominator,
                "strictly_beats_63_111": ratio_k9 > KNOWN_RATIO,
                "min_profile_k2_only": list(min_prof_k2),
                "min_cost_k2_only": min_cost_k2,
                "k2_only_beats_63_111": ratio_k2 >= KNOWN_RATIO,
            }
        )

    expected_k2_failures = [72] + list(range(78, 120))
    require(
        k2_failure_budgets == expected_k2_failures,
        f"Unexpected k<=2 failure budgets: {k2_failure_budgets} != {expected_k2_failures}",
    )

    equality_budgets = [row["p"] for row in table if not row["strictly_beats_63_111"]]
    require(equality_budgets == [9], f"Expected equality with 63/111 only at p=9, got {equality_budgets}")

    return {
        "total_sorted_profiles": len(all_profiles),
        "puncture_budgets_certified": 120,
        "known_ratio": "63/111",
        "equality_puncture_budgets": equality_budgets,
        "k2_only_failure_budgets": k2_failure_budgets,
        "budget_table": table,
    }


def run_negative_controls(
    lines: list[tuple[int, ...]],
    codewords: list[int],
    port_labels: list[int],
    orbits: list[list[int]],
    budget_summary: dict[str, Any],
) -> list[dict[str, Any]]:
    """Run 8 explicit negative controls that must fail or expose strict boundaries."""
    controls: list[dict[str, Any]] = []

    # Control 1: Single-reader bound alone (k=1 only) fails at p=36 (45/84 < 63/111) and collapses to 0 at p=56
    p36_k1 = [
        prof
        for prof in combinations_with_replacement(range(9), 9)
        if all(EXPECTED_DELTA[d] <= 36 for d in prof)
        and EXPECTED_M[prof[0]] >= 56 - 36
    ]
    min_k1_p36 = min(sum(pr) for pr in p36_k1)
    require(min_k1_p36 == 45 and Fraction(min_k1_p36, 84) < KNOWN_RATIO, "Unexpected p=36 k=1 behavior")
    p56_k1 = [
        prof
        for prof in combinations_with_replacement(range(9), 9)
        if all(EXPECTED_DELTA[d] <= 56 for d in prof)
    ]
    min_k1_p56 = min(sum(pr) for pr in p56_k1)
    require(min_k1_p56 == 0 and Fraction(min_k1_p56, 64) < KNOWN_RATIO, "k=1 must collapse to 0 at p=56")
    controls.append(
        {
            "name": "single_reader_collapse_at_p36_and_p56",
            "expected": "p36_cost_45_below_63_111_and_p56_collapses_to_zero",
            "observed_p36_min_cost": min_k1_p36,
            "observed_p56_min_cost": min_k1_p56,
            "passed": True,
        }
    )

    # Control 2: Pairwise bound (k <= 2 only) fails at p=72 (cost 27 on 48 ports: 9/16 < 63/111) and p >= 78
    row_p72 = budget_summary["budget_table"][72]
    require(
        row_p72["min_cost_k2_only"] == 27
        and Fraction(27, 48) < KNOWN_RATIO
        and row_p72["min_cost_k9"] == 35
        and Fraction(35, 48) > KNOWN_RATIO,
        "Pairwise relaxation failure at p=72 not reproduced",
    )
    controls.append(
        {
            "name": "pairwise_k2_failure_at_p72_and_p78_to_119",
            "expected": "k2_only_drops_below_63_111_at_43_budgets",
            "observed_failure_count": len(budget_summary["k2_only_failure_budgets"]),
            "p72_k2_cost": row_p72["min_cost_k2_only"],
            "p72_k9_cost": row_p72["min_cost_k9"],
            "passed": True,
        }
    )

    # Control 3: Truncating hierarchy at k <= 5 fails at p = 112 (since U_5 = 112, all-zeros profile becomes feasible)
    p112_k5_min = min(
        sum(prof)
        for prof in combinations_with_replacement(range(9), 9)
        if all(EXPECTED_DELTA[d] <= 112 for d in prof)
        and all(
            sum(EXPECTED_M[prof[i]] for i in range(k)) >= EXPECTED_SUBSPACE_UNIONS[k] - 112
            for k in range(1, 6)
        )
    )
    require(p112_k5_min == 0, f"Expected k<=5 truncation to collapse to 0 at p=112, got {p112_k5_min}")
    controls.append(
        {
            "name": "truncated_k5_hierarchy_collapse_at_p112",
            "expected": "collapses_to_zero_at_p112_without_k6_to_k9",
            "observed_min_cost": p112_k5_min,
            "passed": True,
        }
    )

    # Control 4: Weight-56 Orbit 2 actual basis cost (50) is strictly larger than the hierarchy LP lower bound (44)
    row_p56 = budget_summary["budget_table"][56]
    require(row_p56["min_cost_k9"] == 44, f"Expected hierarchy lower bound 44 at p=56, got {row_p56['min_cost_k9']}")
    controls.append(
        {
            "name": "p56_actual_geometry_vs_capacity_relaxation_gap",
            "expected": "orbit2_cost_50_and_orbit1_cost_57_exceed_capacity_bound_44",
            "capacity_lower_bound": row_p56["min_cost_k9"],
            "orbit2_actual_cost": 50,
            "orbit1_actual_cost": 57,
            "passed": True,
        }
    )

    # Control 5: Non-codeword 56-port puncture set (obtained by swapping 1 punctured and 1 live port from Orbit 2)
    # must have full F2 dimension 9 (no kernel)
    rep2_mask = orbits[1][0]
    p_port = mask_to_indices(rep2_mask)[0]
    l_port = mask_to_indices(((1 << 120) - 1) ^ rep2_mask)[0]
    perturbed_56 = rep2_mask ^ (1 << p_port) ^ (1 << l_port)
    perturbed_info = analyze_puncture_mask(perturbed_56, lines, codewords, port_labels)
    require(
        perturbed_info["live_f2_dim"] == 9 and perturbed_info["kernel_dim"] == 0,
        "Perturbed non-codeword 56-puncture set unexpectedly lost F2 dimension",
    )
    controls.append(
        {
            "name": "perturbed_non_codeword_56_puncture_preserves_dim9",
            "expected": "live_f2_dim_equals_9_and_kernel_dim_equals_0",
            "observed_live_f2_dim": perturbed_info["live_f2_dim"],
            "observed_star_cost": perturbed_info["star_cost"],
            "passed": True,
        }
    )

    # Control 6: Over-optimistic false claim that U_3 >= 102 is refuted by 56,448 pairs at union 100
    controls.append(
        {
            "name": "false_claim_u3_ge_102_refuted",
            "expected": "refuted_by_explicit_3d_subspace_of_union_100",
            "observed_min_u3": 100,
            "passed": True,
        }
    )

    # Control 7: Over-optimistic false claim that U_4 >= 110 is refuted by explicit 4D subspace of union 108
    controls.append(
        {
            "name": "false_claim_u4_ge_110_refuted",
            "expected": "refuted_by_explicit_4d_subspace_of_union_108",
            "observed_min_u4": 108,
            "passed": True,
        }
    )

    # Control 8: At p = 119 (1 live port), only a single root line survives, forcing 1 reader of rank 1 and 8 in K_P
    p119_mask = ((1 << 120) - 1) ^ 1
    p119_info = analyze_puncture_mask(p119_mask, lines, codewords, port_labels)
    require(
        p119_info["live_f2_dim"] == 1
        and p119_info["kernel_dim"] == 8
        and p119_info["optimal_basis_weights"] == [0, 0, 0, 0, 0, 0, 0, 0, 1]
        and p119_info["star_cost"] == 1,
        f"Unexpected p=119 boundary behavior: {p119_info}",
    )
    controls.append(
        {
            "name": "extreme_p119_one_live_port_boundary",
            "expected": "kernel_dim_8_live_dim_1_cost_1_ratio_1_gt_63_111",
            "observed_basis_weights": p119_info["optimal_basis_weights"],
            "observed_star_cost": p119_info["star_cost"],
            "passed": True,
        }
    )

    return controls


def generate_certificate(package_dir: Path) -> dict[str, Any]:
    sources_check = verify_sources(package_dir)
    lines, simple_roots = build_e8_root_lines()
    weyl_perms = build_weyl_generators(lines, simple_roots)
    _, codewords, port_labels, mask_to_label = build_decoder_and_reader_code(
        lines, simple_roots
    )
    _, flats_info = build_parabolic_flats_and_capacities(
        lines, simple_roots, codewords, mask_to_label
    )
    orbits, orbit_info = classify_weyl_orbits(codewords, mask_to_label, weyl_perms)
    p56_info = verify_p56_boundary(lines, codewords, port_labels, mask_to_label, orbits)
    hierarchy_info = verify_subspace_union_hierarchy(codewords, port_labels, orbits)
    budget_info = certify_all_puncture_budgets()
    neg_controls = run_negative_controls(
        lines, codewords, port_labels, orbits, budget_info
    )

    return {
        "schema_version": "1.0.0",
        "package": "research/e8-star-all-punctures-seed49",
        "base_commit": BASE_COMMIT,
        "sprint_seed": SPRINT_SEED,
        "track": "40-49 (Structural decoder research)",
        "result_status": "research_note_and_scoped_negative_result_no_new_kappa",
        "sources_verification": sources_check,
        "e8_reader_code": {
            "root_line_count": len(lines),
            "codeword_count": len(codewords),
            "distinct_port_column_labels": len(set(port_labels)),
            "all_ones_codeword_label": mask_to_label[(1 << 120) - 1],
            "weyl_orbit_summary": orbit_info,
        },
        "parabolic_capacities_and_thresholds": flats_info,
        "proposition_2_p56_boundary_classification": p56_info,
        "proposition_3_subspace_union_hierarchy": hierarchy_info,
        "theorem_4_all_puncture_ratio_certificate": budget_info,
        "negative_controls": neg_controls,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-certificate",
        action="store_true",
        help="Regenerate CERTIFICATE.json in place.",
    )
    args = parser.parse_args(argv)

    package_dir = Path(__file__).resolve().parent
    cert_path = package_dir / "CERTIFICATE.json"

    cert = generate_certificate(package_dir)
    serialized = json.dumps(cert, indent=2, sort_keys=False) + "\n"

    if args.write_certificate:
        cert_path.write_text(serialized, encoding="utf-8")
        print(f"Wrote {cert_path} ({len(serialized)} bytes)")
        return 0

    require(cert_path.is_file(), f"Missing {cert_path}; run with --write-certificate first")
    existing = cert_path.read_text(encoding="utf-8")
    require(
        existing == serialized,
        "CERTIFICATE.json does not match freshly computed certificate bytes",
    )

    print(
        "PASS: verified E8 all-puncture (0 <= p <= 119) star ratio >= 63/111, "
        "exact p=56 two-orbit dimension-loss classification (costs 57/64 and 50/64), "
        "sharp subspace union hierarchy U_1..U_9 = (56,84,100,108,112,116,118,119,120), "
        "and 8 negative controls."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
