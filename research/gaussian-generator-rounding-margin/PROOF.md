# A quantitative rounding margin for Gaussian tensor generators

Base: `e54523517d0f03e58352e647c403a5af3e525a57`.

This strengthens the boundary-minor calculation in the predecessor
`tensor-gaussian-displacement-rank` package. The required algebra is restated
here. The conclusion concerns an exact ordinary Toeplitz-generator
representation of an approximate matrix, not runtime or separable circuits.
No foundational assumption is discharged and no new kappa is claimed.

All norms below are spectral operator norms. Indices start at zero; Z_k is
the k-by-k strict lower shift. Define `E(X)=X-Z_k X Z_k^T`. The lower and
upper triangular Toeplitz matrices L(u), U(v) have first column u and first
row v. Since `E(L(u)U(v))=u v^T`, an exact representation of X by r such
products implies `rank E(X)<=r`. X may itself approximate another target.

## 1. Quantitative boundary-minor lemma

Let A be invertible of size m, and B Toeplitz of size n>=2, with
`B_ij=b_(i-j)`. Put H=`A tensor B`, the B index fastest, and set

\[
 R=b_{-1}I_m-b_{n-1}Z_m,\quad
 S=b_1I_m-b_{-(n-1)}Z_m^{\mathsf T},\quad
 P=b_0(A-Z_mAZ_m^{\mathsf T}).
\]

Select rows and columns of E(H) with fastest indices 0 and 1, grouping the
zero-index coordinates first. Entrywise subtraction gives the minor

\[
 M=\begin{pmatrix}P&RA\\AS&0\end{pmatrix}.
\]

Every entry of E(H) with both fastest indices positive vanishes, so
`rank E(H)<=2m`. If `b_-1 b_1` is nonzero, R and S are invertible and

\[
 M^{-1}=\begin{pmatrix}0&(AS)^{-1}\\
 (RA)^{-1}&-(RA)^{-1}P(AS)^{-1}\end{pmatrix}.
\]

Suppose `U>=||A||`, `V>=||A^-1||`, `alpha>=||R^-1||` and
`zeta>=||S^-1||`. The triangle and product inequalities imply

\[
 \|M^{-1}\|\le K:=V(\alpha+\zeta)
                 +2|b_0|UV^2\alpha\zeta.\tag{1}
\]

Hence `rank E(H)=2m`, and its 2m-th largest singular value is at least 1/K:
selecting rows and columns cannot increase the correspondingly indexed
singular value, while M has least singular value `1/||M^-1||`.

**Approximation consequence.** If

\[
 \|X-H\|<1/(2K),\tag{2}
\]

then `rank E(X)>=2m`, so X needs at least 2m ordinary `L(u)U(v)` terms.
Indeed, `||E(X)-E(H)||<=2||X-H||`, and the selected perturbed minor remains
invertible. This allows unstructured errors. It is a lower bound, not a
claim that the perturbed displacement rank remains exactly 2m.

## 2. Gaussian geometric bounds without an exponential dimension loss

Take `b_k=exp(-gamma k^2+2 gamma s k)`, with gamma>0, |s|<=1/2 and n>=3.
Then b_0=1, both adjacent coefficients are positive, and

\[
 b_{n-1}/b_{-1}=e^{-\gamma n(n-2-2s)}\le1,
 \qquad b_{-(n-1)}/b_1=e^{-\gamma n(n-2+2s)}\le1.\tag{3}
\]

The finite geometric inverse and `||Z_m||<=1` show that

\[
 \alpha=m/b_{-1},\qquad\zeta=m/b_1\tag{4}
\]

are valid in (1). Each is at most `m exp(2 gamma)`. There is no factor
exponential in m. At n=2 and nonzero shift a ratio can exceed one: q=1/2,
v=3/2 in `b_k=q^(k^2)v^k` gives the R ratio `v^2=9/4`, and the bound
`m/b_-1` fails at m=3. The exact rank theorem remains true there. The
unshifted two-point case can separately use (4).

## 3. Inverse target and singular-value indexing

