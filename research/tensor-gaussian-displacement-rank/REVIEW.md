# Independent mathematical review: flattened Gaussian displacement rank

Reviewed: `worker-a/research/tensor-gaussian-displacement-rank/PROOF.md`.
Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
Method: independent entrywise algebra and rank-factorization argument;
the package verifier was neither read nor used for this review.

**Outcome: the stated all-size algebraic theorem and its scoped generator
corollary are correct. No substantive mathematical defect found.**

## Boundary minors

With row index `(a,i)` and column index `(b,j)`, fast B coordinate last,
`(HZ-ZH)` cancels whenever `i>0` and `j<n-1`. Its support lies on the m
fast-zero rows and m fast-last columns, giving the claimed2m upper bound.
At row fast indices0,n-1 and column fast indices0,n-1, I independently
obtain block entries `RA`, `b0(AZ_m-Z_mA)`,0,`-AR`, with
`R=b_-1 I-b_(n-1)Z_m`. The minor determinant is
`(-1)^m det(R)^2 det(A)^2=(-b_-1^2)^m det(A)^2`.
The selected rows/columns are disjoint even when n=2. No invertibility of B
is used, and no genericity premise is hidden.

For Stein displacement, interior fast indices `i,j>0` cancel. Selecting
fast0,1 gives blocks `b0(A-Z_m A Z_m^T)`, `RA`, `AS`,0, with
`S=b_1 I-b_(-(n-1))Z_m^T`. Swapping the two m-column blocks has sign
`(-1)^(m^2)=(-1)^m`; the determinant is exactly
`(-b_-1 b_1)^m det(A)^2`. Thus both stated nonzero minors are valid over
an arbitrary field under their respective assumptions.

Minor wording clarification recommended: in section2.1, replace “its
determinant” after the sentence about R with “the determinant of this
2m-by-2m minor.” The displayed determinant is that of the block minor,
whereas `det R=b_-1^m`. The intended mathematics is unambiguous from the
display, but the pronoun currently permits the wrong antecedent.

## Inverse Stein orientation and persymmetry

The Sylvester identity follows directly by multiplying
`-H^-1(HZ-ZH)H^-1`. For the Stein identity, pivoting respectively on H and
H^-1 in `[[H,Z],[Z^T,H^-1]]` gives the two ranks
`N+rank(H^-1-Z^T H^-1 Z)` and `N+rank(H-ZHZ^T)`. This validates the
reverse-shift statement for general invertible H.

For a tensor of Toeplitz factors, full reversal is the tensor of factor
reversals and gives `JHJ=H^T`, hence `JH^-1J=H^-T`. Conjugating the
same-shift inverse Stein displacement by J and then transposing gives
exactly `H^-1-Z^T H^-1 Z`. Consequently same-shift rank equality is
correct in the stated persymmetric tensor setting; the proof correctly
avoids extending it merely from arbitrary invertible A.

## Gaussian nonsingularity and generator minimality

The Gaussian diagonal/Vandermonde factorization is exact. Each pair i<j
contributes `q^(-2j)(1-q^(2(j-i)))`; its total q exponent cancels the two
diagonal products, while v cancels between left/right diagonals. This yields
the displayed positive determinant. Tensor-axis permutations then make
the fastest-factor formula and its minimum immediate.

Entrywise, `L(u)U(v)=sum_k Z^k u v^T (Z^T)^k`. Applying Stein telescopes
to `uv^T`, proving the lower bound on term count. Conversely any exact
rank-r factorization of E(X), followed by that finite nilpotent sum,
recovers X exactly, so r terms suffice. The minimum is therefore precisely
the displacement rank, not only an upper bound. This applies to H and H^-1
after the independently verified inverse-rank step.

The exclusions are appropriately scoped. The result is for exact ordinary
lower-times-upper Toeplitz generator sums and fixed lexicographic axis
orders, not arbitrary permutations, approximate rank, shared-work runtime,
or tensor-circuit complexity. The conditional rounding discussion explicitly
requires structure and nonsingularity and does not infer them from a
nonzero ideal minor alone. No new kappa or assumption discharge is supported
or claimed by this mathematical result.

Root closeout clarified which2m-by-2m minor determinant is computed; no mathematical change. Registered replays and exact-base pins pass. VALIDATION.json records the shallow-history gate refusal.
