# The helper-462 landing permutation needs 18 odd-denominator shears

This note proves one statement. It does not prove that 25 is the minimum
shear count of a two-scale zero-swap word for the matcher.

## Statement

Let `P` be the permutation matrix whose row `i` is the basis vector in column

```text
σ = (4, 3, 5, 6, 7, 0, 1, 2).
```

As a map, `σ` is the product of cycles `(0 4 7 2 5)(1 3 6)`. Both cycles are
even permutations, so `det(P) = 1`. The verifier recomputes the cycles, the
determinant and the matrix reached by the cleanup below.

A letter is a shear `row t += c * row s` with `t ≠ s` and `c ≠ 0`, or a
single-coordinate scale `row t *= u` with `u ∉ {0, 1}`. There are no swaps.
A word is applied to `I` from the first letter through the last, so the
product of the corresponding elementary matrices is the resulting matrix.
Shears have determinant 1. For a swap-free word, the product of the scale
coefficients equals the determinant of the product.

Write `Z_{(2)}` for the rational numbers whose denominator, in lowest terms,
is odd. Its units are the rationals whose numerator and denominator are both
odd.

**Theorem.** Every swap-free word for `P` whose shear coefficients lie in
`Z_{(2)}`, and whose scale coefficients are units of `Z_{(2)}`, has at least
18 shears. Eighteen shears are achieved, with six scales by `-1`.

## Where this matrix comes from

The pinned matcher `S` is the `matcher` field of
`research/bit-completed-backend-api/science/RESULT.json`, and `det(S) = -16`.
The open 25-shear route clears `S` with seven integer shears and five scales:

| letter | coefficient class |
| --- | --- |
| `R2 -= R1` | shear `±1` |
| `R2 *= 1/2` | denominator `2` |
| `R1 += R2` | shear `±1` |
| `R4 += R7` | shear `±1` |
| `R4 *= 1/2` | denominator `2` |
| `R7 -= R4` | shear `±1` |
| `R7 *= -1` | odd unit |
| `R1 -= R7` | shear `±1` |
| `R5 -= R1` | shear `±1` |
| `R5 *= 1/2` | denominator `2` |
| `R6 -= R1` | shear `±1` |
| `R6 *= 1/2` | denominator `2` |

The verifier checks that these twelve letters send `S` to `P`. Four of the
scales have denominator 2, so this cleanup is not itself a word in the
coefficient class of the theorem. It contributes seven shear letters to the
unreduced concatenation below. The theorem is about factoring `P`, not about
replacing the cleanup.

## Reduction to CNOT circuits

Reducing a lowest-terms fraction `a/b` with `b` odd modulo 2 sends it to
`a mod 2`, because `b ≡ 1`. This is a ring homomorphism `Z_{(2)} → F2`.

Under that homomorphism:

- a shear with odd numerator becomes the CNOT that adds its source row to its
  target row;
- a shear with even numerator becomes the identity;
- a scale by a unit of `Z_{(2)}` becomes the identity, because that unit is
  odd and hence `1` in `F2`.

The elementary matrices of a word in the stated class therefore have entries
in `Z_{(2)}`. If their product is `P`, reducing modulo 2 deletes the even
shears and every allowed scale and leaves a CNOT circuit for `P`. Its length
is the number of odd-numerator shears, which is at most the number of shears.
The next two sections show that every CNOT circuit for `P` has at least 18
gates. Hence every word in the class has at least 18 shears.

Even-numerator shears only make the word longer. They cannot replace an odd
shear, because they disappear before the CNOT count.

## Two graphs and three kinds of CNOT

Let `M` be an invertible `n × n` matrix over `F2`. In this section `n` is
arbitrary; the landing matrix uses `n = 8`.

The **support graph** `G_v(M)` has a vertex for each index and an undirected
edge `{i, j}`, `i ≠ j`, when `M_ij = 1` or `M_ji = 1`. Write `v(M)` for its
number of connected components.

The **bipartite graph** `G_e(M)` has a row vertex `R_i` and a column vertex
`C_j`, with an edge when `M_ij = 1`. Write `e(M)` for its number of connected
components.

