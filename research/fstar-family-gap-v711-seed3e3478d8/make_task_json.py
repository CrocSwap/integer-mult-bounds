#!/usr/bin/env python3
"""Write TASK.json with original_card taken VERBATIM from the pinned catalogue
card object (the checker compares parsed JSON for exact equality). One-shot
metadata generator; run once, then the file is static evidence."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CARD_ID = "supplier-boundary-audit"

with open(os.path.join(ROOT, "docs", "research", "agent-task-catalog.json"),
          "r", encoding="utf-8") as fh:
    catalog = json.load(fh)
cards = [t for tr in catalog["tracks"] for t in tr["tasks"]
         if t["id"] == CARD_ID]
assert len(cards) == 1, "card %s not unique: %d" % (CARD_ID, len(cards))
card = cards[0]

task = {
    "schema_version": 1,
    "task_id": CARD_ID,
    "original_card": card,
    "scope_status": "changed",
    "scope_change_reason": (
        "Authorized 'explicit open request' scope change to kappa-blocker "
        "KB5h, recorded per the assignment (discussion 1166; PR 2914's "
        "recorded remaining gap of the family-gap question is the named open "
        "request). The chooser OS draw (seed 3e3478d8db3f113c6d56f586419795de, "
        "track adversarial-audit) proposed supplier-boundary-audit, "
        "selected-stock-envelope and uniform-transfer-audit; none is this "
        "object, and the assignment names the KB5h request as the recorded "
        "reason for taking the explicit request instead of the drawn cards. "
        "Pair-collision checks before computation (toolkit disc-comments "
        "--grep on discussions 1317 and 1166 including nested replies, "
        "2026-10-16 10:45-10:47 UTC and the refined pre-computation re-run "
        "11:21 UTC) found no live claim on the v = 7..11 enumeration, "
        "box-completeness, the family gap or the sub-anchor box: the only "
        "F-star family activity in the last hours is KB5g's "
        "FINDING/DONE/RELEASED (PR 2914, 2026-10-16 10:40:51 UTC), which this "
        "assignment explicitly extends. Entry overlap surveys "
        "(find_overlap.py with the object's proper names and synonyms, "
        "complete pagination: 494 then 496 open PRs, 1588 then 1597 "
        "discussions, 2026-10-16 10:45 and 11:21 UTC) found only the known "
        "F-star lineage (PRs 2717/2747/2774/2869/2890/2901/2914, "
        "research/fstar-entry-class-scope-seed63d5f999, "
        "research/fstar-cert-census-seed298df375) and unrelated board "
        "traffic."),
    "actual_scope": (
        "Kappa-blocker KB5h (authorized explicit open request): SETTLE THE "
        "EXACT REMAINING SEARCH SPACE of open problem F-star's family gap as "
        "recorded by PR 2914 - (1) enumerate v = 7..11 (extending PR 2914's "
        "census, its engine extracted byte-exactly and hash-pinned) with the "
        "falsifier criterion armed (exact cert below floor(2v/3), or "
        "admissible chain cost below threshold), looking for the FIRST "
        "gap-2-or-more instance below v = 12; (2) attack box-completeness "
        "(cert = box-max for tau >= 1 at general v): prove it or find the "
        "minimal instance where cert > box-max; (3) report the matched-pivot "
        "floor status honestly (PR 2914 DEMOTED route (a))."),
    "bottleneck_link": (
        "F-star is the named route to closing every open T = 3 window at once "
        "(research/root-unit-decoder-lemmas section 7, consequence PROVEN "
        "given F-star). PR 2914 lifted the family gap on the realized domain "
        "and recorded the exact remaining gap: box-completeness plus the box "
        "floor, or the matched-pivot floor, at general v, with v = 7..11 "
        "unenumerated. Closing the enumeration and pinning box-completeness's "
        "status sharpens the remaining search space of the residue."),
    "existing_restriction_being_changed": (
        "Nothing is relaxed. Extended and audited: PR 2914's recorded "
        "remaining gap (its verdict: 'prove the sub-anchor box complete (cert "
        "= box-max, at least when every line has tau(t) >= 1) and then prove "
        "the box floor, or prove the matched-pivot floor; both remain OPEN') "
        "and its recorded compute obstruction ('sizes v = 7..11 of both "
        "fixtures ... were not enumerated (compute cap)'). Every claim "
        "carries its exact status label; no 'exactly when', necessity or "
        "exhaustive-without-proof wording is used."),
    "method": (
        "Exact stdlib integer/F2 arithmetic on the vendored PR 2914 engine "
        "(predecessor/pr2914/, SHA-256 pins verified at replay): "
        "smallest-first sub-decoder census M[S,S] of both canonical fixtures "
        "at v = 7..11 (restriction is exact), cheap rungs on every record "
        "(exhaustive MP at v <= 11, named_lo, threshold and falsifier "
        "screens, seeded bounded witness hill-climbs with replay), deep rungs "
        "(exact named via exhaustive Lemma MX + CL3 construction spaces with "
        "a raised 3M cap, exact cert/box by exhaustive a-enumeration where "
        "the products allow, ceiling exactness via replayed size-v "
        "witnesses), a named-settlement pass on every scan record whose MX "
        "product fits 3M, the box-completeness attack (explicit tau = 0 v = 2 "
        "demonstration, Lemma BPP projection parity, 126-instance synthetic "
        "sweep with exact cert vs exact box), and a registered replay "
        "verify.py that replays every stored witness and recomputes "
        "headlines deterministically."),
    "parameter_ranges": (
        "T = 3 totals exactly; integer factorizations (entry-class-"
        "independent by PR 2869); v = 7..11 sub-decoders of PR 2111's "
        "tied_min (v = 12) and cex_min_1 (v = 19), byte-identical data "
        "copies (sha256 670ed90924b601ade22f0d4adaff46d1667e5449326a0f7ba7b"
        "88dd8f5906f93 and 86064701dde94b4f35427bc3e19275eaf1e40e9e90d4fea2"
        "8e7857f3564d4dd7); census domain: tied_min complete at v = 9..11 and "
        "240/495-strided at v = 7..8, cex_min_1 strided 240/200/160/140/120 "
        "of 50388/75582/92378/92378/75582; deep tier 113 records; synthetic "
        "sweep 126 deterministic decoders at v = 4..7 (seed 20261016); "
        "deterministic seeds and strides recorded in CERTIFICATE.json and "
        "the receipts under data/census_v711/."),
    "falsification_test": (
        "An explicit admissible pairing B with cost(B) = sum_j rank_F2 "
        "B[R_j,A_j] < floor(2v/3) refutes F-star on that instance (the chain "
        "cost >= cert(M) is proven in research/root-unit-decoder-lemmas), as "
        "does exact cert < floor(2v/3) where exhaustive a-enumeration "
        "terminates. For box-completeness, any instance with cert > box-max "
        "on tau >= 1 lines demotes the box route. Corrupted witnesses must "
        "fail the independent replay checker. Armed on every record; never "
        "fired; PROVEN inoperative on the enumerated domain (named_lo >= "
        "floor(2v/3) witnesses replay)."),
    "success_evidence": (
        "PASS markers from verify.py (PASS_KB5H_PINS, PASS_FG_CONTROLS, "
        "PASS_FG_CALIBRATION tied_min=11/12 cex_min_1=18/19 mp=9/16 chain=22 "
        "reach=0/12,8/19, PASS_KB5H_CENSUS records=1638 ... falsifiers=0, "
        "PASS_KB5H_DEEP records=113 ... box-violations=0, PASS_BOX_ATTACK "
        "tau0-demo-cert2-box1 ..., PASS_FSTAR_FAMILY_GAP_V711 "
        "no-falsifier-in-domain) plus README.md analysis labelled PROVEN / "
        "CHECKED / DEMOTED: the first gap-2-or-more instance below v = 12 at "
        "v = 7; the family gap nonzero (1) from v = 7 exact; gap_named = 2 "
        "excluded below v = 12 outside the 12 tied_min v = 11 sub-decoders "
        "(Lemma MX product 1977326743 obstruction); box = cert on all 113 "
        "deep records and 11 tau >= 1 synthetic instances; the tau >= 1 "
        "hypothesis PROVEN necessary (explicit v = 2 decoder cert = 2 > box "
        "= 1); Lemma BPP; the scan pitfall quantified (3 of 10 settled "
        "records)."),
    "outcome": "completed",
    "author": "Aaron Wang (with help from opencode)",
    "base_commit": "5a0dc2c0f4685b02bef7776bc196c7c1231cbac1",
    "ai_assistance": "Substantial AI assistance: this package was produced by Aaron Wang with help from opencode (opencode agent harness). No model named per orchestrator attribution rules. No independent human review claimed.",
    "stop_rule": (
        "Stop at the first exact falsifier (explicit admissible B with chain "
        "cost below floor(2v/3), or exact cert below threshold where "
        "exhaustive), or at a confirmed box-completeness counterexample "
        "(cert > box on tau >= 1), or, absent both, at the declared census "
        "domain with the exact residual recorded (the 12 tied_min v = 11 "
        "sub-decoders and their Lemma MX obstruction). One bounded pivot "
        "maximum (the 3M named settlement); early kill with the exact "
        "obstruction recorded."),
    "time_compute_cap": (
        "One session; single-process stdlib Python; no SAT solver, no "
        "third-party packages; the registered verify.py below 600 s "
        "(observed 58.5 s); heavy census and sweep sharded into resumable "
        "checkpoint jobs with receipts under data/census_v711/ (about 25 "
        "minutes total); package registered with timeout_seconds 600."),
    "optimistic_full_cost_budget": (
        "No kappa, supplier, word or moment budget is in play "
        "(missing-lemma/audit work). The price is one bounded deterministic "
        "stdlib registered run (58.5 s) plus the sharded checkpoint runs and "
        "written analysis."),
    "intended_artifact": (
        "research/fstar-family-gap-v711-seed3e3478d8/ with TASK.json, "
        "TASK-CARD.md, SOURCES.json pins, VERIFY.json, verify.py, "
        "predecessor/pr2914/ (byte-exact PR 2914 engine + fixtures, SHA-256 "
        "pins), data/census_v711/ receipts and data/box-attack-receipt.json, "
        "CERTIFICATE.json (written by verify.py, digest a4525ee97862ba34) "
        "and README.md; reproduce with python3 -B "
        "research/fstar-family-gap-v711-seed3e3478d8/verify.py then python3 "
        "scripts/research_package.py --package "
        "research/fstar-family-gap-v711-seed3e3478d8 --check-only."),
    "nearest_overlapping_prs": (
        "https://github.com/CrocSwap/integer-mult-bounds/pull/2914 (Aaron "
        "Wang: the sub-anchor box, Lemmas SB/LB, the v = 3..6 census and the "
        "recorded remaining gap this package closes; its engine is vendored "
        "byte-exactly). https://github.com/CrocSwap/integer-mult-bounds/"
        "pull/2901 (Aaron Wang: the family-gap definition and record). "
        "https://github.com/CrocSwap/integer-mult-bounds/pull/2747 (Aaron "
        "Wang: Lemma MX, exhaustive MP/MX fixture values). "
        "https://github.com/CrocSwap/integer-mult-bounds/pull/2717 (Aaron "
        "Wang: Lemmas SF/MP/RK/AN and the exact-completion engine). "
        "https://github.com/CrocSwap/integer-mult-bounds/pull/2869 (Aaron "
        "Wang: Lemmas SC/SG). https://github.com/CrocSwap/integer-mult-bounds"
        "/pull/2774 and https://github.com/CrocSwap/integer-mult-bounds/"
        "pull/2890 (Aaron Wang: other residue classes). PR 2111 "
        "(DreamingOfClouds: fixtures and recorded certificate limits 11/18) "
        "and PR 1590 (DreamingOfClouds: F-star, cert(M), the proven chain) "
        "are cited, not restated. No other work on this object existed at "
        "entry or at the pre-computation overlap re-run (2026-10-16 10:45 and "
        "11:21 UTC, complete pagination)."),
    "predecessor_authors": (
        "F-star, the cert(M) definition, L8 labellings and the proven chain "
        "cost >= sum_j r_j >= cert(M): research/root-unit-decoder-lemmas, PR "
        "1590 by DreamingOfClouds (Claude Opus 5.5 (Anthropic) via Claude "
        "Code assistance). The rank-3 configuration model, the canonical "
        "fixtures tied_min and cex_min_1 and their recorded one-copy "
        "certificate limits 11 and 18 (CP-SAT): DreamingOfClouds, PR 2111. "
        "The exact-completion engine design, Lemmas SF/MP/RK/AN and the "
        "residue statement: Aaron Wang, PR 2717. Lemma MX and the exhaustive "
        "MP/MX fixture values: Aaron Wang, PR 2747. The zero-digraph "
        "machinery: Aaron Wang, PR 2774. Lemmas SC/SG and the canonical "
        "reduced normalization: Aaron Wang, PR 2869. The chi(Z) machinery: "
        "Aaron Wang, PR 2890. The family-gap definition and record: Aaron "
        "Wang, PR 2901. The sub-anchor box, Lemmas SB/LB and the extended "
        "census engine: Aaron Wang, PR 2914. All authors verified at current "
        "ground truth with gh pr view --json author,title on 2026-10-16."),
    "open_questions": [
        {
            "question": (
                "Is the sub-anchor box complete at general v when every line "
                "has tau(t) >= 1: cert(M) = box-max(M)?"),
            "why_it_matters": (
                "It reduces F-star to the finite sub-anchor label space (at "
                "most 24 certifying pairs per line) and makes the family gap "
                "exactly the box interior the named forms miss; box = cert "
                "on all 113 deep records, both fixtures and all tau >= 1 "
                "synthetic instances."),
            "first_step": (
                "Prove or refute that Lemma BPP's projection conditions "
                "(i)-(ii) are without loss: massage any witness into one "
                "satisfying them at no value cost, or find the smallest "
                "instance where that fails (the 12 tied_min v = 11 "
                "sub-decoders are the current minimal candidates)."),
            "blocked_by": (
                "Both sides exact on the candidates needs a better named/box "
                "algorithm than product enumeration (Lemma MX product "
                "1977326743, box a-enumeration 2^33)."),
        },
        {
            "question": (
                "What is the family gap on the 12 tied_min v = 11 "
                "sub-decoders: is gap_named = cert - named ever 2 below "
                "v = 12?"),
            "why_it_matters": (
                "It is the exact remaining search space for 'gap 2 below "
                "v = 12'; every other enumerated record has gap_named <= 1 "
                "settled."),
            "first_step": (
                "A DP over the Lemma MX construction space (the value "
                "|A| + |U| + sum MAS(classes) is additive under the "
                "hypothesis constraints) instead of the 2e9-product "
                "enumeration."),
            "blocked_by": (
                "The Lemma MX hypothesis checks couple A/U/T choices across "
                "zero arcs; no DP was found in this session."),
        },
        {
            "question": (
                "Is max_c sum_i MAS(Z[C_i]) >= floor(2v/3) for every "
                "realizable rank-3 pattern (PR 2747 open question 1)?"),
            "why_it_matters": (
                "Lemma MP alone would prove F-star with no anchor; witnessed "
                "on all 1638 census records and all 113 deep records (0 "
                "below threshold with MP alone) but not proved."),
            "first_step": (
                "A SAT/CP construction of rank-3 patterns minimizing the "
                "floor (fixture-density zeros resist random construction; "
                "Lemma RK (c) forces |pi(t) intersect sigma(s)| >= 2 at "
                "every arc)."),
            "blocked_by": (
                "Needs a constraint solver, not random search; and MP is "
                "strictly weaker than cert on the fixtures (9 < 11, 16 < "
                "18), so the route is DEMOTED without new evidence."),
        },
    ],
    "evidence": (
        "V = 7..11 ENUMERATED WITH ZERO FALSIFIERS; FIRST GAP-2 INSTANCE "
        "BELOW V = 12 AT V = 7; FAMILY GAP NONZERO FROM V = 7; GAP_NAMED = 2 "
        "EXCLUDED OUTSIDE THE 12 TIED_MIN V = 11 SUB-DECODERS; BOX = CERT "
        "EVERYWHERE MEASURED; TAU >= 1 HYPOTHESIS PROVEN NECESSARY; F-STAR "
        "NOT PROVED AND NOT REFUTED. CHECKED (verify.py, stdlib, "
        "deterministic, 58.5 s, certificate digest a4525ee97862ba34): "
        "predecessor pins 11/11 byte-exact; PR 2914's controls and every "
        "recorded anchor (PASS_FG_CALIBRATION tied_min=11/12 cex_min_1=18/19 "
        "mp=9/16 chain=22 reach=0/12,8/19; PR 2914 digest 031927ba33ed45a0 "
        "reproduced); 1638 cheap records at v = 7..11 (identities, 1384 "
        "replayed witnesses, 946 trivial gap-0 closures, 38 gap-2-witnessed "
        "records, 70 gap-2-potential records, falsifiers 0, below-threshold "
        "0, MP-below-threshold 0, min named_lo ratio 5/7); 113 deep records "
        "(gap_named exact max 1, 17 records exact gap 1 at v = 7..10; "
        "gap_named = 2 excluded outside the 12 tied_min v = 11 sub-decoders "
        "where named is scan-only at Lemma MX product 1977326743; box = cert "
        "on all 113 with zero box violations); 126 synthetic instances "
        "(11 tau >= 1: box = cert; 115 tau = 0-line: box = #{t : tau(t) >= "
        "1} exactly). PROVEN: tau >= 1 necessary (explicit v = 2 decoder P = "
        "[[1,0,1],[2,1,0]], Q = [[1,0,0],[1,0,1]]: cert = 2 > box = 1); "
        "Lemma BPP (projection parity); falsifier criterion inoperative on "
        "the domain. The scan pitfall is quantified: on 3 of 10 settled "
        "records the seeded 20k-iteration Lemma MX scan under-reported named "
        "by 1..2."),
}

out = os.path.join(HERE, "TASK.json")
with open(out, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(task, fh, indent=1, sort_keys=True)
    fh.write("\n")
print("TASK.json written with card %s (%d keys)" % (CARD_ID, len(card)))
