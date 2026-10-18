# Historical 92-PR reconciliation

See [the scoped review](../../docs/research/community-reconciliation92-review.md).
Original source trees are retained via the separately pinned Git tag in ARCHIVE.json.
Run `python3 research/community-reconciliation92-audit/verify.py` for offline integrity,
or add `--git-blobs` after fetching the source tag to authenticate all original file bytes.
`replay.py --pr N --fetch --destination /new/path` materializes one original tree.

Logs distinguish fresh local runs from exact-head historical CI. Integrity checks do
not certify mathematical correctness. The current frontier is unchanged.

## Open next questions

PR #122 needs its complete parent word/profile before terminal-elision replay can finish.
See REVIEW.json for that blocker, retractions, draft limitations and all contributor credits.
