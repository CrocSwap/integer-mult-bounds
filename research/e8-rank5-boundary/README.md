# The first E8 rank-five puncture boundary

**Scoped negative result; no new supplier or κ.** At exactly 36 deleted
E8 root lines, no bit-side star label decoder improves the copy-rank/live-port
ratio `63/111`. Together with Chi Zhao's [PR631](https://github.com/CrocSwap/integer-mult-bounds/pull/631),
this extends its exclusion from at most 35 to **at most 36 punctures**.

The new evidence explains why the first opening in that predecessor's coarse
rank bound does not help. Exactly **7,560** 36-puncture sets admit a reader of
rational rank five. They form **one Weyl orbit**. Every such set has the same
reader-rank histogram and exact minimum star cost:

| Reader rank | 5 | 6 | 7 | 8 |
|---|---:|---:|---:|---:|
| Number of nonzero readers | 1 | 0 | 42 | 468 |
| Binary dimension spanned by readers up to this rank | 1 | 1 | 8 | 9 |

An optimal nine-total basis therefore has weights `5,7,7,7,7,7,7,7,8`, costing
**62** on 84 live ports. Having one rank-five reader does not provide nine
independent cheap readers. All other 36-puncture sets have cost at least 54.
Both ratios exceed `63/111`:

```
62/84 = 31/42 > 21/37 = 63/111,
54/84 =  9/14 > 21/37.
```

This is an exhaustive equality-class calculation with a written coverage
argument, not a failed random search. The minimum cost across *all*
36-puncture sets is not determined; 54 is only the lower bound used for the
nonexceptional cases.

## Reproduce

From the repository root, Python 3.10+ and its standard library suffice:

```sh
python3 -B research/e8-rank5-boundary/verify.py
```

Expected final line:

```
PASS_E8_RANK5_BOUNDARY: 28616 rank-five pairs; 2 representatives; 7560 conjugate punctures; cost 62; 72 restorations; 5 negative controls; no new kappa
```

The default command checks the entire committed `CERTIFICATE.json`, including
the predecessor source hashes. It writes nothing. `--write /tmp/e8-rank5.json`
regenerates the deterministic certificate after all checks pass.

A separate implementation uses normalized Fraction RREF, low-pivot binary
elimination, direct span-membership tests instead of simple-coordinate masks,
and the cumulative-rank cost formula instead of the greedy basis algorithm:

```sh
python3 -I -O -B research/e8-rank5-boundary/independent_check.py \
  --check research/e8-rank5-boundary/CERTIFICATE.json
```

It imports neither the primary verifier nor predecessor code. It checks all
28,616 rank-five pairs and both complete 511-reader rank tables. Its scope is
the `independent_summary` portion of the certificate; the orbit traversal and
other-dimensional threshold census are checked by the primary verifier.
Both new implementations retain all checks under optimized Python.

The predecessor is retained byte-for-byte and can also be replayed:

```sh
python3 -B research/e8-rank5-boundary/sources/pr631/verify.py --negative-controls
```

That older script intentionally refuses `-O`. See [VALIDATION.md](VALIDATION.md)
for the actual local validation record and its limits.

## Model and coverage proof

Use the standard 120 real E8 root **lines**, with representatives `L_t` in
doubled coordinates, squared norm eight. The binary decoder matrix is
`B_st = (1 + L_s · L_t / 4) mod 2`. Its row space `C` has dimension nine.
Its nonzero words have weights 56 (255 words), 64 (255 words), and 120 (one).
For a puncture set `P`, the star weight of a reader `c` is

```
s_P(c) = rank_Q {L_t : c_t = 1 and t not in P}.
```

We use exactly the star model in Joel Pulikkan / GamingPuzzled's PR620
`s2-decoder/bitp.py`, inherited by PR631: minimize the sum of these weights
over a basis of the nine-dimensional reader space. A collection of additional
star totals must span that space and contains a basis; nonnegative weights
cannot make that collection cheaper than the minimum basis. This does not
cover general source/reader pairing-rank factorizations.

**1. The code still has nine dimensions after 36 deletions.** A nonzero word
can vanish on all live ports only if its entire support was deleted. Its
minimum weight is 56, greater than 36. Restriction to the live ports is
injective, so independence before and after puncturing agrees. Invertible
changes of label coordinates also preserve it.

**2. Any rank-five case is an equality case.** PR631's sharp deletion
thresholds for reader ranks at most `0,...,7` are
`[56,55,53,50,44,36,26,1]`. The primary verifier regenerates all of them over
255 standard flats and 511 readers. Since 44 deletions are needed for rank
four, a reader of rank at most five at our boundary has rank exactly five.
Let `F` be the span of its surviving roots. All reader roots outside `F`
were deleted. At least 36 deletions are needed to achieve this, and `|P|=36`,
so necessarily

```
P = support(c) \ F.
```

There are no leftover arbitrary deletions in this case. This equality is
the new search restriction; we are not reopening PR620's annealing search.

**3. Standard flats cover every equality case.** We inherit PR631's
parabolic-flat reduction, repeated here for clarity. Choose a generic normal
in `F` perpendicular space, perpendicular to exactly the roots in `F`.
Move it to the closed fundamental Weyl chamber. Every positive root has
nonnegative simple-root coordinates, so the perpendicular roots are precisely
the roots supported on those simple roots perpendicular to the normal. Their
span is a standard rank-five parabolic flat. Thus it suffices to inspect
all `binom(8,5)=56` standard flats and all 511 reader words. The main verifier
checks integral, common-sign simple coordinates and preservation of the full
reader code by each of the eight simple reflections. Physical ranks are
preserved because these reflections are orthogonal. This supplies the
invariance needed to transport the cost calculation back to any original
puncture set.

