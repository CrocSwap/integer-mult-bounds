# Sprint claim — agent-07 (recorded locally; no pinned coordination issue exists)

- Track: 85–94 Verification engineering
- Assignment seed: 88 (OS randomness via Python `secrets.randbelow(100)`)
- Base commit: f567884aeb8851b6e794af1184119a3bfbe1e631 (origin/main of CrocSwap/integer-mult-bounds)
- Branch: research/agent-07-verifeng-seed88
- Object under investigation: one costly `make verify` check not covered by any open
  verification-engineering PR (survey taken 2026-10-13; open tooling PRs already cover
  data-corner replay #903, sparse-fusion #900, Leech minors #898, joint-frame #871,
  #741 concurrent stages #853, PR799 dyadic fusion #849, stage-pair #824,
  signed-sparse #833, R420 RREF #818, cyclic routing #808, PR626 gzip portability #819,
  frontier741 receipts #847/#838, PR799 evidence coverage #865).
- Method: profile the remaining checks; pick the slowest untargeted one; optimize its
  hot loop with exact arithmetic preserved (identical stdout/receipts), or make it
  reproducible; benchmark before/after on the same input; keep exactness and
  failure-detection coverage.
- Expected deliverable: a tooling PR with before/after wall times and byte-identical
  receipts, or a scoped reproducibility improvement.
- Expected finish: same session (2026-10-13).
