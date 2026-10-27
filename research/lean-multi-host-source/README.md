# One concrete invocation of whole-residual hosting

**Lean 4.21 port: fresh verification PASS.** The exact upstream Mathlib pin,
153 fresh local module builds and all five axiom inventories are recorded in
[the current validation report](../lean-external-review/VALIDATION.md).
No external stack, flags or environment tuning is needed. The CI projection
is 34.90 minutes under its stated cache/setup assumptions.

All 66 original contribution files are covered. Nine unchanged third-party
snapshots under `review-receipts/external-overlap/raw/` are archival evidence,
excluded from the Lake build, CI compilation and axiom audit. The historical
4.33 receipts and Phase 1 probes are separate evidence, not reused local builds.

This is Task B of the local verification contribution. Task A, the abstract
multi-host theorem and recovery of the previous single-host theorem, is
separately committed as `13611a8958fc71046a83d8431d2bd6335e6a3e2f` in
`../lean-multi-host-framework`. Its success does not establish this source
connection.

The selected source is PR442 at
`4e16d001d505d4f21dd2bcfc44591f9be4c279bd`, stage 2, replica 0, pair 0,
forward orientation. It uses the inherited R747 word: 19,002 events,
987 live roles, and one clean private temporary. All 747 helpers may contain
arbitrary, correlated dirty payloads. The original and relocated templates
contain the identical local word.

**Lean 4.33 baseline fresh build: PASS.** At review base
`c4b1560a569f54064608bf88440f9e492c03fba3`, the replay completed at 2026-10-12 03:19:37 UTC
from an empty project build directory, without resume: all 52 modules were
freshly compiled and all 931 declarations audited, including
`SourceInvocation.actualContract`. No project artifacts were reused.
The [fresh receipt](../lean-external-review/validation/task-b.json) directly
matches the baseline manifest and sources and records the installed Lean/Mathlib and
dependency fingerprints. It does not claim a fresh build of Mathlib itself.

**Historical build status: PASS.** The earlier coherent source build checked all 52 modules
(50 in this directory and two local dependencies) with `lean -t 0` and
audited 930 named theorem closures, using only standard
Lean axioms. Hash-checked resume retained successful builds from the same
initially empty directory. See [replay-result.json](replay-result.json) and
[VALIDATION.md](VALIDATION.md). Source extraction also passed independently.

## What the concrete checks establish

`SourceEndpoint.lean` reflects the complete literal word into a symbolic
matrix and proves its interpretation for every Boolean payload function.
Every target row receives its corresponding source row, all other live
normalized rows are restored, and the private row starts and ends at zero.
All nine COPY and nine ERASE guards hold throughout the actual sequence.
This is an arbitrary-input theorem, not a sample of input assignments.

`SourceFramed.lean` joins the scalar certificate to the literal chronological
frame trace. It proves the decoded and physical endpoint for a family of
genuine address gauges, including every frame-label and clean-private guard.
The concrete geometry and ownership modules discharge the identification of
those gauges and nominal roles with the source.

The final statements are collected in `SourceInvocation.lean`:

| Declaration | Obligation |
| --- | --- |
| `actualContract` | Construct the old/new invocation contract from their literal execution folds. |
| `selected_call_completion` | Apply the multi-host theorem to this invocation and its remaining pending swaps. |
| `selected_native_completion` | Compare those same executions in common native coordinates. |
| `selected_matrix_realization`, `selected_original_matrix_realization` | Identify active-role gathers of both complete execution folds with the source matrix word; exterior preservation is proved separately. |
| `selected_data_formula` | Display the data endpoint with actual entrance/exit frames and port charts. |
| `selected_native_clean`, `selected_temporary_restoration` | Establish chronological COPY/ERASE legality and return the private row blank. |

The permanent axiom-audit inventory now includes the constructed definition
`SourceInvocation.actualContract`, alongside the 930 named theorem declarations:
931 declarations in total. The historical 930-declaration receipt does not
certify that expanded inventory. The completed historical 4.33 fresh replay
audits all 931 declarations. The fresh 4.21 replay also audits this complete
inventory. Current status is reported in
[`../lean-external-review/VALIDATION.md`](../lean-external-review/VALIDATION.md).

