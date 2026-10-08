# A sharper exponent for integer multiplication

**Research draft by Douglas Colkitt — conditional on the underlying manuscript
and the written extensions supplied here.**

This draft improves OpenAI's
[*Integer multiplication below n log n*](https://github.com/openai/math/tree/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Integer-multiplication-below-n-log-n-September-23-2026)
(result family #109). In its fixed finite-alphabet Turing-machine model with a
fixed number of one-dimensional tapes, the strongest supplied witness is

$$
T(n)=O\!\left(n(\log n)^{1-\kappa}\right),\qquad
\boxed{\kappa=\frac{591}{10^{12}}=5.91\times10^{-10}>2^{-31}}.
$$

The simpler **`kappa = 2^-31`** is a corollary. The exact saving is
**591/83 ≈ 7.12 times** the preceding compact-control witness `83/10^12`.
These compare asymptotic exponents, not practical runtimes.

**[Read the combined construction](docs/research/shared-retained-complex.md)** ·
[Review the source patch](patches/retained-complex-31.patch) ·
[Inspect the exact certificate](certificates/retained-complex-layer.json)

The shared-exclusion builder is imported verbatim from [PR #3](https://github.com/CrocSwap/integer-mult-bounds/pull/3)
by `eumemic` (Claude-assisted), at commit `dfe5b818aad4d386cb5dd7d76df108088107765d`.
The retained-total and stage-sharing extensions are by `dleen` with substantial
OpenAI Codex assistance.

## What changed

The existing compact-control movement and paired-bit network are retained.
The `h=24` complex producer combines PR #3's shared-exclusion DAG with
retained one-point exclusion totals and stage-1/3 bank sharing. Grouped scatter
at a common low/full frame gives return loss `(h-1)²+h`, restores arbitrary
initial scratch, and preserves both phase paths and all-role endpoints.
The larger global coefficient is split into half-sized updates, with every
scalar gate included in the precision guard. The bit and complex arities
remain independent.

The exact complex saving is `1-sigma=2970/10^11=2.97e-8`, about **2.12 times**
PR #3's certified `1.4e-8`. The bit saving remains `296/10^11`, so the combined
headline stays `591/10^12 > 2^-31`. The complete compact consumer
uses `c=1`, with exact minimum assembly margin

$$
G_* = \frac{2956521}{5\cdot10^{15}} > \kappa,
\qquad G_*-\kappa=\frac{1521}{5\cdot10^{15}}>0.
$$

The complete upstream theorem, compact-control tape proofs and analytic
interfaces remain assumptions. Exact producer and parameter checks support
the supplied written argument; they do not formally verify the full machine.
The [preceding compact-control witness](artifacts/compact-control-note.pdf)
and its [review guide](docs/research/compact-control-review.md) remain available.

## Evidence and scope

| Component | Evidence |
| --- | --- |
| Parameters, logarithm enclosures, final margins | Exact rational certificate |
| Dirty-control identities, inverses and repair | Finite exhaustive cases and seeded tests |
| Wider-control tape bound, reservations and recursion | Written general proofs |
| Separate complex arity and precision guard | Written proofs and exact accounting |
| Source integration | Combined patch, reference checks and patch applicability |
| Full upstream multiplication theorem | Assumed |
| Independent review / full formalization | Not supplied |

The [review guide](docs/research/compact-control-review.md) identifies the new
proof obligations and their tests. [Current research status](docs/research/current-status.md)
is authoritative when older notes describe superseded barriers or hypothetical
witnesses. The earlier artifacts remain available and unchanged.

## Reproduce

With Python 3.11 or newer, Git and Make, run from the repository root:

```sh
make verify
git diff --exit-code -- certificates patches
```

No third-party Python packages or network access are needed for these checks.
They regenerate the certificates and patches, run the tests, verify upstream
hashes, and check each patch against the pinned manuscript. The second command
checks exact regeneration on a clean checkout.

The preceding rectangle variant has a preserved PDF. With Tectonic installed,
rebuild that earlier note using:

```sh
make retained-complex-note
```

The output is `artifacts/retained-complex-note.pdf`. The first PDF build may
download TeX resources. See [reproducibility instructions](docs/reproducibility.md)
for applying the combined patch in a disposable copy and building older notes.
[GitHub Actions](.github/workflows/verify.yml) runs the arithmetic and patch checks.
Passing tests does not establish the complete multiplication theorem; this
repository contains no full multiplication-machine implementation.

## Earlier witnesses and independent patches

Each patch applies independently to the **unmodified** pinned source; they are
alternatives, not a sequence to apply together. The
[result history](docs/research/result-history.md) records the earlier mechanisms
and scoped ceilings.

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

## Attribution, citation, and license

Author: **Douglas Colkitt**. Research, implementation and drafting were performed
with assistance from OpenAI Codex. The compact-control proposal originated
with a separate research agent; the supplied note develops its tape, layout,
repair and assembly arguments. AI assistance is not independent review or
endorsement by OpenAI. No priority or unrestricted optimality claim is made.

The original manuscript is by OpenAI, pinned at commit
`adc7f1241b42e322a6451854ab7e4b4c146bf78a`. Source URLs and SHA-256 hashes are in
[upstream/manifest.json](upstream/manifest.json). Files under `upstream/` remain
unchanged; modifications are supplied as separate patches.

Use [CITATION.cff](CITATION.cff) and also cite the
[upstream manuscript](upstream/README.md). Until a release is archived, include
the repository commit used. Licensed under [Apache-2.0](LICENSE); see
[NOTICE](NOTICE) and [CONTRIBUTING.md](CONTRIBUTING.md).
