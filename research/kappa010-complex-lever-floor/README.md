# κ = 0.1 budget screens and a corrected paired-plane route

**Scoped budget screen; no κ improvement or supplier is claimed.** The selected conditional result remains κ = 0.001672660197076918. This checks what the already explored two-output anchor, centre removal, rank-16 repacking and a changed coverage law would need to accomplish at `κ=1/10`.

## Result

The retained transfer `κ = a/(1+a)` maps `κ=1/10` to the exact target `a=1/9`. We use the certified outward-rational interval engine in `complex-local-word-ceiling/ceiling.py` and the pinned selected profile and two-output-anchor receipt.

The selected complex word still fails badly at the target after deleting its eight rank-8 centre children and all 64 units of centre charge. Its largest feasible unpaid count with that fixed local profile is `u=17`; the exact interval moment there is approximately **1.151904798395**, above one. Since increasing `u` only reduces the idle remainder and this is already the largest feasible `u`, no coverage change alone can rescue the fixed selected profile in this relaxed model.

We next grant the strongest combination from the local two-output-anchor exploration:

1. Seven hypothetical 112-port blocks replace 332 rank-one children with 112 children per block.
2. The 112 affine additions in each block are charged as 112 rank-one-equivalent units, giving rank-one profile count 1,656.
3. The complete centre path is deleted, including its 64-unit charge and eight rank-8 children.
4. All remaining paid local rank mass, exactly 4,766, is fractionally repacked into rank-16 children.
5. All source alignment, dirty-state handling, routing, frame, precision, restoration and physical costs are waived.

Even this combined relaxation has target moment **1.077445412079** with four unpaid coordinates. Its exact unpaid-coordinate boundary is:

| Model at `a=1/9` | Previous integer | Moment | First passing integer | Moment |
|---|---:|---:|---:|---:|
| Seven anchors, centre free, original local ranks | `u=23` | 1.007064932212 | `u=24` | 0.992809414512 |
| Seven anchors, centre free, all mass at rank 16 | `u=9` | 1.006167823580 | `u=10` | 0.991912305880 |
| Same rank-16 model, centre charge retained | `u=10` | 1.001076567258 | `u=11` | 0.986821049559 |

The inequalities are decided by exact rational interval endpoints; decimals are for orientation. The positive control reproduces a passing moment at the repository's smaller planning target `a=1/99` with the same ideal rank-16 profile and only one unpaid coordinate.

There is also a concrete five-plane P112 decoder in the local archive with a reported `u=5` endpoint. Its pinned profile is `{1:2412, 2:418, 3:432, 4:142, 5:82, 7:10, 8:6}`. Using the exact same selected replay archive as the present checkpoint, its moment at `a=1/9`, `u=5`, and centre charge 64 is **1.336180761792**. More strongly, its paid local terms alone contribute at least **1.165241830803**, before any idle remainder is added. Therefore no change to `u`, centre charge or idle packing can make this *fixed local profile* reach the 0.1 target. This is scoped to its profile, not to the P112 endpoint family or other decoders.

Even replacing that whole profile with fractional rank-16 children and deleting the centre leaves moment **1.080393847328** at `u=5`; the first passing counts are `u=11` centre-free and `u=12` with the centre charge. With `u=5` held fixed, every 5,640 units would instead need a uniform local rank of at least 37 centre-free or 41 with the centre. The existing decoder's paid terms have ranks 7 and 8. The exact threshold checker reuses its pinned profile and source manifest; it does not replay that decoder's algebra.

There is a clear exchange rate between the two remaining structural levers. Keep the same 4,766 units of local mass, place it fractionally at one uniform rank `r`, and leave only the idle remainder at rank 51. The first passing `u` is:

| Assumed local rank `r` for all 4,766 units | First passing `u`, centre free | First passing `u`, centre retained |
|---:|---:|---:|
| 16 | 10 | 11 |
| 32 | 6 | 7 |
| 48 | 4 | 4 |
| 51 | 3 | 4 |

Conversely, with only four unpaid coordinates, the local consumer must place all this mass at rank at least 42 if the centre is removed, or rank at least 47 if it remains. These are exact boundaries in the relaxed profile model. They suggest the concrete alternatives for further construction work: prove substantially more unpaid coverage, or build a consumer close to the maximum admitted idle rank. Neither exists at the selected provider boundary today.

