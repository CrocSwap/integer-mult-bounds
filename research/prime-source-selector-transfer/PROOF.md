# Proof: prime-source selector transfer

## Statement and hypotheses

Let \(n\) be a sufficiently large positive integer and put

\[
b=\lceil\log_2 n\rceil,\quad p=6b,\quad
\epsilon=2^{-75},\quad d=\lfloor b^\epsilon\rfloor.
\]

Assume \(b\ge 5^{2^{75}}\), and choose the source's power of two \(T\) in
\([4n/b,8n/b)\). For \(i=1,\dots,d\), let
\(t_i\in\{r/2,r\}\), where

\[
r=2^\ell,\qquad \ell=\left\lceil\frac{\log_2T}{d}\right\rceil,\qquad
\prod_{i=1}^d t_i=T.
\]

Set \(\eta=1/(4d)\) and
\(\alpha=\lceil(12d^2b)^{1/4}\rceil\). We prove, conditional on the explicit
Chebyshev estimate (RS) below, that distinct odd primes \(s_i\) can be chosen
so that

\[
(1-2\eta)t_i<s_i\le(1-\eta)t_i,
\]

and that these choices give the source's prime-length product, coprimality,
gap, and setup-time conclusions.

The only imported analytic hypothesis is

\[
\tag{RS}
y-\frac{y}{2\log y}<\vartheta(y)<y+\frac{y}{2\log y}
\quad\text{for every }y>563,
\qquad
\vartheta(y)=\sum_{\substack{q\le y\q\text{ prime}}}\log q,
\]

with natural logarithms. This is Rosser–Schoenfeld, Theorem 4, as quoted in
Harvey–van der Hoeven, proof of Lemma 5.1. No claim here reproves (RS).

## 1. Parameter inequalities and the explicit cutoff

Since \(b\ge5^{2^{75}}\) and \(\epsilon=2^{-75}\),
\(b^\epsilon\ge5\), hence \(d\ge5\). The cutoff also implies \(b\ge2^{16}\).
We have

\[
0<\epsilon<\frac14,\qquad d\le b^\epsilon\le\sqrt b,\qquad d\le b.
\]

For \(b\ge8\), the definition of \(T\) gives

\[
\frac b2\le\log_2T\le b.
\]

