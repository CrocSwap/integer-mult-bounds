# Rectangular boundary batching (new in this package)

**Status.** This construction is a new contribution of this package. The capped phase-cell fusion outer, its boundary algebra and the batching of right-hand sides are Vlado Vojdanovski's
PR1673 (PHASE-LAYOUT-AUDIT.md, "Batched right-hand sides"); the specialisation of the matrix boundary to an established published exponent is Chafik Boukhalfa's PR1699; the
radix-distributed sparse-union schedule is new in pkg4 (outer/UNION-SCHEDULE.md). The change here: the boundary solves are batched with **W^k right-hand-side columns per factor page
(k = 2)** instead of W, so that rectangular matrix multiplication <W, W, W^2> is used. The published input is the bound omega(1,1,2) = omega(1,2,1) < 3.250035 of Josh Alman, Ran Duan, Virginia
Vassilevska Williams, Yinzhan Xu, Zixuan Xu and Renfei Zhou, "More Asymmetry Yields Faster Matrix Multiplication" (arXiv 2404.16349, SODA 2025), Table 1 (k = 2.00, upper bound on omega(1,k,1) = 3.250035, previous bound 3.250385 [VXXZ24]; versions v1 and v3 agree on this row, v3 only changes the k = 1 row via a later paper; Section 3.4 states the permutation symmetry omega(a,b,c) = omega(a,c,b) = omega(c,a,b), so omega(1,1,2) = omega(1,2,1)).
The theorem is used as a cited input and is not re-proved here. All inherited all-size hypotheses of PR1673 remain.

## 1. Batch width and the per-column cost (a)

In the audit, all inner coordinates and following tensor axes are independent right-hand sides; their number R is superpolynomial. The audit batches them in a dyadic width between W and 2W.
Here a batch has width between W^2 and n^2 W^2, where n is the fixed base of the rectangular format of section 3 (a constant; the width is a power n^(2j) matching the padded row dimension n^j).
Batching more columns is allowed for the same reason as before: the number of right-hand sides in an axis substream is superpolynomial, so padding the last incomplete batch costs a polynomial amount
per axis substream (at most W^2 n^2 lines of |E_f| records; at most g axes and g rounds per window), negligible against the superpolynomial volume; the batch matrix of |E_f| x n^2 W^2 consecutive lines (each line |E_f| long) is rearranged so that W-row slices times all batch columns are contiguous by another small-field transpose with O(log(n^2 W^2)) = O(log p) riffle passes, so moving it costs O(log p) times the boundary volume, exactly as in the audit. Premise used explicitly: every prefix block of an axis substream contains L^(g-f) times the spectators >> n^2 W^2 lines, i.e. enough independent right-hand sides per prefix block. Each W x W factor page is still scanned once per batch (W^2 <= batch size).

Cost bookkeeping per axis: a band of boundary rows has V W / B right-hand-side entries per axis. A batch handles W * W^2 = W^3 entries with one product of shape <W, W, W^2> costing W^(omega(1,1,2)+eps).
So per axis the boundary arithmetic is (V W / B) / W^3 * W^(omega(1,1,2)) = (V/B) W^(omega(1,1,2) - 2), i.e. the old form (V/B) W^(tau - 1) with
**tau_eff = omega(1,1,2) - 2 + 1 = omega(1,1,2) - 1**  (in general tau_eff = omega(1,1,k) - k + 1; k = 1 is the square case tau = omega). With the published bound, tau_eff < 2.250035.
The boundary row exponent is epsilon - xi + (tau_eff - 1)/2 and its saving is c + xi - epsilon with c = (3 - tau_eff)/2.

## 2. Blocked triangular solve against W^2 columns (b)

The no-pivot band solve of the audit is the block recursion X_j = L_jj^-1 (Y_j - L_{j,j-1} X_{j-1}) on W x W blocks along an axis line, with R = batch width columns:
Y_j, X_j are W x R. Each step is two products of a W x W factor block with a W x R matrix: shape <W, W, R> with R = n^(2j), W = n^j padded. The precomputed diagonal inverses L_jj^-1 are part of the factor page.
Let M(W) be the cost of one <W, W, W^2> product by the recursion of section 3: M(W) <= R_f M(W/n) + O(W^3), where R_f is the rank of the base format; since R_f < n^sigma with sigma > 3 the ratio
n^3 / R_f < 1 and the levels form a geometric series dominated by the leaves, M(W) = O(R_f^(log_n W)) = O(W^sigma) with sigma the chosen exponent (ledger check `rect_leaf_domination`: sigma - 3 > 0). Per band of W boundary rows a
step costs 2 M(W) arithmetic operations; the number of blocks per line is polynomial and independent of the batching (they are summed in the (V W / B)/W^3 normalisation above).
The additions of the recursion (linear combinations of blocks, accumulations) are complete block scans: O(W^3) entries per level touched, O(W^3) per node up to logarithms, as in the square-case tape accounting of PR1673/PR1699 (depth-first scheduling, fixed block permutations, tape repositioning O(W^3 polylog) per node).

