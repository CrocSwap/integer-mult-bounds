# Notice

This package accelerates the historical partial-swap shared-point verify digest
in `scripts/partial_swap/shared.py:SharedPointCircuit.verify` while preserving
support checks and `circuit_sha256`.

Predecessor credit:

- Douglas R. Colkitt — shared-point / exclusion circuits and the historical
  common-point motif.
- icekylinx — partial-swap producer adaptation of the shared-point circuit
  (`scripts/partial_swap/shared.py`, Apache-2.0).
- Closest tooling priors on *different* objects: CrocSwap/integer-mult-bounds
  PRs #756 (balanced-Fano packed replay), #1793 (inplace-side prefix), #1861
  (parity-side basis/contains), #1922 (joint-frame cleared product), #1984
  (mixed-point scalar digests), and #1994 (canonical
  `scripts/shared_point_circuit.py` verify digests; this package applies the
  same byte-identical formatter to the partial-swap fork).

Prepared by Wentao Li with substantial AI assistance under Apache-2.0.
This is not independent human peer review and is not a formal proof of the
multiplication theorem.
