# Local sprint claim

- Track: verification engineering; OS-random assignment seed **94** (`secrets.randbelow(100)`), drawn 2026-10-13 04:35:57 UTC.
- Upstream base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Object: rational row reduction used twice per nonempty frame by PR543's `code/xcheck.py`, including its nullspace construction.
- Method: adapt PR367's exact primitive-integer elimination to the list-of-Fractions plus pivot API; no geometry cache. Compare every R420 frame's exact RREF/nullspace, the full checker and its unchanged 9-negative/1-positive harness. Use seed 94 for supplemental rational, singular and row-permuted matrix coverage.
- Deliverable: isolated opt-in adapter, pinned predecessor kernel, exact equivalence argument, rejection controls and same-input alternating A/B timings; no new kappa.
- Expected finish: 2026-10-13 05:15 UTC. Final quarter reserved for verification and handoff.

Three narrow candidates were examined: (1) cache the R420 geometry across mutation checks; (2) share exact leading Gram determinants; (3) replace cold R420 Fraction row reduction. #709 already covers (1), #707 covers (2). Selected (3) reuses, rather than claims novelty for, Aman's PR367 arithmetic. That PR targets PR364 rank/canonical keys; this contribution supplies the missing R420 pivot/nullspace adapter and complete selected-bit checker evidence. #662, #667 and #672 address other kernels. None of those optional optimizations is composed here.

Initial overlap review read the 100 most recently updated open PR descriptions through #709 and searched all PRs for `rref`, `fraction-free` and `bitset`. PR367's full description/source was read. The review ledger and selected #626/#543 sources were followed; larger pending titles were not treated as accepted. No closed mathematical search is reopened.

No pinned coordination issue exists: the pinned-issue query returned none; the only open issue is #650 requesting Discussions, with no comments. Claim therefore recorded locally. Direct Git transport is unavailable in this environment; source files were fetched by the GitHub connector at exact commits, with blob IDs verified, into an isolated branch. The local source-subset snapshot commit is not represented as the upstream commit.

Prepared for @MrPink604 with substantial OpenAI Codex assistance, Apache-2.0.

## Result (single claim update)

Completed: [R420 RREF/nullspace adapter and evidence](README.md), no new κ.
Seven alternating fresh-process pairs give 2.70× for the complete exact checker
and 3.03× for the unchanged mutation harness; all paired outputs agree byte for
byte. Exact 672-frame, 1,090-matrix and negative-control coverage passed. See
[validation](VALIDATION.md) and [raw timing evidence](evidence/benchmark.json).
Submission overlap refresh through #732 found no duplicate; #367 is reused and
credited, while #707/#709/#721/#727 address different mechanisms. Main is unchanged.
No pinned issue exists. An initial clean patch and offline replay archive were
handed off while a writable fork was unavailable. The user subsequently created
the MrPink604 fork, enabling publication of this same verified contribution.
