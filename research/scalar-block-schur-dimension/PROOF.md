# Exact dimension for a common scalar block

This proof was produced by Nick Petalas. Apache-2.0.

Let K be any field, d >= 1, lambda in K nonzero and H in M_d(K).
Consider commuting idempotents P,Q on K^n whose first d-by-d blocks are
both lambda I_d and whose product PQ has first block H. Let S,Z be the
two Schur complements after deleting those first d coordinates. Then the
least n permitting rank(SZ-ZS)=2d is exactly

```text
n_min(lambda,H) = 3d + rank((1-2lambda)I+H)
                       + 2 nullity(lambda I-H) + nullity(H).       (1)
```

Every minimum is attained over K, without diagonalizability assumptions
on H. This answers Open next question 2 of Nick Petalas's #4771. The
identity-block result of #4746 and ssafwann's #4671, and the scalar-block-size
one result of #4771, are cited predecessors. The new part is the common
nonidentity scalar block with an arbitrary prescribed matrix product.

## Compression and the full-rank criterion

Put U=K^d, V=K^n. Let i:U -> V be coordinate inclusion and pi:V -> U
coordinate projection, so pi i=I. The joint eigenspace projectors are

```text
E00=(I-P)(I-Q), E10=P(I-Q), E01=(I-P)Q, E11=PQ.
```

They give a direct sum V=V00+V10+V01+V11 in every characteristic. Set
Y_j=E_j i:U -> V_j and X_j=pi restricted to V_j:V_j -> U. Write

```text
D=lambda I-H,   T0=(1-2lambda)I+H,
a=nullity(H),  b=nullity(D),  c=rank(T0).
```

Compression gives

```text
X00 Y00=T0,  X10 Y10=D,  X01 Y01=D,  X11 Y11=H.             (2)
```

In particular, their sum T0+2D+H is I. The signed joint-sector method
comes from ssafwann's #4671 and Nick Petalas's #4746. Here the products
and the rank argument retain lambda throughout.

Use Nick Petalas's ordered block Schur identity from #4597, with equal
pivot blocks lambda I. Its ambient factors are

```text
A=[PQ i-Q i H/lambda, (P-Q)i/lambda] : U^2 -> V,
B=[pi(P-Q)/lambda; -pi PQ+H pi Q/lambda] : V -> U^2.
```

We have pi A=0 and Bi=0. Since V=i(U) direct-sum ker pi, the Schur
commutator is the product of A in ker pi coordinates and B restricted to
ker pi. Thus its rank is 2d exactly when A is injective and B is onto.
In joint-sector coordinates,

```text
A(x,y) = (1/lambda)(0, Y10 y, -Y01(Hx+y), Y11 D x),
B(v00,v10,v01,v11)
       = (1/lambda)(X10 v10-X01 v01,
                     H X01 v01-D X11 v11).                    (3)
```

**Criterion.** Rank(SZ-ZS)=2d if and only if Y10,Y01,Y11 are injective
and X10,X01,X11 are onto.

For necessity, rank 2d forces A injective. If Y10 z=0, (2) implies
Dz=0, hence Hz=lambda z. Equation (3) then gives A(z,-lambda z)=0,
so z=0. If Y01 z=0, the same product equation gives Dz=0 and
A(z,0)=0, hence z=0. If Y11 z=0, (2) gives Hz=0. Thus
Dz=lambda z and again A(z,0)=0, hence z=0. This proves all three
injections. Apply the same necessity argument to the dual commuting
projectors with inclusion pi* and projection i*. Their commutator has
the same rank, and their sector inclusion ranks are the ranks of X_j*.
Consequently the three X_j are onto.

For sufficiency, A(x,y)=0 first gives y=0 by injectivity of Y10.
The other two sectors give Hx=Dx=0. Since H+D=lambda I and lambda
is nonzero, x=0. Thus A is injective. If a covector (u,v) annihilates B,
surjectivity of X10 gives u=0. Surjectivity of X01 and X11 then gives
vH=vD=0, hence lambda v=0 and v=0. Thus B is onto. As Bi=0,
its restriction to ker pi is onto too. Their product has rank 2d,
proving the criterion.

## Lower bound and attaining construction

Let r_j=dim V_j. For every active sector 10,01,11, the criterion and
the rank inequality for a product imply

```text
rank(X_j Y_j) >= rank X_j + rank Y_j - r_j = 2d-r_j.
```

Equation (2) therefore gives the componentwise necessary bounds

```text
(r00,r10,r01,r11) >= (c,d+b,d+b,d+a).                         (4)
```

Their sum is (1). Also rank P=r10+r11 and rank Q=r01+r11 are
each at least 2d+a+b. These input-rank bounds can be attained together
with all four sector bounds.

For an arbitrary d-by-d matrix T, let N_T have columns forming a
complement to im T in U. On a space of dimension d+nullity(T) put

```text
X_T=[T N_T],     Y_T=[I;0].
```

Then X_T Y_T=T, X_T is onto and Y_T is injective. Use this for T=D
in sectors 10 and 01 and for T=H in sector 11. In sector 00 take any
rank factorization T0=X00 Y00 through dimension c, including dimension
zero if T0=0. Stack the Y maps to form i and concatenate the X maps to
form pi. By (2), pi i=T0+2D+H=I.

On this direct sum let P0 and Q0 act by their sector eigenvalues 00,
10,01,11. Complete i to a coordinate basis M=[i N], where N is a basis
of ker pi. This is invertible because pi i=I. Then

```text
P=M^-1 P0 M,    Q=M^-1 Q0 M
```

are commuting idempotents with the prescribed leading blocks and product.
All six active maps have full rank, so (3) proves sharpness. The dimension
is exactly c+2(d+b)+(d+a). This proves (1) and simultaneous attainment
of (4) and both input-rank bounds over every field.

## Specializations and a nondiagonal example

At lambda=1, c=rank(H-I)=d-b, so (1) reduces to the predecessor
identity-pivot formula 4d+a+b. At d=1 it reduces to all three cases
of the predecessor scalar formula in #4771. These are calibration
specializations, not new results.

For a new nondiagonal instance, over F5 take

```text
lambda=2,   d=2,   H=[[3,1],[0,3]].
```

Here T0=[[0,1],[0,0]] has rank one, while H and D=2I-H are
invertible. Thus the exact minimum is seven, with sectors (1,2,2,2),
input ranks four and Schur-commutator rank four. Replacing this Jordan
block by 3I gives minimum six. A nondiagonal nilpotent part can therefore
change the minimum even when H and lambda I-H have the same nullities.
The construction above realizes both cases directly.

This is a scoped algebraic proof, not a complete multiplication theorem.
It supplies neither header frequencies nor a paid header producer or
consumer. Unequal block pivots, general coefficient rings, subsequent
Schur-state transitions, precision, restoration and stock remain separate
obligations. Independent human and formal proof-kernel review are unclaimed.
