# Exact proofs and interface limits

The three claims below have separate source proofs and reviews. Their
full arguments are retained in this annex. The finite replay checks the
actual source objects; it does not replace the all-width proofs. Every
source byte is bound in [SOURCES.json](SOURCES.json).

## 1. Exact growing Walsh frames

The [root construction](frozen/work/centre-encoding-campaign-20261014/root/GROWING-WALSH.md) and [independent phase proof](frozen/work/centre-encoding-campaign-20261014/lanes/interface-proof/WALSH-FRAME-REVIEW.md)
use U_s of dimension `n=9+8s`, for `0<=s<=8`. Let omega_n be its
all-ones vector and let `H_n=omega_n-perp`. Since n is odd, H_n is
nondegenerate. Every x has the unique decomposition `a omega_n+h`.
Define G_n as the normalized real Walsh transform on H_n and the
identity on its complement. This exact kernel fixes its scalar phase
and gives `G_n^2=I`. Every orthogonal route supported in U_s fixes
omega_n and preserves the kernel, so it commutes with G_n exactly.

For the source line `C_q=((1+i)I+(1-i)X_q)/2` and odd q, put
`v=q+omega_n` and `b=x dot v`. Define the monomial L_q by

```text
L_q |x> = i^b |x+b omega_n>.
```

Comparing the two Gaussian coefficients for b=0 and b=1 gives
`G_n C_q G_n=C_omega_n L_q`, with no omitted scalar phase. The L_q
commute with the common line C_omega_n. These exact identities tensor
to every positive tensor size. The common line remains a native
operation.

For `m=n-8`, the even hyperplanes are nested. Their orthogonal
difference K has basis `k_i=omega_m+e_(m+i)`, `1<=i<=8`, and Gram
matrix `B=I+11^T`, with `B^2=I`. Thus `A_n=G_n G_m` is exactly the
Walsh transform on K. In the address chart A with first eight columns
k_i and ninth column omega_n, let S_8 multiply by i to the weight of
the first eight chart bits. The exact child recipes are

```text
A_n                 = P_A P_B S_8 F_8 S_8 P_A^-1,
C_omega_n A_n       = P_A P_B S_8 F_9 S_8 P_A^-1.
```

Each uses one native child and two composed monomial maps. The right
factor acts first. Even common-line powers are translations; a negative
odd power differs from the positive one by a translation.

Set `T_n^a=C_omega_n^a G_n`. For integers a,b,j and an admitted
orthogonal route g supported in U_s, the exact ordered identity is

```text
T_n^a C_q^j P_g (T_m^b)^-1
 = C_omega_n^(a+j-b) L_(q,n)^j P_g L_(omega_m,n)^(-b) A_n.
```

The rank is eight when a+j-b is even and nine when it is odd. The
route need not commute with A_n, so the displayed order is required.
For plain frame transport j=0, alternating types 1,0,1,...,1 have
rank-nine transitions. With the initial rank-nine frame, the nine-call
frame schedule has total rank 81 per mode and endpoint rank 73.
If an odd source phase j=1 is inserted, differing types give rank
eight and equal types give rank nine. These are different calculations;
the frame schedule is not a complete source-phase caller invoice.

Define `D_n|x>=i^(wt(x)-parity(x))|x>`.
Comparing the exact kernels gives

```text
C_omega_n G_n = D_n F_n D_n
```

for n=9+8s. The scalar factor for general odd n is one at these n.
The n=73 endpoint therefore has explicit diagonal F73 adapters. This
acts on arbitrary arrays, but only when the actual mode carries the
stated frame and required contents. It does not restore changed
contents or supply a zero-cost decoder.

The [receipt](frozen/work/centre-encoding-campaign-20261014/lanes/interface-proof/WALSH-FRAME-REVIEW.json) checks 61,440 exact common-line
coefficients, all 120 completed odd labels, growing ranks through 73,
65,536 rank-eight kernel entries, 262,144 rank-nine kernel entries,
and the full width-nine endpoint kernel. At larger widths it checks
complete quadratic-phase witnesses. The written kernel proof supplies
the general identity. The full typed transition is proved algebraically;
these counts do not claim a separate full-matrix test for every typed
transition.

