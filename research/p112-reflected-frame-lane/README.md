# The reflected P112 bit-lane iterator returns the transported supports

**Set comparison of one published iterator on one reflected basis. No new κ.**
The selected conditional exponent stays `781451/250000000`. On the reflected
36-generator basis recorded by open PR #7017, `low_weight_words` at its
default batch size 16 returns zero and the seven transported weight-16
supports. The SHA256 of `json.dumps` of those seven sorted integers is
`9ce7e5edc72ee3104d62cb068146b73840e9a3c42c4132403dece70c8146cccb`.

## Result

The line list is the coordinate model in
`research/p112-rank6-frame-coverage/engine.py`. An independent E8 builder
reproduces that ordered list. The simple system is the eight roots in
`research/p112-a3-six-flat/geometry.py`. Its Gram matrix divided by 4 is the
E8 Cartan matrix, and every one of the 240 roots is an integer combination of
these simple roots with coefficients all nonnegative or all nonpositive.

In simple-root order, then punctured-line order, the first pair that moves a
line is simple root 0,

```text
α = (1, -1, -1, -1, -1, -1, -1, 1)
```

acting on punctured line 1,

```text
β = (2, -2, 0, 0, 0, 0, 0, 0).
```

The image is `(1, -1, 1, 1, 1, 1, 1, -1)`, line 88 of the pinned list. The
reflection fixes four punctured lines and moves four. The rebuilt 112-line
complement, in increasing position, has SHA256
`a2ac7049d9eef1cff8af1eec35b084e6d261efad5311625e5356cceafe260da7`.

Transport of the seven supports recorded for the unreflected frame is a
bijection of the 112 bit positions. The transported integers are

```text
12726038110963558112484457976320
61084916320812443394843581087904
2433889152476423258413102440464394
6363012028601310481939177671680
954453281446482856702353473856
580303949270928947429810196
2677278706012631304342476888735745
```

They are seven disjoint weight-16 words, they cover every rebuilt line, and
their sorted-list SHA256 is the hash above. Each meets every orthogonal
8-frame of the rebuilt list evenly. Each of the seven untransported integers
fails a frame parity.

On that list there are 1260 orthogonal 8-frames, and every line lies in 90
of them. The incidence matrix has rank 76. The kernel basis with an identity
on the free coordinates

```text
(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 17, 19, 21,
 25, 26, 27, 28, 30, 34, 36, 38, 42, 43, 52, 53, 54, 55, 56, 60, 68, 84)
```

has the weights recorded by PR #7017. The SHA256 of `json.dumps` of these 36
generator integers is
`f71157e487ad45377cb6a92651d3a8d8b1055b6978f14a44dea511049ca7da8c`.
A local comparison during this session, against the functions in PR #7017 at
`11af08b8ff57dc26492501b4efaffdb34d298a00`, found the same ordered basis and
the same transported integers. That comparison is not a registered input.
The replay rebuilds the basis from the three pinned files on this base and
checks the hashes above.

`low_weight_words` is the function in
`research/e7-bitsliced-exhaustion/binary.py`. Its signature is
`(generators, width, maximum, batch_bits)` and the default of `batch_bits`
is 16. The call here is that function on this ordered basis, width 112,
weight bound 16, batch size 16. The yield has no duplicates. It is exactly

```text
{0} ∪ {the seven transported supports}
```

Every positive yielded word has weight 16. Deleting one support makes the
sets unequal. Clearing the top bit of the first transported support produces
a weight-15 word outside the yield and outside the code, and the weight
predicate rejects a set that contains it. The seven untransported integers
are not the yielded set. The function rejects a repeated copy of the first
generator with `binary generators must be independent`. On generators
`(1, 2, 4)`, weight bound 1 returns `{0, 1, 2, 4}` and weight bound 0
returns `{0}`.

### Completeness of this call

The domain is the span of these 36 independent generators, a set of `2^36`
words. Batch size `k = 16` splits each coefficient vector into a low part of
16 bits and a high part of 20 bits. The implementation walks the high part
by the Gray recurrence of length `2^20` and, at each step, stores all `2^16`
low parts as bit lanes. The coefficient-partition argument in
`research/e7-bitsliced-exhaustion/PROOF.md` says every coefficient vector
appears in exactly one batch and one lane, and the lane comparator keeps the
words of weight at most 16. Independence, which the basis identity and the
function's pivot check both give, makes those images distinct. This package
checks those hypotheses on this input and compares the yielded set with the
transported supports. It uses that published argument for the lane arithmetic
and does not reprove it.

