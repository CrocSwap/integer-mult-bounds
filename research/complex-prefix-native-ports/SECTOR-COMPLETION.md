# A three-call completion of the repaired prefix on swap sectors

Prepared for Dugongue with substantial OpenAI Codex assistance. This is a sufficient all-input theorem on two explicitly stated input subspaces. It is not a five-array, fourteen-call unit and establishes no improved multiplication κ.

## Constructive theorem

Let V = C^8, let C_j = ((1+i)/2)I + ((1−i)/2)X_j, and put K=C_2 C_1 C_0. At every positive digit width f, write G_f = G^(tensor f) for each individual base letter G. Let T exchange address bits 0 and 2 and let σ be either +1 or −1. Suppose the input x satisfies T_f x = σ x. Then the target K_f x can be obtained by completing the actual PR #4710 two-call prefix with **one further paid call**, free maps/mixing and free scratch erasure. The total is three rank-one calls, with two data registers and no unaccounted extra input copy.

This theorem gives an actual continuation on both swap sectors, rather than only a rank or target-alignment test. The eigenspace can be prepared explicitly by e_σ=(I+σT_f)/2 when its complementary piece is retained elsewhere. Preparing that projector is not a license to erase the complementary piece of an arbitrary full input.

## Exact program and proof

Use the actual repaired prefix of Yiyang’s PR #4710, built on lee-phys’s PR #4688:

    S e_x = i^popcount(x) e_x,
    U = CNOT(0 to 2),   V01 = SWAP(0,1),
    P = S U S,          Q = S V01 S,
    F_f = C0_f (P_f + 2 Q_f) C0_f.

Execute its two-register schedule but retain the state immediately before the optional final erasure:

    t = C0_f x,     s = F_f x.

For the Q branch restore t using Q_f^−1, as in the repaired prefix. Its two paid calls and initial zero scratch are the actual predecessor schedule; neither P_f+2Q_f nor F_f is tensorized as a whole sum.

The predecessor’s exact separately tensorizable word identities give

    J_f W_f s = M_f C2_f x + 2 K_f a_f x,

where

    J = Z1 V01 C2             (one paid call),
    W = Z0 Z2,
    M = X1 V01 CNOT(2 to 0) Z1 S2 CZ02,
    a = Y0 Z1.

All of W,M,a are admitted free monomial letters or fixed free words. Apply W and then J to s, and call the resulting register u. Since T C0 T=C2 and T_f x=σx,

    C2_f x = T_f C0_f T_f x = σ T_f t.

Consequently the free update

    u <- (u − σ M_f T_f t)/2

returns K_f a_f x. The actual free Pauli

    B = K a K^−1 = −Z0 Y1

satisfies B_f^−1 K_f a_f=K_f. Applying B_f^−1 to u therefore returns the canonical target K_f x. Erase t by the same permitted singular free mixing convention as the predecessor and rename u as the output. The initially zero scratch is again zero. The only additional paid operation was the C2 inside J. This proves the construction at every f and for every vector in the stated sector.

Every product identity used above is first checked on the actual base letters and then tensorized **separately**. Coefficients 2, σ and 1/2 remain outside tensor powers. In particular the minus sign in B contributes (−1)^f inside B_f; replacing it by a width-independent minus sign would change the identity at even widths.

The maps P,Q,J,W,M,T and B are unitary. The prefix has Euclidean operator norm at most 3, and the newly completed formula uses one subtraction and a factor 1/2. This is a bounded explicit local arithmetic program. It does not replace the full native caller’s coordinatewise precision, conditioning, grouping or recovery analysis.

## Native implementation and sufficient precision

The sector continuation has an explicit bounded-array implementation. Let N = 8^f, let the ideal input have complex coordinate magnitudes at most 2^H, and request final absolute coordinate error at most 2^(-P). Assume each of the three charged rank-one Gaussian calls, on its actual input, returns its exact result with coordinate error at most rho. This is a stated accuracy contract for the existing Gaussian implementation, not an assumed new fast transform. All other address permutations and phases are exact; copies and erasures are ordinary charged array passes. Each scalar addition, shift or division is performed on a common dyadic grid with rounding error at most rho.

Choose rho = 2^(-(P + 2 f + 6)). Write L = 2^(f/2), an upper bound on the infinity operator norm of each Cj_f. Free monomial maps have infinity norm 1. The first output t has error at most rho from its Gaussian call. Its mixed input P_f t + 2 Q_f t has error at most 3 rho. After the second Gaussian call, its error is at most (3 L + 1) rho. After the third call J and the final residual subtraction and division by 2, the error is at most 4 L^2 rho when exact dyadic additions are used and only that final division rounds. Allowing a further fixed-grid rounding at each displayed scalar operation, and initial input quantization of complex error at most rho, gives the conservative bound 10 L^3 rho. This is less than 2^(-P) for every f >= 1. Initial quantization need not preserve the sector relation exactly: its discrepancy is included by applying the fixed linear completed program to the input error, whose infinity norm is bounded by the same conservative factor.

To justify the conservative constant without relying on cancellation, propagate errors through the actual schedule: input quantization contributes at most ((3 L^3 + L)/2) rho <= 2 L^3 rho; the first call contributes the same bound; the middle update contributes at most (L^2/2) rho; the second call contributes at most (L/2) rho; the third contributes at most rho/2; and the final division contributes at most rho. Their sum is at most 7 L^3 rho, hence below the stated bound 10 L^3 rho. Multiplication by 2, permutations, phases and copies are exact. Complex grid rounding is required to meet the stated complex-error bound rho, for example by rounding real and imaginary coordinates to half that tolerance.

