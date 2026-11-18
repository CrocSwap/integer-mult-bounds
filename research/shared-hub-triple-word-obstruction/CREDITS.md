# Attribution and exact sources

Ali Romman prepared the new commutator lemma, word classification, full
endpoint argument and checks with substantial OpenAI Codex assistance.
New work is Apache-2.0. This is author-checked work, not independent
review of the consumed source proofs.

Ali Romman's [PR #7707](https://github.com/CrocSwap/integer-mult-bounds/pull/7707),
head `57e24923b609d2588b83321f530fa2a1e75ed364`, supplies the
[exceptional six-projector pool](https://github.com/aliromman/integer-mult-bounds/blob/57e24923b609d2588b83321f530fa2a1e75ed364/research/edge-matching-even-attainment/PROOF.md).
The pool, its irreducibility and geometric maximum remain prior results.
The [retained geometric credit chain](https://github.com/aliromman/integer-mult-bounds/blob/57e24923b609d2588b83321f530fa2a1e75ed364/research/edge-matching-even-attainment/CREDITS.md)
identifies unpaidmoon's normal triples and different dimension-five
attainer, Nick Petalas's links and one-edge bound, and earlier pattern-
fiber work. Those results are not new here.

Ali Romman's [PR #7710](https://github.com/CrocSwap/integer-mult-bounds/pull/7710),
head `c396e9ee03b331f3b46aa87526817b237f5ad6f8`, gives the
[bridge-family obstruction and explicit sixth-projector exclusion](https://github.com/aliromman/integer-mult-bounds/blob/c396e9ee03b331f3b46aa87526817b237f5ad6f8/research/orthogonal-bridge-family-obstruction/PROOF.md).
It provides the open question. Its separate-bridge argument does not
prove the result here. The added projector changes the linear relations
to common totals within each triple.

Ali Romman's [PR #7695](https://github.com/CrocSwap/integer-mult-bounds/pull/7695),
head `996c002d82420141c19797e4e3b699ed88aee330`, supplies the prior
[augmentation and paid-subset argument](https://github.com/aliromman/integer-mult-bounds/blob/996c002d82420141c19797e4e3b699ed88aee330/research/orthogonal-basis-bridge-obstruction/PROOF.md)
and the [binary, rank, degree-two and Laurent primitives](https://github.com/aliromman/integer-mult-bounds/blob/996c002d82420141c19797e4e3b699ed88aee330/research/orthogonal-basis-bridge-obstruction/verify.py)
adapted in this checker. These routines are copied into the self-contained
package. No predecessor module is imported. The new allocation, chronology,
full-endpoint fixtures and controls concern the six-member pool.

The original chronology and Laurent methods are CubeJerry's work in
[PR #6782](https://github.com/CrocSwap/integer-mult-bounds/pull/6782),
head `685457252b51b9c7932ece363365bdf0b12c9c31`:
[five-core word proof](https://github.com/CubeJerry/integer-mult-bounds/blob/685457252b51b9c7932ece363365bdf0b12c9c31/research/bit-three-relation-core/FIVE-CORE-WORD.md)
and [original recurrence](https://github.com/CubeJerry/integer-mult-bounds/blob/685457252b51b9c7932ece363365bdf0b12c9c31/research/bit-three-relation-core/independent_five_word.py).
The nonzero-even-total control is an adaptation of that prior distinction,
not a newly discovered need to check exact exponents.

The consumed PR #7695 also retains Ali Romman's
[PR #7694](https://github.com/CrocSwap/integer-mult-bounds/pull/7694),
head `96b8b22f5925c4cf4514ed27575f465ebc95e51a`, and its
[edge-family proof](https://github.com/aliromman/integer-mult-bounds/blob/96b8b22f5925c4cf4514ed27575f465ebc95e51a/research/extremal-core-word-obstruction/PROOF.md).
Douglas Colkitt and the repository contributors supplied the framework,
task catalogue and package tools.

SOURCES.json pins main-branch provenance at
`e54523517d0f03e58352e647c403a5af3e525a57`. The unmerged proof and code
sources are pinned separately above. They are not represented as
ancestors of main. Their full replay suites were not rerun.
