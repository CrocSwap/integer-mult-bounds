# Verification and handoff

Local validation on macOS 26.6.2:

    python3 -B research/hurwitz-asymmetric-copy-floor/verify.py
    /usr/local/bin/python3.12 -I -B -O research/hurwitz-asymmetric-copy-floor/verify.py
    make selected-record-check

All passed. The first interpreter was Python 3.14.6; the second was 3.12.8.
Both reproduce the committed deterministic receipt. The exact replay
includes all eight negative controls and both positive controls by default.
No assertion statements are used for acceptance, so optimized Python keeps
the checks active.

The completed domain is 240 E8 roots, ten quaternionic lines, all 45
two-line spans, all 3,025 ordered Gram blocks on singleton/two-line sets,
all 1,048,576 reader/source support pairs, all 32 transversals and all 1,024
fitting decoders. The proof reduces larger support spans to two-line spans;
it does not use random geometric samples. Two separately implemented exact
rational elimination routines agree on every Gram block.

Additional temporary-copy checks, performed without changing the inherited
source files:

- Copy the new package and exactly the six source-pin files to a fresh
  temporary root, then run the verifier from / with Python 3.14 in isolated,
  optimized mode. It passes (about 1.1 seconds in this local run).
- Change the receipt's claimed floor from ten to nine. The default verifier
  fails with "receipt mismatch".
- Restore the receipt, then append a line to the copied predecessor
  hurwitz_exact.py. The verifier fails with "source pin:" before computing
  the result.

All local Markdown links resolve. Staged whitespace and source-scope checks
pass. The only repository changes are this research package. Neither
upstream/ nor the selected certificate, generators, existing verifiers,
supplier words or assembly inputs are modified.

The expensive repository-wide suite and selected-construction cold replay
were not repeated because no construction or shared code changed. No Linux
CI result, full multiplication proof, or independent human review is
claimed. The mathematical argument and exact finite evidence are supplied
for review.

New contribution: a weighted transversal rank proof for the exact asymmetric
problem posed by #620, plus an independent portable replay. The predecessor
owns the geometry, symmetric upper bound and problem formulation. See
[PROOF.md](PROOF.md), [SOURCES.json](SOURCES.json) and [NOTICE.md](NOTICE.md).