Every exact intermediate coordinate is bounded by 3 L^3 2^H; increasing this to 2^(H + 2 f + 4) accommodates the stated rounding errors when H,P >= 0. A signed representation with P + H + 4 f + 12 bits per real or imaginary component therefore suffices for the displayed program. The Gaussian implementation's own separately charged internal guard is additional to this interface allocation. For f = O(log p), H,P = O(p) and p = Theta(log n), each field entry occupies a fixed number of ordinary C log n-bit words for a sufficiently large fixed C. No entire array is treated as a unit-cost word, and no unbounded-word multiplication primitive is used.

The displayed free schedule uses only a fixed number of passes over the two N-entry data fields. Every free letter is a fixed base-8 tensor monomial, so its address and phase stream can be generated in O(N) ordinary bounded-word operations. Maintain the f base-8 digits, the mapped address and the phase exponent modulo 4. On a carry, change only the affected digit contributions. The total number of changed digits over a complete N-address traversal is at most N + N/8 + N/8^2 + ... < 8N/7. A changed digit uses fixed table lookups, a shift by its precomputed place and a constant number of additions and bit operations. Initialization costs O(f), which is O(N). No multiplication or division instruction is needed by this address generator.

For an explicit in-place implementation, generate and store the N-entry permutation table with that odometer, traverse its cycles using an N-bit visited table and one temporary complex entry, and then clear both tables. This uses O(N) owned address workspace, charged O(N) stores for initialization and restoration, and does not borrow either data register as hidden independent input. The phase table can be generated in the same stream and applied in one additional pass. Alternatively a separately owned N-entry work field permits direct out-of-place scatter followed by copy-back and clear. Either implementation gives O(N) free-operation work and O(N) owned words in addition to the three charged Gaussian calls. A final clear costs N stores and restores the data scratch. The two-register claim refers to the algebraic data interface; native address workspace is explicitly charged here. This proves a costed, precision-explicit native subroutine on either stated sector; it does not create an independent full-array productive job or improve the complete supplier exponent by itself.

## An exact all-width identity criterion for further synthesis

Let g_1,…,g_D be pairwise distinct nonzero base matrices over C. If fixed scalars c_j satisfy

    sum_j c_j g_j^(tensor f) = 0    for every positive integer f,

then every c_j is zero. Indeed choose a linear functional ℓ on the finite-dimensional matrix space such that the numbers λ_j=ℓ(g_j) are all distinct and nonzero. Such ℓ exists because the finitely many conditions ℓ(g_j)=0 and ℓ(g_j−g_k)=0 exclude only proper hyperplanes. Contracting the tensor identity by ℓ^(tensor f) gives sum_j c_j λ_j^f=0 for f=1,…,D. Its determinant is the nonzero Vandermonde product times product_j λ_j, so all coefficients vanish.

Thus a fixed-coefficient finite word identity valid at every width can be verified by exact coefficient collection on the distinct actual base matrices. This justifies a finite group-algebra representation for searches using the finite Clifford group. It requires the **actual** matrices, including scalar phases. Projectively equal matrices with different phases cannot simply be merged. Width-dependent mixing coefficients require their own contract and are outside this fixed-coefficient statement.

## Finite geometry for a larger continuation

The standalone exact `finite_geometry.py` independently constructs the 10,752-element symplectic quotient of the free monomial-Clifford subgroup, its 14 rank-one Lagrangian neighbors and the 768-element common stabilizer of the reference and called Lagrangians. The stabilizer’s neighbor orbit sizes are 1,1,12. The dual quadratic-character orbit sizes under GL_3(F_2) are 1,7,7,21,28. This is an explicit finite search coordinate system; the quotient does not preserve the Pauli/central phases and is not itself a certificate for an all-width unit.

A useful extension of the sector port uses H-valued encodings. If A is an explicit free group-algebra coefficient, T A=B0 A, and B0 is free with C0 B0 C0^−1 also free, then

    C2 A = (T C0 B0 C0^−1) C0 A.

The proof is literal multiplication of T C0 T A and the assumed equality T A=B0 A. This supplies a concrete residual-cancellation port for an encoded channel. Any larger use must exhibit the actual coefficients and an injective complete input encoding, retain all complementary pieces, and count every call. No such five-in-fourteen continuation is claimed here.

## Evidence and credit

`verify_sector_completion.py` authenticates the pinned predecessor residual checker, independently assembles the actual Gaussian-rational matrices, verifies both sector projectors and completed targets, checks B’s absolute phase and rejects both wrong residual signs. Its finite matrix checks corroborate the separately tensorized all-width proof above. `finite_geometry.py` uses only exact binary arithmetic; no floating rank, solver, Lean build or full multiplication replay is involved.

Credit Yiyang / Lyy-iiis’s PR #4710 at b0d5192390af493d626054b060921895df3c94d2 for the repaired two-call prefix and residual identity; lee-phys’s PR #4688 at 264c4b3cb13c82d171de352ecf60486dfb8d2bd4 for the original prefix, inverse and rank engine; Jacob Alan Sussman’s PR #4628 at ee4fd87f064017c23e5a86fc1dcfe0a5237caed3 for the complex engine model and small-block problem; and their retained predecessors. Source URLs and hashes are in SOURCE-PINS.json. The new material is the explicit swap-sector completion and its canonical-output correction, plus the stated group-algebra synthesis criterion. No worldwide novelty or independent human review is claimed.
