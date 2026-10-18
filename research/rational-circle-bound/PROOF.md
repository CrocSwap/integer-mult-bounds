# A degree-controlled inverse bound by root reflection

## Result

Let P be a nonzero complex polynomial of degree n, and suppose
|P(z)| >= delta > 0 for |z|=1. Let m count its roots strictly inside
the disk, with multiplicity. The absolutely convergent Laurent series
of 1/P on the circle has coefficient norm

\[
 \boxed{\quad \|1/P\|_W
 \le { (1+4m)(1+4n)\over\delta}
 \le { (1+4n)^2\over\delta}.\quad}                 \tag{1}
\]

Here W denotes the sum of absolute values of all Fourier coefficients,
including negative indices. No separation between roots, nor a lower
bound on each root's distance to the circle, enters the multiplier.
Repeated roots and roots at zero are allowed. A constant polynomial
has m=n=0 and satisfies the same statement.

If an invertible bounded operator U on a complex Banach space satisfies
||U^k|| <= 1 for every integer k, then

\[
 \|P(U)^{-1}\|\le (1+4n)^2/\delta.                \tag{2}
\]

This applies to U=tau Z_L^w for every L>=1, integer w (including zero
and noncoprime strides), and |tau|=1, in induced infinity norm. It also
applies to a permutation with independently varying unit phases.

The ingredients below are classical. The contribution is their explicit,
self-contained application to the circle certificate retained from Ali
Romman's PR621 and its comparison with our previous Fourier audit. It
is not a literature-priority claim, a paid inversion algorithm, a formal
proof-assistant result, or a new multiplication exponent.

The source and analytic audit responding to the review of commit
`d213ac12d4a1ab8f717d942e844df318ceb395fb` is in
[audit/README.md](audit/README.md). It maps each implication to its proof
and records the limits of that audit separately from finite evidence.
Throughout, circle integrals use `dt/(2 pi)` unless explicitly unnormalized,
and the Fourier convention is

\[
 \widehat f(k)={1\over2\pi}\int_0^{2\pi}f(e^{it})e^{-ikt}\,dt,
 \qquad \|f\|_W=\sum_{k\in\mathbb Z}|\widehat f(k)|.
\]

## 1. A coefficient inequality with an elementary constant

For an analytic function h in a neighborhood of the closed disk, write
h(z)=sum_{j>=0} h_j z^j. With normalized circle measure, we will use

\[
 \sum_{j\ge0}{|h_j|\over j+1}\le4\|h\|_{L^1}.   \tag{3}
\]

Here is a proof of this nonoptimal version of Hardy's inequality.
First the matrix K_{jk}=1/(j+k+1), j,k>=0, has l2 operator norm at most
4. Set w_j=(j+1/2)^(-1/2) and a=j+1/2. For
f_a(x)=x^(-1/2)/(a+x), direct differentiation gives

\[
 f_a''(x)={3\over4x^{5/2}(a+x)}
        +{1\over x^{3/2}(a+x)^2}
        +{2\over x^{1/2}(a+x)^3}>0.
\]

The integral at zero is improper but finite. Jensen's midpoint inequality
also applies on [0,1] (or by a limit of interior integrals).
The midpoint inequality on each [k,k+1] therefore gives

\[
 \sum_{k\ge0}{w_k\over j+k+1}
 \le\int_0^\infty{dx\over(a+x)\sqrt{x}}
 \le {4\over\sqrt a}=4w_j.
\]

For the last bound, split the integral at a. Use 1/a for 1/(a+x)
on (0,a), and 1/x on (a,infinity); each piece is at most 2/sqrt(a).
Weighted Cauchy-Schwarz applied to finite nonnegative sequences s,t
now yields

\[
 \sum_{j,k}{s_jt_k\over j+k+1}
 \le \left(\sum_{j,k}K_{jk}{w_k\over w_j}s_j^2\right)^{1/2}
      \left(\sum_{j,k}K_{jk}{w_j\over w_k}t_k^2\right)^{1/2}
 \le4\|s\|_2\|t\|_2.                            \tag{4}
\]

