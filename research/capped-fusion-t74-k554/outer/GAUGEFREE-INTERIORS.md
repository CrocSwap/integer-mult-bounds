# Gauge-free interiors: fractional-shift Toeplitz kernels, accretive shallow circuits, and the chirp-only guard

**Status.** New in this package series (not in PR1673 by Vlado Vojdanovski, whose capped phase-cell fusion, SHALLOW-TOEPLITZ.md, CAPPED-GAUGE-AUDIT.md and LOG-A-PHASE-SCHUR-AUDIT.md this note modifies and relies on). Conditional on every hypothesis of PR1673 except the three statements replaced below. Independent review required before release. Executable support: `outer/check_gaugefree.py` (exact identities, 50-digit symbol checks, section/Schur bounds, circuit replay) and `outer/check_ledger.py` / `outer/independent_check.py` (the ledger).

## 0. Result and what changes

kappa (this package = structured boundary + this note) = **0.0016797455088022990515465336851999736723...** (exact, 58 strict checks positive, all rejecting controls fire; previous package (structured boundary, linear guard) 0.0016783441717365..., gain +1.4013e-6; rectangular k=5 package 0.0016781238306335..., gain +1.6217e-6). Parameters: eps = 0.9999943758, xi = 0.5016741213, beta = 0.9966461332.

Three statements of #1673 are replaced (everything else is unchanged):

| # | #1673 / earlier packages | this note |
|---|---|---|
| R1 | local gauge of a capped interior: diagonals of range O(aB) (narrow), O(b0 B) (broad) | the linear part of the gauge is exactly a fractional centre shift of the Toeplitz kernel; only the quadratic chirp remains, range O(a theta B^2) = O(a B^2/d). (Section 2) |
| R2 | SHALLOW-TOEPLITZ sec. 9 needs mu I <= H <= M I (SPD) or ||H-I||<1/4 | accretive: (H+H^*)/2 >= mu I and ||H|| <= Lambda, with the absolute-scale guard log(2+Lambda+1/mu) (a ratio Lambda/mu alone is false, Remark 4.1a); for the unit-diagonal kernels used here Lambda >= 1 >= mu, so the guard is O(log(2+Lambda/mu)) (Corollary 4.1b). The shifted Gaussian symbol is accretive with explicit mu. (Sections 3, 4) |
| R3 | ledger guard beta + xi <= 1-r-zeta; union tag check 1-2 beta > 0 | guard beta + 2 xi - eps <= 1-r-zeta; tag check 1-beta > 0 (Sections 5, 6) |

## 1. Setting

Phase cell: beta_i = theta i - c in [-1/2,1/2), rho = 1+theta, lambda = 1/rho, 1/(4d) <= theta <= 1/(2d-1). An interior is a contiguous block of selected target coordinates (unit q-gaps), length n <= B (dyadic), anchor m at its centre; x = i-m, y = k-m, t = i-m for the narrow operator. B = p^xi, d = p^eps, xi < eps.

* Broad forward block (FORWARD-SMALL-A-AUDIT, CAPPED-GAUGE-AUDIT sec. 3): K_{ki} = alpha^-1 exp(-b0 (x - lambda y + delta)^2), delta = (1-lambda) m - c, |delta| <= 1/2, b0 = pi/alpha^2.
* Narrow inverse block (LOG-A-PHASE-SCHUR-AUDIT sec. 1): N_{i,i+h} = exp(-a[(rho h + beta_i)^2 - beta_{i+h}^2]), a = pi alpha^2, beta_i = beta0 + theta t_i.

## 2. Exact gauge <-> shift identities

