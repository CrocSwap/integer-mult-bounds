# Source-invocation review

Review snapshot: 2026-10-11, after the shared native-cover correction.
This is a separate agent's source-level review of the execution/contract
connection, not an independent human audit. The reviewer authored the
ownership/layout modules, `SourceInitialPayload`, and the corrective
`SourceCommonCover`; those portions are not independent of their author.

The principal files reviewed were `SourceInvocation.lean`,
`SourceInvocationComparison.lean`, `SourceNativeInvocation.lean`,
`SourceInitialPayload.lean`, and `SourceMoveGeometry.lean`. The review also
followed their definitions into `SourceInvocationState`, `SourceRaw`,
`SourceRawGuards`, `SelectedGeometry`, and the pinned PR442 source.

## Result and build qualification

The raw execution-to-contract connection has the intended arbitrary-input
scope. It does not assume an endpoint contract, injective owner mapping,
helper-relative-frame equation, or clean dirty-helper input in its final
theorem. The concrete arguments are constructed and the intermediate
premises are discharged by named source certificates.

One material issue was found jointly with the separate interface reviewer:
the first native comparison used two different extensions of the owner
cover charts. The original extension assigned identity to hosted owners
outside its active image; the relocated extension assigned their actual
cover maps. Equal raw payloads therefore did **not** imply equal native
retained inputs. The raw theorem was unaffected, but the stronger native
interpretation required correction.

`SourceCommonCover` now supplies one shared extension. Its kernel-checked
finite bound excludes the hosted private family 9457 from every selected
original live owner. Its overlap theorem proves that the two active images
overlap only on identical data roles, whose charts agree. Both common-cover
identities then follow. This module and `SourceInitialPayload` passed Lean
with `-t0`. The revised `SourceNativeInvocation` uses this shared extension
and states explicit initialized native input equalities for hosts, data,
and exterior payloads. Its author confirmed the revised module, including
the initialized-state equalities, passed Lean with `-t0`. The separate-cover
issue is resolved. The final coherent replay has subsequently passed.

At the original review snapshot, the geometry and final invocation modules
were still drafts. The subsequent component builds of `FrameData`,
`FrameGeometry`, `SelectedGeometry`, `SourceMoveGeometry`, and
`SourceInvocation` all passed against the actual source certificates with
`-t 0`. The final bridge source/artifact hashes are archived in
`review-receipts/final-bridge-components.json`. The subsequent coherent
package replay passed all 52 modules and 930 named theorem-closure audits;
`replay-result.json` and `VALIDATION.md` record that integration check.

## Retained outputs and dirty inputs

The retained state contains all 747 affected host streams, all 240 active
data streams, and a function on the entire complement of the union of the
two active owner images. Host observations use an invertible fixed family
chart, so they observe complete streams rather than selected coordinates.
`oldResult_framed` also equates every actual original-bank output with the
bank output returned by the contract. These outputs are not assumed restored
or silently projected away during that correspondence. The completion
equation itself compares retained outputs, as its type explicitly states;
old-bank outputs are auxiliary outputs, not equalities to initial bank data.

All displayed payloads are arbitrary Boolean functions. They can contain
arbitrary correlations. `oldPayload_data`, `newPayload_data`,
`oldPayload_bank`, `newPayload_host`, and `shared_host_input` verify that the
explicit chart embeddings do not constrain or replace those inputs.
Exactly one designated private row is initially blank in each invocation.
The initializer describes that permitted initial state; it is not an
instruction that clears arbitrary dirty storage. Inaccessible tree padding
is not an additional physical allocation.

The common slot universe and defaults on slots unused by one layout are a
local comparison device. They do not establish equivalence of the complete
global allocations or account for PR442's renumbering of other banks.

## Literal execution and physical interpretation

`SourceRaw.final` folds the complete chronological list of 19,002 source
events. `FrameTraceRoutes.route_projection` identifies the finite-register
encoding with the same frame trace; index bounds prevent modulo indexing
from changing an actual operand. `SourceRaw.gather_final` follows that whole
fold, not merely its first or last event. The exterior theorem preserves
every physical row outside its active owner image through the same fold.

`SourceRawGuards` transports COPY blankness and ERASE equality through the
actual preceding raw/native states. It does not insert a fresh initial
state between guards. `SourceNativeInvocation` returns both private rows
blank. Its native ADD reads the same address in both physical streams:
the route cancellation follows from the common-cover identity, not a
newly assumed cross-stream interface.

The geometry addresses the remaining distinction between abstract
frame labels and source matrix operators. The selected gauges include the
stage-2 exterior swap on axes 8 through 21. `SourceMoveGeometry` explicitly
cancels this common exterior factor, selects each actual MOVE's certified
nested projectors, and identifies its relative gauge with
`D_(Pnew-Pold)`. COPY is identified with the full local eight-coordinate
swap; ERASE uses the corresponding equality guard. The complete
`actual_matrix_run` theorem carries frame matching and chronological
validity through the entire list. The component build and subsequent coherent
package replay have both passed.

The chosen helper charts are source-permitted coordinate isometries, not
numeric matrices claimed to have been emitted by the symbolic template.
The actual port bases and data-route matrices are bound separately. The
theorems quantify over any field with `2 ≠ 0` and any invertible common map
`d`, which includes the source's admitted odd fields and cover elements.
This broader identity does not claim that every arbitrary bijection `d`
is an admissible member of the source's orthogonal cover.

## Source boundary and limits

