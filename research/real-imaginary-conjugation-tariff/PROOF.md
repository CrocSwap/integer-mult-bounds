# Exact conjugation tariff for separate real and imaginary frames

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof. Finite rational checks corroborate the
construction. Independent human and formal proof-kernel review are unclaimed.

## Contract and theorem

Fix a positive integer n and real orthogonal n-by-n matrices P,Q. The target is

    T(x+iy) = Px + iQy,       x,y in R^n arbitrary.

There may also be any finite number s of arbitrary dirty complex coordinates.
The complete endpoint must be T direct-sum I_s, including all dirty returns.
Intermediate mixing with those coordinates is permitted.

A program is a fixed finite sequence with these operations:

- Any invertible complex-linear map on C^(n+s), at zero price in this model.
- Conjugation of one coordinate z_j, leaving every other coordinate unchanged,
  at unit price.

No other real-linear, nonlinear, approximate, branching or irreversible
operation is free. In particular, simultaneous conjugation of an arbitrary
block is not one unit-price call.

**Theorem.** The minimum paid-call count is exactly

    rank_R(P-Q).

It is independent of s. If P,Q are rational, an attaining program uses rational
real matrices as its complex-linear maps. It requires no square roots and no
dirty coordinates. The upper construction has r paid calls and 2r+1 displayed
linear instructions, where r=rank(P-Q); adjacent linear instructions may be
combined. This instruction count gives no physical scalar-cost bound.

This is an exact tariff in the declared relaxation, not a lower bound on all
possible real-linear provider alphabets or an admitted native supplier.

## Lower bound from the antilinear part

Every real-linear map S on C^d has a unique expression

    S(z)=A_S z+B_S conjugate(z).

Define b(S)=rank_C(B_S). For two such maps,

    B_(S R) = A_S B_R + B_S conjugate(A_R).

Rank subadditivity and the rank bound for a product imply

    b(S R) <= b(S)+b(R).

A complex-linear map has b=0. Single-coordinate conjugation has B=e_j e_j^t,
so b=1. Consequently, any program with k paid calls has b(endpoint)<=k,
irrespective of the number of dirty coordinates or intermediate mixing.

For the required endpoint,

    A = diag((P+Q)/2, I_s),
    B = diag((P-Q)/2, 0_s).

Its antilinear rank is rank_C(P-Q)=rank_R(P-Q). This proves the lower bound
and the dirty-workspace assertion. It also proves additivity for independent
direct-sum targets in this model. The last statement follows from the one
theorem by choosing block-diagonal P,Q, rather than from a separate search.

## A rank-tight rational reflection factorization

Set R=P^t Q. Then R is real orthogonal and rank(I-R)=rank(P-Q). We give the
classical Euclidean Householder reduction explicitly to specify the compiler.

For a nonzero real v put H_v=I-2vv^t/(v^t v). Suppose R is not identity.
Choose a coordinate e_j with Re_j != e_j and put v=Re_j-e_j. Since R preserves
length, H_v Re_j=e_j. If f is fixed by R, then

    f^t v = f^t R e_j - f^t e_j = (R^t f)^t e_j - f^t e_j = 0.

Thus H_v also fixes every old fixed vector, and H_v R fixes e_j in addition.
The new fixed space has dimension at least one larger. Conversely,

    I-H_v R = (I-R)+(I-H_v)R

differs from I-R by a rank-one matrix. Its rank can decrease by at most one.
It therefore decreases by exactly one. Repeating terminates after exactly
r=rank(I-R) steps, with

    H_(v_r) ... H_(v_1) R = I,
    R = H_(v_1) ... H_(v_r).

All v_j and H_(v_j) are rational when R is rational. Positive definiteness
ensures every nonzero v_j has v_j^t v_j>0. No assertion about arbitrary
indefinite forms is used.

## One coordinate conjugation per imaginary reflection

Let J_v act by J_v(x+iy)=x+iH_v y. Choose an index k with v_k != 0. Define
a rational real matrix S with first column v and, for every j != k, another
column

    u_j=e_j-(v_j/v_k)e_k.

The u_j form a basis of v-perp, so S is invertible. Explicit inverse
coordinates of a vector a are

    c_0=(v^t a)/(v^t v),
    c_j=a_j-v_j c_0,       j != k.

Write C_0 for conjugation of coordinate zero. It fixes the real parts of all
coordinates and flips only the imaginary part of coordinate zero. Therefore

    S C_0 S^-1 (x+iy) = x+i S diag(-1,1,...,1) S^-1 y = J_v(x+iy).

The identity follows because the displayed real matrix negates v and fixes
v-perp. Each J_v costs exactly one paid call. Apply J_(v_r),...,J_(v_1)
chronologically, then the free real matrix P. The result is

    x+iy -> x+iRy -> Px+iPRy = Px+iQy.

This uses exactly r conjugations and attains the lower bound. Extending each
operation by identity supplies every s without using its dirty contents.

## Discriminating two-coordinate example

Take P=I_2 and

    Q = [ 3/5  -4/5 ] = H_(-1,2) H_(0,1).
        [ 4/5   3/5 ]

Then rank(I-Q)=2. Conjugating the imaginary coordinates in the two displayed
reflection bases, in reverse order, attains two calls. One call is impossible
even with arbitrary complex-linear mixing and exactly restored dirty space.
The complete real target has positive determinant, so orientation alone does
not give this exclusion. Ordinary real displacement rank is not the right
tariff either: multiplication by i is a free complex-linear map with
rank_R(T-I)=2 and zero paid calls.

## Attribution and scope

Real-linear complex decomposition, rank subadditivity and the
Cartan-Dieudonne-Scherk reflection method are classical. See
[Rodriguez-Andrade, Aragon-Gonzalez, Aragon and Verde-Star, 2010](https://arxiv.org/abs/1011.1027)
for constructive reflection factorization and minimum-length context. The
reflection theorem itself and the antilinear-rank principle are not claimed
as new. The contribution is their exact combined tariff, the explicit rational
conjugation compiler and its dirty-workspace interface in this research model.
No general literature-priority claim is made.

The matrices P,Q need not commute. Free frames may be arbitrary complex-linear
maps, although the attaining compiler uses real rational ones. Arbitrary
real-linear targets outside the separate orthogonal P,Q contract are not
classified. Conjugation delivery, the actual scalar/basis invoice, native
frames, independent productive targets, all-size supplier compilation,
precision, stock, tape movement and the outer multiplier are not provided.
