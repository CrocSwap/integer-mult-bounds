# Prescribed arbitrary pivots: the exact Schur dimension

Krzysztof Wojt, with substantial OpenAI Codex assistance. Apache-2.0.

This is a scoped all-field algebraic proof. The ordered Schur factorization
is Nick Petalas's #4597. The joint-sector and split-factor methods come from
ssafwann #4657/#4671 and Nick Petalas #4746/#4771/#4774/#4785. The new step is
the six-map criterion for arbitrary invertible, possibly noncommuting block
pivots, and its exact prescribed-boundary minimum. No historical priority
is claimed for the underlying linear algebra.

## 1. Statement

Let K be any field, d >= 1, and let A,B in GL_d(K) and H in M_d(K) be
prescribed. There is no commutation assumption on A,B,H. Among all commuting
idempotents P,Q in M_n(K) satisfying

```
P11=A, Q11=B, (PQ)11=H,
S=P22-P21 A^-1 P12, Z=Q22-Q21 B^-1 Q12,
rank(SZ-ZS)=2d,
```

the exact least dimension is

```
n_min = 3d + rank(I-A-B+H)
           + nullity(A-H) + nullity(B-H) + nullity(H).       (1)
```

For the simultaneous eigenspaces indexed by 00,10,01,11, every such pair
satisfies the componentwise bounds

```
r00 >= rank(I-A-B+H),
r10 >= d+nullity(A-H),
r01 >= d+nullity(B-H),
r11 >= d+nullity(H).                                      (2)
```

All four equalities are attained together. The same construction attains
both least input ranks

```
rank P = 2d+nullity(A-H)+nullity(H),
rank Q = 2d+nullity(B-H)+nullity(H).                        (3)
```

Consequently it also minimizes both residual ranks, obtained by subtracting d.
One may add any number of unused 00-sector dimensions, so every n >= n_min
is feasible. Formula (1), not the finite verification, is the universal claim.

## 2. Ordered ambient factors

Let U=K^d, V=K^n, i:U -> V be inclusion of the first d coordinates and
pi:V -> U the corresponding projection. Thus pi i=I and
pi P i=A, pi Q i=B, pi PQ i=H. Define maps L:U^2 -> V and R:V -> U^2 by

```
L = [PQ i-Q i B^-1 H,  P i A^-1-Q i B^-1],
R = [A^-1 pi P-B^-1 pi Q;
     -pi PQ+H B^-1 pi Q].                                (4)
```

The order of all factors is part of (4). Direct substitution gives
pi L=0 and R i=0. The operators

```
Ptilde=P-P i A^-1 pi P, Qtilde=Q-Q i B^-1 pi Q
```

have block forms diag(0,S), diag(0,Z). Multiplying (4) and cancelling the
two identical terms Q i B^-1 H B^-1 pi Q gives

```
L R = Ptilde Qtilde-Qtilde Ptilde = diag(0,SZ-ZS).          (5)
```

This is the ambient form of #4597's ordered identity. It neither moves H
past B^-1 nor moves any pivot past another block. In particular
rank(SZ-ZS)<=2d. Equality holds exactly when L is injective and R is
surjective: a surjection onto U^2 followed by an injection from U^2 has
rank 2d, and rank 2d of the product forces both conditions.

## 3. The six-map criterion without scalar pivots

Commuting idempotents split V as the direct sum of their four simultaneous
eigenspaces, in every characteristic. Write

```
E00=(I-P)(I-Q), E10=P(I-Q), E01=(I-P)Q, E11=PQ,
Yj=Ej i:U -> Vj, Xj=pi|Vj:Vj -> U.
```

Their compressed products are

```
X00 Y00=I-A-B+H, X10 Y10=A-H,
X01 Y01=B-H,     X11 Y11=H.                              (6)
```

In these coordinates the left factor is

```
L(x,y) = (0,
          Y10 A^-1 y,
         -Y01 B^-1(Hx+y),
          Y11((I-B^-1 H)x+(A^-1-B^-1)y)).                (7)
```

**Criterion.** rank(SZ-ZS)=2d if and only if each of Y10,Y01,Y11 is
injective and each of X10,X01,X11 is surjective.

First prove that L is injective exactly when all three active Y maps are
injective. For necessity:

* If 0!=z is in ker Y10, then (A-H)z=0 by (6). The nonzero pair
  (x,y)=(-z,Az) is killed by (7): its first active component is Y10 z,
  its second uses -Hz+Az=0, and its last argument is
  -z+B^-1 Hz+z-B^-1 Az=0.
* If 0!=z is in ker Y01, then Hz=Bz. The pair (z,0) is killed by (7),
  since B^-1 Hz=z and (I-B^-1 H)z=0.
