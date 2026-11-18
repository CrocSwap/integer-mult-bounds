# Sharp radial budget for each finite Gaussian iterate identity

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
This is an author-checked local precision theorem. No new kappa follows.

## 1. Statement

For Gaussian integers x,y, put `s=x+y`, `d=x-y`, and
`C_+(x,y)=((s+i*d)/2,(s-i*d)/2)`. Use the Euclidean norm of the pair.
For a positive integer m, consider total maps F on Gaussian pairs with
exact sum, error at most one from C_+, and `F^m=id`. Define

```text
Delta(F) = sup_z max(0, ||F(z)||-||z||).
```

Such a map exists exactly when 4 divides m. In that case let R be the
least odd integer at least five that does not divide m. The exact minimum is

```text
beta_R = sqrt((R^2+2R+3)/2) - sqrt((R^2+1)/2).         (1)
```

The construction below attains this value on a full four-cycle. It has
an explicit inverse and global Gaussian-unit covariance. Its forward,
inverse outward and absolute radial suprema all equal beta_R. The lower
bound assumes none of these additional symmetry properties.

The requirement is the iterate identity `F^m=id`. The theorem does not
require m to be the least positive global period. The constructed map's
least period divides m and can be smaller. An exact-least-period constraint
is a different optimization problem.

Examples of (m,R,beta_R) are

```text
(4,     5,  sqrt(19)-sqrt(13)),
(20,    7,  sqrt(33)-5),
(140,   9,  sqrt(51)-sqrt(41)),
(1260, 11,  sqrt(73)-sqrt(61)),
(13860,13,  sqrt(99)-sqrt(85)).
```

