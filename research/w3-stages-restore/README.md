# w3 word: #312's kernel, target-prefix, plateau and reorder stages plus 438 early restorations

**Conditional κ = 151024082262820774685631 / (2·10²⁶) = 7.55120411314104·10⁻⁴**, +0.0756% over PR #312
(7.54549816771013·10⁻⁴), +0.214% over PR #311, +0.296% over PR #310's w3 word; priced against PR #304's complex
supplier as #312 is (bit coarse binds; nine ordinary levels).

This package is chafreaky's PR #312 package (`w3-bitword-stages`: utcorvusvolat-dotcom's #310 w3 word with the kernel,
target-prefix + plateau and reorder stages and #304's supplier admission) with **one more native transcript stage
after the reorder stage: PR #280's early restoration of cleanup helpers**, exactly as in PR #313 — the stage #312
reports as blocked because #310's legality checker rejects endpoint changes.

* **The stage** (`code/cleanup.py`, `cleanup_screen.py`, `cleanup_emit.py`, `cleanup_reference.py`: #280's own
  screen/emitter re-pinned to this word). At the first `cleanup_gate` ADD (record 925,515) of #312's final word every
  data target already has its scalar endpoints (checked on the exact F₂ prefix); 440 helpers `a` have a single later
  scalar incidence `a −= b` with a donor unwritten in between, both at rank-22 frames whose rational span `E` is a
  nondegenerate 23-dimensional frame. With 40 physical replicas 438 are moved (438·40 = 146·120 width-3 bank slots);
  the write commutes over the integers with every crossed gate, `a` and `b` advance to `E`, the ADD runs there and `a`
  retires at `E`. New-frame annihilators and cleared Gram determinants (mod 2¹²⁷ − 1), commutation, forward/inverse/
  roundtrip F₂ replays and an omitted-restoration control are checked. Local delta {1: +1314, 2: −876}; rank mass
  398,057 → 397,619; endpoint residual 316,569 → 316,131.
* **Admission of endpoints below the full frame.** `code/cohort-bank-review.cpp` (#312's plan-driven review) now takes
  the candidate's `COHORT249-FINAL.json`: each helper's residual width is dim(endpoint) − dim(entrance), and the
  stock invariant is the generic one (all slot coordinates fill the banks exactly). `stages/bank-tiling.json` carries
  the new width census (438 at width 3, 1,762 at width 4, #312's kernel widths unchanged) and an exact integer tiling
  (ILP over patterns of ≤ 3 widths; 105,377 banks per stage), which the C++ verifies in full as before (collision-free
  tiling of all 3,026,400 slots, every bank a full 120-coordinate partition, per-pattern endpoint and
  omission/repetition controls, exact charts: 4,703 new, ≤ 320 factors). Legality runs against the candidate's declared
  endpoints with the export's base frame table; 23,870 changed projector charts (3,221 retired endpoints, ≤ 342
  factors). Literal stock 809,215 → 808,485 (normalized 161,697); finite coefficient 58,519,066,603,435,601 < 2⁸⁰;
  selector charge 571,949,825,600 < 2⁴⁰. Re-pinned: `code/admit_geometry.py`, `code/price.py` (word hash `a972abfe…`,
  897,241 ADDs, 3,709,480 calls, mass 19,368,440, deficit 35,200, κ), `code/finish.py` (which also cross-binds the
  restoration receipt and the pre-restoration word hash to #312's reorder output).

## Reproduce

```sh
python3 -m pip install -r research/w3-stages-restore/requirements.txt
python3 -B research/w3-stages-restore/verify.py --output /tmp/w3-stages-restore-proof --cxx g++ --boost-include /usr/include
```

About 12 minutes (both prerequisite source verifiers and #304's supplier admission fresh); prints `PASS conditional
kappa = 151024082262820774685631/200000000000000000000000000`.

## Scope

Exactly #310/#312's conditional interfaces; not a Lean certificate, an unconditional theorem or a benchmark. Not yet
composed on w3: sinks and the constructed-frame descent. #312's README/PROOF are kept as `README-PR312.md`,
`PROOF-PR312.md`. Prepared by Rohan Arun with Anthropic Claude assistance; Apache-2.0; see `NOTICE.md`.
