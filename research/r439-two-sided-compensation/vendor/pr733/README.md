# Two-sided basis factoring of the R420 dirt correction

**Finite bit-circuit construction and composition evidence; no new κ.**
This combines Greer Guthrie's PR694 helper-basis construction with a fresh
target matching on its transformed coefficient matrix. The result saves
**8,368 binary XORs** in PR543's complete native word:
**26,916 → 18,548**, including all preparation and restoration. It saves
**1,434 more ADDs than PR694**. The predecessor mechanisms are credited to
their authors; the contribution here is the checked two-sided construction.

| Quantity | Original PR543 | Helper basis PR694 | Two-sided |
|---|---:|---:|---:|
| D additions | 19,922 | 12,988 | 11,554 |
| Complete native ADDs | 26,916 | 19,982 | 18,548 |
| Exported records | 29,874 | 22,940 | 21,506 |
| Forward positive prefix | 144,651 | 202,699 | 202,699 |
| Reverse positive prefix | 2,270,064 | 2,446,788 | 4,152,374 |
| Local payload allowance, bits | 100 | 102 | 103 |
| Helpers / copies / rank mass | 420 / 9 / 5,112 | same | same |

All 201 helper pairs from PR694 are fixed. All 57 target pairs are nominated
on the resulting matrix `KQ`, using seed 2. The complete D cost is
**201 + 57 + 11,038 + 57 + 201 = 11,554 ADDs**. It uses the same registers,
no new source access, no additional scratch, no new frame movements, and
no additional copies or recursive children. All transformed helpers are
restored before A.

The larger reverse prefix is fully charged:
`64 * 202699^3 * 4152374^2 = 9190258315617780048732559342336 < 2^104`.
This is a local cohort bound, not a rebuilt hosted-parent invoice. No old
global precision charge or bit exponent is inherited for the changed word.

## Reproduce

Python 3.9 or later, standard library only:

```sh
python3 -B research/r420-two-sided-basis/verify.py
python3 -B -m unittest discover -s research/r420-two-sided-basis -p 'test_*.py'
```

Expected verifier output:

```text
PASS_R420_TWO_SIDED_BASIS native_ADDs=26916->18548 saved=8368 beyond_PR694=1434 payload_bits=103 kappa=unchanged
```

For fresh, unchanged C++17 legality and five-/nine-/eleven-stage checks:

```sh
python3 -B research/r420-two-sided-basis/native.py
```

Boost headers are required; set `BOOST_INCLUDE` to their containing directory
and `CXX` to the compiler if needed. Expected final line:

```text
PASS_R420_TWO_SIDED_BASIS_NATIVE words=2 stages=5,9,11 columns=900,1380,1620 bridge_controls=96 missing_D_controls=6
```

Both entry points compare the complete committed certificates. Explicit
`--write-certificate NEW_PATH` requires a new path and never overwrites a
file. Optimized Python is refused because the inherited exporter uses
assertions. The checker compares decompressed source bytes, so changing gzip
headers does not invalidate the mathematical input.

## Exact construction and sufficient interface

All matrices in this construction act over F2. Let the old D be
`(x,s,y) -> (x,s,y+Ks)`, for 420 arbitrary dirty helpers `s` and 120 arbitrary
targets `y`. Let `Q` be PR694's product of disjoint helper transvections,
and `P` the product of the new disjoint target transvections. Both satisfy
`P^2=I` and `Q^2=I`. The literal new D is:

1. Execute Q on the helpers, obtaining `Qs` (201 ADDs).
2. Execute P on the targets, obtaining `Py` (57 ADDs).
3. Add `(PKQ)(Qs)` to `Py`, using exactly 11,038 helper reads.
4. Undo P (57 ADDs), then undo Q (201 ADDs).

Thus the target output is `P(Py+PKQ Qs)=y+Ks`, and the helpers return to `s`.
Every gate touches only target/helper registers at frame zero. No source is
accessed in D. Every field outside D is required to equal the original word.
Substitution of this equal complete prefix preserves the original endpoint.

The target matching must be scored on `KQ`, not K. For a proposed pair
`(a,b)`, its fully charged saving is
`weight((KQ)_b) - weight((KQ)_a XOR (KQ)_b) - 2`.
Adding the standalone predecessor savings (6,934 + 3,150 = 10,084) is not
the saving of this circuit. The exact result is 8,368.

Writing `P=I+A` and `Q=I+B` gives
`PKQ = K + AK + KB + AKB`. The last term is necessary: a control that omits
only `AKB` fails the full D operator. The tests separately check all 50,400
middle-matrix coefficients using this direct four-term formula rather than
the producer's sequential row changes.

The original literal H2 and literal extraction of K reject the changed D
syntax. They remain unchanged. The sufficient semantic replacement is that
D is a legal zero-frame prefix implementing exactly `(x,s,y+Ks)` and
restoring every helper. The proof above and the complete 660-input operator
check establish that finite claim; all other original H1/H3/H4/H5 and
decomposed conclusions are checked. Acceptance of this semantic replacement
under the inherited common-label/mutable-basis interface remains a review
obligation.

