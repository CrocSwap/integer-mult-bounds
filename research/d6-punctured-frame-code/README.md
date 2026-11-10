# The D6 punctured frame code matches the bit-lane iterator

**Coverage check of a published replay engine on one D6 slice. No new κ.**
The selected conditional exponent stays `781451/250000000`. On the 30 D6
lines orthogonal to one pinned orthogonal pair of E8 roots,
`low_weight_words` returns exactly the words of weight at most 2 in the F2
incidence code of the 15 orthogonal 6-frames. That code is 20-dimensional.
Zero and exactly 15 weight-2 words occur, and no nonzero word is lighter.

## Result

The root list is pinned in [ROOTS.json](ROOTS.json). The anchors are the E8
lines `(2, 2, 0, 0, 0, 0, 0, 0)` and `(2, -2, 0, 0, 0, 0, 0, 0)`. Their inner
product is 0 and each has norm 8. The stored lines are exactly the E8 lines
orthogonal to both anchors. They are also exactly the coordinate lines
`±2e_i ± 2e_j` on axes `2, 3, 4, 5, 6, 7`, one representative of each sign
pair, first nonzero coordinate positive. The line-list SHA256, of the JSON
array with no extra spaces, is
`bd3d7efd8a94a7d0a6a7339cfd95805bb6907f3951ff67e9669b317655869538`.

Two such lines are orthogonal if and only if their supports are equal or
disjoint. The supports are the 15 edges of `K_6`. An orthogonal 6-frame is
the both-sign lift of a perfect matching: each of the three edges contributes
its two lines. There are `5·3·1 = 15` perfect matchings, and the clique
search returns that same set of 15 frames. Every line lies in 3 frames. The
sum of the 15 frame rows is the all-one word, so every kernel word has even
weight.

| Quantity | Value |
|---|---:|
| Lines | 30 |
| Orthogonal 6-frames | 15 |
| Incidence rank | 10 |
| Kernel dimension | 20 |
| Distinct codewords | 1048576 |
| Least positive weight | 2 |
| Words of weight 2 | 15 |
| Words of weight at most 2 | 16 |

The 15 weight-2 words are the partner-pair indicators: the two sign lines of
one edge. That identification does not use the bit-lane engine. Every vector
in `F_2^30` of weight 0, 1 or 2 was tested against the 15 frame parities
(1 + 30 + 435 vectors). The vectors that pass are zero and those 15
indicators. A non-partner pair fails because some matching contains exactly
one of its two edges, and the corresponding frame then meets the pair in one
line.

A kernel basis with an identity on the free coordinates
`(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 13, 14, 15, 16, 20, 21, 22, 23, 24)`
is orthogonal to every frame row. Walking the binary-reflected Gray code
flips the lowest set bit of the step index and visits each of the `2^20`
codewords once. The free bits of the current word are checked against
`index XOR (index >> 1)` at every index, so the visit is bijective onto the
kernel. The words of weight at most 2 are the screened set.
The weight distribution of the whole code is symmetric and supported on even
weights:

```text
0:1  2:15  4:105  6:1095  8:10965  10:59067  12:170125  14:282915
16:282915  18:170125  20:59067  22:10965  24:1095  26:105  28:15  30:1
```

A half-split after 10 generators returns the same 16-word set. The halves are
spans of complementary pieces of an independent basis, so each codeword is
`high XOR low` for exactly one pair. `low_weight_words` from
`research/e7-bitsliced-exhaustion/binary.py`, at batch sizes 16 and 8,
returns that set with no repeated yield. Weight bound 1 returns only zero.
These enumerations do not call each other.

The sorted positive supports, as integers in the pinned line order, are

```text
3, 24, 36, 768, 1152, 2112, 98304, 147456, 270336, 528384,
50331648, 75497472, 138412032, 270532608, 537919488
```

Their SHA256, of `json.dumps` of that list, is
`23a7b374a6bc62bc2aca47843d52a01fa8e791ed3a98085133829d816c5094e8`.

A copy of the set with one support removed compares unequal. Clearing the
top bit of a partner mask produces a weight-1 word that is absent from the
code, and the weight predicate rejects a set that contains it. The mask of
lines 0 and 2 is a weight-2 word outside the set. The engine rejects a
repeated generator.

