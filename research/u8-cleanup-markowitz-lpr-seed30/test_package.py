#!/usr/bin/env python3
"""Adversarial and negative-control test suite for u8-cleanup-markowitz-lpr-seed30.

Tests 12 distinct mutations / adversarial controls:
1. drop_R_inv_gate: dropping a right-elimination gate from R^{-1} breaks operator equality.
2. drop_P_cycle_gate: dropping an add gate from a Weyl signed cycle in P breaks operator equality.
3. drop_L_inv_gate: dropping a left-elimination gate from L^{-1} breaks operator equality.
4. flip_weyl_cycle_sign: flipping a Weyl signed swap W_+ to W_- breaks column sign exactness.
5. reverse_R_inv_order: reversing R^{-1} execution order breaks non-commuting column eliminations.
6. cleanup_touches_target: touching a target register (112..223) in cleanup is rejected.
7. cleanup_touches_hpe_helper: touching a hyperplane-ended helper (e.g. 225) in cleanup is rejected.
8. cleanup_wrong_frame: a cleanup gate at frame != 1 (FULL) is rejected.
9. non_dyadic_add_denominator: an add gate with denominator 3 is rejected.
10. non_power_of_two_scale_numerator: a scale gate with numerator 3 is rejected.
11. self_addition_gate: an add gate with dst == src is rejected.
12. partial_e4_promotion_claim: claiming that m in {1, 2, 3} partial E4 promotion avoids extra rank-2/rank-3 climbs is rejected by the climb-splitting check.

Prepared with Gemini 4 Argon assistance. Apache-2.0; see NOTICE.md.
"""
import copy
import gzip
import json
import pathlib
import sys
import tarfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import independent


def require(cond, msg):
    if not cond:
        raise RuntimeError(f"NEGATIVE CONTROL SUITE FAILED: {msg}")


def check_cleanup_candidate(candidate_word, base_rows_fwd, base_rows_bwd, hpe_helpers, n=728, v=112):
    for idx, g in enumerate(candidate_word):
        regs = [int(g[1])] + ([int(g[2])] if g[0] == "add" else [])
        independent.require(int(g[-1]) == 1, f"gate {idx} not at frame 1")
        for r in regs:
            independent.require(not (v <= r < 2 * v), f"touches target register {r}")
            independent.require(r not in hpe_helpers, f"touches HPE helper {r}")
        independent.horner_real_primitives(g)

    rows_fwd = independent.eval_word_int(candidate_word, n, backward=False)
    independent.require(rows_fwd == base_rows_fwd, "forward operator mismatch")
    rows_bwd = independent.eval_word_int(candidate_word, n, backward=True)
    independent.require(rows_bwd == base_rows_bwd, "backward operator mismatch")


