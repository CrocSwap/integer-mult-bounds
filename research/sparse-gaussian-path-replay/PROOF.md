# Exact row-sparse Gaussian evaluation

This contribution was produced by Nick Petalas. Claim type: scoped
implementation-preservation proof, with exact finite conformance. Apache-2.0.

The retained PR800 matrix representation is a triple `(e, ar, ai)`, representing
the matrix with entries `(ar[8*i+j] + i*ai[8*i+j])/2^e`. Each component array
has 64 integer entries. The source supplies immutable tuples and nonnegative
integer exponents. The evaluator is internal to this authenticated consumer;
it does not parse externally supplied matrices.

For input matrices A and B, write their Gaussian numerator entries as
`x+iy` and `u+iv`. The numerator of entry `(i,j)` of their product is

```text
real = sum_k (x_ik*u_kj - y_ik*v_kj)
imag = sum_k (x_ik*v_kj + y_ik*u_kj).
```

The denominator exponent is `e_A+e_B`. The original evaluator omits a summand
when the left Gaussian entry is zero, but still evaluates every right-hand
column for each remaining left entry. The new evaluator first lists, in
increasing column order, every nonzero Gaussian entry in each right-hand row.
It then traverses those entries for each nonzero left entry.

Every newly omitted summand has `u=v=0` and hence contributes zero to both
integer sums. Every remaining summand is evaluated once with exactly the
original signs. For each output entry the surviving summands are still added
in increasing k order. All arithmetic is exact integer arithmetic, so even
the order of summation is unnecessary for equality. No overflow or floating
rounding is introduced. Thus the entire unnormalized triple is equal for
every pair of matrices in the declared representation.

The adapter invokes the unchanged source `normalize` with that triple and
the unchanged projective flag. Both the ordinary result and the minimum over
the four central phases therefore agree, including zero matrices and complete
Gaussian cancellation. It retains the original 40,000-entry LRU result-cache
capacity and key convention. It adds no persistent row or product cache.

Only `dense.multiply` is replaced. All consumers use the same authenticated
module object. Each call returns the same immutable canonical matrix, so
induction over the finite execution preserves every branch, exception,
grouping key, path, conjugation, independent Pauli reconstruction, rank,
frame, certificate decision and scientific result. In particular, replacing
the multiplication engine does not replace dense conjugation with symbolic
tableau transitions. The two independent path engines remain distinct.

The comparison mode additionally checks the replacement against the original
on every reached request, including cache hits, and hashes the ordered input,
flag and output stream. Its cache-miss counters agree. Work counts are computed
only on misses. If `a_k` is the number of nonzero entries in column k of A
and `b_k` the number of nonzero entries in row k of B, the original evaluates
`8 sum_k a_k` Gaussian products and the new evaluator evaluates
`sum_k a_k*b_k`. The difference counts precisely the omitted zero products.
It does not count real multiplications, CPU instructions or cache hits.

The written argument is uniform over exact integer component values at the
fixed matrix dimension. Bounded conformance tests corroborate it; they are
not a proof-kernel certificate or an independent audit of PR800's exclusion
theorems. Sparse multiplication is classical. The new contribution is its
source-bound complete-consumer implementation and evidence.