**Lemma 2.1 (broad).** For every real s,
(x - lambda y + delta)^2 - lambda (x - y - s)^2 = (1-lambda) x^2 - lambda(1-lambda) y^2 + delta^2 - lambda s^2 + 2(delta + lambda s) x - 2 lambda (delta + s) y.
Hence K = Drow G_s Dcol exactly, with the Toeplitz kernel G_s(y,x) = exp(-b0 lambda (x-y-s)^2) and diagonals separable in (y,x) (proved by expansion; sympy and 600 exact rational mixed-difference checks in `check_gaugefree.py` stage A/B).
Choose **s = -delta (1-theta)**. Then the x-linear coefficient is 2 b0 (delta + lambda s) = 2 b0 delta (1 - lambda(1-theta)) = 2 b0 delta * 2 theta/(1+theta), |.| <= 2 b0 theta, and the y-linear coefficient is -2 b0 lambda (delta + s) = -2 b0 lambda theta delta, |.| <= b0 theta. Over a block with |x|,|y| <= B/2 the linear leftover has logarithmic range <= 2 b0 theta B (total), and the quadratic parts b0 (1-lambda) x^2, b0 lambda (1-lambda) y^2 have range <= b0 theta B^2/4 each. Also |s| <= (1-theta)/2, i.e. 1 - 2|s| >= theta.
(With s = -delta/lambda the linear terms vanish in x and are 2 b0 delta (1-lambda) in y, but |s| can exceed 1/2 by theta/2, which changes the winding number of the symbol; so the shift is shrunk by (1-theta). The price is the O(b0 theta B) linear leftover, dominated by the chirp.)

**Lemma 2.2 (narrow).** With beta_{i+h} = beta_i + theta h, rho = 1+theta:
(rho h + beta_i)^2 - beta_{i+h}^2 = (1+2theta) h^2 + 2 beta_i h. Writing beta_i = beta0 + theta t_i, j = i+h, t_j = t_i + h, and 2 t_i h = t_j^2 - t_i^2 - h^2:
log N_{ij} = -a rho h^2 - 2 a beta0 h + a theta (t_i^2 - t_j^2) (exact; sympy check, stage A).
So N = D' k D'^{-1}-type: N_{ij} = e^{a theta t_i^2} k(j-i) e^{-a theta t_j^2} with the Toeplitz kernel k(h) = exp(-a rho h^2 - 2 a beta0 h) = exp(a beta0^2/rho) exp(-gamma (h-s)^2), **gamma = a rho, s = -beta0/rho**. Here |s| <= 1/(2 rho) so **1 - 2|s| >= 1 - 1/rho = theta/rho >= theta/2**: no shrinking is needed, and the gauge is the chirp D' = exp(a theta t^2) of logarithmic range a theta B^2/4 (centred). The old weights are the same objects: log w_i = const + a theta (i - c/theta)^2 (the old linear slope 2 a beta0 is exactly the term moved into k).

**Normalisation.** G'_s(u) := e^{gamma s^2} e^{-gamma (u-s)^2} = exp(-gamma u^2 + 2 gamma s u) has G'_s(0) = 1 (unit diagonal, as the audited N). The scalars e^{gamma s^2} are exact constants (stored in the anchor ratios).

