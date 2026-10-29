#!/usr/bin/env python3
"""Generate TASK.json and SOURCES.json for this package.

draw_card() reads the full catalogue card object from
docs/research/agent-task-catalog.json at the pinned base commit, so TASK.json's
original_card is byte-equal to the catalogue object (the generic generator's
trimmed card fails scripts/research_package.py's exact comparison).

Aaron Wang, with help from opencode. Apache-2.0.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TASK_ID = "complex-rank-shape-decoder"
BASE_COMMIT = "d8e0f83f00191df62174b641e9fff055c357f641"
CATALOGUE_SHA256 = "47b42433f5a85809a3aadd29c2c339da2c6ed728e4f7762df6b88bccb7874cf0"
SELECTED_RECORD_SHA256 = "bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129"
SEED = "1ed71298f6f32dd18e15e5ed217adb95"
SCOPE_KEY = "02b31ebd160542c86299"


def draw_card(task_id):
    """Return the full catalogue card object for task_id at the pinned base commit."""
    raw = subprocess.run(
        ["git", "show", BASE_COMMIT + ":docs/research/agent-task-catalog.json"],
        cwd=ROOT, capture_output=True, check=True).stdout
    catalog = json.loads(raw.decode("utf-8"))
    cards = [t for tr in catalog["tracks"] for t in tr["tasks"] if t["id"] == task_id]
    if len(cards) != 1:
        raise ValueError("expected exactly one catalogue card for " + task_id)
    return cards[0]


def git_blob(path):
    out = subprocess.run(["git", "ls-tree", BASE_COMMIT, "--", path],
                         cwd=ROOT, capture_output=True, check=True).stdout.decode("ascii")
    fields = out.split()
    if len(fields) < 3 or fields[1] != "blob":
        raise ValueError("missing blob at base commit: " + path)
    return fields[2]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    card = draw_card(TASK_ID)
    task = {
        "schema_version": 1,
        "task_id": TASK_ID,
        "original_card": card,
        "scope_status": "unchanged",
        "actual_scope": card["question"],
        "base_commit": BASE_COMMIT,
        "priority_revision": 6,
        "catalogue_sha256": CATALOGUE_SHA256,
        "selected_record_sha256": SELECTED_RECORD_SHA256,
        "assignment_seed": SEED,
        "assignment_scope_key": SCOPE_KEY,
        "bottleneck_link": (
            "Rank-1 children are about half of the selected word's recursive cost "
            "(2,412 of 5,586 local mass; effective child rank about 3.9). Block-climb "
            "delivery in fewer, larger-rank children is the card's lever (ideal rank-16 "
            "budget 2.31x in levers.py). The complete per-call profile, with charged "
            "frame transports and restoration, decides whether any charged realization "
            "of that lever survives."),
        "stop_rule": (
            "Stop at the smallest falsifying instance (the k=2 exact identity and its "
            "complete invoice), one bounded pivot to the PR 1605 threshold partitions "
            "and full reblock, and the recorded exact obstruction. Do not reprice the "
            "word's non-payload children, change the coverage law, or build a supplier."),
        "evidence": (
            "RESULT.json: k=2 exact identity classification (matching payload pairs admit "
            "only coordinate-aligned child outputs; mixing with free decode additions exists "
            "only for shared-row/shared-column pairs and never reduces charged transports); "
            "dirty gather-slot restoration forces at least one paid rank-1 save per block; "
            "per-group charged-climb nets are strictly negative for every k in 2..51, every "
            "alpha >= 1 transports per group, and every a <= 1/99 (closed form: a block group "
            "pays only when k^a > alpha + 1, i.e. a > ln(1+alpha)/ln k >= ln2/ln51 > 0.1757); "
            "complete per-call screens at a* = 21/20 * 1690054109089/1e15 fail for every "
            "per-group charged realization (one shared rank-16 transport already fails, "
            "matching PR 1605), and the card's +5% ceiling gate is missed by every charged "
            "realization screened at the threshold partitions (best case with full idle "
            "credit reaches +4.5% over the baseline ceiling) while it stays open for "
            "call-level invoices within PR 1605's 10 added rank units; controls include "
            "an independent cost enclosure cross-check and PR 1605 threshold "
            "sign reproduction."),
        "outcome": "negative-result",
        "author": "Aaron Wang",
        "ai_assistance": (
            "Substantial opencode assistance in choosing the scope, deriving the identity "
            "classification and transport obstruction, implementing the exact arithmetic and "
            "verification, and writing the documentation; no model named; no independent "
            "human review."),
        "open_questions": [
            {
                "question": (
                    "Do zero-charge co-frame climb groups exist among the selected word's "
                    "actual 2,412 rank-one payload children?"),
                "why_it_matters": (
                    "Only alpha = 0 groups (both operand vectors already at the block frame, "
                    "no restoration) clear the complete-profile gate; PR 1605's budget admits "
                    "zero added work at its k = 363 threshold and up to 10 added rank units "
                    "after full reblock, so co-frame coverage decides the whole lever."),
                "first_step": (
                    "Read the pinned t16 canonical word's per-child operand frames, partition "
                    "payload pairs whose two operand vectors already sit at one common rank-k "
                    "frame, and price exactly those groups with zero charged transports."),
                "blocked_by": (
                    "The per-child frame data lives in the pinned word archives "
                    "(t16/global/base/providers/gauge44); extracting and classifying it is a "
                    "separate data pass not attempted here."),
            },
            {
                "question": (
                    "What complete profile results if a block climb also replaces the word's "
                    "rank-2/rank-3 frame-step children (PR 1605 open question 2)?"),
                "why_it_matters": (
                    "Rank-one-only reblocking cannot reach a = 1/99; the frame-step children "
                    "are the 'rank-1 to rank-3 steps' the card names, and subsuming them in "
                    "one block climb is the only other mass-moving route."),
                "first_step": (
                    "Declare the joint replacement contract (which step children each block "
                    "group subsumes) and its coverage identity, then recompute the complete "
                    "per-call profile before any synthesis."),
                "blocked_by": (
                    "The coverage identity fixes paid mass at 72w + 64 per call; moving step "
                    "mass requires a proved replacement identity, which this package does not "
                    "supply."),
            },
        ],
        "claim_url": (
            "https://github.com/CrocSwap/integer-mult-bounds/discussions/1166"
            "#discussioncomment-18981731"),
        "overlap": {
            "entry": {
                "searched_at": "2026-10-16T19:22:14Z",
                "coverage": {
                    "open_prs": {"fetched_at": "2026-10-16T19:21:43Z",
                                 "complete_pagination": True, "records": 275},
                    "discussions": {"fetched_at": "2026-10-16T19:22:14Z",
                                    "complete_pagination": True, "records": 1756},
                },
                "limits": (
                    "Remote PR scope is open PRs including drafts. Closed work is searched "
                    "through local READMEs, TASK metadata and ledger only. No code diffs or "
                    "arbitrary package files are searched."),
            },
            "nearest_work": [
                {"pr": 1605,
                 "author": "Arham Tahir (Arham-Tahir64)",
                 "title": "Research: sharp rank-one block budgets and per-block overhead obstruction",
                 "retained_package": "research/complex-rank-one-block-budget",
                 "difference": (
                     "Cost-alphabet screening with generic added-work budgets; this package "
                     "constructs the smallest exact block-climb identity and prices its "
                     "charged frame transports and dirty restoration, closing its open "
                     "question 1 for every charged realization.")},
                {"pr": 1240,
                 "author": "Doug Colkitt (Mister-Meeseeks)",
                 "retained_package": "research/complex-local-word-ceiling",
                 "difference": "Packing ceiling and ideal lever budgets; retained as the screening engine."},
                {"pr": 1429,
                 "author": "Ali Romman (aliromman)",
                 "retained_package": "research/complex-block-rank-optimum",
                 "difference": (
                     "Moment optimality of fixed eight-array blocks and the transport-charge "
                     "contract (each rank-r transport charged as a rank-r recursive child) "
                     "that this package's invoices use.")},
            ],
            "pair_collision": (
                "disc-comments --grep scans of discussions 1317 and 1166 (nested replies, "
                "timestamps) found no live CLAIM on this object at entry; the Oct 14-15 "
                "complex-rank-shape-decoder claims there are all DONE/released."),
            "final_conclusion": (
                "No competing claim on the charged-climb realization question was located in "
                "the searched coverage; this is not proof of novelty."),
        },
    }
    (HERE / "TASK.json").write_text(json.dumps(task, indent=2) + "\n", encoding="utf-8", newline="\n")

    inputs = [
        "research/complex-local-word-ceiling/ceiling.py",
        "research/complex-local-word-ceiling/RESULT.json",
        "research/complex-rank-one-block-budget/RESULT.json",
    ]
    provenance = [
        "certificates/selected-result.json",
        "docs/research/agent-task-catalog.json",
    ]
    rows = []
    for usage, paths in (("input", inputs), ("provenance", provenance)):
        for path in paths:
            blob = git_blob(path)
            digest = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
            rows.append({"path": path, "usage": usage, "git_blob": blob, "sha256": digest})
    sources = {"schema_version": 1, "base_commit": BASE_COMMIT, "files": rows}
    (HERE / "SOURCES.json").write_text(json.dumps(sources, indent=2) + "\n",
                                       encoding="utf-8", newline="\n")
    print("WROTE_TASK_AND_SOURCES card_keys=" + ",".join(sorted(card)))


if __name__ == "__main__":
    main()
