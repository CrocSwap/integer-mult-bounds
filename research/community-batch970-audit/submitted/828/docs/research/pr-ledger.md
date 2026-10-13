# PR review and integration ledger

The immutable starting snapshot contains **446 PRs**. Explicit later family rounds extend the current inventory to **535**; unrelated arrivals remain outside the round.

[Machine-readable ledger](pr-ledger.json) · [Starting snapshot](../../research/pr-reconciliation-20261012/starting-snapshot.json)

The ledger separates historical review from integration. A prior snapshot or a mention in a note does not certify a contribution. “Partially reviewed” includes scoped review and triage with their original limitations; “changed since review” means the present head lacks matching recorded coverage. Archived incorporation preserves a historical implementation and attribution without making it the selected result.

| Disposition | Count |
|---|---:|
| changed since review | 6 |
| incorporated | 97 |
| partially reviewed | 150 |
| unreviewed | 282 |

The earlier reconciliation closing snapshot had 438 starting PRs still open and 441 total open. These are historical counts, not a live queue measurement. Later dispositions are recorded below.

[Earlier family review](community-family533-review.md) · [Earlier dispositions](../../research/community-family533-audit/DISPOSITIONS.json)

The earlier construction family #533–#537 and formal connections #513/#528 are covered there, including the #503/#510 bit dependency. #463 has only its vendored pipeline subset reviewed.