The target also leaves little room for a complete anchor invoice. With all 4,766 units placed at rank 16, the largest integer per-block rank-one-equivalent fee is `e=170` at `u=10` with the centre removed; `e=171` fails. The known 112 affine additions use 112 of that allowance, leaving at most 58 units per block for every other interface cost under the same tariff. If the centre charge remains and coverage rises to `u=11`, the boundary is `e=207` passing versus `e=208` failing, leaving 95 units beyond the 112 affine additions. These are exact moment boundaries, not realized physical prices.

This gives a concrete target-scale requirement for this bundle: even after granting all its local and consumer costs for free, it needs **ten unpaid coordinates per live family** if the centre is actually removed, or eleven if the centre charge remains. The existing selected contract has one. The local anchor result does not realize any replacement coverage identity, and fractional rank-16 repacking is not a decoder.

## Tensorized paired-plane endpoint: separate scalar work from child rank

The exact [block-valued paired-plane endpoint](../paired-plane-block-rank/README.md) and its [49-support fitting matrix](../paired-plane-minrank-bracket-audit/README.md) partition the 112 ports into supports of sizes `{1: 2, 2: 31, 3: 16}`. Under the full port-space charge used by PR2203, a support of size `s` costs rank `2s`; the per-copy child profile is `{2: 2, 4: 31, 6: 16}`, with mass **224**. Tensor multiplicity `d` gives profile mass `224d`; the proposed two-plane coverage rule is `u=2d`.

The previous screen treated the minimum `q−2=110` dirty-target `ADD`s per block as rank-one-equivalent fees inside the exponent moment. That was only a hypothetical tariff. The arbitrary-dirty anchor's source package explicitly charges its 224 scalar additions per block in the scalar compiler envelope separately. The corrected screen therefore keeps scalar `ADD`s out of the recursive child-rank profile and reports rank-one-equivalent fees only as sensitivity cases.

Seven hypothetical q=112 dirty-output anchors replace 332 rank-one children by 112 per block. After deleting the centre path, the remaining mass is 3,982. I grant an optimistic consumer by fractionally repacking it at the maximum idle rank 51. The exact moment intervals at `a=1/9` then give:

| Tensor copies `d` | Proposed unpaid `u=2d` | Centre-free moment | Moment with centre |
|---:|---:|---:|---:|
| 1 | 2 | 1.021884 | 1.033143 |
| 2 | 4 | 1.003115 | 1.014374 |
| 3 | 6 | **0.984346** | **0.995605** |
| 4 | 8 | 0.965578 | 0.976836 |
| 5 | 10 | 0.946809 | 0.958068 |
| 6 | 12 | 0.928040 | 0.939299 |
| 7 | 14 | 0.909271 | 0.920530 |

The intervals are outward-rational and the decimals are for orientation. In this relaxation, `d=3` is the first moment pass even with the centre retained. The zero-fee mass capacity is feasible through `d=7`; `d=8` exceeds it by exactly `298/3`. This corrects the earlier fee-based rejection. It does **not** establish that the tensorized endpoint can be placed in the selected provider, or that the proposed `u=2d` coverage identity holds for a complete hosted call.

The exact arbitrary-dirty anchor receipt also checks its known scalar invoice: seven blocks use 1,568 unit-addition macros, giving a conservative local primitive bound of **10,688,681,187,742**, below the strict `2^48` guard **281,474,976,710,656**. This covers the anchor schedule only. The paired-plane factorization's child implementation, operand preparation, frame paths, precision/tape effects, restoration, and complete source placement remain to be priced. As a sensitivity, if other interface charges were translated to rank-one-equivalent units, the passing `d=3` row has room for at most 28 per block without the centre or 8 with it; no such conversion is claimed for scalar `ADD`s.

The unchanged bit-side primitive endpoint is `a=0.001733427039589844234749`, which converts to a complete `κ` cap of about `0.001730427469823603`. Even if this complex-side relaxation were made real, the complete selected construction would still be capped far below `κ>0.1`. No new κ or supplier is claimed.

## Scope and next step

