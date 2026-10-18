# Arbitrary-term cost 20 on eighteen physical C5 cores

This proof extends thakrarsagar's weighted-rank and equality-trace method in
[PR3256 at 1ea98246dabb46fc7bedf6127eff63f008414a39](https://github.com/CrocSwap/integer-mult-bounds/tree/1ea98246dabb46fc7bedf6127eff63f008414a39/research/c5-asymmetric-cost-floor).
The new premises are the actual rectangular tariffs of seventeen additional
physical cores and a valid orientation for each. The complete proof is given
here, so replay needs no pending-PR executable or Git object.

## Object and theorem

PR2782's pinned 112 scalar ports are partitioned into 56 two-port planes.
Their binary labels lie in F2^9. Every plane's binary Gram matrix is I2.
The orthogonality graph has exactly 23 induced five-cycles. A row in
RESULT.json `covered` lists an actual cycle and a cyclic `order` E0,...,E4.
Adjacent planes are orthogonal and every other pair is nonorthogonal.

Each plane has two scalar coordinates. A strict fitting matrix K over Q, R
or C has diagonal one, off-diagonal entries within each plane zero, and
all cross entries between nonorthogonal planes zero. Cross entries between
adjacent planes are free. Consider any finite decomposition

    K = sum_t u_t v_t^T.

Transpose is ordinary transpose, including over C. Scalar coefficients can
be absorbed into u_t. Discard zero factors. A_t and B_t are the subsets of
planes touched by u_t and v_t. The cost of a term is

    c(A_t,B_t) = rank_F2 [x dot y : x in complete planes A_t,
                                   y in complete planes B_t].

Touching either port charges both plane labels. Costs do not depend on
coefficient magnitudes, signs or denominators. Asymmetric factors, zero-cost
nonzero terms and arbitrary finite term counts are allowed.

**Theorem.** For every one of the eighteen physical cores in RESULT.json
`covered`, total cost is at least 20. Five explicit terms attain 20 on each.
Seventeen of these cores extend PR3256's single-core result. This theorem
makes no assertion about the five cores in `unresolved`.

## Rank counts and a checked weighted cover

Let Q={(0,2),(0,3),(1,3),(1,4)}. These four pairs, and the missing pair
(2,4), are nonorthogonal pairs of planes. Each pair's four scalar coordinates
form a forced I4 principal block. The singleton planes 2 and 4 give I2 blocks.
For a block H, let b_H(A,B)=1 if A and B both meet H, and zero otherwise.
For a decomposition let n_H=sum_t b_H(A_t,B_t). Its restriction to H is a
sum of n_H rank-one matrices equal to I_r, so n_H>=r.

For each accepted physical orientation, replay checks all 32*32 ordered
support pairs and establishes

    d(A,B) = 2c(A,B) - 2 sum_(H in Q) b_H(A,B) - b_2(A,B) - b_4(A,B) >= 0.

This is a premise about actual complete-plane binary pairing matrices.
An abstract graph isomorphism does not establish it. The receipt retains
an ordered tariff-table hash for every accepted orientation.

Write x_H=n_H-4, y_i=n_i-2 for i=2,4, and D=sum_t d(A_t,B_t). All are
nonnegative integers. If C is total cost, then

    2C-36 = 2 sum_(H in Q) x_H + y_2 + y_4 + D.

Thus C>=18. At C=18 all excesses and D vanish. At C=19 their weighted sum is
two. There are exactly ten cases. Either one of the four x_H equals one and
all other excesses and D are zero, or all x_H vanish and (y_2,y_4) is one of
(0,0),(1,0),(0,1),(2,0),(0,2),(1,1), with D=2-y_2-y_4.

## Necessary trace equations

If exactly r rank-one matrices sum to I_r, write their factors as square
matrices U,V. Then UV^T=I_r implies V^TU=I_r. Each summand consequently has
trace one. This uses neither positivity nor complex conjugation.

For each term put z_i=u_(t,i)^T v_(t,i) on the two coordinates of plane i.
If i is absent from A_t or B_t, then z_i=0. Whenever one of the six selected
blocks has n_H equal to its rank, the same term necessarily satisfies

    sum_(i in H) z_i = b_H(A_t,B_t).

A block with excess imposes no individual trace equation. These equations
have integer coefficients. Consistency over Q is equivalent to consistency
over R or C. The primary checker solves the four-pair path by affine
propagation with singleton anchors. The separate checker uses Fraction
Gaussian elimination, including the zeros outside A_t intersect B_t.

These are only necessary conditions. A consistent trace system need not
come from a fitting scalar factorization.

## Exact exhaustion without a term bound

For each of the eleven cases, retain all trace-consistent support pairs.
Each contributes an eight-coordinate increment consisting of the four Q
hits, the two singleton hits, d, and the missing-pair hit. Bound the first
seven totals by that case's exact target and cap the last total at four.
The missing I4 block requires at least four hits.

The checks establish that every zero-cost support pair has zero in all eight
increment coordinates. Such terms can be removed from this count image,
regardless of their number or scalar coefficients. Every positive-cost
support pair advances at least one of the first seven coordinates.

Start at zero and repeatedly add any permitted increment, including reuse
of an identical increment. This contains the count image of every finite
fitting decomposition at that cost. The domain has at most
5*product_(i=0..6)(target_i+1) states. The primary queue exhausts this finite
domain with an explicit bound. The separate checker groups states by exact
integer cost, so every transition goes to a strictly later cost layer.

For every covered core, none of the eleven target states with missing-pair
count four is reachable. The receipt records 198 individual cases and
54,014 visited states in total. Thus neither C=18 nor C=19 is possible.
Because costs are integers, C>=20. This is an exact necessary-condition
certificate, not a failed coefficient search.

## Exact attainment

For cyclic i=0,...,4, take the scalar vector

    w_i = e_(i,1) + e_(i+1 mod 5,0).

Use the five terms w_i w_i^T. They partition all ten scalar coordinates.
Their only off-diagonal entries join adjacent, orthogonal planes, where
entries are free. The full matrix therefore fits every constrained entry.
Each term touches two orthogonal nondegenerate complete planes and costs
four. Their total cost is exactly 20. The primary checker verifies all 100
matrix entries and the actual binary pairing rank of every term on every
accepted orientation.

## Residuals and scope

The following five physical cycles do not pass the fixed weighted-cover
and trace certificate in any of the ten cyclic orientations tested here:

    (3,10,4,6,13)
    (3,10,12,23,13)
    (6,13,23,54,26)
    (10,12,23,35,16)
    (14,24,47,18,55)

Their failure is not a cost-19 decoder and is not evidence that the floor is
false. They remain open for arbitrary-term asymmetric factors. The all-cycle
signed-Gram and five-term results are separate predecessor statements.
No local floors are added across overlapping cores. Native programs, dirty
restoration, hosting, precision, all-size implementation, supplier admission
and the selected exponent are outside this theorem. The scalar argument is
written mathematics with exact finite premises, not a proof-kernel theorem.
