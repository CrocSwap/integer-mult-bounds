# A smaller Fourier-to-operator bound for the prime-power kernels

## Statement and inherited premises

This note audits the quantitative Fourier step in Ali Romman's incorporated
PR #621. The old estimate is valid. A standard weighted Cauchy-Schwarz
argument makes it substantially smaller without changing the polynomial,
the nonvanishing theorem, or the circle lower bound. No literature-priority
claim, paid algorithm, or new multiplication exponent is made.

Retain the notation and proved circle bound of the pinned predecessor:

\[
r=\ell^a\ge3,\quad n=r-1,\quad D=\varphi(r),\quad H=2^r-1,
\qquad \delta=(2rnH^{nD-1})^{-1}.
\]

Here \(\ell\) is prime, the kernel uses any primitive \(r\)-th root, and
\(P(z)=\sum_{j=0}^{r-1}z^j/\prod_{s=1}^j(1-u^s)\).
The predecessor establishes \(|P(z)|\ge\delta\) on \(|z|=1\) and
\(|P'(z)|\le M=nH/r\) there. These are inherited inputs, not conclusions
of the finite checks in this package. Put

\[
A=\delta^{-1},\qquad X=nH^{nD/2}.
\]

For every cyclic length \(L\ge1\), integer stride \(w\), and scalar
\(|\tau|=1\), the following exact integer is an upper bound:

\[
\boxed{\ \|P(\tau Z_L^w)^{-1}\|_\infty
       \le C_{\rm new}=A(1+4X).\ }
\]

The old bound is exactly \(C_{\rm old}=A(1+4X^2)\). Thus this is a strict
improvement for every admitted \(r\ge3\). Both bounds remain uniform in
length, stride, and scalar phase. This is an analytic norm estimate, not
a count of arithmetic operations or a guarantee of rounded execution.

## Weighted Fourier lemma

Use normalized Lebesgue measure on \([0,2\pi]\). Let \(g\) be continuously
differentiable and periodic, with Fourier coefficients \(c_k\). Suppose
\(\|g\|_2\le A\) and \(\|g'\|_2\le B\), where \(A>0\), \(B>0\).
For every real \(t>0\),

\[
\sum_{k\in\mathbb Z}|c_k|
 \le\sqrt{(1+4t)(A^2+B^2/t^2)}.
\tag{1}
\]

To prove this without assuming absolute convergence in advance, first
apply Cauchy-Schwarz to the finite sum over \(-N\le k\le N\), with
weights \(1+k^2/t^2\). Parseval for \(g\) and \(g'\) bounds its first
factor squared by \(A^2+B^2/t^2\). For the second factor, the function
\(f(x)=(1+x^2/t^2)^{-1}\) decreases on the nonnegative half-line, so

\[
\sum_{k\in\mathbb Z}(1+k^2/t^2)^{-1}
\le1+2\int_0^\infty f(x)\,dx\le1+4t.
\]

The last inequality follows by bounding the integral on \([0,t]\) by
\(t\), and on \([t,\infty)\) by
\(t^2\int_t^\infty x^{-2}\,dx=t\). Both signs of the frequency are
charged. Letting \(N\) increase proves (1), including absolute convergence.
This is a standard Fourier/Sobolev estimate, proved here for completeness.

Choosing \(t=B/A\) gives

\[
\sum_k|c_k|\le A\sqrt{2+8B/A}.
\tag{2}
\]

If \(B=0\), Parseval makes every nonzero-frequency coefficient zero and
the bound is simply \(\sum|c_k|\le A\). Equation (2) is only used with
positive \(B\). It is not claimed to improve the old bound for every
possible ratio \(B/A\); the prime-power specialization below does.

## Specialization and exact comparison

Set \(g(\theta)=1/P(e^{i\theta})\). Nonvanishing makes \(g\) smooth, and
the pointwise estimates give the normalized \(L^2\) bounds

\[
\|g\|_2\le A=\delta^{-1},\qquad
\|g'\|_2\le B=M\delta^{-2}.
\]

Then

\[
t=B/A=M/\delta=2n^2H^{nD}=2X^2.
\]

For every integer \(r>2\), \(\varphi(r)\) is even: pair each unit modulo
\(r\) with its distinct negative. Hence \(nD/2\) is an integer and
\(X\) is an integer, at least two in the present domain. Equation (2)
and the exact identity

\[
(1+4X)^2-(2+16X^2)=8X-1>0
\]

give \(\sum|c_k|\le A(1+4X)\). The old expression rewrites as

\[
\delta^{-1}+2M\delta^{-2}=A(1+2t)=A(1+4X^2).
\]

Thus \(C_{\rm old}-C_{\rm new}=4AX(X-1)>0\). All quantities in this
comparison are exact integers. No logarithm or floating-point rounding
is needed to certify the comparison or the reported binary ceilings.

## Transfer to an operator

Write \(U=\tau Z_L^w\). Every integer power of \(U\), including negative
powers and non-coprime or zero strides, has induced infinity norm one.
Consequently \(\sum_k c_kU^k\) converges absolutely in that matrix norm.
The absolutely convergent Fourier series equals \(g\): it has the same
Fourier coefficients and both functions are continuous. Multiplying the
series by the finite polynomial \(P\) gives the constant one. Substitution
of \(U\), justified by absolute convergence and the finite product, yields

\[
P(U)\sum_kc_kU^k=\sum_kc_kU^kP(U)=I.
\]

The series is therefore the inverse and its norm is at most \(\sum|c_k|\).
This proves the statement for all \(L,w,\tau\); there is no assumption
that the eigenvalues of \(U\) are distinct. Finite products are bounded
by the product of these constants. Unit diagonal conjugation preserves
the induced infinity norm, as in #621. The radix-two special bound of
two remains separate and unchanged.

The spectral bound \(\sup_{|z|=1}|P(z)^{-1}|\) alone is insufficient
for the induced infinity norm. An exact counterexample is

\[
P(z)=1+z/2+z^2/2,\qquad
|P(e^{i\theta})|^2=2(\cos\theta+3/8)^2+7/32.
\]

The valid rational lower bound \(\delta=7/15\) would give
\(\delta^{-1}=15/7\). But for the three-cycle,
\(P(Z_3)^{-1}=(3I-Z_3-Z_3^2)/2\), with row sum \(5/2>15/7\).
This rejects a deliberately invalid shortcut; it is not a counterexample
to #621 or to the weighted estimate.

## What improves, and what does not

The leading powers of \(H\) in the explicit bounds change from
\(2nD-1\) to \(3nD/2-1\). The dominant term in the logarithm of this
particular norm overestimate is therefore reduced by one quarter as
\(r\) grows. Both estimates still have logarithm \(O(r^2\varphi(r))\).
The integer bit ceilings in EXPECTED.json describe these constants only;
they are not sufficient working precisions for a complete algorithm.

The finite verification checks exact budget arithmetic, the implementation
of (1) on a declared finite family, and the counterexample. It is not a
formal proof of the Fourier lemma or the multiplication theorem. The
written argument above supplies the all-frequency/all-length reasoning.
Kernel nonvanishing and its circle lower bound remain inherited from
#621. Preparation, rounding, error propagation, dirty restoration,
routing, compiler, tape, hosting, and multiplication transfer are not
discharged, and no new kappa, complex saving, or BIT saving follows.

Prepared for Rafael Guevara (@alephnan) with substantial OpenAI Codex
assistance. Apache-2.0. See NOTICE.md for predecessor attribution.
