# A sharp pentagonal obstruction to the common S4 cut certificate

Prepared for Arham Tahir with substantial OpenAI Codex assistance. Apache-2.0.
This is a written proof with exact finite corroboration, not formal-kernel or
independent human verification.

## Statement and model

Retain the formal `F2[S4]` register model of Nick Petalas's PR2583 and the
permutation-cut handoff of Ross Richardson in Discussion2570. Permutations
are written in one-line notation; `ab` means `a after b`. Adjacent labels
`s1=2134`, `s2=1324`, `s3=1243` have prices `(beta,alpha,beta)`, where
`0 <= alpha <= beta`. All scalar roles start arbitrary, every spectator
is restored, and the endpoint is literally diagonal over the full group
algebra. Paid gates are `I+([s]+1)N`, for binary rank-one idempotents N;
scalar `GL_R(F2)` mixing is free.

For a finite permutation S4-set Omega and a coordinate subset H, repeat the
H/complement splitting uniformly over roles. The inherited crossing-rank
potential has paid/diagonal profile

    c_g(H) = #{x in H : gx not in H}.

A nonnegative sum of these potentials is **admissible** if its generator
charges are at most `(beta,alpha,beta)`. Different finite permutation
modules and different subsets may occur in the same sum. The inherited
block-rank inequality makes its diagonal profile f subadditive and bounds
the circuit invoice below by `sum f(target)`. Finite sums and their
convergent limits are covered.

**Theorem.** On the four-target tuple

    T = (2143, 3142, 4231, 2143),

the largest lower bound from this entire coordinate-cut class is exactly

    8 beta + 4 alpha.

The sum of separate scalar shortest-word costs is `9 beta + 3 alpha`.
Consequently, whenever `beta>alpha`, no common admissible coordinate-cut
combination is tight on all 24 S4 targets. At `(2,1,2)` the sharp method
bound is 20 and the direct construction costs 21.

This theorem does not assert that the optimal circuit costs 20 or 21. It
does not exclude arbitrary subspace cuts, other representations, or other
invariants. It supplies no native supplier or new kappa.

## 1. Every such profile satisfies the pentagonal inequality

For every g, the bijection action gives

    c_g(H) = |H symmetric_difference gH|/2 = c_(g^-1)(H).

For any five group elements z_i define

    d_f(z_i,z_j) = f(z_i z_j^-1).

For one coordinate subset this is half the symmetric difference between
`z_i^-1 H` and `z_j^-1 H`. It is therefore a nonnegative sum of binary
coordinate cut distances on the five points. This applies to every finite
permutation action directly; no faithfulness or regular-action reduction is
needed. It concerns generator and diagonal profiles, not intermediate ranks.

Partition five points into three x points and two y points. Every binary
coordinate pattern satisfies

    sum_(i<j<=3) d(x_i,x_j) + d(y_1,y_2)
      <= sum_(i<=3,j<=2) d(x_i,y_j).                 (1)

Indeed, give x points sign +1 and y points sign -1. If s is the signed sum
of the five membership bits, the left side minus the right side is
`s(1-s) <= 0`, since s is an integer. Sum over coordinates, divide by two,
and sum nonnegative potential coefficients. Thus (1) holds for every f in
the stated class. Passing to a convergent limit preserves it.

## 2. The five points and the upper certificate

Choose, in order,

    x_1=1234, x_2=2143, x_3=2413,
    y_1=1243, y_2=2134.

The four positive pair differences `z_i z_j^-1` in (1) are precisely
`2143,3142,4231,2143`. The six negative differences are two copies each
of s1 and s3, plus `2431` and `4213`. Thus

    2f(2143)+f(3142)+f(4231)
      <= 2f(s1)+2f(s3)+f(2431)+f(4213).             (2)

Both 2431 and 4213 have words with two exterior and two interior calls.
Subadditivity and admissibility give

    f(2431), f(4213) <= 2 beta + 2 alpha.