def compute_partial_e4_profile_delta(fw, cw, m):
    v = 112
    n = 728
    tau = lambda x: x ^ (43 if (x & 43).bit_count() % 2 else 0)
    ports = cw["ports"]
    mapping = {i: ports.index(tau(p)) for i, p in enumerate(fw["ports"])}
    mapping.update({v + i: v + mapping[i] for i in range(v)})
    mapping.update({r: r for r in range(2 * v, n)})

    def basis(vs):
        pivots = {}
        for x in vs:
            for k in sorted(pivots, reverse=True):
                if (x >> k) & 1:
                    x ^= pivots[k]
            if x:
                k = x.bit_length() - 1
                for j in pivots:
                    if (pivots[j] >> k) & 1:
                        pivots[j] ^= x
                pivots[k] = x
        return tuple(pivots[k] for k in sorted(pivots, reverse=True))

    e4_raw = [298, 170, 102, 30]
    group = [659, 661, 662, 663]
    reverted = set(group[:m])

    w_mod = copy.deepcopy(fw)
    for h in reverted:
        w_mod["start_extra"][str(h)] = e4_raw

    blk = w_mod["B"][420:432]
    g_e4 = []
    g_e5 = []
    for g in blk:
        if g[2] in reverted:
            g_c = list(g)
            g_c[-1] = e4_raw
            g_e4.append(g_c)
        else:
            g_e5.append(g)
    w_mod["B"][420:432] = g_e4 + g_e5

    full = tuple(1 << i for i in range(8, -1, -1))
    frames = [(), full]
    frame_ids = {(): 0, full: 1}

    def fid(vecs):
        b = basis(vecs)
        if b not in frame_ids:
            frame_ids[b] = len(frames)
            frames.append(b)
        return frame_ids[b]

    def tr(e):
        e = list(e)
        e[1] = mapping[e[1]]
        if e[0] == "add":
            e[2] = mapping[e[2]]
        if e[-1] is not None:
            e[-1] = fid([tau(x) for x in e[-1]])
        return e

    can_A = [tr(e) for e in w_mod["A"]]
    can_B = [tr(e) for e in w_mod["B"]]
    can_cut = [tr(e) for e in w_mod["cut"]]
    can_tail = [tr(w_mod["cleanup"][i][:-1] + [f]) for i, f in w_mod["early_cleanup"]]
    start = [fid([p]) for p in ports] + [0] * (v + 504)
    for r_str, fr in w_mod["start_extra"].items():
        start[int(r_str)] = fid([tau(x) for x in fr])
    final = (
        [1] * v
        + [fid(x for x in range(1, 512) if (x & p).bit_count() % 2 == 0) for p in ports]
        + [1] * 504
    )
    for r_str, fr in w_mod["helper_final"].items():
        final[int(r_str)] = fid([tau(x) for x in fr])

    centers = [mapping[r] for r in w_mod["centers"]]
    center_frames = [fid(tau(x) for x in fr) for fr in w_mod["center_frames"]]
    levels = {mapping[v + int(t)] - v: fid(tau(x) for x in fr) for t, fr in w_mod["target_levels"].items()}

    cur = list(start)
    paid = {}

    def climb(r, f):
        old = cur[r]
        independent.require(basis(frames[old] + frames[f]) == frames[f], f"nonmonotone climb on {r}")
        if old != f:
            deg = len(frames[f]) - len(frames[old])
            paid[deg] = paid.get(deg, 0) + 1
            cur[r] = f

    for e in can_A:
        for r in [e[1]] + ([e[2]] if e[0] == "add" else []):
            climb(r, e[-1])
    for r, fr in zip(centers, center_frames):
        served = {levels.get(e[1] - v, 0) for e in can_cut if e[2] == r}
        old = fr
        for f in sorted(served, key=lambda x: -len(frames[x])):
            if old != f:
                deg = len(frames[old]) - len(frames[f])
                paid[deg] = paid.get(deg, 0) + 1
                old = f
    for e in can_B:
        for r in [e[1]] + ([e[2]] if e[0] == "add" else []):
            climb(r, e[-1])
    for e in can_tail:
        for r in [e[1]] + ([e[2]] if e[0] == "add" else []):
            climb(r, e[-1])
    for r, f in enumerate(final):
        climb(r, f)

    base_prof = {int(k): val for k, val in fw["report"]["local_profile"].items()}
    delta = {}
    for k in sorted(set(paid.keys()) | set(base_prof.keys())):
        d = paid.get(k, 0) - base_prof.get(k, 0)
        if d != 0:
            delta[str(k)] = d
    return delta


