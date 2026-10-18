# Retention receipt: #1015's block programs in main through #1062

**Research consolidation (credit and provenance). No new κ; no ledger, disposition or construction change.**

Main `c0e3631d` retains open PR #1015's work verbatim, but no ledger row, credit line or retained notice says so.
This receipt records the fact with hashes and adds the missing credit. It corrects an omission in my own #1062,
which copied the file.

| fact | evidence |
|---|---|
| retained file | `research/r439-bsection-stars-seed01/inputs/PR1015-CANDIDATE.json` (merged with #1062) has git blob `16532f2d`, identical to `research/r439-bsection-multwrite/CANDIDATE.json` at #1015's open head `7588c797` |
| what it contributes | 9 of the 10 phase-B block programs spliced into #1062's word |
| share of #1062's saving | 11,783 → 11,500 ADDs: **PR1015 244**, PR923 24, rerun star pass 15 (recomputed from #1062's `CERTIFICATE.json`; each gate saved counts twice, block plus literal cleanup) |
| ledger | `docs/research/pr-ledger.json` has a #1062 row whose scope names "nine PR1015 blocks", and no #1015 row |
| credit | `CONTRIBUTORS.md` credited #1062 and had no #1015 entry |
| notice | #1062's package has no NOTICE. #1015's `NOTICE.md` (blob `727d5b58`: Apache-2.0 offer, AI disclosure "Prepared with help from opencode", predecessor credits) was not retained beside the copied file. #1062's README and SOURCES.json do credit and pin #1015. |

## Change

- Adds `NOTICE-PR1015.md`, #1015's `NOTICE.md` byte for byte (blob `727d5b58`), so the license offer and AI
  disclosure accompany the retained file in main.
- Adds one `CONTRIBUTORS.md` line in the batch #1099 section, crediting Aaron Wang / navinor for #1015's retained
  programs. This follows the precedent of #946, "credited as pending integration".
- Does not edit `pr-ledger.*`, any batch disposition, the #1062 package or the selected record. #1015 stays open for
  its own review. Whether the ledger records it as "partially retained via #1062" is a maintainer decision.

```sh
python3 -I -B research/r439-pr1015-retention-seed95/verify.py
```

Expected (read-only, no network, standard library only):

```text
base ledger: #1015 row absent (gap recorded)
PASS_R439_PR1015_RETENTION blob=16532f2d saving=PR1015:244+PR923:24+star15=283 controls=2
```

The script recomputes both blob ids and the per-source split, and checks the credit line. It asserts the missing
ledger row only while the ledger is still the base blob; after a maintainer update it reports the new state
instead. Two negative controls must fail: a block misattributed to PR923, and a one-byte change to the retained
file.

## Reviewer notes for related open PRs

These were observed read-only at the stated heads and are not checked by `verify.py`.

- **#1122** (`a2551e70`, compose R439 A/B/star D to 10,652 ADDs) is a strict superset of merged #1062 plus merged
  #980's A part. Its `vendor/pr1062` files are byte-identical to main's merged files, so its "pending PR1062"
  wording is now stale. Its 848-not-872 accounting for #980 is forced: #980's B edits fall in frames 507–509 and
  519–523, inside the ten blocks #1062 replaces.
- **#1127** (`2e9dc9d3`, 3→2 z-program rewrites) is not additive to #1062 or #1122 as packaged. All 330 of its A
  moves fall in frames already rewritten by PR904–980, and all 75 of its B moves fall inside the ten replaced blocks.

## Provenance

Selected by a consolidation-track task card (`overlap-receipt`) from `scripts/choose_research_task.py --track
consolidation`. The track came from OS-random seed 95 under the user's sprint assignment. Base `c0e3631d`;
heads observed on 2026-10-14. Five explorer subagents evaluated alternative consolidation scopes and three judges
scored them. The scope was then narrowed to this credit gap, which is new and hash-checkable.

`NOTICE-PR1015.md` is Aaron Wang's text, retained under the repository's Apache-2.0 license. Everything else here was
prepared by Sagar Thakrar with substantial assistance from Anthropic Claude (Claude Code). Apache-2.0.
