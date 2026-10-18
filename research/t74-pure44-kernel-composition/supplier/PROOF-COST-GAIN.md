# A uniform physical-profile gain

Let `S_H(p) = sum_r H[r] r^p` for a complete paid-rank profile H. The native moment at complex saving b is `S_H(1-b)/(W*m^(1-b))`. Both suppliers have the same live stock W=66304 and dimension m=73, so their denominator agrees and is positive.

The freshly admitted profile has the following exact difference from [PR2269's source profile](https://github.com/jeremykothe2/integer-mult-bounds/blob/b479fc5567bc09ab9185bffe89b62594f36d74e5/research/gmx-t74-borrow43/new/SPEC.json):

`S_new(p)-S_old(p) = 249*(-12+8*2^p+4*3^p-4*4^p) + 666*(5^p-1-4^p) + (14^p-2*7^p)`.

`COST-GAIN-IDENTITY.json` binds both exact source profiles and checks every coefficient. The weighted rank-mass difference is zero. The number of paid children decreases by 1663.

Every parenthesized term is strictly negative for every real p with `0 <= p < 1`. `ProviderExchange.extra_provider_strictly_cheaper` proves the first term, with the stronger explicit saving bound `4*(2-2^p)^2`. `BorrowDeletion.rank_four_deletion_strictly_cheaper` proves the second. The general `BorrowDeletion.strict_subadditive_rpow_pos`, instantiated at x=y=7, proves the third. `ProfileGain.lean` assembles both components as a single standalone Mathlib-only module and adds `entire_actual_profile_gain` and the exact `actual_paid_power_difference` coefficient identity. Its nine distinct exported theorems have fresh kernel/transitive-axiom receipts. Use this standalone module OR the two components, because it intentionally preserves their seven declaration names; those copies are not additional mathematical results. Thus the analytic improvement holds throughout the sublinear exponent interval, independently of the particular numerical root search.

The physical meaning of the three terms is separate from this analytic algebra. First, replace the remaining 249 gauge44 invocations by their source-bound extra provider, using their identical ordered data/centre/normalized helper interfaces. Second, the exact alias 619 to 530 removes one width-four helper role from every one of the 666 complete invocations. The actual owner map returns those four pending axes to a rank-one remainder, replacing ranks 1 and 4 by rank 5. Third, the checked owner repacking replaces two rank-seven remainders by one rank-fourteen remainder. The full source-event/phase/owner checks establish those physical claims. The additional private cleanup stock, actual CLEARs and monomial warp work are charged by the corrected fresh invoice.

This establishes a strict sufficient moment improvement for the actual new physical profile. Its particular complex endpoint and final multiplication exponent still require the exact numerical enclosures, the stopped-ordinary bootstrap and the stated inherited compiler/outer assumptions. The scalar inequalities alone do not establish a multiplication theorem.
