# Research record and reusable routes

The frozen sweep covered 453 PR entries and 69 new or changed heads since the previous
snapshot. All changed descriptions/comments were downloaded. Full source downloads were
selected for PR425,433,445,447,448,449,450,451,452,453. We did not rerun unchanged full public
verification chains or refresh the public snapshot while packaging.

## What survived

- Global integer pooling of WHOLE residuals: implemented for both suppliers. Packing is
  nominated by native HiGHS and then validated in exact integer arithmetic, independently
  of the optimizer. No optimizer or floating solution is trusted at replay.
- Invocation-specific selection of COMPLETE equivalent programs: variants removing one,
  two, or three entrance pivots were tested. The final witness uses only the two-pivot
  variant at five reverse calls; the other complete variants are discovery results.
- Two partial-prefix recoveries after PR450 target mixing: fully emitted and checked,
  but explicitly credited as reuse of earlier target-prefix work.
- Conservative norm-product accounting: avoids reliance on independent replica growth.

## What was rejected or not claimed

Initial coordinate-flow nominations split one residual between physical families. Some
placement and column checks passed, but they did not prove the required operator identity.
PR451's trace obstruction refutes that derivation. The earlier larger prices and rank137
split-portfolio candidates are withdrawn, not included in this deliverable's kappa.
A matrix-address factorization is not an array-family direct sum. No invertible-conjugation
repair can change trace. Higher PR453 numerical claims using that derivation are therefore
not our benchmark; this artifact improves the retained whole-residual PR451 construction.

Multi-donor/prefix and reverse-time searches did not produce an additional fundamentally
new positive mechanism beyond the selected prefix ports. That is a bounded search result,
not an impossibility theorem. PR452's speedup prototype was reviewed but not used.
None of the floating search bounds is an exact optimum or global upper bound.

## Structural retrieval from other work

We retrieved six bounded structural query classes from the shared typed DAG (up to80 hits
each) and inspected relevant sources; this was not exhaustive kernel re-verification.

- Mathlib `Data/Matrix/Block.lean`, `Matrix.blockDiagonal_mul` and its unequal-size variant:
  composition of independent complete maps motivates whole-program portfolio substitution.
- Project `MUBProjectionInduction20260923.lean`, `atoms_mul` and `weighted_mul`:
  orthogonal idempotent factors support SAME-FAMILY residual/complement composition.
- Project `LinearAlgebra/Matrix/DeterminantalComplexity.lean`: explicit block reindexing
  motivates whole-slot relabeling, not cross-family splitting.
- Project `TISLTransvectionWord` and Mathlib transvections motivate the reused chronological
  setup/recovery shear identity. It is not a new technique in this submission.

These are mathematical analogues and checked source references, not imported certificates
for the multiplication theorem. The two new uses in this finite construction are the global
whole-owner allocation domain and joint call-program/storage selection. Novelty beyond the
reviewed repository snapshot is not established.

## Useful next experiments

The complex supplier binds. A further valid improvement must change its complete paid
profile or a genuinely charged shared resource. Test pooled whole blocks at larger replica
counts, joint choices among independently correct complex programs, and exact integer
packing with physical-window constraints. For the bit side, retain the program-portfolio
variable while searching compatible whole-owner allocations. Admit a candidate only after
operator semantics, all dirty columns, actual physical owners, coefficient bounds, emitted
costs, and the full joint assembly agree. Never optimize a split inventory lacking an
operator-level realization, and never add separately estimated kappa gains.
