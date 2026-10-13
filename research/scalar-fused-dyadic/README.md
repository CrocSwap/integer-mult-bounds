# Fused exact dyadic updates in the PR799 independent auditor

**Verification tooling; no new κ.** This optional adapter accelerates the
independent scalar/frame/cone audit retained by Jeremy Kothe's #799 X4 supplier.
It computes `y + q*x` with one rational normalization when the denominators
are powers of two. Rows still contain ordinary `fractions.Fraction` values;
the original checks, gate order, compensation construction and comparison
logic run unchanged. Original source files and default commands are untouched.

Five alternating fresh-process pairs per interpreter measured **1.45–1.50×**
faster complete audits on this Linux host:

| CPython | Reference wall median | Fused wall median | Ratio | Reference / fused child CPU medians |
|---|---:|---:|---:|---:|
| 3.12.3 | 0.559843 s | 0.374207 s | 1.496× | 0.558649 / 0.374032 s |
| 3.14.4 | 0.501354 s | 0.345660 s | 1.450× | 0.501150 / 0.345456 s |

Every timed process produces the complete original receipt, excluding only
its elapsed-time field. Timings include imports, source admission, input
reading, parent-interface binding, all original audit phases, output and
serialization. This is one independent audit stage on one fixed word, not a
whole-frontier speedup or a multiplication runtime result. The host was not
isolated and caches were not flushed; timing is descriptive, not a pass gate.

## Reproduce

Python 3.11+ and the standard library; offline:

```sh
python3 -B -I research/scalar-fused-dyadic/verify.py
python3 -B -I research/scalar-fused-dyadic/test_kernel.py
```

Expected primary result:

```text
PASS_FUSED_DYADIC_AUDIT columns=728 complete_receipts=identical controls=15 native_updates=70765 scalar_prefixes=10240
```

The second command runs nine tests, including deliberately faulty optimizer
implementations. To repeat the complete-process benchmark on a POSIX system,
choose an output that does not exist:

```sh
python3 -B -I research/scalar-fused-dyadic/benchmark.py \
  --rounds 5 --output /tmp/scalar-fused-benchmark.json
```

Expected final marker: `PASS_IDENTICAL_COMPLETE_SCALAR_AUDITS`, followed by the
measured ratio. Both arms start a fresh isolated Python process for each run;
their order alternates. CPU time uses child process resource accounting. All
samples, environment, implementation hashes, source pins and the full matched
receipt are retained in [the 3.12 evidence](evidence/benchmark-python312.json)
and [the 3.14 evidence](evidence/benchmark-python314.json). Preliminary
[profile](evidence/pilot-profile.txt) and
[pilot receipts](evidence/pilot-receipts.json) are kept separately; the profiled
run is not treated as a reference timing sample.

Use the faster auditor directly on a native word:

```sh
python3 -B -I research/scalar-fused-dyadic/adapter.py \
  --word /path/to/FULL-WORD.json.gz --output /tmp/new-audit.json
```

`--engine reference` runs the original audit through the same wrapper. The
adapter checks immutable source pins before loading that audit, then replaces
only its `apply` function in memory. It always enables the original parent
interface check. It accepts changed words for experiments and leaves their
admission to the original checker; the differential suite separately pins its
benchmark input. All public wrapper outputs refuse overwriting an existing
path. `verify.py --write /new/path.json` reconstructs the differential receipt.

## Why the arithmetic is identical

Let `q*x = N/D` before reduction, and `y = A/B`. For dyadic inputs D and B
are positive powers of two, so one divides the other. With `L=max(D,B)`,

```text
y + q*x = (A*(L/B) + N*(L/D)) / L.
```

Both divisions are exact integer divisions. Constructing one `Fraction` from
this numerator/denominator gives exactly the same reduced result as the
original multiplication followed by addition. It handles negative values,
unequal denominator scales, reducible products and exact cancellation. A
missing or zero destination requires only `Fraction(N,D)`. If either existing
denominator is not a power of two, the helper falls back to the original
general-rational operations; it never rounds or silently truncates.

