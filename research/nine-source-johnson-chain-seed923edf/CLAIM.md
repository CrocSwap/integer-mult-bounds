# Cycle 32 local research claim

**Status:** RESULT SUBMITTED as [PR #2296](https://github.com/CrocSwap/integer-mult-bounds/pull/2296).
The PR was open and mergeable at head `b4af93f238e69ccf000eb9e90030be4c01cda391`
against base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2` at the initial
submission check; hosted checks were queued. The subsequent handoff metadata
update advanced the branch; consult the PR for its current head and checks. The
public Discussion claim remains local-only: the
authenticated GraphQL overlap refresh hung and was stopped after about two
minutes, the final pre-submission retry produced no output before timing out
after 50 seconds at 03:56 UTC on 2026-10-15, and a prior direct REST Discussions
comment attempt returned 404. No public claim was posted.

- **Track / task / seed:** `recursive-interfaces` / `connector-alphabet-change` /
  `923edf31ad6e8cfdc58bb11a6c6d6b3d`.
- **Exact base:** `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.
- **Catalogue / selected record:** revision 4; catalogue SHA256
  `d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7`; selected
  record SHA256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- **Question:** In the established singleton F2 dirty-connector alphabet, can
  five separate dirty outputs with supports
  `{01234, 01235, 01256, 01567, 05678}` be computed with nine read-only
  sources at the complete-call floor? These five 5-subsets form a path in
  `J(9,5)`, each step replacing one source, and their union is all nine
  sources.
- **Changed scope:** The selector card asks to add one connector operation.
  This investigation adds no operation; it studies one explicit sparse
  output-support family under the existing alphabet. It is a construction,
  not a repeat of Cycle 31's eight-source full weight-four two-sweep census.
- **Candidate screen:** The two-unpaid-coordinate coverage-law question is
  already claimed in Discussion #1587. Centre-path hosting is claimed in
  #1516 through 05:00 UTC, with older related nonadjacent-path records #1963
  and #2058. The joint-query
  lane has open PRs #2153 and #2268, including the immediately preceding
  Cycle 30 contribution. The general connector lane has active GF(4) and
  seven-source claims plus open alphabet/path PRs; this claim narrows it to a
  different positive n=9, weight-five support chain with no new operation.
- **Method / domain:** Use the source walk `0 → S1 → S2 → S3 → S4 → S5 → 0`,
  toggle each symmetric difference, and read each `A_i` once at `q=0` and once
  at `q=S_i`. Charge all B and A calls. Exhaust all `2^9` source assignments,
  dirty connector bits and `2^5` dirty-output vectors. Stop after exact replay,
  the lower-bound proof and the listed failure controls; no search over
  unrelated support families.
- **Favorable screen:** Optimistic floor and proposed schedule are both
  `2*9 + 2*5 = 28` complete calls. Five independent restored row stars cost
  `5*(2*5+2)=60`. The intended saving is 32 calls in this abstract interface;
  under stable per-call source prices `c_j`, the weighted saving is exactly
  `2*sum_j (d_j-1)c_j`, where `d=(5,4,3,2,1,4,3,2,1)`; A-call prices cancel.
  Position-dependent transitions and concrete supplier placement remain
  unpriced, so no recursive supplier or kappa is claimed.
- **Expected evidence:** A standalone verifier, exact source/readout word,
  arbitrary dirty-state replay, lower-bound argument, negative controls,
  complete provenance pins, and a focused package PR. Submitted as PR #2296;
  hosted checks were queued when checked.
- **Relevant work and distinction:** Open PR #2208 (head
  `28480ef4fdb4caeab89765ea56595bf1f6f37688`) develops all-word two-root
  dirty-connector bounds and an exact minimum-read compiler for supplied source
  walks over as many as 511 outputs. It is adjacent source-walk work, but uses
  a two-root framed interface and does not present this one-connector, five-
  mask Johnson chain or its 28-call floor. PR #2271 (head
  `95fd439596f72575d3869277c2d01aca1ca6ab6a`) is a 12-row bit-register Gray
  tour through three masks, not this nine-source recursive B/A interface.
  PR #2283 (head `21145202e9a27cd9b18ffc7e23383cc83461c4a0`) is Cycle 31's
  negative result for the full n=8 weight-four shell under two complete
  sweeps. PR #2229 covers n=7 weights 1--3; PR #2266 changes to GF(4) for two
  sources. Active neighboring claims #2262 (GF(4)) and #2275 (seven-source
  paired-call roots) do not use this mask family. Targeted live PR searches at
  04:00 UTC found no `J(9,5)`, exact five-mask or "nine-source Johnson-chain"
  match. The complete cached snapshot covered 511 open PRs and 990 Discussions
  (PR data 03:42 UTC; Discussion data 03:26 UTC, 2026-10-15).
- **Expiry:** The local claim is released on completion; the recorded planning
  expiry was 2026-10-15 05:45 UTC.

The selected conditional result is `836330098538459/500000000000000000` at
this base, reviewed in `docs/research/community-batch1099-review.md`; the
selected assembly and source manifest are pinned in `SOURCES.json`. The
selected supplier reproduction is `make frontier1094-verify`; it is not part
of this connector-level experiment.
