# Calibrated endpoint-gauge tours

A constructive reduction removes arbitrary restored target gauge paths from
separately calibrated pair-port words without increasing any concave phase-rank
moment. The exact source-tour minima are proved in [PROOF.md](PROOF.md).
No new kappa or supplier improvement is claimed.

For even h >= 6 and 0 <= p <= 1, the oriented phase alphabet has minimum
`2h(h-2)^p + h(h-4)`. With binary translations separately counted but assigned
zero recursive phase-moment cost, the minimum is
`2h(h-2)^p + h(h-4)2^(p-1)`.

Every source is independent and restored. Every dirty target has its own pair
output and exactly two individually calibrated reads from its declared source.
Sources do not mix; targets are not consumed by other roles. These restrictions
are essential. In particular, this is not a lower bound for arbitrary circuits
computing the same final operator.

## Reproduce

Python 3.10 or later, standard library only, from the repository root:

```sh
python3 -I -B research/calibrated-endpoint-gauge-tours/test_verify.py
python3 -I -B research/calibrated-endpoint-gauge-tours/verify.py NEW_RECEIPT.json
```

Existing output files are refused. The finite verifier checks twelve complete
words at h=6,8,10: oriented tours, translation-closed tours, overlapping endpoint
gauges with late negative reads, and source-detour normalization. A sparse
integer Laurent-monomial full-input replay and a dense Gaussian-integer replay
through the intrinsic binary projectors agree on all old-input columns and
Fourier characters. The oriented phase groups at h=4,6 are exhaustively searched.
Mutation controls reject changed/missing reads, dirty-input restoration errors,
unpaid ranks, cross-role operations and type-confused records.

The written all-size proof is separate from finite replay. The executable
normalizer establishes rank-mass monotonicity (p=1); it is not a general
all-p shortest-path optimizer. Translations remain in their own literal ledger.
No supplier replay, tape implementation or proof-assistant build is claimed.

## Open next questions

Can cross-role mixing and additional readouts beat these tours while retaining
all separate pair outputs? This would change an essential hypothesis of the
detour theorem and could expose real phase-inventory headroom. A feasible first
step is h=6: six sources, twelve independent dirty targets, coordinate phases
of ranks one through four, and a small explicitly bounded window of signed
cross-role ADDs. Require its full old-input operator to match before comparing
with rank mass 60 and the translation-closed inventory of 18 phase calls plus
six translations. Count every added scalar operation separately.

The blocker is constructing a full restored operator rather than a cheaper
aggregate output. This package supplies no profitable mixed-role word and no
unrestricted lower bound; finite failure in one bounded window would not close
that question. Supplier allocation and the complete recursive invoice would
still be needed before any exponent claim.

## Prior work and overlap

The coordinate-phase model and rank-priced residual interface are inherited
from the project's stopped and partial-gauge construction lineage, including
icekylinx's [#104](https://github.com/CrocSwap/integer-mult-bounds/pull/104)
and [stopped-product note](../../notes/stopped-product-note.tex).
The binary translation identity is elementary and is not the claimed novelty.
The contribution is the target-to-source detour reduction and the exact scoped
minima with all individual pair ports retained.

Inspected public heads and source context are in [SOURCES.json](SOURCES.json).
Eumemic's [#288](https://github.com/CrocSwap/integer-mult-bounds/pull/288)
contains broader paradigm obstructions; @CubeJerry's
[#907](https://github.com/CrocSwap/integer-mult-bounds/pull/907) corrects its
unrestricted abelian-metric premise. This proof derives its metric for its
explicit coordinate alphabet and does not use that premise. Navinor's
[#825](https://github.com/CrocSwap/integer-mult-bounds/pull/825) concerns the
common-flag rational-frame XOR model, rather than these complex phase readouts.
No code from those submissions is imported. The inspected open PR bodies and
active discussions did not reveal a matching calibrated endpoint-tour theorem;
this is not an exhaustive literature-priority claim.

Prepared by Richard Hoekstra with substantial OpenAI Codex assistance in the
mathematics, implementation and writing. New standalone material is offered
under the repository's Apache-2.0 terms; predecessor attribution is retained.
