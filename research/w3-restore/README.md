# w3 word with 209 target-prefix squares and 438 early restorations

**Conditional κ = 754077687633330234295251 / 10²⁷ = 0.000754077687633330234295251**, +0.0755% over PR #311
(0.000753508664880762517753401), +0.157% over PR #310's w3 word, +0.343% over PR #309.

This package is PR #311's (`w3-target-prefix`: utcorvusvolat-dotcom's PR #310 w3 word and admission chain with the 209
exact F₂ target-prefix squares) with **one more native transcript stage after the squares: PR #280's early
restoration of cleanup helpers**, with its screen and emitter (`code/cleanup_screen.py`, `code/cleanup_emit.py`,
`code/cleanup_reference.py`, utcorvusvolat-dotcom's PR #280 scripts re-pinned to this word) and PR #280's
endpoint-aware bank accounting carried into #310's bank review.

* **The stage.** At the first `cleanup_gate` ADD (record 962,945) every data target already has its scalar
  endpoints; the screen reproduces this on the exact F₂ prefix, then finds the helpers `a` whose only later scalar
  incidence is one write `a −= b` with a donor `b` unwritten in between, both at rank-22 frames whose rational span is
  a nondegenerate 23-dimensional frame: 440 of PR #280's shape (and 477 multi-incidence candidates at dimension 3 that
  are not moved). With 40 physical replicas the restored width-3 slots must tile width-120 banks, so **438** are moved
  (438 · 40 = 146 · 120; #280 kept the same 438/440 distinction under its own replica count): the write commutes over
  the integers with every crossed gate, `a` and `b` advance to the span `E`, the ADD runs there and `a` retires at
  `E`. The emitter checks every new frame's full-rank annihilator and nonzero cleared Gram determinant mod 2¹²⁷ − 1,
  the commutation conditions, the forward/inverse/roundtrip F₂ replays and an omitted-restoration control. Local
  histogram delta {1: +1314, 2: −876}, local rank mass 398,897 → 398,459, helper endpoint residual 317,409 → 316,971.
* **Admission of endpoints below the full frame.** `code/cohort-bank-review.cpp` now takes the candidate's
  `COHORT249-FINAL.json` and a tiling plan: each helper's residual width is dim(endpoint) − dim(entrance) (24 − dim
  entrance for every helper that still retires at the full frame, so #310's census is reproduced when nothing is
  restored), the pattern list and the expected width census come from `inputs/bank-plan.json` (an exact integer
  tiling found by a small ILP over patterns of at most three widths: 105,657 banks per stage, every bank a full
  120-coordinate partition; the C++ still verifies the census, the collision-free full tiling of all 3,026,400
  role/replica/stage slots, the per-pattern endpoint and omission/repetition controls, and the exact charts), and the
  bank-stock invariant is the generic one (all slot coordinates fill the banks exactly). Literal stock 810,615 →
  809,885, normalized 162,123 → 161,977; 438 new exact frame charts (3,911 in all, ≤ 320 factors); 22,806 changed
  projector charts (2,703 retired endpoints, ≤ 342 factors). Legality is checked against the candidate's declared
  endpoints with the export's base frame table.
* **Price and invoice.** `code/price.py` re-pinned (word hash `8f05b2af…`, rank mass 398,459, residual 316,971,
  3,687,240 five-stage calls, mass 19,402,040, deficit 35,200, nine ordinary levels); finite coefficient
  58,322,299,353,183,001 < 2⁸⁰; selector charge 571,950,385,600 < 2⁴⁰; `code/finish.py` re-pinned accordingly.

## Reproduce

```sh
python3 -m pip install -r research/w3-restore/requirements.txt
python3 -B research/w3-restore/verify.py --output /tmp/w3-restore-proof --cxx g++ --boost-include /usr/include
```

About 10 minutes (both prerequisite source verifiers fresh); prints `PASS conditional kappa = …`.

## Scope

Exactly #310/#311's conditional interfaces; not a Lean certificate, an unconditional theorem or a benchmark. Not yet
composed on w3: the kernel, sink, descent and reorder stages. #311's and #310's README/PROOF are kept as
`README-PR311.md`, `PROOF-PR311.md`, `README-PR310.md`, `PROOF-PR310.md`. Prepared by Rohan Arun with Anthropic
Claude assistance; Apache-2.0; see `NOTICE.md`.
