# External claim review

Reviewed 2026-10-12 against local contribution commit
`f7330c5f5b1c5e85f91a98c95e8efc0e27c03490`, including Task A at
`13611a8958fc71046a83d8431d2bd6335e6a3e2f`. The selected algorithm source is
PR442 `4e16d001d505d4f21dd2bcfc44591f9be4c279bd`.

**Verdict:** the statements support a checked abstract multi-host theorem
and a concrete connection for one selected source invocation. They do not
support a verification of the complete algorithm, a resource saving or an
integer-multiplication bound. No unresolved mathematical mismatch was found
between the final entry theorem and that bounded claim. The source-extraction
and continuation boundaries below are essential parts of the claim.

This is a Codex agent review, not an independent human audit. The reviewer
also developed frame/raw refinement modules and `SourceDataBehavior.lean`,
and helped debug `PhysicalSourceConnection.lean`; the ownership, geometry,
comparison and final connection were reviewed across agents. The requesting
contributor initiated and coordinated the AI effort. Codex agents developed
the proofs, ran automated checks and produced written reviews. This report
does not represent the contributor as having personally derived the
mathematics or independently checked the proofs.

## Task A: what is proved and what remains a premise

[`MultiHosting.multi_hosting`](../lean-multi-host-framework/MultiHosting.lean)
proves the retained-state equality for an arbitrary list of complete events
on multiple host streams. Every event must have the specified independent
coordinate-mask action on each host and an `other : R → R` action on the
remaining retained state. Residual masks must be pairwise disjoint and lie
inside the pending mask, separately for each host. Arbitrary input
correlations are allowed; a mathematical dependence of `other` on a host
is not allowed by this interface.

`MultiHosting.physical_multi_hosting` transfers this identity to original
and relocated execution functions supplied through `PhysicalContract`.
Those contracts universally quantify over dirty auxiliary inputs and are
genuine premises of Task A. Actual auxiliary outputs feed subsequent calls.
The resulting equality compares retained outputs; it does not assert that
auxiliary outputs are restored or interchangeable.

[`MultiHosting.SingleHost.whole_hosting_recovered`](../lean-multi-host-framework/SingleHostRecovery.lean)
derives the previous one-host operator statement by inverse singleton
embeddings. `physical_whole_hosting_recovered` derives the corresponding
physical statement using the preceding projection lemmas. Neither recovery
discharges a source-program endpoint premise. The two theorems in
`MultiHostControls.lean` are checked inequalities demonstrating the
cross-host mixing and physical-aliasing boundaries.

The abstract product type does not itself prove that its host indices
denote distinct physical streams or that their coordinate charts match a
source program. Task B supplies these interpretations for the selected call.

## Task B: concrete checked statements

All entry declarations below are in [`SourceInvocation.lean`](SourceInvocation.lean).
They concern stage 2, replica 0, pair 0, forward orientation: 19,002 events,
240 data roles, 747 helper roles and one designated private role.

| Declaration | Exact claim |
| --- | --- |
| `actualContract` | Constructs `MultiHosting.PhysicalContract` from the old and hosted execution folds and their explicit input/output layouts. Its endpoint obligations are proved, rather than passed as additional provider hypotheses. |
| `selected_call_completion` | Equates all retained outputs after the hosted call plus remaining pending swaps with the old call plus full pending swaps. Its single event is the complete 19,002-instruction invocation. |
| `selected_native_completion` | Gives the same equality for native instruction executions, read in the fixed retained coordinate charts. |
| `selected_native_realization` | Identifies each complete raw execution with its native execution through one shared cover-chart extension. |
| `selected_matrix_realization`, `selected_original_matrix_realization` | Identify the active-role gathers of both complete execution folds with the certified matrix word. Exterior preservation is supplied separately by the raw/native refinement results. |
| `selected_data_formula` | Gives the common old/new data endpoint, preserving the actual port charts and unequal entrance/exit frame pullbacks. |
| `selected_native_clean`, `selected_temporary_restoration` | Prove chronological COPY blankness and ERASE equality along those native runs, and return each layout's designated private row blank. |

The following dependencies are substantive parts of that source connection:

- `SourceMatrix.arbitrary_dirty_payloads` and `actual_payload_clean` interpret
  the complete embedded word on every Boolean-valued input stream. They
  follow from the checked symbolic matrix execution, not sampled payloads.
- `SourceFrameTrace.scalar_word` and `route_projection` connect the scalar,
  frame and finite-role event lists. Actual indices are checked below 988;
  the other 36 binary-tree leaves are inaccessible representation padding.
- `SelectedGeometry.helper_relative` supplies the actual helper endpoint
  geometry. `SourceMoveGeometry.actual_matrix_run` uses checked membership
  of actual MOVE pairs in the projector table to identify the complete
  word's MOVE and COPY matrix operators. The stage-2 exterior factor is
  included and cancelled in the proofs.
- The source and parent ownership modules prove injectivity of actual
  family-and-cover-function keys. A family label alone is not treated as
  a distinct physical stream. The port and slot charts are concrete choices
  constructed from the source descriptors.
- `SourceInvocation.owner_overlap_data`, `old_common_cover` and
  `new_common_cover` construct one native convention for both layouts.
  `initialized_native_host_input`, `initialized_native_data_input` and
  `initialized_native_tail_input` prove equality of retained native inputs
  after private-row preparation. This closes an earlier review finding in
  which two different inactive-owner cover extensions were used.