A fixed common chart has rank 17 for the stated cross-stage operators,
and rank one within a stage. That is a statement about the full
operator, not a restriction to a centre image. A local isometry into
`span(omega_m,E_s)` need not extend to the ambient orthogonal cover.
The general linear chart in the child recipe does not grant new scalar
couplings or owner routes. Source access, initial frames, productive
and idle mode schedules, borrowed contents, restoration, monomial
prices, and recursive costs remain separate obligations.

## 2. Ordered phase classes and the rational baseline

The [general proof](frozen/work/centre-encoding-campaign-20261014/root/PHASE-CLASS-CAPTURE-20261020.md) and [independent review](frozen/work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/phase-class-reduction-review-20261020/REVIEW.md)
allow arbitrary invertible spatial phases Q_i on each field. Choose
one anchor Z_g per global phase class. Assume each
`A_i=Q_i Z_g^-1` is an admitted monomial in the current frame. Let Z
repeat Z_g on the class, so Q=AZ. If T preserves classes, then TZ=ZT.
For `C=T^-1 S T`, where S reads and changes only active fields J and
is identity elsewhere, direct multiplication gives

```text
Q C Q^-1 = A T^-1 [Z_J S_J Z_J^-1 direct-sum I] T A^-1.
```

No scalar factor is moved through A. The identity holds on arbitrary
fields and does not require a clean input. The inverse uses S_J^-1
and the same alignment passes. If each anchor and inverse anchor has
an admitted rank-one implementation, there are `2|J|` anchor children.
Scalar words, alignment maps, and entry and exit frames remain paid.
For any class-supported scalar response K, `QKQ^-1=AKA^-1`; this
identity does not turn an additive use of K into an in-place K inverse.

A transported inverse has the exact order
`Q C^-1 Q=(Q C^-1 Q^-1)Q^2`. The rightmost Q^2 acts first. It can be
included as the right factor of the first alignment only when that
composed map is admitted. Negative conjugation needs a separate
premise that `Q_i^-1 Z_g` is monomial. The positive premise alone does
not imply it. In the actual directional-phase case the phases commute,
which supplies the inverse alignments. The retained review gives a
noncommuting counterexample to the unjustified general implication.

The actual response is `E=H^-1 E_mode H`. It has eight signed
six-mode blocks and eight eight-mode blocks `I-dd^T`. The root space
`R=span(30,45,75,384)` gives fourteen classes of eight ports; H
preserves them. In each block choose a class pair and let e equal d
there and zero elsewhere. Set

```text
u=2e-d,  v=2d/k-e/2,  S=I+uv^T,   k in {6,8}.
```

Then `Sd=2e`, `e^T S=(4/k)d^T`, and
`det(S)=1+v^Tu=2(4-k)/k`, which is nonzero. It follows that
`S(I-dd^T)S^-1=I-(k/2)ee^T`, supported within one phase class.
Signed pair sums and differences give a class-preserving P. All
pair differences are passive in this rational construction. With
`T=PH`, the reduced code uses exactly `8*3+8*4=56` active fields.
The passive block is identity and active rows do not read passive data.

The exact literal forward and inverse words each cost 4,204 old real
scalar primitives. Forward capture also has sixteen real
**division-by-three** scans; inverse capture has sixteen real
**multiplication-by-three** scans. These are separate services.
The prefix row one-norm is twelve. The independent reverse-output
interpreter checks all 640 inputs, all 528 unchanged fields, both
matrix inverse orders, the literal restoration word, response
conjugation, and the exact 56-field reduction. The
[final receipt](frozen/work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/phase-class-reduction-review-20261020/verified-normal/CHECKS.json) binds this rational baseline.

## 3. The separate dyadic capture

The [dyadic construction](frozen/work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/phase-class-dyadic-capture-20261020/DYADIC-CAPTURE.md) and [distinct peer review](frozen/work/centre-encoding-campaign-20261014/lanes/bridge-review-20261017/dyadic-phase-capture-review-20261020/REVIEW.md)
replace the rational six-mode block. For its selected pair p,t set
`a_p=2d_p`, `a_t=0`, `b_p=3d_p`, `b_t=-d_t`, with a,b zero off the
pair. Put `u=a-d`, `v=(d-b)/4`, `S=I+uv^T`. Then
`v^Td=1`, `v^Tu=-2`, `Sd=a`, `b^TS=d^T`, and `b^Ta=6`.
Thus S is an involution with determinant -1, and
`S(I-dd^T)S=I-ab^T`. Its changed pair block is
`[-5,2d_p d_t;0,1]`.

