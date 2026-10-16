# Audit: logarithmic Gaussian width retains the phase-cell Schur solver

This audit checks the analytic hypotheses of the retained rad20 phase-cell solver at `a=pi alpha^2=Theta(log p)`, `theta=Theta(1/d)`, even though `a theta` tends to zero. It also audits the shallow Toeplitz circuit algebra and identifies the actual matrix that must be precomputed. It does not certify the final tensor layout or multiplication exponent.

Read inputs: `references/semantic-bulk/rad20/reports/review-bulk-resampling.md`, `review-phase-cell-inverse.md`, `downstream-phase-cell-inverse.md`, and `work/inplace_algebra_ultra/SHALLOW-TOEPLITZ.md`.

## 1. The sharp elementary diagonal-dominance estimate

Let `rho=1+theta`, `beta_i=rho*i-q_i`, and let the Gaussian row coefficient at integer offset h be

`n_i,h=exp(-a[(rho*h+beta_i)^2-beta_(i+h)^2])`.

The h=0 coefficient is 1. Set `g_i=q_i-q_(i-1)` and `g_(i+1)=q_(i+1)-q_i`, each in {1,2}. For the nearest coefficients,

`n_i,-1=exp(-a*g_i*(2rho-2beta_i-g_i))`,

`n_i,+1=exp(-a*g_(i+1)*(2rho+2beta_i-g_(i+1)))`.

If g_i=1, the first exponent is exactly `1+2theta-2beta_i`; if g_i=2, that gap forces `beta_i<theta-1/2`, and the exponent is at least the same expression. Similarly g_(i+1)=2 forces `beta_i>=1/2-theta`, so the upper exponent is at least `1+2theta+2beta_i`. Consequently

`n_i,-1+n_i,+1`

` <=exp(-a(1+2theta-2beta_i))+exp(-a(1+2theta+2beta_i))`

` <=exp(-2a theta)+exp(-2a(1+theta))`.

The last step is convexity in beta on [-1/2,1/2]. The two nearest directions cannot both be charged as exp(-2a theta).

For |h|>=2,

`(rho*h+beta_i)^2-beta_(i+h)^2 >= h^2-|h|`,

so their entire two-sided tail is below `4 exp(-2a)` for a>=1. Therefore

`||N-I||_infinity <= exp(-2a theta)+5 exp(-2a)`.

This includes nonzero periodic diagonal aliases in the tail; no alias is silently omitted from this bound.

For p>=101, theta>=1/(4p), and `a>=4 log(16p)`,

`1-exp(-2a theta) >= 1-exp(-1/(2p)) >=1/(4p)`,

`5exp(-2a)<=5/(16p)^8<1/(8p)`.

Hence N has row diagonal-dominance margin at least `1/(8p)` in the following robust sense: after deleting its tiny nonzero diagonal aliases, its diagonal is 1 and its off-diagonal row sum is at most `1-1/(8p)`. In particular the fixed-width inverse theorem is not needed to supply the retained strict row dominance.

Choose the legal integer alpha by

`alpha=ceil(sqrt((4/pi)log(16p)))`.

Then a has the required lower bound and is O(log p). The old sufficient condition `u>=ceil(log2(8p))` need not be reused: the direct estimate above replaces that prerequisite.

## 2. Actual rounded H, interior matrices, and guard range

Use exactly the retained structure:

- `w=ceil(sqrt(16p/u))+2`, u=alpha^2=a/pi;
- cell weights `a_j=exp(-a(1/4-beta_j^2)/theta)`;
- one globally fixed downward dyadic Toeplitz kernel `Ghat_delta` for |delta|<=w, zero outside, with Ghat_0=1;
- positive downward dyadic weights ahat_j;
- within a physical cell, define H_jk **exactly** as `ahat_j Ghat_(j-k)/ahat_k`;
- across cells, use the retained downward Gaussian entries; set H_jj=1.

Thus the actual interior block being inverted is

`A_cell=diag(ahat) Ghat_cell diag(ahat)^-1`.

It is not the unrounded Gaussian matrix, and its retained truncated Ghat is not silently replaced by the infinite Gaussian kernel.

The weight range is

`0<=-log a_j<=a/(4theta)=O(a d)`

under theta between 1/(4d) and 1/(2d-1). The old eventual condition u*d<=p holds whenever d=p^epsilon, epsilon<1, and u=O(log p). It bounds the old rational perturbation calculation by the same `2^(O(p)) eta` allowance. The stronger range `O(a d)` should be used for grouped tensor precision, rather than charging O(p) independently for every axis.

Choose the coefficient precision high enough that `||H-N||<1/(16p)`, including the Gaussian truncation, omitted diagonal aliases and weight-ratio rounding. The retained bound `p*2^(16p+7)*eta+2^(-46p)` at eta=2^(-32768p) is more than sufficient. Then H has diagonal 1, row gap at least `1/(16p)`, row norm below 2, and inverse norm at most 16p. All clipped principal windows inherit the same row gap. The physical period cut must remain a cell boundary, as in the retained bulk review.

## 3. Schur complement bounds without an a*theta>1 assumption

A scalar elimination step on a strictly row-diagonally-dominant matrix cannot decrease its minimum absolute row gap. For pivot k,

`gap_i(new) >= gap_i(old)+(|a_ik|/|a_kk|) gap_k(old)`.

The full absolute row sum also cannot increase, since the added update row has off-pivot sum less than |a_kk|. Induction applies regardless of the signs of filled entries. Since the diagonal begins real positive and the correction magnitude is below it, the surviving diagonal remains positive.

