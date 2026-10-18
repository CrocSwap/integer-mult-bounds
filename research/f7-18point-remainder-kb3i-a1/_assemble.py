"""Assemble TASK.json / SOURCES.json / VERIFY.json for the KB3i package,
embedding the drawn catalogue card verbatim so the checker's original_card
dict-equality holds.  Writes each file with LF newlines (byte-stable replay)."""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.stdout.reconfigure(encoding="utf-8")

BASE = "d8e0f83f00191df62174b641e9fff055c357f641"
PKG = "research/f7-18point-remainder-kb3i-a1"

card = json.load(open(HERE / "_card.json", encoding="utf-8"))

provenance = [
    {"path": "docs/research/agent-task-catalog.json",
     "git_blob": "67f085acd86acd7d4e03922d9cf4b26bca66fed5",
     "sha256": "47b42433f5a85809a3aadd29c2c339da2c6ed728e4f7762df6b88bccb7874cf0",
     "usage": "provenance"},
    {"path": "certificates/selected-result.json",
     "git_blob": "b1fea0c94436b236cc2b7d41a7be032811b94c81",
     "sha256": "bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129",
     "usage": "provenance"},
]

vendored = [
    ("vendor/tight.py", "14670ef2d3df9e4ecc9e1db962f4e8cb77545d1c889144352760c1fd14e2273b", 2961,
     "bitmask primitives, the (7,1) Fourier identity, rho classification"),
    ("vendor/cover18.py", "24c6a2f4911dc2d5de76972eb5ae93dc4e66d8fa1e904443de6d0638e70c0a04", 2961,
     "the reduced (A,D) covering model, Fourier profile system, squeeze numbers, pair-representation rows, bounded search"),
    ("vendor/vanish.py", "6c605c54074f725321c5d770d538a652bf7727598a128270831f92fe7b9746d9", 2961,
     "the vanishing-character class tables and the L7 Sidon tight-equality lemma"),
    ("vendor/agent64_cover17.py", "082bc838134cba9754368cff894d53c729467a689b4cafee8374423688d93654", 2773,
     "profile_c_values (PR 2773 pair-representation shape primitives)"),
    ("vendor/agent64_search17.py", "9eb1bf79ffb99b0efcdaf57916c493bc781abd4a0096d584dc6bc6ca294bf674", 2773,
     "the 17-point search primitives (PR 2773)"),
    ("vendor/anchors.py", "73d73a9b94539403448d7ff8c914c03711907f75c019c4ccb6843b32c259e8e7", 2961,
     "the anchor-reproduction helpers"),
]

references = [
    {
        "local_path": lp,
        "source_path": "research/f7-18point-tight-classes-seed4c1e7b30/" + lp.split("/")[1]
                       if pr == 2961 else "research/f7-18point-rows/" + lp.split("/")[1],
        "pr": pr,
        "sha256": sha,
        "note": "Vendored byte-exact (extracted with agent_tools.py pr-tree-extract from the immediate predecessor "
                "PR 3023's package research/f7-18point-avtail-seed010d26fa, which vendored it from PR %d), credit "
                "Aaron Wang (navinor), PR %d: %s. Enforced by byte-pin checks in verify.py." % (pr, pr, what),
    }
    for (lp, sha, pr, what) in vendored
]

