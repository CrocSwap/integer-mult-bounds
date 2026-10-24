# Radical reduction for invertible right-vector targets

Let `K` be a field. Let `R = R_1 x ... x R_k`, with `1 <= k < infinity`,
where each `R_i` is an associative unital `K`-algebra whose non-units form
a proper two-sided ideal `J_i`. This is the local-algebra hypothesis used
by Nick Petalas's #4276. Put `J = product J_i` and `D = R/J`. Each
`D_i = R_i/J_i` is a division algebra with the induced central copy of `K`.
No commutativity, finite-dimensionality or nilpotence hypothesis is needed.

Use the retained two-role alphabet

```text
P(u,y) = I + u y^T,    u in R^2, y in K^2,
free maps GL_2(K), usable anywhere,
delta_R(M) = min_{T in GL_2(K)} dim_K ((MT-I)K^2).
```

The cost is the least number of paid factors. A bar denotes reduction
modulo `J`. The target `M` is assumed invertible throughout.

## The result

```text
cost_R(M) <= 2  iff  cost_D(Mbar) <= 2,
cost_R(M) = max(delta_R(M), cost_D(Mbar)) <= 3.
```

Thus local radicals cannot create or remove a three-factor obstruction
on invertible targets. They can increase a zero- or one-factor residue
cost, and `delta_R` measures precisely that remaining increase.

For finite `K` of size `q`, every invertible target costs at most two when
`k <= q`. For each fixed product with `k >= q+1`, there is an invertible
target of cost three and `delta_R = 2`. For infinite `K`, every invertible
target in a finite product costs at most two. The finite-field component
threshold therefore extends #4334 from field products to these local
products, including noncommutative local algebras.

## 1. Units and the common pivot

An element of `R_i` is a unit exactly when its image in `D_i` is nonzero.
Indeed, the zero coset is `J_i`, the set of non-units by hypothesis. The
quotient is a division algebra since every nonzero coset has a unit
representative. Units in a finite product are exactly the tuples of units.

For any invertible `N` over `R`, the first row `(A,B)` is right unimodular.
Writing `(x,z)^T` for the first column of `N^{-1}` gives `Ax+Bz=1`.
If `B=AC`, this becomes `A(x+Cz)=1`. In each component a non-unit `A_i`
would make the left side belong to the proper ideal `J_i`. Consequently
`A` must be a unit. Conversely, a unit `A` always gives `B in AR`.

By #4276, Theorem B, two paid factors suffice exactly when some
`G,H in GL_2(K)` make `N=GMH` satisfy `N12 in N11 R`. The preceding
paragraph reduces this, on invertible targets, to `N11` being a unit.
Every nonzero `K` row `phi` can be the first row of `G`, and every nonzero
`K` column `t` can be the first column of `H`. Therefore

```text
cost_R(M) <= 2
iff some common nonzero phi,t over K make phi M_i t a unit for every i
iff some common nonzero phi,t over K make phi Mbar_i t nonzero for every i
iff cost_D(Mbar) <= 2.
```

The same argument applies to `D`, since a division algebra is local with
zero non-unit ideal. This proves radical invariance of the two-factor set.
It does not assume componentwise free maps or componentwise right vectors.

## 2. Three paid factors always suffice

This extends ToikY's #4334, Section 3, with the order of every product kept
as written. Write `M=[[a,b],[c,d]]`. In each component its second column
is left unimodular. If `d_i` is a non-unit, then `b_i` is a unit, since
otherwise both entries and all their left linear combinations lie in
`J_i`, contradicting the second row of `M_i^{-1}` applied to that column.

Choose the element `r in R` by `r_i=0` if `d_i` is a unit and `r_i=1`
otherwise. Set

```text
D0 = d-rb,
f = D0^{-1}(c-ra),
e = a-bf.
```

Each `D0_i` is a unit. In the second case its residue is `-bbar_i != 0`;
in the first case it is `d_i`. Hence the inverse in the formula exists.
Direct multiplication, without interchanging any ring factors, gives

```text
M = [[1,0],[r,1]] [[1,b],[0,D0]] [[e,0],[f,1]]
  = P((0,r)^T,e1) P((b,D0-1)^T,e2) P((e-1,f)^T,e1).
```

The four entries of this product are `e+bf=a`, `b`,
`r(e+bf)+D0 f=ra+c-ra=c`, and `rb+D0=d`. This uses three allowed factors
with the common right-vector sequence `e1,e2,e1` and no free map.
The componentwise coefficient choice belongs to the allowed left vector.
It does not make the right vectors or free maps componentwise.

## 3. The exact cost formula

By the predecessor column bound and quotient functoriality,

```text
cost_R(M) >= delta_R(M),
cost_R(M) >= cost_D(Mbar).
```

Both costs are at most three by Section 2. If `cost_D(Mbar)=3`, these
bounds force `cost_R(M)=3`, while `delta_R(M)<=2`. Otherwise Section 1
gives `cost_R(M)<=2`. Theorem A of #4276 gives exact cost `delta_R`
when `delta_R<=1`. If `delta_R=2`, the column bound forces cost two.
Thus `cost_R=delta_R` in this second case, and the quotient lower bound
also gives `cost_D(Mbar)<=delta_R`. The stated maximum formula follows.

For example, over the single local algebra `F2[e]/e^2`, the targets
`diag(1+e,1)` and `diag(1+e,1+e)` reduce to the free identity but cost
one and two respectively. For the first, `T=I` gives dimension one and
the target is not free. For the second, a binary kernel vector `v` of
`(1+e)T-I` must satisfy both `(T-I)v=0` and `Tv=0`, hence `v=0`.
So every free endpoint gives dimension two. The exact formula applies.

## 4. The sharp component threshold

Fix a nonzero `t in K^2`. Each `Mbar_i t` is nonzero in `D_i^2`.
At most one projective `K` row can annihilate it. If two distinct
projective rows did so, they would form a `K` basis of the row space,
forcing both entries of this vector to vanish. For finite `K`, there
are `q+1` projective rows. When `k<=q` some row is not forbidden.
For infinite `K`, a finite union of these singleton forbidden sets
also leaves a row. Section 1 supplies the two-factor word in each case.

For sharpness when `K` is finite and `k>=q+1`, take the `q+1` scalar
matrices in `GL_2(K)` constructed in #4334, Section 4, from the
projective representatives of a quadratic extension. Place these in
the first `q+1` components, using the central copy of `K` in each `R_i`,
and put identities in extra components. For every nonzero `phi,t`,
one of these component pivots is literally zero, so it is not a unit.
Section 1 excludes two factors; Section 2 supplies three. Theorem A
then forces `delta_R=2`. The extension-field construction and its
projective covering property are credited to #4334, not reproved here.

## Scope and credit

This is a scoped algebraic proof in the formal alphabet. It supplies no
native implementation, frame conversion, routing, precision, restoration,
stock bound, supplier admission or multiplication theorem. These physical
costs remain unknown. Singular targets are excluded. Independent human
and formal proof-kernel review are unclaimed.

Produced by Nick Petalas. The new result is the local-product reduction
and exact lift formula. ToikY's #4334 supplies the field-product result,
the three-factor formula being extended, and the sharp scalar examples.
Nick Petalas's #4276 supplies the one- and two-factor criteria, following
#4265 and #4243. Wentao Li's #4099 supplies the right-vector alphabet and
column bound, building on #2513. Source bytes and commits are pinned in
SOURCES.json. Apache-2.0.
