# Verification scope and evidence

All mathematical proofs are informal. The operational models are Python 3.12
standard-library source, portable across Windows and Linux. There is no Lean,
GPU, external solver or TM dependency in replay. No benchmark establishes a
practical speedup, and no new best κ is certified.

The source-bound verifier runs under isolated optimized Python (-I -O -B),
using explicit checks rather than disabled assert statements. It authenticates
all local source/proof/metadata bytes before evaluating checked source, bypasses
stale .pyc imports by compiling source bytes, and fails on extra/missing files.
A stable checkout is required throughout replay; this is not an atomic snapshot
against a concurrent malicious writer.

Evidence included in replay:

- 37 complete packed multiplication cases, including an extremal 65,535-bit
  product with 2-bit packed digits; independent Python integer product oracle.
- 80 directly generated root seeds against independent high-precision series;
  all-p precision and word-size proofs are separate from those samples.
- 960 carry/product fixtures and 10,752 CRT plus 10,752 rounding coefficients.
- 45 phase-table configurations and 774 exact rational phase queries.
- 12 signed exponential tables and 60 reference queries. A separate independent
  worker review checked 448 tables and 2,240 queries; that larger review is not
  silently counted as the registered replay's work.
- 12 Gaussian chirp algebra cases: 117 exact matrix entries and 33 exact outputs.
- 12 executed native Gaussian blocks, 45 outputs, checked below 2^-60.
- 20 ordinary real band systems, 208 rows, with exact rational residual controls.
- 3 periodic real systems, 9 reused right-hand sides, 123 rows; ordinary and
  small Schur factors are prepared once and reused.
- 3 actual Gaussian N coefficient/periodic solve fixtures, 55 rows, checked
  below 2^-100 against an independent finite high-precision Gaussian sum.

Decimal/Fraction/big-integer reference work is validation only, not charged to
the proposed native algorithm. Exact error, infinite-tail and rounding proofs
supply the universal statements. The test examples do not verify the full
asymptotic Fourier/resampling parameter assembly.

Negative controls include wrong root, invalid packed ABI, altered phase entry,
insufficient phase/root precision, overflow, singular band and out-of-range
exp argument. Publication preflight additionally checks a changed proof source
fails the hash guard before component execution. The real periodic solve now
executes; only the general complex-matrix elimination extension remains solely
at proof level. For the actual real Gaussian matrix, complex right-hand sides
are handled by two real solves.

Independent AI reviews accepted the root/FFT precision, exp implementation and
periodic factor-reuse accounting. They are not independent human review or
kernel certificates. Contents, generic registered replay, Git-free export,
commit identity and short upload staging are checked separately before handoff.
