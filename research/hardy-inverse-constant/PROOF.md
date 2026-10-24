# A sharper constant in the degree-controlled inverse envelope

The claim is a scoped analytic proof. Let P be a nonzero complex polynomial
of degree n and suppose |P(z)| >= delta > 0 on the unit circle. Let m be
the number of roots strictly inside the circle, including multiplicity.
With normalized circle measure and the two-sided Fourier coefficient norm W,

\[
 \|1/P\|_W\le\frac{(1+\pi m)(1+\pi n)}{\delta}
 \le\frac{(1+22m/7)(1+22n/7)}{\delta}.                 \tag{1}
\]

The second inequality is strict when n>0. For n=0 both expressions equal
1/delta. If U is an invertible bounded operator on a complex Banach space
with ||U^k|| <= 1 for every integer k, the same right side bounds
||P(U)^(-1)||. Thus the statement covers unit-phase cyclic shifts at
every length and integer stride, including zero and noncoprime strides.

Rafael Guevara's PR803 proves the same assertions with 4 in place of pi.
Its proof at `a0f15ce84f0951f69b39795f229cb854307ca52b`, retained unchanged
on the package base, supplies the Hardy factorization, normalized rational
arc-length inequality, root reflection and operator substitution used below.
Those are cited premises. This contribution sharpens the coefficient
estimate in that chain; it does not audit the predecessor or claim a new
Hardy inequality.

## 1. Evaluate the Schur integral instead of splitting it

For j,k >= 0 put K_jk=1/(j+k+1), w_j=(j+1/2)^(-1/2), and a=j+1/2.
The positive function f_a(x)=1/((a+x)sqrt(x)) is convex on x>0, since

\[
 f_a''(x)=\frac{3}{4x^{5/2}(a+x)}
       +\frac{1}{x^{3/2}(a+x)^2}
       +\frac{2}{x^{1/2}(a+x)^3}>0.
\]

The midpoint bound, including the integrable interval starting at zero,
gives the same Schur row estimate as PR803 Section 1. Evaluate its integral
using x=a t^2:

\[
 \sum_{k\ge0}K_{jk}w_k
 \le\int_0^\infty\frac{dx}{(a+x)\sqrt{x}}
 =\frac{2}{\sqrt a}\int_0^\infty\frac{dt}{1+t^2}
 =\pi w_j.                                           \tag{2}
\]

PR803 instead bounds the two parts at x=a separately, obtaining 4w_j.
The weighted Cauchy-Schwarz argument applied to finite nonnegative
sequences s,t therefore gives

\[
 \sum_{j,k}K_{jk}s_jt_k\le\pi\|s\|_2\|t\|_2.         \tag{3}
\]

For h analytic in a neighborhood of the closed disk, use the classical
Hardy factorization h=ab with ||a||_2 ||b||_2=||h||_1, as in PR803
Section 1. Coefficient convolution, (3), and increasing finite truncations
give

\[
 \sum_{l\ge0}\frac{|h_l|}{l+1}\le\pi\|h\|_1.        \tag{4}
\]

The predecessor's radial limit handles boundary zeros of h. The constant
change does not alter that limit or any analyticity hypothesis.

## 2. Carry the constant through the inherited analytic chain

For a rational R of degree at most d analytic near the closed disk, apply
(4) to h=R'. The normalized Dolzhenko-Spijker inequality, used in PR803
Sections 2 and 3, is ||R'||_1 <= d||R||_infinity. Consequently

\[
 \|R\|_W
 \le |R(0)|+\pi\|R'\|_1
 \le(1+\pi d)\|R\|_\infty.                          \tag{5}
\]

Use the exact factorization P=JQ from PR803 Section 4. Here J is the
finite Blaschke product of the m interior roots, has rational degree m
and unit circle magnitude one. The polynomial Q has degree at most n
and no roots in the closed disk, with |Q|=|P| on the circle. Hence J
and 1/Q are analytic near the closed disk. Applying (5) gives

\[
 \|J\|_W\le1+\pi m,\qquad
 \|1/Q\|_W\le(1+\pi n)/\delta.
\]

On the circle, 1/P=conjugate(J)/Q. Absolute coefficient convolution gives
the first bound in (1). PR803 Section 5's absolutely convergent
two-sided operator substitution then gives the asserted operator bound.
This uses the full integer-power hypothesis; spectral location alone is
not a replacement. No roots need to be computed to apply the bound with m=n.

## 3. A rational upper certificate and strict improvement

The elementary polynomial identity

\[
 x^4(1-x)^4=(1+x^2)(x^6-4x^5+5x^4-4x^2+4)-4
\]

integrates on [0,1] to

\[
 0<\int_0^1\frac{x^4(1-x)^4}{1+x^2}\,dx
   =\frac{22}{7}-\pi.                               \tag{6}
\]

The numerator is positive on (0,1), and the quotient polynomial has
integral 22/7. This proves the rational version of (1) without a decimal
approximation to pi. The integral certificate is classical; no historical
priority is asserted for it or for the Hardy constant pi.

The exact difference between the old and new rational multipliers is

\[
 (1+4m)(1+4n)-(1+22m/7)(1+22n/7)
  =\frac67(m+n)+\frac{300}{49}mn.                   \tag{7}
\]

It is positive for every n>0 and 0<=m<=n. At m=n the leading quadratic
coefficient decreases from 16 to 484/49, a ratio of 121/196. This is a
comparison of sufficient upper bounds. It is not a ratio of actual norms
or a lower bound on the improvement to a working implementation.

## 4. Scope of the exact checks

The verifier checks (6)'s polynomial identity and rational integral, (7)
on its declared finite calibration domain, exact binary ceiling brackets,
and new sufficient norm budgets for fourteen named prime-power radices.
The budget input from PR803 Section 5 is the cited circle certificate
delta^(-1)=2rn(2^r-1)^(n phi(r)-1), with n=r-1. We substitute the new
multiplier, not replay the source's circle theorem or numerical results.
Later #1025 improves that gap certificate in another regime; the theorem
here accepts any independently supplied positive delta, including that one.

Finite checks do not prove the infinite Schur bound, classical arc-length
premise, or analytic limits. Those are the written argument and explicit
dependencies above. No optimal degree dependence, paid inverse routine,
rounded precision recurrence, complete supplier or multiplication theorem
is established. Independent human and formal proof-kernel review are unclaimed.

This refinement was produced by Nick Petalas. Credit Rafael Guevara/PR803,
Ali Romman/PR621, and the classical Hardy, Hilbert, Blaschke,
Dolzhenko-Spijker and Baranov-Zarouf lineage retained in PR803. Apache-2.0.
