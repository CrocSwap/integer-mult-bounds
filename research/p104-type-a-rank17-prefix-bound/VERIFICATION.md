# Verification receipt

CPython 3.12 with standard-library dependencies and assertions. The package-relative replay on 2026-11-12 UTC exited 0 and regenerated all five pinned receipts. A relocated copy ran with an empty environment in 0.72 seconds and produced byte-identical receipts. The official registered package wrapper also exited 0 in 1.23 seconds, with `PASS_REGISTERED_RESEARCH_PACKAGE` for this package.

The exact forward and reverse replays check the original caller endpoint and planted valid prefixes. The rank-17 gate accepts pure even and pure odd one-body prefixes, rejects a mixed-parity prefix and a foreign body, and checks an exact reverse negative QUERY direction. The package driver rejects altered caller bytes and altered price bytes before mathematical output, each with exit 1. A duplicate path key in the dependency manifest also exits 1 before replay. The five output hashes are in [receipts/SHA256.json](receipts/SHA256.json).

The initial even-prefix-only role-7 check and the later both-allocation check produced identical normalized column hashes at every cut. The package replays the stronger both-allocation check. At no cut was a paired suffix or physical construction needed. This local result does not replay the native supplier or promote the selected record. The exact earlier comparable replay and its assumptions are pinned in [inputs/ADMITTED.json](inputs/ADMITTED.json).

Hosted status for this contribution is pending publication. The registered source-history and proposed-file mode checks are applicable once the contribution is committed.
