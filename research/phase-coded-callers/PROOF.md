# Proof contracts and exact scope

This document states the retained claims and connects them to the full
byte-exact proofs. It does not replace a general proof with finite test
results. Each source path and receipt is hash-bound in
[SOURCES.json](SOURCES.json). [CLAIMS.json](CLAIMS.json) gives the direct
proof and review map.

## 1. The 16/96 phase-coded local word

Use the ordered selected ports
`P=(0,27,36,111,20,7,57,46,1,3,6,8,17,18,24,23)` and the other 96
ports R. Let H be the actual 16 by 96 response matrix and `D=-H*`.
Let Q be the positive line operator and `q=Q^-1`, separately on each
physical input port. These operators do not commute through arbitrary
responses. Their source attachment and order must be retained.

The [local proof](frozen/work/centre-encoding-campaign-20261014/lanes/controller-followthrough-20261017/phase-coded-clean-20261020/PHASE-CODED.md) starts with the pinned clean late-exchange
word. It removes 592 ordinary cross-bank ADDs, retains the native
kernels, frames, and adapters, and inserts 96 physical unit ADDs before
the input adapters. Its formal maps are

```text
F_Q(a,u,z,v) = (-z, u, a+Hu, v+Q_R u),
B_Q(a,u,z,v) = (z, u+Dz-q_R v, -a, v).
```

For the Q-entry forward contract, physical inputs are `X=Q(a,u)`,
`Y_P=Q_P z`, and `Y_R=v`. The output X bank and selected Y bank are
FULL. Ordinary Y has the stated F9 q_R type. The initial I-entry
variant removes the selected input Q_P and replaces sixteen rank-eight
calls by rank-nine calls. The backward contract uses its declared
inverse orientation. The full proof gives the types at each event.

Each local word has 1,520 native children. The Q-entry profile is
`{1:1392,2:64,3:48,8:16}`, with mass 1,792. The initial I-entry
profile has sixteen rank-nine children instead of rank-eight children,
with mass 1,808. Each word costs
`1720+1760+384+768=4632` real scalar primitives. No owned or private
field and no odd division is added.

The [local receipt](frozen/work/centre-encoding-campaign-20261014/lanes/controller-followthrough-20261017/phase-coded-clean-20261020/final-normal/CHECKS.json) and the fresh package replay check
all 640 independent inputs for both providers and all three local
orientations. They check that all 416 arbitrary helpers return unchanged.
This replay regenerates the literal transcript. The spatial native
kernels and endpoint adapters are inherited exact records; the replay
does not regenerate their dense Clifford compilations. Their native
phase proof remains a separate pinned premise.

## 2. Three calls, three legal FULL shears, and the D25 terminal

The [D25 proof](frozen/work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/phase-coded-triple-20261020/PHYSICAL-ENDPOINT.md) uses the actual orthogonal stage routes G_s.
Set `H_s=G_P H G_R` and `D_s=G_R D G_P` in each current chart. The
routes fix the intrinsic line for their own stage. They do not make H
stage-independent. At the physical entry put
`(a,u)=qX0`, `z=q_P Y0_P`, and `v=Y0_R`.

Set `alpha=a+H_0u` and `r=D_1 alpha-q_Rv`. The full stage-1 cover
sweep and helper returns occur before the first added shear. At that
cut X_R and X_P are both FULL. Thus

```text
X_R -= D_1 X_P
```

replaces r by `-q_Rv`. After the last local call, the data are

```text
X = F25(-z,-q_Rv),
Y = F25(alpha-H_2q_Rv,u).
```

The two FULL output shears

```text
Y_P -= H_2 X_R,
Y_P -= H_0 Y_R
```

give `X=-F25 qY0`, `Y=F25 qX0`. This proves the endpoint for
arbitrary physical X0 and Y0. It never reads an ordinary hole through
a scalar shear. The [independent proof](frozen/work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/owner-review/phase-coded-triple-review-20261020/REVIEW.md) derives all
224 data columns with a separate phase engine. It verifies all 1,344
phase identities and all three complete FULL shear matrices. Its
negative controls reject omitted entry translations and the false
ordinary-FULL type.

The three shears use 648 complex ADDs, at most 6,144 real scalar
primitives, and 448 affine map calls. This is the direct coefficient
invoice; no smaller factored invoice is consumed. Three local calls
and these shears cost 20,040 scalar primitives before terminal wrappers
and map costs. The Q-entry words have 672 explicit local views; these
are distinct from the shear maps and native side maps.

The direct Q terminal uses 224 positive line calls. Its complete
profile is `{1:4400,2:192,3:144,8:48}` and mass is
`5376+224=5600`. The initial I-entry alternative uses 208 line calls.
Its complete profile is `{1:4384,2:192,3:144,8:32,9:16}` and mass is
`5392+208=5600`. These are two specified constructions. The 224 and
208 line counts are not universal lower bounds for every decoder.
An unsigned output convention adds 112 field signs, priced at 224
scalar primitives, unless the caller consumes the signed exchange.

