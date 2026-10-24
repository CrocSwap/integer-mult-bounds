# Independent native review of the two response extensions

The reciprocal-large and rank-sixteen words pass the independent native
checks. Each complete word implements its declared response on all 640
input roles in both directions. The two actual providers have identical
words and port directions.

The reciprocal-large word uses the exact rank-thirty native sequence.
The rank-sixteen word uses 685 exact inherited ordered frame pairs and
876 new edges. All 876 new recipes pass all 512 spatial columns, including
global phase. The 224 endpoint adapters are unchanged.

## Frozen inputs

The consumed
[extension freeze](../../new-core-transfer-20261017/low-displacement-20261020/EXTENSIONS-FREEZE.json)
has SHA256
`aec99dd0638e635619b14ffd056ab2581424d765d435462aed94b8c8f882a689`.
Only its final v2 payloads are used:

| Variant | Decompressed SHA256 |
| --- | --- |
| reciprocal-large | `e4df61bf4e121364ba53538eb2ad612bd314807cfb2050050d4595efce9cf416` |
| odd-grid-rank16 | `d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4` |

The accepted base phase dependency is
[NATIVE-REVIEW-FREEZE.json](NATIVE-REVIEW-FREEZE.json), at SHA256
`cfdc4fa0361aa79c1d53a59ff48bdde1715ea8e3eb6b9efbc109c97bcc44a976`.
Its complete input and result receipts are pinned in the extension
checker. The extension does not repeat an inherited phase calculation.

The separate
[matrix extension review](../../independent-review-20261017/response-extensions-review-20261020/FREEZE.json)
has SHA256
`1c20e6736b1109ce10746472d3e00d464d5ea2629fe30c37a9d51bd5b74feedc`.
It owns the reciprocal identities, correction rank, principal inverses,
and clique geometry. This review checks that the literal native streams
implement those final matrices. The complete inputs are in
`extensions-normal/EXTENSIONS-INPUTS.json`.

## Inherited and fresh physical operators

A phase recipe is inherited only when both ordered frame bases and the
complete recipe are exactly equal to an accepted base entry. Equal
subspaces, equal native ranks, or equal frame names are not sufficient.

For the reciprocal-large variant, the entire native occurrence sequence,
frame table, and recipe table are equal to the base word. There are 1141
inherited edges and no fresh edge. Scalar coefficient changes and
omitted zero-coefficient ADDs do not change this native sequence.

For the rank-sixteen variant, all 685 inherited entries pass that exact
comparison. Each of the other 876 entries is checked as

\[
 R T_{\mathrm{old}}=T_{\mathrm{new}}
\]

on all 512 spatial basis vectors. The independent sparse Gaussian
interpreter is the same as in the base review. It imports no producer,
Clifford compiler, or producer phase checker. The fresh checks cover
448512 complete columns and 41619456 exact nonzero coefficients.

All entry and final frame IDs retain their exact ordered bases from the
base word. The 224 stored endpoint adapters are equal to the accepted
records. Their previously checked physical phases therefore apply
without a new endpoint sweep.

## Complete data maps and legal access

For either variant, let \(A\) be the response in that variant's final
model. The literal maps are

\[
 F_A:(x,y,h)\longmapsto(x,y+Ax,h),\qquad
 B_A:(x,y,h)\longmapsto(x-A^{\mathsf T}y,y,h).
\]

The physical input is \(X=Qx,\ Y=y\). The physical output is
\(X=F_9x'\), \(Y=F_9Q^{-1}y'\). No response matrix is moved through \(Q\).
In particular, the backward map does not use \(A^{-1}\).

The frame ledger verifies each native entry, each strictly nested exit,
each rank difference, each equal-frame scalar ADD, and every final
frame. It also checks that transfer metadata selects the actual ADD.
The complete reverse coefficient propagation checks every one of the
640 input columns in each direction. An omitted nonzero transfer is
rejected for both variants and both directions.

Every operation is confined to the 224 data roles. All 416 other live
roles retain their arbitrary values and frames. There are no owned
fields, private fields, CLEAR operations, or hidden source accesses.
As in the base word, this supplies no productive progress on those roles.

For the reciprocal-large variant, the separate matrix review proves

\[
 A=E_{48}^{-\mathsf T}\oplus C.
\]

Thus the backward map supplies the old large-sector inverse
\(-E_{48}^{-1}\). The small sector still supplies \(-C^{\mathsf T}\),
not \(-C^{-1}\). The native review preserves this exact scope.

## Local invoices

| Variant | Native profile | Children | Mass | Real scalar primitives |
| --- | --- | ---: | ---: | ---: |
| reciprocal-large | 1036 H1 + 48 H3 + 55 H4 + 55 H5 + 9 H6 + 9 H7 | 1212 | 1792 | 5288 |
| odd-grid-rank16 | 1520 H1 + 64 H2 + 48 H3 | 1632 | 1792 | 7384 |

Both directions have the stated profile and scalar bill. Each word has
224 external endpoint maps. The native side-map upper bounds are 2424
and 3264, respectively. These maps are not treated as free.

The native mass still telescopes to eight per data role. The number and
sizes of the children change. Equal mass alone therefore does not prove
equal recursive cost.

The exact top-level array norm bounds are 30 forward and 46 backward
for the reciprocal-large variant. The rank-sixteen bound is 22 in either
direction. These are bounds at the literal event boundaries, not on
recursive or scalar primitive internals.

The scalar price check admits only nonzero dyadic ADD coefficients and
dyadic unit scales. Every native phase recipe has Gaussian-dyadic
entries. No odd division occurs in either emitted native word.

## What the rank-sixteen word does not implement

The separate matrix review proves that the rank-sixteen response is an
integer matrix whose correction has rank sixteen. Its inverse uses
denominators five and seven. The selected ordinary normalization also
uses prime 31.

Those inverse matrices are metadata and later code requirements. They
are not native instructions in the word checked here. This review does
not turn division by five, seven, or 31 into a dyadic scalar primitive.
It does not prove the retained-grid conversion, a denominator-height
bound, legal access for the inverse queries and scatters, or the final
conversion.

The rank-sixteen opportunity changes two restrictions. It uses an inverse
with a nonzero diagonal as a later scalar code, and it permits the odd
denominators needed by that code. Odd denominators alone do not defeat
the earlier reciprocal zero-diagonal rank-two obstruction.

Recursive child hosting, productive helper progress, the full precision
bound, stage access, terminal removal, and the complete supplier remain
open. The selected frontier and the complete kappa calculation do not
change as a result of this local review.

## Reproduction

First reproduce the base native review. Then run, from the workspace
root:

```text
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 -B work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/low-displacement-review-20261020/check_extensions.py --out work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/low-displacement-review-20261020/extensions-normal
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 -O -B work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/low-displacement-review-20261020/check_extensions.py --out work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/low-displacement-review-20261020/extensions-optimized
```

The expected final line is:

```text
PASS_INDEPENDENT_NATIVE_EXTENSIONS
```

Both final runs passed, with byte-identical result and input receipts.
The extension review freeze records that comparison and the final input
hash check. All producer and base-review bytes are
preserved. The source packets retain credit for the response, cyclic
flags, pair factors, and phase construction. AI assistance was used.

No PR, push, commit, or publication is authorized. Before any future PR
description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
