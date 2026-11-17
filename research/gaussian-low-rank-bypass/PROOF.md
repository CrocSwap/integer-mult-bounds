# A dense bypass must retain almost full rank

This contribution was produced by Nick Petalas. New work is Apache-2.0.

Claim type: scoped written proof with exact finite corroboration.

## Endpoint contract

Let T be a complex d by d unitary matrix. Let K be a complex N by N
unitary matrix with every entry of modulus 1/sqrt(N). Allow arbitrary
rectangular matrices A of size N by d and B of size d by N. Write

    T = B K A + H + E,
    rank_C(H) = h,
    ||E||_(2->2) <= eta < 1,
    M = ||A||_1 ||B||_infinity.

Here ||A||_1 is the maximum absolute column sum and ||B||_infinity is
the maximum absolute row sum. The bypass H can be dense, have arbitrary
coefficients and have arbitrarily large norm. No inverse, sparsity or
restoration condition is imposed on the adapters. Encoding into clean
workspace and erasing unwanted outputs are allowed in this relaxation.

The theorem is

    (d-h)(1-eta)^2 <= ||B K A||_F^2 <= d^2 M^2/N.             (1)

In particular,

    h >= ceil(d - d^2 M^2/[N(1-eta)^2]).                     (2)

An integer upper bound on h may be substituted on the left of (1).
The lower bound is vacuous when its right side in (2) is negative.
All ranks in this note are complex coordinate-matrix ranks. They are not
the logarithmic axis ranks used to price recursive native calls.

## Proof

Put X=BKA. For every i,j, the triangle inequality and flatness give

    |X_ij| <= N^(-1/2) (sum_s |B_is|) (sum_t |A_tj|)
            <= M/sqrt(N).

Squaring and summing over the d^2 entries proves the upper bound in (1).

Choose an orthonormal basis v_1,...,v_(d-h) for ker(H), and extend it to
an orthonormal basis of C^d. For each of the first d-h vectors,

    X v_i = (T-E) v_i,
    ||X v_i||_2 >= ||T v_i||_2 - ||E v_i||_2 >= 1-eta.

The squared Frobenius norm is the sum of the squared column norms in
any orthonormal input basis. Its remaining summands are nonnegative.
Therefore ||X||_F^2 >= (d-h)(1-eta)^2. This proves (1) and (2).
The elementary rank/energy argument is not claimed as a new general
matrix-analysis technique. The repository result is its dense-bypass
Gaussian fusion application and the sharp witness below.

## Gaussian specialization

Let C be the two by two matrix with diagonal a=(1+i)/2 and off-diagonal
b=(1-i)/2. Direct multiplication gives C* C=I and C times (1,1)^t=(1,1)^t.
For positive integers f,r,q, put

    n=2^f,  N=2^(rf),  d=q n,
    K=C^(tensor rf),  T=direct_sum_q C^(tensor f).

Both matrices are unitary, K is flat, and T fixes the all-ones vector.
Thus (1) implies

    h >= ceil(q*2^f - q^2 M^2 * 2^((2-r)f)/(1-eta)^2).      (3)

For two targets, one rank-two child, exact output and M<=1,

    h >= 2*2^f - 4.                                       (4)

For two targets, arbitrary r>1, and a dense bypass of rank at most one
target dimension, h<=2^f, equation (1) requires

    M >= (1-eta) * 2^((r-1)f/2) / sqrt(2).                (5)

A uniformly bounded M cannot satisfy
it for growing f when r>1 and eta is bounded away from one. This does not
price the bypass: even a single old complete transform has coordinate
rank 2^f, and a physical implementation of H needs its own full bill.

## The constant is sharp within the Gaussian family

Assume d<=N. Let u be the d-dimensional all-ones vector, e_0 the first
child coordinate, k=K e_0 and P=u u*/d. Then P is the orthogonal
projection onto span(u), and TP=P. For any real 0<=eta<1 choose

    A=(1-eta) e_0 u*/d,
    B=u k*,
    H=(1-eta)(T-P),
    E=eta T.

Since ||k||_2=1, BKA=(1-eta)P and T=BKA+H+E. Also

    rank(H)=rank(T(I-P))=d-1,
    ||A||_1=(1-eta)/d,
    ||B||_infinity=sqrt(N),
    M=(1-eta)sqrt(N)/d,
    ||BKA||_F^2=(1-eta)^2.

Both inequalities in (1) are equalities. Consequently the constant one
cannot be reduced, even for these Gaussian targets and children. This
does not assert attainability for every prescribed h or M. In the
two-target rank-two case, equality uses M=(1-eta)/2 and h=2*2^f-1.
The witness has dense, almost full-rank bypass and receives no physical
cost advantage from this identity.

## Scope and predecessors

ToikY [#7166](https://github.com/CrocSwap/integer-mult-bounds/pull/7166),
scientific head `6efb5d028b3212fba68edfb725608413622d6ab6`, supplies the
rectangular Gaussian adapter normalization and the sparse-bypass amplitude
test. A rank restriction does not bound column support. For example J/d
has rank one and no zero entries. Hence the old missing-entry step cannot
be substituted for the kernel argument above. No predecessor invoice or
native census is rechecked here.

Credit Clear1nsight #4932/#4045/#3989, Rohan Arun #7113, the retained
Gaussian native/compiler lineage, and the classical triangle inequality,
rank-nullity and orthonormal-basis facts. The model here concerns a local
endpoint. Arbitrary coordinate recoding that increases M, changed child
normalization, several children or a differently priced bypass require
their own analysis. No complete supplier or multiplication theorem follows.
