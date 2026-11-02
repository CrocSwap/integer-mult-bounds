# Necessary degree growth for circle-gap cyclic inversion

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped mathematical proof with exact finite corroboration.
The construction gives real dyadic polynomials whose zeros all lie outside
the closed unit disk. Their circle gap is at least one half, while their
inverse Wiener norms and explicit finite cyclic inverse norms grow at least
as the square root of their degree.

## Statement

Define the classical Rudin-Shapiro polynomials by

\[
 R_0=T_0=1,\qquad
 R_{k+1}=R_k+z^{2^k}T_k,\qquad
 T_{k+1}=R_k-z^{2^k}T_k.
\]

For any integer \(s\ge0\), put

\[
 m=2^{2s+1},\quad D=2^{s+2},\quad d=2m-1,\quad
 q=2s+6,\quad L=2m(q+1),\qquad
 P_s(z)=1-\frac{z^mR_{2s+1}(z)}D.
\]

This polynomial has degree exactly \(d\), constant coefficient one, and
exactly \(m\) other nonzero coefficients, each equal to \(1/D\) or \(-1/D\).
For every \(|z|\le1\),

\[
 |P_s(z)|\ge\frac12.
\]

Let \(Z_L\) be the cyclic coordinate shift. Then

\[
 \left\|1/P_s\right\|_W\ge1+2^{s-1},\qquad
 \left\|P_s(Z_L)^{-1}\right\|_\infty>
 \frac34+2^{s-1}.                                      \tag{1}
\]

The first norm sums the absolute values of the Taylor coefficients. The
second is the induced maximum coordinate norm, equal to the maximum
absolute matrix row sum. With the fixed certified gap \(\delta=1/2\),

\[
 \delta\left\|P_s(Z_L)^{-1}\right\|_\infty>
 \frac38+\frac{\sqrt{d+1}}8.                           \tag{2}
\]

The finite witness length is explicit and is \(O(d\log(d+1))\). Thus a
bound \(\|P(Z)^{-1}\|_\infty\le C(d)/\delta\), valid for all such
polynomials and cyclic lengths, requires square-root growth of \(C(d)\)
on this degree subsequence. In particular, \(C\) cannot be constant.
This does not prove that square-root dependence is sufficient or optimal.

## Proof

The two coefficient blocks in the recurrence have disjoint supports.
Induction gives degree \(2^k-1\), coefficients in \(\{-1,1\}\), and,
on the unit circle, the identity

\[
 |R_k(z)|^2+|T_k(z)|^2=2^{k+1}.                        \tag{3}
\]

The induction step uses
\(|u+v|^2+|u-v|^2=2|u|^2+2|v|^2\).
Consequently \(|R_{2s+1}(z)|\le\sqrt{2m}=D/2\).
Set \(A(z)=z^mR_{2s+1}(z)/D\). The maximum modulus principle gives
\(|A(z)|\le1/2\) throughout the closed disk. Hence
\(|P_s(z)|=|1-A(z)|\ge1/2\) there. All zeros of \(P_s\) therefore
lie strictly outside the closed disk.

There is a radius greater than one on which \(1/P_s\) is analytic, so
its Taylor coefficients are absolutely summable. In the geometric identity
\(1/P_s=\sum_{j\ge0}A^j\), the constant coefficient is one and the
coefficients at degrees \(m,\ldots,2m-1\) are exactly the \(m\) signs
of \(R_{2s+1}\), divided by \(D\). Terms with \(j\ge2\) start at
degree \(2m\), so cannot change this block. This proves the first bound
in (1), since \(m/D=2^{s-1}\).

For the cyclic bound, set \(A=A(Z_L)\) and
\(G=\sum_{j=0}^{q}A^j\). The discrete Fourier basis unitarily
diagonalizes \(Z_L\). Equation (3) gives \(\|A\|_2\le1/2\), so
the Neumann series converges in operator norm and

\[
 \left\|(I-A)^{-1}-G\right\|_2
 \le\sum_{j=q+1}^{\infty}2^{-j}=2^{-q}.               \tag{4}
\]

Each matrix row has absolute sum at most \(\sqrt L\) times its Euclidean
norm, which is at most the matrix spectral norm. Therefore

\[
 \left\|(I-A)^{-1}-G\right\|_\infty\le\sqrt L\,2^{-q}. \tag{5}
\]

The polynomial defining \(G\) has degree at most \(qd<L\). Its
coefficient positions occupy distinct columns of each circulant row.
The constant coefficient and degree-\(m\) block consequently give
\(\|G\|_\infty\ge1+m/D\). Later Neumann terms need not preserve
coefficient signs. Their entire effect is charged in (5).

For the stated \(L\) and \(q\),

\[
 \sqrt L\,2^{-q}
 =\frac{\sqrt{2s+7}}{2^{s+5}}
 \le\frac{2s+7}{2^{s+5}}
 \le\frac7{32}<\frac14.                              \tag{6}
\]

The last nontrivial inequality follows by induction from
\(2s+7\le7\,2^s\). It holds at zero; the left side increases by two
at the next step while the right side doubles. The reverse triangle
inequality applied to (5) proves the second bound in (1).
Finally \(\sqrt{d+1}=2^{s+1}\), which proves (2).

These same finite matrices have \(\|P_s(Z_L)^{-1}\|_2\le2\).
The obstruction concerns maximum coordinate norms, not Euclidean inversion.

## Context and limits

Rafael Guevara's [PR803](https://github.com/CrocSwap/integer-mult-bounds/pull/803)
supplies the degree-controlled circle-gap inverse setting. Its stated upper
estimate for polynomials with no interior roots is \((1+4d)/\delta\).
Nick Petalas's older [PR5080](https://github.com/CrocSwap/integer-mult-bounds/pull/5080)
sharpens that upper constant to \((1+\pi d)/\delta\).
These are cited predecessor results, not replayed results. The lower
construction here leaves a gap between necessary square-root growth and
the cited sufficient linear growth on the exterior-root class.
The older [PR4914](https://github.com/CrocSwap/integer-mult-bounds/pull/4914)
settles a fixed mixed quadratic, a different parameter regime.

The Rudin-Shapiro recurrence, identity (3), and binary coefficient formula
are classical. An inspected primary exposition is Paul Balister,
[Bounds on Rudin-Shapiro polynomials of arbitrary degree](https://arxiv.org/html/1909.08777v1),
Section 1 and Proposition 4(a). It credits Golay, Shapiro and Rudin.
The recurrence and identity needed here are proved above. The new repository
step is the explicit dyadic inverse family and its finite cyclic transfer
with a bounded tail. No global literature-priority claim is made.
Ali Romman's PR621 retains credit for the cyclic-kernel motivation.

No specific PR621 kernel is asserted to equal this family. The result does
not obstruct stronger bounds for special kernels, address paid inversion,
or provide coefficient preparation, rounded execution, dirty restoration,
physical tape costs, a complete caller, supplier admission or a new kappa.
It discharges none of the selected frontier's five framework assumptions.
The universal statement rests on this written proof. Finite checks are
corroboration, not a formal proof or a complete multiplication theorem.
Independent human and formal proof-kernel review are unclaimed.
