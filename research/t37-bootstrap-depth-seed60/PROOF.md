# Exact depth boundary in the retained affine accounting

Let `a0 = 384599/10^10`, `b = 0.001664727258740678855772`,
`u = b + 10^-24`, and `k = 1661960547713947/10^18`.
The selected receipt admits b and rejects u using both rational moment
engines. Those moment calculations and their monotonicity theorem are inherited,
not rerun here. The lower bound below is an exact conditional statement for
any permitted savings bounded above by u; it does not require a new root claim.

## Five-level obstruction

The retained affine accounting has transition

`f(a,s) = s(1-s+a)`.

On `0 <= a <= u`, `0 < s <= u < 1/32`, this is increasing in both variables:
`d f / d a = s > 0` and `d f / d s = 1-2s+a > 0`.
Consequently even if every level chooses an independent saving `s_j <= u`,
and the resulting saving is any `a_j <= f(a_(j-1),s_j)`, induction gives

`a_j <= U_j = u-(u-a0)u^j`.

Since `0<a0<u`, the U_j increase with j. The balanced outer compact margin
at nonnegative reservation loss eta is

`m(a,eta) = (1-eta)*a*(1-2eta)/(1+a*(1-2eta)) <= a/(1+a)`

in its admissible domain. Thus every certificate with at most five levels
has compact margin at most `U_5/(1+U_5)`. Exact cross-multiplication in the
certificate proves this is **strictly below k**. The compact constraint is
one of the mandatory 47; the remaining constraints cannot repair this failure.
Zero eta/beta are used only to relax this upper bound: they are not accepted
as finite witnesses, and explicit controls check their rejection.

This is a bound on this fixed starting saving, supplier ceiling, transition
accounting and outer constraint. It is not an algorithmic lower bound.
A stronger initial saving can escape it: solving the relaxed five-level
equality gives `a0_required = u-(u-k/(1-k))/u^5`, approximately
`0.001597384256051765`. A positive control above that threshold crosses k.

## Six-level witness and all source interfaces

Use the original selected values `eta=beta=10^-24` and
`s=min(c,(1-beta)b)-10^-27`, where c is the pinned bit endpoint.
The source recursion gives `a_j=s-(s-a0)s^j`. For every retained level the
checker establishes exactly

`a_(j-1) < a_j < s < 1-a_j`

and positive minimum gap among

`s-a_j`, `1-a_j-s`, `1-a_j-s*(1-a_(j-1))`, `1-s`.

For the T37 payload allowance p=1024, the original sufficient cutoff C obeys

`C*gap^2 >= 36` and `C*gap >= 2*(4+p)`.

The integer checker verifies both inequalities for each unchanged cutoff and
rejects C-1 in every retained level. This is minimality for these two stated
sufficient inequalities, not minimality of the actual analytic error estimate.
The original seven-level records are first reconstructed exactly. The six-level
witness uses their first six records without changing gaps, payload or cutoff
rules. The seventh step and its cutoff are simply unused.

At a6 the pinned outer engine evaluates all 47 strict inequalities with exactly
the original bridge constants and k. All pass. A second exact computation
matches its compact minimum and proves k is the largest strict `10^-18` grid
point below that margin. The next grid point fails the compact constraint.
Since at most five levels fail in the relaxed class and the actual six-level
witness passes, the least number is six in this stated accounting class.

## What remains conditional

The audit preserves the existing conservative admission and supplier evidence
as inputs; it does not run, replace or remove those checks. It changes no
production driver. Natural-number cutoff validity and every finite scalar
interface above are checked. The all-size completion of these bootstrap steps,
ordinary supplier/compiler implementation, physical common-label/mutable-source
realization, hosting, tape/precision implementation and analytic transfer
remain inherited obligations. Neither a native execution nor a full
multiplication theorem is certified by this finite calculation.
