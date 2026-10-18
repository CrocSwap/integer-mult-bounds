# An input source code with sparse target correction

This construction stores the actual eight-coordinate centre query in
eight existing source fields. The local target still receives the
original centre-free operation. All 480 arbitrary borrowed helper fields
are restored. The construction adds eight rank-one native children and
uses one of the eight existing private fields. It adds no array field.

The main theorem applies to a low-rank defect `J=I-KR`. It does not
require a scalar matrix RK or an inverse of RK-I. A pair of disjoint
dyadic coordinate minors gives a source code whose target correction is
supported on one minor. This removes the restriction to the response
space of an internal cut.

This is a local construction. Its physical output frames, source
restoration across different cover charts, recursive hosting, precision,
and complete supplier cost remain separate obligations. It does not
change the complete kappa bound.

## Local interface

All coefficient matrices in this proof have entries in Z[1/2]. They act
on field indices and commute with the common array payload. The retained
backward word has the canonical content map

    B_J(X,Y,h,c) = (X-JY,Y,h,0),       J=I-KR.             (1)

The n source fields Y enter in one common frame I. The target field X_p
enters in its specified native frame C_p. Thus its physical value is
C_p X_p. Canonical content is not a substitute for this frame condition.
The output frames are the retained frames of the supplied word.

Every X, Y, and helper input is arbitrary. The private inputs can also
be arbitrary; a private field is cleared before its first use. The
permission to clear a private field does not apply to a borrowed helper.
The equation h'=h restores canonical helper contents. The physical
helpers retain their original native transforms and endpoint frames;
the equation does not replace those jobs by physical identity maps.

In the actual instance, n=112, r=8, and K=R^T/4. The pinned source gives

    RR^T=56I,       RK=14I.

There are 480 borrowed helpers and eight private fields, hence 712
formal input columns. Each intrinsic input C_p is a positive complex
rank-one line operator. These are the physical input frames before the
retained `old_to_new` adapters. A canonical frame at a later point in the
word cannot replace this input frame.

## General construction

Let R be r-by-n and K be n-by-r. Choose n-by-r P and r-by-n L such that

    RP=I,       LK=I,       LP=0.                            (2)

Put

    M=RK,
    Z=K-P(M-I),       Q=R-L.                                 (3)

Direct multiplication gives

    RZ=I,       LZ=I,       QZ=0,
    JZ=Z-K=-P(M-I).                                         (4)

These formulas use no inverse of M or M-I. In particular, they remain
valid when either matrix is singular or has an odd determinant.

For any dyadic scalar t, define

    G_t=I+tZQ.                                              (5)

Since QZ=0, `(ZQ)^2=0`. Therefore

    G_t^-1=G_-t,       G_s G_t=G_(s+t),       QG_t=Q.

For t=1, `LG_1=R`. The selected L read of the new source contains the
complete original centre query, with all initial source values arbitrary.
Its inverse retains those values; no selected source is an initialized
buffer.

Use this prelude before the retained word:

    X <- X+tJZQY,
    Y <- G_tY.                                              (6)

The native implementation of the first line is given below. The second
line uses only scalar operations at the common input source frame.
After (6), the retained target output is

    X+tJZQY-J(I+tZQ)Y = X-JY.                               (7)

The source output is G_tY. The helper outputs are unchanged because (1)
holds for arbitrary data inputs. This proves the complete logical map

    (X,Y,h,c) -> (X-JY,G_tY,h,0).                            (8)

No internal source read, suffix response, or recovery by `(I+BZ)^-1`
is required in this construction.

## A literal scalar source word

Write z_k for column k of Z and q_k for row k of Q. Process k=0,...,r-1:

1. Clear the owned private field c0 in frame I.
2. Form q_kY in c0 with scalar additions from the input source fields.
3. Add t z_k c0 to Y, one destination field at a time.
4. Clear c0 after its last use.

