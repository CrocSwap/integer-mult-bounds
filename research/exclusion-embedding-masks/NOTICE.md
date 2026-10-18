# Notice

This package accelerates the historical reverse-frame expected-support check in
`scripts/exclusion_circuit.py:ExclusionCircuit.verify_embedding` while preserving
forward/reverse nesting assertions and embedding receipts. It deliberately leaves
Landed together with the leave-two-out closed form from open CrocSwap/integer-mult-bounds#2001 so both rewrite the same production file once.

Predecessor credit:

- Douglas R. Colkitt — exclusion circuits, shared-point circuits, bit-compression
  screens and the historical certificates.
- Closest tooling priors on *different* objects: CrocSwap/integer-mult-bounds
  PRs #756 (balanced-Fano packed replay), #1793 (inplace-side prefix), #1861
  (parity-side basis/contains), #1922 (joint-frame cleared product), #1984
  (mixed-point scalar digests), #1994 (shared-point verify digests), #2001
  (ExclusionCircuit.verify leave-two-out masks; explicit open question this
  package answers), and #1874 (hosted-audit digest path).

Prepared by Wentao Li with substantial AI assistance under Apache-2.0.
This is not independent human peer review and is not a formal proof of the
multiplication theorem.
