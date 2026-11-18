# Attribution and source pins

Ali Romman prepared this bridge-family proof and its checks with substantial
OpenAI Codex assistance. New work is Apache-2.0. This is not an independent
review of the consumed source proofs.

Ali Romman's [PR #7707](https://github.com/CrocSwap/integer-mult-bounds/pull/7707),
head `57e24923b609d2588b83321f530fa2a1e75ed364`, supplies the
[two-link construction and complete-pool exception](https://github.com/aliromman/integer-mult-bounds/blob/57e24923b609d2588b83321f530fa2a1e75ed364/research/edge-matching-even-attainment/PROOF.md).
That geometry and its image maximum remain prior results. The new result
concerns paid words on the named alphabet and its stated family extension.
The sixth projector and other
maximizing pools remain outside this theorem.

Ali Romman's [PR #7695](https://github.com/CrocSwap/integer-mult-bounds/pull/7695),
head `996c002d82420141c19797e4e3b699ed88aee330`, supplies the
[Boolean diagonal partition, augmentation method and target matching](https://github.com/aliromman/integer-mult-bounds/blob/996c002d82420141c19797e4e3b699ed88aee330/research/orthogonal-basis-bridge-obstruction/PROOF.md).
Its [checker](https://github.com/aliromman/integer-mult-bounds/blob/996c002d82420141c19797e4e3b699ed88aee330/research/orthogonal-basis-bridge-obstruction/verify.py)
supplies the adapted binary matrix, exact rank, degree-two and Laurent
routines. The partition, exponent allocation, endpoint and census code
is adapted to a variable number of bridge types and both parities. Source code is copied
into this self-contained checker; no predecessor module is imported.

The new proof computes the exact bridge-family star kernel, separates the
independent bridge-variable sets, and removes all collected blocks
from the full endpoint. Mutual commutation permits literal interleaving;
the one-bridge consecutive-block conclusion is not asserted here.

The original chronology and Laurent methods are CubeJerry's work in
[PR #6782](https://github.com/CrocSwap/integer-mult-bounds/pull/6782),
head `685457252b51b9c7932ece363365bdf0b12c9c31`:
[five-core proof](https://github.com/CubeJerry/integer-mult-bounds/blob/685457252b51b9c7932ece363365bdf0b12c9c31/research/bit-three-relation-core/FIVE-CORE-WORD.md)
and [original Laurent recurrence](https://github.com/CubeJerry/integer-mult-bounds/blob/685457252b51b9c7932ece363365bdf0b12c9c31/research/bit-three-relation-core/independent_five_word.py).
Ali Romman's [PR #7694](https://github.com/CrocSwap/integer-mult-bounds/pull/7694),
head `96b8b22f5925c4cf4514ed27575f465ebc95e51a`, supplies the
[edge-family extension](https://github.com/aliromman/integer-mult-bounds/blob/96b8b22f5925c4cf4514ed27575f465ebc95e51a/research/extremal-core-word-obstruction/PROOF.md)
used by PR #7695. Its contribution remains prior work.

The [retained geometric credits](https://github.com/aliromman/integer-mult-bounds/blob/57e24923b609d2588b83321f530fa2a1e75ed364/research/edge-matching-even-attainment/CREDITS.md)
identify unpaidmoon's normal triples and alternative dimension-five pool,
Nick Petalas's links and one-edge bound, and the earlier pattern-fiber
work. Those geometric results are not counted as new here. Douglas
Colkitt and the repository contributors supplied the research framework,
task catalogue and package tools.

SOURCES.json binds the main-branch provenance at
`e54523517d0f03e58352e647c403a5af3e525a57`. The unmerged consumed proof
and code commits are explicit above; they are not represented as
ancestors of main. Their complete replay suites were not rerun.
