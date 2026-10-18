Conditional κ = **0.001676855229071321886206381217337893**, an absolute increase of **6.2381217337893E-23** over PR1377 (0.001676855229071321886144). **Certificate refinement only: the construction, scalar words, provider inventory, owners and paid profile are unchanged.** This is a tiny numerical improvement, not a new kernel or practical speedup.

**Verified locally and ready for review.** The complete portable finite-admission replay passed: retained-provider and parent admission, exact owner reconstruction, parent lift, strict T74 binding/emission/chronology/invoice, both exact moment engines, all 47 outer inequalities, admission/bit/controller/owner/geometry controls, and a separate closed-form bootstrap audit with five rejected mutants. The unchanged PR1297 native providers were explicitly source-bound reused; no fresh native replay or hosted CI success is claimed. Fresh receipts are `RESULT.json`, `evidence/VERIFIED-ASSEMBLY.json` and `evidence/INDEPENDENT-OUTER.json`; the assembler patch is included. Inherited receipts remain unchanged.

The three witness settings are frozen in `SPEC.json:outer_refinement`: 12 bootstrap iterations, eta = beta = 10^-40 with target backoff 10^-43, and a 10^-36 final κ grid. The inherited complex and bit endpoint grids and their native/surcharge models remain unchanged. Every bootstrap cutoff is recomputed from the exact gap. The next final κ grid point rejects for this witness. No optimality over all outer parameters is claimed.

The recurrence is a_(j+1) = (1-s)s + s a_j. Its closed form is a_j = s - (s-a_0)s^j; 0 < a_0 < s < 1 gives a finite increasing chain below s. This only changes witnesses to the inherited conditional bootstrap and outer lemmas, whose assumptions remain in force. Root endpoints, arithmetic engines and finite construction are inherited unchanged.

Reproduce complete admission with `python3 -B verify.py --work /absolute/new/work --base-native-from /bound/base/native --extra-native-from /bound/extra/native`, or omit the two reuse flags for fresh native supplier runs. The output directory must not exist and assertions must be enabled. `evidence/OUTER-DISCOVERY.json` is discovery evidence, not a completed new-package replay. `evidence/pr1377/` contains predecessor receipts; inherited `PRICE.json` and input/parent receipts are not new verification.

Conditional finite construction only. All-size compiler, common-label/mutable-source realization, whole-call hosting, precision/tape, exact recovery, analytic transfer, PR559 recurrence correction and PR589 bit H1-H5 assumptions remain. No unconditional theorem, full Lean certification, or global packing claim.

Credit Rohan Arun PR1319 (74-replica exact fill) and PR1297 (four cold kernels); Jeremy Kothe PR1377 (finer final grid), PR1019 and PR1274; Jeremy Diviney PR1193; Thomas DiFiore PR1148; Hao Yan and retained owner/controller lineage; eumemic and icekylinx/Zhihao Chen for the exact outer assembly; the PR547/548/559 recurrence and PR589 bit suppliers. Prepared by Rohan Arun with substantial OpenAI Codex assistance. Apache-2.0; predecessor notices and bytes are retained. No independent human or proof-assistant verification is claimed.

## Open next questions

- Find a new paid construction beyond this certificate-only gain. First step: realize the independently checked 864-read P111 decoder with legal frames and a complete invoice; seven rank-nine support sides remain unresolved.
- Determine whether a different centre path or rank profile beats the exact-fill inventory. The present result proves neither global optimality nor a barrier to those changes.


The independent audit command is `python3 -B check_outer_closed.py --assembly WORK/strict/ASSEMBLY.json --legacy evidence/pr1377/ASSEMBLY.json --spec SPEC.json --out NEW-OUTER-RECEIPT.json`. The primary replay took 196.3 seconds on Python 3.14.8; native caches were bound, not recomputed. `evidence/REPLAY-INPUT-MANIFEST.json` records the exact pre-release package tested, and `evidence/RELEASE-BINDING.json` checks that release edits changed only claim/README status and added evidence, not executable or construction inputs.
