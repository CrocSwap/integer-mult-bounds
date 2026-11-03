# Exact dyadic balancing range on a cycle

This contribution was produced by Nick Petalas. Claim type: scoped written
proof with exact finite corroboration. New work is Apache-2.0. Independent
human and formal proof-kernel review are unclaimed.

## The integer problem

Let L>=1 and let d_0,...,d_(L-1) be arbitrary integers. Subscripts are cyclic.
A feasible vector is an integer vector s satisfying

    s_i - s_(i-1) >= d_i,       i=0,...,L-1.                 (1)

Its span is max_i s_i - min_i s_i. A proper cyclic interval is a consecutive
list of edges of length 1,...,L-1. At L=1 this collection is empty. Put

    H(d) = max({0} union {sum_(i in I) d_i : I a proper cyclic interval}).

**Theorem.** If sum_i d_i>0, (1) is infeasible. If sum_i d_i<=0, its exact
minimum span is H(d). One attaining vector, normalized to have minimum zero,
is

    s_i = max(0, max_(1<=k<L) sum_(j=0..k-1) d_(i-j)).     (2)

The formulas include zero total demand, negative demands, repeated optima and
the one-edge cycle. They impose no computational upper bound on L or |d_i|.

**Proof.** Summing (1) gives 0>=sum_i d_i, proving infeasibility in the first
case. Summing (1) along any proper cyclic interval gives
s_end-s_before >= sum_(i in I) d_i. Consequently every feasible span is at
least H(d).

Suppose the total is nonpositive. Each summand in s_(i-1)+d_i is either the
one-edge sum d_i or the sum of a consecutive path ending at i of length
2,...,L. Sums of length at most L-1 occur in (2). The length-L sum is the
nonpositive total and is at most the zero term in (2). Thus
s_(i-1)+d_i<=s_i, and the constructed vector is feasible. For L=1 the same
assertion is d_0<=0 with s_0=0.

Every entry in (2) lies in [0,H(d)], so its span is at most H(d). The lower
bound just proved forces equality. When H(d)>0, some entry equals H(d), and
span equality then forces some entry to equal zero. When H(d)=0 every entry
is zero. This also proves the asserted normalization. QED.

This is an application of classical difference constraints and longest-path
potentials. The contribution is the exact binary scaling range and its
precision interpretation for the cyclic interface below; no priority for
the general optimization method is claimed.

## Weighted cyclic recurrence

Let every a_i be a fixed nonzero complex number and let beta>0. Consider

    y_i - a_i y_(i-1) = x_i.

Set y_i=2^s_i z_i and x'_i=2^-s_i x_i. Then the transformed recurrence is

    z_i - b_i z_(i-1) = x'_i,
    b_i = a_i 2^(s_(i-1)-s_i).                            (3)

The exact cap |b_i|<=beta is equivalent to (1) with

    d_i = ceil(log_2(|a_i|/beta)).                         (4)

Indeed the difference s_i-s_(i-1) is an integer, so taking the ceiling loses
no feasible dyadic scaling. The theorem therefore gives a necessary and
sufficient dyadic balancing criterion and the exact minimum scale span for
arbitrary complex phases. For |a_i|=2^e_i and beta=2^-t with integer e_i,t,
the demands are simply e_i+t. No logarithmic approximation is involved.

Let S=diag(2^s_i) and W_a y=(a_i y_(i-1))_i. Equation (3) says exactly

    S^-1 (I-W_a) S = I-W_b.

It preserves the equation for every source coordinate and right-hand side,
and preserves the cycle product product_i a_i. If that product differs from
one, both systems are nonsingular. Nonsingularity is not needed for the
balancing theorem. This is an algebraic change of variables, not a physical
source-preserving or dirty-restoring program.

### Dyadic feasibility is stricter than a product condition

Continuous positive diagonal scalings can attain the cap exactly when
product_i |a_i| <= beta^L. One direct proof replaces the integer demands in
(1) by their real logarithms and distributes the nonnegative total slack
equally among the L edges; integrating those differences constructs the
real scales. Multiplying the cap inequalities proves necessity.

Dyadic scales require the stronger sum of the ceilings in (4) to be
nonpositive. For a=(3/5,2/5), beta=1/2, the product 6/25 is strictly below
1/4. Real diagonal factors (6/5,1) give magnitudes (1/2,12/25).
But d=(1,0), so no dyadic scales attain that cap. This is an explicit
quantization obstruction, not a failed search.

## Exact grid and error consequences

For any feasible dyadic scaling, the infinity-norm and Euclidean condition
numbers of S are both 2^(max s-min s). Thus the smallest possible condition
number at the requested cap is exactly 2^H(d), attained by (2).

Normalize min s_i=0. If each original input belongs to 2^-w Z with integer
w>=0, every x'_i=2^-s_i x_i belongs to the common grid 2^(-w-H) Z for the
attaining vector. That common grid is sharp over arbitrary grid inputs:
at a coordinate with s_i=H, the permitted input x_i=2^-w becomes exactly
2^(-w-H). When w+H>0 it does not belong to the next coarser binary grid.
The same statement applies separately to real and imaginary components.

Conversely an error vector eta in z becomes S eta in y. For this normalization,

    ||S eta||_infinity <= 2^H ||eta||_infinity,

with equality for an error supported at a maximum-scale coordinate.
Uniform balanced-coordinate errors must therefore be bounded by
2^(-p-H) if this norm transfer alone is to guarantee original error 2^-p.
These are exact grid-containment and norm-transfer statements. They do not
prove a rounded solver needs that many bits: nonuniform grids, data-dependent
precision, a different algorithm or a differently priced representation
have not been excluded. A common shift of all s_i changes absolute input and
output scales but cannot change the condition number or relative grid span.

For the two-coordinate coefficient family

    a=(2^k, 2^(-k-2)),       beta=1/2,       k>=1,

we obtain d=(k+1,-k-1), H=k+1, s=(k+1,0), and b=(1/2,1/2).
Both coefficients are perfectly balanced and the product is still 1/4.
Every such dyadic balancing has condition number at least 2^(k+1).
For arbitrary original inputs on one binary grid, direct exact rescaling
therefore needs a relative grid separation of k+1 bits. Balancing this family
cannot supply a k-independent grid or conditioning guarantee by itself.

## Relation to the open interface

Sricharan Vagvala / theon199's
[PR1481](https://github.com/CrocSwap/integer-mult-bounds/pull/1481),
head `753c1b60eaf6ef464e258ca1fc022e53b5032cff`, asks to price diagonal
balancing, including both grids, numerical height, scaling and restoration.
Its all-cut rounded-scan obstruction is inherited context and is not
replayed here. The new step solves the dyadic scale-range subproblem exactly
and quantifies a necessary relative grid and conditioning cost. It does not
settle the full physical balancing invoice posed by that question.

Credit Chafik Boukhalfa / PR628 and PR905 for the retained weighted-scan
setting, Charles Bethin / PR764 for the contraction-based error context,
and the predecessor's retained cyclic-kernel and precision lineage.
No predecessor numerical result or executable is required by this proof.
Coefficient access, reversible scaling instructions, arbitrary dirty
restoration, scalar scratch, bit movement, storage, complete supplier costs,
all-size admission and the five selected framework assumptions remain open.
