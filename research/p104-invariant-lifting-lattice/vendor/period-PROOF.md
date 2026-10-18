# The full translation group of the integer lifting word

Use Gaussian integers and componentwise Euclidean floor. Define

```
d = a-b; s = b+floor(d/2); d = i*d;
b' = s-floor(d/2); a' = b'+d.
```

Write this pair map as P(a,b). Its ideal complex-linear map is
C(a,b)=((a+b+i(a-b))/2,(a+b-i(a-b))/2).
Let L_r on 2^r addresses apply P on address bits 0 through r-1, and let
U_j be its first j ideal stages. L_0=U_0=I. These are the literal word and
conventions of Tekalign's PR3025/3033 and Nick Petalas's PR3035.

Define Gamma_r as the integer shifts z for which every stage j satisfies

```
(U_j z)[a] - (U_j z)[a xor 2^j] in 2 Z[i]
```

on every pair with address bit j zero. Earlier conditions make U_j z
integral, so each subsequent condition is well defined.

## Pair rigidity

For fixed c,d in Z[i], the increment P(a+c,b+d)-P(a,b) is independent of
a,b if and only if c-d is in 2 Z[i]. In that case it equals C(c,d).

Proof. Write a-b=p+iq and let h(t) be the Euclidean residue t mod 2.
Direct substitution gives, at both output coordinates,

```
P(a,b)-C(a,b) = (h(q)-h(p)) (1-i)/2.
```

The change of this correction under c-d=u+iv is proportional to
`h(q+v)-h(q)-h(p+u)+h(p)`. If u is odd, varying p between 0 and 1 with
q fixed changes that expression by 2. If v is odd, varying q does the
same. Hence a constant increment requires u,v even. Conversely, even
u,v leave the correction unchanged and give the asserted increment.

Two other exact properties will matter. The output difference is
`a'-b'=i(a-b)`. Also P is a bijection. Given outputs (A,B), recover
`d=-i(A-B)`, `s=B+floor((A-B)/2)`, `b=s-floor(d/2)`, and `a=b+d`.
Equivalently, the same lifting recipe with rotation -i is its inverse.

## Theorem

For every integer r>=0 and z in Z[i]^(2^r), the following are equivalent:

1. L_r(x+z)-L_r(x) is independent of x on all Gaussian integer inputs.
2. z is in Gamma_r.

The constant increment is necessarily U_r z. Thus Gamma_r is exactly
the full group of constant translations, including those whose increment
was not specified in advance.

Proof by induction on r. The assertion at r=0 is the identity map.
Split inputs by their highest address bit as x=(x_0,x_1), and split
z=(z_0,z_1) in the same way. Before the last stage, the two halves are
A=L_(r-1)(x_0) and B=L_(r-1)(x_1). Put

```
F(x_0) = L_(r-1)(x_0+z_0)-L_(r-1)(x_0),
G(x_1) = L_(r-1)(x_1+z_1)-L_(r-1)(x_1).
```

Suppose the full output increment is constant. For each last-stage pair,
subtract its two output increments. The output-difference identity gives
`i(F(x_0)[a]-G(x_1)[a])`, a constant. The inputs x_0 and x_1 vary
independently. Fixing either one therefore proves that every coordinate
of F and of G is constant. The induction hypothesis now gives
z_0,z_1 in Gamma_(r-1) and F=U_(r-1)z_0, G=U_(r-1)z_1.

Every lower lifting stage is bijective, so A and B independently range
over all Gaussian integer arrays. Pair rigidity consequently forces
F[a]-G[a] in 2 Z[i] for every address a. These are exactly the final
prefix conditions defining Gamma_r. Pair rigidity also identifies the
last increment as C(F[a],G[a]), hence the full increment as U_r z.

Conversely, if z is in Gamma_r, its two halves satisfy the lower prefix
conditions. Induction gives their ideal constant increments. The final
prefix conditions let pair rigidity propagate these increments through
the last stage. This proves sufficiency and the claimed value.

## Inverse and wrappers

L_r is bijective. Its inverse has a constant translation v with increment
z precisely when L_r has translation z with increment v: substitute
y=L_r(x) in either identity. The theorem therefore makes the full inverse
translation group exactly U_r Gamma_r. It can differ from Gamma_r.

For Gaussian monomial maps A,R, meaning permutations with Gaussian-unit
multipliers and hence automorphisms of the integer lattice, the wrapped
word A L_r R has full input
translation group R^-1 Gamma_r and output increments A U_r Gamma_r.
The inverse group is A U_r Gamma_r. For independent blocks take the direct
product of their groups. These statements use bijectivity of A and R.

## Exact consequence and its boundary

PR3035 computes [Z^256:Gamma_7]=2^343, with quotient factors
`(Z/16)^3 x (Z/8)^22 x (Z/4)^70 x (Z/2)^125`.
The retained, byte-authenticated modular index checker reruns that finite
calculation here. The theorem upgrades its sufficient lattice to the
full translation group. The same index holds for U_7 Gamma_7, since each
ideal pair has complex determinant i and real determinant 1. Four
independent blocks have index 2^1372.

In particular, consider a residue split based on a finite-index lattice
Lambda, with one representative s(x) per coset, satisfying

```
L_7(x) = U_7(x-s(x)) + F(s(x)).
```

For z in Lambda, s(x+z)=s(x). Subtraction forces
L_7(x+z)-L_7(x)=U_7 z for every x. Thus Lambda is contained in Gamma_7
and its index is at least 2^343. PR3035 attains that index. Its 343-bit
coset domain is therefore optimal within this exact translation-lattice
contract for this fixed lifting word. No coarser translation lattice can
further reduce it.

This is not a circuit-size, runtime, storage or general nonlinear-state
lower bound. It does not restrict different lifting words, noncoset
encodings, coupled consumers or approximate interfaces. It does not
price the reducer, wide backend, dirty restoration or the complete
supplier. No multiplication exponent follows from the theorem alone.
