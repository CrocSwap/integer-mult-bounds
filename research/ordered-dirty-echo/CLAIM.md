# Ordered dirty echo under a scratch budget

- Track: recursive interfaces; OS-random assignment seed **56** (`secrets.randbelow(100)`).
- Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Claim time: 2026-10-13 04:42 UTC; expected finish: 05:17 UTC.
- Object: the ordered multiway dirty echo from PR #673 at
  `bfff94e78f0e75ebd2593e3cc7710ae5290e8be3`.
- Method: exact interval dynamic programming for ordered binary/ternary
  composition trees, with arbitrary positive integer leaf costs and a hard
  peak scratch-array budget. No factor permutation or new leaf operation.
- Deliverable: written complete cost recurrence, a small reproducible optimizer,
  exact witnesses, and independent nonlinear restoration/linear product checks.
- Stop rule: one package; finish experimentation by 05:07 UTC and reserve the
  remaining ten minutes for verification and handoff.

No pinned coordination issue existed at the initial GitHub check. This local
claim replaces a public reservation. Open PRs were checked through #709.

Three candidates considered: common Fourier boundary fusion (the existing
`fourier-boundary-fusion/REPORT.md` already supplies a strong obstruction),
Gaussian RHS boundary batching (#481 already supplies that construction), and
scratch-budgeted ordered dirty composition. The third was chosen because
#663 establishes the binary count and #689 optimizes balanced ternary uniform
costs, but #689 explicitly excludes unbalanced splits and unequal leaf costs.
Seed 56 selects the binary/ternary mixed-tree class (2 + 56 mod 3 = 4 is the
first scratch-budget probe); it is not used as evidence of novelty.

The selected conditional result is
`51110230636731/31250000000000000 = 0.001635527380375392`, as bound by
`certificates/selected-result.json` to #626 and its maintainer review.
This work does not change that record or `upstream/` and does not assert a
new multiplication exponent.

Prepared for Sagar Thakrar (@thakrarsagar), with substantial OpenAI Codex
assistance. Apache-2.0. Predecessor attribution and exact source pins will
accompany the completed result.

## Result update — 2026-10-13 04:57 UTC

Completed early and submitted as [PR #730](https://github.com/CrocSwap/integer-mult-bounds/pull/730).
The experiment stopped before the allotted cutoff; the final phase was devoted
to verification, overlap review and packaging. No pinned coordination issue
existed at the final check, so this is the single local result update.

The optimum within the stated all-dirty reserved-connector tree class is
464 calls at 27 factors / six borrowed arrays and 1,600 at 56 factors / eight
borrowed arrays. The improved balanced baseline from #689 uses 512 and 2,112
respectively. Four exact witnesses, a written optimality proof, complete
accounting and independent checks are packaged here. All 642 exhaustive
cost/budget cases, 207 tree shapes, 64 predecessor-word comparisons, four
mathematical mutations and two external package-corruption controls passed.
The selected-record check and standalone isolated replay passed. Full scope
and skipped checks are in README.md and VALIDATION.json; no new κ is claimed.

The final pre-submission refresh covered 547 open PRs through #728. #689
remained at `0dedef12f05f9a06faf9d4e1c8b1462c0e3bff3a`. #673 advanced to
`156f259b99723468cfdd2b5d47d0ba894f09bea7` with separate bit-role sharing
research; all three consumed source files remain unchanged from our pin.
Concurrent #714 (`efad8a40094ab453c0525efef0b0eff2a5d8b850`) uses one clean
root checkpoint with balanced binary children. Our borrowed arrays remain
arbitrary/dirty, and the entire ordered binary/ternary tree is optimized.
That clean-checkpoint result is a distinct storage contract and is not an
input to this contribution. The base and current upstream main remained
`66849e1475c930fd7732b1a0067ffee7e1e95f60` at the publication check.
