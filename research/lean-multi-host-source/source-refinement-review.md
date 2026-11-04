# Review of the concrete PR442 invocation connection

Review scope: the actual stage-2, replica-0, pair-0 forward invocation at
PR442 `4e16d001d505d4f21dd2bcfc44591f9be4c279bd`, and its connection to the
separately proved multi-host theorem. This is a review of source fidelity
and theorem boundaries, not a claim that generic transport/scheduling
algebra is new. The later bounded overlap refresh, including PR509, is
recorded in the package's `overlap-review.md`.

The reviewer authored the frame/raw refinement modules and
`SourceDataBehavior.lean`, and helped debug `PhysicalSourceConnection.lean`.
The comparison, native adapters, ownership and geometry were reviewed across
agent boundaries. This report must not be described as an independent
implementation or independent review of every line of its own modules.

## Material finding and checked repair

The first `SourceNativeInvocation` version used different extensions of the
native cover map for the old and new runs. `OwnerTransport.extendCover`
defaults to identity outside its own active owner image. At a retained host
owner, the parent extension therefore returned identity while the hosted
extension returned its actual cover map. Equal raw owner-coordinate payloads
did not imply equal initial native payloads. Both individual refinement
theorems were valid, but their combination was insufficient to establish a
physical comparison starting from the same retained native input.

The repair uses one shared cover extension over the union of both active owner
images, with both common-cover equations proved from the concrete layouts.
Their overlap consists of data owners with equal charts; helper/private
owners do not collide. The two native initializers must use this same
extension, and the shared native host/data/tail input equalities must then
be stated explicitly. `SourceCommonCover.owner_overlap_data` proves the
concrete intersection property, and `old_common_cover`/`new_common_cover`
supply both required equations. The revised `SourceNativeInvocation` uses
that single extension in both initializers, run refinements, guards and
output readbacks. Its `initialized_native_host_input`,
`initialized_native_data_input` and `initialized_native_tail_input` prove
equality after private-row preparation, using actual exclusion of the
private keys. This closes the finding; it was not a counterexample to the
PR442 construction or to the raw-coordinate endpoint theorem.

## Source and model checks

- The full 19,002-event word is connected by exact Lean list projections:
  `SourceFrameTrace.scalar_word` links frame records to the symbolic scalar
  certificate, and `route_projection` links the finite physical-role events
  to that same frame word. Range checks ensure role indices are below 988;
  the remaining 36 binary-tree leaves are inaccessible representation
  padding, not paid scratch.
- `SourceMatrix.arbitrary_dirty_payloads` quantifies over all 987 original
  Boolean streams, including arbitrary correlated helper values. Its
  chronological COPY/ERASE guards are proved from the symbolic execution,
  not from a handful of test inputs. `SourceFramed.actual_valid` follows the
  exact frame trajectory, while `SourceRawGuards.actual_native_clean`
  transports those guards to the same native execution.
- The raw source's ADD coefficient is `+1` for every actual ADD. Parity
  projection therefore exactly gives Boolean XOR. The sixth ADD field is
  the exporter phase marker 1..5, not a multiplier or complex phase:
  `vendor/export_records.py:3-4,53-64`. The source Boolean interpreter uses
  `coefficient & 1` at `code/bit_global.py:114-119`. An earlier suggestion to
  require that sixth field to be zero was wrong and was corrected before
  source checking. MOVE's sixth field is zero; COPY/ERASE have their own
  record layouts. Source extraction remains a pinned, hashed, reproduced
  external boundary; Lean checks the resulting literal claims.
- The actual owners include the cover function, not just the integer family
  label. This matters because multiple independent streams can share a
  family. `SourceLayouts.data_owner_eq` and `data_chart_eq` identify the
  shared data ports. `parent_owner_ne_host` proves actual original/hosted
  disjointness. Host gather/scatter use explicit invertible family charts.
