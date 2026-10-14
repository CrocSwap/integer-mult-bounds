# Exact free-slack refinement

Let r0 = 10^(-30010), q = certified complex endpoint - 2 r0, F = 10^30046, and B = 10^(-30022), exactly as in the pinned parent. For any delta > r0 in the retained admissible window, put epsilon = 1 - delta and beta = 1 - 3 delta. The explicit saving is K(delta) = floor(F epsilon q)/F - B.

The parent uses delta_old = 2 r0. This contribution uses delta_new = (1025/1024) r0. The difference in unrounded savings is (1023/1024) q r0. Therefore

`(1023/1024) q r0 - 1/F < K_new - K_old < (1023/1024) q r0 + 1/F`.

The lower bound is strictly positive. The exact gain is independently recomputed and compared with CLAIM.json, rather than inferred from a displayed decimal.

The potentially tight gamma condition becomes `1 - epsilon - r0 = r0/1024 > 0`. The Gaussian margin above the transform saving is `delta_new (1 - 2 q) > 0`; the membership margin is `1 - beta - 2(1 - epsilon) = delta_new > 0`. Beta stays inside `[1 - delta_new(1 + 1/q), 1 - 2 delta_new)`. Both epsilon = 1 and delta = r0 remain inadmissible limits. The nine cost powers are independently derived in verify.py; all 62 retained strict inequalities and 17 retained rejection controls are checked in ledger.py.

The source-bound full gate must separately establish the unchanged supplier moment endpoints, both moment engines, adjacent-grid rejection, paid invoice, owner/controller and native phase checks. This proof does not replace those checks or establish the inherited all-size hypotheses. The point approaches the same supplier ceiling and yields an extremely small numerical refinement.