A **river** of `M` is a permutation `π` such that `M_i,π(i) = 1` for every
`i`. Over `F2` the determinant is the sum, over permutations, of the products
of the selected entries. Thus `det M = 1` if and only if the number of rivers
is odd. Every invertible matrix has at least one river.

For the identity, the only river is the identity permutation, `v(I) = n` and
`e(I) = n`. For a permutation matrix of a permutation with `k` cycles,
counting fixed points, the only river is that permutation, `e = n`, and
`v = k`: each cycle is one component of `G_v`. A fixed point is an isolated
vertex, a transposition is a single edge, and a longer cycle is a cycle
graph. Here `k = 2`, so `v(P) = 2` and `e(P) = 8`. The verifier checks these
values directly.

Consider a CNOT that adds row `s` to row `t`, with `s ≠ t`. It replaces row
`t` by `row t + row s` and is an involution.

### A CNOT changes either component count by at most 1

Deleting vertex `t` from `G_v` does not use row `t`. An edge between two
other vertices depends on entries outside that row, so the CNOT does not
change the components of `G_v \ {t}`.

The CNOT can toggle the edge `{t, j}` only when the opposite entry `M_jt` is
`0`. If `M_jt = 1`, the edge is already present and stays present. Every
index `j` at which row `t` actually flips has `M_sj = 1`, so `j` lies in the
component of `s` in `G_v \ {t}`: either `j = s`, or `{s, j}` is an edge. All
toggled neighbors of `t` therefore lie in one component of `G_v \ {t}`.

If `c` is the number of components after deleting `t` and `τ` is the number
of those components touched by `t`, then `v = c - τ + 1`. The touched set
changes by at most the membership of that one component, so `|Δv| ≤ 1`.

The same counting applies to `G_e`. Deleting `R_t` leaves a graph the CNOT
does not change. Every column in which row `s` has a `1` is adjacent to
`R_s`, and that edge survives deletion of `R_t`. Those columns lie in one
component of `G_e \ {R_t}`. The CNOT changes the neighborhood of `R_t` only
inside that component, so `|Δe| ≤ 1`.

### A drop in `v` is a drop in `e`

Suppose the CNOT decreases `v`. Then the component of `s` in `G_v \ {t}` was
not touched by `t` and becomes touched. Some new support edge `{t, j}`
appears. For that edge, `M_jt` was `0` and `M_tj` flips from `0` to `1`, and
`M_sj = 1`.

Rows that share a column are in the same component of `G_v`. If
`M_aj = M_bj = 1` and `a ≠ b`, then either both indices meet `j` by an
off-diagonal `1`, or one of them is `j` and the other entry supplies the edge
`{a, b}` directly. A path in `G_e` alternates rows and columns, so its rows
all lie in one component of `G_v`.

Thus `s` and `t`, which lie in different components of `G_v`, also have `R_s`
and `R_t` in different components of `G_e`. The new bipartite edge
`R_t—C_j` lands in the component of `R_s` in `G_e \ {R_t}`, and that
component was previously untouched. The touched-set count therefore drops
`e` by exactly 1.

### An edge-count change does not change the rivers

First suppose `e` decreases. The same touched-set arithmetic says that the
component of `R_s` in `G_e \ {R_t}` was untouched and becomes touched, and
that no other component changes membership. Every flipped column of row `t`
lies in that component, and none of those columns was a neighbor of `R_t`
before the gate. Every flip in row `t` is therefore `0 → 1`. The CNOT adds
ones; it does not delete any.

Every old river uses a one that is still present, so it remains a river.

There is also no new river. Let `A` and `B` be the row set and column set of
the component of `R_s`. This component does not contain `R_t`, so `t ∉ A`.
Because `M` is invertible it has a river, and that river matches `A` with
`B`: a river edge that starts in the component stays in the component, and
every column in the component is the image of its matched row, which is then
also in the component. Hence `|A| = |B|`.