Suppose H is an invertible tensor of Toeplitz factors, so full reversal J
satisfies `J H J=H^T`. Write N=mn, r=2m, and choose
`U0>=||H||`, `V0>=||H^-1||`. Define

\[
 K_{\rm inv}=\max(K,U_0)(1+U_0)^2(1+V_0)^2.\tag{5}
\]

The r-th largest singular value of `E(H^-1)` is at least `1/K_inv`.
Consequently an approximation to `H^-1` of error below `1/(2K_inv)` needs
at least r ordinary generator terms.

To prove this, let `S_rev=H^-1-Z_N^T H^-1 Z_N`. The same matrix factors as

\[
 \begin{pmatrix}H&Z_N\\Z_N^{\mathsf T}&H^{-1}\end{pmatrix}
 =\begin{pmatrix}I&Z_NH\\0&I\end{pmatrix}
   \operatorname{diag}(E(H),H^{-1})
   \begin{pmatrix}I&0\\HZ_N^{\mathsf T}&I\end{pmatrix},\tag{6}
\]

\[
 =\begin{pmatrix}I&0\\Z_N^{\mathsf T}H^{-1}&I\end{pmatrix}
   \operatorname{diag}(H,S_{\rm rev})
   \begin{pmatrix}I&H^{-1}Z_N\\0&I\end{pmatrix}.\tag{7}
\]

Each triangular factor in (6), and its inverse, has norm at most `1+U0`.
The middle factor has N+r positive singular values, the smallest at least
`min(1/K,1/U0)`. The (N+r)-th singular value of the block matrix is therefore
at least that minimum divided by `(1+U0)^2`. Removing the factors in (7)
loses at most `(1+V0)^2` more. The H block supplies at most N singular
values, so the r-th singular value of S_rev is at least `1/K_inv`.

Reversing and transposing `E(H^-1)` produces S_rev, because of persymmetry
and `J Z_N J=Z_N^T`. These operations preserve singular values. This step
is essential; invertibility alone is not the stated same-shift argument.

## 4. Source-compatible uniform regime

Fix positive constants c0,C0,c1,xi and a fixed `0<=beta<1`. For sufficiently
large precision parameter p, let H be a tensor of g normalized Gaussian
sections satisfying

\[
 1\le g\le p^\beta,\quad 2\le n_i\le p^\xi,
 \quad n_{\rm fast}\ge3,
\]

\[
 c_0/\ln p\le\gamma_i\le C_0\ln p,
 \qquad1-2|s_i|\ge c_1p^{-2}.\tag{8}
\]

Here p is the precision parameter, not theta-function nome notation. Define

\[
 M_0=4+\pi^2/(3c_0),\quad
 Q=2\xi+3+4M_0+4C_0,\quad L=Q+\xi.\tag{9}
\]

For

\[
 p\ge\max(e,c_0c_1,2/(c_0c_1),6,8\pi/c_0),\tag{10}
\]

the one-factor estimates below give `||B_i||<=p` and
`||B_i^-1||<=p^M0`. With `T=product n_i`, it follows that

\[
 K\le4p^{(2\xi+1+2M_0+4C_0)g},
 \qquad K_{\rm inv}\le64p^{Qg}.\tag{11}
\]

Indeed, `m<=p^(xi(g-1))`, `U<=p^(g-1)`, `V<=p^(M0(g-1))`, and the
two bounds in (4) are at most `m p^(2C0)`. The terms in (1) are bounded
together by `4m^2 p^(4C0) p^((1+2M0)(g-1))`. Also `U0<=p^g` and
`V0<=p^(M0 g)`. In (5) bound the maximum by the first bound in (11), and
use `1+U0<=2p^g`, `1+V0<=2p^(M0 g)`. These give the second bound.

**Uniform rounding theorem.** If X approximates either H or `H^-1` with
entrywise error at most `2^(-Cp)`, C>0 fixed, and

\[
 Cp>7+Lg\log_2p,\tag{12}
\]

then `rank E(X)>=2T/n_fast` and X needs at least that many exact ordinary
`L(u)U(v)` terms. The entrywise error gives operator error at most
`T 2^(-Cp)` by the Frobenius norm. Since `T<=p^(xi g)`, (11)-(12) put this
error below both thresholds (2) and its inverse version. No error structure
is required.

