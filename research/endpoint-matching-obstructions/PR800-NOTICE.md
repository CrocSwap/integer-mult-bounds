# Attribution and scope

Prepared by Jeremy Diviney with substantial OpenAI Codex assistance in the
research, proof, implementation and validation. New material is under the
repository's Apache-2.0 license. No independent human review, maintainer
endorsement or literature-priority claim is made.

littleBro's [PR705](https://github.com/CrocSwap/integer-mult-bounds/pull/705),
head `eeb0cd605415a73b792915aaa9185000f293c84a`, supplies the determinant/path
homogeneity argument being extended, all 73 literal words, and unchanged
`screen.py`. Its nine explicitly unclassified evolved words define this
submission's corpus. `words.json.gz` is copied from that head; the decompressed
payload is the mathematical source pin. PR705's original notices identify
substantial OpenAI Codex assistance in its work.

littleBro's [PR680](https://github.com/CrocSwap/integer-mult-bounds/pull/680),
head `c3a5b6b7afec35d259c29bc2d8bb8516e975ad31`, supplies unchanged `model.py`
and `dense.py` through PR705, including the formal phase quotient convention.
Their file hashes are recorded in ORIGINS.json. The new dense conjugation
check uses that exact Gaussian arithmetic without its tableau transition
formulas. The Laurent determinant regression adapts PR705's control matrices.

The complex m=3, W=3, s=8 question and register framework are credited to
eumemic's [PR288](https://github.com/CrocSwap/integer-mult-bounds/pull/288),
head `475a088b5862f75f0b10596cfd6842d19531a5ec`, and its predecessors,
including Swapnil Jain's P1/P2 and upstream Clifford-frame work. This package
does not resolve that general question.

The addition is freely chosen Laurent weights with homogeneity required only
on forbidden coefficient classes, an explicit global certificate for
`evolved-27`, and an exact finite frame census. The selected result and
`upstream/` are unchanged. No new kappa is claimed.

Overlap review read PR705 and PR680 and queried open/all PR metadata for
Clifford, path and valuation work, with a final metadata refresh through PR799.
PR720's nine-call theorem concerns the abelian bit model and different target
assumptions; PR791 audits idempotent endpoint ranks in a different model. This is not
a review of every PR diff or a novelty proof. Sources are pinned because
pending work can change; all runtime dependencies are included locally.

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
