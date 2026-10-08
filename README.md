# A sharper exponent for integer multiplication

**Research draft by Douglas Colkitt — conditional on the underlying manuscript
and the written extensions supplied here.**

This draft improves OpenAI's
[*Integer multiplication below n log n*](https://github.com/openai/math/tree/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Integer-multiplication-below-n-log-n-September-23-2026)
(result family #109). In its fixed finite-alphabet Turing-machine model with a
fixed number of one-dimensional tapes, the strongest supplied witness is

$$
T(n)=O\!\left(n(\log n)^{1-\kappa}\right),\qquad
\boxed{\kappa=\frac{1479}{10^{12}}=1.479\times10^{-9}>2^{-30}}.
$$

The simpler **`kappa = 2^-30`** is a corollary; the witness remains below
`2^-29`. It is **1479/590 ≈ 2.51 times** the preceding compressed-complex
witness `59/10^11` and about **17.8 times** the compact-control witness
`83/10^12`. The original manuscript uses `2^-182`. These compare asymptotic
exponents, not practical runtimes.

**[Read the fast-resampling proof note (PDF)](artifacts/fast-gaussian-note.pdf)** ·
[Review the combined source patch](patches/fast-gaussian-30.patch) ·
[Inspect the exact certificate](certificates/fast-gaussian.json) ·
[Construction and verification summary](docs/research/fast-gaussian.md)

This is a research claim supported by written proofs and reproducible checks.
The complete upstream theorem is assumed; the new arguments have not received
independent mathematical review or formal verification.

## Latest improvement: faster Gaussian resampling

With the compressed complex network the remaining cap was the Gaussian
resampling step. Its line maps cost `O(t p^(3/2+delta) alpha)`, which forces
the dimension exponent `epsilon < 1/5` and hence `kappa < a_b/5`. Two changes
remove that cap:

- **Chirped correlations.** The identity
  `(sigma a - b)^2 = sigma theta a^2 + sigma (a-b)^2 - theta b^2`
  turns every block of Gaussian sums along a line into one correlation,
  evaluated with the established integer multiplier in `O(p^(1+delta))` per
  output, independently of the Gaussian width `alpha`.
- **Faster Neumann series.** A potential-function argument shows that the
  powers of the correction `E = N - I` decay like `exp(-pi alpha^2 sigma n)`
  after a burn-in of order `alpha^2/theta` bits. The Neumann series then needs
  `O(p/alpha^2 + 1/theta)` terms instead of `p/(alpha^2 theta)`.

With `alpha = floor(sqrt(b/(8d)))` the Gaussian cost per bit becomes
`O(d^2 p^delta)`, so `epsilon` may approach `1/2`. The compressed complex
network supplies the room for the larger guard parameter `beta = 19/25` this
requires. The new scoped ceiling for these networks is `kappa < a_b/2 < 2^-29`.

## Preserved compressed complex network

After compact control, the complex network was the binding motif. It still
used the original side wires, one per ordered neighbor pair: **3,693,800 side
wires per invocation** at `h=25`. A shared-sum circuit computes the same side
correction with **108,195 reversible roles**, raising the certified complex
saving from `418/10^12` to **`14/10^9`**.

The complex labels are binary, and every frame residual needs an orthonormal
basis. Coordinate labels for disjoint sums and pair-star spans for
intersection-two sums satisfy this, with one necessary rule: an injected
disjoint piece must leave a point outside its target uncovered. Otherwise the
injection residual is an alternating hyperbolic plane with no orthonormal
basis. Exact checks cover every coefficient, label, inclusion and compiled
role in both stage directions.

With the complex saving no longer binding, the compact-control recurrence has
internal exponent `chi = tau`, and the paired bit network sets the bound:
`kappa < a_b/5 < 2^-30` for the retained Gaussian margin. See the
[construction summary](docs/research/complex-circuit.md) for the remaining
ceiling and next targets.

## Preserved compact-control movement

The compact-control construction moves **compact control fields instead of entire spaced
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

The remaining bottleneck at that stage was the complex layer's saving, which
the compressed complex network above removes. With the **fixed
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
| Compressed complex side circuit and binary frames | Exact full-size coefficient, label and role checks; written transfer proof |
| Source integration | Combined patch, reference checks and manuscript build |
| Full upstream multiplication theorem | Assumed |
| Independent review / full formalization | Not supplied |

The [review guide](docs/research/compact-control-review.md) identifies the
compact-control proof obligations and their tests; the
[complex-circuit summary](docs/research/complex-circuit.md) lists the new ones. [Current research status](docs/research/current-status.md)
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
make complex-note
```

The output is `artifacts/complex-circuit-note.pdf`; `make compact-note`
rebuilds the preceding compact-control note. The first PDF build may
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
| [compact-control-34](patches/compact-control-34.patch) | `83/10^12 > 2^-34` | Compact controls, complete reservations, local repair and separate complex arity |
| [complex-circuit-31](patches/complex-circuit-31.patch) | `59/10^11 > 2^-31` | Compressed complex side circuit with binary frames, on top of compact control |
| **[fast-gaussian-30](patches/fast-gaussian-30.patch)** | **`1479/10^12 > 2^-30`** | **Chirped-correlation Gaussian maps and a sharper Neumann count, on top of the compressed complex network** |

## Attribution, citation, and license

Author: **Douglas Colkitt**. Research, implementation and drafting were performed
with assistance from OpenAI Codex. The compact-control proposal originated
with a separate research agent; the supplied note develops its tape, layout,
repair and assembly arguments. AI assistance is not independent review or
endorsement by OpenAI. No priority or unrestricted optimality claim is made.

The compressed complex network (`complex-circuit-31`) and the faster Gaussian
resampling (`fast-gaussian-30`) were contributed by **eumemic**, prepared with
assistance from Claude (Anthropic); this is likewise not independent review or
endorsement by Anthropic.

The original manuscript is by OpenAI, pinned at commit
`adc7f1241b42e322a6451854ab7e4b4c146bf78a`. Source URLs and SHA-256 hashes are in
[upstream/manifest.json](upstream/manifest.json). Files under `upstream/` remain
unchanged; modifications are supplied as separate patches.

Use [CITATION.cff](CITATION.cff) and also cite the
[upstream manuscript](upstream/README.md). Until a release is archived, include
the repository commit used. Licensed under [Apache-2.0](LICENSE); see
[NOTICE](NOTICE) and [CONTRIBUTING.md](CONTRIBUTING.md).
