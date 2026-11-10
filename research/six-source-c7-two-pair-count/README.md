# Two off-diagonal pairs do not finish the six-source c=7 weight-3 count

**Scoped exchange obstruction. No new κ.** In the unchanged unsigned dirty
connector, keep the centre as the only failed diagonal index. Then the pair
`(9, 15)` and one other pair from `(10, 14)`, `(11, 13)`, and `(33, 33)`
cannot finish the `C(6, 3) = 20` weight-3 masks. Every such chain has
weight-3 cover at most 7. The value 7 is attained, but only when `(9, 15)`
is the single new mask. Two or three of the masks can be new at the same
time, and different from the mask of `(0, 3)`; the cover is then at most 6.

This does not decide whether a six-source depth-two block exists at `c = 7`.
Masks of every weight other than 3, and chains with two or more failed
diagonal indices, stay open. The selected conditional κ remains
`781451/250000000`.

## Hypothesis, inherited

A floor word has length 42 and calls each of six sources seven times. `q_t`
counts the first `t` letters. A pair realizes a weight-3 mask when every
coordinate of `q_s + q_t` lies in `{0, 1, 7, 8, 14}` and exactly three lie
in `{1, 8}`. The coordinate sum is then `s + t = 3 + 7λ`.

The one-index exchange, open upstream PR #7016, proves that if exactly one
index in `4..22` fails, that index is the centre `s = 22`, and that one
off-diagonal pair still leaves the cover at most 19. This package does not
repeat that argument. It takes the resulting free-type chains as the
hypothesis: `S(s) = q_s + q_{45-s}` is a permutation of `(8, 8, 8, 7, 7, 7)`
for every `s = 4..21`. The state at index `s` is the suffix usage on
`[45-s, 42)` together with the mask of `S(s)`. The prefix is usage plus one
on the mask, and the only in-type steps are a stay or a Johnson swap, as in
that exchange. The checker rebuilds the layered graph and compares two
writings of the step. It has the same layer sizes, ending at one saturated
state per mask.

## The only `(9, 15)` shape

Among all free-type states at `s = 9` and `s = 15`, exactly 20 pairs have
prefixes that sum to a weight-3 vector. There is one pair for each mask
`M`. Both endpoints carry `M`, and the sum is `7` on `M` and `1` on the
complement `M^c`. Thus `(9, 15)` realizes `M^c`. The usages are `2` on `M`
and `0` off `M` at `s = 9`, and `3` on `M` and `1` off `M` at `s = 15`.
No other free-type pair sums to weight 3. The scan is exhaustive: every
centre-only chain meets the forward closure, and every sum-24 weight-3
vector is tested against those prefixes. There are 700 such vectors and
20 hits.

## Support collapse

Counts are monotone, so `q_9` supported on `M` forces every earlier prefix
to be supported on `M`. A free-type mask is a 3-subset of the positive
coordinates, so `s = 4..9` all carry `M`. The checker also walks every
graph ancestor back to `s = 4` and finds the same mask.

At `s = 15` every source in `M` already has suffix usage 3, so it cannot be
the letter added to the suffix. A swap would require that, and a stay on
`M` would too. The only remaining steps are stays on `M^c`. They preserve
the mask. Six stays saturate the usage, and `s = 16..21` all carry `M`.

The only indices that can carry a mask other than `M` are therefore
`s = 10, 11, 12, 13, 14`. The diagonal image has size at most 6.

The first nine letters use only `M`. If `(0, 3)` is weight 3, its three
letters are three distinct sources in `M`, so its mask is `M`, already in
the image.

The suffix usage at `s = 12` is three steps beyond the `s = 9` usage. The
pair `(33, 33)` is weight 3 only when that usage lies in `{0, 3}` with
exactly three 3s: `q_33 = 7` minus the usage, and twice that value lies in
`{0, 1, 7, 8, 14}` only for usage 0 or 3, with the 3s as the mask. A
complement source starts at usage 0 and would need all three steps to reach
3, leaving the other coordinates at 2 or 0. That is not a legal support.
The only remaining usage is 3 on `M` and 0 off `M`, and `(33, 33)` realizes
`M`.

The diagonal image, `(0, 3)`, and `(33, 33)` therefore contribute at most
six masks. The three pairs `(9, 15)`, `(10, 14)`, and `(11, 13)` add at
most one mask each. The cover is at most `6 + 3 = 9`, which is less than
20.

## The walks sharpen 9 to 7

Each complement shape has one state at `s = 9` and one at `s = 15`. Every
in-type walk of length 6 between them was enumerated. A forward count and
a classifying recursion agree: 31,788 walks for each of the 20 masks.
On these walks the five intermediate masks and the three pair-sums were
read directly. No sum at `(10, 14)` or `(11, 13)` is weight 3 unless the
endpoints agree, and `(33, 33)` never leaves the image.

For each mask the cover is at most 7. The 3,276 walks of cover 7 all have
image size 6 and exactly one new mask, the complement. Another 1,044 walks
per mask have two or more new masks, and 72 of those have all three of
`(9, 15)`, `(10, 14)`, and `(11, 13)` outside the image. Whenever two or
more are new, the image has shrunk enough that the cover is at most 6.
Joint newness occurs, and it does not finish the count.

