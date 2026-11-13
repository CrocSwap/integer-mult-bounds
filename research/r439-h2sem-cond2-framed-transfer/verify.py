#!/usr/bin/env python3
"""H2-F: PR1194's H2-sem condition 2 is not used by the framed transfer.

On the pinned selected R439 word and the unchanged xcheck_p owner checker, the
F4-shaped target-feeding-helper wrap of research/r439-copyshare-h2sem-admission
passes every semantic premise of the substitution bridge (zero-frame condition
1, complete boundary operator on all 661 basis columns, identical state and
frames at the D/A cut, semantic N = K) and every conclusion component of the
interleaved scalar-interface lemma (U, J, Uinv on W0; K semantically), and
fails only the global syntactic flags H1_no_target_feeds_z,
H2_D_frame0_targets_from_helpers and K_equals_D, exactly as recorded in the
predecessor certificate. The hypothesis restriction "no target feeds a helper
inside D" (H2-sem condition 2) is therefore not exercised anywhere in the
transfer: by the R420/#543 lemma text, H1's proof role is confined to the
z-gate transvection induction over the gates of W0 = (A, scatter, B) (and
C = U^-1), all of which are outside D and byte-identical to the baseline whose
flags all pass. F5-shaped source feeds stay inadmissible through condition 1
(distinct operands drawn from targets and helpers) and the framed replay's
nested-climb legality, not through condition 2.

New negative controls show the semantic conditions carry the load that
condition 2 was conservatively holding for target-column dirt: an
uncompensated feed (the fed helper's row reads stay dirty), a feed compensated
by the wrong target, and a restore moved past the fed target's own gate all
break the complete-operator check on explicit columns, while the F4 wrap
itself remains exact.

Apache-2.0. Prepared by Abhinav Ramachandran (geckods) with substantial
assistance from a Hermes agent (GLM-5.3). The word, checker and the
predecessor package research/r439-copyshare-h2sem-admission (its verify.py,
CERTIFICATE.json and F4/F5 construction) and
research/r439-semantic-d-contract-seed10/PROOF.md are consumed as pinned,
unmodified sources.
"""
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
H2SEM_DIR = ROOT / "research/r439-copyshare-h2sem-admission"
H2SEM_CERT = H2SEM_DIR / "CERTIFICATE.json"
WORD = ROOT / "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_pins():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for entry in pins["files"]:
        if entry["usage"] != "input":
            continue
        data = (ROOT / entry["path"]).read_bytes()
        need(hashlib.sha256(data).hexdigest() == entry["sha256"],
             "source pin mismatch: " + entry["path"])


def build_feed(word, a, t_reg, k, comp_reg=None, compensate=True, restore_after_k=False):
    """The F4 target-feeding-helper wrap, factor for factor as in the
    predecessor package's inline construction, plus the dial positions used
    by the negative controls.

    prep: a ^= t_reg (the feed; a becomes a0 ^ t0 on basis columns).
    body: every row i < k that reads a gains t_reg as an extra operand when
    compensate=True, so its a-read is compensated (a ^ t = a0); with
    comp_reg set, the wrong target is used instead.
    restore: a ^= t_reg, placed before gate k (reading the still-unmodified
    target) or, when restore_after_k=True, after it (reading t_new).
    """
    if comp_reg is None:
        comp_reg = t_reg
    need(comp_reg not in set().union(*(set(g[2]) for g in word["D"])),
         "compensation target already read by D")
    body = []
    for i, g in enumerate(word["D"]):
        row = set(g[2])
        if compensate and i < k and a in row:
            row.add(comp_reg)
        body.append([g[0], g[1], sorted(row)])
    feed = copy.deepcopy(word)
    if restore_after_k:
        feed["D"] = [[0, a, [t_reg]]] + body[:k] + body[k:] + [[0, a, [t_reg]]]
    else:
        feed["D"] = [[0, a, [t_reg]]] + body[:k] + [[0, a, [t_reg]]] + body[k:]
    return feed


