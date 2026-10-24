# Exact composition interface: FOUR428 and PR2435 entrance24

Tekalign (@tekuuu), with substantial OpenAI Codex assistance; Apache-2.0.
The entrance construction is Jeremy Kothe's PR2435 at
`324d7d3590dc21003940a44cb0cbdc32b3620f25`. Original FOUR428 and all inherited
source notices remain unchanged.

`check_composition.py` transfers exactly 24 entrance-frame changes, 45 A-gate
frame changes and 48 B-gate frame changes. It verifies the old frames and
scalar operations before transferring each delta. A matches the entire old
program after FOUR428's 28-event prelude. Each changed B operation has a unique
matching five-event context, checked explicitly rather than trusting sequence
alignment. The scalar operations, coefficients, operation order, prelude,
source restoration, target levels, center COPY segments, warp operators,
cleanup and helper removals remain byte-for-byte equal outside these deltas.

The 24 original registers are
`474,475,476,477,486,487,488,489,522,523,524,525,526,527,528,529,534,535,536,537,538,539,540,541`.
Each survives FOUR428, has no warp, enters at dimension one, and ends at FULL.
The new dimension-two entrance contains its old entrance. None is accessed by
zero-frame precondition or compensation. Their existing entry/exit wrapper
pairs require new dimension-two recipes; no extra pair is introduced.

Frame changes do not touch FOUR428's four source registers, their restoration
partners, or its four lifted targets. Some A frames decrease in dimension;
therefore legality and accounting rely on the complete chronology replay,
not a blanket monotonicity claim about all edited labels.

Both composed words pass the retained transport's exact free noncommutative
operator algebra on all 652 arbitrary inputs in both orientations, every
native frame chain, and restoration of all 76 private zero buffers. Their
profile delta is `+24 H1 +120 H2 -96 H3`, reducing local rank mass from 5328
to 5304 and helper-width mass from 3472 to 3448. The actual width inventory is
`{4:36, 5:4, 7:60, 8:88, 9:240}`. All 52 warp operators and 112 events remain.

Run from the repository root:

```sh
python3 -B research/complex-structure-seed39/nonzero-lender-evidence/composition2435/interface/check_composition.py
python3 -B research/complex-structure-seed39/nonzero-lender-evidence/composition2435/interface/check_bridge_and_controls.py
```

Expected statuses are
`PASS_EXACT_FRAME_DELTA_COMPOSITION_AND_BOTH_ORIENTATION_FREE_ALGEBRA_NO_NATIVE_GLOBAL_ADMISSION`
and
`PASS_ADDITIONAL_COMPOSITION_CONTROLS_AND_UNCHANGED_BRIDGE_RECOUNT_NO_PHASE_ADMISSION`.
Both providers reject omitted A and B frame changes and a false dimension-three
entrance. The second checker emits each local program and invokes the original
independent global bridge recount without changing it, verifying all emitted
climb/COPY ranks and boundary frames. It leaves the first receipt unchanged.

These are precise finite interface checks. Physical Clifford phase/wrapper
admission, actual global owner packing, the complete invoice and outer transfer
are still separate obligations. This directory alone certifies no new kappa.
The constructor writes only the separate `COMPOSED-*.json.gz` candidate files;
the submitted FOUR428 snapshot remains unchanged.
