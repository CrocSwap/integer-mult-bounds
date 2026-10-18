# Overlap receipt: open selected-replay tooling PRs

**Consolidation receipt. No new κ, no disposition, nothing closed.** The selected
frontier and every pinned file are unchanged.

This receipt covers eight open PRs at exact heads, against main `1f7a9349`. Seven
have the selected #1094 cold replay path as their premise; that path runs
`verify_frontier1094.py` → `1042` → `799` → `741`. The eighth, #1108, is included
because #1142 re-adds its package. Four of them (#1101, #1108, #1142, #1151) are
in the maintainer queue's next batch
(`research/community-efficient200-audit/QUEUE-CURSOR.json`).

| PR | Head | Author | Subject | Applies to main | Own checks at trial merge |
|---|---|---|---|---|---|
| #1101 | `4d45bef9` | rcfc-jreed | concurrent bit589/complex741 driver for the #741 ancestry | clean | PASS (8 tests) |
| #1108 | `b76bb285` | martinxxx9 | compact-boundary cancellation obstruction | clean | PASS |
| #1142 | `0c2873e6` | martinxxx9 | #1042 replay-capsule closure audit | clean | **FAIL** (see below) |
| #1151 | `99d4f42f` | thakrarsagar | parallel layer-end controls, frontier1042 chain | clean | PASS (`verify.py`, 155 s) |
| #1277 | `02d27951` | thakrarsagar | #1094 reuse-mode ancestry binding audit | clean | PASS |
| #1361 | `40965b22` | thakrarsagar | CI drift/trigger guard for the 35 hash-asserted files | clean | PASS (35 pins, 0 drift, 21 tests) |
| #1509 | `362d2f91` | thakrarsagar | checked `cpp_int` stand-in for bit589 step 4 | clean | PASS |
| #1646 | `3f21415b` | JosieElliston | sparse phase recipes, frontier1042 `phases` steps | clean (head on `858771bc`) | not rerun |

**Retention.** None of the eight heads has content already on main: no changed
path has an identical blob at the base. The only path that exists on main is
`.github/workflows/frontier1094.yml`, which #1361 edits. So there is nothing to
receipt as "already integrated". Each PR needs its own review.

**#1142 does not pass on current main.**

1. `research/frontier1042-capsule-closure-seed75/verify.py` prints `FAIL: repository pin
   differs: certificates/selected-result.json`. `PINS.json` pins the #1042 record
   (sha256 `207d1f49…`) at the path that now holds #1094's record.
2. That record is retained byte for byte at `certificates/checkpoints/frontier1042.json`.
   Changing only `selected_record.path` to that file gives
   `PASS_FRONTIER1042_CAPSULE_CLOSURE`. This was tested in scratch and is not part of this
   package. The contributor or reviewer should decide whether to repin.
3. The body's reproduce command, `make frontier1042-capsule-closure-verify`, exists
   neither in the PR nor on main.
4. #1142 also adds all seven files of #1108's `research/compact-boundary-cancellation-seed51/`.
   Five of them still differ after CRLF→LF normalization. #1142's copy is the
   earlier one: it pins `certificates/selected-result.json` to the #942 blob `3d7529d7`
   and fails with `Source drift`. #1108's copy pins `certificates/checkpoints/frontier942.json`
   and passes. Merging either PR and then the other gives an add/add conflict.

**Premises that still hold at the base.**
- #1277: `verify_frontier1094.py` still has exactly one bare `check_selected(...)`
  statement, so the `--baseline1042` reuse path discards its result.
- #1361: the guard still finds 35 live pins.
- #1101: `verify_frontier741.py` is unchanged since #1101's base.
- #1151, #1509: their declared inputs are unchanged.

**Pairwise overlap.** Apart from the #1108/#1142 collision, no two PRs in the family change the same file. The pairs that
look similar address different steps or questions:
- #1151 and #1646 cover the lec and phases steps of the frontier1042 chain.
- #1101 and #1509 both concern bit589 in the #741 ancestry. #1101 runs it concurrently
  with complex741; #1509 replaces Boost for its step 4. #1101's driver does not scrub
  `BOOST_INCLUDE`, but I did not test the two together.
