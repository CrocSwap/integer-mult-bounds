# Independent exact review of the four actual constructions

The reviewed report is `product/combined-cap-2957-01/RESULT.json`, SHA-256 `da001fd772aceae36d4eb3ad0a840f7bf87647a23956135335cf271ce7e50474`. The independent checker is `review_ablations.py`, SHA-256 `00ba809c1b2fcb49c212f8304103c63905c146fa58104cc4267b22f43cf659fe`. Its final receipt is `four-way-review-01.json`, SHA-256 `4c2a58dcb8f5f2260c3120021549c19f57b5a206146295c82c87f495326c38f7`.

## Checked finite quantities

The checker authenticates the frozen result and its complete artifact manifest. It freshly evaluates the inherited authenticated frame rules on all eight actual words: common anchor, four normal-45 extractions only, fourteen rewrites only, and the combination, with both base and extra providers. Every local profile, helper-width inventory, and private-buffer count agrees with the report. The 82 or 86 buffers are charged through each scenario's actual physical stock. The exact all-column receipts are hash-checked, while their heavy native phase chains and the outer admission are not repeated here.

All four complete profiles have rank mass 65,088 × 370 = 24,082,560. The moment is

M(b) = Σ_r c_r r (73/r)^b / (73 × 896 × 370).

Consequently M(0) = 1,017/1,022 in every scenario. All supported ranks are positive and below 73, which makes M continuous and strictly increasing in b. The checker independently certifies M(lower) < 1 < M(upper) at every reported narrow rational bracket. It reads the actual complete profile files, rather than deriving a joint root by adding claimed decimal gains.

## Integer interval proof

Set B = 2¹⁹². Normalize any positive ratio 73/r as 2ᵏ y, where 1 ≤ y < 2. For z = (y−1)/(y+1), use

ln y = 2 Σ_{j≥0} z^(2j+1)/(2j+1).

Here 0 ≤ z ≤ 1/3. The first 128 positive terms are each rounded down to an integer multiple of 1/B. Their sum is a lower bound. Adding 128/B covers all those rounding errors, and the remaining tail is at most

2 z²⁵⁷ / (257 (1−z²)).

The same calculation bounds ln 2, so adding k copies yields a rigorous interval for ln(73/r). Multiplication by the exact rational b gives a directed interval for x = b ln(73/r).

Every evaluated x lies in [0,1). Starting with the term 1, the checker recursively rounds xⁿ/n! down or up at each multiplication and division. Summing through n = 40 gives a lower and upper enclosure of the truncated exponential series. The omitted positive tail is at most twice its first omitted term, because all subsequent term ratios are below 1/2. Thus adding twice the upward-rounded next term makes a valid upper bound. Multiplying these exponential intervals by positive integer weights c_r r and summing preserves enclosure. No floating-point library logarithm, exponential, root finder, or producer arithmetic is used by this independent check.

## Significant contributions

For a mechanism X, its leave-one-out lower gain is the joint lower endpoint minus the other mechanism's upper endpoint. Divide this by the joint upper endpoint minus the common-anchor lower endpoint to obtain a rigorous lower fraction of the total gain. These exact fractions are

- normal-45 extraction: 31780967736670757920 / 153531830483031419353 > 0.206999210760;
- fourteen rewrites: 121795400525535764056 / 153531830483031419353 > 0.793290877483.

Each is strictly greater than 1/10. These are nonlinear leave-one-out contributions; they need not sum to exactly one. The normal-45 and rewrite groups are inherited from PR #2942 and PR #2957 with their authors' attribution. This certificate establishes the exact finite tariff and ablation arithmetic, not priority for those mechanisms, a global optimum, or an unconditional integer-multiplication theorem.

The final checker also rejects one extra rank-1 charge and a perturbed contribution value through the same exact equality predicates used for the positive review. Complete ownership of every literal role and full native/source/compiler/outer admission remain separate final-release checks.

## Replay

Use Python 3 with only its standard library. Run `review_ablations.py --help`, then supply the frozen report directory, the actual eight-word directory, the pinned `preload_move.py` source, the PR #2957 `CLAIM.json`, and a fresh output path. The helper is executed by compiling its authenticated source bytes in a new module, so timestamp-valid stale bytecode cannot replace the checked code. No global configuration is changed.
