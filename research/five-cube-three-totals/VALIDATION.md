# Validation and handoff evidence

Research base: `c0e3631dc24e3c24a861f7d3d79e0608481cccec`.
Validation date: 2026-10-13 UTC (2026-10-14 in Australia/Melbourne).
Platform: macOS arm64. Python standard library only; no external solver,
native compiler, numerical rank tolerance or network dependency in replay.

Completed checks:

- CPython **3.14.6**: primary full replay, separate Fraction oracle and all
  **nine** package test groups pass in isolated optimized mode (`-I -O -B`).
- CPython **3.9.6**: both full checkers and all nine package test groups
  pass with the same receipts, including offline minimal-tree relocation.
- Primary and independent JSON receipts regenerate **byte identically**.
  No compressed-container identity is used.
- The primary census exhausts 65,535 nonempty subsets of the fixed
  coordinate-1-zero slice: 510 attain total 32. Price histogram and exact
  ordered-row digest are committed. This does not exhaust all 2^32 masks;
  the written rank argument covers that entire domain.
- The separate Fraction implementation reconstructs G from literal
  coordinate-set intersections, confirms all 189 parity/affine pairing
  ranks, checks all 433 reduced affine templates and 319 dense masks, and
  checks literal decoder equations for all 131,068 equality masks.
  Representatives of every equality cardinality receive dense rank checks.
- Ten primary mathematical controls reject dropped/zero terms, a
  coefficient error, invalid/Boolean masks, broken clique/cross geometry,
  missing rank charges and falsely affine classification. The coefficient
  control preserves every diagonal entry and fails off-diagonal exactness.
- Nine package groups include 150 independent rank-oracle fixtures,
  positive repeated-reader and transposed witnesses, the sparse-Gram
  scope boundary, source/manifest corruption and deletion, a false floor,
  altered Gram certificate, omitted sample coverage, typed receipt
  comparison and read-only replay outside the repository in a path with spaces.
- Seven source Git blobs match the exact research base. The three retained
  PR1046 files and PR958 proof also match their explicit predecessor heads.
  The source manifest's own SHA256 is pinned in the primary checker.
- `python3 -I -B scripts/verify_selected_result.py` and all five tests in
  `tests/test_selected_result.py` pass. The selected result remains
  conditional PR1094, `836330098538459/500000000000000000` at the validation
  refresh. Source and selected files are not changed by this contribution.

Verification and packaging began before the planned final-quarter deadline
(19:46:30 UTC in a 30-minute envelope ending at 19:54 UTC). The claim records
scope, time, seed, three candidates and the completed handoff.

The live overlap refresh inspected recent PRs through #1176, plus targeted
five-cube/non-affine/three-total searches. The only matching predecessor was
PR1046 at `7cadcb0a2fc71fdedc0066704dec3fec58c2ca2c`; it is credited explicitly.
The submission refresh also read the newly introduced discussion board: #1163, #1166 and #1167 were the complete three-thread inventory, all with no comments or overlapping claims. No pinned coordination issue existed; the original local claim was retained as instructed, with no separate reservation issue.
Upstream had neither `codex` nor `codex-automation` labels available.

Unrun/unclaimed: full repository artifact regeneration, selected supplier
cold replay, native physical word/phase/hosting checks, Lean, all-size
compiler, precision/tape, analytic transfer and independent human review.
The added path-scoped Linux workflow runs the full package tests; hosted
CI status is separate and no hosted pass is claimed by this local note.
Only the new research package and its focused workflow are submitted.

Submission base: `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`. The package is byte-identical before and after rebasing onto that refreshed main, and all seven input Git blobs are unchanged there. Selected-record integrity and its five tests pass after rebase. Implementation commit: `201c15fa7ed522396d3f4ebfb0eeabae7060f9bb`. Published for review as [PR1177](https://github.com/CrocSwap/integer-mult-bounds/pull/1177); subsequent closeout changes only this note and CLAIM.json.