Every positive child rank in either complete profile is below 25.
For `0<=sigma<1`, `r^sigma > r*25^(sigma-1)` at each such rank.
Summing gives a moment strictly above `224*25^sigma`. Thus these paid
profiles do not provide a strict moment improvement. This conclusion
does not rule out a different terminal or a different interface.

## 3. The actual nine-call D73 chain

The [chain proof](frozen/work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/phase-coded-chain-20261020/CHAIN.md) and [general-view proof review](frozen/work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/phase-coded-chain-20261020/GENERAL-VIEWS-REVIEW.md)
use the nine actual routes, grouped as three triples. The route/level
pairs for the shears are
`(1,1),(2,2),(0,2),(4,4),(5,5),(3,5),(7,7),(8,8),(6,8)`.
The shared input line factor remains attached to the original data.
Each corrected triple applies the signed exchange `J(A,B)=(-B,A)`
to those carried variables. It does not apply a new q. Since
`J^3(A,B)=(B,-A)`, the endpoint is

```text
X = F73 qY0,
Y = -F73 qX0.
```

The exact phase check covers 3,584 natural boundary identities and
1,008 FULL shear-view identities. Removing either the entry or exit
translation causes 896 failures. The all-width view argument uses the
quadratic refinement and spectator-axis extension; it is not inferred
from one width. The executable claim concerns these nine routes.

Nine Q-entry words have profile `{1:12528,2:576,3:432,8:144}` and
mass 16,128. The direct terminal adds 224 positive line calls, so the
complete profile is `{1:12752,2:576,3:432,8:144}` with mass
`16352=224*73`. The same rank argument gives no strict moment gain.
The scalar subtotal is `41688+18432=60120`, before terminal wrappers.
Keep 1,792 shear maps and 3,584 global entry/exit maps separate from
that scalar subtotal and from native side maps.

Neither caller proves a recursive consumer for q, a global host, a
complete address and stream invoice, or a numerical-grid bound. The
retained [recursive interface note](frozen/work/centre-encoding-campaign-20261014/lanes/coherent-port/recursive-code-interface-20261020/INTERFACE.md) states a possible
contract and its obligations. It does not discharge them.

## 4. Separate 8/104 section geometry

This section has a different interface. Select
`A=(0,7,20,27,36,46,57,111)` and let U contain the other 104 ports.
Construct the 8 by 104 matrix B from the pinned response, and put
`D=B*`. Here `BD=13I`, Q is unitary, and `Q^4=I`.
The query is `A_query=BQ`; define `T=BQ^2D`.

The [geometry proof](frozen/work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/PHASE-SECTION-GEOMETRY.md), [source qualification](frozen/work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/PHASE-SECTION-GEOMETRY-SOURCES.md),
[power classification](frozen/work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/schur-power-classification/CLASSIFICATION.md), and
[independent review](frozen/work/centre-encoding-campaign-20261014/lanes/bridge-access-20261017/phase-section-review-20261018/REVIEW.md) prove the following at every
positive width. The nine commuting translation involutions split the
space into 512 character sectors. The copy characters combine by XOR,
and every sector is present. In each sector the actual symmetric
8 by 8 matrix has eigenvalues among `±1,±3,±5,±11,±13`; each listed
value occurs. Exact characteristic calculations and the ten-root
annihilator prove the spectrum. This also proves that T is invertible
and gives its exact inverse in the translation algebra.

There are two useful right sections of A_query:

```text
K_minus = qD/13,
K_plus  = QD T^-1.
```

Since `D*D=13I` and Q is unitary, K_minus has norm `1/sqrt(13)`
and is the minimum-norm section. The singular values of K_plus are
`sqrt(13)/abs(lambda)` for lambda in the spectrum of T. Thus its norm
is `sqrt(13)`, its least singular value is `1/sqrt(13)`, and its
condition number is 13. Its oblique projector
`P_plus=K_plus A_query` has norm 13, image `im(QD)`, and kernel
`ker(BQ)`. Hence `im(QD)` complements `ker(BQ)`.

The normalized cross-Gram matrix for `im(QD)` and `im(qD)` is T/13.
Their principal cosines are `{1,3,5,11,13}/13`. In particular they
intersect; they are not a direct-sum pair. This is different from the
image/kernel complement just stated.

