# Scoped copy-cost obstructions for Gaussian E8 decoders

This mathematical note closes three restricted routes toward a cheaper asymmetric decoder for the 60 Gaussian E8 lines.
It gives a general rank proof and exact finite incidence certificates.
It does **not** determine the unrestricted optimum, construct a better supplier, or change the selected kappa.

## Model and results

Use the standard positive-definite Hermitian form on `K^4`, where `K = Q(i)`.
Let `G` be the Gram matrix of the 60 distinct Gaussian E8 lines.
A scalar binary decoder has

```text
B = sum_j 1_Rj 1_Aj^T over F2,
B[i,i] = 1,
B[i,j] = 0 for distinct nonorthogonal lines i,j,
C = sum_j beta_j,    beta_j = rank_K G[R_j,A_j].
```

Entries on orthogonal pairs remain free, independently in both directions.
The model permits any finite number of totals and repeated supports.
Every charge refers to physical pairing rank, not binary matrix rank.

| Result | Exact scope | Conclusion |
|---|---|---|
| [General rank theorem](PROOF.md) | Each total has joint support dimension at most two, or `beta_j = min(|R_j|,|A_j|)` | `C >= 60`, with equality attained |
| [Six-line plane incidence theorem](search/SIX_PLANE_OBSTRUCTION.md) | Every reader indicator lies in the binary span of the 30 full six-line planes; sources are arbitrary | All fitting diagonal entries vanish |
| [Hyperplane coefficient identity](geometry/HYPERPLANE.md) | Full 15-line hyperplane rectangles with equal or orthogonal normal lines: 960 ordered types | Every fitting decoder costs at least 180 |

The first theorem holds for any finite set of distinct lines in a positive-definite Hermitian space.
It permits asymmetric totals and overlapping planes.
It includes mixtures of planar replacements and the standard orthogonal-frame decoder.
The exact Gaussian certificate supplies fifteen disjoint four-line frames with total cost 60.

The six-plane theorem also holds after transposition.
Adding rectangles that individually have no forbidden entry gives a cost floor of 60.
Its short witnesses are eight-line nonorthogonal sets that intersect each six-line plane in zero or two lines.
The proof applies to arbitrary source supports, beyond the 900 full-plane pairs checked directly.

The hyperplane result permits arbitrary repetitions of its 960 types.
It excludes the other 2,640 unequal-normal types and partial hyperplane supports.
An exact cost-820 witness establishes feasibility; we do not claim that 820 is optimal.

These are **separate classes**.
Their unrestricted mixtures do not inherit the stated bounds.

## What an improvement must change

The general theorem gives the necessary condition

```text
60 - C <= sum over positive-cost nonplanar totals j of
          (min(|R_j|,|A_j|) - beta_j).
```

Thus a saving needs a nonplanar rectangle with deficient pairing rank relative to both support sizes.
Such rectangles exist in the actual Gaussian geometry.
For example, supports `{0,1}` and `{0,3}` have pairing rank one but joint support dimension three.
The exact certificate checks this example and a pairing-rank-two example whose joint support spans all four dimensions.
Neither example is itself a fitting decoder.

The six-plane obstruction shows why filling those supports to whole six-line planes does not resolve the fitting equations.
The hyperplane identity blocks another natural attempt to use low pairing rank.
Partial supports and coupled mixtures remain unresolved.

## Optimistic complete budget

This application assumes the existing stage accounting, including axiom Dfc in the [format-limit note](../format-limits-corrected/README.md).
The abstract decoder theorems do not depend on that accounting.

A Gaussian line has rational rank `k = 2`.
There are `v = 60` ports, and the rational copy charge is `cst = 2C`.
For any covered class with `C >= 60`, the inherited deficit satisfies

```text
D/T = (s - 1) v k - s cst
    <= 120(s - 1) - 120s
     = -120
```

for every positive stage count `s`.
For the 960-type hyperplane class alone, `C >= 180` gives `D/T <= -120 - 240s`.
Even zero additional expense for helpers, source access, frame changes, restoration, and recursive children cannot give a positive deficit.
This failed optimistic budget stops physical supplier implementation for these mechanisms.
Other supplier or assembly constraints cannot repair this local deficit within Dfc.

## Reproduce

Run from the repository root with Python 3.9 or later:

```sh
python3 -B research/gaussian-e8-asymmetric-copy/verify.py
```

Expected final line:

```text
PASS: Gaussian E8 scoped copy-cost obstructions; unrestricted optimum remains open.
```

The replay uses only the standard library and exact integer or rational arithmetic.
It rebuilds the roots, line orbits, flats, pairing ranks, and finite binary certificates.
It compares the rebuilt certificates with the saved data.
Independent rational realification checks 480 ranks.
The finite checks support the written proofs; they are not a proof-assistant formalization.
See [VALIDATION.md](VALIDATION.md) for coverage and negative controls.

## Provenance and status

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
The existing selected conditional result remains unchanged.
This work addresses the Gaussian copy-cost question in [PR620](https://github.com/CrocSwap/integer-mult-bounds/pull/620).
[PR703](https://github.com/CrocSwap/integer-mult-bounds/pull/703) supplies related matching-geometry precedent for the distinct quaternionic system.
The new contributions are the planar grouping and deletion theorem, the six-plane incidence identities, and the hyperplane coefficient identity.
Neither proof relies on the predecessor's reported SAT minrank or solver lower bounds.

The final overlap check finds concurrent [PR738](https://github.com/CrocSwap/integer-mult-bounds/pull/738), which reports a general cost floor of 40.
We inspect its weighted-clique proof but do not replay its finite certificate here.
Our contribution gives stronger obstructions for the stated subclasses and distinct incidence identities.
It does not improve PR738's general lower bound.

[SOURCES.json](SOURCES.json) pins the source state and retained files.
[NOTICE.md](NOTICE.md) credits the predecessors and discloses substantial AI assistance.
The local claim and bounded search record appear in [CLAIM.md](CLAIM.md) and [SESSION.json](SESSION.json).
