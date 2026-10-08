# Reordered rank-first regions: conditional saving 5.1028985071975e-5

This branch proposes **κ = 2041159402879/(4×10^16) = 5.1028985071975×10^-5**,
about **0.00277% above [PR #63](https://github.com/CrocSwap/integer-mult-bounds/pull/63)**.
The bit saving is **5103158916233/10^17**. Within each frame rank, use
cover/core order at h=23 and decreasing minimum-node order at h=25. The scalar graph, rank-first
retired-slot policy, role counts and paid endpoints remain inherited from #63;
the changed schedule changes the physical frame transitions and their complete
fixed-basis child profile. W remains **137,151,806**.

[Construction, proof and credits](research/reordered-rank-pair/README.md) ·
[Exact arithmetic certificate](research/reordered-rank-pair/arithmetic/certificate.json)

Run `make reordered-rank-pair-verify` to rebuild both physical words and profiles,
then check the exact moment and inherited assembly. `make verify` includes this
new target and all inherited verification groups. Full repository validation
is pending for this draft; focused checks passed before publication.

This is a finite conditional witness under the inherited analytic, all-size
compiler and fixed finite-alphabet multitape hypotheses. It is not a proof
of global optimality or a measured practical speedup. The schedule gain and
the finer arithmetic-grid gain are distinguished in the research note.

Prepared by Rohan Arun with OpenAI Codex assistance. Credit Dominik Scholz
(#63), Avi Eisenberg (#62), Chafik Boukhalfa (#60), eumemic (#57), and the
Alejandro Zarzuelo Urdiales (#61, parameter-refinement precedent), together with all inherited contributors.
The reviewed main-branch result below remains separately identified.

# A sharper exponent for integer multiplication

**Community research maintained by Douglas Colkitt — conditional on the original
OpenAI #109 framework.**

The reviewed community witness gives

$$
T(n)=O\!\left(n(\log n)^{1-\kappa}\right),\qquad
\boxed{\kappa=\frac{4123863984}{10^{14}}
=4.123863984\times10^{-5}>2^{-15}}.
$$

This uses the fixed finite-alphabet Turing-machine model with a fixed number of
one-dimensional tapes in OpenAI's
[*Integer multiplication below n log n*](https://github.com/openai/math/tree/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Integer-multiplication-below-n-log-n-September-23-2026).
The saving is **6.10% above our previous PR #39 release**, and still below 2^-14. These numbers compare
asymptotic exponent savings, not practical running times.

**Latest circuit contribution: [Rohan Arun (@rohanarun), PR #49](https://github.com/CrocSwap/integer-mult-bounds/pull/49).**
This composes **Chafik Boukhalfa's** reordered exclusion sums and exact recovery,
**RaD / hipotures's** alternating producers and physical compiler, and Rohan's
weighted matching and order search. Their full dependency chain and
AI-assistance disclosures remain credited in the source notices.

**[Proof and reproduction guide](research/climbed-48/README.md)** ·
[Exact certificate](research/climbed-48/certificate.json) ·
[Maintainer review](docs/research/community-followup-review.md) ·
[Integration record](docs/research/community-followup-integration.md)

## What changed

The community work combines recursive batching and partial-swap frames with
semantic precision bounds, arbitrary-coordinate routing and bulk Gaussian
resampling. Two-stage circuits, paid copied-center operations and improved
contiguous blocks strengthen the finite networks. The latest increment
reorders disjoint sums and retains more compatible carriers, with both local
bases fixed and the entire physical circuit replayed exactly.

The selected bit network has m=575 and 177,284,805 roles. Its recursive saving
is 4124034054/10^14; the unchanged complex network supplies 717/10^7.
The assembly retains all seven strict exponent margins, including numerical,
movement and normalization costs.

Also incorporated: **Alejandro Zarzuelo Urdiales's Gaussian parity and finite
tensor proofs (PR #45)** and **Ryan S's historical Lean certificates and circuit
checks (PR #26)**. These strengthen verification within their stated scope;
they do not change κ or formally verify the complete multiplication theorem.

## Attribution

This is a community result. Principal incorporated contributions include:

- **[Rohan Arun (@rohanarun)](https://github.com/rohanarun):** corner geometry,
  fixed-basis composition, weighted matching and the latest [#49](https://github.com/CrocSwap/integer-mult-bounds/pull/49) circuit.
- **[Chafik Boukhalfa (@chafreaky)](https://github.com/chafreaky):** exact data
  recovery, independent checkers and reordered exclusion sums ([#43](https://github.com/CrocSwap/integer-mult-bounds/pull/43), [#46](https://github.com/CrocSwap/integer-mult-bounds/pull/46), [#48](https://github.com/CrocSwap/integer-mult-bounds/pull/48)).
- **icekylinx:** recursive batching, partial swaps, fixed projector profiles,
  copied retained centers and the selected complex construction.
- **Zhihao Chen (@jacklightChen):** controlled bases, translated frames,
  semantic/bulk compatibility and two-stage integration.
- **RaD project (@hipotures):** semantic precision, arbitrary-coordinate
  routing, phase-cell inversion, bulk resampling, alternating pair order and
  the independent physical role compiler ([#41](https://github.com/CrocSwap/integer-mult-bounds/pull/41)).
- **James Chang (@jamesyc):** reversed two-stage geometry and exact controls.
- **Aurel Prosz (@Paureel) and Swapnil Jain:** attributed two-stage development
  and the paid copied-stream endpoint construction.
- **Dominik Scholz (@DominikScholz):** dimension, parameter and fixed-basis refinements.
- **eumemic:** complex circuits, Gaussian resampling and source-frame work;
  **Bortlesboat** and **dleen:** aligned pairing, retained totals and sharing.
- **[Alejandro Zarzuelo Urdiales (@alejandrozu)](https://github.com/alejandrozu):**
  Gaussian parity, finite tensor execution proofs and mixed-center reference
  checks ([#45](https://github.com/CrocSwap/integer-mult-bounds/pull/45)).
- **[Ryan S (@princezuda)](https://github.com/princezuda):** historical Lean
  certificates, frame/movement lemmas and independent circuit checks
  ([#26](https://github.com/CrocSwap/integer-mult-bounds/pull/26)).

The [full contribution record](CONTRIBUTORS.md) also credits parallel,
incremental, superseded and pending work. Inclusion there does not claim incorporation
or verification of every PR. Douglas Colkitt maintains the project and its
original research, review and integration, with OpenAI Codex assistance.
OpenAI's original manuscript and Harvey–van der Hoeven's analytic work retain
their attribution. Contributor-specific AI disclosures remain in [NOTICE](NOTICE).

## Evidence and limits

The selected contribution is PR #49 at `f95d2910e027495983b53cae1693cf535abf2569`.
The [follow-up review](docs/research/community-followup-review.md) accepts its
increment conditionally on the retained [PR #39 audit](docs/research/community-final-audit.md)
and original #109 framework. This is not a claim of full formal verification,
independent human peer review, worldwide priority or optimality. No complete
practical multiplication-machine implementation is supplied.

Validation includes fresh finite producers, exact rank profiles, full dirty
workspace restoration, historical patch checks and an independent rational
moment/assembly checker. Both formal submissions were built with their pinned
Lean versions; their axiom audits accept only Lean's standard axioms.
See the [review receipts](docs/research/community-followup-validation.json) and
[combined integration record](docs/research/community-followup-integration.md).

The earlier PR #39 release and **2^-30 checkpoint** (`1a74950`) remain preserved,
with all earlier certificates, proofs, patches and contributor notices.

## Reproduce

Requires Python 3.11 or newer, Git, Make and a C++17 compiler with unsigned
128-bit integer support (tested with GCC and Clang). No third-party Python
packages or network access are needed for the arithmetic/circuit verification.
The separate formal targets require Lean and an initial toolchain/Mathlib download.

```sh
make verify
git diff --exit-code -- certificates patches
```

For the final witness and the independent arithmetic/source audit:

```sh
make copied-fixed-verify climbed-48-verify
make community-followup-check
make formal-verify
```

Allow several minutes and multiple gigabytes of memory for full producer
rebuilds. See [reproduction details](docs/reproducibility.md).

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
