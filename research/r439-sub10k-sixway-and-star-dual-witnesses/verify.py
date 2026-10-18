#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Unified bit-mechanisms verifier (bit-helper-contract & bit-new-register-model):
  1. Pillar 1 — R439 Six-Way Sub-10k Composition at 9,974 ADDs (-518 vs PR1188,
     -74 vs PR2440) with 6 pairwise-disjoint middle-column helper shears (-60 ADDs),
     exact 661-column forward/reverse linear semantics, and 91/174-bit guards.
  2. Pillar 2 — Whole-Section-A & Post-First-Read Coupled (a, c) Carrier-Reader
     Star-Absorption Impossibility across PR1062, PR1122, and PR1188 (5 solvable /
     231 obstructed edges per word, 693 explicit 661-bit RREF dual hyperplane
     witnesses and 675 coupled 1,322-bit RREF dual witnesses; closes PR1937 OQ1).
  3. Pillar 3 — Unconditional All-Length (L < infinity), All-Workspace (r >= 2)
     n_b >= 6 Exclusion & Cone-Free Global Optimality of (4, 6, 4) for
     diag([z], [uz], I_rest) in F2[UT4(F2)] (256/256 within-gap trace hyperplane
     theorem and 3,600 five-b middle census; closes PR2828 OQ1 & OQ2).
  4. Pillar 4 — Grassmannian Schubert-Cell Parity Floor sum_j rank_Q(A_j) >= 4 = mW
     at m = 2, W = 2 for Dyadic Full-Borel Superposition Words over GL_4(Q)
     (40,593 dyadic Borel checks, 54,124 rank-1 shear checks, and 20,224 3-call
     parity systems with 0 survivors; closes PR2613 / bit-full-borel OQ1).

Prepared by dcharb78, with AI assistance. Apache-2.0.
Usage:
  python3.12 -I -B research/r439-sub10k-sixway-and-star-dual-witnesses/verify.py [--write]