The geometry uses exact integer witnesses, cast into any field with
`2 ≠ 0`. Projectors have denominator dividing four; complete basis inverses
have denominator dividing 256. This avoids assuming a rational-to-field
map that would be invalid in positive characteristic. The actual stage-2
exterior factor is included in both endpoint gauges and cancels formally.

The relocated layout has 747 distinct helper streams on 317 family labels;
a stream owner includes its cover map. The original bank uses 172 families,
61 slot descriptions, and 59 distinct coordinate permutations. Owner
injectivity concerns the actual functions on coordinates, not nominal tag
inequality. The source permits a choice of slot isometry; the certificates
construct one exact permitted choice from the literal slot descriptors.

The native-coordinate bridge identifies an ADD with reading the same
native address in its two streams. Its identity is
`g_source σ_source σ_target⁻¹ = g_target`, where `g σ = d` is the common
invocation chart. This uses one stream per helper. It assumes no split-helper
interface from PR448.

Both native executions use one common cover-chart extension on the union
of their active owners. The intersection is proved to consist exactly of
the shared data owners, where the charts agree. This is necessary to make
equal retained raw inputs denote equal native inputs in both layouts.

The private identifier names the source's reserved clean storage. For this
fixed invocation its native chart is the common cover chart `d`; the
identifier's placeholder is not an assertion that `d` is identity. The
source explicitly reserves private storage. The 36 extra leaves of the
certificate's binary tree are inaccessible padding, not algorithm registers.

## Comparison boundary

The comparison's retained state includes all 747 affected host streams,
all 240 active data streams, and arbitrary payloads outside the union of
the two layouts' active owner sets. Original helper-bank outputs
are returned and threaded as auxiliary outputs. They are not silently
asserted equal to their initial values. `selected_native_clean` and
`selected_temporary_restoration` prove temporary cleanliness for the actual trace.

The common slot universe is a device for this local comparison. The input
embeddings assign defaults to slots unused by a layout; this is not equality
of arbitrary complete global allocations. Separately, the raw/native
execution theorem permits arbitrary payloads on all actual exterior streams
and proves they are preserved. The host observations use an explicit,
invertible family coordinate chart, so their complete payloads are retained.

The corollary applies the multi-host theorem to one complete invocation:
all 19,002 instructions form the single event in its event list.
Consequently, the theorem's disjointness condition between separate events
is vacuous here; cross-invocation disjointness is not exercised. The proved
injectivity of physical owners within this invocation is a separate result.

The pending-coordinate ranges 15..21 and 1..28 (half-open `[15,22)` and
`[1,29)`) are hand-supplied in `PhysicalSourceConnection.pendingTag`.
For these ranges, Lean's `tag_pending_contains` checks that they contain
the corresponding target masks. Neither Lean nor the source-extraction
check binds these ranges to the source schedule. The comparison applies
the remaining pending swaps immediately after the invocation; it does not
establish the full cover sweep or identify this immediate completion with
the later child schedule of the full algorithm. It also does not establish
a physical instruction-cost bill, an all-size compiler, analytic transfer,
or a higher κ. PR448's advertised split gain remains unestablished.

## Reproduction and review

See [the current Lake build instructions](../lean-external-review/BUILD.md),
[source-versions.json](source-versions.json) for the source and input hashes,
and [proof-manifest.json](proof-manifest.json) for the local module inventory.
`check_sources.py` checks the raw source binding and regenerates the literal
certificates. JSON extraction is a reproducible external boundary; Lean
checks the mathematical statements about those embedded literals.

`SourceControls.lean` proves that deleting an actual ADD changes the next
certified checkpoint despite preserving that chunk's clean-work checks.
It also applies the first actual COPY instruction to a state with a dirty
private temporary and proves that its guard rejects the overwrite. These
are focused controls, not full replays of the corrupted word.

The overlap search and its limits are in `overlap-review.md`. In particular,
PR509 already formalizes overlapping generic transport and replay principles;
the contribution here is the concrete source obligations. Attribution is
recorded in `NOTICE.md`.

For the external-review delivery, start with
[`../lean-external-review/README.md`](../lean-external-review/README.md).
It provides the cumulative public-base patch, all local dependencies, exact
setup and reproduction instructions, a refreshed bounded overlap review,
and an explicit audit of these claims in [EXTERNAL-CLAIM-REVIEW.md](EXTERNAL-CLAIM-REVIEW.md).