* If 0!=z is in ker Y11, then Hz=0. Again (z,0) is killed by (7).

Conversely, if all three Y maps are injective and L(x,y)=0, its 10 component
first gives y=0 because A is invertible. Its 01 component then gives Hx=0
because B is invertible. Its 11 component finally gives x=0.

Necessity of surjectivity of the X maps follows by applying this argument to
P^t,Q^t. Their leading blocks are A^t,B^t, their product block is H^t
(because PQ=QP), and their Schur commutator is -(SZ-ZS)^t. For each sector,
rank(Ej^t i)=rank(pi Ej)=rank Xj. Hence equality of commutator rank forces
all three X maps onto. This argument uses ranks, not an assumption that
the given coordinate splitting is orthogonal to the joint eigenspaces.

For sufficiency, the preceding argument gives injectivity of L. If a pair
of row covectors (u,v) annihilates R, its restrictions to sectors 10,01,11
are respectively

```
u A^-1 X10,
(-u+vH) B^-1 X01,
(u(A^-1-B^-1)-v+vH B^-1) X11.                           (8)
```

Surjectivity of X10 implies u=0. Surjectivity of X01 then implies vH=0.
The 11 expression reduces to -v X11, so v=0. Thus R is onto, proving the
criterion by (5). This also shows explicitly why noncommutation of A,B,H
does not obstruct the argument.

## 4. Lower bound and simultaneous attainment

If X:K^r -> K^d is onto and Y:K^d -> K^r is injective, the rank inequality
rank(XY)>=rank X+rank Y-r gives r>=d+nullity(XY). Apply it in each active
sector of (6). The 00 sector needs only r00>=rank(X00Y00). These are (2),
whose sum is (1). Adding the active sector dimensions of P and Q gives (3).

Here is an explicit construction attaining them for every prescribed A,B,H.
For any T in M_d(K), choose a matrix N_T whose columns complement im T
in K^d and put

```
X_T=[T N_T], Y_T=[I;0].
```

The middle space has dimension d+nullity(T); X_T is onto, Y_T is injective,
and X_T Y_T=T. Use these factors for T=A-H, B-H, H in sectors 10,01,11.
For T00=I-A-B+H choose an ordinary rank factorization X00Y00=T00 through
dimension rank T00. A zero-dimensional 00 sector is allowed.

Let i be the vertical concatenation of the four Y maps and pi the horizontal
concatenation of the four X maps. By (6), pi i=I. On the sector direct sum,
define

```
P0=diag(0,I,0,I), Q0=diag(0,0,I,I).
```

They commute and are idempotent. Compression gives pi P0 i=A,
pi Q0 i=B, pi P0 Q0 i=H. Choose a basis N of ker pi. Since pi i=I,
M=[i N] is invertible. Set

```
P=M^-1 P0 M, Q=M^-1 Q0 M.
```

In the resulting coordinates, i is the first-block inclusion and pi its
projection. Thus P,Q have exactly the prescribed three leading blocks.
All six active maps have full rank, so their Schur commutator has rank 2d.
Their sector dimensions and input ranks attain (2) and (3) simultaneously.
This completes the proof; no diagonalization of H or compatibility condition
between A,B,H is needed.

## 5. Specializations and a noncommuting sharp example

If A=B=lambda I, (1) is precisely the common scalar-block formula of #4785.
If d=1 and A=p, B=q are distinct nonzero scalars, the three nullities sum
to [h in {0,p,q}], recovering #4774. A=B=I specializes to #4746/#4671.
These are consistency comparisons, not new results or predecessor audits.

Over Q take

```
A=[[2,1],[0,2]], B=[[2,0],[1,2]], H=[[3,1],[1,3]].
```

All three pairwise commutators of A,B,H are nonzero. Yet H=A+B-I, and
H, A-H=I-B, B-H=I-A are invertible. Formula (1) therefore gives n_min=6,
with sectors (0,2,2,2), rank P=rank Q=4 and Schur-commutator rank 4.
The same matrices reduced modulo three still give these ranks. These
examples lie outside the scalar-block predecessors. The verifier constructs
their complete matrices and checks their literal Schur products exactly.

## 6. Boundary of the conclusion

The theorem assumes both pivots invertible and P,Q commuting idempotents.
It concerns one common deletion over a field. It does not classify arbitrary
nonidempotent commuting inputs, singular-pivot generalized complements,
coefficient rings, nonmaximal commutator ranks or complete-header frequencies.
The attaining algebraic representation does not construct or price a physical
header producer/consumer, arbitrary dirty-owner restoration, precision, stock,
fixed tapes, recursive compilation or outer transfer. No new kappa follows.
