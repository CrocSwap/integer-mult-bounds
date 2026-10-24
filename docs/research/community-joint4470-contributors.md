# Joint-helper checkpoint: contributor map

Prepared October 22, 2026 for the selected conditional κ = 0.00302015.
This map credits construction, enabling work and adversarial verification
separately. It does not assert priority over parallel work or validate every
claim in the linked submissions. Source notices remain unchanged.

| Contributor | Contribution | Sources |
| --- | --- | --- |
| **Cinna Davis / 1337isnot1337** | Joint helper boundaries, fresh-helper thinning, query-thinned controllers and their cumulative construction; the preceding p7 improvement. | [#4470](https://github.com/CrocSwap/integer-mult-bounds/pull/4470), [#4447](https://github.com/CrocSwap/integer-mult-bounds/pull/4447), [#4441](https://github.com/CrocSwap/integer-mult-bounds/pull/4441), [#4440](https://github.com/CrocSwap/integer-mult-bounds/pull/4440), [#4416](https://github.com/CrocSwap/integer-mult-bounds/pull/4416) |
| **zxv** | Productive-helper/native construction and explicit compiler underlying the checkpoint, plus the higher-moment compiler used in its predecessor. | [#4359](https://github.com/CrocSwap/integer-mult-bounds/pull/4359), [#4433](https://github.com/CrocSwap/integer-mult-bounds/pull/4433) |
| **Jacob Alan Sussman** | Mixed-target recursion underlying the compiler; his original result concerns DFT bounds, not this multiplication κ. | [#4268](https://github.com/CrocSwap/integer-mult-bounds/pull/4268) |
| **Mihir Srivastava / mihir-s-05** | Independent joint-frame audit and stage-zero commutation audit, replayed in the selected verification. | [#4504](https://github.com/CrocSwap/integer-mult-bounds/pull/4504), [#4464](https://github.com/CrocSwap/integer-mult-bounds/pull/4464) |
| **Ryanson (Ryan) Jonathan / pinterbanget** | Independent arithmetic and forced-translation audits, replayed in the selected verification; earlier compiler audits remain credited. | [#4478](https://github.com/CrocSwap/integer-mult-bounds/pull/4478), [#4466](https://github.com/CrocSwap/integer-mult-bounds/pull/4466) |
| **Mark / Matarener** | Stage-zero commutation question and adversarial example that motivated explicit scoped resolution. | [#4457](https://github.com/CrocSwap/integer-mult-bounds/pull/4457) |

The [preceding contributor map](community-productive4359-contributors.md)
retains the cumulative lineage, including Rohan Arun, David Ganz, Jeremy Kothe,
Marius-Paul Dumitrean, Erwan Secousses, Chafik Boukhalfa, Zhihao Chen, Vlado-V,
eumemic, DreamingOfClouds and the broader construction, verification and
formalization community. See also [CONTRIBUTORS.md](../../CONTRIBUTORS.md).
Douglas Colkitt maintains this integration, with substantial OpenAI Codex assistance.

The [review](pr-intake-evidence/pr4470/PROOF-REVIEW.md) distinguishes newly
replayed identities from exact-source prior evidence. The
[integration receipt](pr-intake-evidence/pr4470/INTEGRATION.json) records the
selected migration. These finite checks retain the inherited theorem assumptions;
they are not a Lean proof or a full independent verification of integer multiplication.
Later compiler-size proposals #4483 and #4507 are separate from this selection.
