# The intersection-counter engine refuses the P112 36-generator basis

**Capacity refusal on one basis. No new κ.** The selected conditional exponent
stays `781451/250000000`. On the 36-generator kernel basis of the P112
punctured frame code, `research/e7-intersection-counters/engine.py` returns
no set. At every legal batch size, including the named batch size 20,
`low_weight_words` raises `ValueError: dimension exceeds 27` before yielding
a word. The eight-word target stays the set recorded by open PR #7007. The
SHA256 of its seven positive words is
`ff8861dab18040c03d403a860773218df7c120d03770d701afb61b78c941e3d3`.

## Result

The lines are the coordinate complement in
`research/p112-rank6-frame-coverage/engine.py`. An independent E8 builder
reproduces that ordered 120-line list and the same eight punctured positions.
The 112 live lines carry 1260 orthogonal 8-frames, and every live line lies
in 90 of them. The incidence matrix has rank 76. The kernel basis with an
identity on the free coordinates

```text
(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20,
 24, 25, 26, 28, 30, 32, 34, 36, 40, 42, 48, 49, 50, 51, 52, 56, 58, 64, 80)
```

matches the free coordinates and weights recorded by PR #7007. The kernel
vector with a single 1 on a given free coordinate is unique, so this ordered
basis is that one. The SHA256 of `json.dumps` of the 36 generator integers is
`c93a6ec3f6d61b3bbf4086218c723761e517bc42ac2c26f551436d271a081e9d`.
Each generator is a positive integer below `2^112`.

The seven target words are the coordinate partition from that PR, recomputed
here. They are pairwise disjoint, they cover every live line, each has weight
16, and each meets every live 8-frame evenly. In the pinned live order they
are

```text
64691900160
1034819666160
280375465144335
4772259772306660006937399132160
15509841550538713979819718082560
1216944648758260568639796318044160
3955070108453721685622467917250560
```

`json.dumps` of that sorted list has the hash above. Deleting the first
integer changes the hash. PR #7007's half-split census says these seven
words, together with zero, are the weight-at-most-16 codewords. This package
does not rerun that census and does not call `scan.c` or the bit-lane
iterator.

The engine call injects `population_planes` and `at_most` from
`research/e7-bitsliced-exhaustion/binary.py`. Those two helpers are
keyword-only on the intersection engine. The bit-lane `low_weight_words`
rejects the same keywords with `TypeError`, so this stream is the
intersection engine.

`checked_rows` accepts a batch size only when it is an integer in `1..20`.
The verifier calls `low_weight_words` on the 36-tuple at each of those twenty
integers, and at the adjacent integers 0 and 21. This is an exhaustive finite
census of that batch-size domain on this one input. The completeness argument
is the engine's own range check, plus one call at every integer it accepts
and one call at each adjacent integer it rejects.

| Call | Result |
|---|---|
| Batch sizes 1..20 on the 36 generators | `dimension exceeds 27`, 0 yields |
| Batch sizes 0 and 21, and the non-integers `True` and `20.0` | `invalid batch size`, 0 yields |
| Batch size 20 on the reversed 36-tuple | `dimension exceeds 27`, 0 yields |
| Two copies of the first generator | `dependent generators`, 0 yields |
| First 27 generators at batch size 10 | `batch count exceeds 65536`, 0 yields |
| First 27 generators at batch size 20 | admitted; the first yield is 0, then the stream is closed |
| 27 generators followed by a copy of the first | `dimension exceeds 27`, 0 yields |

Batch size 20 is the named comparison. It is the only legal batch size for
which `36 - batch_size <= 16`, so it is the only legal size that would pass
the later guard `batch count exceeds 65536`. The message actually raised is
the dimension guard, which the engine checks while reading generator index
27, before that later guard and before any lane table. The refusal is raised
at zero-based index 27, the 28th generator, after the first 27 generators
have been accepted. The same message at
the other nineteen legal sizes is the same guard, not a lane-split
disagreement. No timing is recorded.

The ordered 27-prefix is a separate linear fact, read off the identity
coordinates. The basis vector `i` is the unique vector in this basis with a
1 at free coordinate `i`. A recorded support therefore lies in the prefix
span exactly when its bits at free coordinates 48, 49, 50, 51, 52, 56, 58,
64 and 80 are all zero. The first three published supports lie in that span.
The other four do not: each has a 1 on at least one of those coordinates, and
reassembling it from the first 27 generators does not recover it. Truncating
this ordered basis to the engine's capacity cannot contain the eight-word
set. The prefix stream itself is not enumerated. One yielded zero shows that
the public function admits that shorter tuple; it is not a census of the
prefix.

