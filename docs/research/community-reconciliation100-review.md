# Historical reconciliation: 100 open PRs, October 13, 2026

This round reconciles the frozen 100-PR inventory spanning #2–#189 against
published main `49b3157d1d89adcef16df8be98445451672be5ba`. It does **not**
claim 100 completed mathematical reviews. Three dispositions are complete;
97 remain open with explicit content/dependency tasks. The selected conditional
κ and its inherited assumptions are unchanged.

[Exact-head decisions](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) ·
[Next actions](../../research/pr-reconciliation100-20261013/NEXT-ACTIONS.json) ·
[Coverage and reproduction](../../research/pr-reconciliation100-20261013/README.md)

## Completed dispositions

| PR | Contributor | Disposition and retained evidence |
|---|---|---|
| [#3](https://github.com/CrocSwap/integer-mult-bounds/pull/3) | eumemic | Historical compressed complex circuit: the core code, construction and certificate were already retained. Restore the original exact tests, preserve the full 14-file submitted packet, and reconcile the old release wrappers without replacing the selected result. |
| [#90](https://github.com/CrocSwap/integer-mult-bounds/pull/90) | Anas Khan / anxkhn | Documentation intent incorporated through current selected-record lookup. Fix the reproduction guide's newly stale #596 heading, identify the PR39 release as historical, and retain contributor credit. The old round-two links are superseded. |
| [#183](https://github.com/CrocSwap/integer-mult-bounds/pull/183) | Romain Hédouin / romainhedouin | Import exact assembly-ceiling module and tests unchanged. Import the note with a historical-status banner. All three submitted files are covered. Arithmetic tooling only, no new κ. |

For #3, ten exact tests pass on Python 3.12, including the full retained
certificate regeneration, complete side-map/frame checks in the generator,
small-size basis-vector and arbitrary-dirty invocation checks, both directions,
parameter failures and unchanged counts. The core files match the submitted Git
blobs. Its source proof uses disjoint shared sums, nondegenerate nested binary
labels, a missing outside point to avoid alternating injection residuals,
and cancellation of arbitrary dirty values in the forward/inverse schedule.
The three-stage bank exchange, transfer, precision and compact-control interfaces
retain the historical hypotheses. This is not a new proof of the upstream
multiplier or approval of later changes in other PRs.

The #3 archive preserves every original changed file, including the PDF and
independent patch. Original README/status/reproduction/build wrappers describe
a historical release and are retained in that archive, rather than reinstalling
their old frontier claims. Existing producer verification still includes the
historical complex generator. The restored test module participates in the
normal isolated-test discovery. No PDF rebuild or full Linux suite is claimed
for this metadata/historical-tooling integration.

For #183, all 22 exact tests pass on Python 3.12. They compare both retained
assembly variants at the supplied certificates and rational grids, test strict
boundaries, individual failures and incomplete bridge inputs, and check the
coverage identities. The short argument is reviewed in its stated domain:
`0 < a < (1-beta)b < b < 1/32`, `0 < eta < 1/2`. With
`q=a(1-2eta)`, the original and balanced denominators are `1+q(2+eta)` and
`1+q`; the minimum margin is `q(1-eta)/D`. Positive reduced slacks imply the
remaining reference inequalities through the listed identities and range bounds.
This is a scoped arithmetic reduction, not formal verification. The imposed
`1/32` range is **not a universal multiplication barrier**; see the
[domain audit](assembly-domain-audit.md). The preserved source credits RaD,
James Chang, Zhihao Chen and icekylinx, and retains Claude assistance disclosure.

## What the 100-PR reconciliation found

All 100 current heads still match the prepared inventory and were open/non-draft
at refresh. GitHub's changed-file count is independently matched for every PR.
The full original diffs contain **31,796 file entries**:

- 2,593 exactly match the same path in the pinned main tree.
- 7,605 match a file elsewhere in that tree.
- 967 match a member of the previously checked PR181 source archive; those
  matches alone do not establish active incorporation or executable mode.
- 20,631 have no such byte/mode match, representing **2,605 distinct contents**.

The prepared screen had compared each head with a merge base against current
main. GitHub's recorded PR bases expose additional paths for 26 submissions:
later incorporation can change the merge base against main. This round corrects
the full file inventory before any disposition. The first 29,658-path screen
was not used as complete closure evidence.

Most of the apparent volume comes from nested frame-compiler copies and stacked
construction dependencies. The shared-content index records *every contextual
occurrence*, so a reviewer can compare a source once and then check how each
PR uses it. Identical content is not itself an equivalence proof for different
inputs, frames, schedules or theorem claims. A later stronger κ likewise does
not dispose of an earlier alternative construction or research note.

## Remaining review work

The other 97 PRs remain `partially_reviewed`, **not** “waiting for author” or
“fully incorporated.” Their exact residual paths and individually named next
steps are in the linked decision files. Preserve existing scoped evidence;
do not repeat a complete cold replay unless its sources, inputs or contract
have changed. These are maintainer reconciliation tasks, not requests that
contributors rewrite their historical work.

The next dependency batches are early circuit/geometry packages; source-frame
and two-stage dependencies; matching/producer variants; frame compilers;
deferred words; sharing/reuse; and late physical/finite-bootstrap constructions.
Keep #83's profile/barrier work and #154's verification engineering separate
from numerical frontier comparisons. In particular, #154 still needs the
concurrency runner's invalid-job handling and integration/isolation checks;
the earlier frame-algebra comparisons did not settle that whole PR.

Start the next small active set with #2/#4/#8/#9/#12 (historical circuits and
geometry), then #38/#41/#44/#47 (producer lineage), and #154 (tooling).
Each must receive complete scientific-source and wrapper decisions before
closure. No unresolved PR is bulk-closed by this round.

Review and reconciliation prepared for Douglas Colkitt with OpenAI Codex
assistance. This is maintainer review, not independent human peer review.
Publication and GitHub resolution are recorded separately in the receipts.