For the query `B Q^m` with a section constrained to `im(Q^nD)`, the
proof reduces existence to surjectivity of `BQ^(m+n)D`. When m+n is
0 modulo 4, the unique constrained section is `Q^nD/13`. When m+n is
2 modulo 4, it is `Q^nD T^-1`. These statements hold at every positive
width. For odd m+n there is no such section at width at least five,
even if the proposed section is nonlinear: the restricted linear query
is not onto. The explicit width-five character choice
`(1,2,3,6,6)` has null vector `(0,0,1,0,-1,1,0,1)` and a nonzero
leading seven-minor `-73`, so its rank is seven. Spectator extension
proves the larger-width statement. No minimum-width claim follows.

## 5. Translation services and the corrected one-bank inverse

The [two-bank service proof](frozen/work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/owner-review/centre-schur-probe/TRANSLATION-SERVICE.md) and
[independent review](frozen/work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/translation-service-review/REVIEW.md) implement the T from Section 4.
They require two existing eight-field FULL banks and one owned C0 field.
The source bank is unchanged and the target bank can have an arbitrary
baseline. The C0 input is discardable, its input contribution is removed,
and its output is zero. No other owner changes. The literal words have
zero native children. Each row in the following table also needs 32
completed outer-view maps.

| Service, either sign | Real scalar primitives | Body translation maps | Real odd-division scans |
| --- | ---: | ---: | ---: |
| Add T | 8,530 | 104 | 0 |
| Add T inverse, fewer maps | 166,912 | 2,048 | 16 |
| Add T inverse, fewer scalars | 114,528 | 8,944 | 16 |
| Coded exchange, fewer maps | 183,972 | 2,256 | 16 |
| Coded exchange, fewer scalars | 131,588 | 9,152 | 16 |

The exchange is the literal three-shear composition
`x+=Ty; y-=T^-1x; x+=Ty`, which gives `(Ty,-T^-1x)`.
The check combines the exact shear programs with the separately proved
all-width inverse. It does not claim a second full sparse replay of the
entire exchange. The exact forward prefix row norm is 53; the inverse
prefix row norm is `9073/715`. These are local bounds.

The [one-bank inverse proof](frozen/work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/owner-review/inplace-translation-service/INPLACE-SERVICE.md) requires one existing eight-field
bank and one owned C0 field. It uses the free 512-point orbits of the
nine translations, a normalized Walsh transform, the exact inverse in
each character sector, and the inverse Walsh transform. This proves the
word at every positive width. The [literal independent check](frozen/work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/inplace-service-review/REVIEW.md)
verifies all nine formal input columns, both inverse orders at all 512
modes, all 32,768 inverse-kernel coefficients, 144 Walsh-pair blocks,
and 64 completed-level phase identities. It verifies zero C0 output
and removal of the arbitrary C0 input.

The one-bank word costs 2,080 uniform and 110,284 conditional real scalar
primitives, 144 simultaneous translation maps, sixteen real odd-division
scans, and sixteen outer views. It has zero native children. Its full
word uses nine extra dyadic bits and increases the odd height by one.
The largest mode prefix row norm is 462,848; this gives a local
nineteen-bit guard bound. It is not a full recursive precision invoice.

The [map-cost correction](frozen/work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/inplace-service-review/MAP-COST-CORRECTION.md) withdraws the earlier review's
O(V) shortcut and its fixed-linear whole-body claim at general K. The
selected f bits are interleaved when K>1, so a contiguous complement is
not the physical translation. No extraction view or lowering for that
shortcut was proved. Retain all 144 translation maps at the applicable
packed-map cost, plus sixteen outer maps. The shortcut is valid only
for K=1. The direct conditional marked-counter scans remain valid for
arbitrary selected-bit positions. None of these facts makes the maps
free in a supplier recurrence.

The rational inverse uses odd denominator 2,145 and sixteen real odd
scans. The frozen translation-service review omits the record count in
one bit-cost sentence. For n complex entries per field, the retained
A8 bound is `64*n*(w_g+1)` arithmetic-head steps, plus stream control,
not `64*(w_g+1)` for an entire service call. The scalar and map invoices
above do not use that typo. The [A8 odd-grid theorem](frozen/work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/odd-grid-a8-20261017/A8-ODD-GRID.md) is a retained conditional
premise. A child endpoint must satisfy its exact dyadic-grid contract;
a completed parent must cancel the rational endpoint before unscaling.
The services do not supply a global owner lease or a caller terminal.
They are not decoders for Section 2's 16/96 common-q endpoint.

## 6. Current scalar-code closure

The [D25 proof](frozen/work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/unitary-code-closure-20261020/CLOSURE.md), [standalone independent proof](frozen/work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/owner-review/unitary-code-closure-review-20261020/REVIEW.md),
and [corrected source binding](frozen/work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/owner-review/unitary-code-closure-binding-20261020/BINDING.md) cover invertible scalar
codes C0, C1, C2 in their current fresh charts. Their routed product is

```text
K = (G2 C2 G2)(G1 C1 G1)C0.
```

