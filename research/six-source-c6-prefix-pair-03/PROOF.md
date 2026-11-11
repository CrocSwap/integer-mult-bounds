# The pair (0, 3) on the sharp T2 window

Scoped written proof with an exhaustive finite certificate in `verify.py`.
The model is six sources, characteristic 6, and floor words of length 36.
No claim is made about the unrestricted six-source depth-two exclusion, which
remains the solver verdict of PR6141. The selected frontier is unchanged.

## 0. Setting

The interface is the one in the merged package
`research/six-source-c6-centre-classification`, pinned in `SOURCES.json`.
A floor word calls each source `0,...,5` exactly six times. `q_t` counts the
first `t` letters. For `4 <= s <= 18`,

```text
S(s) = q_s + q_{39-s}.
```

`S(s)` is weight-3 when every coordinate lies in `{0,1,6,7,12}` and exactly
three lie in `{1,7}`. The same predicate applied to `q_t` is the weight-3
condition at the pair `(0,t)`. A chain on `[8,18]` is a floor word whose
`S(s)` is weight-3 for every `s` in that interval. Its family is the sorted
tuple `S(18)`. The T2 family is `(0,6,7,7,7,12)`.

Open PR #7176 proves that this family has sharp window `[8,18]`, that exactly
720 of the `180 * 120` endpoint pairs are joined there, and that weight-3 at
`(0,9)` coexists with a chain on `[s0,18]` exactly for `s0 >= 8`. Its first
open question asks which further pair with `s + t ≡ 3 (mod 6)` can hold
together with `(0,9)` and that window, starting from the 180 extendible states
at `s = 8` and retaining prefix order. This note answers that question for the
named pair `(0,3)`.

## 1. Lemma. One-low states at s = 8

*There are exactly 180 weight-3 diagonal states at `s = 8` with one coordinate
at most 1. Each has `q_8` a permutation of `(6,1,1,0,0,0)` and `S(8)` a
permutation of `(1,6,6,7,7,12)`. None has sorted sum `(0,6,7,7,7,12)`.*

A weight-3 vector sums to 39 and has exactly three coordinates congruent to 1
modulo 6, so its bases `6 * floor(S_j / 6)` sum to 36. Writing `n0, n6, n12`
for the number of coordinates of each base gives `n0 + n6 + n12 = 6` and
`n6 + 2 n12 = 6`, hence `n12 = n0`. Call this common value `L`.

At `s = 8` the complementary count is `q_31`, the state records a pair
`(q, t)` with `0 <= q_j <= t_j <= 6` and `S = q + t`, and
`sum_j (6 - t_j) = 5`. Those five letters occupy positions `31,...,35`. A
coordinate of base 0 has `t_j <= 1`, so it contributes at least five of those
suffix letters. Two such coordinates need at least ten suffix letters. Thus
`L <= 1`. If the unique low coordinate has `S_j = 0`, then `t_j = 0` and that
coordinate alone needs six suffix letters. So `S_j = 1`, which forces
`(q_j, t_j) = (0, 1)`, and the suffix is five copies of this low source.

The unique high coordinate has sum 12. The only solution of `q + t = 12` with
`0 <= q <= t <= 6` is `(6, 6)`. The four middle coordinates then have
`t`-sum `31 - 6 - 1 = 24` and each `t_j <= 6`, so each equals 6. Their allowed
sums are 6 or 7, so their `q` entries lie in `{0,1}` and sum to
`8 - 6 - 0 = 2`. Exactly two of them equal 1.

Choose the high source in 6 ways, the low source in 5 ways, and which two of
the remaining four sources have prefix count 1 in `C(4,2) = 6` ways:
`6 * 5 * 6 = 180`. Each choice is a weight-3 state, and the two paragraphs
above exclude every other one-low state. The sorted sum is
`(1,6,6,7,7,12)`. In particular the T2 tuple `(0,6,7,7,7,12)` does not occur
at `s = 8`.

`verify.py` enumerates the diagonal states independently from the ten legal
column pairs and checks that the one-low subset is exactly this set of 180.
The same enumeration finds 3,420 zero-low states at `s = 8` and no state with
two or more low coordinates.

## 2. Lemma. Prefixes that make (0, 3) weight-3

*For each of these 180 states, exactly 6 of the 56 words of length 8 with
letter counts `q_8` make `q_3` weight-3.*

The count vector is six copies of a heavy source `H` and one copy each of two
sources `A` and `B`. The number of distinct words is `8 * 7 = 56`. A length-3
prefix has sum 3, so the only weight-3 shape available to it is a permutation
of `(1,1,1,0,0,0)`: three distinct letters. The only three letters present are
`H, A, B`, and the two singletons must occupy two of the first three positions.
There are `3 * 2 = 6` such words; the other five positions are `H`. The other
50 words repeat `H` often enough that `q_3` has a coordinate outside
`{0,1,6,7,12}` or has fewer than three residues 1.

The diagonal sums `S(s)` for `s >= 8`, and the count `q_9`, depend on `q_8`
and on letters at positions `>= 8`. They do not depend on the order inside
the first eight letters. Reordering that prefix preserves every chain of
diagonal states and preserves the truth value of weight-3 at `(0,9)`.

## 3. Theorem. An explicit word for every state

*For every one-low state at `s = 8` and every one of its six favorable
prefixes, there is a floor word that is weight-3 at `(0,3)`, at `(0,9)`, and
at every `s` in `[8,18]`, with `S(18) = S(9)` equal to a permutation of
`(0,6,7,7,7,12)`.*