def run_negative_controls():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    recipe = json.loads((HERE / "RECIPE.json").read_text())

    tar_path = ROOT / sources["replay_bundle"]["path"]
    with tarfile.open(tar_path, "r:gz") as tf:
        fw = json.loads(gzip.decompress(tf.extractfile("native/barch/FULL-WORD.json.gz").read()).decode())
        cw = json.loads(gzip.decompress(tf.extractfile("native/local/CANONICAL-WORD.json.gz").read()).decode())

    n = 728
    v = 112
    hpe_helpers = {r for r in range(2 * v, n) if cw["final"][r] != 1}
    lpr_word = recipe["cleanup_word"]
    r_len = recipe["section_lengths"]["R_inv"]
    p_len = recipe["section_lengths"]["P"]

    base_rows_fwd = independent.eval_word_int(lpr_word, n, backward=False)
    base_rows_bwd = independent.eval_word_int(lpr_word, n, backward=True)

    # Positive sanity check first
    check_cleanup_candidate(lpr_word, base_rows_fwd, base_rows_bwd, hpe_helpers)

    rejected = []

    def expect_reject(name, mut_fn, expected_substr):
        cand = copy.deepcopy(lpr_word)
        mut_fn(cand)
        try:
            check_cleanup_candidate(cand, base_rows_fwd, base_rows_bwd, hpe_helpers)
        except RuntimeError as exc:
            require(
                expected_substr in str(exc),
                f"control {name} failed with unexpected message '{exc}' (expected '{expected_substr}')",
            )
            rejected.append(name)
            return
        raise RuntimeError(f"NEGATIVE CONTROL ACCEPTED: {name}")

    # 1. Drop an R^{-1} gate
    expect_reject("drop_R_inv_gate", lambda w: w.pop(0), "operator mismatch")

    # 2. Drop a Weyl cycle gate in P
    expect_reject("drop_P_cycle_gate", lambda w: w.pop(r_len), "operator mismatch")

    # 3. Drop an L^{-1} gate
    expect_reject("drop_L_inv_gate", lambda w: w.pop(r_len + p_len), "operator mismatch")

    # 4. Flip a Weyl signed swap sign in P
    def flip_weyl(w):
        g = w[r_len]
        g[3] = -g[3]

    expect_reject("flip_weyl_cycle_sign", flip_weyl, "operator mismatch")

    # 5. Reverse R^{-1} gate execution order
    def rev_r_inv(w):
        w[:r_len] = list(reversed(w[:r_len]))

    expect_reject("reverse_R_inv_order", rev_r_inv, "operator mismatch")

    # 6. Touch a target register in cleanup
    expect_reject(
        "cleanup_touches_target",
        lambda w: w.append(["add", 0, 112, 1, 1, 1]),
        "touches target register 112",
    )

    # 7. Touch a hyperplane-ended helper in cleanup
    expect_reject(
        "cleanup_touches_hpe_helper",
        lambda w: w.append(["add", 0, 225, 1, 1, 1]),
        "touches HPE helper 225",
    )

    # 8. Wrong frame in cleanup
    expect_reject(
        "cleanup_wrong_frame",
        lambda w: w[0].__setitem__(-1, 0),
        "not at frame 1",
    )

    # 9. Non-dyadic add denominator
    expect_reject(
        "non_dyadic_add_denominator",
        lambda w: w[0].__setitem__(4, 3),
        "non-dyadic add denominator",
    )

    # 10. Non-power-of-two scale numerator
    def bad_scale(w):
        idx = next(i for i, g in enumerate(w) if g[0] == "scale")
        w[idx][2] = 3

    expect_reject("non_power_of_two_scale_numerator", bad_scale, "invalid scale")

    # 11. Self-addition gate
    expect_reject(
        "self_addition_gate",
        lambda w: w.insert(0, ["add", 0, 0, 1, 1, 1]),
        "self-addition gate",
    )

    # 12. Partial E4 promotion climb-splitting control
    try:
        for m in (1, 2, 3):
            delta = compute_partial_e4_profile_delta(fw, cw, m)
            if delta.get("3", 0) > 0 and delta.get("2", 0) > 0:
                raise RuntimeError(
                    f"INDEPENDENT CHECK FAILED: partial E4 promotion m={m} splits 1->5 climbs into 1->4->5 with delta={delta}"
                )
    except RuntimeError as exc:
        require("splits 1->5 climbs" in str(exc), f"unexpected message: {exc}")
        rejected.append("partial_e4_promotion_claim")
    else:
        raise RuntimeError("NEGATIVE CONTROL ACCEPTED: partial_e4_promotion_claim")

    require(len(rejected) == 12, f"expected 12 rejected controls, got {len(rejected)}")
    result = {
        "status": "PASS_PACKAGE_NEGATIVE_CONTROLS",
        "rejected_count": len(rejected),
        "rejected_controls": rejected,
    }
    print(json.dumps(result, indent=2), flush=True)
    return result


if __name__ == "__main__":
    run_negative_controls()
