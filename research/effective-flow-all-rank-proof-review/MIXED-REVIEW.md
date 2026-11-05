# Independent written audit of mixed-layer propagation, sections2–5

**Conditional PASS; no blocking implication error found in this scope.** I
independently derived the tilt normalization, kernel discrepancy bound and
first3001-layer estimate from the stated premises. For this review I read inert PROOF,
LOCAL_LIMIT/README and provenance text; I did not read scientific Python or the
source author's REVIEW, run/import/compile a program, perform a new numerical
experiment, or use a proof kernel. This is source-aware AI mathematical review.
Later mixed/leaf tails and the final onset/induction are separately assigned;
their correctness is not implied merely by this PASS.

The reviewed source is alephnan/PR6713 head
`cd666f05c4e9006025b634687cc493911c8371c8`, session10/INPUTS/PROOF.md,
16,628 bytes, declared SHA256
`e7dbe4e1705a307e9eb32f6f06b340fb2c49948cc749110d6be2c6fb3da94ea9`.
That is retained acquisition provenance, not a new remote authentication.
The exact finite mirror decomposition, source/exit ranks and multiplicities,
default height and scalar recurrence remain source-bound inherited premises.
No original Flow execution or all-size source-code audit is claimed here.

## 1. Exact normalization, without a limiting ratio

Fix the source's literal P,T, m=121, s=99739/100000 and exact tilt alpha.
Write A=P(alpha), D=T(alpha), J=A-D and q=D/A. The declared numerical
premises give A>0,J>0,0<q<1,0<alpha<s<1 and tau=s-alpha>0. These sign
premises are substantive and are not independently numerically recomputed here.
For a parent N define B=log(N/121)=G*a+delta with a=log5 and0<=delta<a.
All products being integers, z<=floor(N/121) is exactly equivalent to
z<=N/121=exp(B). There is no approximate floor or favorable-offset assumption.

For a fixed mixed layer h, ell=G-1-h. If an ordered base word has product z
and multiplicity w, its probability under ell independent paid letters and h
independent target letters is

    Pr(base)=w*z^alpha/(A^ell*D^h)
            =w*z^alpha/(A^(G-1)*q^h).

Thus w=A^(G-1)*q^h*exp(-alpha*B)*exp(alpha*u)*Pr(base), u=B-log z.
This is a per-chronological-layer identity. No binomial choice of layer
positions belongs in it: the inherited decomposition already specifies the
paid/target base at each h, and each h is summed once.

The rank rkz has normalized parent fraction
x=rkz/N=(rk/121)*exp(-u). Source inclusion rz<=exp(B)<kz is exactly
u in[log r,log k), possible only for k>r. Its capacity contribution is
1-(1-x)^s. Boundary inclusion kz<=exp(B)<rz is exactly
u in[log k,log r), possible only for r>k, with exit cost x^s. Combining
these facts with the preceding weight identity gives precisely

    mixed = A^(G-1)*exp(-alpha*B)
            *sum_(h=0)^(G-1)q^h E[f(u_h)],

where f is the signed kernel defined by the source, including every P_r*T_k.
For a paid leaf base, its multiplicity is A^G*z^(-alpha)*Pr(base). The
base cap is u_leaf>=0, including equality. Summing every terminal paid rank r
therefore gives the entire leaf cost

    A^G*exp(-alpha*B)*[P(s)/121^s]*E[g(u_leaf)],
    g(u)=exp(-tau*u)*1_(u>=0).

There is no second cap on terminal r and no omitted boundary term in these
formulas. Root ranks kz fit in N because z<=N/121 and k<=121. Their
capacities are nonnegative, so dropping only those root capacities is a
valid lower bound on D_N.

Now divide by the positive factor

    F_G=A^G*exp(-alpha*B)/(J*c_sigma*sqrt(G)),   G>0.

The mixed multiplier is J/A=1-q, and the leaf multiplier is
B_leaf=J*P(s)/121^s. This independently yields source equation(1), with
no missing reciprocal1-q and no division of two approximate limiting values.
G=0 is excluded from this normalization; the later initial-range argument
must cover such parents instead of applying the large-G estimate there.

For completeness, the scalar power comparison is algebraic:
D_N=C_N-[sum c_z(1-z/N)^s+sum d_e(e/N)^s], hence
H_N=1-D_N/C_N when C_N>0. The exact finite recurrence and smaller-child
premises, rather than any physical operation bill, make that the relevant
scalar induction test.

