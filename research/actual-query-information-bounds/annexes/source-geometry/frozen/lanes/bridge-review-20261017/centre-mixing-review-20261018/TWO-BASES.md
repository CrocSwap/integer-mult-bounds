# A two-basis proof of centre rigidity

The scalar centre restriction has a short algebraic explanation. Two
sets of eight actual ports suffice. The proof permits every entry of
the centre matrix to vary. It does not assume that the matrix is
symmetric.

## General criterion

Let `V` and `W` be invertible square matrices over a field. Set
`H=V^-1 W`. Form a bipartite graph with one vertex for each column of
`V` and one for each column of `W`. Join vertices `i` and `j` when
`H[i,j]` is nonzero.

The vector space of linear maps diagonal in both bases has dimension
equal to the number of connected components of this graph. In
particular, a connected graph forces every such map to be `cI`.

To prove this, write a common diagonal map as

```text
A V = V diag(lambda),    A W = W diag(mu).
```

Since `W=V H`, these equations give

```text
diag(lambda) H = H diag(mu).
```

On every edge, `lambda_i=mu_j`. Thus all labels in one connected
component are equal. Conversely, choose one scalar for each component.
Assign this scalar to each vertex in that component. Every entry of
the last matrix equation then holds. These assignments give all the
common diagonal maps and are independent.

The same proof works over a commutative ring if `V` and `W` are
invertible and every nonzero entry of `H` is a unit. In that case the
common diagonal module is free, with one generator per component.
The unit condition is needed to infer equality from
`(lambda_i-mu_j) H[i,j]=0`.

## The actual 16-port certificate

Use the current integer matrix `R` from the clean core with decompressed
SHA256 `a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa`.
Set

```text
P = [0, 7, 20, 27, 36, 46, 57, 111]
Q = [3, 6, 18, 21, 89, 92, 105, 109]
V = R[:,P],    W = R[:,Q].
```

Exact substitution gives `V^T V=W^T W=4I`. All actual binary port
labels within either set have dot product one, including the distinct
pairs. The forbidden-pair equations therefore say that both `V^T A V`
and `W^T A W` are diagonal. Since the Gram matrices are `4I`, this is
equivalent to `A` being diagonal in both bases.

Here `H=V^T W/4` is one half of the following integer matrix:

```text
 1  1  0  0  1  1  0  0
 0 -1  1  0  0  1 -1  0
 0  0 -1  1  0  0 -1  1
 0  0  1  0  1 -1  0  1
 0  1  1  1 -1  0  0  0
-1  1  0 -1  0  0 -1  0
-1  0  0  0  0  1  1  1
-1  0  0  1  1  0  0 -1
```

Its bipartite support graph is connected. `TWO-BASES.json` gives a
15-edge spanning tree on its 16 vertices. Every nonzero overlap is
`1/2` or `-1/2`. Thus the common diagonal module is exactly `cI`
over every commutative coefficient ring in which two is a unit.

This proves the scalar-I restriction directly from two orthogonal
bases. The independent `-2^71` determinant check remains a separate
certificate for the same restriction. The two-basis proof uses 112
within-basis off-diagonal equations; the determinant uses 63 equations
from the larger list. Neither proof assumes that `A` is diagonal in
the original coordinate basis.

## Why the graph hypothesis matters

Keep `V` and instead use the actual basis with port list

```text
[21, 37, 47, 76, 81, 87, 92, 110].
```

It also has Gram matrix `4I`, and all its within-basis binary dot
products are one. But its overlap graph with `V` has two components,
each with four vertices from either basis. Those two basis constraints
alone allow two independent scalar blocks. The checker verifies this
case. Thus the conclusion does not follow merely from having two
orthogonal bases; the connection between them is decisive.

The linear-algebra criterion is elementary. The contribution here is
its exact application to the current port geometry and to the physical
support restriction. This is an explanation of the obstruction, not
an additional supplier construction or a cost improvement. A changed
query or scatter space must be checked against its own basis graph.

OpenAI Codex assisted this derivation. The producer cut proof and the
coherent-port integer certificate supplied the starting result. No
frozen producer artifact was changed. No publication was made.
