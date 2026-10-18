# Phase B has too few consecutive mixed rank-six block candidates

**Scoped negative result. No Phase B placement, supplier, conditional bound, or new \(\kappa\) is claimed.** The exact rank-six tensor for child ranks \((3,1,1,1)\), proved in merged PR #1866, has only 12 disjoint four-child candidate windows in the pinned Phase B stream. Even granting all scalar moves, common-frame work, copies, hosting, precision, and restoration for free, 12 blocks fall well short of the 135-block 5% ceiling threshold.

## Bounded question

The predecessor block replaces one rank-three and three rank-one children by a single rank-six child, preserving rank mass. This follow-up examines only Phase B of the selected provider pinned by PR #1087. A candidate is four consecutive climb calls in child-call order, in any rank order with multiset \(\{1,1,1,3\}\), on four distinct registers. Scalar events may lie between those calls; for the ceiling screen they are deferred and charged zero. No other climb may be crossed. This is an optimistic candidate envelope, not an in-place implementation.

The complete Phase B interval has zero-based event indices 13223 through 17092 in both source orientations: 3,870 events, 1,952 climbs, and 1,918 scalar operations. The climb-rank histogram is rank 1: 1,160; rank 2: 352; rank 3: 344; rank 4: 96.

There are no four-event-contiguous raw windows of this shape. After projecting away scalar events and retaining consecutive climb-call order, the complete census finds 12 windows in each orientation. Dynamic programming and earliest-finish interval scheduling both confirm that all 12 can be selected disjointly. The exact event indices, register IDs, source and target frame IDs, frame-union dimensions, and intervening scalar-event counts and payload digests are recorded in [RESULT.json](RESULT.json). The two orientations agree on every candidate address and climb/frame record.

| First climb ordinal | Event span | Ranks | Registers | Scalar events between | Source union / largest source | Target union / largest target |
|---:|---:|---|---|---:|---:|---:|
| 85 | 13586–13618 | 1,1,1,3 | 216,159,149,684 | 29 | 1/1 | 5/4 |
| 879 | 15091–15096 | 3,1,1,1 | 431,283,299,100 | 2 | 7/4 | 9/6 |
| 893 | 15112–15117 | 1,1,1,3 | 395,67,5,279 | 2 | 7/4 | 9/6 |
| 1087 | 15403–15408 | 3,1,1,1 | 571,488,560,489 | 2 | 7/4 | 9/6 |
| 1247 | 15699–15704 | 1,3,1,1 | 226,168,439,150 | 2 | 8/6 | 8/7 |
| 1263 | 15723–15728 | 1,3,1,1 | 450,214,444,131 | 2 | 8/6 | 8/7 |
| 1279 | 15747–15752 | 1,3,1,1 | 228,144,438,136 | 2 | 8/6 | 8/7 |
| 1295 | 15771–15776 | 1,3,1,1 | 452,162,440,221 | 2 | 8/6 | 8/7 |
| 1311 | 15795–15800 | 1,3,1,1 | 7,187,597,140 | 2 | 8/6 | 8/7 |
| 1327 | 15819–15824 | 1,3,1,1 | 454,196,599,172 | 2 | 8/6 | 8/7 |
| 1343 | 15843–15848 | 1,3,1,1 | 238,115,595,178 | 2 | 8/6 | 8/7 |
| 1359 | 15867–15872 | 1,3,1,1 | 456,181,601,209 | 2 | 8/6 | 8/7 |

The frame-union columns give exact \(\mathbb F_2\) span dimensions of the four individual frames, followed by the largest individual frame dimension. They are structural data only; this package does not convert them into a frame-transition price or claim a common-frame tensor realization.

## Optimistic cost screen

The selected per-call local profile is

```text
{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}
```

Replacing \(k\) mixed blocks changes it by \((-3,-1,+1)\) at ranks \((1,3,6)\), so rank mass stays 5,586. The exact ceiling engine, with all other selected profile terms and the center charge fixed, gives:

| Case | Exact ceiling bracket for \(a\) |
|---|---:|
| Selected profile | `[52814190909/31250000000000, 1690054109089/1000000000000000]` |
| 12 candidate blocks, every other expense waived | `[169728852851/100000000000000, 1697288528511/1000000000000000]` |
| 5% target above the selected upper endpoint | `35491136290869/20000000000000000` |
| 134 ideal blocks | `[354904755149/200000000000000, 887261887873/500000000000000]` |
| 135 ideal blocks | `[443796495809/250000000000000, 1775185983237/1000000000000000]` |

The 12-block upper endpoint is only 0.428059% above the selected lower endpoint. At 134 blocks the ceiling remains below the 5% target; at 135 its lower endpoint exceeds the target. Since this Phase B candidate family has at most 12 disjoint four-child windows, even its ideal zero-extra-cost profile cannot meet the task's 5% gate. The screen assigns zero charge to source routing, frame, copy, hosting, precision, and restoration work; any such item that consumes paid child-rank units would make the ceiling less favorable.

This result closes only the consecutive four-child `(3,1,1,1)->6` Phase B candidate envelope on the pinned source. It does not rule out collecting nonconsecutive calls with a new buffer or schedule, a different selected word, another phase, or another tensor. The 12 windows are not certified placements: their exact frame compatibility and the inherited tensor's caller-level input/output maps remain unproved.

## Provenance and relation to nearby work

- [PR #1866](https://github.com/CrocSwap/integer-mult-bounds/pull/1866) supplies the exact six-atom `(3,1,1,1)->6` tensor and dirty-output contract. This package pins its certificate and README and does not repeat its tensor proof. Its source scan covered phase A; this package addresses the expressly open Phase B census.
- [PR #1779](https://github.com/CrocSwap/integer-mult-bounds/pull/1779) groups rank-one children; the current block remains heterogeneous.
- The adjacent active [Discussion #1693](https://github.com/CrocSwap/integer-mult-bounds/discussions/1693) concerns same-column rank-one-to-rank-two retiming and a different paid-profile change.
- The claim and result handoff are in [Discussion #2119](https://github.com/CrocSwap/integer-mult-bounds/discussions/2119).

## Reproduce

From the repository root with Python 3.12:

```sh
python3.12 scripts/research_package.py --package research/complex-rank6-phaseb-seedb43a017f --check-only
python3.12 scripts/research_package.py --package research/complex-rank6-phaseb-seedb43a017f
```

The registered replay checks all source and member pins, both Phase B orientations, each candidate window and frame span, the disjoint schedule, negative controls, and the exact ceiling boundary. Expected marker:

```text
PASS_PHASEB_RANKSHAPE_SCREEN windows=12 disjoint=12 target_minimum=135 gain_upper_pct=0.428058
```

## Open next questions

- Can an exact buffered or nonconsecutive Phase B schedule implement the inherited tensor on a common input/output frame with enough blocks to matter? Begin with one selected window: derive its caller-level operands, complete delayed scalar dependency graph, common-frame encoding, output routing, and arbitrary-dirty inverse, then account for every added frame, copy, and child charge before expanding the census.

Credit PR #1866 for the tensor, exact rank proof, and dirty-state identity; the selected-provider lineage is retained in its pinned source manifest. Prepared by Cinna / commdata2338 with substantial OpenAI Codex assistance in source profiling, exact frame analysis, bounded enumeration, verifier, cost calculation, and writing. No independent human review is claimed. New material is Apache-2.0.
