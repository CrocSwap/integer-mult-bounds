# Independent review of the phase-section geometry

The review passes. No material defect was found in the algebra, the
norm bounds, or the stated line-power classification. The result is an
operator theorem. It does not give a complete native scatter or a
supplier cost improvement.

The reviewed proof is `native-escape-20261017/PHASE-SECTION-GEOMETRY.md`,
SHA256 `a3d970f070e6aaf67b79bd80d564cd7d653580f1f7fc1daadc3170dbdb9249ff`.
Read it with `PHASE-SECTION-GEOMETRY-SOURCES.md`, SHA256
`ae8ec52c10c77658190b996a529a405736e377ebc76e9804eaf73e7ff965cc97`.
The source qualification preserves the frozen proof and links the map
cost correction. No norm claim uses the withdrawn O(V) translation
shortcut.

## Independent exact checks

The checker reads the actual R matrix and the actual 112 line labels.
It forms B from the selected eight-column minor. It does not import
the producer's spectral, classification, or geometry checker.

- It verifies BD=13I with exact arithmetic.
- It forms all 512 real symmetric character matrices for T=BQ^2D.
- It proves that each matrix is annihilated by the product of the ten
  factors with roots -13, -11, -5, -3, -1, 1, 3, 5, 11, and 13.
- It proves that each of these ten roots occurs in at least one matrix.
  Since every matrix is real symmetric, these checks give the exact
  spectrum without a numerical eigensolver.
- It rebuilds the width-five odd-power mode from characters
  (1,2,3,6,6). The stated null vector is nonzero and lies in the kernel.
  The leading seven-by-seven minor of S_1 is -73. Thus the mode has
  rank seven. Its real phase also applies to S_3.

At any positive tensor width, the Q^2 sign depends only on the XOR of
the copy characters. All 512 XOR values occur. The ten-value spectrum
therefore holds at each positive width. The odd-power witness extends
to every width at least five by adding zero copy characters.

## Algebra review

Set A=BQ, D=B*, q=Q^-1, and T=BQ^2D. The identities BD=13I and
Q^4=I give AK_minus=AK_plus=I for

```text
K_minus=qD/13,       K_plus=QD T^-1.
```

Since AA*=13I, K_minus=A*/13 is the minimum-norm right inverse.
Every other solution differs from it by a vector in ker(A), which is
orthogonal to im(A*). The claimed minimum norm follows.

The identity K_plus* K_plus=13 T^-2 gives the five stated singular
values. The largest is sqrt(13), the smallest is 1/sqrt(13), and their
ratio is 13. The occurrence checks make all three bounds sharp.

P_plus=K_plus A is idempotent. Its image is im(QD), and its kernel is
ker(A). To check its exact norm, put U=D/sqrt(13). Then U is an
isometry and

```text
D T^-1 B=13 U T^-1 U*.
```

An isometric embedding preserves the norm of the middle operator.
The unitary Q factors also preserve norm. Hence ||P_plus||=13. This
does not assert that P_plus is an orthogonal projection.

The two isometries qD/sqrt(13) and QD/sqrt(13) have cross-Gram map
T/13. Its singular values give the stated principal-angle cosines.
Cosine one occurs, so the two phase images have a nonzero intersection.
The useful complement is im(QD) plus ker(BQ).

For an image constrained to im(Q^nD), injectivity of D gives a unique
coefficient map H. The right-inverse equation is S_(m+n) H=I.
Residues zero and two give the stated unique sections. At the singular
odd-power mode, S_(m+n) is not onto. This excludes a section even if
the choice of preimage is nonlinear. The conclusion has the stated
width restriction. It does not assert a minimum singular width.

Unitary stage routes that commute with their own port lines transport
these identities and norms. This is the route hypothesis used here;
the review does not claim free access between different stage charts.

## Cost boundary and validation

The map correction is
`native-escape-20261017/inplace-service-review/MAP-COST-CORRECTION.md`,
SHA256 `fbf9ef6d0069ab6b5d4ac8ad5daa480a88fdc8bc363cfacb309d47010e3f3c7f`.
The 144 simultaneous translations retain their declared packed-map
cost. The interleaved layout does not justify the withdrawn contiguous
bit-field shortcut. This correction does not change the exact inverse
or the geometry above.

The review ran the checker in normal and optimized Python modes. The
receipts were byte-identical. The command is:

```text
python3 -I -B check_review.py
PASS_INDEPENDENT_PHASE_SECTION_GEOMETRY
```

The optimized command adds `-O`. All final values use exact integer or
rational arithmetic. The checker uses one process. No new source or
target access, borrowed-state restoration, native emission, recursive
hosting, or complete supplier budget was verified in this review.

OpenAI Codex assisted the review. No PR, commit, or push was made.
Before a future PR description, read
/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md.