A new mask is one outside the diagonal image of `s = 4..21`. It is
disjoint from `(0, 3)` when it differs from the mask `(0, 3)` realizes.
On these chains that mask is `M` or `(0, 3)` is not weight 3, and `M` is
already in the image, so every new mask is disjoint from `(0, 3)`. The
complement is also disjoint from `M` as a 3-subset. The masks of `(10, 14)`
and `(11, 13)` need not be: on the word below they meet `M`.

## Two words

Both words call each source seven times. The only failed diagonal index in
`4..22` is the centre. The checker reads every pair whose index sum is
congruent to 3 modulo 7, which is every pair that can realize a weight-3
mask, because a weight-3 vector sums to `3 + 7λ`.

```text
012001122012345334455345554433543210221100
```

The first nine letters are three copies of `(0, 1, 2)`, and positions
`9..14` are `012345`. The diagonal image is `{(0, 1, 2)}`. The pair
`(0, 3)` realizes `(0, 1, 2)`. The only other weight-3 masks are

| pair | sum | mask |
|---|---|---|
| `(9, 15)` | `(7, 7, 7, 1, 1, 1)` | `(3, 4, 5)` |
| `(10, 14)` | `(8, 7, 7, 1, 1, 0)` | `(0, 3, 4)` |
| `(11, 13)` | `(8, 8, 7, 1, 0, 0)` | `(0, 1, 3)` |

and `(33, 33)` repeats `(0, 1, 2)`. The cover is 4. All three new masks
differ from `(0, 3)`. A one-letter change of the first letter is rejected.

```text
012001122301452554433345334455543210221100
```

The same `(0, 3)` mask sits in a diagonal image of size 6,

```text
(0,1,2), (1,2,3), (0,2,3), (0,1,3), (0,1,4), (0,1,5),
```

and `(9, 15)` supplies the seventh mask `(3, 4, 5)`. The pairs `(10, 14)`
and `(11, 13)` are not weight 3, and `(33, 33)` repeats `(0, 1, 2)`. The
cover is 7, so the census ceiling is sharp. It is still not 20.

## What this does not say

The bound applies only to centre-only free-type chains on which `(9, 15)`
is weight 3. A chain whose `(9, 15)` sum is not weight 3 is not classified.
Two or more failed diagonal indices are not classified. Masks of weight
other than 3 are not listed; a completed weight-3 count would still not be
a depth-two block. The slot bounds that kill the other off-diagonal sums
in PR #7016 are used only as the reason this package does not search them
again. On the two words above, the exhaustive residue scan finds no further
weight-3 mask, but that is a check of those words, not a new proof of the
82-slot obstruction. No supplier, consumer, or selected frontier changes.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -W error -B research/six-source-c7-two-pair-count/verify.py
python3.12 -I -O -W error -B research/six-source-c7-two-pair-count/verify.py
python3.12 -B scripts/research_package.py --package research/six-source-c7-two-pair-count --check-only
```

The marker is `PASS_SIX_SOURCE_C7_TWO_PAIR_COUNT endpoint_pairs=20/20 walks_per_mask=31788 image_at_most=6 structural_cover_at_most=9 census_cover_at_most=7 several_walks=1044 several_cover_at_most=6 three_new_walks=72 cover7_walks=3276 three_word_cover=4 sharp_word_cover=7 block33_outside=0 unclassified=0 controls=12`.

The twelve controls are the agreement of the two step generators, the
terminal layer, the 20 complement pairs, the forward stays, the ancestors
back to `s = 4`, the agreement of the two walk counts, the absence of an
unclassified sum, the absence of a new `(33, 33)` mask, the cover ceilings
together with the attained cover-7 and three-new cases, the three-new word,
the sharp word, and the rejected one-letter mutation. No SAT solver, Lean,
or Docker replay is used.

## Open next questions

1. On a centre-only chain whose `(9, 15)` sum is not weight 3, can
   `(10, 14)` and `(11, 13)` be new at the same time and push the weight-3
   cover to 20? *Why:* the collapse above uses the complement shape, so it
   says nothing about a chain that misses `(9, 15)`. Separate endpoint
   equalities would suggest an image of size at most 16 and a cover of at
   most 19, but that counting is not proved here. *First step:* enumerate
   the joint walks on which `s = 10` and `s = 14` share a mask, `s = 11`
   and `s = 13` share a mask, and the states at `s = 9` and `s = 15` are
   not a complement pair; record the image size and whether `(0, 3)` is
   outside it. *Blocked by:* those walks are outside the 31,788 complement
   windows classified here.

## Credit

The depth-two interface and the weight identity are Nick Petalas's
(PR #4231, PR #4248, PR #6107), with the Ross Richardson PR #934 / PR #943
lineage. JosieElliston's PR #6141 leaves `c = 7` open. The empty diagonal
equality case is upstream PR #6941. The one-index exchange and the released
question answered here are upstream PR #7016, head
`3a89abb195ec9a63476c12042df5fbb0760e3534`; its centre reduction and its
one-pair ceiling are not repeated. zxv's PR #6057 and JosieElliston's
PR #6061 supply the `c ≥ 8` words. queelius's open PR #6216 is a `c = 5`
certificate only.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
