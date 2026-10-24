# Independent review of the dirty-target prefix and sector continuation

This review accepts the stated interfaces and does not certify a new multiplication exponent. The predecessor is the phase-repaired prefix of Yiyang / Lyy-iiis, PR #4710, built on lee-phys's PR #4688 and Jacob Alan Sussman's PR #4628. The new interface preserves an arbitrary independent second input instead of assuming a zero target.

## Two-call all-input theorem

For each positive width f, let A = C0_f and L = P_f + 2 Q_f, with each individual base letter separately tensorized. Starting from arbitrary independent arrays (x,y), compute t = A x, add P_f t + 2 Q_f t to y, and apply A to the second array. The exact output is

    (A x, A y + A L A x).

There are exactly two charged rank-one calls. In block notation U = [[A,0],[A L A,A]]. Its inverse is [[A^-1,0],[-L,A^-1]]. Both block multiplication orders give the identity. Each inverse Gaussian is one forward call followed by its literal translation, because Cj^-1 = Xj Cj. The reverse program therefore uses two calls. There is no target-zero assumption and no unreturned independent input copy.

A is unitary and norm(L) <= 3. Factoring U into two unitary block-diagonal maps and [[I,0],[L,I]] proves norm(U) <= 4 and norm(U^-1) <= 4, uniformly in f. The condition number bound 16 applies to the complete two-output map. This proof is valid for arbitrary complex input arrays, not just a tested subspace.

## Three-call full-input triangular interface

Let D = J_f W_f A, where J contains one charged C2 call. Applying J_f W_f to the second output produces

    (A x, D y + (M_f C2_f + 2 K_f a_f) x).

The two predecessor word identities identify the two summands separately. Since the off-diagonal block equals D L A, the inverse is exactly [[A^-1,0],[-L,D^-1]], with three calls. D is unitary, so the same norm and inverse-norm bounds 4 hold. The term D y must remain in the statement; omitting it is false for arbitrary y. It is not an additional productive full Gaussian output.

All scalar coefficients 2 and -1 remain outside tensor powers. In particular, the bottom-left inverse block is the width-level negative -L, not the tensor power of a base matrix -L. Replacing a base Pauli by a projectively equal representative also changes even-width behavior and is disallowed without accounting for its phase.

The source also supplies a free algebraic inverse for L. With R = P_f^-1 Q_f and R^4 = I, multiplication of the geometric polynomial proves L^-1 = -(I - 2 R + 4 R^2 - 8 R^3) P_f^-1 / 15. Since these four monomial terms have total absolute coefficient (1 + 2 + 4 + 8) / 15 = 1, the inverse infinity norm is at most 1, uniformly in f. This is a useful precision guarantee. Exact division by the odd denominator 15 is not exact dyadic-grid arithmetic; numerical use must explicitly charge its precision, rounding and native instruction implementation. The two-call and three-call forward/reverse schedules above do not need this coupling inverse.

## Three-call sector completion

For T exchanging bits 0 and 2 and epsilon in {+1,-1}, assume T_f x = epsilon x. Then C2_f x = epsilon T_f A x. The explicit residual subtraction, division by 2 and output Pauli correction therefore recover K_f x from the three-call clean-prefix program. The output correction must be the tensor power of the actual phase-bearing B = K a K^-1 = -Z0 Y1. This includes the parity-dependent central sign and is correct at even widths.

The sector theorem is sufficient on the specified input subspace. It does not produce a complete full-input solver by discarding the complementary projection. Its permitted final scratch clear is a charged singular operation; the reversible full-input norm theorem does not claim that this erasing map has an inverse.

## Native cost and numerical contract

The documents charge each free monomial, mixed update and workspace initialization or restoration as an O(N) array pass, N = 8^f. This is necessary: a complete field is not a native word. Their address odometer has amortized constant work per address, with O(N) explicitly owned address workspace or an explicitly owned scatter field. The Gaussian implementations' internal guard and time remain separately charged.

The stated error budget is conservative and valid under its explicit accuracy contract. With L0 = 2^(f/2), three-call forward error is at most 10 L0^3 rho after input quantization and call errors; rho = 2^(-(P + 2 f + 6)) is sufficient for coordinate error below 2^-P. This assumes the displayed free integer additions and phase changes are exact on the allocated grid, or that any additional rounding is included in the budget. The stated P + H + 4 f + 12 coordinate bits cover the displayed program for nonnegative H and P. This is not a fresh implementation of the charged Gaussian calls.

## Independent evidence

verify_word_review.py authenticates the frozen PR #4710 residual engine with SHA-256 0d277854396e4ceda1e0f26916bd576b6decb474c0692b6671ebf2595283ddb9. It independently executes the actual two-register vector schedule at widths 1 and 2, using exact Gaussian rational coordinates. It passes 60 identities, including both sector signs, dirty-target inverses and phase-correct canonical outputs, and 12 controls showing that the dirty baseline is retained. It does not tensor a sum or discard the second input. Run:

    python -I -O -B verify_word_review.py .

The universal proof is the literal block multiplication and separately tensorized predecessor word identities above; finite tests are corroboration. This is independent computational review by another Codex worker, not independent human review or a kernel formalization. No completed supplier, paid-profile improvement or new kappa is established by this leaf.
