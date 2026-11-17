# Rational header orbits retain their integer lattice

This scoped proof was produced by Nick Petalas. Apache-2.0.

## Contract and cited inputs

Fix an even integer n >= 2, V = Q^n, and a nondegenerate alternating
rational form omega. A normalized saturated header is an ordered tuple
T = ((x_i,y_i)) for i = 0,...,n, with

```text
y_i = omega(x_i, .),
y_i x_j = sgn(i-j),
U_i = I - 2 x_i y_i,
U_n ... U_0 = -I.
```

The form and ambient rational coordinates are fixed. Allowed equivalence
is a finite sequence of the normalized Hurwitz moves

```text
mu_i^+ : (x_i,x_(i+1)) -> (x_(i+1), 2x_(i+1)-x_i),
mu_i^- : (x_i,x_(i+1)) -> (2x_i-x_(i+1), x_i),
```

with the corresponding covectors obtained from the same fixed omega.
There are no additional rational changes of frame or rescalings in this
equivalence relation. A simultaneous global sign may be quotiented out
without changing the result below, since it changes neither invariant.

We cite DreamingOfClouds's #6842, `p104-header-braid-classification`,
Theorems 1, 3 and 4, for the normalized header structure, the moves and
the integral-frame classification. In particular the unique relation is
sum_i (-1)^i x_i = 0, the first n vectors are a basis, and in a fixed
integral unimodular frame two integral normalized headers are equivalent
exactly when their vector multisets modulo 2 agree. These results are
premises here, not results independently checked by this package.

The integral sufficiency input in dimensions n >= 4 uses the pure braid
image theorem, Brendle and Margalit, *The level four braid group*,
[Theorem 3.3(1)](https://arxiv.org/pdf/1410.7416), which states the
surjectivity for genus g >= 2 and credits A'Campo. We do not reprove it.
For n = 2 the elementary argument at the end of the next section suffices.

## The lattice and the classification

Define L(T) = sum_i Z x_i inside V. This is an embedded integer lattice,
not the rational span and not the 2-local span. Define C(T) to be the
multiset of the classes x_i + 2L(T) in the intrinsic quotient L(T)/2L(T).
Comparing C(T) and C(T') is meaningful as an equality in the same quotient
only after L(T) = L(T') has been established.

**Theorem.** For two normalized rational headers in the same fixed form,

```text
T ~ T'  iff  L(T) = L(T') and C(T) = C(T').
```

Thus the missing rational invariant is the embedded integer lattice.
Once that lattice is fixed, the remaining classification is exactly the
predecessor's integral one, evaluated intrinsically in that lattice.

**Proof.** Let B have columns x_0,...,x_(n-1). The cited alternating
relation expresses x_n as an integral combination of these columns.
Consequently L(T) = B Z^n. Its Gram matrix is

```text
B^T omega B = S,  S_ij = sgn(i-j),  0 <= i,j < n.
```

It is an integral unimodular alternating matrix, by the cited header
structure. In particular L(T) is an integral unimodular symplectic lattice
even when its embedding in the original coordinate lattice is rational.

A forward move replaces two generators a,b by b,2b-a. Conversely
a = 2b-(2b-a), so the integer span is unchanged. An inverse move gives
the same conclusion. Modulo 2L the move just exchanges the two classes,
so the multiset C is also unchanged. This proves necessity without any
braid-image theorem.

For sufficiency suppose L(T') = L(T) = L. Choose the single lattice basis
B from T, and express both entire headers in its coordinates. Both vector
tuples are integral; their covectors are integral because the form S is
integral. The form is the same fixed unimodular S for both tuples. Their
ambient integral residue multisets in these coordinates are exactly C(T)
and C(T'). Apply #6842's integral classification to obtain a finite
Hurwitz word connecting them. Every move is an integer linear formula,
so changing coordinates back by B carries that same literal word from T
to T'. This proves sufficiency. No rational frame change has been added
to the allowed operations; the single coordinate chart is only used in
the proof.

For n = 2, the three residue vectors of a normalized header are exactly
the three nonzero elements of L/2L. The two differences
d_0 = x_0-x_1 and d_1 = x_1-x_2 = x_0 are an integer basis with pairing
-1. The two move transformations are the transvections along d_0,d_1,
which in that basis are the two elementary unipotent generators of
SL_2(Z), up to inverse and sign conventions. They generate SL_2(Z) by
the integer Euclidean algorithm. Rigidity gives a symplectic integral
transition between any two headers on L, so all of them are connected.
This establishes the required dimension-two sufficiency directly. QED.

The theorem is independent of a chosen basis of L: changing the common
basis applies one invertible linear map to both intrinsic multisets.
Using a separately chosen basis for each header and comparing the two
coordinate lists would discard the invariant and is not the criterion.

## An infinite obstruction invisible modulo 2

Take n = 2, omega = [[0,-1],[1,0]], and for each positive odd integer m set

```text
x_0(m) = (1/m, 0),
x_1(m) = (0, m),
x_2(m) = (-1/m, m),
y_i(m) = x_i(m)^T omega.
```

These are the conjugates of the normalized header at m = 1 by the
symplectic rational matrix G_m = diag(1/m,m), so they are normalized
headers in the same fixed omega. Equivalently, their covectors are
(0,-1/m), (m,0), (m,1/m); their pairings give the required sign Gram,
and multiplying the three literal units gives -I.

All coordinates lie in Z_(2), the rationals with odd denominators.
Reduction of any odd integer or its inverse modulo 2 is 1. Hence every
tuple has the identical ambient reduction

```text
{(1,0), (0,1), (1,1)} in F_2^2.
```

But L_m = (1/m)Z e_0 + m Z e_1. Its first-coordinate projection is
(1/m)Z, so equality L_m = L_k for positive m,k implies m = k.
Necessity in the theorem therefore proves that these headers occupy
pairwise different Hurwitz orbits. Each lattice has covolume one and
the same unimodular form; neither covolume nor ambient mod-2 data detects
the obstruction. In dimension two the lattice alone is also sufficient,
as established above.

This conclusion does not contradict #6842's integral theorem, whose
integral ambient-frame hypothesis forces L = Z^n. It shows why replacing
that hypothesis by 2-local integrality while keeping only ambient mod-2
data would lose information. It excludes connecting distinct L_m by
Hurwitz moves, not connecting them by an explicitly paid rational frame
change or by a larger operation alphabet.

## Evidence boundary

The theorem and the infinite family follow from the written argument.
The new standalone checker corroborates rational instances, literal
Hurwitz walks, both invariants, and the full product on each checked
tuple. It also supplies a same-lattice pair with different intrinsic
residue multisets, demonstrating the need for both parts in dimension
four. This is not a census of rational headers or an independent replay
of #6842. Native implementation, site-mask legality, compiler closure,
physical frame changes, precision, storage and complete pricing remain
outside scope. No multiplication theorem or new kappa follows.