def main():
    need(__debug__, "run without -O: the inherited checker requires assertions")
    check_pins()
    word = json.loads(gzip.decompress(WORD.read_bytes()))
    h2sem = load_module(H2SEM_DIR / "verify.py", "h2sem_verify")
    checker = h2sem.load_checker()
    cert = json.loads(H2SEM_CERT.read_text())["f4_target_feed_probe"]
    controls = []

    # Baseline: the pinned word passes every inherited flag; this is the
    # PR1194 virtual splice (literal A/scatter/B/C with the original
    # target-only D), on which the interleaved lemma is invoked.
    val0, cur0, shape0, N0 = h2sem.d_shape(word, checker)
    need(shape0, "baseline D operator is not (x, y + N h, h)")
    _, _, _, H0, C0, _ = checker.check(word)
    need(all(H0.values()) and all(C0.values()), "baseline flags failed")
    K0 = h2sem.raw_K(word, checker)
    need(N0 == K0, "baseline semantic N != raw K")
    controls.append("baseline word passes all inherited flags and the virtual-splice premises")

    matching, census = h2sem.nominate_d(word, 42)
    need(census["best_pair"] == [277, 434] and census["best_saving"] == 65,
         "PR848 best pair moved")
    a, _b = matching[0]
    t_reg = word["D"][-1][1]
    k = len(word["D"]) - 1
    need(sum(1 for g in word["D"] if g[1] == t_reg) == 1, "fed target not written exactly once")

    # (I) the F4-shaped target-feeding wrap, rebuilt through the same
    # construction as the predecessor certificate: every semantic premise and
    # every conclusion component holds; only the global syntactic flags fail.
    feed = build_feed(word, a, t_reg, k)
    cond1, cond2 = h2sem.h2sem_conditions(feed)
    val, cur, shape_ok, N = h2sem.d_shape(feed, checker)
    _, _, _, H, C, _ = checker.check(feed)
    failed = sorted(k2 for k2, v2 in list(H.items()) + list(C.items()) if not v2)
    need(cond1, "F4 fails zero-frame/direct-operand condition 1")
    need(not cond2, "F4 unexpectedly satisfies condition 2")
    need(shape_ok and val == val0 and cur == cur0, "F4 breaks the D-prefix equivalence")
    need(N == N0 == K0, "F4 breaks the semantic K equality")
    need(failed == cert["inherited_flag_failures"],
         "F4 inherited failures diverge from the pinned certificate: " + repr(failed))
    need(h2sem.reads(feed) == cert["d_source_reads"], "F4 source reads diverge")
    need(all(feed[key] == word[key] for key in word if key != "D"),
         "F4 modified a non-D section")
    need(H0["H1_no_target_feeds_z"], "baseline global H1 did not pass")
    h1_w0c = all(feed[key] == word[key] for key in word if key != "D") and \
        H0["H1_no_target_feeds_z"]
    need(h1_w0c, "H1 restricted to W0 and C failed")
    compensated_rows = sum(1 for i, g in enumerate(word["D"]) if i < k and a in set(g[2]))
    admission = {
        "cond1_zero_frame_distinct_operands": cond1,
        "cond2_no_target_feeds_helper_or_source": False,
        "boundary_operator_exact": bool(shape_ok and val == val0),
        "frames_at_cut_equal": cur == cur0,
        "semantic_K_equals_raw_K": bool(N == K0 == N0),
        "h1_restricted_to_W0_and_C": True,
        "conclusion_U_J_Uinv_flags_pass": all(C[f] for f in C if f != "K_equals_D"),
        "inherited_flag_failures": failed,
        "compensated_a_rows_before_fed_gate": compensated_rows,
        "d_source_reads": h2sem.reads(feed),
    }
    need(admission["boundary_operator_exact"] and admission["frames_at_cut_equal"]
         and admission["semantic_K_equals_raw_K"] and admission["h1_restricted_to_W0_and_C"],
         "H2-F admission premises failed")
    controls.append("F4 target-feeding wrap admitted under H2-F; "
                    "only the global syntactic flags H1_no_target_feeds_z, "
                    "H2_D_frame0_targets_from_helpers, K_equals_D fail, as pinned")

    # N1: uncompensated feed. The fed helper stays dirty (a0 ^ t0) through the
    # body, every a-reading row shifts on the fed target's column, and the
    # complete-operator check must catch it: target-column dirt through the
    # helper is exactly what conditions 3 (boundary) sees.
    n1 = build_feed(word, a, t_reg, k, compensate=False)
    val1, _, shape1, _ = h2sem.d_shape(n1, checker)
    diff1 = sorted(i for i in range(len(val0)) if val1[i] != val0[i])
    need(val1 != val0, "uncompensated feed preserved the operator")
    need(diff1 and all(word["v"] <= d < 2 * word["v"] for d in diff1),
         "uncompensated feed broke something other than target columns: " + repr(diff1))
    controls.append("N1 uncompensated feed rejected: %d target columns moved by the "
                    "fed target's dirt (first: %d)" % (len(diff1), diff1[0]))

    # N2: feed compensated by the wrong target. The compensation operand is
    # pinned by the complete-column check, not by any gate-local rule.
    a_row_dsts = {g[1] for g in word["D"] if a in set(g[2])}
    other_t = next(g[1] for g in word["D"] if g[1] != t_reg and g[1] not in a_row_dsts)
    need(other_t != t_reg, "no second target available")
    n2 = build_feed(word, a, t_reg, k, comp_reg=other_t)
    val2, _, _, _ = h2sem.d_shape(n2, checker)
    diff2 = sorted(i for i in range(len(val0)) if val2[i] != val0[i])
    need(val2 != val0, "wrong compensation target preserved the operator")
    need(diff2 and all(word["v"] <= d < 2 * word["v"] for d in diff2),
         "wrong compensation target broke something other than target columns")
    controls.append("N2 wrong compensation target rejected on %d target columns" % len(diff2))

    # N3: restore moved past the fed target's own gate (span crosses the
    # boundary the F4 shape respects). The restore now reads t_new, so the
    # helper row itself is no longer identity: the cut-state clauses bite.
    n3 = build_feed(word, a, t_reg, k, restore_after_k=True)
    val3, _, shape3, _ = h2sem.d_shape(n3, checker)
    diff3 = sorted(i for i in range(len(val0)) if val3[i] != val0[i])
    need(val3 != val0, "late restore preserved the operator")
    need(not shape3 and a in diff3,
         "late restore must break the fed helper's identity row")
    controls.append("N3 late restore (span crossing the fed target's own gate) rejected; "
                   "the fed helper's identity row breaks")

    # F5 recheck: source-feeding wrap. The raw operator is exact, but the
    # framed replay rejects the frame-0 source read outright, and condition 1
    # (operands drawn from targets and helpers) already excludes it. What
    # condition 2 was conservatively covering is covered here without it.
    s_reg = 0
    body5 = []
    for g in word["D"]:
        row = set(g[2])
        if a in row:
            row.add(s_reg)
        body5.append([g[0], g[1], sorted(row)])
    sfeed = copy.deepcopy(word)
    sfeed["D"] = [[0, a, [s_reg]]] + body5 + [[0, a, [s_reg]]]
    val_s, _, _ = checker.Word(sfeed).replay(sections=("D",), frames_on=False)
    need(val_s == val0, "F5 was supposed to preserve the raw scalar operator")
    cond1_s, cond2_s = h2sem.h2sem_conditions(sfeed)
    need(not cond1_s and cond2_s, "F5 unexpected condition pattern")
    try:
        h2sem.d_shape(sfeed, checker)
    except checker.Reject as exc:
        f5_reject = str(exc)
        need("climb not nested" in f5_reject, "F5 rejected for an unexpected reason: " + f5_reject)
    else:
        raise ValueError("negative control accepted: source-feeding helper wrap")
    controls.append("F5 source-feeding wrap still rejected without condition 2: "
                    "condition 1 and the framed replay's nested-climb check refuse it")

    report = {
        "status": "PASS_R439_H2SEM_COND2_FRAMED_TRANSFER",
        "assignment_nonce": "2276dce171053917945d67a485ce77f3",
        "task_id": "bit-helper-contract",
        "scope_status": "refined",
        "columns": 2 * word["v"] + word["R"],
        "word_canonical_sha256": hashlib.sha256(json.dumps(word, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "h2f_admission_f4_target_feed_wrap": admission,
        "predecessor_f4_record_matches_pinned_certificate": True,
        "f5_source_feed_still_excluded": {
            "raw_operator_exact": True,
            "cond1_zero_frame_distinct_operands": cond1_s,
            "cond2_no_target_feeds_helper_or_source": cond2_s,
            "framed_replay_rejection": f5_reject,
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
    print("PASS_R439_H2SEM_COND2_FRAMED_TRANSFER columns=%d compensated_rows=%d "
          "n1_columns=%d n2_columns=%d controls=%d no_new_kappa"
          % (2 * word["v"] + word["R"], compensated_rows, len(diff1), len(diff2), len(controls)))


if __name__ == "__main__":
    main()
