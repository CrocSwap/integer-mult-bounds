# External review of complete effective flow propagation

**Conditional confirmation; no analytic propagation gap found in the stated scope.** For alephnan PR6713 at `cd666f05c4e9006025b634687cc493911c8371c8`, this review checks PROOF sections2–8 and LOCAL_LIMIT sections8–9. It independently reconstructs the passage from the exact finite mirror/conservation identities, finite numerical premises and uniform interval estimate to the explicit all-rank majorant. The source already states and proves that theorem. This is external review, not a new exponent/onset or a claim that the author omitted a proof.

The source theorem is, with `s=99739/100000`,

```
n_LLT=2^(10^12), G0=2*n_LLT+2, N0=121*5^G0,
L(n)<=N0^(1-s)*n^s  for every integer n>=1.
```

The source scalar recurrence has `L(0)=0`, `L(n)=n` for `1<=n<121`, and for `N>=121` averages the complete source children `N-z` and exit children `e`, divided by the complete source count `C_N`. Default height/base, every multiplicity, unmatched boundary and terminal paid exit stay fixed. The threshold is symbolic, not materialized or a practical-cost bound.

## Premise ledger

The conclusion is conditional on the following exact interfaces; this written review does not recertify their finite executable realization.

1. The complete mirror decomposition and conservation identity in the pinned canonical predecessor, including the stated default-height cap tests, all target/paid word multiplicities, `C_N>0`, `N/121<z<=N` and `1<=e<=48N/121<N`. The literal decomposition in the successor agrees with predecessor sections2/4; this text comparison is not an operator census or `Flow.merged()` replay.
2. The declared positive paid/target laws, exact mean-log5 tilt and finite constants: `0<alpha<1`, `a=ln5<2`, `ln121<5`, `sigma^2>2`, `c_sigma<4`, `0<q<247/250`, `0<J<2000`, `tau=s-alpha>3/400`, `P(s)/121^s<2000`, and the complete limiting capacity margin `D_full>40000`. The current finite q/J/margin/census certificates are inherited, not rerun. PR6723/6728 provide separate nearby local-limit/tilt evidence; they do not automatically admit every finite premise or original paid census.
3. The uniform interval estimate(3), with `epsilon=10^-8`, for every paid length `ell>=n_LLT`, every location, length at most5000 and every open/closed endpoint convention. LOCAL_LIMIT's earlier Fourier estimate and classical Beurling–Selberg approximation remain their separately scoped premises. The symbolic onset and kernel deductions are audited below.

All target and paid letters used in conditioning are independent under their stated tilted laws. Positivity, completeness, independence and endpoint uniformity are substantive, not optional implementation details. No selected physical/native/ownership/compiler/precision/analytic-recovery assumption is discharged.

## Exact normalization and signed kernels

Put `A=P(alpha)`, `D=T(alpha)`, `J=A-D`, `q=D/A`, `B=ln(N/121)=G*a+delta`, `0<=delta<a`, and `ell=G-1-h`. For a mixed base of h target and ell paid letters, undoing its probability tilt contributes exactly

```
A^(G-1)*q^h*exp(-alpha*B)*exp(alpha*u_h),
u_h=B-sum X_i-sum Y_j.
```

The complete source-minus-exit capacity kernel f has positive components on `[ln r,ln k)` when `k>r` and negative boundary components on `[ln k,ln r)` when `r>k`. The cap test against `floor(N/121)` equals the comparison against `N/121` because the products are integers. Equal products add multiplicities; no endpoint atom or cross-layer multiplicity is removed.

For leaves the base prefactor is `A^G*exp(-alpha*B)` and every terminal paid r remains summed in `P(s)`. Consequently division by

```
F_G=A^G*exp(-alpha*B)/(J*c_sigma*sqrt(G))
```

gives exactly the mixed coefficient `J/A=1-q` and leaf coefficient `B_leaf=J*P(s)/121^s<4*10^6`. Thus, after discarding only nonnegative root-source capacity,

