# The other 61 masks on the #7041 block word

**Exhaustive finite census of one word, plus a direct miss for the full mask. No new κ.** The length-42 floor word recorded in PR #7041,

```text
350122222224444444000000111111333333555555
```

with blocks `3, 5, 0, 1, 2^7, 4^7, 0^6, 1^6, 3^6, 5^6`, realizes both `(3, 5)` and `(0, 1, 3, 5)`. On the same 903 pairs, the other 61 nonzero masks split as follows: **11 are realized and 50 are missed.** A depth-two block needs every nonzero mask, so this word is not a depth-two block.

The selected conditional κ remains `363005817/100000000000` in `certificates/selected-result.json`. This package does not change it.

## Interface, unchanged

A floor word on six sources in characteristic 7 has length 42 and calls each source seven times. `q_t` counts the first `t` letters, so `q_0 = 0` and `q_42 = (7, 7, 7, 7, 7, 7)`. A pair `0 ≤ s ≤ t ≤ 41` realizes a binary mask when every coordinate of `q_s + q_t` lies in `{0, 1, 7, 8, 14}` and the mask bit is 1 exactly on `{1, 8}`. Those six integers are the members of `{0, ..., 14}` whose residue modulo 7 is 0 or 1. The allowed-set reading and the residue reading are both computed. A disagreement fails the predicate. This is the predicate of PR #7041, which is the interface of PR #4231 / PR #4248 as used by the c=7 diagonal note. Boundary 42 is outside the predicate.

The coordinate sum of `q_t` is `t`, so a realizing pair satisfies `s + t ≡ weight (mod 7)`. The checker requires that identity on every pair that has a reading, including the zero mask.

## Closed form of this word

Write counts in source order `(0, 1, 2, 3, 4, 5)`. For `0 ≤ t ≤ 42`,

| source | `q_t` |
|---|---|
| 0 | `0` on `t ≤ 2`, `1` on `3 ≤ t ≤ 18`, `t − 17` on `19 ≤ t ≤ 24`, then `7` |
| 1 | `0` on `t ≤ 3`, `1` on `4 ≤ t ≤ 24`, `t − 23` on `25 ≤ t ≤ 30`, then `7` |
| 2 | `0` on `t ≤ 4`, `t − 4` on `5 ≤ t ≤ 11`, then `7` |
| 3 | `0` at `t = 0`, `1` on `1 ≤ t ≤ 30`, `t − 29` on `31 ≤ t ≤ 36`, then `7` |
| 4 | `0` on `t ≤ 11`, `t − 11` on `12 ≤ t ≤ 18`, then `7` |
| 5 | `0` on `t ≤ 1`, `1` on `2 ≤ t ≤ 36`, `t − 35` on `t ≥ 37` |

At `t = 41`, source 5 is 6. The value 7 on source 5 occurs only at `t = 42`, which is not a pair endpoint. The checker compares this formula with the cumulative count of the block literal at every `t` from 0 through 42.

## The other 61

The domain is the 63 nonzero masks. The two targets below are a predicate control: their realizing pairs are exactly the six pairs recorded in PR #7041. The other 61 are the claim.

**Realized, 11 masks, 19 pairs.**

| mask | pairs and sums |
|---|---|
| `(3)` | `(0, 1) → (0,0,0,1,0,0)`; `(2, 41) → (7,7,7,8,7,7)`; `(30, 41) → (14,14,14,8,14,7)` |
| `(5)` | `(0, 36)` and `(1, 35) → (7,7,7,7,7,1)`; `(37, 41)`, `(38, 40)` and `(39, 39) → (14,14,14,14,14,8)` |
| `(0, 3)` | `(3, 41) → (8,7,7,8,7,7)` |
| `(1, 3)` | `(24, 41) → (14,8,14,8,14,7)` |
| `(0, 3, 5)` | `(0, 3) → (1,0,0,1,0,1)` |
| `(1, 3, 5)` | `(0, 24) → (7,1,7,1,7,1)` |
| `(0, 1, 3)` | `(4, 41) → (8,8,7,8,7,7)`; `(11, 41) → (8,8,14,8,7,7)`; `(18, 41) → (8,8,14,8,14,7)` |
| `(0, 1, 2, 3)` | `(5, 41) → (8,8,8,8,7,7)` |
| `(0, 1, 3, 4)` | `(12, 41) → (8,8,14,8,8,7)` |
| `(0, 1, 2, 3, 5)` | `(0, 5) → (1,1,1,1,0,1)` |
| `(0, 1, 3, 4, 5)` | `(0, 12) → (1,1,7,1,1,1)` |

