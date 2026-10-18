# Scale qualification of the accretive Toeplitz circuit (erratum to GAUGEFREE-INTERIORS Theorem 4.1)

**Source of the correction.** The maintainer review of PR1758 at
https://github.com/CrocSwap/integer-mult-bounds/pull/1758#issuecomment-6203527654 (retained by this PR, #2265). This note is
this package's own text. The files that carry the uncorrected statement are inherited verbatim and are **not edited**:
`outer/GAUGEFREE-INTERIORS.md` (PR1758 text as bundled by PR2220; only a pointer note is prepended, following PR2220's own
package-note precedent), `outer/FINE-PADDING-COMPOSITION.md` (table row "accretive circuit lemma", obligation 3) and
`vendor/pr1786/FINE-PRIME-PADDING.md` (section 3, "Its accretive shallow-circuit theorem therefore has polylog(p) guard bits").
Wherever those files cite the accretive circuit theorem, this package relies on the form stated here.

## 1. The defect

GAUGEFREE-INTERIORS Theorem 4.1 states, uniformly in Lambda and mu,
`log(max prefix / suffix / inverse-prefix norm) = O(log N log(2 + Lambda/mu) + log N)`.
This is false as a uniform statement: for N = 2 and H = tI (t > 0), Lambda = mu = t, so Lambda/mu = 1, but the completed
circuit has norm t and its inverse norm 1/t; the left side is at least |log t|, unbounded in t. The precision statement
`p + O(log N log(2 + Lambda/mu))` bits has the same defect. (`check_accretive_scale.py` stage A.)

## 2. Corrected statement

**Theorem 4.1' (general form).** Let N be a power of two and H an N x N complex Toeplitz matrix with ||H||_2 <= Lambda and
(H + H^*)/2 >= mu I, mu > 0. The circuit of Theorem 4.1 (same rounds, gates, no ancilla) has

    log(max prefix / suffix / inverse-prefix operator norm) = O(log N * log(2 + Lambda + 1/mu) + log N),

and rounding every coefficient to p + O(log N * log(2 + Lambda + 1/mu)) bits gives operator error 2^-p.
This is the absolute-scale guard already used by the vendored PR1673 `SHALLOW-TOEPLITZ.md` sec. 9 (line 195,
`log(2+M+1/mu)`), on which the proof of Theorem 4.1 rests.

