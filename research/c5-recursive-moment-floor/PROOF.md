# A sharp recursive moment on the named physical C5

## Contract and result

Use exactly the five complete planes `(13,23,35,16,34)` in that cyclic order
from the pinned PR2782 matching and labels. Each plane is nondegenerate of
binary dimension two. Adjacent planes are orthogonal; the other plane pairs
are nonorthogonal. These are actual physical planes, not an abstract graph
replacement. `verify.py` checks their complete rectangular tariff table.

Over Q, R or C, a strict scalar fit K has five diagonal blocks I2, zero
blocks between distinct nonadjacent planes, and arbitrary blocks between
adjacent planes. Allow any finite decomposition

```text
K = sum_t u_t v_t^T.
```

Transpose is ordinary transpose, including over C. Let A_t and B_t be the
plane supports of the two factors. A touched scalar port charges its whole
plane. Set r_t to the binary pairing rank between the complete plane spans
of A_t and B_t. Thus `0 <= r_t <= 9`. Scalar factors, signs, denominators and
asymmetry are unrestricted.

For every `0 <= a <= 1/20`,

```text
sum_t r_t^(1-a) >= 5 * 4^(1-a).                    (1)
```

Five explicit edge terms attain equality. For `a>0`, equality requires exactly
five positive-cost terms, each of rank four. Zero-cost terms may be present.
This is a local optimistic recursive-moment floor. A common normalization
by `m^(1-a)` preserves the comparison. It does not supply the other charges
or make the local terms into a physical supplier.

The scalar cost20 floor is predecessor work, thakrarsagar's PR3256 and
PR3268. The five-term classification is Nick Petalas's PR3248. The new
implication is that arbitrary-term rank concentration cannot improve this
core's small-saving moment. The finite product certificate below supplies
the missing implication; a scalar rank-mass bound alone does not.

## Zero-cost terms and the five-term boundary

A zero binary pairing rank means every scalar block on that term's support
lies between orthogonal planes. It touches no diagonal or nonadjacent block.
Its entire support is therefore free in the strict mask. Removing all such
terms leaves a strict fit. Discard zero factors too. We may now assume every
term has positive integer cost, and count only those terms.

Here is PR3248's classification argument, retained explicitly so the proof
needs no pending executable or foreign Git object. If a fit uses n terms,
write its factors as 10-by-n matrices A,B and let U_i,W_i be the two-row
spaces of their plane blocks in coefficient space F^n. The diagonal I2
makes both spaces two-dimensional with perfect mutual pairing. Nonadjacent
U_i,U_j are disjoint: a common vector annihilates W_i, so perfect pairing
forces it to vanish. Adjacent U_i,U_(i+1) both annihilate W_(i+3); hence their
intersection has dimension at least `6-n`. Within U_i its intersections with
its two neighbors are disjoint, so `2 >= 2*(6-n)`. Thus `n>=5`.

At n=5, write `H_i=U_i intersect U_(i+1)`. Each H_i is a line and
`U_i=H_(i-1) direct-sum H_i`. A chosen nonzero h_i in H_i annihilates W_j
except at its two incident planes. In any relation among the five h_i,
pairing with W_j forces both incident coefficients to vanish. Thus the h_i
form a basis. Its dual basis g_i gives
`W_j=span(g_(j-1),g_j)`. The two square basis matrices satisfy both
`H G^T=I` and `H^T G=I`. At each term coordinate t, therefore,
`sum_i h_i[t] g_i[t]=1`. Some product is nonzero. Both factor supports of
that term contain the incident orthogonal planes i,i+1, whose sum is a
nondegenerate four-space. Its binary pairing rank is at least four.
Consequently any five-term cost20 fit has exactly five rank-four terms.

The term-count hypothesis cannot be dropped. Splitting one edge term into
two unequal-support factors gives the exact rank profile `2,2,4,4,4,4`,
still of total cost20. The control suite checks that complete fitting matrix.
We do not claim that all cost20 histograms are identical.

## Physical weighted-rank and trace premises

Index the local planes by 0,...,4. Use the four forced I4 blocks

```text
Q = {(0,2), (0,3), (1,3), (1,4)}
```

and the two I2 singleton blocks 2 and 4. For a support pair A,B, let b_H be
one when both supports meet H and zero otherwise. Exact binary elimination
on all 1,024 ordered support pairs verifies the physical inequality

```text
d = 2r - 2 sum_(H in Q) b_H - b_2 - b_4 >= 0.
```

The fifth nonadjacent pair `(2,4)` is a further forced I4 block. Its hit
count must be at least four. Every zero-cost support pair has all six
selected block counts, d and the fifth-pair count zero, as checked directly.

