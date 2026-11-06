# Sharp four-axis rounding with Gaussian phase covariance

Prepared by @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The native factorization, sharp half-grid witness and correction predicates
come from Nick Petalas's #6574. The new work is the minimal odd-compatible
period, its negation-equivariant matching, the compact quotient, and the
retained caller binding in [CALLER.md](CALLER.md). Exact sources and further
lineage credit are in [SOURCES.json](SOURCES.json) and [NOTICE.md](NOTICE.md).

## 1. Statement and scope

Index sixteen coordinates by four-bit integers, and put

$$
 W_{rs}=(-1)^{\operatorname{popcount}(r\mathbin\&s)},\qquad
 A=W/4,\qquad D_{jj}=(-i)^{\operatorname{popcount}(j)}.
$$

The native four-axis operator is

$$
 U=(1+i)^{-4}\begin{pmatrix}i&1\\1&i\end{pmatrix}^{\otimes4}
   =-DAD.
$$

Indeed, $(1+i)^4=-4$ and
$\operatorname{wt}(r\mathbin\oplus s)=\operatorname{wt}(r)+
\operatorname{wt}(s)-2\operatorname{wt}(r\mathbin\&s)$, which gives
the displayed factorization entry by entry.

**Theorem.** The finite certificate in this package defines a bijection
$F:\mathbb Z[i]^{16}\to\mathbb Z[i]^{16}$, with a literal inverse,
such that for all Gaussian integer vectors $x,y$:

$$
\begin{split}
 F(0)&=0,\qquad F(ix)=iF(x),\qquad \sum_j F(x)_j=\sum_j x_j,\\
 \|F(x)-Ux\|_2&\le\sqrt8,\qquad
 \|F^{-1}(y)-U^*y\|_2\le\sqrt8.
\end{split}
$$

Both error constants are sharp among all integer-output maps. For this
certificate, every complex coordinate error is at most $3\sqrt2/4$
forward and $5\sqrt2/4$ inverse. The corresponding statements on a grid
$h\mathbb Z[i]$, for $h>0$, follow by scaling and multiply each
error by $h$.

The real map used by $F$ has a full-rank affine period with exactly
2,048 classes. This is the smallest possible period index for any odd map
approximating $A$ in the affine-period sense defined below, irrespective
of its error bound or bijectivity. The resulting native period has index
$2^{22}=4,194,304$, also minimal among globally odd native maps with such
a period, including maps with coupled real/imaginary corrections.
These statements concern quotient indices, not minimum table bytes, lookup
costs, or arbitrary nonperiodic algorithms.

The particular $F$ does **not** satisfy $F^4=I$. A checked exact
counterexample appears in Section 8. The proof is a scoped mathematical
argument with a finite certificate checked by exact Python arithmetic; it
is not a formal proof-kernel verification or a multiplication theorem.

## 2. Why the predecessor quotient cannot be odd

The Walsh identities give $A^2=I$, and $A$ is orthogonal. Define

$$
 L=\{z\in\mathbb Z^{16}:Az\in\mathbb Z^{16}\}.
$$

For an integer vector $z$, let
$T=\sum_s z_s$ and $B_j=\sum_{s:\operatorname{bit}_j(s)=1}z_s$.
Expansion of the signs modulo four gives

$$
 (Wz)_r\equiv T-2\sum_j\operatorname{bit}_j(r)B_j\pmod4.
$$

Consequently $z\in L$ exactly when $T=0\pmod4$ and all four
$B_j=0\pmod2$. The homomorphism
$z\mapsto(T\bmod4,B_0\bmod2,\ldots,B_3\bmod2)$ is onto:
$e_0$ supplies the first factor and $e_{2^j}-e_0$ supplies each
binary factor. Thus

$$
 \mathbb Z^{16}/L\simeq\mathbb Z/4\oplus(\mathbb Z/2)^4,
 \qquad [\mathbb Z^{16}:L]=64.
$$

#6574 uses a fixed correction on each of these 64 classes. Consider any
map $R(z)=(Wz+e(Wz\bmod4))/4$ of that form. The inputs $2e_0$
and $-2e_0$ have the same residue $(2,\ldots,2)$. Oddness would
therefore force its correction to satisfy $e=-e$, hence $e=0$.
But zero cannot cancel that residue modulo four. This rules out oddness in
the fixed 64-class architecture. It does not rule out refinement, extra
state, or a different architecture. The construction below refines it.

## 3. A compact quotient of index 2,048

Let $H=(7,11,13,14,15)$ and

$$
 Q=\mathbb Z/8\oplus(\mathbb Z/4)^4.
$$