[Family through #588](community-family588-review.md) · [Exact-head dispositions](../../research/community-family588-audit/DISPOSITIONS.json)

This frozen round covers #543/#545/#555 and related construction, research and tooling packages through #588. Each disposition distinguishes completed checks, publication and remaining obligations. The separate formalization PRs and later arrivals are not approved by this round.

## Remaining priorities

1. Follow the new Linux CI for the published #442/#484/#509/#516/#520 batch; the [scoped review](community-formal-20261012-review.md) records completed local checks.
2. Follow the explicit construction-family dispositions and remaining obligations; do not repeat completed foundation replays without a source/input change.
3. Review #525’s checkpoint/ceiling and #529/#532’s distinct construction mechanisms; retain parallel credit.
4. Reconcile #210/#279 updates with their earlier incorporated heads; audit #236’s source-package integration separately from its already published review receipts.
5. Continue finite-instance connections for formal interfaces; abstract theorem builds do not instantiate all current physical constructions.

## Starting PR inventory

Each evidence link leads to the original scoped assessment. The JSON records exact heads, unresolved questions, integration locations and closure receipts.

| PR | Contributor | Disposition | Evidence or remaining question |
|---|---|---|---|
| [#1](https://github.com/CrocSwap/integer-mult-bounds/pull/1) | Paureel | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#2](https://github.com/CrocSwap/integer-mult-bounds/pull/2) | Bortlesboat | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#3](https://github.com/CrocSwap/integer-mult-bounds/pull/3) | eumemic | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#4](https://github.com/CrocSwap/integer-mult-bounds/pull/4) | dleen | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#5](https://github.com/CrocSwap/integer-mult-bounds/pull/5) | eumemic | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#6](https://github.com/CrocSwap/integer-mult-bounds/pull/6) | eumemic | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#7](https://github.com/CrocSwap/integer-mult-bounds/pull/7) | jacklightChen | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#8](https://github.com/CrocSwap/integer-mult-bounds/pull/8) | rohanarun | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#9](https://github.com/CrocSwap/integer-mult-bounds/pull/9) | rohanarun | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#12](https://github.com/CrocSwap/integer-mult-bounds/pull/12) | rohanarun | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#13](https://github.com/CrocSwap/integer-mult-bounds/pull/13) | eumemic | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#14](https://github.com/CrocSwap/integer-mult-bounds/pull/14) | rohanarun | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#15](https://github.com/CrocSwap/integer-mult-bounds/pull/15) | eumemic | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#16](https://github.com/CrocSwap/integer-mult-bounds/pull/16) | jacklightChen | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#17](https://github.com/CrocSwap/integer-mult-bounds/pull/17) | rohanarun | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#19](https://github.com/CrocSwap/integer-mult-bounds/pull/19) | rohanarun | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#20](https://github.com/CrocSwap/integer-mult-bounds/pull/20) | hipotures | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#21](https://github.com/CrocSwap/integer-mult-bounds/pull/21) | jacklightChen | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#22](https://github.com/CrocSwap/integer-mult-bounds/pull/22) | DominikScholz | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#23](https://github.com/CrocSwap/integer-mult-bounds/pull/23) | jacklightChen | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#25](https://github.com/CrocSwap/integer-mult-bounds/pull/25) | rohanarun | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#27](https://github.com/CrocSwap/integer-mult-bounds/pull/27) | DominikScholz | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#28](https://github.com/CrocSwap/integer-mult-bounds/pull/28) | rohanarun | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#29](https://github.com/CrocSwap/integer-mult-bounds/pull/29) | jacklightChen | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#31](https://github.com/CrocSwap/integer-mult-bounds/pull/31) | rohanarun | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#33](https://github.com/CrocSwap/integer-mult-bounds/pull/33) | DominikScholz | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#34](https://github.com/CrocSwap/integer-mult-bounds/pull/34) | jamesyc | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#35](https://github.com/CrocSwap/integer-mult-bounds/pull/35) | DominikScholz | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#38](https://github.com/CrocSwap/integer-mult-bounds/pull/38) | DominikScholz | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#40](https://github.com/CrocSwap/integer-mult-bounds/pull/40) | rohanarun | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#41](https://github.com/CrocSwap/integer-mult-bounds/pull/41) | hipotures | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#42](https://github.com/CrocSwap/integer-mult-bounds/pull/42) | rohanarun | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#44](https://github.com/CrocSwap/integer-mult-bounds/pull/44) | rohanarun | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#47](https://github.com/CrocSwap/integer-mult-bounds/pull/47) | rohanarun | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#63](https://github.com/CrocSwap/integer-mult-bounds/pull/63) | DominikScholz | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#65](https://github.com/CrocSwap/integer-mult-bounds/pull/65) | rohanarun | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#66](https://github.com/CrocSwap/integer-mult-bounds/pull/66) | chafreaky | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#67](https://github.com/CrocSwap/integer-mult-bounds/pull/67) | rohanarun | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#68](https://github.com/CrocSwap/integer-mult-bounds/pull/68) | DominikScholz | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#69](https://github.com/CrocSwap/integer-mult-bounds/pull/69) | eumemic | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#70](https://github.com/CrocSwap/integer-mult-bounds/pull/70) | alejandrozu | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#71](https://github.com/CrocSwap/integer-mult-bounds/pull/71) | chafreaky | partially reviewed | [record 1](../../docs/research/community-round3-validation.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#74](https://github.com/CrocSwap/integer-mult-bounds/pull/74) | tomdif | partially reviewed | [record 1](../../docs/research/community-round3-validation.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#75](https://github.com/CrocSwap/integer-mult-bounds/pull/75) | alejandrozu | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#76](https://github.com/CrocSwap/integer-mult-bounds/pull/76) | DominikScholz | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#77](https://github.com/CrocSwap/integer-mult-bounds/pull/77) | huxint | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#78](https://github.com/CrocSwap/integer-mult-bounds/pull/78) | rohanarun | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#79](https://github.com/CrocSwap/integer-mult-bounds/pull/79) | chafreaky | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#80](https://github.com/CrocSwap/integer-mult-bounds/pull/80) | rohanarun | partially reviewed | [record 1](../../docs/research/community-round3-validation.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#81](https://github.com/CrocSwap/integer-mult-bounds/pull/81) | DominikScholz | partially reviewed | [record 1](../../docs/research/community-round4-validation.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#82](https://github.com/CrocSwap/integer-mult-bounds/pull/82) | rohanarun | partially reviewed | [record 1](../../docs/research/community-round4-validation.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#83](https://github.com/CrocSwap/integer-mult-bounds/pull/83) | JosephDemarest | partially reviewed | [record 1](../../docs/research/community-round4-validation.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#84](https://github.com/CrocSwap/integer-mult-bounds/pull/84) | chafreaky | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#85](https://github.com/CrocSwap/integer-mult-bounds/pull/85) | rohanarun | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#86](https://github.com/CrocSwap/integer-mult-bounds/pull/86) | rohanarun | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#87](https://github.com/CrocSwap/integer-mult-bounds/pull/87) | gupt1156 | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#88](https://github.com/CrocSwap/integer-mult-bounds/pull/88) | chafreaky | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#89](https://github.com/CrocSwap/integer-mult-bounds/pull/89) | rohanarun | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#90](https://github.com/CrocSwap/integer-mult-bounds/pull/90) | anxkhn | partially reviewed | [record 1](../../docs/research/community-round5-validation.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#91](https://github.com/CrocSwap/integer-mult-bounds/pull/91) | chafreaky | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#92](https://github.com/CrocSwap/integer-mult-bounds/pull/92) | maxime-fleury | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#93](https://github.com/CrocSwap/integer-mult-bounds/pull/93) | rohanarun | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#94](https://github.com/CrocSwap/integer-mult-bounds/pull/94) | maxime-fleury | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#95](https://github.com/CrocSwap/integer-mult-bounds/pull/95) | rohanarun | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#97](https://github.com/CrocSwap/integer-mult-bounds/pull/97) | jacklightChen | partially reviewed | [record 1](../../docs/research/community-round5-validation.json) · [record 2](../../docs/research/community-round6-validation.json) · [record 3](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#98](https://github.com/CrocSwap/integer-mult-bounds/pull/98) | rohanarun | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#99](https://github.com/CrocSwap/integer-mult-bounds/pull/99) | djsmanchanda | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#100](https://github.com/CrocSwap/integer-mult-bounds/pull/100) | rohanarun | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#102](https://github.com/CrocSwap/integer-mult-bounds/pull/102) | SovereignSteak | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#103](https://github.com/CrocSwap/integer-mult-bounds/pull/103) | rohanarun | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#106](https://github.com/CrocSwap/integer-mult-bounds/pull/106) | Th0rgal | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#107](https://github.com/CrocSwap/integer-mult-bounds/pull/107) | rohanarun | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#108](https://github.com/CrocSwap/integer-mult-bounds/pull/108) | rohanarun | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#109](https://github.com/CrocSwap/integer-mult-bounds/pull/109) | rohanarun | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#110](https://github.com/CrocSwap/integer-mult-bounds/pull/110) | ikeboy | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#111](https://github.com/CrocSwap/integer-mult-bounds/pull/111) | rohanarun | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#113](https://github.com/CrocSwap/integer-mult-bounds/pull/113) | rohanarun | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#114](https://github.com/CrocSwap/integer-mult-bounds/pull/114) | eumemic | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#116](https://github.com/CrocSwap/integer-mult-bounds/pull/116) | rohanarun | changed since review | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#117](https://github.com/CrocSwap/integer-mult-bounds/pull/117) | eumemic | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#118](https://github.com/CrocSwap/integer-mult-bounds/pull/118) | rohanarun | changed since review | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#121](https://github.com/CrocSwap/integer-mult-bounds/pull/121) | Th0rgal | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#122](https://github.com/CrocSwap/integer-mult-bounds/pull/122) | SovereignSteak | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#123](https://github.com/CrocSwap/integer-mult-bounds/pull/123) | rohanarun | changed since review | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#124](https://github.com/CrocSwap/integer-mult-bounds/pull/124) | jamesyc | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#125](https://github.com/CrocSwap/integer-mult-bounds/pull/125) | GamingPuzzled | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#126](https://github.com/CrocSwap/integer-mult-bounds/pull/126) | DanieleCorso | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#127](https://github.com/CrocSwap/integer-mult-bounds/pull/127) | GamingPuzzled | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#128](https://github.com/CrocSwap/integer-mult-bounds/pull/128) | an664 | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#129](https://github.com/CrocSwap/integer-mult-bounds/pull/129) | eumemic | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#131](https://github.com/CrocSwap/integer-mult-bounds/pull/131) | eumemic | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#133](https://github.com/CrocSwap/integer-mult-bounds/pull/133) | Th0rgal | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#135](https://github.com/CrocSwap/integer-mult-bounds/pull/135) | DanieleCorso | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#137](https://github.com/CrocSwap/integer-mult-bounds/pull/137) | eumemic | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#138](https://github.com/CrocSwap/integer-mult-bounds/pull/138) | geckods | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#141](https://github.com/CrocSwap/integer-mult-bounds/pull/141) | chafreaky | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#142](https://github.com/CrocSwap/integer-mult-bounds/pull/142) | eumemic | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#143](https://github.com/CrocSwap/integer-mult-bounds/pull/143) | eumemic | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#145](https://github.com/CrocSwap/integer-mult-bounds/pull/145) | Th0rgal | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#146](https://github.com/CrocSwap/integer-mult-bounds/pull/146) | Th0rgal | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) · [record 2](../../research/pr-reconciliation-20261012/content-comparison.json) |
| [#148](https://github.com/CrocSwap/integer-mult-bounds/pull/148) | gupt1156 | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) · [record 2](../../research/pr-reconciliation-20261012/content-comparison.json) |
| [#153](https://github.com/CrocSwap/integer-mult-bounds/pull/153) | geckods | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#154](https://github.com/CrocSwap/integer-mult-bounds/pull/154) | eumemic | partially reviewed | [record 1](../../research/community-round8-audit/validation.json) |
| [#158](https://github.com/CrocSwap/integer-mult-bounds/pull/158) | geckods | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#160](https://github.com/CrocSwap/integer-mult-bounds/pull/160) | GamingPuzzled | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#162](https://github.com/CrocSwap/integer-mult-bounds/pull/162) | DaysSky | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#163](https://github.com/CrocSwap/integer-mult-bounds/pull/163) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#164](https://github.com/CrocSwap/integer-mult-bounds/pull/164) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#165](https://github.com/CrocSwap/integer-mult-bounds/pull/165) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#166](https://github.com/CrocSwap/integer-mult-bounds/pull/166) | jamesyc | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#167](https://github.com/CrocSwap/integer-mult-bounds/pull/167) | GamingPuzzled | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#168](https://github.com/CrocSwap/integer-mult-bounds/pull/168) | eumemic | incorporated | [record 1](../../research/community-round8-audit/validation.json) · [record 2](../../research/pr-reconciliation-20261012/incorporation-checks.json) |
| [#169](https://github.com/CrocSwap/integer-mult-bounds/pull/169) | GamingPuzzled | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#170](https://github.com/CrocSwap/integer-mult-bounds/pull/170) | huxint | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#171](https://github.com/CrocSwap/integer-mult-bounds/pull/171) | jon314159 | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#172](https://github.com/CrocSwap/integer-mult-bounds/pull/172) | mikey1201 | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#173](https://github.com/CrocSwap/integer-mult-bounds/pull/173) | GamingPuzzled | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#174](https://github.com/CrocSwap/integer-mult-bounds/pull/174) | TeS44 | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#175](https://github.com/CrocSwap/integer-mult-bounds/pull/175) | chafreaky | incorporated | [record 1](../../research/community-round8-audit/validation.json) · [record 2](../../research/pr-reconciliation-20261012/incorporation-checks.json) |
| [#177](https://github.com/CrocSwap/integer-mult-bounds/pull/177) | gabriele-nespoli | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#178](https://github.com/CrocSwap/integer-mult-bounds/pull/178) | rohanarun | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#179](https://github.com/CrocSwap/integer-mult-bounds/pull/179) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#180](https://github.com/CrocSwap/integer-mult-bounds/pull/180) | M6LI | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#181](https://github.com/CrocSwap/integer-mult-bounds/pull/181) | chafreaky | incorporated | [record 1](../../research/community-round8-audit/validation.json) · [record 2](../../research/pr-reconciliation-20261012/incorporation-checks.json) |
| [#182](https://github.com/CrocSwap/integer-mult-bounds/pull/182) | chafreaky | partially reviewed | [record 1](../../research/community-round8-audit/validation.json) · [record 2](../../research/pr-reconciliation-20261012/content-comparison.json) |
| [#183](https://github.com/CrocSwap/integer-mult-bounds/pull/183) | romainhedouin | partially reviewed | [record 1](../../research/pr-reconciliation-20261012/content-comparison.json) |
| [#185](https://github.com/CrocSwap/integer-mult-bounds/pull/185) | rohanarun | partially reviewed | [record 1](../../research/community-round8-audit/validation.json) · [record 2](../../research/pr-reconciliation-20261012/content-comparison.json) |
| [#187](https://github.com/CrocSwap/integer-mult-bounds/pull/187) | rohanarun | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#188](https://github.com/CrocSwap/integer-mult-bounds/pull/188) | huxint | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#189](https://github.com/CrocSwap/integer-mult-bounds/pull/189) | chafreaky | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#191](https://github.com/CrocSwap/integer-mult-bounds/pull/191) | ikeboy | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#192](https://github.com/CrocSwap/integer-mult-bounds/pull/192) | DaysSky | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#193](https://github.com/CrocSwap/integer-mult-bounds/pull/193) | ikeboy | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#194](https://github.com/CrocSwap/integer-mult-bounds/pull/194) | ikeboy | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#195](https://github.com/CrocSwap/integer-mult-bounds/pull/195) | huxint | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#196](https://github.com/CrocSwap/integer-mult-bounds/pull/196) | chafreaky | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#197](https://github.com/CrocSwap/integer-mult-bounds/pull/197) | evmckinney9 | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#199](https://github.com/CrocSwap/integer-mult-bounds/pull/199) | maxime-fleury | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#200](https://github.com/CrocSwap/integer-mult-bounds/pull/200) | chafreaky | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#201](https://github.com/CrocSwap/integer-mult-bounds/pull/201) | DaysSky | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#202](https://github.com/CrocSwap/integer-mult-bounds/pull/202) | chafreaky | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#203](https://github.com/CrocSwap/integer-mult-bounds/pull/203) | huxint | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#204](https://github.com/CrocSwap/integer-mult-bounds/pull/204) | maxime-fleury | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#205](https://github.com/CrocSwap/integer-mult-bounds/pull/205) | rohanarun | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#207](https://github.com/CrocSwap/integer-mult-bounds/pull/207) | Dugongue | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#208](https://github.com/CrocSwap/integer-mult-bounds/pull/208) | maxime-fleury | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#210](https://github.com/CrocSwap/integer-mult-bounds/pull/210) | eumemic | changed since review | [record 1](../../docs/research/community-pr210-integration.json) · [record 2](../../research/community-round9-audit/review-ledger.json) · [record 3](../../research/pr-reconciliation-20261012/content-comparison.json) |
| [#211](https://github.com/CrocSwap/integer-mult-bounds/pull/211) | rohanarun | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#212](https://github.com/CrocSwap/integer-mult-bounds/pull/212) | chafreaky | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#214](https://github.com/CrocSwap/integer-mult-bounds/pull/214) | antoine-olivier | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#215](https://github.com/CrocSwap/integer-mult-bounds/pull/215) | GamingPuzzled | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#216](https://github.com/CrocSwap/integer-mult-bounds/pull/216) | Dugongue | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#217](https://github.com/CrocSwap/integer-mult-bounds/pull/217) | hcg890 | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#221](https://github.com/CrocSwap/integer-mult-bounds/pull/221) | maxime-fleury | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#223](https://github.com/CrocSwap/integer-mult-bounds/pull/223) | ikeboy | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#224](https://github.com/CrocSwap/integer-mult-bounds/pull/224) | maxime-fleury | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#225](https://github.com/CrocSwap/integer-mult-bounds/pull/225) | chafreaky | changed since review | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#226](https://github.com/CrocSwap/integer-mult-bounds/pull/226) | pCwOrM | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#227](https://github.com/CrocSwap/integer-mult-bounds/pull/227) | Dugongue | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#228](https://github.com/CrocSwap/integer-mult-bounds/pull/228) | tehruhn | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#229](https://github.com/CrocSwap/integer-mult-bounds/pull/229) | maxime-fleury | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#233](https://github.com/CrocSwap/integer-mult-bounds/pull/233) | chafreaky | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#234](https://github.com/CrocSwap/integer-mult-bounds/pull/234) | hcg890 | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#235](https://github.com/CrocSwap/integer-mult-bounds/pull/235) | gabriele-nespoli | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#236](https://github.com/CrocSwap/integer-mult-bounds/pull/236) | jamesyc | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#237](https://github.com/CrocSwap/integer-mult-bounds/pull/237) | rohanarun | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#240](https://github.com/CrocSwap/integer-mult-bounds/pull/240) | rohanarun | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#241](https://github.com/CrocSwap/integer-mult-bounds/pull/241) | maxime-fleury | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#242](https://github.com/CrocSwap/integer-mult-bounds/pull/242) | Dugongue | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#243](https://github.com/CrocSwap/integer-mult-bounds/pull/243) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#244](https://github.com/CrocSwap/integer-mult-bounds/pull/244) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#245](https://github.com/CrocSwap/integer-mult-bounds/pull/245) | sandersdavid90-droid | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#248](https://github.com/CrocSwap/integer-mult-bounds/pull/248) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#249](https://github.com/CrocSwap/integer-mult-bounds/pull/249) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#250](https://github.com/CrocSwap/integer-mult-bounds/pull/250) | SovereignSteak | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#251](https://github.com/CrocSwap/integer-mult-bounds/pull/251) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#252](https://github.com/CrocSwap/integer-mult-bounds/pull/252) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#254](https://github.com/CrocSwap/integer-mult-bounds/pull/254) | Dugongue | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#255](https://github.com/CrocSwap/integer-mult-bounds/pull/255) | hvaliconAI | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#256](https://github.com/CrocSwap/integer-mult-bounds/pull/256) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#258](https://github.com/CrocSwap/integer-mult-bounds/pull/258) | amanforindia | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#259](https://github.com/CrocSwap/integer-mult-bounds/pull/259) | Dugongue | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#260](https://github.com/CrocSwap/integer-mult-bounds/pull/260) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#261](https://github.com/CrocSwap/integer-mult-bounds/pull/261) | sennemmi | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#262](https://github.com/CrocSwap/integer-mult-bounds/pull/262) | maxime-fleury | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#263](https://github.com/CrocSwap/integer-mult-bounds/pull/263) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#264](https://github.com/CrocSwap/integer-mult-bounds/pull/264) | dataisfire | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#265](https://github.com/CrocSwap/integer-mult-bounds/pull/265) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#266](https://github.com/CrocSwap/integer-mult-bounds/pull/266) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#267](https://github.com/CrocSwap/integer-mult-bounds/pull/267) | Dugongue | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#268](https://github.com/CrocSwap/integer-mult-bounds/pull/268) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#269](https://github.com/CrocSwap/integer-mult-bounds/pull/269) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#270](https://github.com/CrocSwap/integer-mult-bounds/pull/270) | utcorvusvolat-dotcom | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#271](https://github.com/CrocSwap/integer-mult-bounds/pull/271) | evmckinney9 | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#272](https://github.com/CrocSwap/integer-mult-bounds/pull/272) | Dugongue | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#273](https://github.com/CrocSwap/integer-mult-bounds/pull/273) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#274](https://github.com/CrocSwap/integer-mult-bounds/pull/274) | shea256 | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#275](https://github.com/CrocSwap/integer-mult-bounds/pull/275) | lydakis | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#277](https://github.com/CrocSwap/integer-mult-bounds/pull/277) | hcg890 | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#278](https://github.com/CrocSwap/integer-mult-bounds/pull/278) | hcg890 | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#279](https://github.com/CrocSwap/integer-mult-bounds/pull/279) | rohanarun | changed since review | [record 1](../../docs/research/community-pr279-integration.json) · [record 2](../../research/pr-reconciliation-20261012/content-comparison.json) · [later-head source and contributor replay](../../research/pr279-target-prefix-reconciliation/README.md); maintainer disposition pending |
| [#280](https://github.com/CrocSwap/integer-mult-bounds/pull/280) | utcorvusvolat-dotcom | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#281](https://github.com/CrocSwap/integer-mult-bounds/pull/281) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#282](https://github.com/CrocSwap/integer-mult-bounds/pull/282) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#283](https://github.com/CrocSwap/integer-mult-bounds/pull/283) | Dugongue | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#284](https://github.com/CrocSwap/integer-mult-bounds/pull/284) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#285](https://github.com/CrocSwap/integer-mult-bounds/pull/285) | DreamingOfClouds | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#286](https://github.com/CrocSwap/integer-mult-bounds/pull/286) | GamingPuzzled | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#287](https://github.com/CrocSwap/integer-mult-bounds/pull/287) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#288](https://github.com/CrocSwap/integer-mult-bounds/pull/288) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#289](https://github.com/CrocSwap/integer-mult-bounds/pull/289) | gupt1156 | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#290](https://github.com/CrocSwap/integer-mult-bounds/pull/290) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#291](https://github.com/CrocSwap/integer-mult-bounds/pull/291) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#292](https://github.com/CrocSwap/integer-mult-bounds/pull/292) | sannidhi-hemanth | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#293](https://github.com/CrocSwap/integer-mult-bounds/pull/293) | jacklightChen | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#294](https://github.com/CrocSwap/integer-mult-bounds/pull/294) | maximussthegreat | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#295](https://github.com/CrocSwap/integer-mult-bounds/pull/295) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#296](https://github.com/CrocSwap/integer-mult-bounds/pull/296) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#297](https://github.com/CrocSwap/integer-mult-bounds/pull/297) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#298](https://github.com/CrocSwap/integer-mult-bounds/pull/298) | M6LI | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#299](https://github.com/CrocSwap/integer-mult-bounds/pull/299) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#300](https://github.com/CrocSwap/integer-mult-bounds/pull/300) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#301](https://github.com/CrocSwap/integer-mult-bounds/pull/301) | maximussthegreat | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#302](https://github.com/CrocSwap/integer-mult-bounds/pull/302) | maximussthegreat | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#303](https://github.com/CrocSwap/integer-mult-bounds/pull/303) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#304](https://github.com/CrocSwap/integer-mult-bounds/pull/304) | DreamingOfClouds | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#305](https://github.com/CrocSwap/integer-mult-bounds/pull/305) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#306](https://github.com/CrocSwap/integer-mult-bounds/pull/306) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#307](https://github.com/CrocSwap/integer-mult-bounds/pull/307) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#308](https://github.com/CrocSwap/integer-mult-bounds/pull/308) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#309](https://github.com/CrocSwap/integer-mult-bounds/pull/309) | Dugongue | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#310](https://github.com/CrocSwap/integer-mult-bounds/pull/310) | utcorvusvolat-dotcom | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#311](https://github.com/CrocSwap/integer-mult-bounds/pull/311) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#312](https://github.com/CrocSwap/integer-mult-bounds/pull/312) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#313](https://github.com/CrocSwap/integer-mult-bounds/pull/313) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#314](https://github.com/CrocSwap/integer-mult-bounds/pull/314) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#315](https://github.com/CrocSwap/integer-mult-bounds/pull/315) | DreamingOfClouds | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#316](https://github.com/CrocSwap/integer-mult-bounds/pull/316) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#317](https://github.com/CrocSwap/integer-mult-bounds/pull/317) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#318](https://github.com/CrocSwap/integer-mult-bounds/pull/318) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#319](https://github.com/CrocSwap/integer-mult-bounds/pull/319) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#320](https://github.com/CrocSwap/integer-mult-bounds/pull/320) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#321](https://github.com/CrocSwap/integer-mult-bounds/pull/321) | Dugongue | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#322](https://github.com/CrocSwap/integer-mult-bounds/pull/322) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#323](https://github.com/CrocSwap/integer-mult-bounds/pull/323) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#324](https://github.com/CrocSwap/integer-mult-bounds/pull/324) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#325](https://github.com/CrocSwap/integer-mult-bounds/pull/325) | DreamingOfClouds | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#327](https://github.com/CrocSwap/integer-mult-bounds/pull/327) | DreamingOfClouds | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#328](https://github.com/CrocSwap/integer-mult-bounds/pull/328) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#329](https://github.com/CrocSwap/integer-mult-bounds/pull/329) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#330](https://github.com/CrocSwap/integer-mult-bounds/pull/330) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#331](https://github.com/CrocSwap/integer-mult-bounds/pull/331) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#332](https://github.com/CrocSwap/integer-mult-bounds/pull/332) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#333](https://github.com/CrocSwap/integer-mult-bounds/pull/333) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#334](https://github.com/CrocSwap/integer-mult-bounds/pull/334) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#335](https://github.com/CrocSwap/integer-mult-bounds/pull/335) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#336](https://github.com/CrocSwap/integer-mult-bounds/pull/336) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#337](https://github.com/CrocSwap/integer-mult-bounds/pull/337) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#338](https://github.com/CrocSwap/integer-mult-bounds/pull/338) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#339](https://github.com/CrocSwap/integer-mult-bounds/pull/339) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#340](https://github.com/CrocSwap/integer-mult-bounds/pull/340) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#341](https://github.com/CrocSwap/integer-mult-bounds/pull/341) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#342](https://github.com/CrocSwap/integer-mult-bounds/pull/342) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#343](https://github.com/CrocSwap/integer-mult-bounds/pull/343) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#344](https://github.com/CrocSwap/integer-mult-bounds/pull/344) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#345](https://github.com/CrocSwap/integer-mult-bounds/pull/345) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#346](https://github.com/CrocSwap/integer-mult-bounds/pull/346) | LJH-217 | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#347](https://github.com/CrocSwap/integer-mult-bounds/pull/347) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#348](https://github.com/CrocSwap/integer-mult-bounds/pull/348) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#349](https://github.com/CrocSwap/integer-mult-bounds/pull/349) | erebos-labs | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#350](https://github.com/CrocSwap/integer-mult-bounds/pull/350) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#351](https://github.com/CrocSwap/integer-mult-bounds/pull/351) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#352](https://github.com/CrocSwap/integer-mult-bounds/pull/352) | DaysSky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#353](https://github.com/CrocSwap/integer-mult-bounds/pull/353) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#354](https://github.com/CrocSwap/integer-mult-bounds/pull/354) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#355](https://github.com/CrocSwap/integer-mult-bounds/pull/355) | Dugongue | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#356](https://github.com/CrocSwap/integer-mult-bounds/pull/356) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#357](https://github.com/CrocSwap/integer-mult-bounds/pull/357) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#358](https://github.com/CrocSwap/integer-mult-bounds/pull/358) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#359](https://github.com/CrocSwap/integer-mult-bounds/pull/359) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#360](https://github.com/CrocSwap/integer-mult-bounds/pull/360) | Dugongue | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#361](https://github.com/CrocSwap/integer-mult-bounds/pull/361) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#362](https://github.com/CrocSwap/integer-mult-bounds/pull/362) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#363](https://github.com/CrocSwap/integer-mult-bounds/pull/363) | DaysSky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#364](https://github.com/CrocSwap/integer-mult-bounds/pull/364) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#365](https://github.com/CrocSwap/integer-mult-bounds/pull/365) | aliromman | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#366](https://github.com/CrocSwap/integer-mult-bounds/pull/366) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#367](https://github.com/CrocSwap/integer-mult-bounds/pull/367) | amanforindia | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#368](https://github.com/CrocSwap/integer-mult-bounds/pull/368) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#369](https://github.com/CrocSwap/integer-mult-bounds/pull/369) | applecrusher | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#370](https://github.com/CrocSwap/integer-mult-bounds/pull/370) | utcorvusvolat-dotcom | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#371](https://github.com/CrocSwap/integer-mult-bounds/pull/371) | artuskg | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#372](https://github.com/CrocSwap/integer-mult-bounds/pull/372) | DesmondForward | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#373](https://github.com/CrocSwap/integer-mult-bounds/pull/373) | DaysSky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#374](https://github.com/CrocSwap/integer-mult-bounds/pull/374) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#375](https://github.com/CrocSwap/integer-mult-bounds/pull/375) | DaysSky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#376](https://github.com/CrocSwap/integer-mult-bounds/pull/376) | applecrusher | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#377](https://github.com/CrocSwap/integer-mult-bounds/pull/377) | jacklightChen | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#378](https://github.com/CrocSwap/integer-mult-bounds/pull/378) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#379](https://github.com/CrocSwap/integer-mult-bounds/pull/379) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#380](https://github.com/CrocSwap/integer-mult-bounds/pull/380) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#381](https://github.com/CrocSwap/integer-mult-bounds/pull/381) | DaysSky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#382](https://github.com/CrocSwap/integer-mult-bounds/pull/382) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#383](https://github.com/CrocSwap/integer-mult-bounds/pull/383) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#384](https://github.com/CrocSwap/integer-mult-bounds/pull/384) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#385](https://github.com/CrocSwap/integer-mult-bounds/pull/385) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#386](https://github.com/CrocSwap/integer-mult-bounds/pull/386) | jacklightChen | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#387](https://github.com/CrocSwap/integer-mult-bounds/pull/387) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#388](https://github.com/CrocSwap/integer-mult-bounds/pull/388) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#389](https://github.com/CrocSwap/integer-mult-bounds/pull/389) | ai-nanachi | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#390](https://github.com/CrocSwap/integer-mult-bounds/pull/390) | Dugongue | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#391](https://github.com/CrocSwap/integer-mult-bounds/pull/391) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#392](https://github.com/CrocSwap/integer-mult-bounds/pull/392) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#394](https://github.com/CrocSwap/integer-mult-bounds/pull/394) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#395](https://github.com/CrocSwap/integer-mult-bounds/pull/395) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#396](https://github.com/CrocSwap/integer-mult-bounds/pull/396) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#397](https://github.com/CrocSwap/integer-mult-bounds/pull/397) | artuskg | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#398](https://github.com/CrocSwap/integer-mult-bounds/pull/398) | Dugongue | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#399](https://github.com/CrocSwap/integer-mult-bounds/pull/399) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#400](https://github.com/CrocSwap/integer-mult-bounds/pull/400) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#401](https://github.com/CrocSwap/integer-mult-bounds/pull/401) | Dugongue | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#402](https://github.com/CrocSwap/integer-mult-bounds/pull/402) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#403](https://github.com/CrocSwap/integer-mult-bounds/pull/403) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#404](https://github.com/CrocSwap/integer-mult-bounds/pull/404) | Dugongue | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#405](https://github.com/CrocSwap/integer-mult-bounds/pull/405) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#406](https://github.com/CrocSwap/integer-mult-bounds/pull/406) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#407](https://github.com/CrocSwap/integer-mult-bounds/pull/407) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#408](https://github.com/CrocSwap/integer-mult-bounds/pull/408) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#409](https://github.com/CrocSwap/integer-mult-bounds/pull/409) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#410](https://github.com/CrocSwap/integer-mult-bounds/pull/410) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#411](https://github.com/CrocSwap/integer-mult-bounds/pull/411) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#412](https://github.com/CrocSwap/integer-mult-bounds/pull/412) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#413](https://github.com/CrocSwap/integer-mult-bounds/pull/413) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#414](https://github.com/CrocSwap/integer-mult-bounds/pull/414) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#415](https://github.com/CrocSwap/integer-mult-bounds/pull/415) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#416](https://github.com/CrocSwap/integer-mult-bounds/pull/416) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#417](https://github.com/CrocSwap/integer-mult-bounds/pull/417) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#418](https://github.com/CrocSwap/integer-mult-bounds/pull/418) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#419](https://github.com/CrocSwap/integer-mult-bounds/pull/419) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#420](https://github.com/CrocSwap/integer-mult-bounds/pull/420) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#421](https://github.com/CrocSwap/integer-mult-bounds/pull/421) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#422](https://github.com/CrocSwap/integer-mult-bounds/pull/422) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#423](https://github.com/CrocSwap/integer-mult-bounds/pull/423) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#424](https://github.com/CrocSwap/integer-mult-bounds/pull/424) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#425](https://github.com/CrocSwap/integer-mult-bounds/pull/425) | jacklightChen | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#426](https://github.com/CrocSwap/integer-mult-bounds/pull/426) | ai-nanachi | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#427](https://github.com/CrocSwap/integer-mult-bounds/pull/427) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#428](https://github.com/CrocSwap/integer-mult-bounds/pull/428) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#429](https://github.com/CrocSwap/integer-mult-bounds/pull/429) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#430](https://github.com/CrocSwap/integer-mult-bounds/pull/430) | artuskg | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#431](https://github.com/CrocSwap/integer-mult-bounds/pull/431) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#432](https://github.com/CrocSwap/integer-mult-bounds/pull/432) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#433](https://github.com/CrocSwap/integer-mult-bounds/pull/433) | icekylinx | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#434](https://github.com/CrocSwap/integer-mult-bounds/pull/434) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#435](https://github.com/CrocSwap/integer-mult-bounds/pull/435) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#436](https://github.com/CrocSwap/integer-mult-bounds/pull/436) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#437](https://github.com/CrocSwap/integer-mult-bounds/pull/437) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#438](https://github.com/CrocSwap/integer-mult-bounds/pull/438) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#439](https://github.com/CrocSwap/integer-mult-bounds/pull/439) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#440](https://github.com/CrocSwap/integer-mult-bounds/pull/440) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#441](https://github.com/CrocSwap/integer-mult-bounds/pull/441) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#442](https://github.com/CrocSwap/integer-mult-bounds/pull/442) | DaysSky | incorporated | [record 1](../../docs/research/community-formal-20261012-integration.json) · [record 2](../../docs/research/community-formal-20261012-review.md) |
| [#443](https://github.com/CrocSwap/integer-mult-bounds/pull/443) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#444](https://github.com/CrocSwap/integer-mult-bounds/pull/444) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#445](https://github.com/CrocSwap/integer-mult-bounds/pull/445) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#446](https://github.com/CrocSwap/integer-mult-bounds/pull/446) | DreamingOfClouds | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#447](https://github.com/CrocSwap/integer-mult-bounds/pull/447) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#448](https://github.com/CrocSwap/integer-mult-bounds/pull/448) | higherbeing | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#450](https://github.com/CrocSwap/integer-mult-bounds/pull/450) | DreamingOfClouds | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#451](https://github.com/CrocSwap/integer-mult-bounds/pull/451) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#452](https://github.com/CrocSwap/integer-mult-bounds/pull/452) | amanforindia | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#453](https://github.com/CrocSwap/integer-mult-bounds/pull/453) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#454](https://github.com/CrocSwap/integer-mult-bounds/pull/454) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#455](https://github.com/CrocSwap/integer-mult-bounds/pull/455) | Dugongue | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#456](https://github.com/CrocSwap/integer-mult-bounds/pull/456) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#457](https://github.com/CrocSwap/integer-mult-bounds/pull/457) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#458](https://github.com/CrocSwap/integer-mult-bounds/pull/458) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#459](https://github.com/CrocSwap/integer-mult-bounds/pull/459) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#460](https://github.com/CrocSwap/integer-mult-bounds/pull/460) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#461](https://github.com/CrocSwap/integer-mult-bounds/pull/461) | Srikrishnabalaji | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#462](https://github.com/CrocSwap/integer-mult-bounds/pull/462) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#463](https://github.com/CrocSwap/integer-mult-bounds/pull/463) | DreamingOfClouds | partially reviewed | [record 1](../../research/community-family533-audit/DISPOSITIONS.json) |
| [#464](https://github.com/CrocSwap/integer-mult-bounds/pull/464) | ahrazzle | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#465](https://github.com/CrocSwap/integer-mult-bounds/pull/465) | Srikrishnabalaji | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#466](https://github.com/CrocSwap/integer-mult-bounds/pull/466) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#467](https://github.com/CrocSwap/integer-mult-bounds/pull/467) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#469](https://github.com/CrocSwap/integer-mult-bounds/pull/469) | ahrazzle | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#470](https://github.com/CrocSwap/integer-mult-bounds/pull/470) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#471](https://github.com/CrocSwap/integer-mult-bounds/pull/471) | Dugongue | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#472](https://github.com/CrocSwap/integer-mult-bounds/pull/472) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#473](https://github.com/CrocSwap/integer-mult-bounds/pull/473) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#474](https://github.com/CrocSwap/integer-mult-bounds/pull/474) | artuskg | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#475](https://github.com/CrocSwap/integer-mult-bounds/pull/475) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#476](https://github.com/CrocSwap/integer-mult-bounds/pull/476) | Dugongue | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#478](https://github.com/CrocSwap/integer-mult-bounds/pull/478) | Dugongue | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#479](https://github.com/CrocSwap/integer-mult-bounds/pull/479) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#480](https://github.com/CrocSwap/integer-mult-bounds/pull/480) | higherbeing | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#481](https://github.com/CrocSwap/integer-mult-bounds/pull/481) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#482](https://github.com/CrocSwap/integer-mult-bounds/pull/482) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#483](https://github.com/CrocSwap/integer-mult-bounds/pull/483) | Dugongue | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#484](https://github.com/CrocSwap/integer-mult-bounds/pull/484) | DreamingOfClouds | incorporated | [record 1](../../docs/research/community-formal-20261012-integration.json) · [record 2](../../docs/research/community-formal-20261012-review.md) |
| [#485](https://github.com/CrocSwap/integer-mult-bounds/pull/485) | DreamingOfClouds | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#486](https://github.com/CrocSwap/integer-mult-bounds/pull/486) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#487](https://github.com/CrocSwap/integer-mult-bounds/pull/487) | jamesyc | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#488](https://github.com/CrocSwap/integer-mult-bounds/pull/488) | jamesyc | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#489](https://github.com/CrocSwap/integer-mult-bounds/pull/489) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#490](https://github.com/CrocSwap/integer-mult-bounds/pull/490) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#491](https://github.com/CrocSwap/integer-mult-bounds/pull/491) | M6LI | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#492](https://github.com/CrocSwap/integer-mult-bounds/pull/492) | Dugongue | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#494](https://github.com/CrocSwap/integer-mult-bounds/pull/494) | higherbeing | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#495](https://github.com/CrocSwap/integer-mult-bounds/pull/495) | aliromman | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#496](https://github.com/CrocSwap/integer-mult-bounds/pull/496) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#497](https://github.com/CrocSwap/integer-mult-bounds/pull/497) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#498](https://github.com/CrocSwap/integer-mult-bounds/pull/498) | Dugongue | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#499](https://github.com/CrocSwap/integer-mult-bounds/pull/499) | rosswaycaster | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#500](https://github.com/CrocSwap/integer-mult-bounds/pull/500) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#501](https://github.com/CrocSwap/integer-mult-bounds/pull/501) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#502](https://github.com/CrocSwap/integer-mult-bounds/pull/502) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#503](https://github.com/CrocSwap/integer-mult-bounds/pull/503) | DreamingOfClouds | incorporated | [record 1](../../research/community-family533-audit/DISPOSITIONS.json) |
| [#504](https://github.com/CrocSwap/integer-mult-bounds/pull/504) | DreamingOfClouds | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#505](https://github.com/CrocSwap/integer-mult-bounds/pull/505) | Dugongue | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#506](https://github.com/CrocSwap/integer-mult-bounds/pull/506) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#507](https://github.com/CrocSwap/integer-mult-bounds/pull/507) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#508](https://github.com/CrocSwap/integer-mult-bounds/pull/508) | Dugongue | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#509](https://github.com/CrocSwap/integer-mult-bounds/pull/509) | DreamingOfClouds | incorporated | [record 1](../../docs/research/community-formal-20261012-integration.json) · [record 2](../../docs/research/community-formal-20261012-review.md) |
| [#510](https://github.com/CrocSwap/integer-mult-bounds/pull/510) | DreamingOfClouds | incorporated | [record 1](../../research/community-family533-audit/DISPOSITIONS.json) |
| [#511](https://github.com/CrocSwap/integer-mult-bounds/pull/511) | jamesyc | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#512](https://github.com/CrocSwap/integer-mult-bounds/pull/512) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#513](https://github.com/CrocSwap/integer-mult-bounds/pull/513) | jamesyc | incorporated | [record 1](../../research/community-family533-audit/DISPOSITIONS.json) |
| [#515](https://github.com/CrocSwap/integer-mult-bounds/pull/515) | DreamingOfClouds | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#516](https://github.com/CrocSwap/integer-mult-bounds/pull/516) | DreamingOfClouds | incorporated | [record 1](../../docs/research/community-formal-20261012-integration.json) · [record 2](../../docs/research/community-formal-20261012-review.md) |
| [#517](https://github.com/CrocSwap/integer-mult-bounds/pull/517) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#518](https://github.com/CrocSwap/integer-mult-bounds/pull/518) | Dugongue | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#519](https://github.com/CrocSwap/integer-mult-bounds/pull/519) | jamesyc | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#520](https://github.com/CrocSwap/integer-mult-bounds/pull/520) | higherbeing | incorporated | [record 1](../../docs/research/community-formal-20261012-integration.json) · [record 2](../../docs/research/community-formal-20261012-review.md) |
| [#521](https://github.com/CrocSwap/integer-mult-bounds/pull/521) | applecrusher | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#522](https://github.com/CrocSwap/integer-mult-bounds/pull/522) | Dugongue | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#525](https://github.com/CrocSwap/integer-mult-bounds/pull/525) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#526](https://github.com/CrocSwap/integer-mult-bounds/pull/526) | jamesyc | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#527](https://github.com/CrocSwap/integer-mult-bounds/pull/527) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#528](https://github.com/CrocSwap/integer-mult-bounds/pull/528) | jamesyc | incorporated | [record 1](../../research/community-family533-audit/DISPOSITIONS.json) |
| [#529](https://github.com/CrocSwap/integer-mult-bounds/pull/529) | chafreaky | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#530](https://github.com/CrocSwap/integer-mult-bounds/pull/530) | jamesyc | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#532](https://github.com/CrocSwap/integer-mult-bounds/pull/532) | Dugongue | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#533](https://github.com/CrocSwap/integer-mult-bounds/pull/533) | chafreaky | incorporated | [record 1](../../research/community-family533-audit/DISPOSITIONS.json) |
| [#534](https://github.com/CrocSwap/integer-mult-bounds/pull/534) | rohanarun | incorporated | [record 1](../../research/community-family533-audit/DISPOSITIONS.json) |
| [#535](https://github.com/CrocSwap/integer-mult-bounds/pull/535) | icekylinx | incorporated | [record 1](../../research/community-family533-audit/DISPOSITIONS.json) |
| [#536](https://github.com/CrocSwap/integer-mult-bounds/pull/536) | rohanarun | incorporated | [record 1](../../research/community-family533-audit/DISPOSITIONS.json) |
| [#537](https://github.com/CrocSwap/integer-mult-bounds/pull/537) | Dugongue | incorporated | [record 1](../../research/community-family533-audit/DISPOSITIONS.json) |
| [#538](https://github.com/CrocSwap/integer-mult-bounds/pull/538) | chafreaky | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#539](https://github.com/CrocSwap/integer-mult-bounds/pull/539) | rohanarun | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#541](https://github.com/CrocSwap/integer-mult-bounds/pull/541) | Dugongue | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#542](https://github.com/CrocSwap/integer-mult-bounds/pull/542) | rohanarun | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#543](https://github.com/CrocSwap/integer-mult-bounds/pull/543) | eumemic | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#544](https://github.com/CrocSwap/integer-mult-bounds/pull/544) | chafreaky | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#545](https://github.com/CrocSwap/integer-mult-bounds/pull/545) | DreamingOfClouds | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#546](https://github.com/CrocSwap/integer-mult-bounds/pull/546) | rohanarun | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#547](https://github.com/CrocSwap/integer-mult-bounds/pull/547) | rohanarun | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#548](https://github.com/CrocSwap/integer-mult-bounds/pull/548) | Dugongue | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#549](https://github.com/CrocSwap/integer-mult-bounds/pull/549) | chafreaky | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#550](https://github.com/CrocSwap/integer-mult-bounds/pull/550) | eumemic | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#551](https://github.com/CrocSwap/integer-mult-bounds/pull/551) | chafreaky | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#552](https://github.com/CrocSwap/integer-mult-bounds/pull/552) | Dugongue | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#554](https://github.com/CrocSwap/integer-mult-bounds/pull/554) | rohanarun | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#555](https://github.com/CrocSwap/integer-mult-bounds/pull/555) | eumemic | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#556](https://github.com/CrocSwap/integer-mult-bounds/pull/556) | Dugongue | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#557](https://github.com/CrocSwap/integer-mult-bounds/pull/557) | chafreaky | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#558](https://github.com/CrocSwap/integer-mult-bounds/pull/558) | eumemic | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#559](https://github.com/CrocSwap/integer-mult-bounds/pull/559) | rohanarun | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#560](https://github.com/CrocSwap/integer-mult-bounds/pull/560) | Dugongue | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#561](https://github.com/CrocSwap/integer-mult-bounds/pull/561) | eumemic | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#562](https://github.com/CrocSwap/integer-mult-bounds/pull/562) | eumemic | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#563](https://github.com/CrocSwap/integer-mult-bounds/pull/563) | Dugongue | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#564](https://github.com/CrocSwap/integer-mult-bounds/pull/564) | eumemic | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#567](https://github.com/CrocSwap/integer-mult-bounds/pull/567) | jon314159 | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#568](https://github.com/CrocSwap/integer-mult-bounds/pull/568) | jeremykothe2 | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#569](https://github.com/CrocSwap/integer-mult-bounds/pull/569) | DominikScholz | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#571](https://github.com/CrocSwap/integer-mult-bounds/pull/571) | DominikScholz | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#572](https://github.com/CrocSwap/integer-mult-bounds/pull/572) | chafreaky | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#574](https://github.com/CrocSwap/integer-mult-bounds/pull/574) | jeremykothe2 | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#575](https://github.com/CrocSwap/integer-mult-bounds/pull/575) | jon314159 | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#576](https://github.com/CrocSwap/integer-mult-bounds/pull/576) | jeremykothe2 | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#577](https://github.com/CrocSwap/integer-mult-bounds/pull/577) | chafreaky | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#578](https://github.com/CrocSwap/integer-mult-bounds/pull/578) | jeremykothe2 | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#579](https://github.com/CrocSwap/integer-mult-bounds/pull/579) | chafreaky | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#580](https://github.com/CrocSwap/integer-mult-bounds/pull/580) | artuskg | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#582](https://github.com/CrocSwap/integer-mult-bounds/pull/582) | jeremykothe2 | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#583](https://github.com/CrocSwap/integer-mult-bounds/pull/583) | chafreaky | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#584](https://github.com/CrocSwap/integer-mult-bounds/pull/584) | jeremykothe2 | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#586](https://github.com/CrocSwap/integer-mult-bounds/pull/586) | chafreaky | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#587](https://github.com/CrocSwap/integer-mult-bounds/pull/587) | jeremykothe2 | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#588](https://github.com/CrocSwap/integer-mult-bounds/pull/588) | jeremykothe2 | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#589](https://github.com/CrocSwap/integer-mult-bounds/pull/589) | DreamingOfClouds | incorporated | [record 1](../../research/community-hyperplane599-audit/DISPOSITIONS.json) |
| [#591](https://github.com/CrocSwap/integer-mult-bounds/pull/591) | jeremykothe2 | incorporated | [record 1](../../research/community-hyperplane599-audit/DISPOSITIONS.json) |
| [#592](https://github.com/CrocSwap/integer-mult-bounds/pull/592) | jeremykothe2 | incorporated | [record 1](../../research/community-hyperplane599-audit/DISPOSITIONS.json) |
| [#593](https://github.com/CrocSwap/integer-mult-bounds/pull/593) | jeremykothe2 | incorporated | [record 1](../../research/community-hyperplane599-audit/DISPOSITIONS.json) |
| [#594](https://github.com/CrocSwap/integer-mult-bounds/pull/594) | eumemic | partially reviewed | [record 1](../../research/community-hyperplane599-audit/DISPOSITIONS.json) |
| [#595](https://github.com/CrocSwap/integer-mult-bounds/pull/595) | DreamingOfClouds | incorporated | [record 1](../../research/community-hyperplane599-audit/DISPOSITIONS.json) |
| [#596](https://github.com/CrocSwap/integer-mult-bounds/pull/596) | jeremykothe2 | incorporated | [record 1](../../research/community-hyperplane599-audit/DISPOSITIONS.json) |
| [#598](https://github.com/CrocSwap/integer-mult-bounds/pull/598) | DominikScholz | incorporated | [record 1](../../research/community-hyperplane599-audit/DISPOSITIONS.json) |
| [#599](https://github.com/CrocSwap/integer-mult-bounds/pull/599) | DreamingOfClouds | incorporated | [record 1](../../research/community-hyperplane599-audit/DISPOSITIONS.json) |
| [#600](https://github.com/CrocSwap/integer-mult-bounds/pull/600) | jeremykothe2 | incorporated | [record 1](../../research/community-cold617-audit/DISPOSITIONS.json) |
| [#601](https://github.com/CrocSwap/integer-mult-bounds/pull/601) | jeremykothe2 | incorporated | [record 1](../../research/community-cold617-audit/DISPOSITIONS.json) |
| [#602](https://github.com/CrocSwap/integer-mult-bounds/pull/602) | artuskg | incorporated | [record 1](../../research/community-cold617-audit/DISPOSITIONS.json) |
| [#603](https://github.com/CrocSwap/integer-mult-bounds/pull/603) | jeremykothe2 | incorporated | [record 1](../../research/community-cold617-audit/DISPOSITIONS.json) |
| [#604](https://github.com/CrocSwap/integer-mult-bounds/pull/604) | DreamingOfClouds | incorporated | [record 1](../../research/community-cold617-audit/DISPOSITIONS.json) |
| [#605](https://github.com/CrocSwap/integer-mult-bounds/pull/605) | jamesyc | partially reviewed | [record 1](../../research/community-cold617-audit/DISPOSITIONS.json) |
| [#606](https://github.com/CrocSwap/integer-mult-bounds/pull/606) | DominikScholz | incorporated | [record 1](../../research/community-cold617-audit/DISPOSITIONS.json) |
| [#607](https://github.com/CrocSwap/integer-mult-bounds/pull/607) | jeremykothe2 | incorporated | [record 1](../../research/community-cold617-audit/DISPOSITIONS.json) |
| [#608](https://github.com/CrocSwap/integer-mult-bounds/pull/608) | higherbeing | incorporated | [record 1](../../research/community-cold617-audit/DISPOSITIONS.json) |
| [#609](https://github.com/CrocSwap/integer-mult-bounds/pull/609) | jeremykothe2 | incorporated | [record 1](../../research/community-cold617-audit/DISPOSITIONS.json) |
| [#610](https://github.com/CrocSwap/integer-mult-bounds/pull/610) | DreamingOfClouds | incorporated | [record 1](../../research/community-cold617-audit/DISPOSITIONS.json) |
| [#611](https://github.com/CrocSwap/integer-mult-bounds/pull/611) | eumemic | partially reviewed | [record 1](../../research/community-cold617-audit/DISPOSITIONS.json) |
| [#612](https://github.com/CrocSwap/integer-mult-bounds/pull/612) | jamesyc | partially reviewed | [record 1](../../research/community-cold617-audit/DISPOSITIONS.json) |
| [#613](https://github.com/CrocSwap/integer-mult-bounds/pull/613) | eumemic | incorporated | [record 1](../../research/community-cold617-audit/DISPOSITIONS.json) |
| [#614](https://github.com/CrocSwap/integer-mult-bounds/pull/614) | jeremykothe2 | incorporated | [record 1](../../research/community-cold617-audit/DISPOSITIONS.json) |
| [#615](https://github.com/CrocSwap/integer-mult-bounds/pull/615) | jeremykothe2 | incorporated | [record 1](../../research/community-cold617-audit/DISPOSITIONS.json) |
| [#616](https://github.com/CrocSwap/integer-mult-bounds/pull/616) | chafreaky | incorporated | [record 1](../../research/community-cold617-audit/DISPOSITIONS.json) |
| [#617](https://github.com/CrocSwap/integer-mult-bounds/pull/617) | jeremykothe2 | incorporated | [record 1](../../research/community-cold617-audit/DISPOSITIONS.json) |
| [#618](https://github.com/CrocSwap/integer-mult-bounds/pull/618) | jeremydiviney | incorporated | [record 1](../../research/community-k492-audit/DISPOSITIONS.json) |
| [#619](https://github.com/CrocSwap/integer-mult-bounds/pull/619) | chafreaky | incorporated | [record 1](../../research/community-k492-audit/DISPOSITIONS.json) |
| [#620](https://github.com/CrocSwap/integer-mult-bounds/pull/620) | GamingPuzzled | partially reviewed | [record 1](../../research/community-k492-audit/DISPOSITIONS.json) |
| [#621](https://github.com/CrocSwap/integer-mult-bounds/pull/621) | aliromman | incorporated | [record 1](../../research/community-k492-audit/DISPOSITIONS.json) |
| [#622](https://github.com/CrocSwap/integer-mult-bounds/pull/622) | jeremykothe2 | incorporated | [record 1](../../research/community-k492-audit/DISPOSITIONS.json) |
| [#623](https://github.com/CrocSwap/integer-mult-bounds/pull/623) | jeremykothe2 | incorporated | [record 1](../../research/community-k492-audit/DISPOSITIONS.json) |
| [#624](https://github.com/CrocSwap/integer-mult-bounds/pull/624) | jeremydiviney | incorporated | [record 1](../../research/community-k492-audit/DISPOSITIONS.json) |
| [#625](https://github.com/CrocSwap/integer-mult-bounds/pull/625) | jeremykothe2 | incorporated | [record 1](../../research/community-k492-audit/DISPOSITIONS.json) |
| [#626](https://github.com/CrocSwap/integer-mult-bounds/pull/626) | chafreaky | incorporated | [record 1](../../research/community-k492-audit/DISPOSITIONS.json) |
| [#675](https://github.com/CrocSwap/integer-mult-bounds/pull/675) | tekuuu | incorporated | [record 1](../../research/community-frontier741-audit/DISPOSITIONS.json) |
| [#681](https://github.com/CrocSwap/integer-mult-bounds/pull/681) | alluri-ritual | incorporated | [record 1](../../research/community-frontier741-audit/DISPOSITIONS.json) |
| [#695](https://github.com/CrocSwap/integer-mult-bounds/pull/695) | jsnider3 | incorporated | [record 1](../../research/community-frontier741-audit/DISPOSITIONS.json) |
| [#704](https://github.com/CrocSwap/integer-mult-bounds/pull/704) | roife | incorporated | [record 1](../../research/community-frontier741-audit/DISPOSITIONS.json) |
| [#740](https://github.com/CrocSwap/integer-mult-bounds/pull/740) | azide0x37 | incorporated | [record 1](../../research/community-frontier741-audit/DISPOSITIONS.json) |
| [#741](https://github.com/CrocSwap/integer-mult-bounds/pull/741) | chafreaky | incorporated | [record 1](../../research/community-frontier741-audit/DISPOSITIONS.json) |
| [#777](https://github.com/CrocSwap/integer-mult-bounds/pull/777) | tekuuu | partially reviewed | [record 1](../../research/community-frontier741-audit/DISPOSITIONS.json) |
