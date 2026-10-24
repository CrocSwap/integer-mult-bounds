# PR442 level-model connection: Phase 2

AI-assisted verification and writing; this is not an independent human audit.
Apache-2.0. Attribution uses `AI-assisted verification contributor
<verification-contributor@example.invalid>`.

This separate package interprets the unchanged Phase 1 endpoint descriptors as
ambient operators and compares their differences with PR1231's `pendingAxes`.
Its target is only **children 1 and 2 used by PR540, all 120 ports and both
data sides**, over every field `K` with `(2 : K) ≠ 0`.

The dependency is frozen Phase 1 commit
`d418130e3bbee1cb6923f0f734d5788e09933f57` (PR #1365), based on
`448690c3b7e5c2b5975b760075b162fe0a8cfb03`. The Phase 1 package, its 38
theorem statements, and its published receipt are preserved byte for byte.
`PROTECTED-FILES.json` also preserves all 519 predecessor files recorded by
Phase 1 and its CI workflow, for a total of 542 protected files.

## Reproduce

Use Lean **4.21.0** and Mathlib
`308445d7985027f538e281e18df29ca16ede2ba3`, pinned by the Lake manifests.
The verification scripts use only the Python standard library.

```sh
cd research/lean-pr442-level-model-phase2
lake exe cache get Mathlib.Data.Matrix.Mul Mathlib.Algebra.BigOperators.Fin Mathlib.Tactic.FieldSimp Mathlib.Tactic.Ring Mathlib.Tactic.NormNum Mathlib.LinearAlgebra.Span.Defs
python3 verify.py --receipt /tmp/pr442-level-model-phase2.json
```

The verifier checks frozen sources and published input hashes, performs a
read-only check that the Phase 1 literal extractor reproduces its published
descriptors, and runs ordinary `lake build` and `lake env lean Audit.lean`.
It supplies no compiler flags, Lean environment overrides, resource-limit
changes, or raised source-level options. New Lean declarations use default
settings; the existing dependency's published settings are unchanged.

`python3 verify.py --check-only` validates sources and inventories without
invoking Lean. It is not a proof-build result. `update_manifest.py` regenerates
the reviewed inventory, exact theorem documentation, and permanent axiom
probes; it is a maintainer command, never part of verification. Dependency
cache acquisition is separate from measured proof-build time.

The dedicated new workflow is
`.github/workflows/pr442-level-model-phase2.yml`. Local compilation and
successful CI are separate claims. The passed Phase 1
[CI run](https://github.com/cheesegrader/integer-mult-bounds/actions/runs/38482036983)
is a baseline result only.

## Input reconstruction and reflection

`SOURCES.json` retains the published PR370/PR386/PR442 input hashes from
Phase 1. Its unchanged finite joins bind old/current roots and endpoint IDs,
frame basis rows, PR540 frame trajectories and ownership, literal call
orientation, route axes and bridge partner state. No Phase 2 endpoint is
defined from `PendingDerivation.inLevel` or `pendingAxes`.

`FieldEntrance.lean` casts the literal integer frame certificates directly
into `K`, with no rational-to-field homomorphism. It derives source and target
entrance and exit projectors separately. In particular the source entrance is
the root projector, while the target entrance is zero; their exit projectors
also differ. Their equal *differences* must be proved.

`RouteTransport.lean` interprets a descriptor by complementing its **local
eight-dimensional frame first**, adjoining its literal cumulative exterior
axes, and transporting along its literal route. A reflected call also swaps
the physical side before choosing its frame. Complementing the entire ambient
64-dimensional operator would incorrectly select untouched exterior axes.

The transport reuses the certified literal route results
`PortGeometry.quarteredRoute_exact`, `PortGeometry.route15_entry`, and
`PortGeometry.sourceRoute64_eq`. Endpoint reconstruction retains the
source/target distinction; cancellation of their shared correction is proved
in the final pending-operator comparison.

`IdleOperators.lean` maps Phase 1's `sourceBefore` and `sourceAfter`
descriptors to operators. Their difference defines `idlePendingOperator`.
`pendingOperator` alone supplies the chart-coordinate comparison target from
PR1231's `pendingAxes`. The final theorems quantify over arbitrary input
vectors, not a finite set of test vectors.

`EntranceContinuity.lean` connects the stage 0–3 local input descriptors to
the preceding physical endpoints needed for the two selected children. It
preserves the same literal endpoint and reflection interpretation.

## Main statement and boundary

The exact final comparison statement is:

```lean
theorem idle_pending_operator (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (child : Nat) (hchild : child = 1 ∨ child = 2)
    (port : Fin 120) (side : Bool) :
    idlePendingOperator K child port side = pendingOperator K h2 child port
```

This is equality of functions on all ambient vectors. The physical operator is
`sourceAfterOperator - sourceBeforeOperator`; its endpoint descriptors come
from the unchanged independent reconstruction. The target is conjugation of
the coordinate mask for `PendingDerivation.pendingAxes child` by the certified
port chart. Children 1 and 2 give axes `[15,22)` and `[1,29)` respectively.

`source_before_sided_difference` and `source_after_sided_difference` retain the
literal entrance-root projector as the difference between the physical sides.
`idle_source_target_cancellation` follows after separately identifying each
side's pending increment. The levels themselves are not equated.

This connection is restricted to the two selected idle children. It does not
prove the other eight idle events, a full cover sweep, physical disjointness
across invocations, complete scheduled execution, later scheduling, a cost
bound, all-size compilation, or a kappa result. The independent JSON parser,
source extractor and hash checks remain external trust boundaries. Provenance
credits remain with PR370's word/exporter, PR386's geometry, PR442's hosting,
PR540's literal invocation proof and PR1231's schedule work. This AI-assisted
work does not represent an independent human audit.

## Audit and controls

`THEOREMS.md` contains exact source theorem statements, and `Audit.lean`
probes every named new definition, abbreviation and theorem. The only allowed
axioms are `propext`, `Quot.sound`, and `Classical.choice`. The source scanner
rejects proof escapes, new axioms, nondefault options and circular endpoint
definitions. The verifier checks dependency revisions and source cleanliness
and records executable/source/artifact hashes, timing, inherited stack limits,
actual axiom sets and artifact freshness.

Each Lean mutation control first checks that its candidate proposition is
well typed, then compiles the positive witness and requires semantic rejection
of the corresponding changed input. Import errors, malformed Lean, missing
instances and resource-limit failures do not count as rejection. Large literal
tables are reduced through certified joins or Lean kernel evaluation, with no
nondefault options. Controls
exercise frame IDs, a root coordinate, stage axes, reflected orientation,
reflection's side swap, bridge partners and cumulative exterior axes. The
critical ambient-complement witness uses an untouched exterior coordinate.

The independent Python source review is corroboration outside Lean's kernel.
Lean proves the algebraic operator statements; it does not verify Python,
JSON parsing or SHA-256 execution. Measured validation results and remaining
boundaries belong in `validation/README.md` and its receipts.
