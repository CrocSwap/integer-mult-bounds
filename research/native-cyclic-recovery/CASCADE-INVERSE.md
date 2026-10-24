# Finite monomial cascade inverse

This is a sufficient, constructive consumer theorem. It does not assert that any of the claimed 9-, 10-, 14-, or 41-call producer schedules actually emits its required observations. No new κ is established.

Let W be a fixed positive integer and let H_0,...,H_(W-1) be phase-retaining Pauli monomials on a qubit address space. Define U on W arrays by (Uz)_k = H_k z_((k+1) mod W). Let M=I+U/2. Then U is unitary, U^(4W)=I, and

    M^-1 = [sum_(j=0)^(4W-1) (-1/2)^j U^j] / (1-2^(-4W)).

Every factor U is one literal role permutation plus one monomial address pass per role. Horner evaluation uses at most 4W such passes and 4W ADD passes, one fixed rational final scale, the unchanged observation array, and two owned work arrays. Thus this decoder introduces no additional recursive Gaussian child. Its native costs, storage and precision remain charged. It is not an unpriced dense inverse or oracle.

## Proof and all-width quantifier

Each diagonal block of U^W is a cyclic product of the H_k. The phase-retaining Pauli group is closed under products and every Pauli has fourth power I, including its quarter phase. Therefore every diagonal block has fourth power I and U^(4W)=I. The finite geometric-series identity gives M times the displayed polynomial equal to I on both sides. This argument applies at every tensor width f: tensorized Paulis remain Paulis; the coefficient 1/2 stays outside tensor products.

If H_k are pure XOR translations, they commute, square to I and their cycle product squares to I. Then U^(2W)=I and the same formula shortens to 2W terms. In the exact source examples, W=3 with shifts [1,2,4] and W=13 with shifts [1,...,13], the XOR sum is nonzero. The role cycle forces every period to be a multiple of W and the nonzero return translation forces an even multiple. Hence 2W is the exact order, for those literal operators at positive width.

For target observations v_k=K x_k + K G_k x_(k+1), write y_k=K x_k. The couplers in the y coordinates are H_k=K G_k K^-1. Clifford K conjugates a Pauli G_k to a phase-retaining Pauli. When G_k includes the scalar 1/2, factor that scalar out before defining H_k. Therefore the theorem recovers all y from genuinely emitted v. It does not create v from the original inputs; an actual chronological producer and its paid profile are prerequisites.

The norm bounds are ||M|| <= 3/2 and ||M^-1|| <= 2. The absolute sum of decoder coefficients is exactly 2, since the geometric sum numerator is 2(1-2^-L) for even period L. A perturbation of the input observations is therefore amplified by at most 2. The exact complete-cascade condition number is 3 in the inspected source examples, as already proved in PR #4842; the small Schur-return bound 9/7 or 8193/8191 is not substituted for this full condition number.

## Factored operational implementation

The supplied program also compiles V=U^W as a single monomial, including the exact accumulated phase; it does not perform W live data passes to apply V. Write beta=(-1/2)^W and let q=2 for pure XOR or q=4 for general quarter-phase Pauli routing. Then

    M^-1 = S_W(U) * [sum_(j=0)^(q-1) beta^j V^j] / (1-beta^q),
    S_W(U) = sum_(j=0)^(W-1) (-U/2)^j.

The two Horner evaluations need W-1 and q-1 monomial passes respectively, totaling W+q-2. This is 3 passes for each three-role XOR source and 13 passes for the thirteen-role XOR source; the quarter-phase three-role test uses 5 passes. The same number of ADD passes suffices, followed by the fixed rational scaling. Compared with the direct geometric polynomial, this reduces 6 passes to 3 and 26 passes to 13. The direct count was a constructive upper bound, not an optimality theorem.

The factored evaluation retains the observation arrays. At most three owned work arrays suffice for general q=4 with separate source and destination buffers; the q=2 case needs two. The Python executable also materializes one monomial routing table, charged as O(W N) index/phase storage. A native Pauli implementation can instead store the W composed Pauli descriptors and enumerate addresses, but this replacement is a mathematical implementation prescription rather than a benchmarked machine program. Compilation and final cleanup are separately charged linear work.

The coefficient absolute sum of the factored polynomial is again exactly 2: the sums are 2(1-2^-W) and 1/(1-2^-W). This supplies a bound for roundoff and perturbation; it does not make rational scaling free.

## Native interpretation

W and L are fixed. An address odometer implements the tensorized Pauli with one XOR/phase update per addressed scalar; all role routing, reads, writes, ADDs and fixed rational scaling are part of the finite bill. With coefficient precision p and word width w, general fixed-denominator rational arithmetic can be charged explicitly by d(w); a restoring-division fallback gives d(w)=O(w). This yields O(W L N d(w)) word operations and O(W N) scalar storage, with a constant depending on the fixed program. No hardware division instruction is assumed.

Magnitude and roundoff are bounded by a constant independent of width because the Horner multiplier has norm 1/2 and there are only L steps. Choosing p = O(log(2+B)+log N+log(1/δ)) suffices for bounded input magnitude B and requested global error δ, after retaining the input's exact scale. Word-address headroom must include all original, output, scratch and guard fields. The sufficient storage condition is 2^w >= c W N for an explicit implementation constant c; no input is silently overwritten or counted twice as productive data.

## Exact checks and provenance

cascade_free.py implements the polynomial directly using exact rational complex pairs. It checks every basis column of the actual permutation operators on dimensions 48, 96 and 208, and a signed quarter-phase Pauli case of dimension 24. CASCADE-ORIGINS.json freezes the exact source bytes of PRs #4818, #4819 and #4826. The checker explicitly compares all 7,168 source coupler entries and verifies K G_k = G_k K. For #4826 it evaluates only the exact constructor prefix through E3, never the dense recovery test. These source checks stay active under optimized Python. The last case has noncommuting phase-bearing couplers; a decoder which discards these phases is rejected. Normal and optimized Python both use explicit checks rather than assertions.

This leaf builds on hexapode's PRs #4818, #4819 and #4826 for the particular proposed cascade observations; Clear1nsight's PR #4842 for the exact full-cascade conditioning and producer-admission distinction; Dugongue's PR #4743 for the actual dirty native ports and monomial implementation; and the source lineage through Yiyang/Lyy-iiis #4710, lee-phys #4688 and Jacob Alan Sussman #4628. The finite-order geometric-series identity and Clifford/Pauli conjugation are standard facts, not claimed as new general mathematics. The contribution is a literal phase-preserving finite-pass decoder and explicit cost contract at this proposed consumer boundary. Prepared with substantial OpenAI Codex assistance, Apache-2.0.

## Open next question

Emit one of these observations from arbitrary independent inputs with an actual favorable paid Gaussian profile, retained source ownership, correct chronology and all-width phases. Then the present decoder can replace the unpriced dense recovery stage. A source which merely inserts K and E into a matrix does not satisfy the prerequisite. Compiler reserve, ordinary/outer admission, native precision and the full multiplication transfer must still be bound to the completed producer before any κ claim.
