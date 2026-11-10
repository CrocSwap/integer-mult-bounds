# Length-30 sojourns in the eight-source singleton model

This note proves three restrictions on a restored closed word of length 30 in
Ross Richardson's singleton connector. It does not decide whether any universal
word of that length exists. The selected exponent is unchanged.

## Model

Sources `x_0,...,x_7` are immutable. One connector starts arbitrary and must
return to its initial state. Each call adds exactly one full source. For a word
`w` of length `L`, the prefixes are `q_0=0` and `q_t = e_{w_1} + ... + e_{w_t}`.
Restoration means `q_L=0`. The word is universal when

```text
P + P = F_2^8,  P = {q_0,...,q_(L-1)}.
```

Addition is XOR. Every source that occurs does so an even number of times. A
source that never occurs traps `P+P` in a hyperplane. The inherited deletion
bound `f(7)=24` forces `L - c_i >= 24`, hence `c_i <= L-24`. At `L=30` every
multiplicity lies in `{2,4,6}`.

## Admissible counts

The verifier enumerates all 8-tuples with entries in `{2,4,6}` and sum 30.
There are 1016 labeled tuples, in exactly four shapes up to order:

```text
(4,4,4,4,4,4,4,2), (6,4,4,4,4,4,2,2), (6,6,4,4,4,2,2,2), (6,6,6,4,2,2,2,2).
```

Every one of them has at least one coordinate of multiplicity 2. The rest of
the argument follows that coordinate.

## Layer split

Fix a source `i` with `c_i=2`, at 0-based word positions `f < g`. The bit of
prefix `q_t` is the parity of occurrences of `i` in the first `t` letters, so
it equals 1 precisely for `f < t <= g`. Write `m=g-f`. There are `m` layer-1
prefixes and `30-m` layer-0 prefixes. Since `m>=1`, the layer-0 slot count is
at most 29.

Delete coordinate `i` and write `Q0`, `Q1` for the two projected sets. Then
`P+P` fills `F_2^8` if and only if both of the following hold in the
7-dimensional quotient:

```text
Q0 + Q1 = F_2^7,
(Q0 + Q0) ∪ (Q1 + Q1) = F_2^7.
```

The steps strictly between the two occurrences of `i` are
`w_(f+1),...,w_(g-1)`. They move `Q1`, and each distinct source among them
contributes its basis vector to the direction space of `Q1`. Distinct basis
vectors are independent, so that direction space has dimension `r` equal to
the number of distinct sources in the open sojourn. Thus `Q1` lies in one
coset of an `r`-dimensional subspace `V`, and `Q1+Q1 ⊆ V`.

## Rank at most 2 is impossible

The cross-sum condition requires `Q0` to meet every coset of `V`. There are
`2^(7-r)` cosets, so `|Q0| >= 2^(7-r)`. Layer 0 has at most 29 prefixes, so
`|Q0| <= 29`. For `r <= 2` the coset count is 128, 64 or 32, all larger than
29.

## Rank 3 forces at least 17 layer-0 points

Now `r=3`, so `|Q0| >= 16`. Suppose `|Q0|=16`. Then `Q0` contains exactly one
point of each coset of `V`. No two points lie in the same coset, so the only
sum of `Q0` with itself that lands in `V` is 0. Every one of the 120 vectors
outside `V` must therefore be a sum of two points of `Q0` from different
cosets. There are exactly `C(16,2)=120` such pairs, so those sums are a
bijection onto the complement of `V`.

Choose a linear complement of `V` and write the chosen point of coset `q` as
`q + a_q` with `a_q in V`. For every nonzero quotient element `s` and every
`v in V`, exactly one unordered pair `{q, q+s}` satisfies `a_q + a_(q+s) = v`.
For every nonzero linear character `λ` of `V`,

```text
sum_q (-1)^{λ(a_q) + λ(a_(q+s))} = 2 sum_{v in V} (-1)^{λ(v)} = 0.
```

Thus every nonzero component of `a: F_2^4 → F_2^3` is a bent Boolean function
on four variables. The verifier enumerates all `2^16` truth tables. Exactly
896 are bent, including `x0 x1 + x2 x3`, and the zero function is not bent.
It then checks every triple whose seven nonzero `F_2`-linear combinations are
bent. No such triple exists. This configuration is impossible, so
`|Q0| >= 17` whenever the open sojourn uses exactly three sources.

The same census finds bent pairs, so the absence of a triple is not a failure
to recognize a 2-dimensional bent space.

## A prefix set inside a 4+4 union has at least 31 points

Let `F_2^8 = V ⊕ W` with `dim V = dim W = 4`, and suppose `P ⊆ V ∪ W` satisfies
`P+P = F_2^8`. Every vector has a unique expression `v+w`. Sums of two elements
of `V` stay in `V`, and sums of two elements of `W` stay in `W`. Consider a
nonzero `a in V` outside `P`. The set `P` cannot lie in `V`, so some nonzero
`w` lies in `P ∩ W`. The vector `a+w` is in neither subspace. Its only
decomposition is `a+w`, and `a` is absent, so `a+w` is missed. The symmetric
argument applies to `W`. Therefore `V ∪ W ⊆ P`. Since `V ∩ W = {0}`,

```text
|V ∪ W| = 31.
```

Every prefix set contains `q_0=0`. A universal prefix set contained in such a
union therefore has at least 31 points, so it cannot be the prefix set of a
closed word of length 30. Dropping a visited nonzero vertex from the
coordinate concatenation of two full 4-cubes destroys the cover. The
length-32 Gray concatenation remains a universal upper example.

Deleting `0` from `V ∪ W` leaves a 30-point difference basis. That example
shows why the hypothesis `0 in P` is necessary, and it is not a prefix set.
Another 30-point basis meets the complement of the coordinate union: delete
`1` and `16`, then add `17 = e_0+e_4`. It is not claimed to be the prefix set
of a closed walk.

## What remains

A universal length-30 word, if one exists, has every multiplicity-2 sojourn
using at least three other sources, and at least 17 distinct layer-0
projections when that sojourn uses exactly three. The explicit witness

```text
1 5 4 0 4 3 6 4 7 4 1 7 6 4 2 6 5 6 7 0 6 5 6 2 5 0 3 7 4 0
```

is closed, has legal counts `(6,6,4,4,4,2,2,2)` up to order, has 30 distinct
prefixes, and misses only mask 131. Its multiplicity-2 sources are 1, 2 and 3.
Their open sojourns use 6, 4 and 7 other sources, with 20, 21 and 9 distinct
layer-0 projections. None of those sojourns is in the excluded region. Coverage
255 shows that the pair count `C(30,2)=435` can come within one mask of a
cover. It is not a proof that a full cover is unreachable.

The inherited bounds `28 <= f(8) <= 32` stay in force. Length 28 is not
treated. No supplier, readout schedule, or selected frontier is changed.
