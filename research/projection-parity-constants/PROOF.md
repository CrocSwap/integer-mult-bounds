# Exact parity constants for the projection recurrence

Status: a proposed scoped mathematical solution with exact finite corroboration.
Prepared with OpenAI Codex assistance for this task, 2026-10-24 (Asia/Shanghai).
New text and code: Apache-2.0. No claim of prior literature priority.

## 1. Question, sources, and result

The source is CrocSwap/integer-mult-bounds at
`ff3cc58e370d0f678e529246f8c73e8094e18fcf`.
Krzysztof Wojt's PR #5193, `research/projection-geometric-tail`, proves
the order of convergence and explicitly leaves exact leading parity constants
and elementary/q-series expressions for the modes open. This note solves
those two scoped questions. It does not classify monotone seeds.

At block four start with

\[
a_4=(0,27456,48576,68320,86592).
\]

For k >= 5, use the unstrengthened recurrence

\[
a_k(r)=\sum_s N_k(r,s)a_{k-1}(s),
\]

where the only possibly nonzero entries are

\[
\begin{aligned}
N_k(r,r)&=2^{k-r}-1+4^k-2^{k+r},\\
N_k(r,r-1)&=2(2^k-2^{k-r})+(2^r-1)2^{k-1},\\
N_k(r,r-2)&=(2^r-1)(2^{r-1}-1)2^{k-r}.
\end{aligned}
\]

The last entry is zero when r < 2; omit indices outside the old profile.
Set T_m=a_m(m)/a_m(1). Let

\[
\mathcal K=\prod_{i=1}^{\infty}
\left(\frac{1-2^{-i}}{1+2^{-i}}\right)^2>0.
\]

**Theorem.** As integer m tends to infinity,

\[
\boxed{
T_m=\frac{439277}{149175}
+2^{-m}\left(\frac{815083}{596700}
+(-1)^m\frac{323}{28}\mathcal K\right)
+O(4^{-m}).
}
\tag{1}
\]

Consequently the exact even and odd scaled limits are respectively

\[
\frac{815083}{596700}+\frac{323}{28}\mathcal K
=1.535225897075989\ldots,
\]
\[
\frac{815083}{596700}-\frac{323}{28}\mathcal K
=1.196743266657880\ldots.
\]

The full scaled sequence has no limit, since K > 0. The known limit
439277/149175 is recovered, not claimed as new. Exact coefficient extraction
from (7) below also gives a nonrecursive q-series expression for every mode
and hence for every finite T_m.

## 2. The credited four-mode reduction

Here is a self-contained verification of the reduction from #5193, which is
credited to that work. Define

\[
\begin{aligned}
h_r&=3/2+2^{-r}-2^r,\\
B_r&=2^{r-1}+3/2-2^{1-r},\\
C_r&=2^{r-1}-3/2+2^{-r}.
\end{aligned}
\]

Let e_j(r)=0 for r<j, e_j(j)=1, and for r>j put

\[
(h_j-h_r)e_j(r)=B_re_j(r-1)+C_re_j(r-2).
\tag{2}
\]

Because h_r strictly decreases, this determines e_j. With

\[
d_k=(2^{k-1}-1)(2^{k+1}+1),
\]

the raw row operator is d_k I + 2^k H, where H is the lower-banded operator
with coefficients h_r,B_r,C_r. Thus H e_j=h_j e_j. At the new endpoint
r=k the raw diagonal coefficient is zero, so no undefined old value is needed.
Solving the unit triangular seed system gives

\[
(c_1,c_2,c_3,c_4)=
\left(1,\frac{17}{39},\frac{6181}{14586},\frac{99085}{239811}\right).
\]

Define

\[
p_{m,j}=\prod_{k=5}^{m}
\frac{(2^{k-j}-1)(2^{k+j}+1)}{d_k}.
\]

The seed equations and induction with H give, for 0 <= r <= m,

\[
\frac{a_m(r)}{a_m(1)}=\sum_{j=1}^4 c_jp_{m,j}e_j(r).
\tag{3}
\]

## 3. A new q-series expression for each eigenmode

Fix j >= 1, and write Q=1/2 and s=2^j. Use the convention

\[
(z;Q)_n=\prod_{i=0}^{n-1}(1-zQ^i),\qquad (z;Q)_0=1.
\]

For n >= 0 define v_n by

\[
e_j(j+n)=\frac{(Q^{n+1};Q)_j}{(Q;Q)_j}v_n.
\tag{4}
\]

Thus v_0=1. To check the substitution, put y=2^r. Equation (2) becomes

