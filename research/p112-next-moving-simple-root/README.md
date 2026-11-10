# The next moving P112 simple root keeps the transported weight-16 equality

**Exhaustive finite census of one later reflected frame code. No new κ.**
The selected conditional exponent stays `781451/250000000`. Continue the
pinned simple-root order past the first moving pair, reflect by the next
simple root that moves a punctured line, rebuild that 112-line complement,
and transport the seven supports recorded for the unreflected frame. One
half-split of the rebuilt incidence kernel returns exactly those seven
transported words.

## Result

The order is the one fixed by #7017: simple-root index in
`research/p112-a3-six-flat/geometry.py`, then punctured-line index in the
120-line model of `research/p112-rank6-frame-coverage/engine.py`. All 64
pairs were evaluated. Sixteen pairs move a line, and they lie on simple
roots 0, 3, 5 and 7, four lines each. Simple roots 1, 2, 4 and 6 fix every
punctured line, so they do not rebuild a frame.

Simple root 0 is the reflection already compared in #7017. Its three later
moving punctured lines use that same reflection and the same rebuilt list.
The next simple root that moves a punctured line is index 3,

```text
α = (0, -2, 2, 0, 0, 0, 0, 0),
```

and the first punctured line it moves is index 0,

```text
β = (2, 2, 0, 0, 0, 0, 0, 0).
```

The reflection coefficient is `β·α / 4 = -1`, so

```text
s_α(β) = β + α = (2, 0, 2, 0, 0, 0, 0, 0).
```

That vector is line 2 of the pinned list. The same reflection applied to
the whole puncture fixes four lines and moves four:

| Old line | Old vector | New line | Image vector |
|---:|---|---:|---|
| 0 | `(2, 2, 0, 0, 0, 0, 0, 0)` | 2 | `(2, 0, 2, 0, 0, 0, 0, 0)` |
| 1 | `(2, -2, 0, 0, 0, 0, 0, 0)` | 3 | `(2, 0, -2, 0, 0, 0, 0, 0)` |
| 26 | `(0, 0, 2, 2, 0, 0, 0, 0)` | 16 | `(0, 2, 0, 2, 0, 0, 0, 0)` |
| 27 | `(0, 0, 2, -2, 0, 0, 0, 0)` | 17 | `(0, 2, 0, -2, 0, 0, 0, 0)` |
| 44 | `(0, 0, 0, 0, 2, 2, 0, 0)` | 44 | same line |
| 45 | `(0, 0, 0, 0, 2, -2, 0, 0)` | 45 | same line |
| 54 | `(0, 0, 0, 0, 0, 0, 2, 2)` | 54 | same line |
| 55 | `(0, 0, 0, 0, 0, 0, 2, -2)` | 55 | same line |

The image is a different orthogonal 8-frame. The rebuilt 112-line list is
the complement of that frame, in increasing position in the same 120-line
order. Its SHA256, of `json.dumps` of the 112 coordinate lists, is
`36e3ad43dbfd53d71b20cfac522fbf9c0c1c065054994b9c81767a228d7e6f3c`.
It is not the #7017 list
`a2ac7049d9eef1cff8af1eec35b084e6d261efad5311625e5356cceafe260da7`.

The seven recorded supports, in the order published with their hash, are

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
the unreflected half-split or the #7017 half-split.

Transport sends each old live line to its reflected line and records the
new position. The resulting permutation of the 112 bit positions is a
bijection and fixes 62 positions. The transported supports are

```text
68451290880
1031047741680
280375477678095
4814039611113066403813140725760
15468061711732307582943976488960
1216944811960755906164784113909760
3955069945251226348097480121384960
```

Their SHA256, of `json.dumps` of that sorted list, is
`0ab33f7ea89182ea1cbc5ca06d5f3bdcaeb72a08aef3eaceb33e6a43bbb96636`.
They are seven disjoint weight-16 words and cover every rebuilt line.
They are not the untransported integers, and they are not the #7017
transported integers
`9ce7e5edc72ee3104d62cb068146b73840e9a3c42c4132403dece70c8146cccb`.

On that line list there are 1260 orthogonal 8-frames, and every line lies
in 90 of them. The F2 incidence matrix has rank 76. A kernel basis with an
identity on the free coordinates

```text
(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 18, 20, 22, 24,
 26, 28, 32, 34, 36, 40, 42, 48, 49, 50, 51, 52, 56, 58, 64, 80)
```

is orthogonal to every frame row. These free coordinates differ from the
#7017 basis. The seven transported supports meet every frame evenly. Each
of the seven untransported integers fails a frame parity.

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
unreflected enumerator. It is a separate run, on this simple-root-3 basis.
The seven words themselves differ from both earlier support lists.

A copy of the low-weight set with one support removed compares unequal.
Clearing the top bit of a transported support produces a weight-15 word
that fails a frame parity, and the weight predicate rejects a set that
contains it. The seven untransported integers are not the low-weight set.

