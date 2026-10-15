# Structured boundary solves (new in this package)

> **Package note.** This construction is retained as an alternative but is **not used** by this package's kappa: with fine source-prime padding the boundary row is not binding (xi = 0.908 < epsilon), and the explicit Strassen boundary of PR1786 is used (outer/FINE-PADDING-COMPOSITION.md). The numbers in sec. 7 below belong to the earlier package.

**Status.** This construction is a new contribution of this package. It builds on Vlado Vojdanovski's PR1673 (capped phase-cell fusion: the interior/boundary factorisation, the no-pivot boundary solver, the audited
conditioning bounds BILATERAL-LDU.md, FORWARD-SMALL-A-AUDIT.md, LOG-A-PHASE-SCHUR-AUDIT.md, PHASE-LAYOUT-AUDIT.md), on the radix-distributed union schedule (pkg4, outer/UNION-SCHEDULE.md) and on the classical structured-matrix
theory of Gohberg and Semencul (inversion of Toeplitz matrices, 1972), Kailath, Kung and Morf (displacement rank, 1979), Bitmead and Anderson (1980) and Pan (structured matrices and polynomial computations). It replaces the dense/fast-rectangular
products of the boundary algebra (pkg1 to pkg6: W x W blocks against W..W^k right-hand sides at cost W^tau) by applications of generator representations of the blocks: O(r W log W) ring operations per right-hand-side column, i.e. polylog(p) per entry.
The boundary row then has exponent epsilon - xi + 1/2 + o(1) (tau_eff = 2 + delta for every fixed delta > 0; tau_eff = 2 itself is not claimed). All inherited all-size hypotheses of PR1673 remain. The package pkg6 (rectangular k = 5, tau_eff = 2.1567081) is the fallback.

## 1. Where the structure comes from

