# Notices
- Kernel principle and exact replay: chafreaky, PR #417 (shared-donor response kernel; the earlier implementation had substantial Anthropic
  Claude assistance) and PR #443 (replica kernel with a checked replication count, residual isometries): used unchanged from `e8-r740-replica32`
  (`replica_kernel.py`, `e8core.py`, `stages.py`, `iface386.py`).
- PR #370 (Dylan Crow, utcorvusvolat-dotcom, with Anthropic Claude assistance): E8 bit format, producer, independent checkers; PR #436 (eumemic):
  R740 word, elimination reuse and retiming; PR #434 (rohanarun) and PR #440/#441 (eumemic): primitive retiming composed with response kernels;
  PR #435 (rohanarun): mixed-width residual banks. All used unchanged through `e8-r740-replica32/parent436`.
- PR #442 (DaysSky) idle-axis whole-residual hosting and PR #451/#454 (chafreaky) whole-residual rule: cited and verified unchanged
  (`idle-axis-hosting`); PR #386 and #425 (Zhihao Chen / jacklightChen) compressed nine-stage geometry; PR #433 (icekylinx) split centres.
- Bit supplier lineage of this package: the R715 word, frame-pair D4 sums, cancelling re-expressions, the kernel rebuild and target mixing generalised
  to chained receivers (PR #463, `e8-r715-eleven-stage-whole`, used unchanged) and PR #450's target mixing: DreamingOfClouds with Claude Opus 5.5
  (Anthropic), via Claude Code. PR #458 (chafreaky, with OpenAI Codex assistance): paid residual adapters, used unchanged
  (`e8-complex-adapted-kernel`). PR #460 (rohanarun, with OpenAI Codex assistance): composition and verifier structure (`compose.py`, `verify.py`
  follow `e8-r715-paid-complex`, itself after #460).
- Frontier context cited in the comparison: #465 (Srikrishnabalaji), #467, #470 (rohanarun: retimed kernel and reordered R715 deliveries on the
  R715 word), #471, #476, #478 (Dugongue), #472, #473. The numbers quoted for #472, #473 (as updated on Oct 11, κ = 1.295630·10⁻³) and #478 are those
  reported on their threads; nothing of theirs is used here.
- New in this package (`code/`, `data/`, `compose.py`, `verify.py`): the width-rule check, the proved pivot ceiling and its analysis, the exact pivot maximum (`code/exact_pivots.py`: min-sum-rank formulation, matroid component and block decomposition, exhaustive search with optimistic completion), the seeded
  annealing selection (self-contained xorshift64* generator), the kernel build from an explicit selection, the CP-SAT whole-residual hosting
  re-solve and the pivot-count scan: DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.
