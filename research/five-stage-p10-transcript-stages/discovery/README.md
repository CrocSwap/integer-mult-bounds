# Discovery (not run by verify.py)

`repin.py` / `REPIN.md` are #315's re-pinning tools. The rest re-derives the transcript-stage selections on the p = 10
word. Each builder runs the package's own pipeline up to the stage before and freezes a selection bound to that
exact word. Python 3.12+ with sympy 1.14.0; `coll/families.py` and `coll/pack_restarts.py` also need numpy.

| step | command (from the package root) | result on this word |
| --- | --- | --- |
| descent | `python3 -B discovery/descent_search.py . descent-selection.json` | 480 gates, φ −637.17 |
| target squares | `python3 -B discovery/target_search.py . descent-selection.json target-selection.json` | 120 groups, φ −456.0 |
| kernel census | `discovery/dump_at.py . D target`, `coll/census.py D H.pkl` | 6,960 plain helpers (dims 1–15) |
| entrance pools | `coll/lines.py H.pkl L.pkl 5` (numpy), `coll/planes.py H.pkl P.pkl 15` (numpy) | 24,203 lines; 10,541 rank 2–14 intersections |
| shared-donor closure | `EXCLUDE=6439,6945,6949,8429,8459,8489,8519 ORDERS=4 NT=3 NOISE=0.3 SEED=5 coll/closure_pack.py H.pkl L.pkl P.pkl K.json`, then `coll/trim5.py H.pkl K.json K5.json` | 1,047 entries, rank 1,200, φ −1,601.47 (best of 16 seeds; −1,575 to −1,601) |
| kernel freeze | `python3 -B discovery/build_shared_kernel_selection.py K5.json` | delta read off the emitted word |
| restorations | `python3 -B discovery/build_restore_selection.py` | 240 helpers |
| sinks | `python3 -B discovery/build_sink_selection.py` | 7 sinks |
| second descent | `discovery/descent2_dump.py`, `descent2_search.py`, `descent2_freeze.py` | 0 gates (after the sinks and after the reorder) |
| reorder | `python3 -B discovery/build_reorder_selection.py reorder` | 133 moves, φ −276.09 |
| reorder round 2 | `python3 -B discovery/build_reorder_selection.py reorder2` | 0 moves |

The search tools are p = 10 ports of the p = 12 tools (φ(r) = r ln(100/r), frame ranks h − 4 and h − 3 for the
target squares, 20-coordinate exact linear algebra in `coll/linalg.py`). `descent_search.py` and `target_search.py`
are re-implementations that reproduce #287's frozen selections exactly on #287's word. `coll/` is the collective
census of our PR #284/#290/#299 with Rohan Arun's PR #300 restart loop; its κ printout uses the p = 10 ledger and
trims the packing to a total entrance rank divisible by 5 (needed for the width-100 bank tiling).

#320's kernel was the restart packing of `coll/families.py` circuits (pairs, triples, quadruples; 775 entries,
φ −1,355.95); the shared-donor closure above replaces it (+245.5 φ). Variants: lines only −1,513.8; #320's
rank ≥ 2 families preloaded plus lines −1,575.6; lines + intersections −1,591.1 (unrandomised). The same closure
on the final word of #320 (as a late `kernel2` round after the reorder, #319's placement) gives 95 entries, φ −55.06
(κ 7.69278157061989e-4, verified by a record-mode replay); after the new kernel it gives 4 entries (φ −0.77).

Kernel packing and sinks interact: on the post-target word the sink screen admits 7 helpers; six packings
(seeds 11–61, 400 restarts and 300 iterated-greedy rounds each) reach φ −1,353.8 to −1,360.3 but consume 3 of them.
Excluding the 7 (`--exclude` with `{"all": [6439, 6945, 6949, 8429, 8459, 8489, 8519]}`) costs ≈ 4.3 φ (best of seeds 11, 31, 61: seed 31,
φ −1,355.95) and keeps all 7 sinks (≈ −40 φ each), so #320 froze the excluded seed-31 packing; the closure above
excludes the same 7 helpers.

Prepared by Chafik Boukhalfa (chafreaky) with Anthropic Claude assistance; Apache-2.0.
