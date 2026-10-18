# Concrete Lean label certificates for the selected k8 programs

This package translates both complete selected k8 local programs into the
retained `LemmaG.Event` grammar and checks their label admissibility in Lean.
Each source stream has 24,767 serialized events. Only its ten phase markers
are omitted, leaving 24,757 formal events per orientation.

The target theorem is `Stream.WellLabelled`, with the exact final labels
proved by `Stream.labRun` as a separate conclusion. This is the concrete H1
instance requested after Sagar Thakrar's [PR1964](https://github.com/CrocSwap/integer-mult-bounds/pull/1964) Python audit. Generic
COPY/CLEAR semantics and conjugation already exist in Lemma G; this package
does not claim them as new results.

## Source and formal boundary

The source-bound rebuild reuses Hanson Sun's [PR1611](https://github.com/CrocSwap/integer-mult-bounds/pull/1611) regeneration driver and
its pinned transport, emitter and wrapper producers. Both complete event
streams must match the selected slot hashes. Every non-phase event is
translated in its original order, with exact rational coefficients.
[SOURCES.json](SOURCES.json) pins all consumed predecessor files.

The mapping follows PR1964's written extended-label specification:

- Climbs and centre steps become `relabel` events in the ordinary frame family.
- Source entry and target exit adapters cross explicit per-register tags.
- Pre/post helper wrappers cross per-register `prew` and `done` tags, including
  all 48 cold hyperplane-ended helpers.
- ADD, SCALE, COPY and CLEAR use the retained formal constructors. COPY requires
  its source label and overwrites the private label; CLEAR resets the label to
  its stated ordinary frame. The strict CLEAR interpretation is used.

Labels encode tag, owner and frame injectively in a bounded numeric domain.
The register type is `Fin 1024`, embedding the actual 704 local and eight
private registers without aliasing. The other 312 registers remain unused,
with label zero. All initial scalar contents remain arbitrary in the generic
conjugation theorem. Assigning an initial private label does not assume its
contents are zero. This package proves label evolution, not private scalar
restoration or a storage allocation theorem.

`TreeCheckpoint.lean` proves that its balanced-tree checker implies the
existing `Stream.WellLabelled` and `labRun` definitions. A compositional
`Chain` theorem joins adjacent checked blocks. The generator emits 97 blocks
per orientation, with at most 256 events each, and explicit shared boundary
states. The four final theorem roots refer to the complete flattened words.
Every block is checked with `decide +kernel`; `native_decide` is not used.
Generated Lean files live in a temporary directory instead of adding several
megabytes of literals to this repository.

The Python/JSON adapter and source parser are outside the formal proof.
`KERNEL.json` binds the generated source hashes, formal checker, generator,
translation and all predecessor input hashes. The default Python replay
regenerates those exact Lean sources and checks that binding, without a fresh
Lean build. A source change therefore requires a new formal receipt.

## Reproduce

Use Python 3.12 and the standard library on a POSIX host. From the repository root:

```sh
uv run --python 3.12 --no-project python -B scripts/research_package.py \
  --package research/k8-lean-label-instance
```

For the formal replay, prepare the existing `formal/lean` Lake project with
Lean 4.21.0 and Mathlib v4.21.0, revision
`308445d7985027f538e281e18df29ca16ede2ba3`. Its dependencies and compiled Mathlib
imports must already be available. Then run:

```sh
uv run --python 3.12 --no-project python -B \
  research/k8-lean-label-instance/check_lean.py --lake-project formal/lean
```

The formal driver rebuilds the pinned `Stream.lean`, new checker and both
concrete words from source in fresh temporary directories. It audits live
axiom reports and rejects a false relabel theorem. Only `propext`,
`Classical.choice` and `Quot.sound` are allowed. Imported Mathlib objects and
the compiler installation remain in the trust base. Compiler platform strings
are recorded as environment metadata, rather than compared as proof data.
The driver requires POSIX process groups, uses one compiler at a time and
bounds each invocation to 180 seconds.

`verify.py --write-result NEW_PATH` and
`check_lean.py --write-receipt NEW_PATH` create separate receipts and refuse to
overwrite files. Normal checks do not rewrite committed evidence.

## Evidence and limits

`RESULT.json` records both translation digests, constructor counts, final label
boundaries and ten rejected semantic controls. They remove source adapters or
pre-wrappers, change private COPY/CLEAR frames, or change climb/wrapper frames.
The focused tests cover each constructor, tag and coefficient boundaries,
private overwrite/reset behavior and typed receipt comparison.

Two separate read-only reviews checked the Python translation and formal
checker/generator. The latter independently parsed every generated event and
all 98 checkpoint states per orientation. Neither review is independent human
review. `KERNEL.json` records the actual formal replay; local execution and
hosted CI are separate.

This proves a concrete label instance for the translated words. It does not
prove the adapter's semantics, exact serialized operator recipes,
`RecipesExact`, scalar helper rows/columns, the generic operator-to-physical
interpretation, footprints, hosting, the all-size compiler, precision/tape,
complete cost or analytic transfer. No complete selected cold replay or
supplier admission is performed. The selected record and kappa are unchanged.

## Open next questions

Join this concrete label instance to exact operator recipes and the selected
scalar endpoint in one formal theorem. Start with helper 450 and the explicit
label operators in PR1964. The missing serialized-recipe and Python/JSON
semantic correspondence blocks that conclusion. More label examples do not
remove it. The structured question and claim are in [TASK.json](TASK.json).

## Credit and engineering decisions

Nick Petalas contributed this package with substantial AI assistance in
investigation, implementation, checking and prose. No independent human review
is claimed. New work is Apache-2.0; predecessor source notices are unchanged.

Credit Sagar Thakrar/PR1964 for the extended-label specification and Python
instance audit; Hanson Sun/PR1611 for helper 450's binding and regeneration
driver; DreamingOfClouds for Lemma G/A and its COPY/CLEAR formal semantics;
Jeremy Kothe for HPE and the selected k8 lineage; icekylinx for the retained
compiler; Rohan Arun for selected packing; Josie Elliston, Ali Romman and
Sagar Thakrar for the retained word/audit lineage; and Chafik Boukhalfa,
Zhihao Chen and the other credited realization contributors. Nick Petalas's
PR2748 supplies the nearby non-cold wrapper event binding. None of those
predecessor results is claimed as new here.

The Build the Lever principle led to a deterministic generator and replay
instead of hand-maintained event literals. Prove It Works requires fresh
formal compilation and live axiom reports before claiming the concrete result.
Laziness Protocol kept the existing event semantics and confined the addition
to the concrete instance and its checker.

Power-of-Ten deviations are bounded to this research tool. Managed Python/Lean
runtimes allocate dynamically; inputs are pinned, events are capped at 25,000,
registers at 1,024 and blocks at 100 per orientation. Lean recursion in the
proof/checker is structural: tree depth 10, a generated block at most 256 events,
and a chain of 97 blocks. Replacing these proof recursors with imperative code
would enlarge the semantic bridge. The controls and kernel replay check the
bounded use. Reassess capacities and proof evaluation before extending the
domain. Imported Mathlib diagnostics and allocation are outside this package;
new Python code is checked with Ruff E4,E7,E9,F,B,I,UP, and fresh Lean compilation
treats warnings as errors. The standard-library replay also treats Python
warnings as errors. Ruff is a local preflight; a shared pinned Ruff CI
environment remains outside this proof package and can be adopted when the
repository provides one. The initial vector-state prototype was discarded
after excessive kernel memory use; no vector prototype is retained here.