For every fixed beta<1 and C>0, (12) holds eventually, because
`p^(beta-1) log p` tends to zero. The guard costs `O(g log p)=o(p)` bits,
so it is nonvacuous at the retained Cp-bit scale. The conclusion also holds
for operator error `2^(-Cp+o(p))`, or a fixed polynomial multiplier on the
entrywise error. This is asymptotic; no practical cutoff is asserted for
the source's extremely small exponent slack.

### 4.1 Conditioning near the half-shift boundary

The following is the retained `GAUGEFREE-INTERIORS.md` section 3 estimate;
its argument is restated to expose the needed uniform hypotheses, not as
new work. For every finite shifted Gaussian Toeplitz section,

\[
 \|B\|\le3+\sqrt{2\pi/\gamma},\qquad
 \|B^{-1}\|\le\mu^{-1},\quad
 \mu=(1-e^{-\gamma(1-2|s|)})e^{-\pi^2/(3\gamma)}.\tag{13}
\]

For the first estimate, coefficients at 0 and +/-1 contribute at most
three; for |h|>=2, `h^2-2sh>=h^2/2`, and a Gaussian integral bounds the
tails. For the second, assume s>=0 by transposition. The symbol's Jacobi
product has factors `(1-q^(2j))(1+a_j exp(iw))(1+b_j exp(-iw))`, up to
complex conjugation, where `q=exp(-gamma)`, `a_j=q^(2j-1-2s)` and
`b_j=q^(2j-1+2s)`. For w in [0,pi], the increasing function
`f(x)=arg(1+x exp(iw))` and `a_(j+1)<=b_j<=a_j` bound the total argument
in magnitude by `f(a_1)`. Cancelling the a_1 factor's modulus, the real
part is at least

`(1-a_1) product_j(1-q^(2j)) product_(j>=2)(1-a_j) product_j(1-b_j)`.

