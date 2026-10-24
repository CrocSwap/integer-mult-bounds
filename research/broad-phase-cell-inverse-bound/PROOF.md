# A finite phase-cell Gaussian inverse bound from coupled gauges

JoyboyBrian, with substantial OpenAI Codex assistance. Written scoped theorem; finite certificates and independent review are separate evidence. Sources: PR4193 PROOF.md §3a (exact Gaussian Toeplitz inverse entry estimate), PR1673 FORWARD-SMALL-A-AUDIT.md §2,4 (actual broad phase-cell matrix and exact diagonal factorization), PR4435 explicit unproved rigorous-upper-bound handoff. No leading asymptotic constant or physical theorem claimed.

Let alpha>0, theta>0, rho=1+theta, lambda=1/rho, b0=pi/alpha², gamma=b0/rho. Take a finite contiguous interval I of N>=1 integers and c real, with beta_k=theta*k-rho*c in[-1/2,1/2] for every k in I. Define K[k,i]=alpha^-1 exp(-b0*(i-lambda*k-c)²). Put q=exp(-gamma), P_j=product_{r=1}^j(1-q^(2r)), P_0=1.

The explicit estimate is

 |K^-1[i,j]| <= A_N exp(-gamma*theta*(i-j)²),
 A_N=alpha exp(b0/(4rho²)) / P_(N-1)^3,
 ||K^-1||_2 <= A_N min(N,1+sqrt(pi/(gamma*theta))).

It holds on the closed phase interval, so also on the source's half-open interval. Necessarily theta(N-1)<=1, but no extra cap N<=p^xi is assumed. Constant alpha or growing alpha must be distinguished; the formula displays both dependencies.

Proof. Shift I to0,...,N-1, replacing c by c-(1-lambda)*min(I), so beta and K remain unchanged. Set G[i,j]=exp(-gamma*(i-j)²). The exact source factorization is K=Dr G Dc, where

 Dc[i]=exp(-b0*(theta/rho*i²-2c*i)),
 Dr[j]=alpha^-1 exp(b0*(theta/rho²*j²-2c/rho*j-c²)).

Indeed their exponents sum to -b0*(i-j/rho-c)². PR4193 proves for this exact finite Gaussian Toeplitz G that |G^-1[i,j]|<=exp(-gamma*|i-j|)/P_(N-1)^3. Its proof uses exact finite q-LDU and both half-shift endpoints, without a symbol-margin assumption or numerical inverse.

Since K^-1=Dc^-1 G^-1 Dr^-1, retaining the two gauges together gives the exponent

 E_ij = b0*beta_j²/rho² + gamma*((i-j)*(beta_i+beta_j)-|i-j|).

This follows by expanding the displayed diagonal factors and beta_i=beta_j+theta*(i-j). It is an exact identity, not a norm estimate on each diagonal separately.

For d=i-j>=0, beta_i<=1/2 and beta_j=beta_i-theta*d, so beta_i+beta_j<=1-theta*d; hence d*(beta_i+beta_j)-d<=-theta*d². For d<0, write h=-d>0. beta_i>=-1/2 and beta_j=beta_i+theta*h, so beta_i+beta_j>=-1+theta*h; hence -h*(beta_i+beta_j)-h<=-theta*h². The remaining beta_j²<=1/4 gives the stated entry envelope.

Every row and every column of exp(-a*(i-j)²), a=gamma*theta>0, has sum at most N and at most 1+2*sum_{h>=1}exp(-a*h²). Monotone integral comparison gives the latter <=1+2*integral_0^infinity exp(-a*x²)dx=1+sqrt(pi/a). The Schur row/column bound ||M||_2<=sqrt(||M||_1||M||_infinity) proves the norm estimate.