This is a corrected, optimistic moment screen for a fixed support fit, seven dirty-output anchor replacements, and a proposed two-unpaid-coordinate-per-copy law. The algebraic fitting matrix has exact source-bound premises, but the work here does not compose its 49-support channels with the selected supplier's chronological operand and frame trace. The rank-51 repacking also grants every remaining local mass unit its best permitted idle rank. Unknown costs remain unknown; they are not zero in a supplier claim.

The next useful test is one complete source-bound block: bind its 112 input and dirty output coordinates to a selected-provider trace, state how the 49 support queries are produced and decoded, and account for every child payload, scalar operation, frame, inverse, precision effect, and caller transfer. A pass there would make the d=3 profile a meaningful construction target. Separately, the bit-side mechanism needs a distinct path capable of moving its endpoint from about `0.00173343` to above `0.1`; this complex-side result cannot do that work.

## Reproduction

From the repository root:

```sh
python3 -B research/kappa010-complex-lever-floor/verify.py
python3 scripts/research_package.py --package research/kappa010-complex-lever-floor --check-only
python3.12 scripts/research_package.py --package research/kappa010-complex-lever-floor
```

The verifier binds the selected record, current local ceiling model, two-output and arbitrary-dirty anchor receipts, and paired-plane fit receipts in [SOURCES.json](SOURCES.json). It checks the exact `a=1/9` interval boundaries, the rank/unpaid and fee frontiers, the 49-support full port-space profile, all feasible tensor multiplicities `d=1..7` with scalar additions separate, the `d=8` mass excess, the arbitrary-dirty anchor's scalar guard invoice, and the lower `a=1/99` positive control.

## Predecessors and credit

This is a target refinement of the `coverage-law-change` question, motivated by the donor-set target κ > 0.1. The local two-output and arbitrary-dirty temporary-sum maps retain Cinna / commdata2338's [anchor](../complex-two-output-sum-anchor-seed65ce19/README.md) and the dirty-output extension's predecessor attribution in [its package](../complex-dirty-output-temporary-sum-anchor/README.md). The paired-plane construction retains the credits in its own README, including thakrarsagar's 49-support fit, ywz65's block-rank extension, Adam Gall's strict mask, and the PR1825 matching and PR2203 native payload accounting. The interval ceiling and selected profile are credited in [complex-local-word-ceiling](../complex-local-word-ceiling/README.md). This package adds only target-specific combined-lever budgets and a correction to scalar-versus-rank charging. Prepared by Codex with substantial OpenAI assistance; no independent human review is claimed. New work is Apache-2.0.

A fresh overlap refresh on 2026-10-17 covered 259 open PRs and 1,866 discussions (complete pagination). Open PR #3093 checks two fixed local profiles (#2979 and #3042) at the same target. This package instead screens the selected profile, pinned five-plane profile, and seven-anchor/tensorized paired-plane relaxation, including exact unpaid-coordinate, scalar-guard and rank-one-equivalent fee-sensitivity boundaries; scopes are complementary. Local matches include the earlier `kappa01-complex-target-screen`, the P112 five-plane decoder and prior coverage-law packages, so novelty is not claimed. Relevant PRs #3064 and #3097 and Discussions #1163, #1166, #1167 and #2838 were also checked. Canonical main was refreshed at `18aacb215fc3717b06be8ceb9fca62aeca0d3e99` (priority revision 6); the selected record and quantitative predecessor receipts are unchanged.

## Open next questions

1. **Can one d=3 paired-plane block be composed with a selected-provider trace?** It matters because this is the first exact moment pass at `a=1/9`. First step: bind all 112 source and arbitrary-dirty target coordinates, the 49 support queries, child payloads, and their inverse to one chronological subword. Blocker: no such product grouping or frame path is source-bound.
2. **What is the complete scalar and native invoice for that block?** The known seven-anchor ADD schedule fits its local scalar guard, but this does not price query preparation, child wrappers, frame conversions, precision, tape or outer cleanup for the paired-plane factorization. First step: list the literal operations for one block and apply the exact guard adapters. Blocker: the algebraic fitting certificate has no native schedule.
3. **How could the bit-side endpoint rise above 0.1?** Even a complete complex-side win leaves the selected bit endpoint near `0.00173343`. First step: identify a separate bit-side mechanism and a fully charged target profile; no such candidate is part of this package.