\[
2(y-s)(sy+1)e_j(r)
=s(y-1)(y+4)e_j(r-1)+s(y-1)(y-2)e_j(r-2).
\]

The ratio of the prefactors in (4) at consecutive r is
(y-1)/(y-s). Cancellation therefore gives, for n >= 1,

\[
2(1+s^{-2}Q^n)v_n
=(1+4s^{-1}Q^n)v_{n-1}+(1-2Q^n)v_{n-2}.
\tag{5}
\]

At n=1 the last coefficient is zero, and we set v_{-1}=0.

Let V_j(z)=sum_{n>=0} v_n z^n near zero. Multiplying (5) by z^n
and summing gives

\[
(1-z)(2+z)V_j(z)+\frac{(z-2/s)^2}{2}V_j(z/2)
=2(1+s^{-2}).
\tag{6}
\]

Iterating this functional equation yields the explicit expression

\[
\boxed{
V_j(z)=(1+s^{-2})\sum_{\ell=0}^{\infty}
\frac{(-s^{-2})^\ell(sz/2;Q)_\ell^2}
{(z;Q)_{\ell+1}(-z/2;Q)_{\ell+1}}.
}
\tag{7}
\]

At z=0 the geometric series gives V_j(0)=1. Near zero the series is
absolutely convergent and satisfies (6); comparing coefficients uniquely
recovers (5). This also establishes that it is the generating function.

More generally, (7) converges locally uniformly away from
z=1,2,4,... and z=-2,-4,-8,... . On any such compact set its finite products
are uniformly bounded and its denominator products are bounded away from zero,
while s^{-2ell} decays geometrically. Removing the one vanishing factor at
any listed point makes the series locally uniformly convergent there too.
Hence V_j is meromorphic with at most simple poles at these points.

## 4. Three explicit poles determine the leading terms

Define the pole coefficients

\[
A_j=\lim_{z\to1}(1-z)V_j(z),\quad
D_j=\lim_{z\to2}(1-z/2)V_j(z),\quad
E_j^-=\lim_{z\to-2}(1+z/2)V_j(z).
\]

We use the classical q-Gauss identity (NIST DLMF 17.6.1):

\[
{}_2\phi_1(a,b;c;Q,c/(ab))
=\frac{(c/a;Q)_\infty(c/b;Q)_\infty}
{(c;Q)_\infty(c/(ab);Q)_\infty},\qquad |c/(ab)|<1.
\tag{8}
\]

Here the basic hypergeometric series includes the denominator (Q;Q)_ell.
All denominator parameters below avoid its forbidden nonnegative powers
Q^{-n}, and both arguments have absolute value s^{-2}<1.

At z=1 equation (7) gives

\[
A_j=\frac{1+s^{-2}}{1+Q}
{}_2\phi_1(s/2,s/2;-Q^2;Q,-s^{-2})
=\frac{(-Q;Q)_{2j}}{(-Q;Q)_j^2}.
\tag{9}
\]

All terms with ell >= j vanish because s/2=Q^{1-j}; the last potentially
nonzero term is ell=j-1.
For example A_1=5/6. The final equality follows by (8) and cancellation
of the shifted infinite products; it can also use terminating q-Chu-Vandermonde.

Taking the pole at z=2 in (6), where V_j(z/2) contributes A_j, gives

\[
D_j=\frac{(1-s^{-1})^2}{2}A_j.
\tag{10}
\]

At z=-2 equation (7) instead gives

\[
\begin{aligned}
E_j^-&=\frac{1+s^{-2}}3
{}_2\phi_1(-s,-s;-1;Q,-s^{-2})\\
&=\frac{1+s^{-2}}3
\frac{(Q^j;Q)_\infty^2}{(-1;Q)_\infty(-Q^{2j};Q)_\infty}\\
&=\frac{(-Q;Q)_{2j}}{6(Q;Q)_{j-1}^2}\mathcal K.
\end{aligned}
\tag{11}
\]

The last equality uses (-1;Q)_infty=2(-Q;Q)_infty and
K=(Q;Q)_infty^2/(-Q;Q)_infty^2.

The meromorphic description proves the coefficient asymptotic

\[
v_n=A_j+D_j2^{-n}+E_j^-(-2)^{-n}+O(4^{-n}).
\tag{12}
\]

For completeness this is not an unproved transfer heuristic: subtract the
simple-pole parts at 1, +/-2, and +/-4. The remainder is analytic on |z|<8,
so Cauchy's coefficient estimate on |z|=5 is O(5^{-n}). The two subtracted
parts at +/-4 have coefficients O(4^{-n}). Their constants need not be
computed to obtain (12). All statements here are for fixed j.