The same coordinate vector α is the simple root used by the D6
reflected-anchor census in discussion comment 19515229. That census
transports the #6959 anchors on a 30-line rank-10 code. It does not rebuild
this 112-line list and it does not compare these seven supports.

## Scope

Task card `replay-runtime`, priority revision 8, base
`17469fff78c22941280f04d39dc5a1faee09c840`. Scope status is **refined**.

The card asks for a new measured speedup that keeps coverage. The
revision-8 verification row instead says that faster output is not the same
coverage until checked. Open PR #7017 recorded the first moving pair and
asked whether the next simple root, in the same order, induces the same set
equality on its own rebuilt list. This package is that comparison for
simple root 3 and punctured line 0. Width 112, weight bound 16, one split
after 18 generators.

The selected record's κ is `781451/250000000`. The priority note on this
base still quotes the older displayed value `0.00310045` from PR #5599.
This package uses the selected record and leaves it unchanged.

Ordered overlap check on 2026-11-10, after fetching upstream `main` at
`17469fff78c22941280f04d39dc5a1faee09c840`. `scripts/find_overlap.py
--refresh` read 339 open pull requests, including drafts (fetched
`2026-11-10T10:25:29Z`, pagination complete) and 7013 discussion records
(fetched `2026-11-10T10:26:30Z`, pagination complete), plus 10178 local
notes at that head, with a complete local inventory. The matches were open
PR #7017, which poses this question and answers only the first pair, and
discussion comment 19514152, which records that first pair. A cache search
for “simple root 3” also hits discussion comment 19515229, the D6
reflected-anchor census named above. No open pull request and no fork
`cursor/*` branch had named this next P112 simple root. That search is not
a proof that no comment uses other wording.

This is an exhaustive finite census of two finite domains. The movement
predicate is all 64 pairs of the 8 simple roots with the 8 punctured lines;
the recorded 16 moving pairs are the completeness statement for which root
is next. The code census is all `2^36` kernel words of this one reflected
frame, through one half-split. The basis identity and the seen-count are
the completeness argument for that kernel. It is not a census of simple
roots 5 or 7, not a proof that every simple reflection preserves the
equality, not a proof that the iterator is correct for every generator
matrix, and not an unrestricted nonexistence result. A failed search was
not used. The unreflected equality of #7007, the first reflected equality
of #7017, the D6 equality of #6959, and the E6 equality of #6948 are not
claimed as this result.

## Reproduce

Python 3.12, `gcc`, and the standard library, from the repository root.
One half-split of this kernel measured about 67 seconds on 4 cores.

```sh
python3 -B scripts/research_package.py --package research/p112-next-moving-simple-root --check-only
python3 -I -B research/p112-next-moving-simple-root/verify.py
python3 -B scripts/research_package.py --package research/p112-next-moving-simple-root
```

The direct verifier prints

```text
PASS_P112_NEXT_MOVING_SIMPLE_ROOT width=112 frames=1260 dimension=36 minimum=16 supports=7 codewords=68719476736 split=18 simple=3 punctured=0 moved_lines=4 fixed_roots=4 later_roots=5,7 same_frame=false first_pair=false unreflected_census=false engine=false no_new_kappa=true
```

Outside this run: the unreflected half-split, the #7017 half-split, a
second split of this kernel, `low_weight_words`,
`research/e7-intersection-counters/engine.py`, the E6 and D6 censuses, the
frames of simple roots 5 and 7, Lean, Docker, and
`scripts/research_selected_baseline.py` as a scientific replay. The
selected record is provenance only.

## Open next questions

1. Does simple root 5, the next root after this one in the same pinned
   order that moves a punctured line, induce the same set equality on its
   own rebuilt list? The 64-pair scan records that root, and simple root 7
   after it, but neither half-split was run. The transported integers above
   belong to simple root 3. First rebuild the simple-root-5 complement and
   compare one half-split with that root's transported supports.
2. Does `low_weight_words` on this simple-root-3 36-generator basis return
   the same seven transported supports? This is the bit-lane iterator on
   the basis pinned here, compared with
   `0ab33f7ea89182ea1cbc5ca06d5f3bdcaeb72a08aef3eaceb33e6a43bbb96636`.
   It is not the #7017 reflected basis and not the hash
   `9ce7e5edc72ee3104d62cb068146b73840e9a3c42c4132403dece70c8146cccb`.
   First run that iterator at one batch size on the free coordinates
   pinned above.

## Credit

The 120-line coordinate order and the unreflected puncture are the model in
`research/p112-rank6-frame-coverage`, from the PR1226/PR1323 E8 listing
used by Cinna Davis. The simple system is the one fixed in
`research/p112-a3-six-flat/geometry.py`, from Nick Petalas's PR3161/PR3162
lineage. The seven supports, their hash, and the unreflected weight
distribution are the recorded result of open PR #7007. The first moving
pair, the question answered here, and the doubling half-split are from
open PR #7017. This scanner reads a different basis. The D6 use of the
same simple-root vector is discussion comment 19515229 and is a different
code.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review and no formal-kernel acceptance are claimed.
