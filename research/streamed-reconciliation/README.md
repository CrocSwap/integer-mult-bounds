# Bounded-memory reconciliation archive replay

**Tooling improvement; no new κ or mathematical claim.** The offline review
reconciliation verifier now streams the immutable PR181 split ZIP into a
seekable temporary file, then hashes each decompressed Git blob in 1 MiB
chunks. Previously it retained every compressed part, their concatenation,
and a whole decompressed member. Other reconciliation checks are unchanged.

## Evidence and reproduction

From the repository root, with the base Git object available:

```sh
python3 -B research/streamed-reconciliation/benchmark.py --rounds 5 --memory-limit-mib 96
```

The integrated harness compares the current verifier with a reference that
restores the exact historical buffered archive block while retaining every
current ledger check. It executes both versions against the
**same current checkout** in fresh processes, alternating their order. It checks
identical complete stdout for all successful runs. `RESULT.json` is the recorded
Linux/Python 3.14.7 run, with source/manifest hashes and all ten samples:

| Full offline verifier | Before | After |
|---|---:|---:|
| Median peak process RSS | 107,958,272 bytes | 47,034,368 bytes |
| Median elapsed time | 2.255 s | 2.244 s |
| 96 MiB `RLIMIT_AS` replay | `MemoryError` | passes, same stdout |

Peak process RSS falls **56.4%**. Runtime is effectively unchanged; the small
observed difference is not evidence of a reliable speedup. Expected output is
JSON with successful uncapped runs and equal stdout hashes. The memory-limited
outcome and absolute timings are environment-dependent, not acceptance thresholds.
The benchmark uses Unix `resource` (RSS unit conversion for Linux/macOS).

This trades retained Python heap for **33,595,108 bytes of temporary storage**.
`TMPDIR` can select that storage; insufficient space or permissions fail normally.
On tmpfs, the spool still consumes system memory: this is a process-RSS and
address-space improvement, not a measured reduction of total system RAM usage.
The whole verifier is not constant-memory; unrelated file-hash paths still buffer
files. No persistent cache or extra dependency is introduced.

## Exactness and negative controls

```sh
python3 -B -m unittest discover -s tests -p 'test_*reconciliation*.py' -v
```

Expected on the integrated branch: **19 tests pass** (also checked with `python3 -B -O`). The new tests
compare all **1,700** real blob identities against the original whole-buffer
calculation, independently of the runtime/stdout benchmark. Synthetic controls
cover empty and binary members, multi-chunk members, four compression methods,
split boundaries, duplicate names, each manifest guard, changed part bytes,
repinned CRC corruption and a repinned truncated ZIP. Inflate a member's central
uncompressed size while preserving its correct payload CRC: the new size check
rejects it and closes its tempfile, whereas the original buffer reader tolerated
that inconsistency. This is intentional additional rejection, not lost coverage.

Every original part size/SHA256, complete compressed archive SHA256, member CRC,
Git blob identity and unique-name count obligation remains. Duplicate-name
lookup deliberately retains the original last-entry semantics. No extraction
occurs. The immutable ZIP pin is not replaced by semantic container equivalence;
the repository's gzip portability policy for regenerated artifacts is separate.

## Pins, scope, attribution and handoff

- Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Historical archive source: `7fb2194801e3a10f54772c7f0d5505035a4fc0ad`,
  as recorded in `research/coordinated-frames-and-entrance-banks/BASELINE.json`.
- Archive SHA256: `2f8b4294620228116cfe993a376e2c848a7f280c4a7380d6ff4d2c8a8ea076eb`.
- Seed **86**, OS randomness; candidate choice and local claim in `CLAIM.json`.
- Credit Douglas R. Colkitt's reconciliation infrastructure and Chafik Boukhalfa
  (`chafreaky`)'s preserved PR181 baseline package and predecessor sources.
- Prepared by **cxnmai**, with substantial OpenAI AI-assistant assistance for
  implementation, tests and documentation, plus a separate AI reviewer. That
  review found no regression and requested the added member-size/cleanup control.
  This is not independent human review. New work is Apache-2.0.

PR704 (`152583fe2062f23b1149b4b20255f8e85946d558`, roife) separately hardens
ledger-to-decision bindings in this same file. This contribution neither relies
on nor duplicates those checks; the archive-reader change is independently
reviewable and should compose with that work. No mathematical negative search
is reopened. The selected #626/#543 conditional witness and all inherited
compiler, hosting, precision, tape and analytic assumptions remain unchanged.

Validation completed: normal and optimized focused tests, full offline
reconciliation in ten benchmark processes plus the successful capped replay,
`make selected-record-check`, and `git diff --check`. No construction or
certificate was regenerated; `upstream/` is unchanged. The expensive full
`make verify`/cold-construction suite was not rerun for this archive-I/O change.
No claim about a full multiplication theorem follows from these integrity checks.
