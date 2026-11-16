# One length-27 P112 generating set returns the eight-word intersection stream

**One witnessed generating set, one exhaustive span census, and one engine comparison. The selected conditional exponent stays `781451/250000000`.**

On an explicit independent 27-tuple inside the P112 punctured frame code,
`research/e7-intersection-counters/engine.py` at batch size 20 returns zero
and the seven weight-16 supports whose SHA256 is
`ff8861dab18040c03d403a860773218df7c120d03770d701afb61b78c941e3d3`.

## Result

The lines and the punctured frame are the model in
`research/p112-rank6-frame-coverage`. The 1260 orthogonal 8-frames on the
112 live lines have F2 incidence rank 76. The kernel basis with an identity
on the free coordinates

```text
0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 25, 26,
28, 30, 32, 34, 36, 40, 42, 48, 49, 50, 51, 52, 56, 58, 64, 80
```

is the same 36-generator basis whose ordered 27-prefix contains the first
three published supports and misses the other four. Open PR #7034 records
that the published engine raises `dimension exceeds 27` on all 36 generators.
This package uses a different ordered tuple.

The seven supports, in the recorded order, are pairwise disjoint and each has
weight 16. They partition the 112 coordinates. The XOR of a subset therefore
has weight `16` times the subset size: bits from different supports do not
cancel. In the F2-span of these seven vectors, the words of weight at most 16
are exactly zero and the seven supports. That is a proof about these seven
integers. It does not by itself describe a larger span.

The 27-tuple is those seven supports, followed by the first twenty kernel
basis vectors. Each of those twenty vectors stays independent after the seven
supports under the same high-bit elimination the published engine uses. Their
weights are the first twenty basis weights, from 22 through 50, so each lies
in the span and outside the weight-at-most-16 set. The ordered integers are

```text
64691900160
1034819666160
280375465144335
4772259772306660006937399132160
15509841550538713979819718082560
1216944648758260568639796318044160
3955070108453721685622467917250560
4443670059850152665101255383351297
476478169960083547941896362557442
1235404508498744078868673813159940
9983029542622351334877321371656
1551087412582331123977819014078480
333427041513561210778684215566368
2596466671826523360078412021669952
389342703893815899092640717774976
3833216057007571418503107247251712
432611841641411318609815106396672
2920587414949371429908798658749440
454485081471164625171710277756928
1225342658187465785230322160381952
4146009544401891323911366300975104
3306510103253472586250966597304320
1622990553999583501864018977226752
263432417834582793991910927106048
2435278157458505060063050639343616
476517444942813366547851144855552
3172674985599289618361799917174784
```

SHA256 of `json.dumps` of that list, with the default separators, is
`2d580566f960c80d3f0f6f76342e83a4bf9b650ee9697226e58d8cc15da7da98`.

The twenty-seven vectors are independent, lie in the frame-code kernel, and
every published support is one of the generators. The span therefore contains
all seven supports. It is a 27-dimensional subspace of the 36-dimensional code.
A binary-reflected Gray code visits each of its `2^27 = 134217728` vectors
once: the coefficient at step `i` is `i xor (i >> 1)`, and the verifier checks
that identity at every step. Exactly eight of those vectors have weight at
most 16, and they are zero together with the seven supports.

The engine call is `low_weight_words` from
`research/e7-intersection-counters/engine.py`, with `population_planes` and
`at_most` injected from `research/e7-bitsliced-exhaustion/binary.py`. The
published `checked_rows` still contains `need(index < 27, "dimension exceeds 27")`.
This package does not edit that file. The bit-lane enumerator in `binary.py`
rejects the same keyword arguments with `TypeError`. Batch size 20 puts 20
generators in the lane block and leaves `2^7 = 128` high-offset batches.
The stream is eight distinct words, with no missed support and no extra word.
Its positive-word SHA256, of `json.dumps(sorted(positive_words))`, is
`ff8861dab18040c03d403a860773218df7c120d03770d701afb61b78c941e3d3`.
The stream equals the Gray-code census.

| Quantity | Value |
|---|---:|
| Live lines | 112 |
| Orthogonal 8-frames | 1260 |
| Incidence rank | 76 |
| Kernel dimension | 36 |
| Generating-set length | 27 |
| Appended basis vectors | indices 0..19 |
| Span words | 134217728 |
| Batch size | 20 |
| Lane generators | 20 |
| High-offset batches | 128 |
| Census words of weight at most 16 | 8 |
| Engine stream | 8 distinct words |
| Set equality | yes |
| Missed supports | 0 |
| Extra words | 0 |
| Positive-word SHA256 | `ff8861dab1…c941e3d3` |

Three claim types are separate. The disjointness argument is a proof about
the seven supports. The Gray code is an exhaustive finite census of one
27-dimensional span; the domain is finite, every coefficient is visited, and
the bijection check is in `verify.py`. The engine run is a set comparison of
one call at batch size 20. A second 27-tuple is outside this census. The
36-generator input remains outside the published dimension guard.