This is at least `(1-a_1) exp(-pi^2/(3 gamma))`: use the product with
spacing two twice, that with spacing one once, and the elementary estimate
`-log product_(j>=1)(1-exp(-h gamma j)) <= pi^2/(6h gamma)`.
The latter follows by expanding the logarithm and using `exp(x)-1>=x`.
Fourier integration gives Hermitian part at least `mu I` for every finite
section, hence the inverse bound. The w=pi endpoint follows by continuity.
The primary product identity is
[NIST DLMF 20.5.9](https://dlmf.nist.gov/20.5.E9).

Under (8), `x0=c0 c1/(p^2 ln p)<=1`. Monotonicity and
`1-exp(-x0)>=x0/2` give

\[
 \mu\ge \frac{c_0c_1}{2p^2\ln p}\,p^{-\pi^2/(3c_0)}.
\]

Conditions (10) and `ln p<=p` imply `mu^-1<=p^M0`. They also give
`3+sqrt(2 pi ln p/c0)<=3+sqrt(2 pi p/c0)<=p`. This proves the one-factor
estimates in (11) without an exponential-in-n diagonal-similarity bound.

### 4.2 An entirely explicit precision example

Take `c0=C0=1`, `c1=1/8`, `xi=1`, `g<=sqrt(p)` and `p>=2^20`. Allow
all `gamma_i` in `[1/ln p,ln p]` and shifts satisfying (8). Use the larger
rational exponent `M0=8` (valid because `pi^2<12`), giving `L=42`.
Then `p>7+42 sqrt(p) log2(p)`, so C=1 satisfies (12). At p=`1048576`,
the right side is `860167`. The difference stays positive for larger p:
`sqrt(p)-42 log2(p)-7/sqrt(p)` is increasing in that range. Thus absolute
entry rounding error at most `2^-p` cannot reduce the ordinary generator
requirement below `2T/n_fast` for either target.

This is a narrower explicit regime of the normalized-core and precision
contracts, not a claim that the selected outer point uses beta=1/2 or
these constants. The general theorem covers any fixed constants and
beta<1 in (8), including the source's much closer-to-one beta.

### 4.3 Rounding the individual coefficient tables

The source rounds one-factor tables. To make that interface explicit, let
each `Bhat_i` have entrywise error at most `2^-Cp` from B_i, without
requiring that the rounding preserve Toeplitz structure. Set
`delta=p^xi 2^-Cp`; then `||Bhat_i-B_i||<=delta`.
If delta<=p, tensor telescoping gives

\[
 \|\bigotimes_i\widehat B_i-H\|
       \le g\delta(2p)^{g-1}.\tag{14}
\]

If additionally `delta p^M0<=1/2`, the Neumann inverse identity gives
`||Bhat_i^-1||<=2p^M0` and
`||Bhat_i^-1-B_i^-1||<=2p^(2M0)delta`. Telescoping the inverse factors gives

\[
 \|\bigotimes_i\widehat B_i^{-1}-H^{-1}\|
 \le g\,2^g p^{M_0(g+1)+\xi}2^{-Cp}.\tag{15}
\]

For p>=2, `log2 g<=g<=g log2 p` and `g+1<=2g`. Thus a single sufficient
condition for the admission inequalities and both protected rank margins is

\[
 Cp>7+(L+2+2M_0)g\log_2p.\tag{16}
\]

This again holds eventually throughout (8). In the explicit regime of
section 4.2 the coefficient is 60. For `p>=2^22`, `g<=sqrt(p)` and C=1,
(16) holds: at the endpoint its right side is `2703367`, below `4194304`,
and `sqrt(p)-60 log2(p)-7/sqrt(p)` is increasing thereafter.

These are statements about the linear matrices defined by rounded
coefficient tables and their exact inverses. Rounding data-dependent
arithmetic can produce a nonlinear algorithm; no circuit or algorithmic
lower bound is inferred from the matrix representation theorem.

## 5. Relationship to the retained source

The pinned `CAPPED-GAUGE-AUDIT.md` section 2 states actual `a=Theta(log p)`;
section 4 uses `g<=p^beta` with beta<1 and polynomial capped dimensions.
The pinned `GAUGEFREE-INTERIORS.md` gives narrow `gamma=a rho` and broad
`gamma=(pi^2/a) lambda`, where rho and lambda are bounded near one. Both
therefore satisfy (8) for fixed c0,C0. Its fine-prime note and
`FINE-PADDING-COMPOSITION.md` give
`1/(4p^2)<theta<=1/(2p^2-1)`. The narrow shift gap is at least
`theta/rho>=1/(8p^2)` and the broad gap at least theta. Thus c1=1/8 works
eventually. The retained dyadic interiors are longer than the growing
bandwidth; active dimensions are eventually at least four, satisfying n>=3.

This establishes precision compatibility for the normalized tensor core
and its inverse. It does not identify those matrices with a raw gauged
block, the full periodic Reference or a hole-completed physical operator.
A separately proved source-to-core operator error within the margin can
be used explicitly. Paid gauges, source access and movement still need
their own source-faithful analysis. No complete three-transform budget or
multiplication exponent changes.

## 6. Verification boundaries and next obligations

The verifier checks literal and block inverses, rational norm bounds,
positive-semidefinite singular-gap certificates, protected unstructured
perturbations, and both Schur factorizations with exact rational arithmetic.
Its failure controls include shifted n=2, insufficient precision, a forged
singular-gap certificate and the scope condition beta<1. Failure of the
last condition is not an impossibility theorem for beta>=1.

Open next questions are a quantitative margin for the paid diagonal gauges
of the actual source; arbitrary coordinate permutations; and multilevel
algorithms that avoid this ordinary representation with a full cost
account. The predecessor's small separable circuits remain valid despite
the robust ordinary-generator obstruction.

Prepared for @CubeJerry with substantial OpenAI ChatGPT assistance. The
boundary-minor predecessor, Vlado Vojdanovski's capped-phase-fusion work,
the fractional-shift source and Chafik Boukhalfa's fine-prime work retain
their credit. New files are Apache-2.0. No new kappa; all five selected
assumptions remain.
