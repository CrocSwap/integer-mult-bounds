# Three-cube local solubility for every cubic-reader arity

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
Nick Petalas's PR6200 supplies the fixed reader and defect; apoursh's PR6212
supplies the coefficient-ring and general-frame contract. Nick Petalas's
PR6653 supplies the node lemma and the remaining-arity question. The
pure-original-B identity used below belongs to apoursh's PR6215.

## Contract and theorem

Let R=Z[1/2]. Keep all r>=3 children, in their original order and without
changing their interiors:

```
y += a^3
a += b
```

The three streams are distinct registers with arbitrary incoming values
(Y,A,B); their values need not differ. The eager comparator restores
`a -= b` after each child and ends at (Y+rA^3,A,B). The deferred endpoint is
(Y+sum_{i=0}^{r-1}(A+iB)^3,A+rB,B). Put

```
S = r(r-1)/2,   n = 2r-1,
f_r(A,B) = sum_{i=0}^{r-1}(A+iB)^3 - rA^3
         = 3S A^2 B + Sn A B^2 + S^2 B^3.
```

The inherited exact repair problem permits fixed, input-independent
R-weighted cube queries and invertible R-linear source transformations.
There is no output feedback, intermediate observation, nonlinear source
change, output recoding, child fusion or access to child interiors. Sources,
source inverses and query coefficients must be charged separately. An exact
repair would subtract f_r as a polynomial over R. This package proves a
necessary-condition result in finite quotients, not such an exact repair.

**Theorem.** For every integer r>=3 and every odd integer m>1, there exist
integers q_j,u_j,v_j, j=0,1,2, with gcd(u_j,v_j)=1, such that

```
f_r(A,B) = sum_{j=0}^2 q_j(u_j A+v_j B)^3   (mod m)
```

coefficientwise. Each source row (u_j,v_j) extends to a determinant-one
integer matrix. Consequently an appended program with at most three
nonzero weighted cube queries restores the two sources **exactly** and
reproduces the eager output **modulo m**. The coefficients and frames may
depend on r and m but are independent of Y,A,B.

There is also a three-term identity with coefficients and invertible source
frames in Z_p, the p-adic integers, for every odd prime p. This statement
asserts attainability by at most three queries; it is not a local query
minimum.

For operational congruences, incoming values may be arbitrary elements of
R, reduced by R -> R/mR. The polynomial statement avoids any restriction to
finite test inputs. Fractions whose denominators are not invertible modulo
m are not assigned an artificial modular evaluation.

**Consequence.** No proof that solely establishes nonexistence of an
unrestricted three-query representation in a finite odd quotient of R can
show an exact dyadic four-query lower bound for this family. The same is
true of finitely many such congruence tests imposed simultaneously. This
does not rule out odd-prime valuation arguments that constrain one fixed
global rational representation, or additional restrictions on its forms,
weights or schedule.

## Identity integral at the prime 3

Set

```
c  = (3r-1)/4,
w0 = -r(r-1)(r+13) / [6(3r-1)],
w1 = r(r^2-1) / [6(3r-5)],
wc = 16r(r-1)(r-2) / [3(3r-1)(3r-5)].
```

Then the following identity holds over Q:

```
f_r = w0 A^3 + w1(A+B)^3 + wc(A+cB)^3.                 (I)
```

All three weights are nonzero for r>=3, and c>=2, so its three directions
0,1,c are distinct. Here is a derivation using the credited node lemma.
For nodes 0,1,c, that lemma's condition

```
3 e2 = n e1 - 3S
```

becomes (3-n)c=n-3S. Since r>=3, cancellation of r-2 gives c=(3r-1)/4.
The first three coefficient equations are

```
w0+w1+wc = 0,
w1+c*wc = S,
w1+c^2*wc = Sn/3.
```

Subtracting the second from the third and using c(c-1)!=0 gives
`wc=S(n/3-1)/(c(c-1))`, then `w1=S-c*wc` and `w0=-w1-wc`.
Substitution and cancellation give the three displayed weights. For
completeness, each node x satisfies x^3=(1+c)x^2-cx. Thus their weighted
third moment is

```
w1+c^3*wc = (1+c)Sn/3-cS
           = S[n(1+c)/3-c] = S^2,
```

where the last equality is exactly the node condition. This supplies the
B^3 coefficient and proves (I) without a finite-search premise.

