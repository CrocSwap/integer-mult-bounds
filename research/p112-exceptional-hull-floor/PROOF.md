# Exceptional-hull cross forms keep the P112 two-call floor

## Statement and inherited model

Use the arbitrary directed cross-form model of Sagar Thakrar's PR2294,
with the support theorem and incidence count stated in commdata2338's
[PR2395 proof](../p112-cross-form-rank-tradeoff/PROOF.md). These results are
premises, not new results of this package.

The reader and source label spaces are both F2^9, with the ordinary dot
product as the within-call pairing. Every nonzero P112 root-code coefficient
vector has label span F2^9 or one of eight coordinate-support hyperplanes.
Write the reader hyperplanes as U_a = r_a^perp and the source hyperplanes
as V_b = s_b^perp. Their pairings have rank eight. Equivalently,

    r_a dot s_b = 1 for every a,b in {0,...,7}.                 (1)

Let S = span_F2{s_0,...,s_7}. Take any nonzero binary vector v, any
i in {0,...,7}, and independent directed cross forms

    beta01 = r_i v^T,
    beta10 = C, with every row of C in S.                      (2)

**Theorem.** Every exact two-call root-code factorization in this model
has total union COPY-rank price at least 128. The minimum is exactly 128.
There is no restriction on the number of terms or their complex scalars.
The reverse form C may have rank greater than one.

## New transfer step

Take any double term, meaning that both reader blocks and both source
blocks are nonzero. Restrict its four support spans to coordinate
hyperplanes U_a,V_b,U_c,V_d. This is possible by the inherited support
theorem. Restricting a matrix cannot increase its rank.

The within-call pairing on U_a x V_b is nonsingular. The vector in V_b
representing the functional x -> x dot r_i on U_a is

    z = r_i + (r_i dot s_b) r_a = r_i + r_a.                   (3)

Indeed, z dot s_b = 1+1 = 0, so z is in V_b. Also x dot z = x dot r_i
for x in U_a. Nonsingularity gives uniqueness.

Every exceptional source normal kills z, since

    s_j dot z = s_j dot r_i + s_j dot r_a = 1+1 = 0.           (4)

By linearity, every vector of S kills z. The row-space hypothesis on C
therefore implies C z = 0.

Write the restricted double pairing in block form as [A B; E D], with
A and D nonsingular eight-by-eight matrices. For a source vector y in
V_d, the vector representing B's functional on U_a is z (v dot y).
Equation (4) gives E A^-1 B = 0. Block elimination now gives

    rank_F2 [A B; E D] = 8 + rank_F2(D - E A^-1 B) = 16.       (5)

Thus every double term has price at least 16. This is the new step.
In particular, it applies when C is a sum of independent exceptional
source functionals, rather than one rank-one cross form.

## From term prices to the sharp floor

The inherited coefficient identity is sum_j a_j c_j^T = I_16 over C,
with ordinary transpose. Discard terms having a zero entire factor.
Call a term pure if it has a reader in one call and a source only in the
other. Let n count all non-pure terms and d count the double terms.

Each diagonal identity block has complex rank eight and therefore needs
at least eight diagonal-contributing terms. A double contributes to both
blocks; every other non-pure term contributes to exactly one. Hence

    n + d >= 16.                                              (6)

Every non-pure term has price at least eight from its within-call block.
Equation (5) raises the double-term charge to sixteen. Pure prices are
nonnegative, so the complete separate-total COPY price is at least

    8(n-d) + 16d = 8(n+d) >= 128.                             (7)

The sixteen separate coordinate terms give I_16 and cost 16*8 = 128,
independently of the cross forms. This proves attainment.

## An explicit case outside the prior sufficient test

Use the actual retained geometry. Its annihilators, as nine-bit integers,
are

    r = [129,65,209,17,197,5,149,85],
    s = [33,289,297,41,267,11,3,259].

Let e = 1, the first binary coordinate vector, and set

    beta01 = r_0 e^T,
    beta10 = r_1 s_0^T + e s_1^T.

Their row arrays are respectively

    [1,0,0,0,0,0,0,1,0],
    [256,0,0,0,0,0,33,0,0].

The global ranks are (1,2), while both minimum coordinate-support cross
ranks are zero. The forward restriction vanishes on U_0. The reverse
restriction vanishes on U_1 x V_1. Its two left vectors and two right
vectors are independent, so its global rank is two. PR2395's sufficient
test c01+c10 >= min(8,r01,r10) reads 0 >= 1 and abstains here. The theorem
above proves the exact minimum 128 for this example and its whole family.

This does not settle the entire rank-(1,2) class. It excludes this
exceptional-hull way of exploiting the zero pure prices.

## Evidence boundary and credit

The arbitrary-complex-factorization theorem is a written scoped proof.
The verifier derives the eight normals from the pinned geometry, checks
8,192 transfer instances and all 6,561 choices of the fixture's four
support spans, including full spans. It checks the fixture's ranks and
zero minima, the coordinate attainer, and two actual price-15 doubles
after removing the respective geometric hypotheses. It does not rerun
the inherited complete support census or enumerate complex decoders.

JoyboyBrian's adjacent PR5141, head
`b75399c455aa24f21ec9c78c337c3c277efd177d`, proves the full rank-(1,1)
floor. Its mixed-orientation argument covers a rank-one reverse form
with one exceptional source functional. Equations (3)-(5) extend that
argument to a reverse row space in their linear span, giving new
higher-rank cases. No PR5141 code or theorem is a runtime dependency.

The inherited model and support/count lemmas retain Sagar Thakrar,
commdata2338, alephnan, Mihir Srivastava and Adam Gall's credit. The new
exceptional-hull extension and package were produced by Nick Petalas.
Apache-2.0. Independent human and formal proof-kernel review are unclaimed.
