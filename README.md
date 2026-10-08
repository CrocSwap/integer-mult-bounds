# Conditional multiplication saving 4.099494519 × 10^-5

RaD's alternating producers combined with both fixed bases and copied reversed
corners give **κ = 4099494519/10^14 > 2^-15**, under the inherited analytic
and fixed-tape hypotheses: **1.6193% above PR #41's alternating candidate**.

See the [proof and reproduction guide](research/rad-fixed-reversed/README.md).
Full `make verify` passed: **215 tests**, fresh geometry/producer/profile and
independent schedule checks, and **18 historical patch checks**. See the
[validation receipt](research/rad-fixed-reversed/validation.json). Earlier
results below retain their own validation status.

# Conditional multiplication saving 3.918734894 × 10^-5

Fixing both local bases while preserving copied reversed corners gives
**κ = 1959367447/50000000000000 > 2^-15**, under the retained analytic and
fixed-tape hypotheses: approximately **0.8248% above PR #39**.

See the [proof and reproduction guide](research/copied-both-reversed/README.md).
Full `make verify` passed: **203 tests**, fresh exhaustive geometry and producer checks, and **18 historical patch checks**. See the [validation receipt](research/copied-both-reversed/validation.json). Earlier results retain their own validation status below.

# Conditional multiplication saving 3.886675852 × 10^-5

A fixed middle basis composed with copied reversed corners gives
**κ = 971668963/25000000000000 > 2^-15**, under the retained analytic and
fixed-tape hypotheses. This is approximately **0.011627% above PR #38**.

See the [proof and reproduction guide](research/copied-fixed-reversed/README.md).
Full `make verify` passed: 192 tests, fresh producer/profile and geometry checks, and 18 historical patch checks. See the [validation receipt](research/copied-fixed-reversed/validation.json). Earlier results below retain their own validation status.

# Conditional multiplication saving 3.850771033 × 10^-5

Reversed two-stage corners composed with copied retained centers give
**κ = 3850771033/10^14 > 2^-15**, under the retained analytic and fixed-tape
hypotheses. This is approximately **0.1321% above PR #36**.

See the [proof and reproduction guide](research/copied-reversed/README.md).
Full `make verify` passed: 182 tests, fresh producer/label checks and 18
historical patch checks. See the [validation receipt](research/copied-reversed/validation.json).
Earlier results below are retained as dependencies and historical records.

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