task = {
    "schema_version": 1,
    "task_id": "bit-new-register-model",
    "scope_key": "7084092dd726e7ba1f2f (drawn card); refined object key f7-18point-remainder-kb3i",
    "track": "bit-mechanisms (drawn); scope changed to the assigned explicit open request kappa-blocker KB3i: "
             "the FINAL 18-point remainder for F2^7 - decide (12,6) A-vanish (4,2)/(3,3) and break the both-odd "
             "splits (11,7)/(9,9) (PR 3023's recorded remainder)",
    "scope_status": "changed",
    "scope_change_reason": "Authorized 'explicit open request' scope change, recorded as instructed by the assignment. "
        "The chooser (seed 80ba761410c9ac2a5210cedf738100a6, track bit-mechanisms) drew the cards "
        "bit-new-register-model / bit-helper-contract (a larger/nonabelian register model and a helper-mixing word; "
        "neither targets the F2^7 cover question, and the draw landed on bit-mechanisms cards rather than the "
        "set-level F2^7 track). The assignment (kappa-blocker KB3i) explicitly authorizes taking discussion 1166's "
        "open request instead - the FINAL 18-point remainder for F2^7 recorded by PR 3023 (its open questions 1-3): "
        "the surviving (12,6) A-vanish classes (4,2)/(3,3) and the both-odd splits (11,7)/(9,9) that carry no "
        "vanishing character. Pair-collision checks (discussions 1317 and 1166 via agent_tools.py disc-comments "
        "--grep including nested replies, before computation, plus a refined re-run with the object's proper names "
        "and synonyms) found no claim on this object; the concurrent f(7) work (PR 2973/PR 3005, Nicholas Stone / "
        "Nick Petalas) is WORD level and this task stays strictly on the SET level.",
    "actual_scope": "Kappa-blocker KB3i (explicit open request; set level, no words): the FINAL 18-point remainder "
        "for F2^7 (exact condition P + P = F2^7 in the PR 943 prefix-walk model) - does ANY 18-point set cover F2^7? "
        "The 17-point question is closed (PR 2542/2773/2870); the 18-point splits (12,6),(11,7),(10,8),(9,9) survive "
        "(PR 2911); (10,8) is fully excluded (PR 2961); (12,6) A-vanish (5,1) is PROVEN impossible (PR 3023). "
        "REMAINDER taken here: (12,6) A-vanish (4,2) and (3,3), plus the both-odd splits (11,7) and (9,9). "
        "Delivered outcome=partial (narrowed remainder, no false kill): (a) (4,2)/(3,3) NOT decided (walk-ready "
        "reduced forms with budgets, walks too large for the session); (b) the both-odd parity shortcut to breaking "
        "(11,7)/(9,9) is PROVEN false by a complete m=3 census (both-odd reduced covers exist), the m=5 ground truth "
        "(F2^5 covers only in even splits (2,8)(4,6)(6,4)(8,2)) is established and its obstruction localized per "
        "split, and it is shown NOT to lift as a parity rule; the exact rho^2/identity frontier for (11,7)/(9,9) is "
        "reproduced and pinned (E_o=13/17, even_half_max=42/34, min sum rho^2=17/19); (c) bounded construction "
        "search finds no covering 18-set (best 118/128 at k=18, consistent with the 119/128 record ceiling).",
    "bottleneck_link": "The set-level restricted addition basis value r((C2)^7) decides how small a universal word's "
        "prefix set can be inside the unchanged PR943 query model: 17-point covers are excluded and the 18-point "
        "question is narrowed to four splits, with the vanishing classes pressed (PR 2933/2961/3023). Under the "
        "concurrent word-level gap 22 <= f(7) <= 24 (PR 2973/3005), whether any 18-point set covers F2^7 is the "
        "deciding necessary condition for f(7) = 22: if none covers, every universal word at L=22 needs >= 19 "
        "distinct prefixes. This package narrows the remainder (demotes the parity shortcut, localizes the m=5 "
        "obstruction, pins the identity frontier) but decides no class outright. It changes no supplier, tariff or "
        "kappa and instantiates no physical interface.",
    "stop_rule": "Stop at the first of: (a) a covering 18-set found in any surviving split (outcome (c), a "
        "construction), (b) one of (4,2)/(3,3)/(11,7)/(9,9) decided (PROVEN empty or a witness), or (c) the priced "
        "budget expiring with each class's exact status recorded. Outcome (c) reached: no class decided; the "
        "parity-shortcut route (b) pivoted once into the m=3/m=4 covering census which DEMOTED the shortcut and "
        "localized the m=5 obstruction, then stopped (one bounded pivot maximum). (4,2)/(3,3) recorded as exact "
        "walk-ready reductions with budgets (PR 3023's classification), not decided; (11,7)/(9,9) recorded at the "
        "rho^2/identity frontier, not excluded. No second pivot taken.",
    "smallest_falsifying_instance_first": "The falsifying instance for 'no 18-point cover exists' is one covering "
        "18-point set; for the both-odd parity hypothesis it is one covering both-odd reduced pair. The machinery was "
        "validated on the smallest instances first: all seven recorded anchors reproduced before any new number "
        "(FOURIER 7,1 =175/239, OBSTRUCTION 696/504/192, CLASSIFY 32=32 TIGHT cases=6720 recomputed live; "
        "CLASS82/CLASS60/AV51 read back from PR 3023's receipts). The parity hypothesis was then tested at the "
        "SMALLEST instance (m=3 complete census, 2^8 x 2^8 subset pairs) where covers are known to exist, so a "
        "false-empty is distinguishable from broken machinery (m=3 (5,5) has 3136 covers, (7,7) has 64). The m=5 "
        "ground truth was confirmed by complete m=4 sum-10 censuses (both-even (2,8)=15360,(4,6)=143360 cover; "
        "both-odd (1,9),(3,7),(5,5) empty) and the (5,5) self-obstruction localized (4,085,760 cross-covering pairs, "
        "all fail self, max self-union 15/16).",
    "outcome": "partial",
    "author": "Aaron Wang",
    "ai_assistance": "Substantial AI assistance from opencode in scoping, implementation, verification and writing "
        "(no model named); no independent human review claimed.",
    "evidence": "CERTIFICATE.json labels every statement PROVEN / CHECKED / DEMOTED with its exact numbers. "
        "verify.py re-derives every cited number (three modes: quick = anchors + the complete m=3 parity-demotion "
        "census + the (11,7)/(9,9) frontier; full = the complete m=4 sum-10 censuses (m=5 ground truth) + the (5,5) "
        "self-obstruction localization; search = the bounded construction ceiling). parity_census.py is the complete "
        "reduced-covering census (m=3 exhaustive 2^8 x 2^8); split_census.py is the per-split complete census with a "
        "cross/self failure breakdown; self_obstruction.py localizes the (5,5) self failure (selfsum sizes, ranks, "
        "self-union deficit); fourier_probe.py prints the rho^2/identity numbers; construct_search.py is the bounded "
        "seeded construction search. The six vendored engines are byte-exact with SHA-256 pins (verify.py check_pins). "
        "Anchors reproduced before any new number (see README): PR 2870 OBSTRUCTION 696/504/192 and PR 2911 "
        "ROWS18/NOVANISH, PR 2933 CLASSIFY cases=6720 TIGHT=2, PR 2961 FOURIER (7,1) need=175 lower=239 recomputed "
        "live; CLASS82 checked=28,815,360 covering=0, CLASS60 d_checked=169,911, PR 3023 AV51 uv_pairs=3,049,492,320 "
        "covering=0 read back from PR 3023's per-shard receipts (values match exactly).",
    "de_diagnostic": "Not applicable: a finite set-level question in the PR943 query model, with no supplier width m, "
        "role count W, child ranks or recursive moment to price. The applicable diagnostic is exact reproduction "
        "against the pinned predecessor numbers plus complete exact-integer enumerations with brute-force-validated "
        "censuses.",
    "open_questions": [
        {"question": "Push the even-half (self-sum) coverage identity for (11,7)/(9,9) (PR 2961's open question 2): "
                     "what identity couples odd-line cross-sum multiplicities to even-line selfsums where no character "
                     "can vanish and sum rho^2 >= 17/19 does not contradict?",
         "why_it_matters": "These two both-odd splits carry the other half of the 18-point question (row remainders "
                           "501/196); the PR 2870 squeeze uses only odd coverage and requires opposite parity, so the "
                           "un-pushed even-half (self-sum) direction is the one route left to break them.",
         "first_step": "Derive the even-half self-sum multiplicities ((A+A) u (D+D) = E) at the 501/196 surviving rows "
                       "and check them against every cover of F2^5 (PR 2933's census) before lifting to m=6.",
         "blocked_by": "No known coupling identity between odd-line cross-sum multiplicities and even-line selfsums "
                       "(PR 2961 recorded the same blocker); the parity shortcut is DEMOTED (both-odd covers exist at "
                       "m=3), so no self-sum-size argument is available either."},
        {"question": "Decide (12,6) A-vanish (4,2): does the exact reduced form (W 4-sets, D1 = {0,1}) admit a "
                     "covering (U,V,W) triple?",
         "why_it_matters": "(4,2) is the next surviving (12,6) class after (5,1)'s exclusion; clearing it forces any "
                           "(12,6) A-vanish cover into (3,3).",
         "first_step": "Extend the (5,1) walk to W 4-sets and D1 = {0,1}: enumerate normalized pairs (U,V) with "
                       "|U+V| >= 24 and per pair the W candidates with M = F2^5 \\ (U+V) in W u (W+1), testing the "
                       "four reduced lines exactly; shard over normalized U with per-shard receipts and generous "
                       "budgets (PR 3023's lesson: 3000 s was too small).",
         "blocked_by": "Nothing structural; the walk is strictly larger than (5,1)'s 3,049,492,320-pair walk (need 24 "
                       "vs 27 and looser W), a few hours of sharded walk beyond this session's budget."},
        {"question": "Decide or identify (12,6) A-vanish (3,3): is it realizable, and does any coupling of the four "
                     "slack L3 lines exclude it?",
         "why_it_matters": "(3,3) is the last A-vanish class after (4,2); excluding all three A-vanish tail classes "
                           "would leave (12,6) covers dependent on D-vanish (9,3)/(8,4)/(7,5)/(6,6) only.",
         "first_step": "Set up the exact normalized enumeration for (A0,A1 6-sets, D0,D1 3-sets) with 0 in A0, 0 in "
                       "A1 and complete the four-line test per configuration, or derive a cross-line multiplicity "
                       "identity coupling (I)/(II) with (III)/(IV).",
         "blocked_by": "No forced structure: all four line budgets are slack at (3,3) (line IV: 36+9 against 32); the "
                       "direct configuration space needs a new reduction or a much larger walk."},
        {"question": "Find a valid lift of the (5,5) self-sum obstruction to (9,9): at what m/split threshold, if any, "
                     "does a self-sum-size bound forbid a both-odd self cover?",
         "why_it_matters": "The m=4 mechanism (|A+A| <= 11 for cross-covering (5,5), self-union <= 15/16) is "
                           "scale-dependent and fails at m=3 ((5,5) covers); a valid threshold would decide (9,9).",
         "first_step": "Enumerate cross-covering (k,k) both-odd pairs at m=3 and m=4 and record the selfsum-size "
                       "bound versus m; determine whether a rank/doubling invariant forces |A+A| below the covering "
                       "threshold for m >= 4.",
         "blocked_by": "The selfsum bound is not monotone in m (both-odd covers exist at m=3), so no general invariant "
                       "is yet identified."},
    ],
    "original_card": card,
    "base_commit": BASE,
    "selected_record_sha256": "bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129",
    "session_seed": "80ba761410c9ac2a5210cedf738100a6",
    "priced_budget_minutes": 150,
    "priced_budget_breakdown": "25 min entry orientation (task draw, pair-collision checks on discussions 1317/1166, "
        "overlap terms); 20 min predecessor extraction (PR 3023 pr-tree-extract to scratch, hash pins, author "
        "verification) and anchor reproduction (FOURIER/OBSTRUCTION/CLASSIFY/ROWS18/NOVANISH recomputed live; "
        "CLASS82/CLASS60/AV51 read back from receipts); 15 min the m=3 complete parity-demotion census and the "
        "(11,7)/(9,9) identity-frontier probe; 25 min the m=4 sum-10 ground-truth censuses and the (5,5) "
        "self-obstruction localization (cross-checking split_census.py vs self_obstruction.py vs verify.py full); "
        "15 min the bounded construction search; 30 min package metadata, registration (--check-only), PR markdown "
        "gates, PR and board posts.",
    "object_synonyms_used_in_overlap": [
        "18-point", "18point", "18-set", "A-vanish", "(4,2)", "(3,3)", "(11,7)", "(9,9)", "AV-tail",
        "vanishing character", "P+P cover", "P + P", "F2^7", "cover of F2^7", "rho", "cross-sum",
        "even-half coverage", "self-sum", "universal word", "L=22", "f(7)", "both-odd", "parity split",
    ],
    "pair_collision_check": {
        "checked_utc": "2026-10-16 entry (before computation) and a refined re-run before heavy computation",
        "result": "No claim on the 18-point set-level remainder (4,2)/(3,3)/(11,7)/(9,9) or the covering-split "
                  "census at any check. Discussion 1317 carries only word-level union-support posts (petalas, "
                  "16:41Z/17:01Z, PR 3005 corroboration of PR 2973) and bit-mechanism claims; nothing on this "
                  "object. Discussion 1166's recent posts are the predecessor/released lineage (KB3d 17-point "
                  "complete, KB5d/KB5e F-star residue) plus other tracks; no CLAIM on the 18-point remainder. The "
                  "concurrent f(7) line (PR 2973 Nicholas Stone, merged; PR 3005 Nick Petalas) is WORD level "
                  "(22 <= f(7) <= 24) and explicitly scopes the set-level chain PR 2773-3023 as unaffected. This "
                  "package stays strictly on the SET level and enumerates no words.",
        "threads_scanned": [
            "discussion 1317 full scan (agent_tools.py disc-comments --since 2026-10-16, incl. nested replies) + "
            "grep for 18-point/A-vanish/(4,2)/(3,3)/(11,7)/(9,9)/AV-tail/F2^7/KB3i",
            "discussion 1166 full scan (agent_tools.py disc-comments --since 2026-10-16, incl. nested replies) + "
            "grep for the object's proper names and synonyms",
        ],
        "tool": "agent_tools.py disc-comments --grep (with nested replies); timestamps used to scope to the last few "
                "hours",
    },
}

