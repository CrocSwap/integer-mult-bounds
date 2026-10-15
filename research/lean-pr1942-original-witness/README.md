# Original-witness completeness and the PR1942 envelope

This package publishes four unchanged, independently accepted Lean 4.21.0 sources. Three are reusable finite-dimensional checker/completeness results. One is a conditional application to the original L450 entry of PR1942.

Author-checked source context: κ = 836330098538459/500000000000000000 = 0.001672660197076918, at selected main revision 299eb8effe080183313757ac36e76c1b98ed9fae. The generic theorems do not depend on or change κ. This is not a proof of the full multiplication theorem.

## What is proved

- `BoundedChartWitnessCompleteness` keeps the original bounded forward and inverse tables, packed columns, update bits and coefficient bits. The existing table/scalar checks derive acceptance of those original five arrays, through both Value and Lean.Json AST interfaces, including dimension zero.
- `JsonChartWitnessEnvelope` executes the actual PR1942 `format`, `dimension` and `entries` checks. It selects the same named key as the source dictionary and invokes the unchanged `certifyEntry` checker on the selected five-array AST. Successful execution yields the original field equations and the existing operator/inverse result.
- `JsonChartEnvelopeCompleteness` derives that wrapper's success from the two original witness checks and five explicit field equations. Desired downstream execution is no longer a premise.
- `PR1942L450OriginalWitness` kernel-identifies the five original arrays for one source-matched entry. Four small ordered Nat-list decisions identify the forward, inverse, update and coefficient arrays; the 73 columns reuse the accepted typed-value theorem. Candidate equality transports the existing scalar certificate, so no scalar census is repeated. `envelope_success` then applies the generic join.

The exact success endpoint, all 16 axiom probes and all seven printed theorem types are in `ACCEPTANCE.json`. The four roots have no diagnostics and use only the standard axioms listed there. Their exact accepted source hashes determine this claim; earlier failed attempts remain preserved separately. The exact four source files contain no historical UNCOMPILED or pending status labels.

## Source and coverage boundaries

The original upstream witness is Adam Gall's PR1942 at c7d8c9febf0fcc52d2002db657165cd206ff9cec, `research/selected-sigma-chart-binding/WITNESSES.json.gz`. The selected entry key is `ccf973ede5baca87618c361e2fe62bb8a80f11b79f1551237ab7a16c887b4e90`. `L450_ENTRY.json` preserves its exact 1,627-byte five-array excerpt; each array has 73 entries. `ARTIFACT_PROVENANCE.json` records the original compressed/decompressed identities and byte interval. Only this one entry was inspected and source-matched. No Python verifier or full witness census was run for these proofs.

The final L450 theorem still takes the exact format, dimension, entries, selected certificate and source-column AST field equations. This package does not construct the whole original file's AST or prove its parser equations. Lean.Json's opaque logical parser is not identified with an external or runtime parser result. The source excerpt mapping is independently source-reviewed; it is not a Lean filesystem or parser-span theorem. Hash records support exact identity checks and do not authenticate an artifact supplier. General duplicate-key/lexical policy, physical execution, complex phase and cost remain separate.

## Reuse and reproduction

Only four sources, totaling 26,633 bytes, are new here. The minimal accepted import closure uses 94 immutable public prerequisites, including the exact `Current1094L450FragmentData` published in PR2371. None is copied into this package. The one inherited import-renaming recipe is explicit in the manifest.

`PUBLIC_SOURCE_MANIFEST.json` gives all public source paths, revisions, raw/derived hashes and topological order. `REPRODUCTION.md` gives prospective hash-checked, serial, bounded commands for either four roots with verified retained predecessors or the complete 98-module public research closure. No compiler, dependency installation, parser diagnostic or archive extraction was run during this publication preparation. Setup or recovery requires separate authorization.

Credits: Adam Gall with OpenAI assistance for the PR1942 witness producer and audit; Rohan Arun for PR1094; Jeremy Kothe for T16/PR514; James Chang with OpenAI assistance for the paired bank/frame Lean work; Lean and Mathlib contributors. Existing source attribution and Apache-2.0 declarations are retained.
