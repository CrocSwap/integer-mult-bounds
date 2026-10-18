# Seed 86 verification engineering claim

- Assignment: OS randomness (`secrets.randbelow(100)`) returned **86** at
  2026-10-13 10:29:34 UTC; track 85–94, verification engineering.
- Exact base: `f567884aeb8851b6e794af1184119a3bfbe1e631` (fetched upstream main).
- Object: the five historical Leech lattice minor replays in
  `scripts/experiments/affine_vector_screens.py`, using every recorded row and
  column in `scripts/experiments/affine_vector_witnesses.json`.
- Method: replace pairwise Python dot products by carry-safe exact integer
  lanes; compare full packed row streams, ranks and certificates on identical
  inputs. Preserve validation and rejection checks; no probabilistic ranks.
- Deliverable: opt-in source-pinned accelerator, before/after benchmark,
  complete equivalence checks and negative controls. No new kappa or theorem.
- Expected finish: 2026-10-13 11:10 UTC (22:10 Australia/Sydney).

Three candidates were (0) memoizing repeated subset-core interval evaluations,
(1) accelerating the coded-carry exhaustive affine-agreement control, and
(2) reconstructing the five Leech minors with exact integer lanes. `86 % 3 = 2`
selects the last after excluding occupied recent tooling targets. Seed 86 also
fixes the supplemental generated test cases; it does not change the five
historical fixtures or their complete coverage.

The selected record was followed to the PR799 X4 construction and maintainer
review (conditional kappa 0.001661634653669567, with PR589/555). The PR ledger,
contribution guidance and historical affine-vector negative-result scope were
read. The latest 100 open PRs through #891 and all-state tooling, subset,
affine, coded-tooling, Leech-tooling and `affine_vector_screens` searches were
checked. #752 accelerates quadratic-affine minors and #778 single-intersection
Gram matrices: related integer-packing techniques, distinct matrices and
checks. #849 concerns dyadic X4 arithmetic and #871 historical joint-frame
rank checks. No duplicate Leech-minor accelerator was found.

Only issue #650 (request to enable Discussions) was open and had no comments;
no pinned sprint coordination issue was available. Claim recorded locally per
the sprint instructions. No delegated workers.

Contributor: CubeJerry, with substantial OpenAI Codex assistance. Apache-2.0.

## Result — 2026-10-13 10:50 UTC

Completed the opt-in accelerator: all 5,927 original Leech rows (7,531,037
entries) and the complete nine-screen certificate agree exactly. Three final
alternating fresh-process pairs measured 18.946560s to 8.988220s median,
**2.107932x** on Linux/CPython 3.12.14. Eleven test groups, all three unchanged
predecessor tests in both modes, minimal offline relocation, selected-record
integrity and its five tests pass. No new kappa is claimed.

Result package and reproducible evidence:
[leech-minor-byte-lanes](https://github.com/CubeJerry/integer-mult-bounds/tree/tooling/seed86-exact-verification/research/leech-minor-byte-lanes).

Final metadata refresh covered new PRs through #894 and all-state Leech and
affine-checker searches. No overlapping accelerator was found. DominikScholz's
#598 (head `615ca6f06fdea0c50dbef733370c47349e25c555`) studies different
Leech/Turyn constructions and fitting bounds; those negative searches are not
reopened here. The pinned-issues GraphQL query returned no coordination issue.
Upstream main remains the recorded base. All 41 retained input hashes also
match the base Git objects. The branch is ready for one focused tooling PR.
