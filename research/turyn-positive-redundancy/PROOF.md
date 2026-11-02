# Exact cost of positive redundant Turyn encoders

This scoped result was produced by Nick Petalas. Apache-2.0.

## Contract

Let the port labels be vectors ell_i in F_2^h. For a real column v, charge

    c(v) = dim_F2 span {ell_i : v_i != 0}.

Consider an exact factorization K = A H A^T with finitely many real encoder
columns and a real symmetric positive definite metric H. The bill is the sum
of c(a_j). Zero columns cost zero; R counts only nonzero columns. The metric
and scalar work are granted free. This is an algebraic encoder support bill,
not a complete physical or recursive invoice. Positive sums of outer products
are the diagonal-metric case; a dense metric can couple different columns.

## Range lemma

For every such factorization, range(K) = range(A) and rank(K) = rank(A).
Indeed, for every real x,

    x^T K x = (A^T x)^T H (A^T x).

Positive definiteness makes this zero exactly when A^T x = 0. If Kx = 0
then x^T Kx = 0, while A^T x = 0 implies Kx = 0 directly. Thus
ker(K) = ker(A^T). Taking orthogonal complements proves the range identity.
The argument permits dependent columns, any finite redundancy, arbitrary
real coefficients and a dense positive definite metric.

## Fixed-kernel cost theorem

Suppose K is positive semidefinite, rank(K) = r > 0, and every nonzero
v in range(K) has c(v) = h.
Then every positive definite factorization with R nonzero columns satisfies

    R >= r,  sum_j c(a_j) = h R.

Every column lies in range(K), so every nonzero column costs h. Also
rank(A) <= R. These prove both conclusions.

Every integer R >= r is attainable. A positive semidefinite K of rank r
has a real Gram factor K = U U^T with r independent columns. Replace the
first column by t = R-r+1 identical copies. Give each duplicate weight 1/t
and every other column weight 1 in a diagonal H. The resulting A H A^T
is still K, every column is nonzero and H is positive definite. Hence
the minimum bill at prescribed R is exactly hR. No coefficient-height or
physical-cost bound is asserted by this construction.

## Turyn specialization and predecessor premises

DominikScholz's [PR598](https://github.com/CrocSwap/integer-mult-bounds/pull/598)
supplies two results that this package cites without replaying:

1. The full canonical Turyn product kernel has 23,040 ports and real rank
   512. It is the Gram kernel of the 512 tensor coordinates, up to a positive
   normalization. See `research/leech-lattice/TURYN.txt`, "Product kernel".
2. Under the existing direct-sum 27-bit labels, every nonzero real tensor
   encoder has label-support rank 27. See the final section of
   `research/turyn-port-labels/PROOF.txt` and its README's explicit restriction
   to rank-minimal factorizations and encoders in the tensor column space.

The tensor-coordinate matrix has full column rank, so its column space is
range(K). Applying the theorem gives the exact algebraic optimum

    B(R) = 27 R for every integer R >= 512.

No factorization in this class exists with R < 512. The optimum over all
finite positive definite factorizations is therefore 13,824. Every nonzero
redundant column adds exactly 27. The cited tensor Gram factor attains the
minimum, and duplication attains every larger R. The extension to arbitrary
positive redundancy is new here; the geometry, rank and support theorem
remain the predecessor's results. The elementary Gram range identity is
classical, and no general linear-algebra priority is claimed.

## Why the metric hypothesis matters

Let u = (1,1)^T, K = u u^T and the port labels be e_1,e_2. Every nonzero
vector in range(K) has label-support rank two.

* For A = I_2 and H = [[1,1],[1,1]], the equality K = A H A^T holds, but
  H is singular positive semidefinite. Each column of A costs one and lies
  outside range(K). The formula hR would predict four instead of the actual
  two. Thus a singular positive semidefinite coupling metric is outside
  the theorem.
* For A = [u,e_1,e_1] and H = diag(1,1,-1), the same K is obtained.
  The outside columns cancel. Its bill is four rather than hR = six.
  This escapes confinement but does not supply a cheaper Turyn decoder.

A diagonal nonnegative metric can discard its zero-weight terms and apply
the theorem to the positive-weight terms. A singular dense metric cannot
generally discard original columns individually, as the first example shows.
Asymmetric factorizations and signed cancellations remain open routes.

## Verification boundary

The proof is all-size real linear algebra. The verifier checks new bounded
rational examples, attaining duplications, dense positive definite metric
changes and the boundary counterexamples. Finite checks do not prove the
all-size theorem or re-establish the cited PR598 premises. Independent human
and formal proof-kernel review are unclaimed. No physical supplier, new kappa,
selected-frontier update or complete multiplication theorem follows. All five
selected framework assumptions remain separate.
