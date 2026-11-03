# Stronger rational credit for paid rank exchanges

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped mathematical proof with exact finite corroboration.
For every integer rank k>=2, a midpoint convexity argument strengthens
the rational curvature allowance in Dugongue's
[PR3863](https://github.com/CrocSwap/integer-mult-bounds/pull/3863).
It answers that package's second Open next question. On its stated interval,
1,181 proposed `2+2 -> 1+3` exchanges suffice to fund one extra rank-one
child, reducing the cited sufficient target of 1,775 by 594 exchanges.
This is a stronger accounting certificate, not a constructed rewrite,
a minimum count for the true power moment, or a new kappa.

The predecessor's capped-mass identity and paid-overhead transfer are
cited ingredients. No predecessor program, supplier or theorem is audited.
The new step is the larger uniform rational coefficient below and its
strict paid consequence. Jensen's inequality is classical; no general
convexity or literature-wide priority claim is made.

## Uniform coefficient and proof

For any real `0 < ell <= a <= u < 1`, let

```text
f_a(x) = x^(1-a),  f_a(0)=0,
theta_k(a) = 2 f_a(k) - f_a(k-1) - f_a(k+1).
```

For every integer k>=2, the new bound is

```text
theta_k(a) >= ell(1-u) / [ k (1+u(k-1)) ].                 (1)
```

The endpoints can be rational, making the right side rational without
evaluating a logarithm or a nonintegral power. The earlier sufficient
coefficient was `ell(1-u)/[(k+1)(1+uk)]`. The new coefficient is strictly
larger for every k>=2 and every permitted interval.

Two integrations give the credited triangular-kernel identity

```text
theta_k(a) = a(1-a) integral_-1^1
              (1-|t|) (k+t)^(-1-a) dt.
```

The triangular density has mass one and mean zero. The function
`x -> x^(-1-a)` is strictly convex on positive x, since its second derivative
is `(1+a)(2+a)x^(-3-a)>0`. Jensen's inequality therefore gives

```text
theta_k(a) > a(1-a) k^(-1-a).
```

All arguments of the integrand are positive because k>=2. The tangent
inequality for the concave function `x^a` at x=1 gives

```text
k^a <= 1+a(k-1) <= 1+u(k-1),
a(1-a) >= ell(1-u).
```

Taking the reciprocal of the first positive inequality and multiplying
proves (1), in fact strictly. For the coefficient comparison, both factors
in `(k+1)(1+uk)` exceed their positive counterparts in
`k(1+u(k-1))`. The numerators agree and are positive.

At k=1 retain the predecessor bound

```text
theta_1(a) >= 4 ell/(3+2 ell).
```

For completeness, `theta_1=2(1-exp(-a log 2))`,
`log 2>=2/3`, and `1-exp(-x)>=x/(1+x)` for x>=0 prove this bound.
No midpoint integral through zero is asserted.

## Complete finite profiles and paid charges

Let old and new counts `o_r,n_r` be nonnegative integers on ranks 1,...,T,
with T>=2, and define

```text
d_r = n_r-o_r,
C_k = sum_r d_r min(r,k).
```

Assume `C_T=0` and every `C_k<=0`. The retained finite identity gives

```text
sum_r (o_r-n_r) r^(1-a) = sum_(k=1)^(T-1) (-C_k) theta_k(a).
```

Thus a sufficient uniform raw credit is

```text
L_mid = (-C_1) 4 ell/(3+2 ell)
        + sum_(k=2)^(T-1) (-C_k) ell(1-u)/[k(1+u(k-1))].
```

It never weakens the earlier credit. It strictly strengthens that credit
whenever any `C_k<0` for k>=2. This comparison concerns sufficient lower
bounds, not exact moment optima. If the only nonzero deficit is at k=1,
the two certificates coincide.

For any actual additional nonnegative integer-rank histogram `e_r`, put
`Q=sum_r r e_r`. Since `r^(1-a)<=r` for r>=1, the complete paid raw moment
strictly improves whenever `Q<L_mid`. Multiplying by an unchanged positive
normalization and adding unchanged common costs preserves the strict
comparison. All extra costs must be included. Changed normalizers, missing
target debits or unpriced physical operations cannot be absorbed by this
algebraic statement. The argument applies to every finite T; the evaluator
separately enforces a rank-64 resource bound.

## First sufficient improvement

For one `2+2 -> 1+3` exchange, only `C_2=-1` is nonzero. At
`ell=17/10000` and `u=18/10000`,

```text
L_mid = 84847/100180000,
1180 L_mid <= 1 < 1181 L_mid,
1181 L_mid - 1 = 24307/100180000 > 0.
```

Therefore 1,181 exchanges, followed by one additional rank-one child,
strictly lower the complete raw moment throughout that closed interval.
The proposed exchanges need 2,362 available rank-two children. This package
does not assert that any particular current source can realize them.
The preceding rational coefficient is `84847/150540000`; its sufficient
threshold is 1,775. At 1,181 exchanges it does not certify the paid charge.

The count 1,181 is minimal for the displayed sufficient inequality. No
claim is made that 1,180 actual exchanges cannot pay the charge. The bound
deliberately discards curvature information. Research stops at this first
strict improvement rather than optimizing that true threshold.

## Exact replay

From the repository root, with CPython 3.12 and only its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/midpoint-rank-credit/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/midpoint-rank-credit/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/midpoint-rank-credit
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/midpoint-rank-credit --check-source-history
```

Any CPython 3.12 executable may replace the local path. The final command
checks exact publication bytes and source ancestry after committing.
Expected direct marker is `PASS_MIDPOINT_RANK_CREDIT`. JSON stdout is a
generated receipt bound to all five package files. No receipt is handwritten
or committed; replay writes no files and imports no predecessor executable.

The checker independently encloses powers with rational positive atanh
series and Taylor series, each with an explicit geometric remainder. It
reduces r to `2^b t` with `1<=t<2`, evaluates 24 logarithm terms, and
encloses `exp(-x)` by reciprocating and raising an enclosure of `exp(x/8)`
to the eighth power. Its 24th-degree positive exponential sum has first
omitted term `v_25`, with tail at most `v_25/(1-y/26)` for `y=x/8<=5/8`.
Monotonicity determines the endpoint directions. No floating-point
acceptance or sampled claim about an entire interval is used.

The direct replay reports 288 curvature comparisons at ranks 1,...,32,
using both endpoints and midpoints of three intervals: the paid example,
`[1/8,1/4]` and `[1/3,2/3]`. Ninety-nine integer square/cube comparisons
separately corroborate the power enclosures at a=1/3,1/2,2/3.
All 81 count profiles on ranks 1,...,4 with counts 0,1,2 are paired.
There are 155 unequal eligible pairs, giving 465 profile/interval pairs
and 1,395 complete power-moment comparisons at the nine points.
These finite checks support the implementation. The written proof supplies
the all-rank and all-real-interval result.

Twelve invalid profile/interval cases must reject. Separate controls cover
zero gain, exact rank-one powers and the unsound favorable-endpoint bound
`theta_2(1/2)>=1/4`. Explicit exceptions keep all fifteen controls active
under `-O`.

## Scope, provenance and limits

Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority
revision 8. The selected source-binding positive control passed and resolves
PR6030 as selected. It is metadata orientation, not a supplier replay.
TASK.json changes the scalar-to-moment card to this accounting side result;
it does not claim a chronological construction satisfying the original gate.
SOURCES.json pins the card, selected record and conceptual predecessor
README/proof as provenance. There are no live external proof inputs.

The verifier accepts no CLI search-size parameters. Its profile evaluator
allows at most 65 entries, each count at most one million, and rational
endpoint denominators at most one million. The fixed enumeration examines
three sets of 6,561 profile pairs. Curvature checks use at most 33 positive
power values per point; every analytic series has exactly 24 iterations.
All functions fit within sixty physical lines. There is no recursion,
subprocess, network request, dynamic evaluation or persistent resource.
CPython managed allocation is a bounded deviation from fixed steady-state
allocation. Standard-library internal allocation is not audited.
Warning-strict normal and optimized execution and AST inspection provide
available diagnostics; no standalone linter is installed.

No physical/native circuit, supplier admission, dirty restoration, compiler,
stock, precision/tape proof, selected-frontier change or complete
multiplication theorem is supplied. No selected cold replay, Lean or Docker
suite was run. Independent human and formal proof-kernel review are unclaimed.

Credit Dugongue / PR3863 for the explicit opening, the triangular integral,
the earlier quantitative allowance and paid-overhead framework. Credit the
ranked-pair verification and Avi Eisenberg / ikeboy, eumemic, Chafik Boukhalfa,
Dominik Scholz and their retained lineage for the capped-mass identity and
all-exponent sign theorem. MathProof supplies the earlier reserve framework.
The classical tools retain their credit. Predecessor files and credit lines
are unchanged.

Live open and account PRs, active Discussions, recent handoffs, local
reservations, main README formula/object searches and merged general-form
searches were checked before the
[advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19362857).
The cached card search covered 406 open PRs and 6,350 Discussion records,
with only 114 of 8,917 local HEAD notes in the sparse checkout. Separate
main-tree searches supplement that limit. No search establishes novelty
against unpublished work, arbitrary historical diffs or all literature.

## Open next questions

1. Can a legal chronological exchange attain this stronger paid target?
   First freeze one compatible source pair, construct its arbitrary-dirty
   endpoint identity and list every added fee. Native compatibility,
   ownership, chronology, restoration and compiler/precision/stock remain
   blockers. The accounting certificate alone does not fund unknown work.
2. What is the least actual exchange count on the stated interval?
   First bound the derivative of `2*2^(1-a)-1-3^(1-a)` and certify its
   minimum with rational enclosures. Global monotonicity and true-threshold
   optimality are unproved here. No follow-on search is reserved.

Structured questions and blockers are in [TASK.json](TASK.json).