Write Z_(3) for the rationals whose reduced denominator is prime to 3.
All coefficients of (I) lie in Z_(3). The factors 3r-1 and 3r-5 are prime
to 3; the remaining factor 3 in each displayed denominator cancels. Indeed,
modulo 3 the w0 numerator r(r-1)(r+13) becomes r(r-1)(r+1), and the w1
numerator is r(r-1)(r+1). Each is a product of three consecutive residue
classes. The wc numerator contains r(r-1)(r-2), with the same property.
The node c has denominator 4. No cancellation claim about other odd primes
is made or needed.

In particular, (I) defines an exact identity over Z_3 and a coefficientwise
identity modulo every power of 3. Its rows have the following
Z_(3)-valued determinant-one completions:

```
H0 = [[1,0],[0,1]],
H1 = [[1,1],[0,1]],
Hc = [[1,c],[0,1]].
```

Their inverses are obtained by negating the upper-right entry. A source
frame may therefore expose each cube and then restore both sources in the
local ring.

## Credited identity integral away from 3

The pure-original-B identity from PR6215 is

```
f_r = (S/9)(3A+rB)^3
      -(S/9)(3A+(r-1)B)^3
      + [S(3S-1)/9] B^3.                              (II)
```

As a rational identity it is valid for every r, including the arities at
which these coefficients fail to be dyadic. Expansion gives A^3 coefficient
zero, A^2 B coefficient 3S, and A B^2 coefficient Sn. Since
`r^3-(r-1)^3=6S+1`, its B^3 coefficient is

```
S(6S+1)/9 + S(3S-1)/9 = S^2.
```

Every coefficient in (II) lies in Z[1/3]. The source rows have
Z[1/3]-valued determinant-one completions

```
K0 = [[3,r],[0,1/3]],
K1 = [[3,r-1],[0,1/3]],
K2 = [[0,1],[-1,0]].
```

These matrices and their inverses are defined over Z_p for every prime
p!=3 and modulo every integer coprime to 3. Thus (II) gives the required
local identity at all odd primes other than 3; (I) supplies the prime 3.
These are exact local identities with rational coefficients whose relevant
prime denominators are absent, not approximations.

## A common elementary-shear word for the local frames

Write

```
U(x) = [[1,x],[0,1]],   L(x) = [[1,0],[x,1]].
```

Their literal actions are `a += x*b` and `b += x*a`, respectively. Each has
determinant one and inverse obtained by negating x. For five coefficients
x0,...,x4, define W(x0,...,x4) by the following **execution order**:

```
U(x0), L(x1), U(x2), L(x3), U(x4).
```

On a column source vector its matrix is therefore
`U(x4)L(x3)U(x2)L(x1)U(x0)`. The same word realizes every local frame above:

```
H_j = W(c_j,0,0,0,0),               (c0,c1,c2)=(0,1,c),
K_j = W(t_j/3,-3,-2/3,1,2),         (t0,t1)=(r,r-1),
K2  = W(1,-1,1,0,0).
```

For the middle line, direct multiplication gives

```
U(2)L(1)U(-2/3)L(-3) = [[3,0],[0,1/3]],
```

and multiplication on the right by U(t/3) gives `[[3,t],[0,1/3]]`.
For the last line, `U(1)L(-1)U(1)=[[0,1],[-1,0]]`. This checks the
execution orientation, not just the individual source directions. All
H-word coefficients are defined modulo a power of 3, and all K-word
coefficients are defined modulo an integer coprime to 3.

## Combining the identities at an arbitrary odd modulus

Fix odd m>1 and write

```
m = m3*m0,   m3=3^v_3(m),   gcd(m0,3)=1.
```

Then gcd(m3,m0)=1. Use the three terms of (I), in their displayed order,
modulo m3; use the three terms of (II), in their displayed order, modulo m0.
When a factor is 1, omit its vacuous component. For each term j, combine
its pair of weights by the Chinese remainder theorem to obtain an integer
representative q_j in `{0,...,m-1}`. Separately combine each of the five
H-word coefficients with the corresponding K-word coefficient, obtaining
integer representatives x_j0,...,x_j4 in the same range. This is a
componentwise CRT operation on rational values whose denominators are
invertible in the component where they are used.

Define the actual integer source frame

```
N_j = W(x_j0,x_j1,x_j2,x_j3,x_j4).
```