Within one phase cell, with the notation of the note and of BILATERAL-LDU.md (rho = 1 + theta, q_i = floor(rho i + 1/2) = i + k on the cell's stretch of constant offset k, beta_j = rho j - q_j = theta j - k),
G_ij = exp(-a[(rho j - q_i)^2 - beta_j^2]). Expanding with rho j - q_i = (j - i) + beta_j gives the exponent (j-i)^2 + 2(j-i) beta_j = rho (j-i)^2 + theta (j^2 - i^2) - 2k(j - i), hence **exactly**

  G = D_r T D_c,  T_ij = exp(-a rho (j-i)^2) (Toeplitz), (D_r)_i = exp(a theta i^2 - 2 a k i), (D_c)_j = exp(-a theta j^2 + 2 a k j).

(The same factorisation, with a, rho and the offsets of the forward map, holds for the broad forward operator H of FORWARD-SMALL-A-AUDIT.md, which is itself a symmetric Toeplitz matrix after the anchored diagonal gauge, and for the augmented Haug = E H C + (I - E C),
which is permutation-similar to H (+) I.) The truncation to bandwidth W (rows farther than W are below 2^-P and are zero in the retained rounded matrix) keeps T banded Toeplitz. Cells are separated by physical cuts, which the note already makes boundary coordinates, so no block of the
boundary system couples two cells; the cell-wise offset k only enters D_r, D_c.

**Diagonal cancellation.** In the interior/boundary decomposition the Schur complement S = D - C A^-1 B and every step of the block LU are built from products K_{ab} K_{bb}^-1 K_{bc} with K = D_r T D_c;
D_c(b) D_c(b)^-1 and D_r(b)^-1 D_r(b) cancel, so in the coordinates Y = D_r^-1 X D_c^-1 *every block of S, every LU pivot and every inverse pivot is the corresponding block of the Schur complement of the plain Toeplitz matrix T* (checked exactly in struct_check.py). The diagonals are only applied at
the input and output of a boundary solve, as the same anchored ratios (relative to the block anchor) as the capped gauge of CAPPED-GAUGE-AUDIT.md: their range over a block of the line, including consecutive boundary segments, is O(aB) with the linear (old) gauge of CAPPED-GAUGE-AUDIT.md, and O(a theta B'^2) = O(a B^2/d) (B' <= B + 2W) in the fractional-shift representation of GAUGEFREE-INTERIORS.md (chirp only), inside the group guard g a B^2/d = o(p) used by this package (beta + 2 xi - eps < 1). No new gauge is introduced. In the shifted representation the pivot bounds are those of GAUGEFREE-INTERIORS.md Corollary 4.3 (P_j^-1 is a principal block of the inverse of the accretive contiguous section T[J]); the displacement-rank statements are unchanged (they hold for any Toeplitz T).

## 2. Displacement ranks (the algebraic statement)

Let W x W be the segment size and Z the W x W down-shift. The displacement of a matrix M with row and column index sets that are intervals (shifts Z of the corresponding sizes) is Delta(M) = Z M - M Z (Sylvester) or M - Z M Z^T (Stein); the two ranks differ by at most 2 (Kailath-Sayed).
Facts for a banded Toeplitz T and interval index sets:
(a) every rectangular block of T has displacement rank <= 2 (the displacement lives in the first row and last column);
(b) for invertible Toeplitz A, Delta(A^-1) = -A^-1 Delta(A) A^-1 has rank <= 2 (Gohberg-Semencul); principal and corner blocks of such a matrix have rank <= 2 + 2;
(c) Delta(XY) = Delta(X) Y + X Delta(Y) with the middle shift matched, so ranks add under products; ranks do not increase under sums beyond the sum; Delta(M^-1) = -M^-1 Delta(M) M^-1, so M and M^-1 have equal rank;
(d) (Kailath) the Schur complement of a leading block of a matrix with displacement rank r has displacement rank <= r (w.r.t. the shift of the remaining indices).
Consequences for the boundary J = G separated W-segments with interiors I_j between them (all interiors eliminated):
* coupling S_{j,j+1} = - T_{j,I_j} A_{I_j}^-1 T_{I_j,j+1}: rank <= 2 + 2 + 2 = 6 (a, b, c); S_{j+1,j} likewise;
* diagonal block S_{jj} = T_{jj} - T_{j,I_{j-1}} A^-1 T_{I_{j-1},j} - T_{j,I_j} A^-1 T_{I_j,j}: rank <= 2 + 6 + 6 = 14;
* the LU pivot P_j = S_{jj} - S_{j,j-1} P_{j-1}^-1 S_{j-1,j} is the Schur complement of T onto segment j after eliminating all indices to its left (a leading block of T: rank <= 2 by (d)) minus the single right-interior correction T_{j,I_j} A^-1 T_{I_j,j}
  (rank <= 6; indices farther to the right do not couple to segment j, in T or in its left Schur complement, because the band is W and the separators have length >= W): **rank(P_j) <= 8 uniformly in j and G**, and rank(P_j^-1) = rank(P_j).
A *global* displacement operator on the concatenated J has rank growing like 2G (IdeaLiterature's screen); the claim here is block-wise, with one shift per segment, which is exactly what a block-tridiagonal LU needs. The constants 14 and 8 are proved bounds; the observed ranks are <= 4 (struct_check.py,
and IdeaLiterature's 70-110-digit screens of the real chirp-weighted blocks: coupling 2, diagonal and pivot 2-4, flat in W and in G).

## 3. Generator representation

A block M with Stein displacement M - Z M Z^T = sum_{k<=r} g_k h_k^T is represented by (g_k, h_k) and recovered by the Kailath-Kung-Morf formula **M = sum_k L(g_k) L(h_k)^T**, L(g) lower-triangular Toeplitz with first column g
(rectangular off-diagonal blocks use the same formula with the matched shifts). Generators are computed **offline, from generators, never from the dense blocks**: the leading Schur complements of the banded Toeplitz T are propagated by the generalised Schur algorithm (r = 2 generators,
O(r W) work per eliminated index, or the superfast O(r W log^2 W) variant of Bitmead-Anderson and Pan per segment); the interior corner blocks T_{j,I} A_I^-1 T_{I,j'} come from the Gohberg-Semencul generators of A_I^-1 (first and last columns of the inverse of the interior Toeplitz block);
the pivot and inverse-pivot generators are then obtained by the rank-<= 8 recompression of the sum (generators of the Schur piece and of the correction), an exact operation on ranks (QR/SVD at working precision P + poly bits). This is the page regeneration the audit already charges
(polynomial in p per complete microbox and axis, amortised by the superpolynomial payload); the generator pages replace the dense W x W factor pages. Balanced generators from the SVD of the displacement (g_k = sqrt(sigma_k) u_k, h_k = sqrt(sigma_k) v_k) satisfy |g_k||h_k| = sigma_k <= ||Delta(M)|| <= 2||M||,
so each term of the KKM sum has norm <= W ||Delta(M)|| (|L(g)|_2 <= |g|_1 <= sqrt(W)|g|_2) and the sum has norm <= 2 r W ||M|| = poly(W) ||M||: no hidden cancellation beyond a polynomial factor.

## 4. The solve on the tape

For one boundary band the block-tridiagonal system S x = y (stage diag(I, S^-1) of the audit; the C and B stages are products with the banded Toeplitz coupling blocks T_{J,E}, themselves rank-2 Toeplitz blocks) is solved by block forward and backward substitution with the audited no-pivot LU:
  z_j = P_j^-1 (y_j - S_{j,j-1} z_{j-1}),  x_j = z_j - P_j^-1 S_{j,j+1} x_{j+1}.
Each operator application (S_{j,j±1}, P_j^-1 and the Toeplitz couplings) is r pairs of triangular-Toeplitz products L(g) (L(h)^T v), each a convolution of length W computed by FFT of length 2W at working precision: O(r W log W) ring operations of p-bit numbers per right-hand-side column.
Layout: the right-hand sides of an axis substream (the lines of the union schedule, UNION-SCHEDULE.md) are batched in the dyadic width of the audit; the batch matrix |E_f| x batch width is arranged so that the W-axis of every column is contiguous by the small-field transpose (O(log p) riffle passes), the FFT is a sequence of O(log W) butterfly
passes, each a scan with a bit-reversal permutation realised by O(log W) riffle passes: O(log^2 W) scans of the batch data, polylog p overhead. The generator page of a block (r W numbers) is scanned once per batch; with the batch width >= W this is a 1/W fraction of the batch data (as for the dense pages in the audit).
Cost: per band and per column O(r W log^2 W M(p)) bit operations, i.e. per entry O(r log^2 W M(p)) = (M(p)/p) polylog p * p; with the retained short multiplier M(p)/p = polylog p, the boundary arithmetic is **O(V (d/B) W polylog p)**, so the boundary exponent is epsilon - xi + 1/2 + o(1), i.e. tau_eff = 2 + delta (any fixed delta > 0 absorbs the polylog factors since W = p^(1/2) polylog p).
(The ledger uses delta = 1e-10010, the same convention as the other strict slacks.)

## 5. Precision and stability at Cp bits (the regime: row gap about 1/(16p), poly(p) conditioning)

The argument reuses the audited bounds and adds the factors introduced by the structured representation.
1. *Pivots and couplings.* By PR1673's no-pivot theorem (BILATERAL-LDU.md Sections 1-2: unit L and U with all entries and all inverse entries bounded by constants times exp(-a rho theta |i-j|), c = prod(1 - r^-m) > 0, ||N^-1||_inf < 16 theta^-2; and the narrow/broad row-gap bounds of LOG-A-PHASE-SCHUR-AUDIT.md and FORWARD-SMALL-A-AUDIT.md:
   Schur row gap >= 1/(16 p) survives elimination), every P_j^-1 is a principal block of the inverse of a partially eliminated matrix and satisfies ||P_j^-1||, ||S_{j,j±1}||, ||P_j|| <= poly(p) uniformly in j, with the unit L^-1 / U^-1 bounded independently of G (this is the audited no-factor-equal-to-the-number-of-windows property). In the SPD (broad, Saug/4) case the principal-submatrix inverse has norm <= lambda_min(H)^-1 <= poly(p).
2. *Generators.* From section 3, balanced generators have norm <= sqrt(2 ||M||) = poly(p)^(1/2) and the KKM reconstruction has norm <= 2 r W ||M|| = poly(p).
3. *One application.* An FFT convolution of length 2W in fixed point with Cp-bit coefficients and a precomputed table of 2W roots of unity (computed once, offline, to P + poly bits by Newton iteration in O(M(P'))) has absolute error <= O(log W) 2^-P' times the product of the l1/l2 norms of its operands. So one application of an operator M to a vector v has
   absolute error <= poly(p) ||v|| 2^-P' + (the error of the stored generators, <= 2^-P' poly(p)). The diagonal gauges D_r, D_c enter only through the anchored ratios of range O(aB) (section 1), which cost O(aB) = o(p) extra bits: the same guard as the interiors (chirp-only O(a B^2/d) per axis in this package; O(aB) in the earlier linear-gauge version); no exponential growth beyond it.
4. *Accumulation.* The forward and backward substitutions are the unit L^-1 and U^-1 of the audited LU followed by diagonal factors P_j^-1; errors of different steps enter linearly through the unit factors whose inverse is bounded independently of G, so the total absolute error is <= poly(p) 2^-P' (a sum over at most poly(p) = L/B segments of poly(p) terms, with the audited exponential decay of the L^-1, U^-1 entries
   making the dependence on G at most polynomial). Hence P' = P + O(log p) + o(p) (the guard), i.e. O(p) bits suffice, the same record width as for the dense algorithm.
5. *Offline generator accuracy.* Generators are generated at working precision P + poly(p) bits in polynomial time; their conditioning is that of the blocks themselves (the generalised Schur algorithm is applied to the banded Toeplitz T with strictly diagonally dominant / SPD structure whose leading Schur complements are bounded below by the row gap), so no loss beyond poly(p) factors occurs.
The one point where structured algorithms are known to be unstable in general (indefinite or nearly singular leading minors) is excluded here by the audited uniform lower bounds on the pivots (item 1); this is where an independent reviewer should look first.

## 5b. Cleaner conditioning argument, rounding convention, anchors and pages (added after independent review)

* **Conditioning without the no-pivot theorem.** In the coordinates Y = D_r^-1 X D_c^-1 every block, pivot and inverse pivot is a block or a Schur complement of the plain symmetric positive definite Toeplitz matrix T (a Gaussian symbol is positive for every a; the narrow case has cond(T) = 1 + O(e^-a)).
  By interlacing and monotonicity of Schur complements, every principal submatrix and every Schur complement of T has its spectrum inside [lambda_min(T), lambda_max(T)], hence every leading minor and every pivot P_j (and P_j^-1) has condition number at most cond(T), and cond(T) <= (1 + sqrt(pi/gamma))/(sqrt(pi/gamma) e^(-pi^2/(4 gamma))) = O(e^(a/4)) = O(p)
  with the eigenvalue bounds of FORWARD-SMALL-A-AUDIT.md (the same constants as the broad forward audit). The Bunch-type danger of structured solvers (indefinite or nearly singular leading minors) cannot occur for SPD T; the Schur/Levinson recursion and the Gohberg-Semencul application on an SPD Toeplitz matrix are weakly stable, losing O(log cond) = O(log p) bits.
  (This replaces the appeal to the row gap 1/(16 p) in section 5 item 1 for the SPD blocks; the row-gap bounds remain the justification for the non-symmetric narrow blocks. Independent numerical evidence, LeverRank, 80-160 digits, alpha = 4, a = 50.3, rho = 1 + 1/6000: pivot condition numbers saturate at cond(T) ~ 1.4e5 for W = 16, 32, 64; balanced-generator norm ratio sigma_1(grad L^-1)/||L^-1|| 0.14-0.27 (no growth); generator-to-inverse rounding amplification <= 1;
  Levinson/Gohberg-Semencul error about 2^9.5 u flat in n; a perturbation of the first pivot is damped along the chain, so accumulation is independent of G.)
* **Rounding convention (required).** The retained rounded matrix must be rounded *factorwise*: K^ = D^_r T^ D^_c with T^ exactly Toeplitz (symmetric rounding of exp(-a rho x^2) by |i-j|) and D^_r, D^_c the rounded gauge weights. This is the structure-preserving rounding of FORWARD-SMALL-A-AUDIT.md and the Toeplitz-similar cell matrix of LOG-A-PHASE-SCHUR-AUDIT.md. Entrywise rounding of K would destroy the Toeplitz structure (this is the dense non-Toeplitz control of section 6: the displacement rank jumps to W).
* **Anchors.** The diagonal conversions between X and Y coordinates use segment-local anchors. The inter-segment constant ratios D_r(m_j)/D_c(m_{j-1}) (about e^{O(aB)}) are stored inside the coupling pages and cost O(aB) = o(p) guard bits per page; no range over the whole line is ever formed.
* **Pages.** In the interior of a line the pivots are identical (observed), so each cell needs O(1) distinct generator pages (only the cell-end blocks differ): page regeneration is cheap. A batch width W suffices (no W^k batching is needed in this package).

## 6. Executable check (`outer/struct_check.py`)

On the exact rational model K = D_r T D_c with a random (non-symmetric) banded Toeplitz T, W = 3..5, G = 3..6 segments, interiors of length 3W: (1) the exact diagonal cancellation S_Y = Schur(T); (2) the Stein displacement ranks of every segment block, coupling block, LU pivot and inverse pivot (all <= 4, flat in the segment index and in G);
(3) exact reconstruction of every block from its rank factorisation by the KKM formula; (4) the block forward/back substitution performed only with generator representations equals the dense solve exactly; (5) controls: a dense non-Toeplitz perturbation of the band raises the pivot and diagonal ranks to the full W (here 6 > 4), and a perturbed pivot is not reproduced by the original generators.
This checks the algebra exactly at small W; it does not check the analytic stability argument of section 5, which is an argument, nor does it replace a check on the real chirp-weighted blocks at 70-110 digits (IdeaLiterature's screens: scratch/IdeaLit/real.py, real2.py).

Scope of the real-matrix screen (IdeaLiterature, disclosed): block ranks 2-4 were observed for W <= 16 and G <= 8 segments only. In that toy the pivot condition number grows with W (about 3.5 at W = 8 and 1.2e3 at W = 16) because the toy takes a proportional to 1/W^2.
In the regime of the note a = pi alpha^2 >= 1 is fixed independently of W (alpha = ceil(sqrt((4/pi) log 16p))), theta >= 1/(4d), and BILATERAL-LDU.md bounds the periodic inverse by ||N^-1||_inf < 16 theta^-2 and the pivots/factors uniformly (items of section 5), so the conditioning is polynomial in p; the toy's growth with W is therefore not the real regime, but it is exactly the point that is *not* verified numerically here.

## 7. Ledger consequence

tau_eff = 2 + delta (delta = 1e-10010): c = (3 - tau_eff)/2 = 1/2 - delta/2. Balance: main = fused Gaussian = boundary - slack with xi = epsilon - c + kappa; the union row xi + 1/2 - epsilon has the same exponent as the boundary row (both epsilon + 1/2 - xi), so both bind at kappa + 1e-10010 together with main and the Gaussian row;
with the chirp-only guard of GAUGEFREE-INTERIORS.md: xi = 0.50167, xi - 1/2 = 0.00167 > 0 (cap holds), beta = 0.99665, union tag work per visit 1 - beta = 0.00335 > 0. kappa = 0.00167974550880...; +1.40e-6 over the structured-boundary balance with the linear guard (kappa 0.0016783441717...; that was +2.20e-7 over k = 5, tau_eff = 2.1567081).

## 8. What is not proved

* The constants c0 = 14, 8 follow from the displacement calculus (a)-(d) above; (d) and the Gohberg-Semencul statement (b) are classical theorems used as inputs; the corner-block increment (+2) and the application to the real chirp-weighted blocks (Haug, Saug, narrow and broad pairs) rest on the exact factorisation of section 1.
* Section 5 is an error argument built from the audited bounds, not a verified stability theorem for structured solvers. The real-regime numerical check (row gap 1/(16 p), p large) has not been run.
* Everything inherited from PR1673 (all-size compiler, precision/tape, exact recovery, analytic transfer) remains an assumption.
