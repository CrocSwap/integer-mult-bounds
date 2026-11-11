# One reflected P112 frame keeps the transported weight-16 equality

**Exhaustive finite census of one reflected frame code. No new κ.**
The selected conditional exponent stays `781451/250000000`. Reflect the first
punctured line that the pinned E8 simple system moves, rebuild the 112-line
complement, and transport the seven supports recorded for the unreflected
frame. One half-split of the rebuilt incidence kernel returns exactly those
seven transported words.

## Result

The unreflected root list and the eight punctured lines are the model in
`research/p112-rank6-frame-coverage/engine.py`. An independent E8 builder
reproduces that ordered list. The seven recorded supports, in the order
published with their hash, are

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
This package uses those integers as the set to transport. It does not rerun
the unreflected half-split.

The simple system is the eight roots fixed by
`research/p112-a3-six-flat/geometry.py`, in that order. Each has norm 8.
The Gram matrix divided by 4 is the Cartan matrix

```text
2  0 -1  0  0  0  0  0
0  2  0 -1  0  0  0  0
-1  0  2 -1  0  0  0  0
0 -1 -1  2 -1  0  0  0
0  0  0 -1  2 -1  0  0
0  0  0  0 -1  2 -1  0
0  0  0  0  0 -1  2 -1
0  0  0  0  0  0 -1  2
```

The diagram is E8: node 3 is the branch, with legs of 1, 2 and 4 nodes.
Each simple reflection permutes the 120 lines and is an involution on the
stored vectors. Every one of the 240 roots is an integer combination of
these simple roots, with coefficients all nonnegative or all nonpositive.

In simple-root order, then punctured-line order, the first pair that moves
a line is simple root 0,

```text
α = (1, -1, -1, -1, -1, -1, -1, 1)
```

acting on punctured line 1,

```text
β = (2, -2, 0, 0, 0, 0, 0, 0).
```

The reflection coefficient is `β·α / 4 = 1`, so

```text
s_α(β) = β - α = (1, -1, 1, 1, 1, 1, 1, -1).
```

That vector is line 88 of the pinned list. The same reflection applied to
the whole puncture fixes four lines and moves four:

| Old line | Old vector | New line | Image vector |
|---:|---|---:|---|
| 0 | `(2, 2, 0, 0, 0, 0, 0, 0)` | 0 | same line |
| 1 | `(2, -2, 0, 0, 0, 0, 0, 0)` | 88 | `(1, -1, 1, 1, 1, 1, 1, -1)` |
| 26 | `(0, 0, 2, 2, 0, 0, 0, 0)` | 95 | `(1, -1, 1, 1, -1, -1, -1, 1)` |
| 27 | `(0, 0, 2, -2, 0, 0, 0, 0)` | 27 | same line |
| 44 | `(0, 0, 0, 0, 2, 2, 0, 0)` | 113 | `(1, -1, -1, -1, 1, 1, -1, 1)` |
| 45 | `(0, 0, 0, 0, 2, -2, 0, 0)` | 45 | same line |
| 54 | `(0, 0, 0, 0, 0, 0, 2, 2)` | 54 | same line |
| 55 | `(0, 0, 0, 0, 0, 0, 2, -2)` | 118 | `(1, -1, -1, -1, -1, -1, 1, -1)` |

The image is a different orthogonal 8-frame. The rebuilt 112-line list is
the complement of that frame, in increasing position in the same 120-line
order. Its SHA256, of `json.dumps` of the 112 coordinate lists, is
`a2ac7049d9eef1cff8af1eec35b084e6d261efad5311625e5356cceafe260da7`.

Transport sends each old live line to its reflected line and records the
new position. The resulting permutation of the 112 bit positions is a
bijection and fixes one position. The transported supports are

```text
12726038110963558112484457976320
61084916320812443394843581087904
2433889152476423258413102440464394
6363012028601310481939177671680
954453281446482856702353473856
580303949270928947429810196
2677278706012631304342476888735745
```

Their SHA256, of `json.dumps` of that sorted list, is
`9ce7e5edc72ee3104d62cb068146b73840e9a3c42c4132403dece70c8146cccb`.
They are seven disjoint weight-16 words and cover every rebuilt line.

On that line list there are 1260 orthogonal 8-frames, and every line lies
in 90 of them. The F2 incidence matrix has rank 76. A kernel basis with an
identity on the free coordinates

```text
(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 17, 19, 21,
 25, 26, 27, 28, 30, 34, 36, 38, 42, 43, 52, 53, 54, 55, 56, 60, 68, 84)
```

is orthogonal to every frame row. These free coordinates and the basis
weights differ from the unreflected basis. The seven transported supports
meet every frame evenly. Each of the seven untransported integers fails a
frame parity, so the recorded masks are not codewords until they are
transported.

