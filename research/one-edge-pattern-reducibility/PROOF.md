# One edge cannot support an irreducible five-dimensional pool

This scoped proof was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

## Statement and imported premise

Work over F2. Let P be a three-dimensional space of zero-diagonal W-by-W
matrices. Its complete noncoordinate pool is

```
C(P) = {xy^T : y^T x = 1, off(xy^T) in P, off(xy^T) != 0}.
V = sum_{N in C(P)} im(N).
```

Suppose P contains exactly one off-diagonal matrix unit p=E_ab. Put
E=span(e_a,e_b), and let pi be the coordinate projection deleting a and b.
The pool preserves V, so its restrictions to V are well defined.

**Theorem.** If dim V=5, every N in C(P) preserves E. More precisely,
each N either has image contained in E or annihilates E. Consequently
the restricted pool is reducible. Every irreducible restricted pool with
these hypotheses has dim V<=4.

The proof uses the following result of CubeJerry's
[PR6782, Section 3](https://github.com/CubeJerry/integer-mult-bounds/blob/685457252b51b9c7932ece363365bdf0b12c9c31/research/bit-three-relation-core/PROOF.md).
Let P0=span(p). Projectors whose patterns lie in P0 have image in E.
For each nonzero coset alpha of P/P0, the images modulo E of all pool
members in that coset span a space of dimension at most one. Thus

```
dim V <= dim E + 2^(3-1)-1 = 5.
```

This edge-quotient result is a cited mathematical premise, not a new
result or an independently audited claim of this package. Its proof builds
on Nick Petalas's PR5921 diagonal-deletion fiber lemma and the retained
woklerx pattern-space lineage. Exact citation metadata is in ORIGINS.json.

## Proof of the new theorem

The two lifts of p are e_a(e_a+e_b)^T and (e_a+e_b)e_b^T.
Their images span E, so E is contained in V.

There are exactly three nonzero cosets alpha_1, alpha_2, alpha_3 of P/P0,
and their sum is zero. If dim V=5, then dim pi(V)=3. The three at-most-one-
dimensional quotient image spaces must therefore be nonzero and linearly
independent. Choose N_i=x_i y_i^T from coset alpha_i, for i=1,2,3.
The vectors pi(x_1), pi(x_2), pi(x_3) are linearly independent.

Since the three cosets sum to zero,

```
off(N_1+N_2+N_3) in P0.
```

In particular the block with rows outside {a,b} and columns in {a,b}
vanishes. Let X have columns pi(x_i), and let Y have rows y_i restricted
to E. That block equation is XY=0. The three columns of X are independent,
so X is injective and Y=0. Each selected N_i annihilates E.

Now take any N=xy^T in C(P). If pi(x)=0, its image is contained in E.
Otherwise its pattern lies in some alpha_i. The imported quotient result
and the fact that the field is F2 give pi(x)=pi(x_i): a one-dimensional
binary space has only one nonzero vector. The off-diagonal difference of
N and N_i lies in P0. Its outside-row/E-column block is therefore

```
pi(x_i) (y|E + y_i|E)^T = 0.
```

Here pi(x_i) is nonzero and y_i|E=0. It follows that y|E=0, so N
annihilates E. This proves the asserted dichotomy for every pool member.

Thus the nonzero two-dimensional space E is a common invariant subspace
strictly inside the five-dimensional V. The restricted pool is reducible.
Combining this exclusion with the imported upper bound five proves the
irreducible upper bound four. This does not assert that four is attained.

## A reducible pool attaining joint-image dimension five

The conclusion is reducibility, not a smaller unrestricted joint-image
bound. Here is a concrete attaining example on coordinates 0,...,5:

```
P = span(E01, (e3+e4)e2^T, (e4+e5)e2^T).
```

Exactly one nonzero element of P is a matrix unit, namely E01.
The three nonzero patterns supported in column 2 each have exactly two
rows in {3,4,5}. Their unique idempotent lifts are

```
(e2+e3+e4)e2^T, (e2+e4+e5)e2^T, (e2+e3+e5)e2^T.
```

For a direct completeness argument, the two prescribed rows force the
covector to be e2, and idempotence forces the coordinate-2 entry of the
image vector to be one. No pattern obtained by adding E01 to one of these
three column patterns is realizable: entries (0,1) and (i,2), i>=3,
would force the absent off-diagonal entry (0,2) in a rank-one matrix.
Together with the two lifts of E01, these are the complete five members.

The last three image vectors are independent. Their sum is e2, and none
is zero or equal to another. Their span is disjoint from span(e0,e1).
Hence dim V=2+3=5. All five projectors preserve E=span(e0,e1), as required.
Padding by zero coordinates gives the same example at every W>=6.

## What the finite enumeration covers

The verifier enumerates all binary rank-one idempotents at W=5 and W=6,
excluding zero off-diagonal patterns. It fixes the unique directed edge
to E01, which any other directed edge can reach by permuting coordinates.

For each realized pattern q, remove its E01 bit to obtain its quotient
key. Every equality case has all three nonzero quotient cosets realized,
by the imported quotient bound. It therefore occurs among triples of
distinct realized keys q,r,q+r. Ordering q<r<q+r counts each such quotient
plane once. Their inverse images under deletion of the E01 bit are
exactly the spaces span(E01,q,r). Testing all seven nonzero patterns
retains precisely the spaces with one edge. The verifier reconstructs
their complete pools, computes each joint-image rank and checks the
edge-space action for every dimension-five case.

The resulting counts concern spaces with all three nonzero quotient
cosets realized. They are not counts of every three-dimensional pattern
space. They count representatives with fixed edge E01, not conjugacy
classes. Finite enumeration corroborates the written argument; it does
not prove the theorem at unbounded W.

## Boundary of the result

The field is F2, the pattern dimension is three, and the pool is complete
and excludes coordinate projectors. Adding other patterns or coordinate
calls to a word need not preserve E. The theorem concerns the restrictions
to the joint image, not a cost-free physical change of basis.

The remaining one-edge active dimensions at most four, zero-edge pools,
three-relation diagonal words, rational frame realization, arbitrary dirty
helpers, chronological restoration, native operators and complete recursive
invoices are separate questions. No supplier, saving in kappa, selected-
frontier change or complete multiplication theorem is claimed.
