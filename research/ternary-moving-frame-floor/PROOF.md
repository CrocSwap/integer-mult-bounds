# Four unrestricted terms cannot beat thirteen ternary lines

## Statement and contract

Let K be any field of characteristic zero. Let P contain the thirteen vectors
in {-1,0,1}^3 whose first nonzero coordinate is 1, in lexicographic order.
Let X be the 13 by 3 matrix with those rows and G = X X^T. Define the binary
13 by 13 matrix B by

```text
B_st = 1 if s=t or p_s dot p_t=0, and 0 otherwise.
```

For an exact decomposition G = sum_j u_j v_j^T over K, set R_j = supp u_j,
A_j = supp v_j, and charge

```text
C = sum_j rank_F2 B[R_j,A_j].
```

The factors may leave the evaluation code, use arbitrary characteristic-zero
coefficients and cancel. Frames are unrestricted. The pairing B and the
thirteen ports are fixed. No nonnegativity or Gram-factor constraint is
imposed on the factors.

**Theorem.** Every decomposition with at most four terms has C >= 14.
Every decomposition with at most three terms has C >= 18. The latter bound
is attained by the coordinate decomposition. No attainment of 14, or exact
four-term optimum, is asserted.

The below-thirteen four-term question of Aaron Wang's PR2518 is therefore
settled negatively for its full-orthogonality pairing. This is a scoped
mathematical obstruction, with a finite exact rank lemma. It is not a search
failure, physical decoder construction or complete multiplication theorem.

## 1. The exact restriction-rank lemma

Write E = im X. For 0 <= n <= 13 define

```text
e(n) = min rank_F2 B[supp(Xa),A],
       over nonzero a in K^3 and A subset of P with |A|=n.
```

The exact values, in increasing n, are

```text
n     0  1  2  3  4  5  6  7  8  9 10 11 12 13
e(n)  0  1  2  3  3  4  4  5  5  6  6  6  7  7.
```

Here is a complete finite reduction, including extension fields K. The zero
ports of Xa are the rational vectors p in P satisfying p dot a = 0.
If there are at least two, take two distinct zero ports p,q. They are
linearly independent, and a is a nonzero K-multiple of their rational cross
product d = p cross q. The zero-port set is exactly that of d. Three
independent zero ports would force a=0, which is excluded.

If there is one zero port p, choose any other port q. The cross product d
vanishes at p, so supp(Xd) is a subset of supp(Xa). If there are no zero
ports, choose any two distinct ports. The same support containment holds.
Deleting rows cannot increase binary rank. Consequently it suffices to
check primitive cross products of all 78 unordered port pairs.

After division by the coordinate gcd and a sign change making the first
nonzero coordinate positive, there are exactly 25 distinct cross products
and 25 distinct supports. Their support sizes are 9, 10 or 11. The checker
independently reconstructs these directions from primitive vectors in
[-2,2]^3 having at least two zero ports. This box is complete because every
cross-product coordinate is a difference of two products in {-1,0,1}.
Distinct ports are never proportional, so two zero ports are independent.

For every one of these 25 supports and every one of the 8,192 subsets A,
the checker computes the binary rank twice, using row elimination with high
pivots and transposed-column elimination with low pivots. All 204,800
comparisons agree. Minimizing by |A| gives the displayed table. The generated
receipt includes an attaining support/subset witness for each entry.
Every listed direction is rational and hence belongs to K, so these
witnesses establish equality as well as the lower bounds. In particular,
every nonzero vector in E has at least nine nonzero entries.

This finite lemma is the only exhaustive premise. The argument below
quantifies over all decompositions, rather than enumerating frames.

## 2. A code side is forced at four terms

The rows of X include the coordinate vectors, so X has rank three. Direct
summation also gives X^T X = 9 I_3. Thus G has rank three over K, its column
and row spaces equal E, and its thirteen columns are pairwise nonproportional.
The last assertion follows from the injectivity of X and the distinct
projective representatives p_t, since G[:,t] = X p_t.

Remove every zero outer product, leaving k active terms. Necessarily k>=3.
Write U and V for the 13 by k factor matrices, so G=UV^T. Both have rank
at least three. When k=3 both have rank three and both column spaces equal E.

When k=4, U and V cannot both have rank four: U would be injective as a map
K^4 to K^13 and V^T would be onto K^4, making UV^T have rank four. At least
one therefore has rank three. Its column space equals E, because it contains
the rank-three column space of G or G^T. The symmetry of B makes the tariff
unchanged by transposing the decomposition. We may take the code side to be U.

This permits arbitrary vectors outside E on the other side. It is precisely
why the result covers moving-frame decompositions beyond a fixed one-extra
identity family. The rank argument is classical and is consistent with
joaqcoo's PR1224 one-sided representation context; that general observation
is not claimed as new.

## 3. Three active terms

For k=3, each nonzero v_j lies in E and has support size at least nine.
Each u_j is also a nonzero code vector. The finite lemma therefore gives
rank_F2 B[R_j,A_j] >= min_{9<=n<=13} e(n) = 6. Summing gives C>=18.

The coordinate decomposition uses u_j=v_j=X e_j. Direct evaluation gives
three tariff ranks of six, so it attains 18. This elementary fixture is
constructed from the definitions; no predecessor census is replayed.

## 4. Four active terms

Let n_j=|A_j|. Each n_j is between 1 and 13. Each column of G needs at least
one nonzero coefficient among the corresponding rows of V. If a column uses
only one term, it is proportional to that term's u_j. Because the thirteen
columns of G are pairwise nonproportional, each u_j can serve at most one
such column. At most four columns use only one term; every other column uses
at least two. Therefore

```text
n_1+n_2+n_3+n_4 >= 4 + 2*9 = 22.
```

The restriction-rank lemma gives C >= sum_j e(n_j). Exhausting the 13^4
ordered size tuples, retaining those with sum at least 22, gives

```text
min sum_j e(n_j) = 14,
```

with one attaining relaxation tuple (1,1,7,13). The checker enumerates every
tuple. This tuple is not asserted to come from an actual factorization.
For a short direct confirmation, e(n)>=(n+1)/2 for 1<=n<=13, with equality
only at n in {1,11,13}. A bill below 14 would be at most 13, hence would
require sum n_j=22 and four equality sizes. Four members of {1,11,13}
cannot sum to 22. Thus C>=14. Combining with the three-term case proves
the theorem for every decomposition with at most four terms.

## Scope and credit

Aaron Wang / navinor's PR2518 poses the unrestricted four-term question,
building on his PR2272 screen. DreamingOfClouds's PR2125, PR2228 and PR2111
supply the dense-polar/COPY model; Cinna Davis's PR2240 supplies the narrower
one-extra fixed-frame construction; joaqcoo's PR1224 supplies the retained
one-sided factorization context. The source packages retain their credit.
The new result is this complete 25-direction restriction-rank certificate
and its application to all four-term factorizations on the thirteen ports.

The fixed pairing, characteristic zero and at-most-four-term restrictions
are essential to the proved scope. Five factors can have both factor
matrices of rank four, so the forced-code-side argument does not extend
automatically. Changed pairings, masked identities, shared delivery and
physical/native/ownership/restoration/compiler/precision/stock/outer costs
are outside this theorem. No new kappa or selected-frontier change follows.
Independent human and formal proof-kernel review are unclaimed.

This proof was produced by Nick Petalas. Apache-2.0.
