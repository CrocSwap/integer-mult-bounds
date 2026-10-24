# Proof and review map

This package joins an exact local construction and a limit for its
literal Haar-tree extension. The original evidence files are unchanged.
An amendment listed below is part of the corresponding statement.

## Geometry and density

The [affine access proof](evidence/lanes/portable-source-codes/correlated-access-20261015/ACCESS.md),
Sections 2 and 3, gives the sharp affine bound and the signed projector
identity. Its [independent review](evidence/lanes/residual-syndrome/physical-algebra/correlated-access-review/REVIEW.md)
proves the common-form radical argument. The affine odd-width phase is
proved in the local ODD-WIDTH.md packet cited below. The retained
ODD-WIDTH-AMENDMENT.md corrects the separate Bell-gauge statement in
ACCESS.md, Section 5. That section is background and is outside the
submitted claims.

For an affine direction space `L`, let `r` be the rank of the common
pulled-back row form and let `s_i` be the row radical dimensions. Then

```text
dim L <= r + sum_i s_i <= r+n floor((lambda-r)/2)
      <= n floor(lambda/2)+(lambda mod 2),  n>=2.
```

The pair code attains the last bound. The
[rigidity proof](evidence/lanes/residual-syndrome/physical-algebra/review-gauss/maximal-affine-sectors/RIGIDITY.md)
classifies all maximum-dimension pieces for `n>=3`. The `n=2` diagonal
counterexample remains part of the scope.

The [product-cover proof](evidence/lanes/residual-syndrome/physical-algebra/affine-sector-cover/COVERAGE.md)
and its [amendment](evidence/lanes/residual-syndrome/physical-algebra/affine-sector-cover/AMENDMENT.md)
use `a=x_1`, `E=omega^perp`, and `W_0=span(x_i+a)`.
The exact point criterion is

```text
wt(a)=d mod 4, W_0 subset E, and q_a vanishes on W_0,
q_a(w)=wt(w)/2+a.w mod 2 on E.
```

A binary quadratic-form extension puts each point in an optimal product
piece and gives the exact extension count. This is a Fourier-address
construction. It does not make the address readable or price a physical
choice among the pieces. The
[independent cover review](evidence/lanes/residual-syndrome/physical-algebra/review-gauss/affine-sector-cover/REVIEW.md)
accepts the proof with both amendment conditions.

The general density formula is in Sections 3 and 4 of the
[correlated-sector proof](evidence/lanes/coherent-port/shared-cover-quotient-20261015/QUOTIENT.md),
with its [scope addendum](evidence/lanes/coherent-port/shared-cover-quotient-20261015/ADDENDUM.md)
and [independent density review](evidence/lanes/residual-syndrome/physical-algebra/correlated-sector-review/REVIEW.md).
The signature quotient has order `2^((n-1)(n+2)/2)`. Its exact Gauss-sum
formula gives a positive limiting density. The package uses this general
formula and its exact `n=73` threshold. It does not claim or replay the
separate actual 17-axis frame maximality result.

## Local physical access

The [stream proof](evidence/lanes/residual-syndrome/physical-algebra/affine-projector-stream/STREAM.md)
and its [amendment](evidence/lanes/residual-syndrome/physical-algebra/affine-projector-stream/AMENDMENT.md)
give the full layout, address maps, work-tape cleanup, and precision
conditions. The [independent stream review](evidence/lanes/residual-syndrome/physical-algebra/review-gauss/affine-projector-stream/REVIEW.md)
accepts this local statement under the pinned stream assumptions.

After the paid binary map `P`, the signed Haar code `B` has leaf
selector `E` and satisfies `B^-1 E B=P Pi P^-1`. The map

```text
H(u,v)=((u-v)/2,(u+v)/2)
```

retains both outputs. Only its first output is refined. All details
remain available for the inverse. The active volumes form a geometric
sum. Thus the split and merge work is `O(V)` after the address maps.
Encoding both arbitrary fields, adding their leaves, and decoding gives
`(x,y)->(x,y+Pi x)`. No input baseline or complement is discarded.

The [odd-width proof](evidence/lanes/residual-syndrome/physical-algebra/affine-projector-stream/ODD-WIDTH.md)
and [independent review](evidence/lanes/residual-syndrome/physical-algebra/review-gauss/odd-affine-projector/REVIEW.md)
retain one leaf bit. A completed frame acts there by a Gaussian unit
times `I`, `C_u`, `X_u`, or `C_u^-1`. This is a paid two-point coefficient
operation on the compressed leaf. It is not an unpaid full-field child.
The total tensor phase convention and the possible extra address map
remain part of the frame contract.

The [one-pass-turn proof](evidence/lanes/residual-syndrome/physical-algebra/affine-projector-stream/ONE-PASS-TURN.md)
combines the three leaf shears before either field is decoded:

```text
x'=(I-Pi)x-Pi y,  y'=(I-Pi)y+Pi x.
```

For different admitted frames, the physical leaf map is
`(a,b)->(-D^-1 b,D a)`, with `D=O_t O_s^-1` in that order. It has
fourth power identity. Its
[independent review](evidence/lanes/residual-syndrome/physical-algebra/review-gauss/one-pass-turn/REVIEW.md)
is a proof review. The finite replay uses the producer's original
code primitives. The owner cuts mentioned in the frozen proof are
outside this package's submitted claim.

## Literal affine Haar-tree limit

The [split-limit proof](evidence/lanes/residual-syndrome/physical-algebra/affine-sector-cover/SPLIT-LIMIT.md)
and [independent review](evidence/lanes/residual-syndrome/physical-algebra/review-gauss/affine-split-limit/REVIEW.md)
allow branch-dependent affine tests, invertible affine chart changes,
and groups of literal splits with unequal leaf depths. Every detail
and rejected branch is retained. The forward record count is

```text
T = sum_(internal nodes v) |A_v|
  = sum_(all leaves l) |A_l| depth_l.
```

If no affine subset of the accepted set `S` has codimension below `k`,
every accepted leaf has depth at least `k`. Hence `T>=k|S|`.
For complete fixed-format records, the work is at least
`Omega(k delta V)`, where `delta=|S|/N`. For the all-odd sector,
`k` grows linearly in `lambda` and `delta` has a positive limit at
fixed `n`. This gives `Omega(lambda V)` in the stated class.

A direct block algorithm is not one free split. A method with
non-affine branches, overlapping cancellation, changed coefficient
formats, or productive native children is outside the proof. The bound
does not exclude a circuit that computes only a centre query.

## Verification boundaries

The fresh finite replay and the original independent reviews have
different roles. Exact finite checks verify identities, prefix bounds,
source pins, selected phase columns, extension counts, and retained
record counts. The written proofs give the all-width statements.

The complete recursive use remains conditional on a strict dependency
path envelope. The submitted result does not provide that envelope for
a changed internal controller. It gives no actual owner admission,
complete finite native invoice, new supplier, or kappa improvement.
