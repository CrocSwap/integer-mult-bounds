# Signed whole-idle completion of an overlapping stage demand

This scoped proof about a determinant relaxation was produced by Nick Petalas.
It is not a construction of the proposed caller.

## Formal contract

Work over K = Q(q,A,B,C), with algebraically independent stage variables
A,B,C. There are six arbitrary independent main fields. Helpers are autonomous
outputs outside these six fields and cannot be mixed into them. Use each of
three full calls exactly once. The A call is A times a determinant one query
on a two-dimensional subspace, and identity on its complement. Define the B
and C calls likewise. Query orientations and chronology are unrestricted.

Any number of invertible maps over Q(q) are free in this relaxation, including
constant field mixing and determinant one thin queries. Their physical costs
are not declared zero. A paid whole-idle atom chooses a nonempty subset S of
{A,B,C}, a sign epsilon in {-1,+1}, and one field line. It multiplies that line
by (product of the stages in S)^epsilon. Constant conjugation is allowed.
Each stage has eight fresh axes. An atom costs H(8|S|), including an inverse
atom. There are no other stage-dependent operations. Every word is finite.

The desired stage multiset has two ABC outputs, two AB outputs and two BC
outputs. Central query factors may remain on the first pair, with
stage-independent determinant. The target determinant has stage degrees
(4,6,4). The three full calls have degrees (2,2,2). Each atom contributes
epsilon times the indicator of S. Constant mixing cannot change these degrees.
Every exact word therefore requires the signed idle balance

    sum_atoms epsilon * 1_S = (2,4,2).                    (1)

This necessary condition does not assert that every satisfying inventory
has a legal query endpoint.

## Exact completion theorem

Let H(0)=0, with H positive on (0,24], nondecreasing and concave on [0,24]. Among all
finite signed inventories satisfying (1), the minimum cost is

    2 H(24) + 2 H(8).                                   (2)

Two positive ABC atoms and two positive B atoms attain this value in the
inventory relaxation. If H is strictly concave, this is the unique minimizing
signed subset multiset. Positions and conjugating maps are not classified.

Write a=H(8), b=H(16), c=H(24). Give the coordinates dual weights

    y_A = y_C = (c-a)/2,    y_B = a.

These are nonnegative. Each nonempty subset S satisfies y(S)<=H(8|S|).
For B this is equality. For A or C, c<=3a gives (c-a)/2<=a.
For AB or BC, midpoint concavity gives (a+c)/2<=b. For AC use c-a<=b:
the increment on [16,24] is at most the increment on [0,8], so c<=a+b.
For ABC there is equality at c.

A positive atom costs at least y(S). A negative atom costs at least -y(S),
since its cost is positive and y(S)>=0. Summing and using (1) gives
cost >= 2y_A+4y_B+2y_C = 2c+2a. The stated inventory attains this bound.
This proves (2) for arbitrary word length and arbitrary inverse calls.

Strict concavity gives c<3a, (a+c)/2<b and c<a+b. Only B and ABC are tight
positive subsets. Every negative atom has strictly positive dual slack.
Equation (1) forces exactly two of each tight subset, proving uniqueness.
Every power H(r)=r^s with 0<s<1 meets these conditions. No sampled exponent
or word-length cutoff enters this proof.

This is a three-coordinate application of the classical greedy dual for a
submodular set cost. The claimed new step is the signed caller completion
application and the following comparison.

## A strict improvement in the necessary budget

With one central axis and eight fresh axes per stage, the overlapping target
ranks are two 25 and four 17. Its optimal target-minus-idle reward is

    R_overlap = 2H(25) + 4H(17) - 2H(24) - 2H(8).

A comparator with six ABC jobs has six rank-25 targets and deficit (4,4,4).
Its exact signed idle minimum is 4H(24). Uniform dual weights H(24)/3
certify this, since k H(24)/3<=H(8k) for k=1,2,3; four ABC atoms attain it.
Thus R_uniform = 6H(25) - 4H(24). For every strictly concave H on [0,25],

    R_overlap - R_uniform
      = 4H(17) + 2H(24) - 2H(8) - 4H(25) > 0.           (3)

For an explicit proof, start with (8,8,25,25,25,25). Twice replace a pair
(8,25) by (16,17), then twice replace (16,25) by (17,24). The result is
(17,17,17,17,24,24). Every replacement preserves the sum and strictly
increases the sum of H by strict concavity. Both lists sum to 116.
For a linear tariff the rewards agree.

The comparison cancels identical full-call/helper and other charges between
two hypothetical contracts. It does not assume equal thin-query, ordinary,
storage or compiler costs. Any difference must be subtracted separately.
Neither six-field comparator is supplied as an operator word here. Equation
(3) is an improved optimistic budget, not a larger kappa or feasible supplier.

## Applicability and remaining obligations

The formal Laurent stage identity is an explicit hypothesis. A finite-order
Gaussian may satisfy additional relations. This degree condition is not an
impossibility theorem for every specialized native implementation.
Stage-dependent free maps, helper feedback, another rank/support relation,
changed native multiplicities or changed output contracts need new arguments.

An attaining inventory need not be placeable at legal chronological cuts.
The exact query coefficients, independent output map, native frames and
absolute phases, arbitrary helper preservation, owned erasure, thin-query
count, precision, stock, tape movement, compiler and outer costs remain open.
No selected-frontier or complete multiplication theorem follows.