Every register has exactly its original ordered frame path. The entire
MOVE/COPY/ERASE subsequence is identical, so the paid histogram remains
`{1:1320, 2:1440, 4:60, 5:120, 8:9}` with rank mass 5,112. All retained
copies, their closing operations, helper restoration and recursive children
are counted. F2 endpoint equality is not asserted to be equality of the
two forward integer operators. Signed inverse shears and cancellation-free
integer prefix bounds are checked separately by the retained C++ tools.

## Evidence, search coverage and independence

The verifier reconstructs PR694 from its recipe using direct row updates,
checks its complete native record hash and both prefix bounds against that
author's certificate, then constructs and exports the new word. It checks
original, helper-only and two-sided words on all 660 arbitrary inputs in
both directions. E8 geometry and full scalar legality use eumemic's retained
checker. Record synthesis and set-valued replay reuse pinned PR713 utilities;
this is **not a wholly independent implementation** of those checks.

The official exporter independently matches every literal instruction.
Fresh unchanged C++ checks cover original and combined words on
900/1,380/1,620 formal columns at five/nine/eleven stages. All 96 omitted
bridges and six omitted-D-end controls are rejected across the two words.
Ten local controls include both helper/target preparation and restoration,
a wrong coefficient, illegal frame, omitted cleanup, stale target pricing,
using PK instead of PKQ, and omitting only the cross term. Four additional
tests check the direct matrix formula, all pair scores, overlap and cost.

The OS assignment seed is **2**. Candidate tasks were another phase-B block
synthesis (crowded by PR670/674/688), split target frames (closed in the
specified domain by PR718), and this two-sided composition (chosen).
Exactly 14,280 ordered target pairs on the fixed KQ matrix are scored.
Lexicographic pair enumeration with `random.Random(2)` tie keys and one
decreasing `(gain,tie,a,b)` greedy disjoint pass selects 57 pairs. Search
stops after that pass. There is no matching optimality or general circuit
optimality claim. `CLAIM.json` records the local claim because no pinned
coordination issue existed. The presubmission refresh covered open PRs through
#730 and found no two-sided composition.

## Provenance, attribution and scope

Exact base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Selected source: PR626 `660de893d27bb7abd1d5b01b1640207528a5c851`,
conditional κ `51110230636731/31250000000000000`, using eumemic's PR543
`2065fe4f72a914d907f1046603f5a36f17018535` bit supplier.

Direct predecessors:

- **Greer Guthrie's [PR694](https://github.com/CrocSwap/integer-mult-bounds/pull/694)**,
  `9732ac127dd4bef98a846aaa904c20b5a84e72c1`: all 201 helper pairs and the
  helper-only construction. Its recipe, certificate, README and notice are
  retained byte for byte. PR686 (Mikhail R. Gadelha) supplies the preceding
  single-helper-pair mechanism and semantic prefix contract.
- **Scott Woolsey Biggart's [PR713](https://github.com/CrocSwap/integer-mult-bounds/pull/713)**,
  `1a19af5c5ddb6de9797a6d085e5df0b90ed6d58b`: target-basis construction and
  record/set verification utilities. Those utilities and its recipe/README
  are retained byte for byte; the native harness is adapted with attribution.
- Sagar Thakrar's concurrent [PR716](https://github.com/CrocSwap/integer-mult-bounds/pull/716),
  `c804e7d79ac524723aa8c2d0d6a59d5e662763b3`, independently corroborates the
  target-pair construction. It is credited, not imported. Its attribution
  points to Dugongue's earlier [PR476](https://github.com/CrocSwap/integer-mult-bounds/pull/476),
  `e850569c33ad1d5771e2f8b1c6dfe7a445396167`, for reversible target factoring
  in phase B, following PR450. No new elementary identity is claimed here.

PR708's decoder sharing, PR710's cleanup conjugation and the phase-A/B block
improvements are not composed here. PR661/711/718 concern restricted frame
searches, which this changed circuit does not reopen. `SOURCES.json` pins
every consumed source and the exact commits/Git blobs of vendored inputs.
Original attribution and licenses are retained in the linked notices.

The selected construction and `upstream/` are unchanged. The selected assembly
is complex-limited, and this identical recursive profile does not produce a
new exponent. Full hosted-parent emission, whole-owner allocation, revised
global precision/finite invoices and outer assembly are separate integration
work. All inherited compiler/common-label/mutable-basis/physical/hosting/
residual/precision/tape/analytic assumptions remain. This is finite evidence,
not a formal proof of the full multiplication theorem or a measured runtime
improvement.

Prepared by **Scott Woolsey Biggart (@swbiggart)** with substantial
**OpenAI Codex assistance** in research, implementation, proof, verification
and packaging. Apache-2.0; no independent human review claimed. Credit also
remains with eumemic, Dylan Crow, DaysSky, Zhihao Chen, DreamingOfClouds,
Chafik Boukhalfa, icekylinx, Rohan Arun and the cumulative lineage in the
unchanged [R420 notice](../e8-bit-r420/NOTICE.md),
[carrier notice](../e8-bit-carrier-skeleton/NOTICE.md) and
[PR694 notice](vendor/pr694-NOTICE.md).
