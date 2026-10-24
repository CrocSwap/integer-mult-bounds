# A criterion for dyadic interfaces from complete minors

This result concerns algebraic interfaces. It does not assert physical
source access or a complete supplier. It applies to unions of the complete
square minors specified below. It does not apply to arbitrary port sets.

## Hypotheses

Work over the dyadic rationals `R = Z[1/2]`. Let `K` be an `r` by `rd`
matrix with entries in `R`. Partition its columns into `d` square blocks
`K_1, ..., K_d`, where

`K_j K_j^T = lambda I_r`

for every `j`. Here `lambda` is a positive power of two. Thus each block
is invertible over `R`, also satisfies `K_j^T K_j = lambda I_r`, and
`K K^T = d lambda I_r`. Assume `d >= 4`.

Select a union `S` of `k` blocks, and let `U` be the complement. Put
`G = K^T K`. Let `P` be `-I` on `S` and `I` on `U`. For the response
`J = I - G/lambda`, define the ordinary map

`H = I_U - K_U^T K_U/lambda`.

All formulas below use column vectors. The maps act on arbitrary data.

## Inverse formulas and the exact dyadic criterion

For `k != d-1`,

`H^-1 = I_U + K_U^T K_U/[lambda(k-d+1)]`.

For `k != d-1`, define the data map

`A = P + G/[lambda(k-d+1)]`.

If also `k != 1`, then

`A^-1 = P + P G P/[lambda(k-1)]`.

For an interior split `2 <= k <= d-2`, all four maps `H`, `H^-1`,
`A`, and `A^-1` have dyadic entries if and only if both integers

`k-1` and `d-1-k`

are powers of two. Hence some interior complete-minor dyadic interface
exists if and only if `d-2` is the sum of two powers of two. This is an
exact criterion within the specified family, not a search result.

To prove the formulas, set `G_U = K_U^T K_U`. The complete-minor identities
give

```text
G_U^2 = (d-k) lambda G_U,
K P K^T = (d-2k) lambda I_r,
G P G = (d-2k) lambda G.
```

Substitution into the two products for each claimed inverse gives the
identity. For the dyadic criterion, sufficiency follows from these
formulas. For necessity, restrict `H^-1` to any complete ordinary block.
Its principal block is `(1 + 1/(k-d+1)) I_r`. The numerator and denominator
are consecutive integers. Thus this block is dyadic only if `d-1-k` is
a power of two. Restrict `A^-1` to any complete selected block. Its
principal block is `(-1 + 1/(k-1)) I_r`. The same argument forces `k-1`
to be a power of two. These arguments also cover a denominator of one.

One can also check the criterion from determinants:

```text
det(H) = (k-d+1)^r,
det(A) = (-1)^(rk) [(k-1)/(d-1-k)]^r.
```

The determinant of `H` uses its `r` centre eigenvalues and the identity
action on `ker(K_U)`. The determinant of `A` follows from the matrix
determinant identity and the signed Gram above.

## Balanced serial gauges

Suppose `d` is even and `k = d/2`. Then `K P K^T = 0`. If `q_i` is row
`i` of `K`, all products

`(P q_i^T q_i)(P q_j^T q_j)`

are zero. Moreover, each row of `K` is unchanged by every shear
`I + t P q_i^T q_i`, for every scalar `t`. Therefore the product of the
`r` shears with `t = 1/[lambda(k-d+1)]` is `I + t P G` in any order.
Apply `P` after this product to obtain `A`.

A serial common-frame implementation can form each query in one owned
zero field, scatter it, then subtract the same query from the updated
data. The field returns to zero because that query did not change.
The inverse uses the opposite shear sign and the opposite order for `P`.
This statement supplies the cancellation rule. The costs of query
formation and scatter still depend on the entries and supports of `K`.

The balanced interface is dyadic exactly when `d/2-1` is a power of two.
Equivalently, `d = 2 + 2^(a+1)` for an integer `a >= 0`. The balanced
condition is necessary for this complete-minor query-preservation rule:
the signed Gram is `(d-2k) lambda I_r`.

## One selected minor: the remaining content kernel

For `k = 1`, the selected block of `-J` is zero. Let

`B = K_S^T K_U/lambda`, `D = K_U^T K_S/lambda`.

Then `BD = (d-1) I_r`. Each complete ordinary minor gives a square
dyadic-unit minor of `B`: for its block `B_j`, `B_j B_j^T = I_r`.

The data map exists when `d > 2`, but is singular:

`A = P - G/[lambda(d-2)]`,
`ker(A) = range(P K^T)`,
`dim ker(A) = r`.

Indeed `A P K^T = 0`, by the signed Gram. Conversely, `Ax=0` implies
`x` lies in this range. This singularity is over the rationals. More
precise dyadic arithmetic cannot remove it.

If an odd prime `p` divides `d-1`, then this same interface also meets
the hypotheses of the query-separation theorem in
`../dyadic-query-separation-review-20261018/REVIEW.md`. For any dyadic
matrix `M` for which `MD` is a dyadic unit matrix, the stacked map
`[B;M]` has rank `2r` over the rationals. To see this, reduce modulo `p`.
The product `BD` is zero, `B` has row rank `r`, and `MD` is invertible.
In a relation `u B + v M = 0`, multiplication by `D` first gives
`v=0`, then `u=0`. The minor that proves rank `2r` modulo `p` is also
nonzero over the rationals. This is a bound on linear observations in
that interface. It is not a bound on native children or on all encodings.

## Application to the two actual complete-minor families

The original eight-centre family has `d=14`, `lambda=4`, and `r=8`.
Its interior complete-minor dyadic interfaces have `k=5` or `k=9`.
The balanced choice `k=7` fails the criterion because `k-1=6`.

The changed 48-port family has `d=6`, `lambda=2`, and `r=8`.
Its only interior complete-minor dyadic interface has `k=3`. All
`binomial(6,3)=20` choices have the same identities. They select 24
ports and leave 24 ordinary ports in this block. Their signed Gram is
zero, which gives the serial query-preserving gauge used by the producer.
The separate 64-port Hadamard block remains outside this theorem.

For one selected minor in the changed family, `BD=5I_8`, and the data
map still has an eight-dimensional kernel. The preceding observation
bound applies modulo five. Thus the new response changes the complete
minor structure and permits the 24/24 interface; a return to an 8/40
interface does not remove the content kernel or the dyadic query split.

The physical native words are proved only for the two actual pinned
families. The abstract theorem does not supply native words for every
value of `d` that meets the arithmetic criterion.

This is AI-assisted research. It uses the producer's changed response
and complete minors, and the earlier complete-minor and query-separation
results from this campaign. It makes no kappa or frontier claim.