sources = {
    "schema_version": 1,
    "base_commit": BASE,
    "files": provenance,
    "references": references,
    "notes": {
        "concurrent_scopes": "Nicholas Stone (NicholasStone) PR 2973 (merged) and Nick Petalas (petalas) PR 3005 "
            "hold the f(7) WORD-level line (22 <= f(7) <= 24, a false-prune correction to the word-census parity "
            "budgets); PR 2973's scope note records bit 0 as valid in set-level searches and the set-level chain "
            "PR 2773-3023 as unaffected. This package is set-level only and enumerates no words. The pair-collision "
            "check (discussions 1317 and 1166 via agent_tools.py disc-comments --grep including nested replies) "
            "found no claim on the 18-point remainder (4,2)/(3,3)/(11,7)/(9,9) or the covering-split census.",
        "model_and_pinned_results": "PR943 query model (research/universal-connector-boundary, Ross Richardson); "
            "pinned f(5)=12, f(6)=16 (research/universal-connector-six-source, Doug Colkitt) and the word-level gap "
            "22 <= f(7) <= 24 (PR 2973/3005). Read and reproduced byte-exact: PR 2870 OBSTRUCTION 696/504/192, "
            "PR 2911 ROWS18 808/501/251/196 and NOVANISH, PR 2933 CLASSIFY cases=6720 TIGHT=2, PR 2961 FOURIER "
            "(7,1) need=175 lower=239 (all recomputed live from the vendored engines); PR 2961 CLASS82/CLASS60 and "
            "PR 3023 AV51 read back from PR 3023's per-shard receipts.",
    },
}

