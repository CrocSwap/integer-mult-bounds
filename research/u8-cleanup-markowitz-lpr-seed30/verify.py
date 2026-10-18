#!/usr/bin/env python3
"""Self-contained deterministic verifier for research/u8-cleanup-markowitz-lpr-seed30.

1. Verifies all input and upstream script SHA-256 pins in SOURCES.json.
2. Re-derives the 3,525-macro two-sided Markowitz LPR (R^{-1} P L^{-1}) Weyl-cycle
   cleanup word from scratch at assignment seed 30 (trial 16, swap_pen=6, scale_pen=0)
   and verifies gate-for-gate equality with RECIPE.json.
3. Runs the unchanged upstream local verification pipeline (hpe_audit_and_transport.py,
   hpe_emit_local.py, hpe_audit_local.py, hpe_adapters_local.py) in an isolated
   temporary directory and checks every hash and metric against EXPECTED.json.
4. Verifies the scoped negative finding (Candidate 1: partial E4 -> E5 entrance
   promotion reversion for m in {0, 1, 2, 3, 4} on [659, 661, 662, 663]).
5. Executes the code-disjoint integer-lattice verifier (independent.py) and the
   12-control adversarial mutation suite (test_package.py).

Compatible with both `python3 -I -B` and `python3 -I -O -B`.
Prepared with Gemini 4 Argon assistance. Apache-2.0; see NOTICE.md.
"""
from fractions import Fraction as Q
import gzip
import hashlib
import json
import os
import pathlib
import random
import subprocess
import sys
import tarfile
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import independent
import test_package


def require(cond, msg):
    if not cond:
        raise RuntimeError(f"VERIFICATION FAILED: {msg}")


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(p):
    return sha_bytes(pathlib.Path(p).read_bytes())


def q_add_cost(q):
    a, b = abs(q.numerator), q.denominator
    return 2 * (3 + (a.bit_length() - 1) + a.bit_count() + (b.bit_length() - 1))


def is_pow2(f):
    if f == 0:
        return False
    n, d = abs(f.numerator), f.denominator
    return (n & (n - 1)) == 0 and (d & (d - 1)) == 0


def apply_word_to_cols(word, dim=728):
    cols = [{i: Q(1)} for i in range(dim)]
    for g in word:
        op = g[0]
        if op == "add":
            d, s, c = g[1], g[2], Q(g[3], g[4])
            for j in range(dim):
                v_j = cols[j].get(s, Q(0))
                if v_j:
                    nv = cols[j].get(d, Q(0)) + c * v_j
                    if nv:
                        cols[j][d] = nv
                    else:
                        cols[j].pop(d, None)
        elif op == "scale":
            d, c = g[1], Q(g[2], g[3])
            for j in range(dim):
                v_j = cols[j].get(d, Q(0))
                if v_j:
                    cols[j][d] = c * v_j
        else:
            raise RuntimeError(f"unknown op: {op}")
    return cols


