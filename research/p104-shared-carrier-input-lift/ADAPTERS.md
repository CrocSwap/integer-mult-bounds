# Explicit adapters to retained sources

All files under `retained/caller`, `retained/runtime` and `retained/native`
are byte-identical to their pinned originals. Their assertions and scientific
checks have not been edited in place.

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
- `pricing.py` adapts retained #6726 pricing. Only the declared native
  histograms/census, claim/tested/root endpoints, status and explanatory text
  change, and the local sign proof `local_lift_gain` is added, together with the explicitly decomposed canonical-job adapter
  charges from #6763. The invoice construction, ordinary envelope, both rational interval
  engines, strictification, compiler threshold, retained BIT input and outer
  ledger retain their full checks.
- `context.py` maps the six historical runtime paths to explicitly pinned
  self-contained files. It provides no fallback network fetch or PASS cache.
- `verify.py` regenerates the literal words and composes the complete checks,
  now over the lifted word. The changed-pair column check covers every chart pair
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
Its old frozen standalone `run()` is not invoked. The 286,728 fixed elementary
canonical maps are charged separately; full 153-axis permutations are never
assigned a single 1000-unit route charge. This corrects the predecessor price
driver’s partial 252,223,008 estimate to the sufficient 535,415,008 envelope.
- `independent/check_native.py` keeps the #6805 split audit as `run_split` and adds
  `run_lift`, an independent audit of the lift (defect vector, delivery, suffix,
  all 47 erased values, controls); `independent/check_invoice.py` has its claim,
  tested price, raw lower endpoint, compiler gap and cumulative histogram
  deltas against #6702 recomputed for the new word.
- `retained/physical-review/verify.py` is byte-identical to its pin; its stale
  explanatory `growth_bound` text (178080) is not used, the receipt carries the
  recounted paid rank mass 178,044.