**Rounding.** The circuit applies the ideal truncated kernel (band W) rounded to Cp bits (the unit diagonal G'_s(0) = 1 is kept exactly by truncation and by rounding, so the circuit kernels are exactly unit-diagonal, Corollary 4.1b and stage F of `check_gaugefree.py`); the audited global rounded matrix differs from it by <= poly(p) 2^{-Cp} times the diagonal range e^{O(g (a theta B^2 + polylog))}, which is covered by the same precision guard (Section 5). **Restated comparison (audited rounded matrix vs ideal shifted kernel).** The audits (BILATERAL-LDU, FORWARD-SMALL-A, CAPPED-GAUGE-AUDIT sec. 2-3) bound the unshifted globally rounded matrix H^. Let K be the ideal block (exact Gaussian entries) and K~ = Drow' G^_s Dcol' the matrix the circuit applies (truncated at W, G^_s rounded to Cp bits, anchored diagonals). Entrywise |H^ - K| <= 4 * 2^{-P} e^{a/(4 theta)} relative to the weights (audit sec. 2), and |K~ - K| <= 2^{-Cp} W-banded; the diagonal conversions contribute the factor e^{O(a theta B^2)} per axis (chirp range of Section 5; the linear leftover is smaller). Hence ||K~ - H^|| <= poly(p) 2^{-Cp} e^{O(g a theta B^2 + g polylog p)} (g axes tensored), and the exponent is o(p) bits by the precision guard beta + 2 xi - eps < 1 of Section 5. For C > 1 the perturbation is <= 2^{-(C-o(1))p} <= 2^{-p}/poly, and since ||K^-1||, ||H^-1|| <= p^{O(1)} (Section 3; audits) every audited uniform bound (row gap, inverse norms, Neumann tail J = Cp^2, halo radius A) holds for K~ with polynomially perturbed constants. No structural change.

## 3. The shifted Gaussian symbol is accretive

Let q = e^{-gamma}, 0 <= s' = |s| < 1/2, phi(w) = sum_u e^{-gamma(u-s)^2} e^{-iuw}.

**Lemma 3.1 (product form).** Jacobi triple product with Z = q^{-2s} e^{-iw}:
phi(w) = e^{-gamma s^2} prod_{m>=1}(1-q^{2m}) (1 + a_m e^{-iw})(1 + b_m e^{iw}), a_m = q^{2m-1-2s}, b_m = q^{2m-1+2s}.
For s < 0 the symbol is the complex conjugate (swap a, b). All a_m, b_m in (0,1) iff |s|<1/2; a_1 = q^{1-2|s|} is the unique factor near 1. At |s| = 1/2: a_1 = 1 and phi(pi) = 0. (Verified at 50 digits, relative error 2.5e-42 on 1025 points.)

**Lemma 3.2 (phase).** For w in [0,pi] and s >= 0, f(x) := arg(1 + x e^{iw}) = atan(x sin w/(1 + x cos w)) is increasing in x in [0,1) (f'(x) = sin w/|1+x e^{iw}|^2 > 0). arg phi = sum_m [f(b_m) - f(a_m)]. Since 2m+1-2s >= 2m-1+2s iff s <= 1/2, a_{m+1} <= b_m, so f(b_m) >= f(a_{m+1}) and
0 <= -arg phi = sum_m [f(a_m)-f(b_m)] <= sum_m [f(a_m) - f(a_{m+1})] = f(a_1) < w/2 <= pi/2.
For w in [-pi,0] use phi(-w) = conj(phi(w)).

**Lemma 3.3 (real part).** cos(f(a_1)) = (1 + a_1 cos w)/|1 + a_1 e^{iw}|, so
Re phi(w) >= |phi(w)| cos f(a_1) >= e^{-gamma s^2} prod_{m>=1}(1-q^{2m}) * (1 - a_1) prod_{m>=2}(1-a_m) prod_{m>=1}(1 - b_m) =: m_s(gamma).
(The bound is attained at w = pi up to the other factors: stage C finds min Re phi / m_s = 1.0.) Normalising by e^{gamma s^2}:

mu(gamma, s) := m_s e^{gamma s^2} >= (1 - e^{-gamma(1-2|s|)}) exp(-pi^2/(3 gamma)).

Proof of the closed form: -ln prod_k (1 - e^{-k gamma x}) = sum_h (1/h)/(e^{h x gamma}-1) <= pi^2/(6 x gamma); the three infinite products are bounded by prod_{k>=1}(1-q^{2k}) >= e^{-pi^2/(12 gamma)} (twice, the second for m >= 2 since a_m <= q^{2m-2}) and prod_{k>=1}(1-q^{2k-1}) >= prod(1-q^k) >= e^{-pi^2/(6 gamma)}; total e^{-pi^2/(3 gamma)}.
Norm: Lambda := ||G'_s||_2 <= ||symbol||_{l1} = sum_u e^{-gamma(u^2 - 2su)} <= 3 + sqrt(2 pi/gamma) (u^2 - 2su >= u^2 - |u| >= 0 and >= u^2/2 for |u| >= 2).

Parameter values. Broad: gamma = b0 lambda = pi/(alpha^2 rho) = Theta(1/log p), 1-2|s| >= theta >= 1/(4d): mu >= (gamma theta/2) e^{-pi alpha^2 rho /3} = p^{-O(1)}. Narrow: gamma = a rho >= 4 log(16 p), 1 - 2|s| >= theta/2: mu >= (1 - e^{-a theta/2}) e^{-pi^2/(3 gamma)} >= a theta/3 = p^{-O(1)} (this is the audited row gap).

## 4. The accretive Toeplitz circuit (replaces SHALLOW-TOEPLITZ sec. 9)

**Theorem 4.1.** Let N be a power of two and H an N x N complex Toeplitz matrix with ||H||_2 <= Lambda and (H + H^*)/2 >= mu I, mu > 0. There is an N-wire circuit of disjoint invertible 1x1/2x2 gates applying H, with O(log^4 N) rounds, O(N log^4 N) gates, no ancilla, and
log(max prefix / suffix / inverse-prefix operator norm) = O(log N * log(2 + Lambda + 1/mu) + log N).
Rounding every coefficient to p + O(log N * log(2+Lambda+1/mu)) bits gives operator error 2^-p. If Lambda and 1/mu are p^{O(1)} the guard is O(log N log p) bits per axis. (The guard is the absolute-scale one of SHALLOW-TOEPLITZ sec. 9, M = Lambda, 1/mu; it is not a function of Lambda/mu alone.)

**Remark 4.1a (why the absolute scale is needed).** The statement is not uniform in Lambda/mu: for N = 2 and H = tI, t > 0, Lambda = mu = t, Lambda/mu = 1, but the completed circuit has norm t and its inverse has norm 1/t, so the left side is >= |log t|, unbounded as t varies. (Reviewer observation, Mister-Meeseeks, review of PR 1758.) The proof below is written with Lambda + 1/mu throughout.

**Corollary 4.1b (unit-diagonal kernels: ratio-only form).** If in addition every diagonal entry d of H satisfies |d - 1| <= 1/2 (in particular d = 1, the normalised kernels G'_s), then Lambda >= |d| >= 1/2 and mu <= Re d <= 3/2 (test the accretivity inequality on a unit vector e_j: Re H_jj >= mu; and ||H|| >= |H_jj|). Hence 1/mu <= 2 Lambda/mu and Lambda = (Lambda mu)/mu <= (3/2) Lambda/mu, so Lambda + 1/mu <= (7/2) Lambda/mu and log(2 + Lambda + 1/mu) <= log(2 + 4 Lambda/mu) <= 2 log(2 + Lambda/mu) + O(1). For d = 1 exactly: Lambda >= 1 >= mu and Lambda + 1/mu <= 2 Lambda/mu. Therefore for unit-diagonal kernels log(max prefix / suffix / inverse-prefix norm) = O(log N log(2 + Lambda/mu) + log N), the ratio-only form originally stated, and the rounding guard is p + O(log N log(2+Lambda/mu)) bits.

*Proof.* Identical to SHALLOW-TOEPLITZ sec. 4, 5, 6, 9 except for the single place where the hypothesis is used, the uniform control of every recursive matrix, which we prove now.

(a) *Descendants are Schur complements of sections.* Let T_b be the leading b x b section of H. The recursion of sec. 4 acts on index intervals J = [a,b); the matrix at J is S(a,b) = T_b / T_a (Schur complement of the leading a x a block of T_b, as an (b-a) x (b-a) matrix). Indeed the root is S(0,N); the children of S(a,b) with midpoint m are S(a,m) = T_m/T_a (leading block of S(a,b)) and S(a,b)/S(a,m) = T_b/T_m by the quotient property (T_b/T_a)/(T_m/T_a) = T_b/T_m. All of these are contiguous leading-type sections of the same Toeplitz H.

(b) *Accretive matrices.* If Re <Tx,x> >= mu ||x||^2 then ||Tx|| >= mu||x||, so ||T^-1|| <= mu^-1; every principal submatrix has the same property. Hence ||T_b^-1|| <= 1/mu for all b and ||S(a,b)^-1|| = ||(T_b^-1)[a,b)|| <= 1/mu (absolute bounds, not ratios). Also ||S(a,b)|| <= ||T_b[a,b)|| + ||T[a,b); [0,a)|| ||T_a^-1|| ||T[0,a); [a,b)|| <= Lambda + Lambda^2/mu =: Lambda'. The shear matrices K = A^-1 B, L = C A^-1 have norm <= Lambda/mu (a product of an inverse bound 1/mu and a norm bound Lambda; with the absolute guard Lambda/mu <= (Lambda+1/mu)^2). Writing M := 2 + Lambda + 1/mu, every quantity so far is <= M^3: ||S|| <= Lambda' <= M^3, ||S^-1|| <= M, ||K||, ||L|| <= M^2, and so Lambda' + 1/mu <= 2 M^3 =: M'. (No Hermitian structure was used.)

(c) *Displacement rank, generators, compiler.* Sec. 4's rank identities (Delta = ZM - MZ, rank Delta(H) <= 2, ranks of A,S <= 2 + depth) and the sec. 5 bounded-generator compiler use only that each node's A, S, K, L are bounded matrices with the displayed ranks; the Stein generators g_j (orthonormal), h_j (norm <= ||E_T|| <= 2 Lambda'') have polynomial norm, and gamma_P = 64 N Lambda'' suffices, where Lambda'' is any common bound for the norms of the node matrices and their inverses, here Lambda'' = M' = 2 (2+Lambda+1/mu)^3 (the inverse bound 1/mu enters through it; it is not a function of Lambda/mu). The recursion D_full(N) <= D_full(N/2) + O(log^3 N) is unchanged.

(d) *Prefix norms.* With each completed node factor of norm and inverse norm <= poly(N) M'^{O(1)}, B(N) <= max(C B(N/2), N^C M'^C), so log B(N) = O(log N log M') = O(log N log(2+Lambda+1/mu)) as in sec. 9 (M = Lambda, 1/mu there; Lambda'' = Lambda' + 1/mu <= 2 (2+Lambda+1/mu)^3, which changes log only by the constant 3). For H = tI this correctly gives log B >= |log t|. QED.

**Corollary 4.2 (perturbation, truncation, rounding).** If the symbol is perturbed in l1 by eps' <= mu/2 (band truncation at W, rounding to Cp bits), the Hermitian part stays >= mu/2, the norm stays <= Lambda + mu/2, and Theorem 4.1 applies to the perturbed matrix with (Lambda, mu) replaced by (Lambda + mu/2, mu/2) (guard log(2+Lambda+mu/2+2/mu) <= log(2+Lambda+1/mu)+O(1) as mu <= 3/2). Truncation at any band W >= 0 and rounding of the kernel to Cp bits (fixed or floating point) do not touch the diagonal entry G'_s(0) = 1, which is exactly representable and is the u = 0 term kept by every truncation; so the perturbed kernels remain exactly unit-diagonal and Corollary 4.1b applies verbatim (Lambda >= 1 >= mu for the perturbed matrix). Were the diagonal to drift (e.g. a diagonal conversion with a rounding error), a drift |d-1| <= 2^{-Cp} <= 1/2 is covered by the hypothesis |d-1| <= 1/2 of Corollary 4.1b; the constants change by factors <= 7/2 only (stage F of `check_gaugefree.py`). For the broad kernel the truncation tail is <= 2^{-p}, and mu >= p^{-O(1)}.

**Corollary 4.3 (boundary pivots for the structured boundary).** The boundary LU pivot P_j of STRUCTURED-BOUNDARY (Schur complement of T[J] onto segment j after eliminating all indices left of it and the interval I_j to its right, J = [0, end of I_j)) satisfies ||P_j^-1|| <= 1/mu, ||P_j|| <= Lambda + Lambda^2/mu, because P_j^-1 is the principal block of (T[J])^-1 and T[J∖seg_j] is a principal submatrix of T[J], both accretive. The couplings are band entries of G_s. The statement holds per constant-offset stretch: each stretch of a cell (maximal run with constant phase offset c, i.e. one Toeplitz matrix T, one shift s) is handled with its own anchor at the segment centre, so that the chirp D' = exp(a theta t^2) (broad: b0 theta t^2) has range a theta B'^2/4 for boundary segments of physical length B' <= B + 2W (and the linear leftover is <= 2 b0 theta B'); a pivot chain crossing a cell cut restarts, since cell cuts are boundary coordinates. Rank-2 Stein/Sylvester displacement for P_j, P_j^-1 holds for every Toeplitz T (Kailath), shifted or not; screened in `check_gaugefree.py` D/E and in the earlier IdeaOuter screen (displacement rank 2 along the whole chain at s = 0.5). Thus the structured-boundary pivot bounds (which used BILATERAL-LDU for the unshifted gauge) transfer without change of statement.

## 5. Assembly and the guard

For every capped interior (dyadic length n <= B, with its own anchor and shift s):
 broad: Drow' (circuit of G'_s, Theorem 4.1 with mu = mu(b0 lambda, s); unit diagonal, so Corollary 4.1b applies)) Dcol';
 narrow: D' (circuit of G'_s, gamma = a rho) D'^-1 (inverse circuit = reversed gate sequence).