Define the source homomorphism $\alpha:\mathbb Z^{16}\to Q$ by

$$
 \alpha_0(z)=4z_7-T\pmod8,\qquad
 \alpha_{j+1}(z)=2z_{H_{j+1}}-B_j\pmod4\quad(0\le j<4).
$$

For $a=(a_0,\ldots,a_4)\in Q$, using canonical nonnegative residues,
the vector

$$
 r(a)=\Bigl(\sum_{j=1}^4a_j-a_0\Bigr)e_0
       -\sum_{j=0}^3a_{j+1}e_{2^j}
$$

has $\alpha(r(a))=a$. Hence $\alpha$ is onto. Write
$\Lambda=\ker\alpha$. It has index 2,048, and $\Lambda\subset L$:
$\alpha_0(z)=0$ forces $T=0\pmod4$, while the other equations
force all $B_j$ even.

The output quotient is different. For $v=Wy$, define

$$
 \beta_0(y)=v_7-4y_0\pmod8,\qquad
 \beta_{j+1}(y)=\frac{v_{H_{j+1}}-v_7}{2}+2y_{2^j}\pmod4.
$$

Each numerator in the half difference is even for every integer $y$,
so this is an integer homomorphism. It is onto. One explicit section is
as follows: if the final four coordinates of a key are $(a,b,c,d)$, put

$$
 (t_0,t_1,t_2,t_3)=
 (2a+c+3d,\ 3b+3d,\ a+2c+3d,\ d)\pmod4,
$$

set $y_{2^j}=t_j$, set
$y_0=5(a_0+t_0+t_1+t_2-t_3)\pmod8$, and set all other
coordinates to zero. Substitution gives $\beta(y)=a$.

For $z\in L$ and $y=Az$, the unreduced expressions satisfy

$$
 \beta_0(y)=4z_7-T,\qquad
 \beta_{j+1}(y)=2z_{H_{j+1}}-B_j-(4z_7-T)/2
$$

with the respective moduli understood. Thus $A\Lambda\subset\ker\beta$.
Since $|\det A|=1$, both lattices have index 2,048, giving

$$
 A\Lambda=\ker\beta.
$$

It follows that $\alpha$ classifies the source cosets and $\beta$
classifies the target cosets. The target table must use $\beta$;
substituting the source classifier is not a justified inverse.

### Independent lattice normal forms

The checker reconstructs lattice bases without using these quotient formulas.
Let $u_0=4e_0$, $u_{j+1}=2(e_{2^j}-e_0)$, and, for
$\operatorname{wt}(s)\ge2$, let

$$
 k_s=e_s+(\operatorname{wt}(s)-1)e_0
        -\sum_{j:\operatorname{bit}_j(s)=1}e_{2^j}.
$$

The five $u$'s followed by the eleven $k$'s form an integral basis
of $L$. For each $s\in H$, put
$v_s=k_s-\sum_{t\subset s,\operatorname{wt}(t)=2}k_t$.
A basis matrix $M$ for $\Lambda$ has columns

$$
 (u_i+v_{H_i})_{i=0}^4,\quad
 (k_s)_{\operatorname{wt}(s)=2},\quad
 (2v_s)_{s\in H}.
$$

Replacing the five high-weight $k_s$'s by $v_s$'s is an integral
unimodular column change. Relative to the resulting basis of $L$, the
five replacements $(u_i,v_{H_i})\mapsto(u_i+v_{H_i},2v_{H_i})$
each have determinant two. Thus $|\det M|=64\cdot2^5=2048$.
Direct substitution gives $\alpha(M)=0$, so the index calculation
also proves that these columns span exactly $\Lambda$.

The checker obtains $|\det M|=|\det(AM)|=2,048$, verifies
$\alpha(M)=0$, $\beta(AM)=0$, and computes the inverse matrices
over the rationals. Both inverses become integral after multiplication by
eight. The sixteen-coordinate residues $8M^{-1}z\bmod8$ and
$8(AM)^{-1}y\bmod8$ independently classify all 2,048 representatives
on each side. This is a separate normal-form check of the compact quotient.

## 4. The finite negation-equivariant matching

Negation on $Q$ is coordinatewise. It has 32 fixed keys, with
$a_0\in\{0,4\}$ and $a_j\in\{0,2\}$ for $j>0$, and
$(2048-32)/2=1008$ free pairs. The certificate contains one row for
each free pair, using the lexicographically smaller key. Each row supplies
an integer correction $e(a)$; define $e(-a)=-e(a)$. Set $e=0$
at every fixed key.

For a source key $a$, compute

$$
 y(a)=\frac{Wr(a)+e(a)}4,\qquad p(a)=\beta(y(a)).
