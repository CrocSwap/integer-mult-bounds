# Cyclic band elimination with an explicit variable gap

## Contract and result

Let A be an N by N real dyadic matrix with positive diagonal. Suppose

    a_ii - sum_(j != i) |a_ij| >= delta > 0,
    max_i sum_j |a_ij| <= M,
    a_ij = 0 if min(|i-j|, N-|i-j|) > W.

Here 0 <= W < N, and delta need not be constant. The input matrix is supplied
on a grid of precision p. A complex right-hand side b is supplied on the
internal grid or a coarser grid. Use the vector norm max_i(|Re b_i|+|Im b_i|),
and suppose it is at most Y>0. Let t>0 be the required solution error.

Put K=max(1,2M). Choose internal grid step h=2^-q, q>=p, such that

    h <= delta/(2 N K),
    h <= t delta^2 / (2 N K Y + 4 delta + 12 M^2).

The algorithm below returns x with ||x-A^-1 b|| <= t. It has at most
4 N W^2 factor products and at most 8 N W products per complex solve. It
retains at most (4W+1)N factor entries, including zero entries in its fill
pattern. Setup and solve use O(N(W+1)) numeric storage. These are arithmetic
counts. They do not include matrix formation, a physical tape layout or a
complete native/outer invoice.

Thus q=max(p, log2(1/t)+O(log N+log(1+M)+log(1+Y)+log(1+1/delta))).
In particular, a gap delta=1/(16r) costs logarithmic guards in r. The theorem
does not require ||A-I|| to be bounded by a fixed constant below one. It does
not assert that any unnamed Gaussian family satisfies the input contract.

## Exact row-dominance bounds

This paragraph is classical Gaussian elimination, with constants retained for
use below. Let a real matrix B have positive diagonal, row gap at least g>0
and row norm at most R. In one Schur step, write l=b_ik/b_kk. The remaining
row gap increases by at least |l| times the pivot row gap, and the remaining
absolute row sum decreases by at least that same quantity. This follows from
the triangle inequality after deleting column k. The diagonal stays positive:
the update cannot cross zero while its row gap remains positive.

All pivots are at least g, and every surviving row sum is at most R. For a
fixed row, let s be the sum of the absolute multipliers used to eliminate it.
The final gap is at least g(1+s), whereas the final row sum is at most R-gs.
The gap is no larger than the row sum. Therefore

    ||L|| <= (R+g)/(2g),     ||U|| <= R.

Every upper row has gap at least g. The maximum-coordinate argument gives
||B^-1|| <= 1/g and ||U^-1|| <= 1/g. Also L^-1=U B^-1, so
||L^-1|| <= R/g. The corresponding bounds hold for leading principal factor
pairs, since a principal submatrix cannot reduce a row-dominance gap.

## One rounding per factor entry

Use integers at scale S=2^q. Store the unfinished Schur entries C_ij at scale
S^2. Initially C_ij=A_ij S^2, exactly. At pivot k:

1. Set U_kj=trunc(C_kj/S) for j>=k. These integers have scale S.
2. Set L_ik=trunc(C_ik/U_kk) for i>k. These integers have scale S.
3. Update C_ij -= L_ik U_kj exactly for every remaining nonzero pattern pair.

Here trunc rounds toward zero. The diagonal of L is one. No product or Schur
update is rounded. Round only the factor entry at its final use.

Expanding the stored integer updates gives a factor residual E=LU-A.
Each upper entry has residual at most h. Each lower entry has residual at
most h times its pivot magnitude. The same identities hold for a partial
factorization: assign these residuals to completed entries of A, and set the
residuals of unfinished entries to zero. Its completed factors are exact
factors of this partially perturbed matrix.

This gives a closed induction, not an assumption of stable factors. Suppose
previous pivots are at most 2M. The errors in a newly completed upper row are
at most h, and those in a lower column are at most 2Mh. Thus the partial row
residual is at most e=NKh <= delta/2. The partially perturbed matrix has gap
at least delta-e and row norm at most M+e. Apply the preceding exact bounds.
The new upper row has norm at most M+e <= 3M/2 < 2M, and its pivot is at least
delta-e >= delta/2. This proves the induction and completes every division.
After all entries are completed, B=LU satisfies

    ||E|| <= e,
    ||U|| <= 3M/2,       gap(U) >= delta/2,
    ||L|| <= 2M/delta,
    ||B^-1|| <= 2/delta, ||L^-1|| <= 3M/delta.

