# Fourth frozen 100-PR review archive

This package records source provenance, scoped review, execution and actual closure separately.
It is not a verifier for the multiplication theorem. Start with
[the review](../../docs/research/community-reconciliation-fourth100-review.md).

Run `python3 research/community-reconciliation-fourth100-audit/verify.py --git-blobs`
for archive/ledger integrity. To obtain an original source checkout, use
`python3 research/community-reconciliation-fourth100-audit/replay.py --pr 627 --fetch --destination /tmp/pr627-source`.
The archive tag is separate from main ancestry. Original sources and notices are retained intact;
packaging repairs live under adapters and operate on separate copies.

## Open next questions

See DISPOSITIONS.json for incomplete executions and REVIEW.json for each interface's limits.
A completed historical review does not discharge inherited all-size or analytic assumptions.
Continue the next queue chunk without repeating completed unchanged package replays.