## 5. Returning to the physical block index

Define the rational constants

\[
F_j=\frac{(-Q;Q)_{2j}}{(Q;Q)_j(-Q;Q)_j^2},\qquad
G_j=\frac{(-Q;Q)_{2j}}{6(Q;Q)_{j-1}^2(Q;Q)_j}.
\]

Since n=m-j, (4) and (12), including the first-order change in the
finite product in (4), yield

\[
e_j(m)=F_j\left(1-\frac{s-s^{-1}}2\,2^{-m}\right)
+(-1)^m(-1)^j sG_j\mathcal K\,2^{-m}+O(4^{-m}).
\tag{13}
\]

For 1 <= j <= 4 the mode product has the rational limit

\[
P_j=\frac{\prod_{i=5-j}^{3}(1-Q^i)}
{\prod_{i=6}^{4+j}(1+Q^i)},
\tag{14}
\]

with empty products equal to 1. In fact its exact finite formula is

\[
p_{m,j}=P_j
\frac{\prod_{i=m+2}^{m+j}(1+Q^i)}
{\prod_{i=m-j+1}^{m-1}(1-Q^i)}.
\tag{15}
\]

Thus, by expansion of these finitely many factors,

\[
p_{m,j}=P_j(1-h_j2^{-m}+O(4^{-m})).
\tag{16}
\]

Multiplication with (13) gives

\[
p_{m,j}e_j(m)=P_jF_j
+2^{-m}\left[P_jF_j\frac{s-s^{-1}-3}{2}
+(-1)^mP_j(-1)^j sG_j\mathcal K\right]+O(4^{-m}).
\tag{17}
\]

The three exact sums from (3) are

\[
\sum_j c_jP_jF_j=\frac{439277}{149175},
\]
\[
\sum_j c_jP_jF_j\frac{2^j-2^{-j}-3}{2}
=\frac{815083}{596700},
\]
\[
\sum_j c_jP_j(-1)^j2^jG_j=\frac{323}{28}.
\]

They prove (1). The accompanying exact checker reconstructs these sums.

## 6. Exact numerical enclosures and verification boundaries

Let K_N be the product defining K truncated after N. For 0 <= x < 1,

\[
1-\left(\frac{1-x}{1+x}\right)^2=\frac{4x}{(1+x)^2}\le4x.
\]

Applying product(1-d_i) >= 1-sum d_i to finite tails and then taking
limits proves, for N >= 3,

\[
K_N(1-2^{2-N})\le\mathcal K\le K_N.
\tag{18}
\]

This both proves positivity and provides rational certified enclosures for
the two constants. The verifier uses N=80, an original integer recurrence,
a separately implemented mode recurrence, the rational identities above,
and rejection controls. Those bounded checks corroborate, rather than replace,
the universal analytic proof and the classical q-Gauss identity.

## 7. Credit, scope, and remaining questions

- Jacob Alan Sussman #4628: recurrence, seed, and proposed engine interpretation.
- Maximilian Lutz #4643: independent projection counts and recurrence audit.
- Nick Petalas #5151: exact rational limiting value and general seed theorem.
- JoyboyBrian #5184: strict finite-block descent and unattained infimum.
- Krzysztof Wojt #5193: fixed triangular operator, four-mode representation,
  and sharp geometric order; these are explicit inputs and credited here.
- Eumemic #288, Swapnil Jain, and the retained certificate/engine lineage
  retain their original credit. Q-Gauss summation is classical, not new here.

Sources:

- https://github.com/CrocSwap/integer-mult-bounds/pull/5193
- https://github.com/CrocSwap/integer-mult-bounds/tree/ff3cc58e370d0f678e529246f8c73e8094e18fcf/research/projection-geometric-tail
- https://github.com/CrocSwap/integer-mult-bounds/pull/5151
- https://dlmf.nist.gov/17.6.E1
- https://dlmf.nist.gov/17.6.E2

This is an arithmetic theorem about the specified recurrence. The inherited
hook-rank certificates, engine interpretation, physical caller, dirty-state
restoration, complete costs, and multiplication theorem are not established
by it. No new kappa or selected-frontier change is claimed. No human review
or proof-kernel verification is claimed. Public novelty is limited to the
reviewed source snapshot and targeted live overlap search; unpublished work
and every historical discussion reply were not exhaustively inspected.

Open next questions: characterize monotone seed profiles; determine whether
the q-series expression can be reduced further for finite m; resolve the
independent inherited hook-rank obligations. These are separate tasks.
