# A charged in-place half-source ADD on two tapes

For every positive width n, the literal finite controller in `machine.py`
updates an n-bit signed target by plus or minus half an even n-bit signed source,
preserving the source, all exterior cells and both initial head positions in
exactly **2n+3 unit-head transitions**. It uses two tapes, four symbols and no
work tape. Its 224-entry table is independent of n. The signed answer is exact
when it fits; otherwise the controller returns the modular wrap. It does not
check overflow. Odd sources reject in one transition without changing anything.

This supplies a physical prepared fixed-grid component boundary for PR2370's
selected call000 raw2 `ADD(L119,L169,1/2)` reference equation. It does not supply
the selected caller's physical layout, chart equality or precision invariant.
PR2439 already supplies paid variable-exponent half-source addition with a fresh
reusable output and independent workspaces. That different interface is credited;
neither result subsumes the other's stated caller hypotheses.

`PROOF.md` gives the quantified processed-bit invariant, sign extension, exact
first-halt charge, trace locality and inverse proof. Inputs are marked equal-width
two's-complement streams on distinct tapes, heads at their first bits. All target
bits may initially be dirty. Both markers and arbitrary exterior storage survive.
Marker installation, acquisition and routing are outside this prepared boundary.

The reference component has a visible accumulator; this physical controller does
not reproduce that full reference state. Only the projected memory equation is
bound. Real/imaginary components need two paid calls, plus their actual movement.
No proof-kernel compilation, selected supplier, full tape compiler, global time
bound, selected precision change, new kappa or runtime speedup is claimed.

## Evidence

The registered CPython 3.12 replay covers all 87,380 even-source/dirty-target/sign
cases through width 8, including 76,458 fitting signed outputs, and traces
1,601,988 physical transitions. A separate integer endpoint oracle checks both
signed and modular interpretations. Every trace checks the precise write
footprint, source/exterior preservation, head return and invoice. There are 255
odd-source rejection fixtures, 192 translated fixtures at widths through 1024,
and 158 exact two-orientation dirty-state round trips.

Eight controls witness faulty output/carry, zero extension, omitted negative
carry, omitted head return, odd-source/divisibility, overflowing signed output,
aliased tapes and unequal chart premises. The machine rejects odd input; the
other premise controls are countermodels, not additional runtime validators.
The Git-free optimized replay also rejects changed live source bytes, changed
retained Lean source and a typed bool/int receipt alteration.

```
python3 scripts/research_package.py --package research/fixed-grid-half-add
```

Direct replay: `python3 -B research/fixed-grid-half-add/verify.py`.
`--write NEW_PATH` is explicit authoring mode and refuses to overwrite. Normal
checks write nothing. `SOURCES.json` pins main inputs; `SNAPSHOTS.json` pins
unchanged PR2370 and PR2439 sources. The literal source extractor is not a Lean
elaborator; the retained Lean proof is neither imported nor recompiled here.

## Open next questions

1. Bind actual selected acquisition and writeback to this two-word interface,
   with common charts, even source, signed headroom and explicit marker/routing
   charges. This matters because a local scalar transition count is not a
   supplier invoice. The missing physical allocator and prefix precision policy
   block that adoption.
2. Kernel-check the finite table and all-length processed-bit invariant in the
   existing multitape framework. The current universal claim is a written proof
   with exact finite corroboration, not an inferred formal theorem.

## Credit and overlap

James Chang supplied PR2370's reference and PR2439's variable-exponent physical
lineage, with credited DreamingOfClouds PR509/516, Gareth Davidson PR1309, bank
routing and generic machine predecessors. PR2235, PR1869 and PR2411 provide
related generic multitape/adder infrastructure. Ripple addition, complement-plus-
one subtraction and arithmetic sign extension are standard and not claimed new.
The new table, explicit boundary proof and checks are by ywz65 with substantial
OpenAI Codex assistance. Apache-2.0; no independent human review is claimed.

The uniform-transfer task was drawn once on main
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4. Screening rejected
bounded floor-sum rounding (already PR1853) and later-stage reserve composition
(already PR2547); no duplicate packages were submitted. Full overlap snapshot
768 open PRs/1232 Discussion records at 15:00/15:03 UTC was searched for fixed-grid,
half-source, in-place, right-shift and signed-adder interfaces. PR2439 explicitly
leaves automatic fixed-grid caller implementation open. Coverage and current-head
checks are recorded in TASK.json; metadata search is not a novelty guarantee.
