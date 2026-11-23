# Rounded parity-triangular execution

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.
Apache-2.0.

## Domain and result

I extend the FFT/shear argument in [PROOF.md](PROOF.md) to Vlado/PR1673's
retained `triangle_plan` and its exact stored-coefficient inverse.
For \(N=2^d\), let \(T=L(f)\) be lower triangular Toeplitz over
\(\mathbb Q(i)\). I admit
\[
\sum_{j=0}^{N-1}(|\Re(f_j-\delta_{j0})|
                 +|\Im(f_j-\delta_{j0})|)\le\tfrac12.
\tag{1}
\]
This executable condition implies both induced \(1\)- and infinity-norm
bounds \(\|T-I\|\le1/2\). I do not extend the executable admission to
complex symbols that satisfy only the weaker modulus-sum condition.
The caller may supply a permutation of the \(N\) wires, including reversal.

For target \(2^{-t}\), input norm at most \(R\ge1\), and an incoming dyadic
grid with \(F_0\) fractional bits, I construct one rational gate program
\(\widehat T\) and its inverse using the same stored coefficients.
After nearest component rounding on one common \(F\)-grid at each gate,
I prove error at most \(2^{-t}\) for either \(Tx\) or \(T^{-1}x\).
The input to each direction must satisfy the stated radius and grid.
I give a separate allowance for a rounded forward/inverse round trip.

I use the following conservative bounds:
\[
B=100N^3,\quad q=2d+1,\quad
D=4d^2+12d+1,\quad G=N(2d^2+8d+1).
\tag{2}
\]
Here \(q\) counts macro layers, \(D\) bounds physical gate layers and \(G\)
bounds logical one/two-wire gates. I preserve empty source layers and
zero shears. I claim logical execution and precision, with physical tape
delivery and full bounded-generator composition left for later work.

## Descendants and ideal prefixes

I use the predecessor's parity identity. The source executes the upper
shear, then the block diagonal, then the lower shear. After parity
permutation, their ordinary matrix product is
\[
T\sim\begin{pmatrix}I&0\\K&I\end{pmatrix}
\begin{pmatrix}E&0\\0&S\end{pmatrix}
\begin{pmatrix}I&ZK\\0&I\end{pmatrix},
\quad
K=OE^{-1},\quad S=E-ZOK.
\tag{3}
\]
All \(E,O,K\) are commuting lower
triangular Toeplitz matrices. The source computes their coefficients
with exact truncated series and convolution.

Every recursive descendant is a principal Schur complement of a
principal restriction of the original \(T\), after a permutation.
For either induced norm, a principal restriction \(I+H\) still has
\(\|H\|\le1/2\). Its inverse has norm at most two. For a Schur complement
\(M\), the inverse is a principal block of that inverse, so
\(\|M^{-1}\|\le2\). The Schur formula also gives
\[
\|M-I\|\le\tfrac12+
  \frac{(1/2)^2}{1-1/2}=1,\qquad \|M\|\le2.
\tag{4}
\]
Nested principal restrictions of Schur complements preserve this
description by retaining the previously eliminated set. I need the
original near-identity hypothesis on arbitrary principal restrictions;
conditioning only leading sections would not suffice.

Thus \(\|O\|_{1,\infty},\|E^{-1}\|_{1,\infty}\le2\), and
\(\|K\|_{1,\infty},\|ZK\|_{1,\infty}\le4\). For a lower triangular
Toeplitz matrix, the full coefficient modulus sum equals its induced
1-norm. The component sum is therefore at most \(4\sqrt2<6\).
An ideal completed shear and its inverse have norm at most five.
An ideal middle block and its inverse have norm at most two.

I apply the FFT/shear segment lemma to each child, whose cyclic and
negacyclic kernel component envelopes sum to less than six.
Both ideal and compiled child internal prefixes, suffixes and their
inverses have norm at most seven; for compiled children the additional
multiplier allowance \(2v\) still fits because \(v\le1/32\) and
\(4\sqrt2+2v<6\).