Removing the least positive support changes the hash. Passing the first
generator twice raises `dependent generators`. Length 28, formed by repeating
the first generator, raises `dimension exceeds 27` before any yield. Batch
size 10 on the same 27-tuple raises `batch count exceeds 65536`, because
`27 - 10 = 17` exceeds the published limit of 16. The ordered 27-prefix of
the kernel basis is a different tuple: it contains the first three supports
and misses the last four. That membership split is recomputed here from the
kernel. The prefix stream is not enumerated.

## Scope

Task card `replay-runtime`, priority revision 8, base
`17469fff78c22941280f04d39dc5a1faee09c840`. Scope status is **refined**.

The card asks for a measured speedup that keeps coverage. Priority revision 8
requires the yielded sets to be compared before a faster replay counts as the
same coverage. Open PR #7034 compares every legal batch size on the
36-generator basis and records a capacity refusal. Its second open question
asks whether some other independent generating set of length at most 27,
still inside this code, makes the same engine return the eight-word set at
batch size 20. This package names one such 27-tuple and compares that stream.
The selected record at this base is `781451/250000000`. The priorities page
on the same base still prints the older PR #5599 decimal. This package uses
the selected record. No timing is recorded.

Ordered overlap check on 2026-11-10, after fetching canonical `main` at
`17469fff78c22941280f04d39dc5a1faee09c840`. `scripts/find_overlap.py --refresh
--include-closed` searched `ff8861dab18040c0`, `length at most 27`,
`admissible 27`, `ordered 27-prefix`, and `p112 intersection-counter`.
Coverage: local notes at that head, 10178 records, complete inventory; 339
open PR bodies fetched at `2026-11-10T10:29:31Z`; 7013 discussion records
fetched at `2026-11-10T10:30:33Z`; 6175 closed PR bodies fetched at
`2026-11-10T10:31:23Z`. Five matches: open #7034, discussion reply 19513866,
discussion reply 19507785, open #7007, and open #7017. #7034 and reply
19513866 state the 36-generator refusal and leave this 27-tuple question
open. #7007 and reply 19507785 record the bit-lane eight-word set and leave
the intersection-counter engine unrun. #7017 compares a reflected frame with
the bit-lane iterator and separates that hash from this engine. None names
this 27-tuple or runs the published engine on a length-27 generating set.
The helper searches titles and bodies, not code diffs.

## Reproduce

Python 3.12 and the standard library, from the repository root. The Gray-code
census is `2^27` popcounts and finishes in a few seconds on this host. The
engine call is one batch-size-20 stream with 128 high-offset batches.

```sh
python3 -B scripts/research_package.py --package research/p112-length27-intersection-return --check-only
python3 -I -B research/p112-length27-intersection-return/verify.py
python3 -I -O -B research/p112-length27-intersection-return/verify.py
python3 -B scripts/research_package.py --package research/p112-length27-intersection-return
```

The direct verifier prints

```text
PASS_P112_LENGTH27_INTERSECTION_RETURN batch=20 generators=27 span_words=134217728 words=8 hash=ff8861dab18040c03d403a860773218df7c120d03770d701afb61b78c941e3d3 equal=True missed=0 extra=0 timed=false no_new_kappa=true
```

Checked here: normal and optimized direct runs, the metadata check, and the
registered package runner. `scripts/research_selected_baseline.py` printed
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY` with selected κ `781451/250000000`
and is provenance only. The 36-dimensional bit-lane census, the E6 and D6 comparisons,
the E7 census, a copy of the engine with the dimension guard raised, Lean,
Docker, and any timing harness were not run.

## Open next questions

1. Does this same 27-tuple return the eight-word set at batch size 11? Batch
   size changes the lane split. Batch size 20 uses 20 lane generators and 128
   high-offset batches. Batch size 11 is the smallest legal batch for 27
   generators, because `27 - 11 = 16`, and it uses 65536 high-offset batches.
   First rerun this comparison with `batch_bits` 11, the same 27 integers,
   weight bound 16, and support hash. This package stops after batch size 20,
   so that split has not been compared. The published dimension guard stays 27.

2. Does one other admissible 27-tuple inside this code, whose span contains
   the seven supports and which is not this extension by basis vectors 0
   through 19, return the same stream at batch size 20? This census covers
   one span. A different subspace could contain another word of weight at
   most 16. First name that tuple and compare one batch-size-20 stream with
   the hash above. The 36-dimensional bit-lane census is open PR #7007 and is
   not replayed here, so this package does not treat it as a proof that every
   containing subspace has the same low-weight set.

## Credit

The 120-line order and the punctured frame are the model in
`research/p112-rank6-frame-coverage`, from the PR1226/PR1323 listing used by
Cinna Davis. The intersection-counter engine is Nick Petalas's
`research/e7-intersection-counters/engine.py`. The injected population and
threshold routines are Ali Romman's PR #5729. The seven supports, the
eight-word hash, and the bit-lane set equality are open PR #7007. The
36-generator refusal, the ordered prefix that misses four supports, and the
question answered here are open PR #7034. The reflected-frame comparison is
open PR #7017 and uses a different iterator.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review and no formal-kernel acceptance are claimed.
