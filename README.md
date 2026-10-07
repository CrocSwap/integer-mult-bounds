# A sharper exponent for integer multiplication

**Research draft by Douglas Colkitt, with a parameter refinement by Aurel Prosz
(Paureel) — conditional on the underlying manuscript.**

This repository improves the parameters, axis routing, and finite bit network in OpenAI's
[*Integer multiplication below n log n*](https://github.com/openai/math/tree/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Integer-multiplication-below-n-log-n-September-23-2026)
(result family #109). Subject to its algorithmic interfaces and the construction
changes audited here, the strongest supplied bound is

$$
T(n)=O\!\left(n(\log n)^{1-\kappa}\right),\qquad
\boxed{\kappa=1.7523184\times10^{-18}>2^{-59}}.
$$

The computational model is the manuscript's fixed finite-alphabet Turing machine
with a fixed finite number of one-dimensional tapes. The original manuscript
uses `kappa = 2^-182`. The new parameter witness increases the exponent saving
by about **0.603% over the preceding parameters' limiting margin**, or 1.014%
over their rounded `2^-59` headline. It retains the paired circuits and their
declared bit and complex exponent savings.
These are asymptotic exponent comparisons, not measured practical speedups.

**[Read the parameter refinement and supremum derivation](docs/paired-tuned-parameters.md)** ·
[Review the latest patch](patches/h50-paired-tuned.patch) ·
[Read the inherited paired proof (PDF)](artifacts/paired-note.pdf) ·
[Inspect the routing audit](docs/nonadjacent-axis-audit.md) ·
[Reproduce the checks](docs/reproducibility.md)

## Latest improvement: a near-optimal fixed-exponent parameter witness

Paureel's refinement retains `h=50`, `a=1-tau=296/10^11`, and
`s=1-sigma=1/10^11`. It uses the exact rational choices
`beta=0.99999912384`, `epsilon=0.1999999999999`, and `delta=10^-14`,
with `C1=2`, `c=beta*a`, `lambda=1-(1+beta)*a^2/2`, and
`lambda'=1-beta*a^2`. All thirty side conditions are strict. The minimum margin is

$$
G=\epsilon\beta a^2
=1.7523184646864326407676563456\times10^{-18}>\kappa.
$$

For these fixed declared exponent savings and the revised inequalities, the
exact supremum is `G*=q*/(5+4*q*)`, where `q*` is the smaller positive root of
`a*q^2-(s+a^2)*q+a^2*s=0`. Exact rational bisection encloses it near
`1.7523184646886585e-18`. The advertised witness exceeds 99.999996% of this
scoped supremum. This does not establish optimality for other exponent estimates,
circuits, or multiplication algorithms, or establish global priority.

The [integrated certificate](certificates/paired-tuned-parameters.json) rechecks
the inherited paired circuit, frames, source hashes, and guard, then compares
every new slack and margin against the existing parameter verifier. The
[independent manuscript patch](patches/h50-paired-tuned.patch) updates rational
setup comparisons, stopping tests, and Gaussian cutoff accounting together.
The audit also records a role-budget target for `2^-58` as **unachieved**.

## Paired sums and tighter downstream estimates underlying the refinement

Three changes combine to reach `2^-59`:

1. A paired-block circuit keeps internal edge sums as vertex weights through
   the recursion. At `h=50`, cross-group sharing gives **509,194 side roles**,
   down from 694,495 for the preceding circuit at the same ground size.
2. Using the actual early stopping depth proves a **quadratic guard width**,
   replacing the conservative twentieth power.
3. The smaller Gaussian width `alpha=ceil((32*d*b)^(1/4))` meets the retained
   resampling interface and permits a larger transform dimension.

The exact minimum margin is

$$
G=\frac{272158569}{156250000000000000000000000}>2^{-59}.
$$

The [construction and dependency audit](docs/research/paired-network.md)
explains all three changes and the [certificate](certificates/paired-network.json)
checks their arithmetic, circuit coefficients, and both frame directions.
The strict margin is about 0.4%. Both motifs now use `h=50`; the complex motif
retains its original construction. The upstream theorem remains an assumption.

## Preserved cross-group sharing refinement

Equal sums can now be shared across different common-point groups. The reverse
computation uses orthogonal complements of the forward source spans, so it no
longer needs a separate positive-definiteness proof for reachable-target spans.
Every retained source span still has a common point and is positive definite.

This removes 45,706 additions and reduces side roles from **577,576 to 531,870**.
The rank deficit is unchanged. Exact checks support `a_b=203/10^11` and
`G=17661/10^23 > 13*2^-66`, with the complex saving unchanged. See the
[construction and next-search budget](docs/research/cross-point-sharing.md)
and [certificate](certificates/shared-point-network.json). With its then-retained guard and assembly bounds, that circuit fell short of
`2^-62`. The latest witness also changes those downstream bounds.

## Preserved shared-computation improvement

A cancellation-free computation graph shares intermediate sums across
outputs. Its reversible embedding uses **one role per output plus one per
binary addition**. Source supports provide nested forward frames; reachable
target supports provide nested frames for the reversed second stage.
All these spans are nondegenerate because each local circuit's triples share
a common point. Thus the new computation introduces no extra backward rank.

At `h=46`, side roles per invocation fall from **2,394,438 to 577,576**,
preserving the absolute rank deficit. The certified bit saving is
`a_b=187/10^11`; the complex saving remains `a_c=9/500000000000`. The
existing parameter recipe yields

$$
G=\frac{3a_{\rm b}^2}{70}\approx1.4987\times10^{-19}>2^{-63}.
$$

The [construction audit](docs/research/shared-computation.md) proves the
reversible embedding and both frame assignments. The
[exact certificate](certificates/dag-network.json) checks every output
coefficient at the target size, all compiled support inclusions, and the
downstream inequalities. The compiler is reusable for other compatible
cancellation-free circuits; the latest witness builds on this transfer.

## Preserved rectangle-circuit improvement

Neighboring triple pairs are partitioned into rectangles. A rectangle with
`a` sources and `b` targets uses an invertible mixer on `a+b-1` scratch roles,
instead of one role per pair. A common nondegenerate frame lets the mixer
share intermediate computations without adding backward rank. All auxiliary
roles, including centers, can then be shared between the first and third stages.

At `h=46`, this reduces side roles per invocation from **41,122,620 to
2,394,438** while preserving the absolute rank deficit. The certified bit
saving is `a_b=46/10^11`; the complex saving remains `a_c=9/500000000000`.
The existing parameter recipe gives

$$
G=\frac{3a_{\rm b}^2}{70}\approx9.0686\times10^{-21}>2^{-67}.
$$

The [construction and frame audit](docs/research/incidence-network.md) cover
dirty-scratch restoration, the reversed second stage, and every new frame
transition. The [exact certificate](certificates/incidence-network.json)
includes an exhaustive check of all 893,970 ordered disjoint pair instances
underlying the rectangle partition. This changes the scalar circuit and its
frames, so the bounds on pooling unchanged trajectories do not apply.

## Preserved stage-sharing improvement

An explicit matching lets the first and third stages share their side scratch
roles. Each invocation restores arbitrary initial scratch values. The matching
also makes the connecting frame labels nested, so sharing introduces no extra
rank loss. This removes one third of the side roles while preserving the
absolute rank deficit. The complex network is unchanged.

That witness uses bit saving `a_b = 27/10^12`, while the retained complex saving is
`a_c = 9/500000000000`. Set `tau = 1-a_b`, `sigma = 1-a_c`, and use the tuning
recipe below with `a = a_b`. The exact minimum margin is

$$
G=\frac{3a_{\rm b}^2}{70}\approx3.1243\times10^{-23}>2^{-75}.
$$

The [proof](notes/stage-reuse-note.tex) accounts for scalar restoration, the new
edge ranks, every role's endpoint identity, and the separate primitive
exponents. The [certificate](certificates/stage-reuse.json) checks counts and
all downstream parameter inequalities. Finite tests check the full h=46
matching, small rational projectors, and a complete h=6 shared-scratch circuit.
The earlier fixed-network ceiling does not apply to these changed role counts.

## Preserved parameter improvement

The new witness combines direct routing with the previously audited variable
stopping threshold. With `a = 9/500000000000`, set

$$
\epsilon=\frac1{21},\quad \beta=\frac9{10},\quad c=\frac{9a}{10},\quad
\lambda=1-\frac{19a^2}{20},\quad \lambda'=1-\frac{9a^2}{10}.
$$

The network and routing schedule stay the same; the dimension and recursion
stopping parameters change. Exact checks give `G = 3a^2/70 > 2^-76`.
The guard remains sublinear: `epsilon C1 = 20/21 < 1`.
The [tuning note](artifacts/routing-tuned-note.pdf) audits composition, precision,
and setup, and gives a transferable recipe for `0 < a < 1/16` with compatible
primitive interfaces and `C1 = 20`.

A simple necessary bound under those fixed primitive exponents and layer
constraints is `kappa < a^2/(20(1-a)) < 2^-75`. This is not an exact optimum
or a ceiling for stronger primitives or improved cost accounting.

## Further search and its boundaries

The [research log](docs/research/network-search-log.md) records the bounded
investigation that found stage sharing. The [scoped bounds](docs/research/network-screens.md)
exclude improvement from thinning the original triple family or using unequal
factor sizes, and limit one shared binary aggregation hierarchy. These are
family-specific results. The [next-step roadmap](docs/research/next-steps.md)
distinguishes concrete search targets from speculative stronger primitives.
The [block-label feasibility audit](docs/research/block-label-feasibility.md)
rules out several simple models for the proposed 2^-59 target; it does not
establish a new construction or a stronger multiplication bound.
The [additive-label obstruction](docs/research/additive-label-obstruction.md)
and [exact small control](docs/research/small-block-control.md) further narrow
the search; the small control does not have a positive network deficit.
The [quick 67 screen](docs/research/quick-67-screen.md) also excludes that
milestone from further pooling of the unchanged scratch trajectories.

The [packed movement audit](docs/packed-movement-audit.md) reduces a constant
swap count and sharpens the layer recurrence, but finds no stronger exponent
certificate from those changes. The root cost still forces `c = O(a)` under
the audited estimates. It identifies the stronger sparse-bit movement bound
that would be needed to remove this restriction. The 2^-75 result comes from
the stronger network, not from that recurrence refinement.

## The routing improvement and first witness

The new routing schedules use direct nonadjacent swaps already supported by
the manuscript. CRT axis reversal needs floor(d/2) field interchanges; exposing
and restoring all resampling axes needs at most 2(d-1). This replaces the
original O(d^2) count of adjacent moves by O(d) full-field interchanges.
The finite network and numerical operations remain the same as in our earlier
h = 46 construction. The exact sequence of data-movement operations changes.

The normalized layout cost improves from `d^2(1 + ell^tau)` to
`d(1 + ell^tau)`. Its exponent margin therefore becomes

$$
g_4=(1-\tau)(1-\epsilon),
$$

which permits a fixed dimension exponent `epsilon = 1/40`. With
`a = 9/500000000000`, the other choices are

$$
\tau=\sigma=1-a,\quad \beta=\frac12,\quad c=\frac a2,\quad
\lambda=1-\frac{3a^2}{4},\quad \lambda'=1-\frac{a^2}{2},\quad
\delta=\frac1{16},\quad C_1=20.
$$

Exact rational arithmetic gives

$$
\min_i g_i=\frac{a^2}{80}=4.05\times10^{-24}>2^{-78}.
$$

The [routing audit](docs/nonadjacent-axis-audit.md) checks coordinate order,
padding, coefficient records, fixed tapes, descriptor costs, precision, and
all remaining parameter dependencies. The routing change itself uses primitives
already present in the source. With OpenAI's original network and recurrence
exponents unchanged, it also supports the simpler bound **kappa = 2^-107**.

## The earlier parameter-only result and its ceiling

Our [first note](artifacts/parameter-note.pdf) gives `kappa = 5.8e-33` under
the original layout cost accounting. Within the stated network-counting
family and those cost inequalities, it establishes `kappa < 5.838e-33`, even
allowing variable `beta` and unequal `tau` and `sigma`. The exact search covers
every admissible integer h, using a decreasing bound for the infinite tail.

That ceiling remains valid for its stated assumptions. The original layout
cost forced `epsilon < a`, yielding a cubic constraint `kappa < a^3`.
The new schedules improve that cost and remove the restriction. With a fixed
epsilon, the supplied saving instead scales quadratically in a. We do not
claim that quadratic dependence is unavoidable or that the latest bound is optimal for
the revised accounting.

## What has been checked

| Component | Status |
| --- | --- |
| Parameter inequalities and logarithm bounds | Exact rational certificates |
| Network-counting search and its infinite tail | Exact rational certificates |
| Nonadjacent routing, parameter dependencies, and earlier variable-beta extension | Written mathematical audits |
| Selected finite identities | Exhaustive small cases and deterministic sampled tests |
| Stage-sharing construction | Written frame proof, complete matching and finite scalar checks |
| Fixed-exponent parameter refinement | Independent rational arithmetic, integrated circuit checks, scoped supremum enclosure |
| Source patch application | All seventeen alternatives checked by `make verify` |
| Full upstream multiplication theorem | Assumed; not independently established here |

The scripts do not constitute a formal proof of the complete algorithm. This
repository contains no full multiplication-machine implementation or Lean
formalization of the claimed bound. Independent review is welcome, especially
of the finite-network interfaces and fixed-tape recurrence. See
[the audit's remaining work](docs/audit.md#what-remains-before-an-unconditional-claim).

## Reproduce

From the repository root, with Python 3.11 or newer, Git, and Make:

```sh
make verify
```

The mathematical checks use the Python standard library and bundled source;
no package installation or network access is needed. The command regenerates
the certificates and patches, runs the tests, verifies upstream hashes, and
checks each patch against the pinned manuscript. On a clean checkout, generated
files should have no changes:

```sh
git diff --exit-code -- certificates patches
```

To rebuild the latest PDF, install Tectonic and run `make dag-note`;
`make incidence-note` rebuilds the preceding rectangle-circuit note,
`make reuse-note` rebuilds the preceding stage-sharing note,
`make tuned-note` rebuilds the parameter tuning note,
`make audit-note` rebuilds the routing proof, and
`make note` rebuilds the earlier parameter-only note. The first run may
download TeX resources. See [reproducibility details](docs/reproducibility.md)
for individual commands and how to apply a patch in a disposable copy.
[GitHub Actions](.github/workflows/verify.yml) runs the numerical and patch checks.

## Alternative patches

Each patch applies independently to the unmodified pinned source.

| Patch | Certified conditional saving | Scope |
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
| **[h46-dag-63](patches/h46-dag-63.patch)** | **`2^-63`** | **Shared intermediate sums, reversible role allocation, full auxiliary sharing, routing, and parameter tuning** |
| [h46-shared-point](patches/h46-shared-point.patch) | `13*2^-66` | Cross-common-point sharing with retained guard and assembly accounting |
| [h50-paired-59](patches/h50-paired-59.patch) | `2^-59` | Paired circuits, stopped-depth guard, and tighter Gaussian width |
| **[h50-paired-tuned](patches/h50-paired-tuned.patch)** | **`1.7523184e-18`** | **Paureel's fixed-exponent parameter refinement of the paired construction** |

Machine-readable results are in [parameters.json](certificates/parameters.json), [network-search.json](certificates/network-search.json),
[nonadjacent-axis.json](certificates/nonadjacent-axis.json), and
[routing-tuned.json](certificates/routing-tuned.json), and
[stage-reuse.json](certificates/stage-reuse.json), and
[incidence-network.json](certificates/incidence-network.json), and
[dag-network.json](certificates/dag-network.json),
[paired-network.json](certificates/paired-network.json), and
[paired-tuned-parameters.json](certificates/paired-tuned-parameters.json). The first note also gives
a closed-form supremum for the earlier fixed-`beta` parameter problem.

## Attribution, citation, and license

Author: **Douglas Colkitt**. The research, implementation, and drafting were
performed with assistance from OpenAI Codex. This assistance is not independent
review or endorsement by OpenAI. No priority claim is made.

The fixed-exponent paired parameter refinement and supremum analysis in this
fork are by **Aurel Prosz (Paureel)**, developed in the “Improve Integer Mult
Bounds” project with assistance from OpenAI ChatGPT and integrated with assistance
from OpenAI Codex. The preceding constructions and proof extensions remain
attributed to Douglas Colkitt and the underlying manuscript to OpenAI.

The original manuscript is by OpenAI. Its source is pinned at commit
`adc7f1241b42e322a6451854ab7e4b4c146bf78a`, with URLs and SHA-256 hashes in
[upstream/manifest.json](upstream/manifest.json). The files under `upstream/`
are preserved unchanged; modifications are distributed as separate patches.

Use [CITATION.cff](CITATION.cff) for this project and also cite the
[upstream manuscript](upstream/README.md) when discussing the multiplication
bound. Until a release is archived, include the repository commit you used.

Licensed under [Apache-2.0](LICENSE). See [NOTICE](NOTICE) for attribution and
[CONTRIBUTING.md](CONTRIBUTING.md) for review and contribution guidance.