## Scope

Task card `replay-runtime`, priority revision 8, base
`17469fff78c22941280f04d39dc5a1faee09c840`. Scope status is **refined**.

The card asks for a measured speedup that keeps coverage. The revision-8
verification row requires the sets to be compared before a faster replay
counts as the same coverage. The merged package
`research/e6-intersection-counter-support` answers that question for the E6
64-word hash
`ad4a1d101774e6c2da40cde3d097d39aa56ee5668dcdca858513c5fec3578215`.
Open PR #7007 records this P112 hash and states that its verifier does not
call `research/e7-intersection-counters/engine.py`. The D6 16-word hash
`23a7b374a6bc62bc2aca47843d52a01fa8e791ed3a98085133829d816c5094e8` is a
different code. This package runs the engine on the P112 basis only.

The selected record at this base is `781451/250000000`. The priorities page
on the same base still prints the older PR #5599 decimal. This package uses
the selected record and does not change it. Orientation
`python3 -B scripts/research_selected_baseline.py` printed
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY` with that same fraction. That command
checks source bindings only.

Ordered overlap check on 2026-11-10, after fetching upstream `main` at
`17469fff78c22941280f04d39dc5a1faee09c840`. `scripts/find_overlap.py
--refresh --include-closed` searched `ff8861dab18040c0`, `p112
intersection-counter`, and `dimension exceeds 27`. Coverage: local notes at
that head, 10180 records, complete inventory; 317 open PR bodies fetched at
`2026-11-10T08:49:18Z`; 6971 discussion records fetched at
`2026-11-10T08:50:22Z`; 6175 closed PR bodies fetched at
`2026-11-10T08:51:11Z`. The two matches are open PR #7007 and discussion
reply 19507785. Both record this hash for the bit-lane census and state that
the intersection-counter engine was not run. No closed PR body contains the
hash. The helper searches titles and bodies, not code diffs.

This is a refusal census of a finite parameter, not a yielded-set symmetric
difference and not an enumeration of the `2^36` codewords. It does not say
what a copy of the engine would return if the dimension guard were raised.
It does not say that every generating set of length 27 misses the eight
words. A failed search was not used.

## Reproduce

Python 3.12 and the standard library, from the repository root. Rebuilding
the 1260 frames and refusing twenty batch sizes finishes in well under a
second. No compiler is required.

```sh
python3 -B scripts/research_package.py --package research/p112-intersection-counter-capacity --check-only
python3 -I -B research/p112-intersection-counter-capacity/verify.py
python3 -I -O -B research/p112-intersection-counter-capacity/verify.py
python3 -B scripts/research_package.py --package research/p112-intersection-counter-capacity
```

The direct verifier prints

```text
PASS_P112_INTERSECTION_COUNTER_CAPACITY batch=20 legal_batches=20 yielded=0 message=dimension exceeds 27 hash=ff8861dab18040c03d403a860773218df7c120d03770d701afb61b78c941e3d3 returned=False prefix_misses=4 enumerated=false timed=false no_new_kappa=true
```

Checked here: normal and optimized direct runs, metadata check, and the
registered package runner. The 27-dimensional E7 census, the #5729 timing
harness, the bit-lane scan, the half-split census, Lean, and Docker were
not run.

## Open next questions

1. If an opt-in copy raises only the dimension guard from 27 to 36, does
   batch size 20 on this same basis yield the eight-word set with the hash
   above? The published function stops before the lane loop, so the refusal
   leaves that arithmetic comparison open. The first step is a separate
   harness that does not edit
   `research/e7-intersection-counters/engine.py`. The blocker is the
   36-dimensional stream. This package does not remove the guard.

2. Does some other independent generating set of length at most 27, still
   inside this code, make the same engine return these eight words at batch
   size 20? The seven supports span seven dimensions, so the length cap
   alone does not forbid every admissible input. The ordered 27-prefix
   misses four supports, and searching a different generating set is a
   different question. The first step is to name one such 27-tuple and
   compare one batch-size-20 stream with this hash.

## Credit

The 120-line order and the punctured frame are the model in
`research/p112-rank6-frame-coverage`, from the PR1226/PR1323 listing used
by Cinna Davis. The intersection-counter engine is Nick Petalas's
`research/e7-intersection-counters/engine.py`. The injected population and
threshold routines are Ali Romman's PR #5729. The 36-generator basis, the
seven supports, and the open engine question are PR #7007. The E6 comparison
is merged PR #6960.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review and no formal-kernel acceptance are claimed.
