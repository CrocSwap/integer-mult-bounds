# Five terms still have residue rank at most two

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement and credited premises

Let m >= 4, V = M_m(F2), and let U_j(z) = L_j z R_j for
L_j,R_j in GL_m(F2), j = 1,...,5. Suppose a_j in V has matrix rank
at most one and

    sum_j a_j = 0,
    sum_j a_j * (U_j z) = 0 in Sym^2(V), for every z in V.           (1)

The multiplication in (1) is ordinary polynomial multiplication of linear
forms. Squares are retained. Define beta = sum_j U_j^-1(a_j).

**Theorem.** rank(beta) <= 2. For every m >= 4 there is a solution with
five nonzero rank-one a_j and rank(beta) = 2.

The model and necessary conditions are JoyboyBrian's #5490, Sections 1-3
of `research/bit-three-term-twist-rigidity/PROOF.md`. We cite its
transport-distance lemma: distinct U and U' have rank(U+U') >= m as
linear maps on V. We also cite Nick Petalas's #5978, Theorem parts 2-3
in `research/bit-four-term-twist-escape/PROOF.md`: for four contributions
at m >= 3, a nonzero residue requires all four frames equal to x and
sum U_j = 0; its rank is at most 2 rank(x), and rank two is attained by
rank-one x at every m >= 3. These are premises, not new verification
claims. SOURCES.json pins the exact proof bytes on canonical main.

The new step is the complete reduction from five contributions to that
four-contribution theorem. It answers the m >= 4 rank-one part of
Open next question 2 in #5978. It does not answer its proposed m = 2 census
or the exceptional five-term m = 3 case.

## Linear-syzygy fact

Use the same linear-syzygy fact as #5978. If independent linear forms
b_1,...,b_d and linear forms f_1,...,f_d satisfy sum b_i f_i = 0,
then f_i lies in span{b_h : h != i}. To see the needed implication,
extend the b_i to a coordinate basis of the polynomial ring. The
coefficient of b_i^2 makes the b_i coefficient of f_i zero. The
coefficient of b_i c for each complementary coordinate c makes that
coefficient of f_i zero. Terms b_i b_h allow only the other b_h.
This explains why discarding squares would change the argument.

Consequently, if sum b_i (F_i z) = 0 for all z, then the linear map
F_i has image dimension at most d-1. All ranks in this paragraph are
vector-space ranks on V, rather than the matrix rank of a frame.

## Reduction by frame-span dimension

If one a_j is zero, delete that term. At most four terms remain and the
credited four-term theorem applies after adding zero terms if necessary.
Its nonzero-residue case has four equal rank-one frames, so rank(beta)
is at most two. Hence assume all five a_j are nonzero.

Put d = dim span{a_1,...,a_5}. Their zero sum gives d <= 4.
Dimension one is impossible: over F2 five equal nonzero vectors sum to
that same nonzero vector. The remaining cases are as follows.

**d = 4.** After reordering, the frames are independent x_1,...,x_4
and x_1+...+x_4. Substitution into (1) gives

    sum_(i=1)^4 x_i * ((U_i+U_5) z) = 0.

Each U_i+U_5 has image dimension at most three by the syzygy fact.
Since 3 < m, the credited distance lemma forces U_i = U_5 for every
i. Thus beta = U_5^-1(sum a_j) = 0.

**d = 3.** The frames, after reordering, are x,y,x+y,z,z with x,y,z
independent. Here is the full multiplicity argument. The set of values
occurring an odd number of times has odd size at most five and sums to
zero. Size one is impossible. Size five is impossible in F2^3: all
seven nonzero vectors sum to zero, so its two-element complement would
also sum to zero, despite having distinct elements. Thus there are
three odd-multiplicity values x,y,x+y. The other two entries are an
equal pair z,z. If z lay in span{x,y}, d would be at most two.

Equation (1) becomes

    x*((U_1+U_3)z') + y*((U_2+U_3)z') + z*((U_4+U_5)z') = 0

for every argument z' in V. Each displayed difference has image
dimension at most two, less than m. Therefore U_1=U_2=U_3 and
U_4=U_5. The triple and the pair cancel separately in beta, giving zero.

**d = 2.** The three possible nonzero frame values are x,y,x+y. Their
multiplicities all have the same parity because their sum is zero.
Their total is five, so each multiplicity is odd; the only possibility
is 3,1,1. Reorder the frames as x,x,x,y,x+y. Equation (1) reads

    x*((U_1+U_2+U_3+U_5)z) + y*((U_4+U_5)z) = 0.

The second map has image dimension at most one. Transport distance
forces U_4=U_5. The equation then forces U_1+U_2+U_3+U_5=0, since
multiplication by the nonzero linear form x is injective. Moreover

    beta = (U_1^-1+U_2^-1+U_3^-1+U_5^-1)(x).

These are exactly four equal-frame contributions satisfying (1).
The cited four-term theorem gives rank(beta) <= 2 rank(x) <= 2.
This proves the bound in all cases.

## Attainment with five nonzero rank-one frames

Take a credited four-term rank-two witness at this m, with all four
frames x = u v^T and invertible transports U_1,...,U_4 summing to zero.
Choose w independent of u and replace the first contribution by

    (w v^T, U_1), ((u+w) v^T, U_1).

Both new frames have rank one, are nonzero, and sum to x. This
replacement preserves each equation in (1) and the residue exactly.
There are now five nonzero frames and residue rank two. No new
four-term construction is claimed.

For direct finite corroboration, identify F2^m with F_(2^m) and write
M_c for multiplication by c. The checked new five-term witness has

    frames = (e_1 e_0^T, (e_0+e_1)e_0^T, x, x, x), x=e_0 e_0^T,
    left multipliers  = (1, 1, b, 1+b, 1+b),
    right multipliers = (1+b, 1+b, 1+b, 1, b),
    U_j(z) = M_left[j] z M_right[j], b = t.

The finite verifier checks all input basis matrices in (1), inverse
transport, all five frame ranks and the actual rank of beta at
m=4,5,6,7,8. The moduli are t^4+t+1, t^5+t^2+1, t^6+t+1,
t^7+t+1 and t^8+t^4+t^3+t+1. It checks a multiplicative inverse for
every nonzero element of each finite field. These new five-frame checks
do not replay the predecessor's census or its four-frame verifier.

## Scope and next step

This is a necessary-condition obstruction in one off-diagonal block.
A five-contribution block with rank-one frames cannot alone supply a
full-rank residue when m >= 4. Other blocks, direct diagonal contributions,
the second-order constant-input cross terms and complete words may alter
a caller's total target. No arbitrary-word lower bound follows.

The threshold m >= 4 is used at d=4, where the rank-three image bound
need not identify the transports if m=3. This case is left open. Native
twist costs, physical realization, recursive invoices, the five selected
framework assumptions and a complete multiplication theorem are unrun.
