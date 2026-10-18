# Exact deletion thresholds for three prescribed two-port targets

Scope: binary nonempty proper-star observations at `k=2`, with three
distinct prescribed retained target edges and arbitrary values at every
other retained edge. The graph is `G = K_(2p) minus a perfect matching`.
The empty star is not included. The argument is self-contained and does not assume the predecessor's
higher-weight theorem. A separate Codex worker checked the mathematics;
this is not independent human review or machine-checked formalization.

**Theorem.** For every `p>=3`:

* A target triangle is impossible to decode after any allowed deletion.
* A target path of three edges whose four vertices are exactly two original
  matched pairs needs exactly `6p-11` deletions.
* Every other target triple needs exactly `6p-12` deletions.

At `p=2`, every triple of distinct edges is the exceptional path in the
four-cycle, and the optimum is one deletion, again `6p-11`.

## 1. Exact decoding is equivalent to being a bridge

Let `H=G-D` be the retained graph. Its observations are the binary sums of
the edge inputs incident to each vertex. If a retained edge `e` belongs to
a cycle, toggling all inputs on that cycle leaves every observation fixed
and changes the input at `e`. Consequently even nonlinear exact
postprocessing cannot recover that input.

Conversely, if `e` is a bridge, sum the vertex observations over one
component of `H-e` meeting `e`. Every internal edge is counted twice and
`e` is the only crossing retained edge, so this sum is exactly its input.
Thus a target triple is simultaneously recoverable if and only if all
three target edges are bridges of `H`.

In particular, a target triangle is impossible. Otherwise the target
graph is a forest, with one of the four forms `3K2`, `P3+K2`, `K1,3`, or
`P4`.

## 2. The deletion lower bound and all equality cases

Write `n=2p` and `E=2p(p-1)`. If three target edges are bridges of `H`,
then `J=H-F` has `c(H)+3>=4` connected components. A vertex set of size `s`
contains at least `max(0,s-p)` complete original matched pairs, so it
induces at most

```
f(s) = binom(s,2)-max(0,s-p)
```

edges. For component sizes `s_1,...,s_c`, therefore,
`|E(J)| <= sum_i f(s_i)`.

The required concentration argument is strict. If two blocks have sizes
`x>=y>=2`, transfer one vertex from the smaller to the larger. The increase
in the bound is

```
[f(x+1)-f(x)]-[f(y)-f(y-1)]
  = x-1[x>=p]-(y-1-1[y-1>=p]).
```

This is positive except possibly when `x=y=p`. That exception is impossible
in a partition of `2p` vertices into at least four nonempty blocks. Hence
the largest possible sum for `c>=4` blocks occurs with sizes
`n-c+1,1,...,1`. Also `f(s)` is strictly increasing for positive `s`, so
the bound can equal `f(n-3)` only when `c=4` and the component sizes are
`n-3,1,1,1`.

For `p>=3`,

```
|D|+3 = E-|E(J)| >= E-f(n-3) = 6p-9,
```

giving `|D|>=6p-12`. Equality forces three singleton vertices `A` and
one remaining block `B`. If `m(A)` is the number of original matched
pairs wholly inside `A`, the number wholly inside `B` is `p-3+m(A)`.
Thus equality holds only when `m(A)=0`, and `J` contains every edge
induced on `B`.

Moreover equality gives `c(J)=4` and `c(H)=1`; the three targets connect
these four blocks as a tree. Equivalently, the three vertex-incidence
rows indexed by `A`, restricted to the targets, form an invertible
three-by-three matrix. This proves the full equality condition without
invoking any higher-weight rigidity theorem.

## 3. Constructing a decoder from three selected vertices

Choose three vertices `A` whose incidence rows restricted to the target
edges form an invertible matrix. Let `U` be all edges incident to at least
one vertex of `A`. All targets belong to `U`. Delete `D=U-F`; a change of
basis in the three selected vertex observations gives the three target
unit rows. Since `|E(G[A])|=3-m(A)`,

```
|U| = 3(2p-2)-(3-m(A)) = 6p-9+m(A),
|D| = 6p-12+m(A).
```

