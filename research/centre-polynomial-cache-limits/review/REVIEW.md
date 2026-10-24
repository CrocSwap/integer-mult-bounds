# Independent agent review: centre polynomial and scalar-cache limits

Result: PASS for the two claims in the package `PROOF.md`. No material
mathematical or implementation defect was found. This is an independent
OpenAI Codex agent review, not human peer review or a formal-kernel proof.
The package does not give a native encoder, a complete supplier, or an
improved complete kappa value.

The checked package is
`work/project-final-cleanup-20261022/campaign-audit/centre-polynomial-cache-limits`.
`CHECKED-FILES.json` records the exact file bytes at review completion.
The PR description standard at
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`
was read. The coordinating agent must still check the final PR description,
GitHub source targets, and rendered Markdown.

## Bell Gram proof

The operator has the explicit definition
`A_lambda=(1/4) sum_q r_q r_q^T tensor Gamma_q^tensor(lambda)`.
The root coefficient occurs once. The 112 columns and their order are the
historical query columns, not the completed 120-root table. The scalar
word inputs match the two original archive members byte for byte at
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. The complete archive has SHA-256
`22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754`.
The interface bytes also match the published PR #4720 object at
`cb102a57254748651ce16aa4454bb611f6380e53`.

The retained sparse reviewer reconstructs R by a transpose calculation.
This review also reconstructs R in the opposite direction: it propagates
sparse rational source rows through all 10,851 scalar gates before the
centres phase. It sets all other inputs to zero. The result equals every
entry of the eight-by-112 interface matrix. This extra check does not
import either retained reconstruction function. It establishes the clean
query matrix only; it is not a new arbitrary-helper supplier check.

For odd q, the normalized real matrix `(X_q+Z_q)/sqrt(2)` is a symmetric
involution. Conjugation on the Pauli matrix `X^b Z^a` gives the two stated
Bell cases and preserves `c=a+b`. The retained reviewer checks all 57,344
columns in the selected `c=11` block by four-term Pauli multiplication.
It separately checks that the identity Pauli matrix is fixed by all
112 operators. The normalized doubled port agrees with the exact formula
in PR #1719's pinned `NATIVE-PROOF.md`; no phase is dropped.

The producer and separate sparse reviewer both give the 817 retained
moments and determinant 2,984 modulo the prime 65,537. The prime check
covers every possible divisor through its square root. The Hankel
determinant lies in `Z[1/2]`. Its nonzero reduction proves a nonzero
characteristic-zero determinant. This proves independence of the first
409 Krylov vectors and hence the degree bound. It does not require a
guessed recurrence or a claim about the exact minimal polynomial.

Tensoring the selected Bell block with the common fixed identity vector
in the remaining slots gives the same operator on an invariant subspace
at every positive tensor size. This proves the bound at each size,
including size-dependent candidate polynomials. A nonzero rational
minor remains nonzero after a characteristic-zero field extension.
For an invertible `aI+bA_lambda`, with `b != 0`, a polynomial inverse q
would make `(a+bt)q(t)-1` a nonzero annihilator. Thus `degree(q) >= 408`.
This is a representation bound, not a circuit-gate or native-cost bound.

All NumPy arithmetic used for the certificate is exact signed int64
arithmetic. The producer's largest absolute inner sum bounds are
262,144 for `R^T value` and 3,670,016 for `R acted`. The independent
sparse row bound is 14,680,064. The moment bound is 17,591,917,608,960,
which is less than `2^44`. Field products and the absolute difference
of the two nonnegative Bareiss products are at most `2^32`. Every bound
is below the signed int64 limit. The residue reduction occurs before
the next field product.

## Minimal invariant scalar cache

The theorem assumes a finite complex source space, fixed diagonal update
matrices, and a linear scalar cache that contains the query row space.
It does not give free source-dependent payload maps or source rereads.
Within this class, the proof is correct. A linear combination of the
updates separates the finitely many joint diagonal fibers. Polynomial
interpolation supplies each fiber projector. Every invariant cache that
contains the query must contain its row projections onto all fibers.
Their supports are disjoint, so their dimensions add. Conversely, the
direct sum of these fiber row spaces is invariant and contains the query.
The empty update family also satisfies the statement.

The rational checker reproduces the normal-direction dimensions
`8,15,28,44,44,56,56,56,56` and coordinate-direction dimensions
`8,16,31,53,85,101,112,112,112,112`. It verifies fourteen final normal
fibers, each with eight columns and rank four. It constructs the 56-row
basis, checks that it contains R, and checks every stated diagonal
update on every basis row. Removal of one necessary row fails a required
projected-row test. The 512 two-demand ranks are two of rank eight,
sixteen of rank fifteen, and 494 of rank sixteen. Exact rational rank
has the same value over C for these rational matrices.

The 56-row result applies only to the specified normal-character family.
Six specified coordinate characters force the full 112-dimensional
source space in this model. This is a useful exact cache-size criterion;
it does not price cache birth, native access, storage, or restoration.

## Reproduction and controls

From the workspace root, this review ran:

```sh
env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 work/autonomous-kappa-run/venv/bin/python -I -B work/project-final-cleanup-20261022/campaign-audit/centre-polynomial-cache-limits/replay.py --out work/project-final-cleanup-20261022/reviews/bell-cache/replay
env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 work/autonomous-kappa-run/venv/bin/python -I -B work/project-final-cleanup-20261022/reviews/bell-cache/check_review.py --package work/project-final-cleanup-20261022/campaign-audit/centre-polynomial-cache-limits --out work/project-final-cleanup-20261022/reviews/bell-cache/portable-replay --repo .
```

Both passed, under Python 3.14.7 and NumPy 2.5.4, with one numerical
thread. The first output directory was new. Its Bell producer and
review receipts equal the retained receipts byte for byte. The duplicate
row, duplicate column, and removed-cache-row controls passed. The extra
review script changed one moment and separately changed the interface
bytes in a scratch copy. The independent moment comparison rejected the
first mutation; the interface digest check rejected the second. Original
package sources were unchanged. The extra script accepts explicit `--package`, `--out`, and `--repo`
paths. It creates a new output directory on every run. Its source-history
check needs a Git repository that contains the cited historical objects.
It does not need the old workspace folder layout.

No full supplier, native decoder, selected-frontier replay, outer kappa
calculation, or formal-kernel proof was run. The all-size and general
cache conclusions follow from the displayed proofs, not finite samples.

## Credit and bounded overlap check

All five copied license/notice objects match the pinned Git source.
The new notice identifies the roles of the prior Codex research lanes,
credits the historical supplier notices, and distinguishes AI review from
human review. This review read PR #1719's pinned native lift proof,
PR #4750's fixed-code projector criterion, and PR #4720's QUERY-SPAN
theorem. The first supplies the port representation. The second tests a
given code, rather than its least invariant enlargement. The third gives
a different payload-query source-span bound. These are not claimed again.

A bounded search of research Markdown at current main
`cef4b52f2a59009865bf8eabde1be3f159063703` found no equivalent Bell
degree-409 or minimal diagonal-invariant cache statement. Broader
fiber/rank matches concern different E8 frame-capacity or partition
results. The parent-fetched list of 315 open PR titles and bodies had no
matching Bell/Hankel/phase-cache/scalar-cache/minimal-polynomial terms.
The search is recorded in the two overlap receipts. It does not cover
every open diff, Discussion, closed PR, or external literature result,
and it does not establish universal novelty.

The final two documentation edits add scoped open questions and remove
a redundant determinant sentence. They do not change a proof or checker.
No material review finding remains open.