Indeed \(2^{b-1}\le n\le2^b\), so
\(\log_2(4n/b)\ge b+1-\log_2b\ge b/2\), while
\(T<8n/b\) gives \(\log_2T<b+3-\log_2b\le b\).
We use \(1/2<\log2<1\), which follows by integrating \(1/u\) on the interval \([1,2]\).
For the lower bound, \(f(b)=b/2+1-\log_2b\) has \(f(8)=2\) and
\(f'(b)=1/2-1/(b\log2)>1/2-2/b\ge1/4\) for \(b\ge8\),
so \(\log_2b\le b/2+1\). The upper bound uses \(\log_2b\ge3\).

The ceiling defining \(\ell\) therefore yields

\[
\frac{b}{2d}\le\ell<\frac bd+1\le\frac{2b}{d}.
\tag{1}
\]

Because \(1-2\epsilon>1/2\) and \(b\ge2^{16}\),

\[
\frac b{d^2}\ge b^{1-2\epsilon}\ge\sqrt b\ge256>64.
\tag{2}
\]

This stronger-than-needed cutoff makes the prime-counting hypotheses
quantitative without estimating the value of \(n\) in decimal notation.

## 2. Deriving the prime-interval count from (RS)

We first give the precise conditional estimate used below. Suppose
\(0<\eta<1/4\) and \(x>e^{2/\eta}\). Put

\[
y_0=(1-2\eta)x,\qquad y_1=(1-\eta)x.
\]

Since \(\eta<1/4\), \(x>e^8\). Also
\(e>5/2\), for example from the first four terms of its series, and
\((5/2)^8/2>563\). Thus \(y_0>x/2>e^8/2>563\), and also
\(563<y_0<y_1<x\). The function \(u/\log u\) is increasing for \(u>e\).
Applying (RS) at \(y_0,y_1\), and bounding both error terms by
\(x/(2\log x)\), gives

\[
\vartheta(y_1)-\vartheta(y_0)>
y_1-y_0-\frac{x}{\log x}
=\eta x-\frac{x}{\log x}
>\frac{\eta x}{2},
\]

where the last strict inequality follows from \(\log x>2/\eta\).
Every prime \(q\) with \(y_0<q\le y_1\) has \(\log q\le\log x\), so

\[
\#\{q\text{ prime}: (1-2\eta)x<q\le(1-\eta)x\}
>\frac{\eta x}{2\log x}.
\tag{3}
\]

This proves the interval estimate conditional on (RS); it is not an
independent proof of the prime-number estimate itself.

## 3. Both source intervals contain enough primes

For the source choice \(\eta=1/(4d)\), \(d\ge5\) gives
\(0<\eta\le1/20<1/4\) and \(2/\eta=8d\). Let
\(x_0=r/2=2^{\ell-1}\). From (1) and (2),

\[
\log x_0=(\ell-1)\log2
\ge\left(\frac b{2d}-1\right)\log2
\ge(32d-1)\log2>8d.
\]

For the final inequality it is enough that \(\log2>1/2\), since
\((32d-1)/2>8d\). Thus both \(x=x_0\) and \(x=r\) satisfy
\(\log x>8d=2/\eta\), so (3) applies.

It remains to check that the lower bound in (3) exceeds \(d\). For
\(b\ge2^{16}\),

\[
\frac b{2d}\ge\frac12b^{1-\epsilon}\ge\frac{\sqrt b}{2}.
\tag{4}
\]

Also \(\log_2b\le\sqrt b/8\) for \(b\ge2^{16}\): the difference
\(\sqrt b/8-\log_2b\) is positive at \(2^{16}\) and increasing, since its
derivative is positive whenever \(\sqrt b\log2>16\). Using \(\log2>1/2\),
this derivative condition holds throughout \(b\ge2^{16}\). Since
\(\sqrt b/4>5\),

\[
\frac b{2d}\ge\frac{\sqrt b}{2}>
5+2\log_2b\ge5+\log_2b+\log_2d.
\]

Equivalently,

\[
\frac b{2d}-1>4+\log_2b+\log_2d,
\]

and consequently \(x_0\ge2^{b/(2d)-1}>16bd\). From (1) and \(d\le b\),

\[
\log r=\ell\log2<\frac{2b}{d},\qquad
8d^2\log r<16bd<x_0.
\]

For either \(x=x_0\) or \(x=r\), we have \(x\ge x_0\) and
\(\log x\le\log r\), hence \(x>8d^2\log x\). Substituting
\(\eta=1/(4d)\) into (3) gives

\[
\#\{q\text{ prime}: (1-2\eta)x<q\le(1-\eta)x\}
>\frac{x}{8d\log x}>d.
\tag{5}
\]

Each of the two source intervals therefore contains at least \(d\) primes.
The number of axes with \(t_i=r/2\) and the number with \(t_i=r\) are each
at most \(d\), so the required number can be selected in each interval.

## 4. Distinctness, padding, and resampling gaps

The intervals for \(x=r/2\) and \(x=r\) are disjoint because

\[
(1-\eta)\frac r2 < (1-2\eta)r
\quad\Longleftrightarrow\quad \eta<\frac13,
\]

and here \(\eta\le1/20\). Their lower endpoints exceed \(2\): by (1),
\(d\le\sqrt b\), and \(b\ge2^{16}\), we have
\(\ell\ge b/(2d)\ge\sqrt b/2\ge128\), so \(r/2\ge2^{127}\);
also \(1-2\eta\ge9/10\). Thus every selected prime is odd, and disjointness
of the intervals makes all \(s_i\) distinct.

Since each \(t_i\) is a power of two, \(\gcd(s_i,t_i)=1\). The interval
endpoints imply

\[
\frac{t_i}{s_i}-1
\ge\frac{\eta}{1-\eta}>\eta=\frac1{4d},
\qquad
\frac{t_i}{s_i}-1
<\frac1{1-2\eta}-1
=\frac1{2d-1}\le\frac19<\frac18.
\tag{6}
\]

For \(S=\prod_i s_i\) and \(T=\prod_i t_i\), strict Bernoulli inequality
for integer \(d\ge2\) gives

\[
\frac ST>
\left(1-\frac1{2d}\right)^d
>1-d\frac1{2d}=\frac12.
\]

The upper interval endpoints also give \(s_i<t_i\), hence \(S<T\). Therefore
\(T/2<S<T\).

Finally, \(\alpha^4\ge12d^2b\). From (6),

\[
\alpha^4\left(\frac{t_i}{s_i}-1\right)>
\frac{12d^2b}{4d}=3db\ge6b=p,
\]

since \(d\ge5\). This verifies the prime-length-dependent gap needed by the
source's resampling application. It does not prove the other hypotheses of
that lemma.

## 5. Deterministic setup cost

The total number of integers in the two searched intervals is \(O(r)\).
Testing every candidate by trial division visits at most \(O(\sqrt r)\)
divisors per candidate. Candidate and divisor integers have
\(O(\log r)=O(p)\) bits by (1); ordinary binary division and maintenance of
the selected list therefore cost at most
\(O(d\,r^{3/2}\operatorname{poly}(p))\) bit operations.

Because \(d=\lfloor b^\epsilon\rfloor\to\infty\), (1) gives

\[
\log\!\left(d\,r^{3/2}\operatorname{poly}(p)\right)
=O(\log p+p/d)=o(p)=o(\log n).
\]

Thus the scan cost is \(n^{o(1)}\). In particular it is \(o(n)\): eventually
an \(n^{o(1)}\) quantity is at most \(n^{1/2}\).

## Exact scope

Proved here: the source parameter choice and (RS) imply existence of all
required distinct odd prime lengths, the displayed product and gap bounds,
and the stated sublinear deterministic scan bound, for every input length
with \(b\ge5^{2^{75}}\).

Conditional here: (RS) is imported from Rosser–Schoenfeld Theorem 4, as cited
by Harvey–van der Hoeven Lemma 5.1. The scan bound uses the source's ordinary
trial-division cost model.

Not proved here: (RS), the full no-sort resampling lemma, the other assembly
interfaces, any supplier/compiler/precision transfer, or the selected
multiplication theorem.
