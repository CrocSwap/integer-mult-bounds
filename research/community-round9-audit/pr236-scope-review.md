# PR236: theorem scope review

Pinned PR236 head: `f825b6fdfd763f189db3aa1c02fdd5d604c85a01`. This note reviews the readable principal theorem statements and the offline driver. The complete accepted-set rebuild and final receipt audit have now passed; see `pr236-final-integrity.json`.

## What the statements establish

- `FullCoefficientIdentity.actual_combined_coefficients` quantifies over all 1,760 targets and proves equality of complete integer coefficient vectors. It uses bounded radix injectivity with explicit coefficient bounds, not equality of hashes. The coefficient graph, readout and correction terms are concrete imported data.
- `FullActualIdentity.actual_source_matrix_fresh_response` quantifies over arbitrary integer payloads and proves that the decoded actual word plus the actual input correction gives six times the payload at every target.
- `FullActualIdentity.actual_source_matrix_dirty_response` quantifies over arbitrary initial workspace, payload and target states. The displayed subtraction/correction expression yields the required target update. The identity alone does not price the implementation of those corrections or establish the global tape layout.
- `AssemblySummary13955` and `AssemblyCoreLink13955` connect the source-derived slack/margin expressions to exact integer-pair arithmetic, link the core parameters, and preserve κ=4609169/10^10. They do not prove that every analytic/compiler interface giving rise to those inequalities holds.
- `PreparedSequentialRootEvent` is a local event theorem over a supplied field/table interface with stated hypotheses. It is not a concrete uniform rational/Gaussian realization or all-size multiplication construction.
- `SequentialRootScratchBoundary` proves local traffic and restoration properties while explicitly proving an obstruction: both resident scratch and the original spill bank are restored by the displayed wrapper only under the appropriate bank equality. Its `unequal_banks_obstruction` must not be advertised as a global dirty-workspace restoration theorem.

## Execution and trust boundaries

The source map and hashes bind the imported finite data and expected audit names. The driver requires exact source/import/audit-command matches, invokes the pinned official Lean4.21.0 compiler, checks the resulting declaration axiom reports, and limits permitted transitive axioms to `propext`, `Quot.sound`, and `Classical.choice`. Resume binds source, dependency object, compiler, object and log identities. Installed standard-library correctness and executable source extraction/provenance remain stated trust boundaries.

The original Darwin resource policy fails at `RLIMIT_AS`. Our saved adapter omits only that unsupported address-space limit, retaining compilation, source checks, timeouts and axiom audits. It must not be described as a Linux run under the advertised memory cap. Its historical policy identifier includes `subset`; that identifier was retained unchanged when launching the full accepted-set build and does not itself prove which modules ran. The terminal build summary and revalidated complete receipts establish the full accepted-set scope.

The package itself correctly disclaims a complete asymptotic integer-multiplication theorem. The successful full rebuild validates the submitted finite formalization under these boundaries; it does not close the real-logarithm/exponential, concrete field/operator realization, physical-word/readout composition, restored-row/tape-cost or all-size reduction gaps.
