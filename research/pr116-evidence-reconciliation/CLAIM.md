# Sprint claim

This is the historical 2026-10-13 claim and outcome. The 2026-10-16 revision
addresses the [maintainer's PR1007 request](https://github.com/CrocSwap/integer-mult-bounds/pull/1007#issuecomment-6161276240):
retain this source-identification result through the current ledger generator
without overwriting PR116's subsequent completed review, incorporation or
closure. Scientific pins and the offline capsule remain unchanged. This revision
does not reopen a construction search or claim a new bound.

- Track: research consolidation; OS-random assignment seed **96** (Python secrets.randbelow(100)).
- Base: `8bddbee377e2f3ce1f1247196c4b290d55767d20`.
- Claimed at 2026-10-13 16:09 UTC; expected finish 16:34 UTC. Planning envelope 30 minutes, final 25% reserved for verification and handoff. Orientation completed within the first 20%.
- Object: PR116's `changed_since_review` ledger record versus the round-eight statement that its later head only records verification evidence. Compare historical `97750ec74fc714638c0aa4f31aaa880e56cb8b4d` and current `295a48a3b966428896057a98c6b4834c0b4b7416`.
- Method: independently reconstruct the exact Git-object delta, validate the changed README/SOURCE/validation fields, and reconcile the preserved 42-check claim against GitHub's historical check metadata. No assumption that author receipts imply mathematical review.
- Deliverable: a small offline source/evidence certificate, checker with corruptions, and a narrowly scoped reconciliation note. No new bound or frontier mutation.
- Three initial candidates: PR236 source availability (already PR746), PR210 later parity/fusion head (already PR930), and PR279's twelve-path target-prefix increment. A targeted overlap search found PR828 covering PR279 exactly, before any work was claimed. One pivot to the unmatched changed-head records: [116,118,123,225][96 mod 4] = 116.
- Overlap: PR116/118/117 are producer lineage, not independent receipt reconciliation; no PR116-specific consolidation found in the open PR queue. Earlier round-eight pr116-delta.json is a historical summary to corroborate, not fresh source identity evidence. Prior negative results are not reopened; no circuit search is proposed.
- No pinned coordination issue exists (GraphQL checked immediately before this claim); local claim used. No workers delegated.

## Result — 2026-10-13 16:24 UTC

Submitted [PR1007](https://github.com/CrocSwap/integer-mult-bounds/pull/1007).
Complete Git-tree reconciliation finds only the three evidence/status paths;
41 dependency objects are unchanged. All 42 historical check records match,
and the three focused jobs' actual synthetic merge has the historical source
tree. Twenty-eight local tests, cross-version offline replay, regeneration and
the complete 642-entry ledger checks pass; see `VALIDATION.md`. Mathematical
acceptance and the unrecovered author local-run archive remain separate.
Selected frontier and upstream are unchanged. No PR116 overlap appeared in the
final queue; the separately claimed PR279 reconciliation merged during this run.
