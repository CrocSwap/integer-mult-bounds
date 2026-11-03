# Exact dense B3 and C3 term tariffs

Let K be any field with characteristic other than two. Use the nine full B3
root lines represented by e_i and e_i+e_j, e_i-e_j for i<j. For C3 replace
each e_i by 2e_i. Let R be the resulting line matrix. The fixed binary
pairing B has entry one on its diagonal and on the pairs orthogonal in the
integer root geometry, and zero elsewhere. Orthogonality is determined before
passing to K. All costs below are ranks over F2, separately from K.

For a nonzero x in K^3 let S(x) be the nonzero coordinates of Rx, and let
A(x) be the nonzero coordinate indices of x itself. Then, for all nonzero x,y,

```text
rank_F2 B[S(x),S(y)] = 3  if |A(x)|=1 or |A(y)|=1,
                       5  otherwise.
```

Independent invertible diagonal rescaling of the two root codes does not
change this statement, since it preserves supports. Zero factor columns have
cost zero and are omitted throughout.

## Remove repeated signed-edge rows

The two roots on the same unsigned edge {i,j} have identical pairing rows
and columns. Against an axis, the entry is one exactly when the axis is
outside the edge. Against another edge, it is one exactly when the edges
are identical or disjoint. In particular the two-by-two block on opposite
signs of one edge consists of ones, including its diagonal.

At least one of x_i+x_j and x_i-x_j is nonzero exactly when at least one of
x_i,x_j is nonzero. The nontrivial implication uses 2 != 0 in K. Thus, after
removing identical rows, the row labels are precisely the axes in A(x)
and the unsigned edges incident with A(x). The same applies to columns and
A(y). Removing identical rows and columns preserves binary rank. Consequently
the cost depends only on these two coordinate supports. Coefficient ratios
and the number of surviving signs on an edge cannot affect it.

## One coordinate on either side

If |A(x)|=1, the reduced row set contains one axis and its two incident
edges, so the rank is at most three. The cross-star theorem of ywz65's
[PR2582](https://github.com/CrocSwap/integer-mult-bounds/pull/2582),
[retained proof](../bc-dense-root-code-floor/PROOF.md), gives rank at least
three for every pair of nonzero root-code factors. Hence the rank is three.
Transpose gives the same conclusion when |A(y)|=1. This step uses the cited
theorem as a premise; its all-size proof and verification are predecessor work.

## At least two coordinates on both sides

Write A=A(x), C=A(y), a=|A| and c=|C|. Every unsigned edge is incident with
each of A and C. Order the three edges as {2,3},{1,3},{1,2}, with indices
1,2,3 for the axes. Distinct edges share a vertex, so their pairing block
is I_3. The reduced matrix is

```text
          [ J_(a,c)   E_A   ]
          [ E_C^T    I_3   ],
```

where E_A selects the rows of I_3 indexed by A, and E_C selects those indexed
by C. Binary block elimination gives the exact rank

```text
3 + rank_F2 (J_(a,c) + I_3[A,C]).
```

The remaining matrix has rank exactly two whenever a,c are in {2,3}:

- If a=c=2 and A=C, it is the invertible two-by-two off-diagonal matrix.
- If a=c=2 and A!=C, their intersection has size one. Up to row and column
  permutation it is [[0,1],[1,1]], also invertible.
- If a=2,c=3, its rows are distinct nonzero vectors, so its rank is two.
  The a=3,c=2 case follows by transpose.
- If a=c=3, it is J_3+I_3. Its rows sum to zero and any two are independent,
  so its rank is two.

The total rank is therefore five. This proves every case of the formula.

## Exact invoice consequence

For any finite list of root-code rank-one terms, let m be the number with
both factors nonzero, and let h count those for which both coefficient vectors
use at least two coordinates. Additivity of the declared term prices gives
the exact total

```text
cost = 3m + 2h.
```

In particular, an admissible B3/C3 decoder of cost nine has exactly three
nonzero terms and h=0. Indeed, PR2582's axis-minor argument requires m>=3;
the displayed formula then forces m=3 and h=0. Conversely any admissible
three-term decoder with h=0 has cost nine. Admissibility is essential here:
the term formula alone does not assert that arbitrary chosen terms form a
decoder. The existence and optimality of cost nine are already in PR2582.
The new result identifies the exact two-rank surcharge on the other terms.

## Scope

This is a written algebraic theorem, corroborated by a finite standalone
checker. It assumes the full root configuration, characteristic other than
two, root-code factors and the fixed dense pairing. Sparse pairings, deleted
lines and external factors can change the cost. No physical native maps,
helper access or restoration, hosting, precision, stock, tape, recursive
compiler or multiplication theorem is supplied. No kappa or selected
frontier change follows. Independent human and formal proof-kernel review
are unclaimed.

The new formula and proof were produced by Nick Petalas. Credit ywz65's
PR2582 for the model, cross-star bound and all-size floor; Aaron Wang's
PR2272/PR2518 for the root generators and finite screens; and DreamingOfClouds'
PR2228/PR2277 for the root-code floor method and its retained predecessor
lineage. Apache-2.0.
