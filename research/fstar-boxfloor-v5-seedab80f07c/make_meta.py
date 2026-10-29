#!/usr/bin/env python3
"""KB5L metadata generator: TASK.json (drawn catalogue card verbatim),
TASK-CARD.md, SOURCES.json, VERIFY.json, and the vendored PINS.json for the
PR 3012 tree.  Stdlib only; writes every file with newline="\\n".
Run: python3 -B make_meta.py
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
BASE = "d8e0f83f00191df62174b641e9fff055c357f641"
PACKAGE = "fstar-boxfloor-v5-seedab80f07c"
VEND_ROOT = os.path.join(HERE, "predecessor", "pr3012")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob(rel):
    out = subprocess.run(["git", "rev-parse", "%s:%s" % (BASE, rel)],
                         cwd=REPO, capture_output=True, text=True, check=True)
    return out.stdout.strip()


def draw_card(card_id):
    with open(os.path.join(REPO, "docs", "research",
                           "agent-task-catalog.json"), encoding="utf-8") as fh:
        cat = json.load(fh)

    def walk(node):
        if isinstance(node, dict):
            if node.get("id") == card_id or node.get("task_id") == card_id:
                return node
            for v in node.values():
                got = walk(v)
                if got is not None:
                    return got
        elif isinstance(node, list):
            for v in node:
                got = walk(v)
                if got is not None:
                    return got
        return None
    card = walk(cat)
    assert card is not None, card_id
    return card


def gen_pins():
    """Pin every vendored PR 3012 file (57) into predecessor/PINS.json."""
    files = {}
    for root, _dirs, names in os.walk(VEND_ROOT):
        for nm in sorted(names):
            p = os.path.join(root, nm)
            rel = os.path.relpath(p, os.path.join(HERE, "predecessor"))
            files[rel.replace("\\", "/")] = sha256_file(p)
    pins = dict(schema_version=1,
                source="PR 3012 head 63c6525120c20543c4a7acae1a1e1ea36e099b81 "
                       "package research/fstar-boxfloor-minimal-seed758ae8fe "
                       "(pr-tree-extract, byte-exact)",
                files=files)
    with open(os.path.join(HERE, "predecessor", "PINS.json"), "w",
              encoding="utf-8", newline="\n") as fh:
        json.dump(pins, fh, indent=1, sort_keys=True)
        fh.write("\n")
    return len(files)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    card = draw_card("complex-new-helper-inventory")
    task = {
        "actual_scope":
            "Kappa-blocker KB5L (authorized explicit open request): the FIRST "
            "OPEN CASE of the tau >= 1 box floor (v = 5) and the shareable-class "
            "remainder - as recorded by PR 3012 (agent-79). (a) prove "
            "box(M) >= floor(2v/3) = 3 for every exact 3-total rational decoder "
            "with v = 5 and tau >= 1, or find the minimal counterexample with "
            "box < 3 (exact both sides); (b) settle some or all of PR 2978's 21 "
            "unrealized v = 3 combinatorial patterns (shareable-class "
            "completeness); (c) report honestly what remains for F-star. "
            "One bounded pivot maximum; smallest falsifying instance first.",
        "ai_assistance":
            "Substantial AI assistance: this package was produced by Aaron Wang "
            "with help from opencode (opencode agent harness). No model named "
            "per orchestrator attribution rules. No independent human review "
            "claimed.",
        "author": "Aaron Wang (with help from opencode)",
        "base_commit": BASE,
        "bottleneck_link":
            "F-star (cert(M) >= floor(2v/3), research/root-unit-decoder-lemmas "
            "section 7) is the named route to closing every open T = 3 window at "
            "once. After PR 3012 the box-floor route survives exactly on the "
            "tau >= 1 domain, PROVEN for v <= 4 and open first at v = 5 "
            "(threshold 3). This package settles v = 5 (PROVEN) and narrows the "
            "shareable-class remainder.",
        "evidence":
            "VERDICT (a): the tau >= 1 box floor HOLDS at v = 5 - PROVEN. "
            "Chain: (1) exhaustive combinatorial envelope classification over "
            "all 749398 multisets of 5 raw line types with tau >= 1 (joint bit "
            "structure preserved): box = 2 on the envelope forces exactly 33 "
            "families, all of the rank-2-cap + all-pairs-even shape; (2) the "
            "anchor-attainment screen (a0 omits bit j everywhere => p_j == 0; "
            "b0 omits bit j everywhere <=> q_j == 0 or c_j > gamma) rejects 15 "
            "of the 33 as unrealizable and leaves 6 shapes up to total "
            "relabeling (5 unshareable-total rank-3 shapes + 1 zero-p-column "
            "rank-2 shape); (3) exact blocking-Z enumeration per surviving "
            "shape (per-triple kept-3 feasibility tables, all 2^20 arc subsets): "
            "the ONLY zero-arc set blocking every triple is the complete "
            "digraph; complete Z forces M diagonal, rank(M) = 5 > 3, impossible "
            "for any 3-total decoder. Hence box >= 3 = floor(2v/3) for every "
            "exact 3-total rational decoder with v = 5 and tau >= 1. "
            "Corroboration: 120 realizable tau >= 1 v = 5 decoders (tau-forced "
            "generator) all have exact box >= 5 with replayed in-box witnesses; "
            "a 35-instance hunt (tau-targeted, PR 2978-core extensions, "
            "nullspace-dense) finds 0 falsifiers. VERDICT (b): PR 2978's "
            "3/3/21 classification replayed exactly (same seed and stages); the "
            "cap push (exact kernel q-solver, 10000 P-restarts per pattern, plus "
            "the vendored big alphabet at 2000) realizes none of the 21; one "
            "pattern is PROVEN unrealizable ((a0,b0) = (3^3,3^3) with complete "
            "Z: A1 gives p_2 == 0 so rank(M) <= 2, but complete Z forces "
            "diagonal rank 3); the remaining 20 stay CHECKED not-found-in-cap "
            "(all 20 are shareable class r_box = 3; the proven-unrealizable one "
            "forces r_box = 2, correcting PR 3012's 'all 21' framing). "
            "VERDICT (c): F-star is NOT proved and NOT refuted; cert >= "
            "floor(2v/3) has survived every falsifier test in the lineage, and "
            "the box floor is now PROVEN on the full tau >= 1 domain for "
            "v <= 5.",
        "existing_restriction_being_changed":
            "PR 3012 recorded the tau >= 1 box floor as 'PROVEN for v <= 4, "
            "bounded at v = 5 (240 instances, 0 below threshold), first open "
            "case v = 5'. This package converts the bounded v = 5 evidence into "
            "a proof by exhaustive envelope classification plus exact "
            "blocking-Z enumeration, and settles one of the 21 shareable-class "
            "patterns.",
        "falsification_test":
            "The v = 5 floor claim is falsified by any exact 3-total rational "
            "decoder with v = 5, tau >= 1 everywhere and exact box <= 2 "
            "(ladder-exact; both sides certified by replayed witnesses). The "
            "envelope classification is falsified by any 5-line type multiset "
            "with envelope box = 2 outside the 33 recorded families (the "
            "enumeration is exhaustive over 749398 multisets and re-runs from "
            "scratch). The blocking-Z claim is falsified by any surviving shape "
            "and any non-complete arc subset that blocks all ten triples "
            "(per-triple tables are exact kept-3 feasibility). The shareable "
            "replay is falsified by a pattern whose replay status differs from "
            "3 realized / 3 unrealizable-column / 21 not-found-in-cap.",
        "intended_artifact":
            "research/fstar-boxfloor-v5-seedab80f07c/ with verify.py "
            "(python3 -B research/fstar-boxfloor-v5-seedab80f07c/verify.py) and "
            "the vendored predecessor/pr3012/anchor_replay.py.",
        "method":
            "Smallest falsifying instance first. (1) Written reduction: box "
            "depends only on (a0, b0, Z) and is monotone non-increasing in Z; "
            "Lemma SG forces Z inside the even pairs; so a realizable box-2 "
            "decoder must sit inside a box-2 combinatorial envelope. (2) "
            "Exhaustive envelope enumeration at v = 5 (749398 raw-type "
            "multisets; cheap singleton-witness test memoized, exact kept-set "
            "ladder as fallback; ladder pinned to the independent "
            "definition-level brute enumeration on 400 random configs). (3) "
            "Anchor-attainment screen (engine-definition facts) on the 33 "
            "families. (4) Exact blocking-Z enumeration per surviving shape "
            "(2^20 subsets against exact per-triple blocking tables) with the "
            "rank obstruction recorded. (5) Realizable replay on 120 "
            "tau-forced decoders; bounded falsifier hunt (35 instances). "
            "(6) Shareable class: exact replay of PR 2978's realize pipeline "
            "(same seed), then a cap push with an exact kernel q-solver. "
            "Int-only arithmetic; every acceptance engine-checked with "
            "replayed witnesses.",
        "nearest_overlapping_prs":
            "PR 3012 (Lemma K, Lemma LB2, Lemma TB, the four tau = 0 falsifiers "
            "and the recorded v = 5 obstruction shape - the predecessor and "
            "handoff source), PR 2978 (Lemma V2, Lemma RT + shareable totals, "
            "the v = 3 combinatorial census and realize_kj), PR 2963, PR 2936, "
            "PR 2914 (sub-anchor box, Lemmas SB/LB). None enumerates the v = 5 "
            "combinatorial envelope, none gives the anchor-attainment screen, "
            "and none settles any of the 21 patterns.",
        "open_questions": [
            {
                "blocked_by":
                    "The same reduction works at v = 6 but the blocking-Z "
                    "enumeration grows (2^30 arc subsets needs smarter "
                    "propagation); no obstruction is recorded yet.",
                "first_step":
                    "Run the envelope classification at v = 6 (threshold 4) and "
                    "enumerate blocking Z per surviving shape with constraint "
                    "propagation; smallest falsifying instance first.",
                "question":
                    "The tau >= 1 box floor at v = 6: box >= 4 on that domain?",
                "why_it_matters":
                    "v = 6 is now the first open case of the tau >= 1 floor; the "
                    "same envelope + blocking-Z pipeline should decide it.",
            },
            {
                "blocked_by":
                    "The 20 patterns survive an exact kernel q-solver at 10000 "
                    "P-restarts and the big alphabet at 2000; unrealizability "
                    "needs a valuation-level argument beyond the anchor screen.",
                "first_step":
                    "Characterize the (a0, b0, Z) patterns forced by rank-3 "
                    "factorizations with prescribed odd/even valuations (the "
                    "kernel feasibility condition p(t) not in span{p(u) : "
                    "(u, s) in Z} for all non-arcs is necessary and sufficient "
                    "for the Z side; the anchor side needs valuations).",
                "question":
                    "Are the remaining 20 v = 3 combinatorial gap patterns "
                    "realizable (shareable-class completeness at v = 3)?",
                "why_it_matters":
                    "All 20 lie in the shareable class (r_box = 3); a "
                    "realization refutes box-completeness there; "
                    "unrealizability would prove it.",
            },
            {
                "blocked_by":
                    "The named/box/cert relations are mapped but the last rung "
                    "cost >= cert has no proof-level improvement in reach.",
                "first_step":
                    "Use the tau-pattern control (Lemma K, LB2, TB plus this "
                    "package's envelope classification) to state a joint lower "
                    "bound in the shareable-class vocabulary.",
                "question":
                    "F-star itself: cert(M) >= floor(2v/3) at general v.",
                "why_it_matters":
                    "It is the named route to closing every open T = 3 window; "
                    "it has survived every falsifier test in the lineage.",
            },
        ],
        "optimistic_full_cost_budget":
            "No kappa claim; the milestone is the settled v = 5 floor question. "
            "Compute cap: envelope enumeration ~25 s; blocking-Z enumeration "
            "~6 s per shape (6 shapes); shareable replay + push ~70 s; anchor "
            "replay ~120 s; every registered command well under the 600 s cap, "
            "all blocking with periodic receipts.",
        "outcome": "completed",
        "parameter_ranges":
            "v = 5 (floor) and v = 3 (shareable class); three totals; label "
            "space F2^3 bit masks; 5-line type multisets over 37 raw (a0, b0) "
            "types with tau >= 1 (749398 multisets, all joint bit structures up "
            "to line relabeling); all 2^20 arc subsets per surviving shape; "
            "integer P, Q entries in {-7..7} for the hunt and "
            "{-3,-1,1,3}/{-2,2} odd/even recipe alphabets for realization.",
        "predecessor_authors":
            "PR 1590 DreamingOfClouds (Claude Opus 5.5 (Anthropic) via Claude "
            "Code assistance); PR 2111 DreamingOfClouds; PRs "
            "2717/2747/2774/2869/2890/2901/2914/2936/2963/2978/3012 Aaron Wang "
            "(navinor); all verified at current ground truth with gh pr view "
            "--json author,title on 2026-10-16.",
        "schema_version": 1,
        "scope_change_reason":
            "Authorized 'explicit open request' scope change to kappa-blocker "
            "KB5L, recorded per the assignment (discussion 1166; the first open "
            "case of the tau >= 1 box floor at v = 5 plus the shareable-class "
            "remainder, as recorded by PR 3012, is the named open request). The "
            "chooser draw (seed 77e4d785b77ca4c31a99b98a9b8143d4, track "
            "complex-mechanisms) proposed complex-new-helper-inventory, "
            "p104-side-correction and complex-rank-shape-decoder; none is this "
            "object, and the assignment takes the KB5L request instead. Pair "
            "collision check at entry (discussions 1166/1317 via disc-comments "
            "--grep, complete windows through 2026-10-16 18:00 UTC, and "
            "find_overlap.py with the object's proper names) found no CLAIM on "
            "this object: KB5k (PR 3012) was released at 17:37 UTC and KB5L "
            "was unclaimed.",
        "scope_status": "changed",
        "stop_rule":
            "Stop when the v = 5 tau >= 1 floor is settled (proved or exact "
            "minimal falsifier) and the shareable-class remainder is pushed "
            "with any settled pattern recorded. Achieved: floor PROVEN; 1 of 21 "
            "patterns PROVEN unrealizable; 20 remain CHECKED not-found-in-cap "
            "under the pushed cap. No further search without a new hypothesis.",
        "task_id": "complex-new-helper-inventory",
        "time_compute_cap":
            "One bounded pivot maximum (the v = 5 tau >= 1 floor); registered "
            "replay under 600 s per command (observed: verify.py ~250 s, "
            "anchor_replay.py ~120 s); all searches deterministic (fixed seeds "
            "and instance counts, not wall-clock caps).",
    }
    task["original_card"] = card
    n_pins = gen_pins()
    SOURCES = {
        "base_commit": BASE,
        "files": [
            {"path": "certificates/selected-result.json",
             "usage": "provenance",
             "git_blob": git_blob("certificates/selected-result.json"),
             "sha256": sha256_file(os.path.join(REPO, "certificates",
                                                "selected-result.json"))},
            {"path": "docs/research/agent-task-catalog.json",
             "usage": "provenance",
             "git_blob": git_blob("docs/research/agent-task-catalog.json"),
             "sha256": sha256_file(os.path.join(REPO, "docs", "research",
                                                "agent-task-catalog.json"))},
            {"path": "research/root-unit-decoder-lemmas/README.md",
             "usage": "input",
             "git_blob": git_blob("research/root-unit-decoder-lemmas/README.md"),
             "sha256": sha256_file(os.path.join(REPO, "research",
                                                "root-unit-decoder-lemmas",
                                                "README.md"))},
        ],
        "schema_version": 1,
    }
    VERIFY = {
        "commands": [
            {"argv": ["{python}", "-B", "{package}/verify.py"],
             "checks":
                 "KB5L package replay: vendored PR 3012 pin set (%d files); "
                 "the exact v = 5 tau >= 1 floor chain (ladder pinned to "
                 "definition-level brute on 400 configs; exhaustive 749398 "
                 "multiset envelope enumeration; anchor-attainment screen; "
                 "exact blocking-Z enumeration on 6 surviving shapes); "
                 "120 realizable tau-forced v = 5 decoders with replayed "
                 "witnesses; the 35-instance bounded hunt; the shareable-class "
                 "replay (3/3/21) and cap push; writes CERTIFICATE.json; "
                 "prints PASS_KL_* and PASS_KL_VERIFY" % n_pins,
             "timeout_seconds": 600},
            {"argv": ["{python}", "-B",
                      "{package}/predecessor/pr3012/anchor_replay.py"],
             "checks":
                 "Predecessor anchor reproduction through the vendored PR 3012 "
                 "tree: its anchor_replay.py runs the vendored PR 2978 "
                 "verify.py UNCHANGED on a byte-copy and must print "
                 "PASS_KM_ANCHORS markers=12 digest=0b5b55f84375b37c "
                 "vendored-verify=exit0, including PASS_FG_CALIBRATION "
                 "tied_min=11/12 cex_min_1=18/19 mp=9/16 chain=22 "
                 "reach=0/12,8/19, PASS_KJ_COUNTEREXAMPLE v=3 tau=2/2/2 "
                 "cert=3 box=2 r_box=2 independent=3/2 and the PR 3012 "
                 "markers PASS_KM_VERIFY falsifiers=4 lb2=16761 mixed=240 "
                 "v3-configs=3023 pivot=240 digest=fb29a75bde520732",
             "timeout_seconds": 600},
        ],
        "inputs": [
            "research/root-unit-decoder-lemmas/README.md",
            "research/fstar-boxfloor-v5-seedab80f07c/floor_v5.py",
            "research/fstar-boxfloor-v5-seedab80f07c/family_v5.py",
            "research/fstar-boxfloor-v5-seedab80f07c/shareable_v3.py",
            "research/fstar-boxfloor-v5-seedab80f07c/verify.py",
            "research/fstar-boxfloor-v5-seedab80f07c/README.md",
            "research/fstar-boxfloor-v5-seedab80f07c/TASK.json",
            "research/fstar-boxfloor-v5-seedab80f07c/data/floor-v5-receipt.json",
            "research/fstar-boxfloor-v5-seedab80f07c/data/family-v5-receipt.json",
            "research/fstar-boxfloor-v5-seedab80f07c/data/shareable-v3-receipt.json",
            "research/fstar-boxfloor-v5-seedab80f07c/predecessor/PINS.json",
        ],
        "python": "3.12",
        "requirements": [],
        "schema_version": 1,
        "status": "ready",
    }
    for name, obj in (("TASK.json", task), ("SOURCES.json", SOURCES),
                      ("VERIFY.json", VERIFY)):
        with open(os.path.join(HERE, name), "w", encoding="utf-8",
                  newline="\n") as fh:
            json.dump(obj, fh, indent=1, sort_keys=True)
            fh.write("\n")
    with open(os.path.join(HERE, "TASK-CARD.md"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write("# Drawn task card (verbatim): %s\n\n" % task["task_id"])
        fh.write("Scope changed to kappa-blocker KB5L (explicit open request "
                 "from discussion 1166); see TASK.json `scope_change_reason` "
                 "and `actual_scope`.\n\n")
        fh.write("```json\n")
        fh.write(json.dumps(card, indent=1, sort_keys=True))
        fh.write("\n```\n")
    print("PASS_KL_META task=1 sources=3 verify-commands=2 pins=%d" % n_pins)


if __name__ == "__main__":
    main()