The sharper L estimate follows by using R=M+e and g=delta-e in the exact
formula: (R+g)/(2g)=(M+delta)/(2(delta-e)) <= 2M/delta.

## Solve residual and error

For each real and imaginary component, accumulate each triangular dot product
exactly, then round the solved coordinate once to the q-bit grid. The forward
and backward equations are

    L z = b + f,         ||f|| <= 2h,
    U x = z + g,         ||g|| <= 3Mh.

The factor two accounts for the two components. Thus

    B x = b + r,
    ||r|| <= R_s = 2h(1+3M^2/delta).

Compare with x_*=A^-1 b. Since ||A^-1||<=1/delta and
||B^-1||<=1/(delta-e),

    ||x-x_*|| <= (eY + delta R_s)/(delta(delta-e))
               <= h(2NKY+4delta+12M^2)/delta^2 <= t.

The last inequality is the stated precision choice. If a caller rounds this
result to a different output grid, it must add that rounding error. If it
formed A as an approximation to another operator, it must also add the
coefficient and truncation errors through a separate perturbation bound.

## Uniform integer range

The proof first analyzes the same algorithm over unbounded integers. Put

    L_0=2M/delta, U_0=3M/2,
    Z=(3M/delta)(Y+2h), X=(2/delta)(Y+R_s),
    C=max(1, M+L_0 U_0, Y+L_0 Z, Z+U_0 X, L_0,U_0,Y,Z,X).

All factor, forward and backward accumulators have absolute value at most
C S^2. For a partial dot product use the sum of absolute terms and the bounds
on the full row of L or U. The leading-principal bounds control all forward
prefixes. Every backward coordinate is a coordinate of the final vector, so
the final bound also controls each stored coordinate. It does not depend on
that coordinate being generated last. A signed integer width

    2q + ceil(log2 C) + 2

therefore covers all products, sums, division numerators and stored integers.
The executable checks this range at every numeric update. This establishes a
uniform input bound; an observed peak from a finite test is not its proof.
The input and retained factors are preserved, and the owned forward buffer is
cleared after each solve. Clearing here is an array operation, not a physical
tape-erasure theorem.

## Cyclic fill and arithmetic cost

If N>2W, place the last W indices in a border set. The remaining indices form
an ordinary band of half-width W. Under natural-order elimination, an interior
pivot can touch only its next W interior indices and the W border indices.
An update can add only pairs among those indices; it cannot connect more
distant interior indices. Induction preserves this pattern. Each pivot
therefore has at most 2W later row neighbors and 2W later column neighbors.
Once only border indices remain, the same bound is immediate. If N<=2W, the
dense bound N-1<=2W suffices. W=0 is diagonal.

There are at most 4W^2 updates at a pivot, at most 2NW lower entries and at
most 2NW+N upper entries. One solve uses each strict triangular entry once
per real component. A complex solve therefore uses at most 8NW products,
plus 4N scalar truncations/divisions. Numeric storage is O(N(W+1)); active
Schur entries and retained factors can coexist within that order. Indexing,
allocation and Python overhead are not a certified native instruction tariff.

## Prior results and evidence

Dugongue's [PR #4554](https://github.com/CrocSwap/integer-mult-bounds/pull/4554)
proves a near-identity ordinary-band fixed-point algorithm and a periodic
Woodbury reduction with constant norm bounds. Ryanson Jonathan's independent
banded-inverse check retains that exact scope. The earlier batched principal-
window note uses noncyclic factors. [PR #5260](https://github.com/CrocSwap/integer-mult-bounds/pull/5260)
supplies the fixed385-row direct consumer; its matrix-specific residual does
not provide this all-size precision guarantee. This result supplies direct
cyclic fill, one-round factor residuals and explicit variable-gap guards.

Row-dominance and Gaussian-elimination stability are classical; see Nicholas
J. Higham's [growth-factor summary](https://nhigham.com/2020/07/14/what-is-the-growth-factor-for-gaussian-elimination/)
and the Wilkinson/Higham references there. No new general stability theorem
or global literature priority is claimed. The proof here makes the algorithm,
absolute error, integer range and cyclic cost explicit for this interface.

Exact tests include an independently transcribed pivoted rational solver,
symbolic cyclic fill and original-matrix residuals at larger sizes. These
corroborate the written all-size proof. Independent human or proof-kernel
review is not claimed. Source matrix formation, analytic recovery, native
relations, fixed tapes and the full multiplication invoice remain open.
No new kappa, production-family admission or selected-frontier change is made.

Prepared by Ali Romman with substantial OpenAI Codex assistance; Apache-2.0.