Suppose initially that h has no zero on the circle and is not identically
zero. Remove its finitely many disk zeros, with multiplicity, by a finite
Blaschke product J. The apparent singularities of h/J at these zeros
are removable, with
nonzero limiting values because the multiplicities match. The quotient
is therefore analytic and zero-free on the closed disk. By compactness,
it is analytic and zero-free on some disk |z|<1+eta, eta>0; shrink eta
also to avoid the finitely many poles of J. On that simply connected
disk it has an analytic logarithm, so v=exp(log(h/J)/2) is an analytic
square root. Put a=Jv, b=v. These functions satisfy h=ab and

\[
 \|a\|_2^2=\|b\|_2^2=\|h\|_1,
\]

since |J|=1 on the circle. The coefficient convolution, the triangle
inequality, (4), and Parseval give

\[
 \sum_{l\ge0}{|h_l|\over l+1}
 \le\sum_{j,k\ge0}{|a_j||b_k|\over j+k+1}
 \le4\|a\|_2\|b\|_2=4\|h\|_1.
\]

More explicitly, for each N bound sum_{l=0}^N |h_l|/(l+1) by the
nonnegative convolution sum over j+k<=N, then by the square truncation
0<=j,k<=N of (4). Parseval bounds both truncated l2 norms uniformly.
Let N tend to infinity. This proves the infinite inequality without
assuming the desired weighted absolute summability in advance.
The zero function is immediate. For possible
circle zeros, apply the result to h(rho z) along rho increasing to 1
and avoiding the finitely many zero radii, then use monotone convergence
on the coefficients and uniform convergence on the circle. This proves
(3), including its normalization and endpoint case.

## 2. Rational degree controls arc length

For R=A/B of rational degree d=max(deg A,deg B), without poles on the
circle, put M=max_{|z|=1}|R(z)|. The classical Dolzhenko-Spijker estimate is

\[
 \|R'\|_{L^1(\mathbb T)}\le dM.                 \tag{5}
\]

The following is the projection argument of Spijker's original Lemma 2,
with the polynomial and normalization made explicit; it is not a new
proof method. See BIT 31 (1991), pp. 552-554, equation (4) and Lemma 2;
the original author-uploaded text is linked in SOURCES.json. The same
normalized statement is Baranov-Zarouf, Section 1.2.2, equation (1.3).

Cancel any common factors first. Use the reduced degree d, or any larger
integer degree bound; B has no zero on the circle. For a polynomial A of
degree at most d define its padded conjugate reciprocal by

