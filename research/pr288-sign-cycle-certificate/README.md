# Four constraints certify PR288's sign-gauge obstruction

This package gives an explicit certificate and a separate exact checker for
the obstruction already reported by eumemic in PR288 §1.4(d). It adds no
multiplication bound. Braverman and He supplied the PG(2,9) graph and sessions.
Read [PROOF.md](PROOF.md) for the complete statement and ordinary proof,
[SOURCES.md](SOURCES.md) for immutable sources, and [NOTICE](NOTICE) for credits.

The restricted model has fixed additive 5×5 rational vertex matrices,
rank-at-most-one physical edge differences, and each session target equal
to ± one common invertible matrix. Three five-edge paths force sessions 7
and 30 to have both equal and opposite signs. Their four constraints have
sign product −1. This excludes all assignments in that model; it covers
neither unrelated Levi targets nor nonadditive frames or higher-rank edges.

Run from the repository root with Python 3.11 or newer:

```sh
make pr288-sign-cycle-verify
```

Or run `python3 -B run_checks.py` in this directory. The standard-library
runner checks the certificate, runs 24 tests normally and under `-O`,
regenerates into a temporary directory, requires identical certificate
bytes, and checks the new file. Tests include a geometrically valid
balanced cycle, a false sign, removed path edges, wrong endpoints and
source-pin rebinding. No dependency or network access is needed.

The checker reconstructs the graph by projective-vector normalization and
imports neither the producer nor upstream checker. The producer uses a
separate direct construction and BFS; it is not trusted by the verifier.
The matrix-to-sign implication remains an ordinary written proof. This is
not human peer review, a Lean proof, or a full multiplication theorem audit.
The unprovided PR288 SAT/MITM/Gröbner searches are outside this package.

This small integration omits the original handoff's large PR snapshots,
copied upstream documents and historical execution receipts. It retains
the complete witness and mathematical premises. Validation of this local
integration is reported separately; no broad gate success is asserted here.
New work is Apache-2.0 with substantial OpenAI ChatGPT/Codex assistance.