**4. The complete equality census has two standard representatives.** The
two `(simple subset, reader)` pairs are recorded in the certificate, with all
reader and deleted root indices. The simple subsets are `[0,1,2,3,4]` and
`[1,2,3,4,5]` in the explicitly generated simple system. These are *two
standard-flat representatives*, not two distinct Weyl orbits. The following
word in the eight simple reflections carries the first puncture set to the
second (apply from left to right):

```
5,4,3,1,2,0,3,2,4,3,1,5,4,3,2,0
```

Breadth-first closure of the first set under all eight reflections has exactly
7,560 distinct masks. Every newly encountered image is enqueued and all eight
outgoing images are inspected before completion. Combined with the covering
argument and the explicit connection, this proves the asserted single orbit
and its exact size. Root numbering belongs to this standard-coordinate
package, not the Hamming-coordinate numbering of a shipped supplier.

**5. Exact minimum cost.** For both representatives, compute all 511 rational
reader ranks. The histogram is shown above. Let `r_k` be the binary rank of
the span of all readers of weight at most `k`. For integer weights in `[0,8]`,
the minimum basis cost is `sum_{k=0}^7 (9-r_k)`: a greedy basis contains a
maximum independent set from each nested weight threshold. Here
`(r_0,...,r_7)=(0,0,0,0,0,1,1,8)`, yielding 62. The certificate also gives
an explicit attaining basis, whose weights are recomputed from roots.

**6. The other cases.** If a 36-puncture set has no rank-five reader, Step 2
also excludes lower ranks. Every basis reader has rank at least six, hence
the star cost is at least `9*6=54`. This completes the stated ratio exclusion.
Combining it with PR631's earlier theorem gives the at-most-36 corollary.

## Controls and scope

Every default primary replay includes:

- Corrupted root geometry, binary decoder and flat-membership rejection.
- A tempting set of **nine distinct** cheap readers with invoice 61, rejected
  because its binary span has dimension eight.
- A wrong-characteristic control: rational physical rank is not binary rank.
- All 72 single-port restorations across the two representatives. Each raises
  the unique rank-five reader to rank six, confirming the deletion boundary.

The final item is a positive boundary control, not 72 malformed-file rejections.
The independent implementation supplies separate rational, binary and geometry
controls. Receipt and source mutations are tested during packaging.

The result concerns root-only E8 ports, unrestricted independent input bits,
the fixed label decoder, and additive **star** copy-rank accounting. It does
not rule out general pairing-rank decoders, extra/non-root ports, helper
savings, correlated inputs, changed stage geometry, or other mechanisms.
Puncture counts 37 and above are outside the new theorem. There is no new
global puncture optimum, formal proof-assistant theorem or full multiplication
theorem here.

The hypothesis tested was a reduction of this copy-rank ratio at its first
unexcluded boundary. That necessary arithmetic opportunity fails even if
additional helper, source-access, frame, restoration and recursive-child
expenses are optimistically assigned zero. This says nothing about improving
another part of a full supplier invoice at an unchanged or worse copy ratio.
No new supplier or outer assembly is proposed or priced. The selected
construction's all-size/compiler, hosting, precision/tape and analytic
assumptions remain separate and unresolved by this note.

## Provenance, prior work and assignment

Base commit: `f567884aeb8851b6e794af1184119a3bfbe1e631`. At that base the
selected conditional saving is `1661634653669567/10^18` (PR799 with PR589 on
PR555), as recorded in `certificates/selected-result.json`. Its actual
construction, maintainer review and the PR ledger were inspected. This package
does not modify the selected record or any existing repository file.

Assignment seed **46** was drawn once from operating-system randomness.
[CLAIM.json](CLAIM.json) records the three candidates, scope, stopping rule
and overlap checks. No pinned sprint coordination issue existed; the claim
and its result update are local. Completed coverage is 28,616 boundary pairs,
130,305 total threshold pairs, both equality representatives, both 511-reader
rank tables and the complete 7,560-mask equality orbit. There is no random
search or unreported timeout in these domains.

The predecessor is pinned to PR631 head
`fb893b5ee1317c2da3b297e6fe78eca0857d1a76`; its original README and verifier
are retained under `sources/pr631/` without changes. [SOURCES.json](SOURCES.json)
records their hashes and exact paths, plus base-context hashes. Context hashes
describe the inspected base and are not a claim that future selected records
must stay unchanged. New scripts import no predecessor implementation.

Credit **Chi Zhao / PR631** for the all-flat reduction, sharp single-reader
thresholds and earlier at-most-35 theorem; **Joel Pulikkan / GamingPuzzled /
PR620** for the model, optimum-basis method and puncture investigations;
**DreamingOfClouds / PR595 and PR602** for format-limit context; and **eumemic /
PR543** and the prior E8 supplier lineage for the original construction
context. These inherited results are not claimed as new. The new contribution
is the equality classification, its exact orbit and invoice, and the
36-puncture exclusion with independent arithmetic evidence.

Prepared by **Philipp (@mightyOil)** with **substantial OpenAI Codex assistance**
in proof development, implementation, independent computational checking and
writing. The separate checks were also AI-assisted; no independent human
review is claimed. Apache-2.0; see [NOTICE.md](NOTICE.md).