**Missed, 50 masks, no realizing pair.** By weight, the counts are 4, 12, 17, 12, 4 and 1.

- Weight 1: `(0)`, `(1)`, `(2)`, `(4)`.
- Weight 2: `(0, 1)`, `(0, 2)`, `(0, 4)`, `(0, 5)`, `(1, 2)`, `(1, 4)`, `(1, 5)`, `(2, 3)`, `(2, 4)`, `(2, 5)`, `(3, 4)`, `(4, 5)`.
- Weight 3: `(0, 1, 2)`, `(0, 1, 4)`, `(0, 1, 5)`, `(0, 2, 3)`, `(0, 2, 4)`, `(0, 2, 5)`, `(0, 3, 4)`, `(0, 4, 5)`, `(1, 2, 3)`, `(1, 2, 4)`, `(1, 2, 5)`, `(1, 3, 4)`, `(1, 4, 5)`, `(2, 3, 4)`, `(2, 3, 5)`, `(2, 4, 5)`, `(3, 4, 5)`.
- Weight 4: `(0, 1, 2, 4)`, `(0, 1, 2, 5)`, `(0, 1, 4, 5)`, `(0, 2, 3, 4)`, `(0, 2, 3, 5)`, `(0, 2, 4, 5)`, `(0, 3, 4, 5)`, `(1, 2, 3, 4)`, `(1, 2, 3, 5)`, `(1, 2, 4, 5)`, `(1, 3, 4, 5)`, `(2, 3, 4, 5)`.
- Weight 5: `(0, 1, 2, 3, 4)`, `(0, 1, 2, 4, 5)`, `(0, 2, 3, 4, 5)`, `(1, 2, 3, 4, 5)`.
- Weight 6: `(0, 1, 2, 3, 4, 5)`.

The two predicate-control masks, not part of the 61, are `(3, 5)` at `(0, 2)`, `(0, 30)` and `(1, 36)`, and `(0, 1, 3, 5)` at `(0, 4)`, `(0, 11)` and `(0, 18)`.

## Completeness for this word

There are `42 · 43 / 2 = 903` pairs. The checker visits each pair once. On every pair the two readings agree, and every reading satisfies the weight identity. The visit splits as 25 nonzero-mask pairs, 4 zero-mask pairs and 874 pairs with a coordinate outside `{0, 1, 7, 8, 14}`.

The zero-mask pairs are `(0, 0)`, `(36, 41)`, `(37, 40)` and `(38, 39)`. They are not nonzero masks, so they are outside the 61. The 25 nonzero pairs are exactly the 19 pairs of the 11 masks above and the 6 target pairs. Every one of the 50 listed masks is absent from that hit set, and the 11 + 50 + 2 lists are pairwise disjoint and exhaust the 63 nonzero masks.

That is an exhaustive finite census of the nonzero masks on this one word. The weight-6 row also has the direct argument in the next section. A failed or incomplete search is not this claim.

## The full mask is missed

Source 5 on `0 ≤ t ≤ 41` takes only the values 0, 1, 2, 3, 4, 5 and 6, on the level sets `{0, 1}`, `{2, ..., 36}`, `{37}`, `{38}`, `{39}`, `{40}` and `{41}`. It is nondecreasing. A mask bit on source 5 is 1 only when the two prefix counts sum to 1 or 8.

The pairs with that sum are exactly 73:

- `(0, t)` and `(1, t)` for `t = 2, ..., 36`, because those are the pairs of a 0 with a 1;
- `(37, 41)`, `(38, 40)` and `(39, 39)`, because those are the pairs `2+6`, `3+5` and `4+4`.

No other combination of attained values sums to 1 or 8 with the left index at most the right index. In particular source 5 never equals 7 inside the pair domain, so `1+7` does not occur. The checker builds this set from the level sets, from the three-line rule above, and from the 903-pair scan, and requires the three sets to be equal.

None of the 73 sums is the full mask.

