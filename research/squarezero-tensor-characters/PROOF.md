# Square-zero local multiplication tensors

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement and conventions

Let K=F_q, let V be a K-vector space of dimension d>=2, and set n=d+1.
Give A=K plus V the multiplication

```text
(a,x)(b,y) = (ab, ay+bx).
```

Thus A is a commutative unital local algebra, its radical is J=V, and
J squared is zero. Conversely every commutative unital local K-algebra
with residue K and square-zero radical has this form: its given scalar
copy of K complements J, and all radical products vanish. Its socle is J,
of dimension d, so the d>=2 class is non-Gorenstein.

Let t be the multiplication tensor in A* tensor A* tensor A. We use the
ordinary covariant action of GL(A*) times GL(A*) times GL(A). In chosen
dual/input and output bases these are three independent GL_n(K) factors.
Write Delta(t) for the ordered determinant image of its stabilizer, and
H_n={c^n:c in K*}. Then

```text
Delta(t) = {(u,v,w) in (K*)^3 : uw in H_n and vw in H_n}.
```

If g=gcd(n,q-1), the same subgroup is defined by the two equations

```text
(uw)^((q-1)/g) = (vw)^((q-1)/g) = 1.
```

It has (q-1)^3/g^2 elements. The GL_n(K)^3 orbit of t contains exactly
g^2 orbits under SL_n(K)^3. These statements hold after three independent
basis changes, because stabilizers conjugate factor by factor and
determinants are invariant under conjugation.

This is a scoped algebraic proof. The finite verification below only
corroborates its constructions on explicitly bounded domains.

## 1. Unit and automorphism determinants

Use a basis (1,e_1,...,e_d) with e_i in J. Multiplication L_a by
a=(a_0,x) has matrix

```text
          [a_0   0       ]
L_a =     [x     a_0 I_d ].
```

Therefore det(L_a)=a_0^n. The element a is a unit exactly when a_0 is
nonzero; its inverse is (a_0^-1,-a_0^-2 x). The unit determinant image is
precisely H_n. Nilpotent coordinates change no determinant.

Every unital K-algebra automorphism fixes the scalar copy of K and
preserves the radical, since nilpotence and units are intrinsic. It is
therefore (a,x) -> (a,Px) for P in GL_d(K). Conversely every such P
preserves multiplication. Consequently Aut_K(A)=GL_d(K), with determinant
det(P) on the whole n-dimensional algebra. Its determinant map is onto
K*: the diagonal map with radical entries delta,1,...,1 attains delta.

## 2. Normalize every autotopism

Let F,G,H be invertible K-linear maps satisfying

```text
F(x)G(y)=H(xy) for all x,y in A.
```

Put a=F(1), b=G(1). Setting one input to 1 gives H=L_b F=L_a G.
Thus L_a and L_b are invertible, and a,b are units. Define
sigma=L_(ab)^-1 H. The preceding identities give

```text
F=L_a sigma, G=L_b sigma, H=L_(ab) sigma.
```

Substituting into the autotopism equation and cancelling the unit ab
shows sigma(x)sigma(y)=sigma(xy). Also sigma(1)=1, and sigma is invertible.
It is an algebra automorphism. Conversely every pair of units a,b and
every algebra automorphism sigma give an autotopism by these formulas.
This normalization is classical unital isotopy; it is included to fix the
action convention and does not rely on a predecessor's computation.

## 3. Pass to the covariant tensor action and prove exactness

The stabilizer triple associated to this autotopism is
(F^-T,G^-T,H). In fact its transformed bilinear map is

```text
(x,y) -> H(F^-1(x) G^-1(y)) = xy.
```

Let alpha=a_0^n, beta=b_0^n, delta=det(sigma). Its ordered determinants are

```text
u=alpha^-1 delta^-1,
v=beta^-1 delta^-1,
w=alpha beta delta.
```

In particular vw=alpha and uw=beta. Section 1 proves the necessity of
both nth-power restrictions.

Conversely suppose (u,v,w) satisfies them. Choose a_0,b_0 in K* with
a_0^n=vw and b_0^n=uw. Take any radical coordinates for a,b, and choose
sigma with determinant delta=(uvw)^-1 using section 1. The displayed
formulas now give exactly u,v,w. Thus every allowed triple has an explicit
stabilizer, including nonzero radical coordinates in both unit factors.
This proves equality of the images, rather than just an upper bound.

There is no additional restriction on uvw. For example, at q=5 and n=4,
the image is {(c,c,c^-1):c in F5*}. Its products c can be arbitrary.
Conversely a product-one triple can fail both nth-power restrictions:
(2,3,1) over F5 has product one but is excluded when n=4.

## 4. Equations, size and special-linear orbit count

The multiplicative group K* is cyclic of order m=q-1. Hence its nth-power
subgroup has size m/g and consists exactly of the roots of z^(m/g)=1,
where g=gcd(n,m). This proves the two equations in the statement.

The map

```text
(u,v,w) -> (uw,vw)
```

from (K*)^3 to (K*)^2 is onto and each fiber has m elements: choose w
freely and then u,v are forced. The preimage of H_n times H_n therefore
has m*(m/g)^2=m^3/g^2 elements.

For completeness let G=GL_n(K)^3 and N=SL_n(K)^3. The componentwise
determinant map G -> (K*)^3 is surjective with kernel N, so N is normal.
The N-orbits on G/Stab(t) correspond to the cosets of
det(Stab(t)) in (K*)^3. Indeed two elements of G differ by a left element
of N and a right stabilizer precisely when their determinants differ by
an element of Delta(t). Their number is m^3/|Delta(t)|=g^2.

This orbit count refers to ordinary linear tensor equivalence over K.
It asserts no semilinear count, physical implementation or computational
recognition algorithm for arbitrary tensors.

## Interface, credit and scope

Ali Romman's #5540 reconstructs commutative multiplication from arbitrary
square tensors over prime fields and leaves the recovered-algebra and
determinant-character interfaces open. It is a cited predecessor, not
replayed here. For its recovered square-zero local class, the above proof
gives the exact determinant subgroup. Given a multiplication chart,
membership of its determinant triple in Delta(t) decides whether a
general-linear equivalence can be adjusted to a special-linear one.
No extractor or transporter from an arbitrary uncharted tensor is supplied.

Finite-field cyclicity, unital isotopy, radical invariance and the normal-
subgroup orbit argument are classical. The new contribution is their exact
assembly for this non-Gorenstein class, the two equations, attaining maps
and explicit replay. Related etale and rectangular truncated-polynomial
packages cover different algebras. Their verifiers, inventories and numerical
results are not used as steps of this proof.

Independent human and formal proof-kernel review are unclaimed. This is no
new kappa, native caller, paid supplier, selected-frontier update or complete
multiplication theorem.