## Scope

Task card `replay-runtime`, priority revision 8, base
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Scope status is **refined**.

The card asks for a new measured speedup that keeps coverage. The
revision-8 verification row instead says that faster output is not the same
coverage until checked. The merged E7 package compared the engine with the
27-dimensional kernel. The E6 4-frame package compared width 36 and weight
16. This package is the D6 half of the question that package left open.
Width 30, weight bound 2, twenty generators. It does not time the engine,
replace a consumer, rerun the E6 census, or build the P112 deletion.

The selected record's κ is `781451/250000000`. The priority note on this
base still quotes the older displayed value `0.00310045` from PR #5599.
This package uses the selected record and does not change it.

Ordered overlap check on 2026-11-10, after fetching upstream `main` at
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. `scripts/find_overlap.py
--refresh` read 885 open pull requests and 6934 discussion records
(fetched `2026-11-10T02:05:29Z`). The phrases "D6 punctured frame", "d6
frame code" and "orthogonal 6-frame" had no matches. Discussion comment
19492511 is the E6 finding; it does not build this kernel. Comment
19003654 records PR #3266, a D6 frame-puncture support-capacity
obstruction, which is a different object and is not replayed. Open #6632
partitions the E7 weight-12 words. No fork `cursor/*` branch named this
comparison before this one.

This is an exhaustive finite census of two finite domains: all 466 vectors
of weight at most 2, and all `2^20` kernel words. It is not a proof that
the iterator is correct for every generator matrix, and it is not an
unrestricted nonexistence result. A failed search was not used.

## Reproduce

Python 3.12 and the standard library, from the repository root. The census
is `2^20` codewords and finishes in well under a second.

```sh
python3 -B scripts/research_package.py --package research/d6-punctured-frame-code --check-only
python3 -I -B research/d6-punctured-frame-code/verify.py
python3 -I -O -B research/d6-punctured-frame-code/verify.py
python3 -B scripts/research_package.py --package research/d6-punctured-frame-code
```

The direct verifier prints

```text
PASS_D6_PUNCTURED_FRAME_CODE width=30 frames=15 dimension=20 minimum=2 supports=15 codewords=1048576 batches=16,8 split=10 e6_census_replayed=false p112_built=false no_new_kappa=true
```

Not run: the #5729 timing harness, the E6 4-frame census, the E7 kernel,
`research/e7-intersection-counters/engine.py`, any P112 root list, Lean,
Docker, and `scripts/research_selected_baseline.py` as a scientific replay.
The selected record is provenance only.

## Open next questions

1. Does one other orthogonal E8 anchor pair induce the same set equality
   after the coordinate permutation that carries it to this pair? This pin
   is one pair. First reflect one pinned anchor by one simple E8 root,
   rebuild the 30-line list, and compare the transported partner supports
   with the hash above.
2. Does the same set equality hold for one P112 punctured frame code, at a
   named width and weight bound? The D6 check does not transfer. First pin
   that 112-line complement of one orthogonal 8-frame and compare one
   half-split with `low_weight_words` on that basis alone. No P112 list is
   pinned here.
3. Does the opt-in intersection-counter engine return this same 16-word set?
   A faster substitute is not coverage for this basis until the sets are
   compared. This is not the E6 64-word hash. First run
   `research/e7-intersection-counters/engine.py` on this 20-generator basis
   at one batch size and compare it with the support hash above. This
   package does not load that engine.

## Credit

The D6 model as the lines orthogonal to an orthogonal E8 pair is the
geometry used by Nick Petalas's mixed-support arguments, including the
frame-puncture obstruction in PR #3266. That obstruction is not this
iterator comparison. The coordinate root lines match the `D(6)` construction
in `research/char2-threshold/lib/roots.py`. The bit-lane engine is Ali
Romman's PR #5729, `research/e7-bitsliced-exhaustion/binary.py`. The request
to test one D6 punctured frame code is the first open question of the E6
4-frame coverage check, discussion comment 19492511.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review and no formal-kernel acceptance are claimed.