\[
 A^{\#}_d(z)=\sum_{j=0}^d\overline{a_j}z^{d-j},
 \qquad A^{\#}_d(z)=z^d\overline{A(z)}\quad(|z|=1).
\]

Define B^{#}_d likewise. Put gamma(t)=R(e^{it}) and
x_phi(t)=Re(e^{-i phi} gamma(t)). For z=e^{it}, the level equation
x_phi(t)=s is equivalent to

\[
 F_{\phi,s}(z)=e^{-i\phi}A(z)B^{\#}_d(z)
       +e^{i\phi}A^{\#}_d(z)B(z)-2sB(z)B^{\#}_d(z)=0.       \tag{5a}
\]

Indeed, this is obtained by multiplying the level equation by
2 z^d |B(z)|^2, which is nonzero on the circle. Every term in (5a)
has degree at most 2d, also when A or B has degree less than d.

If x_phi is constant its variation is zero. Otherwise F_{phi,s} is a
nonzero polynomial for every s: an identically zero F would make the
projection constantly s. It therefore has at most 2d distinct unit-circle
zeros, hence at most 2d preimages in 0<=t<2pi for every level s.

The projection is real analytic on a neighborhood of the parameter
circle. Its derivative either vanishes identically (the constant case)
or has finitely many zeros on a period, by the identity theorem and
compactness. Split at these zeros and at the period endpoint. On each
open piece x_phi is strictly monotone, so its variation is the integral
of the indicator of its image interval. Summing the finitely many
pieces gives the integral of the number of preimages for almost every
s; the finitely many endpoint and critical values have measure zero.
Since |x_phi|<=M,

\[
 \int_0^{2\pi}|x_\phi'(t)|\,dt\le 4dM.
\]

Integrating over 0<=phi<2pi, the integral of
|Re(e^{-i phi}v)| is 4|v| for every complex v. Hence
4 int_0^{2pi} |gamma'| dt <= 8pi dM. Interchanging these
nonnegative continuous integrands is valid. The chain rule gives
gamma'(t)=i e^{it} R'(e^{it}), so dividing the last bound by 8pi
proves ||R'||_1 <= dM with normalized circle measure, as in (5). The
case of a constant R is immediate. This is an
elementary proof of a classical result, not a new arc-length theorem.

## 3. An analytic rational function has a degree-only Wiener penalty

If R is rational of degree at most d and analytic in a neighborhood of
the closed disk, then so is h=R'. For R(z)=sum r_j z^j, its derivative
has coefficients h_j=(j+1)r_{j+1}. Applying (3) therefore gives exactly

\[
 \sum_{j\ge1}|r_j|\le4\|R'\|_1\le4d\|R\|_\infty.
\]

Also |r_0|<=||R||_infinity by the maximum principle. Therefore

\[
 \|R\|_W\le(1+4d)\|R\|_\infty.                \tag{6}
\]

The analyticity requirement matters: 1/P can have disk poles. Applying
(6) to it before addressing those poles would be an invalid argument.

## 4. Reflect interior roots without changing circle magnitude

Factor P(z)=c product_{j=1}^n(z-alpha_j). All |alpha_j| differ from 1.
Define

\[
 Q(z)=c\prod_{|\alpha_j|<1}(1-\overline{\alpha_j}z)
          \prod_{|\alpha_j|>1}(z-\alpha_j),
 \qquad
 J(z)=\prod_{|\alpha_j|<1}{z-\alpha_j\over1-\overline{\alpha_j}z}.
\]

Then P=JQ exactly. Every nonconstant reflected factor of Q has its
root outside the disk, and a zero root contributes the constant factor
1 to Q and a factor z to J. Thus Q has no zeros in the closed disk,
deg Q<=n, J has rational degree m, and |J|=1 on the circle. In
particular |Q|=|P|>=delta there.

Both 1/Q and J are analytic in a neighborhood of the closed disk.
By (6),

\[
 \|1/Q\|_W\le(1+4n)/\delta,\qquad \|J\|_W\le1+4m.
\]

On the circle, 1/P=overline(J)/Q. Write J(z)=sum_{j>=0} b_j z^j
and 1/Q(z)=sum_{l>=0} a_l z^l. Both coefficient sequences are in l1
by (6), and their series converge uniformly on the circle. Thus

\[
 {1\over P(z)}=\sum_{j,l\ge0}\overline{b_j}a_l z^{l-j},
 \qquad c_k=\sum_{l-j=k}\overline{b_j}a_l,
 \qquad \sum_{k\in\mathbb Z}|c_k|
       \le\left(\sum_j|b_j|\right)\left(\sum_l|a_l|\right).  \tag{7}
\]

The double absolute sum is finite, which justifies regrouping and
termwise integration to identify c_k as the Fourier coefficients of
1/P. This establishes (1), including negative indices; no Fourier
sampling or limit in the cyclic length is involved. It also agrees
with the Laurent series on a root-free annulus containing the circle.
No roots need be computed to use the worst-case m<=n.

## 5. Operator substitution and the prime-power comparison

Write P(z)=sum_{j=0}^n p_j z^j and use c_k from (7). In the Banach
algebra of bounded operators, ||U^k||<=1 for every integer k makes
S=sum_{k in Z} c_k U^k converge absolutely in operator norm, with
||S||<=sum_k |c_k|. Invertibility of U makes all negative powers defined.

The uniformly convergent circle identity P(z) sum_k c_k z^k=1 gives,
by termwise Fourier integration,

\[
 \sum_{j=0}^n p_jc_{q-j}=\begin{cases}1,&q=0,\\0,&q\ne0.\end{cases}
\]

Moreover sum_{j,k}|p_j c_k| ||U^{j+k}|| is finite. Regrouping the
operator series by q=j+k is therefore valid and gives P(U)S=I.
All integer powers of U commute, giving SP(U)=I by the same calculation.
Thus S is the inverse, proving (2) without assuming invertibility of
P(U) or diagonalizing it in advance.

A fixed permutation matrix multiplied by a diagonal of unit-modulus
entries, and its inverse, are infinity-norm isometries. Their integer
powers have norm one, including zero/noncoprime strides and arbitrary
coordinate-dependent unit phases. Unit-circle spectrum alone would
not suffice: U=[[1,25],[0,1]] and P(z)=z-2 have delta=1 and
||P(U)^{-1}||_infinity=26>25=(1+4)^2. That U violates the power-norm
hypothesis. The separate weighted-cycle audit PR852 likewise treats
this hypothesis as essential, not as a consequence of spectral location.

Retain PR621's certified inputs, without changing its nonvanishing proof:

\[
 r=\ell^a\ge3,\quad n=r-1,\quad D=\varphi(r),\quad H=2^r-1,
 \quad A=\delta^{-1}=2rnH^{nD-1},\quad X=nH^{nD/2}.
\]

The inherited PR621 expression is A+(2nH/r)A^2. Since
(2nH/r)A=4n^2 H^{nD}=4X^2, it equals A(1+4X^2) exactly.
The three explicit norm overestimates are

| Estimate | Constant | Leading power of H |
|---|---|---|
| Incorporated PR621 | A(1+4X^2) | 2nD-1 |
| Previous local weighted-Fourier audit | A(1+4X) | 3nD/2-1 |
| This degree-controlled application | A(1+4n)^2 | nD-1 |

The new constant is strictly smaller than both predecessors for every
admitted r. Indeed n>=2, D>=2, H>=2n+1, and
H^{nD/2}>=H^2>4n+2. Thus
1+4nH^{nD/2}>(1+4n)^2. The previous audit already proved its own
strict improvement over PR621; alternatively X>1 makes it immediate.

The dominant logarithmic term is reduced by one third relative to our
previous audit and one half relative to PR621 as r grows. The order is
still O(r^2 phi(r)), not a better asymptotic order. Binary ceilings in
EXPECTED.json concern these sufficient norm constants, not measured
condition numbers, execution speed, or full working precision.

Radix two keeps its sharper geometric bound 2. The general theorem
applies to composite radices if a separate circle lower bound is proved;
it does not prove that missing nonvanishing premise. For products of
operators one may multiply the displayed constants. Independently
varying unit phases and unit diagonal conjugation preserve the required
power-norm property. No new weighted-stride solver is claimed.

## 6. The inverse-gap power cannot be reduced in general

The factor delta^{-1} is necessary even at fixed degree. For 0<epsilon<1,
take P_epsilon(z)=z-(1+epsilon). The reverse triangle inequality gives
min_{|z|=1}|P_epsilon(z)|=epsilon, with equality at z=1. For U=I,
||P_epsilon(U)^{-1}||=epsilon^{-1}. Thus no bound C(n) delta^{-beta}
with beta<1 and finite C(1) can hold uniformly as delta decreases to zero.
Multiplication by z^{n-1} gives the same witness at every fixed n>=1.
This establishes the necessary gap exponent, not optimality of the
quadratic degree factor in (1).

## 7. Limits and relation to other work

The reflection factorization is used for a proof, not an instruction to
find roots during execution. This package therefore supplies no new
factor-preparation, arithmetic, traffic, routing, scratch, or bit-cost
bound. PR628 and the concurrent PR764 concern rounded implementations;
this estimate has not been integrated into their error recurrences. It
does not imply their per-factor margins, dirty-restoration precision,
or their operation counts automatically improve.

In particular the finite verifier cannot prove the analytic lemmas. It
checks exact polynomial/reflection identities, independent cyclic inverse
formulas, finite Hilbert inequalities, budget arithmetic, and specified
failure modes. The written argument supplies the all-frequency and
all-length reasoning. Independent human or proof-assistant review remains
open, as do the repository's full multiplication obligations.

Classical references and repository pins are recorded in SOURCES.json,
NOTICE.md, and audit/README.md. Spijker's original equation (4) and
Lemma 2 use unnormalized arc length; dividing by 2 pi gives (5).
Baranov-Zarouf, arXiv:1310.1182v1, Section 1.1 and Section 1.2.2,
equation (1.3), confirm the normalized form and Dolzhenko attribution.
The opening of Kanjin-Sato records Hardy's coefficient inequality with
an unspecified constant and unnormalized H1 measure. It is background
attribution, not a source for our normalized constant four; Section 1
proves that constant directly. Finite Blaschke reflection is classical.

Prepared for Rafael Guevara (@alephnan) with substantial OpenAI Codex
assistance. Apache-2.0.
