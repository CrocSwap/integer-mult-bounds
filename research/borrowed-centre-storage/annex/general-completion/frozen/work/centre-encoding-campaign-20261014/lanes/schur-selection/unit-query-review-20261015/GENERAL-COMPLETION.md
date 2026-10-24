# A full-query unit completion and its exact row count

A unit selected query minor is sufficient to store the complete query
in those output fields while keeping every other row of I-KR. The
selected part of K need not be the inverse minor. The resulting code
is a product of two invertible triangular maps.

If RK=gI and 1-g is not a unit, no unit encoding can change fewer
output fields than the query dimension. If 1-g is a unit, I-KR is
already a unit. This gives an exact field-count distinction when a
unit query minor is available. It gives no native-child lower bound.

## Construction without the compatibility condition

Let A be a commutative ring with 1 different from 0. Let

    V = A^(nN),   W = A^(dN),   1 <= d <= n,   N >= 1.

Partition V into n fields, each with N coordinates. Select d complete
fields, denoted S, and let U be the other fields. Let R:V->W and
K:W->V be A-linear maps. Write R_S=R i_S. Suppose R_S is a unit.
No identity involving RK is needed in this section.

Define

    L = R_S pi_S,       G = i_S R_S^-1,
    B = R-L,           D = i_U pi_U K,
    J = I-KR.

The identities LG=I, LD=0, and BG=0 follow from the field supports.
Thus (DL)^2=(GB)^2=0. Set

    T = (I-DL)(I+GB),
    T^-1 = (I-GB)(I+DL).                         (1)

Each factor has the displayed inverse over A. The two products in
(1) are exact inverses in both orders. No determinant or odd inverse
is needed to execute this algebraic code.

Expansion and the three identities above give

    T = I+GB-DR,
    pi_U T = pi_U J,
    L T = R,
    T-J = GB + (i_S pi_S K) R.                   (2)

Every output row in (T-J) lies in S. The equations pi_U T=pi_U J and
LT=R determine T uniquely, since R_S is invertible.

