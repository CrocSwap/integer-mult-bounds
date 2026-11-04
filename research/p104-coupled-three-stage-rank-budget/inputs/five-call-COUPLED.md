# The bounds hold at every coupled width

The scalar bounds extend to arbitrary port coupling. This extension does
not assume that the matrix coefficients commute. It excludes the proposed
escape of replacing scalar parameters by larger matrices in the same
shortest-query contract. It does not exclude extra query calls, initialized
work, shorter stage periods or noncentral native address maps.

## Statement

Let q be any positive integer and let n be 4, 6 or 8. There are nq
independent fields and n+1 chronological queries. Each query has rank q
and is square-zero. Each full stage is a rank-2q projector compatible
with its query; a thin call has no stage. The scalar field has
characteristic zero, and the stage z and involution S are central.
Arbitrary constant invertible maps on all nq fields are allowed.

If W_minus(z)=-W_plus(z) for formal z, the word needs at least
n/2-1 thin calls. At that minimum the only possible interior thin sites
are 2,4,...,n-2, and both boundary calls are full. The bound is attained
for the query identity by the scalar alternating construction tensored
with I_q. Its natural stage endpoint still has the stated Jordan defect.
Attainment of the query identity is not a complete Gaussian caller.

The finite-period theorem also extends to every q. For any positive even
n, equality at every p-th root with p>=n-1 forces the formal query
identity. Thus an eight-block/nine-full caller cannot escape by coupling
ports and using the actual order-seven native stage. In particular, the
algebraic exclusion permits coupling all 104 source ports at once.

## Complete block query normal form

Factor R_i=U_i V_i with U_i of size nq by q, V_i of size q by nq and
V_i U_i=0. Concatenate these factors into U and V, and put G=VU. Let L
be the strict block-lower part of G. Chronological expansion gives

    product_i (I-2R_i) = I-2U(I+2L)^(-1)V.

At z=1 the required endpoint is -I. The same projector argument as in
PROOF.md shows that Z=I+2L-G has rank q. Its diagonal blocks are I_q.
Write Z=AB with inner dimension q. Each diagonal identity A_i B_i=I_q
makes both square blocks invertible, so B_i=A_i^(-1). Change the factor
coordinates by U_i -> U_i A_i and V_i -> A_i^(-1)V_i. The query does
not change. Its Gram blocks become

    V_i U_j = sign(i-j) I_q.

The leading n-by-n block matrix is the invertible even skew sign matrix
tensored with I_q. A global basis change therefore gives exactly the
canonical tuple in PROOF.md tensored with I_q. This proves completeness
for all constant frames, including maps that mix different ports.

## Complete block projector chart and free-algebra certificate

In a basis that makes R_i=E_01 tensor I_q, every compatible rank-2q
projector has the form

    P_i = [[I_q, C_i, B_i],
           [  0, I_q,   0],
           [  0, A_i,   0]],       C_i+B_i A_i=0.

Here the long row and column consist of n-2 blocks of size q. The product
B_i A_i has this order. To prove completeness, compatibility fixes the
first block column and second block row. If the remaining diagonal block
is D, idempotence makes D idempotent. Block elimination gives
rank(P_i)=2q+rank(D), so the rank condition forces D=0. The displayed
quadratic equation is then the remaining idempotence condition.

The boundary cancellation and first two mixed equations in PROOF.md
still apply. Regard each q-by-q parameter as a generator of the free
associative algebra over Q. A monomial is now an ordered word. The
standard-library checker free_replay.py reconstructs P_i^2-P_i and the
second coefficient from the original chronological word. It does not use
commutative projector quadratics.

Rational row operations combine necessary equations. Each affine
consequence is a matrix equation with scalar coefficients, so ordinary
linear elimination and substitution describe its complete solution set.
Repeated elimination produces a nonzero constant in every prohibited
domain. That constant becomes a nonzero multiple of I_q in any matrix
representation. Hence those domains fail at every positive q.

The same 84 site-pattern domains as in PROOF.md are checked. Only the
three alternating patterns survive at their stated minima. No bounded
matrix-width search or finite coefficient enumeration is used. Exact
controls evaluate the ordered polynomials as literal 2-by-2 and 3-by-3
matrices and compare the full second coefficient with direct matrix
products. Sorting each word as if its variables commuted changes those
controls and is rejected. These are author-side implementation checks,
not independent human or proof-kernel review.

## The two-corner argument needs no commutation

At each stage root, apply the block normal form to the transformed query
vectors in PERIOD.md. Adjacent Gram blocks equal z I_q. Thus their
normalizing factors obey A_(i+1)=z A_i, and every Gram block is
sign(i-j) z^(i-j) I_q. Short-interval degree bounds again fix every
block formally except possibly the two corners.

After normalization, write the remaining corner blocks as X(z) and
-Y(z). The other blocks are the canonical skew sign blocks. The leading
n-by-n block matrix K tensor I_q is invertible and constant. The full
Gram matrix has rank at most nq, so its q-by-q Schur complement is zero.

That complement is X-Y. To see this without a commutative determinant,
expand the block row times (K^(-1) tensor I_q) times the block column.
The only possible X Y term has coefficient (K^(-1))_00=0, since K is
invertible and skew. The two linear coefficients are 1 and -1 and the
constant is zero, as in the scalar determinant calculation. All these
coefficients are rational scalars. No exchange of X and Y is used.

Thus X=Y. Each entry of X is a polynomial in z^(-1); each entry of Y is
a polynomial in z. Their equality is constant, and its value at z=1 is
I_q. The whole Gram matrix is therefore canonical over F(z). This gives
the formal query identity and proves the period extension. The literal
native faithfulness check in PERIOD.md applies to every port copy.

## Limits and next question

This closes larger block width as an escape for this shortest-query
model. It does not bound words with more than n+1 calls, a mixture of
different query ranks, initialized or discarded fields, noncentral
ordinary coefficients, or finite periods below n-1. The fixed-frame
initialized-work screens are separate discovery records. No kappa
increase or complete multiplication theorem is claimed.

The source contract and canonical query lineage credit Cinna Davis and
the retained native/controller contributors. The earlier binary
split-star certificate has different stage and query assumptions; this
proof does not reclassify that result. New block normal-form extension,
ordered-word replay and period argument: Ali Romman with substantial
OpenAI Codex assistance. Apache-2.0.