$$

The finite certificate checker verifies all of the following:

1. Every key occurs exactly once; every correction has sixteen integer entries.
2. $Wr(a)+e(a)$ is divisible by four coordinatewise.
3. $\|e(a)\|_2^2\le64$ and $\sum_jD_{jj}e(a)_j=0$.
4. $e(-a)=-e(a)$, including zero at the 32 fixed keys.
5. The 2,048 target keys $p(a)$ are distinct and exhaust $Q$.
6. The inverse offsets $f(p(a))=-We(a)/4$ are integers, have squared
   norm at most 64, and satisfy $\sum_jD_{jj}f(p(a))_j=0$.
7. All forward correction coordinates have magnitude at most 3; all inverse
   correction coordinates have magnitude at most 5. Both maxima are attained.

The fixed classes require no search: $Ar(a)$ is integral and their
target keys are
$(a_0,a_1-a_0/2,\ldots,a_4-a_0/2)$ with the displayed moduli.
This permutes the 32 fixed keys. The remaining rows were obtained by a
finite bipartite matching on free negation orbits using the predecessor's
admissible correction candidates. The witness is retained directly, so replay
needs no matching solver, search transcript or assertion of search completeness.
Its correctness depends only on the checked predicates.

## 5. The all-integer real map and its inverse

Define

$$
 R(z)=\frac{Wz+e(\alpha(z))}{4}.
$$

If $z=r(a)+\lambda$ with $\lambda\in\Lambda$, then
$R(z)=y(a)+A\lambda$. This is an integer vector, and its target key
is $p(a)$. On each source coset the map is the affine lattice bijection
$\lambda\mapsto A\lambda$ from $\Lambda$ onto $A\Lambda$.
The finite permutation of cosets therefore proves that $R$ is bijective
on **all** integer vectors, not merely on the tested representatives.

The literal inverse is

$$
 R^{-1}(y)=\frac{Wy+f(\beta(y))}{4},\qquad f(p(a))=-We(a)/4.
$$

Indeed, if $y=Az+e(a)/4$, then
$Ay=z+Ae(a)/4$, and $f(p(a))=-Ae(a)$ cancels the latter term.
This also proves inverse integrality throughout each target coset.
Orthogonality gives $\|f\|_2=\|e\|_2$, so both real errors are at
most 2. Linearity of $\alpha$ and the opposite corrections imply
$R(-z)=-R(z)$. Its inverse is odd as well. At the zero class the
correction vanishes, so $R(0)=0$.

## 6. Native phase, sum, inverse and sharp error

Extend the real map componentwise:
$R_{\mathbb C}(a+ib)=R(a)+iR(b)$. Then define

$$
 F(x)=-D R_{\mathbb C}(Dx),\qquad
 F^{-1}(y)=D^{-1}R_{\mathbb C}^{-1}(-D^{-1}y).
$$

These are literal inverse bijections of the Gaussian lattice. Oddness of
$R$ is precisely what makes this componentwise extension commute with
global multiplication by $i$:
$R_{\mathbb C}(i(a+ib))=R(-b)+iR(a)=iR_{\mathbb C}(a+ib)$.
Diagonal quarter rotations commute with global $i$, so both $F$
and its inverse have Gaussian phase covariance. Iterating this identity also
gives covariance under the other Gaussian units.

The ideal $U$ is unitary and preserves the sum because each one-axis
matrix has those properties. The forward error is a diagonal rotation of
$(e_{\rm re}+ie_{\rm im})/4$. Its sum is zero by the two real
weighted-sum checks, and its squared norm is at most
$(64+64)/16=8$. For the inverse, use the offsets $f$ and
$D^{-1}$; the required weighted sum is the complex conjugate of the
checked weighted sum for each real offset. The same error bound follows.
The coordinate bounds follow from
$\sqrt{3^2+3^2}/4=3\sqrt2/4$ and
$\sqrt{5^2+5^2}/4=5\sqrt2/4$.

For sharpness, take $x=(2+2i)e_0$. Every coordinate of $Ux$ has
both real and imaginary part equal to a signed half-integer. Every Gaussian
integer output therefore has squared distance at least $1/2$ in each
of sixteen coordinates, hence at least 8 in total. The same argument applies
to $U^*x$. Our upper bounds attain these unavoidable lower bounds.

For independent sixteen-point fibers in an $N$-coordinate field, squared
errors add, giving the sharp uniform bound $h\sqrt{N/2}$. The retained
caller proof in [CALLER.md](CALLER.md) uses the stronger coordinate constants
to lower its grid request by two fractional bits at exactly $f=4$.

## 7. Minimal affine-period indices