In coordinates a=R_S x_S and u=x_U, let f=a+Bu. Then

    T:(a,u) -> (f,u-Df),
    T^-1:(f,u') -> ((I-BD)f-Bu',u'+Df).           (3)

The two shears have determinant 1 on the full finite free module.
Hence T has determinant 1. More generally, the product formula is
valid over a noncommutative coefficient ring whenever the stated
module maps and two-sided inverse R_S^-1 exist. The commutative-ring
hypothesis is used below for the converse and residue-field claims.

If pi_S K=R_S^-1, with the inclusion understood, then K=G+D.
Equations (1)-(2) become the producer's construction, and

    T-J = G(2R-L),       (T-J)G=G.                (4)

The repair in (4) is a split projection: (T-J)^2=T-J. Its image is
exactly the selected field module. This statement uses the compatibility
condition; the more general repair in (2) need not be a projection.

If also RK=gI, then BD=(g-1)I. The inverse in (3) becomes

    T^-1:(f,u') -> ((2-g)f-Bu',u'+Df).            (5)

In the actual case g=14, the first coefficient is -12.

## When a selected full-query completion exists

Assume that R is onto. Fix the selected set S of d fields. Then the
following statements are equivalent:

1. R_S is a unit over A.
2. There is a unit code T with pi_U T=pi_U J and LT=R, where
   L=R_S pi_S.
3. There is a unit code T and some linear readout Q:V_S->W such that
   pi_U T=pi_U J and Q pi_S T=R.

The construction proves 1 implies 2, and 2 implies 3. For 3 implies 1,
R being onto forces Q to be onto. It is a square matrix over a
commutative ring, so it has a right inverse and its determinant is
a unit. Thus Q is a unit. With row order S,U, the matrix

    M = [ R ; pi_U J ] = diag(Q,I) T

is a unit. Add (pi_U K) times its first block row to its second block
row. This invertible row operation gives

    [[R_S,R_U],[0,I]].

Its determinant is det(R_S). Hence R_S is a unit. The readout Q need
not equal R_S. The conclusion applies to any linear full-query code
in precisely the selected fields when all other rows are retained.

Surjectivity is essential for this converse. Over Z[1/2], take
R=[3,0], K=0, and T=I. The equation R_S pi_S T=R holds with the
nonunit minor R_S=3, because R itself is not onto.

A unit minor is not necessary for a row repair that does not store
the complete query. For example, over Z[1/2], let

    R=[3,1],   K=[4,2]^T,   RK=14,
    J=[[-11,-4],[-6,-1]].

Changing the first row to [1,0] gives a unit matrix of determinant -1,
but its selected output does not give the full query through the
required linear readout. This separates a query completion from an
arbitrary unit repair.

## Exact minimum number of changed fields

Now assume RK=gI, where g is a scalar in A. A unit d-field minor of
R remains available. The minimum number c of complete output fields
on which an A-linear unit T' can differ from J is

    c_min = 0, if 1-g is a unit;
    c_min = d, if 1-g is not a unit.              (6)

The minimum in (6) permits any unit repair. It does not require that
the repaired output also store the complete query.

If 1-g is a unit, then

    J^-1 = I + (1-g)^-1 KR.

Thus c=0 is possible. Conversely, if J is a unit, the identity

    (I-RK)^-1 = I+R J^-1 K

shows that (1-g)I is a unit. Since dN>0, this implies that 1-g is
a unit. This also proves J is a unit if and only if 1-g is a unit.

Suppose instead that 1-g is not a unit. It belongs to a maximal ideal
m of A. Let k=A/m and use bars for the reduced maps. Then

    Rbar Kbar=I,
    ker(Jbar)=im(Kbar),
    dim_k ker(Jbar)=dN.                          (7)

Indeed Kbar is injective, Rbar is onto, and Kbar Rbar is an
idempotent of rank dN. If T' is an A-unit, T'bar is a k-unit.
The restriction of T'bar-Jbar to ker(Jbar) equals T'bar and is
injective. Therefore

    rank_k(T'bar-Jbar) >= dN.                    (8)

If T'-J changes only c whole fields, this rank is at most cN. Hence
c>=d. Construction (1) changes at most d fields and attains equality.
This proof does not require the compatibility condition on K_S.

For any specified field homomorphism A->k with g mapping to 1, the
same lower bound holds. Existence of a maximal ideal is only needed
to state the exact dichotomy (6) for every nonunit 1-g.

The field-count bound also applies to a nonlinear code which has a
surjective reduction on the complete residue module and retains
the same unselected output coordinates. If c<d, those unselected
outputs lie in the image of pi_U Jbar, whose rank is at most (n-d)N.
That image cannot be all of k^((n-c)N), as surjectivity would require.
This does not apply to arbitrary nonlinear or rounding codes that
do not induce such a residue map. The rank statement (8) itself is
only for linear maps.

## Actual Gaussian-dyadic supplier

Take A=Z[i,1/2], n=112, d=8, and g=14. The source R has
RR^T=56I, and K=R^T/4. The selected fields are

    [0,7,20,27,36,46,57,111].

Their minor satisfies R_S R_S^T=4I, so its inverse is R_S^T/4.
The actual compatibility condition holds. Both Gaussian maps

    Z[i,1/2] -> F13,   i ->5 or i ->8=-5

are defined: the two images square to -1, and 2 is invertible. Under
either map 14 becomes 1. Hence J has residue rank 104N, every unit
repair has difference rank at least 8N, and exactly eight output
fields are necessary. The explicit repair has rank 8N and the
completed operator has rank 112N.

For the complete finite cover, each field has a common finite number
N of cover and payload coordinates. Do not replace this module with
its constant-array sector. The identities tensor with I_N. Matched
unit views R'=W R V^-1 and K'=V K W^-1 preserve RK=14I. If V
preserves each complete data field, the selected minor becomes
W R_S V_S^-1 and stays a unit. Thus the argument applies to the
complete routed module.

More generally, independent unit input and output views preserve
the residue nullity of J. A fieldwise output view also preserves
which complete output fields a repair changes. Thus the lower bound
does not depend on writing every physical endpoint in one common
input-output view. The view maps must actually be units over the
stated ring; an inherited inverse that divides by 13 cannot be
silently included.

The literal local component has relative old-baseline code C_S T,
where C_S applies a native line only on the eight selected outputs.
C_S is a Gaussian-dyadic unit which preserves each output field.
Therefore (C_S T-J)_U=0, and its changed-field count is also exactly
eight. The selected physical outputs are FULL; the other Y outputs
keep their inverse-line frames. The field-count theorem does not
permit a scalar gate between those unequal frames.

The same actual lower bound covers dyadic real-linear unit codes,
including complex conjugation. Realify every complex field into 2N
coordinates over Z[1/2], then reduce modulo 13. The centre module
has dimension 16N and J has nullity 16N. A change in c complex fields
has rank at most 2cN. Thus c>=8 again. This version uses the full
realified module; one Gaussian residue sector alone is not enough
for a map which exchanges the two sectors.

The result permits an exact lossless full-query encoding without
extra query output fields and without an odd inverse. Compositions
and algebraic inverses of these codes stay dyadic. It does not price
their native access, their changing frame types, a later old-stage
query, recursive hosting, borrowed workspace, approximation error,
or the complete supplier. The actual local word pays eight native
line children, but no lower bound on that child count is proved here.

Dyadic coefficients alone do not make a data map a dyadic unit.
J itself is a counterexample. Helper restoration also does not prove
that property if the word can clear owned private fields. The explicit
two-sided inverse in (1) proves the required property for T. A code
which leaves information in unreturned helpers is outside the final
unit-data-map contract.

The complete input module is also essential. On the restricted
subspace ker(R), J is already the identity, so no changed row is
needed there. If division by 13 is allowed, the actual J is a unit
with its usual inverse, so this coefficient-ring obstruction is gone.
Approximate or grid-dependent decoders need a separate analysis.

The coordinating agent proposed the actual modulo 13 lower bound.
The paired-package-review lane supplied the unit code and its local
word. This extension removes the selected-K compatibility premise
and proves the query-completion converse and exact g distinction.
It was developed and checked with AI assistance. Publication remains
on hold.
