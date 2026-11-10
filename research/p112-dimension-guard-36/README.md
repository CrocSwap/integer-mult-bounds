# A dimension-36 copy returns the P112 eight-word set

**Exhaustive finite comparison of one copied stream, at one batch size.
No new κ.** The selected conditional exponent stays `781451/250000000`.
On the 36-generator kernel basis of the P112 punctured frame code, an
in-memory copy of `research/e7-intersection-counters/engine.py` that raises
only the dimension guard from 27 to 36 returns, at batch size 20, the
eight-word set whose seven positive words have SHA256
`ff8861dab18040c03d403a860773218df7c120d03770d701afb61b78c941e3d3`.

## Result

The published function stops before the lane loop. Its source contains one
guard statement,

```text
need(index < 27, "dimension exceeds 27")
```

and `low_weight_words` on this basis raises `ValueError: dimension exceeds 27`
with no yield. The harness reads that file, replaces that one statement with

```text
need(index < 36, "dimension exceeds 36")
```

and executes the copy. Four characters change, the two numerals `27` to `36`.
No other character differs. The published file is not written. Its SHA256
remains `882d0177e990b0534bb16ec188a622b6167051505bdb5a7b19b4462499a72e47`.

The basis is the same object recorded by open PR #7034. It is the F2 kernel
of the 1260 orthogonal 8-frames on the 112 lines left by the pinned puncture
in `research/p112-rank6-frame-coverage/engine.py`. The free coordinates and
the generator-list SHA256 are

```text
(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20,
 24, 25, 26, 28, 30, 32, 34, 36, 40, 42, 48, 49, 50, 51, 52, 56, 58, 64, 80)
c93a6ec3f6d61b3bbf4086218c723761e517bc42ac2c26f551436d271a081e9d
```

The seven positive words are the partition supports from that same
construction, in the order recorded by open PR #7007:

```text
64691900160
1034819666160
280375465144335
4772259772306660006937399132160
15509841550538713979819718082560
1216944648758260568639796318044160
3955070108453721685622467917250560
```

The target set is zero together with these seven words. Each support has
weight 16, the supports are disjoint and cover every live line, and each is
orthogonal to every frame row. The hash is SHA256 of the UTF-8 bytes of
`json.dumps(sorted(positive_words))`, with the default separators.

Batch size 20 is the lane split. `checked_rows` puts the first 20 generators
in the lane block and leaves `36 - 20 = 16` high-offset batches, so the
offset loop runs `2^16 = 65536` times and each batch has `2^20` lanes. The
copy's stream is consumed completely. It yields eight distinct words. Zero
is the first yield, and the seven positive yields follow in the recorded
increasing order. Every word has weight at most 16, every word lies in the
frame code, and the set equals the target. The positive-word hash is the
hash above.

| Quantity | Value |
|---|---:|
| Lines | 112 |
| Orthogonal 8-frames | 1260 |
| Incidence rank | 76 |
| Kernel dimension | 36 |
| Batch size | 20 |
| Lane generators | 20 |
| High-offset batches | 65536 |
| Copied stream | 8 distinct words |
| Set equality | yes |
| Zero is the first yield | yes |
| Positive yield order | the recorded increasing list |
| Positive-word SHA256 | `ff8861dab1…c941e3d3` |
| Published file edited | no |

The unchanged batch-count guard still rejects this 36-generator input at
every batch size `1..19`, with message `batch count exceeds 65536`. Batch
size 20 is the only size in `1..20` that passes both the new dimension guard
and that old guard. The values `0`, `21`, `True`, and `20.0` are refused as
illegal batch sizes. A 37th generator is refused with
`dimension exceeds 36`. A repeated generator is refused with
`dependent generators`. On the first eight generators, at batch size 20, the
copy and the published engine yield the same sequence.

Removing one support changes the hash. This is an exhaustive finite
comparison of one function's output on one finite input: the domain is the
`2^36` coefficient pairs encoded by 65536 offsets and `2^20` lanes, the
iterator is read until it ends, and the engine's own exhaustion check is
part of that read. It is not a heuristic search. It does not rerun the
`scan.c` weight census, and it does not by itself prove the copied arithmetic
for every other basis or batch size.

## Scope