*Proof changes.* Step (b) of the proof is unchanged and already absolute: every descendant S(a,b) = T_b/T_a satisfies
||S^-1|| <= 1/mu and ||S|| <= Lambda + Lambda^2/mu =: Lambda'; the shears K = A^-1 B, L = C A^-1 have norm <= Lambda/mu.
Step (d) must read "each completed node factor has norm <= poly(N) Lambda'^{O(1)} and inverse norm <= poly(N) mu^{-O(1)}",
hence log B(N) = O(log N log(2 + Lambda' + 1/mu)); and log(2 + Lambda' + 1/mu) = O(log(2 + Lambda + 1/mu)) since
Lambda' <= (Lambda + 1/mu)^3 (Lambda^2/mu <= (Lambda + 1/mu)^3 by the binomial term 3 Lambda^2/mu, and Lambda <= (Lambda + 1/mu)^3
because Lambda >= mu gives Lambda + 1/mu >= mu + 1/mu >= 2). The only error was replacing the pair (Lambda', 1/mu) by
the single ratio Lambda'/mu.

**Corollary 4.1'' (ratio form, unit diagonal).** If in addition H has unit diagonal (h_0 = 1), then
Lambda >= |h_0| = 1 (||H|| >= ||H e_0|| >= |h_0|) and mu <= Re <H e_0, e_0> = 1, so

    Lambda + 1/mu <= 2 Lambda/mu       (2 Lambda/mu - Lambda - 1/mu = (Lambda - 1)/mu + Lambda (1 - mu)/mu >= 0),

and the bounds of Theorem 4.1 hold as originally written, with log(2 + Lambda/mu) (constant factor absorbed in the O).
The hypothesis is needed **at the root kernel only**: descendants do not keep unit diagonal, but their bounds are in root
quantities, and on unit diagonal Lambda' + 1/mu <= 3 (Lambda/mu)^2, 2 + Lambda' + 1/mu <= 4 (2 + Lambda/mu)^2,
1/mu <= Lambda/mu, shears <= Lambda/mu. So every per-node log factor is <= 2 log(2 + Lambda/mu) + log 4.
(`check_accretive_scale.py` stages B and C: exact polynomial-coefficient checks.)

*Near-unit fallback.* If |h_0 - 1| <= 1/2 then |h_0| >= 1/2 and Re h_0 <= 3/2, and
Lambda + 1/mu = (Lambda/mu)(mu + 1/Lambda) <= (Re h_0 + 1/|h_0|) Lambda/mu <= (7/2) Lambda/mu (stage D).

## 3. Truncated and rounded kernels (Corollary 4.2) and boundary pivots (Corollary 4.3)

* **Corollary 4.2.** Band truncation at W removes only off-diagonal coefficients, and G'_s(0) = e^0 = 1 is stored exactly
  (the inherited texts fix it: GAUGEFREE-INTERIORS Section 2, "G'_s(0) = 1 (unit diagonal, as the audited N)";
  FINE-PRIME-PADDING section 3, "rounded Gaussian entries, with diagonal exactly one"). So the truncated/rounded kernel
  has diagonal exactly one and Corollary 4.1'' applies to it directly with (Lambda + eps', mu/2), eps' <= mu/2:
  Lambda + eps' >= 1 and mu/2 <= 1/2, so the guard is O(log N log(2 + Lambda/mu)). Even if a diagonal were perturbed by
  |delta| <= mu/2 <= 1/2, the near-unit fallback gives the same order with constant 7/2.
* **Corollary 4.3.** The pivot bounds ||P_j^-1|| <= 1/mu and ||P_j|| <= Lambda + Lambda^2/mu are absolute statements and
  remain true; where they feed a circuit or precision guard, the root kernel G'_s is unit diagonal, so the descendant
  inequalities of Section 2 convert them to the ratio form.
* **Descendant / shear bounds** (proof step (b)): unchanged as absolute statements; in ratio form only via Section 2.

## 4. Our application satisfies the restricted hypothesis

Both circuits applied in GAUGEFREE-INTERIORS Section 5 are circuits of the normalised kernel
G'_s(u) = exp(-gamma u^2 + 2 gamma s u) (broad: gamma = b0 lambda; narrow: gamma = a rho), whose diagonal is G'_s(0) = 1;
the narrow block itself has N_ii = 1 (Lemma 2.2 at h = 0). The anchored chirps and the constants e^{gamma s^2} are
outside the circuit (diagonal factors, exact anchor ratios). Hence the root kernel has unit diagonal, Lambda >= 1, mu <= 1,
and the inherited parameter values (Section 3 of GAUGEFREE: Lambda <= 3 + sqrt(2 pi/gamma), mu >= p^{-O(1)} for
theta^-1 = O(p^2), the fine-prime range of PR1786) give log(2 + Lambda + 1/mu) <= log 2 + log(2 + Lambda/mu) = O(log p),
i.e. **O(log N log p) guard bits per axis, exactly as stated**. `check_accretive_scale.py` stage E checks symbolically
G'_s(0) = 1 and N_ii = 1, and on exact rational truncated/rounded sections (gamma in {1/2, 2, 20}, s in {0, 1/4, +-0.499},
n in {2, 4, 8}) that the diagonal is exactly one, e0* H e0 = 1, ||H e0||^2 >= 1 and the Hermitian part is positive definite
(exact LDL^T).

## 5. Effect on numbers and on the claim

**None.** The circuit guard enters the ledger only as an additive g * polylog(p) bit term inside the o(p) precision
budget; `outer/check_ledger.py`, `outer/independent_check.py`, `LEDGER.json` and `INDEPENDENT.json` have no Lambda or mu
input, and the binding exponent inequality beta + 2 xi - eps <= 1 - r - zeta is unchanged. `outer/run_outer.py`
regenerates LEDGER.json / INDEPENDENT.json byte-identically after this change; kappa is unchanged. The correction
changes which form of the theorem the package relies on (Corollary 4.1'' / Theorem 4.1'), not any exponent or constant
of the ledger. The rest of the shared PR1673 / PR1758 / PR1786 analytic and fixed-tape review is unaffected by this note
and remains open, as stated in README.md.

Credit: the counterexample and both repairs are the maintainer's (PR1758 review); Theorem 4.1 and its proof are PR1758's,
resting on PR1673 (Vlado Vojdanovski) SHALLOW-TOEPLITZ.md.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0.
