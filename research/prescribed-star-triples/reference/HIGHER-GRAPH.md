# The complete higher-target hierarchy for signed two-ports

**All generalized weights for `k=2`; no new κ.** The first two generalized
weights do not distinguish the proper-star code with and without the empty
star when `p>=4`. Higher weights do. This note determines both complete
hierarchies and gives their precise interpretation as deletion thresholds
for a selectable set of targets. It also supplies upper bounds for higher
k by fixing a common signed face; those bounds are not asserted to be exact.

## The theorem

A signed two-port chooses one coordinate from each of two different original
pairs. Let `C^-_{p,2}` be the binary evaluation span of the nonempty proper
stars, and let `C^+_{p,2}` also include the empty star. For a binary code C,
write `d_r(C)` for the smallest union of supports of an r-dimensional
subcode. Put

```text
n = 2p,
E = 2p(p-1),
A_r = E - binom(2p-r,2) + max(0,p-r).
```

For every `p>=2`, the nonempty-star code has dimension `2p-1`, and

```text
d_r(C^-_{p,2}) = A_r,                   1<=r<=2p-1.       (1)
```

For every `p>=3`, the empty-allowed code has dimension `2p`, and

```text
d_1(C^+_{p,2}) = 2p-2,
d_r(C^+_{p,2}) = min(A_r, E-floor((2p-r+1)^2/4)),
                                        2<=r<=2p-1,
d_(2p)(C^+_{p,2}) = E.                                    (2)
```

At `p=2`, the two codes coincide and have hierarchy `(2,3,4)`. This is a
separate boundary case, not an extra rank in (2).

For example, `p=4` gives 24 signed two-ports:

| r | `d_r(C^-)` | `d_r(C^+)` | Selectable-target deletions, `C^-` | Selectable-target deletions, `C^+` |
| --- | --- | --- | --- | --- |
| 1 | 6 | 6 | 5 | 5 |
| 2 | 11 | 11 | 9 | 9 |
| 3 | 15 | 15 | 12 | 12 |
| 4 | 18 | 18 | 14 | 14 |
| 5 | 21 | 20 | 16 | 15 |
| 6 | 23 | 22 | 17 | 16 |
| 7 | 24 | 23 | 17 | 16 |
| 8 | — | 24 | — | 16 |

The last two columns are `d_r-r`. A selectable target set means that some
set of r retained coordinates attains the bound. An arbitrary prescribed
set of r targets can require a different number of deletions.

## Relation to the known graph-code theorem

The signed two-ports are the edges of the graph obtained from the complete
graph on `2p` vertices by removing the original p matched pairs. Each
singleton star is a vertex-incidence row. Thus `C^-` is the binary cut code
of this graph, sometimes called the cocktail-party graph.