The completed k-th update leaves every later query unchanged, since
`q_j z_k=0` for every j and k. Each query must be completely read before
its own scatter starts. An individual partial scatter need not preserve
Q. The verification includes a legal-frame mutation that violates this
read order.

All source reads and writes occur at frame I, before any retained native
event. The scalar word is exact on arbitrary source values. It does not
need r extra fields or a division by an entry of Z.

## Sparse native target correction

Let H=tJZQ. For each nonzero row H_p, clear c0 at frame I and form H_pY.
Apply the exact native operator C_p to c0, add it to X_p, and clear c0.
The physical addition is `X_p += C_p(H_pY)`, as required by (6).

The target X_p already has frame C_p. It is not transformed or cleared.
The source Y is unchanged during this part of the prelude. After a private
field is cleared, its zero value can be used in the next specified frame;
there is no nonzero value whose native return is omitted.

Equation (4) confines H to the row support of P. If P is supported on r
selected ports, this uses at most r native copies. In a more general
interface, the native rank allowance is the sum of the input frame ranks
over the active rows. Scalar formation, child address maps and recursive
hosting must also be charged.

The actual instance uses eight rank-one children and 16 explicit binary
address permutations. Each positive input C_p is checked with exact
Gaussian dyadic arithmetic. A wrong inverse sign or global phase fails.
The exact nine-axis identities extend by tensor products to every
positive tensor size, including arbitrary superpositions of payload
coordinates. A scalar native phase is raised to the tensor power.

## The actual disjoint minors

Use the two disjoint eight-port sets

    A=[0,7,20,27,36,46,57,111],
    T=[21,37,47,76,81,87,92,110].

The source verifier derives and checks

    R_A R_A^T=4I,       R_T R_T^T=4I.

Let E_A insert eight coordinates in A. Set

    P=E_A R_A^-1,       L=R_T selector_T.

Then RP=I, LK=I, and LP=0. Equations (3)-(4) become

    Z=K-13P,       Q=R-L,
    RZ=LZ=I,       QZ=0,       JZ=-13P.                      (9)

The selected output fields satisfy

    (G_1Y)_T=R_T^-1 RY.                                    (10)

The off-selected fields can change. In particular, this construction
does not claim to preserve the original value of every port outside T.
The retained source outputs have physical frames `F C_p^-1`; their
selected locations do not give free common-frame access at the output.

The factor 13 in (9) is a multiplication coefficient. No inverse of 13
or of 3 occurs. The actual Z has 448 nonzero entries, Q has 416, and
JZQ has 392 entries in eight rows. These matrices are derived from the
pinned R; they are not independent numerical assumptions.

## A reusable fixed-support source group

Suppose A has exactly r ports and R_A has a dyadic inverse, with
P=E_A R_A^-1. Let J_offA denote the rows of J outside A. Then

    ker J_offA = im Z                                      (11)

as modules over Z[1/2]. The inclusion from right to left follows from
JZ=-P(M-I). For the reverse inclusion, take v in the left kernel and
put d=v-ZRv. Then Rd=0, so Jd=d. The off-A rows of Jd are zero. Thus d
is supported on A. Since Rd=R_A d_A=0 and R_A is invertible, d=0.

Consequently every dyadic source automorphism G that preserves the
off-A target rows, `J_offA G=J_offA`, has the unique form

    G=I+ZB,       B=R(G-I).                                (12)

Such G is invertible over the dyadic ring if and only if `I+BZ` is.
One can use the decomposition `Y=ZRY+(I-ZR)Y` to see the triangular
action. Explicitly,

    G^-1=I-Z(I+BZ)^-1 B,
    B12=B1+B2+B1 ZB2.                                     (13)

Define the corresponding input prelude by

    E_G(X,Y)=(X+J(G-I)Y,GY).

It satisfies

    E_G1 E_G2=E_(G1G2),
    B_J E_G=diag(I,G) B_J.                                (14)

