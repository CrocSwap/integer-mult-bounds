# Exact signed star-query census

This note independently checks the sharp star-query argument in
[PR889](https://github.com/CrocSwap/integer-mult-bounds/pull/889), at commit
`e2021d1c9e06948528cbc0a8fd7079b671da981d`, and characterizes every equality
case. The predecessor supplies the construction and its query lower bound;
the contribution here is the complete equality census and an independently
justified coefficient-state checker. The repository base for this contribution
is `91a2094f2e022930069e8cfdc810a3ea1b81cd09`.

## Statement and scope

Fix an integer `k >= 1`. The only allowed letters are

```
B_s:    z   <- z   + s Bx
A_i,s:  y_i <- y_i + s A_i z       (1 <= i <= k; s in {-1,+1}).
```

Source `x`, connector `z`, and outputs `y_i` occupy distinct storage. Each
letter preserves its source and restores any private scratch before returning.
The maps are exact additive linear maps, remain unchanged, and are available
only through these letters. A valid word must implement, for every allowed
choice of maps and arbitrary initial data,

```
z <- z;          y_i <- y_i + A_i Bx;          x <- x.
```

There are no combined-output letters, direct product letters, extra
connectors, or other data operations. We count literal words: output labels,
signs, and ordering distinguish words even when two adjacent operations
commute.

**Result.** No valid word has length below `2k+2`. The exact number of valid
words of length `2k+2` is

```
C_k = 2(k+1)(k!)^2.
```

This is a mathematical proof for the stated query alphabet, accompanied by
finite executable checks. It is not a machine-checked formal proof, a lower
bound for general circuits, or a proof of the full multiplication theorem.
The universal-map condition matters: a fixed zero map, torsion in a fixed
characteristic, or other special identities can change the valid-word set.
`k=0` is excluded because its shortest valid word is the empty word.

## Exact integer state

At every prefix there are integers `t`, `a_i`, and `b_i` such that

```
z   = z_0 + t Bx,
y_i = y_i,0 + a_i A_i z_0 + b_i A_i Bx.
```

All coefficients start at zero. A letter `B_s` updates only `t <- t+s`.
A letter `A_i,s` uses the current `t` and updates only

```
(a_i,b_i) <- (a_i+s, b_i+s*t).
```

Induction proves these identities using additivity alone; no commutation or
invertibility of the maps is needed. Consequently a word is universally valid
if and only if its final state has

```
t = 0;          a_i = 0 and b_i = 1 for every i.
```

Sufficiency follows directly from the displayed identities. For necessity,
one may already specialize to integer scalars with identity maps: independently
varying `z_0` and `x` separates the two output coefficients, and varying `x`
tests connector restoration. Thus these integer conditions do not merely test
a sample of free-map instances; they characterize universal validity in this
alphabet. A finite matrix replay is a separate implementation check.

## Minimum length and equality characterization

Each output must have at least one `A_i` letter to obtain `b_i=1`. Since its
signed count must finish at `a_i=0`, it needs at least two. At least one `B`
letter is necessary to make any observed `t` nonzero, and `t=0` at the end
requires at least two. This proves the lower bound `2k+2`.

At equality there are exactly two `B` letters of opposite signs, and exactly
two letters of each output, also of opposite signs. Write the first `B` sign
as `s`. The value of `t` is zero before the first `B`, `s` between the two
`B` letters, and zero after the second. Call the middle interval the plateau.

For output `i`, both letters outside the plateau give `b_i=0`; both inside
give `b_i=s(+1-1)=0`. Hence exactly one must lie inside. To produce `b_i=1`,
its sign must be `s`; the outside letter then has sign `-s`. Conversely, any
word satisfying these conditions has the required final coefficient state.
This characterizes every equality case, with no further ordering condition
among letters from different outputs.

For a fixed number `j` of outputs whose outside letter is before the first
`B`, choose their labels in `binom(k,j)` ways. Order those `j` letters in
`j!` ways, all `k` plateau letters in `k!` ways, and the remaining `k-j`
outside letters after the second `B` in `(k-j)!` ways. Either first `B` sign
is possible. Therefore the number for this `j` is

```
2 binom(k,j) j! k! (k-j)! = 2(k!)^2.
```

The `k+1` possible values of `j` are disjoint and exhaustive. This proves
the stated formula. For `k=1,...,5` it gives `4, 24, 288, 5760, 172800`.

## Why the symmetry quotient preserves exact word counts

Permuting output labels permutes the pairs `(a_i,b_i)` and commutes with all
state transitions, up to the same permutation of letter labels. A canonical
state can therefore retain `t` and the sorted multiset of these pairs.

Suppose a pair `(a,b)` has multiplicity `m`. For either sign `s`, there are
exactly `m` distinct labelled next letters whose chosen output has this pair.
Each produces the same canonical successor: replace one copy by
`(a+s,b+s*t)` and sort. Assign that transition weight `m`. Each of the two
`B` transitions has weight one. Distinct transitions reaching the same
canonical successor must have their weights added; they must not be
deduplicated as unlabelled words.

Starting with count one at the all-zero state, propagate nonnegative integer
counts by multiplication by transition weights and addition at successors.
Induction on word length shows that each state's count equals the number of
literal labelled words whose coefficient state has that canonical form.
Every labelled state in an orbit has the same outgoing multiplicities, so
aggregating incoming counts introduces neither an orbit-size factor nor a
division by `k!`. The desired terminal orbit consists of `t=0` with `k`
copies of `(0,1)`.

## Safe remaining-length pruning

For any intermediate state define

```
h = |t| + sum_i f(a_i,b_i),
f(a,b) = |a|   if a != 0,
         0     if a == 0 and b == 1,
         2     if a == 0 and b != 1.
```

Any successful continuation must use at least `|t|` additional `B` letters
to restore the connector, because only those letters change `t` and each
changes it by one. If `a_i != 0`, at least `|a_i|` additional `A_i` letters
are needed to cancel its signed dirt coefficient. If `a_i=0` but `b_i!=1`,
zero further `A_i` letters cannot correct `b_i`, and one cannot leave
`a_i=0`; at least two are necessary. These are disjoint letter families,
so their lower bounds add. This proves `h` is a lower bound on every
successful continuation's length. Pruning only when `h` exceeds the remaining
length cannot remove a successful word.

The bound need not be attainable. For example, at the initial state it equals
`2k`, although two additional `B` letters are necessary to create a signal.
Such underestimation affects speed, not completeness. Also `h=0` holds exactly
at the desired terminal coefficient state, so an exhausted horizon does not
accept an unresolved output.

## Attribution and remaining obligations

PR889 supplies the batched interface and sharp restricted-query minimum;
its cited predecessor, Chafik Boukhalfa's
[PR628](https://github.com/CrocSwap/integer-mult-bounds/pull/628), supplies
the dirty product commutator lineage. No priority claim is made for the
commutator identity. This proof and its companion verifier were prepared for
the requesting contributor with substantial OpenAI Codex assistance and are
provided under the repository's Apache-2.0 license.

The abstract query contract is inherited. This result does not supply native
source access, coefficient preparation, physical layout, precision guarantees
for approximate maps, supplier integration, or a new exponent `kappa`.
Finite census results should be reported with their completed `k` and length
domain; they do not independently establish obligations outside this alphabet.
