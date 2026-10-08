# A sharper exponent for integer multiplication

**Research draft by Douglas Colkitt — conditional on the underlying manuscript
and the written extensions supplied here.**

This draft improves OpenAI's
[*Integer multiplication below n log n*](https://github.com/openai/math/tree/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Integer-multiplication-below-n-log-n-September-23-2026)
(result family #109). In its fixed finite-alphabet Turing-machine model with a
fixed number of one-dimensional tapes, the strongest supplied witness is

$$
T(n)=O\!\left(n(\log n)^{1-\kappa}\right),\qquad
\boxed{\kappa=\frac{83}{10^{12}}=8.3\times10^{-11}>2^{-34}}.
$$

The simpler **`kappa = 2^-34`** is a corollary. The witness remains below
`2^-33`. It increases the exponent saving by approximately **47.85 million
fold** over our preceding published `2^-59` witness. The original manuscript
uses `2^-182`. These compare asymptotic exponents, not practical runtimes.

**[Read the compact-control proof note (PDF)](artifacts/compact-control-note.pdf)** ·
[Review the combined source patch](patches/compact-control-34.patch) ·
[Inspect the exact certificate](certificates/compact-control-layer.json) ·
[Review guide and dependencies](docs/research/compact-control-review.md)

This is a research claim supported by written proofs and reproducible checks.
The complete upstream theorem is assumed; the new arguments have not received
independent mathematical review or formal verification.

## What changed

The new construction moves **compact control fields instead of entire spaced
windows**. For `f` selected axes, it replaces the layer's movement cost
`O(V*((f*K)^tau+1))` by

$$
O\!\left(V\bigl((f\log p)^\tau+1\bigr)\right).
$$

The proof reserves temporary fields from existing address coordinates,
allows arbitrary initial temporary values, restores them exactly, and charges
exceptional-address repair at every recursion node. The temporary ranges
remain complete through padding and recursive row splitting.

Removing `K^tau` removes the restriction responsible for the preceding
quadratic dependence on the finite-network saving. The bit network stays at
`h=50`. The original complex network is separately instantiated at `h=25`,
and a generalized stopping-depth guard completes the new parameter witness.
This is a change to the movement construction and its proof, beyond parameter
tuning of the preceding algorithm.

The exact minimum assembly margin is

$$
G_* = \frac{333833}{4\cdot10^{15}}
    = 8.345825\times10^{-11} > \kappa.
$$

The remaining bottleneck is the complex layer's saving. With the **fixed
`h=25` complex motif and retained Gaussian/leaf inequalities**, the scoped
ceiling is below `8.369598075e-11`, hence below `2^-33`. This is not a ceiling
for other networks or integer multiplication in general.

## Evidence and scope

| Component | Evidence |
| --- | --- |
| Parameters, logarithm enclosures, final margins | Exact rational certificate |
| Dirty-control identities, inverses and repair | Finite exhaustive cases and seeded tests |
| Wider-control tape bound, reservations and recursion | Written general proofs |
| Separate complex arity and precision guard | Written proofs and exact accounting |
| Source integration | Combined patch, reference checks and manuscript build |
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

With Tectonic installed, rebuild the latest note using:

```sh
make compact-note
```

The output is `artifacts/compact-control-note.pdf`. The first PDF build may
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

## Additional draft research record

[RaD's source-framed h53 review package](research/rad-source-framed/README.md)
preserves a separately checked conditional witness above `2^-20`, with
portable exact arithmetic replay, pinned full evidence and explicit source
attribution. Newer pending contributions state larger savings; this package
makes no current-best claim and does not replace the retained release
manuscript. Run `make rad-source-framed-check` for its targeted checks.

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
