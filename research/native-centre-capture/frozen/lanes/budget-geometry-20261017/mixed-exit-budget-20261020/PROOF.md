# Budgets with one or two changed exits

## Result and scope

This addendum uses D=25, productive width 224, three local calls, and no idle jobs. It uses the same exact exponent snapshot as `low-displacement-budget-20261020/BUDGET.json`. Its SHA256 is `12836f56beffb0c136b075b44ec25377bba88d122924c67bd0a159a5037b84d2`.

Let k calls use the W48/I64 exit. Let the other 3-k calls use the raw exit of the same response family. Add a terminal comparator of 224 H1. The exact remaining allowances are:

| Response | Changed calls k | Extra H1 limit | Extra H2 limit |
| --- | ---: | ---: | ---: |
| Rank thirty | 1 | 71 | 35 |
| Rank thirty | 2 | 167 | 83 |
| Rank thirty | 3 | 263 | 131 |
| Rank sixteen | 1 | 66 | 33 |
| Rank sixteen | 2 | 162 | 81 |
| Rank sixteen | 3 | 258 | 129 |

Each limit must pay for all added native work. The table does not allow both limits at the same time. For example, the first row allows 71 H1 with no other added children, or 35 H2 with no other added children.

These are conditional histograms. The table does not prove that a changed-output word can be put at any selected stage. It does not construct a 224-H1 decoder for the changed global output. The output code, routed access, phases, arbitrary borrowed state, restoration, and recursive host remain separate obligations. No finite cost or kappa improvement is claimed.

The one-call rows give a useful construction target. A construction can try a single changed exit at the final stage. It need not first solve repeated transport between three changed exits. If that construction also admits the stated terminal comparator, its other native work must fit within the first or fourth row.

## Proof

For a native histogram H, the moment is

    M(H) = sum_r H[r] * r/(25*224) * (25/r)^b.

It is linear in H. Let R and C be the three-call raw and changed histograms, each with the same 224-H1 terminal comparator. The k-call histogram is

    H_k = ((3-k)R + kC)/3.

Thus M(H_k)=((3-k)M(R)+kM(C))/3. The frozen source gives outward rational bounds for both endpoint moments. This identity gives an outward rational interval for each mixed moment.

The checker also derives the cost of one H1 or H2 from the frozen bounds. If A is the raw preterminal moment, B is its moment after n copies of one child rank, and u is the cost of one such child, then B-A=nu. Therefore

    (B_lower-A_upper)/n <= u <= (B_upper-A_lower)/n.

The checker uses these exact rational intervals. For each stated limit n, it verifies that the upper bound for M(H_k)+nu is less than one. It verifies that the lower bound with n+1 copies is greater than one. The three-call limits also agree with the earlier frozen packet. No floating-point calculation determines a result.

The complete mass before other debt is 5,600-96k. Restoring 96 ranks after each changed call raises it to 5,600=DW. If every child rank is below D, that restored bill has moment greater than one for every b>0. This does not prove that such restoration is necessary.

For an all-H1 restoration, the exact table requires at least 25 H1 to be removed from 96k in the rank-thirty case, or 30 in the rank-sixteen case. These differences hold for k=1, 2, and 3 at the stated exponent. They are budget targets, not lower bounds on a legal decoder.

## Verification and credit

Run `python3 -I -B check_mixed_budget.py` and repeat with `-O`. The two runs must produce identical receipt bytes. The checker verifies the frozen source hash and the dimension, width, and number of calls. It then uses only rational interval operations. It does not repeat the source native replay or its phase compiler. A separate review of this addendum is pending.

The root and new-core-transfer lane supplied the response construction and the raw and changed native words. The earlier budget packet supplied the exact source counts and two-engine moment bounds. This addendum used AI assistance.

No PR, push, commit, or publication is authorized. Before any future PR description, read `/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