```
D_N/F_G >= sum_(h=0)^(G-1) (1-q)q^h F_h - B_leaf*L_G,
F_h=c_sigma*sqrt(G)*E f(u_h),
L_G=c_sigma*sqrt(G)*E[exp(-tau*u_leaf)1_(u_leaf>=0)].
```

This is source(1) with the complete signed bill. A changed terminal rule, omitted boundary or missing J would change that object. The limiting comparison is `M-B_leaf/tau=D_full`, where `M=integral f`; its identification with the full predecessor complement margin remains an explicit premise.

## Uniform kernels and effective onset

For `0<s<1`, `Q_s(x)=1-(1-x)^s` is convex, `Q_s(0)=0`, and `x Q_s'(x)>=Q_s(x)` on `(0,1)`. A source component therefore has derivative `exp(alpha*u)[alpha Q_s(x)-x Q_s'(x)]<=0` for `x=(rk/121)exp(-u)<=1`. At an included `x=1` endpoint its derivative may diverge but its value is continuous and has finite variation. Boundary components decrease because tau is positive.

Each finite window lies in `[0,5)`, has length below5 and left amplitude at most121. Their weighted amplitude sum is bounded by

```
Q=121*55998*7688=52092027504,
sup|f|<=Q, |M|<=5Q.
```

If a signed measure has interval discrepancy at most d on a window, Stieltjes integration of a decreasing continuous v bounds its integral error by `d*v(left)`. The terminal-constant whole-window term is included; the derivative-only argument would fail even for v=1. The half-open convention and interval estimate include endpoint atoms. One sums each positive/negative component's absolute error; the signed sum f and its zero extension need not be globally monotone.

LOCAL_LIMIT section8's substitution `w=ln n` bounds the interval/density error, for `b<=5000`, by

```
1/w + 2^23*exp(-w/2)
    +5001*w*exp(w/2)*exp[-exp(w/2)/320].
```

For `w>=60`, each remainder multiplied by w decreases and is below1/2 at60, using the positive exponential series and `e^30>2^40`. Hence the sum is at most `2/ln n` for `n>=2^100`. At `n>=2^(10^12)`, `c_sigma<5` and `ln2>2/3` give `c_sigma*2/ln n<15/10^12<10^-8`. This includes every location/endpoint convention; no convolution of that length is run.

Layer cake gives the shift-uniform Gaussian-comparison kernel estimate(13). Formula(14)'s subsequent flat-density error depends on the shift through its square and absolute value; it is not a uniform small bound at arbitrary shifts. The source correctly uses bounded shifts only for the first block, uniform interval masses in the middle, and a trivial end-layer bound.

## Every mixed layer and the missing limiting weight

Take `H=3000` and `G>=G0`. For `0<=h<=H`, `ell>=G/2>=n_LLT`. Conditional on the target sum, `u_h=v-Z_ell` with `-5h<=v<4`. Reflection of a mixed-window subinterval has length at most5 and left endpoint magnitude at most15010. With `rho=sqrt(G/ell)<=2`, the interval discrepancy from Lebesgue measure is at most

```
rho*epsilon+b*(rho-1)+rho*b*15010^2/(4*ell)
 <=2*epsilon+[30010+5*15010^2]/G <3*10^-8.
```

It holds for every target word and every actual delta, and survives conditioning/averaging. The Stieltjes bound yields `|F_h-M|<1563`. Nonnegative geometric weights sum to at most1, so the first block's total error is below1563, not3001 times that. Its main term is `(1-q^3001)M`, not M.

For `3000<h<=floor(G/2)`, `ell>=G/2-1>=n_LLT` and `sqrt(G/ell)<=2`. Uniform interval masses give `|F_h|<=12Q` without a bounded-shift premise. Actual middle layers and the entire missing infinite geometric mass of M cost together at most `17Q*q^3001<1/1000`.

For `h>floor(G/2)`, ell may be zero. No local-limit theorem is used there. The probability bound and `sup|f|<=Q` give

```
late <=4Q*sqrt(G)*q^(G/2)
     <=8Q/[(3/500)^2*G]<1  at G>=10^18.
```

