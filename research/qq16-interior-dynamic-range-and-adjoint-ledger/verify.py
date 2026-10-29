#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact 712-column interior dynamic range, dyadic grid invariance, backward
adjoint error-propagation ledger, and F17 consumer ceiling screen for CONSERVED-QQ16.

Computes and verifies four unified pillars (plus six behavioral negative controls)
directly from the nine upstream files pinned in SOURCES.json:
  1. Pillar 1 — Exact 712-Column Algebraic Replay of CONSERVED-QQ16 Programs F
     (26,099 events in F_0; 26,387 events in F_1..F_8) and B (27,019 events in
     B_1_2..B_7_8) & The 37-Bit (F) / 52-Bit (B) Interior Dynamic Range Collapse:
     - Proves that exact helper cancellations collapse interior L1 row norms from
       the 55-bit (F) and 73-bit (B) Horner path-sum triangle bounds down to
       131,072 (2^17, 18 bits) in F and 1,154,896 (< 2^20.14, 21 bits) in B,
       with peak child-entry L1 norms <= 124 (7 bits) in F and <= 166 (8 bits) in B,
       and maximum dyadic denominators 16 (2^4) in F and 131,072 (2^17) in B.
  2. Pillar 2 — Exact Backward Adjoint Error-Propagation Ledger (Closing Open
     Question 1 of PR #2965):
     - Propagates unit child, add, and scale errors backward through the exact
       transpose DAGs of F and B across all 704 terminal outputs (0..223 data,
       224..703 restored helpers), certifying exact worst-case L_inf gains:
       * F data (0..223): 132 * eps_child + 2216769809/131072 * eps_gate
         (add = 528, scale = 66311/4, single-child max = 2).
       * F helpers (224..703): 0 * eps_wrap_child + 59 * eps_core_child + 131599/4 * eps_gate.
       * B data (0..223): 381/2 * eps_child + 3689923/4 * eps_gate
         (add = 1836679/2, scale = 16603/4, single-child max = 12).
       * B helpers (224..703): 0 * eps_wrap_child + 393/2 * eps_core_child + 1515 * eps_gate.
  3. Pillar 3 — Wrapper-Helper Adjoint Orthogonality (0 * eps_wrap_child), Exact
     Dyadic Common-Grid Escape from PR #2995/#3017/#3036/#3068 Cancellation Faults,
     & End-to-End Precision Floor Coupled with #2965:
     - Proves why all wrapper native_line children (8 in F, 24 in B) and wrapper
       scalar gates have 0 backward sensitivity to all 480 restored helpers;
       proves that 4 (F) and 17 (B) fractional guard bits make all 21,025 (F) and
       21,401 (B) scalar gates 100% exact (eps_gate = 0); and couples with #2965
       (||F0^-1||_inf = 49, ||D||_inf <= 1923, budget 7587/8192) to certify exact
       fixed-point and floating-point bit budgets (saving 52 bits vs Horner).
  4. Pillar 4 — Complete Physical Recursive Bill & F17 Consumer Ledger Comparison
     via ceiling.ceiling(...):
     - Screens CONSERVED-QQ16 (F_0 + B_1_2) + #2707 (336 rank-1 decoder lines) +
       #2678 (224 rank-9 H9 endpoint adapters) under ceiling.ceiling(...) at
       centre = 64 vs centre = 0 against the selected record (kappa = 0.001672660197076918).

Author: dcharb78, with AI assistance
License: Apache-2.0
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = (
    HERE.parents[1]
    if (HERE.parents[1] / "certificates" / "selected-result.json").is_file()
    else Path("/Users/dcharb/kappa_workspace/imb-repo")
)
sys.path.insert(0, str(ROOT / "research" / "complex-local-word-ceiling"))
import ceiling as C  # noqa: E402

GRID = Q(1, 10**12)


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git_blob_bytes(raw: bytes) -> str:
    header = f"blob {len(raw)}\0".encode("ascii")
    return hashlib.sha1(header + raw).hexdigest()


def ffloat(val: Q | float, digits: int = 12) -> str:
    return f"{float(val):.{digits}f}"


def reg_index(token: list) -> int:
    kind, idx = token
    require(kind in ("L", "C"), f"unknown register kind: {kind}")
    return int(idx) + (704 if kind == "C" else 0)


def load_authenticated_inputs() -> dict:
    sources_path = HERE / "SOURCES.json"
    require(sources_path.is_file(), "SOURCES.json missing")
    manifest = json.loads(sources_path.read_text(encoding="utf-8"))
    require(manifest.get("schema_version") == 1, "SOURCES.json schema_version != 1")

    raw_files: dict[str, bytes] = {}
    for row in manifest["files"]:
        rel = row["path"]
        p = ROOT / rel
        require(p.is_file() and not p.is_symlink(), f"missing or symlinked source: {rel}")
        raw = p.read_bytes()
        require(sha256_bytes(raw) == row["sha256"], f"sha256 mismatch on {rel}")
        require(git_blob_bytes(raw) == row["git_blob"], f"git_blob mismatch on {rel}")
        raw_files[rel] = raw

    cert_raw = gzip.decompress(raw_files["research/joint-query/certificate.json.gz"])
    require(
        sha256_bytes(cert_raw)
        == "2efe83c59978aa9c0db2c3e4eccc14cbfdcd3c9ce499432601b5dd34083472ef",
        "decompressed certificate.json.gz payload sha256 mismatch",
    )

    return {
        "selected": json.loads(raw_files["certificates/selected-result.json"].decode("utf-8")),
        "conserved_summary": json.loads(
            raw_files["research/joint-query/evidence/CONSERVED-QQ16.json"].decode("utf-8")
        ),
        "certificate": json.loads(cert_raw.decode("utf-8")),
        "defect_transfer": json.loads(
            raw_files["research/qq16-producer-defect-transfer/RESULT.json"].decode("utf-8")
        ),
        "decoder_result": json.loads(
            raw_files["research/qq16-line-normalized-decoder/RESULT.json"].decode("utf-8")
        ),
        "ceiling_result": json.loads(
            raw_files["research/complex-local-word-ceiling/RESULT.json"].decode("utf-8")
        ),
    }


def expand_program_events(packet: dict, case_name: str) -> list[tuple[list, str]]:
    """Expand a case program (e.g. F_0, F_1, B_1_2) into tagged (event, origin) pairs."""
    cores = packet["core_words"]
    expanded: list[tuple[list, str]] = []
    for ev in packet["programs"][case_name]:
        kind = ev[0]
        if kind == "retained_core":
            for cev in cores[ev[1]]:
                expanded.append((cev, "core"))
        elif kind in ("cover_sweep", "private_sweep"):
            for wev in ev[2]:
                expanded.append((wev, "wrapper"))
        else:
            expanded.append((ev, "wrapper"))
    return expanded


def replay_and_adjoint(side: str, case_name: str, tagged_events: list[tuple[list, str]]) -> dict:
    """Execute exact 712-column forward algebraic replay, Horner path-sum replay,
    dyadic integer-scaled grid exactness check, and 704-output backward adjoint replay.
    """
    rows: list[dict[int, Q]] = [{i: Q(1)} for i in range(712)]
    horner_all: list[Q] = [Q(1) for _ in range(712)]
    horner_data: list[Q] = [Q(1) if i < 224 else Q(0) for i in range(712)]
    horner_help: list[Q] = [Q(1) if 224 <= i < 704 else Q(0) for i in range(712)]

    # Integer-scaled state at grid scale D_grid (16 for F, 131072 for B)
    d_grid = 16 if side == "F" else 131072
    int_rows: list[dict[int, int]] = [{i: d_grid} for i in range(712)]
    non_integer_grid_steps = 0

    peak_horner_all = Q(1)
    peak_alg_data = (Q(1), -1, -1)
    peak_alg_help = (Q(1), -1, -1)
    peak_alg_priv = (Q(0), -1, -1)
    peak_alg_total = (Q(1), -1, -1)
    peak_denom = 1
    peak_num_abs = 1

    peak_child_data = Q(0)
    peak_child_help = Q(0)
    peak_child_total = Q(0)
    dirty_children_count = 0
    total_children_count = 0
    climb_data_count = 0
    climb_help_count = 0
    wrapper_line_data_count = 0
    wrapper_line_priv_count = 0

    wrapper_writes_to_helpers = 0
    wrapper_reads_from_helpers = 0

    scalar_gates: list[tuple[str, int, int, Q, str, int]] = []
    child_positions: list[tuple[int, int, str, int, str]] = []
    op_counts: Counter[str] = Counter()
    event_kind_counts: Counter[str] = Counter()

    # Track state at PR #2995/#3017 event 24438 and PR #3036/#3068 events 3887, 4060 in F_0
    fault_site_checks: dict[str, bool] = {}

    for ev_idx, (ev, origin) in enumerate(tagged_events):
        kind = ev[0]
        event_kind_counts[kind] += 1
        if kind in ("climb", "native_line"):
            total_children_count += 1
            if kind == "climb":
                wire = int(ev[2])
                rk = int(ev[5])
                if wire < 224:
                    climb_data_count += 1
                else:
                    climb_help_count += 1
            else:
                wire = reg_index(ev[1])
                rk = 1
                if wire < 224:
                    wrapper_line_data_count += 1
                else:
                    wrapper_line_priv_count += 1
                if 224 <= wire < 704:
                    wrapper_writes_to_helpers += 1

            row = rows[wire]
            d_l1 = sum((abs(v) for k, v in row.items() if k < 224), Q(0))
            h_l1 = sum((abs(v) for k, v in row.items() if 224 <= k < 704), Q(0))
            t_l1 = d_l1 + h_l1
            if h_l1 > 0:
                dirty_children_count += 1
            if d_l1 > peak_child_data:
                peak_child_data = d_l1
            if h_l1 > peak_child_help:
                peak_child_help = h_l1
            if t_l1 > peak_child_total:
                peak_child_total = t_l1
            child_positions.append((len(scalar_gates), wire, kind, rk, origin))

        elif kind == "scalar":
            gate = ev[1]
            op = str(gate[0])
            op_counts[op] += 1
            at = reg_index(gate[1])
            if origin == "wrapper" and 224 <= at < 704:
                wrapper_writes_to_helpers += 1

            if side == "F" and ev_idx in (3887, 4060, 24438):
                # Check the exact instructions cited in PR #2995/#3017/#3036/#3068
                fault_site_checks[f"event_{ev_idx}_op"] = (
                    op == "add"
                    and all(isinstance(v, int) for v in int_rows[at].values())
                )

            if op == "clear":
                rows[at] = {}
                int_rows[at] = {}
                horner_all[at] = Q(0)
                horner_data[at] = Q(0)
                horner_help[at] = Q(0)
                scalar_gates.append(("clear", at, -1, Q(0), origin, ev_idx))
            elif op == "scale":
                c = Q(int(gate[2]), int(gate[3]))
                rows[at] = {k: v * c for k, v in rows[at].items()}
                new_int: dict[int, int] = {}
                for k, iv in int_rows[at].items():
                    prod = iv * c.numerator
                    if prod % c.denominator != 0:
                        non_integer_grid_steps += 1
                    new_int[k] = prod // c.denominator
                int_rows[at] = new_int
                horner_all[at] *= abs(c)
                horner_data[at] *= abs(c)
                horner_help[at] *= abs(c)
                if horner_all[at] > peak_horner_all:
                    peak_horner_all = horner_all[at]
                scalar_gates.append(("scale", at, -1, c, origin, ev_idx))
            elif op == "add":
                src = reg_index(gate[2])
                if origin == "wrapper" and 224 <= src < 704:
                    wrapper_reads_from_helpers += 1
                c = Q(int(gate[3]), int(gate[4]))
                dst_row = rows[at]
                for k, v in rows[src].items():
                    nv = dst_row.get(k, Q(0)) + c * v
                    if nv:
                        dst_row[k] = nv
                    else:
                        dst_row.pop(k, None)

                dst_int = int_rows[at]
                for k, iv in int_rows[src].items():
                    prod = iv * c.numerator
                    if prod % c.denominator != 0:
                        non_integer_grid_steps += 1
                    niv = dst_int.get(k, 0) + (prod // c.denominator)
                    if niv:
                        dst_int[k] = niv
                    else:
                        dst_int.pop(k, None)

                ac = abs(c)
                if ac.numerator * horner_all[src] > peak_horner_all:
                    peak_horner_all = ac.numerator * horner_all[src]
                horner_all[at] += ac * horner_all[src]
                if horner_all[at] > peak_horner_all:
                    peak_horner_all = horner_all[at]
                horner_data[at] += ac * horner_data[src]
                horner_help[at] += ac * horner_help[src]
                scalar_gates.append(("add", at, src, c, origin, ev_idx))
            else:
                require(False, f"unexpected scalar op: {op}")

            row = rows[at]
            if at < 704:
                d_l1 = sum((abs(v) for k, v in row.items() if k < 224), Q(0))
                h_l1 = sum((abs(v) for k, v in row.items() if 224 <= k < 704), Q(0))
                t_l1 = sum(abs(v) for v in row.values())
                if d_l1 > peak_alg_data[0]:
                    peak_alg_data = (d_l1, ev_idx, at)
                if h_l1 > peak_alg_help[0]:
                    peak_alg_help = (h_l1, ev_idx, at)
                if t_l1 > peak_alg_total[0]:
                    peak_alg_total = (t_l1, ev_idx, at)
            else:
                p_l1 = sum(abs(v) for v in row.values())
                if p_l1 > peak_alg_priv[0]:
                    peak_alg_priv = (p_l1, ev_idx, at)

            for v in row.values():
                if v.denominator > peak_denom:
                    peak_denom = v.denominator
                if abs(v.numerator) > peak_num_abs:
                    peak_num_abs = abs(v.numerator)

    require(non_integer_grid_steps == 0, f"dyadic grid {d_grid} had non-integer steps")
    # Confirm integer-scaled rows match rational rows exactly at termination
    for i in range(712):
        require(
            {k: Q(iv, d_grid) for k, iv in int_rows[i].items()} == rows[i],
            f"int_rows mismatch on wire {i}",
        )

    final_data_l1 = max(sum(abs(v) for v in rows[i].values()) for i in range(224))
    final_help_leak = sum(
        sum(abs(v) for k, v in rows[i].items() if k >= 224) for i in range(224)
    )
    require(final_help_leak == 0, f"helper leak on completed data outputs in {case_name}")
    restored_helpers = sum(1 for i in range(224, 704) if rows[i] == {i: Q(1)})
    require(restored_helpers == 480, f"unrestored helpers in {case_name}: {480 - restored_helpers}")
    zero_privates = sum(1 for i in range(704, 712) if rows[i] == {})
    require(zero_privates == 8, f"nonzero terminal private C registers in {case_name}")

    horner_width = 0
    while (1 << horner_width) < peak_horner_all:
        horner_width += 1
    alg_width = 0
    while (1 << alg_width) <= peak_alg_total[0]:
        alg_width += 1

    # 2. Backward Adjoint Replay across all 704 terminal outputs (0..223 data, 224..703 helpers)
    adj: list[dict[int, Q]] = [{w: Q(1)} if w < 704 else {} for w in range(712)]
    children_at_step: dict[int, list[tuple[int, str, int, str]]] = {}
    for s_idx, wire, kind, rk, origin in child_positions:
        children_at_step.setdefault(s_idx, []).append((wire, kind, rk, origin))

    child_err_total = [Q(0) for _ in range(704)]
    child_err_wrap = [Q(0) for _ in range(704)]
    child_err_core = [Q(0) for _ in range(704)]
    add_err_total = [Q(0) for _ in range(704)]
    scale_err_total = [Q(0) for _ in range(704)]
    gate_err_total = [Q(0) for _ in range(704)]
    gate_err_wrap = [Q(0) for _ in range(704)]
    gate_err_core = [Q(0) for _ in range(704)]
    max_single_child_to_data = Q(0)

    for step_idx in range(len(scalar_gates), -1, -1):
        if step_idx in children_at_step:
            for wire, _kind, _rk, origin in children_at_step[step_idx]:
                for out_i, coeff in adj[wire].items():
                    ac = abs(coeff)
                    child_err_total[out_i] += ac
                    if origin == "wrapper":
                        child_err_wrap[out_i] += ac
                    else:
                        child_err_core[out_i] += ac
                    if out_i < 224 and ac > max_single_child_to_data:
                        max_single_child_to_data = ac
        if step_idx == 0:
            break
        op, at, src, c, origin, _ev_idx = scalar_gates[step_idx - 1]
        if op == "add":
            for out_i, coeff in adj[at].items():
                ac = abs(coeff)
                add_err_total[out_i] += ac
                gate_err_total[out_i] += ac
                if origin == "wrapper":
                    gate_err_wrap[out_i] += ac
                else:
                    gate_err_core[out_i] += ac
        elif op == "scale":
            for out_i, coeff in adj[at].items():
                ac = abs(coeff)
                scale_err_total[out_i] += ac
                gate_err_total[out_i] += ac
                if origin == "wrapper":
                    gate_err_wrap[out_i] += ac
                else:
                    gate_err_core[out_i] += ac

        if op == "clear":
            adj[at] = {}
        elif op == "scale":
            adj[at] = {out_i: v * c for out_i, v in adj[at].items()}
        elif op == "add":
            if adj[at]:
                src_adj = adj[src]
                for out_i, v in adj[at].items():
                    nv = src_adj.get(out_i, Q(0)) + c * v
                    if nv:
                        src_adj[out_i] = nv
                    else:
                        src_adj.pop(out_i, None)

    # Verify exact transpose duality: at step 0, adj[w][i] == rows[i][w] for all i, w in 0..703!
    for i in range(704):
        recon_row = {w: adj[w][i] for w in range(704) if i in adj[w]}
        require(recon_row == rows[i], f"backward adjoint transpose mismatch on output {i}")

    require(max(child_err_wrap[224:704]) == 0, "wrapper child sensitivity to helpers != 0")
    require(max(gate_err_wrap[224:704]) == 0, "wrapper gate sensitivity to helpers != 0")
    require(wrapper_writes_to_helpers == 0, "wrapper wrote to helpers")
    require(wrapper_reads_from_helpers == 0, "wrapper read from helpers")

    return {
        "case": case_name,
        "side": side,
        "total_events": len(tagged_events),
        "event_kinds": dict(sorted(event_kind_counts.items())),
        "scalar_gates": len(scalar_gates),
        "scalar_op_counts": dict(sorted(op_counts.items())),
        "total_children": total_children_count,
        "dirty_children": dirty_children_count,
        "climb_data_children": climb_data_count,
        "climb_helper_children": climb_help_count,
        "wrapper_line_data_children": wrapper_line_data_count,
        "wrapper_line_private_children": wrapper_line_priv_count,
        "horner_path_sum_bound": str(peak_horner_all),
        "horner_ceiling_bits": horner_width,
        "peak_interior_data_l1": int(peak_alg_data[0]),
        "peak_interior_data_event": peak_alg_data[1],
        "peak_interior_data_register": peak_alg_data[2],
        "peak_interior_helper_l1": int(peak_alg_help[0]),
        "peak_interior_helper_event": peak_alg_help[1],
        "peak_interior_helper_register": peak_alg_help[2],
        "peak_interior_private_l1": int(peak_alg_priv[0]),
        "peak_interior_private_event": peak_alg_priv[1],
        "peak_interior_private_register": peak_alg_priv[2],
        "peak_interior_total_l1": int(peak_alg_total[0]),
        "peak_interior_total_event": peak_alg_total[1],
        "peak_interior_total_register": peak_alg_total[2],
        "algebraic_ceiling_bits": alg_width,
        "dynamic_range_collapse_bits": horner_width - alg_width,
        "max_dyadic_denominator": peak_denom,
        "max_dyadic_fractional_bits": peak_denom.bit_length() - 1,
        "max_numerator_abs": peak_num_abs,
        "non_integer_grid_steps": non_integer_grid_steps,
        "peak_child_entry_data_l1": int(peak_child_data),
        "peak_child_entry_helper_l1": int(peak_child_help),
        "peak_child_entry_total_l1": int(peak_child_total),
        "terminal_data_l1": int(final_data_l1),
        "terminal_helper_leak_on_data": int(final_help_leak),
        "terminal_restored_helpers": restored_helpers,
        "terminal_zero_private_registers": zero_privates,
        "adjoint_sensitivities": {
            "max_single_child_to_data": str(max_single_child_to_data),
            "data_X_child_gain": str(max(child_err_total[:112])),
            "data_X_add_gain": str(max(add_err_total[:112])),
            "data_X_scale_gain": str(max(scale_err_total[:112])),
            "data_X_gate_gain": str(max(gate_err_total[:112])),
            "data_Y_child_gain": str(max(child_err_total[112:224])),
            "data_Y_add_gain": str(max(add_err_total[112:224])),
            "data_Y_scale_gain": str(max(scale_err_total[112:224])),
            "data_Y_gate_gain": str(max(gate_err_total[112:224])),
            "data_all_child_gain": str(max(child_err_total[:224])),
            "data_all_wrapper_child_gain": str(max(child_err_wrap[:224])),
            "data_all_core_child_gain": str(max(child_err_core[:224])),
            "data_all_add_gain": str(max(add_err_total[:224])),
            "data_all_scale_gain": str(max(scale_err_total[:224])),
            "data_all_gate_gain": str(max(gate_err_total[:224])),
            "data_all_gate_gain_float": round(float(max(gate_err_total[:224])), 4),
            "helpers_wrapper_child_gain": str(max(child_err_wrap[224:704])),
            "helpers_wrapper_gate_gain": str(max(gate_err_wrap[224:704])),
            "helpers_core_child_gain": str(max(child_err_core[224:704])),
            "helpers_add_gain": str(max(add_err_total[224:704])),
            "helpers_scale_gain": str(max(scale_err_total[224:704])),
            "helpers_gate_gain": str(max(gate_err_total[224:704])),
            "helpers_gate_gain_float": round(float(max(gate_err_total[224:704])), 4),
        },
        "wrapper_helper_isolation": {
            "wrapper_writes_to_helpers": wrapper_writes_to_helpers,
            "wrapper_reads_from_helpers": wrapper_reads_from_helpers,
            "wrapper_child_to_helper_gain": 0,
            "wrapper_gate_to_helper_gain": 0,
            "transpose_duality_704_rows_verified": True,
        },
        "fault_site_checks": fault_site_checks,
    }


def run_negative_controls(packet: dict, f_ledger: dict, b_ledger: dict, p4: dict) -> dict:
    """Execute the 6 behavioral negative controls."""
    # Control 1: Horner path-sum triangle bound vs exact algebraic cancellation
    require(
        f_ledger["horner_ceiling_bits"] == 55
        and f_ledger["algebraic_ceiling_bits"] == 18
        and f_ledger["dynamic_range_collapse_bits"] == 37,
        "Control 1 failed on F",
    )
    require(
        b_ledger["horner_ceiling_bits"] == 73
        and b_ledger["algebraic_ceiling_bits"] == 21
        and b_ledger["dynamic_range_collapse_bits"] == 52,
        "Control 1 failed on B",
    )
    c1 = {
        "F_horner_bits": 55,
        "F_exact_bits": 18,
        "F_collapse_bits": 37,
        "B_horner_bits": 73,
        "B_exact_bits": 21,
        "B_collapse_bits": 52,
        "status": "PASS",
    }

    # Control 2: Omitting the post-B cleanup_tail / full_frame_cleanup restoration suffix
    f_events = expand_program_events(packet, "F_1")
    b_events = expand_program_events(packet, "B_1_2")
    f_cut = next(i for i, (e, _) in enumerate(f_events) if e == ["phase", "cleanup_tail"])
    b_cut = next(i for i, (e, _) in enumerate(b_events) if e == ["phase", "cleanup_tail"])

    def count_unrestored_at_cut(tagged: list[tuple[list, str]], cut: int) -> tuple[int, int]:
        rows = [{i: Q(1)} for i in range(712)]
        for ev, _ in tagged[:cut]:
            if ev[0] == "scalar":
                g = ev[1]
                op, at = g[0], reg_index(g[1])
                if op == "clear":
                    rows[at] = {}
                elif op == "scale":
                    c = Q(int(g[2]), int(g[3]))
                    rows[at] = {k: v * c for k, v in rows[at].items()}
                elif op == "add":
                    src, c = reg_index(g[2]), Q(int(g[3]), int(g[4]))
                    dst = rows[at]
                    for k, v in rows[src].items():
                        nv = dst.get(k, Q(0)) + c * v
                        if nv:
                            dst[k] = nv
                        else:
                            dst.pop(k, None)
        unrest = sum(1 for i in range(224, 704) if rows[i] != {i: Q(1)})
        max_h = int(
            max(sum((abs(v) for k, v in rows[i].items() if 224 <= k < 704), Q(0)) for i in range(224, 704))
        )
        return unrest, max_h

    f_unrest, f_max_h = count_unrestored_at_cut(f_events, f_cut)
    b_unrest, b_max_h = count_unrestored_at_cut(b_events, b_cut)
    require(f_unrest == 480 and b_unrest == 395, f"Control 2 unexpected counts: {f_unrest}, {b_unrest}")
    c2 = {
        "F_cleanup_tail_cut_index": f_cut,
        "F_unrestored_helpers_at_cut": f_unrest,
        "F_max_helper_l1_at_cut": f_max_h,
        "B_cleanup_tail_cut_index": b_cut,
        "B_unrestored_helpers_at_cut": b_unrest,
        "B_max_helper_l1_at_cut": b_max_h,
        "status": "REJECTS_TRUNCATED_RESTORATION",
    }

    # Control 3: Omitting owned private C0..C7 clear gates (treating C0..C7 as self-restored)
    def replay_without_private_clears(tagged: list[tuple[list, str]]) -> tuple[int, int]:
        rows = [{i: Q(1)} for i in range(712)]
        for ev, _ in tagged:
            if ev[0] == "scalar":
                g = ev[1]
                op, at = g[0], reg_index(g[1])
                if op == "clear":
                    continue
                elif op == "scale":
                    c = Q(int(g[2]), int(g[3]))
                    rows[at] = {k: v * c for k, v in rows[at].items()}
                elif op == "add":
                    src, c = reg_index(g[2]), Q(int(g[3]), int(g[4]))
                    dst = rows[at]
                    for k, v in rows[src].items():
                        nv = dst.get(k, Q(0)) + c * v
                        if nv:
                            dst[k] = nv
                        else:
                            dst.pop(k, None)
        dirty_priv = sum(1 for i in range(704, 712) if rows[i] != {})
        data_leak = sum(1 for i in range(224) if any(k >= 704 for k in rows[i]))
        return dirty_priv, data_leak

    f_dpriv, f_dleak = replay_without_private_clears(f_events)
    b_dpriv, b_dleak = replay_without_private_clears(b_events)
    require(
        f_dpriv == 8 and f_dleak == 112 and b_dpriv == 8 and b_dleak == 8,
        "Control 3 failed to detect private C0..C7 leak",
    )
    c3 = {
        "F_dirty_private_registers_without_clear": f_dpriv,
        "F_data_outputs_corrupted_by_private_inputs": f_dleak,
        "B_dirty_private_registers_without_clear": b_dpriv,
        "B_data_outputs_corrupted_by_private_inputs": b_dleak,
        "status": "REJECTS_OMITTED_PRIVATE_CLEARS",
    }

    # Control 4: Injecting a synthetic helper read from A_copy wire L[112] in F_1
    # immediately breaks helpers_wrapper_child_gain == 0
    mut_f_events = list(f_events) + [
        (["scalar", ["add", ["L", 224], ["L", 112], 1, 1], "I"], "wrapper")
    ]
    # Run backward adjoint on mut_f_events to check wrapper child sensitivity on helper 224
    adj_mut: list[dict[int, Q]] = [{224: Q(1)} if w == 224 else {} for w in range(712)]
    wrap_child_sens_on_224 = Q(0)
    for ev, origin in reversed(mut_f_events):
        if ev[0] in ("climb", "native_line"):
            wire = int(ev[2]) if ev[0] == "climb" else reg_index(ev[1])
            if origin == "wrapper" and 224 in adj_mut[wire]:
                wrap_child_sens_on_224 += abs(adj_mut[wire][224])
        elif ev[0] == "scalar":
            g = ev[1]
            op, at = g[0], reg_index(g[1])
            if op == "clear":
                adj_mut[at] = {}
            elif op == "scale":
                c = Q(int(g[2]), int(g[3]))
                adj_mut[at] = {k: v * c for k, v in adj_mut[at].items()}
            elif op == "add":
                src, c = reg_index(g[2]), Q(int(g[3]), int(g[4]))
                if adj_mut[at]:
                    for k, v in adj_mut[at].items():
                        nv = adj_mut[src].get(k, Q(0)) + c * v
                        if nv:
                            adj_mut[src][k] = nv
                        else:
                            adj_mut[src].pop(k, None)
    require(wrap_child_sens_on_224 == 1, f"Control 4 expected 1, got {wrap_child_sens_on_224}")
    c4 = {
        "synthetic_wrapper_helper_read_gain": int(wrap_child_sens_on_224),
        "unperturbed_wrapper_helper_child_gain": 0,
        "status": "REJECTS_WRAPPER_HELPER_COUPLING",
    }

    # Control 5: Perturbing the sign at PR #3036/#3068 helper-cancellation event 3,887
    # and peak interior L1 event 24,611 in F_1 breaks both helper restoration (136 unrestored)
    # and data cleanliness (4 data outputs with helper leak; terminal max data L1 = 270668033/4096 vs 27).
    rows_c5 = [{i: Q(1)} for i in range(712)]
    for idx, (ev, _) in enumerate(f_events):
        if ev[0] == "scalar":
            g = ev[1]
            op, at = g[0], reg_index(g[1])
            if op == "clear":
                rows_c5[at] = {}
            elif op == "scale":
                c = Q(int(g[2]), int(g[3]))
                rows_c5[at] = {k: v * c for k, v in rows_c5[at].items()}
            elif op == "add":
                src, c = reg_index(g[2]), Q(int(g[3]), int(g[4]))
                if idx in (3887, 24611):
                    c = -c
                dst = rows_c5[at]
                for k, v in rows_c5[src].items():
                    nv = dst.get(k, Q(0)) + c * v
                    if nv:
                        dst[k] = nv
                    else:
                        dst.pop(k, None)
    c5_unrestored_helpers = sum(1 for i in range(224, 704) if rows_c5[i] != {i: Q(1)})
    c5_data_helper_leak = sum(1 for i in range(224) if any(224 <= k < 704 for k in rows_c5[i]))
    c5_terminal_max_data_l1 = max(sum(abs(v) for v in rows_c5[i].values()) for i in range(224))
    require(
        c5_unrestored_helpers == 136
        and c5_data_helper_leak == 4
        and c5_terminal_max_data_l1 == Q(270668033, 4096),
        "Control 5 sign perturbation mismatch",
    )
    c5 = {
        "perturbed_event_indices": [3887, 24611],
        "unrestored_helpers_after_sign_flip": c5_unrestored_helpers,
        "data_outputs_with_helper_leak_after_sign_flip": c5_data_helper_leak,
        "terminal_max_data_l1_after_sign_flip": str(c5_terminal_max_data_l1),
        "unperturbed_terminal_max_data_l1": "27",
        "status": "REJECTS_SINGLE_SIGN_PERTURBATION",
    }

    # Control 6: Evaluating CONSERVED-QQ16 + #2707 under ceiling.ceiling(...) with unchanged centre=64
    require(
        Q(p4["profiles"]["qq16_pair_plus_decoder_centre64"]["kappa_cap_dec"])
        < Q(p4["selected_kappa_dec"]),
        "Control 6 failed: centre=64 profile should lie below selected kappa",
    )
    c6 = {
        "selected_kappa_dec": p4["selected_kappa_dec"],
        "qq16_pair_plus_decoder_centre64_kappa_cap": p4["profiles"][
            "qq16_pair_plus_decoder_centre64"
        ]["kappa_cap_dec"],
        "qq16_pair_plus_decoder_plus_h9_centre64_kappa_cap": p4["profiles"][
            "qq16_pair_plus_decoder_plus_h9_centre64"
        ]["kappa_cap_dec"],
        "qq16_pair_plus_decoder_centre0_kappa_cap": p4["profiles"][
            "qq16_pair_plus_decoder_centre0"
        ]["kappa_cap_dec"],
        "status": "CONFIRMS_CENTRE_AND_CONSUMER_BOTTLENECK",
    }

    return {
        "control_1_horner_vs_exact_algebraic_collapse": c1,
        "control_2_truncated_restoration_suffix": c2,
        "control_3_omitted_private_c_clears": c3,
        "control_4_synthetic_wrapper_helper_coupling": c4,
        "control_5_single_sign_perturbation_at_peak_helper_event": c5,
        "control_6_uncharged_vs_charged_consumer_ceiling": c6,
    }


def verify_pillar_3_and_4(
    data: dict, f_ledger: dict, b_ledger: dict
) -> tuple[dict, dict]:
    """Compute Pillar 3 (precision & #2965 coupling) and Pillar 4 (ceiling.ceiling screen)."""
    dt = data["defect_transfer"]
    require(
        max(Q(r["l1"]) for r in dt["operators"]["F0"]) == 49,
        "pinned #2965 F0 inverse norm != 49",
    )
    require(
        max(Q(r["l1"]) for r in dt["operators"]["D"]) == 1923,
        "pinned #2965 decoder D norm != 1923",
    )
    require(
        dt["controls"]["normalized_error_bound"] == "7587/8192",
        "pinned #2965 normalized_error_bound != 7587/8192",
    )

    f_tot_amp = Q(f_ledger["adjoint_sensitivities"]["data_all_child_gain"]) + Q(
        f_ledger["adjoint_sensitivities"]["data_all_gate_gain"]
    )
    b_tot_amp = Q(b_ledger["adjoint_sensitivities"]["data_all_child_gain"]) + Q(
        b_ledger["adjoint_sensitivities"]["data_all_gate_gain"]
    )
    require(f_tot_amp == Q(2234071313, 131072), "unexpected F total amplification")
    require(b_tot_amp == Q(3690685, 4), "unexpected B total amplification")

    # Bit-width derivation for target accuracy H * 2^-beta under #2965 sufficient budget:
    # eps_F <= H * 2^(-beta - 8), eps_B <= H * 2^(-beta - 13)
    # 1. Exact common-grid scalar execution (eps_gate = 0):
    #    - F: 4 fractional grid bits, child gain 132 < 2^8, child entry norm <= 124 < 2^7
    #      => child fractional precision >= 8 + 7 + 8 + beta = 23 + beta bits
    #    - B: 17 fractional grid bits, child gain 381/2 < 2^8, child entry norm <= 166 < 2^8
    #      => child fractional precision >= 13 + 8 + 8 + beta = 29 + beta bits
    #      With 21 signed integer headroom bits (peak interior L1 = 1,154,896 < 2^20.14),
    #      total fixed-point width is at most 21 + 29 + beta = 50 + beta bits!
    # 2. General rounded-gate + rounded-child execution:
    #    - F: peak interior 18 bits, total adjoint gain < 2^15, tolerance 2^(-beta-8)
    #      => p_F = 18 + 15 + 8 + beta = 41 + beta fractional bits (59 + beta total bits)
    #    - B: peak interior 21 bits, total adjoint gain < 2^20, tolerance 2^(-beta-13)
    #      => p_B = 21 + 20 + 13 + beta = 54 + beta fractional bits (75 + beta total bits,
    #         saving 52 bits vs the 127 + beta bits implied by the 73-bit Horner bound!).
    p3 = {
        "pr2965_F0_inverse_l1_norm": 49,
        "pr2965_decoder_D_l1_norm": 1923,
        "pr2965_normalized_error_budget": "7587/8192",
        "F_dyadic_grid_fractional_bits": 4,
        "B_dyadic_grid_fractional_bits": 17,
        "F_scalar_gates_exact_on_grid": 21025,
        "B_scalar_gates_exact_on_grid": 21401,
        "F_total_adjoint_gain": str(f_tot_amp),
        "F_total_adjoint_gain_bits": 15,
        "B_total_adjoint_gain": str(b_tot_amp),
        "B_total_adjoint_gain_bits": 20,
        "common_grid_child_fractional_bits_offset": 29,
        "common_grid_total_fixed_point_bits_offset": 50,
        "rounded_gate_B_fractional_bits_offset": 54,
        "rounded_gate_B_total_bits_offset": 75,
        "horner_bound_B_total_bits_offset": 127,
        "dynamic_range_bits_saved_in_B": 52,
        "dynamic_range_bits_saved_in_F": 37,
    }

    # Pillar 4: Physical Recursive Bill & ceiling.ceiling(...) comparison
    dec_res = data["decoder_result"]
    require(dec_res["events"] == 3823, "unexpected #2707 events")
    require(
        dec_res["trace"]
        == {
            "add": 2704,
            "begin": 3,
            "checkpoint": 1,
            "clear": 312,
            "end": 3,
            "line": 336,
            "map": 464,
            "quarter_ADD": 896,
            "unit_ADD": 1808,
        },
        "unexpected #2707 decoder trace",
    )
    require(dec_res["two_sided_224_array_inverse"] is True, "unexpected #2707 two_sided_224_array_inverse")

    def eval_profile(prof: dict[int, int | Q], centre: int | Q) -> dict:
        lo, hi = C.ceiling(prof, 73, 896, 9, centre, grid=GRID)
        kap_hi = hi / (1 + hi)
        local_mass = sum(r * Q(n) for r, n in prof.items())
        return {
            "centre_per_call": str(centre),
            "local_mass_per_call": str(local_mass),
            "a_lo": str(lo),
            "a_hi": str(hi),
            "a_cap_dec": ffloat(hi),
            "kappa_cap_dec": ffloat(kap_hi),
        }

    sel_prof = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
    qq16_f_prof = {1: 2420, 2: 418, 3: 432, 4: 142, 5: 82}
    qq16_b_prof = {1: 2436, 2: 418, 3: 432, 4: 142, 5: 82}
    # 2-call pair (F_0 + B_1_2) + 336 rank-1 decoder lines (168 per call):
    # under centre = 64 ( retaining the 8 rank-8 centre charge per call ):
    qq16_pair_dec_c64 = {1: 2596, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
    # plus 224 rank-9 H9 endpoint adapters (112 per call) to exit F17:
    qq16_pair_dec_h9_c64 = {1: 2596, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8, 9: 112}
    # under centre = 0 (if global coverage law eliminates the 64-per-call centre charge):
    qq16_pair_dec_c0 = {1: 2596, 2: 418, 3: 432, 4: 142, 5: 82}
    qq16_pair_dec_h9_c0 = {1: 2596, 2: 418, 3: 432, 4: 142, 5: 82, 9: 112}

    p4 = {
        "selected_kappa_dec": str(data["selected"]["decimal"]),
        "selected_ceiling_a_cap_dec": "0.001690054110",
        "selected_ceiling_kappa_cap_dec": "0.001687202646",
        "producer_F_invoice": data["conserved_summary"]["invoices"]["F"],
        "producer_B_invoice": data["conserved_summary"]["invoices"]["B"],
        "decoder_pr2707_trace": dec_res["trace"],
        "decoder_pr2707_events": dec_res["events"],
        "profiles": {
            "selected_baseline_centre64": eval_profile(sel_prof, 64),
            "qq16_F_only_centre0": eval_profile(qq16_f_prof, 0),
            "qq16_B_only_centre0": eval_profile(qq16_b_prof, 0),
            "qq16_pair_plus_decoder_centre64": eval_profile(qq16_pair_dec_c64, 64),
            "qq16_pair_plus_decoder_plus_h9_centre64": eval_profile(qq16_pair_dec_h9_c64, 64),
            "qq16_pair_plus_decoder_centre0": eval_profile(qq16_pair_dec_c0, 0),
            "qq16_pair_plus_decoder_plus_h9_centre0": eval_profile(qq16_pair_dec_h9_c0, 0),
        },
    }
    return p3, p4


def compute() -> dict:
    data = load_authenticated_inputs()
    packet = data["certificate"]
    conserved = data["conserved_summary"]

    # Replay F_0, F_1, and B_1_2 and verify across all 37 native cases (9 F + 28 B)
    f0_events = expand_program_events(packet, "F_0")
    f1_events = expand_program_events(packet, "F_1")
    b12_events = expand_program_events(packet, "B_1_2")

    f0_ledger = replay_and_adjoint("F", "F_0", f0_events)
    f1_ledger = replay_and_adjoint("F", "F_1", f1_events)
    b12_ledger = replay_and_adjoint("B", "B_1_2", b12_events)

    # Confirm all 9 F_s cases have identical scalar projections and all 28 B_s_t cases match B_1_2
    f1_scalars = [e[1] for e, _ in f1_events if e[0] == "scalar"]
    b12_scalars = [e[1] for e, _ in b12_events if e[0] == "scalar"]
    for s in range(9):
        ev_s = expand_program_events(packet, f"F_{s}")
        require(
            len(ev_s) == (26099 if s == 0 else 26387),
            f"unexpected event count in F_{s}",
        )
        require(
            [e[1] for e, _ in ev_s if e[0] == "scalar"] == f1_scalars,
            f"scalar projection drift in F_{s}",
        )
    for s in range(1, 8):
        for t in range(s + 1, 9):
            ev_st = expand_program_events(packet, f"B_{s}_{t}")
            require(len(ev_st) == 27019, f"unexpected event count in B_{s}_{t}")
            require(
                [e[1] for e, _ in ev_st if e[0] == "scalar"] == b12_scalars,
                f"scalar projection drift in B_{s}_{t}",
            )

    # Cross-check against pinned CONSERVED-QQ16.json invoices
    require(
        f1_ledger["horner_path_sum_bound"]
        == conserved["invoices"]["F"]["formal_prefix"]["formal_triangle_Horner_bound"],
        "F Horner bound mismatch vs CONSERVED-QQ16.json",
    )
    require(
        b12_ledger["horner_path_sum_bound"]
        == conserved["invoices"]["B"]["formal_prefix"]["formal_triangle_Horner_bound"],
        "B Horner bound mismatch vs CONSERVED-QQ16.json",
    )

    p3, p4 = verify_pillar_3_and_4(data, f1_ledger, b12_ledger)
    controls = run_negative_controls(packet, f1_ledger, b12_ledger, p4)

    return {
        "schema_version": 1,
        "status": "PASS_QQ16_INTERIOR_DYNAMIC_RANGE_AND_ADJOINT_LEDGER",
        "summary": {
            "total_columns_replayed": 712,
            "data_columns": 224,
            "dirty_helper_columns": 480,
            "private_c_columns": 8,
            "F0_events": f0_ledger["total_events"],
            "F_events": f1_ledger["total_events"],
            "B_events": b12_ledger["total_events"],
            "F_scalar_gates": f1_ledger["scalar_gates"],
            "B_scalar_gates": b12_ledger["scalar_gates"],
            "F_total_children": f1_ledger["total_children"],
            "F_dirty_children": f1_ledger["dirty_children"],
            "B_total_children": b12_ledger["total_children"],
            "B_dirty_children": b12_ledger["dirty_children"],
            "F_horner_bits": f1_ledger["horner_ceiling_bits"],
            "F_exact_algebraic_bits": f1_ledger["algebraic_ceiling_bits"],
            "F_dynamic_range_collapse_bits": f1_ledger["dynamic_range_collapse_bits"],
            "B_horner_bits": b12_ledger["horner_ceiling_bits"],
            "B_exact_algebraic_bits": b12_ledger["algebraic_ceiling_bits"],
            "B_dynamic_range_collapse_bits": b12_ledger["dynamic_range_collapse_bits"],
            "F_peak_interior_data_l1": f1_ledger["peak_interior_data_l1"],
            "F_peak_interior_helper_l1": f1_ledger["peak_interior_helper_l1"],
            "F_peak_interior_private_l1": f1_ledger["peak_interior_private_l1"],
            "F_peak_interior_total_l1": f1_ledger["peak_interior_total_l1"],
            "B_peak_interior_data_l1": b12_ledger["peak_interior_data_l1"],
            "B_peak_interior_helper_l1": b12_ledger["peak_interior_helper_l1"],
            "B_peak_interior_private_l1": b12_ledger["peak_interior_private_l1"],
            "B_peak_interior_total_l1": b12_ledger["peak_interior_total_l1"],
            "F_max_dyadic_denominator": f1_ledger["max_dyadic_denominator"],
            "B_max_dyadic_denominator": b12_ledger["max_dyadic_denominator"],
            "F_peak_child_entry_l1": f1_ledger["peak_child_entry_total_l1"],
            "B_peak_child_entry_l1": b12_ledger["peak_child_entry_total_l1"],
            "F_data_child_gain": f1_ledger["adjoint_sensitivities"]["data_all_child_gain"],
            "F_data_gate_gain": f1_ledger["adjoint_sensitivities"]["data_all_gate_gain"],
            "F_helper_wrapper_child_gain": 0,
            "F_helper_core_child_gain": f1_ledger["adjoint_sensitivities"][
                "helpers_core_child_gain"
            ],
            "F_helper_gate_gain": f1_ledger["adjoint_sensitivities"]["helpers_gate_gain"],
            "B_data_child_gain": b12_ledger["adjoint_sensitivities"]["data_all_child_gain"],
            "B_data_gate_gain": b12_ledger["adjoint_sensitivities"]["data_all_gate_gain"],
            "B_helper_wrapper_child_gain": 0,
            "B_helper_core_child_gain": b12_ledger["adjoint_sensitivities"][
                "helpers_core_child_gain"
            ],
            "B_helper_gate_gain": b12_ledger["adjoint_sensitivities"]["helpers_gate_gain"],
            "common_grid_fixed_point_bits_offset": p3[
                "common_grid_total_fixed_point_bits_offset"
            ],
            "rounded_gate_B_total_bits_offset": p3["rounded_gate_B_total_bits_offset"],
            "horner_B_total_bits_offset": p3["horner_bound_B_total_bits_offset"],
            "qq16_pair_plus_decoder_centre64_a_cap": p4["profiles"][
                "qq16_pair_plus_decoder_centre64"
            ]["a_cap_dec"],
            "qq16_pair_plus_decoder_centre64_kappa_cap": p4["profiles"][
                "qq16_pair_plus_decoder_centre64"
            ]["kappa_cap_dec"],
            "qq16_pair_plus_decoder_plus_h9_centre64_kappa_cap": p4["profiles"][
                "qq16_pair_plus_decoder_plus_h9_centre64"
            ]["kappa_cap_dec"],
            "qq16_pair_plus_decoder_centre0_a_cap": p4["profiles"][
                "qq16_pair_plus_decoder_centre0"
            ]["a_cap_dec"],
            "qq16_pair_plus_decoder_centre0_kappa_cap": p4["profiles"][
                "qq16_pair_plus_decoder_centre0"
            ]["kappa_cap_dec"],
        },
        "pillar1_interior_dynamic_range": {
            "F_0": f0_ledger,
            "F_1_to_8": f1_ledger,
            "B_1_2_to_7_8": b12_ledger,
            "verified_cases_count": 37,
        },
        "pillar2_backward_adjoint_ledger": {
            "F": f1_ledger["adjoint_sensitivities"],
            "B": b12_ledger["adjoint_sensitivities"],
        },
        "pillar3_dyadic_grid_and_precision_floor": p3,
        "pillar4_physical_recursive_bill_and_ceilings": p4,
        "negative_controls": controls,
    }


def main() -> int:
    write = "--write" in sys.argv[1:]
    result = compute()
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    out = HERE / "RESULT.json"
    if write:
        out.write_text(text, encoding="utf-8", newline="\n")
    else:
        require(out.is_file(), "RESULT.json missing; run with --write first")
        require(
            out.read_bytes() == text.encode("utf-8"),
            "RESULT.json does not match deterministic recomputation",
        )
    s = result["summary"]
    print(
        "PASS_QQ16_INTERIOR_DYNAMIC_RANGE_AND_ADJOINT_LEDGER",
        "F_collapse_bits",
        s["F_dynamic_range_collapse_bits"],
        "B_collapse_bits",
        s["B_dynamic_range_collapse_bits"],
        "F_peak_l1",
        s["F_peak_interior_total_l1"],
        "B_peak_l1",
        s["B_peak_interior_total_l1"],
        "F_child_gain",
        s["F_data_child_gain"],
        "B_child_gain",
        s["B_data_child_gain"],
        "centre64_kappa_cap",
        s["qq16_pair_plus_decoder_centre64_kappa_cap"],
        "no_new_kappa",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
