# One other c=7 floor word realizes both missed masks

**Constructive witness, plus an exhaustive pair census for two masks on
one word. No new κ.** The length-42 floor word recorded in PR #7037
misses the nonzero masks `(3, 5)` and `(0, 1, 3, 5)`. The word below is
a different six-source floor word, and the same 903-pair predicate
realizes both.

```text
350122222224444444000000111111333333555555
```

The blocks are `3, 5, 0, 1, 2^7, 4^7, 0^6, 1^6, 3^6, 5^6`. On this word,
`(3, 5)` is realized exactly at `(0, 2)`, `(0, 30)` and `(1, 36)`, and
`(0, 1, 3, 5)` is realized exactly at `(0, 4)`, `(0, 11)` and `(0, 18)`.

The selected conditional κ remains `781451/250000000` in
`certificates/selected-result.json`.

## Interface, unchanged

A floor word on six sources in characteristic 7 has length 42 and calls
each source seven times. `q_t` counts the first `t` letters, so
`q_0 = 0` and `q_42 = (7, 7, 7, 7, 7, 7)`. A pair `0 ≤ s ≤ t ≤ 41`
realizes a binary mask when every coordinate of `q_s + q_t` lies in
`{0, 1, 7, 8, 14}` and the mask bit is 1 exactly on `{1, 8}`. Those six
integers are the members of `{0, ..., 14}` whose residue modulo 7 is 0
or 1. This is the predicate of PR #7037, which is the interface of
PR #4231 / PR #4248 as used by the c=7 diagonal note. Boundary 42 is
outside the predicate because `q_42 = 7·1 ≡ q_0`.

The coordinate sum of `q_t` is `t`, so a realizing pair satisfies
`s + t ≡ weight (mod 7)`.

## Why these two masks can occur together

Both masks are single-prefix masks: `q_0 = 0`, so `q_t` itself is the
mask whenever its coordinates are the mask bits.

**Lemma.** Let the first two letters be `{3, 5}` in either order, and
the next two letters be `{0, 1}` in either order. Then `(0, 2)` realizes
`(3, 5)` and `(0, 4)` realizes `(0, 1, 3, 5)`.

The first two letters contribute one count on source 3 and one on source
5, so `q_2 = e_3 + e_5`. The next two contribute one count on source 0
and one on source 1, so `q_4 = e_0 + e_1 + e_3 + e_5`. Adding `q_0`
leaves those vectors. Their coordinates lie in `{0, 1}`, the bits are
the coordinates, and the weights are 2 and 4. The pairs are inside
`0 ≤ s ≤ t ≤ 41`, and `0 + 2 ≡ 2`, `0 + 4 ≡ 4` modulo 7. The later
letters are not used. There are `2! · 2! = 4` such prefixes:
`3501`, `3510`, `5301` and `5310`. The count does not depend on the
order inside each pair, and the checker evaluates all four.

Any length-42 completion that calls each source seven times is therefore
a floor word realizing both masks. The block word is one completion.
Its first four letters are `3501`. The remaining counts are
`(6, 6, 7, 6, 7, 6)`, which sum to 38, and the six constant blocks use
exactly those calls.

This lemma is a direct prefix count under the stated initial-segment
hypothesis. It is not a census of floor words.

## The six realizing pairs

Write counts in source order `(0, 1, 2, 3, 4, 5)`. The block boundaries
give:

| `t` | block that finishes at `t` | `q_t` |
|---:|---|---|
| 0 | none | `(0, 0, 0, 0, 0, 0)` |
| 1 | `3` | `(0, 0, 0, 1, 0, 0)` |
| 2 | `5` | `(0, 0, 0, 1, 0, 1)` |
| 3 | `0` | `(1, 0, 0, 1, 0, 1)` |
| 4 | `1` | `(1, 1, 0, 1, 0, 1)` |
| 11 | `2^7` | `(1, 1, 7, 1, 0, 1)` |
| 18 | `4^7` | `(1, 1, 7, 1, 7, 1)` |
| 24 | `0^6` | `(7, 1, 7, 1, 7, 1)` |
| 30 | `1^6` | `(7, 7, 7, 1, 7, 1)` |
| 36 | `3^6` | `(7, 7, 7, 7, 7, 1)` |
| 42 | `5^6` | `(7, 7, 7, 7, 7, 7)` |

Each row is the previous count plus that one block. From `q_18` to `q_30`
the two blocks are six `0`s and then six `1`s.

The six sums are then:

| pair | sum | bits | mask | `s + t` mod 7 |
|---|---|---|---|---:|
| `(0, 2)` | `q_2 = (0, 0, 0, 1, 0, 1)` | `1` on `{3, 5}` | `(3, 5)` | 2 |
| `(0, 30)` | `q_30 = (7, 7, 7, 1, 7, 1)` | `1` on `{3, 5}` | `(3, 5)` | 2 |
| `(1, 36)` | `q_1 + q_36 = (7, 7, 7, 8, 7, 1)` | `1` on `{3, 5}` | `(3, 5)` | 2 |
| `(0, 4)` | `q_4 = (1, 1, 0, 1, 0, 1)` | `1` on `{0, 1, 3, 5}` | `(0, 1, 3, 5)` | 4 |
| `(0, 11)` | `q_11 = (1, 1, 7, 1, 0, 1)` | `1` on `{0, 1, 3, 5}` | `(0, 1, 3, 5)` | 4 |
| `(0, 18)` | `q_18 = (1, 1, 7, 1, 7, 1)` | `1` on `{0, 1, 3, 5}` | `(0, 1, 3, 5)` | 4 |

