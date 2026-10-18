# Validation and limits

The sections below retain the original 2026-10-13 execution record.
The later PR803 source/analytic review continuation is documented in
[audit/README.md](audit/README.md), with separate revision checks in
[audit/VALIDATION.json](audit/VALIDATION.json). The historical receipts
are unchanged and are not promoted to an analytic-proof certificate.

Executed on Windows 11 (10.0.26300), CPython 3.12.2, 2026-10-13 UTC.
The detailed interpreter/platform strings and command receipts are in
`evidence/environment.json`, `evidence/verify.txt`, and
`evidence/package-tests.txt`. Captured text logs are normalized to LF;
vendored source files are copied byte for byte and separately hashed.

## Executed checks

The normal verifier passed in 2.859 seconds on this session's machine.
This timing describes one evidence replay; it is not a benchmark of an
inversion algorithm or a claimed speedup. Its deterministic receipt is
`EXPECTED.json`. Counts there refer to one run, not sums across reruns.

It checks 14 integer budget comparisons, 126 root/reflection families,
756 exact circle identities, 546 cyclic inverse matrices (9,516 inverse
entries), 6,565 finite Hilbert comparisons, 128 near-circle instances,
and 21 rejection/counterexample controls. All arithmetic is integer or
rational, including Gaussian-rational complex arithmetic. No numerical
root finder, floating-point quadrature, solver, or sampled circle minimum
is used as evidence of nonvanishing.
The cyclic matrices in these finite tests use the explicitly supplied
rational root families; they are not new exact inverses of PR621's
cyclotomic kernels.

Eight package tests passed in 11.312 seconds including subprocess launch.
Each runs with `python -I -B -O` from an unrelated temporary directory:

1. An intact offline copy under a path containing spaces passes.
2. Changed vendored proof bytes fail their pinned SHA-256, even after
   updating that file's package checksum.
3. A changed pinned Git blob fails, even after updating the package checksum.
4. An unrecorded proof edit fails the package manifest.
5. A changed expected radix budget fails the recomputed evidence comparison,
   even after updating the expected file's package checksum.
6. Removing conjugation from the reflection code fails a circle-modulus check.
7. Changing the closure denominator sign fails dense/geometric inverse agreement.
8. An attempt to overwrite existing evidence is rejected before any write.

The code fault tests update the modified verifier's package checksum so
they reach the mathematical checks; hash rejection alone is not counted
as catching those mathematical faults. All checks use explicit exceptions
and remain active when Python assertions are optimized away.

## Proof audit

The written proof was reviewed locally for measure normalization,
both Fourier directions, degree versus number of distinct roots, boundary
zeros in the Hardy factorization, roots at zero, repeated and mixed roots,
the exceptional constant projection in the arc-length argument, and the
operator-series convergence hypothesis. This is author/AI review, not an
independent human assessment or proof-assistant certificate.

Two analytic statements remain distinct from finite evidence: the
all-frequency coefficient inequalities proved in `PROOF.md`, and PR621's
inherited nonvanishing/circle estimate. The latter's unchanged expensive
foundation replay was not repeated. PR621's original notice and proof are
included with immutable pins.

## Unexecuted and unclaimed

No Linux/macOS or second-Python-version replay, remote CI, Lean proof,
full repository `make verify`, or selected-supplier cold replay is claimed.
The contribution changes no selected construction or existing implementation.
Source preparation, rounded execution, error propagation, scratch restoration,
traffic/routing, tape/compiler/hosting, and the all-size multiplication
transfer remain outside this result. No new kappa is reported.

The local preparation branch is based on an explicitly partial snapshot
of exact upstream text inputs. The initial handoff was a focused patch
because clone/browser access was unavailable and no writable fork was
accessible. The user subsequently created `alephnan/integer-mult-bounds`.
Publication uses the GitHub API with the complete pinned upstream tree and
upstream commit as parent. GitHub main and the fork's main both matched
that base before publication. The handoff records clean patch application
and byte checks.
The initial fresh-repository application detected Windows CRLF conversion.
The package now supplies `.gitattributes` to preserve exact bytes; the handoff
also disables conversion for that one apply command. The final applied
artifact is compared byte for byte and replayed under optimized Python.