For a decomposition, every I4 block needs at least four rank-one terms and
every I2 block at least two. Writing their excesses as x_H,y_2,y_4 and the
sum of d as D gives

```text
2C - 36 = 2 sum_H x_H + y_2 + y_4 + D,
C = sum_t r_t.
```

In particular C>=18. At C=18,19,20 the nonnegative integer slack has exactly
1,10,49 possibilities, respectively. All are enumerated, including cases
where a tight-block condition is lost because that block has excess.

If exactly k rank-one matrices sum to I_k, their square factor matrices
satisfy both `UV^T=I_k` and `V^T U=I_k`. Each summand has trace one. For
an individual term write z_i for its diagonal trace on plane i. It is zero
outside A intersect B. On any selected block whose hit count is exactly
its rank, necessarily `sum_(i in H) z_i=b_H`. These linear equations are
necessary over Q, R and C, without positivity or conjugation. Their rational
consistency is the same in all three fields. The primary checker solves
an affine path system. The separate checker uses Fraction elimination.
Consistent traces are not asserted to be realizable scalar factors.

## Exact product exhaustion

For each slack case retain every positive-cost support pair whose trace
equations are consistent. Its count increment consists of the four Q hits,
two singleton hits, d, and the fifth-pair hit. Track the first seven counts
exactly up to their target; cap the last hit count at four. Also cap the
positive term count at six, which distinguishes five from at least six.

The primary checker processes states by total integer cost. For each state
it keeps the largest exact integer product

```text
P = product_t r_t^r_t.
```

Keeping only the largest P loses no maximum: every continuation multiplies
it by the same positive factor. Equal count increments have the same cost,
by the weighted-rank identity. Every positive-cost term advances a bounded
count and goes to a strictly later cost layer. A case has at most
`35 * product_i(target_i+1)` states. Its product is at most `9^20`.
Thus arbitrary finite term counts reduce to a finite exhaustive domain,
not a heuristic term cap. At cost20 there can be at most twenty positive
terms, and zero-cost terms have already been removed legally.

The exact results in RESULT.json are:

- No target for cost18 or cost19 is reachable, even before imposing the
  scalar lower bound of five terms. This reproduces the predecessor floor.
- In every cost20 case, the product for at least six positive-cost terms is
  at most `640000000000`, strictly below `4^20=1099511627776`.

The maximum is in a necessary-condition relaxation, not an exhibited fitting
factorization. The separate implementation reconstructs all physical ranks
with dense F2 matrices, solves the trace systems rationally, and processes
states by exact term count rather than cost. It agrees on every case's
reachability and maximum. No predecessor executable is imported.

Two failure controls matter. Dropping the trace equations makes the cost18
target reachable. Dropping the scalar term-count premise permits a four-term
cost20 count image with product `5^20`, larger than `4^20`. That image is
not a fitting matrix. The controls prevent either relaxation from being
silently treated as the theorem.

## From products to the moment

For C=20 and at least six positive-cost terms, use weights `r_t/20` and
Jensen's inequality for the real exponential:

```text
sum_t r_t^(1-a)
 = 20 sum_t (r_t/20) exp(-a log r_t)
 >= 20 exp(-(a/20) sum_t r_t log r_t)
 = 20 P^(-a/20)
 >= 20 * 4^(-a) = 5 * 4^(1-a).
```

The last inequality is strict for a>0 because `P<4^20`. At five terms the
classification already gives the attaining rank profile. Costs below20
are excluded by the finite certificate.

For every C>=21, ambient rank nine gives

```text
sum_t r_t^(1-a) >= C * 9^(-a) >= 21 * 9^(-a).
```

The exact integer inequality `9*20^20 < 4*21^20` implies
`(9/4)^(1/20) < 21/20`. Therefore throughout `0<=a<=1/20`,
`21*9^(-a) > 20*4^(-a)`. This proves (1) for all larger costs as well.
No floating-point root or sampled saving parameter is used for acceptance.

For attainment take, cyclically, `w_i=e_(i,1)+e_(i+1,0)` and the five terms
`w_i w_i^T`. They partition all ten scalar ports. Their only off-diagonal
entries join orthogonal adjacent planes, where the mask is free. All
constrained entries and all five physical rank-four tariffs are checked.

## Limits

Only the named already-covered core is addressed. The other seventeen
covered cores and all five residual cores from PR3268 are unclaimed here.
No result on any residual core is assumed here. Local core bounds cannot
be added across overlapping cores. The saving interval is sufficient, not
claimed maximal. Changed labels, tariffs, scalar mask, block-linear factors,
access contracts or shared children require a new analysis. No native
implementation, physical invoice, supplier admission, formal-kernel theorem,
selected-frontier change or new kappa follows.
