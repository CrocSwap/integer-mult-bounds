# Notice

This package accelerates the historical partial-swap shared-point merge
construction in `scripts/partial_swap/shared.py:SharedPointCircuit.__init__`
while preserving node allocation order, merge counts, support checks and
`circuit_sha256`.

Predecessor credit:

- Douglas R. Colkitt — shared-point / exclusion circuits and the historical
  common-point motif.
- icekylinx — partial-swap producer adaptation of the shared-point circuit
  (`scripts/partial_swap/shared.py`, Apache-2.0).
- Closest tooling priors on *different* objects: CrocSwap/integer-mult-bounds
  PRs #756 (balanced-Fano packed replay), #1793 (inplace-side prefix), #1861
  (parity-side basis/contains), #1922 (joint-frame cleared product), #1984
  (mixed-point scalar digests), #1994 (canonical shared-point verify digests),
  #2039 (partial-swap verify digests; this package stacks on that tip and only
  rewrites `__init__`), #2054 (canonical `SharedPointCircuit.__init__` merge
  rewrite; this ports the same construction object to the partial-swap fork),
  and #2001 (ExclusionCircuit / DisjointTensor support masks — not touched).

Prepared by Wentao Li with substantial AI assistance under Apache-2.0.
This is not independent human peer review and is not a formal proof of the
multiplication theorem.
