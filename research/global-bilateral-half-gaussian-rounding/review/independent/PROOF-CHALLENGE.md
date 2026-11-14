# Independent challenge of the proposed global map

## Review result

I found no counterexample. The proposed map passes the exact boundary,
parity, inverse, unit-error, and half-unit radial checks below. The
coordinate-pair involution together with the R/M/E factorization gives a
direct all-input proof; the finite-point checks in RESULT.json are
cross-checks, not substitutes for that proof.

## Exact matrices and cosets

Let \(U=H_4/2\), \(J=\operatorname{diag}(1,1,1,-1)\), and
\(s=(1,-1,-1,1)^T\). Direct integer multiplication gives

\[
U^2=I,\qquad U^T=U,\qquad R:=UJU=I-\frac{ss^T}{2}.
\]

Since \(s^Ts=4\), \(R^2=I\) and \(R\) is orthogonal. Put
\(E=JU\); it is also orthogonal.

For odd-sum integer \(x\), \(s^Tx\) is odd, and

\[
Rx=x-\frac{s^Tx}{2}s.
\]

Every coordinate of \(Rx\) is half-integral; because \(\sum_i s_i=0\),
its coordinate sum remains odd. Conversely, if \(t\) is half-integral with
odd coordinate sum, then \(s^Tt\) is an odd integer and the same formula
shows \(Rt\in\mathbb Z^4\) with odd sum. Thus \(R\) is a bijection from
odd-sum integer vectors to

\[
A=\{t\in(\mathbb Z+\tfrac12)^4:\sum_i t_i\text{ is odd}\}.
\]

Define

\[
B=\{t\in(\mathbb Z+\tfrac12)^4:\sum_i t_i\text{ is even}\}.
\]

If \(t\in B\), write \(t=z+\tfrac12(1,1,1,1)\). Then \(z\in\mathbb Z^4\)
has even sum. Since every entry of \(H_4\) is odd, \(U z\) is integral,
and \(U(\tfrac12\mathbf1)=(1,0,0,0)\). Hence \(Ut\) is integral.
Also \(\sum_i(Ut)_i=2t_1\) is odd; flipping its fourth coordinate with
\(J\) preserves parity. Therefore \(E(B)\) consists of odd-sum integer
vectors. Conversely, for odd integer \(y\), \(E^{-1}y=UJy\) is
half-integral and has sum \(2y_1\), which is even. Thus \(E:B\to X_{\rm odd}\)
is a bijection, with inverse \(UJ\).

## The half-lattice pairing

Every half-integer magnitude belongs to exactly one pair:

- Axes 0 and 1: for each sign and \(k\ge0\), pair
  \(a=\tfrac12+2k\) with \(a+1=\tfrac32+2k\).
- Axes 2 and 3: pair \(-\tfrac12\) with \(+\tfrac12\) as the central pair;
  for each sign and \(k\ge0\), pair
  \(a=\tfrac32+2k\) with \(a+1=\tfrac52+2k\).

Give a coordinate the score equal to the lower absolute magnitude of its
pair, except that the central pair has score zero. Choose the coordinate
with least (score, index), and toggle its pair. This is exactly M.

The toggle leaves that coordinate's score unchanged. All other scores are
unchanged, including the central score. Thus the same coordinate remains
selected after the toggle and M is an involution. Every toggle changes
one coordinate by \(+1\) or \(-1\), so it flips the parity of the integer
coordinate sum. Consequently \(M\) exchanges A and B bijectively. This
also covers ties: the selected index is fixed by the unchanged score
vector.

## Map, inverse, and rounding error

Define the full map on integer vectors by

\[
F(x)=
\begin{cases}
Ux,&\sum_i x_i\text{ even},\\
EMRx,&\sum_i x_i\text{ odd}.
\end{cases}
\]

The even branch is a bijection of the even-sum integer lattice because U
is an involution and maps even-sum integers to even-sum integers.
For the odd branch, R maps the odd integer coset bijectively to A, M maps
A bijectively to B, and E maps B bijectively to odd integers. Hence F is
a bijection of \(\mathbb Z^4\) preserving total-sum parity.

The explicit inverse is

\[
F^{-1}(y)=
\begin{cases}
Uy,&\sum_i y_i\text{ even},\\
RMUJ\,y,&\sum_i y_i\text{ odd}.
\end{cases}
\]

For odd x put \(t=Rx\). Since \(ER=JU\,UJU=U\) and \(M(t)-t\) is a
signed coordinate unit vector \(\delta\),

\[
F(x)-Ux=E\delta=JU\delta.
\]

The matrix \(JU\) is orthogonal, so this error has norm exactly one.
Because x and F(x) are both odd-sum integers while Ux is
half-integral, F(x) is one of the 16 nearest corners, and parity selects
the required eight-corner subfamily. The even branch has zero error.

## Bilateral radial bound

For odd x, orthogonality of R and E gives

\[
\|x\|_2=\|t\|_2,\qquad \|F(x)\|_2=\|M(t)\|_2.
\]

If M selects the central pair, it only changes \(-1/2\) to \(+1/2\) or
vice versa, so the norm is unchanged.

Otherwise let \(a>0\) be the selected lower magnitude and
\(q=2a+1\). The two phase classes of lower scores are
\(\tfrac12+2\mathbb Z_{\ge0}\) on axes 0,1 and
\(\tfrac32+2\mathbb Z_{\ge0}\) on axes 2,3. Since a is globally minimal,
the other same-phase axis has lower score at least a, and each of the two
opposite-phase axes has lower score at least \(a+1\). No central
coordinate is present in this case because its score zero would have
been selected. Therefore the endpoint with lower norm r satisfies

\[
r^2\ge a^2+a^2+2(a+1)^2
=4a^2+4a+2
=(2a+1)^2+1=q^2+1.
\]

Toggling changes the squared norm by exactly
\((a+1)^2-a^2=q\). If \(r'\) is the larger endpoint radius, then
\(r>q\) and \(r'>r>q\), so

\[
|r'-r|=\frac{q}{r'+r}<\frac{q}{2q}=\frac12.
\]

Thus the bilateral radial bound holds strictly on every noncentral pair
and with equality zero on the central pair. There are no omitted
boundary or tie cases.

## Exact challenge checks

The separate integer implementation in mechanism_check.py:

- verifies \(H_4^2=4I\) and the reflection identity after clearing
  denominators;
- applies M twice on 65,536 half-lattice vectors, including 27,136 score
  ties and 15,360 central-pair cases;
- checks the explicit inverse, parity, unit-error corner condition, and
  exact integer half-slack inequality on all odd input points in precisely
  the named balls \(R=5,9,11\), with no collisions;
- checks 28 explicit odd round trips with coordinate magnitudes up to
  \(2^{1024}\), plus large even exact-U round trips;
- checks the radial lower-bound identity for 1,000 positive half-integer
  scores.

The exact checks corroborate the algebra. They do not extend the finite
flow search to other radii. This challenge did not read or compare against
any other current proof package.
