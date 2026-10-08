# A sharper exponent for integer multiplication

**Conditional research draft: Douglas Colkitt's framework, with a new
construction contributed by Zhihao Chen (jacklightChen).**

In the pinned OpenAI manuscript's fixed finite-alphabet Turing-machine model
with a fixed number of one-dimensional tapes, the strongest supplied witness is

$$
T(n)=O\!\left(n(\log n)^{1-\kappa}\right),\qquad
\boxed{\kappa=\frac{373}{10^{11}}=3.73\times10^{-9}>2^{-28}}.
$$

The simpler `kappa = 2^-28` is a corollary. These compare asymptotic exponents,
not practical runtimes. The complete upstream theorem and retained analytic
interfaces remain assumptions; the new arguments have not received independent
mathematical review or formal verification.

**[Read the construction note (PDF)](artifacts/prime-field28-note.pdf)** ·
[Combined manuscript patch](patches/prime-field28.patch) ·
[Exact certificate](certificates/prime-field28.json) ·
[Review guide and attribution](docs/research/prime-field28.md)

## What changed

A new interchange motif uses five-subsets of 28 points and scalar arithmetic
over F3. Paired degree-three recursion, retained pair totals and exact
four-point-star resynthesis reduce the auxiliary role upper bound to
11,840,940. Stage sharing and the written rational-frame argument support
`a_b = 3/400000000`. A paired complex producer gives `a_c = 39/10^9`.
Together with the existing compact-control construction and PR #5's fast
Gaussian resampling, these give the stated conditional bound. The payload
alphabet changes; the address-prime construction is retained.

The exact minimum final margin is
`934813/250000000000000`, with a strict gap of
`2313/250000000000000` above the declared kappa.

This branch is based directly on `main`. Necessary files from eumemic's
Claude-assisted PRs #3 and #5 are imported unchanged and credited. Aligned
pairing (PR #2), retained totals and stage sharing (PR #4), and cheaper centers
(PR #6) are also credited. See the [construction ledger](docs/research/prime-field28.md).

## Evidence and scope

The checks cover every local coefficient, global support equality and
resynthesized boundary value; every replacement gate has disjoint support.
All 98,280 matching images are checked. Small complete F3 cases test arbitrary
dirty scratch and exact rational frames in both directions. The full h=28
complex producer and all final parameter inequalities are checked exactly.
General tensor-stage and finite-alphabet tape-transfer arguments are supplied
as written proofs. These checks do not formalize the complete multiplication
machine or replace independent mathematical review.

## Reproduce

With Python 3.11 or newer, a C++17 compiler, Git and Make:

```sh
make verify
git diff --exit-code -- certificates patches
```

No third-party Python packages or network access are needed. The new producer
uses roughly 1.2 GB memory and under 30 MB temporary storage. Checks regenerate
the certificates and patches, run the tests, verify pinned upstream hashes,
and check each independent patch against the unmodified manuscript.

With pdfLaTeX installed, build the latest note using `make prime-field-note`.
See [reproducibility instructions](docs/reproducibility.md) for full manuscript
builds. [Current research status](docs/research/current-status.md) distinguishes
this witness from historical bounds and scoped ceilings.

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

The new ternary construction is contributed by **Zhihao Chen (jacklightChen)**
with substantial **GPT-6 Astra (OpenAI Codex)** assistance, as identified by
the contributor. Future research using this contribution should explicitly
acknowledge Zhihao Chen and cite the note and PR. This records the first
submission of this specific construction by these contributors to this
repository, not worldwide priority. Earlier contributors retain their credit;
see [the dependency and attribution ledger](docs/research/prime-field28.md).


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
