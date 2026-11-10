# Non-weight-3 masks missed by the recorded c=7 witness

**Exhaustive finite census of one word. No new κ.** On the length-42 floor
word recorded in PR #7016,

```text
023514103524310254054123145203452034213150
```

the pairs `0 ≤ s ≤ t ≤ 41` realize 41 of the 43 nonzero binary masks of
weight other than 3. The two missing masks are `(3, 5)` and `(0, 1, 3, 5)`.
The same census misses the weight-3 mask `(1, 3, 5)`, which is the gap that
PR #7016 already records for this word. This word is therefore not a
depth-two block.

The selected conditional κ remains `781451/250000000` in
`certificates/selected-result.json`.

## Interface

A floor word on six sources in characteristic 7 has length 42 and calls each
source seven times. `q_t` counts the first `t` letters, so `q_0 = 0` and
`q_42 = (7, 7, 7, 7, 7, 7)`. This is the unsigned dirty-connector interface
of PR #4231 / PR #4248, as used by PR #6141 and by the c=7 diagonal note:
the word meets a nonzero binary mask when `q_s + q_t` is congruent to that
mask modulo 7 for some `0 ≤ s ≤ t ≤ 41`. Boundary 42 is omitted because
`q_42 = 7·1 ≡ q_0`.

Each coordinate of `q_s + q_t` lies in `{0, ..., 14}`. The residues 0 and 1
in that range are exactly `{0, 1, 7, 8, 14}`, and the mask bit is 1 on
`{1, 8}`. The weight is the number of mask bits. The coordinate sum of
`q_t` is `t`, so a realizing pair satisfies `s + t ≡ weight (mod 7)`.

## Census

There are `42·43/2 = 903` pairs. The checker visits each pair once, compares
the allowed-set reading with the modulo-7 reading, and classifies all 63
nonzero masks.

| weight | masks | realized | missing on this word |
|---:|---:|---:|---|
| 1 | 6 | 6 | none |
| 2 | 15 | 14 | `(3, 5)` |
| 3 | 20 | 19 | `(1, 3, 5)`, the recorded #7016 gap |
| 4 | 15 | 14 | `(0, 1, 3, 5)` |
| 5 | 6 | 6 | none |
| 6 | 1 | 1 | none |

The non-weight-3 misses are exactly `(3, 5)` and `(0, 1, 3, 5)`. Realizing
pairs of the nonzero masks number 16, 19, 19, 19, 15 and 8 at weights 1
through 6. Eight further pairs realize the zero vector. The zero vector is
not a depth-two obligation.

The first six letters are `023514`, one copy of each source. A reviewer can
check three pairs by hand: `(0, 1)` realizes `(0)`, `(0, 3)` realizes
`(0, 2, 3)`, and `(0, 6)` realizes every source. The checker requires those
three sums.

Of the 16 masks that contain both sources 3 and 5, the census realizes 13.
The three unrealized masks are the whole missing list above. In particular
`(0, 3, 5)` and `(1, 2, 3, 5)` are realized, so the census does not say that
every mask containing `{3, 5}` is missed.

Including `t = 42` adds no nonzero mask beyond this list.

## What the census establishes

Under the interface above, this one word misses exactly two nonzero masks
of weight other than 3, namely `(3, 5)` and `(0, 1, 3, 5)`. A depth-two
block needs every nonzero mask. This word does not provide one.

The evidence is an exhaustive finite census. The domain, the 903 pairs with
`0 ≤ s ≤ t ≤ 41`, is finite. The enumeration is the double loop over that
triangle, and the program checks that the loop visits 903 pairs. The
modulo-7 reading and the allowed-set reading agree on every pair. Every
realizing pair satisfies the weight identity. The separate `t = 42` pass
finds no extra nonzero mask.

This does not prove that every six-source floor word at characteristic 7
misses these masks, and it does not prove that no depth-two block exists.
It does not re-prove the one-pair weight-3 cover bound of PR #7016. The
weight-3 line of the table is a control that this is the recorded witness.
No supplier, consumer, or selected frontier changes.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -W error -B research/six-source-c7-witness-other-weights/verify.py
python3.12 -I -O -W error -B research/six-source-c7-witness-other-weights/verify.py
python3.12 -B scripts/research_package.py --package research/six-source-c7-witness-other-weights --check-only
```

The marker is

```text
PASS_SIX_SOURCE_C7_WITNESS_OTHER_WEIGHTS pairs=903 nonzero_hit=60/63 other_hit=41/43 missing_other=(3,5);(0,1,3,5) weight3_missing=(1,3,5) zero_pairs=8 boundary42_new=0 superset_realized=13/16 controls=7
```

The seven controls are the floor-word shape of the recorded literal, the
agreement of the two mask readings, the weight identity on every nonzero
hit, the three hand-checked prefix pairs together with the recorded
weight-3 gap `(1, 3, 5)`, the empty boundary-42 increment, the thirteen
realized masks among the sixteen that contain `{3, 5}`, and the two
negative words: the adjacent transposition of positions 1 and 2 is still a
floor word and has a different non-weight-3 missing set, while changing the
first letter from 0 to 1 is rejected. Failures raise `SystemExit`.
Optimized mode cannot silence them. No SAT solver, Lean, or Docker replay
is used.

## Open next questions

1. Can one explicit six-source length-42 floor word, other than this
   witness, realize both `(3, 5)` and `(0, 1, 3, 5)`? *Why:* a depth-two
   block needs both masks. This census shows that the recorded witness
   misses both. One other word that realizes both would separate that miss
   from the floor-word hypotheses. An exhaustive census of every floor word
   would be a different claim. *First step:* evaluate the same 903-pair
   predicate on one other concrete length-42 floor word and record, for
   these two masks only, whether each is realized. *Blocked by:* only the
   recorded witness is enumerated here, and no second characteristic-7
   floor word is certified in this package. The two-pair weight-3 exchange
   remains open question 1 of PR #7016.

## Credit

The depth-two interface and the weight identity are Nick Petalas's
(PR #4231, PR #4248, PR #6107), with the Ross Richardson PR #934 / PR #943
lineage. JosieElliston's PR #6141 leaves characteristic 7 open. The diagonal
equality case is upstream PR #6941. The witness word, its weight-3 gap
`(1, 3, 5)`, and the request to evaluate the other weights are open
question 2 of upstream PR #7016 (fork PR 179). This package evaluates that
word and does not repeat the one-pair cover argument.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