A river of the new matrix that was not a river of `M` must use one of the
new ones in row `t`, since every other row is unchanged. That new column lies
in `B`. Every row `i ∈ A` is different from `t`, so the new river also
matches it into `B`. That is `|A| + 1` domain elements mapped into a set of
size `|A|`, which is impossible.

Therefore a CNOT that decreases `e` preserves the set of rivers. A CNOT that
increases `e` is the same involution read backwards, so it preserves the set
of rivers as well.

### The three classes are disjoint

Call a CNOT in a circuit a **link** when it decreases `v`, a **cut** when it
increases `e`, and a **middle** when it changes the set of rivers.

A link decreases `e`, so it is not a cut, and the river set stays the same,
so it is not a middle. A cut changes `e`, so the river set stays the same and
it is not a middle. A middle does not change `e`, so it is neither a link nor
a cut.

A gate may decrease `e` without decreasing `v`, or it may change none of
these three things. Such a gate belongs to none of the three classes. It can
only make a circuit longer. The verifier's `GL(3, F2)` control checks that
the three labels are disjoint, that both component counts move by at most 1,
and that a drop in `v` drops `e`, on all 168 matrices and all 1,008 CNOTs.
That control is not the argument for `n = 8`. The argument above is.

## Six links and six cuts

Take any CNOT circuit from `I` to `P`.

Here `v(I) = 8` and `v(P) = 2`. Each link decreases `v` by exactly 1, and no
gate decreases `v` by more than 1. Gates that increase `v` must be balanced
by extra links. The number of links is therefore at least `8 - 2 = 6`.

Here `e(I) = e(P) = 8`. Let `D` be the number of gates that decrease `e` and
`U` the number that increase `e`. Then `8 = 8 - D + U`, so `U = D`. The cuts
are exactly the gates counted by `U`. Every link decreases `e`, so
`D` is at least the number of links. Hence there are at least 6 cuts.

## Six middles

Fix a CNOT that adds row `s` to row `t`. Pair each permutation `π` with

```text
π′ = π ∘ (s t),
```

so `π′(s) = π(t)`, `π′(t) = π(s)`, and `π′` agrees with `π` elsewhere.

If some index `i` outside `{s, t}` has `M_i,π(i) = 0`, that same entry blocks
`π′`, and the CNOT does not change it. Neither permutation is a river before
or after the gate.

Otherwise the two permutations are rivers exactly according to the four bits

```text
p = M_s,π(s),  q = M_s,π(t),  r = M_t,π(s),  u = M_t,π(t).
```

Before the gate, `π` is a river when `p = u = 1`, and `π′` is a river when
`q = r = 1`. After the gate, row `t` is `row t + row s` and row `s` is
unchanged, so `π` is a river when `p = 1` and `u + q = 1`, while `π′` is a
river when `q = 1` and `r + p = 1`.

Those formulas preserve the parity of the number of rivers in the pair for
every one of the 16 bit assignments:

| `p q r u` | rivers before | rivers after |
| --- | --- | --- |
| `0 0 0 0` | 0 | 0 |
| `0 0 0 1` | 0 | 0 |
| `0 0 1 0` | 0 | 0 |
| `0 0 1 1` | 0 | 0 |
| `0 1 0 0` | 0 | 0 |
| `0 1 0 1` | 0 | 0 |
| `0 1 1 0` | 1 | 1 |
| `0 1 1 1` | 1 | 1 |
| `1 0 0 0` | 0 | 0 |
| `1 0 0 1` | 1 | 1 |
| `1 0 1 0` | 0 | 0 |
| `1 0 1 1` | 1 | 1 |
| `1 1 0 0` | 0 | 2 |
| `1 1 0 1` | 1 | 1 |
| `1 1 1 0` | 1 | 1 |
| `1 1 1 1` | 2 | 0 |

The two rows that change the count, `1 1 0 0` and `1 1 1 1`, change it by an
even number. The verifier recomputes the table from the formulas rather than
trusting this display. Pairs of this form partition the symmetric group, so
one CNOT preserves the parity of the number of rivers in every such pair.