- `oldResult_framed` includes the actual old-bank outputs, through
  `oldRaw_bank`. They are not replaced by their inputs. The final hosting
  equality then compares the retained projection, as its contract specifies.

## Parameters, resources and external boundary

The concrete entry theorem accepts a field `K`, the condition `(2 : K) ≠ 0`,
an invertible invocation chart `d`, arbitrary retained state and arbitrary
old-bank payloads. It does not take geometry, owner injectivity, clean-work
guards or an endpoint-equality theorem as extra hypotheses. These parameters
are inhabited, for example by rational addresses and identity `d`.

The allowed initial states include one designated clean private stream in
each layout. `SourceRaw.initial` constructs that permitted initial state;
it is not an instruction that erases an arbitrary dirty temporary for free.
All 987 original live roles may be dirty. The old auxiliary layout has its
747 independent input streams, while the relocated layout has no separate
helper-bank argument. No physical cost conclusion follows from these types.

The compared retained state consists of all 747 affected host streams,
all 240 active data streams and arbitrary exterior payloads outside the
union of the active owner images. The explicit embeddings assign defaults
to slots unused by a layout. Thus the theorem is not equality for arbitrary
complete global allocations. `SourceRaw.other_payload_preserved` and
`SourceRawGuards.native_other_preserved` separately establish preservation
of arbitrary exterior payloads for their respective executions.

The source-to-literal connection is external to Lean. `check_sources.py`
checks pinned input hashes, reconstructs binary records, compares normalized
events and regenerates certificate sources using Python/SymPy. Lean proves
the mathematical claims about those embedded literals; it does not verify
the JSON parser, Python producer or extraction program. This boundary must
accompany the phrase “actual source invocation.”

The native ADD model is same-address Boolean XOR. Every actual source ADD
has coefficient `+1`; its separate phase field is an exporter annotation,
not another multiplier. The checked frame metadata and native-coordinate
refinement do not introduce the missing split-stream interface discussed
in PR448. Its advertised gain remains unestablished.

## What is not established

The multi-host theorem is applied to a singleton list containing the entire
19,002-instruction invocation. Its pairwise-disjointness condition between
separate events is therefore vacuous; cross-invocation disjointness is not
exercised. Owner injectivity within this selected invocation is proved and
does not establish disjointness across invocations.

The pending-coordinate ranges 15..21 and 1..28 (half-open `[15,22)` and
`[1,29)`) are hand-supplied in `PhysicalSourceConnection.pendingTag`.
`tag_pending_contains` checks only the target-mask containment needed by
the completion theorem. Nothing in Lean or the source-extraction check
binds those ranges to the source schedule. The pending-mask completion is
applied immediately after this invocation. There is no proof here that
these operations occupy the required later positions in the full recursive
child schedule. There is also no complete
cover sweep, reverse-orientation theorem for the selected invocation,
all-size source compiler, fixed-tape implementation, physical cost bill,
register-saving theorem, analytic transfer or new κ bound. A continuation
that observes or reuses auxiliary outputs needs its own scope/restoration
argument. The two mutation controls concern one corrupted next checkpoint
and a dirty-private first-COPY state, not full corrupted-program replays.

## Validation evidence and wording review

At the original review, all then-current Task B manifested source hashes
matched the manifest, whose hash matched the stored PASS replay receipt: 52 source-built
modules, `lean -t 0`, and 930 named theorem axiom closures. Task A's six
source hashes also matched its PASS receipt and 21 named theorem checks.
The Task B receipt completed at 2026-10-11 23:59:17 UTC with only `propext`,
`Quot.sound` and `Classical.choice`. Generated finite checkpoint declarations
account for much of the count; it is not a count of independent mathematical
ideas. This review inspected those receipts and hashes; it did not repeat
the full approximately 46-minute package build. See [VALIDATION.md](VALIDATION.md)
for the hash-checked resume history and [BUILD.md](BUILD.md) for reproduction.
The current permanent inventory adds `SourceInvocation.actualContract`, a
constructed definition, to those 930 named theorem declarations. The separate
fresh replay completed at 2026-10-12 03:19:37 UTC and audited all 931
declarations, with 52 modules freshly compiled and zero reuse. Its
[`actualContract` axiom report](../lean-external-review/validation/task-b.json)
lists only `propext`, `Classical.choice`, and `Quot.sound`. The historical
receipt is not evidence that this added declaration was audited. Current
fresh-build evidence is recorded separately in
[`../lean-external-review/VALIDATION.md`](../lean-external-review/VALIDATION.md).

The README's substantive claim boundary agrees with the statements. Three
wording refinements were requested and verified in the updated README: the
native bridge is described as proved rather than a future requirement;
cleanliness is attributed to the named proved theorems; and the
matrix-realization equalities are described as active-role gathers of
complete folds, with exterior preservation separate. The updated notice
also explicitly distinguishes the human contributor's coordination from
the agents' proof development, checks and reviews. Packaging-only dependency relocation
does not change these mathematical claims, but its source manifests and
reproduction evidence must continue to match the distributed files.

Existing generic transport and completion work, including PR397, Jacob
Sussman's repository, PR509 and PR513, is credited in the overlap review.
The useful checked addition is the selected concrete supplier obligation;
no exhaustive novelty claim is made for the supporting algebra.