- Common-cover conjugacy is necessary for physical fidelity: with
  `g_source * sigma_source = d = g_target * sigma_target`, the apparent
  raw-coordinate route is a native same-address XOR. This is not the
  missing split-stream interface discussed in PR448. The shared-cover
  issue above concerns consistency between the two runs, not this
per-run calculation, and is now repaired as described above.
- Every source frame is represented by an actual checked projector/basis.
  MOVE pair membership must feed its nested-projector absorption theorem;
  `SourceMoveGeometry.actual_matrix_run` does that for the complete actual
  word, identifying MOVE with `D_(Pnew-Pold)` and COPY with the full local
  eight-coordinate transport. Its stage-2 exterior factor is included and
  cancelled explicitly. The final invocation module now contains named
  old/new matrix-realization corollaries so this is an actual dependency
  path, rather than an unused collection of geometry certificates.
- ERASE assigns zero only after the transported source-equality guard has
  been proved. Resetting the now-zero temporary's frame label is metadata
  bookkeeping, not an extra physical reset on arbitrary dirt. Exactly one
  designated private stream begins clean in each layout and is returned
  clean.

## Retained outputs and theorem strength

`SourceInvocationComparison.oldResult_framed` compares the entire pair of
retained state and actual old-bank outputs. `oldRaw_bank` threads the real
output of each bank stream; it does not replace that output by its input.
`newResult_framed` retains all 747 hosted streams, all 240 data streams and
the chosen exterior state. The final completion equation then projects to
retained state, exactly as the abstract physical contract specifies.

The explicit data theorem is not just an arbitrary unnamed `R -> R` map.
`SourceDataBehavior` proves four finite entrance/exit-frame identities:
source rows `i` start at frame `i+2` and finish at frame 1; target rows
`120+i` start at frame 0 and finish at frame `i+824`. It derives the complete
old/new data formula with the actual port and frame pullbacks preserved.
The target receives the corresponding source in normalized coordinates;
no unjustified identity of physical frame maps is used.

The native adapters and ownership geometry introduce no extra provider
premise into the intended concrete theorem. Its algebraic parameters are a
field with `2 != 0` and an invertible cover map `d`. The retained payloads
and old dirty bank are arbitrary functions. These hypotheses are inhabited
(for example by rational addresses and identity `d`), so the theorem is
not vacuous. The clean private row is an explicit allowed resource, not an
assumption that helpers or retained hosts are zero.

## Required scope statements

The input embeddings default slots unused by the respective layout. The
shared tail is outside the union of both active images. Thus the result is
a local comparison with explicit embeddings, not equality of arbitrary
complete global allocations. Separately, the general raw/native execution
theorems preserve arbitrary exterior streams.

The singleton completion applies the remaining pending swaps immediately
after this call. It does not identify that position with the later child
operations in the full recursive schedule. No whole-cover sweep, all-size
compiler, physical gate-cost bill, register saving, analytic transfer, or
new kappa bound follows. PR448's advertised split gain remains
unestablished. The two negative controls concern the next corrupted
checkpoint and a dirty-private first-COPY state, not a replay of the entire
corrupted program.

## Validation status

The reviewer's frame/raw/native-guard modules and data formulas were
compiled with Lean 4.33.0, with printed theorem axioms restricted to
`propext`, `Classical.choice`, and `Quot.sound`. The last data module build
passed in 2.90 seconds and printed all nine named theorem checks. The raw
layout comparison also completed. The reviewer independently compiled the
revised shared-cover native module in 1.72 seconds, printing all 15 named
theorem axiom sets with no additional axioms. Its exact source hash, theorem
inventory and log are in `review-receipts/native-input-review.json` and
`review-receipts/native-input-review-output.txt`. No further material issue was found in
that native-input/output join.

The source geometry and final invocation component builds have since passed
against the real source tables. The subsequent coherent package replay also
passed all 52 modules and 930 theorem-closure audits. Its generated manifest
and `replay-result.json`, rather than this review note, are authoritative for
final build completion; `VALIDATION.md` records the reproduction details.
