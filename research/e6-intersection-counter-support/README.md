# The intersection-counter engine returns the E6 64-word set

**Exhaustive finite comparison on one basis, at one batch size. No new κ.**
The selected conditional exponent stays `781451/250000000`. On the pinned
7-generator kernel of the E6 4-frame incidence code,
`research/e7-intersection-counters/engine.py` at batch size 16 returns the
same 64 words as the literal span. The SHA256 of the 63 positive words is
`ad4a1d101774e6c2da40cde3d097d39aa56ee5668dcdca858513c5fec3578215`.

## Result

The lines and the two anchors are the E6 unit in
`research/e6-e7-shadow-minrank-upper/WITNESSES.json`. The anchors are E8
roots with inner product 4. The stored lines, in witness order, are exactly
the E8 lines orthogonal to both anchors. Each line has norm 8.

An orthogonal 4-frame is an increasing 4-clique in that orthogonality graph.
There are 135 such frames, and every line lies in 15 of them. The F2
incidence matrix has rank 29. A kernel basis with an identity on the free
coordinates `(0, 1, 2, 4, 6, 8, 20)` is orthogonal to every frame row. That
basis is these seven integers, in free-coordinate order:

```text
6591703721
6306835114
13904919564
45813124144
28344004800
68452089600
68718428160
```

Two of these generators have weight 20, so they lie in the span and outside
the weight-at-most-16 set. Doubling through the seven generators lists 128
distinct codewords. The words of weight at most 16 are zero and exactly 63
words of weight 16, and no nonzero word is lighter. The support hash is SHA256 of the UTF-8 bytes of
`json.dumps(sorted(positive_words))`, with the default separators. Both the
literal census and the engine stream produce
`ad4a1d101774e6c2da40cde3d097d39aa56ee5668dcdca858513c5fec3578215`.

The engine call is `low_weight_words` from
`research/e7-intersection-counters/engine.py`, with `population_planes` and
`at_most` injected from `research/e7-bitsliced-exhaustion/binary.py`. Those
two helpers are the engine's required weight routines. The comparison does
not call that file's `low_weight_words`; a direct call with the injected
keywords raises `TypeError`. The stream below is one call at batch size 16,
width 36, and weight bound 16.

| Quantity | Value |
|---|---:|
| Lines | 36 |
| Orthogonal 4-frames | 135 |
| Incidence rank | 29 |
| Kernel dimension | 7 |
| Distinct codewords | 128 |
| Batch size | 16 |
| Lane generators | 7 |
| High-offset batches | 1 |
| Engine stream | 64 distinct words |
| Words of weight 16 | 63 |
| Words of weight at most 16 | 64 |
| Set equality | yes |
| Positive-word SHA256 | `ad4a1d10…c3578215` |

Batch size 16 is at least the dimension, so `checked_rows` puts all seven
generators in one lane block and the high-offset loop runs once. The
literal doubling already lists every codeword. The engine stream equals
that weight-filtered set, with no repeated yield. This is an exhaustive
finite census of this 128-word span at this batch size. It is a comparison
of one finite input, and it does not decide another batch size or another
code.

Removing the least positive word makes the sets unequal and changes the
hash. Passing the first generator twice raises `ValueError` with the
engine's message `dependent generators`.

## Scope

Task card `replay-runtime`, priority revision 8, base
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Scope status is **refined**.

The card asks for a measured speedup that keeps coverage. The revision-8
verification row requires the sets to be compared before a faster replay
counts as the same coverage. The merged package
`research/e7-intersection-counters` times the complete E7 consumer and
states that other codes are outside its claim. The predecessor comparison
on this E6 code binds `low_weight_words` from
`research/e7-bitsliced-exhaustion/binary.py` and leaves this engine unrun.
This package runs that engine on the seven generators above.

The selected record at this base is `781451/250000000`. The priorities page
on the same base still prints the older PR #5599 decimal. This package uses
the selected record and does not change it. No timing is recorded. The
27-dimensional E7 census is not replayed. A D6 or P112 punctured frame is a
different code and is outside this comparison.

Ordered overlap check on 2026-11-10, after fetching `upstream/main` at
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. `scripts/find_overlap.py` searched
the terms `ad4a1d101774e6c2`, `e6-frame-code-lane-coverage`, and
`intersection-counter engine`, including closed pull requests. Coverage:
local notes at that head, 8919 records, complete inventory; 885 open PR
bodies fetched at `2026-11-10T02:02:41Z`; 6934 discussion records fetched at
`2026-11-10T02:03:39Z`; 5530 closed PR bodies fetched at
`2026-11-10T02:04:20Z`. The report lists 0 matches. Comment bodies in that snapshot have no copy
of the hash. Replies past the first 100 on comments after each discussion's
first page are outside that helper's walk. The discussion-comment lookup
for id 19492511 returned HTTP 404. The predecessor text that states
this hash and leaves the engine comparison open is fork commit
`f770aeb71385a5e14b38ca6e1e0df6cccde6c646` on
`cursor/replay-coverage-gap-3fad`. A direct run of that commit's verifier
printed the same hash, the same free coordinates, and 64 words. That run
calls the bit-lane enumerator. This package's comparison does not.

## Reproduce

Python 3.12 and the standard library, from the repository root. The census
is 128 codewords and finishes in well under a second.

```sh
python3 -B scripts/research_package.py --package research/e6-intersection-counter-support --check-only
python3 -I -B research/e6-intersection-counter-support/verify.py
python3 -I -O -B research/e6-intersection-counter-support/verify.py
python3 -B scripts/research_package.py --package research/e6-intersection-counter-support
```

The direct verifier prints

```text
PASS_E6_INTERSECTION_COUNTER_SUPPORT batch=16 words=64 supports=63 hash=ad4a1d101774e6c2da40cde3d097d39aa56ee5668dcdca858513c5fec3578215 equal=True e7_census=false timed=false no_new_kappa=true
```

Checked here: normal and optimized direct runs, metadata check, and the
registered package runner. The selected-baseline script, the E7 census,
Lean, Docker, and any timing harness were not run.

## Open next questions

1. Does the same set equality hold at another legal batch size, for example
   8? Batch size changes the lane split, so batch size 16 does not decide
   it. First rerun this comparison with `batch_bits` 8 and the same seven
   generators, weight bound, and support hash. Nothing mathematical blocks
   that rerun. This package stops after batch size 16.

2. Can this opt-in engine be installed at a caller that consumes the E6
   4-frame code, with regenerated source pins? Set equality on one code
   leaves that replacement untouched. The first step is the installation
   and source-bound compatibility check already stated by
   `research/e7-intersection-counters`. This comparison does not regenerate
   consumer pins.

## Credit

The E6 lines and A2 anchors are Nick Petalas's shadow witness in
`research/e6-e7-shadow-minrank-upper`. The intersection-counter engine is
Nick Petalas's `research/e7-intersection-counters/engine.py`. The injected
population and threshold routines are Ali Romman's PR #5729,
`research/e7-bitsliced-exhaustion/binary.py`. The 64-word set and the
support hash are the predecessor comparison on fork branch
`cursor/replay-coverage-gap-3fad`.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review and no formal-kernel acceptance are claimed.
