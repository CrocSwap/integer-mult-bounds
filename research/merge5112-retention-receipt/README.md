# Post-merge retention receipt: the nine PRs integrated at 51122344

**Research consolidation (credit and provenance). No new kappa; no disposition,
ledger, closure or frontier change.** Prepared by **Aaron Wang**, with help from
opencode (substantial AI assistance; no independent human review claimed).
Apache-2.0.

Card `overlap-receipt` (consolidation track, scope key `757723e3fd38f20fa774`,
chooser OS-draw nonce `66879550e1fc7c124e80fcde11281b4d`, priority revision 3),
**refined** to one existing integration receipt: the maintainer merge
[`51122344`](https://github.com/CrocSwap/integer-mult-bounds/commit/51122344de9382e784c7f89953456d8cd55513ef)
(2026-10-14, "Integrate reviewed research PRs #1805, #1806, #1808, #1810, #1811,
#1812, #1814, #1815, #1827"). Base main `51122344de9382e784c7f89953456d8cd55513ef`;
its first parent (pre-merge main) is `d33f15be91438e3de512fa544c3f5a7cb832588f`.

## What was audited

The existing receipt under audit is the scoped review
[`research/community-efficient800-audit/DISPOSITIONS.json`](../community-efficient800-audit/DISPOSITIONS.json)
plus the merge commit message. That review predates the merge: it records every
one of the nine PRs with `disposition: partially_reviewed` and
`github_state: OPEN`, and names each PR's `integration_location`. Whether the
merged tree actually retained each reviewed head's content byte-for-byte was
therefore open at selection time. This receipt answers exactly that, and nothing
else.

## Method

All facts except the GitHub-observed fields below are re-derived offline from
the local Git object store by [verify.py](verify.py):

1. The parents of the merge commit must be exactly pre-merge main plus the nine
   reviewed heads recorded in `DISPOSITIONS.json` (a changed head or an extra
   parent fails the check).
2. For each reviewed head, its own changed-path set is the three-dot diff from
   its merge base with pre-merge main (`git diff --name-status BASE...head`), so
   paths where the head merely lags main are not counted as its changes.
3. Each changed path's Git blob at the head must equal its blob in the merge
   tree (`retained-identical`). Modified or missing blobs are reported
   separately, never folded into "retained".
4. GitHub observations (author, title, state, `mergedAt`) were pinned on
   2026-10-14 via `gh pr view`; the offline verifier does not re-check them.

[RECEIPT.json](RECEIPT.json) holds the per-PR records with every path and blob.
Seven in-memory rejection controls (corrupted head blob, corrupted merge blob,
wrong verdict, dropped path, fabricated path, false changed-head flag, wrong
totals) must all fail; the identity comparison against fresh Git facts is the
positive fixture. [SOURCES.json](SOURCES.json) pins the scoped review and the
provenance files by Git blob and SHA256.

## Result

All nine reviewed heads are retained completely and identically: **77 of 77**
changed paths carry the same Git blob in the merge tree as at the reviewed
head; 0 modified, 0 missing, 0 deletions by any of the nine PRs. No head
changed since review (`headRefOid` equals the recorded `reviewed_head` for all
nine, and each is a merge parent). Every changed path lies inside the PR's
recorded `integration_location`. All nine authors appear in
[CONTRIBUTORS.md](../../CONTRIBUTORS.md).

| PR | Author | Integration location | Changed paths | Retained identical |
|---|---|---|---:|---:|
| [#1805](https://github.com/CrocSwap/integer-mult-bounds/pull/1805) | VictorLiwentao | research/h2sem-copyshare-priced | 10 | 10 |
| [#1806](https://github.com/CrocSwap/integer-mult-bounds/pull/1806) | mtpsl | research/r439-abc-hosted-invoice | 9 | 9 |
| [#1808](https://github.com/CrocSwap/integer-mult-bounds/pull/1808) | JosieElliston | research/plane-port-copy-budgets | 6 | 6 |
| [#1810](https://github.com/CrocSwap/integer-mult-bounds/pull/1810) | RossRichardson | research/r439-dirty-workspace-frame-bound | 8 | 8 |
| [#1811](https://github.com/CrocSwap/integer-mult-bounds/pull/1811) | 1337isnot1337 | research/five-source-parity-hyperplanes-seed595e | 12 | 12 |
| [#1812](https://github.com/CrocSwap/integer-mult-bounds/pull/1812) | nedveder | research/two-connector-eight-transfer-threshold | 8 | 8 |
| [#1814](https://github.com/CrocSwap/integer-mult-bounds/pull/1814) | 1337isnot1337 | research/complex-gather-child-seed7a6d | 11 | 11 |
| [#1815](https://github.com/CrocSwap/integer-mult-bounds/pull/1815) | jmbarrancoml | research/polarized-p112-code-bound | 5 | 5 |
| [#1827](https://github.com/CrocSwap/integer-mult-bounds/pull/1827) | mightyOil | research/p112-joint-support-loss-audit | 8 | 8 |

At the pinned 2026-10-14 snapshot, the nine
[docs/research/pr-ledger.md](../../docs/research/pr-ledger.md) rows read
"partially reviewed" and cite the pre-merge scoped review. Later maintainer checkpoints update dispositions independently; this historical
receipt should not be read as the current queue status.

## Limits

Git blob identity authenticates file content, not the separate Git mode. The
package checker does not compare modes; the maintainer supplemental retention
check records mode equality separately. This
is not a ZIP-container or Windows-checkout byte comparison. Nothing here
re-reviews the nine packages' mathematics, re-runs their checkers, or certifies
their claims. The GitHub-observed fields are pinned observations and may drift
after 2026-10-14. No disposition is changed, no PR closure is requested, and
the selected record (`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`)
is untouched.

## Reproduce

From the repository root (needs Git history; standard library only):

```sh
python3.12 scripts/research_package.py --package research/merge5112-retention-receipt
python3.12 scripts/research_package.py --package research/merge5112-retention-receipt --check-only
```

## Open next questions

1. Have later maintainer ledger rows moved from "partially reviewed" to "incorporated"
   now that merge 51122344 retains their exact reviewed heads? It matters
   because the ledger is the central review entry point and understated rows
   make reviewers re-scan retained work. First step: a maintainer updates the
   rows citing this receipt. Blocked on: disposition changes are maintainer
   actions.
2. Do the nine contributed packages' own checkers still pass on the merged
   tree? Blob identity is content retention, not green replays. First step: run
   each package's `verify.py` or registered replay under Python 3.12 from a
   merge-5112 checkout. Blocked on: bounded time for the longer replays.

## Credit

The nine packages and their claims belong to their PR authors: VictorLiwentao,
mtpsl, Josie Elliston (JosieElliston), Ross Richardson (RossRichardson), Cinna
Davis (1337isnot1337), nedveder, jmbarrancoml and Philipp (mightyOil). The
scoped review being audited is the maintainer's
`research/community-efficient800-audit` (with its own merge, integrity and
ledger-check receipts). The receipt style follows the PR148 source-retention
receipt (https://github.com/CrocSwap/integer-mult-bounds/pull/1572) and the
fourth100 family receipt (package
`research/pr636-family-witness-manifest-receipt/`, recorded in the handoffs
thread https://github.com/CrocSwap/integer-mult-bounds/discussions/1166), which
audited different
PR sets. Concurrent mathematical work that names PR1805 as a predecessor (an
independent PR1805 audit by Ross Richardson, and a PR1805/PR1062 composition
claim) addresses mechanisms, not merge retention, and is not duplicated here.
