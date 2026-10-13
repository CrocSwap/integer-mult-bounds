# PROOF-NOTE-LAYERS: earlier jp8 layers, here stacked on the no-triangle gauge44 word

> In this package the layers sit on the no-triangle word (R = 504), not on #645's 492-helper word. The mapping, the
> NP chain (regroup `864ff4a1` → swap `beb3579f` → layered `a9de804f`), the per-layer status on this base and the
> checks are in `PROOF-NOTE-NOTRI.md` ("Layers on this word"). The text below is research/gauge44-layered's note. It
> describes the same layers and controls on the 492-helper word; its word shas, helper numbers, counts and result
> table refer to that word.


This note covers the second change of research/gauge44-layered relative to research/gauge44-bit589. The first change,
the PR589 bit supplier, is covered unchanged by `PROOF-NOTE-BIT.md`. Here the community jp8 layers that were reviewed
on the k492 words (#629/#637/#641 lineage) are re-applied to #645's gauge44 provider word. The layers, their
construction code and their recipes were all reviewed earlier, on k492 words. This note says what carries over
unchanged, what is re-checked on the gauge44 word, and what is new. Sources: G44Stack's report (porting and checks on
gauge44); PivotReviewer's report (sections 1-4, Addenda 3-5); H4aReviewer's report (Addenda 7-8); JP8Ends' report.

## What the layered word is

`construction/layers/reproduce_layers.py` builds the layered word from a fresh `construction/reproduce.py --until word`
output. Each step is checked exactly:

1. **Pivot swaps** (`build_pivot_swap.py`, PR641's constructor, LF sha256 `8e8bced8…`, the file PivotReviewer signed for
   st2s4). It reads `PIVOT-SWAP-S6.json` and runs on #645's `regroup/FULL-WORD`. There are six pivot-role swaps: 488→560,
   489→561, 500→572, 501→573 (s4) and 513→537, 525→549 (s6). The `swaps` list is identical, gate for gate, to S6Ship's
   s6/s6j3 recipe (`k492-jp8-pivot_swap.json`); only `input_content_sha256` differs, because the base word is #645's
   regroup word. The constructor replays the zero response exactly, keeps the profile and width multiset unchanged, and
   rejects its 30 negative controls.
2. **HPE.** PR635's `build_hpe.apply` applies the inherited jp8 hyperplane-end changes (`HYPERPLANE-END-S6.json`). Its
   LF sha256 `23c9d7ce…` equals the k492 jp8 hyperplane_end recipe committed in s6j3 and earlier.
3. **cold44, exactly.** #645's `build_gauge_cold44.py` runs on the swapped HPE word. Its 44 rank-four cold ends, premix
   and low tails must equal the unswapped (pinned) cold44 construction; only the FULL inverse differs. Consequently the
   swaps touch no factory block.
