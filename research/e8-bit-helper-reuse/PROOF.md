# Source-bound finite construction

The unchanged parent is PR373 at `3ff87b5dc0b22a57958547ee347d5da25b7f9401`.
`SOURCE.json` pins its manifest and all 162 files, including its own manifest. That parent
in turn binds Dylan Crow's E8 bit word from PR370 and DaysSky's B3 complex runtime from
PR363. The default verifier replays the parent completely before using its fresh complex
certificate or freshly compiled native checker. No stored PASS output is used as evidence.

## Frame witness

`frame_replay.py` first splits the D/A/B/C bundles into the original ordered primitive
ADDs. This can reschedule MOVEs within bundles. It then checks and changes exactly 128
source-bound gate frames. All selected frames already occur in the inherited 944-frame
registry; D, scalar order, labels, states and retained-total map remain unchanged at this
intermediate stage. Canonical JSON SHA256 is
`cfbe976f1106dd56ea3a2b19a9729dbb8e925886db766825da2e6732c8e50bed`.

Discovery used singleton predecessor joins, successor meets and operand-chain frames,
then bounded monotone propagation. Its heuristic scores are not evidence: fixed-witness
replay and independent exact checks certify the resulting construction.

## Helper witness

`reuse_replay.py` applies 43 disjoint pairs of helper lifetimes from `reuse-selection.json`.
Each old helper has one write, is not a retained total, and has no later A/B use before
its successor helper's first write. All selected sites occur in A before the scatter.
Every undo source is a helper whose exact F₂ symbolic value at reuse equals its value
at the old helper's unique write. The old helper therefore contains its own independent
initial dirt after the undo. The successor can use that same register as its initial
dirty helper; it need not be a single-write helper itself.

The replayer checks old/new pair disjointness and protects all undo sources from aliasing.
Exact frame containment verifies that the undo operands can climb to the selected common
frame and that its source operands can still climb to their next frame. Old/new states
agree. The successor IDs are aliased to their predecessors, and surviving IDs are compacted.
The retained totals and scatter are preserved under that explicit renumbering.

Cleanup is rebuilt by reversing every helper-destination operation at the full frame.
Initial target compensation is recomputed from all 822 surviving independent helper dirt
columns, including the retained-total scatter. A/B never read target registers, so these
initial target offsets persist additively and cancel the computed dirt. The final canonical
JSON SHA256 must be `9974db5500941456e49030a5e5f374f34c707f76a40904fe1833df4f893a1c69`.

These local conditions explain the transformation. Full independent scalar checks remain
mandatory: all 1062 local columns and all 1542 global columns, including arbitrary helper
dirt, are replayed afresh after the changes. Six word mutants, six record mutants, twelve
bridge omissions and six source/witness mutations must be rejected.

## Seven-stage geometry and finite bill

The parent checker is freshly compiled with HDIM = 8, NCOPY = 9, VPORTS = 120,
RHELP = 822 and KPAIRS = 3. Native legality certifies 14689 scalar ADDs, 4181 nested MOVEs
and nine COPY/ERASE pairs. Forward/inverse cancellation-free row bounds are 742/7500.
The exact Gram/prime audit, geometry and seven-stage boundary checks use unchanged parent
sources. Seven literal replicas have 7 × 822 residual blocks of rank 8. Grouping seven per
width-56 bank uses every block exactly once in 822 banks.

The priced histogram is
`{1:107373, 2:44198, 3:24745, 4:16317, 5:13426, 6:1729, 7:5040, 8:882,
14:1680, 20:1680, 27:3360}`.
With W = 10794 and m = 56 its mass is 602952 and deficit is 1512. Both rational moment
engines, the full 10⁻¹⁶ fallback and adjacent-grid exclusion give bit coarse saving
247970809397543 / 250000000000000000. The unchanged complex coarse saving is
932783231884153 / 10¹⁸. Original assembly parameters still give PR373's κ because the
complex supplier binds.

`receipts_k.py` derives the finite invoice from the actual word, native and pricing receipts,
including all seven physical replicas and no duplicate normalization. `finite_k.py`
obtains coefficient 56827881566191 (46 bits), 441 copy/erase episodes, a q³¹³⁷ bound and
61-bit payload. Every port route is factored exactly; missing-addition, zero-gap and
negative-constant controls fail.

## Exact assembly refinement

`assembly.py` uses unchanged PR315 moment and outer engines through the pinned parent.
It retains beta = 10⁻⁹, chooses eta = 10⁻²⁴, and selects a saving strictly below the
complex leaf cap on a 10⁻²⁷ grid. Both moment engines plus the fallback certify that saving
against the actual bit histogram. Starting at 384599 / 10¹⁰, it performs eight bootstraps
`a_next = (1-s)s + s*a`. Each step has strictly positive atom, borrowing, remainder and
stock gaps and a finite cutoff that satisfies the parent's exact logarithmic absorption
inequalities using the same freshly derived coefficient.

The eighth step feeds unchanged `outer.assembly`. All 47 constraints hold, the complex
leaf cap is rejected, and the adjacent assembly grid point is rejected. The exact result
is κ = 465956978619683677193229 / (5 × 10²⁶). Its increase over PR373 is
363638677193229 / (5 × 10²⁶), approximately 7.27277354386458 × 10⁻¹³.

The verifier also applies the same refinement to the original PR373 word and finite bill,
and requires the same κ. The headline gain is therefore solely an assembly refinement;
the 2.446374% bit coarse gain is independently verified but remains nonbinding. All open
obligations in the README remain conditional.