The target correction stays supported on A under composition and
inversion. There is also an explicit scalar word for every parameter B.
After the target correction, clear all r private fields, store all r
entries of BY, add Z times these stored values to Y, and clear the
private fields. All reads precede all source writes. This gives GY
without a factorization of G or a division by an entry of B. The actual
interface already has r=8 private fields. The general word uses these
eight fields; the nilpotent logger uses only one.

The general added scalar allowance is

    F(B)+F(Z)+4r + F(JZB)+12r.                              (15)

The native support bound stays r under composition, but the scalar
coefficients and their cost can grow. The emitted words include the
unipotent logger and its inverse, and a non-diagonal parameter with its
inverse. The general construction follows from the complete snapshot
and matrix identities above.

The r-port hypothesis is needed in (11). A larger support set can have
nonzero vectors in `ker R` supported on A, so the equality and maximal
family statement would then require a larger response space.

The non-diagonal example uses the eight-by-eight matrix E with the only
nonzero entry E[1,0]=1. Its parameter and inverse parameter are

    B=(I+E)R,       B_inverse=-(I/2+E/4)R.

Here `I+BZ=2I+E`, with inverse `I/2-E/4`, since E^2=0. Both words use
the eight-snapshot schedule. Moving the complete column-zero source
scatter before the second snapshot changes the result by

    delta Y=Z_1 R_0 Y,       delta X=-J Z_1 R_0 Y.

These are nonzero exact errors. This mutation keeps the event multiset,
scalar cost, and frame access unchanged. It tests the snapshot order,
not only a parameter or cost difference.

## Exact local cost

For a nonzero reduced dyadic coefficient a/2^b, the retained allowance
for a complex ADD is

    2*(3+floor(log2(abs(a)))+popcount(abs(a))+b).

Let F(D) be the sum of this allowance over the nonzero entries of D.
For t=1 or -1, the scalar source word costs

    F(Q)+F(Z)+4r = 3328+5376+32 = 8736.

The target correction costs

    F(JZQ)+12r = 7824+96 = 7920.

Each CLEAR costs two real-component primitives. Each target row uses
two CLEAR gates and one unit complex ADD. No term in these constants
counts a native child or an address permutation as a scalar operation.

The complete local scalar allowance is

    202138+8736+7920 = 218794.

The complete original-rank child profile is

    {1:2420, 2:418, 3:432, 4:142, 5:82},

with mass 5530, compared with 5522 for the retained centre-free word.
The peak additional private use is one field, within the existing eight.
The 5056 retained native events remain in their original order.

The non-diagonal word and its inverse parameter have complete scalar
allowances 222846 and 225794. Each has the same child profile and uses
eight existing private fields. The literal event invoices are checked
against (15).

These scalar bounds count real-component primitives per array
coordinate. The eight added children, their 16 address maps, precision,
recursive owners, and final assembly need a complete supplier invoice.
The local rank mass does not establish a multiplication exponent.

## Verification boundary

The portable replay reconstructs the retained inputs from immutable Git
blobs and checks their content hashes. It checks every one of the 712
formal input columns, all borrowed helper outputs, private lifetimes,
frame accesses, source queries, target outputs, literal scalar counts,
and both inverse orders of the prelude on all persistent fields. Used
private fields end at zero; unused private fields stay unchanged. The
logger preludes use only c0, while the general snapshot preludes use all
eight fields. Thus the inverse pair does not restore arbitrary initial
contents of its used private fields. Each complete call clears all eight
private fields through the retained core. It checks the parameter-addition
law and meaningful mutations of source timing, compensation, native sign
and scalar phase. Native checks use exact arithmetic on every basis
input of each new recipe.

The inverse source code and inverse prelude are distinct from an inverse
full backward call. A full call also applies the retained target shear.
Likewise, equations (13)-(14) are statements at one fixed interface;
they do not identify different routed source charts.

A complete supplier must restore the original data, carry the stored
queries in their actual frames, implement all bridge operations, and
pay for all recursive children and finite work. Those tasks remain open.
