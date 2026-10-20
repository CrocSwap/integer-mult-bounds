# Verification receipt

Base: `47481c89fd30a43f8f882eb4b391e89c29273fd0`. Assignment seed: 93.
Executed on October 14, 2026 AEDT (October 13 UTC), macOS arm64.
Raw test output, the cross-version and relocated receipts, and code hashes
are retained in `VALIDATION.json`; benchmark samples are in `BENCHMARK.json`.

| Check | Result |
| --- | --- |
| Package tests, CPython 3.14.6 | 11 groups pass |
| Package tests, CPython 3.14.6 `-O` | 11 groups pass; full inherited-replay controls run only in normal mode |
| Package tests, CPython 3.12.12 | 11 groups pass |
| Original central-factor tests | All four run with each engine inside each package test run |
| Exhaustive h=8 corruptions | 1,344 scatter replacements + 231 gather sign flips + 231 deletions rejected by both engines |
| Complete h=26 product | All 6,760,000 coefficients checked; identical factor receipt |
| Timed full audits, Python 3.14.6 | Three baseline and three packed fresh processes; identical complete certificate |
| Full packed audit, Python 3.12.12 | Same complete certificate hash |
| Minimal offline relocation | Only pinned inputs and this package copied to a path with spaces; full replay passes from an unrelated cwd |
| `make selected-record-check` | PR890 exact value, original inventory and proof supplements pass |
| Source admission | All 43 inherited pins match base Git objects and refreshed main |

Every complete replay recorded in this October 13 receipt has certificate SHA256
`ffae0f0a22863718e3134a924592dcf4b05e919223323ba536c587c592bfe6a1`.
Timing metadata belongs to the separate wrapper, not that certificate.
The three benchmarked implementation hashes still match the submitted code.

A later pin refresh, 2026-10-20 on main `bb4bccbf42844d2801487450727c2f63e10d1d0f`,
rebinds five drifted files so admission matches the tree
`community-batch952.yml` checks. The replay on CPython 3.12.3 then reports
`receipt_sha256`
`2aabc7e3ed38a27902f88244b80bed579e8ec2158c6ad3253f1c654c79b299e0`
(1.901 s, `coefficients_checked` 6760000). That digest is the current
certificate. It differs from `ffae0f0a` only in three embedded source hashes.
`VALIDATION.json` and `BENCHMARK.json` are left as the October 13 record.

Controls cover structural/type violations, wrong signs, missing first/last
gather columns, large signed scatter values, equivalent accepted factors,
wrong scalar charges despite correct products, a deliberately faulty radix,
mutable-input reuse, altered/missing inputs and adapter, incomplete/understated
receipts, disabled inherited assertions, and attempted output overwrites.
No optional dependency, network access, optimizer or Git command is needed by
the reproduced package.

The package is additive and opt-in. No generator, default verifier, inherited
certificate, selected frontier or `upstream/` byte is changed. The full
`make verify`, selected cold replay, Lean and remote CI were not run for this
isolated historical adapter. This receipt does not claim those gates passed.
The written radix argument explains exactness; finite replay does not prove
the full multiplication theorem or discharge inherited conditional assumptions.
