# Discovery (not run by verify.py)

`repin.py` / `REPIN.md` are #315's re-pinning tools. The rest re-derives the transcript-stage selections on #325's
p = 10 word. Each builder runs the package's own pipeline up to the stage before (`portable_bit.STAGES`) and
freezes a selection bound to that exact word. Python 3.12+ with sympy 1.14.0; `coll/` also needs numpy. The
closure seeds were run on two 20-core machines; every other step takes under a minute on a laptop.

| step | command (from the package root) | result on this word |
| --- | --- | --- |
| descent | `python3 -B discovery/descent_search.py . descent-selection.json` | 480 gates, φ −637.17 |
| target squares | `python3 -B discovery/target_search.py . descent-selection.json target-selection.json` | 120 groups, φ −456.0 |
| pre-kernel sink screen | `python3 -B discovery/sink_screen_at.py . descent_transform,target_transform` | 10 sink helpers (excluded from the kernel) |
| kernel census | `discovery/dump_at.py . D target`, `coll/census.py D H.pkl` | 6,900 plain helpers; all last reads before all touches |
| entrance pools | `coll/lines.py H.pkl L.pkl 5`, `coll/planes.py H.pkl P.pkl 15` | 24,127 lines; 7,045 rank 2–14 intersections |
| shared-donor closure | `EXCLUDE=6947,7141,7519,7789,7793,8407,8437,8501,8647,8677 ORDERS=4 NT=3 NOISE=0 SEED=0 coll/closure_pack.py H.pkl L.pkl P.pkl K.json`, then `coll/trim5.py H.pkl K.json K5.json` | 1,339 entries, rank 1,445, φ −2,376.62 (18 seeds, NOISE 0 and 0.3: −2,376.0 to −2,376.81 before the trim) |
| kernel freeze | `python3 -B discovery/build_shared_kernel_selection.py K5.json` | delta read off the emitted word |
| restorations | `python3 -B discovery/build_restore_selection.py` | 240 helpers |
| sinks | `python3 -B discovery/build_sink_selection.py` | 10 sinks |
| post-sink descent | `discovery/descent2_dump.py S.pkl`, `descent2_search.py S.pkl D2.json`, `descent2_freeze.py S.pkl D2.json descent2-selection.json` | 47 gates, φ −49.68 |
| reorder | `python3 -B discovery/build_reorder_selection.py reorder` | 130 moves, φ −296.89 |
| reorder round 2 | `python3 -B discovery/build_reorder_selection.py reorder2` | 2 moves, φ −5.55 |

The search tools are #320's p = 10 ports of the p = 12 tools (φ(r) = r ln(100/r), frame ranks h − 4 and h − 3 for
the target squares, 20-coordinate exact linear algebra in `coll/linalg.py`); `descent_search.py` and
`target_search.py` reproduce #287's frozen selections exactly on #287's word. `coll/` is the collective census of
our PR #284/#290/#299 with Rohan Arun's PR #300 restart loop and #320's shared-donor closure (`lines.py`,
`planes.py`, `closure_pack.py`, `trim5.py`); its κ printout uses the p = 10 ledger and trims the packing to a
total entrance rank divisible by 5 (needed for the width-100 bank tiling).

Without the sink exclusion the closure reaches φ −2,384.70 (1,371 entries) but consumes seven of the ten sink
helpers (≈ −40 φ each as sinks), so the excluded packing is frozen. The descent2 search finds the same 47 gates on
the post-restoration word (eumemic's #322 placement) and on the post-sink word; the stage is placed after the sinks.
A late shared-donor kernel round on the final word finds one rank-2 entry (φ −0.19), removed by the rank-5 trim.

Prepared by Chafik Boukhalfa (chafreaky) with Anthropic Claude assistance; Apache-2.0.
