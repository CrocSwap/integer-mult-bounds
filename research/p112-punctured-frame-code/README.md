# The P112 punctured frame code matches the bit-lane iterator

**Coverage check of a published replay engine on one P112 deletion. No new κ.**
The selected conditional exponent stays `781451/250000000`. On the 112 lines
left by one pinned orthogonal 8-frame, `low_weight_words` returns exactly the
words of weight at most 16 in the F2 incidence code of the 1260 orthogonal
8-frames. That code is 36-dimensional. Zero and exactly seven weight-16 words
occur, and no nonzero word is lighter.

## Result

The root list is the coordinate complement in
`research/p112-rank6-frame-coverage/engine.py`. The eight punctured lines are

```text
(2, 2, 0, 0, 0, 0, 0, 0),  (2, -2, 0, 0, 0, 0, 0, 0),
(0, 0, 2, 2, 0, 0, 0, 0),  (0, 0, 2, -2, 0, 0, 0, 0),
(0, 0, 0, 0, 2, 2, 0, 0),  (0, 0, 0, 0, 2, -2, 0, 0),
(0, 0, 0, 0, 0, 0, 2, 2),  (0, 0, 0, 0, 0, 0, 2, -2)
```

at positions `0, 1, 26, 27, 44, 45, 54, 55` in that file's 120-line order.
They are pairwise orthogonal and each has norm 8. The stored live lines are
the other 112 lines, in increasing position. An independent E8 builder
reproduces the same ordered list. Its SHA256, of `json.dumps` of the 112
coordinate lists, is
`4db9ba14034f55b0b95d69451e809a0c3bf618473209ae3d47d4992e180d14ab`.

An orthogonal 8-frame is an 8-clique in the live orthogonality graph. There
are 1260 such frames, and every live line lies in 90 of them. The F2
incidence matrix has rank 76. A kernel basis with an identity on the free
coordinates

```text
(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20,
 24, 25, 26, 28, 30, 32, 34, 36, 40, 42, 48, 49, 50, 51, 52, 56, 58, 64, 80)
```

is orthogonal to every frame row.

| Quantity | Value |
|---|---:|
| Lines | 112 |
| Orthogonal 8-frames | 1260 |
| Incidence rank | 76 |
| Kernel dimension | 36 |
| Distinct codewords | 68719476736 |
| Least positive weight | 16 |
| Words of weight 16 | 7 |
| Words of weight at most 16 | 8 |

The seven weight-16 words are disjoint and cover every live line, so their
symmetric difference is the all-ones word. With the axis pairs
`A={0,1}`, `B={2,3}`, `C={4,5}`, `D={6,7}`, they are:

1. Both signs of every root joining `A` with `D`, or `B` with `C`.
2. Both signs of every root joining `A` with `C`, or `B` with `D`.
3. Both signs of every root joining `A` with `B`, or `C` with `D`.
4.–7. The spinor lines whose four within-pair sign disagreements lie in
   `{0000,1111}`, `{0011,1100}`, `{0101,1010}`, or `{0110,1001}`.

That description does not use the bit-lane engine. Each of the seven blocks
meets every live 8-frame evenly. Moving the top bit of the first block onto
the top bit of the second leaves a weight-16 word outside the seven, and
that word fails a frame parity.

The blocks, as integers in the pinned live order, are

```text
64691900160
1034819666160
280375465144335
4772259772306660006937399132160
15509841550538713979819718082560
1216944648758260568639796318044160
3955070108453721685622467917250560
```

Their SHA256, of `json.dumps` of that sorted list, is
`ff8861dab18040c03d403a860773218df7c120d03770d701afb61b78c941e3d3`.

`scan.c` lists each half of the ordered basis by doubling. Splits after 18
generators and after 16 generators each visit `2^36` codewords once. They
return one weight distribution, symmetric under complement, with the eight
words above as the weight-at-most-16 set:

```text
0:1  16:7  20:336  22:3584  24:3752  26:10752  28:6864  30:50176
32:872613  34:2243584  36:5633600  38:21482496  40:123827424
42:275960832  44:878407488  46:1531507712  48:3797117779
50:4774038528  52:8574631520  54:8427087872  56:11893702896
58:8427087872  60:8574631520  62:4774038528  64:3797117779
66:1531507712  68:878407488  70:275960832  72:123827424
74:21482496  76:5633600  78:2243584  80:872613  82:50176
84:6864  86:10752  88:3752  90:3584  92:336  96:7  112:1
```