An **affine period lattice** for an integer-output map $R$ relative to
$A$ is a full-rank sublattice $\Gamma\subset\mathbb Z^{16}$
such that

$$
 R(z+\lambda)=R(z)+A\lambda
 \quad\text{for every }z\in\mathbb Z^{16},\ \lambda\in\Gamma.
$$

Necessarily $\Gamma\subset L$. Suppose $R$ is odd. If
$\lambda\in\Gamma\cap2\mathbb Z^{16}$, apply the period identity
at $-\lambda/2$ and use oddness:
$2R(\lambda/2)=A\lambda$. Thus $A\lambda$ is even and
$\lambda/2\in L$, so

$$
 \Gamma\cap2\mathbb Z^{16}\subset2L.
$$

In $V=L/2L$, the subspace
$E=(L\cap2\mathbb Z^{16})/2L$ is isomorphic to
$(\mathbb Z^{16}/L)[2]$: send the class of $z$, with $2z\in L$,
to $2z+2L$. From the quotient in Section 2, $\dim E=5$, while
$\dim V=16$. The image
$J=(\Gamma+2L)/2L$ meets $E$ trivially, so $\dim J\le11$.
Consequently

$$
 [L:\Gamma]\ge[L:\Gamma+2L]\ge2^5,\qquad
 [\mathbb Z^{16}:\Gamma]\ge64\cdot32=2048.
$$

This argument does not assume $2L\subset\Gamma$, does not use a
radius bound, and does not require bijectivity. The period $\Lambda$
of the constructed odd map attains the bound. For a bijective odd map,
applying the same reasoning to the inverse also forces
$\lambda$ even if and only if $A\lambda$ is even on its period.
The reconstructed bases independently check this two-sided condition.

For the native extension, regard $Z=\mathbb Z[i]^{16}$ as a rank-32
integer lattice. Its integrality lattice is

$$
 L_U=\{x\in Z:Ux\in Z\}=D^{-1}(L+iL),
 \qquad Z/L_U\simeq(\mathbb Z/4\oplus(\mathbb Z/2)^4)^2.
$$

It has index $2^{12}$, and its even-class subspace
$(L_U\cap2Z)/2L_U$ has dimension 10. Any globally odd native map
with full-rank affine period $\Gamma$ satisfies
$\Gamma\cap2Z\subset2L_U$, by the same half-period argument.
Its image in $L_U/2L_U$, a 32-dimensional vector space, has dimension
at most 22. Thus

$$
 [Z:\Gamma]\ge2^{12}\,2^{10}=2^{22}=4,194,304.
$$

Gaussian phase covariance implies global oddness, so this includes coupled
real/imaginary correction tables. The constructed native map has period
$D^{-1}(\Lambda+i\Lambda)$, of index $2048^2=2^{22}$, and the
appropriate affine image under $U$. It attains this native bound while
sharing the same real correction table between both components. Nothing in
this proof gives a memory lower bound: separability, table compression,
algebraic evaluation and nonperiodic schemes are separate questions.

## 8. Exact fourth-power failure and verification limits

The ideal operator has $U^2=J$, where $J$ complements all four
coordinate bits, and $U^4=I$. The certified rounded map instead has

$$
 F^4(e_0)=e_0-ie_1-ie_4-ie_7-e_{10}+e_{12}+2ie_{13}+ie_{14}\ne e_0.
$$

The checker computes and retains this exact vector. It proves failure for
this particular certificate, not impossibility for a different sharp
phase-covariant map. The retained two-/three-call ports require the literal
inverse, so their exact dirty-bank return does not require the failed identity.

`verify.py` checks all real source and target classes, rational period normal
forms, the complete matching, literal real round trips and all finite error
and sum predicates. A separate native-coefficient oracle checks 4,096 paired
complex fixtures, both sharp witnesses, and signed large-word fixtures. It
does not enumerate all $2048^2$ complex class pairs; the componentwise
proof establishes their universal coverage. Failure controls preserve local
correction admissibility while breaking negation or creating a target collision,
and also reject a corrupted period, wrong native phase, a false smaller radius,
forward-as-inverse substitution, and malformed executable inputs.

The mathematical formulas are defined on every integer vector. `kernel.py`
places a 4,096-bit-per-component guard on its public reference entry point;
4,090-bit fixtures leave room for intermediate round-trip growth. This guard
is not a mathematical restriction of the theorem. The retained caller has its
own explicitly checked signed-word interface. Neither replay establishes
norm-inward rounding, a nearest-output rule, graph flatness, a Boolean/tape
lowering, complete compiler costs, or any of the selected multiplier's five
inherited assumptions.