Task card `replay-runtime`, priority revision 8, base
`17469fff78c22941280f04d39dc5a1faee09c840`. Scope status is **refined**.

The card asks for a measured speedup that keeps coverage. The revision-8
verification row requires the sets to be compared before a faster replay
counts as the same coverage. Open PR #7034 ran the published engine on this
basis and recorded the refusal. Its first open question is this copy. Merged
#6960 compared the same engine with the E6 64-word set. Open #7007 recorded
this hash with the bit-lane iterator and did not call the intersection
counter. Open #7017 is the reflected basis and a different hash.

`scripts/find_overlap.py --refresh --include-closed` on 2026-11-10 searched
`ff8861dab18040c0`, `dimension exceeds 36`, `dimension guard`, and
`p112 dimension-guard`. Coverage: local notes, 10178 records, complete
inventory at `17469fff78c22941280f04d39dc5a1faee09c840`; 339 open PR bodies
at `2026-11-10T10:30:00Z`; 7013 discussion records at
`2026-11-10T10:31:06Z`; 6175 closed PR bodies at `2026-11-10T10:31:55Z`.
The five matches are #7034, discussion reply 19513866, discussion reply
19507785, #7007, and #7017. None executes a dimension-36 copy of
`engine.py`. The helper searches titles and bodies, not code diffs. Fork
`cursor/*` branch names were listed before this branch; none named this
dimension-guard copy.

The selected record at this base is `781451/250000000`. The priorities page
on the same base still prints the older PR #5599 decimal. This package uses
the selected record and does not change it. On the two registered runs on
this host, the stream portion took 127.082 seconds in normal bytecode and
116.527 seconds in optimized bytecode. Each verifier prints that figure as
`host_elapsed_seconds`. It is not a speedup claim and not coverage. The
27-dimensional E7 census is not replayed.

## Reproduce

Python 3.12 and the standard library, from the repository root. The stream
is one `2^36` lane enumeration. Each registered command allows 600 seconds.

```sh
python3 -B scripts/research_package.py --package research/p112-dimension-guard-36 --check-only
python3 -I -B research/p112-dimension-guard-36/verify.py
python3 -I -O -B research/p112-dimension-guard-36/verify.py
python3 -B scripts/research_package.py --package research/p112-dimension-guard-36
```

The direct verifier prints

```text
PASS_P112_DIMENSION_GUARD_36 batch=20 lanes=20 high_batches=65536 words=8 hash=ff8861dab18040c03d403a860773218df7c120d03770d701afb61b78c941e3d3 equal=True published_edited=False enumerated_code=false timed_as_coverage=false no_new_kappa=true
```

Not run: the `scan.c` half-split census, the bit-lane iterator, the E6 and
D6 comparisons, the E7 census, the #5729 timing harness, a second batch size,
Lean, Docker, and `scripts/research_selected_baseline.py` as a scientific
replay. The selected record is provenance only.

## Open next questions

1. If a second opt-in copy also raises the unchanged 65536-batch guard, does
   one other batch size on this same basis return the eight-word set with
   the hash above? Batch size 20 is the only size that passes both guards.
   The first step is a separate harness that admits one other batch size,
   for example 16, and compares that stream with this hash. The blocker is
   that second guard. This package does not raise it.

2. Does the yield order of this batch-size-20 stream equal the yield order
   of `low_weight_words` in `research/e7-bitsliced-exhaustion/binary.py` on
   the same basis? This package compares sets and does not call that
   iterator. The first step is one paired run. The blocker is that second
   `2^36` enumeration. Open PR #7007 already records the bit-lane set.

A length-at-most-27 generating set, and the reflected basis, are different
questions and are not taken here.

## Credit

The 120-line order and the punctured frame are the model in
`research/p112-rank6-frame-coverage`, from the PR1226/PR1323 listing used by
Cinna Davis. The intersection-counter engine is Nick Petalas's
`research/e7-intersection-counters/engine.py`. The injected population and
threshold routines are Ali Romman's PR #5729,
`research/e7-bitsliced-exhaustion/binary.py`. The 36-generator basis, the
seven supports, and the refusal that stops before the lane loop are open
PR #7034. The eight-word hash and the bit-lane comparison are open PR #7007.
The E6 engine comparison is merged PR #6960.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review and no formal-kernel acceptance are claimed.
