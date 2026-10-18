# Task card — agent-24 (local, pre-computation)

Task ID / proposed scope key: `bit-new-register-model` / `7084092dd726e7ba1f2f`,
refined to `coordinate-CNOT/GL2(F2)/four-SWAP/r=4/balanced-5a5b-at-q=10/J3-augmentation-layer`.

Base commit: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`
(selected-record SHA-256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`,
priority revision 3). Branch `research/agent-24-four-swap-balanced-cd67986e`.
Chooser nonce `cd67986ec4d736b6ed683332001aecde`, track `bit-mechanisms`.

Exact predecessor and dependency heads (read-only, no files imported):
- https://github.com/CrocSwap/integer-mult-bounds/pull/1705 head `ad6b7d641b3e8576a95add7981fa75b6a8278fbc`
  (four-SWAP r=4: q in {8,10,12}), package `research/four-swap-r4-cnot/` on its branch;
- commdata2338 https://github.com/CrocSwap/integer-mult-bounds/pull/1414 and
  https://github.com/CrocSwap/integer-mult-bounds/pull/1491 (model, sign-quotient parity, three-SWAP finite result);
- Gareth Davidson https://github.com/CrocSwap/integer-mult-bounds/pull/1333 (free-scalar normalization);
- Cinna Davis https://github.com/CrocSwap/integer-mult-bounds/pull/1541 (arbitrary-workspace three-SWAP theorem);
- local `research/coordinate-cnot-register-bound/` (two-SWAP all-register theorem, PROOF.md) — model reference.

Concrete object and question:
In the formal group-algebra register model `R = F2[GL_2(F2)]` on exactly `r = 4` registers,
paid calls `I + ([g]+1) u v^T` with `g in {a,b}` the two coordinate CNOTs of `GL_2(F2)`
(`a = [[1,1],[0,1]]`, `b = [[1,0],[1,1]]`, `S = aba = bab = [[0,1],[1,0]]`), `v^T u = 1`
binary rank-one idempotents, free scalar `GL_4(F2)` mixing between calls, all four registers
arbitrary dirty inputs restored exactly: can the complete formal boundary
`T = diag([S],[S],[S],[S])` be realized by a **10-call word with exactly 5 a-labels and
5 b-labels** (the balanced profile)?

Scope status: refined (card `bit-new-register-model`, allowed variation "fixed larger register
count"; the concrete residual of the four-SWAP r=4 line).

Existing restriction being changed / exact claim being audited:
PR1705 narrows the four-SWAP r=4 minimum to `q in {8,10,12}` and leaves `q = 10` open. The live
label-saturation claim (discussions/1715, Ross Richardson, expires 2026-10-14 09:35 UTC) would
leave exactly the balanced (5 a, 5 b) ten-call profile as the only sub-12 candidate, and states
"The ten-call balanced case is explicitly outside this session." The handoff
(discussions/1166#discussioncomment-18918391) names "derive the `J^2`-coefficient-layer bound in
`F_2[G]/J^3` (`sum E_i + sum_{i<j} E_i E_j = T - I`) to exclude `q = 10` in writing" as a
smallest useful next task.

Method; explicit parameter ranges/candidate alphabet:
1. Exact `F2[S3]` algebra with bit-linear algebra (stdlib only): augmentation ideal `J`, `J^2`,
   `J^3`, quotient `R/J^3`; verify `([a]+1)^2 = ([b]+1)^2 = 0` (a, b involutions).
2. Derive the word expansion `prod(1+eps_i) = 1 + sum eps_i + sum_{i<j} eps_i eps_j` exactly in
   `(R/J^3) M_r` and record it as L1/L2 necessary equations (label-order aware; same-label pairs
   vanish by involution).
3. Positive controls: the exact 3-call word at r=1, 6-call word at r=2, 9-call word at r=3 and the
   four-disjoint-`aba` 12-call word at r=4 must satisfy the layer equations and the full formal
   equation. Negative controls: mutated words/targets must fail.
4. Main bounded search: decide feasibility of the balanced (5,5) layer system at r=4 over the
   120 binary rank-one idempotents `u v^T` (`v^T u = 1`), all 252 interleavings, seeded and
   time-capped. Any hit is replayed at full formal level (`M_4(F2[G])`, 96-bit states) as a
   candidate; if no hit, report the exact searched domain as a scoped search failure.

Nearest overlapping PRs and why this adds something:
PR1705 (same model/target) excludes q in {2,4,6} by a natural-image census and leaves q = 10
open; this work isolates the balanced (5,5) residual at the augmentation layer, which PR1705 does
not decide and discussion 1715 explicitly excludes from its session. It is not a re-run of any
census: the layer equations are a written algebraic reduction, and the search domain is the
balanced profile only.

Optimistic full cost budget; required observable improvement:
The priced budget is the paid-call bill: a balanced 10-call word would beat the 12-call direct
bill (`q = 10 < 12`); required observable improvement is either an exact certificate that the
balanced (5,5) layer system is infeasible (then, with PR1705 and any saturation result, the
four-SWAP minimum is narrowed further) or an explicit layer-satisfying balanced assignment with
its exact word-level status, i.e. a precise obstruction for this route.

Success evidence; falsification test; time/compute cap:
Success = exact-arithmetic certificate (`verify.py` PASS with counts) plus written lemmas.
Falsification of the layer route = a balanced (5,5) assignment satisfying L1/L2 found.
Controls above falsify the machinery if they fail. Search cap: one bounded seeded pass
(~10-20 min wall), one bounded pivot maximum.

Predecessor authors; intended artifact and reproduction command:
Credit Aaron Wang, with help from opencode; predecessors as listed above (commdata2338, Gareth
Davidson, Cinna Davis, Aaron Wang PR1705, Ross Richardson discussion 1715 as concurrent).
Artifact: `research/four-swap-balanced-j3-layer/` (README, TASK.json, verify.py, exact certificate).
Reproduce: `python3 -B research/four-swap-balanced-j3-layer/verify.py` (expected PASS in seconds
to a few minutes; exact stdlib arithmetic, no network).