The original eager `Fraction(0)` default is also avoided. The source snapshot,
zero-entry deletion, arbitrary source/target distinction, inverse-transpose
sign and scale reciprocal are preserved. Scalars, scales and row values retain
their original types. The original `self add`, `zero scale` and unknown-gate
guards remain, while every surrounding admission/frame/endpoint/cone guard is
executed directly from the pinned unmodified auditor.

Thus, by induction over its calls, the auditor sees the same exact rows after
every update. There is no memoized acceptance decision, modular sampling,
floating approximation, skipped gate or shortened input-column domain.

## Differential and failure coverage

The full checker reconstructs compensation and evaluates all **728 arbitrary
native input columns in both orientations**, native frames, centre levels,
width inventory, entrance response, residual-wrapper exclusion and final
helper row/column cones. Its parent port and ordered-centre-frame binding is
enabled in both arms. These are scalar macro rows; this package does not
expand the private coefficient microcircuits or add precision claims.

The differential checker compares every report field except elapsed time,
against both the reference and the retained maintainer receipt. A further
untimed pass compares the exact target row and unchanged source at **all
70,765 actual updates**, with a deterministic row-stream digest. The complete
surrounding native audit still runs during that pass.

Additional checks include:

- **810** fused arithmetic cases: cancellation, missing destinations, zero,
  unequal binary denominators, very large signed integers and general rationals.
- **10,240** complete state-prefix comparisons over 64 seeded initial states,
  80 gates and both orientations. Seed 93 is fixed for reproducibility.
- **15** full changed-word controls: geometry, non-dyadic/non-unit/zero
  coefficients, self-addition, register range, missing work, entrance response,
  paid profile, width inventory, parent centre/port binding, duplicate cleanup
  and non-monotone frames. Both engines reject with identical type and message.
- **Three** invalid primitive controls and nine focused tests. Two faulty
  optimizer implementations are rejected by the complete audit: dropping the
  destination term fails entrance response; ignoring dual mode passes forward
  then fails the dual endpoint.
- A recompressed input still passes both native audits; only its compressed
  provenance digest changes. The underlying payload and mathematical report
  remain identical. The inherited immutable parent-file pin is retained.

[EXPECTED.json](EXPECTED.json) holds the deterministic evidence, and
[VALIDATION.md](VALIDATION.md) records executed environment and packaging checks.
Both implementations/checks in this contribution were prepared by one AI
agent; there is no independent human-review claim.

## Provenance and limits

Base: **f567884aeb8851b6e794af1184119a3bfbe1e631**. Selected source #799:
`80e6463157cfc80b85af09e7e2f14748fe2dac60`. The exact auditor, immutable parent
input and maintainer receipt have SHA-256 and Git-blob pins in
[SOURCES.json](SOURCES.json). The #799 word is read from the committed replay
archive, without extraction or executing archive content, and its member and
payload hashes are checked. The archive container hash is recorded separately.

Credit **icekylinx** for the independent exact auditor (originally prepared
with GPT-6 Astra assistance), **Jeremy Kothe** for retaining it in #799, and
**Chafik Boukhalfa**, **DreamingOfClouds**, **Rohan Arun**, **eumemic** and the
retained construction/compiler/verification lineage. The kernel adapts the
auditor's scalar interface; all source notices remain intact.

The local [claim](CLAIM.json) records OS assignment seed **93**, three candidates
and overlap. #667/#672 concern transcendental intervals, #707 determinants,
#721 source-archive streaming, #727 owner masks and #824 historical stage-pair
arithmetic. Those kernels differ from this native scalar update loop; none of
their pending implementations is imported. No sprint coordination issue was
available, so the claim is local.

The selected κ and mathematical construction are unchanged. Whole supplier
reconstruction, phase/wrapper replay, global owner admission, exponent assembly
and full repository or Lean checks are outside this benchmark. Uniform
compiler, realization, hosting, recursive, precision/tape and analytic
assumptions remain inherited. This is exact finite verification tooling, not a
formal proof of the multiplication theorem.

Prepared for **Gareth Davidson (@bitplane) with substantial OpenAI Codex
assistance**. Apache-2.0.