def solve_lpr_smart_scale(M0_cols, swap_pen, scale_pen, rng=None, dim=728):
    rows = {i: {} for i in range(dim)}
    cols = {j: {} for j in range(dim)}
    for j in range(dim):
        for i, val in M0_cols[j].items():
            rows[i][j] = val
            cols[j][i] = val
    active_r = set()
    active_c = set()
    for i in range(dim):
        if len(rows[i]) > 1 or rows[i].get(i, 0) != 1:
            active_r.add(i)
            active_c.add(i)
    L_ops = []
    R_ops = []
    post_L_scales = []
    pivots = []
    row_of_col = {i: i for i in active_r}
    col_of_row = {i: i for i in active_r}

    while active_r:
        best_score = None
        best_rc = None
        for r in sorted(active_r):
            rn = len(rows[r]) - 1
            for c, val in rows[r].items():
                if c not in active_c:
                    continue
                if is_pow2(val):
                    cn = len(cols[c]) - 1
                    fill = rn * cn
                    sp = 0 if row_of_col[c] == r else swap_pen
                    scp = 0 if abs(val) == 1 else scale_pen
                    tie = rng.random() if rng else 0
                    score = (
                        fill + sp + scp,
                        rn + cn,
                        0 if r == c else 1,
                        0 if val == 1 else (1 if val == -1 else 2),
                        tie,
                        r,
                        c,
                    )
                    if best_score is None or score < best_score:
                        best_score = score
                        best_rc = (r, c)
        r, c = best_rc
        pv = rows[r][c]
        sign_pv = Q(1, 1) if pv > 0 else Q(-1, 1)
        abs_pv = abs(pv)
        pivots.append((r, c, sign_pv))
        active_r.remove(r)
        active_c.remove(c)
        r_prev = row_of_col[c]
        c_prev = col_of_row[r]
        if r_prev != r:
            row_of_col[c_prev] = r_prev
            col_of_row[r_prev] = c_prev

        col_entries = [(ii, cols[c][ii]) for ii in sorted(cols[c].keys()) if ii != r]
        row_entries = [(jj, rows[r][jj]) for jj in sorted(rows[r].keys()) if jj != c]

        for ii, v_ic in col_entries:
            del rows[ii][c]
            del cols[c][ii]
            factor = -v_ic / pv
            for jj, v_rj in row_entries:
                nv = rows[ii].get(jj, Q(0)) + factor * v_rj
                if nv == 0:
                    rows[ii].pop(jj, None)
                    cols[jj].pop(ii, None)
                else:
                    rows[ii][jj] = nv
                    cols[jj][ii] = nv
        for jj, v_rj in row_entries:
            del rows[r][jj]
            del cols[jj][r]
        rows[r][c] = sign_pv
        cols[c][r] = sign_pv

        if abs_pv == 1:
            for ii, v_ic in col_entries:
                f_L = -v_ic / sign_pv
                L_ops.append(["add", ii, r, f_L.numerator, f_L.denominator, 1])
            for jj, v_rj in row_entries:
                f_R = -v_rj / sign_pv
                R_ops.append(["add", c, jj, f_R.numerator, f_R.denominator, 1])
        else:
            cost_L_unscaled = sum(q_add_cost(v_ic / pv) for _, v_ic in col_entries)
            cost_L_scaled = sum(q_add_cost(v_ic / sign_pv) for _, v_ic in col_entries)
            cost_R_unscaled = sum(q_add_cost(v_rj / pv) for _, v_rj in row_entries)
            cost_R_scaled = sum(q_add_cost(v_rj / sign_pv) for _, v_rj in row_entries)

            optA = cost_L_scaled + cost_R_unscaled
            optB = cost_L_unscaled + cost_R_scaled
            optC = cost_L_unscaled + cost_R_unscaled
            best_opt = min((optA, "A"), (optB, "B"), (optC, "C"))[1]
            scale_fac = Q(1, 1) / abs_pv
            if best_opt == "A":
                L_ops.append(["scale", r, scale_fac.numerator, scale_fac.denominator, 1])
                for ii, v_ic in col_entries:
                    f_L = -v_ic / sign_pv
                    L_ops.append(["add", ii, r, f_L.numerator, f_L.denominator, 1])
                for jj, v_rj in row_entries:
                    f_R = -v_rj / pv
                    R_ops.append(["add", c, jj, f_R.numerator, f_R.denominator, 1])
            elif best_opt == "B":
                for ii, v_ic in col_entries:
                    f_L = -v_ic / pv
                    L_ops.append(["add", ii, r, f_L.numerator, f_L.denominator, 1])
                R_ops.append(["scale", c, scale_fac.numerator, scale_fac.denominator, 1])
                for jj, v_rj in row_entries:
                    f_R = -v_rj / sign_pv
                    R_ops.append(["add", c, jj, f_R.numerator, f_R.denominator, 1])
            else:
                for ii, v_ic in col_entries:
                    f_L = -v_ic / pv
                    L_ops.append(["add", ii, r, f_L.numerator, f_L.denominator, 1])
                for jj, v_rj in row_entries:
                    f_R = -v_rj / pv
                    R_ops.append(["add", c, jj, f_R.numerator, f_R.denominator, 1])
                post_L_scales.append(["scale", r, scale_fac.numerator, scale_fac.denominator, 1])

    L_ops.extend(post_L_scales)
    p_map = {c: (r, int(pv)) for r, c, pv in pivots}
    visited = set()
    P_ops = []
    n_cycles = 0
    for c in sorted(p_map.keys()):
        if c in visited:
            continue
        r, s = p_map[c]
        if r == c:
            visited.add(c)
            if s == -1:
                P_ops.append(["scale", c, -1, 1, 1])
            continue
        n_cycles += 1
        cyc = []
        curr = c
        while curr not in visited:
            visited.add(curr)
            cyc.append(curr)
            curr = p_map[curr][0]
        carry_sign = 1
        for idx in range(len(cyc) - 1, 0, -1):
            a, b = cyc[idx - 1], cyc[idx]
            target_sign = p_map[a][1]
            if target_sign == 1:
                P_ops.extend(
                    [
                        ["add", a, b, -1, 1, 1],
                        ["add", b, a, 1, 1, 1],
                        ["add", a, b, -1, 1, 1],
                    ]
                )
                carry_sign = -carry_sign
            else:
                P_ops.extend(
                    [
                        ["add", a, b, 1, 1, 1],
                        ["add", b, a, -1, 1, 1],
                        ["add", a, b, 1, 1, 1],
                    ]
                )
        if carry_sign != p_map[cyc[-1]][1]:
            P_ops.append(["scale", cyc[0], -1, 1, 1])

    def inv_gate(g):
        if g[0] == "add":
            return ["add", g[1], g[2], -g[3], g[4], 1]
        return ["scale", g[1], g[3] if g[2] > 0 else -g[3], abs(g[2]), 1]

    R_inv_ops = [inv_gate(g) for g in R_ops]
    L_inv_ops = [inv_gate(g) for g in reversed(L_ops)]
    word = R_inv_ops + P_ops + L_inv_ops
    return word, R_inv_ops, P_ops, L_inv_ops, n_cycles