## 3. Existence of an exact rectangular format and precision (c)

Let omega(1,1,2) < sigma0 := 3.250035 (cited). By definition of omega(1,1,2) (the infimum of exponents s with rank of <n, n, n^2> = O(n^s)), for every sigma > sigma0 there are fixed integers n >= 2 and
R_f with an exact bilinear formula of rank R_f for <n, n, n^2> (multiplying n x n by n x n^2 matrices) and R_f < n^sigma: choose s with sigma0 < s < sigma, a constant C with rank <= C n^s for all n, and n large.
Constant overhead of bilinearising a circuit is absorbed by first choosing the exponent below sigma and then n large. This uses strict slack and never asserts that the infimum is attained by a finite formula.
(Symmetry: the matrix multiplication tensors <n, n^k, n> and <n, n, n^k> are cyclic rotations of each other, so omega(1,k,1) = omega(1,1,k); the cited table lists omega(1,k,1).)
The rank equations are finitely many polynomial equations over Z. A complex solution can be replaced by one over the algebraic closure of Q: otherwise, by the weak Nullstellensatz over Qbar, 1 would lie in the ideal, giving the same
contradiction over C. Enumerate finite algebraic tuples with isolating descriptions, test the equations exactly, dovetailing over (n, R_f); the search halts by the existence statement and its cost and description are fixed independently of the growing input.
(This is exactly the argument of PR1699/PR1673's matrix lemma, with the format <n, n, n^2> in place of <m, m, m>; no finite scheme is claimed as generated here.)

Recursion: T(W) <= R_f T(W/n) + O(W^3), with W padded to the next power of n (a constant-factor change of the dimension; the batch width is the padded W^2, so both W and R are powers of n and no axis of the tensor is padded).
Precision: approximate each fixed algebraic coefficient once by precision-doubling Newton iteration, O(M(P')) bit operations for P' bits. The absolute roundoff envelope of the fixed bilinear recursion obeys
E_j <= K E_{j-1} + K n^(3(j-1)) (inputs and products of size n^j x n^j by n^j x n^(2j)) with K fixed by the chosen formula (maximum column sums of the encodings and decoding times the base-case size), hence E_j <= K^j (...) = W^(log_n K) poly(W), polynomial in W.
Input magnitudes at most 2^h need fractional precision P + 2h + O(log W) for absolute error 2^-P; intermediate magnitudes are W^O(1) max(1, 2^(2h)); the total record width is O(P + h + log W) = O(p) at the retained boundary interface (P, h = O(p)),
and a larger fixed guard constant absorbs the formula-dependent K. The bound is absolute, including cancellation.

## 4. Choice of sigma, controls (d)

sigma = 3.2500351 is strictly above the published bound 3.250035 (margin 1e-7, costs about 1.4e-13 in kappa), so tau_eff = 2.2500351. Ledger checks: `rect_exponent_above_published_bound` (sigma - 3.250035 > 0),
`rect_leaf_domination` (sigma > 3), `rect_effective_exponent_above_two` (tau_eff > 2, the trivial output-size bound) and `rect_effective_exponent_below_five_halves`. Rejecting controls: sigma = 3.2500349 (below the published bound) and sigma = 3.250035
(equal to it) must fail `rect_exponent_above_published_bound`; both are asserted to fail.

## 5. Consequence for the ledger

c = (3 - tau_eff)/2 = 0.37498245. The boundary row still binds with main = fused Gaussian (xi = epsilon - c + kappa); kappa = 0.0016779926..., +1.727e-7 over the previous package (square tau = 2.372864).
At the new balance epsilon = 0.99895, xi = 0.6256, beta = 0.3744; cap xi > 1/2 holds with margin 0.1256; union saving xi + 1/2 - epsilon = 0.127 (the old g-factor union row would be -0.248); group scans 0.375; support/key/membership
rows 0.62; union tag work 1 - 2 beta = 0.25. The unproven omega_C <= 9/4 premise is not used.

## 6. What is not proved

The rectangular exponent is a published theorem used as a cited input. The existence of the exact format and the stability constants rest on the arguments above and on PR1673's inherited all-size hypotheses
(compiler, precision/tape, exact recovery, analytic transfer); a reviewer should in particular check the claim that the number of right-hand sides in an axis substream is superpolynomial in the regime used
(spectator payload L^g) and the per-column normalisation in section 1.
