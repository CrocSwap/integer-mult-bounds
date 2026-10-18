# Validation record

Run on 2026-10-13 UTC, on macOS arm64. Base commit:
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
The audit resumed unpublished work after the previous automation lost its
connection; it did not modify that earlier checkout.

## Completed checks

| Command, from the repository root | Observed result |
|---|---|
| `python3.14 -I -B research/p112-parity-lift-audit-seed68/verify.py` | PASS, CPython 3.14.8, about 4.0 seconds |
| `python3.11 -I -O -B research/p112-parity-lift-audit-seed68/verify.py` | Same PASS and complete certificate, CPython 3.11.17, about 4.7 seconds |
| `python3.14 -I -B research/p112-parity-lift-audit-seed68/test_package.py` | PASS, relocated replay plus three external corruption controls |
| `python3.14 -I -B scripts/verify_selected_result.py` | PASS, selected exact kappa, source inventory and proof supplements |

The Python executables for these checks were under
`/Users/thakrarsagar-dev/homebrew/bin/`. An initial invocation of `python3`
through the command runner resolved to an older interpreter without
`int.bit_count`; it failed before the census. The documented requirement
is Python 3.10+, and the successful runs used explicit supported executables.
The timings are observations, not a before/after performance claim.

The receipt regenerates all 4,194,304 parameter-class records. Both rank
engines agree on 325638 support pairs. All 27 literal identity cases and
eleven embedded controls pass. The package test invokes optimized Python
in a temporary relocated tree, then rejects a changed histogram count,
a corrupted source Git-blob pin and changed geometry bytes. Source-file
SHA256 and Git-blob checks both run before the mathematics.

Certificate SHA256:
`d6bd303f5a73a621b423a19c54353dff4b1dad50ee8275f7f4092bb6b81843b4`.
The immutable PR845 proof, selected-record context and selected-review
context also match their recorded hashes. Pending PR1224 and PR1197 proof
bytes were fetched at the exact heads in SOURCES.json and match their
recorded SHA256 and Git-blob IDs. Those proofs are citations, not executable
or theorem dependencies.

## Overlap and publication boundary

Final pre-submission overlap refresh at 22:40:52 UTC covered 813 open PRs,
64 discussion records and 326 local records, with complete reported remote
pagination and no warnings. A targeted query returned all 43 matches for
P112, ten-term or parity-gated. This search covers PR bodies and discussion
claims, not every pending code diff.

PR1224, PR1197 and PR1133 retained their recorded heads. New nearby work is
distinct: PR1304 treats a fixed A8 simplex; PR1313 diagonal-mask completions;
PR1320 a masked co-star crown; PR1323 root-star support trims. Discussion1316
mixes a free odd rectangle with one coordinate term. None is imported as
a premise or claimed as a result of this package. No pinned coordination
issue was present, so the donor's local-claim fallback was used.

The package is eight added files in one research directory. The selected
frontier, existing supplier code, frozen evidence and upstream/ are untouched.
The repository has neither a `codex` nor a `codex-automation` label.

## Not performed

No Linux or hosted execution of this package, full selected-supplier cold
replay, physical/native supplier admission, proof-assistant formalization,
or independent human review was performed. The independent implementation
claim is limited to the two binary-rank engines; both consume the same
support masks. No new kappa, full runtime bound or unrestricted ten-term
impossibility is claimed.

Prepared for Sagar Thakrar with substantial OpenAI Codex assistance.
Apache-2.0.