For an eight-mode block set `u=2e-d`, `v=-u/4`. Then `u^Tu=8` and
`u^Td=-4`, so `S^2=I`, `Sd=2e`, and
`S(I-dd^T)S=I-4ee^T`. Each S-I has rank one. Sixteen disjoint
blocks therefore give `rank(C-I)=16` and `det(C)=1` after conjugation
by H. C remains an involution.

The actual signed pair rotation uses
`s=d_p x_p+d_t x_t`, `t=-d_p x_p+d_t x_t`. For size six, the active
coordinate is the selected **negative difference**, together with two
other sums. The rank-one vectors there are
`u=(-2,-2,-2)`, `v=(1/2,1/4,1/4)`. For size eight, four sums are
active. There are exactly 56 active coordinates, four in each class.
Every prefix of the pair codes preserves classes, and every reduced
prefix reads and changes active fields only. Endpoint support alone
would not suffice for the later norm bound.

For a rank-one update with `v^Tu=-2`, a shear that sends u to one
coordinate reduces the update to one row with diagonal -1. The
resulting literal order is `H,P,S_reduced,P^-1,H^-1`. The invoices are

| Part | Old real scalar primitives |
| --- | ---: |
| H or H inverse | 470 |
| P or P inverse | 1,016 |
| All sixteen reduced blocks | 1,072 |
| C or its literal inverse | 4,044 |
| Either coded additive coupler | 1,544 |

All scales are signed powers of two. The capture has no odd scan,
CLEAR, owned field, or native child in this scalar chart. The literal
check covers all 640 inputs, 528 unchanged capture fields, and both
full inverse orders. Its prefix row one-norm is ten and its scalar
binary denominator height is three.

The coded response is `K=CEC`. It is class-supported but not symmetric.
Its determinant is `35^8`; its inverse denominator LCM is 35. Encoding
both banks by C gives `Y+=KX` forward and `X-=KY` backward. The
backward coefficient is -K, not -K transpose. Each additive word has
168 ADDs and costs 1,544 units. This does not implement an in-place
dyadic K inverse. The factors five and seven remain.

## 4. Actual frame scope

The [peer review](frozen/work/centre-encoding-campaign-20261014/lanes/bridge-review-20261017/dyadic-phase-capture-review-20261020/REVIEW.md) reconstructs the actual W_R and W45
with an independent binary Pauli interpreter. W_R has Fourier rank
four. All 112 class-anchor ratios in W_R have rank zero, and all
112 anchors have rank one. With `Q'=W_R Q W_R^-1`, the ordered
factorization in Section 2 therefore has 56 inverse and 56 forward
anchor occurrences: a **conditional 112-H1** count. It retains the
4,044 scalar invoice, at most 224 alignment maps, and up to 224
native side maps. Preparing W_R, removing it, and lowering all maps
are additional obligations. These binary checks establish ranks and
monomial support; they do not emit full phase records or native wrappers.

The actual rank-one exit is `W45=S_e0 C_45 S_e0`. All 56 proposed
pair ratios in that frame have rank two. It fails the monomial
alignment premise. The conditional 112-H1 count cannot be combined
with its existing one-W45 exit budget.

The [common-gauge proof](frozen/work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/common-gauge-rank-20261020/COMMON-GAUGE.md) gives a scoped lower bound. If one
Clifford W makes every pair ratio monomial, let `L=W^-1 Z` and
`U=L intersect X`. Invariance of L under each ratio forces the pair
difference a+b into U. The actual differences span rank four. The
Fourier rank of W is at least dim U, hence at least four. W_R attains
that rank. This is a limit for one common Clifford, not for arbitrary
joint decoders, cross-field mixtures, or changed constructions.

Under the literal class/active prefix conditions, the unitary anchors
factor out of each input coefficient without changing its cancellation.
Thus the field L2 norm at completed-child boundaries is at most ten
times the largest input field norm. Partial alignment and anchor passes
apply a unitary to a complete field and preserve its norm. Recursive
child interiors are excluded. The scalar binary-height-three bound
does not transfer to the physical word without a separate phase-grid
account. The complete native capture, routed stage matching, source
access, helper progress, terminal output, and recursive invoice remain
open. None of these results changes the complete kappa calculation.
