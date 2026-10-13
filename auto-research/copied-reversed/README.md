# Reversed corners with copied retained centers

Under the inherited analytic and fixed finite-alphabet multitape hypotheses,

$$T(n)=O(n(\log n)^{1-\kappa}),\qquad
\kappa=\frac{3850771033}{10^{14}}=3.850771033\times10^{-5}>2^{-15}.$$

This combines icekylinx's copied-center schedule from
[PR #36](https://github.com/CrocSwap/integer-mult-bounds/pull/36), pinned at
`11817ccacb564bb7f98789c20dc11d3fece207e3`, with James Chang's reversed boundary
family from [PR #34](https://github.com/CrocSwap/integer-mult-bounds/pull/34),
pinned at `7fecbe3651e095fb0f450756afdeefd2a9ee80a2`, and the attributed balanced
semantic/bulk transfer. It improves the reported PR #36 saving 3.84569e-5 by
approximately **0.1321%**. This is a conditional asymptotic exponent comparison,
not a runtime measurement or a claim of global optimality.

## Geometry and copied-center compatibility

Instantiate the same two-stage topology with ordered factors **(23,25)**.
The producer pair is unchanged; the factors' stage assignments are exchanged.
This is a choice when constructing the circuit, not a free transpose of an
already constructed stream.

For h=23, prescribe the first d=47 row labels and last d inverse-column labels
as R=[0,...,22;22;0,...,22] and C=[0,...,22;0;0,...,22]. The fast coordinate
has dimension25 and the inverse-column residue offset is3. The actual
prescriptions have permutation completions. The first/last23 local corner
represents every first-axis projector up to nonzero diagonal scales; the
first/last25 corner does the same for second-axis projectors. Both auxiliary
blocks and the generic ordinary profiles therefore hold in the same free
GL23 x GL25 family.

PR #34's rank cuts are identities for every parameter value. The dimension23
specialization is checked by independent exact integer ranks and exact rational
nonzero prefix witnesses. Those rank cuts and pivots give the data profile
**9 singletons + [21,17,481]**, replacing PR #36's 11 singletons + [21,15,481].
In zero-based physical coordinates the21-block uses rows1..21 and columns
553..573; the17-block uses rows28..44 and columns530..546; the untouched middle
is47..527. All are actual contiguous intervals in the inherited order.

The copied-center schedule changes a full local transition into a rank-one
complement while retaining the paid rank-(h-1) copy transform. These are ordinary
local projectors covered by the same arbitrary-local contraction identities.
Their nonzero-minor conditions, the new data-prefix conditions and the
auxiliary conditions are nonzero rational functions on the same irreducible
basis family. A finite product supplies one simultaneous rational basis.
No gate receives its own runtime basis, and no coordinate gathering is free.

PR #36's copied-center scalar and frame identities are used in both invocation
orientations, including arbitrary dirty scratch. The untouched original stream
proceeds to cleanup; a separately charged transformed copy supplies the
read-only scatters. The new rank-one complements do not remove Paureel's
separate paid endpoint correction. That correction remains once per data pair.

## Complete physical accounting

The reordered construction has the same exterior-bank multiset, original
producer/carrier choices, copied-center local histograms and physical growth
fronts. With N=4,073,300, there are2N data macros. The only child-list change
from the pinned PR #36 construction is

- remove4N width-one children;
- remove2N width-15 children;
- add2N width-17 children.

The rank change is zero. The copied-center transforms are already included in
the local histograms; no extra copy is omitted or counted twice. Reconstructing
the whole list from the two producer records preserves:

| Quantity | Value |
|---|---:|
| Arity m | 575 |
| Producer-pair count N | 4,073,300 |
| Role volume W | 188,181,929 |
| Weighted local loss L | 2,226,400 |
| Total child rank Wm - N + L | 108,202,762,275 |
| Deficit N - L | 1,846,900 |
| Largest child | 529 |
| Paid endpoint width-one corrections | 4,073,300 |

For every exponent0<tau<1, the moment numerator decreases by
2N*(17^tau -15^tau -2)<0. This follows from the derivative tau*x^(tau-1)<1
for x>=1. It proves a strict profile improvement throughout that interval,
independently of the numerical search.

## Exact moments and balanced assembly

The exact bit saving is **962729831/25000000000000 = 3.850919324e-5**.
Rational logarithm and exponential enclosures prove the complete characteristic
strictly below one. The complex graph remains PR #36's (28,28) mixed-center
network, with saving717/10^7. Its scalar charge includes copied centers and the
paid inverse phase on a copy. In particular its semantic envelope is
**E=64*(W_complex +m_complex +G_scalar +1)^3**; the older envelope that omitted
G_scalar is not silently reused.

The completed-child semantic constant is C1=1. The product of bit and complex
row stocks remains bounded by p^2000. Copies are sequential, use the existing
complete role rows and contribute no independent row-index family.

The balanced transfer uses the attributed RaD common-low-bit layout, paid
arbitrary-coordinate router and bulk resampling, as audited in PR #34. For bit
saving a and h=10^-12, choose q=a(1-2h), c=q+h/4 and epsilon=(1-h)/(1+q).
The old geometric gap remains positive; its small value does not bound the
new prefix cost after the balanced physical construction. The controlling
margin is epsilon*q, strictly above the displayed kappa. All47 strict
constraints, seven margins and eventual cutoff comparisons are regenerated
with the actual new complex semantic constants.

## Reproduction and review scope

```sh
make copied-reversed-check
make copied-reversed-producer
make verify
```

Use Python3.11 or newer and the inherited C++ toolchain for producer rebuilds.
The source manifest pins every consumed predecessor input. The focused
[review patch](../../patches/copied-reversed.patch) applies to the pinned PR #36
commit; the inherited manuscript is unchanged. The new geometry
checks, exact child list, moments and assembly are reproducible separately.
Negative controls address bad corner offsets, invalid rank cuts, omitted paid
corrections, rank-preserving child-list corruption, old-prefix substitution and
invalid precision/row constants.

**Full verification passed** for research commit `cb86e50e9a07685068874d8e4174b2e6c209b95c`: 182 tests,
fresh selected complex and inherited bit/label reconstructions, and 18 historical
patch checks. The 12 focused tests also pass. The [validation receipt](validation.json)
records the exact commit and log hash. These are independent agent reviews and
executable checks, not external expert acceptance or formal verification of the
multiplication theorem.

The inherited Gaussian inverse and exact recovery, fixed tape/alphabet model,
ordered climb and complete spectator contracts, native rational basis/prime
setup, constructive catalogues, compact routing, bulk locality and eventual
thresholds remain explicit hypotheses. No practical running-time claim is made.

## Attribution

Rohan Arun, with substantial OpenAI Codex assistance, supplies this composition,
its dimension23 controls, independently rebuilt arithmetic and integration
review. The reversed family itself is James Chang's PR #34; the copied-center
schedule and mixed complex network are icekylinx's PR #36. The balanced transfer
is RaD/hipotures' attributed construction, specialized in PR #34. These source
contributions are not claimed as new inventions here.

Also retain Dominik Scholz's PR #33 parameterization, Rohan Arun/Codex's PR #31
incidence certificates, Zhihao Chen's PR #29/#21/#23 compatibility and semantic
interfaces, Aurel Prosz/Paureel's topology and paid correction, Swapnil Jain's
linked development, icekylinx's earlier producers/bases, eumemic, Douglas
Colkitt, OpenAI, Harvey--van der Hoeven and all preceding source notices.
New source is Apache-2.0; imported licenses and assistance disclosures remain.
