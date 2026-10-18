# Dense B/C root-code floor

Let n>=1. The B_n line representatives are e_i and e_i+e_j, e_i-e_j
(i<j). For C_n replace e_i by 2e_i. Common nonzero scaling of the
representatives does not matter below. There are v=n² lines. Define the
**fixed dense binary pairing** B by B_rs=1 when r=s or the real/integer
representatives are orthogonal, and B_rs=0 otherwise. Every cost below is
rank over **F2**. This field is distinct from the coefficient field K.

Let K be any field of characteristic other than 2, R the line matrix over K,
and x,y nonzero vectors in K^n. Put S(x)={r:(Rx)_r != 0}. We prove

```
rank_F2 B[S(x),S(y)] >= n.                         (1)
```

Choose i with x_i!=0. The axis i lies in S(x). For every j!=i, at least one
of x_i+x_j and x_i-x_j is nonzero: otherwise adding gives 2x_i=0. Thus S(x)
contains a star consisting of its axis and one line from every incident
coordinate edge. Likewise S(y) contains a star anchored at some j.

The two signs of a coordinate edge have **identical rows and columns of B**.
Against an axis, orthogonality means that the axis is outside the edge.
Against another edge, the entry is 1 for the same edge or disjoint edges and
0 for distinct edges sharing a vertex. This includes both the diagonal and
the orthogonal opposite-sign pair. Therefore the chosen root signs do not
change the star submatrix.

For equal anchors, order the axis first and then the n-1 incident edges.
The star submatrix is I_n. For distinct anchors i,j, order rows as axis i,
edge ij, edges ik (k outside {i,j}); order columns as axis j, edge ij, edges
jk in the same k order. With r=n-2, its binary matrix is

```
       [ 1  0  1^T   ]
H_n =  [ 0  1   0^T  ].
       [ 1  0  J_r+I_r]
```

XOR the first row into each of the last r rows. The result is upper
triangular with unit diagonal. It is invertible over F2. The same-anchor
case covers n=1; the distinct-anchor formula starts at n=2. This proves (1)
by restriction to an actual n-by-n submatrix. No monotonicity in entries of
B is used; rank monotonicity is only under selecting rows and columns.

Now let P=D_1 R X and Q=D_2 R Y, where D_1,D_2 are invertible diagonal
matrices over K and X,Y have any common finite number m of columns. Require
M=P Q^T to have nonzero diagonal and zero off-diagonal entries on all
orthogonal pairs in the fixed integer geometry. The n axis lines give an
invertible diagonal principal minor of M, so rank_K(M)>=n. Since P and Q lie in n-dimensional root codes,
rank_K(M)=n. If t columns have both factors nonzero, rank-one subadditivity
gives t>=n. Diagonal rescaling does not change supports, and (1) charges
each of these t terms at least n. Consequently

```
sum_j rank_F2 B[supp(P_j),supp(Q_j)] >= n*t >= n².  (2)
```

Zero factors have empty support and cost zero. They do not count in t.
The proof uses ordinary transpose, not complex conjugation, and includes
arbitrary complex coefficients through K=C. It does not compare ranks of
the same matrix over K and F2: the two separate rank arguments are explicit.

The standard coordinate Gram factorization P=Q=R has n terms. Term i has
axis i and both signs on every incident edge. Its pairing block is one
1-by-1 unit block and n-1 all-one 2-by-2 blocks; its F2 rank is n.
The total is n²=v, and R R^T is admissible in every characteristic other
than 2. Thus (2) is sharp for both full B_n and C_n, for every n>=1.

## Boundaries

This is the dense-pairing, full-root-set, root-code factor class. It is not
the general T² conjecture, a minimum over arbitrary admissible pairings, a
claim for punctured B/C sets, or a physical supplier invoice. A sparse
pairing can destroy the star minor. In characteristic 2, x_i+x_j and
x_i-x_j may both vanish. Without the root-code hypothesis a singleton
factor can have a rank-one support block. These are executable controls,
not omissions hidden in the statement.

The standard transcript/rank-one arguments are prior linear algebra. The
new mechanism is the all-size sign-insensitive cross-star minor for these
two mixed-length root families, extending the fixed-coordinate examples
reported in PR2272 and PR2518. This is a written proof with finite exact
verification, not a theorem-kernel proof or independent human review.