Consequently the exact Schur complement

`S=H_BB-H_BI H_II^-1 H_IB`

has row gap at least `1/(16p)`, row norm below 2, positive diagonal, and

`||S^-1||_infinity<=16p`.

Principal interior inverses also have norm at most 16p. Rounding S by a row perturbation below 1/(32p) preserves gap at least 1/(32p) and inverse norm at most 32p. A row has O(w) nonzeros; the retained P-grid readily meets this target. These are polynomial bounds on arbitrary signed inputs, with no factor equal to the number of cells.

The boundary geometry is unchanged: keep first/last w vertices of each physical cell, yielding O(s*w/d) boundary vertices and circular half-bandwidth at most 2w. Schur fill only joins the two end groups of one cell, while original cross-cell entries join neighboring end groups. Actual inverse and LU coefficient tables must be precomputed for this H/S, not imported from the old parameter values.

Thus the retained banded/cyclic boundary solver's gap-dependent proof remains applicable with fixed constants enlarged. The proposed batched boundary arithmetic still needs its own data-layout and Strassen error audit, but there is no analytic conditioning obstruction at logarithmic a.

## 4. Apply the shallow circuit directly to Ghat inverse

Because a is eventually larger than 4pi, the symmetric Toeplitz matrix Ghat_cell satisfies

`max(||Ghat_cell-I||_1,||Ghat_cell-I||_infinity)<1/8`.

Downward rounding only decreases this off-diagonal sum. The shallow full-Toeplitz theorem therefore applies directly to Ghat_cell. Reverse the resulting invertible circuit and invert its gates to obtain Ghat_cell inverse. This avoids the two-branch Gohberg-Semencul difference entirely. The interior inverse is:

1. multiply by diag(ahat)^-1;
2. apply the reversed shallow circuit for Ghat_cell;
3. multiply by diag(ahat).

Its only superpolynomial individual scale comes from the **local** weight range O(a d). Completed A_cell inverse has polynomial norm by the strict row gap. Across g axes, the uncompleted local weight contribution is at most exp(O(g*a*d)); choosing `g<=p/(d polylog p)` with sufficient logarithmic slack keeps the total data precision O(p). The shallow circuit contributes polynomial-in-d amplification per axis, hence only O(g log d) additional logarithmic range. This is a guard calculation, not a complete simultaneous-layer routing proof.

## 5. Independent shallow-Toeplitz algebra audit and a length caveat

The parity-split triangular identity, block Schur displacement formulas, Stein-generator telescoping identity, and bounded-prefix induction in SHALLOW-TOEPLITZ.md check algebraically. In particular the parity children run in parallel, avoiding the earlier erroneous sequential-depth recurrence. The full block-LU recursion also runs its two children in parallel, with O(log N) displacement rank after O(log N) levels.

That document currently states its circuit theorem for dyadic N. Actual cell interiors are not generally dyadic. Padding every tensor axis to its next power of two would be invalid. A plausible exact extension has been communicated to its author: split an arbitrary N into balanced sizes differing by at most one; a near-square rectangular Toeplitz dirty shear is a square Toeplitz shear plus one extra row/column rank-one shear. The latter can be implemented by a binary tree of unitary 2-coordinate reductions and its inverse, without clean ancilla. The rectangular Stein identity telescopes as before. This extension needs its own written proof/controls before it is used as an established interface.

No new final kappa is asserted by this audit.

## 6. Dyadic interior subdivision resolves the length caveat

No arbitrary-length shallow FFT theorem is actually needed. Refine the interior/boundary partition inside each original physical phase cell of length L as follows. Keep its first and last w vertices as boundary. Starting with the remaining interval of length R=L-2w:

- while R>4w, choose the largest power of two B<=R-w;
- mark the next B vertices as one interior, the following w vertices as boundary, and replace R by R-B-w;
- once R<=4w, mark all remaining vertices as boundary.

Every interior now has exactly dyadic length. If R>4w, then `B>(R-w)/2`, so the next remainder is less than R/2. There are `O(1+log(L/w))` interiors and the total boundary count in the cell is `O(w(1+log(L/w)))`. The final boundary group, including the initially reserved last w vertices, has size at most 5w; all inserted separators have size w.

The width-w matrix H cannot connect two different new interiors: their separating boundary gap has w vertices, so their nearest physical coordinates differ by w+1. Each new interior is still a principal block of the SAME globally fixed Toeplitz-similar cell matrix. Its weights retain the original cell gauge; there is no new rescaling or rerounding at a subdivision boundary.

Eliminating one dyadic interior fills only between its immediately neighboring boundary groups. Each such group has O(w) vertices. Original H edges also connect only the same group or neighboring groups; an interior has length greater than w in the loop above. Thus, in inherited physical boundary order, the new Schur complement has half-bandwidth O(w), not O(w log d). Only its number of rows grows by O(log d):

`n_boundary=O((s/d) w log d)`.

Clipped endpoint cells of size O(w) may be declared wholly boundary, adding only O(w) rows; preserve the original physical period cut. This is the same endpoint convention as the retained bulk review.

The boundary solve and coupling work therefore gain only polylogarithmic factors. All dyadic interior blocks use the established SHALLOW-TOEPLITZ theorem directly, without padding any tensor axis and without requiring a non-dyadic Fourier circuit. This resolves the length caveat in section 5 for the intended phase-cell application; it does not prove the separate simultaneous tensor-layer routing claim.