Equation (2) proves the upper certificate `8 beta + 4 alpha`. Notice that
the potential may be selected specifically for T; even this does not evade
the bound. No complete enumeration of regular subsets is necessary.

## 3. An attaining potential, and the direct bill

Use PR1989's ordered-pair cut giving `inv(g)`, and the two natural prefix
cuts `c_1(g),c_3(g)`, where `c_p(g)=#{i<=p:g(i)>p}`. The potential

    f_0(g) = alpha inv(g) + (beta-alpha)(c_1(g)+c_3(g))

is a nonnegative coordinate-cut combination, charging exactly
`(beta,alpha,beta)` on the generators. Its values are:

| target | multiplicity | inv | c1+c3 | scalar direct cost |
| --- | ---: | ---: | ---: | --- |
| 2143 | 2 | 2 | 2 | 2 beta |
| 3142 | 1 | 3 | 2 | 2 beta + alpha |
| 4231 | 1 | 5 | 2 | 3 beta + 2 alpha |

Consequently `sum_T f_0 = 8 beta + 4 alpha`, proving sharpness. The upper
method certificate and the attaining potential are separate arguments.

For completeness, each scalar direct cost in the last column is optimal.
Every adjacent word has at least inv(g) letters. For the first two targets
the two natural cuts force at least two exterior letters, and words attain
both counts. For t=4231=(14), at least three exterior letters are needed:
label 1 must leave the first position through s1 before entering the last
through s3; label 4 must leave the last through s3 before entering the
first through s1. If there were just one occurrence of each exterior
generator these precedence requirements would contradict each other.
Both are necessary, so there are at least three exterior occurrences.
The chronological word `(s1,s2,s3,s2,s1)` attains five total and three
exterior letters. The lower bill is
`alpha*(total)+(beta-alpha)*(exterior)`, with nonnegative coefficients.
This proves the scalar column uniformly, including zero alpha.

The separate scalar total is `9 beta + 3 alpha`. The shortfall of every
admissible common cut on T is at least `beta-alpha`, sharply. Equivalently,
if `delta(g)=scalar_distance(g)-f(g)`, then

    2 delta(2143)+delta(3142)+delta(4231) >= beta-alpha.

Each deficit is nonnegative by subadditivity and the direct scalar word.

## 4. Evidence, boundary, and credit

The executable primary checker supplies exact shortest-path duals and
simultaneous words for all 24 scalar targets, the two five-point distance
matrices, all 32 binary cut patterns, literal formal words on six dirty
roles, and rejecting single-call omissions. A separately implemented
Floyd-Warshall oracle uses right adjacent swaps and enumerates all 1,093
words of length through six. These finite checks corroborate the written
argument; they are not a new full register-word census.

At beta=alpha the obstruction disappears and the ordered-pair potential
is tight on every target, as already proved by PR1989. A negative potential
coefficient is outside the method. A non-coordinate subspace splitting need
not induce a binary-cut metric, so this proof says nothing about that larger
class. The actual mixed-tuple circuit optimum with arbitrary dirty roles
remains open.

The model and cut-rank method are credited to Adam Gall/PR1941 and Ross
Richardson/PR1966/1989. Nick Petalas/PR2583 supplied the two-role weighted
census. Ross Richardson's archived `s4-permutation-cut-cone`, preserved at
`ebba00f3f66375402c2527ef97cd09a39a1c94ba`, supplied the twenty-target theorem
and the explicit common-certificate successor question. Its proof, README
and license are retained verbatim under predecessor/. David Arias/PR2738
and the complementary one-premium PR2577 remain credited. The elementary
pentagonal inequality is a standard cut-metric fact; no novelty of that
inequality or of the inherited cuts is claimed. New here are this S4
obstruction, the explicit mixed tuple, and its sharp full-cone invoice.
Jerry Chen's retained `abelian-cayley-metric-scope` note applies the same
standard five-point inequality to different abelian/shear metrics; no code
from that note is imported here.
