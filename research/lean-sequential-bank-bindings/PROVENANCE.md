# Provenance and claim boundary

## Exact selected source

Repository: `CrocSwap/integer-mult-bounds`

Selected commit: `12a4934d15006e8c10f9b2264f13f8f341be802b`

All paths in this section are repository-relative.

| Source | SHA-256 |
| --- | --- |
| `certificates/selected-result.json` | `df836c6d34509e980d067bd5678489c968bc6e329af9dd82c6207abf6443da89` |
| `research/community-pr279-audit/certificate.json` | `6a457a34b4db57417e5b253cf1c169da2bd6aff4c21363a31fd85dc931d49589` |
| `research/five-stage-gen4-banks/MANIFEST.json` | `99e202d9ffe5baf89e02796edbfc7095b2b227622eccf7b61afa01fd61aeb385` |
| `research/five-stage-gen4-banks/BANK-PROOF.md` | `bbc328e05848a211c981288514380a4ba12fddaed16c9d23328b5764502be411` |
| `research/five-stage-gen4-banks/bank_template.py` | `ca97c34524b409621336c0d4046f26e8da156f4b657c9d94463d8025ddfdbb4a` |
| `research/five-stage-gen4-banks/code/global_lowering.py` | `12e89150ef633d027d842378caa113a8240225d3dfdaac5177448c061e126206` |

The rational and decimal κ literals in README were checked for exact equality against the selected-result source. The source calls its result a maintainer-reviewed conditional construction. Neither this package nor that attribution converts the retained conditions into a full formal multiplication theorem.

## Attribution

`BANK-PROOF.md` describes a finite allocation extension of the PR197/PR200 completed-bank construction to PR234's five-stage bit geometry, retained from eumemic's source527 package and applied to the gen4 helper census. Its notice credits OpenAI Codex assistance for source527 and Claude assistance for the gen4 numerical rebinding.

`code/global_lowering.py` retains its attribution to Henry Grant / hcg890's PR234 code and records its source-bound adaptation. `bank_template.py` carries its Codex-assistance notice. These notices must be retained wherever the corresponding source is redistributed. The inspected package declares Apache-2.0 licensing; the package license and applicable notices should accompany redistribution.

The five supporting Lean files are reused unchanged from the retained local proof development. Their source headers, including historical source-pin descriptions, are preserved. Their theorems are parameterized; those historical descriptions do not identify the new selected finite matrices or tables.

The three added files provide a sequential composition adapter, an exact address-factor adapter, and the selected source-literal lowering/schedule definitions. They reuse existing routing, group, conjugation, partition and list results. The upstream Sussman / PR397 / PR430 generic chain and physical-stage machinery is prior work; no authorship or novelty claim for it is made here, and it is not imported into this small core-only closure.

## Verification scope

The eight source modules are currently kernel-checked under Lean 4.21.0 through the two recorded root closures. BankRouting was rebuilt once and shared. This fact is distinct from a new combined import-root measurement or a fresh packaged replay; any packaged replay report should describe its own observed result.

The three new modules expose 15 axiom probes. Their accepted checks use only ordinary Lean foundational axioms; no `sorry`, `admit`, new axioms or `native_decide` is introduced. Supporting-module probes remain part of the supplied replay evidence.

The source-literal comparison was made against exact captured files and method spans. No Python provider execution, finite chart replay or all-entry census check was performed to establish that comparison. The actual local record list is still an input. In the selected Python caller, the global lowerer receives the record list after the physical producer, parity transformation and descent transformation; substituting the raw producer list alone would not bind the selected word.

The canonical block-swap address-column check described by the source is separate from the full local physical word's arbitrary-joint-state endpoint. The latter is an explicit premise of `sequential_complete_bank`, along with the exact common chart and reversed-list partition. No counterexample to the selected source is asserted by maintaining this boundary.

The bit source uses dimension 120, local dimension 24, 1760 ports, five stages and 60 physical replicas. This package does not instantiate the complete finite GL120 cover, build actual normalizers, prove the census/partition, eliminate the completion rows, identify boundary operators, or certify costs. The current complex110 source and historical concrete proof families are separate reconciliation targets.

## Isolated package replay

The flat eight-source package was independently compiled offline with the bundled checker and Lean 4.21.0 into a fresh output directory. `REPLAY_SUMMARY.json` records the exact source, checker, object, receipt and axiom identities and the measured resources. All eight object hashes match the prior accepted checks; all 77 complete theorem/axiom outputs match after whitespace normalization. This replay adds no physical-provider or end-to-end construction claim.