For a fixed output port p, the route through intermediate ports j,r is
`rho_(2,p) rho_(2,j) rho_(1,j) rho_(1,r)`. The common logical input
with tags `(e2,e1)` separates all 12,544 routes at width f>=2. The
literal affine input `(0,e2,e1)` separates the physical routes at
f>=3. Thus distinct nonzero coefficient products cannot cancel in
that basis column. Invertibility forces every row and column to be
used. A monomial product therefore forces each code to be monomial;
the converse follows from composition of the monomial factors.

A third Fourier character distinguishes any route that breaks the
intrinsic line. It gives a nonzero Q commutator. Within this current
scalar class, Q commutation therefore holds exactly when all three
codes are diagonal, at f>=3. The full proof states and checks the
line criterion. It does not presume that a small representation has
independent route matrices.

The proof's regular-cover step uses the explicit covariant lift
`f(d,z)=g(d^-1z)`. Equal support sizes in every fibre show that a full
coordinate monomial which preserves this subspace induces a spatial
monomial. Invariance alone would not suffice. The corrected binding
review checks this step and binds the final source receipt
[bound-normal/CHECKS.json](frozen/work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/unitary-code-closure-20261020/bound-normal/CHECKS.json), SHA256
`f1e418155b89f8add0f066c80da2ab3a1120e6d78f047753e7e0698daf506a3a`.
The earlier run-normal and final-normal receipts do not replace it.

For the eight actual C/C* choices, the review reconstructs all literal
routes and verifies 896 nonmonomial basis witnesses and 896 nonzero
commutator witnesses. The C/C/C route count is 54,976, with at least
18 terms in every output row. The 1,066 nonzeros of scalar C^3 alone
do not certify the whole routed operator.

The [general-stage proof](frozen/work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/unitary-code-closure-20261020/GENERAL-CLOSURE.md) and its separate
[proof review](frozen/work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/owner-review/general-scalar-closure-review-20261020/REVIEW.md) use tags `(e_T,...,e_1)` to recover
all ordered intermediate ports for dimension `9+8T`. With T+1
invertible current scalar codes, logical monomial closure holds exactly
for monomial codes at f>=T; physical affine closure uses f>=T+1;
Q commutation holds exactly for diagonal codes at f>=T+1. These are
sufficient width bounds, not width optima. The general-T claim is a
proof claim, not a result of the finite replay.

The theorem excludes old-chart controls, operator-valued coefficients,
changed gathered interfaces, and paid joint decoders. A route count is
not a native child count. The theorem is not a general native decoder
lower bound and does not produce a supplier or kappa improvement.

## 7. Retained adjacent support

The phase engine needs the [natural no-reset triple](frozen/work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/no-reset-triple-20261020/NO-RESET.md) and its
[independent review](frozen/work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/owner-review/no-reset-triple-review-20261020/REVIEW.md). Their exact proof, receipts, and
operator terminal are retained in the closure. That predecessor uses
208 line calls, 16,608 scalar primitives, and 1,344 maps before side
maps and final bank exchange. It is an operator word, not a hosted
native terminal. Its ordinary-hole query differs from the new
phase-coded response. Its costs are not added to the new caller.

The [historical handoff](frozen/work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/HANDOFF-PHASE-CALLERS-20261020.md) also describes reciprocal source-cut
readers and other adjacent results. They are not dependencies of the
checks in this package. Their historical presence is not a claim that
this package admits their allocation, record transport, or late erase.
Their publication disposition belongs to their separate packages.

## 8. One fixed scalar-code interface

The separate [appendix proof](annexes/fixed-code-interface/PROOF.md)
characterizes preservation of one fixed scalar subspace E. Let P be its
orthogonal projector. Join distinct ports i,j when P_ij is nonzero.
For arbitrary finite-dimensional port operators A_i, the block operator
diag(A_i) preserves E tensor V if and only if A_i=A_j on each component.
The operators need not be invertible or normal.

Expand the operators in a linearly independent basis. Each resulting
scalar diagonal coefficient matrix must preserve E. Its spectral
projections are polynomials in that diagonal matrix and are orthogonal,
so it also preserves E perpendicular and commutes with P. The entry
equation forces equality along every edge. Conversely, equality along
edges makes the block operator commute with P tensor I and preserves E.

For the pinned real query R, R R^T=56I. The projector onto ker R is
I-R^T R/56, and its graph is connected on all 112 ports. Thus every
completed port operator must agree for this fixed-code contract. Equal
native ranks alone do not suffice. The [separate review](annexes/fixed-code-interface/REVIEW.md)
accepts this theorem and its exact graph check. Changing the code or
using a joint operator on several arrays remains outside the result.
No native program, free overwrite, or kappa improvement follows. The
source note's later paired-gauge discussion is context only.