- #1277, #1361 and #1142 cover three different parts of the selected evidence:
  #1277 checks the reuse-mode binding, #1361 checks CI drift and triggers, and #1142
  checks the archive bytes.

All the speed-up PRs (#1101, #1151, #1646) are opt-in and unwired. The pinned drivers
are unchanged, so none of them shortens `make frontier1094-verify` by itself. Their
equality claims differ, as their own PR bodies state:
- #1151: its receipts are byte-identical to the archived ones.
- #1646: it reproduces the pinned recipe digests.
- #1101: its output trees match the sequential driver's only after timing fields and
  timing-dependent digests are masked.

## Reproduce

```sh
python3 -B research/selected-replay-tooling-receipt/verify.py            # base-side facts + 5 controls
for n in 1101 1108 1142 1151 1277 1361 1509 1646; do
  git fetch origin pull/$n/head:refs/receipt/pr$n; done                 # exact heads, if still reachable
python3 -B research/selected-replay-tooling-receipt/verify.py --heads    # recompute per-PR facts
```

The default run, which is the registered one, needs Git history containing the base.
It checks the following at `1f7a9349`:
- the selected and #1042-checkpoint record hashes;
- the cold-chain calls;
- #1277's premise;
- the absent make target.

It also checks that five mutated receipts are rejected.

`--heads` recomputes, for every recorded head:
- the changed paths;
- the identical-on-main paths;
- clean application to the base;
- the #1108/#1142 byte differences, pin and add/add conflict;
- #1142's capsule pin.

It writes one temporary merge commit object, which Git garbage-collects as unreachable.
If a contributor force-pushes, `--heads` fails rather than silently re-reading.

The trial-merge check results in `RECEIPT.json` (`trial_merge_checks_recorded`) are
recorded evidence from this session, not recomputed by `verify.py`. They come from a
shared macOS arm64 host with Python 3.14, and Python 3.12 for the registered packages.

**Not checked:** correctness of any PR's mathematics or speed claims beyond its own
verifier, the cold `make frontier1094-verify`, Linux, and the PRs outside this family.

## Open next questions

1. **Should #1142 be repinned or narrowed before review?** Its audit holds once it points
   at the retained #1042 checkpoint. The bundled seed51 copy duplicates #1108. First step:
   the contributor drops the seed51 files and repins one path. Blocked on: the contributor
   or a maintainer decision.
2. **Do other next-batch PRs collide with each other?** #1142 re-adding #1108's directory
   was found only because both were in this family.

   I ran an unregistered path-collision scan of the 100 `next_batch` heads (recorded only
   here, not checked by `verify.py`). Each pair was merged in order with true merge parents.
   - #1129→#1157 and #1148/#1178/#1195 merge cleanly in any order tried.
   - Besides #1108/#1142, these pairs conflict textually:
     - #1110/#1190 (`docs/research/pr-ledger.md`);
     - #1112/#1137 (`Makefile`);
     - `.gitattributes` in the gauge44-ends7 family. Merging any of #1104, #1107, #1117 or
       #1121 and then #1124 or #1130 conflicts, even though those heads are ancestors of
       #1124 and #1130; the reason was not traced. Merging any of the seven and then #1193
       also conflicts. #1104→#1107→#1117→#1121 merge cleanly.
   - #1172 conflicts with each of #1107, #1117, #1121, #1124 and #1130 inside
     `research/gauge44-ends7-t16/` (`MANIFEST.json`, `README.md`, `RESULT.json`,
     `data/`…). These look like competing versions of one package, which needs a reviewer's
     choice rather than a mechanical merge. I did not compare their contents.
3. **Which opt-in speedups should be wired into the pinned cold chain?** #1101, #1151 and
   #1646 each state their own equality evidence (see above). Wiring them needs pinned-driver
   changes that only a maintainer can approve.

## Credit

Covered PRs and their authors are listed above. The maintainer queue cursor and
efficient-review audit are by Douglas Colkitt. Prepared by Josie Elliston's donated
session with Claude Code (Claude Opus); see [TASK.json](TASK.json). Apache-2.0.
