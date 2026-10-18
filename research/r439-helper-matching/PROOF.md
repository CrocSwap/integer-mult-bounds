# Disjoint helper matching, exact floor and precision gap

All endpoint algebra is over F2. Integer positive bounds are calculated
separately, without binary cancellation. Equality of two forward integer
operators is not asserted.

## Fixed recipe and matching reduction

Let K be the original PR589 helper-to-target matrix and E the exact product
of 306 target transvections frozen by PR915. Its middle matrix is R = EK.
For helper pair `(a,b)`, the physical operation is `s[a] ^= s[b]`. Let H be
the product of all such operations in a disjoint pairing. Disjointness makes
the factors commute, each factor is involutive, and H inverse equals H.

Apply H to helpers and E to targets, inject R H inverse, then restore E in
reverse chronological order and H in reverse order. The target output is

```text
E inverse (E y + E K H inverse H s) = y + K s.
```

All helpers are restored and sources are untouched. Operands remain at
frame zero. Every non-D field and the complete state/frame boundary before
A are preserved. The original H2 syntax and literal K extractor do not
describe this basis-changing prefix. Their semantic replacement is the
entire arbitrary-input boundary just proved; their implementation remains
unchanged and reports false. All other original interface predicates hold.

Writing H = I + B and E = I + A gives the necessary middle matrix
`K + AK + KB + AKB`. verify.py computes every coefficient directly from K
and E. Its 7,343 nonzero mixed-term entries cannot be discarded; doing so
fails the full D boundary control.

Right multiplication by the helper transvection changes column b by column
a. If S_j is the support of column j of R, the fully paid saving is

```text
g(a,b) = |S_b| - |S_b symmetric_difference S_a| - 2.
```

The two ADDs prepare and restore the helper. Accepted pairs have disjoint
endpoints, so no pair changes another pair's columns. Consequently the
exact total saving is the sum of g over the pairing. The fixed target
operations and non-D word cost the same in every member of the class.
For each unordered edge `{a,b}`, define `w(a,b) = max(g(a,b), g(b,a))`.
An oriented pairing has saving at most its undirected matching weight;
choosing a best orientation on each matched edge attains that weight.
Nonpositive edges are unnecessary for the unconstrained maximum.

## Integer certificate

NOMINATION.json contains nonnegative doubled vertex prices q_v and positive
doubled odd-set prices z_S. Every S consists of distinct vertices and has
odd cardinality at least three. The independent verifier checks all 96,141
unordered edges, including edges with nonpositive gain:

```text
2 w(a,b) <= q_a + q_b + sum(z_S : a and b both belong to S).
```

For any matching M, summing gives

```text
2 weight(M)
  <= sum(q_v : v is matched) + sum_S z_S * |M intersect edges(S)|
  <= sum_v q_v + sum_S z_S * floor(|S|/2).
```

The second inequality uses only nonnegativity, disjoint matching endpoints
and the fact that each internal edge consumes two vertices of S. Odd sets
may overlap: each cardinality bound is separately valid, and their
nonnegative weighted sum remains valid. No solver, matching-polytope theorem,
laminarity assumption or floating arithmetic is needed to verify this bound.

The 439 vertex prices and 19 odd-set prices give doubled objective **2,520**.
The frozen 199-pair lexicographic witness has exact saving **1,260**, proving
equality. Thus every member of the fixed recipe class costs at least
**13,208 - 1,260 = 11,948 complete ADDs**, and the witness attains that cost
when precision is ignored. The other two nominated matchings independently
attain the same saving. This is an exact class optimum, not a search failure
or a statement about unrestricted XOR circuits.

The default verifier obtains S_j by set-valued reconstruction from the
original K and frozen E. Discovery instead uses packed columns and NetworkX's
integer matching implementation. The solver's private dual state is captured
only during optional nomination, with version and source hash fixed. The
default checker trusts none of that state without checking every inequality
and an attaining matching.

## Bounded precision selection

The three declared nominations use ordinary integer edge weights under
lexicographic or seed-4 insertion order, then a third lexicographic objective.
For the third objective, let c_a be the coefficient of helper a at final
register 291 in the unchanged positive suffix. That register has the largest
ordinary final source/helper value, 49,347. A helper preparation/restoration
increases the positive endpoint bound of its destination a from 1 to 3.
Thus c_a is a useful forward-cost proxy. It is not a claim about which
coordinate maximizes every changed word's complete prefix.

The third integer edge objective is `L*w(a,b) - c_destination`, with
`L = 1 + sum_a c_a`. Each helper can be a destination at most once, so the
total secondary cost lies between zero and `sum_a c_a`. A unit improvement
in primary saving dominates every possible secondary difference. This
preserves primary matching optimality while preferring a smaller proxy.
When both orientations have equal gain, the lower proxy cost is selected.

All three nominated optima require 193 nine-stage prefix bits. The bounded
follow-up prices every one-pair deletion, 199 + 199 + 200 = 598 alternatives.
Together with the three originals, exactly 601 words are evaluated. Seventeen
pass both caps. The selected candidate removes pair `(428,150)` from the
third matching. This loses one unit of saving and lowers F from 72,459 to
70,083. Its B remains 10,548,832.

Candidate D costs `199 + 306 + 4,719 + 306 + 199 = 5,729`, giving 11,949
complete ADDs. Its saving is 1,259 beyond PR915, 31 beyond PR926 and 12,356
beyond PR589. The fixed-class precision-constrained minimum is therefore
in the integer interval **[11,948, 11,949]**. Failure of the three nominated
optima does not exclude a different feasible matching at 11,948. Neither
global precision-constrained optimality nor optimality of this discovery
proxy is claimed.

## Complete bounds and remaining obligations

The positive interpreter lowers all ADDs, COPYs and ERASEs. For the reverse
word it reverses instruction order and interchanges COPY/ERASE roles.
Every ADD is replaced by nonnegative addition, copies inherit their source
bound, and erasures reset the copy slot. Recording each intermediate
coordinate gives the signed triangle-inequality prefix majorant. It does
not use the F2 endpoint identity to cancel integer growth.

All 601 words are replayed in both orientations, totaling 14,390,692 literal
instructions. The candidate's F = 70,083 and B = 10,548,832 yield a 101-bit
local bound and a 192-bit nine-stage bound. Both strict inequalities
`64 F^3 B^2 < 2^104` and `2^18 F^5 B^4 < 2^192` hold. The second uses the
source template at K = 4, nb = 6(K-1) = 18. The original 177-bit estimate
and charged 192 bits are reproduced from the pinned invoice. The candidate
uses about 87.43% of that numerical ceiling.

The arithmetic-floor calibration remains a valid binary circuit and passes
all unchanged local 104-bit native checks. Its 193-bit nine-stage expression
is rejected separately. It is retained as an explicit adverse case, not
published as an admitted improvement.

Every register's MOVE path, all COPY/ERASE operations, 439 helpers, nine
rank-seven totals and paid histogram are unchanged, with rank mass 5,129.
No additional source access, scratch, recursive child or copied total is
free or omitted. Five complete words are checked on 661 distinct D input
columns in both directions, plus original full-word geometry and native
5/9/11-stage columns. Scalar savings at those stages are 155 / 279 / 341
beyond PR926, including every occurrence of the new prefix.

Integration still requires semantic D acceptance, changed whole-hosted
emission and audit, full finite/precision invoices and outer assembly. The
same paid rank profile and this one prefix estimate do not establish those
results. The inherited common-label realization and analytic assumptions
remain in force.