verify = {
    "schema_version": 1,
    "status": "ready",
    "python": "3.12",
    "requirements": [],
    "commands": [
        {"argv": ["{python}", "-I", "-B", "research/f7-18point-remainder-kb3i-a1/verify.py", "quick"],
         "checks": "Byte pins of the six vendored engines; anchor reproduction (PR 2961 FOURIER (7,1) need=175 "
                   "lower=239, PR 2933 CLASSIFY tight-equality Sidon cases=6720 and 32=32 TIGHT count=2, PR 2870 "
                   "OBSTRUCTION 696/504/192); the complete m=3 reduced-covering census (parity-shortcut DEMOTION: "
                   "both-odd covers exist, (5,5)=3136, (7,7)=64, (3,3)=0); the (11,7)/(9,9) identity-frontier numbers "
                   "(E_o=13/17, even_half_max=42/34).",
         "timeout_seconds": 60},
        {"argv": ["{python}", "-I", "-B", "research/f7-18point-remainder-kb3i-a1/verify.py", "full"],
         "checks": "quick plus the complete m=4 sum-10 split censuses (the m=5 ground truth: (2,8)=15360 and "
                   "(4,6)=143360 cover; (1,9),(3,7),(5,5) empty) and the (5,5) self-obstruction localization "
                   "(4,085,760 cross-covering pairs, self_covering_when_cross=0, max self-union=15/16). Complete "
                   "enumerations: a zero count PROVES the split empty at that (m, split).",
         "timeout_seconds": 600},
        {"argv": ["{python}", "-I", "-B", "research/f7-18point-remainder-kb3i-a1/verify.py", "search"],
         "checks": "The bounded construction search ceiling (route c): no covering 18-set found, best coverage "
                   "118/128 at k=18 (record ceiling 119/128, PR 2634).",
         "timeout_seconds": 120},
    ],
    "inputs": [
        "research/f7-18point-remainder-kb3i-a1/verify.py",
        "research/f7-18point-remainder-kb3i-a1/parity_census.py",
        "research/f7-18point-remainder-kb3i-a1/split_census.py",
        "research/f7-18point-remainder-kb3i-a1/self_obstruction.py",
        "research/f7-18point-remainder-kb3i-a1/fourier_probe.py",
        "research/f7-18point-remainder-kb3i-a1/construct_search.py",
        "research/f7-18point-remainder-kb3i-a1/vendor/tight.py",
        "research/f7-18point-remainder-kb3i-a1/vendor/cover18.py",
        "research/f7-18point-remainder-kb3i-a1/vendor/vanish.py",
        "research/f7-18point-remainder-kb3i-a1/vendor/agent64_cover17.py",
        "research/f7-18point-remainder-kb3i-a1/vendor/agent64_search17.py",
        "research/f7-18point-remainder-kb3i-a1/vendor/anchors.py",
    ],
}


def dump(name, obj):
    with open(HERE / name, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("wrote", name)


dump("TASK.json", task)
dump("SOURCES.json", sources)
dump("VERIFY.json", verify)
