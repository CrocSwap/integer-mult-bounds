# Exactly three A2 fibers share each rank-six equality support

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement and inherited premises

Use the full E8 root-line labels R in F2^9 from PR3288, with leading
coordinate one. For a 27-root projective A2 fiber F and a binary space V
of dimension at most six, write

```
J_F(V) = |R intersect V| + |F intersect V|.
```

PR3262 and PR3288 supply the individual bound J_F(V)<=32. PR3288 also
supplies its equality characterization and the count of 27 equality
six-spaces for each of the 3,360 distinct fibers. These are cited premises.
This package does not independently audit their proofs or model census.

**Theorem.** If J_F(V)=32 for at least one fiber, then exactly three
distinct A2 fibers satisfy J_F(V)=32 for this same V. Two distinct fibers
share at most one equality six-space. Consequently there are exactly
30,240 equality six-spaces in total, and every fiber shares equality with
exactly 54 other fibers. A fourth distinct fiber cannot saturate the
individual bound on that same support.

The theorem concerns this finite full-E8 configuration. It does not say that
pairwise compatibility of several fibers forces a common equality space.

## A2 fibers in the quadratic model

Write E=F2^8, with the nondegenerate plus quadratic form q and polar form
B(x,y)=q(x+y)+q(x)+q(y). Root lines correspond to q(x)=1, with label
(1,x). An A2 root plane gives an anisotropic binary two-space N. Its three
nonzero vectors all have q=1. For p in N minus {0}, put

```
K = N-perp,
H(N,p) = p+K,
F(N,p) = {x in H(N,p):q(x)=1} minus {p}.
```

These are the 27-root fibers in the inherited model. To see the parity
identification, choose two roots of an A2 plane. The mod-two evaluation
against them has one zero class and three nonzero classes. Each nonzero
class contains its unique A2 root p and the corresponding large
projective evaluation fiber. The original real fibers have sizes
36,27,27,27,1,1,1, as recorded in the pinned predecessor. Distinct pairs
(N,p) give distinct affine sections and fibers.

The Gauss sum on N is -2. Its orthogonal complement K has Gauss sum -8,
since the ambient sum is +16. Translation by the orthogonal root p gives
sum_(x in H(N,p)) (-1)^q(x)=+8. Thus H contains 28 roots, including p.
The predecessor's seven-dimensional binary span is the homogenization of
H. Its equality six-spaces have affine sections A=a+L of dimension five,
contain 16 roots, and avoid p.

## The singular radical of an equality section

Fix one equality section A=a+L inside H(N,p). The hyperplane L in the
nondegenerate six-space K has a one-dimensional radical <r>. Equivalently,
L is the kernel of B(-,r) on K, for a unique nonzero r in K. Since the
form is alternating, r belongs to L.

The affine hyperplane A avoids p, so B(a-p,r)=1. As p is orthogonal to K,

```
B(a,r)=1.
```

The root count 16 says that the signed quadratic sum on A is zero. The
quadratic restriction identity from PR3288, or its direct squared-sum
calculation, gives

```
(sum_(x in A) (-1)^q(x))^2
    = 32 [1+(-1)^(q(r)+B(a,r))].
```

It follows that q(r)=0. Hence

```
U = L-perp = N direct-sum <r>
```

has dimension three, radical <r>, and q(r)=0. Its quotient by the radical
is the anisotropic plane N.

## Four complementary planes, three admissible projections

Every other fiber F(N',p') containing all 16 roots of this equality
six-space has A contained in H(N',p'), by the inherited equality
characterization. Therefore N' is contained in U. An anisotropic two-space
in U is a complement to <r>. Conversely every complement is anisotropic,
because q descends to the anisotropic quotient U/<r>.

There are exactly four complements. Relative to U=N direct-sum <r>, they
are the graphs

```
N_f = {u+f(u)r:u in N},       f in Hom(N,F2).
```

For each complement let p_f be the unique orthogonal projection of a
onto N_f. The condition p_f=0 is that B(a,-) vanish on N_f. On a graph,

```
B(a,u+f(u)r) = B(a,u)+f(u),
```

because B(a,r)=1. Exactly one f makes this functional zero. For that
complement p_f=0, which is not an A2 root and does not define a large
fiber. For each of the remaining three complements, p_f is nonzero and
q(p_f)=1.

Each of those three affine sections H(N_f,p_f) contains A. Also p_f is
not in A, since B(p_f,r)=0 whereas B(x,r)=1 for every x in A. Thus every
root of A lies in F(N_f,p_f), giving joint score 32. Conversely the
previous paragraph exhausts every possible fiber. This proves exactly
three, including the initially chosen fiber.

The 16 roots determine their affine five-space A. Otherwise they would
fill an affine four-space on which q is constant one. Its direction would
be a four-dimensional totally isotropic subspace of L. But L has radical
dimension one and nondegenerate quotient dimension four, so its largest
totally isotropic subspace has dimension three. This is impossible.
Homogenizing shows that the roots determine V as well.

## Pairwise uniqueness and the counts

Distinct fibers have distinct seven-dimensional binary spans W_F.
Indeed the leading-one section determines N-perp and then N, and its
orthogonal projection determines p. If two distinct fibers share an
equality V, then V is contained in the intersection of their two spans.
That intersection has dimension at most six, so it is exactly V. Hence
the shared equality space is unique.

Double-counting the inherited 3,360 times 27 incidences now gives

```
number of equality spaces = 3360*27/3 = 30240.
neighbors of each fiber = 27*(3-1) = 54.
compatible unordered fiber pairs = 3360*54/2 = 90720.
```

Pairwise uniqueness is needed in the second count, to prevent counting a
neighbor twice. These counts do not enumerate arbitrary cliques in the
pairwise compatibility graph.

## Explicit witness and verification boundary

In the pinned simple-root encoding, one common equality support is

```
[3,11,27,31,39,47,59,63,71,79,83,87,103,111,123,127].
```

The three anisotropic normal planes, listed by their nonzero eight-bit
vectors before homogenization, and their omitted singleton points are

```
N={84,128,212}, p=128;
N={84,134,210}, p=210;
N={82,134,212}, p=82.
```

The verifier uses q0(x)=x0*x1+x2*x3+x4*x5+x6*x7. The columns
`[3,6,18,34,76,78,130,208]` give an explicit invertible transport to the
pinned simple-root quadratic polynomial. All 256 values are compared.
No P112 membership or caller compatibility is asserted for this witness.

The primal enumeration visits the hyperplanes of each inherited fiber
span and constructs the new cross-fiber incidence. The separate dual
enumeration visits every U=N+<r> above, its four complementary planes and
the four cosets of U-perp with B(a,r)=1. They agree on every support and
every incident (N,p), not only totals. All 30,240 zero-projection exclusions
are checked. The code does not import or run predecessor executable code.

The new written proof and finite certificate are author-checked evidence.
Independent human and formal proof-kernel review are unclaimed. The
predecessor's individual bounds and E8 binding remain cited dependencies.
No shortening threshold, physical circuit, paid moment, kappa or complete
multiplication theorem is derived.

Credit Nick Petalas / PR3288, PR3280 and PR3262, David Arias's quadratic
model, DreamingOfClouds / PR3154, joaqcoo and the retained E8/P112 lineage.
Quadratic-form restriction identities and binary symplectic linear algebra
are classical. The new step is the simultaneous three-fiber classification
and its incidence consequences.
