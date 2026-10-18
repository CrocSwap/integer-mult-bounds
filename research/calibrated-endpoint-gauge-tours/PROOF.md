# Calibrated endpoint gauges reduce to source tours

Written scoped theorem, Richard Hoekstra, 2026-10-13. Substantial OpenAI Codex assistance.

## Model and statement

Let h >= 6 be even, c = h-2 and k = h/2. Partition the h indices into two
halves of size k. There are h independent sources x_j and h(k-1) independent
dirty targets y_(i,j), one for each ordered distinct pair in the same half.
The required full map restores the sources and performs

    y_(i,j) += (C_([h] minus {i,j}) - I) x_j.

In binary character coordinates, let n_i = 1+e_i in F2^h and let P_S be the
orthogonal projector onto their span for i in S. The normals are an orthonormal
basis because h is even. Put C_S(chi) = i^wt(P_S chi). Since each n_i has weight
h-1 and every pair overlaps in h-2 even positions,

    wt(P_S chi) = (h-1) sum_(i in S) <n_i,chi>  (mod 4).

Thus C_S is a product of independent order-four coordinate phases. Their
monomial group is (Z/4Z)^h: evaluating a monomial on the character dual to each
n_i separately identifies its exponent. This explicit fact is used below;
no general assertion about metrics of abelian groups is needed.

A circuit may apply any number of oriented phases C_S or C_S^-1, with
1 <= |S| <= c, on any single source or target. Every endpoint gauge path must
close. Sources never mix. Targets do not feed any other role. Each target has
exactly two scalar reads from its declared source, with signs -1 and +1.
Each read is individually calibrated in the *final* target coordinates:
its contribution is respectively -I or +C_([h] minus {i,j}). Timing and
interleaving of phases and reads are arbitrary. No helpers or additional
readouts are admitted. Cost is the sum of |S|^p over all phase calls, including
inverses, for any fixed 0 <= p <= 1. Scalar ADDs are separately counted.

**Theorem.** In this family the exact minimum phase moment is

    M_oriented(p) = 2h(h-2)^p + h(h-4).

If all binary translations X_v are additionally permitted and receive zero
*phase-moment* charge, while their literal calls remain separately counted,
the exact minimum is

    M_translation(p) = 2h(h-2)^p + h(h-4) 2^(p-1).

These are claims about the stated circuit family, not all circuits for the
completed linear map and not an integer-multiplication exponent bound.

## Eliminate each target gauge

Fix p and use the shortest inverse-symmetric word cost d on the permitted
monomial group (or its quotient by zero-cost translations). Suppose the
source and target gauges immediately before a positive read are P and Q.
Because the target's total gauge is restored, its final contribution is
Q^-1 P x_j. Calibration sets this to its required corner monomial.

Remove all target phases. At that positive read, insert the source excursion
Q^-1, read into the now unphased target, then insert Q. The final contribution
is unchanged and the source returns to its previous gauge P. The target
prefix and remaining suffix each have cost at least d(Q), so the excursion
cost 2d(Q) is no greater than that target's entire phase bill. This applies
independently to every target, even when their paths overlap in time. All
monomial gauges commute; no gate-order assumption beyond the stated family
is used.

The calibrated negative contribution is -x_j. It may move to the entrance:
the target has no consumers and all its gauge factors have been removed.
The arbitrary old target column remains the identity. No extra role or ADD
is introduced. We have obtained a source-only word of no greater moment.
The cheapest excursion is allowed to depend on p; the written argument
covers all p, whereas the executable normalizer specifically certifies p=1.

## Exact oriented tour cost

For one source there are m = k-1 distinct corners, all supported on c axes.
Identity to a corner costs exactly c^p. Any path must touch those c axes, so
its total charged rank is at least c; subadditivity gives
sum r_l^p >= (sum r_l)^p >= c^p. One rank-c phase attains the bound.

Two distinct corners for this source differ by exponent +1 on one axis and
-1 on another. One permitted oriented phase cannot realize that mixed sign.
At least two nonempty calls are necessary, each of cost at least one. Two
rank-one phases attain distance 2 for every p in [0,1].

A closed source path visits all m corners. Keep the order of their first
visits and shortcut the intervening paths in the word metric. Its first and
last segments cost at least c^p, and its m-1 between-corner segments cost at
least 2. Any ordering of the corners attains these distances with the stated
calls. Summing over h sources yields

    h [2c^p + 2(m-1)] = 2h(h-2)^p + h(h-4).

The two required reads per port give exactly h(h-2) scalar ADDs.

## Translation closure and its invoice

Since C_{i}^2 is X_{n_i}, the phase group modulo binary translations is
(Z/2Z)^h. For any supports A,B,

    C_A^-1 C_B = X_(sum_(i in A minus B) n_i) C_(A symmetric-difference B).

This elementary identity and the inherited rank-priced residual interface
are not claimed as a new supplier mechanism. In the quotient, a phase path
to a corner must still touch its c odd coordinates, so its minimum cost is
c^p. Between two corners the odd support has size two; subadditivity gives
a lower bound 2^p. One rank-two phase with one literal translation attains it.
The same closed-tour argument gives the second displayed minimum.

An attaining word has 2h rank-c calls, h(h-4)/2 rank-two calls, the same number
of separately counted translations, and h(h-2) scalar ADDs. Its rank mass is
h(3h-8), equal to the oriented word. At h=10 it has 50 phase calls and 30
translations, versus 80 oriented phase calls. It is not a 30-operation saving
in total calls and is not compared with the live multiplication supplier.
Both attaining words have characterwise Gaussian row L1 at most three,
including every arbitrary old source and target column.

## Boundary

Cross-source mixing, target-to-target or target-to-source ADDs, extra reads,
operator-valued gates on several roles, streamed target consumption and changed
output contracts are excluded. A circuit computing the same completed map
without the two individual calibrations is also excluded. Phase-moment cost
is only one invoice: translation/tape implementation, allocation, recursion,
precision and analytic transfer are not discharged. No complete multiplication
algorithm, new kappa or formal proof-assistant result follows from this theorem.
