# Observed validation

Date: 2026-10-13. Linux x86_64, kernel `7.0.0-38-generic`, glibc 2.43.
Exact source base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Prepared with substantial OpenAI Codex assistance; these are agent-executed
checks, not an independent human review.

## Fresh final composition

The complete certificate was generated once after composition and checked
again from a minimal copied checkout in a temporary path containing spaces.
That checkout contained only this package and its eleven pinned input files.
All four gzip inputs were recompressed at level 1 with a different timestamp;
their full decompressed payloads remained identical. The current working
directory was `/tmp`, outside the copied checkout.

| Command variant | Result | Elapsed |
| --- | --- | ---: |
| `/usr/bin/python3.12 -B -I verify.py` (3.12.3) | PASS, committed certificate equal | 4.12 s |
| `/usr/bin/python3.12 -B -I test_verify.py` | 10 tests pass | 1.09 s |
| `/usr/bin/python3.14 -B -I -O verify.py` (3.14.4) | PASS, committed certificate equal | 4.01 s |
| `/usr/bin/python3.14 -B -I -O test_verify.py` | 10 tests pass | 1.14 s |

These timings are descriptive execution receipts, not a before/after runtime
benchmark. Reproduction uses the full paths shown in README.md.

Expected primary output:

```text
PASS_COMPLEX_COEFFICIENT_COMPOSITION programs=4 logical_columns=716 coefficients=686 savings=68512,55554,75622,60160 controls=21
```

Coverage includes all four programs' 716 logical and nine arbitrary private
input columns, all 686 coefficient maps, all 1,945 shared blocks, exact
primitive bills, conservative positive prefix bounds, the paid child census,
and complete restoration/erasure endpoints. A separate flat-column interpreter
checks every coefficient and shared block; separate scans reconstruct grouping
and pricing. The 21 primary adverse controls run in each verifier invocation.

## Additional failure detection

In separate temporary copies under Python 3.14.4 with `-B -I -O`:

- Decrementing the expected JP8 forward saving was rejected as a certificate
  mismatch after recomputation.
- Replacing signed-digit subtraction by addition was rejected at an exact
  block endpoint, rather than by a source-code hash.
- Changing a pinned SPEC byte was rejected by source binding before replay.
- `--write` to an existing certificate was refused and left its bytes intact.

The independent tests also reject an endpoint-neutral prefix excursion that
fits the binary operation budget, omitted clearing and incompatible sharing
boundaries. Recompression passes; altered decompressed source content fails.

`make selected-record-check` passed, including the original selected source
inventory, exact κ and proof supplements. Staged whitespace, local Markdown
links and patch application to the exact base tree were checked at packaging.

## Reuse and limits

The selected native providers were read from their source-bound retained
artifacts, not rebuilt. Production physical frames, phase lowering, wrappers,
global owner admission, global invoice/assembly, the full `make verify` suite,
Lean and remote CI were not run. Existing production files are unchanged.
The complete finite scalar primitive replay is fresh. The ten tests are
additional checks, not a formal proof of the full multiplication theorem.

The final overlap refresh through PR779 found the related PR739/751/755/769
extensions documented in README.md. Matching standalone signed-digit results
are explicitly credited to PR723/734; the final result is the checked
composition, its CK sharing coverage and its exact nonadditivity accounting.

Before publication, the actual upstream commit was fetched and the contribution
was rebased onto it after checking equality with the original archive's base
tree. Only the nine files in this research package differ from upstream.
