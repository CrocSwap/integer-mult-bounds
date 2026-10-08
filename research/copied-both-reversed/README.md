# Both fixed bases with copied reversed corners

Under the inherited analytic and fixed finite-alphabet multitape hypotheses,

$$T(n)=O(n(\log n)^{1-\kappa}),\qquad
\kappa=\frac{1959367447}{50000000000000}
=3.918734894\times10^{-5}>2^{-15}.$$

This fixes the first basis as well as the middle basis in
[PR #39](https://github.com/CrocSwap/integer-mult-bounds/pull/39), pinned at
`70ae24129649f6d6d4ec6360962a80c3c42a38f1`. The ordered factors remain
(23,25), but both local bases now equal I+J. The entire original-envelope
h23 profile replaces the generic h23 profile, while the certified h25
profile, copied-center schedule and reversed data blocks remain.
The saving is approximately **0.8248% above PR #39**. This compares
conditional asymptotic exponents, not measured runtime or global optimality.

## Fixed geometry and exact nonvanishing

The [geometry proof](geometry-proof.txt) keeps every actual PR #37 controlled
permutation, restriction tree and coordinate interval. Both bases are fixed,
so there is no remaining generic first-factor choice. The proof enumerates
all **1,771 × 2,300 = 4,073,300 actual source-triple pairs** and certifies all
47 required ordered rational prefixes for each pair. The data profile is
**9 singletons + [21,17,481]**, in the same physical order.

A successful modular replay at an admissible prime proves that each tested
rational prefix minor is nonzero. If a primary modular pivot vanishes, the
entire pair restarts at another admissible prime; no pair is skipped and no
modular zero is mistaken for a rational zero. Different pairs may use
different witness primes. The finite rational matrices are already fixed;
an eventual address prime can avoid their finite set of exceptional
numerators and denominators as in the inherited setup. The complete replay
checks191,445,100 nonzero prefixes. Universal ordered-zero identities come
from the inherited all-weight rank-cut proof, independently of the modular
zero regression checks.

The source-line weights are31/18 and-5/24 at h23, and68/39 and-5/26 at h25.
All primal and dual coordinates are nonzero. Actual local restrictions are
nonzero diagonal row/column scalings of the complete fixed local matrices.
Their ranks exhaust the ambient local residual rank, so no outside pivot
is left uncounted. Auxiliary blocks and ordinary corank-one growth fronts
retain their inherited profiles. The [independent review](review/) derives
all48 copied-center complements and verifies their actual local transfers.

## Complete original-envelope profiles

Fresh base-two h23 scalar, original-envelope/matching, positive-label and
independent label checks reproduce R23=38,776 and loss506. Every one of its
**71,547 profiled transition matrices** is checked under the five certified
primes used for h25. Exact denominator/numerator bounds at h23 lie below
the already proved h25 uniform rank-four minor bound. Thus every relevant
rational northeast rank is the maximum of its modular ranks, and ordered
pivots follow by mixed differences. This is exact zero certification, not
probabilistic evidence. The unchanged h25 profile has96,273 such matrices.

The h23 fixed local rank is892,860 before copied centers. Exactly23
identity width23 cleanup calls become23 rank-one complement calls,
leaving copied rank892,354=23*38,776+506. All actual rank22 copied transforms
remain in the full fixed-basis profile. At h25 the corresponding previously
checked25 identity-to-complement replacements and rank24 transforms remain.
No copy saving is added twice and no fixed profile is replaced by a generic
rank-only approximation.

The complete new internal23 histogram is replicated N/1771=2300 times.
All other PR #39 child classes stay unchanged. In particular N=4,073,300
paid endpoint corrections, W=188,181,929, m=575, L=2,226,400 and total
rankWm-N+L=108,202,762,275 are retained.

## Exact exponent and inherited transfer

The bit saving is **783777693/20000000000000 = 3.918888465e-5**.
The complete characteristic is checked with exact rational logarithm and
exponential enclosures. The inherited PR #36 complex construction stays
(28,28), mixed-center19, at saving717/10^7. Both moments, all47 strict
assembly conditions, seven margins and eventual cutoff comparisons are
replayed. C1=1, row stock p^2000 and semantic
E=64*(W_complex+m_complex+G_scalar+1)^3 are retained.

The fixed-basis change preserves the scalar circuit and copied-stream
identities. Restoration of arbitrary dirty scratch, complete role volumes,
sequential fixed-tape storage, routing and bulk interfaces, analytic
recovery, prime existence, constructive setup and eventual thresholds remain
inherited proof dependencies. Finite certificates do not constitute formal
verification or external mathematical acceptance of the full theorem.

## Reproduction

```sh
make copied-both-reversed-check
make copied-both-reversed-producer
make verify
```

Python3.11 or newer and a C++ compiler are required. The complete source-pair
check is an exhaustive replay, not a sample. Sources, fixtures and proof
inputs are pinned locally; no sibling checkout is required. The focused
[patch](../../patches/copied-both-reversed.patch) applies to the pinned
PR #39 commit. The inherited manuscripts are unchanged.

**Draft:** full inherited make verify is pending after focused validation.
The validation status will be updated only after the committed research
passes that run.

## Attribution

Rohan Arun, with substantial OpenAI Codex assistance, supplies this
both-fixed/reversed-corner composition, complete pair certificate and
integration. Credit icekylinx's fixed-basis projectors/profiler and copied
centers (PR #32/#36), James Chang's reversed geometry (PR #34), Dominik
Scholz's fixed-basis/dimension compositions (including PR #38), Zhihao Chen,
Aurel Prosz/Paureel, Swapnil Jain, RaD/hipotures, eumemic, Douglas Colkitt,
OpenAI, Harvey–van der Hoeven and every retained predecessor notice.
Original licenses and historical AI-assistance disclosures remain.