Since matrix multiplication commutes with reduction, N_j reduces to H_j
modulo m3 and to K_j modulo m0. It is an actual product of five integer
elementary shears, so it belongs to SL_2(Z), and its inverse is the reversed
word with every coefficient negated. If (u_j,v_j) is its first row, then
gcd(u_j,v_j)=1: any common divisor would divide the determinant 1. Thus
primitive integer source rows and their realizations are produced directly;
no division by a row entry or separate matrix-lifting theorem is required.

The first row of each N_j reduces to the corresponding CRT combination of
the local cube directions. Polynomial operations commute with reduction, so

```
f_r = sum_{j=0}^2 q_j(u_j A+v_j B)^3   in (Z/mZ)[A,B].  (III)
```

Because both sides before reduction have integer coefficients, there is
an integer-coefficient cubic H_{r,m} such that

```
f_r(A,B) - sum_{j=0}^2 q_j(u_j A+v_j B)^3 = m H_{r,m}(A,B). (IV)
```

This is a finite explicit construction of the primitive lifts. Computing
m3 requires only stripping factors of 3, and the remaining preparation
uses rational cancellation, modular inverses and CRT. That preparation is
still work to be charged; no efficient physical backend is asserted.

## Chronology and exact source restoration

Let J be the set of j for which the chosen q_j is nonzero. From the actual
deferred endpoint first apply

```
a -= r*b
```

so that the source pair is exactly (A,B). Then, for each j in J, append

```
(a,b) = N_j(a,b)
y -= q_j*a^3
(a,b) = N_j^-1(a,b)
```

The j-th query reads exactly u_j A+v_j B. Its inverse frame returns both
sources before the next frame. Therefore the full endpoint is exactly

```
(Y+rA^3 + m H_{r,m}(A,B), A, B).                       (V)
```

Sources are restored as exact algebraic expressions, including all dirty
incoming values; only the output comparison is weakened to a congruence.
For arbitrary Y,A,B in R, (V) reduces to the eager endpoint in R/mR.
There is no entry snapshot, initialized source, output feedback or altered
child. Each frame has its displayed algebraic inverse. Each query has a
literal inverse obtained by negating its weight, since its source does not
involve y. Reversing the full event sequence restores the incoming state
exactly, independently of the output congruence.

There are |J|<=3 nonzero query events. Zero residue weights are represented
by zero and their frame/query/inverse blocks are omitted; they are not
counted as nonzero queries. The schedule has one initial shear and at most
three frame/inverse-frame pairs, each pair realized by ten literal shear
slots. Thus at most 31 elementary source shears suffice, with zero shears
omitted. This is neither an exact-three claim for each modulus nor a
source-operation minimum. The explicit shear words use only the two source
registers at the algebraic interface; a physical implementation must still
account for coefficient use and any private storage or restoration.

The same chronology with H_j or K_j and the corresponding rational weights
gives exact output as well as exact sources over the appropriate Z_p.
These local programs can use coefficients outside R. Conversely, the
integer-lift program above uses coefficients in R but generally has only
modular output correctness. Neither statement supplies a global exact
three-query dyadic repair.

## What the modular obstruction consequence does and does not say

Suppose an exact global dyadic three-query program existed. Reducing its
coefficients and source matrices modulo an odd m would yield a program in
the quotient: determinants of GL_2(R) are units in R and remain units under
reduction. Thus nonexistence in a quotient would be a necessary obstruction
to global existence. The theorem proves that this particular nonexistence
condition never occurs for f_r: (III)-(V) provide a valid quotient witness.
Every nontrivial finite quotient of R is covered by an odd modulus. To see
this, intersect its kernel ideal with Z, obtaining dZ. If a/2^k lies in the
kernel, then a lies in that intersection, so the kernel is dR. Removing
factors of 2 from d does not change this ideal. The trivial quotient
provides no nonexistence obstruction either.

For finitely many odd moduli m_1,...,m_k, take their least common multiple
M. The single integer-lift program constructed for M reduces to a witness
for all of them simultaneously. Independently requiring compatibility of
the finite congruences therefore does not create a nonexistence test.

