# The doubled centre Gram needs degree at least 410

This contribution was produced by Nick Petalas. Apache-2.0.

## Operator and inherited identities

Use Ali Romman's actual historical query in PR4958, with eight-by-112
matrix R and distinct port labels q in F2^9. Its exact source digest is
5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3.
Write r_q for its column. No normal columns are added.

The cited doubled representation and Bell identity give

    A_lambda = (1/4) sum_q r_q r_q^T tensor Gamma_q^tensor(lambda),
    Gamma_q = H_q tensor H_q,  H_q = (X_q + Z_q)/sqrt(2).

The root coefficient occurs once, not once per tensor slot. We use PR4958's
Bell-block formula and common fixed vector as premises. Its degree-409
certificate is not replayed or used as an input to the new certificate.

In one doubled slot, c=a+b is invariant. In block c, the action on the
remaining address a in F2^9 is

    P_q(c) e_a = e_(a+q)                    if q dot c = 1,
    P_q(c) e_a = (-1)^(q dot a) e_a        if q dot c = 0.

Thus the 4,096-dimensional block on the eight query coordinates is

    A_c = (1/4) sum_q r_q r_q^T tensor P_q(c).

Different c give disjoint invariant subspaces. This permits a new
certificate on B=A_1 direct-sum A_11, of dimension 8,192. It is a
restriction of the full one-slot operator, not a sum of operators on the
same subspace. This distinction is needed for the moment argument.

## New finite certificate

Set p=65537. This is prime, as trial division through 256 verifies.
Let v and w be eight-by-512 arrays obtained from 8,192 SHAKE256 bytes,
read as little-endian unsigned 16-bit integers and reshaped in row order.
The exact ASCII seeds are

    v: new-degree410-centre-gram
    w: new-degree410-centre-gram-observer

Put V=(v,v) and W=(w,w) on the direct sum. For j=0,...,818 calculate

    s_j = W^T B^j V
        = w^T A_1^j v + w^T A_11^j v     in F_p.

The new Hankel matrix is H_ij=s_(i+j), 0<=i,j<410. Direct exact
calculation gives

    det(H) = 58805 mod 65537, which is nonzero.

The verifier regenerates every moment. It checks every one of the 1,638
block Krylov vectors using two implementations: a factored R^T/labeled
port/R action and a literal sum of the 112 signed rank-one port actions.
It then computes the same determinant using modular Gaussian elimination
with NumPy integer arrays and fraction-free condensation with Python
integers. No floating-point arithmetic or eigensolver occurs.

The optional --emit-result command prints the two complete moment lists,
their summed list, the determinant, exact seeds and SHA256 hashes of all
six package files and the actual query input. This is a generated receipt.
Default verification and receipt generation write no files.

## Characteristic-zero consequence

All entries of B, V, W and H belong to Z[1/2]. Reduction modulo the odd
prime p is therefore defined. A nonzero reduced determinant implies that
the original determinant is nonzero over Q, and remains nonzero after any
characteristic-zero field extension.

If V,BV,...,B^409 V were linearly dependent, left multiplication by
W^T B^i for i=0,...,409 would give the same dependence among the columns
of H. Hence these 410 vectors are independent. No nonzero polynomial
of degree below 410 can annihilate B. Since B is a restriction of A_1,
no such polynomial can annihilate the full A_1 either.

This is a finite exact certificate with a characteristic-zero implication.
It excludes degree exactly 409 for the full operator. It does not supply
an annihilating polynomial or the exact minimal-polynomial degree.

## Every positive tensor size and inverse polynomials

PR4958 supplies a common positive-one eigenvector e of every Gamma_q,
namely the Bell vector a=b=0. For lambda>=1, restrict A_lambda to the
first-slot direct sum above, tensored with e in every remaining slot.
Every term preserves this subspace and acts there exactly as B. The
query coefficient r_q r_q^T is still applied once. Consequently,

    degree(minimal polynomial of A_lambda) >= 410

for every positive lambda, even if the proposed polynomial depends on
lambda. This uses the cited Bell/tensor identities; it is not a new
native all-column implementation proof.

Let alpha,beta lie in any characteristic-zero field containing the
operator entries, beta!=0, and assume alpha I+beta A_lambda is invertible.
If q(A_lambda) is its inverse, then

    ((alpha+beta t) q(t) - 1)(A_lambda) = 0.

The polynomial on the left is nonzero and has degree at most deg(q)+1.
Therefore deg(q)>=409. This improves the predecessor's necessary bound
408 by one. It does not assert that an inverse exists or that 409 is
attainable.

## Exact arithmetic and executable bounds

After each application every vector entry is in [0,p-1]. The factored
root projection has at most four signed terms. The return projection has
at most 112 terms. Their absolute pre-reduction bounds are 4(p-1) and
112(p-1). In the literal implementation the accumulated output is at most
112*4*(p-1) in absolute value. Reduction precedes multiplication by 4^-1,
so that multiplication is below 2^32. Each moment sum is at most
4096(p-1)^2=2^44. Gaussian elimination products are at most (p-1)^2;
subtractions also fit in signed 64-bit integers. Condensation uses
unbounded Python integers. These bounds exclude integer overflow.

All loops have fixed bounds from the authenticated 8-by-112 query,
512 addresses, two blocks, 819 moments and a 410-by-410 matrix. Functions
have fewer than 60 physical lines. Failure checks use explicit exceptions
and remain active under optimization. The verifier has no recursion,
subprocesses, network access or file writes. Both registered commands
make warnings errors. No external static analyzer is claimed.

Power of Ten rule 3 deviation applies to verify.py. CPython and NumPy
allocate integers, lists and arrays during arithmetic; these runtime
allocations cannot be prohibited by preallocation. The scope is this
bounded finite replay. At most two 8-by-512 evolving vectors, fixed
112-by-512 action tables, bounded intermediate arrays, 1,638 moments and
410-by-410 determinant storage are live in each block/determinant phase.
Condensation retains one 410-by-410 Python-integer matrix; temporary
integer sizes are bounded by the modular formula. Runs in both modes
exercise these capacities. A larger executable domain would require a
new capacity review. There are no user-controlled scientific dimensions.
