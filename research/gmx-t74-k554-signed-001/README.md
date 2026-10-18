# pivot 554 helper-donor kernel (k554-signed-001) stacked on the previous record

Adds the exact helper-donor kernel k554-signed-001 (pivot 554, found by LeverRank/kernel566) to the previous record's local words: re-solved frames, fresh natives, PLAN rebound, SPEC refrozen, certified fine endpoints and exact outer witness of the base package. kappa 0.001676938111022438771190100017020725032555691674761792047536039179.

kappa = 0.001676938111022438771190100017020725032555691674761792047536039179. `new/CHAIN.json` lists every kernel step; `new/rebuild_chain.py` re-verifies each step against its own base words (exact B + early-cleanup map over all rows, remaining cleanup, interfaces). Pivot reads: every inserted read of the pivot q must see the row of q equal to s*I with s = +1 or -1 (new/pivotcheck.py). A pivot restored by a sign-flipping cleanup gate (e.g. 554: `scale q by -1`) is read as -q after the restore with the coefficient taken with that sign; exactness is proven by the unchanged map check. Tamper controls (signs unaccounted; each new coefficient moved one dyadic step) must all fail the map check.

Credits: pivot-554 helper-donor kernel generalising PR1625 (kernel566.py; sign-aware pivot-read check pivotcheck.py). PR1625 (mdumitrean): pivot-566 helper-donor kernel, words, edits, rebuild.py, rebind.py. PR1319, PR1297, PR1424, PR1485, PR1574 (rohanarun); PR1274, PR1378... (see README) and the 1e-200/1e-300/1e-400 refinement PR1479, PR1510, PR1513, PR1536, PR1578 (jeremykothe2); PR1534, PR1549 (midhatn); PR1519 (philippeVV, fine Mercator engine soundness finding); PR1286, PR1193 (jeremydiviney), PR1148 (Thomas DiFiore) and the retained lineage. Research direction, prioritisation and release strategy: jeremykothe2. Implementation assistance: oh-my-pi.

---
# PR1625's pivot-566 helper-donor kernel on the T74 exact fill, with certified 1e-70 endpoints and a 1e-66 outer witness

**Current claim (matches `CLAIM.json` and `new/SPEC.json`): conditional kappa = 0.001676896669021299307750710997267962671611490016339159610658464055**.

## Credit and lineage
The construction gain is PR1625 (mdumitrean): a seven-insert helper-donor kernel for cold pivot 566 on the two local words of PR1297, as vendored in PR1319 (H1 +1, H2 -2, H3 +1 per call on both words; owners, dispatch, parent and idle remainder reused byte-for-byte). `new/gauge44-word-566.json.gz`, `new/extra-word-566.json.gz`, `new/EDITS.json`, `new/rebuild.py`, `new/rebind.py` and the rebound `new/PLAN.json`/`new/PROFILE.json` are PR1625's. The T74 construction is PR1319 (rohanarun) over PR1297's four cold kernels (rohanarun; kernel 531 PR1274 jeremykothe2, kernel 543 PR1286 rohanarun). The outer-witness / endpoint refinement lineage: PR1424, PR1485, PR1574 (rohanarun); PR1479, PR1510, PR1513, PR1536, PR1578 (jeremykothe2); PR1534, PR1549 (midhatn); the soundness repair of the fine Mercator engine is PR1519 (philippeVV); PR1625's own 1e-200 stack is the baseline compared against.

## What this package adds on top of PR1625
1. Certified complex endpoints (native and conservative, recomputed for the new global profile) at 1e-70: the retained engines certify the inherited 1e-24 bracket containing each endpoint, and finer-constant copies of both rational engines (`code/fine_mercator.py`: 2^-320 outward rounding, 320 (even) Mercator terms, 40 exponential terms; `code/fine_moment.py`: 1e-100 outward rounding, 110 log terms, 40 exponential terms) certify accept at the endpoint and reject at endpoint + 1e-70, both required. Repaired engine (even term count, asserted) plus the independent exact atanh oracle stage (`code/oracle_check.py`, stage `fine-engine-oracle`).
2. Outer witness settings in `new/SPEC.json:outer_refinement`: grid_digits 66 (the final kappa grid), margin_digits 76 (eta = beta = 10^-76, backoff 10^-79), bootstrap_steps 30, endpoint_digits 70; `dec()` prints 176 significant digits.
3. `verify.py` additionally: rebuilds both shipped words from PR1297's pinned words (`new/rebuild.py`), runs the retained `audit_local.py` on them, runs the lineage native chain on both (or reuses hash-checked cached natives), rebinds the PLAN (`new/rebind.py`, must equal `new/PLAN.json` beyond bind-rebound receipt hashes), then the strict T74 chain on `new/PLAN.json` and `new/SPEC.json`; the fine-engine results are memoised across stages (`code/fine_cache.py`, keyed by engine hash and arguments).