The diagonal factors Dcol', Drow', D' are anchored ratios with logarithmic range
 narrow: a theta B^2/4; broad: <= b0 theta B^2/4 (x^2 and y^2 terms) + 4 b0 theta B (linear leftover) .
Per axis the range is O(a B^2/d); direct sums over blocks run in parallel as before. For g simultaneous axes the precision requirement of CAPPED-GAUGE-AUDIT sec. 4 becomes
 P >= p + O(a d) + O(g a theta B^2) + O(g log N log p) + ... , i.e. g B^2/d * polylog <= p^{1-r-zeta}:
 **beta + 2 xi - eps <= 1 - r - zeta**.
The offline accuracy term a d = o(p) is unchanged. The leftover linear term (exponent beta + xi - eps) is dominated by the chirp (exponent beta + 2 xi - eps) since xi > 0. The circuit norms add g * O(log N log(2+Lambda+1/mu)) bits (Theorem 4.1); here Lambda <= 3 + sqrt(2 pi/gamma) and 1/mu = p^{O(1)} (Section 3), so Lambda + 1/mu = p^{O(1)} directly (and by Corollary 4.1b equivalently Lambda/mu = p^{O(1)}), i.e. g * O(log N log p) bits, polylog per axis, as before. The precision assertion is stated with the absolute-scale guard, not with a ratio alone; the exponent beta + 2 xi - eps and every ledger number are unchanged.
(Why this does not collide with locality: the audited locality/halo constructions use the global rounded matrix only through uniform norms and the row gap, which are properties of the same Toeplitz-similar matrices; the shift is an exact similarity-to-Toeplitz representation of the same blocks, Lemmas 2.1-2.2.)