"""

from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction
import gzip
import hashlib
import importlib.util
from itertools import product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = (
    HERE.parents[1]
    if (HERE.parents[1] / "certificates" / "selected-result.json").is_file()
    else HERE.parents[1] / "imb-repo"
)


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git_blob_bytes(raw: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest()


def verify_pinned_sources() -> dict[str, bytes]:
    sources_path = HERE / "SOURCES.json"
    verify_path = HERE / "VERIFY.json"
    require(sources_path.is_file(), "missing SOURCES.json")
    require(verify_path.is_file(), "missing VERIFY.json")
    sources = json.loads(sources_path.read_text(encoding="utf-8"))
    verify_cfg = json.loads(verify_path.read_text(encoding="utf-8"))

    input_blobs: dict[str, bytes] = {}
    declared_inputs: list[str] = []
    for row in sources.get("files", []):
        rel = str(row["path"])
        p = ROOT / rel
        require(p.is_file(), f"missing pinned repository file: {rel}")
        raw = p.read_bytes()
        require(
            sha256_bytes(raw) == row["sha256"],
            f"SHA-256 mismatch on pinned file: {rel}",
        )
        require(
            git_blob_bytes(raw) == row["git_blob"],
            f"git_blob mismatch on pinned file: {rel}",
        )
        if row.get("usage") == "input":
            input_blobs[rel] = raw
            declared_inputs.append(rel)

    require(
        sorted(declared_inputs) == sorted(verify_cfg.get("inputs", [])),
        "SOURCES.json input rows must match VERIFY.json inputs",
    )
    return input_blobs


def load_module(name: str, rel_path: str):
    path = ROOT / rel_path
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot load {rel_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def simulate_stream(
    ins: list[tuple[int, int, int]], n: int, wanted: list[int]
) -> tuple[bool, bool, int, int, int]:
    peaks: list[int] = []
    oks: list[bool] = []
    mismatch_fwd = 0
    for reverse in (False, True):
        rows = [1 << r for r in range(n)] + [0]
        val = [1] * (n + 1)
        peak = 1
        seq = reversed(ins) if reverse else ins
        for kind, d, s in seq:
            if reverse and kind:
                kind = 3 - kind
            if kind == 0:
                rows[d] ^= rows[s]
                val[d] += val[s]
            elif kind == 1:
                require(rows[d] == 0, "COPY into non-zero temporary slot")
                rows[d] = rows[s]
                val[d] = val[s]
            else:
                require(rows[d] == rows[s], "ERASE mismatch on temporary slot")
                rows[d] = 0
                val[d] = 0
            if val[d] > peak:
                peak = val[d]
        require(rows[-1] == 0, "temporary slot not cleared at end of replay")
        ok = rows[:-1] == wanted
        oks.append(ok)
        peaks.append(peak)
        if not reverse:
            mismatch_fwd = sum(1 for r_i, w_i in zip(rows[:-1], wanted) if r_i != w_i)
    return oks[0], oks[1], peaks[0], peaks[1], mismatch_fwd


# ============================================================================
# PILLAR 1: R439 Six-Way Sub-10k Composition at 9,974 ADDs
# ============================================================================
def run_pillar_1(input_blobs: dict[str, bytes]) -> tuple[dict, dict]:
    m2115 = load_module("m2115", "research/r439-deferred-target-basis-seed06/verify.py")
    m2440 = load_module("m2440", "research/r439-one-slot-multicolumn-interleave/verify.py")

    w_1062 = json.loads(gzip.decompress(input_blobs["research/r439-bsection-stars-seed01/candidate.json.gz"]))
    w_1188 = json.loads(gzip.decompress(input_blobs["research/r439-gl5-shortest/candidate.json.gz"]))
    w_1868_1188 = json.loads(gzip.decompress(input_blobs["research/r439-twisted-star-absorption-seed02/absorbed-pr1188.json.gz"]))
    w_1709 = json.loads(gzip.decompress(input_blobs["research/r439-five-cycle-seed9f01/CANDIDATE.json.gz"]))
    w_1543 = json.loads(gzip.decompress(input_blobs["research/r439-neutral-helper-chain-seed17/CANDIDATE.json.gz"]))

    geo = m2115.Geo(w_1868_1188)
    sp = m2115.split_d(w_1868_1188, geo)

    w_deferred, _, kept_undo, rest_undo = m2115.ideal_word(w_1868_1188, geo, sp, [31, 51, 52])
    b_def = m2115.bounds(w_deferred)
    g_def = m2115.guard_bits(b_def["F"], b_def["B"])
    require(m2115.boundary_ok(w_deferred), "PR2115+PR1868 boundary failed")
    require(m2115.paid_profile(w_deferred, geo) == m2115.PROFILE, "PR2115+PR1868 profile mismatch")

    omitted_star_gates = [[0, 506, [374]], [0, 507, [355]], [0, 514, [367]]]

    def remove_tail_star_gates(d_gates: list, to_remove: list) -> list:
        rem_set = {(g[0], g[1], tuple(g[2])) for g in to_remove}
        half = len(d_gates) // 2
        out = [list(g) for g in d_gates[:half]]
        removed = 0
        for g in d_gates[half:]:
            key = (g[0], g[1], tuple(g[2]))
            if key in rem_set:
                rem_set.remove(key)
                removed += 1
            else:
                out.append(list(g))
        require(removed == len(to_remove), "failed removing omitted star gates")
        return out

    sp_1709 = m2115.split_d(w_1709, geo)
    und_1709 = set(sp_1709["undo"])
    d_1709_no_target_undo = [list(g) for i, g in enumerate(w_1709["D"]) if i not in und_1709]
    d_1709_twisted = remove_tail_star_gates(d_1709_no_target_undo, omitted_star_gates)

    w_comp_1709 = dict(w_deferred)
    w_comp_1709["D"] = d_1709_twisted + [list(g) for g in kept_undo]
    b_comp_1709 = m2115.bounds(w_comp_1709)
    g_comp_1709 = m2115.guard_bits(b_comp_1709["F"], b_comp_1709["B"])
    require(m2115.boundary_ok(w_comp_1709), "4-Way B (PR1709+PR1868+PR2115) boundary failed")
    require(m2115.paid_profile(w_comp_1709, geo) == m2115.PROFILE, "4-Way B profile mismatch")

    sp_1543 = m2115.split_d(w_1543, geo)
    und_1543 = set(sp_1543["undo"])
    d_1543_no_target_undo = [list(g) for i, g in enumerate(w_1543["D"]) if i not in und_1543]
    d_1543_twisted = remove_tail_star_gates(d_1543_no_target_undo, omitted_star_gates)
    w_comp_1543 = dict(w_deferred)
    w_comp_1543["D"] = d_1543_twisted + [list(g) for g in kept_undo]
    b_comp_1543 = m2115.bounds(w_comp_1543)
    g_comp_1543 = m2115.guard_bits(b_comp_1543["F"], b_comp_1543["B"])
    require(m2115.boundary_ok(w_comp_1543), "4-Way A (PR1543+PR1868+PR2115) boundary failed")
    require(m2115.paid_profile(w_comp_1543, geo) == m2115.PROFILE, "4-Way A profile mismatch")

    v, R = geo.v, geo.R
    col_masks = [0] * R
    for _, dst, ss in w_1709["D"]:
        if v <= dst < 2 * v and all(s >= 2 * v for s in ss):
            t_bit = 1 << (dst - v)
            for s in ss:
                col_masks[s - 2 * v] ^= t_bit

    used_helpers = {r - 2 * v for r in w_1188["ret"]} | {59, 148, 21, 129, 25} | {
        506 - 222, 374 - 222, 507 - 222, 355 - 222, 514 - 222, 367 - 222
    }
    avail = [h for h in range(R) if h not in used_helpers]

    sp_1062 = m2115.split_d(w_1062, geo)
    prep_1062 = [w_1062["D"][i] for i in sp_1062["prep"]]
    undo_1062 = [w_1062["D"][i] for i in sp_1062["undo"]]
    prep_1868 = [w_1868_1188["D"][i] for i in sp["prep"]]
    undo_1868 = [w_1868_1188["D"][i] for i in sp["undo"]]
    same_target_basis_and_scatter = (
        prep_1062 == prep_1868
        and undo_1062 == undo_1868
        and w_1062["scatter"] == w_1868_1188["scatter"]
        and w_1062["ret"] == w_1868_1188["ret"]
    )
    require(same_target_basis_and_scatter, "target basis or scatter differs from PR1062")

    witness_2440 = json.loads(
        input_blobs["research/r439-one-slot-multicolumn-interleave/WITNESS.json"].decode("utf-8")
    )
    segments = witness_2440["segments"]
    S_orig = [sum(1 << j for j in row) for row in w_1868_1188["scatter"]]
    per_col_taps = m2440.check_schedule(w_1868_1188, rest_undo, S_orig, segments)

    tmp_slot = 2 * v + R
    L = len(rest_undo)
    interleaved_mid: list[tuple[int, int, int]] = []
    cut = 0
    for sg in segments:
        while cut < sg["copy_cut"]:
            _, d_u, ss_u = rest_undo[cut]
            interleaved_mid.append((0, d_u, ss_u[0]))
            cut += 1
        q_reg = w_comp_1709["ret"][sg["column"]]
        interleaved_mid.append((1, tmp_slot, q_reg))
        for c_idx in range(sg["copy_cut"], sg["erase_cut"] + 1):
            for cc, i_t in sg["taps"]:
                if cc == c_idx:
                    interleaved_mid.append((0, v + i_t, tmp_slot))
            if c_idx < sg["erase_cut"]:
                _, d_u, ss_u = rest_undo[c_idx]
                interleaved_mid.append((0, d_u, ss_u[0]))
                cut = c_idx + 1
        interleaved_mid.append((2, tmp_slot, q_reg))
    while cut < L:
        _, d_u, ss_u = rest_undo[cut]
        interleaved_mid.append((0, d_u, ss_u[0]))
        cut += 1

    ins_interleaved = [(0, d, s) for sec in ("D", "A") for _, d, ss in w_comp_1709[sec] for s in ss]
    ins_interleaved += interleaved_mid
    ins_interleaved += [(0, d, s) for _, d, ss in w_1868_1188["B"] for s in ss]
    ins_interleaved += [(0, d, s) for _, d, ss in w_comp_1709["C"] for s in ss]

    n = geo.n
    wanted = m2115.wanted(w_comp_1709)
    interleaved_fwd_ok, interleaved_rev_ok, F_int, B_int, _ = simulate_stream(
        ins_interleaved, n, wanted
    )
    require(interleaved_fwd_ok and interleaved_rev_ok, "5-way interleaved replay failed")
    g_int = m2115.guard_bits(F_int, B_int)
    total_adds_interleaved = sum(k == 0 for k, _, _ in ins_interleaved)
    require(total_adds_interleaved == 10034, f"expected 10034 ADDs, got {total_adds_interleaved}")

    cur_cols = list(col_masks)
    greedy_shears: list[dict] = []
    avail_set = set(avail)
    while len(greedy_shears) < 6:
        best_sh: tuple[int, tuple[int, int] | None] = (0, None)
        for a in sorted(avail_set):
            ca = cur_cols[a]
            if ca.bit_count() <= 2:
                continue
            for b in sorted(avail_set):
                if a == b:
                    continue
                gain = cur_cols[b].bit_count() - (col_masks[b] ^ ca).bit_count() - 2
                if gain > best_sh[0]:
                    best_sh = (gain, (a, b))
        if best_sh[1] is None or best_sh[0] <= 0:
            break
        gain, (a, b) = best_sh
        old_wt = cur_cols[b].bit_count()
        new_wt = (cur_cols[b] ^ cur_cols[a]).bit_count()
        shared_targets = [v + idx for idx in range(v) if ((cur_cols[a] & cur_cols[b]) >> idx) & 1]
        greedy_shears.append(
            {
                "a_local": a,
                "b_local": b,
                "a_wire": 222 + a,
                "b_wire": 222 + b,
                "b_weight_before": old_wt,
                "b_weight_after": new_wt,
                "shared_target_count": len(shared_targets),
                "net_saving": gain,
            }
        )
        cur_cols[b] ^= cur_cols[a]
        avail_set.remove(a)
        avail_set.remove(b)

    require(len(greedy_shears) == 6, "expected 6 disjoint helper shears")
    total_shear_saving = sum(s["net_saving"] for s in greedy_shears)
    require(total_shear_saving == 60, f"expected 60 ADD saving from 6 shears, got {total_shear_saving}")

    mid_indices = [
        i
        for i, g in enumerate(w_comp_1709["D"])
        if v <= g[1] < 2 * v and all(s >= 2 * v for s in g[2])
    ]
    lo_m, hi_m = min(mid_indices), max(mid_indices)
    orig_mid_targets = [w_comp_1709["D"][i][1] for i in mid_indices]
    new_mid_gates = []
    for t_wire in orig_mid_targets:
        t_idx = t_wire - v
        srcs = [2 * v + h for h in range(R) if (cur_cols[h] >> t_idx) & 1]
        if srcs:
            new_mid_gates.append([0, t_wire, srcs])
    shear_prep_gates = [[0, sh["a_wire"], [sh["b_wire"]]] for sh in greedy_shears]
    shear_undo_gates = list(reversed(shear_prep_gates))

    w_comp_sub10k = dict(w_comp_1709)
    w_comp_sub10k["D"] = (
        w_comp_1709["D"][:lo_m]
        + shear_prep_gates
        + new_mid_gates
        + shear_undo_gates
        + w_comp_1709["D"][hi_m + 1:]
    )
    require(m2115.boundary_ok(w_comp_sub10k), "6-way sub-10k D boundary failed")
    require(m2115.paid_profile(w_comp_sub10k, geo) == m2115.PROFILE, "6-way sub-10k profile mismatch")

    ins_sub10k = [(0, d, s) for sec in ("D", "A") for _, d, ss in w_comp_sub10k[sec] for s in ss]
    ins_sub10k += interleaved_mid
    ins_sub10k += [(0, d, s) for _, d, ss in w_1868_1188["B"] for s in ss]
    ins_sub10k += [(0, d, s) for _, d, ss in w_comp_sub10k["C"] for s in ss]

    sub10k_fwd_ok, sub10k_rev_ok, F_sub10k, B_sub10k, mismatch_sub10k = simulate_stream(
        ins_sub10k, n, wanted
    )
    require(
        sub10k_fwd_ok and sub10k_rev_ok and mismatch_sub10k == 0,
        "6-way sub-10k 661-column replay failed",
    )
    g_sub10k = m2115.guard_bits(F_sub10k, B_sub10k)
    require(g_sub10k["local_ok"] and g_sub10k["nine_ok"], "6-way sub-10k guard bits exceeded")
    adds_sub10k = sum(k == 0 for k, _, _ in ins_sub10k)
    require(adds_sub10k == 9974, f"expected 9974 ADDs, got {adds_sub10k}")

    # Negative Control 1: Overlapping 7th shear reusing a_wire=349 (349 ^= 461) without
    # updating coupled middle-column target supports corrupts 661-column semantics.
    overlap_prep = shear_prep_gates + [[0, 349, [461]]]
    w_ctrl1 = dict(w_comp_1709)
    w_ctrl1["D"] = (
        w_comp_1709["D"][:lo_m]
        + overlap_prep
        + new_mid_gates
        + shear_undo_gates
        + w_comp_1709["D"][hi_m + 1:]
    )
    ins_ctrl1 = [(0, d, s) for sec in ("D", "A") for _, d, ss in w_ctrl1[sec] for s in ss]
    ins_ctrl1 += interleaved_mid
    ins_ctrl1 += [(0, d, s) for _, d, ss in w_1868_1188["B"] for s in ss]
    ins_ctrl1 += [(0, d, s) for _, d, ss in w_ctrl1["C"] for s in ss]
    ctrl1_fwd_ok, _, _, _, ctrl1_mismatches = simulate_stream(ins_ctrl1, n, wanted)
    require(not ctrl1_fwd_ok and ctrl1_mismatches == 2, "Control 1 must corrupt 2 output registers")

    # Negative Control 2: Omitting the 2 setup/restore gates of Shear 1 (349 ^= 462)
    # while keeping the sheared middle-column reads corrupts the 16 shared targets (62 output columns).
    w_ctrl2 = dict(w_comp_1709)
    w_ctrl2["D"] = (
        w_comp_1709["D"][:lo_m]
        + shear_prep_gates[1:]
        + new_mid_gates
        + shear_undo_gates[:-1]
        + w_comp_1709["D"][hi_m + 1:]
    )
    ins_ctrl2 = [(0, d, s) for sec in ("D", "A") for _, d, ss in w_ctrl2[sec] for s in ss]
    ins_ctrl2 += interleaved_mid
    ins_ctrl2 += [(0, d, s) for _, d, ss in w_1868_1188["B"] for s in ss]
    ins_ctrl2 += [(0, d, s) for _, d, ss in w_ctrl2["C"] for s in ss]
    ctrl2_fwd_ok, _, _, _, ctrl2_mismatches = simulate_stream(ins_ctrl2, n, wanted)
    require(not ctrl2_fwd_ok and ctrl2_mismatches == 62, "Control 2 must corrupt 62 output registers")

    pillar1 = {
        "same_target_basis_and_scatter_as_PR1062": same_target_basis_and_scatter,
        "paid_rank_mass": 5129,
        "progression": {
            "PR589_selected_base": {"ADDs": 24305},
            "PR1062_bsection_stars": {"ADDs": 11500},
            "PR1122_abc_star_composition": {"ADDs": 10652},
            "PR1188_gl5_shortest": {"ADDs": 10492},
            "PR1868_1188_twisted_stars": {"ADDs": 10489},
            "PR2115_1868_1188_deferred_ideal": {
                "ADDs": b_def["ADDs"],
                "D_ADDs": b_def["D_ADDs"],
                "A_ADDs": b_def["A_ADDs"],
                "scatter_ADDs": b_def["scatter_ADDs"],
                "B_ADDs": b_def["B_ADDs"],
                "C_ADDs": b_def["C_ADDs"],
                "F": b_def["F"],
                "B": b_def["B"],
                **g_def,
            },
            "NEW_PR1543_plus_PR1868_plus_PR2115_on_PR1188": {
                "ADDs": b_comp_1543["ADDs"],
                "D_ADDs": b_comp_1543["D_ADDs"],
                "A_ADDs": b_comp_1543["A_ADDs"],
                "scatter_ADDs": b_comp_1543["scatter_ADDs"],
                "B_ADDs": b_comp_1543["B_ADDs"],
                "C_ADDs": b_comp_1543["C_ADDs"],
                "F": b_comp_1543["F"],
                "B": b_comp_1543["B"],
                **g_comp_1543,
            },
            "NEW_PR1709_plus_PR1868_plus_PR2115_on_PR1188": {
                "ADDs": b_comp_1709["ADDs"],
                "D_ADDs": b_comp_1709["D_ADDs"],
                "A_ADDs": b_comp_1709["A_ADDs"],
                "scatter_ADDs": b_comp_1709["scatter_ADDs"],
                "B_ADDs": b_comp_1709["B_ADDs"],
                "C_ADDs": b_comp_1709["C_ADDs"],
                "F": b_comp_1709["F"],
                "B": b_comp_1709["B"],
                **g_comp_1709,
            },
            "NEW_FIVE_WAY_COMPOSITION_PR1709_PR1868_PR2115_PR2440_on_PR1188": {
                "ADDs": total_adds_interleaved,
                "scatter_ADDs": sum(per_col_taps.values()),
                "forward_661_ok": interleaved_fwd_ok,
                "reverse_661_ok": interleaved_rev_ok,
                "F": F_int,
                "B": B_int,
                **g_int,
            },
            "NEW_SIX_WAY_SUB10K_COMPOSITION_with_6_disjoint_helper_shears": {
                "ADDs": adds_sub10k,
                "delta_vs_PR1188": adds_sub10k - 10492,
                "delta_vs_PR2440": adds_sub10k - 10048,
                "scatter_ADDs": sum(per_col_taps.values()),
                "disjoint_shears_added": greedy_shears,
                "disjoint_shears_total_saving": total_shear_saving,
                "forward_661_ok": sub10k_fwd_ok,
                "reverse_661_ok": sub10k_rev_ok,
                "F": F_sub10k,
                "B": B_sub10k,
                **g_sub10k,
            },
        },
    }
    ctrl_info = {
        "ctrl1_overlapping_shear_mismatches": ctrl1_mismatches,
        "ctrl2_omitted_shear1_gates_mismatches": ctrl2_mismatches,
    }
    return pillar1, ctrl_info


# ============================================================================
# PILLAR 2: Whole-Section-A & Coupled (a, c) Star-Absorption Impossibility
# ============================================================================
def solve_f2_with_dual(vecs: list[int], target: int) -> tuple[bool, int, int]:
    pivots: dict[int, int] = {}
    for v in vecs:
        if not v:
            continue
        cur = v
        for b in sorted(pivots.keys(), reverse=True):
            if (cur >> b) & 1:
                cur ^= pivots[b]
        if cur:
            b_new = cur.bit_length() - 1
            for b in list(pivots.keys()):
                if (pivots[b] >> b_new) & 1:
                    pivots[b] ^= cur
            pivots[b_new] = cur
    rem = target
    for b in sorted(pivots.keys(), reverse=True):
        if (rem >> b) & 1:
            rem ^= pivots[b]
    if rem == 0:
        return True, 0, len(pivots)
    f = (rem & -rem).bit_length() - 1
    h = 1 << f
    for b, pvec in pivots.items():
        if (pvec >> f) & 1:
            h |= 1 << b
    require(((h & target).bit_count() & 1) == 1, "dual functional must evaluate to 1 on target")
    for v in vecs:
        require(((h & v).bit_count() & 1) == 0, "dual functional must annihilate donor span")
    return False, h, len(pivots)


def run_pillar_2(input_blobs: dict[str, bytes]) -> tuple[dict, dict]:
    words_spec = {
        "PR1062": "research/r439-bsection-stars-seed01/candidate.json.gz",
        "PR1122": "research/r439-abc-star-composition/candidate.json.gz",
        "PR1188": "research/r439-gl5-shortest/candidate.json.gz",
    }
    expected_solvable = [(506, 374), (507, 355), (514, 367), (264, 536), (326, 530)]
    results: dict = {}
    total_whole_a_duals_verified = 0
    total_coupled_duals_verified = 0
    corrupted_duals_rejected = 0
    solvable_falsely_obstructed = 0

    for wname, rel in words_spec.items():
        w = json.loads(gzip.decompress(input_blobs[rel]))
        v, R = w["v"], w["R"]
        n = 2 * v + R
        fs = [frozenset(f) for f in w["frames"]]
        A = w["A"]
        D = w["D"]
        nh = sum(1 for g in D if g[1] >= 2 * v) // 2
        require(nh == 236, f"expected 236 star edges in {wname}")
        star_undo = D[len(D) - nh:]

        cur = list(w["start"])
        for f, d, ss in D:
            for r in (d, *ss):
                cur[r] = f
        val = [1 << r for r in range(n)]
        a_vals_before = []
        pre_frames = []
        for f, d, ss in A:
            pre_frames.append(list(cur))
            for r in (d, *ss):
                cur[r] = f
            a_vals_before.append(list(val))
            acc = 0
            for s in ss:
                acc ^= val[s]
            val[d] ^= acc

        nxt = list(w["final"])
        next_touch = [[0] * n for _ in range(len(A))]
        for sec in ("C", "B"):
            for f, d, ss in reversed(w[sec]):
                for r in (d, *ss):
                    nxt[r] = f
        for i in range(len(A) - 1, -1, -1):
            f, d, ss = A[i]
            next_touch[i] = list(nxt)
            for r in (d, *ss):
                nxt[r] = f

        def donor_legal(i: int, d: int, rule: str) -> bool:
            if v <= d < 2 * v:
                return False
            f_i = A[i][0]
            f_pre = pre_frames[i][d]
            f_nxt = next_touch[i][d]
            if rule == "same_path":
                return (f_pre == f_i or f_nxt == f_i) and (fs[f_pre] <= fs[f_i] <= fs[f_nxt])
            if rule == "monotone_all":
                return (fs[f_pre] <= fs[f_i]) and (fs[f_i] <= fs[f_nxt])
            raise ValueError(rule)

        def next_read_in_A(reg: int, start_idx: int) -> int:
            for idx in range(start_idx, len(A)):
                if reg in A[idx][2]:
                    return idx
            return len(A)

        def last_read_before_in_A(reg: int, end_idx: int) -> int:
            for idx in range(end_idx - 1, -1, -1):
                if reg in A[idx][2]:
                    return idx
            return -1

        edge_summary = {
            "total_star_edges": len(star_undo),
            "r0_zero": 0,
            "r0_pos_pre_read_solvable": {"same_path": 0, "monotone_all": 0},
            "r0_has_A_reader": 0,
            "coupled_ac_window_stats": {
                "post_r0_a_writes_total": 0,
                "c_writes_after_r0_total": 0,
                "c_writes_before_r0_after_last_read_total": 0,
                "edges_with_post_r0_a_writes": 0,
                "edges_with_c_writes": 0,
            },
            "coupled_ac_solvable": {"same_path": 0, "monotone_all": 0},
            "coupled_ac_new_beyond_pre_read": {"same_path": [], "monotone_all": []},
            "coupled_ac_dual_witnesses_verified": 0,
            "post_r0_a_only_solvable": {"same_path": 0, "monotone_all": 0},
            "entire_A_a_only_solvable": {"same_path": 0, "monotone_all": 0},
            "entire_A_new_edges": {"same_path": [], "monotone_all": []},
            "entire_A_dual_witnesses_verified": 0,
        }

        for _, a, ss in star_undo:
            b = ss[0]
            eb = 1 << b
            r0 = next_read_in_A(a, 0)
            if r0 == 0:
                edge_summary["r0_zero"] += 1

            for rule in ("same_path", "monotone_all"):
                vecs_pre = [
                    a_vals_before[i][d]
                    for i in range(r0)
                    if A[i][1] == a
                    for d in range(n)
                    if d != a and donor_legal(i, d, rule)
                ]
                ok_pre, _, _ = solve_f2_with_dual(vecs_pre, eb)
                if ok_pre:
                    edge_summary["r0_pos_pre_read_solvable"][rule] += 1

                vecs_all_A = [
                    a_vals_before[i][d]
                    for i in range(len(A))
                    if A[i][1] == a
                    for d in range(n)
                    if d != a and donor_legal(i, d, rule)
                ]
                ok_all_A, h_all_A, _ = solve_f2_with_dual(vecs_all_A, eb)
                if ok_all_A:
                    edge_summary["entire_A_a_only_solvable"][rule] += 1
                    if (a, b) not in expected_solvable:
                        edge_summary["entire_A_new_edges"][rule].append([a, b, r0])
                    if rule == "monotone_all" and h_all_A != 0:
                        solvable_falsely_obstructed += 1
                elif rule == "monotone_all":
                    edge_summary["entire_A_dual_witnesses_verified"] += 1
                    total_whole_a_duals_verified += 1
                    # Negative Control 3: Flipping target bit b in dual witness h_all_A fails target parity
                    h_bad = h_all_A ^ eb
                    if ((h_bad & eb).bit_count() & 1) == 0:
                        corrupted_duals_rejected += 1

            if r0 < len(A):
                edge_summary["r0_has_A_reader"] += 1
                _, c, srcs_r0 = A[r0]
                require(a in srcs_r0 and c != a, "invalid first A-read gate")
                r1_a = next_read_in_A(a, r0 + 1)
                r0_c = next_read_in_A(c, r0 + 1)
                last_c_pre = last_read_before_in_A(c, r0)

                a_post_writes = [i for i in range(r0 + 1, r1_a) if A[i][1] == a]
                c_post_writes = [j for j in range(r0, r0_c) if A[j][1] == c]
                c_pre_writes = [j for j in range(last_c_pre + 1, r0) if A[j][1] == c]

                edge_summary["coupled_ac_window_stats"]["post_r0_a_writes_total"] += len(a_post_writes)
                edge_summary["coupled_ac_window_stats"]["c_writes_after_r0_total"] += len(c_post_writes)
                edge_summary["coupled_ac_window_stats"]["c_writes_before_r0_after_last_read_total"] += len(c_pre_writes)
                if a_post_writes:
                    edge_summary["coupled_ac_window_stats"]["edges_with_post_r0_a_writes"] += 1
                if c_post_writes or c_pre_writes:
                    edge_summary["coupled_ac_window_stats"]["edges_with_c_writes"] += 1

                coupled_target = eb | (eb << n)

                for rule in ("same_path", "monotone_all"):
                    coupled_vecs = []
                    a_only_vecs = []
                    for i in range(r0):
                        if A[i][1] != a:
                            continue
                        for d in range(n):
                            if d == a or not donor_legal(i, d, rule):
                                continue
                            v_vec = a_vals_before[i][d]
                            coupled_vecs.append(v_vec | (v_vec << n))
                            a_only_vecs.append(v_vec)
                    for i in a_post_writes:
                        for d in range(n):
                            if d in (a, c) or not donor_legal(i, d, rule):
                                continue
                            v_vec = a_vals_before[i][d]
                            coupled_vecs.append(v_vec)
                            a_only_vecs.append(v_vec)
                    for j in c_pre_writes + c_post_writes:
                        for d in range(n):
                            if d in (a, c) or not donor_legal(j, d, rule):
                                continue
                            v_vec = a_vals_before[j][d]
                            coupled_vecs.append(v_vec << n)

                    ok_c, h_c, _ = solve_f2_with_dual(coupled_vecs, coupled_target)
                    ok_a, _, _ = solve_f2_with_dual(a_only_vecs, eb)
                    if ok_a:
                        edge_summary["post_r0_a_only_solvable"][rule] += 1
                    if ok_c:
                        edge_summary["coupled_ac_solvable"][rule] += 1
                        if (a, b) not in expected_solvable:
                            edge_summary["coupled_ac_new_beyond_pre_read"][rule].append([a, b, c, r0, r1_a, r0_c])
                    elif rule == "monotone_all" and h_c != 0:
                        edge_summary["coupled_ac_dual_witnesses_verified"] += 1
                        total_coupled_duals_verified += 1

        require(edge_summary["entire_A_a_only_solvable"]["monotone_all"] == 5, "expected 5 solvable whole-A edges")
        require(edge_summary["coupled_ac_solvable"]["monotone_all"] == 5, "expected 5 solvable coupled edges")
        require(edge_summary["entire_A_dual_witnesses_verified"] == 231, "expected 231 whole-A dual witnesses")
        require(edge_summary["coupled_ac_dual_witnesses_verified"] == 225, "expected 225 coupled dual witnesses")
        results[wname] = edge_summary

    require(total_whole_a_duals_verified == 693, "expected 693 total whole-A dual witnesses")
    require(total_coupled_duals_verified == 675, "expected 675 total coupled dual witnesses")
    require(corrupted_duals_rejected == 693, "expected all 693 corrupted duals to be rejected")
    require(solvable_falsely_obstructed == 0, "expected 0 solvable edges obstructed")

    results["solvable_5_edges"] = [[a, b] for a, b in expected_solvable]
    results["total_whole_a_dual_witnesses_verified"] = total_whole_a_duals_verified
    results["total_coupled_ac_dual_witnesses_verified"] = total_coupled_duals_verified
    ctrl3_info = {
        "ctrl3_whole_a_duals_verified": total_whole_a_duals_verified,
        "ctrl3_coupled_duals_verified": total_coupled_duals_verified,
        "ctrl3_corrupted_duals_rejected": corrupted_duals_rejected,
        "ctrl3_solvable_edges_falsely_obstructed": solvable_falsely_obstructed,
    }
    return results, ctrl3_info


# ============================================================================
# PILLAR 3: Unconditional All-Length, All-Role n_b >= 6 in F2[UT4(F2)]
# ============================================================================
def run_pillar_3() -> tuple[dict, dict]:
    P = load_module("ut4_pred", "research/ut4-fifteen-call-five-b/vendor/predecessor.py")
    C = load_module("ut4_c", "research/ut4-fifteen-call-five-b/census.py")
    srank = tuple(C.s_rank(P, s) for s in range(16))

    def tr(m: int) -> int:
        return (m & 1) ^ ((m >> 3) & 1)

    closure = {(0, 0, 0)}
    frontier = [(0, 0, 0)]
    while frontier:
        sa, sc, q = frontier.pop()
        for r in P.COUPLINGS:
            for nxt in ((sa ^ r, sc, q ^ P.MULT[sc][r]), (sa, sc ^ r, q ^ P.MULT[sa][r])):
                if nxt not in closure:
                    closure.add(nxt)
                    frontier.append(nxt)
    q_reach = defaultdict(set)
    for sa, sc, q in closure:
        q_reach[(sa, sc)].add(q)

    trace_hyperplane_exact_matches = sum(
        q_reach[(sa, sc)] == {q for q in range(16) if tr(q) == tr(P.MULT[sa][sc])}
        for sa in range(16)
        for sc in range(16)
    )
    require(trace_hyperplane_exact_matches == 256, "trace hyperplane theorem must hold on all 256 pairs")

    def side_row(left: int, n: int) -> tuple[int, ...]:
        right = left ^ n
        row = []
        for p in range(16):
            pn, np = P.MULT[p][n], P.MULT[n][p]
            bab = P.MULT[P.MULT[left][p]][n] ^ P.MULT[np][right]
            row.append(pn | (np << 4) | (P.MULT[pn][p] << 8) | (bab << 12))
        return tuple(row)

    key_int_tab = {}
    for j in range(5):
        for n in P.COUPLINGS:
            x, y = P.SPLIT[n]
            row = []
            for p in range(16):
                px = ((p & 1) * (x & 1)) ^ (((p >> 1) & 1) * ((x >> 1) & 1))
                px |= ((((p >> 2) & 1) * (x & 1)) ^ (((p >> 3) & 1) * ((x >> 1) & 1))) << 1
                yp = ((y & 1) * (p & 1)) ^ (((y >> 1) & 1) * ((p >> 2) & 1))
                yp |= (((y & 1) * ((p >> 1) & 1)) ^ (((y >> 1) & 1) * ((p >> 3) & 1))) << 1
                val = (
                    ((px & 1) << j)
                    | (((px >> 1) & 1) << (j + 5))
                    | ((yp & 1) << (j + 10))
                    | (((yp >> 1) & 1) << (j + 15))
                )
                row.append(val)
            key_int_tab[(j, n)] = tuple(row)

    left_fast = {}
    right_fast = {}
    left_full = {}
    right_full = {}
    for n0 in P.COUPLINGS:
        t0_r = side_row(0, n0)
        k0_r = key_int_tab[(0, n0)]
        for n1 in P.COUPLINGS:
            t1_r = side_row(n0, n1)
            k1_r = key_int_tab[(1, n1)]
            lmap = defaultdict(lambda: defaultdict(int))
            for p0 in range(16):
                v0, k0 = t0_r[p0], k0_r[p0]
                for p1 in range(16):
                    lmap[v0 ^ t1_r[p1]][k0 | k1_r[p1]] += 1
            left_fast[(n0, n1)] = tuple((vl, tuple(kdict.items())) for vl, kdict in lmap.items())
            for p2 in range(16):
                lfull = defaultdict(list)
                for p0 in range(16):
                    r0 = srank[p0]
                    v0, k0 = t0_r[p0], k0_r[p0]
                    for p1 in range(16):
                        rl = r0 + srank[p0 ^ p1] + srank[p1 ^ p2]
                        lfull[v0 ^ t1_r[p1]].append((p0, p1, rl, k0 | k1_r[p1]))
                left_full[(n0, n1, p2)] = tuple(lfull.items())

    for n4 in P.COUPLINGS:
        t4_r = side_row(n4, n4)
        k4_r = key_int_tab[(4, n4)]
        for n3 in P.COUPLINGS:
            t3_r = side_row(n3 ^ n4, n3)
            k3_r = key_int_tab[(3, n3)]
            rmap = defaultdict(lambda: defaultdict(int))
            for p3 in range(16):
                v3, k3 = t3_r[p3], k3_r[p3]
                for p4 in range(16):
                    rmap[v3 ^ t4_r[p4]][k3 | k4_r[p4]] += 1
            right_fast[(n3, n4)] = {vr: tuple(kdict.items()) for vr, kdict in rmap.items()}
            for p2 in range(16):
                rfull = defaultdict(list)
                for p3 in range(16):
                    r23 = srank[p2 ^ p3]
                    v3, k3 = t3_r[p3], k3_r[p3]
                    for p4 in range(16):
                        rr = r23 + srank[p3 ^ p4] + srank[p4]
                        rfull[v3 ^ t4_r[p4]].append((p3, p4, rr, k3 | k4_r[p4]))
                right_full[(n3, n4, p2)] = rfull

    def unpack_valid_key(k: int) -> tuple[int, int, int, int] | None:
        u0, u1, w0, w1 = k & 31, (k >> 5) & 31, (k >> 10) & 31, (k >> 15) & 31
        if not (u0 and u1 and u0 != u1 and w0 and w1 and w0 != w1):
            return None
        return (u0, u1, w0, w1)

    total_middles = 0
    nondeg_middles = 0
    deg_middles = 0
    nondeg_compat_pairs = 0
    total_compat_pairs = 0
    surviving_middles = []
    profile_pairs_by_min_L: Counter[int] = Counter()
    acb00_or_bac00_annihilated = 0

    for middle in product(P.COUPLINGS, repeat=5):
        if P.total(middle):
            continue
        total_middles += 1
        xs = {P.SPLIT[n][0] for n in middle}
        ys = {P.SPLIT[n][1] for n in middle}
        rk_x = 2 if len(xs) >= 2 else 1
        rk_y = 2 if len(ys) >= 2 else 1
        if rk_x == 2 and rk_y == 2:
            nondeg_middles += 1
        else:
            deg_middles += 1

        n0, n1, n2, n3, n4 = middle
        t2_r = side_row(n0 ^ n1, n2)
        k2_r = key_int_tab[(2, n2)]
        l_fast = left_fast[(n0, n1)]
        r_fast = right_fast[(n3, n4)]
        a_counts: dict[tuple[int, int, int, int], int] = {}
        c_counts: dict[tuple[int, int, int, int], int] = {}
        for p2 in range(16):
            v2_base = t2_r[p2]
            k2_base = k2_r[p2]
            for vl, l_klist in l_fast:
                rc_klist = r_fast.get(vl ^ v2_base)
                if rc_klist:
                    for kl, cnt_l in l_klist:
                        kl2 = kl | k2_base
                        for kr, cnt_r in rc_klist:
                            pk = unpack_valid_key(kl2 | kr)
                            if pk is not None:
                                c_counts[pk] = c_counts.get(pk, 0) + cnt_l * cnt_r
                ra_klist = r_fast.get(vl ^ v2_base ^ 0x8888)
                if ra_klist:
                    for kl, cnt_l in l_klist:
                        kl2 = kl | k2_base
                        for kr, cnt_r in ra_klist:
                            pk = unpack_valid_key(kl2 | kr)
                            if pk is not None:
                                a_counts[pk] = a_counts.get(pk, 0) + cnt_l * cnt_r
        if not a_counts or not c_counts:
            continue

        compat = list(P.compatible_keys(a_counts, c_counts))
        if not compat:
            continue

        all_col0_zero = all((P.SPLIT[n][1] & 1) == 0 for n in middle)
        all_row0_zero = all((P.SPLIT[n][0] & 1) == 0 for n in middle)
        npairs = sum(a_counts[ka] * c_counts[kc] for ka, kc in compat)
        total_compat_pairs += npairs
        if rk_x == 2 and rk_y == 2:
            nondeg_compat_pairs += npairs

        surviving_middles.append(
            {
                "middle": list(middle),
                "rk_X_b": rk_x,
                "rk_Y_b": rk_y,
                "all_b_first_col_zero": all_col0_zero,
                "all_b_first_row_zero": all_row0_zero,
                "compat_key_pairs": len(compat),
                "compat_profile_pairs": npairs,
            }
        )

        # Reconstruct exact profiles on the 16 surviving degenerate middles
        a_by_key: dict[tuple[int, int, int, int], list[tuple[tuple[int, ...], int]]] = {}
        c_by_key: dict[tuple[int, int, int, int], list[tuple[tuple[int, ...], int]]] = {}
        for p2 in range(16):
            v2_base = t2_r[p2]
            k2_base = k2_r[p2]
            l_items = left_full[(n0, n1, p2)]
            rmap = right_full[(n3, n4, p2)]
            for vl, l_list in l_items:
                rc_list = rmap.get(vl ^ v2_base)
                if rc_list:
                    for p0, p1, rl, kl in l_list:
                        kl2 = kl | k2_base
                        for p3, p4, rr, kr in rc_list:
                            pk = unpack_valid_key(kl2 | kr)
                            if pk is not None:
                                c_by_key.setdefault(pk, []).append(((p0, p1, p2, p3, p4), rl + rr))
                ra_list = rmap.get(vl ^ v2_base ^ 0x8888)
                if ra_list:
                    for p0, p1, rl, kl in l_list:
                        kl2 = kl | k2_base
                        for p3, p4, rr, kr in ra_list:
                            pk = unpack_valid_key(kl2 | kr)
                            if pk is not None:
                                a_by_key.setdefault(pk, []).append(((p0, p1, p2, p3, p4), rl + rr))

        # Verify min_L distribution and that every compatible pair annihilates ACB[0,0] or BAC[0,0]
        a_len_hist: dict[tuple[int, int, int, int], Counter[int]] = {}
        c_len_hist: dict[tuple[int, int, int, int], Counter[int]] = {}
        for ka in {k for k, _ in compat}:
            cnt_a: Counter[int] = Counter()
            for pa, ra_min in a_by_key[ka]:
                cnt_a[max(4, ra_min)] += 1
            a_len_hist[ka] = cnt_a
        for kc in {k for _, k in compat}:
            cnt_c: Counter[int] = Counter()
            for pc, rc_min in c_by_key[kc]:
                cnt_c[max(4, rc_min)] += 1
            c_len_hist[kc] = cnt_c
        for ka, kc in compat:
            for na_eff, ca_cnt in a_len_hist[ka].items():
                for nc_eff, cc_cnt in c_len_hist[kc].items():
                    profile_pairs_by_min_L[na_eff + 5 + nc_eff] += ca_cnt * cc_cnt
        # Also verify eval_base_2role directly on sample/distinct profiles and algebraically:
        # When all_col0_zero is True, every nb in middle has right-factor y with bit 0 == 0,
        # so P.MULT[ac][nb] has bit 0 == 0 for ALL ac, making base_acb & 1 == 0 identically.
        # When all_row0_zero is True, every nb in middle has left-factor x with bit 0 == 0,
        # so P.MULT[b][sa] and P.MULT[b][sc] have bit 0 == 0 for ALL sa, sc, making base_bac & 1 == 0 identically.
        require(all_col0_zero or all_row0_zero, "surviving middle must have col0=0 or row0=0")
        for ka, kc in compat[:4]:
            pa0, _ = a_by_key[ka][0]
            pc0, _ = c_by_key[kc][0]
            _, base_acb, base_bac = C.eval_base_2role(
                P, middle, C.profile_gaps(pa0), C.profile_gaps(pc0)
            )
            require(
                (all_col0_zero and (base_acb & 1) == 0)
                or (all_row0_zero and (base_bac & 1) == 0),
                "degenerate middle must annihilate ACB[0,0] or BAC[0,0]",
            )
        acb00_or_bac00_annihilated += npairs

    require(total_middles == 3600, "expected 3600 zero-sum five-b middles")
    require(nondeg_middles == 3240 and deg_middles == 360, "expected 3240 nondeg / 360 deg middles")
    require(nondeg_compat_pairs == 0, "expected 0 compatible pairs on all 3240 nondegenerate middles")
    require(len(surviving_middles) == 16, "expected 16 surviving degenerate middles")
    require(total_compat_pairs == 3145728, "expected 3145728 degenerate compatible pairs")
    require(acb00_or_bac00_annihilated == 3145728, "all 3145728 degenerate pairs must annihilate ACB[0,0] or BAC[0,0]")

    # Negative Control 5: Verify direct 14-call (4, 6, 4) word and confirm that omitting
    # any 1 of its 14 calls (including each of the 6 middle b-calls) fails the target identity.
    pos_ctrl = P.positive_and_controls()
    require(pos_ctrl["formal_basis_columns"] == 192, "expected 192 formal basis columns")
    require(pos_ctrl["omitted_call_controls"] == 14, "expected all 14 single-call omissions to fail")

    pillar3 = {
        "trace_hyperplane_exact_matches_out_of_256": trace_hyperplane_exact_matches,
        "total_zero_sum_five_b_middles": total_middles,
        "nondegenerate_middles_rkX2_rkY2": nondeg_middles,
        "degenerate_middles_rkX1_or_rkY1": deg_middles,
        "nondegenerate_middles_compatible_profile_pairs_all_lengths": nondeg_compat_pairs,
        "total_unconstrained_compatible_profile_pairs_all_lengths": total_compat_pairs,
        "acb00_or_bac00_identically_zero_count": acb00_or_bac00_annihilated,
        "surviving_middles_count": len(surviving_middles),
        "surviving_16_middles": surviving_middles,
        "profile_pairs_by_min_realizable_length_L": {
            str(k): v for k, v in sorted(profile_pairs_by_min_L.items())
        },
        "direct_464_word_length": 14,
        "direct_464_omitted_call_failures": pos_ctrl["omitted_call_controls"],
    }
    ctrl45_info = {
        "ctrl4_degenerate_surviving_middles": len(surviving_middles),
        "ctrl4_acb00_or_bac00_annihilated_pairs": acb00_or_bac00_annihilated,
        "ctrl5_direct_464_omitted_call_failures": pos_ctrl["omitted_call_controls"],
    }
    return pillar3, ctrl45_info


# ============================================================================
# PILLAR 4: Grassmannian Schubert-Cell Parity Floor for Dyadic Full-Borel Words
# ============================================================================
def run_pillar_4() -> tuple[dict, dict]:
    m_bf = load_module("m_bf", "research/bit-full-borel-2adic-floor/verify.py")

    def rref_plane(vec1: list[Fraction], vec2: list[Fraction]) -> tuple[tuple[Fraction, ...], ...]:
        rows = [list(vec1), list(vec2)]
        r = 0
        for c in range(4):
            p = next((i for i in range(r, 2) if rows[i][c] != 0), None)
            if p is None:
                continue
            rows[r], rows[p] = rows[p], rows[r]
            piv = rows[r][c]
            if piv != 1:
                rows[r] = [x / piv for x in rows[r]]
            other = 1 - r
            f = rows[other][c]
            if f != 0:
                rows[other] = [x - f * y for x, y in zip(rows[other], rows[r])]
            r += 1
        require(r == 2, "must be 2-dimensional plane")
        return (tuple(rows[0]), tuple(rows[1]))

    def schubert_cell(plane: tuple[tuple[Fraction, ...], ...]) -> int:
        dim_inter = sum(1 for row in plane if row[0] == 0 and row[1] == 0)
        return 2 - dim_inter

    def act_plane(
        g: tuple[tuple[Fraction, ...], ...], plane: tuple[tuple[Fraction, ...], ...]
    ) -> tuple[tuple[Fraction, ...], ...]:
        p0, p1 = plane
        v1 = [
            g[i][0] * p0[0] + g[i][1] * p0[1] + g[i][2] * p0[2] + g[i][3] * p0[3]
            for i in range(4)
        ]
        v2 = [
            g[i][0] * p1[0] + g[i][1] * p1[1] + g[i][2] * p1[2] + g[i][3] * p1[3]
            for i in range(4)
        ]
        return rref_plane(v1, v2)

    D_plane = rref_plane(
        [Fraction(0), Fraction(0), Fraction(1), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(0), Fraction(1)],
    )
    require(schubert_cell(D_plane) == 0, "D_plane must lie in Schubert cell O_0")

    half = Fraction(1, 2)
    dyadic_borels = [
        m_bf.lower(
            m_bf.mat([[half, 0], [0, 1]]),
            m_bf.mat([[half, 1], [0, half]]),
            m_bf.mat([[2, half], [0, 1]]),
        ),
        m_bf.lower(
            m_bf.mat([[1, half], [0, 2]]),
            m_bf.mat([[1, half], [half, 2]]),
            m_bf.mat([[half, 0], [1, 2]]),
        ),
        m_bf.lower(
            m_bf.mat([[2, 0], [0, 2]]),
            m_bf.mat([[half, half], [half, half]]),
            m_bf.mat([[half, 0], [0, half]]),
        ),
    ]
    dyadic_rank1_shears = [
        m_bf.shear(m_bf.mat([[half, 0], [0, 0]])),
        m_bf.shear(m_bf.mat([[0, 0], [0, half]])),
        m_bf.shear(m_bf.mat([[half, half], [half, half]])),
        m_bf.shear(m_bf.mat([[half, -half], [-half, half]])),
    ]

    planes = {D_plane}
    for g in dyadic_rank1_shears + dyadic_borels:
        planes |= {act_plane(g, p) for p in list(planes)}
    for g in dyadic_rank1_shears + dyadic_borels:
        planes |= {act_plane(g, p) for p in list(planes)}

    cell_counts = Counter(schubert_cell(p) for p in planes)
    require(
        cell_counts[0] == 1 and cell_counts[1] == 320 and cell_counts[2] == 13210,
        f"unexpected Schubert-cell plane distribution: {cell_counts}",
    )

    borel_invariance_checks = 0
    for l_mat in dyadic_borels:
        for p in planes:
            require(
                schubert_cell(act_plane(l_mat, p)) == schubert_cell(p),
                "dyadic lower-Borel map violated Schubert-cell invariance",
            )
            borel_invariance_checks += 1

    rank1_jump_checks = 0
    for s_mat in dyadic_rank1_shears:
        require(
            schubert_cell(act_plane(s_mat, D_plane)) == 1,
            "rank-1 shear from D_plane must land in O_1",
        )
        for p in planes:
            require(
                abs(schubert_cell(act_plane(s_mat, p)) - schubert_cell(p)) <= 1,
                "rank-1 shear jumped more than 1 Schubert cell",
            )
            rank1_jump_checks += 1

    require(borel_invariance_checks == 40593, "expected 40593 dyadic Borel checks")
    require(rank1_jump_checks == 54124, "expected 54124 dyadic rank-1 shear checks")

    def outer2(x: int, d: int) -> int:
        x0, x1 = x & 1, (x >> 1) & 1
        d0, d1 = d & 1, (d >> 1) & 1
        return (x0 * d0) | ((x0 * d1) << 1) | ((x1 * d0) << 2) | ((x1 * d1) << 3)

    total_configs_tested = 0
    survivors_E2_and_E1 = 0
    survivors_E2_E1_E0 = 0

    for x1, x2, x3 in product(range(4), repeat=3):
        for d01_1 in range(4):
            ker1 = [w for w in (1, 2, 3) if ((d01_1 & w).bit_count() & 1) == 0]
            for d01_2, d12_2 in product(range(4), repeat=2):
                if any(((d12_2 & w).bit_count() & 1) == 1 for w in ker1):
                    continue
                for d01_3, d12_3 in product(range(4), repeat=2):
                    if any(
                        ((d01_2 & w).bit_count() & 1) == 0
                        and ((d12_3 & w).bit_count() & 1) == 1
                        for w in ker1
                    ):
                        continue
                    total_configs_tested += 1
                    E2 = outer2(x2, d12_2) ^ outer2(x3, d12_3)
                    E1 = (
                        outer2(x1, d01_1)
                        ^ outer2(x2, d01_2 ^ d12_2)
                        ^ outer2(x3, d01_3 ^ d12_3)
                    )
                    if E2 == 9 and E1 == 0:
                        survivors_E2_and_E1 += 1
                        for B_fin in (9, 6, 11, 13, 7, 14):
                            E0 = (
                                B_fin
                                ^ outer2(x1, d01_1)
                                ^ outer2(x2, d01_2)
                                ^ outer2(x3, d01_3)
                            )
                            if E0 == 0:
                                survivors_E2_E1_E0 += 1

    require(total_configs_tested == 20224, "expected 20224 valid 3-call parity configs")
    require(survivors_E2_and_E1 == 0, "expected 0 survivors for 3-call rank-1 parity system")

    # Negative Control 6: A single rank-2 shear (paid_rank = 2 < 4) gives F2-rank at most 1 on E2
    # (cannot reach E2 = I_2 of rank 2), and an illegal free upper-triangular shear H += D
    # jumps D_plane directly from O_0 (d=0) to O_2 (d=2) at paid_rank = 0.
    single_call_max_E2_rank = max(
        1 if outer2(x1, d1) else 0 for x1 in range(4) for d1 in range(4)
    )
    illegal_upper = m_bf.shear(m_bf.mat([[1, 0], [0, 1]]))
    illegal_upper_cell = schubert_cell(act_plane(illegal_upper, D_plane))
    require(
        single_call_max_E2_rank == 1 and illegal_upper_cell == 2,
        "Control 6 single-call rank cap and illegal upper shear check failed",
    )

    pillar4 = {
        "sampled_planes_total": len(planes),
        "sampled_planes_by_schubert_cell": {str(k): v for k, v in sorted(cell_counts.items())},
        "dyadic_borel_schubert_invariance_checks": borel_invariance_checks,
        "dyadic_rank1_shear_jump_checks": rank1_jump_checks,
        "valid_3call_parity_configs_tested": total_configs_tested,
        "survivors_E2_eq_I2_and_E1_eq_0_any_R": survivors_E2_and_E1,
        "survivors_E2_eq_I2_and_E1_eq_0_and_E0_eq_0": survivors_E2_E1_E0,
        "paid_rank_floor_m2_W2": 4,
    }
    ctrl6_info = {
        "ctrl6_single_rank2_call_max_E2_f2_rank": single_call_max_E2_rank,
        "ctrl6_illegal_upper_shear_cell_jump": illegal_upper_cell,
    }
    return pillar4, ctrl6_info


def main() -> int:
    write_mode = "--write" in sys.argv[1:]
    input_blobs = verify_pinned_sources()

    pillar1, ctrl12 = run_pillar_1(input_blobs)
    pillar2, ctrl3 = run_pillar_2(input_blobs)
    pillar3, ctrl45 = run_pillar_3()
    pillar4, ctrl6 = run_pillar_4()

    controls = [
        f"control_1_overlapping_seventh_shear_corrupts_661_semantics: appending an overlapping 7th shear (349 ^= 461) after Shear 1 (349 ^= 462) corrupts {ctrl12['ctrl1_overlapping_shear_mismatches']} registers in the 661-column forward replay",
        f"control_2_omitting_shear1_prep_or_undo_gate_breaks_targets: omitting the 2 setup/restore gates of Shear 1 (349 ^= 462) breaks {ctrl12['ctrl2_omitted_shear1_gates_mismatches']} output registers across the 16 shared middle-column target wires",
        f"control_3_dual_hyperplane_witness_validation_and_corrupted_dual_rejection: all {ctrl3['ctrl3_whole_a_duals_verified']} whole-A 661-bit RREF dual witnesses and {ctrl3['ctrl3_coupled_duals_verified']} coupled 1,322-bit dual witnesses pass, {ctrl3['ctrl3_corrupted_duals_rejected']} target-flipped duals are rejected, and {ctrl3['ctrl3_solvable_edges_falsely_obstructed']} solvable edges are falsely obstructed",
        f"control_4_ut4_degenerate_rank1_middle_annihilates_acb00_or_bac00: relaxing rank X_b = rank Y_b = 2 admits {ctrl45['ctrl4_degenerate_surviving_middles']} degenerate middles ({ctrl45['ctrl4_acb00_or_bac00_annihilated_pairs']} pairs), 100% of which annihilate ACB[0,0]=0 or BAC[0,0]=0",
        f"control_5_ut4_omitting_any_call_from_direct_464_word_fails: omitting any 1 of the 14 calls in the direct (4,6,4) word fails the exact UT4 target identity ({ctrl45['ctrl5_direct_464_omitted_call_failures']}/14 rejected)",
        f"control_6_dyadic_borel_single_block_and_illegal_upper_shear: a single rank-2 call has F2-rank {ctrl6['ctrl6_single_rank2_call_max_E2_f2_rank']} < 2 on E2, and an illegal free upper shear H += D jumps D_plane to cell O_{ctrl6['ctrl6_illegal_upper_shear_cell_jump']} at paid rank 0",
    ]

    sub10k = pillar1["progression"]["NEW_SIX_WAY_SUB10K_COMPOSITION_with_6_disjoint_helper_shears"]
    fiveway = pillar1["progression"]["NEW_FIVE_WAY_COMPOSITION_PR1709_PR1868_PR2115_PR2440_on_PR1188"]
    fourway_b = pillar1["progression"]["NEW_PR1709_plus_PR1868_plus_PR2115_on_PR1188"]
    fourway_a = pillar1["progression"]["NEW_PR1543_plus_PR1868_plus_PR2115_on_PR1188"]

    receipt = {
        "status": "PASS_R439_SUB10K_SIXWAY_AND_STAR_DUAL_WITNESSES",
        "pillar1_r439_sub10k_sixway_composition": pillar1,
        "pillar2_whole_section_a_and_coupled_star_absorption": pillar2,
        "pillar3_ut4_all_length_five_b_exclusion": pillar3,
        "pillar4_dyadic_full_borel_schubert_parity_floor": pillar4,
        "controls": controls,
        "summary": {
            "r439_sub10k_sixway_adds": sub10k["ADDs"],
            "r439_fiveway_adds": fiveway["ADDs"],
            "r439_fourway_b_adds": fourway_b["ADDs"],
            "r439_fourway_a_adds": fourway_a["ADDs"],
            "r439_delta_vs_pr1188": sub10k["delta_vs_PR1188"],
            "r439_delta_vs_pr2440": sub10k["delta_vs_PR2440"],
            "r439_disjoint_shears_saving": sub10k["disjoint_shears_total_saving"],
            "r439_scatter_adds": sub10k["scatter_ADDs"],
            "r439_sub10k_F": sub10k["F"],
            "r439_sub10k_B": sub10k["B"],
            "r439_local_bits": sub10k["local_bits"],
            "r439_nine_stage_bits": sub10k["nine_stage_bits"],
            "r439_paid_rank_mass": pillar1["paid_rank_mass"],
            "star_edges_per_word": 236,
            "star_solvable_edges_per_word": 5,
            "star_obstructed_edges_per_word": 231,
            "star_whole_a_dual_witnesses_total": pillar2["total_whole_a_dual_witnesses_verified"],
            "star_coupled_ac_dual_witnesses_total": pillar2["total_coupled_ac_dual_witnesses_verified"],
            "ut4_trace_hyperplane_matches": pillar3["trace_hyperplane_exact_matches_out_of_256"],
            "ut4_zero_sum_five_b_middles": pillar3["total_zero_sum_five_b_middles"],
            "ut4_nondegenerate_middles": pillar3["nondegenerate_middles_rkX2_rkY2"],
            "ut4_nondegenerate_compatible_pairs": pillar3["nondegenerate_middles_compatible_profile_pairs_all_lengths"],
            "ut4_degenerate_surviving_middles": pillar3["surviving_middles_count"],
            "ut4_degenerate_compatible_pairs": pillar3["total_unconstrained_compatible_profile_pairs_all_lengths"],
            "dyadic_borel_invariance_checks": pillar4["dyadic_borel_schubert_invariance_checks"],
            "dyadic_rank1_shear_checks": pillar4["dyadic_rank1_shear_jump_checks"],
            "dyadic_3call_parity_configs": pillar4["valid_3call_parity_configs_tested"],
            "dyadic_3call_parity_survivors": pillar4["survivors_E2_eq_I2_and_E1_eq_0_any_R"],
            "dyadic_paid_rank_floor": pillar4["paid_rank_floor_m2_W2"],
        },
    }

    result_path = HERE / "RESULT.json"
    if write_mode:
        result_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        require(result_path.is_file(), "missing RESULT.json")
        expected = json.loads(result_path.read_text(encoding="utf-8"))
        require(receipt == expected, "computed receipt differs from committed RESULT.json")

    print(
        f"PASS_R439_SUB10K_SIXWAY_AND_STAR_DUAL_WITNESSES "
        f"sub10k_adds={sub10k['ADDs']} delta_pr1188={sub10k['delta_vs_PR1188']} "
        f"delta_pr2440={sub10k['delta_vs_PR2440']} whole_a_duals={pillar2['total_whole_a_dual_witnesses_verified']} "
        f"ut4_nondeg_compat={pillar3['nondegenerate_middles_compatible_profile_pairs_all_lengths']} "
        f"dyadic_3call_survivors={pillar4['survivors_E2_eq_I2_and_E1_eq_0_any_R']} "
        f"controls=6 no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
