# Five-subset shared nodes: sharp nine-coordinate threshold

**Structural geometry research note; no new kappa or paid supplier.** In the
historical orthonormal-residual interface, a doubly degenerate two-source,
two-target shared node with constant-weight-five labels first exists at
ambient dimension **nine**. This changes the label alphabet in the triple-only
ten-coordinate classification of [woklerx's PR1139](https://github.com/CrocSwap/integer-mult-bounds/pull/1139).
It does not lower the eight-coordinate floor for unrestricted norm-one labels
already attained in [ArnavSwiggy's PR920](https://github.com/CrocSwap/integer-mult-bounds/pull/920).

From the repository root, Python 3.9 or later, standard library only:

```sh
python3 -I -B research/five-subset-shared-node-seed48/verify.py
python3 -I -B research/five-subset-shared-node-seed48/independent.py
```

The first command prints
`PASS_FIVE_SUBSET_SHARED_NODE threshold=9 rectangles_h9=453600 canonical_frames=59520 residual_bases=4 no_new_kappa`.
The second independently exhausts all labeled rectangles at h=8,9 and checks
the four residual bases using coordinate sets. Its final lines are
`PASS_INDEPENDENT_FIVE_SUBSET_RECTANGLES h8=0 h9=453600` and
`PASS_INDEPENDENT_RESIDUAL_BASES dimensions=3,3,4,4`.
Both commands are offline, read-only and retain checks under optimized Python.
The optional `verify.py --write-certificate` regenerates only this package's
certificate. See [VALIDATION.md](VALIDATION.md) for completed checks.

## Precise local class

Labels are incidence vectors of five-subsets of a labeled h-coordinate ground
set, in the standard dot-product space F2^h. Each side is an unordered pair
of distinct labels; source and target sides are distinguished. Require:

1. Both endpoint spans E=span(s1,s2) and T=span(t1,t2) are degenerate, so
   both pair intersections have odd size (one or three).
2. Every cross dot product is zero, and the 2x2 signed scalar matrix
   K(s,t)=Re(i^|s intersection t|) has rank one over Q.
3. E intersects T only in zero.
4. A nondegenerate U satisfies E subset U subset T-perp, and all four
   incident residuals U intersect si-perp and U-perp intersect tj-perp
   have orthonormal bases.

The historical side kernel has a common factor 1/2, irrelevant to its rank.
The label lines and target hyperplanes are fixed; no copied carriers, phases,
multiple shared nodes or relaxed residual contract enter this class.
The lower bound is proved in [PROOF.md](PROOF.md), independently of enumeration.

## Exact nine-coordinate witness

Masks use zero-based coordinates, with bit i representing coordinate i:

```text
sources = (31,481) = ({0,1,2,3,4}, {0,5,6,7,8})
targets = (47,87)  = ({0,1,2,3,5}, {0,1,2,4,6})
K = [[1,1],[-1,-1]]
U = span(31,481,3,40), dimension 4
w_U = 40, w_(U-perp) = 471
```

U and U-perp have orthonormal bases `(28,55,481,482)` and
`(47,59,67,131,259)`, respectively. The exact incident residual bases are:

| Endpoint | Orthonormal basis | Dimension |
| --- | --- | ---: |
| Source 31 | 52,457,458 | 3 |
| Source 481 | 28,55,482 | 3 |
| Target 47 | 59,67,131,259 | 4 |
| Target 87 | 131,279,367,379 | 4 |

Both implementations compare each basis's complete generated vector set with
the actual residual and check every Gram-matrix entry. These dimensions are
local geometry, not a paid recursive profile.

## Completed finite coverage

Coordinate permutations reduce source pairs to intersection sizes one and
three. At h=8 only intersection three is possible. At h=9, every valid
rectangle has a dimension-four frame, and each has exactly **48** such legal
frames. The complete canonical frame census tests all 155 two-dimensional
subspaces of T-perp/E for every rectangle: **59,520** candidates total.

| h | Source intersection | Compatible target labels | Canonical valid rectangles | Labeled source pairs | Labeled rectangles |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 8 | 3 | 11 | 0 | 840 | 0 |
| 9 | 1 | 32 | 288 | 315 | 90,720 |
| 9 | 3 | 30 | 96 | 3,780 | 362,880 |

The independent implementation visits every labeled source pair and every
cross-compatible target pair, using set intersections, literal integer kernel
values, determinants and explicit nonzero spans. It imports no primary code
and uses no symmetry multiplier. It also checks source/target swap symmetry.
At h=8 all 4,200 degenerate signed-rank-one candidates fail common-span
disjointness. At h=9 there are 511,560 such candidates, of which 57,960 fail
that condition. The survivors total **453,600**.

The seed is **48**, one fresh OS-random draw. It selects structural decoder
research and the odd-weight-five extension, rather than another triple or
current-frontier search. The fixed domain, three candidate tasks, scope,
stopping rule and local claim are in [CLAIM.json](CLAIM.json). This is complete
finite coverage at h=8,9, not an all-dimension census or a formal proof of the
full multiplication theorem.

## Cost decision, scope and attribution

This mechanism changes copied-information geometry by changing the label
alphabet. No complete cost improvement follows. Even setting local operations
optimistically to zero leaves global label coverage, source access, scalar
gates, helper stock, frame changes, copies, compensation, restoration, recursive
children, whole-call hosting, precision/tape and analytic transfer obligations
unresolved. No global decoder is implemented or fed to assembly. The experiment
stops after the sharp local threshold, witness and exact census; it does not
reopen the rejected fixed h=26 parity-DAG repair with more computation.

Exact base: **ce7ad1b6ab09452c3478723a2e96ed5ff212dc08**. The reviewed selected
result at this base is PR1094 with conditional
kappa=836330098538459/500000000000000000. Its manifest, actual rare-pattern
construction, assembly certificate and maintainer review were followed.
Neither the selected frontier nor upstream/ is changed. [SOURCES.json](SOURCES.json)
records exact source commits and hashes, including pending PR1139's proof.
Our lower-bound proof restates the small triple classification with attribution,
so reproducing the new certificate requires no pending code or network access.

Credit Douglas Colkitt's historical parity-side kernel and frame obstruction;
ArnavSwiggy's PR920 for the residual criterion, four-plus-four floor and general
norm-one fixtures; woklerx's PR1139 for the triple support classification; and
the seed47 frame-completion note for the distinction between separating frames
and legal incident transfers. No predecessor implementation is imported.

Prepared for GitHub contributor **ToikY**, with substantial **OpenAI Codex**
assistance in mathematics, implementation, algorithmically independent checks,
review and writing. This is not independent human peer review. New files are
under Apache-2.0, matching the repository.