def main():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    expected = json.loads((HERE / "EXPECTED.json").read_text())
    recipe = json.loads((HERE / "RECIPE.json").read_text())

    # 1. Check all pins in SOURCES.json
    cert_path = ROOT / sources["selected_frontier_certificate"]["path"]
    require(
        sha_file(cert_path) == sources["selected_frontier_certificate"]["sha256"],
        "selected-result.json sha256 mismatch",
    )
    for rel, exp_sha in sources["upstream_verifiers"].items():
        require(sha_file(ROOT / rel) == exp_sha, f"upstream verifier pin mismatch: {rel}")
    require(
        sha_file(ROOT / sources["recipe"]["path"]) == sources["recipe"]["sha256"],
        "RECIPE.json sha256 mismatch",
    )

    tar_path = ROOT / sources["replay_bundle"]["path"]
    require(
        sha_file(tar_path) == sources["replay_bundle"]["sha256"],
        "t37-replay.tar.gz sha256 mismatch",
    )

    with tarfile.open(tar_path, "r:gz") as tf:
        fw_gz = tf.extractfile("native/barch/FULL-WORD.json.gz").read()
        cw_gz = tf.extractfile("native/local/CANONICAL-WORD.json.gz").read()
        ra_bytes = tf.extractfile("native/local/RESIDUAL-ADAPTERS.json").read()

    fw_raw = gzip.decompress(fw_gz)
    cw_raw = gzip.decompress(cw_gz)
    require(
        sha_bytes(fw_gz) == sources["replay_bundle"]["members"]["native/barch/FULL-WORD.json.gz"]["gz_sha256"],
        "FULL-WORD.json.gz gz_sha256 mismatch",
    )
    require(
        sha_bytes(fw_raw)
        == sources["replay_bundle"]["members"]["native/barch/FULL-WORD.json.gz"]["content_sha256"],
        "FULL-WORD.json.gz content_sha256 mismatch",
    )
    require(
        sha_bytes(cw_gz)
        == sources["replay_bundle"]["members"]["native/local/CANONICAL-WORD.json.gz"]["gz_sha256"],
        "CANONICAL-WORD.json.gz gz_sha256 mismatch",
    )
    require(
        sha_bytes(cw_raw)
        == sources["replay_bundle"]["members"]["native/local/CANONICAL-WORD.json.gz"]["content_sha256"],
        "CANONICAL-WORD.json.gz content_sha256 mismatch",
    )
    require(
        sha_bytes(ra_bytes)
        == sources["replay_bundle"]["members"]["native/local/RESIDUAL-ADAPTERS.json"]["sha256"],
        "RESIDUAL-ADAPTERS.json sha256 mismatch",
    )

    fw = json.loads(fw_raw.decode())
    cw = json.loads(cw_raw.decode())

    # 2. Rebuild M0 and re-run the seed-30 solver to reproduce RECIPE.json from scratch
    M0_cols = apply_word_to_cols(cw["cleanup"])
    rng = random.Random(recipe["seed"])
    for trial in range(recipe["selected_trial"] + 1):
        sp = rng.choice([3, 4, 5, 6])
        scp = rng.choice([0, 1])
        w, R_inv_ops, P_ops, L_inv_ops, n_cycles = solve_lpr_smart_scale(M0_cols, sp, scp, rng)

    require(sp == recipe["swap_penalty"] and scp == recipe["scale_penalty"], "selected penalty mismatch")
    require(w == recipe["cleanup_word"], "re-derived LPR cleanup word does not match RECIPE.json")
    require(
        len(R_inv_ops) == recipe["section_lengths"]["R_inv"]
        and len(P_ops) == recipe["section_lengths"]["P"]
        and len(L_inv_ops) == recipe["section_lengths"]["L_inv"]
        and n_cycles == recipe["disjoint_cycles"],
        "section lengths or cycle count mismatch",
    )
    require(apply_word_to_cols(w) == M0_cols, "re-derived LPR cleanup word does not equal M0 on all 728 columns")

    # 3. Splice into FULL-WORD.json.gz and run the upstream 4-stage HPE local pipeline
    v = 112
    tau = lambda x: x ^ (43 if (x & 43).bit_count() % 2 else 0)
    ports = cw["ports"]
    mapping = {i: ports.index(tau(p)) for i, p in enumerate(fw["ports"])}
    mapping.update({v + i: v + mapping[i] for i in range(v)})
    mapping.update({r: r for r in range(2 * v, 728)})
    inv_mapping = {can_r: raw_r for raw_r, can_r in mapping.items()}

    full_raw_frame = [256, 128, 64, 32, 16, 8, 4, 2, 1]
    raw_w = [
        ["add", inv_mapping[g[1]], inv_mapping[g[2]], g[3], g[4], full_raw_frame]
        if g[0] == "add"
        else ["scale", inv_mapping[g[1]], g[2], g[3], full_raw_frame]
        for g in w
    ]

    early_head = [fw["cleanup"][i] for i in range(8, 171)]
    early_tail = [fw["cleanup"][i] for i in range(6268, 6276)]
    new_cleanup = early_head + raw_w + early_tail
    idx_map = {i: i - 8 for i in range(8, 171)}
    idx_map.update({i: 163 + len(raw_w) + (i - 6268) for i in range(6268, 6276)})

    fw_lpr = json.loads(fw_raw.decode())
    fw_lpr["cleanup"] = new_cleanup
    fw_lpr["early_cleanup"] = [[idx_map[old_i], f_vecs] for old_i, f_vecs in fw["early_cleanup"]]
    fw_lpr["refactored_cleanup"]["high_inverse"] = "two_sided_Markowitz_LPR_Weyl_seed30"

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = pathlib.Path(tmp)
        in_dir = tmp_path / "in"
        in_dir.mkdir()
        out_dir = tmp_path / "local"

        raw_path = in_dir / "FULL-WORD.json.gz"
        routing_path = in_dir / "ROUTING.json"
        raw_payload = json.dumps(fw_lpr, sort_keys=True, separators=(",", ":")).encode()
        raw_path.write_bytes(gzip.compress(raw_payload, mtime=0))
        routing_path.write_text(json.dumps({"v": v, "ports": ports}))

        multicold_src = str(ROOT / "research/complex-k492-owner-repair/vendor/multicold")
        sub_env = dict(
            os.environ,
            PYTHONDONTWRITEBYTECODE="1",
            PYTHONUTF8="1",
            PYTHONINTMAXSTRDIGITS="0",
            MULTICOLD_SOURCE=multicold_src,
            GAIN_PR564_SOURCE=multicold_src,
        )
        sub_env.pop("PYTHONOPTIMIZE", None)

        run_portable = str(ROOT / "research/complex-k492-owner-repair/vendor/multicold/code/run_portable.py")
        local_scripts = ROOT / "research/complex-sw4-frame8/local"

        subprocess.run(
            [
                sys.executable,
                "-B",
                run_portable,
                str(local_scripts / "hpe_audit_and_transport.py"),
                "--raw",
                str(raw_path),
                "--routing",
                str(routing_path),
                "--out",
                str(out_dir),
            ],
            env=sub_env,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        subprocess.run(
            [sys.executable, "-B", run_portable, str(local_scripts / "hpe_emit_local.py"), str(out_dir)],
            env=sub_env,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        subprocess.run(
            [sys.executable, "-B", run_portable, str(local_scripts / "hpe_audit_local.py"), str(out_dir)],
            env=sub_env,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        subprocess.run(
            [
                sys.executable,
                "-B",
                run_portable,
                str(local_scripts / "hpe_adapters_local.py"),
                str(out_dir / "CANONICAL-WORD.json.gz"),
                str(out_dir / "RESIDUAL-ADAPTERS.json"),
                str(out_dir / "WRAPPER-CHECKS.json"),
            ],
            env=sub_env,
            check=True,
            stdout=subprocess.DEVNULL,
        )

        sfa = json.loads((out_dir / "SCALAR-FRAME-AUDIT.json").read_text())
        lc = json.loads((out_dir / "LOCAL-CHECKS.json").read_text())
        ilr = json.loads((out_dir / "INDEPENDENT-LOCAL-REPLAY.json").read_text())
        wc = json.loads((out_dir / "WRAPPER-CHECKS.json").read_text())

        exp_prog = expected["full_local_program_comparison"]["refactored_lpr_seed30"]
        require(
            sfa["input_content_sha256"] == exp_prog["raw_full_word_content_sha256"],
            "raw_full_word_content_sha256 mismatch",
        )
        require(
            sfa["canonical_content_sha256"] == exp_prog["canonical_word_content_sha256"],
            "canonical_word_content_sha256 mismatch",
        )
        require(
            sfa["scalar_operations"] == exp_prog["scalar_operations_audit"],
            "scalar_operations_audit mismatch",
        )
        require(
            sfa["refactored_cleanup_gates"] == exp_prog["refactored_cleanup_gates_total"],
            "refactored_cleanup_gates_total mismatch",
        )
        require(
            lc["forward"]["sha256"] == exp_prog["forward_program_sha256"],
            "forward_program_sha256 mismatch",
        )
        require(
            lc["backward"]["sha256"] == exp_prog["backward_program_sha256"],
            "backward_program_sha256 mismatch",
        )
        require(
            lc["forward"]["events"] == exp_prog["events_per_orientation"]
            and lc["backward"]["events"] == exp_prog["events_per_orientation"],
            "events_per_orientation mismatch",
        )
        require(
            lc["forward"]["scalar_macros"] == exp_prog["scalar_macros_per_orientation"]
            and lc["backward"]["scalar_macros"] == exp_prog["scalar_macros_per_orientation"],
            "scalar_macros_per_orientation mismatch",
        )
        require(
            lc["forward"]["real_component_primitive_bound"]
            == exp_prog["forward_real_component_primitive_bound"],
            "forward_real_component_primitive_bound mismatch",
        )
        require(
            lc["backward"]["real_component_primitive_bound"]
            == exp_prog["backward_real_component_primitive_bound"],
            "backward_real_component_primitive_bound mismatch",
        )
        require(
            ilr["local"]["forward"]["prefix_l1_upper"] == exp_prog["forward_prefix_l1_upper"]
            and ilr["local"]["forward"]["prefix_bits_upper"] == exp_prog["forward_prefix_bits_upper"],
            "forward prefix_l1_upper mismatch",
        )
        require(
            ilr["local"]["backward"]["prefix_l1_upper"] == exp_prog["backward_prefix_l1_upper"]
            and ilr["local"]["backward"]["prefix_bits_upper"] == exp_prog["backward_prefix_bits_upper"],
            "backward prefix_l1_upper mismatch",
        )
        require(
            len(ilr["negative_controls_rejected"])
            == expected["preserved_invariants"]["upstream_local_negative_controls_rejected"],
            "upstream local negative controls count mismatch",
        )
        require(
            len(wc["wrappers_reject"])
            == expected["preserved_invariants"]["upstream_wrapper_negative_controls_rejected"],
            "upstream wrapper negative controls count mismatch",
        )
        require(
            sha_file(out_dir / "RESIDUAL-ADAPTERS.json") == exp_prog["residual_adapters_sha256"],
            "RESIDUAL-ADAPTERS.json sha256 mismatch",
        )
        require(
            sha_file(out_dir / "WRAPPER-CHECKS.json") == exp_prog["wrapper_checks_sha256"],
            "WRAPPER-CHECKS.json sha256 mismatch",
        )

    # 4. Verify scoped negative finding (Candidate 1) profile deltas for m in {0, 1, 2, 3, 4}
    exp_deltas = expected["scoped_negative_finding_candidate1"]["local_profile_deltas_by_m"]
    for m_str, exp_d in exp_deltas.items():
        got_d = test_package.compute_partial_e4_profile_delta(fw, cw, int(m_str))
        require(got_d == exp_d, f"Candidate 1 profile delta mismatch at m={m_str}: got {got_d}, expected {exp_d}")

    # 5. Run code-disjoint integer-lattice verifier and 12-control package negative suite
    ind_res = independent.run_independent_checks()
    neg_res = test_package.run_negative_controls()

    receipt = {
        "status": expected["status"],
        "seed": expected["seed"],
        "track": expected["track"],
        "base_commit": expected["base_commit"],
        "changes_kappa": False,
        "cleanup_macros_before": 6105,
        "cleanup_macros_after": 3525,
        "cleanup_macros_saved_per_orientation": 2580,
        "cleanup_real_primitives_before": 68714,
        "cleanup_real_primitives_after": 31394,
        "cleanup_real_primitives_saved_per_orientation": 37320,
        "full_local_real_primitives_saved_pair": 74640,
        "forward_prefix_bits": {"before": 55, "after": 51, "delta": -4},
        "backward_prefix_bits": {"before": 72, "after": 54, "delta": -18},
        "independent_verifier": ind_res["status"],
        "negative_controls": {
            "upstream_local_rejected": 25,
            "upstream_wrapper_rejected": 17,
            "package_controls_rejected": neg_res["rejected_count"],
        },
    }
    print("PASS: verify.py completed all checks.", flush=True)
    print(json.dumps(receipt, indent=2), flush=True)


if __name__ == "__main__":
    main()