Let `H` be heavy, `L` low, `{A,B}` the two middle sources of prefix count 1,
and `{C,D}` the two middle sources of prefix count 0. Put a permutation of
`(A,B,H)` in positions `0,1,2` and `H` in positions `3,...,7`. Put `C` in
position 8. On each pair of positions `(s, 38-s)` for `s = 9,...,17`, put the
same letter, using `A,A,B,B,C,C,D,D,D` in that order of `s`. Put `A,B,C` in
positions `18,19,20`, put `L` in position 30, and put `L` in positions
`31,...,35`.

Each source occurs six times: `H` six times in the prefix; `A` once in the
prefix, four times in two pairs, and once in the middle, and likewise `B`;
`C` once at position 8, four times in two pairs, and once in the middle; `D`
six times in three pairs; `L` once at position 30 and five times in the
suffix. The word is a floor word. Its prefix count is the state of Section 1,
and its first three letters are `A,B,H` in some order, so `(0,3)` is weight-3.
Position 8 contributes `C`, so

```text
q_9 = e_A + e_B + e_C + 6 e_H,
```

which is a permutation of `(1,1,1,6,0,0)` and is weight-3.

The first 31 letters contain every copy of every source except five copies of
`L`, so `q_31 = 6(1,...,1) - 5 e_L`. Therefore

```text
S(8)_H = 12,  S(8)_A = S(8)_B = 7,  S(8)_C = S(8)_D = 6,  S(8)_L = 1.
```

The step from `s = 8` to `s = 9` adds `e_C` and subtracts `e_L`, because
position 8 is `C` and position 30 is `L`. Hence `S(9)` is the same tuple with
the `C` coordinate raised from 6 to 7 and the `L` coordinate lowered from 1 to
0: a permutation of `(0,6,7,7,7,12)`. For `s = 9,...,17` the letters at `s`
and at `38-s` were chosen equal, so `S(s+1) = S(s)`. Thus `S(s) = S(9)` for
every `s` in `[9,18]`, and the endpoint family is T2.

There are 180 states and 6 prefixes, so the construction produces 1,080 words.
`verify.py` checks each word from the letters alone. The lexicographically
first parameter tuple `(H,L,A,B,C,D) = (0,1,2,3,4,5)`, with prefix order
`(A,B,H)`, produces

```text
230000004223344555234555443322111111
```

## 4. The 180 states are the T2 start states, and (0, 9) keeps every joined pair

Section 3 already shows that every one-low state reaches at least one T2
endpoint through a word that is weight-3 at `(0,9)`. The certificate also
enumerates the whole weight-3 graph for `8 <= s <= 18`:

- column pairs `(q,t)` with `0 <= q <= t <= 6` and `q+t` in `{0,1,6,7,12}`:
  exactly the ten pairs `(0,0), (0,1), (3,3), (2,4), (3,4), (1,5), (2,5),
  (0,6), (1,6), (6,6)`;
- a state is any 6-tuple of those pairs whose `q`-sum is `s`, whose `t`-sum
  is `39-s`, and whose coordinate sums have exactly three residues 1;
- an edge increments one `q` coordinate and decrements one positive `t`
  coordinate, landing on a state at `s+1`.

The layer sizes are `3600, 5520, 7740, 9900, 11220, 11280, 9780, 7240, 4500,
2040, 700`. Every one of the 592,020 edges preserves the base vector. The 700
endpoint states split into the six families with sizes `20, 20, 120, 180, 180,
180`, and the T2 family has 120 states.

Backward reachability and a second, forward reachability agree on the
following. Exactly the 180 one-low states reach T2. Between them and the 120
T2 endpoints there are 720 joined pairs. For each of the 180 states, the set
of reachable T2 endpoints is the same when every `s = 9` state with
non-weight-3 `q_9` is deleted. The same equality holds for the other one-low
endpoint family `(1,6,6,7,7,12)`, whose 1,080 joined pairs are a by-product of
the same masks. Thus weight-3 at `(0,9)` coexists with every T2 pair joined
on `[8,18]`.

The graph does not say that every path is weight-3 at `(0,9)`. The word

```text
345555554433222111234111220334400000
```

printed by PR #7176 is a chain on `[8,18]` with T2 endpoint and with weight-3
`(0,3)`, while its `q_9` is a permutation of `(0,0,0,1,2,6)`. Deleting the
non-weight-3 layer leaves a path to the same endpoints; it does not delete
the endpoints. The companion word

```text
345555552443322111234111223344000000
```

from the same PR is one more explicit point in the coexistence set: weight-3
at `(0,3)`, at `(0,9)`, and on the whole window, with T2 endpoint.

For each of the 720 joined pairs the certificate lifts one filtered path to a
word, using one favorable prefix, and checks that word from the letters. A
favorable prefix does not change `q_8`, so the same lift works for all six
prefixes of Section 2. Every T2 pair joined on `[8,18]` therefore has a floor
word that is also weight-3 at `(0,9)` and at `(0,3)`.

## 5. What this does and does not settle

Settled, in this model: the classification of the 180 states; the 6-out-of-56
prefix count for `(0,3)`; coexistence of `(0,3)` with `(0,9)` and with every
T2 pair joined on `[8,18]`; the explicit 1,080-word family; and the equality
of the filtered and unfiltered T2 endpoint sets.

Not settled: any pair other than `(0,3)` and the already assumed `(0,9)`;
constant-multiset chains, which Section 1 already forbids at `s = 8` for the
T2 tuple; other characteristics and source counts; and the unrestricted
depth-two exclusion. A single exhibited word would have shown bare
coexistence. The census is the stronger statement that the obstruction fails
for every extendible state and for every previously joined T2 pair, on an
explicit 6/56 fraction of the prefix orders.
