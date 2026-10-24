**Research discussion / PR / artifact:** Complementary frozen #5383 zero-row census; local `outputs/price-plane-swarm-20261024/07-frozen-zero/REPORT.md`, `RESULT-v2.json`, `PAID-ROWS-v2.jsonl.gz`, `CERTIFICATE-CHECK-v1.json`. No external publication.

**Exact commit:** Ali Romman's #5383 at `4bd6efa51a495a7c7b7754915cf0244e7e60969e`; capsule-v1 manifest SHA256 `ae6a1b933c386feabc9bab3300163df41e94bd3ddeeff973955695d33d5b11c8`; frozen word SHA256 `7883ba0faefc96505bb61ca7312d588fa22dfe2164050c817c1718b8fa28693a`.

**What is established:** All 3,282 remaining positive local backward paid-input rows are nonzero maps under the exact 624-retained-independent-plus-17-arbitrary-owned boundary at every positive tensor width. Each has one retained input coefficient `q U`, nonzero scalar times invertible word. No additional identity-on-zero deletion exists in this frozen word. Existing eight zero-retags are excluded from new savings; whole-invoice change is zero.

**What remains uncertain:** Lower-rank realizations on reachable subspaces, changed relations/pivots/preparation, changed scalar words, alternative direction and global optimality are outside this census. There is no new funded candidate. The census does not re-prove the inherited all-column native, owned-erasure, compiler, precision/tape or analytic-recovery foundations.

**Smallest useful next task:** Close this frozen-zero route and change one explicit source premise before another construction search; preserve active forward-transpose ownership. No further seed or native relation search is justified by these rows.

**Reproduction command and expected runtime:** `timeout 55s python3 -B outputs/price-plane-swarm-20261024/07-frozen-zero/census.py`, then `timeout 30s python3 -B outputs/price-plane-swarm-20261024/07-frozen-zero/check_certificates.py`; about 3.5 seconds combined and under 50 MiB observed RSS. Expected 3,282 paid rows, zero new zeros and `PASS_FROZEN_PAID_SINGLE_MONOMIAL_CERTIFICATES`.

**Predecessor credit:** Ali Romman #5383/#5377; Cao Yifan #4610; Cinna Davis; zxv; Jacob Alan Sussman; Chris R / Clear1nsight #5241/#5384; Cinna Davis and ToikY termwise tensor argument; retained source notices. Substantial OpenAI Codex assistance.
