# Paired-cube integration

This integration selects the conditional witness
`kappa = 4609169/10000000000 = 0.0004609169` from
[icekylinx's PR #144](https://github.com/CrocSwap/integer-mult-bounds/pull/144),
reviewed at `c8b22bc5c10dba497ac25804e27d9647d818e2ff`.
It is based on main `56b66d58297deca1d7dd130247d720e960f77a37` and retains
the original contributor commits as ancestors. The
[review](community-round6-review.md) and
[receipt](community-round6-validation.json) describe the pre-integration audit;
their statements about main's older state are historical audit observations.

The maintainer changes add optimized-Python rejection to the bit checker,
clarify the elementary inverse of signed scalar gates and refresh the two
corresponding certificate source hashes. Twelve subprocess modes test the
three public entry points under optimized Python. The exponent, inventories,
moments, guards and all assembly values are unchanged.

The README, contributor record, citation metadata, contribution guide and
status/reproduction pages identify this as the selected conditional result.
`certificates/selected-result.json` points to the exact proof, certificate and
review. Previous results retain their sources and credit. The README update
requires a joint-dual manifest refresh; its mathematical fields and prior
finite replay payload remain unchanged, with only provenance digests updated.

The construction's direct contributors are icekylinx, an664 (completed-core
sharing), eumemic (the restricted producer), Zhihao Chen (the physical bit
ledger), and Swapnil Jain (the underlying word and lifted frames). All earlier
framework credits, licenses and assistance disclosures remain in the source
manifests. This integration does not accept every claim in unrelated PRs or
close the remaining review queue.

Validation distinguishes the original audit from integration checks. The
source PR's 45 jobs passed, and its exact-head bit replay was inspected. The
original audit could not retrieve one compressed bit witness. After CLI access
was restored, the complete reviewed commit was fetched and the full selected
`make paired-cube-verify` target passed locally, including the selected bit
reconstruction. The new entry-point regression tests and independent arithmetic
check also pass; see the [local integration receipt](community-round6-integration-validation.json).
The unchanged full historical bit/frame audit remains supported by its earlier
CI evidence rather than a new complete local replay.

The integration branch runs the full repository workflow, including the
repaired bit checker, selected construction and deterministic certificate
checks, before main is advanced. The retained all-size analytic and fixed-tape
interfaces remain assumptions; this is not formal verification of the full
multiplication theorem.