A coordinate `7` has residue 0, and `8 = 7 + 1` has residue 1. Every
coordinate in the table lies in `{0, 1, 7, 8}`. The value 14 does not
occur in these six sums.

## Completeness for this word

The domain is the set of pairs `0 ≤ s ≤ t ≤ 41`. It is finite, and
`42 · 43 / 2 = 903`. The checker visits each pair once and requires the
visit count to be 903. On every pair the allowed-set reading and the
modulo-7 reading agree. Every nonzero hit satisfies the weight identity.
Restricted to the two named masks, the hit set is exactly the six pairs
above: three for `(3, 5)` and three for `(0, 1, 3, 5)`.

That is an exhaustive finite census of these two masks on this one word.
It is not a census of the other 61 nonzero masks, and it is not a census
of floor words. A failed or incomplete search is not this claim.

## What the two control words do

The same predicate, still restricted to these two masks, was run on two
other floor words.

The PR #7037 witness

```text
023514103524310254054123145203452034213150
```

realizes neither mask. This repeats only those two lines of that
census. It is a regression control for the predicate, not a new
inventory of the witness.

Swapping positions 1 and 2 of the witness gives

```text
032514103524310254054123145203452034213150
```

which is still a floor word. PR #7037 records that this transposition
has a different non-weight-3 missing set from the witness. The same
903-pair predicate realizes neither `(3, 5)` nor `(0, 1, 3, 5)` on it.
The difference recorded in #7037 is therefore not the appearance of
these two masks. No other mask of the transposition is listed here.

Changing the first letter of the block word from 3 to 2 calls source 3
six times and source 2 eight times. The floor-word check rejects it.

## What this does not establish

The block word is not claimed to be a depth-two block. A block needs
every nonzero mask, and the other 61 masks were not classified. Realizing
these two masks separates the #7037 miss from the floor-word hypotheses:
the call counts alone do not forbid either mask. It does not show that a
depth-two block exists at characteristic 7, and it does not re-prove the
weight-3 cover bounds of PR #7016 or PR #7032. No supplier, consumer, or
selected frontier changes.

The family expansion gate is not met by this example and is not invoked.
The unsigned dirty-connector alphabet is unchanged. This is a side result
on one released question, not another construction round.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -W error -B research/six-source-c7-second-floor-masks/verify.py
python3.12 -I -O -W error -B research/six-source-c7-second-floor-masks/verify.py
python3.12 -B scripts/research_package.py --package research/six-source-c7-second-floor-masks --check-only
```

The marker is

```text
PASS_SIX_SOURCE_C7_SECOND_FLOOR_MASKS pairs=903 (3,5)=3:(0,2),(0,30),(1,36) (0,1,3,5)=3:(0,4),(0,11),(0,18) witness_both=miss transposition_both=miss lemma_prefixes=4 controls=8
```

The eight controls are the floor-word shape of the block literal, the
boundary prefix table, the six hand sums and their mask readings, the
903-pair scan, the four lemma prefixes, the witness miss, the
transposition miss, and the rejected call-count edit. Failures raise
`SystemExit`. Optimized mode cannot silence them. No SAT solver, Lean,
Docker, or selected-frontier replay was run.

## Open next questions

1. Which of the other 61 nonzero masks does this same block word miss?
   *Why:* a depth-two block needs every nonzero mask. Realizing `(3, 5)`
   and `(0, 1, 3, 5)` does not decide the rest, and a list of these two
   masks is not a block. *First step:* run the same 903-pair predicate
   on this one word and list the masks with no realizing pair.
   *Blocked by:* the checker discards every mask other than the two
   named targets. An exhaustive census of every floor word would be a
   different claim.
2. Does any adjacent transposition of the #7037 witness, other than the
   swap of positions 1 and 2, realize both masks? *Why:* that one
   transposition is a floor word and misses both, so the positive
   example above is not a one-letter move of the recorded witness.
   There are only 41 adjacent positions. *First step:* evaluate the
   903-pair predicate on each adjacent swap of distinct letters and
   record, for these two masks only, whether both are realized.
   *Blocked by:* only the swap of positions 1 and 2 is checked here.

## Credit

The depth-two interface and the weight identity are Nick Petalas's
(PR #4231, PR #4248, PR #6107), with the Ross Richardson PR #934 /
PR #943 lineage. JosieElliston's PR #6141 leaves characteristic 7 open.
The diagonal equality case is upstream PR #6941. The witness, its two
non-weight-3 misses, and the request for one other floor word are open
question 1 of upstream PR #7037, which answers open question 2 of
upstream PR #7016. The adjacent transposition used as a negative control
is the floor word already named in the #7037 checker. This package
evaluates one further word and does not repeat either census.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
