# Notice

This package accelerates the historical mixed-point scalar digest in
`scripts/audit_mixed_point.py:scalar_check` while preserving the mixed-point
and early-sharing mathematical screens.

Predecessor credit:

- Douglas R. Colkitt — mixed-point circuits, source/target-span frame cuts,
  early-sharing screens and the historical certificates.
- Closest tooling priors on *different* objects: CrocSwap/integer-mult-bounds
  PRs #756 (balanced-Fano packed replay), #1793 (inplace-side prefix), #1861
  (parity-side basis/contains), #1922 (joint-frame cleared product), #1217
  (ternary frame-pair memoization), and `research/rational-containment-performance/`
  (mixed-point `contained` adapter).

Prepared by Wentao Li with substantial AI assistance under Apache-2.0.
This is not independent human peer review and is not a formal proof of the
multiplication theorem.
