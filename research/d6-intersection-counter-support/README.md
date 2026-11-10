# The intersection-counter engine returns the D6 16-word set

**Exhaustive finite comparison on one basis, at one batch size. No new κ.**
The selected conditional exponent stays `781451/250000000`. On the pinned
20-generator kernel of the D6 6-frame incidence code,
`research/e7-intersection-counters/engine.py` at batch size 16 returns the
same 16 words as the literal span. The SHA256 of the 15 positive words is
`23a7b374a6bc62bc2aca47843d52a01fa8e791ed3a98085133829d816c5094e8`.

## Result

The lines and the two anchors are the D6 unit in
`research/d6-punctured-frame-code/ROOTS.json`. The anchors are the orthogonal
E8 lines `(2, 2, 0, 0, 0, 0, 0, 0)` and `(2, -2, 0, 0, 0, 0, 0, 0)`. The
stored lines are exactly the E8 lines orthogonal to both anchors, and they
equal the coordinate lines `±2e_i ± 2e_j` on axes `2, 3, 4, 5, 6, 7`. The
line-list SHA256, of the JSON array with no extra spaces, is
`bd3d7efd8a94a7d0a6a7339cfd95805bb6907f3951ff67e9669b317655869538`.

An orthogonal 6-frame is the both-sign lift of a perfect matching of those
six axes. There are 15 such frames. The F2 incidence matrix has rank 10. A
kernel basis with an identity on the free coordinates

```text
(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 13, 14, 15, 16, 20, 21, 22, 23, 24)
```

is orthogonal to every frame row. That basis is these twenty integers, in
free-coordinate order:

```text
101451777
101451778
1007553540
168428552
168428560
1007553568
2112
1152
772279552
772279808
528384
270336
147456
504266752
504299520
537919488
270532608
138412032
75497472
50331648
```

Ten of these generators have weight 2, so they already lie in the
weight-at-most-2 set. The other ten generators are heavier and lie in the
span outside that set. A binary-reflected Gray walk visits each of the
`2^20 = 1048576` codewords once. At step `index` the flipped generator is
the lowest set bit of `index`, and the coefficient vector is
`index XOR (index >> 1)`. The free coordinates of the running word are
checked against that coefficient at every index. Because those coordinates
are an identity basis, the coefficient is the unique preimage of the word,
the Gray map is bijective, and the walk is a complete enumeration of the
span. The words of weight at most 2 are zero and exactly these 15 supports,
and no nonzero word in that subset is lighter:

```text
3, 24, 36, 768, 1152, 2112, 98304, 147456, 270336, 528384,
50331648, 75497472, 138412032, 270532608, 537919488
```

Five of those supports are proper sums: they are not among the twenty
generators. The support hash is SHA256 of the UTF-8 bytes of
`json.dumps(sorted(positive_words))`, with the default separators. Both the
literal census and the engine stream produce
`23a7b374a6bc62bc2aca47843d52a01fa8e791ed3a98085133829d816c5094e8`.

The engine call is `low_weight_words` from
`research/e7-intersection-counters/engine.py`, with `population_planes` and
`at_most` injected from `research/e7-bitsliced-exhaustion/binary.py`. Those
two helpers are the engine's required weight routines. The comparison does
not call that file's `low_weight_words`; a direct call with the injected
keywords raises `TypeError`. The stream below is one call at batch size 16,
width 30, and weight bound 2.

| Quantity | Value |
|---|---:|
| Lines | 30 |
| Orthogonal 6-frames | 15 |
| Incidence rank | 10 |
| Kernel dimension | 20 |
| Distinct codewords | 1048576 |
| Batch size | 16 |
| Lane generators | 16 |
| High-offset batches | 16 |
| High generators outside the lane span | 4 |
| Engine stream | 16 distinct words |
| Words of weight 2 | 15 |
| Words of weight at most 2 | 16 |
| Weight-2 generators | 10 |
| Supports that are proper sums | 5 |
| Set equality | yes |
| Positive-word SHA256 | `23a7b374…6c5094e8` |

Batch size 16 puts the first 16 generators in one lane block. The pinned
engine then walks every offset in the span of the remaining 4 generators:
its loop bound is `1 << (len(rows) - count)`, which is 16 on this input.
Those four generators each have weight 2, and each lies outside the
65536-word span of the first 16, so each is a target word that a lane-only
pass cannot emit. The literal Gray walk already lists every codeword. The
engine stream equals that weight-filtered set, with no repeated yield. The
Gray walk is an exhaustive finite census of this 1048576-word span. The
engine result is equality of its 16 yielded words with the weight-at-most-2
subset, at batch size 16. It is a comparison of one finite input. It does
not decide another batch size or another code.

