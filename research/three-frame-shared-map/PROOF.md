# Shared invertible maps for three frame subspaces

This is a scoped algebraic proof over every finite field F_q. The normal
form is classical three-subspace linear algebra. The contribution here is
an explicit compatibility and multiplicity contract for shared native maps.
No claim of literature priority is made for the normal form or its elementary
orbit-counting consequences.

Let U=(U1,U2,U3) and W=(W1,W2,W3) be ordered triples in F_q^n. A realizing
map is G in GL_n(F_q) with G Ui=Wi for each i. The ordering matters. Put

```
di = dim Ui
pij = dim(Ui intersection Uj)
c = dim(U1 intersection U2 intersection U3)
s = dim(U1 + U2 + U3)
t = d1+d2+d3 - p12-p13-p23 + c - s.
```

For each subset S of {1,2,3}, define an integer m_S by

```
m_empty = n-s
m_123 = c
m_ij = pij-c
m_i = di-pij-pik+c-t, where {i,j,k}={1,2,3}.
```

All these integers and t are nonnegative, and sum_S m_S + 2t=n.

**Compatibility theorem.** There is a realizing map exactly when the two
triples have identical values of n, the three di, the three pij, c and s.
Equivalently they have the same eight m_S and t.

## A simultaneous normal form

Let A_S denote a one-dimensional configuration in which Ui is the whole
line exactly when i belongs to S, and zero otherwise. Let D denote a
configuration on a plane with

```
U1 = <e>, U2 = <f>, U3 = <e+f>.
```

Every ordered triple is a direct sum of m_S copies of A_S and t copies of D.
Here is a direct proof which works over arbitrary fields.

First split off T=U1 intersection U2 intersection U3. Any linear section of
V/T takes each image Ui/T back into Ui, because T is contained in every Ui.
It therefore gives a simultaneous decomposition with dim(T) copies of A_123.
Work in the complementary configuration, whose triple intersection is zero.

Write Pij=Ui intersection Uj. The sum S=P12+P13+P23 is direct. Indeed, a
relation p12+p13+p23=0 puts p23 in all three Ui, hence makes it zero, and
then the other terms vanish too. In V/S the images of the three Ui have
pairwise zero intersections. For example, if x in U1 and y in U2 have the
same quotient image, write x-y=p12+p13+p23. Then
x-p12-p13=y+p23 lies in P12, so x belongs to P12+P13 and its quotient image
is zero. The other cases follow by relabeling.

For a pairwise-disjoint triple, put K=U3 intersection (U1+U2). The sum
U1+U2 is direct, so every z in K has a unique expression x+y. Both
projections from K to U1 and U2 are injective, since K meets either Ui
trivially. A basis z_k=x_k+y_k of K therefore gives t independent D planes.
Choose complements to the x_k in U1, the y_k in U2, and K in U3. These
complements are independent of each other and of those planes. A relation
would put its U3 part into K, then uniqueness in U1+U2 would make all parts
zero. They give the A_1, A_2 and A_3 summands. A complement to the total
sum gives A_empty.

This decomposition also lifts through the previous quotient V/S. Choose
lifts x_k in U1, y_k in U2 and z_k in U3 for each quotient D relation.
If x_k+y_k-z_k=p12+p13+p23, replace x_k by x_k-p12-p13 and y_k by
y_k-p23. Their sum is now z_k, while all three vectors remain in their
required subspaces. Lift the remaining independent quotient basis vectors
arbitrarily inside their Ui. Their collective span is disjoint from S,
because their quotient vectors are a basis of V/S. Each Ui splits into its
lifted part and Ui intersection S, which is Pij+Pik. Thus S contributes
precisely the pair atoms, and the quotient decomposition lifts simultaneously.

Counting intersections, individual dimensions and the total sum in this
normal form gives the formulas above. They also prove uniqueness of the
multiplicities. A realizing G preserves those dimensions, proving necessity.
Matching bases of equal normal-form summands constructs a realizing G,
proving sufficiency.

## Exact number of realizing maps

Define g_q(r)=product_(j=0)^(r-1)(q^r-q^j), with g_q(0)=1. Put

```
E = sum_(S subseteq T) m_S m_T + t^2
    + t (2m_empty + m_1+m_2+m_3 + m_12+m_13+m_23 + 2m_123)
R = E - sum_S m_S^2 - t^2.
```

If compatibility fails the number is zero. If it holds, the exact number is

```
q^R g_q(t) product_S g_q(m_S).
```

To prove the formula, an endomorphism of a configuration means a linear map
which sends every Ui into itself, without requiring invertibility. For the
one-dimensional atoms, Hom(A_S,A_T) has dimension one exactly when S is a
subset of T, and zero otherwise. Hom(A_S,D) has dimension two when S is
empty, one for a singleton, and zero otherwise. Hom(D,A_T) has dimension
two when T is full, one for a pair, and zero otherwise. An endomorphism of
D must preserve three distinct lines, so it is scalar. These statements
follow directly by choosing the images of e and f, and give the displayed E.

Order the blocks as A_empty, the three singleton types, D, the three pair
types, A_123. Every allowable off-diagonal map runs forward in that order.
The whole endomorphism matrix is therefore block triangular. The diagonal
blocks are arbitrary m_S by m_S matrices, and the D-isotypic diagonal block
is B tensor I_2 for an arbitrary t by t matrix B. Consequently an
endomorphism is invertible exactly when each of these nine diagonal matrices
is invertible. The remaining R scalar parameters are unconstrained, giving
q^R choices. This proves the stabilizer formula. If G0 realizes U to W,
all realizers are exactly G0 times the stabilizer of U, so the same formula
counts them. No search through GL_n is needed to evaluate this number.

## Number of compatibility types

The normal-form multiplicities are arbitrary nonnegative integers satisfying
sum m_S+2t=n. Conversely each such tuple constructs a triple. There are
therefore

```
N(n) = sum_(t=0)^floor(n/2) binomial(n-2t+7,7)
```

ordered compatibility types, independently of q. At native ambient dimension
nine this gives 15,792 types. This is an exact enumeration of normal-form
tuples, not a literal enumeration of all nine-dimensional subspaces or
matrices. The finite checker enumerates all literal triples only in its
explicit small-field domains.

## Why both extra invariants matter

Three distinct coplanar lines and three independent lines in F_2^3 have
identical individual dimensions and all intersection dimensions. Their
sum dimensions differ, and their realizing-map stabilizers have orders four
and one respectively. Pairwise compatibility alone cannot impose all three
correspondences.

Three coordinate planes in F_2^3 and three distinct planes through a fixed
line have the same individual dimensions, pairwise dimensions and total sum.
Their triple intersections have dimensions zero and one. Thus the triple
intersection cannot be dropped even when the total sum is retained.

## Scope of the native-map application

Cao Yifan's PR4610 package asks for simultaneous subspace-map consistency
when freeing its twelve prelude contracts together with late contacts. The
criterion answers the algebraic equality contract for any three ordered
subspaces. For two subspaces, setting U3=W3=0 reduces it to equality of
the two dimensions and the intersection dimension.

An actual prelude can prescribe the action on individual vectors, include
more than three subspaces, or impose dual, phase or symplectic conditions.
Those are additional constraints. This theorem does not assert that the
15,792 classes exhaust such contracts, and it does not construct a changed
native word or decide the current construction's profitability. Arbitrary-input
semantics, absolute phase, paid contacts, restoration, hosting, precision,
tape costs and supplier admission remain separate obligations.