The m=4 value and its annular construction are prior results of
[CubeJerry's PR #7570](https://github.com/CrocSwap/integer-mult-bounds/pull/7570),
[pinned proof](https://github.com/CubeJerry/integer-mult-bounds/blob/053c42c68165cf24fd4e8bc33c2b20d6ac3d399b/research/sharp-order-four-gaussian-rounding/proof/PROOF.md),
and the fourth-power-only lower bound in
[PR #7699](https://github.com/CrocSwap/integer-mult-bounds/pull/7699),
[pinned proof](https://github.com/aliromman/integer-mult-bounds/blob/2a5dcb314ccdfeed24bd86ec1f56f519eead56c1/research/gaussian-radial-order-classification/PROOF.md).
The present result supplies the optimum for every prescribed finite
iterate, using the first incompatible ring and a new global assembly.

## 2. Half-grid reduction and lower bound

Use real two-vectors, with `J(a,b)=(-b,a)`, `B(a,b)=(a+b,a-b)`,
`T=B/2`, and `Q=-J`. The output difference f(d) must have the same
component parities as s. The pair error squared is
`|f(d)-Jd|^2/2`. When the component parities of s agree, the ideal
output is integral. Exact sum makes its two Gaussian errors e and -e.
Error at most one then forces e=0. In particular, the nonzero zero-sum
fiber rotates exactly by i. Any global iterate identity requires 4 to
divide m.

For mixed parities, set `t=T Jd` and `u=T f(d)`. Both coordinates lie
in `Z+1/2`. The error bound is equivalent to u being a unit neighbor
of t. Their colors, defined by coordinate-sum parity, are opposite.
At sum s=1 the source color A is even and the target color is odd.
The pair squared norms are `1/2+|t|^2` and `1/2+|u|^2`. The action on
the source coordinate space A is `g=Q M_A`, where M_A sends t to u.
It is conjugate to F on that sum fiber. These conventions and the
unit-edge reduction come from the cited PR #7570 proof.

Let D_r be the square of half-grid points with maximum coordinate
magnitude at most r, for r a positive half-integer. Each color has
the same finite number of points. The minimum forward radial cost of
an edge from its A points to the exterior is

```text
b(r) = sqrt(2r^2+2r+3/2)-sqrt(2r^2+1/2).             (2)
```

Indeed the changing magnitude goes from r to r+1. The radial gap
decreases as the other coordinate magnitude increases, and that
magnitude is at most r. Corners of color A attain the minimum.
If `Delta(F)<b(r)`, injectivity forces M_A to map all A points of D_r
bijectively onto its other color. Hence g permutes A inside D_r.
The iterate identity already implies global bijectivity, but this
finite-capacity step needs only injectivity.

The function b decreases strictly for `r>=3/2`. Comparing its two
positive derivative terms gives the sign of `-2r^2+2r+1/2`, which
is negative there. Also `b(r)>1/sqrt(2)` on this range, by positive
squaring. These boundary facts are retained from PR #7699.

Take r=R/2. Since R>=5, both r and r-1 are in the decreasing range.
If `Delta(F)<beta_R=b(r)`, D_r and D_(r-1) are both invariant. Thus
their intervening ring must match its A points to its other color
within the ring. This ring has 4R vertices and its unit-edge graph
is a cycle. It has exactly two perfect matchings.

Index the cycle from the top-right corner along the top, left, bottom
and right sides. The two matchings send odd indices j to j+1 or j-1.
The quarter-turn Q subtracts R. On the 2R source points, the resulting
permutation is a cyclic translation by `(1-R)/2` or `(-1-R)/2`.
Its order is R or 2R. This ring classification is the cited prior
PR #7699 result, with its short calculation repeated here.

By definition, R does not divide m. Neither of these orders divides
m, contradicting `F^m=id`. This proves (1) as a necessary lower bound.
It does not assume a matching, symmetry or annular construction in
advance. The ring is forced by the two invariant finite squares.

## 3. Local maps on single rings and paired rings

For the upper bound, define one unit-neighbor permutation M on the
entire half-grid L, on both colors. Q preserves each square ring and
exchanges colors. We will make M commute with Q.

On a single ring of radius R0/2, use the cyclic successor in the same
index order as above, on every vertex of both colors. This is a unit-
neighbor permutation, and its inverse is the cyclic predecessor.
It commutes with Q. On either source color, `g=Q M` has order R0 or
2R0. Therefore its order divides m whenever R0 divides m and 4 divides m.
Every edge is tangential and its absolute radial gap is less than
`1/sqrt(2)` on every mixed-sum fiber. The single-ring geometry is prior
work; the choice of which rings to use is part of this construction.

Two consecutive rings can instead use the annular matching from
PR #7570. The following doubled-coordinate rule shows that it works
with any odd inner radius a, not only the source's original starting
sequence. The half-grid coordinates are now odd integers, and a unit
edge has length two. Pair rings with doubled radii a and a+2.

Use the connector `(a,a)<->(a+2,a)` and its four quarter-turn rotations.
On the inner top side, pair consecutive entries of

```text
(-a+2,a), (-a+4,a), ..., (a-2,a).
```

On the outer top side, pair consecutive entries of

```text
(a+2,a+2), (a,a+2), ..., (-a+2,a+2).
```

Rotate those pairs through all four quarter-turns. The two lists have
a-1 and a+1 vertices, both even. After the connector endpoints are
removed, the four rotated arcs are disjoint and cover every remaining
vertex. At a=1 the inner list is empty. Thus this is a complete
involutive matching on the two rings, with M commuting with Q.
Consequently `(Q M)^2=Q^2` and `(Q M)^4=id` there.

The annular edge formula is adapted from CubeJerry's construction.
The general starting radius and its assembly with directed single-ring
maps are the changed steps. M on the whole grid need not be involutive.

## 4. Assemble the global permutation

Fix m divisible by four and its first incompatible odd R>=5.

If 3 divides m, use single-ring cyclic maps on every odd doubled
radius below R, including one and three. If 3 does not divide m,
pair the central radii one and three by the annular rule, and use
single-ring maps at every odd radius from five through R-2.

In both cases, pair all remaining rings as

```text
(R,R+2), (R+4,R+6), (R+8,R+10), ... .                (3)
```

These pieces are disjoint and cover L. All are unit-neighbor bijections
between the colors and commute with Q. Every single-ring radius divides
m by the definition of R and the central case split. Every paired-ring
piece has fourth power one under g=Q M. Thus `g^m=id` on all of L.

The formula is local and total: locate the ring, select its single-ring
or paired-ring case, and use its position on one of four sides. It needs
no growing matching table or search over input points. On single rings,
M inverse is the predecessor. On paired rings, it is the same partner.

Return to Gaussian pairs. For equal-parity sums use f(d)=Jd. For mixed
sums use `f(d)=B M(T Jd)`, then `F(x,y)=((s+f(d))/2,(s-f(d))/2)`.
M exchanges colors, so these outputs are Gaussian integers. Their
sum is s and their error is one in the mixed case, zero otherwise.
In transformed coordinates the action is g=Q M, so `F^m=id` everywhere.

For a mixed output difference d', the inverse difference is
`-J B M^-1(T d')`. For equal parities it is -Jd'. This proves both
inverse identities. The same M is used for all mixed sum fibers and
both colors. Its quarter-turn covariance gives global Gaussian-unit
covariance of F. No sum-dependent lookup table is used.

## 5. Uniform sharp radial bound

On any mixed-sum fiber, the squared pair norms are `c+|t|^2` and
`c+|M(t)|^2`, with `c=|s|^2/2>=1/2`. Increasing c decreases the absolute
radial jump of a fixed edge. Tangential edges have jump below
`1/sqrt(2)`. A connector with inner doubled radius a has jump at most
`b(a/2)`, attained at a corner on a sum of norm one.

For the outer pairs (3), the inner a are R,R+4,... . Since R>=5 and b
decreases there, their largest possible jump is b(R/2)=beta_R.

The only other connectors are the optional central pair, with cost
`b(1/2)=sqrt(3)-1`. If this pair is used, 3 does not divide m. Then 9
does not divide m either, so R is 5, 7 or 9. All three beta values
exceed the central cost. It is enough to check

```text
sqrt(3)-1 < 733/1000 < sqrt(51)-sqrt(41) = beta_9,
```

followed by the decreasing property of b. Both comparisons follow by
positive integer squaring and are checked exactly. This central case is
why the first incompatible radius starts at five, not at three.

Thus every edge has absolute radial gap at most beta_R. Equal-parity
fibers have zero radial change. This proves a uniform all-input upper
bound for forward and inverse outward slack as well.

Let `a=(R+1)/2`. The first outer connector gives the Gaussian four-cycle

```text
(a,1-a) -> (a*i,1-a*i) -> (1-a,a) -> (1-a*i,a*i) -> (a,1-a).
```

Its squared norms alternate `(R^2+1)/2` and `(R^2+2R+3)/2`. It attains
beta_R in both directions, so all three radial suprema equal the lower
bound. This is the source's connector cycle with the new radius R;
the all-input argument above, not this cycle alone, supplies attainment.

Finite iterate identities can approach the unrestricted optimum
`1/sqrt(2)` as closely as desired. Take m divisible by four and by all
odd integers through a growing cutoff. Its first incompatible R tends
to infinity, and (1) tends to `1/sqrt(2)` by rationalization. No finite
m attains that limit, in agreement with PR #7699. This is a radial
precision tradeoff, not a multiplication-exponent improvement.

## 6. Verification and limits

The checker evaluates the first-incompatible-radius rule for all 1024
positive multiples of four through 4096. Twenty-three complete finite
grid fixtures cover 20 distinct cutoffs from five through 61, including both central choices
at R=5,7,9. They cover 41032 half-grid points. A separate arc generator
agrees with the local point rule. Direct orbit traversal agrees with
the algebraic cycle orders and checks divisibility into the prescribed m,
including large m without iterating m times.

All 2424 exterior edges of the two critical squares across 20 cutoffs
meet the claimed lower threshold. The construction checks both colors,
every inverse, unit error, phase covariance, radial inequality and each
attaining cycle. An additional 19208 Gaussian inputs cover all component
parities, eight iterate choices and both inverse identities.

Deleting the central annular case fails the identity for m=4,20,140.
Leaving the first incompatible ring as a single ring also fails. The
unchanged fourth-power construction exceeds the new m=20 radial budget.
The zero-sum control has exact period four. These checks use integer
arithmetic and certified square-root comparisons. The unbounded theorem
rests on the written proof, not the finite grid sizes.

The result changes no selected caller or physical provider. It does not
claim inverse by conjugation, row/column tensor commutation, a native
tariff, restored scratch, a complete multiplier invoice or discharge
of a selected assumption. The known tensor limitations in the cited
source remain. Exact least period, extra state, larger blocks, changed
error bounds and relaxed sum constraints are outside the theorem.
Full predecessor suites, selected cold replay, native/physical replay,
Lean, Docker, independent human and formal-kernel review were not run.