Removing the least positive word makes the sets unequal and changes the
hash. Passing the first generator twice raises `ValueError` with the
engine's message `dependent generators`. Batch size 3 leaves 17 high
generators. The engine raises `ValueError` with the message
`batch count exceeds 65536` before yielding a word. That is one refusal
control. The legal batch sizes other than 16 were not compared.

## Scope

Task card `replay-runtime`, priority revision 8, base
`17469fff78c22941280f04d39dc5a1faee09c840`. Scope status is **refined**.

The card asks for a measured speedup that keeps coverage. The revision-8
verification row requires the sets to be compared before a faster replay
counts as the same coverage. The merged package
`research/e7-intersection-counters` times the complete E7 consumer and
states that other codes are outside its claim. The predecessor comparison
on this D6 code binds `low_weight_words` from
`research/e7-bitsliced-exhaustion/binary.py` and leaves this engine unrun.
This package runs that engine on the twenty generators above.

The selected record at this base is `781451/250000000`. The priorities page
on the same base still prints the older PR #5599 decimal. This package uses
the selected record and does not change it. No timing is recorded, and the
comparison is not a speedup claim. The 27-dimensional E7 census is not
replayed. The bit-lane D6 census, the E6 64-word hash
`ad4a1d101774e6c2da40cde3d097d39aa56ee5668dcdca858513c5fec3578215`, and the
P112 8-word set are different comparisons and are outside this one.

Ordered overlap check on 2026-11-10, after fetching canonical `main` at
`17469fff78c22941280f04d39dc5a1faee09c840`. GitHub search of open pull
requests for the support hash and for a 20-generator intersection-counter
comparison returned no D6 engine comparison. Open PR #7034 records that the
same engine refuses the P112 36-generator basis, because that dimension
exceeds 27. This basis has dimension 20, the engine accepts it, and the
yielded set is the 16-word set above. Merged #6959 is the bit-lane
comparison that states this hash and leaves the engine unrun. Merged #6960
is the E6 64-word engine comparison. The last 25 top-level comments on
discussion #1166, through 2026-11-09, do not mention this hash. A repository
code search was rate-limited and was not used. No fork `cursor/*` branch
named this D6 engine comparison before this one. The predecessor D6 branch,
the E6 engine branch, and the P112 engine branch are different questions.

## Reproduce

Python 3.12 and the standard library, from the repository root. The census
is 1048576 codewords and finishes in well under a second.

```sh
python3 -B scripts/research_package.py --package research/d6-intersection-counter-support --check-only
python3 -I -B research/d6-intersection-counter-support/verify.py
python3 -I -O -B research/d6-intersection-counter-support/verify.py
python3 -B scripts/research_package.py --package research/d6-intersection-counter-support
```

The direct verifier prints

```text
PASS_D6_INTERSECTION_COUNTER_SUPPORT batch=16 words=16 supports=15 hash=23a7b374a6bc62bc2aca47843d52a01fa8e791ed3a98085133829d816c5094e8 equal=True e7_census=false bit_lane_census=false timed=false no_new_kappa=true
```

Checked here: normal and optimized direct runs, metadata check, and the
registered package runner. The selected-baseline script, the E7 census, the
bit-lane D6 census, Lean, Docker, and any timing harness were not run.

## Open next questions

1. Does the same set equality hold at another legal batch size on this
   20-generator basis, for example 8 or 20? Batch size changes the lane
   split, so batch size 16 does not decide it. First rerun this comparison
   with `batch_bits` 8, or 20, and the same twenty generators, weight bound,
   and support hash. Nothing mathematical blocks that rerun. This package
   stops after batch size 16. Batch size 3 is refused before any yield, so
   it is not a second comparison.

2. Can this opt-in engine be installed at a caller that consumes the D6
   6-frame code, with regenerated source pins? Set equality on one code
   leaves that replacement untouched. The first step is the installation
   and source-bound compatibility check already stated by
   `research/e7-intersection-counters`. This comparison does not regenerate
   consumer pins. Other codes are outside that package's claim.

## Credit

The D6 lines, the orthogonal anchors, and the 15-word support hash are the
predecessor comparison in `research/d6-punctured-frame-code`, merged as PR
#6959. The intersection-counter engine is Nick Petalas's
`research/e7-intersection-counters/engine.py`. The injected population and
threshold routines are Ali Romman's PR #5729,
`research/e7-bitsliced-exhaustion/binary.py`. The request to run this engine
on the 20-generator basis is open question 3 of that D6 package. The E6
engine comparison in merged PR #6960 is the pattern for this check and is a
different code. Open PR #7034 records the engine's refusal of the P112
36-generator basis and is not rerun here.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review and no formal-kernel acceptance are claimed.
