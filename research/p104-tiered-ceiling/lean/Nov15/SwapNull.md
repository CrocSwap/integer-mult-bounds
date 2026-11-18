# SwapNull.lean: LAWBUILD M3 law SWAP-NULL. No sorry, 8 s, 2.45 GB RSS
Nov 17. Imports TokenCancel (op model), SwapWord (`run_append`), RelaySandwich (`stopCost`, `fL` via JunkLB2). Axioms: [propext, Classical.choice, Quot.sound].
Source: (internal notes) HubSettle's V mix and {0}-prefix are modelled as `Blk V` / `Blk G0` matrices (left / right multiplication).

**Gadget (4 ops, at the shared chart c):** `add h1 h2 (+1); add h2 h1 (-1); add h1 h2 (+1); scale h2 (-1)`. `gadget_run`: rows of h1,h2 exchanged, nothing else changes; `gadget_legal`.
- `tail_run`: gadget, then every later event renamed h1<->h2 => final state = unswapped final with rows h1,h2 exchanged (F' = P F).
- `head_run`: earlier events renamed, gadget, original later events (sigma-symmetric start) => every final row has its h1/h2 coordinates exchanged (F' = F P).

**(1) legality.** `Undo V G0 F F'` := exists V mix L (identity off V x V) and prefix M (identity off G0 x G0) with L F' M = F.
- `tail_if`/`head_if`: both in V (tail) / both in G0 (head) => undone (L = P, resp. M = P).
- `undo_one_iff` (identity finals, no other hypothesis): undone iff (both V) or (both G0).
- `tail_iff`, `tail_iff_span`: tail swap undone iff both V, GIVEN rigidity of the prefix (the unchanged non-V rows pin M = 1; `rigid_of_span` derives it from a spanning condition).
- `head_iff`: head swap undone iff both G0, GIVEN a non-V row with F x h1 != F x h2.

**(2) ladder.** `Traj.cost f t = f(e-b) - sum f(gaps)` (`cost_stopCost`: equals RelaySandwich.stopCost on the equal-move ladder). `Traj.swap`: (b1,e2,pre1++suf2), (b2,e1,pre2++suf1).
- `stays_multiset`: the multiset of stays is unchanged; `swap_wf`: swapped trajectories are again consistent.
- `delta_eq`: change = f(e2-b1)+f(e1-b2)-f(e1-b1)-f(e2-b2).
- `delta_zero_end` (e1 = e2, both end in V), `delta_zero_birth` (b1 = b2 = 0), `swap_null`: hub-undoable => ladder change 0.

**(3) converse.** `nonzero_not_undoable`: nonzero change => not undoable. `converse_witness` (concrete): helper 0 born dim 5 ends 7 (no hub), helper 1 born {0} ends V (dim 9): f = r ln r change = 7 ln 7 + 4 ln 4 - 2 ln 2 - 9 ln 9 ~ -1.995 < 0 (`witness_num`, 7^7 2^6 < 3^18), and neither the tail nor the head swap is undone by any L, M.

**Finding (M3 wording needs scope).** "tswap legal iff both end in V; hswap iff both born in {0}" is true only with a hypothesis: `tail_prefix_counterexample` (identity finals, both helpers in G0, none in V) is a tail swap undone by the prefix alone. Corrected statement: for identity-final helpers the swap is undone iff (both V) or (both G0) (`undo_one_iff`); the per-kind iff needs prefix rigidity (tail) / a separating non-V row (head). In the real word the non-V rows do pin the prefix (M3's controls XT/XH fail at settle3), but that is an input [C], not a consequence.

**Scope.** Matrix-level model: L, M are not required invertible (strengthens only-if). The M3 census numbers (8,282 pairs, 7,390 absorbable) are data, not re-proved. Mixed gadget placement (swap back later) is not modelled.
