# Executed validation

The seven listed checks passed with Python 3.14.7 in normal mode and with
`-O`. The normal run took 3.175434 seconds. The optimized run took 2.877606
seconds. Each run used one child process at a time and the Python standard
library. The driver required at least 3 GiB of free disk space.

```text
PASS_CENTRE_SUPPORT_GEOMETRY
PASS_INDEPENDENT_CENTRE_SUPPORT_GEOMETRY
PASS_DYADIC_QUERY_SEPARATION
PASS_INDEPENDENT_DYADIC_QUERY_SEPARATION
PASS_INDEPENDENT_NATIVE_CENTRE_REVIEW
PASS_EXACT_QUERY_SOURCE_SPANS
PASS_INDEPENDENT_QUERY_SPAN_SOURCE_AND_CERTIFICATE
PASS_SOURCE_GEOMETRY_ANNEX
```

The [normal receipt](evidence/replay-normal.json) and
[optimized receipt](evidence/replay-optimized.json) record each check,
timing, and typed JSON comparison. Both runs used the
[pre-receipt manifest](evidence/replay-input-manifest.json). That manifest
contains the same executed scripts and frozen sources as the final annex
manifest; the final manifest also contains this validation record and the
saved outputs. The eight actual optimized JSON outputs are retained under
`evidence/optimized-receipts`. The only receipt field allowed to change is
`checker_sha256`, which must equal the executing portable script's hash.

Both runs verified all 129 parent and cache-annex files before and after
execution. The extraction also compared all 72 copied source and notice
files with their exact local originals. No original file changed. The
portable edits preserve every non-main function AST. The seven main
functions change input/output paths only. Two archive readers now load
the exact parent members, whose old whole-archive binding is recorded
separately. The complete differences are in `PORTABILITY.patch`.

This annex did not run the parent package or cache-annex mathematics.
It did not rerun the mixing producer inventory, modular existing-site
rank checker, cut source emitters, native recipe generator, plane route
generator, odd-grid implementation, or a complete supplier. Their results
must not be reported as fresh checks. The independent mixing interval
replay checked the full retained cut product set and physical premises.
The prior reviews remain separate from the fresh publication review.