The exact finite product may be kept. If a closed elementary coefficient is wanted, log P_infinity^-1=sum_{m>=1}1/[m*(exp(2gamma*m)-1)]<=pi²/(12gamma), so P_(N-1)^-3<=exp(pi²/(4gamma)). Thus a weaker explicit prefactor is alpha exp(pi/(4alpha²rho²)+pi*alpha²rho/4). The theta exponent is rigorously -1/2 with an explicit alpha-dependent coefficient. This does not claim PR4435's sharp coefficient exp(pi alpha²/4)/(2alpha sqrt(pi)). No source parameter-family consequence is used until separately checked.

What is new versus sources: PR4193 controls constant-shift capped sections with N/P³ and separately maximized small gauges; PR4435 leaves the varying-phase full-cell boundary estimate unproved. This uses the predecessor entry theorem with the exact coupled gauges, obtaining Gaussian off-diagonal decay across the full admissible cell. Exact q-LDU, the earlier constant-shift theorem, gauge identity and Gaussian integral remain credited dependencies, not new results.

## Retained finite Toeplitz entry lemma

Here is the dependency in full, following PR4193 and its credited q-LDU
lineage. Define Q=q² and the Gaussian binomial coefficient
[k choose i]_Q=P_k/(P_i P_(k-i)). For G[i,j]=q^((i-j)²), finite
Vandermonde elimination gives G=L diag(P_i) L^T with
L[i,j]=q^((i-j)²)[i choose j]_Q for i>=j. Its inverse is
Linv[i,j]=(-q)^(i-j)[i choose j]_Q: substitution reduces each nontrivial
product entry to the finite q-binomial identity
sum_r(-1)^r Q^(r(r-1)/2)[n choose r]_Q=product_(r=0)^(n-1)(1-Q^r)=0.
Thus every finite G is invertible.

For D[i]=q^i, the lower factor D Linv D^-1 has entries in absolute value
Q^(i-j)[i choose j]_Q <= Q^(i-j)/P_(i-j). Its column sums are at most
sum_(r=0)^(N-1) Q^r/P_r=1/P_(N-1), since the summands for r>=1
telescope as 1/P_r-1/P_(r-1). The upper factor D Linv^T D^-1 has
entries [j choose i]_Q<=1/P_(N-1), and each inverse pivot is at most
1/P_(N-1). Consequently every entry of D G^-1 D^-1 is bounded by
P_(N-1)^-3. The opposite diagonal gauge gives its transpose. Choose the
endpoint gauge according to the sign of i-j to obtain
|G^-1[i,j]|<=q^|i-j|/P_(N-1)^3. These are predecessor identities; the
new step is retaining the varying-phase inverse gauges together.

## Evidence, cost and limits

The first source fixture is alpha3,theta1/400,N400,beta_start=-1/2.
The verifier executes the retained block setup/exponent AST with exact
rational scalars after factoring out pi; this is an expression-level source
check, not execution of the original floating-point inversion program. It
checks the coupled identity on boundary/diagonal pairs and the phase decay
inequality on all160000 pairs. Directed intervals enclose36 actual finite
inverse entries via the exact q-LDU sum, without truncating the Gaussian
band, and compare the new envelope with the old displayed ceiling. Independent
rational elimination checks the Toeplitz identity at small exact q values.
Python Decimal correctly-rounded exp/sqrt, widened by adjacent representable
values, is an explicit arithmetic dependency; pi uses rational Machin bounds.

The proof bounds an exact completed inverse. It supplies no algorithm for
applying that inverse at a claimed fast tariff, and it does not reduce
coefficient preparation, tape movement, storage, rounding, native or outer
costs. All those obligations remain. The finite certificate is not the
proof of universal quantifiers; those are the algebra and inequalities above.
No leading asymptotic constant, matching lower bound, or changed selected
frontier is claimed. No whole-cell source gauge is replaced by an uncharged
unitary transformation.

## Open next questions

- Can the explicit alpha-dependent constant be sharpened to PR4435's formal
  leading coefficient, with a matching lower estimate and boundary remainder?
- Can the actual complete Gaussian error/rounding caller consume this bound
  while retaining every coefficient, prefix and physical execution cost?
