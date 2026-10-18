# 300-digit endpoint and outer-witness refinement on PR1424 / PR1578 (construction unchanged)

**Current claim (matches `CLAIM.json` and `SPEC.json`): conditional kappa = 0.00167685522907132188620645677227459261951244873951047526280336519105115665521200964951578469164138454299292754381039421806310169652882028512229353918717571864509128612830494687936330582554446814903439815232715335011391445072917865378699803673653448606937592861929493520281339747942762829041141584064**, which is **4.064e-296** above PR1578's 0.001676855229071321886...114158. **Soundness repair:** PR1519 (philippeVV) showed that the fine Mercator engine added by PR1479 (copied into PR1485, and used by PR1510 and PR1513) summed an odd number of alternating terms (n = 1..799/829), so its lower log end was really an upper bound; accepts stay valid (upper ends) but the rejection claim was unsound in general. This package repairs it (even term count, asserted in code) and adds an independent exact 2*atanh oracle stage (`code/oracle_check.py`, run by `verify.py` as stage `fine-engine-oracle`) that checks both fine engines on log(73/t) for t = 1..72, log(73), 43, 189, 352 and the inner Mercator enclosures. The repair applies to the engines used by #1479, #1510 and #1513. Finding credited to philippeVV (#1519). All endpoint accept/reject certificates below were recomputed with the repaired engine.

Lineage: PR1424 (rohanarun) -> PR1479/PR1510/PR1513/PR1536/PR1578 (jeremykothe2) with PR1485 (rohanarun), PR1534, PR1549 and PR1582 (midhatn) refining the outer witness at the 1e-200, 1e-220 and 1e-300 endpoint levels. The construction, scalar words, provider inventory, owners and paid profile are PR1424's (PR1319's 74-replica exact fill of PR1297's four cold kernels), unchanged.

## What changed relative to PR1578
1. **300-digit grid resolution:** PR1578 established 1e-300 certified endpoints but stopped at a 295-digit grid (grid_digits = 295). This refinement deepens the grid to **grid_digits = 300**, resolving 5 additional decimal digits (`4064` at 10^-296 to 10^-300).
2. **Deepened outer witness settings:** In `SPEC.json:outer_refinement`: `grid_digits` = 300, `margin_digits` = 350 (eta = beta = 10^-350, target backoff 10^-353), `bootstrap_steps` = 130 (deepened from 112 to 130 steps), `endpoint_digits` = 300.
3. Strict assembly replay passes all 47 outer inequalities, conservative checks, and 4 rejection controls (`next_grid`, `zero_eta`, `zero_beta`, `unit_beta`).
4. Full package-owned verification passed (`PASS_T74_EXACT_FILL_COMPLETE_FINITE_ADMISSION`).

---
## PR1424's original description (SUPERSEDED settings; kept for credit and context only)
_Everything below is PR1424's text: its kappa 0.001676855229071321886206381217337893, 12 bootstrap iterations, eta = beta = 1e-40, 1e-36 grid and unchanged 1e-24 endpoints no longer apply to this package._

Conditional candidate κ = **0.001676855229071321886206381217337893**, an absolute increase of **6.2381217337893E-23** over PR1377 (0.001676855229071321886144). **Certificate refinement only: the construction, scalar words, provider inventory, owners and paid profile are unchanged.** This is a tiny numerical improvement, not a new kernel or practical speedup.

**Draft: complete new-package admission is pending.** An exact discovery run on previously verified PR1319 owner and invoice receipts passes both rational moment engines, all 47 strict outer inequalities, and four outer rejection controls. The full portable finite pipeline and a separate closed-form bootstrap audit will run after draft publication. The unchanged PR1297 native providers will be explicitly source-bound reused; no fresh native replay or hosted CI success is claimed.

The three witness settings are frozen in `SPEC.json:outer_refinement`: 12 bootstrap iterations, eta = beta = 10^-40 with target backoff 10^-43, and a 10^-36 final κ grid. The inherited complex and bit endpoint grids and their native/surcharge models remain unchanged. Every bootstrap cutoff is recomputed from the exact gap. The next final κ grid point rejects for this witness. No optimality over all outer parameters is claimed.

The recurrence is a_(j+1) = (1-s)s + s a_j. Its closed form is a_j = s - (s-a_0)s^j; 0 < a_0 < s < 1 gives a finite increasing chain below s. This only changes witnesses to the inherited conditional bootstrap and outer lemmas, whose assumptions remain in force. Root endpoints, arithmetic engines and finite construction are inherited unchanged.

Reproduce complete admission with `python3 -B verify.py --work /absolute/new/work --base-native-from /bound/base/native --extra-native-from /bound/extra/native`, or omit the two reuse flags for fresh native supplier runs. The output directory must not exist and assertions must be enabled. `evidence/OUTER-DISCOVERY.json` is discovery evidence, not a completed new-package replay. `evidence/pr1377/` contains predecessor receipts; inherited `PRICE.json` and input/parent receipts are not new verification.

Conditional finite construction only. All-size compiler, common-label/mutable-source realization, whole-call hosting, precision/tape, exact recovery, analytic transfer, PR559 recurrence correction and PR589 bit H1-H5 assumptions remain. No unconditional theorem, full Lean certification, or global packing claim.

Credit Rohan Arun PR1319 (74-replica exact fill) and PR1297 (four cold kernels); Jeremy Kothe PR1377 (finer final grid), PR1019 and PR1274; Jeremy Diviney PR1193; Thomas DiFiore PR1148; Hao Yan and retained owner/controller lineage; eumemic and icekylinx/Zhihao Chen for the exact outer assembly; the PR547/548/559 recurrence and PR589 bit suppliers. Prepared by Rohan Arun with substantial OpenAI Codex assistance. Apache-2.0; predecessor notices and bytes are retained. No independent human or proof-assistant verification is claimed.

Next: complete finite replay and independent witness audit, then mark ready if they pass. Continue searching for a new paid construction; this numerical gain does not resolve the decoder frame-realization problem.
