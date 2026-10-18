# Local Sprint Claim

Track: verification engineering. Assignment seed: **89**, from OS-random byte
189; accept bytes below 200 and reduce modulo 100 (uniform rejection sampling).
No reroll. No pinned coordination issue exists; GitHub's `pinnedIssues` query
returned an empty list. This is the local claim permitted by the donor prompt.

Base: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
Selected conditional kappa: `0.001672660197076918`, PR1094, retained bit PR589.
This experiment targets historical verification, not a new supplier or bound.

Object: Ross Richardson's incorporated PR917
(`085c32a25e2a09b029fa816195b97fa93d6f0788`), specifically `_normal_row` and
`_sum_rows` in `research/complex-ck-two-sided/independent.py`.
Method: exact integer cancellation on insertion and early termination of the
common two-adic valuation scan. Compare all four complete original/candidate
forward/backward programs, all 725 input columns, every prefix allowance,
endpoint and price. Run the complete unchanged predecessor verifier through an
opt-in adapter, plus arithmetic, aliasing, source and failure controls.
Expected artifact: a source-pinned opt-in replay adapter, deterministic evidence,
paired same-input benchmark, proof of the kernel invariants, registered replay.
Expected finish: 2026-10-14 01:02 UTC (2026-10-13 18:02 Pacific).
Stop rule: abandon acceleration if exact outputs differ or repeated paired
complete-stream benchmarks show no useful reduction. One implementation only.

Candidates considered (89 mod 3 selects the third): endpoint-matching census
(small historical domain and active PR1185/Discussion1403); ranked-word Boolean
basis replay (already integer-bitset based); CK sparse dyadic kernels (measured
bottleneck, selected). No mathematical negative search is reopened.

Overlap snapshot: 871 open PRs including drafts at 2026-10-14 00:24:21 UTC,
134 discussion/comment/reply records at 00:24:43 UTC, complete pagination for
both, plus local package notes and central ledger. Closest tools are PR1234
(rational frame normalization/complements), PR1217 (historical ternary frames),
PR1184 (complete emitted local audit), and PR1092 (Clifford input reuse).
None substitutes these dyadic row kernels in PR917. Their speedups are not
combined with this one. No matches establishes only observed non-overlap, not
novelty. Refresh before submission.

Prepared for Sricharan Vagvala (@theon199), with substantial OpenAI Codex
assistance for selection, implementation, analysis, verification and writing.
No independent human review. Apache-2.0; predecessor notices remain unchanged.

## Done

Result: [PR1426](https://github.com/CrocSwap/integer-mult-bounds/pull/1426),
implementation commit `50865bdac036f171b191c224e8a1e7f0ccafdadf`.
Five paired same-input runs per interpreter give 1.45x (Python 3.12) and 1.50x
(Python 3.14) integer-stage acceleration. Every one of 226,210 kernel returns
and all four complete receipts agree; the complete historical verifier retains
all 10+25 original controls. Python 3.12 registered replay and Python 3.14
optimized full verification pass. Scope released on 2026-10-14 at 00:43 UTC.
No new kappa, selected-frontier edit, full theorem proof or hosted-CI success
is claimed. Exact evidence, pins and next question are in the package.
