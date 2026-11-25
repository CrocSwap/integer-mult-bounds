# PR442 level-model connection: Phase 1

AI-assisted verification and writing; this is not an independent human audit.
Apache-2.0. No attribution requested; please do not add the coordinating account
to CONTRIBUTORS.

This package supplies the finite source joins and rational entrance-line
theorem needed for the **two idle children used by PR540**, children 1 and 2,
at all 120 ports and for both data sides. It is based on PR1231 commit
`448690c3b7e5c2b5975b760075b162fe0a8cfb03`, which includes PR540 commit
`acc1917034d10f464271ab115fda314fd4eee7a3`.

Only new files are added. The 519 predecessor files recorded in
`BASE-FILES.json` must remain byte-for-byte unchanged. No theorem in PR540 or
PR1231 is modified. The package does not prove the Phase 2 pending-operator
equality, and does not claim that PR1231's level-model boundary is fully closed.

## Reproduce

Use Lean **4.21.0** and Mathlib
`308445d7985027f538e281e18df29ca16ede2ba3`, as pinned by the Lake manifest.
Python 3.11 or newer is sufficient; the new verifier uses only its standard
library. An ordinary clean checkout contains every new input.

```sh
cd research/lean-pr442-level-model
lake exe cache get Mathlib.Data.Matrix.Mul Mathlib.Algebra.BigOperators.Fin Mathlib.Tactic.FieldSimp Mathlib.Tactic.Ring Mathlib.Tactic.NormNum Mathlib.LinearAlgebra.Span.Defs
python3 verify.py --receipt /tmp/pr442-level-model-phase1.json
```

The verifier runs `lake build` and `lake env lean Audit.lean`, then compiles
positive controls and mutated-input negative controls. It supplies no compiler
flags, environment overrides, or stack-limit changes. Source-level heartbeat
and recursion options are retained where needed. The dedicated
`.github/workflows/pr442-level-model.yml` runs these same commands on the fork.
Mathlib cache acquisition is a setup step, separate from measured proof build
time; if unavailable, Lake can build missing dependencies from the pinned source.

`python3 verify.py --check-only` checks manifests, unchanged predecessors,
input hashes and reproducible extraction without invoking Lean. It is not a
proof-build pass. `update_manifest.py` is a maintainer tool, not a verification
step: it regenerates the reviewed file inventory and permanent axiom probes.

## Independent source reconstruction

`LevelSourceData.lean` is extracted from the pinned PR442 frame/state/geometry
and hosted-template files and two vendored PR386 artifacts. `SOURCES.json`
records compressed and uncompressed SHA-256 values and their published
references. The JSON parser and extractor remain an external trust boundary;
Lean checks the resulting literal joins, not Python execution or SHA-256.

The PR386 word is PR370's R865 word, whereas the selected PR442 invocation has
747 helpers. These are not treated as the same program. Instead:

* PR386's `RECORD-SHA256SUMS` and PR540's `source-versions.json` publish the
  same raw `frames.json` hash,
  `884480e45865a9d9d57f5f7198844a64271b046bc95e9820efbefb9e10878330`.
* The extractor compares the first 240 data-role entrance and exit labels,
  explicitly excluding the different helper populations.
* It reconstructs the relevant old frame basis rows in the exporter's
  independent-row order and compares them with PR442's literal basis rows.
  Lean then checks the supplied old/current label and row joins.
* PR442 geometry identifies its inherited PR386 compressed artifact by hash.
  The extractor checks equality of all 120 complete port records, including
  roots, complementary columns, route matrices and stage axes. Other geometry
  metadata is allowed to differ; whole-file equality is not asserted.

`LevelFrameJoins.lean` binds these inputs to PR540's existing frame trajectory,
ownership table, certified frame projectors, and port charts. At each port `p`,
the source entrance frame is `p + 2`, the target entrance is frame 0, the source
exit is frame 1, and the target exit is frame `824 + p`. These are checked
consequences of extracted arrays, not the definitions of the arrays.

`sourceBefore` and `sourceAfter` in `LevelSchedule.lean` return endpoint
**descriptors**, not yet interpreted ambient linear operators. A descriptor
contains its literal local frame ID, reflected-complement bit, stage, route
axes, and cumulative exterior axes. Reflected calls swap the source/target
roles; `call_owner_alignment` checks that convention against literal owner
families and route ports.

The reconstruction starts at the literal entrance endpoints. Local events
select their endpoint IDs using the call orientation. An idle event takes its
new endpoint provenance from the current state of the other pair in the next
literal bridge. The recorded idle source level, target level and rank do not
determine that state update. They are checked afterward. No definition or proof
in the new modules imports or refers to `PendingDerivation.inLevel`,
`pendingAxes`, or `derivedPendingTag`.

The resulting observations are:

| Child | Before | After | Recorded mathematical levels | Rank |
|---|---|---|---|---:|
| 1 | Reflected stage-1 exit | Forward stage-2 exit | 1 to 2 | 7 |
| 2 | Literal entrance | Reflected stage-3 exit | -1 to 3 | 28 |

