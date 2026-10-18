# Provenance and reuse boundary

The contribution is the single source `PR516CompleteBankEndpoint.lean`, SHA-256 `d999cff3a33169fa5ce72576181921f530d0174ac8bd6546c0953bcb5c13e747`.

It applies the following upstream results rather than reproving them:

- PR516, exact commit `1c6b6ff9366a94e1f86a6c5d661a7df75c6ff814`: `LemmaA.family_endpoint` and `LemmaA.endpoint_indep` from `research/e8-lemma-a-lean/LemmaA/Realize.lean`, upstream SHA-256 `3aa9afd36035afd94296ef410c647d5a8c6fb282f64062542c7070bb1d99a14f`. All nine declaration/proof blocks are unchanged. The accepted local import alias has SHA-256 `39d6a1031f29b35c59b581ef5ed939aaa4b80b272df39dafc5608c76d2cf4d3f`. Public staging additionally inserts an ordinary modification notice adjacent to the import, yielding SHA-256 `648117b332f4c72a5a653e2ea1b0c2a82cf477f61a3ac64c3eecae8d65996f39`; removing that notice recovers the accepted source exactly.
- PR509, exact commit `7b9c720ecc9f483c383e7cd9c2ab81f06ee5df59`: the exact Stream source, SHA-256 `7138f4b859d0574a803e99401f05ef5e0ec9eeac0eb480775cd9b86595c365f8`, is reused under module name `PR509Stream`. Its source bytes and declarations are unchanged.
- PR513's initial published package source identity at `005dd3f4e3cba8d1761abc4ab391aaf6d14d6f73`: six unchanged support modules, individually pinned in `DEPENDENCIES.json`. Its address and literal-stage modules are not needed by this minimal endpoint closure.
- Mathlib commit `308445d7985027f538e281e18df29ca16ede2ba3`: the existing `Equiv.funSplitAt` state equivalence.

PR516 was prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code, under Apache-2.0. Its complete NOTICE is retained as `PR516-NOTICE.md`; the corresponding PR509 NOTICE is retained separately. Those notices credit the relevant predecessor constructions and event semantics. The upstream realization theorem is not presented as a contribution of this adapter.

No blanket novelty claim is made for the generic algebra. The added work is the exact interface connection: full helper and rest conclusions, a complete-state split, and the universal pair-valued premise expected by the already accepted sequential interface.

The κ context is the captured main-12a4934 conditional selected result, not a new value inferred from this proof. Actual source execution, owner/chart suppliers, full scalar rows and columns, common-chart identification, the complete replica partition, boundaries and costs remain open inputs. PR516's other modules and numerical instance checkers are outside this nine-module closure.

## Public reproduction

A fresh isolated nine-source replay of these exact public bytes completed successfully. All 70 expected complete standard-only probes match. The public Realize source includes the documented ordinary modification notice; its measured object is recorded separately rather than assumed equal to the research object. REPLAY_SUMMARY.json (SHA-256 `bda3d90054646b89d5d598f01c0cbe5e4f52ff1062fdd829a23a1d57bb286aa1`) records all resources, source/object/receipt hashes and comparisons. No scientific statement or dependency scope changed.
