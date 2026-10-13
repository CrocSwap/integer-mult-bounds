# PROOF-NOTE-BARCH: width-neutral triangle-hybrid B-delivery rewrite (U8)

Construction by NewBArch (`construction/barch/`, builder `build_tri.py`, controls `run_controls.py`, recipe
`RECIPE-U8.json`). Driver: `construction/barch/reproduce_barch.py`, chained after `construction/jx`.

## The move
On research/gauge44-frames-x's X4 word (`1e1d99ba…`), eight disjoint slots are rewritten. In each slot X an entering
copy E donates into a halves-copy X: 231 (E 450), 230 (E 452), 232 (E 454), 236 (E 456), 226 (E 451), 228 (E 453), 62 (E 455), 238 (E 457). That way, so that one target
read takes X + H in a single gate. A holder pair (for example 496/484) carries the value. Each holder is restored by a
low-end tail at its frame (early cleanup) and a FULL-cleanup restore. Entrance pre-reads keep the entering helper's
start value away from every target.

The recipe is explicit, with every index referring to the X4 word:
- 40 B deletions;
- 40 B insertions, each with its frame;
- 32 explicit re-chosen B frames;
- 8 early-cleanup tails;
- 8 FULL-cleanup restores.

The A section and X4's tail frames are untouched. The width is unchanged at 3778. The profile goes
{1:2548, 2:338, 3:430, 4:194, 5:56, 8:8} → {1:2548, 2:338, 3:446, 4:162, 5:72, 8:8}, a delta of {3:+16, 4:−32, 5:+16}.
The eight slots are additive (8 × 3.925e-8 ideal = 3.140e-7). Output word `090fd574…`. U8 contains B0's four slots
(231, 230, 226, 228) plus 232, 236, 62 and 238.

## Checks rerun on every rebuild
- `build_tri.py` (standard library only) checks the base sha (`1e1d99ba…`) and the result sha (`090fd574…`).
- `run_controls.py` produces 38 outcomes, all required. The control set is pinned in `LOCAL-PINS-barch-U8.json`.
  - C0 identity reproduces the input.
  - The recipe word PASSes #645's independent `audit_local.py`.
  - Four mutants must each FAIL `audit_local` with a pinned message, both globally and for each of the eight slots
    (NAME@X):
    - drop_restore: the holder is not restored, giving "all-column endpoint failure";
    - restore_full: the low-end restore is moved into the FULL cleanup, giving "all-column endpoint failure";
    - drop_preread: the inserted entrance pre-reads are omitted, giving "nonzero entrance response";
    - donation_after: the donation is placed after the target read, giving "nonzero entrance response".
- The per-end layer-end controls (`../layers_p6n/layer_end_controls.py`) reject 95.
- PR635's native chain runs, with the canonical word, local programs and Clifford recipes pinned.

## Strict
NewBArch's strict replay: the #741 map (`G44Pack/m741`, byte-identical OWNERS) is rebound to the U8 locals with
`rewidth.py` and admitted with this package's own code (NEWWORD `admit645.py` on research/gauge44-frames-x's tree).
The result is κ 0.001661948695165034, +3.1404e-7 over research/gauge44-frames-x. The four-slot subset B0 strict-passes
at 0.001661791659578416 and the single slot V1 at 0.001661673902364948.
