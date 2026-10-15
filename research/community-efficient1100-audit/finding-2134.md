Thanks for the contribution. Review of `388a63c83cf24c3355be9798bde5a381188dadb3` in the frozen 100-PR round found one remaining issue:

The census omits legal source-count profiles. For example singleton counts (1,1,1,2,2,6), followed by a TRIO on the three odd labels, give 16 applications with every source restored and total profile (2,2,2,2,2,6), but are rejected by PROFILES. Supply exclusions for all omitted cases or narrow the stated domain; the two-profile search does not prove the present full one-TRIO claim.

The scoped replay evidence is retained in the [batch review](https://github.com/CrocSwap/integer-mult-bounds/blob/main/docs/research/community-efficient1100-review.md). Passing finite checks and the scope of the written claim are tracked separately. This PR is staying open for the focused revision; contributor and predecessor credit are retained.

<!-- efficient1100-review-2134-388a63c83cf24c3355be9798bde5a381188dadb3 -->
