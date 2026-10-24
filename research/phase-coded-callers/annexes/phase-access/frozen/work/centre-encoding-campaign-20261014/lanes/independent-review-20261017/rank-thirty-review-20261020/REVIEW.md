# Independent review of the full rank-thirty response

The frozen matrix and scalar-code packet passes. It gives an exact
dyadic unit on all 112 ports, with correction rank 30. Both its response
and its inverse retain the specified selected eight-port block. The
ordinary 104-port block has an exact dyadic inverse. All four supplied
common-frame scalar words have the stated map and price.

No material finding remains in this scope. This review does not certify
the separate native packet, helper progress, a routed cut, a terminal,
or a complete supplier cost.

## Response and selected interface

The response on 48 ports is the signed pair conjugate of eight copies
of the root's integer six-mode unit. At each vertex the two modes that
meet selected physical ports occupy the first two a positions. The
sign diagonal gives their two off-diagonal coefficients -alpha_v.
The response and its inverse have the same a-to-a block. These facts
preserve the old selected block in both physical matrices.

The independent checker derives each vertex assignment from the
pinned mode support and the original selected set. It then acts on
physical basis columns in this order:

```text
signed pair code,
selected sign diagonal,
rank-one reflection and final coordinate exchange,
selected sign diagonal,
inverse pair code.
```

For the inverse it reverses the reflection and exchange. It does not
import the producer or use the producer's matrix to define this action.
All 112 columns in each direction agree with the frozen matrices,
including the disjoint small-port response. Both full inverse orders
are the identity.

The selected block L is the old block, and L^-1 is the old inverse.
Both multiplication orders are checked. For the ordinary block H,
write the full inverse as

```text
E^-1 = [[L,N],[P,Q]].
```

The block inverse identity gives H^-1=Q-P L^-1 N. The supplied ordinary
inverse passes both multiplication orders on all 104 columns; every
coefficient is dyadic. The exact determinants are

```text
det(L)=1/16,       det(H)=2^21,       det(E)=2^25.
```

They also satisfy Jacobi's principal-minor identity
det(H)=det(E) det((E^-1)_SS). No Schur-complement determinant has been
substituted for the ordinary determinant.

The supplied U and V have ranks 30 and satisfy E-I=UV on every physical
column. The two disjoint parts contribute ranks 16 and 14. Since U is
injective and V is onto its 30-dimensional output, this proves that
the correction rank is exactly 30.

## The small-port cover and its restricted optimum

The fourteen cliques partition the 64 small ports. Eleven have size
five and three have size three. The checker verifies each pairwise
binary inner product from the actual q labels.

On a clique of size k, I-J has eigenvalue 1-k on the constant vector
and eigenvalue one on its complement. Therefore its inverse is
I-J/(k-1), its determinant is 1-k, and its correction rank is one.
For k=3 and k=5 these are dyadic units. The complete small determinant
is (-4)^11(-2)^3=2^25.

There is a short structural proof that the actual support has no
nine-clique. Every small q satisfies q dot q=1 and q dot z=1 for z=45.
The vector z is nonzero and isotropic. Nine pairwise orthogonal odd
vectors in the nine-dimensional binary space would be an orthonormal
basis. Expanding z in that basis would give z=sum(q_i), and hence
z dot z=1. This contradicts z dot z=0.

As a separate finite check, this review enumerates all cliques by
increasing vertex extension. This differs from the producer's
pivoted maximal-clique method. It finds exactly the same maximal
cliques: 896 of size four and 64 of size eight. It also compares every
maximal clique, not just the two counts.

The fourteen-block optimum is valid within the stated disjoint
dyadic rank-one clique model. More generally, if a k by k zero-diagonal
block has rank(A-I)=1, write A=I+u*v. The diagonal equations imply
v*u=-k, so det(A)=1-k. Dyadic invertibility requires k-1 to be a power
of two. The clique-size bound leaves k=2,3,5. Twelve blocks cover at
most sixty ports. Thirteen size-five blocks would cover sixty-five;
replacing a size-five block by size three or two reduces the total by
two or three, and cannot give sixty-four. Fourteen is therefore
necessary and the supplied cover attains it.

This argument does not apply to an odd-denominator representation,
overlapping blocks, a correction of higher rank within a block, or a
different native encoding. It is not a lower bound for the required
computation.

## Literal scalar words

The review executes every supplied gate on each of the 112 independent
input columns. Every input is arbitrary. All target and source indices
are data fields; no initial zero, borrowed helper, or owned scratch is
used. It checks E, E^-1, E^T, and E^-T separately.

For a signed six-mode block, the in-place reflection code has twelve
unit additions and one negation. The final exchange has three unit
additions and one negation. This costs 124 real scalar primitives per
vertex. The eight blocks cost 992. The physical pair code and inverse
cost 940, so the 48-port scalar code costs 1932.

For a clique of size k, the three groups of k-1 unit additions and
one scale by -(k-1) implement I-J. Their costs are 102 for k=5 and
52 for k=3. Thus the small code costs 1278 and each full word costs
1932+1278=3210. Reversing or transposing the word preserves this
invoice under the stated tariff.

The independent column replay also accumulates the absolute row sums
at every changed row. The maximum prefix row norms are 44 for E and
E^-1, and 14 for E^T and E^-T. These bounds concern the scalar code
alone. They do not bound a recursive child's internal state.

The four words are valid at a common frame. This phrase is a binding
premise. It does not provide access to fields in different hole frames,
or make an accumulated controller chart free to change.

## Reproduction

Run from the workspace root:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/rank-thirty-review-20261020/check_review.py
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/rank-thirty-review-20261020/check_review.py
```

The expected status is `PASS_INDEPENDENT_RANK_THIRTY_RESPONSE`.
The two receipts must be byte-identical. The checker authenticates
the producer proof, checker, payload, receipt, freeze, and the two
underlying input payloads. It does not run or import producer code.
It uses exact integers and fractions.

The new-core-transfer lane supplied the full response, clique cover,
scalar words, and their producer checks. The root supplied the
reciprocal six-mode construction. The actual pair coordinates and
selected block come from the pinned cyclic and matching packets.
This lane supplied the distinct column replay, clique enumeration,
and the isotropic proof of the clique-size bound. OpenAI Codex
assisted this work.

No PR, push, or publication is authorized. Before any PR description,
read
/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md.