For a target forest, three selected rows are invertible precisely when
the selection contains all but one vertex of each nontrivial target-tree
component. To see this, the incidence rows of a tree have their unique
dependence equal to the sum of all its vertex rows; deleting any one row
leaves an independent set of size equal to its edge count. Components
have disjoint target columns. Selected vertices outside the targets give
zero rows and cannot occur in an invertible selection.

## 4. Checking the four forest forms

For `K1,3`, select any three of its four vertices after excluding one
endpoint of a matched pair, if necessary. Its four vertices cannot
contain two complete matched pairs: that would pair the center with a
leaf, contradicting the existence of that target edge. Thus a selection
with `m(A)=0` exists.

For `P4`, every three of its four vertices are an invertible selection.
A three-vertex selection avoiding complete matched pairs exists exactly
when the four vertices do not consist of two complete matched pairs.
In the exceptional case every such selection has `m(A)=1`. By the
equality characterization in Section 2, no other kind of selection can
attain `6p-12`; the integer lower bound improves to `6p-11`, achieved by
Section 3. Along a path `a-b-c-d`, the exceptional original pairs are
necessarily `{a,c}` and `{b,d}`.

For `P3+K2`, write the path as `a-b-c` and the disjoint edge as `d-e`.
If `a,c` are not mates, the path's three vertices belong to three distinct
original pairs. Select either endpoint of `d-e`, then two path vertices
whose original pairs differ from its pair. If `a,c` are mates, select
`b` and one of `a,c`. Neither `d` nor `e` belongs to the exhausted pair
`{a,c}`, and at least one lies outside the pair of `b` since `d,e` are
adjacent. Select that endpoint. Both cases give `m(A)=0`.

For `3K2`, the three disjoint edges collectively use at least three
original pairs, since two pairs contain only four vertices. Take one
edge whose endpoint-pair set is `{P,Q}`. Some other edge has an endpoint
in a pair `R` outside `{P,Q}`; select that endpoint. From the third edge,
select an endpoint in a pair `S!=R`, which is possible because its two
endpoints are adjacent. Finally select from the first edge the endpoint
whose pair differs from `S`. These are one endpoint of each target edge
and have three distinct original pairs, as required.

## 5. Why four-block enumeration is complete

The finite partition checker does not merely search a sufficient subclass.
Given any valid deletion set D, let J be the retained nontarget graph and
contract its connected components. The three retained targets form a forest
in that quotient: otherwise a target would be on a cycle in H. If the
quotient has more than four vertices, identify two vertices in different
forest components, including isolated vertices. This preserves all three
target edges and acyclicity. Repeat until the quotient is a tree on four
vertices. Pull these four labels back to the original vertices and restore
every deleted nontarget edge whose endpoints have the same label. None of
these restorations crosses a block, so the target edges remain bridges.
The number of deletions cannot increase.

Conversely, any four-block partition whose target quotient is a tree gives
a valid decoder by deleting every crossing nontarget edge. A cut of that
tree yields each target unit row. Thus the minimum over the enumerated
four-block partitions equals the unrestricted minimum deletion count in
this observation model. Blocks need not induce connected graphs for this
converse. The independent checker instead enumerates every three-dimensional
binary cut subspace and does not use this reduction.

## 6. Boundary and provenance checks

For `p=3`, `n-3=3`, the concentration proof remains strict and
`f(n-3)=3`; no step requires `p>=5`. For either selection used above,
the remaining induced graph on `n-3` vertices is connected for `p>=3`,
although the algebraic decoder construction does not require a separate
connectivity assertion. For `p=2`, the graph is a four-cycle and deleting
its single nontarget edge leaves a three-edge path, so all targets become
bridges.

The pinned predecessor files inspected for scope and comparison were
`research/asymmetric-hypercube-decoder/HIGHER-GRAPH.md` and
`HIGHER-WEIGHTS.md` at PR #669 head
`7d526020fc368ce4157cd436995c2f4fcf683318`. The former supplies the
selectable-target lower bound; the latter explicitly leaves larger
prescribed-target budgets unresolved. The bridge and strict partition
arguments above independently verify the needed lower bound and its
equality cases. This audit makes no claim about empty-star observations,
general `k`, physical helper costs, or multiplication bounds.

Prepared for woklerx with substantial OpenAI Codex assistance in proof,
review, implementation and writing. Apache-2.0.
