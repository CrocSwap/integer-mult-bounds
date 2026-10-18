#!/usr/bin/env python3
"""H2-sem admission audit for the PR848 copy-path helper-temp sharing wrap.

One replacement H2/K implication, falsification-first, on the pinned selected
R439 word (bitE8mut-p111-tuned) and the unchanged xcheck_p owner checker:

  (I) The PR848 control-C1 wrap (seed-42 best pair 277 -> 434) and the composed
      seed-42 greedy disjoint matching satisfy PR1194's H2-sem conditions 1-3,
      with the semantic boundary equation (x,y,h) -> (x,y+N h,h) exact on all
      661 basis columns (= arbitrary dirty inputs by F2 linearity), so the
      semantic K check passes where the literal extractor fails.

Falsification attempts on dirty inputs and chronological cuts: unrestored temp,
wrong-restore operand, premature (mid-body) restore, and a target-feeding-helper
wrap that preserves the scalar operator but lies outside H2-sem condition 2.

Apache-2.0. Prepared by Aaron Wang with help from opencode.
"""
import copy
import gzip
import hashlib
import importlib.util
import itertools
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
WORD = ROOT / "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
XCHECK = ROOT / "research/e8-bit-p111-tuned/code/xcheck_p.py"
SEED = 42


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def check_pins():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for entry in pins["files"]:
        if entry["usage"] != "input":
            continue
        data = (ROOT / entry["path"]).read_bytes()
        need(hashlib.sha256(data).hexdigest() == entry["sha256"],
             "source pin mismatch: " + entry["path"])


