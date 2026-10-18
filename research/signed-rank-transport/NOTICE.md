# Attribution, context and source pins

Prepared by Jeremy Diviney with substantial OpenAI Codex assistance in
research, proof, implementation and validation. New material is under the
repository's Apache-2.0 license. No independent human review, proof-assistant
formalization, maintainer endorsement or literature-priority claim is made.

Nir Ailon's [2014 conditioned Fourier-transform paper](https://arxiv.org/abs/1403.1307v5)
uses forward/inverse quasi-probabilities to extend an entropy potential beyond
unitary circuits. His [paraunitary follow-up](https://arxiv.org/abs/1609.03278v6)
connects Fourier complexity with algebraic conditioning. These supply the
mathematical inspiration. The present linear rank potential, formal group
coefficient identity, signed budget and diagonal-gauge corollary are derived
in PROOF.md; no theorem from those papers is imported into this model.

The complex register question and broader frame model are credited to
eumemic's [PR288](https://github.com/CrocSwap/integer-mult-bounds/pull/288),
head `475a088b5862f75f0b10596cfd6842d19531a5ec`, and its retained predecessors,
including Swapnil Jain's P1/P2 and upstream Clifford-frame work. PR288's
arbitrary-scalar m=2 results and m=3 open questions have different scope from
the scalar-unitary subclass excluded here.

littleBro's [PR680](https://github.com/CrocSwap/integer-mult-bounds/pull/680),
head `c3a5b6b7afec35d259c29bc2d8bb8516e975ad31`, supplies unchanged `model.py`
and `dense.py`, copied through [PR705](https://github.com/CrocSwap/integer-mult-bounds/pull/705)
head `eeb0cd605415a73b792915aaa9185000f293c84a`. Their exact hashes are in
ORIGINS.json. The inherited model and dense arithmetic were prepared with
substantial OpenAI Codex assistance. All runtime dependencies are local.

Our PR800's path-valuation criterion concerns fixed unary words with generic
scalar blocks. This result instead permits arbitrary unary words while
restricting scalar mixers, and quantifies the signed resource required when
that restriction is lifted. PR800 is not a runtime dependency.

Overlap checks queried the open/all PR queue for unitary, nonunitary,
Plancherel and quasiprobability work, inspected the returned PR401/496
construction summaries and refreshed metadata through PR833. They concern
supplier frame/gauge constructions, not this general transport argument.
PR825's common-flag obstruction is a distinct rational-frame XOR result in
characteristic two; it does not use the complex coefficient pairing here.
This was not an exhaustive literature or PR-diff review.

Base: `f567884aeb8851b6e794af1184119a3bfbe1e631`. Only this research package
is added. The selected result, its proof obligations and `upstream/` are
unchanged. No improved multiplication bound or practical speedup is claimed.
