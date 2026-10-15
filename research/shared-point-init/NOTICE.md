# Notice

This package accelerates the historical shared-point merge construction in
`scripts/shared_point_circuit.py:SharedPointCircuit.__init__` while preserving
node allocation order, merge counts, support checks and `circuit_sha256`.

Predecessor credit:

- Douglas R. Colkitt — shared-point circuits, exclusion circuits, bit-compression
  screens and the historical certificates.
- Closest tooling priors on *different* objects: CrocSwap/integer-mult-bounds
  PRs #756 (balanced-Fano packed replay), #1793 (inplace-side prefix), #1861
  (parity-side basis/contains), #1922 (joint-frame cleared product), #1984
  (mixed-point scalar digests), #1994 (shared-point verify digests), #2039
  (partial-swap verify digests; explicit open question this package answers on
  the canonical constructor), #1874 (hosted-audit digest path), and #2001
  (ExclusionCircuit / DisjointTensor support masks — not touched here).

Prepared by Wentao Li with substantial AI assistance under Apache-2.0.
This is not independent human peer review and is not a formal proof of the
multiplication theorem.
