# Finite rational three-coordinate groups do not give a native gain

Use the complete native ADDRESS contract from PR521. A query is
`H_N(g)=I+N tensor (g-1)` over the binary group algebra. Its rational
ADDRESS map has `rank(g-I)=1`. There are r productive DATA roles and
three ADDRESS difference coordinates. The target is `I_r tensor (-I3)`.
The native lift Phi preserves the group identity. This packet uses the
same all-size separation argument and dual-number inner-factorization
lemma as `../native-dual-number-proof/PROOF.md`.

Assume the ADDRESS maps generate a finite group W in `GL_3(Q)`.
The target -I3 must belong to W: every formal coefficient of the word
has support in W. The result is that at least 3r queries are needed.
Thus the eight-query target on three roles and the eleven-query target
on four roles are impossible in this finite-group model.

## Reduction to four finite reflection types

Average `g^T g` over W. The result is a positive definite rational Gram
matrix preserved by W. A finite-order rank-one update has two eigenvalues
1 and one rational root of unity different from 1. That last eigenvalue
is -1. Each query is therefore a reflection for the averaged Gram matrix.
The group is essential: -I3 fixes no nonzero vector.

We use the finite real-reflection chamber theorem: an essential finite
reflection group has a simplicial chamber, the wall reflections are a
Coxeter generating set, and every reflection is conjugate to a wall
reflection. This standard geometric theorem is described in Bill
Casselman's [Coxeter Groups I](https://personal.math.ubc.ca/~cass/coxeter/R.html),
in the geometry, roots and classification sections. The following
dimension-three and rationality restrictions are derived here.

For two wall reflections whose product has order p, its rational trace
in dimension three is `1+2 cos(2*pi/p)`. The number `2 cos(2*pi/p)` is an
algebraic integer. If it is rational it is an integer in [-2,2]. Hence
`p` is one of 2,3,4,6 for two different reflections.

Normalize the three wall normals to have length one. Their off-diagonal
Gram entries are `-cos(pi/p)`. A triangle in the Coxeter diagram would
give all three cosines at least 1/2. The Gram value on `(1,1,1)` would
then be at most zero, contrary to positive definiteness. A connected
diagram is therefore a chain. For its two labels p,q, positivity gives

    1-cos(pi/p)^2-cos(pi/q)^2 > 0.

With connected labels from 3,4,6, only (3,3) and (3,4) pass. They are
A3 and B3. A3 is the symmetric group on four letters, whose center is
trivial. It cannot contain the nonidentity central map -I3. Thus the
irreducible case is B3.

A reducible essential group is `I2(p) times A1`, or `A1^3`. The planar
central map -I2 belongs to `I2(p)` exactly when p is even. Rationality
restricts p to 2,4,6. The cases are `A1^3`, `B2 times A1`, and
`G2 times A1`. This proves the claimed four-type list without assuming
that every rational finite group is monomial.

The first three types B3, B2 times A1 and A1 cubed have the monomial
dual-number representation already checked in the preceding packet.
It maps -I3 to `(1+e)I3` and every reflection difference to one outer
product. Only G2 times A1 remains.

## An exact nonmonomial G2 times A1 representation

In the plane take

    a=[0 -1; 1 1],        s=[0 1; 1 0].

Then `a^6=1`, `a^3=-I2`, `s^2=1` and `s a s=a^-1`. Add an independent
third-coordinate sign. The resulting rational group has order 24.
Its six planar reflections `a^k s` and its third-coordinate flip are
exactly its seven rank-one updates. Four planar reflections are
nonmonomial in these rational coordinates.

Over `R=F_2[e]/(e^2)`, define

    rho(a)=[0 1+e; 1+e 1+e],       rho(s)=[0 1; 1 0].

The third-coordinate sign maps to 1+e. The presentation relations hold
exactly. The center `a^3` maps to `(1+e)I2`, so -I3 maps to `(1+e)I3`.
For every planar reflection, `rho(g)-I` has a unit entry and determinant
zero. If d_ij is a unit pivot, its column and its pivot-normalized row
give an outer product. The third-coordinate flip has outer product
`e e3 e3^T`. Thus every native query difference still has one outer
factor over R.

The verifier builds all 24 rational matrices and all their R images.
It checks every one of the 576 products, finds all seven rank-one
updates by rational elimination, and checks all 840 native outer
factorizations from seven updates and 120 scalar projectors.
The representation is a group representation; it is not an entrywise
sign map on these nonmonomial matrices.

An isomorphism from an arbitrary reflection realization of a listed
type to its standard reflection group preserves the wall reflections,
all their conjugates, and the central map -I3. We can therefore apply
these representations to every rational finite realization in the list.
No rational change of ADDRESS basis is required for this proof.

## Query bound and limits

The successful represented word would give `e I_(3r)=BC` with one
column of B and row of C per query. The binary coefficient equations
force `3r<=rank(B0)+rank(C0)<=k`. This gives `k>=3r`.
The free DATA and scalar-only helper extensions have the same separate
hypotheses as the preceding inner-factorization proof.

This is a finite-group obstruction. Infinite rational reflection groups,
rank-one unipotents and other nonmonomial infinite groups remain open.
The proof gives no integer-multiplication lower bound or kappa gain.
The finite reflection chamber theorem is an inherited mathematical
dependency. No global novelty claim is made. AI assistance was used.
