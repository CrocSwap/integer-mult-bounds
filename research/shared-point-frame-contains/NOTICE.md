# Notice

This package accelerates the historical shared-point frame nesting check in
`scripts/shared_point_circuit.py:SharedPointCircuit.verify_frames` (and the
`support_in` / `contained` helpers it uses) while preserving nesting predicates
and receipt fields.

Predecessor credit:

- Douglas R. Colkitt — shared-point circuits, exclusion circuits, bit-compression
  screens and the historical certificates.
- Closest tooling priors on *related* shared-point surfaces:
  CrocSwap/integer-mult-bounds PRs #1994 (verify digests; merged) and open #2054
  (`__init__` merge construction). This package leaves both alone and targets
  the residual `verify_frames` / `support_in` LRU thrash.
- Quality-bar priors on *different* objects: #756 (balanced-Fano packed replay),
  #1793 (inplace-side prefix), #1861 (parity-side basis/contains), #2117
  (DisjointTensor.frame_data).

Prepared by Wentao Li with substantial AI assistance under Apache-2.0.
This is not independent human peer review and is not a formal proof of the
multiplication theorem.
