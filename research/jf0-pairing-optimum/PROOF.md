# Exact pairing cost of the pinned `jf0` configuration

The minimum of the three-term binary pairing-rank sum for the configuration
below is **19**, attained with term ranks **(6, 6, 7)**. The lower bound holds
for every admissible pairing, including asymmetric pairings. It is a written
proof using three explicit triangular minors, not an enumeration of pairings.

## Object and objective

Use the zero-based row order of
`research/char2-jets/data/jf0.json` in PR
[#2162](https://github.com/CrocSwap/integer-mult-bounds/pull/2162), head
`113a718265c62aec301c5695f4bfb9c421bef7ab`. The source file's SHA-256 is
`cd8a8c2436e0a025348af0b52ccb48a4f64535b0ff8df32cbe13da73673266b7`.
Its outer JSON entries are `[P,Q]`; their rows are:

| `i` | `P_i` | `Q_i` |
|---:|---|---|
| 0 | (1, 1, 1) | (1, 0, 1) |
| 1 | (0, 1, 1) | (0, 1, 1) |
| 2 | (1, 0, -1) | (1, -1, 0) |
| 3 | (1, 1, 0) | (0, 1, -1) |
| 4 | (1, 1, 1) | (1, -1, -2) |
| 5 | (0, 1, 1) | (1, 0, 1) |
| 6 | (1, 1, 0) | (1, 1, 0) |
| 7 | (1, 1, 1) | (1, -1, -2) |
| 8 | (1, 1, 1) | (1, -1, 1) |
| 9 | (1, 0, -1) | (1, -1, 0) |
| 10 | (1, 1, 1) | (1, -1, 1) |

Dot products in the admissibility condition are taken over the rationals,
without reducing the entries modulo 2. The diagonal products are
`(2,2,1,1,-2,1,2,-2,1,1,1)`, all nonzero. Let `B` range over all
`11 x 11` matrices over `F_2` such that

1. `B_ii = 1` for every `i`;
2. for `i != k`, `P_i dot Q_k != 0` implies `B_ik = 0`.

Every remaining off-diagonal entry is an independent binary choice; symmetry,
idempotence and any further realizability conditions are not assumed. Define

`R_j = {i : P_ij != 0}`, `A_j = {i : Q_ij != 0}`,

and

`C(B) = sum_{j=0}^2 rank_{F_2} B[R_j,A_j]`.

The support sets are:

| `j` | `R_j` | `A_j` |
|---:|---|---|
| 0 | 0,2,3,4,6,7,8,9,10 | 0,2,4,5,6,7,8,9,10 |
| 1 | 0,1,3,4,5,6,7,8,10 | 1,2,3,4,6,7,8,9,10 |
| 2 | 0,1,2,4,5,7,8,9,10 | 0,1,3,4,5,7,8,10 |

This is the raw sum of ranks used in PR #2162's `lib/kit.py` and README
Section 1. That source explicitly drops the additional floor from its earlier
cost contract. The equality proved here concerns `C(B)` as defined above,
not the minimum of an unspecified cost with extra charges.

## Universal triangular-minor lemma

Let `F` be any field, and let `B` be a matrix with nonzero diagonal. Fix row
and column sets `R,A`. Suppose distinct indices
`O=(o_0,...,o_{k-1})` belong to `R intersection A`, and every admissible `B`
satisfies `B[o_a,o_b]=0` whenever `a>b`. Then

`rank_F B[R,A] >= k`.

Indeed, order both the rows and the columns of the principal submatrix on
`O` by this same list. The resulting matrix is upper triangular with nonzero
diagonal, so its determinant is the product of those diagonal entries and
is nonzero. Its rank is `k`; passing to the containing matrix cannot decrease
that lower bound. This argument permits every value above the diagonal and
every entry outside the minor. In the unit-diagonal case its determinant is
exactly 1.

For the present incidence model, an equivalent certificate is an acyclic
directed graph on `O`, with an edge `i -> k` for each allowed off-diagonal
entry (`P_i dot Q_k=0`). A topological order puts all such edges above the
diagonal. The graph must include all allowed incidences on the chosen indices,
not only the incidences selected by a particular `B`.

## Three lower certificates

The following lists are the row and column orders of the principal minors.
The final column is the complete set of allowed off-diagonal entries within
each listed minor, computed from the rational dot products in the table above.

| `j` | Ordered minor `O_j` | Allowed off-diagonal entries within `O_j` |
|---:|---|---|
| 0 | 0,6,4,7,8,10 | (6,4), (6,7), (6,8), (6,10) |
| 1 | 1,6,4,7,8,10 | (1,8), (1,10), (6,4), (6,7), (6,8), (6,10) |
| 2 | 0,1,4,5,7,8,10 | (1,8), (1,10), (5,8), (5,10) |

Each `O_j` lies in `R_j intersection A_j`, and each displayed edge points
forward in its list. Every undisplayed off-diagonal entry in each minor is
forced to zero. The universal lemma therefore gives, simultaneously for all
admissible `B`,

`rank B[R_0,A_0] >= 6`,

`rank B[R_1,A_1] >= 6`,

`rank B[R_2,A_2] >= 7`.

The three terms are separately charged in `C(B)`, so the minors may share
indices. Summing the three inequalities gives `C(B) >= 19`.

The argument does not discard any zero-overlap incidences: it allows arbitrary
values at all entries not forced to zero by the stated model. For this data,
direct inspection additionally finds 41 off-diagonal rational incidences, all
of them lying in at least one `R_j x A_j`. Hence there are exactly `2^41`
admissible pairings, and the proof covers all of them without visiting them.
This count is a description of the domain, not an enumeration claim or a
premise needed for the triangular-minor proof.

## Matching upper witness

Partition the eleven indices into the eight classes

`{0}, {1}, {2,8}, {3,4}, {5}, {6}, {7}, {9,10}`.

Define `B*_ik=1` exactly when `i` and `k` belong to the same class. Equivalently,
`B*` is the identity with the six off-diagonal entries

`(2,8), (8,2), (3,4), (4,3), (9,10), (10,9)`

set to 1. All six rational dot products are zero. More explicitly,

`P_2 dot Q_8 = P_9 dot Q_10 = 1-1 = 0`,

`P_8 dot Q_2 = P_10 dot Q_9 = 1-1 = 0`,

`P_3 dot Q_4 = 1-1 = 0`,

`P_4 dot Q_3 = 1-1 = 0`.

Thus `B*` is admissible. For any coordinate restriction, regroup its rows and
columns by these eight classes. Each class meeting both `R_j` and `A_j`
contributes one nonempty all-ones rectangle. Different classes occupy disjoint
row and column sets. Each such rectangle has rank 1, so the restriction's rank
is exactly the number of these classes:

| `j` | Classes meeting both `R_j` and `A_j` | Rank |
|---:|---|---:|
| 0 | {0}, {2,8}, {3,4}, {6}, {7}, {9,10} | 6 |
| 1 | {1}, {2,8}, {3,4}, {6}, {7}, {9,10} | 6 |
| 2 | {0}, {1}, {2,8}, {3,4}, {5}, {7}, {9,10} | 7 |

Consequently `C(B*)=19`, matching the lower bound. In fact `B*` attains the
minimum of each of the three term ranks simultaneously.

## Scope, verification and attribution

This is an exact result for the pinned, ordered rational configuration and the
stated binary pairing objective. The triangular-minor lemma is a general
written proof over arbitrary fields; its application here checks finite
support and rational-dot-product data. The upper proof is likewise explicit
linear algebra. Neither proof requires SAT, enumeration of `2^41` pairings,
the predecessor's first-order jet conclusions, or its quoted split min-max
theorem. A replay of these finite certificates is computational verification
of the data and witnesses, not a formal-kernel proof.

The configuration, three-total pairing framework, and previous `C >= 16`
SAT lower bound belong to DreamingOfClouds with Claude Opus 5.5 assistance
in PR #2162, building on #1590 and #2111 and their cited predecessors. This
note responds to the explicit independent-check request for the unknown exact
`jf0` value. Its contribution is the universal bound 19 and a matching
six-incidence witness, with a separate exact replay. Substantial OpenAI Codex
assistance was used in preparing this successor result; source licensing and
the predecessor credit remain applicable.

The result does not settle the universal three-total conjecture for other
configurations or decide whether higher-order jets exist for `jf0`. It supplies
no reversible circuit, arbitrary-dirty-helper restoration argument, precision
contract, recursive supplier profile, physical implementation or new
multiplication exponent. Those obligations require separate constructions and
analysis if this algebraic objective is used elsewhere.
