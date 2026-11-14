# Broad forward Gaussian: finite-block and completed-matrix conditioning

This note supports the phase-assembly branch. It distinguishes the broad forward map S from the narrow T used in N=C T D. Its conclusions concern conditioning and local circuit guards; the final simultaneous tensor layout remains that branch's obligation.

Let the narrow parameter be `a=pi alpha^2=Theta(log p)`, `rho=t/s=1+theta`, and `lambda=1/rho`. The forward map is

`S_(k,j)=alpha^-1 exp[-b0(j-lambda*k)^2]`, `b0=pi/alpha^2`.

Equivalently it uses the small resampling parameter

`b=b0 lambda^2=pi/(alpha^2 rho^2)`.

## 1. The bilateral bound works at every positive parameter

The finite and bilateral LDU arguments in BILATERAL-LDU.md use a>=1 only for their final numerical simplification of the product c. For any b>0, define

`c_b=prod_(m>=1)(1-exp(-2b rho m))`.

The same proof gives, for the periodic normalized matrix and for every finite contiguous principal block with q-gaps at least 1 and |beta_i|<=1/2,

`||N_b^-1|| <= c_b^-4 exp(b/2)/(1-exp(-b rho theta))^2`.

There is an explicit useful product bound. Expand the logarithm and sum nonnegative terms:

`log(c_b^-1)=sum_(k>=1) 1/[k(exp(2b rho k)-1)]`

` <=(1/(2b rho)) sum_(k>=1)1/k^2=pi^2/(12b rho)`.

At `b=pi/(alpha^2 rho^2)`, this implies

`c_b^-4 <= exp(pi alpha^2 rho/3)=exp(a rho/3)`.

Since b*rho*theta=pi*theta/(alpha^2 rho)<1 for alpha>=2 and theta<=1, its reciprocal gap is at most `2alpha^2 rho/(pi theta)`. Thus every such normalized block inverse has norm polynomial in p when alpha^2=O(log p) and theta^-1 is polynomial in p.

## 2. Actual target-grid phase-cell block

Embed source j at target coordinate i=q_j. On an original phase cell q_j=j+c, every selected target coordinate i in that cell corresponds to j=i-c. A square interior of the forward target-grid matrix is therefore

`K_(k,i)=alpha^-1 exp[-b0(i-lambda*k-c)^2]`.

Here both i and k run over one contiguous selected-target interval inside that cell. Put

`q'_k=k+rho*c`, `beta'_k=rho*k-q'_k=theta*k-rho*c`.

At a selected coordinate k=q_j, beta'_k is exactly the original beta_j, hence lies in [-1/2,1/2). Also q' has consecutive gap 1. Integrality of q' was never needed in the finite LDU proof; monotone separation and the beta bound suffice. Consequently

`K=alpha^-1 N_b diag(exp(-b*(beta'_i)^2))`,

and

`||K^-1|| <= alpha exp(3b/4) c_b^-4/(1-exp(-b rho theta))^2`

` =O(alpha^5 rho^2 theta^-2 exp(pi alpha^2 rho/3))=poly(p)`.

This controls the **completed** interior inverse. It avoids multiplying the large individual diagonal-gauge norms to estimate K inverse. Target holes should be retained as boundary vertices, so every interior coordinate has the asserted original beta bound.

## 3. Square completion of the global forward map

Add one identity column e_h for every target hole h, and feed zero into these extra columns. This makes an invertible square t-by-t matrix H_aug without changing the desired forward result. Permute selected q_j rows/columns first and holes second. In that order,

`H_aug = [ alpha^-1 N_b D_b^-1   0 ; R   I ]`,

where `D_b=diag(exp(b beta_j^2))` and R consists of broad Gaussian rows at holes. A Gaussian lattice-sum bound gives `||R||=O(1)` after the alpha^-1 factor. Thus

`H_aug^-1=[ alpha D_b N_b^-1   0 ; -R alpha D_b N_b^-1   I ]`

has polynomial row norm. The matrix itself also has O(1) row norm. Gaussian truncation and sufficiently accurate structure-preserving coefficient rounding perturb both it and all required interior blocks by exponentially small amounts, preserving these polynomial bounds.

If A is the block-diagonal interior matrix and S is the completed boundary Schur complement, then S inverse is the boundary principal block of H_aug inverse; hence its norm is polynomial. Also

`||S||<=||H_BB||+||H_BI|| ||A^-1|| ||H_IB||=poly(p)`.

This is enough for the completed Schur map. To justify a particular sequential block-LU implementation, its prefix factor norms still need to be checked. The natural physical-prefix elimination sets consist of one contiguous selected-source prefix plus disjoint future interiors, with identity hole columns. That geometry offers the same uniform contiguous-block inverse bound; it should be made explicit in the assembly proof.

## 4. Exact local Toeplitz split and guard range

Choose an anchor m inside the target cell, and write x=i-m, y=k-m,

`delta=(1-lambda)m-c`, with |delta|<=1/2.

Then the exact factorization is

`K_(k,i)=Drow(y) G(y,x) Dcol(x)`,

`G(y,x)=exp[-b0 lambda(x-y)^2]`,

`Dcol(x)=exp[-b0((1-lambda)x^2+2delta*x)]`,

`Drow(y)=alpha^-1 exp[b0 lambda(1-lambda)y^2+2b0 delta lambda*y-b0 delta^2]`.

Expansion gives exactly `-b0(delta+x-lambda*y)^2`; no approximate recentering is involved. On a phase cell of O(d) coordinates, the two diagonal logarithmic ranges are O(d/alpha^2). These are smaller than the O(alpha^2 d) narrow inverse gauges already paid by the proposed group size.

## 5. SPD Toeplitz conditioning for the shallow circuit

Let `gamma=b0 lambda=pi/(alpha^2 rho)`. The full Gaussian Toeplitz symbol has, by the Gaussian Poisson identity,

`f(omega)=sqrt(pi/gamma) sum_(k in Z) exp[-(omega+2pi*k)^2/(4gamma)]`.

For -pi<=omega<=pi,

`sqrt(pi/gamma) exp[-pi^2/(4gamma)] <= f(omega) <= 1+sqrt(pi/gamma)`.

Every finite principal Gaussian Toeplitz matrix has eigenvalues between these same bounds, by integrating the squared modulus of its coefficient polynomial against f. At alpha^2=O(log p), its condition number is polynomial in p. Truncation width O(sqrt(p/gamma)) and Cp-bit rounding perturb the matrix far less than its lower eigenvalue, so the actual symmetric rounded Toeplitz Ghat remains SPD with polynomial condition number.

The low-displacement block-LU circuit of SHALLOW-TOEPLITZ.md extends from near identity to this SPD setting: every principal Schur complement has norm at most lambda_max and inverse norm at most lambda_min^-1, and ranks grow by the same additive displacement recurrence. Shear coefficients are polynomial in p; multiplying these bounds along O(log d) recursive levels gives exp(O(log^2 p)) partial-prefix growth. This calls for O(log^2 p) internal circuit guard bits per axis, rather than claiming the near-identity theorem's O(log p) unchanged. It is still below the group budget dominated by the local Gaussian diagonals.

Dyadic interior subdivision from LOG-A-PHASE-SCHUR-AUDIT.md applies here too, using the broader width O(sqrt(p alpha^2)). It keeps target holes and separators as boundary, adds only polylogarithmic boundary volume, and lets every interior use a dyadic shallow circuit without 2^g padding.

No numerical final exponent follows from these conditioning statements alone.
