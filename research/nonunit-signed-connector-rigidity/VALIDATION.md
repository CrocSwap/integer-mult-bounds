# Validation and proof boundaries

Research runtime: stable CPython 3.15.0, checked against python.org on 2026-10-14.
All primary checks run through the Math research-python wrapper.
Exact version: 3.15.0 (main, Oct 9 2026, 11:16:41), Clang 21.0.0.
Executable: /opt/homebrew/opt/python@3.15/bin/python3.15.
The repository's explicit VERIFY.json compatibility pin uses CPython 3.12 separately.
The registered replay passes on 3.12.12 at /opt/homebrew/opt/python@3.12/bin/python3.12; this is a disclosed compatibility check, not a runtime fallback.

## Checks

- Normal and optimized primary replay return identical semantic JSON receipts.
- Six mandatory cube vertices have two leaves in all 16 sign/height cases (four templates), corroborating the written cycle contradiction.
- Four height-equality patterns exclude one- and three-transfer equal-height intervals.
- 192 rational linear systems have 48 consistent solutions, all unit; generic elimination and a distinct difference formula agree.
- 720 signed event orders and cube-state dynamic programming agree on all 344 signed vertex sets and the inherited one-root exclusion.
- Free noncommutative forward/inverse replay preserves all independent dirty inputs.
- Independent dense 16x16 block-matrix composition checks all dirty basis columns for the credited word, a balanced nonunit mutation, and a scaled-query control.
- All 16 single-event omissions and the balanced nonunit mutation fail the symbolic target check.
- Scaled ordinary queries and six transfers each admit a valid word with nonunit transfers, demonstrating material hypotheses.
- A read-only copy in a path containing spaces passes; two actual source corruptions fail with explicit exceptions.
- Package metadata, exact main provenance pins, selected-record verification, five selected-record tests, and binding-only research baseline pass.

The exact program word resides in verify.py. It is PR1651's witness, not a new construction.
The four-equation model includes nonchronological source states, so its exclusions use a superset of actual circuits.
The proof supplies the reduction from arbitrary straight-line programs to those equations.
The unit-only 7,257,600-trace census and its reported count of 80 are not repeated or relabeled as independent results.

No human review, proof-assistant verification, new physical supplier, selected cold replay,
or multiplication theorem is claimed. Hosted CI is separate from these local results.
The same assistant wrote the separate models; mathematical-model independence is the claim.
The selected frontier remains conditional on its inherited all-size/compiler, realization,
hosting, precision/tape, exact recovery, analytic, and bit-interface hypotheses.