Internally, the recorded levels are shifted by one to natural numbers, as in
PR1231. The finite reconstruction reads the ten-event prefix through the bridge
after child 2. Child 0 is only a prerequisite needed to establish child 1's
previous endpoint; no additional hosting instance is claimed.

## Main formal statements

All names below are in namespace `PR442LevelModel`. Their complete source
statements are in `LevelFrameJoins.lean`, `LevelSchedule.lean` and `BaseLevel.lean`;
the permanent `Audit.lean` also probes every named definition and theorem.
`THEOREMS.md` collects the exact theorem statements without their proof bodies.

* `old_endpoint_labels_join`, `old_roots_join`, `entrance_basis_join`, and
  `target_exit_basis_join`: connect the separately extracted PR386/PR370
  endpoint labels and root/basis data to PR442's frames at every port.
* `invocation_endpoint_labels` and `ownership_entrance_labels`: connect the
  extracted endpoint IDs to PR540's actual frame-trace and ownership literals.
* `entrance_scaled`: for every port and local matrix entry,
  `FrameGeometry.scaled (sourceEntrance p) i j = rootVector p i * rootVector p j`.
* `target_exit_scaled`: the target exit has scaled projector
  `4 * identity - rootVector * rootVectorᵀ`. The distinction between source
  and target sides is retained, rather than assigning both the same level.
* `route_root_block`: PR540's `quarteredRoute_exact` identifies the literal
  route matrix's upper-left block with the independently joined entrance
  projector. It does not establish the lifted route identity.
* `schedule_prefix_join`, `calls_match_schedule`, `call_owner_alignment`,
  `route_axes_join`, and `stage2_axis_positions`: finite source/schedule,
  reflection, owner and route-embedding joins.
* `child1_provenance` and `child2_provenance`: the observations displayed above.
  `child1_endpoints` and `child2_endpoints` expose their endpoint descriptors
  for every port and each side.
* `recorded_levels_and_ranks`: independently reconstructed provenance tags
  match each recorded level, and literal frame/lift dimensions have the
  recorded difference. This is not a proof of nested physical subspaces.
* `selected_invocation_inside_windows`: the selected stage-2 invocation lies
  between the relevant provenance observations without changing the two
  idle pairs' descriptors. This does not prove physical disjointness.

The rational root is `q p i := (rootVector p i : ℚ)` and
`rootProjector p i j := q p i * q p j / 4`. The base-level theorem is:

```lean
theorem source_entrance_projector (port : Fin 120) :
    FrameGeometry.projector ℚ (sourceEntrance port) = rootProjector port
```

Its range statement concerns every rational input vector:

```lean
theorem source_entrance_range (port : Fin 120) :
    Set.range (fun v : Fin 8 → ℚ =>
      FrameGeometry.projector ℚ (sourceEntrance port) *ᵥ v) =
    (Submodule.span ℚ ({q port} : Set (Fin 8 → ℚ)) : Set (Fin 8 → ℚ))
```

This establishes the literal local entrance line `span(q)` over the rationals.
It does not by itself identify all schedule levels in the ambient address chart.

## Validation and remaining boundary

Recorded runs and their freshness are documented in `validation/README.md`.
The local receipt is `validation/local-phase1.json`; the fork workflow also
publishes its independently produced receipt as the `pr442-level-model-phase1`
Actions artifact. A recorded pass applies to the source manifest and dependency
fingerprints in that receipt, not to arbitrary later edits.

The allowed axiom set is exactly `propext`, `Quot.sound`, and `Classical.choice`;
individual declarations may use fewer. The verifier requires the complete
permanent inventory, scans new Lean sources for forbidden proof escapes and
options, and rejects changed predecessor files. The receipt records actual
axiom sets, toolchain version, dependency revisions, source/artifact hashes,
inherited stack limits, commands, timing, and whether local modules were fresh.

Five semantic controls mutate an entrance frame ID, a root coordinate, a
stage-2 route axis, a reflected-call orientation, and a recorded source level.
Each unmutated control must compile first; each mutation must fail because
Lean decides its proposed certificate is false. A parser, import or syntax
error is not accepted as a successful negative control. Mutations occur after
hash admission, so these controls exercise semantic checks rather than only
detecting altered input hashes.

Phase 2 remains: interpret endpoint descriptors using PR540's actual route
matrices; prove the sided lifted route identities and agreement of local
entrances with previous endpoints; transport the result to every field with
two nonzero; and identify each of the two pending operators with its coordinate
mask. The existing `route15_entry` and `sourceRoute64_eq` are available for
that work. The present bookkeeping replay is not a physical execution proof.

No full cover sweep, cross-invocation physical disjointness, later scheduling,
cost bound, all-size compilation, or kappa result is added. Required provenance
credits remain with PR370's word/exporter, PR386's geometry, PR442's hosting,
PR540's literal-invocation proof and PR1231's pending-schedule work. The user
initiated and coordinated this AI-assisted effort and does not claim to have
independently derived or personally checked its mathematics.
