# Volume IV author review

Scope: D001–D100, all 100 statements and their English proofs. Informal review only; this is not a Lean kernel certificate or a global novelty assessment.

The volume contains 100 proved entries and no conjectures. The finite-dimensional spectral theorem, elementary calculus, polynomial division, and determinant identities are declared background. Every claimed result has an explicit proof and a use; source hooks identify inspected precedents without importing unnamed project assumptions.

## Corrections and mathematical checks

- D022: checked the full majorization induction, including ordering and the residual prefix inequalities after mixing adjacent coordinates. Concavity alone suffices; no monotonicity assumption is introduced.
- D031–D040: checked the nonzero-Hilbert-space shear formula, multiplicativity of tensor operator norms, weighted Schur scaling, and coherent gauge cancellation. Arbitrary mixing between blocks is not assumed to preserve a product estimate.
- D045: checked the invariant metric has off-diagonal entries −a/2. The opposite sign is incorrect. The strict parameter range |a|<2 makes the metric positive definite.
- D053–D059: separated distinct nodes, repeated-node aggregation, nonzero signed weights, and positive flat extension. D058 uniqueness is restricted to at-most-N-atomic measures. D059 uses a positive definite smaller Hankel matrix and an actual flat larger one, constructs the self-adjoint shift, and proves positivity and uniqueness rather than assuming a representing measure.
- D060: checked that the Lagrange coefficient bound controls the columns of the inverse Vandermonde, hence the stated infinity-norm reconstruction error.
- D062–D070: checked that the moment extension is constructed rather than assumed; quadrature positivity, resolvent error, and Galerkin energy statements use their explicit positivity/spectral hypotheses.
- D072: the separated-normal Sylvester estimate is a Frobenius-norm estimate. No dimension-free operator-norm bound is inferred.
- D077: checked group-average intertwining by the reindexing g=kh. Uniform representation norms are required for the stated defect estimate.
- D083–D086: checked the Duhamel generator calculation, the second-order local error, the Taylor coefficient match for Strang splitting, and unitary telescoping for global error.
- D090: corrected q=(b−a)/(b+a) to q≤(b−a)/(b+a), because the spectrum need not attain the declared interval endpoints. Both the section source and assembled volume were corrected with a source-hash guard.
- D091–D097: checked the sign in generalized Vandermonde positivity, positive-node Cauchy–Binet, moment localizers, reflection/inversion support hypotheses, and the explicit Bernstein degree bound, including k<j and constant polynomials.
- D100: laziness is stated; without positive identity mass a periodic walk need not have strict contraction on the mean-zero space.

## Source scope

Actual canonical source text was read for the five paths in ../sources/04-sources.json. Bounded read-only queries of the authoritative DAG are in ../sources/04-dag.json. Historical namespace and source-catalog results are not described as fresh checked imports. Source inspection and a matching source hash are not kernel verification. No source file, DAG, configuration, or persistent proof service was changed.

The library's infinite-support meromorphic discussion is not used as a theorem. The finite Hankel identities and finite Vandermonde arguments are proved here independently. Primary literature attribution is recorded in ../sources/04-literature.json.

## Residual limitations

Human-readable proofs can retain errors despite author and peer review. The collection reconstructs classical tools and local bridges; its 100 entries are not 100 globally new theorems. Mathematical peer review is recorded separately in 04-peer-review.md, against the final source revision or with an explicit correction record.

## Independent-review corrections and overlap repair

The independent reviewer requested D036 positive matrix size, D043 nonnegative r, D086 nonnegative time, and D099 scalar or nonzero Hilbert value space. All four were corrected in the section source and assembled volume with source-hash guards, and read back by the reviewer. D074 was then strengthened to the rectangular closest-isometry theorem, with exact operator and Frobenius minima and a unique Frobenius minimizer; D076 now explicitly uses its square specialization. This distinguishes the main conclusion from B085 while retaining the shared polar error estimate. The reviewer read both changed entries again. The final review file records the revision hash.
