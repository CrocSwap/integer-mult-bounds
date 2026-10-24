# Stream norm-six features without a transform table

**Scoped streaming construction; no new kappa.** Emit all 19,600 norm-six
feature pairs with at most **320 live integer slots**, including both input
vectors, plus **2,304 Gram entries**. There is no per-feature transform table
or target accumulator array. A consumer must release each output before the
next; retaining outputs requires additional storage.

| Quantity | Bound |
|---|---:|
| Emitted factor pairs | 19,600 |
| Owned vector slots | 192 |
| Borrowed x/y input slots | 96 |
| Scalar/counter/current-record allowance | 32 |
| Per-feature descriptor / target accumulator slots | 0 / 0 |
| Immutable Gram slots | 2,304 |
| Common target denominator, not asserted minimal | 256 |
| Uniform target numerator magnitude | 146,804 |
| Uniform source feature magnitude | 32,768 |

The term count and algebraic support upper bill `49*19600=960400` are inherited
from Nick Petalas's [#5084](https://github.com/CrocSwap/integer-mult-bounds/pull/5084).
Concurrent JoyboyBrian [#5132](https://github.com/CrocSwap/integer-mult-bounds/pull/5132)
publicly supplied an explicit construction during this investigation and
receives credit for closing that gap. Its stated allocations are 19,712 target
slots, 64 source slots and 245,884 immutable descriptor slots including G.
The new delta is a one-pass stream with O(d) live workspace and only the O(d^2)
Gram as fixed data. This compares explicit upper allocations, not an optimal
space lower bound. The feature bases differ and must not be interchanged.

## Construction and exact boundary

The kernel is `K(x,y)=((x^T G y)^3-4*x^T G y)/192` on `x^T G x=y^T G y=6`.
A two-coordinate Gram block `[[6,-1],[-1,6]]` gives a dyadic-unit pivot of
determinant -8 for the 48 shell relations. It removes two square-linear
features and 46 distinct-index cubics. Parity gives integral coefficients
over the common scale 256.

[streaming.py](streaming.py) contains the table-free iterator. It owns exactly
four length-d vectors, generates feature keys by nested loops, and forms each
coefficient from at most three local relation entries. [PROOF.md](PROOF.md)
proves the identity, ownership/lifetime contract, operation counts and bounds
on all intermediate integers. Borrowed G,x,y must remain immutable throughout
iteration; the implementation preserves them but does not snapshot or police
concurrent mutation. Outputs retained by the caller are outside the 320 slots.

The combined stream uses at most 159,389 integer multiplications and 61,150
additions/subtractions, with 96 exact divisions by three, two pivot halvings
and at most 144 public Gram-diagonal halvings. All preprocessing intermediates
fit 19 signed bits on the actual norm-six shell. The counts include the Gram
dot-product prefixes, rather than pricing them by their smaller final values.
Divisions define precomputed integer-valued label features, as in #2222; they
are not dyadic scalar gates on arbitrary runtime data. This is an indexed
integer model, not a Python heap measurement or a physical tape tariff.

The optional exact pair-kernel consumer needs one additional 48-bit accumulator.
It checks the feature identity; a variable-data physical decoder is not supplied.
The expansion decision is to stop at the specified stream contract. The changed
scope does not claim the historical card's whole-supplier/five-percent gate.

## Evidence and reproduction

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/norm6-streaming-features
python3.12 -I -B -W error research/norm6-streaming-features/verify.py
python3.12 -I -O -B -W error research/norm6-streaming-features/verify.py
python3.12 -B scripts/check_research_commit.py --package research/norm6-streaming-features --check-source-history
```

Expected direct marker: `PASS_NORM6_STREAMING_FEATURES`; the registered runner
also prints `PASS_REGISTERED_RESEARCH_PACKAGE`. `verify.py --emit-result`
generates the deterministic source-bound receipt on stdout; normal verification
writes nothing and compares it to [RESULT.json](RESULT.json), including JSON types.

New-result evidence:

- An independently implemented literal polynomial-convolution oracle checks
  all 48 relations, with 43,056 coefficient comparisons. It multiplies
  polynomials and expands ordered Gram pairs rather than copying the
  constructor's coefficient formulas.
- The exact -8 minor and all 2,304 entries of `R_P^T Q=8I` check the full pivot
  solve for arbitrary target values. Full polynomial comparisons cover 3,275
  small-dimensional targets and five actual 48-dimensional targets.
- All **3,449,600 emitted coordinates** in **176 complete streams** agree with
  the materialized reference already checked by the independent oracle.
  Borrowed-input preservation, order, completion, early close and the four
  owned vectors are checked. Static inspection supplies the algorithmic
  storage proof; sampled Python frame inventories are only corroboration.
- The 44 actual-Gram norm-six vectors are a diagnostic set, not a full-shell
  enumeration. A nonzero off-shell defect is tested. Exact multiplication of
  G by its computed inverse establishes maximum inverse diagonal 172 and the
  source-coordinate bound 32 under the cited positive-definiteness premise.
- Thirteen mathematical/input/stream corruptions reject. Normal and optimized
  execution retain all checks. The reference implementation and its full
  feature/relation arrays occur only in verification, never in the stream.

The proof supplies universal coverage; finite tests alone do not. The official
export includes the sole live input, the Gram JSON, and direct replay needs
neither Git nor any predecessor executable. Local publication/export evidence
and hosted CI are reported separately in the PR.

## Sources, coordination and credit

Scientific base: `20a1e31bc6009b9b3f4d084bbaadc6350e34fcba`, priority revision 7.
[SOURCES.json](SOURCES.json) pins exact base blobs and SHA256 hashes. The
catalogue, selected record and predecessor proofs are provenance; only the
Gram JSON is a live external input. No frozen source is edited or copied.

- Cinna Davis / 1337isnot1337, [#2222](https://github.com/CrocSwap/integer-mult-bounds/pull/2222),
  `82cf756186c0fc2c542fcd06e486c575d97ffc5c`: kernel, integral-valued features,
  P48p Gram and 49-bit chart.
- Nick Petalas, [#5084](https://github.com/CrocSwap/integer-mult-bounds/pull/5084),
  `9d7f7805d147028fe5f0174e267ee05b73703f0b`: dyadic existence bound and handoff.
- JoyboyBrian, [#5132](https://github.com/CrocSwap/integer-mult-bounds/pull/5132),
  `08572fdb060e73ecc4cb09a024611039881185f4`: concurrent explicit construction
  and its transform/target-array resource bounds. Its proof supplies comparison
  context; its code is neither imported nor replayed.
- DreamingOfClouds, [#2244](https://github.com/CrocSwap/integer-mult-bounds/pull/2244),
  `8ef6fa81403973d3cacaf865bdabe9797a6c34a0`: rational shell-rank perspective.
- David Ganz / Dugongue, [#4494](https://github.com/CrocSwap/integer-mult-bounds/pull/4494),
  `ad31d9fdf000d4ca98dd911afe489a45d2ea4f74`: the dyadic factorization lemma
  used by #5084; the explicit pivot does not need that general lemma.

Nebe/Sloane and the retained Leech/Niemeier geometry and kernel lineage retain
credit. Classical elimination and Cauchy-Schwarz are not new techniques.

The [canonical investigation #5127](https://github.com/CrocSwap/integer-mult-bounds/discussions/5127)
retains the initial claim and the [scope change](https://github.com/CrocSwap/integer-mult-bounds/discussions/5127#discussioncomment-19143848).
The first snapshot covered 310 open PRs, 4,266 Discussion records and 6,884
tracked notes. The later 10:23–10:24 UTC refresh covered 315 PRs and 4,284
Discussion records and found #5132. Its claim had appeared between the
preceding live read and ours. Before publication we narrowed the contribution
to the different memory contract; we do not claim another first resolution of
the original constructibility question. Final freshness is recorded in TASK.json.
Arbitrary diffs, unpublished work and subsequent activity are outside snapshot
coverage. The original account's reflection, Schur, Pauli, association, fanout,
frame and A5 work is excluded.

Prepared by Krzysztof Wojt with substantial OpenAI Codex assistance. Bounded
Luna support covered overlap inventory, the independently written polynomial
oracle, and arithmetic/storage review; the primary agent reviewed and
integrated it. Apache-2.0. Independent human and proof-kernel acceptance are
unclaimed.

## Limitations

Positive definiteness, lattice geometry and the binary chart remain cited
premises. No full-shell table, exact rank, term/space optimality, minimum
denominator or superior total arithmetic cost is claimed. Source acquisition,
physical variable-data side programs, frames, owners, dirty restoration,
precision, tape movement, compiler/recursive and outer admission remain
unknown. Unknown costs are not zero. No selected frontier is changed.

## Open next questions

Can one chronological physical source/target contract consume the stream
without retaining a cubic-size output array and with a favorable full invoice?
Start with one actual kernel invocation, check its data lifetime/order and
charge acquisition, preparation, frames, owners, dirty restoration, precision
and tape placement. The explicit generator removes the transform-table and
target-array requirement of this abstract interface; a physical caller and
its complete cost are still missing. See [TASK.json](TASK.json).