def load_checker():
    spec = importlib.util.spec_from_file_location("r439_xcheck_p", XCHECK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def nominate_d(word, seed):
    """PR848's exhaustive oriented-pair census over D rows, then one seeded greedy matching."""
    v, ret = word["v"], set(word["ret"])
    rows = [set(g[2]) for g in word["D"]]
    pool = sorted(set.union(*rows) - ret - set(range(2 * v)))
    need(min(pool) >= 2 * v, "D reads a non-helper")
    scored = []
    for a, b in itertools.permutations(pool, 2):
        saving = sum((1 if b in row else -1) for row in rows if a in row) - 2
        if saving > 0:
            scored.append((saving, a, b))
    random.Random(seed).shuffle(scored)
    scored.sort(key=lambda item: -item[0])
    chosen, used, total = [], set(), 0
    for saving, a, b in scored:
        if a not in used and b not in used:
            chosen.append([a, b])
            used.update((a, b))
            total += saving
    return chosen, {"operands": len(pool), "oriented_pairs": len(pool) * (len(pool) - 1),
                    "positive_pairs": len(scored),
                    "best_saving": scored[0][0] if scored else 0,
                    "best_pair": list(scored[0][1:]) if scored else [],
                    "matching_pairs": len(chosen), "matching_saving": total}


def construct_d(word, pairs, restore=True, restore_map=None, cut=None):
    """Wrap the whole D section in prep/restore helper temporaries (PR848 C1 shape).

    restore=False drops the restore gates; restore_map remaps each pair's restore
    destination; cut inserts the restores after body[:cut] and the rest after.
    """
    v, ret = word["v"], set(word["ret"])
    rows_pool = set().union(*(set(g[2]) for g in word["D"]))
    flat = [r for pair in pairs for r in pair]
    need(all(len(pair) == 2 for pair in pairs), "malformed pair")
    need(len(flat) == len(set(flat)), "pairs must be disjoint")
    need(all(r >= 2 * v and r not in ret for r in flat) and set(flat) <= rows_pool,
         "temps must be non-retained D-operand helpers")
    pre = [[0, a, [b]] for a, b in pairs]
    if restore_map is None:
        back = [[0, a, [b]] for a, b in pairs]
    else:
        back = [[0, restore_map[a], [b]] for a, b in pairs]
    body = []
    for frame, dst, srcs in word["D"]:
        need(frame == 0 and v <= dst < 2 * v, "D gate not frame-zero target write")
        row = set(srcs)
        for a, b in pairs:
            if a in row:
                row.symmetric_difference_update({b})
        body.append([frame, dst, sorted(row)])
    if cut is None:
        mid = body
        tail = []
    else:
        mid, tail = body[:cut], body[cut:]
    result = copy.deepcopy(word)
    result["D"] = pre + mid + (list(reversed(back)) if restore else []) + tail
    return result


def d_shape(word, checker):
    """Exact D operator on all basis columns plus its extracted semantic N and frames at the cut."""
    w = checker.Word(word)
    val, cur, _ = w.replay(sections=("D",), frames_on=True)
    v, R = w.v, w.R
    smask = ((1 << R) - 1) << (2 * v)
    ymask = ((1 << v) - 1) << v
    xmask = (1 << v) - 1
    shape_ok = all(val[s] == 1 << s for s in range(v)) and \
        all(val[r] == 1 << r for r in range(2 * v, 2 * v + R)) and \
        all(val[v + t] & (ymask | xmask) == 1 << (v + t) for t in range(v))
    N = [val[v + t] & smask for t in range(v)]
    return val, cur, shape_ok, N


def h2sem_conditions(word):
    """H2-sem conditions 1-2 of research/r439-semantic-d-contract-seed10/PROOF.md."""
    v, n = word["v"], 2 * word["v"] + word["R"]
    is_y = lambda r: v <= r < 2 * v
    cond1 = all(g[0] == 0 and v <= g[1] < n and g[1] not in g[2] and len(set(g[2])) == len(g[2])
                and all(v <= s < n for s in g[2]) for g in word["D"])
    cond2 = not any(not is_y(g[1]) and any(is_y(s) for s in g[2]) for g in word["D"])
    return cond1, cond2


def raw_K(word, checker):
    """Helper response K of raw (A, scatter, B), as in the literal extractor's comparison side."""
    w = checker.Word(word)
    raw, _, _ = w.replay(sections=("A", "scatter", "B"), frames_on=False)
    smask = ((1 << w.R) - 1) << (2 * w.v)
    return [raw[w.v + t] & smask for t in range(w.v)]


def literal_N(word):
    """Gate-local sum-of-source-reads extraction, exactly as the inherited K_equals_D check."""
    v = word["v"]
    N = [0] * v
    for g in word["D"]:
        if v <= g[1] < 2 * v:
            for s in g[2]:
                N[g[1] - v] ^= 1 << s
    return N


def reads(word):
    return sum(len(g[2]) for g in word["D"])


def main():
    need(__debug__, "run without -O: the inherited checker requires assertions")
    check_pins()
    word = json.loads(gzip.decompress(WORD.read_bytes()))
    checker = load_checker()
    controls = []

    # Baseline: the pinned word passes every inherited flag; this is the PR1194
    # virtual splice (literal A/scatter/B/C with the original target-only D).
    _, _, _, H0, C0, _ = checker.check(word)
    need(all(H0.values()) and all(C0.values()), "baseline H1-H5/U-J-K-C failed")
    val0, cur0, shape0, N0 = d_shape(word, checker)
    need(shape0, "baseline D operator is not (x, y + N h, h)")
    K0 = raw_K(word, checker)
    need(N0 == K0, "baseline semantic N != raw K")
    controls.append("baseline word passes all inherited flags and the virtual-splice premises")

    matching, census = nominate_d(word, SEED)
    need(census["best_pair"] == [277, 434] and census["best_saving"] == 65,
         "PR848 best pair moved: %s" % census["best_pair"])
    need(census["matching_pairs"] == 205 and census["matching_saving"] == 6231,
         "PR848 greedy matching moved: %s" % [census["matching_pairs"], census["matching_saving"]])

    def audit(label, variant, admitted, expected_failed):
        cond1, cond2 = h2sem_conditions(variant)
        val, cur, shape_ok, N = d_shape(variant, checker)
        operator_ok = (val == val0)
        frames_ok = (cur == cur0)
        need(all(variant[k] == word[k] for k in word if k != "D"), label + ": non-D sections moved")
        _, _, _, H, C, _ = checker.check(variant)
        failed = sorted(k for k, v_ in list(H.items()) + list(C.items()) if not v_)
        if admitted:
            need(cond1 and cond2 and shape_ok and operator_ok and frames_ok,
                 label + ": H2-sem premises failed")
            need(N == N0 == K0, label + ": semantic K mismatch")
            need(failed == expected_failed,
                 label + ": unexpected inherited flags " + repr(failed))
            need((literal_N(variant) != N0) == ("K_equals_D" in expected_failed),
                 label + ": literal extractor disagreement does not match the flags")
        else:
            need(not (cond1 and cond2 and shape_ok and operator_ok and frames_ok and N == N0),
                 label + ": expected an H2-sem failure")
        return {"cond1_zero_frame_distinct_operands": cond1,
                "cond2_no_target_feeds_helper_or_source": cond2,
                "boundary_operator_exact": operator_ok and shape_ok,
                "frames_at_cut_equal": frames_ok,
                "semantic_K_equals_raw_K": N == K0 == N0,
                "literal_N_equals_semantic_N": literal_N(variant) == N0,
                "inherited_flag_failures": failed,
                "d_source_reads": reads(variant)}

    base_reads = reads(word)

    # (I) smallest falsifying instance first: the single best pair 277 -> 434.
    c1 = construct_d(word, [matching[0]])
    r_c1 = audit("C1 pair 277->434", c1, admitted=True,
                 expected_failed=["H2_D_frame0_targets_from_helpers", "K_equals_D"])

    # Bounded extension: the full seed-42 greedy disjoint matching.
    full = construct_d(word, matching)
    r_full = audit("greedy 205-pair matching", full, admitted=True,
                   expected_failed=["H2_D_frame0_targets_from_helpers", "K_equals_D"])
    need(r_full["d_source_reads"] == base_reads - 6231,
         "matching read delta is not -6231: %d" % (r_full["d_source_reads"] - base_reads))
    need(r_c1["d_source_reads"] == base_reads - 65,
         "pair read delta is not -65: %d" % (r_c1["d_source_reads"] - base_reads))

    # F1: unrestored helper temp (PR848 C3 shape).
    unrestored = construct_d(word, [matching[0]], restore=False)
    val_u, _, _, _ = d_shape(unrestored, checker)
    need(val_u != val0, "unrestored temp preserved the operator")
    try:
        checker.check(unrestored)
    except checker.Reject:
        controls.append("F1 unrestored helper temp rejected at endpoints")
    else:
        raise ValueError("negative control accepted: unrestored helper temp")

    # F2: wrong restore operand (dirty-helper counterexample: some helper column moves).
    wrong = construct_d(word, [matching[0]], restore_map={matching[0][0]: matching[0][0] + 1})
    val_w, _, _, _ = d_shape(wrong, checker)
    need(val_w != val0, "wrong restore operand preserved the operator")
    controls.append("F2 wrong-restore operand breaks the boundary equation on a dirty helper column")

    # F3: premature restore at a chronological cut inside the body.
    cut = construct_d(word, [matching[0]], cut=1)
    val_c, _, _, _ = d_shape(cut, checker)
    need(val_c != val0, "premature restore preserved the operator")
    controls.append("F3 mid-body restore (chronological cut inside the wrap) breaks the boundary equation")

    # F4: target-feeding-helper wrap, span-restricted to close before the fed
    # target's own (single) D gate so the scalar operator is preserved exactly.
    # H2-sem condition 2 (retained no-target-feedback) alone rejects it: the
    # boundary probe for any weaker replacement that drops that clause.
    a, b = matching[0]
    t_reg = word["D"][-1][1]
    k = len(word["D"]) - 1
    need(sum(1 for g in word["D"] if g[1] == t_reg) == 1, "fed target not written exactly once")
    body4 = []
    for i, g in enumerate(word["D"]):
        row = set(g[2])
        if i < k and a in row:
            row.symmetric_difference_update({t_reg})
        body4.append([g[0], g[1], sorted(row)])
    feed = copy.deepcopy(word)
    feed["D"] = [[0, a, [t_reg]]] + body4[:k] + [[0, a, [t_reg]]] + body4[k:]
    r_feed = audit("F4 target-feeding-helper wrap", feed, admitted=False, expected_failed=None)
    need(r_feed["boundary_operator_exact"], "F4 was supposed to preserve the scalar operator")
    need(not r_feed["cond2_no_target_feeds_helper_or_source"], "F4 unexpectedly passes condition 2")
    need(r_feed["cond1_zero_frame_distinct_operands"], "F4 unexpectedly fails condition 1")
    need(r_feed["semantic_K_equals_raw_K"], "F4 unexpectedly breaks the semantic K equality")
    controls.append("F4 target-feeding-helper wrap operator-preserving but outside H2-sem condition 2")

    # F5: source-feeding-helper wrap (sources are constant through D). The scalar
    # operator is again exact, but the framed replay rejects the wrap outright:
    # a source sits at its own line frame, and a frame-0 read is a non-nested
    # climb. This is the chronological/frame counterexample to any replacement
    # that drops H2-sem condition 1 and relies on the boundary equation alone.
    s_reg = 0
    body5 = []
    for g in word["D"]:
        row = set(g[2])
        if a in row:
            row.symmetric_difference_update({s_reg})
        body5.append([g[0], g[1], sorted(row)])
    sfeed = copy.deepcopy(word)
    sfeed["D"] = [[0, a, [s_reg]]] + body5 + [[0, a, [s_reg]]]
    val_s, _, _ = checker.Word(sfeed).replay(sections=("D",), frames_on=False)
    need(val_s == val0, "F5 was supposed to preserve the scalar operator")
    cond1_s, cond2_s = h2sem_conditions(sfeed)
    need(not cond1_s and cond2_s, "F5 unexpected condition pattern")
    try:
        d_shape(sfeed, checker)
    except checker.Reject as exc:
        f5_reject = str(exc)
        need("climb not nested" in f5_reject, "F5 rejected for an unexpected reason: " + f5_reject)
    else:
        raise ValueError("negative control accepted: source-feeding helper wrap")
    r_sfeed = {"scalar_operator_exact": True, "cond1_zero_frame_distinct_operands": cond1_s,
               "cond2_no_target_feeds_helper_or_source": cond2_s,
               "framed_replay_rejection": f5_reject,
               "d_source_reads": reads(sfeed)}
    controls.append("F5 source-feeding helper wrap: operator exact, framed replay rejects the frame-0 source read")

    # Positive width control: PR848 C2 target-temp wrap is also admitted (+2 reads).
    target, helper = word["D"][0][1], matching[0][1]
    c2 = copy.deepcopy(word)
    c2["D"] = [[0, target, [helper]]] + [list(g) for g in word["D"]] + [[0, target, [helper]]]
    r_c2 = audit("C2 target-temp wrap", c2, admitted=True, expected_failed=[])
    need(r_c2["d_source_reads"] == base_reads + 2, "C2 cost is not exactly +2")
    controls.append("C2 target-temp wrap admitted with exactly +2 reads (no saving)")

    report = {
        "status": "PASS_R439_COPYSHARE_H2SEM_ADMISSION",
        "assignment_nonce": "df6f572bc7d7dbccbe487fe013268a12",
        "task_id": "bit-helper-contract",
        "scope_status": "refined",
        "columns": 2 * word["v"] + word["R"],
        "word_canonical_sha256": hashlib.sha256(canonical(word)).hexdigest(),
        "pr848_census": census,
        "baseline_d_source_reads": base_reads,
        "implication_I_single_pair_277_434": r_c1,
        "implication_I_greedy_matching_205_pairs": r_full,
        "control_c2_target_temp": r_c2,
        "f4_target_feed_probe": r_feed,
        "f5_source_feed_probe": r_sfeed,
        "bridge": {
            "virtual_splice_flags_all_pass": True,
            "continuation_state_and_frames_equal_at_D_A_cut": True,
            "pr1194_proof": "research/r439-semantic-d-contract-seed10/PROOF.md",
        },
        "negative_and_positive_controls": controls,
        "kappa_claim": "none",
    }
    certificate = HERE / "CERTIFICATE.json"
    if certificate.exists():
        need(report == json.loads(certificate.read_text()), "certificate mismatch")
    else:
        (HERE / "DRAFT-REPORT.json").write_text(json.dumps(report, indent=2) + "\n")
        print("draft report written; inspect DRAFT-REPORT.json, then freeze as CERTIFICATE.json")
    print("PASS_R439_COPYSHARE_H2SEM_ADMISSION pair=277->434 saving=%d matching_pairs=%d "
          "matching_saving=%d columns=%d controls=%d no_new_kappa"
          % (census["best_saving"], census["matching_pairs"], census["matching_saving"],
             2 * word["v"] + word["R"], len(controls)))


if __name__ == "__main__":
    main()
