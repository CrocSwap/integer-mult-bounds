# Conditional complete-bank endpoint adapter

This package contributes one theorem, `CurrentMain.PR516CompleteBankEndpoint.full_state_endpoint`. It applies PR516's `LemmaA.family_endpoint` and `LemmaA.endpoint_indep` to supply the universal bank/rest endpoint premise used by PR513's `SequentialCompleteBank` interface. Existing Mathlib `Equiv.funSplitAt` supplies the exact full-state split. No realization or sequential-composition induction is repeated.

## Author-checked κ context

For pinned main `12a4934d15006e8c10f9b2264f13f8f341be802b`, the retained conditional construction has

`κ = 90446448750933 / 125000000000000000 = 0.000723571590007464`.

The rational, decimal, and selected certificate field were checked for exact equality. `KAPPA_CONTEXT.json` identifies both source hashes. This is unchanged conditional source context; this adapter does not derive a new κ or prove an end-to-end multiplication bound.

## What is proved

For every initial helper-bank value and every initial value of all other physical families, the completed word produces the stated helper operator and a rest evolution independent of the initial helper value. The helper result comes from the complete scalar unit row. Rest independence separately uses the zero off-diagonal helper column.

The definition of the rest evolution evaluates a reference helper value of zero. The proof establishes the same rest output for every actual helper value; it assumes no clean helper or clean rest.

The following remain explicit hypotheses:

- injectivity of the owner map for all local registers;
- the actual complete physical-word execution equality;
- exact recipes and well-labelled events;
- the complete helper unit row and zero off-diagonal column, including the work register;
- the helper operator's identification with the chosen bank step.

To use the selected complete-bank theorem, the caller must additionally supply the common-chart partial-swap identification, all-60-replica partition, actual sweep order, global boundaries and physical costs. A projected scalar checker that omits the work input column cannot by itself supply the full-register premises.

## Coverage and recorded check

- One new Lean source and one new theorem; eight unchanged/relabelled dependencies.
- Nine local modules are current. The new root passed in 3.057048 seconds, with 2,297,208,832 bytes peak virtual memory.
- Three complete axiom probes cover the adapter and both reused endpoint results. Each uses only `propext`, `Classical.choice`, and `Quot.sound`.
- No new selected finite witness, physical word, census or matrix computation was run.
- No selected full provider or full multiplication theorem is claimed.

`CHECKED_BOUNDARY.json` records the accepted local check. A separate fresh isolated nine-source public replay passed with all 70 expected complete standard-only probes. It used 19.3728 compiler seconds and 0.00412 FIFO seconds, with 3,301,359,616 bytes peak VM. 8 object hashes match research; the public notice-modified Realize object is separately recorded. All full logs match after normalizing warning source paths. See REPLAY_SUMMARY.json for exact receipts and comparisons.

## Dependencies and reproduction

The package includes only the new endpoint source. `DEPENDENCIES.json` pins eight reused source inputs from exact PR509, PR516 and PR513 versions, plus Lean 4.21.0 and the Mathlib commit. Upstream realization and earlier sequential machinery retain their authorship.

Provide source directories for the three pinned packages, then run:

```sh
python stage_dependencies.py --pr509 /path/to/e8-lemma-g-lean \
  --pr516 /path/to/e8-lemma-a-lean \
  --pr513 /path/to/lean-sequential-bank-bindings \
  --output /path/to/fresh-build-sources
```

This offline command validates all nine source identities and stages the recorded compile order. It replaces `import LemmaG.Stream` with `import PR509Stream` in the staged upstream Realize file and inserts an ordinary comment adjacent to that import identifying that adaptation and the upstream pin. Removing only this comment recovers the accepted local alias source byte-for-byte; all upstream declarations and proofs are unchanged. It never renames an object, downloads a dependency, runs a compiler or skips a source-hash check.

Use the existing built Lean/Mathlib dependencies at the pinned versions. Compile the staged sources in `STAGED_SOURCES.json` order with the staged directory on `LEAN_PATH`; include the existing Mathlib and required Lake-package library paths. The recorded check used 60-second/4-GiB hard limits and 45-second/3.5-GiB review stops per source. Any future packaged replay must record its own results rather than adopting the local receipt as a fresh replay.

## Bounded offline package checker

The source-only staging command above is optional. For a fresh isolated nine-source reproduction, use the package checker directly with the same exact upstream source worktrees and an already-built pinned Lean/Mathlib runtime:

```sh
python3 check.py --lean /path/to/lean-4.21.0-linux/bin/lean \
  --mathlib-root /path/to/mathlib4 \
  --pr509-root /path/to/PR509/research/e8-lemma-g-lean \
  --pr516-root /path/to/PR516/research/e8-lemma-a-lean \
  --pr513-root /path/to/PR513/research/lean-sequential-bank-bindings \
  --build-dir /path/to/new-empty-reproduction-directory
```

The checker verifies all nine original/staged source identities, the documented reversible Realize import-and-notice transformation, and all 2,213 existing runtime source/object pairs before admission. It copies only those staged sources into a fresh source directory and compiles into a separate fresh object directory. The search path contains that output and eight explicit cache paths; inherited Lean paths/sysroot are ignored. It expects 70 complete standard-only probes across the nine files; the unchanged upstream Stream and Realize sources print none. The optional --slot-service argument shares an existing FIFO admission service and changes no Lean input. It downloads nothing, does not compile Mathlib, and stops at the first failure or review threshold.

The fresh package replay is complete. REPLAY_SUMMARY.json records its nine separate compiler checks and the public Realize source transition; the older accepted local receipts remain available in ACCEPTED_CHECKS.json.