The reviewed source is PR442 commit
`4e16d001d505d4f21dd2bcfc44591f9be4c279bd`, stage 2, replica 0, pair 0,
forward orientation. During this review, `check_sources.py` passed: all six
pinned input hashes, the binary-record reconstruction, the identical parent
and hosted local words, all 19,002 events in order, and reproducible
certificate extraction were checked. The original review receipt was a local
artifact and is not included in this package. A separate, later regeneration
is recorded in the shipped [source-binding receipt](../lean-external-review/validation/source-binding.json).
This Python/source extraction boundary is reproducible, not kernel-verified.
The Lean kernel checks the mathematical claims about the embedded literals.

The completion adds the explicit remaining pending swaps immediately after
this one invocation. It does not identify that completion with the later
recursive child schedule, prove a whole-cover sweep, verify global resource
charging, supply an all-size compiler, or establish any analytic bound.
Nothing here uses PR448's disputed split-helper interface or establishes
its advertised gain.

## Detailed matrix-operation follow-up

The following references were checked directly against the PR442 checkout
at the pinned commit above. Line numbers refer to this review snapshot.
The inherited `research/split-centres-global/proofs/PR386-BIT-GEOMETRY.txt`
supplies the operator definitions; its historical R865 ledger is not being
substituted for the selected R747 word. The latter is emitted by
`research/e8-early-reset-kernel/bit_global.py` and bound to the supplied
template and binary records.

- **Projector identification.** The inherited operator definition is
  `D_P = [[I-P,P],[P,I-P]]` (PR386 geometry, lines 37–46).
  `FrameGeometry.partialSwap` is exactly this action:
  `(x + P(y-x), y - P(y-x))`. The source frame's `B` rows are the image
  subspace. `generate_frame_data.py:83–95` binds the complete `[B;A]`
  row stack and computes integer witnesses; `FrameGeometry.projector_stack`
  proves the supplied projector fixes the `B` columns and kills the
  `A` columns. `stack_right_inverse` and `stack_left_inverse` prevent a
  deficient spanning family from making those equations vacuous after
  reduction to an odd field. Integer casts and denominators 4 and 256
  avoid an invalid rational-field embedding.
- **MOVE direction.** The source advances old frame to new frame and
  records their nonnegative dimension difference
  (`e8-early-reset-kernel/bit_global.py:91–96`). For payload pullback,
  preserving decoded contents requires `old.forward ∘ new.inverse`
  (`FramedReplay.lean:35–46`). After cancelling the common exterior
  factor, the order is therefore `D_old D_new`, not a sign-reversed
  residual. `SourceMoveGeometry:25–56` obtains both absorption equations
  from the literal MOVE pair and uses `P_old P_new = P_old` to obtain
  exactly `D_(P_new-P_old)`. This agrees with the source's displayed
  `D_new D_old` law because the same certified nested projectors commute.
  `SourceFrameMoves.move_pair` in `FrameMoveData.lean` binds the selected transition to the literal
  old/new labels; a nominal rank equality alone is not used.
- **E2 cancellation.** PR386 geometry lines 48–54 specify the same first
  two exterior 7-blocks on every frame of stage 2. They are axes 8–21.
  `FrameGeometry.gaugeStage2` includes this actual swap in the forward map
  and in the inverse map in reverse order. In the relative map the two
  exterior swaps are adjacent and cancel by involution. No unproved
  commutation premise is needed for that cancellation, and the other
  56 coordinates remain fixed by the local residual.
- **COPY.** The actual forward emitter checks a fresh blank temporary,
  no currently retained center, and a frame difference of eight
  (`bit_global.py:104–110`). `SourceFrameLabels.copy_frames` certifies
  that every selected COPY uses frame 1 to frame 0.
  `SourceMoveGeometry:75–110` identifies this relative transport with
  the full swap on local axes 0–7, fixing all exterior axes.
  `physicalStep_copy` (lines 158–178) identifies the operational step;
  COPY legality is separately discharged along the same run, rather
  than being deduced merely from the operator equality.
- **ERASE.** The emitter requires the retained center, the exact source
  and temporary frames, and equal scalar columns before returning the
  temporary to zero (`bit_global.py:111–116`). `FrameTraceCore:31–42`
  checks center lifetime and excludes writes to the center while it is
  retained. `SourceRawGuards:62–75` expresses ERASE as equality with the
  source transported to the temporary's actual current frame, and its
  recursive predicate uses each preceding physical output.
  `SourceMoveGeometry:112–124` identifies that transport as the full
  local swap. Thus the interpreter's zero assignment represents a
  certified uncomputation, not permission to discard arbitrary dirt.
  The post-ERASE frame-zero marker replaces the source's unallocated
  marker; changing metadata on a zero payload has no address operation.
- **Whole execution.** `SourceMoveGeometry.matrix_run_eq:191–214`
  propagates frame matching and chronological checks after each actual
  instruction. `actual_matrix_run:218–224` discharges those hypotheses
  using the literal trace and initial metadata. The final
  `SourceInvocation.selected_call_completion` obtains its endpoint
  through `SourceInvocationComparison` and `SelectedGeometry.helper_relative`.
  Its companion theorems `selected_matrix_realization` and
  `selected_original_matrix_realization` identify those same concrete
  raw runs with the whole matrix word. `selected_native_completion`
  uses the common-cover native readbacks, while
  `selected_native_clean` and `selected_temporary_restoration` provide
  legality and the private-row endpoint. The matrix-operation claim is
  therefore an explicit companion equality, not an inference from a
  module merely being imported.

No further source-level operator mismatch was found in this follow-up.
The geometry and final invocation component builds have since passed, followed
by the coherent package replay recorded in `replay-result.json`.
