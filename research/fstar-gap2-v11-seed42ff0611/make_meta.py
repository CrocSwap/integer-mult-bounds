#!/usr/bin/env python3
"""Generate predecessor/PINS.json (SHA-256 pins of every vendored
predecessor file) and TASK.json (original_card extracted byte-equal from the
pinned catalogue). Deterministic. Run: python3 -B make_meta.py
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.stdout.reconfigure(encoding="utf-8")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, indent=1, sort_keys=True)
        fh.write("\n")


def make_pins():
    pins = {}
    for rel in sorted(os.listdir(os.path.join(HERE, "predecessor", "pr2914"))):
        p = os.path.join(HERE, "predecessor", "pr2914", rel)
        if os.path.isfile(p):
            pins["pr2914/" + rel] = sha256_file(p)
    for rel in sorted(os.listdir(os.path.join(HERE, "predecessor", "pr2914",
                                              "data"))):
        p = os.path.join(HERE, "predecessor", "pr2914", "data", rel)
        if os.path.isfile(p):
            pins["pr2914/data/" + rel] = sha256_file(p)
    for rel in sorted(os.listdir(os.path.join(HERE, "predecessor", "pr2936"))):
        p = os.path.join(HERE, "predecessor", "pr2936", rel)
        if os.path.isfile(p):
            pins["pr2936/" + rel] = sha256_file(p)
    nested = os.path.join(HERE, "predecessor", "pr2936", "predecessor",
                          "pr2914", "verify.py")
    pins["pr2936/predecessor/pr2914/verify.py"] = sha256_file(nested)
    assert pins["pr2936/predecessor/pr2914/verify.py"] == \
        pins["pr2914/verify.py"], "nested engine copy must be byte-identical"
    out = dict(schema_version=1,
               provenance=dict(
                   pr2914="https://github.com/CrocSwap/integer-mult-bounds"
                          "/pull/2914 head 3f7781efccdf10fa61a1e0a6f11c191579b21280 "
                          "extracted with pr-tree-extract 2914 "
                          "research/fstar-family-gap-seed1c25f56f",
                   pr2936="https://github.com/CrocSwap/integer-mult-bounds"
                          "/pull/2936 head f0ef06f13e4de3e50c211c880bdc6891c09620a1 "
                          "extracted with pr-tree-extract 2936 "
                          "research/fstar-family-gap-v711-seed3e3478d8"),
               files=pins)
    write_json(os.path.join(HERE, "predecessor", "PINS.json"), out)
    print("PINS files=%d" % len(pins))


def original_card():
    with open(os.path.join(REPO, "docs", "research",
                           "agent-task-catalog.json"), encoding="utf-8") as fh:
        cat = json.load(fh)
    for track in cat["tracks"]:
        for card in track["tasks"]:
            if card.get("id") == "coverage-law-change":
                return card
    raise SystemExit("drawn card not found in catalogue")


def make_task():
    card = original_card()
    task = {
        "schema_version": 1,
        "task_id": "coverage-law-change",
        "original_card": card,
        "scope_status": "changed",
        "scope_change_reason": (
            "Authorized 'explicit open request' scope change to kappa-blocker "
            "KB5i, recorded per the assignment (discussion 1166; PR 2936's "
            "recorded remainder of open problem F-star's family-gap question "
            "is the named open request). The chooser OS draw (seed "
            "42ff061169763106b201a358b527fd93, track recursive-interfaces) "
            "proposed coverage-law-change, centre-path-sharing and "
            "connector-alphabet-change; none is this object, and the "
            "assignment names the KB5i request as the recorded reason for "
            "taking the explicit request instead of the drawn cards. "
            "Pair-collision checks before computation (toolkit "
            "disc-comments --grep on discussions 1317 and 1166 including "
            "nested replies, 2026-10-16 12:40-12:45 UTC) found no live claim "
            "on the twelve tied_min v = 11 sub-decoders, the family gap, "
            "box-completeness or Lemma BPP: the only family-gap activity in "
            "the last hours is KB5h's FINDING/DONE/RELEASED (PR 2936, "
            "2026-10-16 12:34:18 UTC), which this assignment explicitly "
            "extends. Entry overlap survey (find_overlap.py with the object's "
            "proper names and synonyms, complete pagination: 471 open PRs, "
            "1622 discussions, 2026-10-16 12:41 UTC) found only the known "
            "F-star lineage and unrelated board traffic."),
        "author": "Aaron Wang (with help from opencode)",
        "ai_assistance": ("Substantial AI assistance: this package was "
                          "produced by Aaron Wang with help from opencode "
                          "(opencode agent harness). No model named per "
                          "orchestrator attribution rules. No independent "
                          "human review claimed."),
        "base_commit": "991c50d1ea8ddb7cf88c1b4a45c7b409c02d38fb",
        "actual_scope": (
            "Kappa-blocker KB5i (authorized explicit open request): SETTLE "
            "THE TWELVE OPEN tied_min v = 11 sub-decoders of open problem "
            "F-star's family-gap question - (1) compute named EXACTLY where "
            "PR 2936 has a scan only (Lemma MX construction product "
            "1,977,326,743) and answer the verdict: does gap_named = 2 exist "
            "below v = 12 (the minimal gap-2 instance drops from v = 12 to "
            "v = 11) or is the minimal exact gap-2 instance exactly tied_min "
            "v = 12? Cross-check: cert reproduces or corrects PR 2936's "
            "stored values. (2) Push box-completeness under Lemma BPP: the "
            "tau >= 1 general case with the projection-parity obstruction as "
            "filter - prove cert = box-max or search the minimal tau >= 1 "
            "decoder with cert > box-max, concentrated where PR 2936's sweep "
            "was weak (its 12 gap2-open scans and synthetic families). "
            "(3) Report the matched-pivot floor status honestly (demoted "
            "twice)."),
        "existing_restriction_being_changed": (
            "PR 2936's recorded obstruction 'Lemma MX construction product "
            "1,977,326,743 - named is a seeded scan (value 9) and gap_named "
            "stays in {0,1,2}' and its open question 2 (a DP over the Lemma "
            "MX construction space instead of the 2e9-product enumeration); "
            "PR 2914 open question 1 (box-completeness at tau >= 1) pressed "
            "on the weak cell of PR 2936's sweep. Nothing is relaxed; every "
            "claim carries its exact status label and no 'exactly when', "
            "necessity or exhaustive-without-proof wording is used."),
        "method": (
            "Exact stdlib integer/F2 arithmetic on the byte-exact vendored "
            "PR 2914 engine (predecessor/pr2914/, SHA-256 pins verified at "
            "replay). Exact named = max(SG reach, Lemma MP, Lemma MX, Lemma "
            "CL3) computed by a coarse-assignment DP over the Lemma MX "
            "per-line options (A / U(a*) / T(c)): the construction value "
            "|A| + |U| + sum MAS(classes) does not depend on the repair "
            "labels a*, and the Lemma MX hypothesis checks factor per U "
            "line, so repairs fold into per-line feasibility masks and the "
            "search enumerates only kinds (3^11 = 177147 coarse assignments "
            "per record; feasibility checked only above the running best). "
            "The port is agreement-tested against the engine's own "
            "exhaustive mx_eval product enumeration on 72 small instances "
            "plus random decoders. CL3 = MP exactly at even tau (proof in "
            "README, machine-checked). Cert/box values regenerated with "
            "deterministic multi-seed hill-climbs (the deep run's seeds "
            "first) and every witness independently replayed; ceiling "
            "witnesses (size v) make the rungs exact. Box-completeness: the "
            "vendored tolerant tau = 0 wrapper (PR 2936), Lemma BPP "
            "projection parity on every witness, and a fixture-density "
            "synthetic family (GL_3(Z) column transforms of the fixtures "
            "plus restrictions, tau >= 1 filter) at v = 4..6 with both rungs "
            "exact."),
        "parameter_ranges": (
            "T = 3 totals exactly; integer factorizations; exactly the 12 "
            "tied_min v = 11 sub-decoders (the complete v = 11 family of the "
            "v = 12 fixture tied_min, sha256 670ed90924b601ade22f0d4adaff46d16"
            "67e5449326a0f7ba7b88dd8f5906f93); cross-check domain PR 2936's "
            "receipt-tied_min-s11-deep.json (vendored byte-exactly); box "
            "search domain 60 GL_3(Z)-transformed fixture sub-decoders at "
            "v = 4..6 (seed 20261016) filtered to tau >= 1 everywhere, plus "
            "the v = 2 tau = 0 demonstration decoder; deterministic seeds "
            "recorded in the receipts."),
        "falsification_test": (
            "A named construction witness whose replay value differs from "
            "the DP optimum refutes the exact solver (the port is pinned to "
            "the engine's own mx_eval by agreement tests); a corrupted "
            "witness must fail the independent replay checker. A certified "
            "instance with cert - named = 2 at v = 11 answers the verdict "
            "YES (it fired: 12 of 12). For box-completeness, any tau >= 1 "
            "instance with cert > box-max demotes the box route (armed on 12 "
            "exact v = 11 records and 60 exact v = 4..6 instances; never "
            "fired). An explicit admissible pairing B with chain cost below "
            "floor(2v/3) would refute F-star on an instance (not sought "
            "here: named_lo = 9 >= 7 on every record)."),
        "success_evidence": (
            "PASS markers from verify.py: PASS_KB5I_PINS, PASS_FG_CONTROLS, "
            "PASS_FG_CALIBRATION tied_min=11/12 cex_min_1=18/19 mp=9/16 "
            "chain=22 reach=0/12,8/19 (PR 2914 and PR 2936 anchors "
            "reproduced), PASS_KB5I_NAMED records=12 named-exact=12 "
            "gap2-proven=12, PASS_KB5I_CROSSCHECK (stored PR 2936 values "
            "reproduced or corrected with replayed witnesses), "
            "PASS_BOX_SEARCH bpp-strict-tau0=yes bpp-strict-tau1=no "
            "tau-ge1=60 hard=0 box-violations=0, and README.md analysis "
            "labelled PROVEN / CHECKED / DEMOTED: gap_named = 2 EXISTS below "
            "v = 12 - PROVEN on all 12 tied_min v = 11 sub-decoders (named = "
            "9 exact, cert = 11 exact), so the minimal exact gap-2 instance "
            "drops from v = 12 to v = 11; box = cert = 11 exact on all 12 "
            "and on 60 new fixture-density tau >= 1 instances at v = 4..6; "
            "Lemma BPP projection strictness PROVEN at tau = 0 (v = 2: 2 -> "
            "1) and CHECKED not to drop at tau >= 1 on 21 escaping "
            "witnesses; matched-pivot floor DEMOTED (MP = 9 < cert = 11 on "
            "all 12)."),
        "evidence": (
            "VERDICT: gap_named = 2 EXISTS below v = 12. On all 12 tied_min "
            "v = 11 sub-decoders (complete family): named = 9 EXACT "
            "(Lemma MX coarse-DP optimum with replayed construction "
            "witnesses; MP = 9 exhaustive; CL3 = MP = 9 at even tau), cert = "
            "11 EXACT (replayed ceiling witnesses, size v). gap_named = 2 "
            "PROVEN on 12 of 12. The minimal exact gap-2 instance drops from "
            "tied_min v = 12 (PR 2901/2914 record) to tied_min v = 11. "
            "CROSS-CHECK: PR 2936's stored cert values under-report the true "
            "cert = 11 on 7 of 12 records (stored 9 or 10) - the hill-climb "
            "pitfall quantified on cert, companion to the named scan "
            "pitfall; every stored value is reproduced or corrected with a "
            "replayed witness. BOX: box = cert = 11 EXACT on all 12 (the "
            "weak cell of PR 2936's sweep closed; previously 4 records open "
            "at box, cert in {10,11}); every attaining witness is "
            "box-valued. On 60 new fixture-density tau >= 1 instances "
            "(GL_3(Z) column transforms + restrictions, v = 4..6, both rungs "
            "exact): box = cert on all 60, 0 violations, 0 hard instances. "
            "Lemma BPP: projection strictness PROVEN at tau = 0 (smallest "
            "instance: v = 2 decoder, witness 2 -> projection 1, condition "
            "(i) fails exactly as Lemma BPP predicts); at tau >= 1, 21 "
            "escaping witnesses examined with no strict projection drop "
            "(CHECKED bounded). Box-completeness for tau >= 1 remains NOT "
            "PROVEN and NOT REFUTED. MP floor DEMOTED: MP = 9 < cert = 11 on "
            "all 12 (new counterexamples to named = MP = cert); MP >= "
            "floor(2v/3) = 7 holds on every record. F-star itself is NOT "
            "proved and NOT refuted."),
        "bottleneck_link": (
            "F-star is the named route to closing every open T = 3 window at "
            "once (research/root-unit-decoder-lemmas section 7). PR 2936's "
            "record left exactly two computational unknowns in the family "
            "gap: the 12 tied_min v = 11 sub-decoders (scan-only named) and "
            "box-completeness at tau >= 1. This package settles the first "
            "exactly (gap_named = 2 at v = 11) and closes the weak cell of "
            "the second (box = cert = 11 exact on the 12 and on 60 new "
            "fixture-density instances), sharpening the family-gap record "
            "to: the named families miss exactly 2 points at v = 11 on the "
            "tied_min family, realized inside the sub-anchor box."),
        "nearest_overlapping_prs": (
            "https://github.com/CrocSwap/integer-mult-bounds/pull/2936 "
            "(Aaron Wang: the direct predecessor; this settles exactly its "
            "recorded remainder - the 12 scan-only tied_min v = 11 "
            "sub-decoders and the weak cell of the box attack). "
            "https://github.com/CrocSwap/integer-mult-bounds/pull/2914 "
            "(Aaron Wang: sub-anchor box, Lemmas SB/LB, engine vendored "
            "byte-exactly). "
            "https://github.com/CrocSwap/integer-mult-bounds/pull/2901 "
            "(Aaron Wang: family-gap definition and record). "
            "https://github.com/CrocSwap/integer-mult-bounds/pull/2747 "
            "(Aaron Wang: Lemma MX). "
            "https://github.com/CrocSwap/integer-mult-bounds/pull/2717 "
            "(Aaron Wang: Lemmas SF/MP/RK/AN, exact-completion engine). "
            "https://github.com/CrocSwap/integer-mult-bounds/pull/2869 "
            "(Aaron Wang: Lemmas SC/SG). PR 2111 (DreamingOfClouds: "
            "fixtures and recorded certificate limits 11/18) and PR 1590 "
            "(DreamingOfClouds: F-star, cert(M), the proven chain) are "
            "cited, not restated. No other work on the 12 sub-decoders "
            "existed at entry or at the pre-submission overlap refresh."),
        "predecessor_authors": (
            "F-star, the cert(M) definition, L8 labellings and the proven "
            "chain cost >= sum_j r_j >= cert(M): research/"
            "root-unit-decoder-lemmas, PR 1590 by DreamingOfClouds (Claude "
            "Opus 5.5 (Anthropic) via Claude Code assistance). The rank-3 "
            "configuration model, the canonical fixtures tied_min and "
            "cex_min_1 and their recorded one-copy certificate limits 11 and "
            "18 (CP-SAT): DreamingOfClouds, PR 2111. The exact-completion "
            "engine design, Lemmas SF/MP/RK/AN and the residue statement: "
            "Aaron Wang, PR 2717. Lemma MX and the exhaustive MP/MX fixture "
            "values: Aaron Wang, PR 2747. The zero-digraph machinery: Aaron "
            "Wang, PR 2774. Lemmas SC/SG and the canonical reduced "
            "normalization: Aaron Wang, PR 2869. The chi(Z) machinery: "
            "Aaron Wang, PR 2890. The family-gap definition and record: "
            "Aaron Wang, PR 2901. The sub-anchor box, Lemmas SB/LB, the "
            "tolerant tau = 0 wrapper and the extended census engine: Aaron "
            "Wang, PR 2914. The v = 7..11 census, the box-completeness "
            "attack and Lemma BPP: Aaron Wang, PR 2936. All authors above "
            "were verified at current ground truth with gh pr view --json "
            "author,title on 2026-10-16 (PRs 2717/2747/2774/2869/2890/2901/"
            "2914/2936: Aaron Wang (navinor); PR 2111: DreamingOfClouds; "
            "PR 2206 not used here)."),
        "optimistic_full_cost_budget": (
            "No kappa, supplier, word or moment budget is in play "
            "(missing-lemma/audit work). The price is one bounded "
            "deterministic stdlib registered run plus two bounded "
            "checkpoint runs (run_named_v11.py about 16 minutes multi-seed "
            "witness regeneration; box_search.py about 3 minutes)."),
        "stop_rule": (
            "Stop at the verdict on gap_named = 2 below v = 12 (fired: YES, "
            "12 of 12 at v = 11), or at the first confirmed box-completeness "
            "counterexample (cert > box on tau >= 1; never fired on 12 + 60 "
            "exact instances), or at the declared domain with the exact "
            "residual recorded. One bounded pivot maximum (the "
            "fixture-density GL_3(Z) synthetic family); early kill with the "
            "exact obstruction recorded."),
        "time_compute_cap": (
            "One session; single-process stdlib Python; no SAT solver, no "
            "third-party packages; the registered verify.py below 600 s; "
            "checkpoint runs with receipts under data/ (run_named_v11.py "
            "about 16 minutes, box_search.py about 3 minutes on the "
            "authoring host); package registered with timeout_seconds 600."),
        "intended_artifact": (
            "research/fstar-gap2-v11-seed42ff0611/ with TASK.json, "
            "TASK-CARD.md, SOURCES.json pins, VERIFY.json, verify.py, "
            "named_exact.py (the exact solver), test_named_exact.py "
            "(agreement + target tests), run_named_v11.py and box_search.py "
            "(checkpoint runs), predecessor/pr2914/ and predecessor/pr2936/ "
            "(byte-exact vendored predecessors, SHA-256 pins in "
            "predecessor/PINS.json), data/named-v11-receipt.json and "
            "data/box-search-receipt.json, CERTIFICATE.json (written by "
            "verify.py) and README.md; reproduce with python3 -B "
            "research/fstar-gap2-v11-seed42ff0611/verify.py then python3 "
            "scripts/research_package.py --package "
            "research/fstar-gap2-v11-seed42ff0611 --check-only."),
        "open_questions": [
            {
                "question": ("Is the sub-anchor box complete at general v "
                             "when every line has tau(t) >= 1: cert(M) = "
                             "box-max(M)?"),
                "why_it_matters": ("It reduces F-star to the finite "
                                   "sub-anchor label space and makes the "
                                   "family gap exactly the box interior the "
                                   "named forms miss; box = cert now holds "
                                   "exactly on the 12 tied_min v = 11 "
                                   "sub-decoders and 60 fixture-density "
                                   "tau >= 1 instances."),
                "first_step": ("Prove or refute that Lemma BPP's projection "
                               "conditions (i)-(ii) are without loss: "
                               "massage any attaining witness into one "
                               "satisfying them at no value cost. The "
                               "bounded search found no projection drop at "
                               "tau >= 1 (21 escaping witnesses), so a proof "
                               "route may exist; smallest falsifying "
                               "instance still sought."),
                "blocked_by": ("No route was found to show the parity terms "
                               "are without loss; naive projection is "
                               "PROVEN strictly lossy at tau = 0 (v = 2: 2 "
                               "-> 1).")},
            {
                "question": ("What labels carry the 2-point family-gap "
                             "excess at v = 11: can a repair/CL3-type "
                             "extension of the named families close it?"),
                "why_it_matters": ("gap_named = 2 is now exact on the whole "
                                   "v = 11 tied_min family; characterizing "
                                   "the missing labels turns the family gap "
                                   "into a construction question."),
                "first_step": ("Classify every attaining cert witness "
                               "(diff_labels kinds) against the named forms "
                               "and read off the minimal label extension; "
                               "the stored witnesses in "
                               "data/named-v11-receipt.json are the input."),
                "blocked_by": ("None - open analysis, not computation.")},
            {
                "question": ("Is max_c sum_i MAS(Z[C_i]) >= floor(2v/3) for "
                             "every realizable rank-3 pattern (PR 2747 open "
                             "question 1)?"),
                "why_it_matters": ("Lemma MP alone would prove F-star with "
                                   "no anchor; witnessed on every enumerated "
                                   "record but not proved."),
                "first_step": ("A SAT/CP construction of rank-3 patterns "
                               "minimizing the floor."),
                "blocked_by": ("Needs a constraint solver, not random "
                               "search; MP is strictly weaker than cert "
                               "(9 < 11 on all 12 v = 11 records), so the "
                               "route stays DEMOTED without new evidence.")},
        ],
        "outcome": "completed",
    }
    write_json(os.path.join(HERE, "TASK.json"), task)
    print("TASK.json written; original_card id=%s keys=%d"
          % (card["id"], len(card)))


if __name__ == "__main__":
    make_pins()
    make_task()