- On `(37, 41)`, `(38, 40)` and `(39, 39)` every source other than 5 sums to 14, so the reading is `(5)`.
- On `(0, t)` the sum is `q_t`. Source 4 equals 1 only at `t = 12`, and there `q_12 = (1, 1, 7, 1, 1, 1)`, whose source-2 coordinate is 7 rather than 1 or 8.
- On `(1, t)`, write `q_1 = (0, 0, 0, 1, 0, 0)`. Sources 0, 1 and 4 are simultaneously in `{1, 8}` only at `t = 12`, where the sum is `(1, 1, 7, 2, 1, 1)`. The coordinate 2 has no reading.

Every pair outside the 73 has source-5 sum outside `{1, 8}`, so it cannot realize a mask with source 5 turned on. The full mask is therefore missed on this word. The same candidate set contains every realizing pair of the seven realized masks that do turn source 5 on, and none of the realizing pairs of the masks that leave it off.

## Limitations

The census and the weight-6 argument apply to this one block word. They do not classify any other floor word. PR #7037 records the mask miss of a different word, the witness `023514103524310254054123145203452034213150`; that inventory is not repeated here. Realizing 13 of the 63 nonzero masks, including the two targets, leaves this word short of a depth-two block by the 50 missed masks. Whether some other six-source floor word at characteristic 7 realizes every nonzero mask stays open. The weight-3 cover arguments of PR #7016, PR #7032 and PR #7045 are not used. No supplier, consumer, or selected conditional κ changes.

Evidence class: an exhaustive finite census of a finite domain of 903 pairs and 63 masks, with the visit count checked against `42·43/2`, together with a direct level-set proof of the one weight-6 miss under the prefix formula of this word. The two target rows are a control that the predicate still returns the PR #7041 pairs. They are not a new realization claim.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -W error -B research/six-source-c7-block-word-mask-inventory/verify.py
python3.12 -I -O -W error -B research/six-source-c7-block-word-mask-inventory/verify.py
python3.12 -B scripts/research_package.py --package research/six-source-c7-block-word-mask-inventory --check-only
python3.12 -B scripts/research_package.py --package research/six-source-c7-block-word-mask-inventory
```

The replay command prints:

```text
PASS_SIX_SOURCE_C7_BLOCK_WORD_MASK_INVENTORY pairs=903 nonzero_masks=63 realized=13 missed=50 other61_realized=11 other61_missed=50 other61_pairs=19 target_controls=2 weight6=miss source5_candidates=73 zero_pairs=4 nonreadings=874 controls=10
```

The ten controls are the floor-word literal, the closed form, the 25 hand sums, the 903-pair scan, the two target pair sets, the 11/50 split of the other 61, the four zero-mask pairs, the weight-6 level sets, one rejected non-floor edit, and one rejected shortened inventory. Failures raise `SystemExit`. No SAT solver, Lean, Docker, census of other floor words, or selected-frontier replay was run.

## Open next questions

1. Does the adjacent exchange of positions 17 and 18, the last `4` and the following `0`, realize the missed weight-1 mask `(4)`? *Why:* this word misses `(0)`, `(1)`, `(2)` and `(4)`, and source 4 occurs only as the block `4^7`. One boundary swap is another single floor word. It is not an adjacent transposition of the PR #7037 witness. *First step:* run the same 903-pair predicate on that swapped word and list the pairs, if any, that read as `(4)`. *Blocked by:* only the unswapped block word is evaluated here.

2. Which of the 17 missed weight-3 masks appear after exchanging positions 10 and 11, the last `2` and the first `4`? *Why:* the only weight-3 masks this word realizes are `(0, 3, 5)`, `(1, 3, 5)` and `(0, 1, 3)`. One edit at the `2^7`/`4^7` boundary tests whether a missed weight-3 mask is an artifact of keeping those blocks contiguous. The cover questions in PR #7016, PR #7032 and PR #7045 are different claims. *First step:* evaluate those 17 masks on that one swapped word. *Blocked by:* this package does not edit the block word.

## Credit

The depth-two interface and the weight identity are Nick Petalas's (PR #4231, PR #4248, PR #6107), with the Ross Richardson PR #934 / PR #943 lineage. JosieElliston's PR #6141 leaves characteristic 7 open. The diagonal equality case on this interface is the package `research/six-source-c7-diagonal-obstruction` (upstream PR #6941). The block word, the two realized targets, and this question are open question 1 of upstream PR #7041. The witness inventory is upstream PR #7037 and is not redone. The non-complement cover is upstream PR #7045 and is not taken.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
