# T37 exact allocation replay

This package reconstructs the complete 135,864-role allocation from a saved
integer flow, using the authentic T37 chronology in PR2833's frozen source
owners. It does not reuse any of that source's 480-helper allocation: all 408
helpers in each new call receive newly realized owners.

The two actual local providers have width inventory
`{4:26, 5:2, 7:62, 8:84, 9:234}` and paid profile
`{1:2394, 2:642, 3:266, 4:128, 5:26, 8:8}`. The four changed helpers are registers
460, 462, 478 and 480. Their actual words and native admissibility must be
verified separately by the complete contribution's unchanged scientific
guards; this allocation utility does not establish their local algebra.

Run with NumPy 2.4.5 and SciPy 1.16.1 (tested on Python 3.13.7):

```sh
PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
python -B replay_allocation.py \
  --source /absolute/extracted/gmx-t74-borrow43-handoff \
  --owner-engine /absolute/independent_candidate_owners_retired7.py \
  --work /absolute/fresh-output
```

The source is PR2833 head `e9307b48d7d1b690939935ecef0f8e524e6d92f4`.
The owner engine is the immutable file from PR2839 head
`2fdd289fcd0896f4691f9dd78a8bf1511573e434`.
`PINS.json` authenticates each actual input and all five emitted artifacts.
Regenerated `FILL.json.gz` is checked by the SHA256 of its entire decompressed
canonical payload, allowing compression-container differences across Python or
zlib versions. The original container SHA256 is retained for provenance; source
artifact container pins remain unchanged.
No solver or network access is needed for replay. The output must be fresh and
outside both source and this package. Source bytecode artifacts are rejected.

The replay checks all flow constraints with Python integers: exact bin counts,
global pattern counts, time/width demand, per-pattern width supply, source-window
eligibility, and at most one role in a given bin at each time. Each pattern is
then realized by edge coloring a regular bipartite multigraph. The colors are
literal bins; a perfect matching gives at most one role at each time. Distinct
children in one physical family have disjoint strict source windows, which is
checked before realization. The external owner engine subsequently checks every
literal helper, owner, family, prefix offset, time window and full paid profile.
This assigns helper names to existing source slots; it introduces no routing
operation or uncharged relabeling gate.

The exact integer patterns are:

| Capacity | Widths | Bin count |
| --- | --- | ---: |
| 8 | 8 | 24,864 |
| 16 | 7,9 | 15,021 |
| 16 | 8,8 | 1,554 |
| 16 | 7 | 1 |
| 32 | 4,9,9,9 | 8,658 |
| 32 | 5,9,9,9 | 666 |
| 32 | 7,7,9,9 | 2,812 |
| 32 | 9,9,9 | 4,440 |
| 48 | 9,9,9,9,9 | 3,197 |
| 48 | empty | 13,379 |

Idle cost is `8658 H1 + 3197 H3 + 4440 H5 + H9 + 13379 H48`. The rank9
residue is fully billed. The complete profile is
`{1:805860, 2:213786, 3:91775, 4:42624, 5:13098, 8:2664, 9:1, 48:13379}`;
live width is 33,152, physical width 33,642, and paid rank mass 2,408,256.

`construction/FLOW.json.gz` is the saved exact integer solution.
`construction/MODEL.json`, `SOLVER.json` and `DISCOVERY.log` record discovery.
CP-SAT 9.14.6206 found a feasible solution in 39.3081 seconds, using four workers,
seed 124 and a 300-second limit. Its `OPTIMAL` status refers to a feasibility
problem and does not assert global optimality of the mathematical bound.

`construction/discover_original.py` retains the research script as executed;
its original scratch paths are provenance, not a portable entrypoint.
`construction/PR2843-build_allocation.py` preserves the immutable upstream
algorithm used as the starting point. The portable replay removes optimization
and obsolete T74/T124 discovery branches, authenticates source inputs, checks
the saved flow exactly, and preserves the same edge-coloring realization.

The flow replay was executed in a fresh output path containing a space and
reproduced all five frozen output payloads exactly. The whole contribution's
independent native/global/outer replay is still the authority for the claimed
bound.

Three deliberately corrupted flows were also tested after refreshing their
test-only digest, so the tests exercise mathematical checks rather than merely
hash rejection: an increased pattern count, an increased time/width count, and
an out-of-window time all fail before an output directory is created.

`construction/check_compression_policy.py` additionally performs two complete
replays: changing only gzip level and timestamp succeeds with the identical
full payload; changing a single emitted owner offset fails before output.
Its arguments are the same `--source`, `--owner-engine`, and fresh `--work` paths
as above. Results are retained in `construction/COMPRESSION-CONTROLS.json`.
