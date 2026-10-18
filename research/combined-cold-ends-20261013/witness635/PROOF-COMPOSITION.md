# Exact composition of the h4a and factored cold ends

Chi Zhao, with substantial OpenAI Codex assistance. Apache-2.0.
This composes Jeremy Kothe's PR629 h4a construction with Jeremy Diviney's
PR627 factored ends, retaining their predecessors and verifier assumptions.

## The compatibility problem

Both packages use the same pinned JP8 hyperplane-ended input, content SHA-256
`a51b37b5bd5e9e66ea14e9759f88cb6181bab041cb09aecd08e7a11956100016`.
Their additional terminal helper sets are disjoint, but concatenating the
premixes, absorptions and lower-frame tails is not sufficient. PR629 changes
the joint cold basis. The nominal helper 581 row also gains data coefficients
`(e90 + e91 + e94 + e95)/4`. A cold-coordinate premix cannot remove data
coefficients, so the combination needs an additional legal absorption before
its final cold-basis correction.

## The additional absorption

At original input-A anchor 1665, after the inherited and factored absorptions,
insert

```
q95 += S403 / 4     at [265,137,96,6].
```

Both operands already occupy that four-dimensional frame, so the gate adds no
paid climb. The input word never subsequently touches q95. The unchanged
PR629 constructor independently verifies these conditions and the stable
order of multiple absorptions at one anchor.

A separate sparse Fraction replay in `tools/check_basis_proof.py` derives the
following identities without importing the constructor or native auditor:

* At that position, the projection of S403 onto non-cold coordinates is
  `-2(e90 + e91 + e94 + e95)`.
* Its recipient q95 has coefficient `1/2` in the final row of helper 581 and
  coefficient zero in every other ended helper row.
* The extra absorption therefore cancels exactly the four `1/4` data
  coefficients, leaving `row581 = e581 + (e406-e373)/2`.
* The remaining new row is
  `row590 = e590 + (e421-e423+e391-e388)/2`.

Both row defects now lie entirely in cold coordinates.

## Ten rank-zero basis corrections

The exact correction prefix, in execution order, is

```
S323 -= S590
S309 += S590
S590 += S388/2
S590 -= S391/2
S590 += S423/2
S590 -= S421/2
S321 -= S581
S308 += S581
S581 += S373/2
S581 -= S406/2
```

All operands are cold helpers and all gate frames are empty. These gates
precede the nominal combined premix, inside the inherited paid wrappers.
After the row corrections, exact inverse columns are
`e308-e321+e581` and `e309-e323+e590`; these give the displayed cold column
corrections. The independent proof checker verifies that all 64 ended
helper rows and columns, including every inherited end, are then isolated
identity coordinates. It also verifies that the target rows contain no dirt
from these ended helpers; the native compensation-before-wrapper guard is
rechecked independently rather than inferred from this basis argument.

The remaining 540 non-target, non-ended coordinates are eliminated exactly
using signed-dyadic-unit Gauss–Jordan pivots at FULL. No remainder gate touches
an ended helper or target. The construction verifies all remaining identity
rows, then the unchanged native auditor independently replays arbitrary dirt
in both orientations, recomputes compensation and cones, and checks every
frame and paid-profile count. This is a refactored cleanup, not an assertion
that reversing an incompatible predecessor cleanup works.

## Profile and admission

Against the PR622/PR623 JP8 word, the combined local profile change is
`{1:+6, 2:+2, 4:+4, 5:-2, 6:-4}`, with rank mass reduced by eight.
The JP8 profile is `{1:2518,2:402,3:448,4:164,5:68,6:4,8:8}`. Raw helpers
243, 275, 307 and 339 have width eight; helpers 581 and 590 have width seven.
The CK word is exactly PR629's h4a word. Both words retain 492 helpers.

Every verifier file in `code/` and `verify.py` is unchanged from the pinned
PR629 head. The combined recipe passes all 46 inherited cold-end mutations.
The added composition controls include a positive replay, omissions of each
of the ten correction gates, and omission/sign reversal of the additional
absorption. All twelve corruptions must be rejected. The full strict wrapper
also rebuilds the baseline, suppliers, reflected local programs, residual
wrappers, exact phase edges, physical owner controller, finite invoice and
both exact moment engines. The owner map is certified as one simultaneous
literal allocation; supplier and packing savings are not added numerically.

The deterministic nominator retains pinned PR629 recipe and PR627 factored
primitive inputs and reproduces the exact combined recipe and raw word.
Nomination and search are not admission. The inherited all-size, common-label,
mutable-source, whole-call hosting, precision/tape/exact-recovery, analytic
transfer and bit H1–H5 assumptions remain open.