4. **Layers.** PR635's unchanged `build_cold_end.apply(HPE, COLD-LAYERS-RECIPE)` applies the cold44 recipe plus:
   - 8 entering ends: 560/561/572/573 at U24 (s4) and 597/599/537/549 at U30 (x30: #629's E1 pair, which #645 dropped,
     plus s6's two ends);
   - 10 factored dim-8 cold ends: p123 (310/506, 311/504, 516/327) and q4 (579, 592, 589, 518).
   The output word's sha256 is pinned (`0be48b1d…`), as are its local profile `{1:2542, 2:414, 3:434, 4:154, 5:56,
   8:8}` and width inventory `{4:52, 5:48, 7:42, 8:116, 9:234}`. The recipe's `refactored_cleanup` meta lists the 8
   entering ends in `entering_low_frame_ended_helpers` (LayerReviewer's fix). That meta is copied into the word, which
   is why the pinned word sha moved from `b25f0ed9…` to `0be48b1d…`; gates, frames and report are unchanged.
5. **Layer-end controls** (`layer_end_controls.py`, LayerReviewer's adaptation of PR635's `cold_end_controls.py`
   d966e29a). These are raw-word negative controls on the layered word, judged by PR635's unchanged
   `hpe_audit_and_transport.py`. Each mutant must be rejected at its pinned reason. The adaptation has three parts: the
   lower→FULL mutant is pinned at "cleanup on non-FULL end", where gauge44 rejects it; entering ends come from the
   recipe meta; and the premix-gate controls are skipped for entering ends that have no premix gate. `reproduce_layers.py`
   requires exactly 59 rejections.
6. **Native locals.** PR635's native audit and transport, ledgers, local replay (the 192-bit payload bound), wrappers and
   phases all pass. The result is the `--local` that `verify_global.py` consumes.

G44Stack's run of this driver (`rlayers2`, all steps exit 0, 59 controls rejected) reproduces `locs/pq/local`, the
local G44Pack's strict runs used. Every SPEC-pinned artifact is byte-identical: CANONICAL-WORD, LOCAL-PROGRAMS,
LOCAL-CHECKS, INDEPENDENT-LOCAL-REPLAY, CLIFFORD-RECIPES, RESIDUAL-ADAPTERS and WRAPPER-CHECKS. CLIFFORD-REVIEW differs
only in a seconds field; its semantic hash is what SPEC pins. The two unpinned files that embed the word,
FULL-WORD and SCALAR-FRAME-AUDIT, differ because of the meta.

## Per-layer status on gauge44 (G44Stack, ideal Δκ at ×72)

| layer | prior review (k492 words) | on gauge44 | per-call Δ profile | ideal Δκ |
|---|---|---|---|---|
| pivot swaps (6) | PivotReviewer §1-2 (s4), Addenda 4-5 (s6): exact; omitting any rewritten gate is rejected; cost-neutral | all 6 recipe `before` gates match the regroup word; 30 controls rejected; cold44 rebuilds the same 44 ends | neutral | 0 |
| s4 ends 560/561/572/573 @U24 | PivotReviewer §3: (N) exact for ([24], U24) and its canonical pair; climbs paid | positive | {1:+8, 2:−4, 3:+4, 4:−4}, w −4 | +7.0e-8 |
| x30: E1 597/599 + 537/549 @U30 | #629 (E1); PivotReviewer Addenda 4-5 (537/549 end monotonically at the E1 hyperplane, whose (N) is exact) | positive | {1:+10, 2:−6, 3:+2, 4:−2}, w −4 | +2.0e-7 |
| p123 | H4aReviewer Addendum 7: 0 bad rows, dyadic, exact in all 3 orientations; (N) for (0,1039)-(0,1041); Δ recomputed | positive | {1:+6, 2:+12, 3:−12}, w −6 | +2.0e-8 |
| q4 (after p123) | H4aReviewer Addendum 8 (n_q4): exact; (N) for the 310/311/327 frames and 518's (0,1042); independent of u4 | positive | {1:+4, 2:+8, 3:−8}, w −4 | +1.4e-8 |
| **stack T_pq** | — | built and audited | {1:+28, 2:+10, 3:−14, 4:−6}, w 3794→3776 | **+3.08e-7** |

These layers were left out because they are negative or dead on gauge44: u4 (−1.2e-6), the 249 end (−3.2e-7), a joint
p123+q4 (−2.6e-7, worse than sequential), and #627's dim-7 ends 581/590 (no dyadic basis). j3 is dead: its st2 partner
403 is one of #645's 44 ends, and cold44's block premix uses up the row space.

**Payload.** H4aReviewer's Addendum 8 correction found that the k492 word n_q4 broke the 192-bit local payload bound
(backward prefix 280 bits). On gauge44 the layered word passes PR635's `hpe_audit_local.py` local-replay stage
(`prefix < 2**192`), both in G44Stack's `localchain.py` and as step 5 of `reproduce_layers.py`. So the q4 layer here
does not repeat that failure.

## Verifier changes (spot widths)

A swapped-out pivot p becomes an ordinary cold helper, and its width goes from 8 to 9. #645's global code checks the
spot helpers' widths as all 8, so the five global files gain the spot-width rule PivotReviewer signed as SOUND for
S4Ship (Addendum 3), ported to gauge44:

- `code/witness.py`: `spot_widths(v)` gives 9 at a spot helper h with 2v+h among the swapped-out pivots and 8
  elsewhere. The swapped-out pivots are read from the recipe that SPEC key `pivot_swap` names (path and sha256; the
  sha256 is asserted). Without `pivot_swap` the tuple is all 8, the same as #645.
- `code/bind_providers_portable.py`, `code/audit_allcold.py`, `code/assemble.py`: the `all(... == 8)` spot checks become
  tuple equality with `spot_widths()`, which pins every spot width exactly.
- `code/assembly_controls.py`: the `cold_swap` control picks a swap partner whose width differs, so the mutant can
  never be the identity.

Here the spot helpers 264 and 276 (pivots 488 and 500) expect width 9 and the other spot helpers expect 8. The k492
spot-width review (PivotReviewer Addendum 3) covered the same rule on k492 code. Its gauge44 port is part of this
package's review (LayerReviewer).

## Controls and what is not re-run

- The pivot-swap constructor's 30 controls run inside `reproduce_layers.py` (step 1).
- `verify_global.py`'s strict controls are unchanged, including the 12 bit-supplier controls and #645's admission
  controls. They run on the layered locals.
- Layer-end controls: 59 raw-word mutants, all rejected at pinned reasons, run as step 5 of `reproduce_layers.py`
  (see above). They cover the cold low-frame ends, the refactored cleanup, every entering end (its lower-frame gate,
  profile pin and hyperplane, plus its premix gate where it has one) and each distinct dim-8 frame. LayerReviewer ran
  them on the layered word (59 rejected). The k492 version (d966e29a) rejected 103-112 on the p123/q4 words; the
  k492-only primitives (absorptions, factored accumulators, target writes) are absent from this word.
- #645's independent audit `independent/audit_local.py` on the layered word: PASS, with 204 entering helpers, 96 low ends,
  54 cold ends and 716 columns. Its receipt is `evidence/layers/LOCAL-AUDIT-LAYERED.json` (word `0be48b1d…`, run with
  `--main`). The README's clean-clone command reruns it; only `elapsed_seconds` varies. The other `independent/`
  receipts are #645's own.
- The prior (N), exactness and pricing checks for each layer were done on k492 words. On gauge44 they are covered by
  the native chain (native audit, local replay, wrappers, phases) on the layered word, together with the pinned
  profile and width inventory.

## Inherited assumptions

These are the same as `PROOF-NOTE-BIT.md` (#645 open; PR589 citation; #545/#555/#589 review points; H1-H5). In
addition:

1. **(N) for the entering-end pairs outside #599's three Lean-covered pairs** (U24, U30, the dim-8 frames). As on
   k492, these are covered by the tool check (clifford_exact / `nchk.py`) and by the native wrappers, not by a Lean
   proof (PivotReviewer §3).
2. **The reviews of PR641's pivot-swap constructor and PR635's `build_cold_end.apply` / `build_hpe.apply`**, which this
   package uses unchanged.

## Result

| | gauge44-bit589b (L1g4 map) | this package (layered, LN5c map) |
|---|---|---|
| κ | 0.001652760598550299 | 0.00165395497190225 |
| per-call width | 3794 | 3776 |
| local profile | #645's {1:2514, 2:404, 3:448, 4:160, 5:56, 8:8} | {1:2542, 2:414, 3:434, 4:154, 5:56, 8:8} |
