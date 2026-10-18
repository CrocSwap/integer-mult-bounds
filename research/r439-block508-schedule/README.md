# R439 phase-B block 508: 37 to 30 additions (no new kappa)

Finite bit-supplier construction. The tuned R439 phase-B block at frame 508
(`B[205:242]` of `research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz`,
registers `[19, 27, 35, 43, 57, 65, 66, 74, 89, 97, 466]`) is replaced with a
30-addition program computing the identical forward integer map. Rebuilding its
literal reverse cleanup reduces the complete native word from **24,305 to
24,291 ADDs** (7 forward + 7 reverse).

| Quantity | Before | After |
|---|---:|---:|
| Block additions (frame 508) | 37 | **30** |
| Complete exported ADDs | 24,305 | **24,291** |
| Forward positive bound | 49,347 | 49,347 (equal) |
| Reverse positive bound | 1,113,070 | **1,086,054** |
| Payload | 93 bits | 93 bits (cap 104) |
| Local paid profile / rank mass | `{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}` / 5,129 | unchanged |
| Bit saving / kappa | conditional, complex-bound | unchanged, no new kappa |

## Method

The block is treated as an integer-linear straight-line program over its 11
registers. Discovery (`search.py`, deterministic, no randomness) runs a
forward dynamic program over realized-register subsets: each register is
realized once, in some order, from already-realized rows or entry singletons,
each donor used at most once (doubling-free positive-addition class). The
minimum is 30 and the recovered witness achieves it.

Verification (`verify.py`, imports no search code) rechecks the minimum with an
independently written backward Bellman recursion: 2,048 states, 11,264
state/destination pairs, 4,376 feasible edges, minimum 30. It further checks
forward integer-map equality, reverse-map entrywise domination (strict in 20
entries), all 2,048 Boolean input tables, the splice with literally rebuilt
cleanup, identical register frame paths, the unchanged paid profile and rank
mass, the exact F2 endpoint on all 661 columns, the inherited H1-H5 interface
and conclusions via the pinned `xcheck_p.py`, and the exported scalar bills
and positive/payload bounds via the pinned `export_records.py` (forward bound
equal, reverse bound reduced, payload 93 bits). Eight negative controls are
rejected.

This differs from the neighboring block results: PR #844 (block 4) optimizes
within a fixed two-factor split, PR #857 (block 8) searches whole-block
integer factorizations with randomized trials, and PR #843 (frame 509) reuses
one existing sum. The mechanism here is exact whole-block single-write
rescheduling with a certified class minimum. PRs #728/#792 change phase-A
mini-nodes (a different section); they report no improvement at frames 507/508
in their mini-node class, which does not cover this B-section block.

## Scope and obligations

Base `f567884aeb8851b6e794af1184119a3bfbe1e631` (selected PR799/PR589,
conditional kappa 0.001661634653669567). Only this directory is added;
`upstream/` and the selected certificate are unchanged. The minimum is
certified inside the doubling-free single-write class; multi-write
interleavings outside that class are not excluded. The C++ legality and
5/9/11-stage replays, hosted invoice, global assembly, Lean formalization and
remote CI are not run here; forward-map equality plus reverse domination imply
the payload bounds carry over, and an independent native replay remains to
confirm. All inherited all-size/compiler, common-label/mutable-source,
hosting, precision/tape and analytic assumptions remain.

## Reproduce

Standard-library Python 3.11+ from the repository root:

```sh
python3 -I -B research/r439-block508-schedule/verify.py
```

Expected: `PASS_R439_BLOCK508_SCHEDULE gates=37->30 ADDs=24305->24291
saved=14 columns=661 controls=8 minimum=30 rank_mass=5129 no_new_kappa`.

## Credit

Base word and checkers: eumemic (PR543/PR555), DreamingOfClouds (PR545/PR589),
Dylan Crow (record exporter), Zhihao Chen and the retained supplier lineage.
Method patterns adapt the open PR #844 (Gautam Gupta) and PR #792 (Ryan
Haines) verification structures with attribution; their objects and savings
are not imported. Prepared with help from opencode. Apache-2.0. No
independent human review is claimed.
