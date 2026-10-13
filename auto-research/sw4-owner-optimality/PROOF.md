# Fixed-supplier owner-profile optimum

## Data and scope

Each of the 72 complete calls has helper-width inventory

| Width | 4 | 5 | 7 | 8 | 9 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Helpers per call | 80 | 32 | 54 | 122 | 216 |

There are 112 bins for each window. The 144 windows have capacities 8, 16, 32 and 48 with multiplicities 48, 32, 32 and 32 respectively. Thus total bin capacity is 387,072, helper demand is `72 * 3778 = 272016`, and idle rank mass is

`S = 115056 = 2397 * 48`.

A bin receives whole helper footprints with disjoint cells. Its residual rank is its capacity minus their total width. Since every helper width is at least four, any residual other than 48 is at most 44. The proof relaxes time-window, family and helper-identity restrictions. Every physical assignment admitted by the current whole-call model induces an assignment in this relaxation, so an exclusion in the relaxation applies to the physical model.

The fixed native paid profile per call is

`L = {1:2556, 2:334, 3:430, 4:194, 5:56, 8:8}`.

For idle profile I, the complete profile is `H = 72 L + I`. PR741's admitted profile uses

`I* = {48:2396, 44:1, 3:1, 1:1}`.

Its physical admission is recorded in PR741. This package independently binds the native inventory, billing and literal map to that frozen source, and checks its abstract packing feasibility.

## An integer width-price inequality

Assign helper-width prices

`a(4)=-1, a(5)=-20, a(7)=-8, a(8)=-2, a(9)=4`

and capacity bonuses

`d(8)=2, d(16)=4, d(32)=8, d(48)=-13`.

For a residual r, let u(r) be the maximum of `d(c) + sum a(w)` over every multiset of allowed widths summing to `c-r`, and over the four capacities c. These are small exact integer knapsacks. The verifier computes every value; an independent count-vector enumeration checks them. Relevant values are

`u(0)=0, u(48)=-13, u(44)=-14, u(4)=1, u(3)=7, u(1)=19`.

The total of all capacity bonuses and all helper prices is fixed:

`112*(48*2 + 32*4 + 32*8 - 32*13) + 72*(-80 - 32*20 - 54*8 - 122*2 + 216*4) = -31136`.

Consequently every feasible idle profile satisfies

`-31136 <= sum_r I(r) u(r)`.

The all-48 profile has right-hand side `2397*(-13) = -31161`, and the profile `{48:2396,44:1,4:1}` has right-hand side `2396*(-13)-14+1 = -31161`. Both contradict the inequality by exactly 25. The actual profile attains equality: `2396*(-13)-14+7+19 = -31136`.

This proof uses only integer widths and capacity counts. It does not rely on a solver status, a floating bound or the time windows.

## Moment reduction

Fix the exact admitted endpoint

`b0 = 1663966829367501881629 / 10^24`.

For `0 < b < 1`, define `f_b(r) = r*(73/r)^b`. This is a positive multiple of the strictly concave function `r^(1-b)`, with value zero at zero. The moment is

`M_b(H) = (sum_r H(r) f_b(r)) / (73*7168)`.

For a fixed integer mass m and part cap C, concavity implies that the minimum sum of f over arbitrary positive integer parts is attained at `floor(m/C)` copies of C and one remainder. Indeed, transferring mass from a smaller positive part to a larger part until the smaller vanishes or the larger reaches C cannot increase the sum. Repeating this exchange gives the stated vector.

Let n be the number of rank-48 residuals and write `t = 2397-n`. Then `0 <= t <= 2397`, and the remaining residuals have mass `48t` and part cap 44.

- `t=0` is the excluded all-48 profile.
- For `t=1`, if no part is 44, concavity gives the lower-cost relaxation `[43,5]`. If there is a part 44, the remaining mass is four. The unsplit `[4]` is excluded by the integer inequality. The split `[3,1]` gives the actual profile. Every other split has cost at least `[2,2]`.
- For `t>=2`, concavity gives `floor(48t/44)` copies of 44 and the remainder `48t mod 44`, along with `2397-t` copies of 48. Increasing t by 11 preserves the remainder and changes its cost by `12 f_b(44) - 11 f_b(48)`, which is strictly positive: `12*44 = 11*48`, and `f_b(r)/r` decreases with r. Hence the eleven cases `t=2,...,12` give lower bounds for all `t>=2`.

The verifier uses rational logarithm and exponential enclosures to prove:

1. The actual profile has `M_b0(72 L + I*) < 1`.
2. All 13 competing relaxations above have `M_b0 > 1`.
3. The eleven-step period increment is strictly positive.

All profiles have children smaller than 73, so their moments increase strictly with b. Every different feasible idle profile therefore has its complex root below b0, while the actual profile's root is above b0. The actual profile is optimal; an alternative owner map can at most reproduce its profile.

## Independent exhaustive arithmetic check

`independent_check.py` does not import the main verifier. It enumerates width multisets by count vectors and verifies the integer exclusions separately. It then uses the retained base-two interval engine to round each rank cost downward onto the common `10^-30` grid.

An unbounded integer-partition dynamic program computes lower bounds for all non-48 masses from zero through 115,056 using parts 1 through 44. It checks every `n=0,...,2395` directly. A separate part-cap-43 calculation handles `n=2396` with no 44, and explicit enumeration handles all partitions of the remaining four. Thus this checker does not depend on the main proof's 13-case concavity reduction. Downward rounding can only weaken the exclusions, and every recorded lower bound still exceeds one strictly.

Eight mutation checks reject erased width, duplicate owner, out-of-window ownership, changed native rank billing, two incorrect dual prices, and the endpoints b=0 and b=1.

## Boundary

The conclusion fixes the native paid profile and width inventory, 72 complete calls, and the capacity counts of the current whole-call model. It does not prove optimality over changed local words, mixed providers, changed call counts or capacity inventories, split helper invocations, or a different physical hosting model. PR741's all-size compilation, common-label and mutable-source realization, precision/tape and analytic-transfer assumptions remain inherited. No new κ or unconditional multiplication theorem is claimed.
