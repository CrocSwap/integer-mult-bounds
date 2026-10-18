> **Superseded in this package (pkg7) by outer/STRUCTURED-BOUNDARY.md; kept as the documented fallback (pkg6: k = 5, tau_eff = 2.1567081) if the structured-solve argument is not accepted.**

# Rectangular boundary batching, k = 5 (new in this package)

**Status.** This construction is a new contribution of this package. The capped phase-cell fusion outer, its boundary algebra and the batching of right-hand sides are Vlado Vojdanovski's
PR1673 (PHASE-LAYOUT-AUDIT.md, "Batched right-hand sides"); the specialisation of the matrix boundary to an established published exponent is Chafik Boukhalfa's PR1699; the
radix-distributed sparse-union schedule is new in pkg4 (outer/UNION-SCHEDULE.md). The change here: the boundary solves are batched with **W^k right-hand-side columns per factor page with k = 5**
(pkg5 used k = 2), so that rectangular matrix multiplication <W, W, W^5> is used. The published input is the bound **omega(1,1,5) = omega(1,5,1) = omega(5) < 6.156708** of Francois Le Gall,
"Faster Rectangular Matrix Multiplication by Combination Loss Analysis", SODA 2024, arXiv 2307.06535 (v2, revised 27 Dec 2023), Section 1.2, Table 3 ("Our new upper bounds on omega(kappa)"), kappa = 5.00 -> 6.156708
(same table: kappa = 3.00 -> 4.199095, kappa = 2.00 -> 3.250563, kappa = 1.00 -> 2.372537). Convention (Section 1.1): omega(kappa) is the smallest exponent such that the product of an n x ceil(n^kappa) matrix by a
ceil(n^kappa) x n matrix is computable in O(n^(omega(kappa)+eps)), i.e. the exponent of the tensor <n, n^kappa, n>; footnote 1 there (citing [8, 9]) states that the arithmetic complexity of n x n times n x m, n x m times m x n and m x n times n x n are the same:
the matrix multiplication tensors <a,b,c>, <b,c,a>, <c,a,b> are cyclic rotations of each other, so <n, n^5, n> and <n, n, n^5> (a W x W factor page against W x W^5 right-hand sides) have the same rank and omega(1,5,1) = omega(1,1,5).
The theorem is used as a cited input and is not re-proved here. All inherited all-size hypotheses of PR1673 remain. (The k = 2 value of ADVWXXZ 2024, omega(1,1,2) < 3.250035, is the pkg5 fallback; for k = 5 only Le Gall's table gives a bound.)

## 1. Batch width and the per-column cost

In the audit, all inner coordinates and following tensor axes are independent right-hand sides; their number R is superpolynomial. The audit batches them in a dyadic width between W and 2W. Here a batch has width between W^5 and n^5 W^5,
where n is the fixed base of the rectangular format of section 3 (a constant; the width is a power n^(5j) matching the padded row dimension n^j).
Batching more columns is allowed for the same reason as before: the number of right-hand sides in an axis substream is superpolynomial, so padding the last incomplete batch costs a polynomial amount per axis substream
(at most n^5 W^5 lines of |E_f| records; at most g axes and g rounds per window), negligible against the superpolynomial volume. The batch matrix of |E_f| x n^5 W^5 consecutive lines (each line |E_f| long) is
rearranged so that W-row slices times all batch columns are contiguous by another small-field transpose with O(log(n^5 W^5)) = O(log p) riffle passes, so moving it costs O(log p) times the boundary volume, exactly as in the audit.
**Working set and record count per batch:** one batch is the W x n^5W^5 matrix of a block (and its W x n^5W^5 result) of p-bit records: n^5 W^6 = poly(p) records (about p^3 polylog p), so P-bit entries fit in polynomially many tape cells;
the whole batch matrix |E_f| x n^5 W^5 is |E_f| n^5 W^5 records, polynomial in p. **Superpolynomial supply per factor page (premise used explicitly):** every prefix block of an axis substream contains
L^(g-f) times the spectators lines, which is superpolynomial in p (the spectator payload and the L^(g-f) suffixes), hence >> n^5 W^5 lines: there are enough independent right-hand sides per factor page. For the last axis f = g the suffix is empty and the lines of a block are only the spectator lines: the d - g spectator axes (d = p^epsilon axes in total, g = p^beta in the group) each have length L = p^8, so there are L^(d-g) = p^(8(d-g)) of them, superpolynomial because d - g = p^epsilon - p^beta grows; W^5 = p^2.5 polylog p is far below it. The factor pages depend only on the axis f, the block index along the line and the axis-f coarse label, not on the other coordinates, so lines of every prefix block of the tag-f substream share the same pages. Each W x W factor page is scanned once per batch (page cost W^2 per block-batch versus product W^sigma).

Cost bookkeeping per axis: a band of boundary rows has V W / B right-hand-side entries per axis. A batch handles W * W^5 = W^6 entries with one product of shape <W, W, W^5> costing W^(omega(1,1,5)+eps).
So per axis the boundary arithmetic is (V W / B) / W^6 * W^(omega(1,1,5)) = (V/B) W^(omega(1,1,5) - 5), i.e. the old form (V/B) W^(tau - 1) with
**tau_eff = omega(1,1,5) - 5 + 1 = omega(1,1,5) - 4**  (in general tau_eff = omega(1,1,k) - k + 1; k = 1 is the square case tau = omega). With the published bound, tau_eff < 2.156708.
The boundary row exponent is epsilon - xi + (tau_eff - 1)/2 and its saving is c + xi - epsilon with c = (3 - tau_eff)/2.

## 2. Blocked triangular solve against W^5 columns, geometric ratio

The no-pivot band solve of the audit is the block recursion X_j = L_jj^-1 (Y_j - L_{j,j-1} X_{j-1}) on W x W blocks along an axis line, with R = batch width columns: Y_j, X_j are W x R. Each step is two products of a W x W factor
block with a W x R matrix: shape <W, W, R> with R = n^(5j), W = n^j padded. The precomputed diagonal inverses L_jj^-1 are part of the factor page.
The product is computed by recursion on the fixed format <n, n, n^5; R_f> (n x n by n x n^5 matrices, rank R_f): T(W) <= R_f T(W/n) + A(W), where the additions (linear combinations of blocks and accumulations) at the top level touch
O(W^6) entries (the output W x W^5 and the inputs are of size at most W^6): A(W) = O(W^6). The output size of the format is n * n^5 = n^6 entries, so necessarily R_f >= n^6; the format exponent sigma > 6 satisfies R_f < n^sigma. The level-i additions cost
R_f^i (W/n^i)^6 = W^6 (R_f/n^6)^i, a geometric series with ratio R_f/n^6 > 1 that is dominated by its last term, the leaves (R_f^(log_n W) = W^(log_n R_f) = O(W^sigma)); precisely T(W) = O(W^(log_n R_f)) = O(W^sigma) because the per-level cost
increases geometrically toward the leaves (ledger check `rect_leaf_domination`: sigma - (k+1) = sigma - 6 > 0; if R_f = n^6 exactly there is only a logarithmic factor, absorbed by the strict slack). Equivalently the ratio of the additions' cost
at the top, W^6, to the leaf cost W^sigma is W^(6-sigma) < 1. Per step of the band solve two such products are needed, working set W * n^5 W^5 * P bits (polynomial). The additions are complete block scans: O(W^6) entries per level,
O(W^6) per node up to logarithms, as in the square-case tape accounting of PR1673/PR1699 (depth-first scheduling, fixed block permutations, tape repositioning).

## 3. Existence of an exact rectangular format and precision

Let omega(1,1,5) < sigma0 := 6.156708 (cited). By definition of omega(1,1,5) (the exponent of the arithmetic complexity of <n, n, n^5>; arithmetic complexity and tensor rank have the same exponent up to the constant bilinearisation factor
that is absorbed by the strict slack), for every sigma > sigma0 there are fixed integers n >= 2 and R_f with an exact bilinear formula of rank R_f for <n, n, n^5> and R_f < n^sigma: choose s with sigma0 < s < sigma, a constant C with
rank <= C n^s for all n, and n large (the cited analysis defines omega through the asymptotic rank, and the infimum is over exact formulas for tensor powers). This uses strict slack and never asserts that the infimum is attained by a finite formula.
The rank equations are finitely many polynomial equations over Z. A complex solution can be replaced by one over the algebraic closure of Q: otherwise, by the weak Nullstellensatz over Qbar, 1 would lie in the ideal, giving the same contradiction over C.
Enumerate finite algebraic tuples with isolating descriptions, test the equations exactly, dovetailing over (n, R_f); the search halts by the existence statement and its cost and description are fixed independently of the growing input
(the argument of PR1699/PR1673's matrix lemma with the format <n, n, n^5> in place of <m, m, m>; no finite scheme is claimed as generated here).
Recursion: T(W) <= R_f T(W/n) + O(W^6), with W padded to the next power of n (a constant-factor change of the dimension; the batch width is the padded W^5, so both W and R are powers of n and no axis of the tensor is padded).
Precision: approximate each fixed algebraic coefficient once by precision-doubling Newton iteration, O(M(P')) bit operations for P' bits. The absolute roundoff envelope of the fixed bilinear recursion obeys E_j <= K E_{j-1} + K n^(6(j-1))
with K fixed by the chosen formula (maximum L1 column sums of the encoders and decoder times the base-case size), hence E_j <= K^j (...) = W^(log_n K) poly(W), polynomial in W. Input magnitudes at most 2^h need fractional precision
P + 2h + O(log W) for absolute error 2^-P; intermediate magnitudes are W^O(1) max(1, 2^(2h)); the total record width is O(P + h + log W) = O(p) at the retained boundary interface (P, h = O(p)), and a larger fixed guard constant absorbs the formula-dependent K.
The bound is absolute, including cancellation.

## 4. Choice of sigma, controls

sigma = 6.1567081 is strictly above the published bound 6.156708 (margin 1e-7, costs about 1.4e-13 in kappa), so tau_eff = 6.1567081 - 4 = 2.1567081. Ledger checks: `rect_exponent_above_published_bound` (sigma - 6.156708 > 0),
`rect_leaf_domination` (sigma > k + 1 = 6), `rect_effective_exponent_above_two` (tau_eff > 2, the trivial output-size bound) and `rect_effective_exponent_below_five_halves`. Rejecting controls: sigma = 6.1567079 (below the published bound)
and sigma = 6.156708 (equal to it) must fail `rect_exponent_above_published_bound`; both are asserted to fail.

## 5. Consequence for the ledger

c = (3 - tau_eff)/2 = 0.42164595. The boundary row still binds with main = fused Gaussian (xi = epsilon - c + kappa); kappa = 0.0016781238306..., +1.312e-7 over the k = 2 package (pkg5) and +3.04e-7 over the square tau = 2.372864 package (pkg4).
At the new balance epsilon = 0.99903, xi = 0.5791, beta = 0.4209; cap xi > 1/2 holds with margin 0.0791; union saving xi + 1/2 - epsilon = 0.080 (the old g-factor union row would be -0.341);
group scans 0.422; support/key/membership rows about 0.579; union tag work 1 - 2 beta = 0.158. The unproven omega_C <= 9/4 premise is not used.

## 6. What is not proved

The rectangular exponent is a published theorem used as a cited input. The existence of the exact format and the stability constants rest on the arguments above and on PR1673's inherited all-size hypotheses
(compiler, precision/tape, exact recovery, analytic transfer); a reviewer should in particular check the claim that the number of right-hand sides in an axis substream is superpolynomial in the regime used
(spectator payload L^g) and the per-column normalisation in section 1.