This includes the last, zero-paid-letter layer. The missing geometric M mass is charged once, separately from the actual later layers. The complete mixed error is below `1563+1/1000+1`.

## Whole leaf half-line and a small hand exponential certificate

For leaves `u_leaf=delta-Z_G`. On `[0,5000)`, reflection gives intervals with left magnitude below5002. Their discrepancy is

```
epsilon+5000*5002^2/(4G)<5*10^-8.
```

The decreasing kernel has left value1, so its finite-window integral has that same error. For the remaining half-line, every interval `[5000+j,5001+j)` has scaled probability below2 by the location-uniform estimate. Positive summation bounds the complete probability tail by `2*exp(-5000*tau)/(1-exp(-tau))<3*10^-14`. Separately, the Lebesgue tail is `exp(-5000*tau)/tau<2*10^-14`. Endpoint atoms are assigned exactly once. Multiplication by `B_leaf<4*10^6` gives total leaf error below `1/5+2*10^-7`.

These tail constants admit a short independent hand certificate:

```
exp(3)>sum_(j=0)^8 3^j/j!=89641/4480>20,
exp(3/2)>1+3/2=5/2,
exp(36)>20^12=4096*10^12>10^15,
exp(37.5)>20^12*(5/2)=10240*10^12>10^16.
```

Thus no expansion of the source's larger37th-power comparison is needed here. These are written rational/exponential arguments, not executed numerical tests. The positive all-rank-one paid word can lie beyond the5000 cutoff at large G, so the tail cannot be set to zero. Nor can a second terminal-rank cap be inserted: terminal r was already completely summed in `P(s)`.

## All ranks, offset uniformity and induction

The total loss is strictly below

```
1563+1/1000+1+1/5+2*10^-7=1564.2010002<1600.
```

Therefore `D_N/F_G>D_full-1600>38400>0`, giving `H_N(s)=1-D_N/C_N<1`. Every bound used the actual offset `0<=delta<ln5` or a location-free estimate. Every integer `N>=121*5^G0` has `floor(log_5(N/121))>=G0`; this is not only a favorable subsequence of powers of5.

The inherited complete first-moment identity is `sum c_z*z-sum d_e*e=608*U_N(1)>0`. Its literal paid and target first moments are131115 and131723. Applying the recurrence to n yields exactly `N-608*U_N(1)/C_N<N`. Nonnegative coefficients and smaller children prove `L(n)<=n` by strong induction, with `L(0)=0` handling a possible z=N source.

For `1<=n<N0`, `n<=N0^(1-s)n^s`. For `n>=N0`, the claimed power bound at all smaller positive children, the zero child and `H_n(s)<1` prove the same inequality. No initial-range enumeration up to N0 is required. This is the source's sufficient symbolic majorant, not a first successful rank, improved exponent or practical runtime.

## Scope controls and obligations

The separate review notes give hand controls for omitted J/geometric mass, out-of-domain x, wrong s/tau, missing endpoint atoms, lost Stieltjes terminal term, nonuniform shifts, zero-paid LLT use, truncated leaves and missing conservation. They are written counterexamples to weakened arguments, not executed counterexamples to the stated source theorem.

Actual executable finite decomposition/ranks/census, complete margin certificates and any physical caller rebinding remain unreviewed here. The classical approximation and the selected five assumptions stay explicit. No native supplier, erasure/ownership, compiler/precision/stock/tape/outer or full physical invoice is admitted. No kappa/frontier/merge/adoption change follows.

Credit alephnan6713 for the effective theorem; CubeJerry6329; zxv4436/4483; Ryanson Jonathan/pinterbanget4459/4467 and mirror-flow lineage; DLamdata6118; Nick Petalas6125/6128; Cinna Davis/1337isnot1337; Jacob Alan Sussman and retained contributors; PR6723/6728's separately scoped external premises. Beurling/Selberg/Vaaler/Shou retain classical analytic attribution; variance, Stieltjes, geometric tails and induction are classical. ToikY with substantial OpenAI Codex and separate source-aware AI derivation/review roles, Apache-2.0. No independent human or proof-kernel acceptance.
