# Two added routes do not strictly save a still-rejected dirty word

## Object

The word, the one-edge route table, and the length-at-least-5 one-move domain
are those of `research/g20-length5plus-one-move`. That package moves exactly
one A2 correction onto a different frame of the published table. It classifies
686,779 assignments as dirty failures: the contact pair routes, and the first
missing edge is the next route of a wire whose frame disagrees with the
contact-frame skeleton.

[#7074](https://github.com/CrocSwap/integer-mult-bounds/pull/7074) keeps that
moved correction and inserts the first missing edge. Of the 686,779
assignments, 686,386 still miss a different edge. This proof starts from those
still-rejected words. It inserts that same first edge and the edge that
rejects the one-edge walk, both at rank 1. No second correction moves, and no
third edge is added. The selected conditional exponent stays
`363005817/100000000000`.

A completed route walk has paid histogram `P`. Write `B` for the published
histogram `{1: 1281, 2: 1338, 3: 58, 4: 57, 5: 102, 6: 10}`. The difference is
a **strict saving** on `(0, 1)` when `Σ_r (P_r − B_r) r^t < 0` for every
`t ∈ (0, 1)`. A word that still misses an edge has no paid histogram and is
not a saving.

## The domain is the #7074 still-rejected set

The verifier imports the pinned #6923 classifier and walks every assignment it
labels `dirty_fail`. The count is again 686,779. For each one, the route walk
inserts missing edges lazily, up to two, at rank 1. The first inserted pair
agrees with the classifier's first missing lookup on all 686,779 assignments.
Those pairs form 22,709 ordered frame pairs. Sorted lines `origin target count`
have SHA-256

```text
8f38eb2f6e526ede87a62c1fc88c35fd5d3ba87a16f755df690a76cea5a68494
```

which is the table published by #7074. Exactly 393 walks emit with only the
first edge inserted. The other 686,386 encounter a second missing edge. Every
first missing hop pays. This recount is the definition of the domain. It does
not re-prove that the 393 one-edge emissions are strict losses. The
order-independent fingerprint of the 686,386 records, the XOR of
`sha256(repr(record))` as formed in the verifier, is

```text
461771548bef726d3739201450ffd2acd372e654bd14d6449bcee7ea79ac59ef
```

## Route walk

`paid_histogram` in the #6923 verifier is the published route rule. A live
`ADD` routes its destination and then its source. A missing edge rejects the
word. A dead `ADD` is omitted. At the end every public role returns to its
final frame, and a nonzero owned role rejects the word. Paying hops increment
the histogram of their edge rank.

The census walk is that rule, with two stated changes.

- It may resume at the contact. The #6923 snapshot stores the rows and frames
  immediately before that contact. A dirty failure has already passed the
  prefix on the published table, and the prefix of the moved word is the same
  sequence of events. Adding edges that the prefix never misses does not
  change that prefix, so the state at the contact is the snapshot.
- The first two distinct missing pairs are inserted and kept, each at rank 1.
  A later hop that needs one of those pairs uses it. A third missing pair
  rejects the word.

The two patched events are the contact and its correction. Both remain `ADD`s,
and only their frame fields change, so the scalar endpoint is the endpoint
already checked for the one-move skeleton. The lexicographically first word
and one word of each of the 28 lengths are checked again with `endpoint_ok`.
Every emission is also rebuilt from the start of the word. On all 12,961
emissions the full walk and the suffix walk insert the same edges, with the
same paying uses, and `paid_histogram` reproduces the full-walk histogram.
The suffix and the full walk likewise agree on the lexicographically first
word and on the sampled word of each length.

## Census at rank 1

| Class | Assignments | Outcome |
|---|---:|---|
| A third edge is still missing | 673,425 | no histogram |
| The walk emits and the rank-split search certifies a strict loss | 12,953 | not a saving |
| The walk emits and the rewrite below certifies a strict loss | 5 | not a saving |
| The walk emits and the moment changes sign on `(0, 1)` | 3 | not a saving |
| Strict saving | 0 | — |
| Total | 686,386 | no saving |

The order used for “lexicographically first” is integer comparison of
`(interval start, interval end, correction index, moved frame)`.

The first still-rejected word is the interval `1,003–8,891`. The outer gate
is `ADD(583, 60)`, and the interval has 12 corrections. Correction 0 is
`ADD(583, 87)`, moved from frame 1 to frame 326. The first missing edge is
`(326, 1)`, with three paying uses. The edge that rejects the one-edge walk
is `(591, 553)`, with one paying use. With both edges present, the walk misses
`(467, 396)`. The independent `paid_histogram` returns `missing_edge` when
those two edges are given rank 1, and again when both are given rank 7.

## Strict loss for 12,953 emissions

On an emission let `Q` be the histogram of every paying hop that is not one of
the two inserted edges, and let `u` and `v` be their paying uses. At rank 1,

`P = Q + (u + v) e_1`.

The difference `P − B` is fed to the #6923 split search. While a negative job
of rank `R` remains, the search looks for at least two positive jobs whose
ranks sum to `R`, replaces them, and repeats. For `0 < t < 1` and integers
`a, b ≥ 1`,

`(a + b)^t < a^t + b^t`,

because `(1 + u)^t < 1 + u^t` for `u > 0`: the function
`q(u) = 1 + u^t − (1 + u)^t` has `q(0) = 0` and

`q'(u) = t (u^{t−1} − (1 + u)^{t−1}) > 0`,

since `t − 1 < 0` and `x ↦ x^{t−1}` is strictly decreasing. Each replacement
therefore strictly raises the moment. The search stops with a positive
remainder on these 12,953 words, so each shape is a strict loss. The search
refuses a shape with more than twelve positive atoms. Every split shape in
this census passes it. The multiset of shapes, including the four shapes the
search does not settle, has SHA-256

```text
a185cc64ee40e0a746eb28e478d2f6e6c976833eb97fd43b453a4896441f1011
```

## Five emissions by an elementary rewrite

The split search does not settle four shapes. Three of them are strict losses
by the same subadditivity, applied in the opposite direction: replacing one
negative job of rank `a + b` by negative jobs of ranks `a` and `b` strictly
lowers the function, because `−(a + b)^t > −a^t − b^t`. A positive lower bound
is therefore a strict loss. A negative job of rank 1 cannot be split. If it is
the only negative rank and the total number of positive jobs of rank at least
2 exceeds that count, then `r^t > 1` gives a positive lower bound as well.

| Rank-1 shape | Words | Lower bound |
|---|---:|---|
| `−H1 + 4 H2 − H3` | 3 | one split of `H3` leaves `−2 H1 + 3 H2 > 1` |
| `3 H1 + 2 H2 − 2 H3` | 1 | two splits of `H3` leave `H1` |
| `3 H1 + 3 H2 − H3 − H5` | 1 | one split of `H5` leaves the previous shape |

Thus `−H1 + 4·2^t − 3^t > 3·2^t − 2 > 1`, the second shape is strictly above
`1`, and the third is strictly above the second. These are the five elementary
words. Each uses a positive number of both added edges, as recorded by the
shape key in the verifier.

## Three emissions change sign

The remaining shape is

`k(t) = 1 + 3·2^t − 4^t − 5^t`,

three words, each with one paying use of each added edge. The
lexicographically first is the interval `5,661–7,047`, correction 8,
`ADD(179, 6)` moved from frame 593 to frame 360, with inserted edges
`(360, 358)` and `(360, 131)`. The #6923 repair on this same interval moves
that correction to frame 358 instead, so it is a different assignment. This
shape is not a strict saving and not a strict loss.

At `t = 1/2`, `k(1/2) = 3√2 − √5 − 1`. Both `3√2 − 1` and `√5` are positive
because `18 > 1`. Squaring preserves the comparison:

`(3√2 − 1)^2 = 19 − 6√2 > 5`

if and only if `14 > 6√2`, if and only if `196 > 72`. So `k(1/2) > 0`.

At `t = 4/5` the rational bounds

`2^{4/5} ≤ 35/20`, `4^{4/5} ≥ 60/20`, `5^{4/5} ≥ 72/20`

hold because `35^5 ≥ 16·20^5`, `60^5 ≤ 256·20^5`, and `72^5 ≤ 625·20^5`.
Therefore

`1 + 3·2^{4/5} ≤ (20 + 3·35)/20 = 125/20 < 132/20 ≤ 4^{4/5} + 5^{4/5}`,

so `k(4/5) < 0`. The moment is positive at one interior point and negative at
another. It is not strictly negative on `(0, 1)`.

## Every rank in 1..7 stays free of a strict saving

The route taken by a word does not depend on the ranks of the two inserted
edges, only on their presence. Let `u` and `v` be the paying uses found at
rank 1, and let `P^{(r,s)}` be the histogram when the two edges have ranks
`r` and `s`. Then

`P^{(r,s)} − P^{(1,1)} = u (e_r − e_1) + v (e_s − e_1)`.

For `r, s ≥ 1` and `t ∈ (0, 1)` the moment of the right-hand side is
`u (r^t − 1) + v (s^t − 1) ≥ 0`. If `P^{(1,1)}` is not a strict saving, neither
is `P^{(r,s)}`. If the word misses a third edge, that pair is absent from the
table whatever ranks are assigned to the two inserted edges, so there is still
no histogram. The verifier checks the bin identity on the lexicographically
first sign-changing word by moving its first added edge from rank 1 to rank 7.

## What this does not say

The screen adds two edges to one moved word. It does not add the third missing
edge of any of the 673,425 words that still fail, and it does not move a
second correction. A rejection on this enlarged table is not a proof that
another routing model is impossible. The three sign-changing words are not
strict losses. Ordinary admission, the 18-call caller, adjoint columns, moduli
101 and 10201, and the selected frontier are untouched.
