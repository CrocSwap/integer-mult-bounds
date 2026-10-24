# Rank-one residue lift counts

Let K be a finite field of order q. Let R be a finite-dimensional associative
unital K-algebra with K central, with Jacobson radical J, and suppose the
canonical map K -> R/J is an isomorphism. In particular, R is local and
R = K direct-sum J as a K-vector space. Put d = dim_K J and z = q^d.
Commutativity and J^2 = 0 are not assumed.

Use the two-role alphabet of #4099/#4243/#4276. A paid factor is
P(u,y) = I + u y^T, where u belongs to R^2 and y belongs to K^2. Any map in
GL_2(K) is free anywhere in a word. The cost is the minimum number of paid
factors. All multiplication orders below are algebraic product orders;
column-vector execution applies the rightmost factor first.

Fix A in M_2(K) of rank one. The target family is

```text
L_A = { A + N : N in M_2(J) }.
```

There are z^4 targets in this family.

## Theorem

For every such R and A, exactly

```text
q*z^2 - q + 1                 targets have cost 1,
z^4 - q*z^2 + q - 1           targets have cost 2.
```

No target in L_A has cost zero or needs a third factor. Consequently the
counts depend only on q and d, independently of radical multiplication and
independently of the chosen rank-one residue A.

The new contribution is this uniform counting law. The two-factor upper
bound and the one-factor column criterion are predecessor results of
Nick Petalas's #4276, Theorems A and D, following #4243 and Wentao Li's #4099.
We spell out their specializations to identify precisely what is counted.

## One-factor specialization

For any K-algebra R and any target M, cost(M) <= 1 holds if and only if there
are nonzero v,w in K^2 with Mv = w.

For the forward implication, conjugating by a free map preserves the paid
alphabet, so put a word of cost at most one in the form M = P(u,y) S, with
S in GL_2(K). Choose nonzero w in ker(y^T), or any nonzero w if y = 0.
Then v = S^-1 w is nonzero and Mv = w.

Conversely, suppose Mv = w with v,w nonzero and scalar. Choose
S in GL_2(K) such that Sv = w. The K-linear map
M S^-1 - I : K^2 -> R^2 kills w. Its image therefore has K-dimension at
most one, so it is u y^T for some u in R^2 and y in K^2. Thus
M = P(u,y) S. This is also the two-dimensional form of #4276 Theorem A.

For M = A + N in L_A, reduction modulo J now gives

```text
cost(M) <= 1  iff  some v in K^2 has N v = 0 and A v != 0.
```

The condition A v != 0 is necessary. For example over K[e]/e^2,
M = diag(1+e,0) has a common scalar kernel line, but that line is ker(A).
This target costs two, not one. The verifier checks this distinction against
the complete literal one-factor image, without using the criterion to build it.

## Counting the eligible kernel lines

There are q+1 lines in K^2, and ker(A) is exactly one of them. Thus there
are q eligible lines L, namely those not equal to ker(A).

Choose a K-basis j_1,...,j_d of J and write

```text
N = sum_i j_i B_i,   B_i in M_2(K).
```

For an eligible line L define E_L to be the set of tuples (B_1,...,B_d)
with every B_i killing L. A 2-by-2 matrix killing a fixed line is an
arbitrary linear map K^2/L -> K^2, so there are q^2 choices for each B_i.
Hence |E_L| = q^(2d) = z^2.

If L and L' are distinct, any B_i killing both is zero, since the two lines
span K^2. Therefore E_L intersects E_L' in the single tuple N = 0. The
nonzero parts E_L minus {0} are disjoint, while the zero tuple belongs to
every event. Their union has cardinality

```text
1 + q*(z^2 - 1) = q*z^2 - q + 1.
```

This argument also covers d = 0, when the zero tuple is the only tuple.
No product of radical elements occurs in the count.

## Exactness of the two costs

A zero-cost target is a scalar invertible matrix. Every target in L_A has
singular residue A, so none has cost zero. The counted union therefore
consists of targets of exact cost one.

Every target in L_A has a unit entry, since some entry has nonzero scalar
residue. Permutation maps move that entry to (1,1). Write the resulting
matrix as [[a,b],[c,d0]], with a a unit. The word used in #4276 is

```text
F1 = [[a,0],[c,1]] = P((a-1,c), e1),
F2 = [[1,a^-1 b],[0,d0-c a^-1 b]]
   = P((a^-1 b,d0-c a^-1 b-1), e2),
F1 F2 = [[a,b],[c,d0]].
```

These identities hold in a noncommutative algebra with exactly the displayed
orders. The surrounding permutations are free. Thus every target in L_A
costs at most two, and all z^4 minus the counted union have exact cost two.
This completes the counting proof, using the credited predecessor upper bound.

There are (q^2-1)^2/(q-1) = (q-1)(q+1)^2 possible rank-one residues A.
Indeed A = u v^T with u,v nonzero, and exactly q-1 such pairs give the same A.
Multiplying the two per-residue counts by this number gives the complete
rank-one-residue census. The verifier enumerates every one of these residues
in its finite examples, rather than assuming their counts agree.

## Scope

This is a scoped algebraic counting proof. It does not classify zero-residue
targets, residue-field extensions, matrix-block residues, products of local
algebras, or more than two roles. It supplies no native producer, routing,
restoration, precision, stock, recursive invoice, supplier admission or
complete multiplication theorem. Independent human and formal proof-kernel
review are unclaimed.

Produced by Nick Petalas. Predecessor credit is detailed in README.md.
