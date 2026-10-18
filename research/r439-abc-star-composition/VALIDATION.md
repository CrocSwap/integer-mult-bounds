# Executed validation

On Linux, 2026-10-13, the complete verifier passed under **CPython 3.14.4**
and under isolated optimized **CPython 3.12.3**, with GCC **15.2.0** and Boost
**1.83.0**. The latter replay used a relocated sparse source tree whose files
and directories had write permissions removed, with all generated output
outside it. The complete receipts were byte-identical, SHA-256:

`1233f67048a30639d3ae3928353d65f43e8f3eb1535d568e823af21a848d9ea4`

The local command used `BOOST_INCLUDE=/tmp/math-pass09-boost/extracted/usr/include`.
That is an environment setting, not a required repository path. A standard
Boost installation works through the default `/usr/include`. C++ builds use
`-O2 -std=c++17`; the original finite checkers and exporters are unmodified.
Machine paths, commands and timing logs are outside the deterministic receipt.

## Coverage

- All eight exact compositions and complete decoded candidate regeneration.
  Three phase maps in both directions on all 661 independent dirty columns
  for every corner. Literal complete streams contain 139,972 instructions
  summed across the eight words, each replayed forward and backward.
- The original owning E8 checker: full label/lattice/frame geometry once,
  then all eight scalar words with byte-identical geometry, full endpoints,
  retained-total frames and all original interface flags. H2 and K_equals_D
  are required false on exactly the four changed-D corners.
- Fresh unchanged native legality and column programs on **all eight words**
  at **5, 9 and 11 stages**. Coverage is 883, 1,327 and 1,549 physical columns
  per word; all **384** omitted-bridge controls are rejected. Every paid rank,
  per-register MOVE path, COPY/ERASE lifetime, scalar and bridge bill agrees.
  Baseline / PR1062 / candidate local records: **27,234 / 14,429 / 13,581**.
- Exact local and nine-stage positive expressions, including the failed
  D-only 193-bit corner. The full composition has 92/176 bits and the same
  inherited 104/192 production allowances.
- **17 semantic/accounting rejection controls**, including missing A or B
  gates, omitted dirty-helper preparation/restoration, stale literal cleanup,
  omitted COPY or ERASE, wrong ERASE original, invalid gate types, self ADD,
  double-counted savings, stale bounds, unpaid bridge pricing, failed D-only
  precision, both strict cap equalities and a non-nested physical frame.
  The stale cleanup is independently confirmed F2 exact before rejection by
  the stronger literal-cleanup contract.
- **10 package tests**, including relocation, both level-1 and level-9
  recompression of the generated candidate, source and vendor pin mutation,
  changed candidate with rebound digest, omitted failed corner, undercharged
  invoice, unrelated payload edit, duplicate/nonfinite JSON and boolean
  numeric receipt fields. Immutable source containers remain byte-pinned.
- **14 existing tests** from `tests.test_selected_result` and
  `tests.test_finite_bit_contract` passed. Exact retained source bytes were
  compared to the Git objects recorded in SOURCES.json.

The first native-driver attempt detected a mistaken assertion equating all
fresh copies with the reverse-stage subset. Inspection of the unchanged
native source established totals `9*(2*k+1)` and reverse-stage copies `9*k`.
The driver was corrected to check both distinct quantities; both complete
final replays then passed. No source checker was changed.

## Publication scope

Upstream was refreshed at **ba82555c64e1879e4b7decce28186f208fcb8262**;
all 17 repository source pins were unchanged. The PR queue was refreshed
through **1120**. PR1113 explores precision near the historical PR941
disjoint-pair floor, and PR1102 supplies omission probes for PR967; neither
is the A/B/D composition checked here. PR1062 remains the explicitly pinned
pending source and is credited for its B/D construction. No priority or
unrestricted best-word claim is made.

The original PR980/1062 synthesis searches are not independently rerun. The
frozen resulting programs, their phase maps and their actual complete words
are checked directly. No full hosted supplier emission, outer assembly,
selected complex cold replay, full repository `make verify`, formal theorem
proof, practical benchmark or independent human review was performed.
Hosted CI is separate from the local evidence; no CI pass is asserted here.