`low_weight_words` from `research/e7-bitsliced-exhaustion/binary.py`, at
batch size 20, returns that same eight-word set and no repeated yield. These
enumerations do not call each other. Batch size 16 was not run: one scan of
this dimension is the registered comparison. A copy of the set with one
support removed compares unequal. Clearing the top bit of a support produces
a weight-15 word that fails a frame parity, and the weight predicate rejects
a set that contains it. The engine rejects a repeated generator. On
generators `(1, 2, 4)`, weight bound 1 returns `{0,1,2,4}` and weight bound
0 returns only zero.

## Scope

Task card `replay-runtime`, priority revision 8, base
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Scope status is **refined**.

The card asks for a new measured speedup that keeps coverage. The
revision-8 verification row instead says that faster output is not the same
coverage until checked. The merged E7 package compared the 27-dimensional
kernel. The E6 package compared width 36 and weight 16. This package is the
P112 half of the question that package left open. Width 112, weight bound
16, thirty-six generators. It does not time the engine, replace a consumer,
rerun the E6 or D6 census, or call the intersection-counter engine.

The selected record's κ is `781451/250000000`. The priority note on this
base still quotes the older displayed value `0.00310045` from PR #5599.
This package uses the selected record and does not change it.

Ordered overlap check on 2026-11-10, after fetching upstream `main` at
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. `scripts/find_overlap.py
--refresh` read 895 open pull requests and 6951 discussion records
(discussions fetched `2026-11-10T02:33:54Z`). The phrases "P112 punctured
frame", "p112 frame code", "punctured frame code" and "orthogonal 8-frame
incidence" matched three items, none of which builds this kernel. Open
#6948 is the E6 comparison and asks this question. Discussion reply
19507129 compares the intersection counter with the E6 64-word set and
names this P112 question as out of scope. Discussion reply 19507177 is the
D6 width-30 comparison. No fork `cursor/*` branch had named this P112
frame-code comparison before this one.

This is an exhaustive finite census of one finite code: all `2^36` kernel
words, through two half-splits, plus the engine's weight-at-most-16 yield
on the same basis. It is not a proof that the iterator is correct for every
generator matrix, and it is not an unrestricted nonexistence result. A
failed search was not used. The E6 and D6 equalities are not claimed as
P112 results.

## Reproduce

Python 3.12, `gcc`, and the standard library, from the repository root. The
two registered commands split the work because together they measured 608
seconds on this host, above the 600-second command limit. The half-split
census is the shorter command. The engine batch is the longer one: a
separate run of that batch measured 494 seconds.

```sh
python3 -B scripts/research_package.py --package research/p112-punctured-frame-code --check-only
python3 -I -B research/p112-punctured-frame-code/verify.py census
python3 -I -B research/p112-punctured-frame-code/verify.py engine
python3 -I -B research/p112-punctured-frame-code/verify.py
python3 -B scripts/research_package.py --package research/p112-punctured-frame-code
```

`verify.py` with no argument runs both parts in one process. With `census`
or `engine` it runs one part. The combined process prints

```text
PASS_P112_PUNCTURED_FRAME_CODE width=112 frames=1260 dimension=36 minimum=16 supports=7 codewords=68719476736 mode=all batches=20 splits=18,16 e6_replayed=false d6_replayed=false no_new_kappa=true
```

Not run: the #5729 timing harness, a second engine batch, the E6 4-frame
census, the D6 6-frame census, the E7 kernel,
`research/e7-intersection-counters/engine.py`, Lean, Docker, and
`scripts/research_selected_baseline.py` as a scientific replay. The
selected record is provenance only.

## Open next questions

1. Does one reflected copy of this coordinate frame induce the same set
   equality after the root list is transported? This pin is one orthogonal
   8-frame. First reflect one punctured root by one simple E8 root, rebuild
   the 112-line list, and compare one half-split with the transported
   images of these seven supports.
2. Does the opt-in intersection-counter engine return this same 8-word set?
   A faster substitute is not coverage for this basis until the sets are
   compared. This is not the E6 64-word hash and not the D6 16-word set.
   First run `research/e7-intersection-counters/engine.py` on this
   36-generator basis at one batch size and compare it with the support
   hash above.

## Credit

The 120-line coordinate order and this punctured frame are the model in
`research/p112-rank6-frame-coverage`, from the PR1226/PR1323 E8 listing
used by Cinna Davis. The bit-lane engine is Ali Romman's PR #5729,
`research/e7-bitsliced-exhaustion/binary.py`. The request to bind one other
code is the open question of the E6 frame-code comparison, open as #6948.
The D6 width-30 comparison is a different deletion and is not redone here.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review and no formal-kernel acceptance are claimed.