The general connection between binary incidence codes and graph cuts is
established in José Martínez-Bernal, Miguel A. Valencia-Bucio, and Rafael H.
Villarreal, [*Generalized Hamming weights of projective Reed–Muller-type
codes over graphs*](https://arxiv.org/html/1812.04106v2), arXiv:1812.04106v2,
16 August 2019, Corollary 2.13. For a connected graph with n vertices, that
corollary identifies the r-th generalized weight of its binary incidence
code with the minimum number of edges whose removal creates r+1 connected
components, for `1<=r<=n-1`.

We credit that general bridge. The proof below derives the explicit
matched-pair formulas and treats the extra constant row directly; it does
not infer (2) by applying the incidence-code theorem to a different code.
No claim of literature-wide novelty for the graph invariant is needed.

## Restriction kernels turn weights into an edge optimization

Let G be the graph above. Let H retain any subset of its edges, on all n
vertices; isolated vertices count as components. Write `c(H)` for its
number of connected components. The binary incidence matrix of H has rank
`n-c(H)`: a vertex labeling lies in its left kernel precisely when it is
constant on each component.

The all-one edge row belongs to that incidence row span exactly when H is
bipartite. Indeed, expressing that row is the system `a_u+a_v=1` on all
edges, which is precisely a two-coloring. Put `epsilon(H)=0` when H is
bipartite and `epsilon(H)=1` otherwise. The matrix with the constant row
adjoined therefore has rank `n-c(H)+epsilon(H)`.

G is connected for `p>=2`. For `p>=3` it also contains a triangle, so its
constant row is independent of the incidence rows. This proves the code
dimensions stated above. The kernels of restriction from the full code to
the coordinates retained in H have dimensions

```text
C^-: c(H)-1,
C^+: c(H)-epsilon(H).                                    (3)
```

An r-dimensional subcode supported on deleted coordinates exists exactly
when the corresponding restriction kernel has dimension at least r.
Consequently, `d_r(C^-)` is E minus the largest number of edges that can be
retained in a graph with at least r+1 components. For `C^+` there is one
additional possibility: a bipartite retained graph with at least r
components. We now optimize these two possibilities.

## Arbitrary retained components

A set of s vertices contains at least `max(0,s-p)` complete original matched
pairs. Its induced graph therefore has at most

```text
f(s) = binom(s,2)-max(0,s-p)
```

edges. This bound is attained by choosing as few complete matched pairs as
possible. For `s>=1`, the increments

```text
f(s+1)-f(s) = s - 1[s>=p]
```

are nondecreasing, and `f(1)=0`. If a partition has two nonsingleton blocks,
move a vertex from a smaller one to a largest one. The sum of f over its
block sizes cannot decrease. Repeating shows that, for r+1 blocks, that
sum is at most `f(n-r)`. A partition into more blocks has the same upper
bound, for example by grouping its blocks into r+1 parts.

Take one vertex block of size n-r that attains f, and r isolated vertices.
Retain all induced edges in the large block. This reaches `f(n-r)` edges,
while retaining at least r+1 components. Thus

```text
d_r(C^-) = E-f(n-r)
          = E-binom(n-r,2)+max(0,p-r),
```

proving (1). These witnesses can equally be obtained from the independent
singleton-star rows at the r isolated vertices.

## Bipartite retained components

A bipartite component on s vertices has at most `floor(s^2/4)` edges. This
function also has nondecreasing increments for positive integer s and is
zero at s=1. The preceding concentration argument shows that a bipartite
graph with at least r components has at most

```text
floor((n-r+1)^2/4)
```

edges.

For `r>=2` this bound is attained inside G. Set `s=n-r+1` and take a complete
bipartite graph with side sizes `floor(s/2)` and `ceil(s/2)`, leaving r-1
isolated vertices. Place whole original matched pairs within each side.
For each side of odd size, place one additional vertex there and its
matched partner among the isolates. There are enough isolates: odd s needs
one; if both side sizes are odd, then `s=2 mod 4`, so r is odd and `r>=3`,
providing two. Thus no removed matched edge crosses the bipartition. At
`r=n`, this construction is just the empty graph on n vertices.

For `r=1`, no isolate is available, so the parity correction matters. Any
bipartite subgraph is contained in a cut of G. If p is even, a balanced cut
can keep every original matched pair on one side, retaining `p^2` edges.
If p is odd, a balanced cut has two odd side sizes and must separate at
least one matched pair, retaining at most `p^2-1` edges. An unbalanced cut
also has at most `p^2-1` possible crossing pairs. This bound is attained by
sides of sizes p-1 and p+1, both made of whole matched pairs. Hence the
maximum retained bipartite edge count at r=1 is

```text
p^2 - (p mod 2).
```

Its deletion cost is `p(p-2)+(p mod 2)`, which is at least `2p-2` for
`p>=3`. Taking the smaller deletion cost from the arbitrary-component
and bipartite-component constructions proves (2), including its first
and last entries.

When `p=2`, G is the four-cycle, so its constant edge row is already a cut.
The two codes therefore coincide, and (1) gives `(2,3,4)`.

## What the hierarchy says about decoding

Let C be either observation-row span, with its rows evaluated over the
full port family. Suppose r distinct retained target symbols can be decoded
exactly after deleting D, while all other surviving input symbols remain
unrestricted. The r surviving unit rows lift to independent words of C
supported on `D union {the r targets}`. Thus

```text
|D| >= d_r(C)-r.                                          (4)
```

Conversely, take an r-dimensional subcode attaining `d_r(C)`. Its generator
matrix has r independent coordinate columns. Choose those coordinates as
targets and delete the rest of its support. A change of basis makes its
surviving rows the r unit vectors. All coordinates outside its support
remain and contribute zero. Thus (4) is attained for some selectable target
set, proving that the last two columns of the table are exact.

For k=2 the permitted overlap correction is `C_1(T)`. If `T={a,b}`, its
full-family row is `m_{a}+m_{b}`; the target contributes twice and cancels.
The same identity holds after deletion. Therefore adding those corrections
does not change either hierarchy. Arbitrary exact postprocessing of these
same linear observations also gives no improvement, by the kernel argument
in [MINIMUM-WORDS.md](MINIMUM-WORDS.md).

This is an observation-span statement. It assigns no physical cost to
helpers, access to input symbols, copying, restoration, or assembly, and
it makes no multiplication-bound claim.

## Lifting gives upper bounds for higher k

Fix a signed `(k-2)`-face A. The ports containing A correspond exactly to
signed two-ports on the remaining `p-k+2` original pairs. Multiplying a
residual singleton variable by `m_A` gives a global `(k-1)`-star. This
embeds the residual nonempty-star cut code into either global proper-star
code, with identical support sizes and dimensions. Consequently, for every
rank available in the residual code,

```text
d_r(C^-_{p,k}) <= d_r(C^-_{p-k+2,2}),
d_r(C^+_{p,k}) <= d_r(C^-_{p-k+2,2}).                       (5)
```

When `k>=3`, A is nonempty. The residual constant row then becomes the
allowed nonempty star `m_A`, so the stronger bounds hold:

```text
d_r(C^-_{p,k}) <= d_r(C^+_{p-k+2,2}),
d_r(C^+_{p,k}) <= d_r(C^+_{p-k+2,2}),    k>=3.              (6)
```

The right sides are given completely by (1)–(2), with their stated boundary
cases and rank ranges. An information set in any lifted witness supplies
selectable r-target decoders with the same deletion count. These are upper
bounds for general k, not a claim that all higher-k optimizers arise this
way or that every prescribed target set attains them.

Prepared by Sam Sung with substantial OpenAI Codex assistance; Apache-2.0.