## 6. Ledger changes (exact)

1. `group_gauge_power_slack`: 1 - xi - r - beta -> **1 - (2 xi - eps) - r - beta**; `actual_logarithmic_group_guard`: 1 - xi - beta -> **1 - (2 xi - eps) - beta**. Add `shift_leftover_linear_dominated_by_chirp`: xi > 0, `shift_gap_theta_polynomial`: eps > 0.
2. Parameters: eps = (1 + q beta)/(1 + q) (main = Gaussian), xi = eps(1+q) - c + slack (boundary = main + slack), beta = 1 - 2 xi + eps - r - zeta. Closed form beta = (-1 + 2c - 2 slack + 1/(1+q) - r - zeta)/(1 + 2q - q/(1+q)), c = (3 - tau_eff)/2.
3. `union_tag_work_fits_record` (1 - 2 beta) -> **`union_tag_work_per_visit_fits_record`: 1 - beta** (Section 7). `union_header_fits_record` (1-beta) and `membership_arithmetic_fits_record` (1 - beta - 2(1-eps)) stay: pkg8 values 3.354e-3 and 3.343e-3.
4. Controls added: `old_linear_gauge_guard` (1 - xi - beta < 0), `old_union_tag_2beta` (1 - 2beta < 0) must fire as rejecting controls (they do).
5. Numbers (this package): eps = 0.99999437577296, xi = 0.50167412128176, beta = 0.99664613320944; margins above kappa: main = Gaussian = bit router = boundary = union ~ 1e-64; global router 9.4e-9; cap xi - 1/2 = 1.674e-3; group_below_dimension 3.35e-3; epsilon_below_one 5.6e-6; improvement over pkg7 1.4013e-6.
`outer/check_ledger.py` carries exactly these edits relative to the previous (structured-boundary, linear-guard) package; `outer/independent_check.py` re-derives (E,X,B) from the three linear equations by exact elimination.

