# Independent peer review — Volume II

Reviewed every statement and proof/evidence block B001–B100, including the final replacement proofs B030,B094,B097,B098. The final B030 replacement was read back separately after the full-volume review; all other entries were reported stable by the author and root. This is an English mathematical review, not a Lean/kernel audit or a comprehensive literature-status certification.

Verdict: no unresolved mathematical error found in the reviewed revision. Exactly100 IDs remain, with93 proved entries and7 explicitly conjectural targets. Minor scope corrections requested during review were incorporated.

## Detailed sensitive checks

- B005–B010: symplectic quotient counts, graph parametrization and field-multiplication spread construction work in characteristic two. Alternating, rather than merely skew-symmetric, is the correct hypothesis.
- B028: requested an explicit finite-group hypothesis because the proof sums over G; incorporated by the author.
- B030 replacement: the full-row-rank hypothesis makes S=FΣ⁻¹F* positive definite. For any exact competing reconstruction, K=L−L₀ has KF*=0, killing both covariance cross terms. The positive additional covariance KΣK* proves the stated order comparison; its trace is ||KΣ¹ᐟ²||²_F, so equality forces K=0. All matrix dimensions and the measurement covariance interpretation agree. No Gaussian assumption is required. This weighted Gauss–Markov conclusion is substantively different from the former rank-one inverse update.
- B033–B037: constant-diagonal compression gives the prescribed equal norms; spectral tetris borrows only from an untouched row with original budget at least two, and final-row integrality follows from total trace minus used unit columns.
- B041–B050: checked tensor-space dimensions and every displayed projective-design/tomography normalization. Entrywise contraction in B043 yields A, not its transpose. SIC simplex rank and reconstruction constants agree. Product tomography claims recovery, not a global projective-design identity.
- B055: requested explicit complex-linear extension from the Hermitian decomposition for a general trace-one complex matrix; incorporated. The formula is correct.
- B058–B060: commuting d−1 independent traceless residual matrices plus identity span the actual diagonal algebra. The channel commutator identity has the correct factor two and uses the exact unital sum-of-squares hypothesis. These are sufficient certificates, not assertions that their inputs always exist.
- B068–B070: the Weyl commutator is the stated trace-symplectic scalar. Each isotropic class gives q independent commuting normal matrices, hence the full q-dimensional diagonal algebra. This resolves joint-eigenspace multiplicity without any division by two. Disjoint nonidentity labels imply orthogonal contrast algebras. Thus the complete prime-power construction genuinely covers p=2, with no assumed missing-basis oracle.
- B077–B080: Seidel roots produce a positive Gram factor; conference multiplicities and sparse Steiner-frame scaling are correct. Weighted support reduction preserves moments and trace, but does not equalize weights, as stated.
- B081–B084: square orthogonality plus the flat codimension-one core determines every border modulus. Partial-column completion preserves old columns. Applying the same core identity to each cross product proves all cross overlaps, not only the supplied subblock. Cofactor normalization stays inside a conjugation-closed field, but the author correctly does not infer a root alphabet from field membership alone.
- B085–B090: operator versus Hilbert–Schmidt norms are tracked; squared-overlap repair has the correct factor two. The contraction existence certificate includes identities implying all omitted residuals, a self-mapping ball, an invertible preconditioner and a strict contraction bound. Numerical smallness alone is not promoted to existence.
- B094 replacement: quadratic-character correlation follows from the invertible two-variable change with product a²; skew symmetry uses q≡3 mod4. The block signs in the bordered Paley matrix give vanishing cross terms and lower Gram (q+1)I.
- B097 replacement: autocorrelation coefficient equality follows from the prime cyclotomic minimal polynomial; coefficient sum gives L=p−2, then the square/count equality forces all root multiplicities to be zero or one. The resulting missing-root formula makes every phase of the normalized complement a pth root. Includes p=2. Requested explicit minimal-polynomial justification; the author added the translated Eisenstein polynomial and identified the criterion as standard background.
- B098 replacement: for each uncovered h, no old L lies in h-perp because L=L-perp. The exact hyperplane count puts all holes in h-perp. Bilinearity then makes their span isotropic; its cardinality forces dimension n and equality with the hole set. This proves closure and unique completion, not merely assuming closure as in B008.

## Conjectural scope

B091–B093 concern genuine universal MUB/SIC directions with supplied constructions only in verified special cases. B095,B096,B099,B100 are explicitly proposals whose global status is not established by the bounded source search; no novelty or open-status guarantee is inferred. Qualitative compactness in B096 does not prove its quantitative exponent. The gap case in B099 proves only its explicitly restricted scale. Weighted compression and spherical O(d²) results are correctly distinguished from B100's distinct uniform projective-ray target.

## Cross-volume distinctness

Flagged exact repetitions C081/B011, C082/B013 and C083/B001–02; root authorized replacing C081–83 by Möbius inversion, orbit counting and weighted Pólya enumeration. Also flagged B085/D074 polar-factor overlap; root reports D074 was strengthened to rectangular nearest-isometry optimization in both operator and Frobenius norms, with uniqueness of the Frobenius minimizer. That stronger main conclusion is distinct from B085, and overlap in its bound will be noted. No B source edit was made by this reviewer. B061 character orthogonality versus C087 Fourier inversion/Parseval and D099 convolution norm are related but have different substantial outputs. B019 and C088 use different regular/biregular spaces and explicit operator norm hypotheses.

Coverage is all100 entry bodies and the bibliography in the stated revision. Recent-source claims were examined as attributed, bounded retrieval evidence; this review did not independently reproduce external major classification or existence proofs. No sourceGoal, conditional completion premise or numerical witness was used as an unconditional theorem.

Reviewed draft SHA-256: 27220ab0574912297f80379869d39e8b2a7dc83edbfa6d07c36e87985eaa35c3
Reviewer: Volume III worker, independent from Volume II author.

Final readback: B030 passed independent review in the final revision above;100 sequential IDs and93 English proof blocks remain. No unresolved correction request remains.