For ideal physical prefixes and their inverses, I obtain
\[
B(N)\le\max(7,\ 5B(N/2),\ 7\cdot2\cdot5),\qquad B(1)\le2.
\tag{5}
\]
The three cases stop in the first shear, recursive middle or last shear.
For inverse prefixes I reverse the factors in the inverse of that
prefix; the same norm products apply. Equation (2) dominates (5).
Disjoint siblings combine by the maximum of their operator norms.

## Stored coefficients and aligned macro errors

At each recursion depth, equal-size siblings emit identical schedules
regardless of their coefficients. I group their disjoint shear children
into one macro layer, recurse on the middle, and group their scalar leaves.
This gives \(q=2d+1\). The source keeps the two siblings in parallel.
The retained shear count gives
\[
D(d)\le D(d-1)+2(4(d-1)+8),\quad D(0)=1,
\]
and summing the gates at each level gives the bounds in (2).

Set
\[
s=t+\left\lceil\log_2(4qB^3(R+1))\right\rceil,\quad
\varepsilon=2^{-s},\quad
P=s+\left\lceil\log_2(48(d+1))\right\rceil,\quad S=s+2.
\tag{6}
\]
I use \(P\) for the existing certified unit phases and \(S\) for stored
spectral multipliers. A child of size \(m\) has unrounded endpoint defect
\[
4(\log_2m+1)M\,2^{-P}+2^{1-S}\le\varepsilon,
\quad M<6.
\tag{7}
\]
For the scalar leaves I store nearest \(s\)-grid values. Their complex
error is at most \(\varepsilon\). The ideal modulus lies between \(1/2\)
and two; the stored modulus is at least \(1/4\). In the reverse program
I use the exact reciprocal of that same stored scalar. I retain the
unrounded rational coefficients throughout recursive series preparation.
I do not apply leaf rounding to the unitary twist gates.

For each ideal macro \(A_j\), its compiled counterpart has
\(\|\widehat A_j-A_j\|\le\varepsilon\), because its pieces act on disjoint
supports. Write \(Q_j=A_j\cdots A_1\), \(Q_0=I\), and
\[
G_j=Q_j^{-1}(\widehat A_j-A_j)Q_{j-1},\qquad
Z_j=Q_j^{-1}\widehat A_j\cdots\widehat A_1.
\]
Then \(Z_j=(I+G_j)Z_{j-1}\) and
\[
\|G_j\|\le B^2\varepsilon,\qquad
\theta=qB^2\varepsilon\le\tfrac14.
\tag{8}
\]
For a consecutive product \(W\) of these factors, the sum of the bounds
on its perturbations is at most \(\theta\). Expanding the product and
using \(\prod(1+a_j)\le1/(1-\sum a_j)\) gives
\[
\|W\|,\|W^{-1}\|\le(1-\theta)^{-1}<2,\quad
\|W-I\|,\|W^{-1}-I\|\le\theta/(1-\theta)\le2\theta.
\tag{9}
\]
For the inverse inequality I use
\(\prod(1-a_j)\ge1-\sum a_j\), and the expansion of the inverse factors.
Since \(\widehat T=T Z_q\), both directions satisfy the loose common bound
\[
\|\widehat T-T\|,\ \|\widehat T^{-1}-T^{-1}\|
\le 2qB^3\varepsilon=:e.
\tag{10}
\]
I use the exact inverse of the stored approximate circuit here.
The proof does not replace a nonunitary scalar's inverse with its adjoint.

## Suffixes, accumulated rounding and word widths

Actual macro prefixes and their inverses have norm at most \(2B\).
For a suffix after macro \(j\), I write it as
\[
Q_q W Q_j^{-1}.
\]
Its inverse has the reversed inverse factors. Since
\(\|Q_q\|,\|Q_q^{-1}\|\le2\), (9) bounds both by \(4B\).
An internal child fragment adds a factor of at most seven.
Thus \(K=32B\) bounds physical prefixes, suffixes and their inverses
in either execution direction.

