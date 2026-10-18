# Independent informal peer review of Volume IV

Reviewer: Volume I algebra worker. Scope: read every statement and proof D001–D100 in the actual Volume IV draft, not only its headings. Review input was SHA256 ac0c2492ff36d0c688202bf0b32e5b166ff2d4659582adc1638d3f080d854949 (the first35entries read at that hash; later reads included the already announced D090 correction). No source edits, Lean runs, or independent external discovery claims were made. This is mathematical peer review, not formal certification.

## Corrections requested from the owning author

1. **D043, definite false boundary:** add r≥0. As written Q=I, A=I, r=−1 satisfies A*QA≤r²Q but its n=1 asserted bound is negative. The proof and intended result are correct with r≥0.
2. **D086, missing time hypothesis:** add t≥0 (or reformulate every odd power and exponential with |t|). As written its RHS is negative for t<0, so it cannot bound a norm in general. The positive-time proof is valid.
3. **D099, zero value space:** require scalar-valued functions or a nonzero Hilbert value space. D098 allows Hilbert-valued functions in the zero space; the resulting operator has norm0 while the scalar multiplier maximum can be1. The Fourier proof is correct on a nonzero value space.
4. **D036, empty size convention:** specify positive matrix size before using max_i(1−1/w_i), or explicitly treat a zero-dimensional space separately. This is a definitional boundary, not a substantive obstruction.
5. **D090:** the owning author had already changed equality for the SPD interval estimate to ≤; the corrected actual statement was read and is correct.

## Positive mathematical checks, by full coverage

- **D001–D010:** differentiated tilt weights, finite variance, exponential-series factorial constants, entropy equality case, binary Pinsker curvature and concentration optimization checked. The characteristic issue does not arise here because distributions are real.
- **D011–D020:** positive-rate root existence, global inverse range, implicit derivatives, signed-time integral Taylor formula, amortization strictness, second-order expansion and rational series tails checked. Local root and bracket hypotheses are explicit.
- **D021–D030:** the constructive majorization induction D022 was checked with its sorted residual w; its prefix comparison works on both sides of k. Endpoint termination D023 and minimizer-with-most-endpoints D024 are valid. The power-integral constants D028 and Hölder exponent D030 agree.
- **D031–D040:** scalar shear eigenvalues, tensor singular values, direct-sum no-independence argument, weighted Schur factors, positive resolvent weights, path sums, complete-prefix typing and coherent-gauge telescoping checked. D036 has only the empty-size caveat above.
- **D041–D050:** forcing indices, adjustable splitting, paired-shear invariant Q, Hermitian growth, Lyapunov-series convergence, metric conditioning and observability left-inverse norm checked. D043 needs the stated sign correction.
- **D051–D060:** transpose orientation and aggregated signed nodes checked. In D059, the last-column identity H_N a=b makes J self-adjoint; the cyclic vector yields N distinct eigenvalues and positive spectral weights. Its Schur complement supplies exactly m_2N, and positivity of P² proves uniqueness among all positive representing measures. Lagrange coefficient bound D060 has the correct induced1/infinity norm orientation.
- **D061–D070:** flat-extension construction, repeated-Rolle Hermite remainder, Christoffel minimizer, exact resolvent identity, finite geometric tail, variational compression and Chebyshev trial-polynomial degree checked. Positivity and support assumptions are retained.
- **D071–D080:** ordered power telescoping, Frobenius-only Sylvester coercivity, polar inverse margin, self-adjoint polar intertwiner, finite averaging reindexing and complete-positive projection checked. Approximate conclusions are not mislabeled exact.
- **D081–D090:** Duhamel sign, unitary factor norms, two nested commutator integrals, telescoping n-step bounds, symmetric-series coefficients through degree2, Taylor majorants, log-det congruence and Neumann tail checked. D086 needs t≥0.
- **D091–D100:** exponential zero count and Vandermonde sign, Cauchy–Binet signs, localizing Jacobi matrix, finite symmetry moment certificates, Bernstein product errors and degree-elevation coefficients checked. D099 needs a nonzero value space. The lazy mixing result correctly distinguishes the trivial character and states a mean-zero domain.

## Disposition

All100 entries received an actual informal mathematical read. No further mathematical flaw was found after the explicit fixes above; the required corrections were sent to the owning author. I do not certify that they have been applied until the final draft hash and corresponding text are rechecked. Standard results and the explicit sufficient bridge structure are credible; this review makes no novelty or computer-kernel claim.

## Final correction readback

The actual D036,D043,D086,D099 statement-and-proof blocks were reread in final draft SHA256 a46e779467ef31f46757e4e4227ba7aa2faf7cc1b96cd0630d9ea2ff4e738899. All four requested corrections are present and mathematically resolve the findings. The scalar/nonzero-Hilbert Fourier norm attainment argument is explicit. D090 was already corrected. The100-entry informal review therefore has no unresolved mathematical finding at this final snapshot.

## Rectangular polar strengthening readback

At final draft SHA256 c5bfd24ad0329c6f9ceb5eb5e5d3717372b1f715872c9128d096edd482076816 I reread D074 and D076 in full. The thin-SVD argument correctly proves the operator-norm lower bound on each right singular vector, simultaneous attainment by the polar isometry, and unique Frobenius minimization because every positive singular weight forces equality in the unit-vector inner products. The rectangular dimension and positive domain size assumptions are explicit. The square specialization retains the inverse bound needed by later arguments, and D076 now explicitly assumes square X. No new finding.

## Final Vandermonde index alignment

Final Volume IV SHA256 cab130df9857ab46b1cb55bda3c7cdfc797b67b0f64895f7058dd2d03e3169c3: D091 was reread. The statement now specifies r≥1 and the two Taylor-leading determinants consistently use indices1,…,r with exponent k−1. Their signs and factorial denominator agree with the proof. This corrects presentation without changing the argument; no unresolved finding remains.