Now let the circuit be arbitrary, and let `H` be the subgroup generated by
the transpositions `(s t)` of its middle gates, one transposition for each
middle gate's source and target. Consider the left cosets of `H`.

A gate that is not middle preserves the river set, so it preserves the parity
of the number of rivers in every coset. A middle gate has its transposition
`τ` inside `H`. Right multiplication by `τ` preserves each left coset and
cuts it into pairs `{g, gτ}`. The one-step table preserves parity on each
pair, hence on each coset.

At `I` the only river is the identity, and the coset `H` contains it, so that
coset has odd river parity. At `P` the only river is `σ`. The same coset
still has odd parity, so `σ ∈ H`.

Therefore `σ` preserves every connected component of the simple graph formed
by those transpositions. Each component is a nonempty union of cycles of `σ`.
The cycles are disjoint, so the number `c` of components is at most `k = 2`.

A simple graph on `n` vertices with `c` components has at least `n - c`
edges, and `n - c ≥ n - k = 6`. Each edge comes from at least one middle
gate. Repeated gates on the same pair add gates without adding an edge, so
they do not help a shorter circuit. The number of middle gates is at least 6.

## The length is exactly 18

Links, middles and cuts are disjoint, and there are at least six of each.
Every CNOT circuit from `I` to `P` therefore has at least 18 gates.

The bound is achieved. The six content exchanges

```text
(0, 5), (1, 6), (2, 7), (3, 6), (4, 5), (5, 7)
```

sort the rows of `P` back to `I`. One exchange of positions `(a, b)` is the
four letters

```text
Ra += Rb,  Rb -= Ra,  Ra += Rb,  Rb *= -1.
```

Over `Z` the three shears send `(A, B)` to `(B, -A)`, and the scale by `-1`
corrects the sign. The verifier checks that these 24 letters send `P` to `I`.
Inverting the word, reversing order, negating each shear coefficient and
replacing each scale by its reciprocal gives 18 shears of coefficient `±1`
and six scales by `-1`. Their product is `P`. All of these coefficients lie
in `Z_{(2)}`, and the product of the scales is `(-1)^6 = 1 = det(P)`.

Over `F2`, each scale by `-1` is the identity and each shear coefficient
`±1` is `1`. The 18 shears become 18 CNOTs. The verifier checks that those
CNOTs send `I` to `P`, that deleting any one of them misses `P`, and that
along this circuit the gates are exactly six links, six middles and six cuts.
The middle pairs are six distinct edges and form a graph with two components,
both preserved by `σ`. Each of the three lower bounds is therefore sharp, and
the odd-denominator shear length is exactly 18.

## What the first shortening step can and cannot do

The proposed first step was to factor `P` in fewer than 18 shears and prepend
the inverse of the seven-shear cleanup. Inside the odd-denominator class, no
such factorization of `P` exists.

The cleanup contributes seven shear letters. Placing those seven letters in
front of any odd-denominator landing factor, and not cancelling a letter
where the two blocks meet, produces at least 25 shear letters. The verifier
checks the arithmetic `7 + 18 = 25` and checks that the recorded cleanup
followed by the recorded landing reduction does send `S` to `I`. That check
identifies the blocks. It is not a new 25-shear word, and it is not a proof
that every two-scale zero-swap word has at least 25 shears.

## What is not proved

A coefficient with `2` in its denominator does not reduce to a CNOT or to the
identity. A scale by `2` is singular modulo 2, and a compensating scale by
`1/2` is not a unit of `Z_{(2)}`. The theorem says nothing about words that
use those coefficients.

The theorem also says nothing about a zero-swap word for `S` that does not
factor through this matrix `P`. Commutation, a Steinberg identity, or any
other rewrite that deletes a shear across the cleanup/landing junction is a
different word. The blocks are bounded separately, before that rewriting.

No minimum of 25 is claimed. No new value of `κ` is claimed. The selected
record remains `781451/250000000`.

The pattern of counting links, middles and cuts is the one used for CNOT
circuits of permutations. The argument needed here is written out above; the
package does not treat an external theorem as a substitute for these pages.
