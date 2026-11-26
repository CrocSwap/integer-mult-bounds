# Full-rate affine factorization from a characteristic-two formula

## 1. Cyclic affine factorizations

Let `K` be a commutative characteristic-two algebra and let the query
variables commute. A cyclic length-d factorization of a scalar polynomial
`f` consists of square affine pencils `A_0,...,A_(d-1)` of common size r
such that **every cyclic rotation** of their ordered product equals
`f I_r`. Products act in temporal order: starting at grade i means
`A_(i+d-1) ... A_i`, with indices modulo d.

An affine scalar leaf has length one and size one. Constants are retained
as length-zero scalars. For a positive required length d, a constant a has
the cyclic factorization `(a,I,...,I)` of size one. Padding any positive
cyclic factorization with identity factors preserves the property. These
conventions handle zero constants and unequal-degree sums without assuming
that any factor is invertible.

Use a formula's **syntactic degree**: constants have degree zero, affine
nonconstant leaves degree one, addition takes the maximum, and multiplication
takes the sum. Cancellation is not used to lower this degree. Prescribed
larger degree budgets can also be used, padding with identities. All budgets
below are at most a fixed D.

## 2. Multiplication costs no extra row factor

If f and g have cyclic factorizations of lengths a,b and sizes r,s, take
the a factors `A_i tensor I_s`, followed by the b factors `I_r tensor B_j`.
This is a length-(a+b), size-rs cyclic factorization of fg. To verify a
rotation starting inside one list, commute the other list past it: the
other list multiplies to its scalar times the identity, and the split list
rejoins in one of its valid cyclic rotations. Factors from the two tensor
coordinates commute. If one input is constant, multiply one factor of the
other list by that scalar. If both are constant, retain their product as a
constant. These operations also work when a scalar polynomial vanishes.

## 3. Addition costs a factor d in the row dimension

Pad the two cyclic factorizations to common length d=max(a,b)>=1. Write
`d=2^v c` with c odd, and suppose K contains a root xi satisfying the
primitive-c cyclotomic polynomial. For c=1 set xi=1.

On the graded module `K^d tensor K^r`, define

\[
 L_A(e_i\otimes x)=e_{i+1\bmod d}\otimes A_i x,
 \qquad Z_A(e_i\otimes x)=\xi^i e_i\otimes x.
\]

Then `L_A^d=f I`, `Z_A L_A=xi L_A Z_A`, and `Z_A^d=I`.
Define `L_B` analogously. On their tensor product put

\[
 X=L_A\otimes I,\qquad Y=Z_A\otimes L_B,\qquad L=X+Y.
\]

Here `YX=xi XY`. The Gaussian-binomial identity gives
`(X+Y)^c=X^c+Y^c`: its mixed coefficients vanish at a primitive c-th root.
This identity holds in `Z[xi]` and after specialization; no division by c
inside K is needed. The two resulting powers commute. Frobenius in
characteristic two now gives

\[
 L^d=(X^c+Y^c)^{2^v}=X^d+Y^d=(f+g)I.             \tag{FL1}
\]

This is the critical characteristic-two step. It does **not** ask for a
primitive even-order root, which would be unavailable in a field of this
characteristic.

Grade the tensor product by the sum of its two cyclic grades modulo d.
Every total-grade space has dimension `d r s`; both X and Y raise total
grade by one. Restricting L between successive total-grade spaces therefore
gives d square affine pencils of size `d r s`. Equation (FL1) gives every
cyclic product, so this is a cyclic length-d factorization of f+g.

## 4. The formula lemma

**Lemma FL.** A commutative arithmetic formula of syntactic degree at most
D>=1, with S addition gates, has a cyclic factorization into D affine
pencils on at most `D^S` independent rows, over an explicit finite extension
of its coefficient algebra containing primitive roots of every odd order
at most D. A smaller final length is padded to D.

**Proof.** Induct using Sections 1--3. A multiplication multiplies row
dimensions. An addition of positive degree d multiplies them by d; a
constant addition does not enlarge them. Hence the final size is the
product of these positive d values, at most `D^S`. The construction retains
the cyclic property even for identically zero intermediate polynomials.
Every product equals the scalar formula value times the **whole identity**.
Thus every row carries an arbitrary independent input. No selected-output
or zero-workspace interpretation is used. QED.

## 5. An explicit syntactic-degree-D formula for the count predictor

Work over `F4` and treat the two powers of each order-three query as two
formal commuting variables. For a fixed shift beta, let `I_(j,b)` be the
source affine indicator for shifted digit b in `{0,1,2}`. In characteristic
two the local generating function becomes

\[
 (1+T)^{b_j}=1+I_{j,1}T+I_{j,2}T^2.                    \tag{FL2}
\]

This is an identity at every allowed spectral tuple; its right side is
the formal multivariate representation used to construct the predictor.
Pad the list of m factors with constant ones to `m0=2^ceil(log2 m)`.
For a balanced interval I define the coefficient formula

\[
 F_{I,h}=[T^h]\prod_{j\in I}(1+I_{j,1}T+I_{j,2}T^2).
\]

At a leaf the coefficients are 1, `I_(j,1)`, `I_(j,2)`, then zero. At an
internal node use the genuine formula, with copied subexpressions,

\[
 F_{I,h}=\sum_{a=0}^h F_{I_L,a}F_{I_R,h-a}.             \tag{FL3}
\]

Its syntactic query degree is at most h: a coefficient of T-degree one
or two at a leaf has query degree at most its T-degree, and the displayed
degree budgets add under products. This avoids interpolation formulas whose
high-degree cancellations would not control the factor length.

Retain only `h<=D`. If `T_r` bounds the number of nodes in any coefficient
formula after r balanced levels, then
`T_r<=2(D+1)T_(r-1)+2D+1<=4(D+1)T_(r-1)` with `T_0>=1`.
The source multiplication by the fixed series `(1+T)^(-u)`, followed by
the final expression
`omega^(u-sum_j beta_j) sum_(h<=D)(omega-1)^h L_h`, adds only a polynomial
in D number of copies and scalar operations. Retain the displayed scalar
prefactor from the source predictor; it is absorbed into one affine factor
and changes neither the syntactic degree nor the row width. One explicit
loose bound for the
total formula size is

\[
 S_m\le[8(D+1)]^{\lceil\log_2m\rceil+3}.               \tag{FL4}
\]

Its syntactic degree is at most D. Its scalar coefficients lie in `F4`:
the generalized binomial coefficients of `(1+T)^(-u)` are reduced modulo
two. They can be generated by integer arithmetic in time polynomial in
m and D. The tree shape and assigned degree budgets can be chosen
independently of beta, so all shifts receive factors of a common size.
Constant zero subtrees are retained or represented by a zero factor, rather
than invoking an unproved nonvanishing assumption.

For the constant-tail window `D=6 ceil(sqrt m)`, (FL4) gives

\[
 S_m=2^{O((\log(m+2))^2)},\qquad
 r_m\le D^{S_m}=2^{\,2^{O((\log(m+2))^2)}}.             \tag{FL5}
\]

The D pencils on this whole row module multiply to `P_beta I_(r_m)`.
Direct-sum them over all `3^m` shifts and duplicate by 32. The resulting
predictor has `R=32*3^m*r_m` independent rows, still satisfies (FL5), and
takes **D** shared pencil stages. Every pencil is affine in the individual
query powers. This is a full-rate formula construction, not the
single-output branching-program interface.
