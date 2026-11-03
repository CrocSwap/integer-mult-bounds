# Terminal-owner blocks for independent-stage BIT controllers

This scoped proof was produced by Nick Petalas. New work is Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

## Model and predecessor

Ali Romman's [PR5456](https://github.com/CrocSwap/integer-mult-bounds/pull/5456),
at `0d64d4d5d73f370182ada9825a611c86cfbf0049`, supplies the independent-stage
coordinate-support model, its coefficient equation, and the last-call
obstruction when every field has at most two owners and supports meet
pairwise in at most one field. Its more-than-two-owner opening motivates
this result. We remove the ownership bound. The general terminal-block
description below is the new step; the coefficient equation is inherited.

There are n finite field coordinates and f >= 1 ordered calls. Let
C_i be the coordinate support of call i, and let D_0,...,D_(f-1) be
independent commuting involutions. Work over

    R = F_2[(C_2)^f][q]/(q^2).

The group basis symbols remain linearly independent in characteristic two.
Equality means equality of every group and q coefficient, rather than
equality under a finite address representation. All scalar matrices below
have entries in F_2. Let T_i be diagonal, with D_i on C_i and 1 elsewhere.
Call i is

    F_i = T_i (I + q R_i),

where every column of R_i outside C_i is zero. Rows outside C_i are allowed.
The endpoint requirement is

    F_(f-1) ... F_0 = (T_(f-1) ... T_0) (I + q diag(t)),    t in F_2^n.       (1)

Thus a target may be D-only. No ownership bound or intersection condition
is initially imposed. The sharp linear endpoint statement below does not
require native chains. To derive the obstruction, the final call must have
u,w supported on C_(f-1) with

    u != 0,    R_(f-1) u = 0,    R_(f-1) w = u.                            (2)

The original four-support model has this chain on its two main directions
and arbitrary columns on two helper directions. Requiring it only at the
final call is a relaxation, so an exclusion also applies when every call
must have its own native chain. Arbitrary inputs and every output coordinate
are included in (1). There are no extra thin calls or intervening free maps
outside the displayed normal form.

## Exact terminal-block theorem

Write l = f-1. For a coordinate a in C_l, define

    mu(a) = max { i < l : a belongs to C_i },

using -1 if the set is empty. Partition C_l into one block for every
nonempty class with the same mu >= 0. Every coordinate with mu = -1 is
its own singleton block, even when several private coordinates exist.

**Theorem.** Every solution of (1) has R_l restricted to C_l block diagonal
in this partition. Conversely, every scalar matrix A on C_l with this
block pattern occurs as that restriction in a solution of (1), when
earlier R_i are unrestricted except for their column supports and t may
be chosen. This converse is for the linear endpoint relaxation; it does
not impose (2) or native chains on earlier calls.

For distinct a,b in C_l, the theorem says exactly that a nonzero terminal
entry is possible in this relaxation if and only if

    mu(a) = mu(b) >= 0.                                                     (3)

### Necessity

Let s_i(a) be the bit vector of earlier supports containing a. Factoring
all T_i to the left and using q^2 = 0 gives the inherited exact coefficient
formula

    (T_(f-1) ... T_0)^(-1) F_(f-1) ... F_0
      = I + q sum_i T_<i^(-1) R_i T_<i,
    T_<i = T_(i-1) ... T_0.

The coefficient from R_i(a,b) therefore has group label

    s_i(a) XOR s_i(b).                                                       (4)

Only calls containing b can contribute to column b. Suppose first that
mu(a) != mu(b), and put k = max(mu(a),mu(b)). At stage k exactly one
of a,b is present. Consequently the terminal label in (4) has bit k equal
to one. Every earlier possible contributor j to column b has
j <= mu(b) <= k, and its prefix s_j omits bit k. Its label has bit k
zero. Independence of the D symbols then forces R_l(a,b) = 0 in the
off-diagonal endpoint equation.

