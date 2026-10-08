# Conditional saving 4.105106623e-5 from hill-climbed producers

**κ = 4105106623/10^14 = 4.105106623×10⁻⁵ > 2^-15**, conditional on OpenAI's
base theorem and retained analytic and fixed-tape interfaces: **0.10918% above
PR #46**. Pinned summand-order swaps in RaD's producers remove roles: R falls
from 36,685 to 36,656 at h=23 and from 48,479 to 48,398 at h=25, each with a
numerically selected carrier matching whose pinned output is checked exactly. See
[research/climbed-producers](research/climbed-producers/README.md) and run
`make climbed-producers-verify`. Full `make verify` passed: 191 tests and 18 historical
patch checks; see the [validation receipt](research/climbed-producers/validation.json).

# Conditional saving 4.10062945e-5 from weighted matching and exact data recovery

The [proof and reproduction note](research/copied-fixed/PROOF.md) gives
**κ = 82012589/2000000000000 > 2^-15**, conditional on OpenAI's base theorem
and retained analytic and fixed-tape interfaces. This is **6.6292252%**
above PR #36, **0.0268189%** above PR #43, and **0.00000477975%** above #44.

Compose Rohan Arun's PR #44 weighted carrier matching with exact rational
recovery of its ten conservative data-corner fallbacks. The matching,
complete fixed profiles and dirty physical timelines are replayed locally.
Every data pair now uses 9 singletons plus blocks of widths 21, 17 and 481.
Exact bounds show the #44 network fails at the new bit saving while this
network passes. PR #40/#42 previously recovered the same pairs by another
prime; no new matching algorithm or global optimality is claimed here.

Run `make copied-fixed-verify` for full scalar, label, matching, fixed-profile,
physical timeline, exhaustive data-pair and exact-fraction checks.
`make verify` includes these and the inherited suite. The proof, source
credits and limitations are included. Finite certification is not formal
verification or external acceptance of the full theorem.
The original PR #36 result follows for comparison.

# Integer multiplication with conditional saving 3.84569e-5

$$
T(n)=O\!\left(n(\log n)^{1-\kappa}\right),\qquad
\kappa=\frac{384569}{10000000000}=3.84569\times10^{-5}.
$$

Copied retained-center reads replace each local rank pair `(r,h)` by
`(r,h-r)`, including the transformed copy. In the adopted two-stage topology,
this reduces the total rank from `Wm-N+2L` to `Wm-N+L`.

The selected bit construction uses dimensions `(25,23)` and the certified
data profile `11 singletons; 21,15,481`. The complex construction uses
`(28,28)` with mixed-center parameter `d=19`. Their strict savings are
`384599/10000000000` and `717/10000000`, respectively. Semantic assembly
uses `C1=1` and product row stock `p^2000`; the final absorption gap
exceeds `4.0746e-11`.

The result remains conditional on the retained multiplication framework,
the attributed analytic and tape interfaces, and their eventual thresholds.
Finite checks support the written proofs; they do not constitute a formal
verification or a complete multiplication implementation.

## Proof and reproduction

- [Current proof source](notes/copied-centers-note.tex).
- [Exact certificate](certificates/copied-centers-network.json): complete
  child lists, moments, semantic precision and 47 strict constraints.
- [Incremental producer and corner checks](scripts/copied_centers_producer.py).
- [Adopted two-stage and corner proofs](references/copied-centers/README.md),
  [analytic dependencies](references/semantic-bulk/README.md),
  [reproduction instructions](docs/reproducibility.md) and [provenance](SOURCES.json).

```sh
make copied-centers-verify
```

This target checks the new mixed-center producer and exact corner witness,
reuses the unchanged verified bit producers, and certifies the new assembly.
`make verify` additionally runs inherited checks. Proofs are supplied as
LaTeX source; no new PDF is included.

## Contribution history

The immediate parent is [PR #32](https://github.com/CrocSwap/integer-mult-bounds/pull/32),
commit `0ef3aeb61f55cc0b321ce6a0ef00acee25cefe52`.
The preceding contributions by **icekylinx** are:

| PR | Conditional saving | Contribution |
|---|---:|---|
| [#10](https://github.com/CrocSwap/integer-mult-bounds/pull/10) | `1.2299998e-7` | Projector batching, controlled bases and mixed-width recursion |
| [#18](https://github.com/CrocSwap/integer-mult-bounds/pull/18) | `1.884586e-6` | Partial-swap frames, binary triples and compatible positive labels |
| [#24](https://github.com/CrocSwap/integer-mult-bounds/pull/24) | `5.98615e-6` | Endpoint gauges and general binary phase residuals |
| [#32](https://github.com/CrocSwap/integer-mult-bounds/pull/32) | `1.2523415e-5` | Structured blocks, mixed centers and semantic/bulk composition |

The [combined manuscript patch](patches/batched-23.patch) remains the #10
baseline; subsequent extensions have standalone proof sources.

## Attribution

The copied retained-center schedule, complex endpoint transfer and selected
composition are contributed by **icekylinx**, with substantial OpenAI GPT-6
Astra and Codex assistance.

This round adopts **Aurel Prosz (Paureel)**'s two-stage topology and paid
endpoint copy, **Zhihao Chen (jacklightChen)**'s PR #29 unequal-axis
composition, **Rohan Arun**'s PR #31 corner method and **Dominik Scholz**'s
PR #33 parameterization. PR #29 also credits **Swapnil Jain**'s linked
two-stage development. Semantic and analytic dependencies retain the
PR #21/#23 and **RaD (hipotures)** credits.

The framework and retained producers build on **Douglas Colkitt**, **eumemic**,
**Bortlesboat**, **dleen**, and the other contributors recorded in [NOTICE](NOTICE).
OpenAI's manuscript remains pinned at `adc7f1241b42e322a6451854ab7e4b4c146bf78a`.
The repository retains Apache-2.0; imported RaD proof sources retain their
separate CC0 terms and original notices.
