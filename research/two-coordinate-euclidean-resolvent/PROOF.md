# Exact two-coordinate Euclidean envelope

## Statement

Fix real 0 < rho < 1 and beta >= 1. Let E run over all complex 2-by-2
matrices with absolute row sums at most rho and absolute column sums at
most beta*rho. Put

    c = min(beta-1, 1),
    t = rho*c / (1-rho+rho*c),
    L = 1-t+t^2 + t*sqrt(t^2-2t+2).

Then the exact maximum is

    max ||(I-E)^(-1)||_2 = sqrt(L)/(1-rho).

One attaining matrix is

    E_* = rho * [[1, 0], [c, 1-c]].

The theorem allows all complex phases and fractional beta. It concerns
exact matrices and the Euclidean operator norm. It assumes no support or
zero-diagonal restriction. Dimension is exactly two.

## 1. Reduction to nonnegative saturated rows

For M=|E|, the row cap makes both Neumann series converge, and

    |(I-E)^(-1)| <= (I-M)^(-1)

entrywise. A nonnegative entrywise comparison A<=B implies
||A||_2<=||B||_2: apply |Ax|<=A|x|<=B|x| to every x. The same argument
therefore bounds the complex resolvent by its nonnegative comparison.

We may fill the rows of M to sum exactly rho while keeping each column
sum at most beta*rho. Indeed, the two row deficits have total 2rho-sum M;
the two column capacities have total 2beta*rho-sum M, at least that much.
Every row can use either column. Greedily filling a deficient row against
available columns therefore cannot fail: before each such row, remaining
total capacity is at least remaining total deficit. This gives M' >= M
with both row sums rho and the same column caps. The Neumann series and
the preceding norm comparison give

    ||(I-M)^(-1)||_2 <= ||(I-M')^(-1)||_2.

No prescribed support is preserved by this filling step. That is why the
theorem does not claim an optimum with prescribed zeros.

## 2. The stochastic polygon

Write M'=rho P, where

    P = [[a, 1-a], [b, 1-b]],  0<=a,b<=1.

Set s=a+b-1 and d=a-b. The column caps say |s|<=beta-1; the four entry
inequalities say |s|+|d|<=1. Conversely these inequalities describe the
entire feasible polygon. Conjugating by the coordinate swap changes s to
-s and preserves d and the norm, so assume

    0 <= s <= c,  -(1-s) <= d <= 1-s.

In the orthonormal basis u=(1,1)/sqrt(2), v=(1,-1)/sqrt(2), P becomes

    [[1, s], [0, d]].

Consequently its resolvent is

    [[alpha, alpha*rho*s/(1-rho*d)], [0, 1/(1-rho*d)]],
    alpha = 1/(1-rho).

All entries displayed are nonnegative. For fixed s they increase
entrywise with d, so the largest norm occurs at d=1-s. The resulting
matrix is

    alpha B(t_s),
    B(t) = [[1, t], [0, 1-t]],
    t_s = rho*s/(1-rho+rho*s).

## 3. The final one-variable maximum

The map s -> t_s is increasing, with t_0=0 and 0<=t_s<1. Also
||B(t)||_2>=1 because B(t)(1,0)=(1,0). For 0<=u<=v and v>0,

    B(u) = (u/v) B(v) + (1-u/v) I,

so convexity of the operator norm gives

    ||B(u)||_2 <= (u/v)||B(v)||_2 + (1-u/v) <= ||B(v)||_2.

Thus s=c maximizes the norm. A direct calculation gives

    tr(B(t)^T B(t)) = 2(1-t+t^2),
    det(B(t)^T B(t)) = (1-t)^2.

The larger eigenvalue is L above, since the discriminant divided by
four is t^2(t^2-2t+2). This proves the upper bound. The feasible matrix
E_* has s=c and d=1-c, so every final inequality is attained. This
proves equality and supplies the promised maximum, not only a supremum.

## Consequences and a worked example

At beta=1, the value is exactly 1/(1-rho). At beta>=2, the column
constraint is redundant and the formula uses t=rho. These cases are
included in the proof, without a limiting argument.

At rho=1/2, beta=3/2, the attaining matrix and inverse are

    E_* = [[1/2, 0], [1/4, 1/4]],
    (I-E_*)^(-1) = [[2, 0], [2/3, 4/3]],
    ||(I-E_*)^(-1)||_2 = (2/3)*sqrt(7+sqrt(13)).

## Scope and credit

This settles only dimension two of the exact-finite-optimum question in
zhaobenny's PR6816. Its dimension-growth theorem is not used as a lemma.
Nick Petalas PR6788 and ToikY PR6806 concern the distinct induced 1-norm
problem. Nonnegative Neumann comparison, stochastic coordinates,
convexity of a norm and the 2-by-2 singular-value formula are classical.
The contribution is their exact optimization for this cap class; no
general literature-priority claim is made.

This is a scoped written proof, corroborated by finite exact arithmetic.
It is not a physical Gaussian caller, complete invoice, proof-kernel
formalization, complete multiplication theorem or new kappa. Independent
human and formal proof-kernel review are unclaimed.

This contribution was produced by Nick Petalas. Apache-2.0.