If mu(a) = mu(b) = -1, no earlier call contains b. There is no earlier
contributor to cancel R_l(a,b), so it is again zero. These are exactly
the forbidden pairs in (3), proving necessity. Notice that the argument
counts all earlier owners of b. It does not discard a third or later owner.

### Sufficiency in the stated relaxation

Set R_l equal to A on C_l and zero elsewhere. For each off-diagonal
entry A(a,b) = 1, (3) gives an earlier call i = mu(a) = mu(b). Put the
same entry into R_i and put every other earlier entry equal to zero.
Both a and b belong to C_i, so these matrices obey the column restriction.

Neither a nor b belongs to any support strictly between i and l. Both
belong to C_i. Their labels in (4) at stages i and l are therefore equal.
The two copies cancel over F_2. This happens entry by entry, without
interactions, because q^2 = 0. All remaining terms are diagonal with
identity group label. Choose t to be diag(A) on C_l and zero elsewhere.
This proves (1) and the claimed converse. It supplies no native-chain
guarantee for these earlier matrices.

## Consequence for unbounded ownership

**Corollary.** If the final support meets every earlier support in at
most one coordinate, (1) and (2) cannot both hold. In particular, no
nonempty controller with pairwise intersections at most one and a native
main chain in every call can close its diagonal endpoint, regardless of
how many calls own an individual coordinate. Support size four is allowed;
the proof also permits other finite support sizes.

Indeed, two different coordinates with the same nonnegative mu = i
would both belong to C_i intersect C_l. The intersection hypothesis
forbids this, so every terminal block is a singleton and the restriction
A of R_l is diagonal. Since u,w are supported on C_l, restricting (2)
gives A u = 0 and A w = u. Over F_2, a diagonal matrix has A^2 = A, hence

    0 = A u = A^2 w = A w = u,

contrary to (2). Rows outside C_l cannot remove this restricted contradiction.
The target flags t are unused, so allowing D-only outputs does not help.

More precisely, any completed controller in this model whose final call
has a native chain must repeat a pair of terminal coordinates in one
earlier call, with neither coordinate used between that call and the
terminal call. Mere extra ownership of separate coordinates cannot do this.

## A full three-owner control outside linear intersections

Take three calls with C_0 = C_1 = C_2 = {0,1,2,3}. On the first two
coordinates use, respectively,

    A = [[0,1], [0,0]],
    B = [[0,0], [1,0]],
    C = [[1,1], [1,1]],

and extend every matrix by zero on the other two coordinates. Each has
a native main chain. The respective (u,w) are (e_0,e_1), (e_1,e_0),
and (e_0+e_1,e_0). Their sum is diag(1,1,0,0). All T_i are scalar
on the four-coordinate space, so the full word is exactly

    D_2 D_1 D_0 (I + q diag(1,1,0,0)).

Every field has three owners. This is an algebraic boundary control,
not a funded supplier or a new native implementation. Its four-coordinate
intersections are outside the corollary. It also prevents interpreting
the result as a universal many-owner obstruction.

## Relation to the existing results

The two-owner linear case was already proved by PR5456 and is not a new
claim. Brian's [PR5507](https://github.com/CrocSwap/integer-mult-bounds/pull/5507)
at `1691a6024b60bdf28d7a2eed13cb32d78e2ea5b4` permits arbitrary parallel
intersections but keeps at most two owners, and proves a complete funding
obstruction in that class. Our result permits unbounded ownership and
excludes linear intersections. It makes no claim for general multigraphs
with unbounded ownership. Its exact terminal-block statement may also be
used as a necessary condition when earlier intersections are arbitrary.

The construction of Fano supports and the binary matrix identities used
for corroboration are classical. No global literature priority is claimed.
Physical native realization, complete paid/productive invoices, uniform
compiler closure, precision/tape and all-size multiplication remain outside
this scoped algebraic proof. The selected frontier is unchanged.
