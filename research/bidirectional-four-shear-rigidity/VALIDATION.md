# Exercised validation

Environment: macOS 27.0.1 arm64; CPython 3.12.12 (Clang 21.1.4), selected with
`uv run --python 3.12 --no-project`. Standard library only. Base/worktree:
`e112d71c8d7bb32435debcc54df932593dd8223a`, isolated `research/round3-08`.
No full repository suite, selected cold replay, Lean build or CI triage was run.

## Commands actually completed

1. Assigned working example:

   ```sh
   uv run --python 3.12 --no-project python -B research/universal-connector-boundary/verify.py
   ```

   Output: `PASS_UNIVERSAL_CONNECTOR_BOUNDARY pairings=945 max_coverage=31 queries=74 leaves=182`.
   This is predecessor orientation, not a new result.

2. Final focused evidence generation and semantic smoke:

   ```sh
   uv run --python 3.12 --no-project python -I -B research/bidirectional-four-shear-rigidity/verify.py --record
   ```

   Output: `PASS_BIDIRECTIONAL_FOUR_SHEAR_RIGIDITY canonical_traces=69948 signed_traces=559584 mixed_successes=0 symbolic_shapes=16 no_new_kappa`.
   This generated the committed `EVIDENCE.json`. Observed wall time about 9.4 s;
   this is a replay receipt, not a measured optimization claim.

3. Final registered CPython 3.12 replay:

   ```sh
   uv run --python 3.12 --no-project python scripts/research_package.py --package research/bidirectional-four-shear-rigidity
   ```

   Outputs:

   ```text
   PASS_BIDIRECTIONAL_FOUR_SHEAR_RIGIDITY canonical_traces=69948 signed_traces=559584 mixed_successes=0 symbolic_shapes=16 no_new_kappa
   PASS_FOUR_SHEAR_PACKAGE_CONTROLS source_mutations=5 receipt_mutations=1 relocated_optimized=true read_only=true
   PASS_REGISTERED_RESEARCH_PACKAGE research/bidirectional-four-shear-rigidity outcome=negative-result
   ```

   Observed wall time about 29.1 s for both registered commands. The launcher
   checked base/catalogue/task/source metadata. The second command exercised
   optimized `-I -O -B` runs in a temporary relocated export, without Git or
   predecessor executables at runtime; its source root was explicitly supplied.
   The successful export's complete content inventory was unchanged. This is
   content-based read-only verification, not a filesystem permission claim.

## Exact coverage and sensitivity

- All sixteen direction shapes checked by exact polynomial identities. Eight
  three/one and two alternating mixed shapes fail restoration; four mixed
  inverse-excursion shapes reduce to one disjoint loop by the written central
  endpoint/cyclic-rotation argument. The two one-way shapes are predecessor work.
- Same-port cross-source/reader placements: 420 per ordered root pair, 236
  admitted per pair, zero nonzero cross terms. Dropping source restoration
  admits 18 nonzero cases per pair; dropping reader dirt admits 18 as well.
  These are polynomial calculations, not a finite coefficient sample.
- Exceptional loop: 90 source orders times 210 phase assignments. The two
  independent models agree on all 69,948 canonical source traces and their
  entire reader-row masks. Exactly 7,020 traces contain a source-port switch.
  Eight column-sign choices give 559,584 signed traces and zero target successes.
  The all-ones target is a positive control with 51,192 successful signed traces.
- Target row-availability histogram:
  `[298888,29656,29656,7008,165320,14528,14528,0]`.
  Canonical full record SHA256:
  `f8f48287c1503821f80007d798034c52cb9f46b18e3c8cb2bc83c0282b724b4c`.
- Credited one-way witness and both genuine port-switch pilots pass exact free
  noncommutative endpoint/inverse checks. All sixteen cyclic rotations of the
  one-way witness preserve its central endpoint. An independent block-array
  model checks 120 dirty basis columns total at dimensions two and three,
  including singular, noncommuting maps.
- Four individual missing-shear mutations fail. Wrong source restoration and
  identifying independent root dirt fail. Removing the dirt monomials makes
  the latter incorrect shortcut appear valid, isolating the intended failure.
- Each of five live input files is actually corrupted in a temporary export;
  every pin check rejects. Changing `target_successes` in the copied evidence
  is rejected after full recomputation. An unmodified relocated optimized
  replay passes without changing its file inventory.

## Overlap and boundaries

The shared cached snapshot searched at entry covered 329 open PRs including
 drafts and 692 discussions with complete pagination, fetched 2026-10-14 at
18:11:09.770757Z and 18:12:32.610168Z respectively. Offline cache warnings were
retained as freshness limitations, not treated as a novelty certificate.
Local integrated predecessors through PR2027 were inspected.

Targeted live reads confirmed PR1983 at
`9cb25cd2851fd4d4474abd515b63d721f5f370c7`, merged at 18:01:04Z, and the unchanged
PR1675/Discussion1660 four-pass handoff. Discussion1660 still had no comments
and update time 06:21:20Z at the pre-submission read. A targeted live PR search
also found the new PR2065 F2 five-source/six-transfer result; it has different
characteristic, target and budget and is not used here. Title/body searches do
not inspect every live diff and cannot establish universal novelty.

The proof's unbounded quantifiers depend on the written reductions in README,
not finite experiments alone. The residual census is exact and complete, but
not checked in a formal proof kernel. The distinct algorithms were written by
the same AI assistant, not independent humans. No full lowering of the
predecessor's recursive children, native physical realization, improved moment,
new selected kappa or hosted GitHub CI pass is claimed.

Prepared for Adam Gall with substantial OpenAI Codex assistance. Apache-2.0.