The top-level PLAN.json/SPEC.json are the unchanged PR1424/PR1319 files used by the owner reconstruction and parent lift checks; the strict stage uses `new/`. All 47 strict outer inequalities, the rejection controls and next-grid rejection hold (checked offline with the package's own outer witness and engine). The remaining gap to the exact root is the 1e-70 endpoint bracket; the displayed digits are set by the 1e-66 grid.

---
## PR1424's original description (SUPERSEDED settings and profile; kept for credit and context only)

Conditional candidate κ = **0.001676855229071321886206381217337893**, an absolute increase of **6.2381217337893E-23** over PR1377 (0.001676855229071321886144). **Certificate refinement only: the construction, scalar words, provider inventory, owners and paid profile are unchanged.** This is a tiny numerical improvement, not a new kernel or practical speedup.

**Draft: complete new-package admission is pending.** An exact discovery run on previously verified PR1319 owner and invoice receipts passes both rational moment engines, all 47 strict outer inequalities, and four outer rejection controls. The full portable finite pipeline and a separate closed-form bootstrap audit will run after draft publication. The unchanged PR1297 native providers will be explicitly source-bound reused; no fresh native replay or hosted CI success is claimed.

The three witness settings are frozen in `SPEC.json:outer_refinement`: 12 bootstrap iterations, eta = beta = 10^-40 with target backoff 10^-43, and a 10^-36 final κ grid. The inherited complex and bit endpoint grids and their native/surcharge models remain unchanged. Every bootstrap cutoff is recomputed from the exact gap. The next final κ grid point rejects for this witness. No optimality over all outer parameters is claimed.

The recurrence is a_(j+1) = (1-s)s + s a_j. Its closed form is a_j = s - (s-a_0)s^j; 0 < a_0 < s < 1 gives a finite increasing chain below s. This only changes witnesses to the inherited conditional bootstrap and outer lemmas, whose assumptions remain in force. Root endpoints, arithmetic engines and finite construction are inherited unchanged.

Reproduce complete admission with `python3 -B verify.py --work /absolute/new/work --base-native-from /bound/base/native --extra-native-from /bound/extra/native`, or omit the two reuse flags for fresh native supplier runs. The output directory must not exist and assertions must be enabled. `evidence/OUTER-DISCOVERY.json` is discovery evidence, not a completed new-package replay. `evidence/pr1377/` contains predecessor receipts; inherited `PRICE.json` and input/parent receipts are not new verification.

Conditional finite construction only. All-size compiler, common-label/mutable-source realization, whole-call hosting, precision/tape, exact recovery, analytic transfer, PR559 recurrence correction and PR589 bit H1-H5 assumptions remain. No unconditional theorem, full Lean certification, or global packing claim.

Credit Rohan Arun PR1319 (74-replica exact fill) and PR1297 (four cold kernels); Jeremy Kothe PR1377 (finer final grid), PR1019 and PR1274; Jeremy Diviney PR1193; Thomas DiFiore PR1148; Hao Yan and retained owner/controller lineage; eumemic and icekylinx/Zhihao Chen for the exact outer assembly; the PR547/548/559 recurrence and PR589 bit suppliers. Prepared by Rohan Arun with substantial OpenAI Codex assistance. Apache-2.0; predecessor notices and bytes are retained. No independent human or proof-assistant verification is claimed.

Next: complete finite replay and independent witness audit, then mark ready if they pass. Continue searching for a new paid construction; this numerical gain does not resolve the decoder frame-realization problem.