## 2. Domains, monotonicity and weighted total variation

In a positive window, u>=log r gives x<=k/121<=1. Thus Q_s(x)=1-(1-x)^s
is real and nonnegative even at the endpoint x=1. For0<s<1,
Q_s''(x)=s(1-s)(1-x)^(s-2)>0 inside[0,1), so convexity with Q_s(0)=0
implies x*Q_s'(x)>=Q_s(x). Differentiating the positive kernel in the
interior gives

    exp(alpha*u)[alpha*Q_s(x)-x*Q_s'(x)]
       <=(alpha-1)exp(alpha*u)Q_s(x)<=0.

At x=1 the derivative may be unbounded, but the value is finite and the
one-sided monotonic/continuous extension exists. A negative-sign boundary
kernel before its sign is applied is (rk/121)^s*exp(-tau*u), also positive
and decreasing because tau>0. These claims concern each kernel on its own
closed limiting window; its zero extension may jump at either window edge.

All windows lie in[0,log121), or end there by their limiting endpoint, and
have length<5 by the declared log121<5. At a positive window's left endpoint,
its value is r^alpha*Q_s(k/121)<=r^alpha<=r<=48<121. At a boundary
window's left endpoint it is (r/121)^s*k^alpha<=k^alpha<=k<=121.
So121 is a common loose amplitude bound. It uses positive alpha<1, positive
s and the literal rank caps; it is not a cancellation estimate.

Let nu be the difference between a scaled probability measure and Lebesgue
measure on W=[l,r). Suppose |nu(I)|<=d for every relevant subinterval,
including its actual endpoint convention. For any continuous nonincreasing
v>=0 on[l,r], let eta=-dv be its finite positive Stieltjes measure. For x<r,
v(x)=v(r)+eta((x,r]). Integrating this identity over W gives

    integral_W v dnu
      =v(r)*nu([l,r))+integral_(l,r]nu([l,t))deta(t).

All measures are finite on this compact window, so the signed-measure/Fubini
step is justified. Continuity of v removes any ambiguity from eta's point
masses; the actual half-open intervals still bind atoms of nu correctly.
Taking absolute values gives d*[v(r)+eta((l,r])]=d*v(l).
The unbounded derivative at x=1 causes no failure: monotonicity and bounded
endpoint values supply finite Stieltjes variation. A derivative bound, mesh
or density assumption for the probability distribution is unnecessary.

Apply this to each unsigned component of f and then take the triangle
inequality over signed components. Its weighted amplitude sum is at most

    Q=121*(sum P_r)*(sum T_k)
     =121*55998*7688=52092027504.

Including nonexistent/equal-rank pairs only enlarges this bound. Therefore
|integral f dnu|<=Q*d, sup|f|<=Q and |M|<=5Q. No cancellation between
windows or positive/negative terms is presumed. The same estimate survives
averaging any uniform-in-conditioning bound.

## 3. First3001 layers and every parent offset

Assume the source's uniform interval estimate(3), with epsilon=10^-8,
for all ell>=n_LLT, all locations, lengths up to5000 and every endpoint
convention. This analytic premise is inherited here, not re-proved by finite
checks. Let G>=G0=2*n_LLT+2 and H=3000. The declared enormous n_LLT ensures
for0<=h<=H that ell=G-1-h>=G/2 and ell>=n_LLT. Also G>=10^18.

Condition on the h target letters. Independence leaves the paid centered sum
Z_ell with exactly the law required by(3), while

    u_h=v-Z_ell,
    v=(h+1)*a+delta-sum_(j=1)^h Y_j.

The literal target support gives a<=Y_j<5. Together with0<=delta<a<2,
this gives -5h<=v<4. Reflecting a subinterval of a mixed window, whose
coordinates lie in[0,5), gives a Z_ell interval of length b<=5 with left
endpoint x satisfying |x|<=15010. Reflection swaps which endpoints are
included; estimate(3) permits all such conventions, including cap atoms.
These bounds are uniform over every possible target word and every actual
delta in[0,a), not merely over integer powers of5 or average offsets.

Put rho=sqrt(G/ell)<=2 and w=x^2/(2*sigma^2*ell). Multiplying(3) by rho
and comparing its Gaussian reference with interval length b gives

    |c_sigma*sqrt(G)*Pr(I)-b|
       <=rho*epsilon+b*(rho-1)+rho*b*(1-exp(-w))
       <=rho*epsilon+b*(rho-1)+rho*b*R^2/(4*ell),
       R=15010,

using sigma^2>2 and1-exp(-w)<=w. Also
rho-1=(G-ell)/(sqrt(G*ell)+ell)<=(G-ell)/ell<=6002/G.
The three terms are consequently bounded by

    2*epsilon+[30010+5*15010^2]/G
       <2*epsilon+2*10^9/G<3*10^-8.

The source's constants are therefore valid, with substantial slack. Because
this interval discrepancy holds under every conditioning, averaging over the
target sum preserves it. Section2's Stieltjes argument then gives, separately
for each h in0..3000,

    |c_sigma*sqrt(G)*E[f(u_h)]-M|<3*10^-8*Q<1563.

The geometric coefficients are nonnegative and
(1-q)*sum_(h=0)^3000 q^h=1-q^3001<=1. Their combined approximation error
is thus<1563, with no factor3001. The central block's main term is
(1-q^3001)*M, not M itself. The omitted M*q^3001 and all later actual
layers must still be charged by section6; that interface obligation is explicit
and cannot be discarded even when M is positive. This review does not replace
the separately assigned later-layer/leaf proof.

## 4. Adversarial hypothesis controls, not executed experiments

- Omitting J from F_G changes the mixed factor to1/A, generally not1-q.
  For A=3,D=1 these are1/3 and2/3. The normalization equality is substantive.
- Allowing a target rank k>121 can make x>1 at u=log r; for k=242,r=1,
  x=2. The fractional capacity kernel then ceases to be real. The literal
  maximum target/parent normalization is needed.
- The convexity step is not valid for arbitrary s. For s=2,alpha=1/2,x=9/10,
  alpha*Q_s(x)-x*Q_s'(x)>0, so the proposed decreasing-source argument fails.
  Tau<0 likewise makes a boundary component grow rather than decrease.
- If endpoint control is supplied only on open initial pieces inside W,
  nu=delta_l has zero mass on all(l,t), but integral_[l,r)v dnu=v(l).
  Thus a cap atom cannot be ignored. The full interval/endpoint premise and
  Stieltjes half-open convention are required.
- q>=1 removes both the probability-like geometric weighting and J>0.
  Even with0<q<1, replacing the first block's weight by1 silently omits
  q^3001*M. The first-block conclusion must stay as written above.
- Conditioning without independence can change the paid-sum law, invalidating
  an unconditional LLT application. The stated independent letters are used.
- A nonuniform-in-location LLT or an estimate only at delta=0 does not justify
  this argument for every parent. Letting h grow with G also makes the
  R^2/G flattening error uncontrolled; late layers require a different bound.
- A numerical D_full margin, or a bounded number of source histograms, cannot
  on its own prove the exact finite decomposition or all-G propagation.
  Missing boundary exits or an extra terminal cap would change this very
  normalization and the object whose margin is being estimated.

## 5. Premises retained and scope of this verdict

The exact Flow/decomposition/recurrence identities and original chronology,
source and exit multiplicities/rank bounds are inherited source premises.
The exact tilt/root and literal positive law, all interval hypotheses(3), and
numerical inequalities for alpha,sigma,q,J,tau,P(s),D_full remain their
separately certified premises; this review did not numerically rerun them.
In particular D_full>40000 and its identity with the predecessor's complete
limiting capacity margin are not independently recomputed here. The first-
layer transfer needs only its stated constants and the supplied uniform LLT;
all physical/operator/native/compiler/tape/precision and selected analytic
recovery claims remain outside it. Full later-layer, leaf, onset and strong-
induction closure need their separately assigned reviews. No new exponent,
paid supplier, all-five admission, merge or frontier change follows.

Credit alephnan/PR6713 for this effective successor proof; zxv and
Ryanson Jonathan/pinterbanget for the exact flow/mirror lineage; DLamdata,
Nick Petalas, the CubeJerry/PR6329 full-flow exponent contribution,
Cinna Davis/1337isnot1337, Jacob Alan Sussman and the retained predecessor
lineage. S5/PR6723 and S9's tilt audit supply separately scoped external
premise work. Beurling, Selberg, Vaaler and Laura Shou retain the classical
interval-approximation attribution. This independent derivation/source-aware
review used substantial OpenAI Codex assistance; no human or proof-kernel
acceptance is claimed. Apache-2.0.