`scan.c` lists the span of the first 18 generators and the span of the
other 18 by doubling. The basis identity makes the 36 generators
independent, so each of the `2^36` kernel words is the XOR of exactly one
pair. The scan's seen-count and the histogram both equal `68719476736`.
The words of weight 1 through 16 are exactly the seven transported
supports, and the least positive weight is 16. The weight distribution is
the same tuple recorded for the unreflected frame:

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

That agreement is a comparison of this split's histogram with the recorded
unreflected enumerator. It is a separate run, on the reflected basis.

A copy of the low-weight set with one support removed compares unequal.
Clearing the top bit of a transported support produces a weight-15 word
that fails a frame parity, and the weight predicate rejects a set that
contains it. The seven untransported integers are not the low-weight set.

## Scope

Task card `replay-runtime`, priority revision 8, base
`17469fff78c22941280f04d39dc5a1faee09c840`. Scope status is **refined**.

The card asks for a new measured speedup that keeps coverage. The
revision-8 verification row instead says that faster output is not the same
coverage until checked. Open PR #7007 recorded the unreflected P112
weight-16 equality and asked whether one simple reflection preserves that
equality after the root list is transported. This package is that
comparison for the first moving pair: simple root 0 and punctured line 1.
Width 112, weight bound 16, one split after 18 generators.

The selected record's κ is `781451/250000000`. The priority note on this
base still quotes the older displayed value `0.00310045` from PR #5599.
This package uses the selected record and leaves it unchanged.

Ordered overlap check on 2026-11-10, after fetching upstream `main` at
`17469fff78c22941280f04d39dc5a1faee09c840`. `scripts/find_overlap.py
--refresh` read 317 open pull requests, including drafts (fetched
`2026-11-10T08:51:47Z`, pagination complete) and 10180 local notes at that
head, with a complete local inventory. The only match was open PR #7007,
which states this question and does not build the reflected frame. The
discussion refresh returned HTTP 504 and left no usable discussion
snapshot. A separate search for the recorded support hash found that same
pull request and no second item, and the latest top-level comments on
discussion #1166 do not treat this frame. No fork `cursor/*` branch had
named this reflected-frame comparison. That partial discussion coverage is
not a proof that no comment mentions it.

This is an exhaustive finite census of one finite code: all `2^36` kernel
words of this reflected frame, through one half-split. The domain is the
kernel of this one incidence matrix. The basis identity and the seen-count
are the completeness argument. It is not a census of every simple
reflection, not a proof that the iterator is correct for every generator
matrix, and not an unrestricted nonexistence result. A failed search was
not used. The unreflected equality of #7007, the D6 equality of #6959, and
the E6 equality of #6948 are not claimed as this result.

## Reproduce

Python 3.12, `gcc`, and the standard library, from the repository root.
One half-split of this kernel measured about 70 seconds on 4 cores.

```sh
python3 -B scripts/research_package.py --package research/p112-reflected-frame-code --check-only
python3 -I -B research/p112-reflected-frame-code/verify.py
python3 -B scripts/research_package.py --package research/p112-reflected-frame-code
```

The direct verifier prints

```text
PASS_P112_REFLECTED_FRAME_CODE width=112 frames=1260 dimension=36 minimum=16 supports=7 codewords=68719476736 split=18 simple=0 punctured=1 moved_lines=4 same_frame=false unreflected_census=false engine=false no_new_kappa=true
```

Outside this run: the unreflected half-split, a second split of this
kernel, `low_weight_words`, `research/e7-intersection-counters/engine.py`,
the E6 and D6 censuses, any other simple root's frame, Lean, Docker, and
`scripts/research_selected_baseline.py` as a scientific replay. The
selected record is provenance only.

## Open next questions

1. Does the next simple root, in this same pinned order, that moves a
   punctured line induce the same set equality on its own rebuilt list?
   This census is the first moving pair only. The reflected frame changes
   with the simple root, so the transported integers above do not answer
   the next pair. First continue the lexicographic scan of simple root,
   then punctured line, and compare one half-split with that pair's
   transported supports.
2. Does `low_weight_words` on this reflected 36-generator basis return the
   same seven transported supports? This is the bit-lane iterator on the
   reflected basis, compared with
   `9ce7e5edc72ee3104d62cb068146b73840e9a3c42c4132403dece70c8146cccb`.
   It is separate from the intersection-counter comparison on the
   unreflected basis and the hash
   `ff8861dab18040c03d403a860773218df7c120d03770d701afb61b78c941e3d3`.
   First run that iterator at one batch size on the basis pinned here.

## Credit

The 120-line coordinate order and the unreflected puncture are the model in
`research/p112-rank6-frame-coverage`, from the PR1226/PR1323 E8 listing
used by Cinna Davis. The simple system is the one fixed in
`research/p112-a3-six-flat/geometry.py`, from Nick Petalas's PR3161/PR3162
lineage. The seven supports, their hash, and the unreflected weight
distribution are the recorded result of open PR #7007. The doubling
half-split follows that package's scanner and reads a different basis.
The question answered here is open question 1 of #7007.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review and no formal-kernel acceptance are claimed.