An arbitrary physical segment may need the larger bound \(K^2\):
I express it as a prefix times an inverse prefix. I use this bound
for intermediate states after several rounding errors.
One physical layer contributes Euclidean rounding error at most
\(\sqrt{N/2}\,u\le Nu\), where \(u=2^{-F}\).
Therefore I obtain
\[
\|\widehat z-T^{\pm1}x\|\le eR+DKNu,
\qquad
\max_{\text{intermediate states}}\|z\|\le
A:=KR+DK^2Nu.
\tag{11}
\]
Choose
\[
F=\max\left(F_0,\ t+\left\lceil\log_2(64DBN)\right\rceil\right).
\tag{12}
\]
Equations (6), (10) and (12) assign at most \(2^{-t}/2\) to each
of coefficient and data error. Also \(A\le K(R+2^{-t}/2)\).
I retain finer incoming grids.

If \(\widehat a=(a+ib)/2^s\) is a stored leaf, its exact reciprocal is
\(2^s(a-ib)/(a^2+b^2)\). With \(|\widehat a|<3\), its component height
is at most \(2s+6\). I use the still looser common bound
\[
C_{\rm bits}=\max(4P+24,\ S+5,\ 2s+16),\quad
I=\max(1,\lceil\log_2\max(1,A)\rceil)+2.
\tag{13}
\]
The previous constant-size rational gate evaluation argument then gives
signed canonical grid width \(F+I\) and temporary allowance
\[
2F+8C_{\rm bits}+2I+32.
\tag{14}
\]
All these online widths are \(O(F_0+t+\log N+\log R)\).
Exact offline series, Schur coefficients and dense checker matrices can
have longer denominators. I do not include them in the online word claim.
The original preprocessing proof supplies the algebraic preparation
context; complete setup and physical coefficient-delivery costs remain open.

For a rounded forward/inverse round trip, let
\(E=eR+DKNu\). The forward output has norm at most \(2R+E\).
Applying the same inverse program gives the separate allowance
\[
\|\widehat{\operatorname{inverse}}(\widehat{\operatorname{forward}}(x))-x\|
\le 2E+e(2R+E)+DKNu.
\tag{15}
\]
I do not promise exact restoration after data rounding.
For this extra second pass I use radius \(R'=2R+E\) in the amplitude
and integer-width formulas, keeping the same stored gates and \(F\).
The verifier records that enlarged second-pass width separately.

## Executable evidence and attribution

I extract the authenticated `toep`, `lower`, `invseries`, `conv` and
`triangle_plan` functions. I change only the floating diagnostic and the
scalar leaf return. I supply exact array/convolution operations and
certified child callbacks, keeping the source's `parallel` and `inverse`.
I retain even/odd wire order, reversed caller indices, empty layers and
zero shears. The verifier checks exact macro identities against a direct
Toeplitz matrix and the inverse against separate Gauss-Jordan elimination.

The exact endpoint Frobenius checks corroborate consequences of the
operator proof; they do not independently establish its sharper norm
bound. I compare rounded vectors with exact endpoint images in both
directions and include a nonzero rounded round-trip error witness.
I test mutations of the Schur correction, parity banks, parallel middle
and inverse order, plus the nonunitary-leaf adjoint error.
I label observed temporary heights as completed rational components;
I do not claim exhaustive instrumentation of `Fraction` internals.

I credit Vlado Vojdanovski/PR1673 for the parity factorization, recursion,
Schur descendant argument and circuit; Chafik Boukhalfa/PR628 for phases;
and Cinna Davis for the later caller. I add the explicit common
coefficient/grid allocation, inverse and intermediate-width accounting,
and source-bound rational execution. Internal source-analysis agents
belong to the author process. Independent mathematical review,
full generator/caller composition and physical lowering remain open.