The witnesses depend on the modulus. We do not produce one fixed set of
dyadic coefficients that works for every modulus, a compatible bounded
family of integer lifts, or a global rational point satisfying every
integrality requirement. The exact identities over all Z_p likewise need
not select the same global representation. Therefore valuation arguments
concerning a fixed set of rational forms, an imposed direction pattern,
a height bound, one restricted coefficient family, or another global
arithmetic constraint remain possible. The theorem does not refute the
broader odd-prime-valuation suggestion in PR6653; it closes the narrower
route of unrestricted finite-quotient nonexistence.

## The initially open arity r=15

For r=15, S=105 and

```
f_15 = 315A^2B+3045AB^2+11025B^3.
```

The two rational identities become

```
f_15 = -(245/11)A^3 + 14(A+B)^3 + (91/11)(A+11B)^3,

f_15 = 315(A+5B)^3
       -(35/3)(3A+14B)^3
       +(10990/3)B^3.
```

The second display factors the first cube in (II). Its denominators are
powers of 3, while the first display's denominator 11 is prime to 3.
Neither displayed identity is an exact dyadic certificate. They suffice
for every odd prime and, by the construction above, every odd modulus.
No exact global three-query construction or four-query lower bound at r=15
is asserted here.

## Complete event boundary and remaining obligations

Let Q_k^a price a complete weighted query `y += k*a^3`; let La_k and Lb_k
price `a += k*b` and `b += k*a`, respectively. Every price must include the
specified coefficients, source access, private work, restoration and return
under one matched backend. Zero events are omitted rather than assigned
an unspecified physical charge. For x=(x0,...,x4), the complete price
inventory of its forward frame word is

```
F(x) = La_x0 + Lb_x1 + La_x2 + Lb_x3 + La_x4.
```

The inverse executes the coefficients in reverse order with their signs
negated, with inventory

```
F_inverse(x) = La_-x4 + Lb_-x3 + La_-x2 + Lb_-x1 + La_-x0.
```

These are sums of named elementary events, not primitive unpriced frame
operations. The full appended inventory is

```
I_{r,m} = La_-r + sum_{j in J}[F(x_j) + Q_-qj^a + F_inverse(x_j)].
```

All retained children remain paid. The eager bill is

```
E_r = r Q_1^a + r La_1 + r La_-1 + Omega_eager.
```

The constructed program's bill is

```
D_{r,m} = r Q_1^a + r La_1 + I_{r,m} + Omega_modular.
```

The Omega terms include any remaining coefficient generation, modulus
handling, rational cancellation, modular-inverse/CRT preparation, routing,
precision, storage, dispatch and controller costs not included in the
complete event prices. Those prices and residual terms are unknown, not
zero. If a common modular output contract and matched costs were
established, a cost saving would require

```
I_{r,m} + Omega_modular - Omega_eager < r La_-1.
```

No such inequality or backend is supplied. More fundamentally, modular
output equality does not satisfy the inherited exact-output specification;
this program cannot replace the eager exact program on the strength of a
price comparison. Recovering exact output, implementing the coefficients
and controlling growth or rounding would require additional proofs and
paid operations. No physical multiplier, supplier admission,
selected-assumption discharge, selected-frontier change or new kappa follows.

## Attribution and proof status

Nick Petalas's PR6200 supplies the cubic reader, chronological defect and
repair interface. apoursh's PR6212 supplies the localization and
nonmonic/general-frame contract; its unrestricted dyadic two-query floor is
not changed or used to assert a modular minimum here. apoursh's PR6215
supplies identity (II) and the distinction between an original-B direction
and a temporarily changed register. Nick Petalas's PR6653 supplies the node
lemma used to derive (I), the integer-direction search boundary, and the
remaining-arity question that motivates this restricted obstruction result.
CubeJerry's PR6250 and AAAmirinu's PR6246 retain the equal-step and power-of-two
predecessor credit in that question's lineage. Sricharan Vagvala/theon199's
PR1532, Adam Gall's PR1205 and Hanson Sun's PR1246 retain the quadratic and
linear fixed-reader/paid-repair lineage.

The Chinese remainder theorem, elementary matrix operations, localization
and binary-form decomposition are classical. The contribution
is the displayed 3-integral identity and its combination with the credited
identity to close this finite-quotient obstruction route at the repository's
specific cubic-reader interface. No historical-priority claim is made.
The written identities and explicit frame construction address all r and m in the
stated domains. Finite exact replay corroborates them; it does not establish
the infinite quantifiers by enumeration. Independent code is not independent
human review or formal proof-kernel acceptance.
