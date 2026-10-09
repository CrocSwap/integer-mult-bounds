# A sharper exponent for integer multiplication

**Community research maintained by Douglas Colkitt — conditional on the original
OpenAI #109 framework.**

## Stopped product-ring extension

The new construction contributed by **icekylinx**, extending merged
[PR #36](https://github.com/CrocSwap/integer-mult-bounds/pull/36), gives

$$
T(n)=O\!\left(n(\log n)^{1-\kappa}\right),\qquad
\kappa=\frac{194869}{2500000000}=7.79476\times10^{-5}.
$$

It combines a stopped product-ring bit interchange on `(23,23)` with an
all-disjoint rational-center complex network on `(24,24)`. The new generic
opposite-bank factorization pays one reversed child per projector rank;
atom adapters, ordinary leaves, endpoint copies and the exact denominator-21
grid are included in the proof. The bound retains the original analytic
and fixed-tape hypotheses.

[Proof source](notes/stopped-product-note.tex) ·
[Exact certificate](certificates/stopped-product-network.json) ·
[Incremental reproduction](docs/stopped-product.md)

```sh
make stopped-product-verify
```

The maintainer-reviewed community checkpoint below remains its own result
and validation record.

## Reviewed community checkpoint

The reviewed community witness gives

$$
T(n)=O\!\left(n(\log n)^{1-\kappa}\right),\qquad
\boxed{\kappa=\frac{25508460085039}{500000000000000000}
=5.1016920170078\times10^{-5}>2^{-15}}.
$$

This is **23.71% above the preceding PR #49 release** and remains below 2^-14.
It is an improvement in the asymptotic exponent saving, not a measured runtime
speedup. The model and general reduction are inherited from OpenAI's
[*Integer multiplication below n log n*](https://github.com/openai/math/tree/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Integer-multiplication-below-n-log-n-September-23-2026).

**[Maintainer review and contribution ledger](docs/research/community-round2-review.md)** ·
[Finite circuit proof](research/pair-assembly/PROOF.md) ·
[Selected parameter certificate](research/matrix-exponent-synthesis/candidate/arithmetic.json) ·
[Independent arithmetic check](docs/research/community-pair-arithmetic.json)

## What changed

**Avi Eisenberg's interval strips and core-aware pair assembly (#62)** arrange
additions to allow more physical wire reuse. Combined with **eumemic's joint
frame compiler (#57)**, this yields the strongest finite network in this batch.
**Alejandro Zarzuelo Urdiales's exact parameter refinement and scoped Lean
certificate (#61)** supply the selected numerical value.

The bit network has m=575 and 137,151,806 physical roles; its certified recursive
saving is 102039046058023/2000000000000000000. The complex network retains saving
717/10^7. All recursive children, workspace restoration, copied centers and
endpoint costs remain charged. The seven final exponent margins are strictly positive.

The preceding combination of Avi's skip-prefix strips (#53), **Rohan Gupta's
dual-suffix layout (#55)**, eumemic's compiler and **Chafik Boukhalfa's composition
and ranked reclamation (#58/#60)** is also fully retained and reviewed.

Other reviewed contributions are retained even when their numerical witnesses
are superseded: **RaD's enlarged-frame and clone machinery (#51)**, **Rohan Arun's
positive-frame composition and order searches (#52/#56)**, **Rohan Gupta's parallel
order search (#50)**, **Chafik's original-envelope clones (#54)**, and **Rohan Garg's
split-pair recursion (#59)**. The review records the exact validation scope of each.

## Attribution

The names below identify GitHub contributors; they are not verified Twitter handles.

- **[Avi Eisenberg (ikeboy)](https://github.com/ikeboy):** skip-prefix and interval strips, core-aware pair assembly ([#53](https://github.com/CrocSwap/integer-mult-bounds/pull/53), [#62](https://github.com/CrocSwap/integer-mult-bounds/pull/62)).
- **[Rohan Gupta (gupt1156)](https://github.com/gupt1156):** dual-suffix strips and parallel order improvements ([#50](https://github.com/CrocSwap/integer-mult-bounds/pull/50), [#55](https://github.com/CrocSwap/integer-mult-bounds/pull/55)).
- **[eumemic](https://github.com/eumemic):** joint frame compilation and paid reclamation ([#57](https://github.com/CrocSwap/integer-mult-bounds/pull/57)); earlier complex circuits, Gaussian resampling and source frames.
- **[Chafik Boukhalfa (chafreaky)](https://github.com/chafreaky):** exact recovery, independent checkers, reordered sums, paid clones and joint-compiler composition/refinement ([#43/#46/#48/#54/#58/#60](docs/research/community-round2-review.md)).
- **[Rohan Arun (rohanarun)](https://github.com/rohanarun):** corner geometry, fixed-basis composition, weighted matching, order searches and positive-frame composition ([#49](https://github.com/CrocSwap/integer-mult-bounds/pull/49), [#52](https://github.com/CrocSwap/integer-mult-bounds/pull/52), [#56](https://github.com/CrocSwap/integer-mult-bounds/pull/56)).
- **[Rohan Garg (rohangar1)](https://github.com/rohangar1):** split-pair recursion, order refinement and paid-clone composition ([#59](https://github.com/CrocSwap/integer-mult-bounds/pull/59)).
- **[Alejandro Zarzuelo Urdiales (alejandrozu)](https://github.com/alejandrozu):** Gaussian parity and finite tensor proofs, matrix/search tools, exact refinement and scoped Lean arithmetic ([#45](https://github.com/CrocSwap/integer-mult-bounds/pull/45), [#61](https://github.com/CrocSwap/integer-mult-bounds/pull/61)).
- **[RaD project (hipotures)](https://github.com/hipotures):** semantic precision, routing, phase-cell inversion, bulk resampling, alternating producers, physical compiler and enlarged-frame/clone machinery ([#41](https://github.com/CrocSwap/integer-mult-bounds/pull/41), [#51](https://github.com/CrocSwap/integer-mult-bounds/pull/51)).
- **icekylinx:** recursive batching, partial swaps, fixed projector profiles, copied retained centers and the selected complex construction.
- **Zhihao Chen (jacklightChen):** controlled bases, translated frames, semantic/bulk compatibility and two-stage integration.
- **James Chang (jamesyc):** reversed two-stage geometry and exact controls.
- **Aurel Prosz (Paureel) and Swapnil Jain:** attributed two-stage development and paid copied-stream endpoints.
- **Dominik Scholz:** dimension, parameter and fixed-basis refinements.
- **Ryan S (princezuda):** historical Lean certificates, algebraic contracts and independent circuit checks ([#26](https://github.com/CrocSwap/integer-mult-bounds/pull/26)).
- **Andrew Barnes (Bortlesboat) and David Leen (dleen):** aligned pairing, retained totals and sharing.

The [full contribution record](CONTRIBUTORS.md) credits incorporated, parallel,
superseded and pending work separately. Douglas Colkitt maintains the project,
original research, review and integration, with OpenAI Codex assistance.
OpenAI's original manuscript and Harvey–van der Hoeven's analytic work retain
their attribution. Contributor-specific AI disclosures remain in [NOTICE](NOTICE).

## Evidence and limits

The [round-two review](docs/research/community-round2-review.md) extends the
[previous follow-up audit](docs/research/community-followup-review.md) and
[PR #39 transfer review](docs/research/community-final-audit.md). The original
#109 framework and retained all-size interfaces remain assumptions. This is not
full formal verification, independent human peer review, a worldwide priority
claim, or a practical multiplication benchmark.

Fresh checks cover complete emitted words and dirty basis vectors, physical
frame transitions, exact fixed-basis profiles, all 4,073,300 data pairs for the
retained geometry, and independent rational recurrence/assembly arithmetic.
The formal packages verify their stated finite/arithmetic contracts. PR #61's
integrated axiom audit contains 169 distinct declarations, including 11 concrete
frontier theorems; its input rows are bound to the replayed finite profile.
They do not formalize the whole multiplication algorithm.

The [review receipt](docs/research/community-round2-validation.json) distinguishes
fresh maintainer checks from contributor-supplied evidence. Earlier witnesses,
patches and attribution remain available. Submissions after #62 are outside this checkpoint's review; exact reviewed heads
are recorded in the ledger.

## Reproduce

```sh
make verify-pair
make verify-joint
make verify-positive
make formal-matrix-verify
# Complete arithmetic, producer, historical and unit-test suite:
make verify
```

Python 3.11+, a C++17 compiler and Boost headers are required for the full
arithmetic suite. The formal targets use their pinned Lean versions. See
[reproduction details](docs/reproducibility.md) and [CI layout](docs/ci-verification.md).

## Historical witnesses and independent patches


Each patch applies independently to the **unmodified** pinned source; they are
alternatives, not a sequence to apply together. The
[result history](docs/research/result-history.md) records the earlier mechanisms
and scoped ceilings. The [preserved research index](docs/research/preserved-research.md)
collects the intermediate compression, routing, Fano, and core searches, including
scoped negative results and reproducible certificates.

| Patch | Conditional saving | Scope |
| --- | --- | --- |
| [frozen-154](patches/frozen-154.patch) | `2^-154` | Original network and recurrence exponents |
| [balanced-153](patches/balanced-153.patch) | `2^-153` | Balanced assembly parameters |
| [same-network-129](patches/same-network-129.patch) | `2^-129` | Original network, sharper recurrence comparison |
| [h46-111](patches/h46-111.patch) | `2^-111` | Smaller network, dyadic parameters |
| [h46-109](patches/h46-109.patch) | `2^-109` | Rational recurrence saving, strict final margin |
| [h46-108](patches/h46-108.patch) | `2^-108` | Variable stopping exponent |
| [h46-rational](patches/h46-rational.patch) | `5.8e-33` | Strongest supplied parameter-only witness |
| [nonadjacent-layout](patches/nonadjacent-layout.patch) | Original parameters retained | Routing proof and revised layout cost only |
| [frozen-nonadjacent-107](patches/frozen-nonadjacent-107.patch) | `2^-107` | Direct routing, original network and recurrence exponents |
| [h46-nonadjacent-78](patches/h46-nonadjacent-78.patch) | `2^-78` | Direct routing with the h = 46 network |
| [h46-nonadjacent-76](patches/h46-nonadjacent-76.patch) | `2^-76` | Direct routing with tuned dimension and stopping parameters |
| [h46-shared-side-75](patches/h46-shared-side-75.patch) | `2^-75` | Stage-1/stage-3 side-role sharing, routing, and parameter tuning |
| [h46-incidence-67](patches/h46-incidence-67.patch) | `2^-67` | Rectangle incidence circuits, full auxiliary sharing, routing, and parameter tuning |
| [h46-dag-63](patches/h46-dag-63.patch) | `2^-63` | Shared intermediate sums and reversible role allocation |
| [h46-shared-point](patches/h46-shared-point.patch) | `13*2^-66` | Cross-group sharing |
| [h50-paired-59](patches/h50-paired-59.patch) | `2^-59` | Paired sums, stopped guard and tighter Gaussian setup |
| **[compact-control-34](patches/compact-control-34.patch)** | **`83/10^12 > 2^-34`** | **Compact controls, complete reservations, local repair and separate complex arity** |
| [complex-compression-31](patches/complex-compression-31.patch) | `2^-31` | Weighted complex circuits, binary phase frames and complete auxiliary sharing |
| **[ternary-30](patches/ternary-30.patch)** | **`2^-30`** | **Ternary five-subset circuit, rational frames and fixed-alphabet interchange** |

## Citation and license

Use [CITATION.cff](CITATION.cff), cite the individual contributions used and
include the repository version or commit. [CONTRIBUTORS.md](CONTRIBUTORS.md),
[NOTICE](NOTICE) and source-specific manifests preserve the dependency credits.

The project is [Apache-2.0](LICENSE). Bundled RaD sources retain their separate
CC0 license and notices. The pinned original OpenAI manuscript remains unchanged
under `upstream/`; its source hashes are in [upstream/manifest.json](upstream/manifest.json).
This project is not an official OpenAI release or endorsement.
