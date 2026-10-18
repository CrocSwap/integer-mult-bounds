# Sharp copy-cost floor for the A8 simplex frame on P120

This is a written argument using explicitly enumerated finite binary lemmas.
It is not a Lean proof or an unconditional integer-multiplication theorem.
All transposes are ordinary transposes, including over the complex numbers.

## 1. Precisely specified family

Let V be the sum-zero subspace of R^9. Take these 120 norm-two root lines:

- r = e_a - e_b, for a < b (36 lines);
- r = 1_S - (1/3)1, for |S| = 3 (84 lines).

This is the E8 root system in its A8 realization. We use the stated orientations.
Let b_k = e_k - (1/9)1, k = 0,...,8. The b_k span V and their only dependency is
sum b_k = 0. Fix T_ik = r_ik = r_i dot b_k. A decoder in our family has
D T^t = 2G, where G_ij = r_i dot r_j. Each term is charged separately by the
binary pairing rank on its row and column supports (the PR717/446 convention).
No masking of the required all-pairs identity is allowed.

Every exact D has the form D_ik = 2r_ik + t_i, with arbitrary t_i in C. Indeed,
the roots span V, so exactness says the projection onto V of row D_i is 2r_i;
the orthogonal complement is the all-ones line. Conversely that form is exact.
This is PR1224's one-sided representation mechanism in a fixed simplex frame;
we derive the special case here without depending on its general theorem.

Assign binary labels u_i in F2^9 by u_ab = 1+e_a+e_b for pair roots and u_S=1_S
for triple roots. Direct inspection gives

    u_i dot u_j = (r_i dot r_j + 1) mod 2.

The 120 labels span F2^9. The column support Y_k = {i:r_ik != 0} also spans F2^9
for each k. Both facts, all 14,400 pairing entries and the complete S9 action
are checked. Hence term cost is simply dim span{u_i:D_ik != 0}.

For each column k define its deficiency space

    K_k = {w in F2^9 : w dot u_i = 0 whenever D_ik != 0},
    delta_k = dim K_k.

Total cost is 81 - sum delta_k. We prove sum delta_k <= 9.

## 2. Necessary compatibility

If w is in K_j and z is in K_k, and w dot u_i = z dot u_i = 1, then
D_ij = D_ik = 0. The representation formula therefore forces r_ij = r_ik.
Write w ~_(j,k) z for this condition at every root line. It is necessary even
when the t_i are arbitrary complex numbers. A generic shift creates no zeros
and does not provide an escape from this condition.

For a two-dimensional binary subspace U contained in K_0, let H_k(U) be the
space of z compatible with every w in U. Equivalently it is the annihilator
of labels u_i satisfying both:

- some w in U has w dot u_i = 1;
- r_i0 != r_ik.

Thus K_k is contained in H_k(U). For a nonzero z in H_k(U), let F_k(z) be the
span of labels with z dot u_i = 1 and r_i0 != r_ik. Compatibility in the other
direction says K_0 is contained in F_k(z)^perp.

## 3. Complete finite lemmas

`verify.py` constructs all 511 nonzero functionals and all
(511*510)/6 = 43,435 binary planes. A plane has exactly one ordered encoding
(a,b) with 0<a<b<a xor b; this enumerates it once. For every such plane and
each k=1,...,8 the following statements are checked:

1. dim H_k(U) <= 1. When nonzero, denote its unique nonzero vector by z_k.
2. dim F_k(z_k) is either 1 or 7. In the rank-one case its nonzero label is
   exactly q_k = 1+e_0+e_k, the line r=e_0-e_k.
3. If all eight H_k(U) are nonzero, their unique vectors are not mutually
   compatible: some z_j is not ~_(j,k) z_k.
4. The eight q_k are independent. Hence every subset of them is independent.

The number of planes with respectively 0,...,8 nonzero H spaces is

    4365, 11552, 13356, 8792, 3710, 1176, 392, 56, 36.

Among all the nonzero partners there are 86,360 rank-one and 2,032 rank-seven
forced spaces. All 36 exceptional eight-partner cases have an explicit
incompatible pair recorded in CERTIFICATE.json. The certificate is compared
against a fresh exhaustive replay, not accepted by trusting its totals.

The second implementation, `independent.py`, starts in standard 8-dimensional
E8 coordinates and the exact A8 weight normals frozen from PR1224. It derives
binary labels from independent columns of the 120-square pairing matrix, and
computes H_k by annihilators rather than the primary compatibility table. Its
unrelated binary coordinate system produces the same aggregate finite lemmas.
This is separate AI implementation, not independent human review.

## 4. Deduction for every complex shift assignment

If every delta_k <= 1, their sum is already at most nine. Otherwise permute
coordinates so delta_0 >= 2 and choose a binary plane U in K_0. The S9 action
preserves the root lines, labels and the decoder family; sign changes of chosen
root representatives preserve supports and the compatibility condition.

By lemma 1 every other nonzero deficiency has dimension exactly one. Let J be
the set of those columns. Lemma 3 gives |J| <= 7: if all eight were present,
the actual K_j would violate the necessary compatibility from section 2.

If some j in J has dim F_j = 7, then K_0 is orthogonal to F_j and delta_0 <= 2.
Therefore delta_0 + |J| <= 2+7 = 9.

Otherwise every j in J has F_j = span(q_j). These |J| constraints are independent
by lemma 4, so delta_0 <= 9-|J|, again giving delta_0+|J| <= 9. This includes
J empty. Consequently every decoder in the specified family costs at least 72.

## 5. Sharp attainment with all nine terms active

Start with t_i = -2r_i0 for every row. Column 0 vanishes; the other eight
columns have rank nine and total cost 72. For the single line r=e_0-e_1 change
its shift to t_i=-2r_i1 instead. Its column-0 entry becomes nonzero and its
column-1 entry becomes zero. All-pairs exactness is preserved because the row
change is a multiple of the all-ones vector. The nine term ranks are

    (1,8,9,9,9,9,9,9,9), with sum 72.

The checker verifies all 14,400 identity entries exactly using denominator
clearing, and derives the ranks from the supports. No zero-term loophole is
needed for sharpness.

## 6. Scope and price

The optimal copy ratio in this family is 72/120 = 3/5, greater than the
standard P112 ratio 64/112 = 4/7. Thus this fixed unpunctured A8 family cannot
supply the contemplated improvement in copied-information ratio even before
paying its physical realization costs. This is a copy-cost statement, not a
complete paid recurrence or a claim about every construction using these ports.

No P112 puncture theorem follows: puncturing can reduce the column spans and
change every finite lemma. Other nine-normal frames, two unrestricted factors,
masked identities, shared-copy billing and physical decoder realizations are
outside this result. The PR1094 selected supplier, source manifest and all-size,
compiler, mutable-source, hosting, precision/tape, recovery, analytic-transfer
and bit-interface obligations remain unchanged. No new kappa is claimed.