## 7. Union tag work: g polylog <= p suffices

The previous version of UNION-SCHEDULE.md (steps 1 tag and section 3 header paragraph) argued "tag work per record <= O(g^2) in total, o(p) because 2 beta < 1". The cost accounting of Section 2.3-2.4 of that note is per visit: round r touches only records of S_r; each visit costs O(p log g + p log a + 1) head travel (radix passes, transposition) plus the tag extraction O(g) bit operations (scan of the g-bit flag header for the r-th set bit) plus O(g log L) header travel (the header is carried with the record). Sum over rounds = sum_r |S_r| = sum_x |F(x)| <= g mu V (Section 2.4). Total = O(g mu V (p polylog p + g log L)) = O(g mu V p polylog p) as soon as g log L = o(p polylog p), i.e. beta < 1 (and this is already the header check `union_header_fits_record`). The O(g^2) per-record total is a pessimistic restatement: each of the |F| <= g visits of a record is paid for by its own Theta(p) move. UNION-SCHEDULE.md now carries this wording. A reviewer should confirm no other place charges g^2 per record.

## 8. Obligations / risks (review checklist)

1. Theorem 4.1 relies on SHALLOW-TOEPLITZ sec. 4-6 (not re-derived); only the descendant bound (Section 4(a)-(b)) is new, and it carries the absolute-scale guard log(2+Lambda+1/mu) (corrected from a ratio-only statement; the application is unaffected because the kernels are unit-diagonal, Corollary 4.1b). The finite replay (`check_gaugefree.py` stage E: the vendored compiler on shifted Gaussian tiles n = 8, 16, 32, gamma in {0.5, 2, 20}, s up to 0.499: max error 1.8e-12, displacement rank <= 3, peak prefix norm <= 91 for n = 8, 16, max generator entry <= 11.4) supports it. The peak prefix norm is tracked only for n <= 16; for n = 32 it is not computed (reported as null).
2. The tile is a contiguous section of the *banded, truncated, rounded* shifted kernel; Corollary 4.2 covers it. The audited global rounded matrix remains the reference for the locality/Neumann/halo arguments; its comparison with the ideal kernel is stated in Section 2 (error poly(p) 2^{-Cp} e^{O(g a theta B^2)} = 2^{-(C-o(1))p}, C > 1).
3. Narrow N formula taken from LOG-A-PHASE-SCHUR-AUDIT (`n_{i,h}`), verified symbolically against the quoted weights of CAPPED-GAUGE-AUDIT sec. 2 (stage A). Broad block formula from CAPPED-GAUGE-AUDIT sec. 3.
4. The parameter point sits at beta = 0.9966, 1 - beta = 3.35e-3: header (g log L bits) and membership (g (log s)^2) rows hold only "eventually", with exponent margins 3.3e-3; the claim is an asymptotic statement with the same status as the other margins (1e-64 slacks).
5. Not changed: supplier, bit/complex rows, union schedule beyond Section 7, cap xi > 1/2 (still binding at 1.67e-3).
6. STRUCTURED-BOUNDARY.md now states the chirp range O(aB^2/d) for consecutive boundary segments (physical length <= B + 2W) and cites Corollary 4.3 for the pivot bounds.