This is an exhaustive finite census of the weight-at-most-16 words of this
one ordered basis, through this one call at batch size 16. It is a set
comparison with the transported hash. It is not a second half-split, not a
census of another batch size, and not a statement about every generator
matrix.

## Scope

Task card `replay-runtime`, priority revision 8, base
`17469fff78c22941280f04d39dc5a1faee09c840`. Scope status is **refined**.

The card asks for a measured speedup that keeps coverage. The revision-8
verification row says faster output is the same coverage only after the sets
are compared. Open PR #7017 recorded the reflected half-split and asked
whether `low_weight_words` on this basis returns the transported supports.
This package is that comparison at the function's default batch size.
Width 112, weight bound 16, thirty-six generators, one call. On this
machine the direct call took 486.22 seconds and the registered package
runner took 278.75 seconds. Both finished inside the 600-second command
bound. Those figures are wall-clock observations of this environment, not
a coverage or speedup claim. The selected conditional exponent stays
unchanged.

The priority note on this base still quotes the older displayed value
`0.00310045` from PR #5599. This package reads the selected record and
keeps `781451/250000000`.

Ordered overlap check on 2026-11-10, after fetching upstream `main` at
`17469fff78c22941280f04d39dc5a1faee09c840`. `scripts/find_overlap.py
--refresh` read 339 open pull requests, including drafts (fetched
`2026-11-10T10:27:07Z`, pagination complete) and 7013 discussion records
(fetched `2026-11-10T10:28:11Z`, pagination complete), with 10178 local notes
and a complete local inventory at that head. The transported hash and the
reflected iterator question match open PR #7017 and discussion reply
[#1166 comment 19514152](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19514152).
Both state the question and record that the bit-lane iterator was not run.
Open PR #7007 is the unreflected half-split and the unreflected call at
batch size 20. Open PR #7034 is the intersection-counter refusal on the
unreflected 36-generator basis. No fork `cursor/*` branch had named this
reflected iterator comparison.

## Reproduce

Python 3.12 and the standard library, from the repository root. Assertions
must remain enabled. The registered command is one call at batch size 16.

```sh
python3 -B scripts/research_package.py --package research/p112-reflected-frame-lane --check-only
python3 -I -B research/p112-reflected-frame-lane/verify.py
python3 -B scripts/research_package.py --package research/p112-reflected-frame-lane
```

The direct verifier prints

```text
PASS_P112_REFLECTED_FRAME_LANE width=112 dimension=36 batch=16 supports=7 hash=9ce7e5edc72ee3104d62cb068146b73840e9a3c42c4132403dece70c8146cccb half_split_rerun=false intersection_engine=false no_new_kappa=true
```

`verify.py basis` rebuilds the basis and does not call the iterator. That
mode is not the registered comparison.

Outside this run: the half-split in #7017, batch size 20 and every batch
size other than 16, a reversed generator order, the unreflected call from
#7007, `research/e7-intersection-counters/engine.py`, any other simple
root, Lean, Docker, and `scripts/research_selected_baseline.py` as a
scientific replay. The selected record is read only to require that its
kappa string is unchanged.

## Open next questions

1. Does `low_weight_words` at batch size 20 on this same ordered reflected
   basis return the same seven transported supports? Batch size 20 is the
   size used for the unreflected basis in #7007. The published iterator says
   the batch size changes storage and runtime only. This package executes
   the default batch size 16, so that statement is unchecked for batch 20
   on this basis. First call the same function at batch size 20 on the
   generator tuple pinned by
   `f71157e487ad45377cb6a92651d3a8d8b1055b6978f14a44dea511049ca7da8c`
   and compare the positive words with
   `9ce7e5edc72ee3104d62cb068146b73840e9a3c42c4132403dece70c8146cccb`.
2. Does the reversed 36-tuple, at batch size 16, return the same set? The
   iterator's result is claimed independent of generator order once the
   rows stay independent. This package uses the free-coordinate order only.
   First reverse that pinned tuple and repeat the batch-16 call.

## Credit

The 120-line coordinate order is the model in
`research/p112-rank6-frame-coverage`, from the PR1226/PR1323 E8 listing
used by Cinna Davis. The simple system is the one fixed in
`research/p112-a3-six-flat/geometry.py`, from Nick Petalas's PR3161/PR3162
lineage. `low_weight_words` and its coefficient-partition argument are Ali
Romman's `research/e7-bitsliced-exhaustion`. The seven unreflected supports
are the recorded result of open PR #7007. The reflection, the transported
integers, the free coordinates, and the basis weights are the recorded
result of open PR #7017. This package runs the iterator that #7017 left
unrun.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review and no formal-kernel acceptance are claimed.
