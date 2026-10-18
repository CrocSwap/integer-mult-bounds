# Sprint validation

Research started 2026-10-13 23:20:55 UTC in the hosting child; common sprint began
23:15:13 UTC. New owner search completed by 23:28 UTC. Full strict verification
completed by 23:31:43 UTC. Frozen-wrapper reproduction completed by 23:33:45 UTC.
Hard stop for new computation was 23:41 UTC; report deadline 23:45:13 UTC.

Commands were run from an isolated author worktree at the repository root.
Base `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
Branch `research/astra-ultra-hosting-20261013`.
Bun 1.4.2; Python 3.14.7; Linux x86_64. No authored Python, external compute,
public posts, pushes, PRs, selected-result edits or concurrent mutations of
shared source inputs.

Commands executed from this worktree are recorded below. The original
machine-specific checkout and checked-supplier paths are replaced with
`/path/to/repository` and `/path/to/checked-selected-native-local`; these denote
the original inputs, not a new replay. Anonymous temporary output paths remain
in the preserved native receipts.

```sh
bun research/astra-ultra-hosting-20261013/search.ts
bun research/astra-ultra-hosting-20261013/neutral-search.ts
bun research/astra-ultra-hosting-20261013/construct.ts
bun research/astra-ultra-hosting-20261013/verify.ts
bun research/astra-ultra-hosting-20261013/replay.ts \
  /tmp/astra-hosting-sprint-20261013-r2 \
  /path/to/checked-selected-native-local
python3 -B /tmp/astra-hosting-sprint-20261013-r2/source/verify_t16.py \
  --main /path/to/repository \
  --local /path/to/checked-selected-native-local \
  --work /tmp/astra-hosting-sprint-20261013-full
RESEARCH_DEADLINE_UTC=2026-10-13T23:41:00Z \
  bun research/astra-ultra-hosting-20261013/verify-native.ts \
  /path/to/checked-selected-native-local \
  /tmp/astra-hosting-sprint-frozen-replay
```

The discovery runner's first attempt, `/tmp/astra-hosting-sprint-20261013`,
correctly failed before emission because it still pinned the predecessor owner
file. Its log is retained there. The runner was corrected to pin the newly
constructed candidate data before discovery. No scientific gate was modified,
no failed stage was skipped, and a fresh directory was used for the entire
successful second run. The new SPEC freezes discovery values; strict replay
compares them after independent recomputation with `WITNESS_DISCOVER=0`.

`receipts/` copies the full untouched-driver run's receipts byte for byte.
The second frozen-wrapper reproduction independently regenerated the same
mathematical result. Compression hashes may differ; proof-relevant content
and native source bindings are authoritative as specified by the repository.

Not run during the author sprint: a new local supplier construction, full cold ancestry replay, Lean
multiplication theorem, hosted CI, publication, or adoption. Those are not
silently inferred from the changed-path native success. Independent AI review
and subsequent publication/CI status are tracked separately on the contribution PR.
