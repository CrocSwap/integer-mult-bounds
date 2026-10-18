# Local sprint claim

- Track: structural decoder research. OS assignment seed: **40**, drawn with Python `secrets.randbelow(100)`.
- Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Started: 2026-10-13 04:36 UTC. Planned finish: 05:21 UTC; verification and handoff start by 05:10 UTC.
- Object: PR #669's punctured paired-hypercube identity, extended from target-local to arbitrary off-target proper stars. Focus on `k=4, p=5`, selected by seed 40, then a uniform certificate if justified.
- Hypothesis: off-target stars cannot reduce the three deletions needed to decode one retained target in this case.
- Method: exact binary linear algebra and explicit dual inconsistency certificates. Exhaust the bounded deletion domain, and investigate a combinatorial lower bound rather than another heuristic search.
- Deliverable: one scoped research note, reproducible standard-library verification, exact source pins, and negative controls. No new kappa or paid supplier claim.
- Three candidates considered: E8 root-flat punctures, asymmetric Hurwitz copy cost, and global proper-star punctures. PR #631 and PR #703 already cover the first two. PR #669 explicitly excludes off-target stars after puncturing, making the third distinct.
- Coordination: GitHub returned no pinned issues immediately before this claim. Open PR titles and relevant bodies through #709 were inspected. No separate reservation issue was opened.
- Predecessor: Sam Sung / @the-missionary-company, PR #669, head `308f1e6ec3bb0b6ec0584cf7bfe219addc219b1e`; its symmetric predecessor is Joel Pulikkan / GamingPuzzled's #231.
- Contributor: @thakrarsagar, with substantial OpenAI Codex assistance.

## Result update, 2026-10-13 04:52 UTC

Submitted [PR #725](https://github.com/CrocSwap/integer-mult-bounds/pull/725).
The global proper-star threshold is exactly three punctures for every
power-of-two `k>=2,p=k+1`. At `k=4,p=5`, the coefficient space has dimension
65 and exactly 67 minimum patterns through the recorded target; only four
work with target-local stars. All 67 literal decoder certificates and seven
controls pass. No new kappa or paid supplier is claimed.

The experiment finished before the planned deadline. Verification and packaging
began at 04:47 UTC, reserving more than the final quarter of the session.
Replays pass on Python 3.14.8, 3.12.15 and 3.11.15, including isolated optimized
mode. A separate agent reviewed the mathematics, implementation and source pins.
Selected-record integrity and staged whitespace checks pass. The repository-wide
suite and selected supplier cold replay were not repeated; no existing supplier
or selected certificate changes.

The final overlap scan covered 541 open PRs through #722. PR #669 remains at
the pinned head and is credited as the predecessor. PR #715 studies a distinct
E8 mixed-port geometry, and #717's decoder floors concern complex E8 ports.
Neither overlaps this paired-hypercube result. Main remains at the recorded
base. A repeated pinned-issue query returned no coordination issue, so this is
the single local claim result update.
