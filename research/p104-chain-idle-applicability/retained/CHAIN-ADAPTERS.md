# Explicit adapters to retained sources

The chain-nested caller replaces the #6726 caller in pricing and physical
replay. The #6726 caller remains under `retained/caller/`, byte-identical to its
pins, and is still rebuilt and replayed as the comparison baseline. Files of the
#6824 step used unchanged are pinned in `retained/SOURCE-PINS.json`.

## What had to change for the new caller

Each item was recomputed from the literal word, not edited to pass.

- `pricing.py`: the invoice now comes from `literal_invoice` and is compared with
  the shape formula `chain_root.outer_formula`. Census, target, paid and rank-mass
  pins are the recount of the literal word. Roles 34 to 20, events 606 to 1,237,
  thin queries 15 to 3, largest paid rank 40 to 64, ordinary bound 535,415,008 to
  488,177,792, compiler grid 1/1,750,000,000 to 1/20,000,000,000.
- `pricing.py`, compiler range: the retained exponential enclosure accepts
  arguments below 16 in absolute value, and `960*TESTED*ln(145)` is about 16.11.
  This is a limit of the enclosure routine. The same quantity `145^(1920*TESTED)`
  is now formed as two exact squarings of `145^(480*TESTED)`. The tested
  inequalities and their bounds are unchanged.
- `pricing.py`, claim and tested price: `TESTED` must lie strictly between the claim
  and the raw crossing and give a unit-numerator compiler grid, so
  claim 0.00337180, tested 0.00337180035.
- `independent/check_invoice.py`: claim constants and census pins are recounted;
  the retirement rebuild is removed because the new caller has no retirements; the
  retained invoice is still reproduced from the #6726 literal, and the native deltas
  against #6702 are still checked. `independent/check_root.py` is new and written
  separately from `chain_root.py`.
- Reviews of the earlier steps moved to `retained/predecessor-reviews/` unchanged.
  They describe earlier words, not this caller.

## Layout assumptions checked

`retained/caller/caller.py` and `root_check.py` fix 8 fields, and `caller.py` fixes
32 roles; they apply to the retained baseline only. No other module assumes 8
fields or 34 inputs once the pins above are recounted. The physical replay,
canonical adapters and allocation are generic in roles and stages.
The largest stage support is 10 coordinates. Stage supports appear only in the root
and basis construction; native calls see two caller registers, as before.

## Whole idle jobs across several sites

A whole idle is one paid transform of rank `8|W|` of the current content of one
caller register, per port, on the disjoint fresh axes of the stage set `W`. The
checks are distinct stages, orthonormal axes, two-coordinate exchanges charged on
both boundaries, and an exact endpoint.

- #6716 `PROOF.md` section 2: "Each therefore needs exactly `D_B D_C` on its own
  unchanged payload. The B and C axes are disjoint fresh blocks; their two positive
  transforms combine into one rank-`8(B+C)` job on each of these two coordinates."
- #6726 uses the same job at rank 40 (5 stages across 2 sites, then pays fragments).
- This caller uses it at ranks 8 to 64 (up to 8 sites). **This extends the rule of
  #6726 and is not a new compiler proof.** The rank-64 job has more exchanges than
  any before it, and each exchange is charged.
- A difference from the precedents: in #6716 the merged coordinates share one
  ordinary basis across adjacent sites, and in this caller they cross sites with
  different bases. What stays fixed is a line and its dual functional, not a register.
  The contract text does not ask for a preserved register, the paid job is applied
  once, and the exact identity is PROOF.md section 4. Reviewers should check this
  reading.

## Retained adapters from earlier steps

- `split.py` adapts Ali Romman's `construct.py`: the eight historical owned
  slots become the literal `word['owned_fields']`, the local helper module is
  `native`, and the old unchanged-paid batch wrapper is omitted. The basis
  construction and independent prefix/suffix identities are unchanged.
- `retimed_construct.py` is the #6805 explicit retiming, source-event/no-contact
  guard and witness application, unchanged apart from its name and header;
  its output is pinned by `base_native_payload_sha256` in `EXPECTED.json`.
- `lift.py` applies the exact edit list `LIFT.json` to that word, asserting
  every bound source event; `construct.py` composes the two steps and is the
  optional canonical-word exporter (`--base-only` writes the #6805 word).
- `native.py` adapts the retained local checker to the counted current public
  and owned inventory, records all CLEAR observations, and enforces pre-COPY
  zero. The physical-map function uses the pinned local compiler/interpreter.
  Both independent replay and complete pricing enforce the exact new census;
  an old historical 750-public/8-owned bound is not treated as this source's
  contract.
- `pricing.py` adapts retained #6726 pricing. Besides the items above, the declared native
  histograms, status and explanatory text change, and the local sign proof `local_lift_gain` is added, together with the explicitly decomposed canonical-job adapter
  charges from #6763. The invoice construction, ordinary envelope, both rational interval
  engines, strictification, compiler threshold, retained BIT input and outer
  ledger retain their full checks.
- `context.py` maps the six historical runtime paths to explicitly pinned
  self-contained files. It provides no fallback network fetch or PASS cache.
- `verify.py` regenerates the literal words and composes the complete checks,
  over the lifted word and the new caller. The changed-pair column check covers every chart pair
  named by the split or touched by an inserted move or lifted helper endpoint,
  and the lift negative controls reject a wrong coefficient, a missing repair,
  aliased lifted helpers, a stale bound event and a missing carrier delivery.
  It adds explicit helper allocation and all 512 columns of each of the three
  changed native boundary pairs, beyond the signed-Pauli/global-phase checks
  on every used map.
- `independent/check_native.py` was written separately without importing the
  constructor, primary replay or price. `independent/check_invoice.py` uses
  its chronological counts and a separately written Laurent adjoint. Its
  initial development-only file paths were replaced by explicit arguments;
  the scientific calculations and controls are unchanged. Container hashes
  are removed only from regenerated combined receipts; canonical complete
  word identity remains checked.

The independent reviews are AI-assisted source reviews, not human acceptance.
None of these changes discharges the five retained framework assumptions.

The exact #6763 physical audit is retained under `retained/physical-review/`.
The driver invokes its generic native, physical, allocation, invoice and
canonical-adapter functions on the actual new word, with data supplied locally.
Its old frozen standalone `run()` is not invoked. The fixed elementary
canonical maps are charged separately; full 153-axis permutations are never
assigned a single 1000-unit route charge. On #6726 this corrected the predecessor price
driver’s partial 252,223,008 estimate to a 535,415,008 envelope; the new caller's recount is 488,177,792 from 225,784 maps.
- `independent/check_native.py` keeps the #6805 split audit as `run_split` and adds
  `run_lift`, an independent audit of the lift (defect vector, delivery, suffix,
  all 47 erased values, controls); `independent/check_invoice.py` keeps the cumulative histogram
  deltas against #6702.
- `retained/physical-review/verify.py` is byte-identical to its pin; its stale
  explanatory `growth_bound` text (178080) is not used, the receipt carries the
  recounted paid rank mass 166,812.
