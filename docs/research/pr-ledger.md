# PR review and integration ledger

The immutable starting snapshot contains **446 PRs**. Explicit later family rounds extend the current inventory to **1865**; unrelated arrivals remain outside the round.

[Machine-readable ledger](pr-ledger.json) · [Starting snapshot](../../research/pr-reconciliation-20261012/starting-snapshot.json)

The ledger separates historical review from integration. A prior snapshot or a mention in a note does not certify a contribution. “Partially reviewed” includes scoped review and triage with their original limitations; “changed since review” means the present head lacks matching recorded coverage. Archived incorporation preserves a historical implementation and attribution without making it the selected result.

| Disposition | Count |
|---|---:|
| incorporated | 1540 |
| partially reviewed | 264 |
| superseded | 1 |
| unreviewed | 60 |

The earlier reconciliation closing snapshot had 438 starting PRs still open and 441 total open. These are historical counts, not a live queue measurement. Later dispositions are recorded below.

[Earlier family review](community-family533-review.md) · [Earlier dispositions](../../research/community-family533-audit/DISPOSITIONS.json)

The earlier construction family #533–#537 and formal connections #513/#528 are covered there, including the #503/#510 bit dependency. #463 has only its vendored pipeline subset reviewed.

[Family through #588](community-family588-review.md) · [Exact-head dispositions](../../research/community-family588-audit/DISPOSITIONS.json)

This frozen round covers #543/#545/#555 and related construction, research and tooling packages through #588. Each disposition distinguishes completed checks, publication and remaining obligations. The separate formalization PRs and later arrivals are not approved by this round.

[100-PR historical reconciliation](community-reconciliation100-review.md): exact-head coverage and individual carry-forward tasks; it is not 100 completed mathematical audits.
[Five early contributions](community-historical-five-review.md): #2/#4/#8/#9/#12 retained with complete historical sources and focused replays.
[Remaining 92 contributions](community-reconciliation92-review.md): source retention, scoped review and closure receipts; #122 awaits its missing parent circuit/profile.
[Previous 100 contributions, #153–#303](community-reconciliation-next100-review.md): individual scope and explicit remaining obligations.
[Third 100 contributions, #304–#421](community-reconciliation-third100-review.md): constructions, research and verification with source-bound execution.
[Fourth 100 contributions, #423–#668](community-reconciliation-fourth100-review.md): full-source reconciliation and scoped execution, with blockers retained.

## Remaining priorities

1. Resolve the explicit remaining questions on partially reviewed or changed heads; consult the latest family disposition before repeating a replay.
2. Continue with a frozen chunk of live, non-draft, unreviewed PRs. Compare current heads with published reviews and exclude submissions awaiting a concrete revision.
3. Keep source retention, scoped execution, publication and actual GitHub closure separate. Preserve research, verification and parallel contribution credit even when a result is superseded.
4. Build formal connections to the actual finite constructions; abstract theorem builds alone do not instantiate the selected multiplication algorithm.

## Starting PR inventory

Each evidence link leads to the original scoped assessment. The JSON records exact heads, unresolved questions, integration locations and closure receipts.

| PR | Contributor | Disposition | Evidence or remaining question |
|---|---|---|---|
| [#1](https://github.com/CrocSwap/integer-mult-bounds/pull/1) | Paureel | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#2](https://github.com/CrocSwap/integer-mult-bounds/pull/2) | Bortlesboat | incorporated | [record 1](../../research/community-historical-five-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#3](https://github.com/CrocSwap/integer-mult-bounds/pull/3) | eumemic | incorporated | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) · [record 2](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#4](https://github.com/CrocSwap/integer-mult-bounds/pull/4) | dleen | incorporated | [record 1](../../research/community-historical-five-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#5](https://github.com/CrocSwap/integer-mult-bounds/pull/5) | eumemic | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#6](https://github.com/CrocSwap/integer-mult-bounds/pull/6) | eumemic | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#7](https://github.com/CrocSwap/integer-mult-bounds/pull/7) | jacklightChen | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#8](https://github.com/CrocSwap/integer-mult-bounds/pull/8) | rohanarun | incorporated | [record 1](../../research/community-historical-five-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#9](https://github.com/CrocSwap/integer-mult-bounds/pull/9) | rohanarun | incorporated | [record 1](../../research/community-historical-five-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#12](https://github.com/CrocSwap/integer-mult-bounds/pull/12) | rohanarun | incorporated | [record 1](../../research/community-historical-five-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#13](https://github.com/CrocSwap/integer-mult-bounds/pull/13) | eumemic | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#14](https://github.com/CrocSwap/integer-mult-bounds/pull/14) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#15](https://github.com/CrocSwap/integer-mult-bounds/pull/15) | eumemic | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#16](https://github.com/CrocSwap/integer-mult-bounds/pull/16) | jacklightChen | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#17](https://github.com/CrocSwap/integer-mult-bounds/pull/17) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#19](https://github.com/CrocSwap/integer-mult-bounds/pull/19) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#20](https://github.com/CrocSwap/integer-mult-bounds/pull/20) | hipotures | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#21](https://github.com/CrocSwap/integer-mult-bounds/pull/21) | jacklightChen | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#22](https://github.com/CrocSwap/integer-mult-bounds/pull/22) | DominikScholz | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#23](https://github.com/CrocSwap/integer-mult-bounds/pull/23) | jacklightChen | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#25](https://github.com/CrocSwap/integer-mult-bounds/pull/25) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#27](https://github.com/CrocSwap/integer-mult-bounds/pull/27) | DominikScholz | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#28](https://github.com/CrocSwap/integer-mult-bounds/pull/28) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#29](https://github.com/CrocSwap/integer-mult-bounds/pull/29) | jacklightChen | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#31](https://github.com/CrocSwap/integer-mult-bounds/pull/31) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#33](https://github.com/CrocSwap/integer-mult-bounds/pull/33) | DominikScholz | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#34](https://github.com/CrocSwap/integer-mult-bounds/pull/34) | jamesyc | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#35](https://github.com/CrocSwap/integer-mult-bounds/pull/35) | DominikScholz | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#38](https://github.com/CrocSwap/integer-mult-bounds/pull/38) | DominikScholz | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#40](https://github.com/CrocSwap/integer-mult-bounds/pull/40) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#41](https://github.com/CrocSwap/integer-mult-bounds/pull/41) | hipotures | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#42](https://github.com/CrocSwap/integer-mult-bounds/pull/42) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#44](https://github.com/CrocSwap/integer-mult-bounds/pull/44) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#47](https://github.com/CrocSwap/integer-mult-bounds/pull/47) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#63](https://github.com/CrocSwap/integer-mult-bounds/pull/63) | DominikScholz | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#65](https://github.com/CrocSwap/integer-mult-bounds/pull/65) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#66](https://github.com/CrocSwap/integer-mult-bounds/pull/66) | chafreaky | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#67](https://github.com/CrocSwap/integer-mult-bounds/pull/67) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#68](https://github.com/CrocSwap/integer-mult-bounds/pull/68) | DominikScholz | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#69](https://github.com/CrocSwap/integer-mult-bounds/pull/69) | eumemic | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#70](https://github.com/CrocSwap/integer-mult-bounds/pull/70) | alejandrozu | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#71](https://github.com/CrocSwap/integer-mult-bounds/pull/71) | chafreaky | incorporated | [record 1](../../docs/research/community-round3-validation.json) · [record 2](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 3](../../research/overnight-pr-review-20261009/dispositions.json) · [record 4](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#74](https://github.com/CrocSwap/integer-mult-bounds/pull/74) | tomdif | partially reviewed | [record 1](../../docs/research/community-round3-validation.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#75](https://github.com/CrocSwap/integer-mult-bounds/pull/75) | alejandrozu | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#76](https://github.com/CrocSwap/integer-mult-bounds/pull/76) | DominikScholz | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#77](https://github.com/CrocSwap/integer-mult-bounds/pull/77) | huxint | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#78](https://github.com/CrocSwap/integer-mult-bounds/pull/78) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#79](https://github.com/CrocSwap/integer-mult-bounds/pull/79) | chafreaky | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#80](https://github.com/CrocSwap/integer-mult-bounds/pull/80) | rohanarun | incorporated | [record 1](../../docs/research/community-round3-validation.json) · [record 2](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 3](../../research/overnight-pr-review-20261009/dispositions.json) · [record 4](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#81](https://github.com/CrocSwap/integer-mult-bounds/pull/81) | DominikScholz | incorporated | [record 1](../../docs/research/community-round4-validation.json) · [record 2](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 3](../../research/overnight-pr-review-20261009/dispositions.json) · [record 4](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#82](https://github.com/CrocSwap/integer-mult-bounds/pull/82) | rohanarun | incorporated | [record 1](../../docs/research/community-round4-validation.json) · [record 2](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 3](../../research/overnight-pr-review-20261009/dispositions.json) · [record 4](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#83](https://github.com/CrocSwap/integer-mult-bounds/pull/83) | JosephDemarest | incorporated | [record 1](../../docs/research/community-round4-validation.json) · [record 2](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 3](../../research/overnight-pr-review-20261009/dispositions.json) · [record 4](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#84](https://github.com/CrocSwap/integer-mult-bounds/pull/84) | chafreaky | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#85](https://github.com/CrocSwap/integer-mult-bounds/pull/85) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#86](https://github.com/CrocSwap/integer-mult-bounds/pull/86) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#87](https://github.com/CrocSwap/integer-mult-bounds/pull/87) | gupt1156 | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#88](https://github.com/CrocSwap/integer-mult-bounds/pull/88) | chafreaky | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#89](https://github.com/CrocSwap/integer-mult-bounds/pull/89) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#90](https://github.com/CrocSwap/integer-mult-bounds/pull/90) | anxkhn | superseded | [record 1](../../docs/research/community-round5-validation.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#91](https://github.com/CrocSwap/integer-mult-bounds/pull/91) | chafreaky | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#92](https://github.com/CrocSwap/integer-mult-bounds/pull/92) | maxime-fleury | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#93](https://github.com/CrocSwap/integer-mult-bounds/pull/93) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#94](https://github.com/CrocSwap/integer-mult-bounds/pull/94) | maxime-fleury | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#95](https://github.com/CrocSwap/integer-mult-bounds/pull/95) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#97](https://github.com/CrocSwap/integer-mult-bounds/pull/97) | jacklightChen | incorporated | [record 1](../../docs/research/community-round5-validation.json) · [record 2](../../docs/research/community-round6-validation.json) · [record 3](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 4](../../research/overnight-pr-review-20261009/dispositions.json) · [record 5](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#98](https://github.com/CrocSwap/integer-mult-bounds/pull/98) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#99](https://github.com/CrocSwap/integer-mult-bounds/pull/99) | djsmanchanda | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#100](https://github.com/CrocSwap/integer-mult-bounds/pull/100) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#102](https://github.com/CrocSwap/integer-mult-bounds/pull/102) | SovereignSteak | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#103](https://github.com/CrocSwap/integer-mult-bounds/pull/103) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#106](https://github.com/CrocSwap/integer-mult-bounds/pull/106) | Th0rgal | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#107](https://github.com/CrocSwap/integer-mult-bounds/pull/107) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#108](https://github.com/CrocSwap/integer-mult-bounds/pull/108) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#109](https://github.com/CrocSwap/integer-mult-bounds/pull/109) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#110](https://github.com/CrocSwap/integer-mult-bounds/pull/110) | ikeboy | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#111](https://github.com/CrocSwap/integer-mult-bounds/pull/111) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#113](https://github.com/CrocSwap/integer-mult-bounds/pull/113) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#114](https://github.com/CrocSwap/integer-mult-bounds/pull/114) | eumemic | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#116](https://github.com/CrocSwap/integer-mult-bounds/pull/116) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#117](https://github.com/CrocSwap/integer-mult-bounds/pull/117) | eumemic | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#118](https://github.com/CrocSwap/integer-mult-bounds/pull/118) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#121](https://github.com/CrocSwap/integer-mult-bounds/pull/121) | Th0rgal | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#122](https://github.com/CrocSwap/integer-mult-bounds/pull/122) | SovereignSteak | partially reviewed | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#123](https://github.com/CrocSwap/integer-mult-bounds/pull/123) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#124](https://github.com/CrocSwap/integer-mult-bounds/pull/124) | jamesyc | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#125](https://github.com/CrocSwap/integer-mult-bounds/pull/125) | GamingPuzzled | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#126](https://github.com/CrocSwap/integer-mult-bounds/pull/126) | DanieleCorso | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#127](https://github.com/CrocSwap/integer-mult-bounds/pull/127) | GamingPuzzled | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#128](https://github.com/CrocSwap/integer-mult-bounds/pull/128) | an664 | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#129](https://github.com/CrocSwap/integer-mult-bounds/pull/129) | eumemic | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#131](https://github.com/CrocSwap/integer-mult-bounds/pull/131) | eumemic | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#133](https://github.com/CrocSwap/integer-mult-bounds/pull/133) | Th0rgal | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#135](https://github.com/CrocSwap/integer-mult-bounds/pull/135) | DanieleCorso | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) |
| [#137](https://github.com/CrocSwap/integer-mult-bounds/pull/137) | eumemic | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#138](https://github.com/CrocSwap/integer-mult-bounds/pull/138) | geckods | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#141](https://github.com/CrocSwap/integer-mult-bounds/pull/141) | chafreaky | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#142](https://github.com/CrocSwap/integer-mult-bounds/pull/142) | eumemic | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#143](https://github.com/CrocSwap/integer-mult-bounds/pull/143) | eumemic | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#145](https://github.com/CrocSwap/integer-mult-bounds/pull/145) | Th0rgal | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#146](https://github.com/CrocSwap/integer-mult-bounds/pull/146) | Th0rgal | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) · [record 4](../../research/pr-reconciliation-20261012/content-comparison.json) |
| [#148](https://github.com/CrocSwap/integer-mult-bounds/pull/148) | gupt1156 | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) · [record 2](../../research/pr-reconciliation-20261012/content-comparison.json) |
| [#153](https://github.com/CrocSwap/integer-mult-bounds/pull/153) | geckods | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#154](https://github.com/CrocSwap/integer-mult-bounds/pull/154) | eumemic | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/community-round8-audit/validation.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#158](https://github.com/CrocSwap/integer-mult-bounds/pull/158) | geckods | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#160](https://github.com/CrocSwap/integer-mult-bounds/pull/160) | GamingPuzzled | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#162](https://github.com/CrocSwap/integer-mult-bounds/pull/162) | DaysSky | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#163](https://github.com/CrocSwap/integer-mult-bounds/pull/163) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#164](https://github.com/CrocSwap/integer-mult-bounds/pull/164) | eumemic | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#165](https://github.com/CrocSwap/integer-mult-bounds/pull/165) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#166](https://github.com/CrocSwap/integer-mult-bounds/pull/166) | jamesyc | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#167](https://github.com/CrocSwap/integer-mult-bounds/pull/167) | GamingPuzzled | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#168](https://github.com/CrocSwap/integer-mult-bounds/pull/168) | eumemic | incorporated | [record 1](../../research/community-round8-audit/validation.json) · [record 2](../../research/pr-reconciliation-20261012/incorporation-checks.json) |
| [#169](https://github.com/CrocSwap/integer-mult-bounds/pull/169) | GamingPuzzled | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#170](https://github.com/CrocSwap/integer-mult-bounds/pull/170) | huxint | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#171](https://github.com/CrocSwap/integer-mult-bounds/pull/171) | jon314159 | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#172](https://github.com/CrocSwap/integer-mult-bounds/pull/172) | mikey1201 | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#173](https://github.com/CrocSwap/integer-mult-bounds/pull/173) | GamingPuzzled | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#174](https://github.com/CrocSwap/integer-mult-bounds/pull/174) | TeS44 | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#175](https://github.com/CrocSwap/integer-mult-bounds/pull/175) | chafreaky | incorporated | [record 1](../../research/community-round8-audit/validation.json) · [record 2](../../research/pr-reconciliation-20261012/incorporation-checks.json) |
| [#177](https://github.com/CrocSwap/integer-mult-bounds/pull/177) | gabriele-nespoli | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#178](https://github.com/CrocSwap/integer-mult-bounds/pull/178) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#179](https://github.com/CrocSwap/integer-mult-bounds/pull/179) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#180](https://github.com/CrocSwap/integer-mult-bounds/pull/180) | M6LI | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#181](https://github.com/CrocSwap/integer-mult-bounds/pull/181) | chafreaky | incorporated | [record 1](../../research/community-round8-audit/validation.json) · [record 2](../../research/pr-reconciliation-20261012/incorporation-checks.json) |
| [#182](https://github.com/CrocSwap/integer-mult-bounds/pull/182) | chafreaky | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/community-round8-audit/validation.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) · [record 4](../../research/pr-reconciliation-20261012/content-comparison.json) |
| [#183](https://github.com/CrocSwap/integer-mult-bounds/pull/183) | romainhedouin | incorporated | [record 1](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) · [record 2](../../research/pr-reconciliation-20261012/content-comparison.json) |
| [#185](https://github.com/CrocSwap/integer-mult-bounds/pull/185) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/community-round8-audit/validation.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) · [record 4](../../research/pr-reconciliation-20261012/content-comparison.json) |
| [#187](https://github.com/CrocSwap/integer-mult-bounds/pull/187) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#188](https://github.com/CrocSwap/integer-mult-bounds/pull/188) | huxint | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#189](https://github.com/CrocSwap/integer-mult-bounds/pull/189) | chafreaky | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#191](https://github.com/CrocSwap/integer-mult-bounds/pull/191) | ikeboy | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#192](https://github.com/CrocSwap/integer-mult-bounds/pull/192) | DaysSky | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#193](https://github.com/CrocSwap/integer-mult-bounds/pull/193) | ikeboy | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#194](https://github.com/CrocSwap/integer-mult-bounds/pull/194) | ikeboy | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#195](https://github.com/CrocSwap/integer-mult-bounds/pull/195) | huxint | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#196](https://github.com/CrocSwap/integer-mult-bounds/pull/196) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#197](https://github.com/CrocSwap/integer-mult-bounds/pull/197) | evmckinney9 | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#199](https://github.com/CrocSwap/integer-mult-bounds/pull/199) | maxime-fleury | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#200](https://github.com/CrocSwap/integer-mult-bounds/pull/200) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#201](https://github.com/CrocSwap/integer-mult-bounds/pull/201) | DaysSky | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#202](https://github.com/CrocSwap/integer-mult-bounds/pull/202) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#203](https://github.com/CrocSwap/integer-mult-bounds/pull/203) | huxint | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#204](https://github.com/CrocSwap/integer-mult-bounds/pull/204) | maxime-fleury | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#205](https://github.com/CrocSwap/integer-mult-bounds/pull/205) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#207](https://github.com/CrocSwap/integer-mult-bounds/pull/207) | Dugongue | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#208](https://github.com/CrocSwap/integer-mult-bounds/pull/208) | maxime-fleury | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#210](https://github.com/CrocSwap/integer-mult-bounds/pull/210) | eumemic | incorporated | [record 1](../../docs/research/community-pr210-integration.json) · [record 2](../../research/community-batch970-audit/COMPANION-REVIEWS.json) · [record 3](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 4](../../research/community-round9-audit/review-ledger.json) · [record 5](../../research/pr-reconciliation-20261012/content-comparison.json) |
| [#211](https://github.com/CrocSwap/integer-mult-bounds/pull/211) | rohanarun | partially reviewed | [record 1](../../research/community-round9-audit/review-ledger.json) |
| [#212](https://github.com/CrocSwap/integer-mult-bounds/pull/212) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#214](https://github.com/CrocSwap/integer-mult-bounds/pull/214) | antoine-olivier | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#215](https://github.com/CrocSwap/integer-mult-bounds/pull/215) | GamingPuzzled | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#216](https://github.com/CrocSwap/integer-mult-bounds/pull/216) | Dugongue | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#217](https://github.com/CrocSwap/integer-mult-bounds/pull/217) | hcg890 | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#221](https://github.com/CrocSwap/integer-mult-bounds/pull/221) | maxime-fleury | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#223](https://github.com/CrocSwap/integer-mult-bounds/pull/223) | ikeboy | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#224](https://github.com/CrocSwap/integer-mult-bounds/pull/224) | maxime-fleury | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#225](https://github.com/CrocSwap/integer-mult-bounds/pull/225) | chafreaky | incorporated | [record 1](../../research/community-efficient300-audit/PARENT-EVIDENCE.json) · [record 2](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 3](../../research/community-round9-audit/review-ledger.json) |
| [#226](https://github.com/CrocSwap/integer-mult-bounds/pull/226) | pCwOrM | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#227](https://github.com/CrocSwap/integer-mult-bounds/pull/227) | Dugongue | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#228](https://github.com/CrocSwap/integer-mult-bounds/pull/228) | tehruhn | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#229](https://github.com/CrocSwap/integer-mult-bounds/pull/229) | maxime-fleury | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#233](https://github.com/CrocSwap/integer-mult-bounds/pull/233) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#234](https://github.com/CrocSwap/integer-mult-bounds/pull/234) | hcg890 | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#235](https://github.com/CrocSwap/integer-mult-bounds/pull/235) | gabriele-nespoli | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#236](https://github.com/CrocSwap/integer-mult-bounds/pull/236) | jamesyc | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#237](https://github.com/CrocSwap/integer-mult-bounds/pull/237) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#240](https://github.com/CrocSwap/integer-mult-bounds/pull/240) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 2](../../research/community-round9-audit/review-ledger.json) |
| [#241](https://github.com/CrocSwap/integer-mult-bounds/pull/241) | maxime-fleury | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#242](https://github.com/CrocSwap/integer-mult-bounds/pull/242) | Dugongue | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#243](https://github.com/CrocSwap/integer-mult-bounds/pull/243) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#244](https://github.com/CrocSwap/integer-mult-bounds/pull/244) | eumemic | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#245](https://github.com/CrocSwap/integer-mult-bounds/pull/245) | sandersdavid90-droid | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#248](https://github.com/CrocSwap/integer-mult-bounds/pull/248) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#249](https://github.com/CrocSwap/integer-mult-bounds/pull/249) | eumemic | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#250](https://github.com/CrocSwap/integer-mult-bounds/pull/250) | SovereignSteak | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#251](https://github.com/CrocSwap/integer-mult-bounds/pull/251) | eumemic | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#252](https://github.com/CrocSwap/integer-mult-bounds/pull/252) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#254](https://github.com/CrocSwap/integer-mult-bounds/pull/254) | Dugongue | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#255](https://github.com/CrocSwap/integer-mult-bounds/pull/255) | hvaliconAI | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#256](https://github.com/CrocSwap/integer-mult-bounds/pull/256) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#258](https://github.com/CrocSwap/integer-mult-bounds/pull/258) | amanforindia | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#259](https://github.com/CrocSwap/integer-mult-bounds/pull/259) | Dugongue | partially reviewed | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#260](https://github.com/CrocSwap/integer-mult-bounds/pull/260) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#261](https://github.com/CrocSwap/integer-mult-bounds/pull/261) | sennemmi | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#262](https://github.com/CrocSwap/integer-mult-bounds/pull/262) | maxime-fleury | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#263](https://github.com/CrocSwap/integer-mult-bounds/pull/263) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#264](https://github.com/CrocSwap/integer-mult-bounds/pull/264) | dataisfire | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#265](https://github.com/CrocSwap/integer-mult-bounds/pull/265) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#266](https://github.com/CrocSwap/integer-mult-bounds/pull/266) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#267](https://github.com/CrocSwap/integer-mult-bounds/pull/267) | Dugongue | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#268](https://github.com/CrocSwap/integer-mult-bounds/pull/268) | eumemic | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#269](https://github.com/CrocSwap/integer-mult-bounds/pull/269) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#270](https://github.com/CrocSwap/integer-mult-bounds/pull/270) | utcorvusvolat-dotcom | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#271](https://github.com/CrocSwap/integer-mult-bounds/pull/271) | evmckinney9 | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#272](https://github.com/CrocSwap/integer-mult-bounds/pull/272) | Dugongue | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#273](https://github.com/CrocSwap/integer-mult-bounds/pull/273) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#274](https://github.com/CrocSwap/integer-mult-bounds/pull/274) | shea256 | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#275](https://github.com/CrocSwap/integer-mult-bounds/pull/275) | lydakis | partially reviewed | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#277](https://github.com/CrocSwap/integer-mult-bounds/pull/277) | hcg890 | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#278](https://github.com/CrocSwap/integer-mult-bounds/pull/278) | hcg890 | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#279](https://github.com/CrocSwap/integer-mult-bounds/pull/279) | rohanarun | incorporated | [record 1](../../docs/research/community-pr279-integration.json) · [record 2](../../research/community-batch970-audit/COMPANION-REVIEWS.json) · [record 3](../../research/community-efficient300-audit/PARENT-EVIDENCE.json) · [record 4](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 5](../../research/pr-reconciliation-20261012/content-comparison.json) |
| [#280](https://github.com/CrocSwap/integer-mult-bounds/pull/280) | utcorvusvolat-dotcom | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#281](https://github.com/CrocSwap/integer-mult-bounds/pull/281) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#282](https://github.com/CrocSwap/integer-mult-bounds/pull/282) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#283](https://github.com/CrocSwap/integer-mult-bounds/pull/283) | Dugongue | partially reviewed | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#284](https://github.com/CrocSwap/integer-mult-bounds/pull/284) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#285](https://github.com/CrocSwap/integer-mult-bounds/pull/285) | DreamingOfClouds | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#286](https://github.com/CrocSwap/integer-mult-bounds/pull/286) | GamingPuzzled | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#287](https://github.com/CrocSwap/integer-mult-bounds/pull/287) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#288](https://github.com/CrocSwap/integer-mult-bounds/pull/288) | eumemic | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#289](https://github.com/CrocSwap/integer-mult-bounds/pull/289) | gupt1156 | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#290](https://github.com/CrocSwap/integer-mult-bounds/pull/290) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#291](https://github.com/CrocSwap/integer-mult-bounds/pull/291) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#292](https://github.com/CrocSwap/integer-mult-bounds/pull/292) | sannidhi-hemanth | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#293](https://github.com/CrocSwap/integer-mult-bounds/pull/293) | jacklightChen | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#294](https://github.com/CrocSwap/integer-mult-bounds/pull/294) | maximussthegreat | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#295](https://github.com/CrocSwap/integer-mult-bounds/pull/295) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#296](https://github.com/CrocSwap/integer-mult-bounds/pull/296) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#297](https://github.com/CrocSwap/integer-mult-bounds/pull/297) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#298](https://github.com/CrocSwap/integer-mult-bounds/pull/298) | M6LI | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#299](https://github.com/CrocSwap/integer-mult-bounds/pull/299) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#300](https://github.com/CrocSwap/integer-mult-bounds/pull/300) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#301](https://github.com/CrocSwap/integer-mult-bounds/pull/301) | maximussthegreat | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#302](https://github.com/CrocSwap/integer-mult-bounds/pull/302) | maximussthegreat | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#303](https://github.com/CrocSwap/integer-mult-bounds/pull/303) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#304](https://github.com/CrocSwap/integer-mult-bounds/pull/304) | DreamingOfClouds | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#305](https://github.com/CrocSwap/integer-mult-bounds/pull/305) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#306](https://github.com/CrocSwap/integer-mult-bounds/pull/306) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#307](https://github.com/CrocSwap/integer-mult-bounds/pull/307) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#308](https://github.com/CrocSwap/integer-mult-bounds/pull/308) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#309](https://github.com/CrocSwap/integer-mult-bounds/pull/309) | Dugongue | partially reviewed | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#310](https://github.com/CrocSwap/integer-mult-bounds/pull/310) | utcorvusvolat-dotcom | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#311](https://github.com/CrocSwap/integer-mult-bounds/pull/311) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#312](https://github.com/CrocSwap/integer-mult-bounds/pull/312) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#313](https://github.com/CrocSwap/integer-mult-bounds/pull/313) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#314](https://github.com/CrocSwap/integer-mult-bounds/pull/314) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#315](https://github.com/CrocSwap/integer-mult-bounds/pull/315) | DreamingOfClouds | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#316](https://github.com/CrocSwap/integer-mult-bounds/pull/316) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#317](https://github.com/CrocSwap/integer-mult-bounds/pull/317) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#318](https://github.com/CrocSwap/integer-mult-bounds/pull/318) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#319](https://github.com/CrocSwap/integer-mult-bounds/pull/319) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#320](https://github.com/CrocSwap/integer-mult-bounds/pull/320) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#321](https://github.com/CrocSwap/integer-mult-bounds/pull/321) | Dugongue | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#322](https://github.com/CrocSwap/integer-mult-bounds/pull/322) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#323](https://github.com/CrocSwap/integer-mult-bounds/pull/323) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#324](https://github.com/CrocSwap/integer-mult-bounds/pull/324) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#325](https://github.com/CrocSwap/integer-mult-bounds/pull/325) | DreamingOfClouds | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#327](https://github.com/CrocSwap/integer-mult-bounds/pull/327) | DreamingOfClouds | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#328](https://github.com/CrocSwap/integer-mult-bounds/pull/328) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#329](https://github.com/CrocSwap/integer-mult-bounds/pull/329) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#330](https://github.com/CrocSwap/integer-mult-bounds/pull/330) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#331](https://github.com/CrocSwap/integer-mult-bounds/pull/331) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#332](https://github.com/CrocSwap/integer-mult-bounds/pull/332) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#333](https://github.com/CrocSwap/integer-mult-bounds/pull/333) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#334](https://github.com/CrocSwap/integer-mult-bounds/pull/334) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#335](https://github.com/CrocSwap/integer-mult-bounds/pull/335) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#336](https://github.com/CrocSwap/integer-mult-bounds/pull/336) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#337](https://github.com/CrocSwap/integer-mult-bounds/pull/337) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#338](https://github.com/CrocSwap/integer-mult-bounds/pull/338) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#339](https://github.com/CrocSwap/integer-mult-bounds/pull/339) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#340](https://github.com/CrocSwap/integer-mult-bounds/pull/340) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#341](https://github.com/CrocSwap/integer-mult-bounds/pull/341) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#342](https://github.com/CrocSwap/integer-mult-bounds/pull/342) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#343](https://github.com/CrocSwap/integer-mult-bounds/pull/343) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#344](https://github.com/CrocSwap/integer-mult-bounds/pull/344) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#345](https://github.com/CrocSwap/integer-mult-bounds/pull/345) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#346](https://github.com/CrocSwap/integer-mult-bounds/pull/346) | LJH-217 | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#347](https://github.com/CrocSwap/integer-mult-bounds/pull/347) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#348](https://github.com/CrocSwap/integer-mult-bounds/pull/348) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#349](https://github.com/CrocSwap/integer-mult-bounds/pull/349) | erebos-labs | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#350](https://github.com/CrocSwap/integer-mult-bounds/pull/350) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#351](https://github.com/CrocSwap/integer-mult-bounds/pull/351) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#352](https://github.com/CrocSwap/integer-mult-bounds/pull/352) | DaysSky | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#353](https://github.com/CrocSwap/integer-mult-bounds/pull/353) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#354](https://github.com/CrocSwap/integer-mult-bounds/pull/354) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#355](https://github.com/CrocSwap/integer-mult-bounds/pull/355) | Dugongue | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#356](https://github.com/CrocSwap/integer-mult-bounds/pull/356) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#357](https://github.com/CrocSwap/integer-mult-bounds/pull/357) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#358](https://github.com/CrocSwap/integer-mult-bounds/pull/358) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#359](https://github.com/CrocSwap/integer-mult-bounds/pull/359) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#360](https://github.com/CrocSwap/integer-mult-bounds/pull/360) | Dugongue | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#361](https://github.com/CrocSwap/integer-mult-bounds/pull/361) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#362](https://github.com/CrocSwap/integer-mult-bounds/pull/362) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#363](https://github.com/CrocSwap/integer-mult-bounds/pull/363) | DaysSky | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#364](https://github.com/CrocSwap/integer-mult-bounds/pull/364) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#365](https://github.com/CrocSwap/integer-mult-bounds/pull/365) | aliromman | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#366](https://github.com/CrocSwap/integer-mult-bounds/pull/366) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#367](https://github.com/CrocSwap/integer-mult-bounds/pull/367) | amanforindia | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#368](https://github.com/CrocSwap/integer-mult-bounds/pull/368) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#369](https://github.com/CrocSwap/integer-mult-bounds/pull/369) | applecrusher | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#370](https://github.com/CrocSwap/integer-mult-bounds/pull/370) | utcorvusvolat-dotcom | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#371](https://github.com/CrocSwap/integer-mult-bounds/pull/371) | artuskg | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#372](https://github.com/CrocSwap/integer-mult-bounds/pull/372) | DesmondForward | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#373](https://github.com/CrocSwap/integer-mult-bounds/pull/373) | DaysSky | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#374](https://github.com/CrocSwap/integer-mult-bounds/pull/374) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#375](https://github.com/CrocSwap/integer-mult-bounds/pull/375) | DaysSky | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#376](https://github.com/CrocSwap/integer-mult-bounds/pull/376) | applecrusher | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#377](https://github.com/CrocSwap/integer-mult-bounds/pull/377) | jacklightChen | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#378](https://github.com/CrocSwap/integer-mult-bounds/pull/378) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#379](https://github.com/CrocSwap/integer-mult-bounds/pull/379) | eumemic | partially reviewed | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#380](https://github.com/CrocSwap/integer-mult-bounds/pull/380) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#381](https://github.com/CrocSwap/integer-mult-bounds/pull/381) | DaysSky | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#382](https://github.com/CrocSwap/integer-mult-bounds/pull/382) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#383](https://github.com/CrocSwap/integer-mult-bounds/pull/383) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#384](https://github.com/CrocSwap/integer-mult-bounds/pull/384) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#385](https://github.com/CrocSwap/integer-mult-bounds/pull/385) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#386](https://github.com/CrocSwap/integer-mult-bounds/pull/386) | jacklightChen | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#387](https://github.com/CrocSwap/integer-mult-bounds/pull/387) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#388](https://github.com/CrocSwap/integer-mult-bounds/pull/388) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#389](https://github.com/CrocSwap/integer-mult-bounds/pull/389) | ai-nanachi | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#390](https://github.com/CrocSwap/integer-mult-bounds/pull/390) | Dugongue | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#391](https://github.com/CrocSwap/integer-mult-bounds/pull/391) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#392](https://github.com/CrocSwap/integer-mult-bounds/pull/392) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#394](https://github.com/CrocSwap/integer-mult-bounds/pull/394) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#395](https://github.com/CrocSwap/integer-mult-bounds/pull/395) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#396](https://github.com/CrocSwap/integer-mult-bounds/pull/396) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#397](https://github.com/CrocSwap/integer-mult-bounds/pull/397) | artuskg | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#398](https://github.com/CrocSwap/integer-mult-bounds/pull/398) | Dugongue | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#399](https://github.com/CrocSwap/integer-mult-bounds/pull/399) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#400](https://github.com/CrocSwap/integer-mult-bounds/pull/400) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#401](https://github.com/CrocSwap/integer-mult-bounds/pull/401) | Dugongue | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#402](https://github.com/CrocSwap/integer-mult-bounds/pull/402) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#403](https://github.com/CrocSwap/integer-mult-bounds/pull/403) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#404](https://github.com/CrocSwap/integer-mult-bounds/pull/404) | Dugongue | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#405](https://github.com/CrocSwap/integer-mult-bounds/pull/405) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#406](https://github.com/CrocSwap/integer-mult-bounds/pull/406) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#407](https://github.com/CrocSwap/integer-mult-bounds/pull/407) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#408](https://github.com/CrocSwap/integer-mult-bounds/pull/408) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#409](https://github.com/CrocSwap/integer-mult-bounds/pull/409) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#410](https://github.com/CrocSwap/integer-mult-bounds/pull/410) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#411](https://github.com/CrocSwap/integer-mult-bounds/pull/411) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#412](https://github.com/CrocSwap/integer-mult-bounds/pull/412) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#413](https://github.com/CrocSwap/integer-mult-bounds/pull/413) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#414](https://github.com/CrocSwap/integer-mult-bounds/pull/414) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#415](https://github.com/CrocSwap/integer-mult-bounds/pull/415) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#416](https://github.com/CrocSwap/integer-mult-bounds/pull/416) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#417](https://github.com/CrocSwap/integer-mult-bounds/pull/417) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#418](https://github.com/CrocSwap/integer-mult-bounds/pull/418) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#419](https://github.com/CrocSwap/integer-mult-bounds/pull/419) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#420](https://github.com/CrocSwap/integer-mult-bounds/pull/420) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#421](https://github.com/CrocSwap/integer-mult-bounds/pull/421) | eumemic | incorporated | [record 1](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
| [#422](https://github.com/CrocSwap/integer-mult-bounds/pull/422) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#423](https://github.com/CrocSwap/integer-mult-bounds/pull/423) | eumemic | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#424](https://github.com/CrocSwap/integer-mult-bounds/pull/424) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#425](https://github.com/CrocSwap/integer-mult-bounds/pull/425) | jacklightChen | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#426](https://github.com/CrocSwap/integer-mult-bounds/pull/426) | ai-nanachi | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#427](https://github.com/CrocSwap/integer-mult-bounds/pull/427) | eumemic | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#428](https://github.com/CrocSwap/integer-mult-bounds/pull/428) | eumemic | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#429](https://github.com/CrocSwap/integer-mult-bounds/pull/429) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#430](https://github.com/CrocSwap/integer-mult-bounds/pull/430) | artuskg | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#431](https://github.com/CrocSwap/integer-mult-bounds/pull/431) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#432](https://github.com/CrocSwap/integer-mult-bounds/pull/432) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#433](https://github.com/CrocSwap/integer-mult-bounds/pull/433) | icekylinx | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#434](https://github.com/CrocSwap/integer-mult-bounds/pull/434) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#435](https://github.com/CrocSwap/integer-mult-bounds/pull/435) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#436](https://github.com/CrocSwap/integer-mult-bounds/pull/436) | eumemic | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#437](https://github.com/CrocSwap/integer-mult-bounds/pull/437) | eumemic | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#438](https://github.com/CrocSwap/integer-mult-bounds/pull/438) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#439](https://github.com/CrocSwap/integer-mult-bounds/pull/439) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#440](https://github.com/CrocSwap/integer-mult-bounds/pull/440) | eumemic | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#441](https://github.com/CrocSwap/integer-mult-bounds/pull/441) | eumemic | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#442](https://github.com/CrocSwap/integer-mult-bounds/pull/442) | DaysSky | incorporated | [record 1](../../docs/research/community-formal-20261012-integration.json) · [record 2](../../docs/research/community-formal-20261012-review.md) |
| [#443](https://github.com/CrocSwap/integer-mult-bounds/pull/443) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#444](https://github.com/CrocSwap/integer-mult-bounds/pull/444) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#445](https://github.com/CrocSwap/integer-mult-bounds/pull/445) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#446](https://github.com/CrocSwap/integer-mult-bounds/pull/446) | DreamingOfClouds | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#447](https://github.com/CrocSwap/integer-mult-bounds/pull/447) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#448](https://github.com/CrocSwap/integer-mult-bounds/pull/448) | higherbeing | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#450](https://github.com/CrocSwap/integer-mult-bounds/pull/450) | DreamingOfClouds | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#451](https://github.com/CrocSwap/integer-mult-bounds/pull/451) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#452](https://github.com/CrocSwap/integer-mult-bounds/pull/452) | amanforindia | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#453](https://github.com/CrocSwap/integer-mult-bounds/pull/453) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#454](https://github.com/CrocSwap/integer-mult-bounds/pull/454) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#455](https://github.com/CrocSwap/integer-mult-bounds/pull/455) | Dugongue | partially reviewed | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#456](https://github.com/CrocSwap/integer-mult-bounds/pull/456) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#457](https://github.com/CrocSwap/integer-mult-bounds/pull/457) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#458](https://github.com/CrocSwap/integer-mult-bounds/pull/458) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#459](https://github.com/CrocSwap/integer-mult-bounds/pull/459) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#460](https://github.com/CrocSwap/integer-mult-bounds/pull/460) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#461](https://github.com/CrocSwap/integer-mult-bounds/pull/461) | Srikrishnabalaji | partially reviewed | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#462](https://github.com/CrocSwap/integer-mult-bounds/pull/462) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#463](https://github.com/CrocSwap/integer-mult-bounds/pull/463) | DreamingOfClouds | incorporated | [record 1](../../research/community-family533-audit/DISPOSITIONS.json) · [record 2](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#464](https://github.com/CrocSwap/integer-mult-bounds/pull/464) | ahrazzle | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#465](https://github.com/CrocSwap/integer-mult-bounds/pull/465) | Srikrishnabalaji | partially reviewed | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#466](https://github.com/CrocSwap/integer-mult-bounds/pull/466) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#467](https://github.com/CrocSwap/integer-mult-bounds/pull/467) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#469](https://github.com/CrocSwap/integer-mult-bounds/pull/469) | ahrazzle | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#470](https://github.com/CrocSwap/integer-mult-bounds/pull/470) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#471](https://github.com/CrocSwap/integer-mult-bounds/pull/471) | Dugongue | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#472](https://github.com/CrocSwap/integer-mult-bounds/pull/472) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#473](https://github.com/CrocSwap/integer-mult-bounds/pull/473) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#474](https://github.com/CrocSwap/integer-mult-bounds/pull/474) | artuskg | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#475](https://github.com/CrocSwap/integer-mult-bounds/pull/475) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#476](https://github.com/CrocSwap/integer-mult-bounds/pull/476) | Dugongue | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#478](https://github.com/CrocSwap/integer-mult-bounds/pull/478) | Dugongue | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#479](https://github.com/CrocSwap/integer-mult-bounds/pull/479) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#480](https://github.com/CrocSwap/integer-mult-bounds/pull/480) | higherbeing | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#481](https://github.com/CrocSwap/integer-mult-bounds/pull/481) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#482](https://github.com/CrocSwap/integer-mult-bounds/pull/482) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#483](https://github.com/CrocSwap/integer-mult-bounds/pull/483) | Dugongue | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#484](https://github.com/CrocSwap/integer-mult-bounds/pull/484) | DreamingOfClouds | incorporated | [record 1](../../docs/research/community-formal-20261012-integration.json) · [record 2](../../docs/research/community-formal-20261012-review.md) |
| [#485](https://github.com/CrocSwap/integer-mult-bounds/pull/485) | DreamingOfClouds | partially reviewed | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#486](https://github.com/CrocSwap/integer-mult-bounds/pull/486) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#487](https://github.com/CrocSwap/integer-mult-bounds/pull/487) | jamesyc | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#488](https://github.com/CrocSwap/integer-mult-bounds/pull/488) | jamesyc | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#489](https://github.com/CrocSwap/integer-mult-bounds/pull/489) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#490](https://github.com/CrocSwap/integer-mult-bounds/pull/490) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#491](https://github.com/CrocSwap/integer-mult-bounds/pull/491) | M6LI | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#492](https://github.com/CrocSwap/integer-mult-bounds/pull/492) | Dugongue | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#494](https://github.com/CrocSwap/integer-mult-bounds/pull/494) | higherbeing | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#495](https://github.com/CrocSwap/integer-mult-bounds/pull/495) | aliromman | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#496](https://github.com/CrocSwap/integer-mult-bounds/pull/496) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#497](https://github.com/CrocSwap/integer-mult-bounds/pull/497) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#498](https://github.com/CrocSwap/integer-mult-bounds/pull/498) | Dugongue | partially reviewed | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#499](https://github.com/CrocSwap/integer-mult-bounds/pull/499) | rosswaycaster | partially reviewed | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#500](https://github.com/CrocSwap/integer-mult-bounds/pull/500) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#501](https://github.com/CrocSwap/integer-mult-bounds/pull/501) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#502](https://github.com/CrocSwap/integer-mult-bounds/pull/502) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#503](https://github.com/CrocSwap/integer-mult-bounds/pull/503) | DreamingOfClouds | incorporated | [record 1](../../research/community-family533-audit/DISPOSITIONS.json) |
| [#504](https://github.com/CrocSwap/integer-mult-bounds/pull/504) | DreamingOfClouds | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#505](https://github.com/CrocSwap/integer-mult-bounds/pull/505) | Dugongue | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#506](https://github.com/CrocSwap/integer-mult-bounds/pull/506) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#507](https://github.com/CrocSwap/integer-mult-bounds/pull/507) | eumemic | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#508](https://github.com/CrocSwap/integer-mult-bounds/pull/508) | Dugongue | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#509](https://github.com/CrocSwap/integer-mult-bounds/pull/509) | DreamingOfClouds | incorporated | [record 1](../../docs/research/community-formal-20261012-integration.json) · [record 2](../../docs/research/community-formal-20261012-review.md) |
| [#510](https://github.com/CrocSwap/integer-mult-bounds/pull/510) | DreamingOfClouds | incorporated | [record 1](../../research/community-family533-audit/DISPOSITIONS.json) |
| [#511](https://github.com/CrocSwap/integer-mult-bounds/pull/511) | jamesyc | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#512](https://github.com/CrocSwap/integer-mult-bounds/pull/512) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#513](https://github.com/CrocSwap/integer-mult-bounds/pull/513) | jamesyc | incorporated | [record 1](../../research/community-family533-audit/DISPOSITIONS.json) |
| [#515](https://github.com/CrocSwap/integer-mult-bounds/pull/515) | DreamingOfClouds | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#516](https://github.com/CrocSwap/integer-mult-bounds/pull/516) | DreamingOfClouds | incorporated | [record 1](../../docs/research/community-formal-20261012-integration.json) · [record 2](../../docs/research/community-formal-20261012-review.md) |
| [#517](https://github.com/CrocSwap/integer-mult-bounds/pull/517) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#518](https://github.com/CrocSwap/integer-mult-bounds/pull/518) | Dugongue | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#519](https://github.com/CrocSwap/integer-mult-bounds/pull/519) | jamesyc | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#520](https://github.com/CrocSwap/integer-mult-bounds/pull/520) | higherbeing | incorporated | [record 1](../../docs/research/community-formal-20261012-integration.json) · [record 2](../../docs/research/community-formal-20261012-review.md) |
| [#521](https://github.com/CrocSwap/integer-mult-bounds/pull/521) | applecrusher | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#522](https://github.com/CrocSwap/integer-mult-bounds/pull/522) | Dugongue | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#525](https://github.com/CrocSwap/integer-mult-bounds/pull/525) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#526](https://github.com/CrocSwap/integer-mult-bounds/pull/526) | jamesyc | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#527](https://github.com/CrocSwap/integer-mult-bounds/pull/527) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#528](https://github.com/CrocSwap/integer-mult-bounds/pull/528) | jamesyc | incorporated | [record 1](../../research/community-family533-audit/DISPOSITIONS.json) |
| [#529](https://github.com/CrocSwap/integer-mult-bounds/pull/529) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#530](https://github.com/CrocSwap/integer-mult-bounds/pull/530) | jamesyc | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#532](https://github.com/CrocSwap/integer-mult-bounds/pull/532) | Dugongue | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#533](https://github.com/CrocSwap/integer-mult-bounds/pull/533) | chafreaky | incorporated | [record 1](../../research/community-family533-audit/DISPOSITIONS.json) |
| [#534](https://github.com/CrocSwap/integer-mult-bounds/pull/534) | rohanarun | incorporated | [record 1](../../research/community-family533-audit/DISPOSITIONS.json) |
| [#535](https://github.com/CrocSwap/integer-mult-bounds/pull/535) | icekylinx | incorporated | [record 1](../../research/community-family533-audit/DISPOSITIONS.json) |
| [#536](https://github.com/CrocSwap/integer-mult-bounds/pull/536) | rohanarun | incorporated | [record 1](../../research/community-family533-audit/DISPOSITIONS.json) |
| [#537](https://github.com/CrocSwap/integer-mult-bounds/pull/537) | Dugongue | incorporated | [record 1](../../research/community-family533-audit/DISPOSITIONS.json) |
| [#538](https://github.com/CrocSwap/integer-mult-bounds/pull/538) | chafreaky | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#539](https://github.com/CrocSwap/integer-mult-bounds/pull/539) | rohanarun | incorporated | [record 1](../../research/community-family588-audit/DISPOSITIONS.json) |
| [#540](https://github.com/CrocSwap/integer-mult-bounds/pull/540) | cheesegrader | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
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
| [#594](https://github.com/CrocSwap/integer-mult-bounds/pull/594) | eumemic | incorporated | [record 1](../../research/community-hyperplane599-audit/DISPOSITIONS.json) · [record 2](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
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
| [#611](https://github.com/CrocSwap/integer-mult-bounds/pull/611) | eumemic | incorporated | [record 1](../../research/community-cold617-audit/DISPOSITIONS.json) · [record 2](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#612](https://github.com/CrocSwap/integer-mult-bounds/pull/612) | jamesyc | partially reviewed | [record 1](../../research/community-cold617-audit/DISPOSITIONS.json) |
| [#613](https://github.com/CrocSwap/integer-mult-bounds/pull/613) | eumemic | incorporated | [record 1](../../research/community-cold617-audit/DISPOSITIONS.json) |
| [#614](https://github.com/CrocSwap/integer-mult-bounds/pull/614) | jeremykothe2 | incorporated | [record 1](../../research/community-cold617-audit/DISPOSITIONS.json) |
| [#615](https://github.com/CrocSwap/integer-mult-bounds/pull/615) | jeremykothe2 | incorporated | [record 1](../../research/community-cold617-audit/DISPOSITIONS.json) |
| [#616](https://github.com/CrocSwap/integer-mult-bounds/pull/616) | chafreaky | incorporated | [record 1](../../research/community-cold617-audit/DISPOSITIONS.json) |
| [#617](https://github.com/CrocSwap/integer-mult-bounds/pull/617) | jeremykothe2 | incorporated | [record 1](../../research/community-cold617-audit/DISPOSITIONS.json) |
| [#618](https://github.com/CrocSwap/integer-mult-bounds/pull/618) | jeremydiviney | incorporated | [record 1](../../research/community-k492-audit/DISPOSITIONS.json) |
| [#619](https://github.com/CrocSwap/integer-mult-bounds/pull/619) | chafreaky | incorporated | [record 1](../../research/community-k492-audit/DISPOSITIONS.json) |
| [#620](https://github.com/CrocSwap/integer-mult-bounds/pull/620) | GamingPuzzled | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-k492-audit/DISPOSITIONS.json) |
| [#621](https://github.com/CrocSwap/integer-mult-bounds/pull/621) | aliromman | incorporated | [record 1](../../research/community-k492-audit/DISPOSITIONS.json) |
| [#622](https://github.com/CrocSwap/integer-mult-bounds/pull/622) | jeremykothe2 | incorporated | [record 1](../../research/community-k492-audit/DISPOSITIONS.json) |
| [#623](https://github.com/CrocSwap/integer-mult-bounds/pull/623) | jeremykothe2 | incorporated | [record 1](../../research/community-k492-audit/DISPOSITIONS.json) |
| [#624](https://github.com/CrocSwap/integer-mult-bounds/pull/624) | jeremydiviney | incorporated | [record 1](../../research/community-k492-audit/DISPOSITIONS.json) |
| [#625](https://github.com/CrocSwap/integer-mult-bounds/pull/625) | jeremykothe2 | incorporated | [record 1](../../research/community-k492-audit/DISPOSITIONS.json) |
| [#626](https://github.com/CrocSwap/integer-mult-bounds/pull/626) | chafreaky | incorporated | [record 1](../../research/community-k492-audit/DISPOSITIONS.json) |
| [#627](https://github.com/CrocSwap/integer-mult-bounds/pull/627) | jeremydiviney | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#628](https://github.com/CrocSwap/integer-mult-bounds/pull/628) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#629](https://github.com/CrocSwap/integer-mult-bounds/pull/629) | jeremykothe2 | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#630](https://github.com/CrocSwap/integer-mult-bounds/pull/630) | vectorsss | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#631](https://github.com/CrocSwap/integer-mult-bounds/pull/631) | vectorsss | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#632](https://github.com/CrocSwap/integer-mult-bounds/pull/632) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#633](https://github.com/CrocSwap/integer-mult-bounds/pull/633) | vectorsss | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#634](https://github.com/CrocSwap/integer-mult-bounds/pull/634) | ShikeChen01 | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#635](https://github.com/CrocSwap/integer-mult-bounds/pull/635) | jeremykothe2 | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#636](https://github.com/CrocSwap/integer-mult-bounds/pull/636) | vectorsss | partially reviewed | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#637](https://github.com/CrocSwap/integer-mult-bounds/pull/637) | jeremykothe2 | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#638](https://github.com/CrocSwap/integer-mult-bounds/pull/638) | vectorsss | partially reviewed | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#639](https://github.com/CrocSwap/integer-mult-bounds/pull/639) | vectorsss | partially reviewed | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#640](https://github.com/CrocSwap/integer-mult-bounds/pull/640) | vectorsss | partially reviewed | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#641](https://github.com/CrocSwap/integer-mult-bounds/pull/641) | jeremykothe2 | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#642](https://github.com/CrocSwap/integer-mult-bounds/pull/642) | vectorsss | partially reviewed | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#643](https://github.com/CrocSwap/integer-mult-bounds/pull/643) | jeremykothe2 | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#644](https://github.com/CrocSwap/integer-mult-bounds/pull/644) | vectorsss | partially reviewed | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#645](https://github.com/CrocSwap/integer-mult-bounds/pull/645) | icekylinx | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#646](https://github.com/CrocSwap/integer-mult-bounds/pull/646) | jeremydiviney | partially reviewed | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#648](https://github.com/CrocSwap/integer-mult-bounds/pull/648) | jeremykothe2 | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#649](https://github.com/CrocSwap/integer-mult-bounds/pull/649) | jeremykothe2 | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#651](https://github.com/CrocSwap/integer-mult-bounds/pull/651) | higherbeing | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#652](https://github.com/CrocSwap/integer-mult-bounds/pull/652) | jeremykothe2 | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#653](https://github.com/CrocSwap/integer-mult-bounds/pull/653) | jaymosley07 | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#654](https://github.com/CrocSwap/integer-mult-bounds/pull/654) | GamingPuzzled | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#655](https://github.com/CrocSwap/integer-mult-bounds/pull/655) | jeremykothe2 | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#656](https://github.com/CrocSwap/integer-mult-bounds/pull/656) | jeremykothe2 | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#657](https://github.com/CrocSwap/integer-mult-bounds/pull/657) | DaysSky | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#658](https://github.com/CrocSwap/integer-mult-bounds/pull/658) | jeremydiviney | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#659](https://github.com/CrocSwap/integer-mult-bounds/pull/659) | jeremykothe2 | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#660](https://github.com/CrocSwap/integer-mult-bounds/pull/660) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#661](https://github.com/CrocSwap/integer-mult-bounds/pull/661) | yuj1r0 | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#662](https://github.com/CrocSwap/integer-mult-bounds/pull/662) | cbethin | incorporated | [record 1](../../research/community-frontier799-audit/DISPOSITIONS.json) |
| [#663](https://github.com/CrocSwap/integer-mult-bounds/pull/663) | 0xkilgore | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#664](https://github.com/CrocSwap/integer-mult-bounds/pull/664) | jeremykothe2 | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#665](https://github.com/CrocSwap/integer-mult-bounds/pull/665) | Mister-Meeseeks | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#666](https://github.com/CrocSwap/integer-mult-bounds/pull/666) | at1as | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#667](https://github.com/CrocSwap/integer-mult-bounds/pull/667) | yuj1r0 | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#668](https://github.com/CrocSwap/integer-mult-bounds/pull/668) | swbiggart | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#669](https://github.com/CrocSwap/integer-mult-bounds/pull/669) | the-missionary-company | partially reviewed | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#670](https://github.com/CrocSwap/integer-mult-bounds/pull/670) | yongjae321 | incorporated | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#671](https://github.com/CrocSwap/integer-mult-bounds/pull/671) | jeremykothe2 | partially reviewed | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#672](https://github.com/CrocSwap/integer-mult-bounds/pull/672) | steph4n-gh | incorporated | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#673](https://github.com/CrocSwap/integer-mult-bounds/pull/673) | androolloyd | partially reviewed | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#674](https://github.com/CrocSwap/integer-mult-bounds/pull/674) | x0hu | incorporated | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#675](https://github.com/CrocSwap/integer-mult-bounds/pull/675) | tekuuu | incorporated | [record 1](../../research/community-frontier741-audit/DISPOSITIONS.json) |
| [#676](https://github.com/CrocSwap/integer-mult-bounds/pull/676) | jeremykothe2 | partially reviewed | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#677](https://github.com/CrocSwap/integer-mult-bounds/pull/677) | commdata2338 | incorporated | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#678](https://github.com/CrocSwap/integer-mult-bounds/pull/678) | 0x-chad | incorporated | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#679](https://github.com/CrocSwap/integer-mult-bounds/pull/679) | g-guthrie | incorporated | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#680](https://github.com/CrocSwap/integer-mult-bounds/pull/680) | littleBro | incorporated | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#681](https://github.com/CrocSwap/integer-mult-bounds/pull/681) | alluri-ritual | incorporated | [record 1](../../research/community-frontier741-audit/DISPOSITIONS.json) |
| [#682](https://github.com/CrocSwap/integer-mult-bounds/pull/682) | swbiggart | incorporated | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#683](https://github.com/CrocSwap/integer-mult-bounds/pull/683) | Mister-Meeseeks | incorporated | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#684](https://github.com/CrocSwap/integer-mult-bounds/pull/684) | ineffyble | incorporated | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#685](https://github.com/CrocSwap/integer-mult-bounds/pull/685) | chafreaky | partially reviewed | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#686](https://github.com/CrocSwap/integer-mult-bounds/pull/686) | mikhailramalho | partially reviewed | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#687](https://github.com/CrocSwap/integer-mult-bounds/pull/687) | cbethin | incorporated | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#688](https://github.com/CrocSwap/integer-mult-bounds/pull/688) | aliromman | incorporated | [record 1](../../research/community-frontier799-audit/DISPOSITIONS.json) |
| [#689](https://github.com/CrocSwap/integer-mult-bounds/pull/689) | dillona | incorporated | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#691](https://github.com/CrocSwap/integer-mult-bounds/pull/691) | mtpsl | incorporated | [record 1](../../research/community-frontier799-audit/DISPOSITIONS.json) |
| [#692](https://github.com/CrocSwap/integer-mult-bounds/pull/692) | Ambassators | incorporated | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#693](https://github.com/CrocSwap/integer-mult-bounds/pull/693) | thakrarsagar | incorporated | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#694](https://github.com/CrocSwap/integer-mult-bounds/pull/694) | g-guthrie | incorporated | [record 1](../../research/community-frontier799-audit/DISPOSITIONS.json) |
| [#695](https://github.com/CrocSwap/integer-mult-bounds/pull/695) | jsnider3 | incorporated | [record 1](../../research/community-frontier741-audit/DISPOSITIONS.json) |
| [#696](https://github.com/CrocSwap/integer-mult-bounds/pull/696) | thakrarsagar | incorporated | [record 1](../../research/community-frontier799-audit/DISPOSITIONS.json) |
| [#697](https://github.com/CrocSwap/integer-mult-bounds/pull/697) | swbiggart | partially reviewed | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#698](https://github.com/CrocSwap/integer-mult-bounds/pull/698) | thakrarsagar | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#699](https://github.com/CrocSwap/integer-mult-bounds/pull/699) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#700](https://github.com/CrocSwap/integer-mult-bounds/pull/700) | davidgovea | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#701](https://github.com/CrocSwap/integer-mult-bounds/pull/701) | BigCactusLabs | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#702](https://github.com/CrocSwap/integer-mult-bounds/pull/702) | BigCactusLabs | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#703](https://github.com/CrocSwap/integer-mult-bounds/pull/703) | Mister-Meeseeks | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#704](https://github.com/CrocSwap/integer-mult-bounds/pull/704) | roife | incorporated | [record 1](../../research/community-frontier741-audit/DISPOSITIONS.json) |
| [#705](https://github.com/CrocSwap/integer-mult-bounds/pull/705) | littleBro | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#706](https://github.com/CrocSwap/integer-mult-bounds/pull/706) | arkfx | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#707](https://github.com/CrocSwap/integer-mult-bounds/pull/707) | cbethin | incorporated | [record 1](../../research/community-frontier799-audit/DISPOSITIONS.json) |
| [#708](https://github.com/CrocSwap/integer-mult-bounds/pull/708) | thakrarsagar | incorporated | [record 1](../../research/community-frontier799-audit/DISPOSITIONS.json) |
| [#709](https://github.com/CrocSwap/integer-mult-bounds/pull/709) | mtpsl | incorporated | [record 1](../../research/community-frontier799-audit/DISPOSITIONS.json) |
| [#710](https://github.com/CrocSwap/integer-mult-bounds/pull/710) | thakrarsagar | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#711](https://github.com/CrocSwap/integer-mult-bounds/pull/711) | thakrarsagar | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#712](https://github.com/CrocSwap/integer-mult-bounds/pull/712) | jsnider3 | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#713](https://github.com/CrocSwap/integer-mult-bounds/pull/713) | swbiggart | incorporated | [record 1](../../research/community-frontier799-audit/DISPOSITIONS.json) |
| [#714](https://github.com/CrocSwap/integer-mult-bounds/pull/714) | FanPUYen | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#715](https://github.com/CrocSwap/integer-mult-bounds/pull/715) | thakrarsagar | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#716](https://github.com/CrocSwap/integer-mult-bounds/pull/716) | thakrarsagar | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#717](https://github.com/CrocSwap/integer-mult-bounds/pull/717) | DreamingOfClouds | partially reviewed | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#718](https://github.com/CrocSwap/integer-mult-bounds/pull/718) | thakrarsagar | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#719](https://github.com/CrocSwap/integer-mult-bounds/pull/719) | thakrarsagar | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#720](https://github.com/CrocSwap/integer-mult-bounds/pull/720) | davidgovea | partially reviewed | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#721](https://github.com/CrocSwap/integer-mult-bounds/pull/721) | cxnmai | incorporated | [record 1](../../research/community-frontier799-audit/DISPOSITIONS.json) |
| [#722](https://github.com/CrocSwap/integer-mult-bounds/pull/722) | ellipsi2 | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#723](https://github.com/CrocSwap/integer-mult-bounds/pull/723) | thakrarsagar | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#724](https://github.com/CrocSwap/integer-mult-bounds/pull/724) | thakrarsagar | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#725](https://github.com/CrocSwap/integer-mult-bounds/pull/725) | thakrarsagar | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#726](https://github.com/CrocSwap/integer-mult-bounds/pull/726) | FabrikonManufacturing | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#727](https://github.com/CrocSwap/integer-mult-bounds/pull/727) | TMM2009 | incorporated | [record 1](../../research/community-frontier799-audit/DISPOSITIONS.json) |
| [#728](https://github.com/CrocSwap/integer-mult-bounds/pull/728) | thakrarsagar | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#730](https://github.com/CrocSwap/integer-mult-bounds/pull/730) | thakrarsagar | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#731](https://github.com/CrocSwap/integer-mult-bounds/pull/731) | jsnider3 | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#732](https://github.com/CrocSwap/integer-mult-bounds/pull/732) | lukemansoor | partially reviewed | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#733](https://github.com/CrocSwap/integer-mult-bounds/pull/733) | swbiggart | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#734](https://github.com/CrocSwap/integer-mult-bounds/pull/734) | AllStars101-sudo | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#735](https://github.com/CrocSwap/integer-mult-bounds/pull/735) | AryanSudhirDev | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#736](https://github.com/CrocSwap/integer-mult-bounds/pull/736) | thakrarsagar | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#737](https://github.com/CrocSwap/integer-mult-bounds/pull/737) | thakrarsagar | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#738](https://github.com/CrocSwap/integer-mult-bounds/pull/738) | thakrarsagar | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#739](https://github.com/CrocSwap/integer-mult-bounds/pull/739) | namredips | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#740](https://github.com/CrocSwap/integer-mult-bounds/pull/740) | azide0x37 | incorporated | [record 1](../../research/community-frontier741-audit/DISPOSITIONS.json) |
| [#741](https://github.com/CrocSwap/integer-mult-bounds/pull/741) | chafreaky | incorporated | [record 1](../../research/community-frontier741-audit/DISPOSITIONS.json) |
| [#742](https://github.com/CrocSwap/integer-mult-bounds/pull/742) | ellipsi2 | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#743](https://github.com/CrocSwap/integer-mult-bounds/pull/743) | 0xjohnnydev | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#744](https://github.com/CrocSwap/integer-mult-bounds/pull/744) | aliromman | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#745](https://github.com/CrocSwap/integer-mult-bounds/pull/745) | thakrarsagar | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#746](https://github.com/CrocSwap/integer-mult-bounds/pull/746) | williamreidrichards | partially reviewed | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#747](https://github.com/CrocSwap/integer-mult-bounds/pull/747) | aladh | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#748](https://github.com/CrocSwap/integer-mult-bounds/pull/748) | cxnmai | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#749](https://github.com/CrocSwap/integer-mult-bounds/pull/749) | theon199 | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#750](https://github.com/CrocSwap/integer-mult-bounds/pull/750) | thakrarsagar | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#751](https://github.com/CrocSwap/integer-mult-bounds/pull/751) | thakrarsagar | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#752](https://github.com/CrocSwap/integer-mult-bounds/pull/752) | Curtis-D | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#753](https://github.com/CrocSwap/integer-mult-bounds/pull/753) | thakrarsagar | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#754](https://github.com/CrocSwap/integer-mult-bounds/pull/754) | namredips | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#755](https://github.com/CrocSwap/integer-mult-bounds/pull/755) | taizaki69 | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#757](https://github.com/CrocSwap/integer-mult-bounds/pull/757) | rseligm2 | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#758](https://github.com/CrocSwap/integer-mult-bounds/pull/758) | Koroffstrogov | partially reviewed | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#759](https://github.com/CrocSwap/integer-mult-bounds/pull/759) | ofennell-quipex | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#760](https://github.com/CrocSwap/integer-mult-bounds/pull/760) | ishan-1729 | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#761](https://github.com/CrocSwap/integer-mult-bounds/pull/761) | VibeCodyH | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#762](https://github.com/CrocSwap/integer-mult-bounds/pull/762) | thakrarsagar | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#763](https://github.com/CrocSwap/integer-mult-bounds/pull/763) | jp3isme | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#764](https://github.com/CrocSwap/integer-mult-bounds/pull/764) | cbethin | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#765](https://github.com/CrocSwap/integer-mult-bounds/pull/765) | Mister-Meeseeks | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#766](https://github.com/CrocSwap/integer-mult-bounds/pull/766) | gaboroa14 | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#767](https://github.com/CrocSwap/integer-mult-bounds/pull/767) | cbethin | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#768](https://github.com/CrocSwap/integer-mult-bounds/pull/768) | BagMan9 | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#769](https://github.com/CrocSwap/integer-mult-bounds/pull/769) | 24kHandsome1201 | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#770](https://github.com/CrocSwap/integer-mult-bounds/pull/770) | chinmayarvind23 | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#771](https://github.com/CrocSwap/integer-mult-bounds/pull/771) | theon199 | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#772](https://github.com/CrocSwap/integer-mult-bounds/pull/772) | ellipsi2 | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#773](https://github.com/CrocSwap/integer-mult-bounds/pull/773) | Kyu | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#774](https://github.com/CrocSwap/integer-mult-bounds/pull/774) | anthonylei | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#775](https://github.com/CrocSwap/integer-mult-bounds/pull/775) | at1as | partially reviewed | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#776](https://github.com/CrocSwap/integer-mult-bounds/pull/776) | ntedvs | partially reviewed | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#777](https://github.com/CrocSwap/integer-mult-bounds/pull/777) | tekuuu | incorporated | [record 1](../../research/community-frontier741-audit/DISPOSITIONS.json) · [record 2](../../research/community-frontier799-audit/DISPOSITIONS.json) |
| [#778](https://github.com/CrocSwap/integer-mult-bounds/pull/778) | merramil | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#779](https://github.com/CrocSwap/integer-mult-bounds/pull/779) | PeterCarp320 | partially reviewed | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#780](https://github.com/CrocSwap/integer-mult-bounds/pull/780) | JoyboyBrian | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#781](https://github.com/CrocSwap/integer-mult-bounds/pull/781) | NeoKazuya | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#782](https://github.com/CrocSwap/integer-mult-bounds/pull/782) | 6ojo | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#783](https://github.com/CrocSwap/integer-mult-bounds/pull/783) | Rohansguliani | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#784](https://github.com/CrocSwap/integer-mult-bounds/pull/784) | AlexS-scale | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#785](https://github.com/CrocSwap/integer-mult-bounds/pull/785) | azide0x37 | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#786](https://github.com/CrocSwap/integer-mult-bounds/pull/786) | ssteeper | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#787](https://github.com/CrocSwap/integer-mult-bounds/pull/787) | bitplane | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#788](https://github.com/CrocSwap/integer-mult-bounds/pull/788) | nightangelflowerwin-ops | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#789](https://github.com/CrocSwap/integer-mult-bounds/pull/789) | yzhouwang | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#790](https://github.com/CrocSwap/integer-mult-bounds/pull/790) | commdata2338 | partially reviewed | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#791](https://github.com/CrocSwap/integer-mult-bounds/pull/791) | Curtis-D | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#792](https://github.com/CrocSwap/integer-mult-bounds/pull/792) | Ryan-Haines | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#793](https://github.com/CrocSwap/integer-mult-bounds/pull/793) | Varun-Mittal-1001 | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#794](https://github.com/CrocSwap/integer-mult-bounds/pull/794) | commdata2338 | partially reviewed | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#795](https://github.com/CrocSwap/integer-mult-bounds/pull/795) | chafreaky | incorporated | [record 1](../../research/community-frontier799-audit/DISPOSITIONS.json) |
| [#796](https://github.com/CrocSwap/integer-mult-bounds/pull/796) | FanPUYen | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#797](https://github.com/CrocSwap/integer-mult-bounds/pull/797) | aliromman | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#798](https://github.com/CrocSwap/integer-mult-bounds/pull/798) | jonathanlam | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#799](https://github.com/CrocSwap/integer-mult-bounds/pull/799) | jeremykothe2 | incorporated | [record 1](../../research/community-frontier799-audit/DISPOSITIONS.json) |
| [#800](https://github.com/CrocSwap/integer-mult-bounds/pull/800) | jeremydiviney | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#801](https://github.com/CrocSwap/integer-mult-bounds/pull/801) | Rohansguliani | partially reviewed | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#802](https://github.com/CrocSwap/integer-mult-bounds/pull/802) | Rohansguliani | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#803](https://github.com/CrocSwap/integer-mult-bounds/pull/803) | alephnan | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#805](https://github.com/CrocSwap/integer-mult-bounds/pull/805) | VictorLiwentao | partially reviewed | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#806](https://github.com/CrocSwap/integer-mult-bounds/pull/806) | Rohansguliani | incorporated | [record 1](../../research/community-frontier799-audit/DISPOSITIONS.json) |
| [#807](https://github.com/CrocSwap/integer-mult-bounds/pull/807) | davidawad | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#808](https://github.com/CrocSwap/integer-mult-bounds/pull/808) | 4RchYMing | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#809](https://github.com/CrocSwap/integer-mult-bounds/pull/809) | Curtis-D | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#810](https://github.com/CrocSwap/integer-mult-bounds/pull/810) | jerrylin-23 | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#811](https://github.com/CrocSwap/integer-mult-bounds/pull/811) | Ryan-Haines | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#812](https://github.com/CrocSwap/integer-mult-bounds/pull/812) | ljste | incorporated | [record 1](../../research/community-frontier890-audit/DISPOSITIONS.json) |
| [#813](https://github.com/CrocSwap/integer-mult-bounds/pull/813) | bitplane | incorporated | [record 1](../../research/community-batch932-audit/DISPOSITIONS.json) |
| [#814](https://github.com/CrocSwap/integer-mult-bounds/pull/814) | shiftybitshiftr | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#815](https://github.com/CrocSwap/integer-mult-bounds/pull/815) | Rohansguliani | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#816](https://github.com/CrocSwap/integer-mult-bounds/pull/816) | dd-hemant | incorporated | [record 1](../../research/community-batch932-audit/DISPOSITIONS.json) |
| [#817](https://github.com/CrocSwap/integer-mult-bounds/pull/817) | thakrarsagar | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#818](https://github.com/CrocSwap/integer-mult-bounds/pull/818) | MrPink604 | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#819](https://github.com/CrocSwap/integer-mult-bounds/pull/819) | MrPink604 | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#820](https://github.com/CrocSwap/integer-mult-bounds/pull/820) | WilliamLawyer | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#821](https://github.com/CrocSwap/integer-mult-bounds/pull/821) | Brodee042 | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#822](https://github.com/CrocSwap/integer-mult-bounds/pull/822) | shhxera | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#823](https://github.com/CrocSwap/integer-mult-bounds/pull/823) | FanPUYen | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#824](https://github.com/CrocSwap/integer-mult-bounds/pull/824) | navinor | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#825](https://github.com/CrocSwap/integer-mult-bounds/pull/825) | navinor | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#826](https://github.com/CrocSwap/integer-mult-bounds/pull/826) | Rohansguliani | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#827](https://github.com/CrocSwap/integer-mult-bounds/pull/827) | cbethin | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#828](https://github.com/CrocSwap/integer-mult-bounds/pull/828) | mihir-s-05 | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#830](https://github.com/CrocSwap/integer-mult-bounds/pull/830) | Ryan-Haines | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#831](https://github.com/CrocSwap/integer-mult-bounds/pull/831) | Maximooch | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#832](https://github.com/CrocSwap/integer-mult-bounds/pull/832) | ThiagoCAltoe | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#833](https://github.com/CrocSwap/integer-mult-bounds/pull/833) | anudeepadi | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#834](https://github.com/CrocSwap/integer-mult-bounds/pull/834) | chinmayarvind23 | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#835](https://github.com/CrocSwap/integer-mult-bounds/pull/835) | Ryan-Haines | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#836](https://github.com/CrocSwap/integer-mult-bounds/pull/836) | jeremydiviney | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#837](https://github.com/CrocSwap/integer-mult-bounds/pull/837) | bitplane | incorporated | [record 1](../../research/community-batch932-audit/DISPOSITIONS.json) |
| [#838](https://github.com/CrocSwap/integer-mult-bounds/pull/838) | ljste | incorporated | [record 1](../../research/community-frontier890-audit/DISPOSITIONS.json) |
| [#839](https://github.com/CrocSwap/integer-mult-bounds/pull/839) | faw01 | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#840](https://github.com/CrocSwap/integer-mult-bounds/pull/840) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#841](https://github.com/CrocSwap/integer-mult-bounds/pull/841) | mihir-s-05 | incorporated | [record 1](../../research/community-frontier890-audit/DISPOSITIONS.json) |
| [#843](https://github.com/CrocSwap/integer-mult-bounds/pull/843) | anudeepadi | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#845](https://github.com/CrocSwap/integer-mult-bounds/pull/845) | mihir-s-05 | incorporated | [record 1](../../research/community-batch952-audit/DISPOSITIONS.json) |
| [#846](https://github.com/CrocSwap/integer-mult-bounds/pull/846) | Rohansguliani | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#847](https://github.com/CrocSwap/integer-mult-bounds/pull/847) | chinmayarvind23 | incorporated | [record 1](../../research/community-frontier890-audit/DISPOSITIONS.json) |
| [#848](https://github.com/CrocSwap/integer-mult-bounds/pull/848) | navinor | incorporated | [record 1](../../research/community-batch952-audit/DISPOSITIONS.json) |
| [#849](https://github.com/CrocSwap/integer-mult-bounds/pull/849) | bitplane | incorporated | [record 1](../../research/community-batch932-audit/DISPOSITIONS.json) |
| [#850](https://github.com/CrocSwap/integer-mult-bounds/pull/850) | cbethin | incorporated | [record 1](../../research/community-batch952-audit/DISPOSITIONS.json) |
| [#851](https://github.com/CrocSwap/integer-mult-bounds/pull/851) | AdemVessell | incorporated | [record 1](../../research/community-frontier890-audit/DISPOSITIONS.json) |
| [#852](https://github.com/CrocSwap/integer-mult-bounds/pull/852) | WilliamLawyer | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#853](https://github.com/CrocSwap/integer-mult-bounds/pull/853) | navinor | incorporated | [record 1](../../research/community-frontier890-audit/DISPOSITIONS.json) |
| [#854](https://github.com/CrocSwap/integer-mult-bounds/pull/854) | chinmayarvind23 | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#855](https://github.com/CrocSwap/integer-mult-bounds/pull/855) | NeoKazuya | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#856](https://github.com/CrocSwap/integer-mult-bounds/pull/856) | chinmayarvind23 | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#857](https://github.com/CrocSwap/integer-mult-bounds/pull/857) | zeusinsight | incorporated | [record 1](../../research/community-batch952-audit/DISPOSITIONS.json) |
| [#860](https://github.com/CrocSwap/integer-mult-bounds/pull/860) | amazedbot | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#861](https://github.com/CrocSwap/integer-mult-bounds/pull/861) | Kairos-Ess | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#862](https://github.com/CrocSwap/integer-mult-bounds/pull/862) | chafreaky | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#863](https://github.com/CrocSwap/integer-mult-bounds/pull/863) | Curtis-D | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#864](https://github.com/CrocSwap/integer-mult-bounds/pull/864) | navinor | incorporated | [record 1](../../research/community-frontier890-audit/DISPOSITIONS.json) |
| [#865](https://github.com/CrocSwap/integer-mult-bounds/pull/865) | nightangelflowerwin-ops | incorporated | [record 1](../../research/community-frontier890-audit/DISPOSITIONS.json) |
| [#866](https://github.com/CrocSwap/integer-mult-bounds/pull/866) | bitplane | incorporated | [record 1](../../research/community-batch932-audit/DISPOSITIONS.json) |
| [#867](https://github.com/CrocSwap/integer-mult-bounds/pull/867) | navinor | incorporated | [record 1](../../research/community-batch932-audit/DISPOSITIONS.json) |
| [#868](https://github.com/CrocSwap/integer-mult-bounds/pull/868) | WilliamLawyer | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#869](https://github.com/CrocSwap/integer-mult-bounds/pull/869) | jeremykothe2 | incorporated | [record 1](../../research/community-frontier890-audit/DISPOSITIONS.json) |
| [#870](https://github.com/CrocSwap/integer-mult-bounds/pull/870) | jeremykothe2 | incorporated | [record 1](../../research/community-frontier890-audit/DISPOSITIONS.json) |
| [#873](https://github.com/CrocSwap/integer-mult-bounds/pull/873) | navinor | incorporated | [record 1](../../research/community-batch952-audit/DISPOSITIONS.json) |
| [#874](https://github.com/CrocSwap/integer-mult-bounds/pull/874) | AmnonTamsut | incorporated | [record 1](../../research/community-frontier890-audit/DISPOSITIONS.json) |
| [#875](https://github.com/CrocSwap/integer-mult-bounds/pull/875) | mightyOil | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#876](https://github.com/CrocSwap/integer-mult-bounds/pull/876) | navinor | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#877](https://github.com/CrocSwap/integer-mult-bounds/pull/877) | bitplane | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#879](https://github.com/CrocSwap/integer-mult-bounds/pull/879) | mightyOil | incorporated | [record 1](../../research/community-batch932-audit/DISPOSITIONS.json) |
| [#880](https://github.com/CrocSwap/integer-mult-bounds/pull/880) | Deftsalt-debug | incorporated | [record 1](../../research/community-batch952-audit/DISPOSITIONS.json) |
| [#881](https://github.com/CrocSwap/integer-mult-bounds/pull/881) | SethBurkart123 | incorporated | [record 1](../../research/community-frontier890-audit/DISPOSITIONS.json) |
| [#882](https://github.com/CrocSwap/integer-mult-bounds/pull/882) | mightyOil | incorporated | [record 1](../../research/community-batch932-audit/DISPOSITIONS.json) |
| [#883](https://github.com/CrocSwap/integer-mult-bounds/pull/883) | mightyOil | incorporated | [record 1](../../research/community-batch932-audit/DISPOSITIONS.json) |
| [#884](https://github.com/CrocSwap/integer-mult-bounds/pull/884) | martinxxx9 | incorporated | [record 1](../../research/community-batch932-audit/DISPOSITIONS.json) |
| [#886](https://github.com/CrocSwap/integer-mult-bounds/pull/886) | SethBurkart123 | incorporated | [record 1](../../research/community-frontier890-audit/DISPOSITIONS.json) |
| [#887](https://github.com/CrocSwap/integer-mult-bounds/pull/887) | bitplane | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#888](https://github.com/CrocSwap/integer-mult-bounds/pull/888) | ToikY | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#889](https://github.com/CrocSwap/integer-mult-bounds/pull/889) | CubeJerry | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#890](https://github.com/CrocSwap/integer-mult-bounds/pull/890) | chafreaky | incorporated | [record 1](../../research/community-frontier890-audit/DISPOSITIONS.json) |
| [#891](https://github.com/CrocSwap/integer-mult-bounds/pull/891) | navinor | incorporated | [record 1](../../research/community-batch932-audit/DISPOSITIONS.json) |
| [#892](https://github.com/CrocSwap/integer-mult-bounds/pull/892) | nightangelflowerwin-ops | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#893](https://github.com/CrocSwap/integer-mult-bounds/pull/893) | WeberChen8128 | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#894](https://github.com/CrocSwap/integer-mult-bounds/pull/894) | navinor | incorporated | [record 1](../../research/community-frontier890-audit/DISPOSITIONS.json) |
| [#895](https://github.com/CrocSwap/integer-mult-bounds/pull/895) | DaysSky | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#896](https://github.com/CrocSwap/integer-mult-bounds/pull/896) | bitplane | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#897](https://github.com/CrocSwap/integer-mult-bounds/pull/897) | DaysSky | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#898](https://github.com/CrocSwap/integer-mult-bounds/pull/898) | CubeJerry | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#899](https://github.com/CrocSwap/integer-mult-bounds/pull/899) | DreamingOfClouds | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#900](https://github.com/CrocSwap/integer-mult-bounds/pull/900) | ToikY | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#901](https://github.com/CrocSwap/integer-mult-bounds/pull/901) | ToikY | incorporated | [record 1](../../research/community-batch932-audit/DISPOSITIONS.json) |
| [#902](https://github.com/CrocSwap/integer-mult-bounds/pull/902) | bg-grillo-alan | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#903](https://github.com/CrocSwap/integer-mult-bounds/pull/903) | just-mn | incorporated | [record 1](../../research/community-batch932-audit/DISPOSITIONS.json) |
| [#904](https://github.com/CrocSwap/integer-mult-bounds/pull/904) | bitplane | incorporated | [record 1](../../research/community-batch952-audit/DISPOSITIONS.json) |
| [#905](https://github.com/CrocSwap/integer-mult-bounds/pull/905) | chafreaky | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#906](https://github.com/CrocSwap/integer-mult-bounds/pull/906) | CubeJerry | incorporated | [record 1](../../research/community-batch952-audit/DISPOSITIONS.json) |
| [#907](https://github.com/CrocSwap/integer-mult-bounds/pull/907) | CubeJerry | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#908](https://github.com/CrocSwap/integer-mult-bounds/pull/908) | RossRichardson | incorporated | [record 1](../../research/community-batch952-audit/DISPOSITIONS.json) |
| [#909](https://github.com/CrocSwap/integer-mult-bounds/pull/909) | ToikY | incorporated | [record 1](../../research/community-frontier890-audit/DISPOSITIONS.json) |
| [#910](https://github.com/CrocSwap/integer-mult-bounds/pull/910) | navinor | incorporated | [record 1](../../research/community-frontier890-audit/DISPOSITIONS.json) |
| [#911](https://github.com/CrocSwap/integer-mult-bounds/pull/911) | ToikY | incorporated | [record 1](../../research/community-frontier890-audit/DISPOSITIONS.json) |
| [#912](https://github.com/CrocSwap/integer-mult-bounds/pull/912) | CubeJerry | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#914](https://github.com/CrocSwap/integer-mult-bounds/pull/914) | RossRichardson | incorporated | [record 1](../../research/community-batch952-audit/DISPOSITIONS.json) |
| [#915](https://github.com/CrocSwap/integer-mult-bounds/pull/915) | bitplane | incorporated | [record 1](../../research/community-batch932-audit/DISPOSITIONS.json) |
| [#916](https://github.com/CrocSwap/integer-mult-bounds/pull/916) | nightangelflowerwin-ops | incorporated | [record 1](../../research/community-batch932-audit/DISPOSITIONS.json) |
| [#917](https://github.com/CrocSwap/integer-mult-bounds/pull/917) | RossRichardson | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#918](https://github.com/CrocSwap/integer-mult-bounds/pull/918) | RossRichardson | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#919](https://github.com/CrocSwap/integer-mult-bounds/pull/919) | RossRichardson | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#920](https://github.com/CrocSwap/integer-mult-bounds/pull/920) | ArnavSwiggy | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#921](https://github.com/CrocSwap/integer-mult-bounds/pull/921) | navinor | incorporated | [record 1](../../research/community-batch932-audit/DISPOSITIONS.json) |
| [#922](https://github.com/CrocSwap/integer-mult-bounds/pull/922) | CubeJerry | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#923](https://github.com/CrocSwap/integer-mult-bounds/pull/923) | RossRichardson | incorporated | [record 1](../../research/community-batch952-audit/DISPOSITIONS.json) |
| [#924](https://github.com/CrocSwap/integer-mult-bounds/pull/924) | CubeJerry | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#925](https://github.com/CrocSwap/integer-mult-bounds/pull/925) | RossRichardson | incorporated | [record 1](../../research/community-batch952-audit/DISPOSITIONS.json) |
| [#926](https://github.com/CrocSwap/integer-mult-bounds/pull/926) | bitplane | incorporated | [record 1](../../research/community-batch932-audit/DISPOSITIONS.json) |
| [#927](https://github.com/CrocSwap/integer-mult-bounds/pull/927) | RossRichardson | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#928](https://github.com/CrocSwap/integer-mult-bounds/pull/928) | rohanarun | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#929](https://github.com/CrocSwap/integer-mult-bounds/pull/929) | chafreaky | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#930](https://github.com/CrocSwap/integer-mult-bounds/pull/930) | RossRichardson | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#931](https://github.com/CrocSwap/integer-mult-bounds/pull/931) | RossRichardson | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#932](https://github.com/CrocSwap/integer-mult-bounds/pull/932) | RossRichardson | incorporated | [record 1](../../research/community-batch932-audit/DISPOSITIONS.json) |
| [#933](https://github.com/CrocSwap/integer-mult-bounds/pull/933) | ianlibanio | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#934](https://github.com/CrocSwap/integer-mult-bounds/pull/934) | RossRichardson | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#936](https://github.com/CrocSwap/integer-mult-bounds/pull/936) | RossRichardson | incorporated | [record 1](../../research/community-batch952-audit/DISPOSITIONS.json) |
| [#937](https://github.com/CrocSwap/integer-mult-bounds/pull/937) | RossRichardson | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#938](https://github.com/CrocSwap/integer-mult-bounds/pull/938) | RossRichardson | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#939](https://github.com/CrocSwap/integer-mult-bounds/pull/939) | RossRichardson | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#940](https://github.com/CrocSwap/integer-mult-bounds/pull/940) | RossRichardson | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#941](https://github.com/CrocSwap/integer-mult-bounds/pull/941) | bitplane | incorporated | [record 1](../../research/community-batch952-audit/DISPOSITIONS.json) |
| [#942](https://github.com/CrocSwap/integer-mult-bounds/pull/942) | jon314159 | incorporated | [record 1](../../research/community-batch952-audit/DISPOSITIONS.json) |
| [#943](https://github.com/CrocSwap/integer-mult-bounds/pull/943) | RossRichardson | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#944](https://github.com/CrocSwap/integer-mult-bounds/pull/944) | RossRichardson | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#945](https://github.com/CrocSwap/integer-mult-bounds/pull/945) | RossRichardson | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#946](https://github.com/CrocSwap/integer-mult-bounds/pull/946) | navinor | partially reviewed | [record 1](../../research/community-batch952-audit/DISPOSITIONS.json) · [record 2](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#947](https://github.com/CrocSwap/integer-mult-bounds/pull/947) | RossRichardson | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#948](https://github.com/CrocSwap/integer-mult-bounds/pull/948) | RossRichardson | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#949](https://github.com/CrocSwap/integer-mult-bounds/pull/949) | RossRichardson | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#950](https://github.com/CrocSwap/integer-mult-bounds/pull/950) | RossRichardson | incorporated | [record 1](../../research/community-batch952-audit/DISPOSITIONS.json) |
| [#951](https://github.com/CrocSwap/integer-mult-bounds/pull/951) | chafreaky | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#952](https://github.com/CrocSwap/integer-mult-bounds/pull/952) | bitplane | incorporated | [record 1](../../research/community-batch952-audit/DISPOSITIONS.json) |
| [#953](https://github.com/CrocSwap/integer-mult-bounds/pull/953) | RossRichardson | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#954](https://github.com/CrocSwap/integer-mult-bounds/pull/954) | RossRichardson | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#955](https://github.com/CrocSwap/integer-mult-bounds/pull/955) | littleBro | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#957](https://github.com/CrocSwap/integer-mult-bounds/pull/957) | navinor | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#958](https://github.com/CrocSwap/integer-mult-bounds/pull/958) | RossRichardson | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#959](https://github.com/CrocSwap/integer-mult-bounds/pull/959) | yssite | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#960](https://github.com/CrocSwap/integer-mult-bounds/pull/960) | davidNbreslauer | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#961](https://github.com/CrocSwap/integer-mult-bounds/pull/961) | woklerx | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#962](https://github.com/CrocSwap/integer-mult-bounds/pull/962) | GamingPuzzled | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#963](https://github.com/CrocSwap/integer-mult-bounds/pull/963) | ToikY | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#964](https://github.com/CrocSwap/integer-mult-bounds/pull/964) | bitplane | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#965](https://github.com/CrocSwap/integer-mult-bounds/pull/965) | RossRichardson | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#966](https://github.com/CrocSwap/integer-mult-bounds/pull/966) | woklerx | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#967](https://github.com/CrocSwap/integer-mult-bounds/pull/967) | theon199 | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#968](https://github.com/CrocSwap/integer-mult-bounds/pull/968) | themilkman216 | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#969](https://github.com/CrocSwap/integer-mult-bounds/pull/969) | ToikY | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#970](https://github.com/CrocSwap/integer-mult-bounds/pull/970) | woklerx | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#971](https://github.com/CrocSwap/integer-mult-bounds/pull/971) | ToikY | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#972](https://github.com/CrocSwap/integer-mult-bounds/pull/972) | ToikY | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#973](https://github.com/CrocSwap/integer-mult-bounds/pull/973) | 1337isnot1337 | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#974](https://github.com/CrocSwap/integer-mult-bounds/pull/974) | avirazza | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#975](https://github.com/CrocSwap/integer-mult-bounds/pull/975) | ToikY | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#976](https://github.com/CrocSwap/integer-mult-bounds/pull/976) | martinxxx9 | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#977](https://github.com/CrocSwap/integer-mult-bounds/pull/977) | chafreaky | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#978](https://github.com/CrocSwap/integer-mult-bounds/pull/978) | franciscoyne001-svg | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#979](https://github.com/CrocSwap/integer-mult-bounds/pull/979) | DLamdata | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#980](https://github.com/CrocSwap/integer-mult-bounds/pull/980) | bitplane | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#981](https://github.com/CrocSwap/integer-mult-bounds/pull/981) | ToikY | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#982](https://github.com/CrocSwap/integer-mult-bounds/pull/982) | RossRichardson | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#984](https://github.com/CrocSwap/integer-mult-bounds/pull/984) | ToikY | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#985](https://github.com/CrocSwap/integer-mult-bounds/pull/985) | aliromman | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#986](https://github.com/CrocSwap/integer-mult-bounds/pull/986) | woklerx | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#987](https://github.com/CrocSwap/integer-mult-bounds/pull/987) | rohanarun | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#988](https://github.com/CrocSwap/integer-mult-bounds/pull/988) | ToikY | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#989](https://github.com/CrocSwap/integer-mult-bounds/pull/989) | woklerx | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#990](https://github.com/CrocSwap/integer-mult-bounds/pull/990) | thakrarsagar | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#991](https://github.com/CrocSwap/integer-mult-bounds/pull/991) | tekuuu | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#992](https://github.com/CrocSwap/integer-mult-bounds/pull/992) | woklerx | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#993](https://github.com/CrocSwap/integer-mult-bounds/pull/993) | woklerx | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#994](https://github.com/CrocSwap/integer-mult-bounds/pull/994) | woklerx | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#995](https://github.com/CrocSwap/integer-mult-bounds/pull/995) | woklerx | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#996](https://github.com/CrocSwap/integer-mult-bounds/pull/996) | woklerx | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#997](https://github.com/CrocSwap/integer-mult-bounds/pull/997) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#998](https://github.com/CrocSwap/integer-mult-bounds/pull/998) | woklerx | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#999](https://github.com/CrocSwap/integer-mult-bounds/pull/999) | ZK-Snarky | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1000](https://github.com/CrocSwap/integer-mult-bounds/pull/1000) | ToikY | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#1001](https://github.com/CrocSwap/integer-mult-bounds/pull/1001) | ToikY | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#1002](https://github.com/CrocSwap/integer-mult-bounds/pull/1002) | woklerx | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#1003](https://github.com/CrocSwap/integer-mult-bounds/pull/1003) | ToikY | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1004](https://github.com/CrocSwap/integer-mult-bounds/pull/1004) | jeremykothe2 | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#1005](https://github.com/CrocSwap/integer-mult-bounds/pull/1005) | jeremykothe2 | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#1006](https://github.com/CrocSwap/integer-mult-bounds/pull/1006) | bitplane | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#1007](https://github.com/CrocSwap/integer-mult-bounds/pull/1007) | RossRichardson | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1008](https://github.com/CrocSwap/integer-mult-bounds/pull/1008) | woklerx | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1009](https://github.com/CrocSwap/integer-mult-bounds/pull/1009) | woklerx | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#1010](https://github.com/CrocSwap/integer-mult-bounds/pull/1010) | cbethin | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#1011](https://github.com/CrocSwap/integer-mult-bounds/pull/1011) | woklerx | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1012](https://github.com/CrocSwap/integer-mult-bounds/pull/1012) | thakrarsagar | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1013](https://github.com/CrocSwap/integer-mult-bounds/pull/1013) | martinxxx9 | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1014](https://github.com/CrocSwap/integer-mult-bounds/pull/1014) | thakrarsagar | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1015](https://github.com/CrocSwap/integer-mult-bounds/pull/1015) | navinor | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient300-audit/PARENT-EVIDENCE.json) |
| [#1016](https://github.com/CrocSwap/integer-mult-bounds/pull/1016) | ToikY | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1017](https://github.com/CrocSwap/integer-mult-bounds/pull/1017) | woklerx | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1018](https://github.com/CrocSwap/integer-mult-bounds/pull/1018) | jeremykothe2 | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#1019](https://github.com/CrocSwap/integer-mult-bounds/pull/1019) | 1337isnot1337 | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#1020](https://github.com/CrocSwap/integer-mult-bounds/pull/1020) | woklerx | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#1021](https://github.com/CrocSwap/integer-mult-bounds/pull/1021) | woklerx | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1022](https://github.com/CrocSwap/integer-mult-bounds/pull/1022) | jeremykothe2 | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#1023](https://github.com/CrocSwap/integer-mult-bounds/pull/1023) | thakrarsagar | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1024](https://github.com/CrocSwap/integer-mult-bounds/pull/1024) | bbMisk | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1025](https://github.com/CrocSwap/integer-mult-bounds/pull/1025) | chafreaky | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1026](https://github.com/CrocSwap/integer-mult-bounds/pull/1026) | aliromman | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1027](https://github.com/CrocSwap/integer-mult-bounds/pull/1027) | bbMisk | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1028](https://github.com/CrocSwap/integer-mult-bounds/pull/1028) | jeremykothe2 | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#1029](https://github.com/CrocSwap/integer-mult-bounds/pull/1029) | aliromman | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#1030](https://github.com/CrocSwap/integer-mult-bounds/pull/1030) | AlexS-scale | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#1031](https://github.com/CrocSwap/integer-mult-bounds/pull/1031) | jeremykothe2 | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#1032](https://github.com/CrocSwap/integer-mult-bounds/pull/1032) | woklerx | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1033](https://github.com/CrocSwap/integer-mult-bounds/pull/1033) | bbMisk | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1034](https://github.com/CrocSwap/integer-mult-bounds/pull/1034) | aliromman | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1035](https://github.com/CrocSwap/integer-mult-bounds/pull/1035) | woklerx | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#1036](https://github.com/CrocSwap/integer-mult-bounds/pull/1036) | bbMisk | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1038](https://github.com/CrocSwap/integer-mult-bounds/pull/1038) | aliromman | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1039](https://github.com/CrocSwap/integer-mult-bounds/pull/1039) | RossRichardson | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1040](https://github.com/CrocSwap/integer-mult-bounds/pull/1040) | woklerx | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#1041](https://github.com/CrocSwap/integer-mult-bounds/pull/1041) | thakrarsagar | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#1042](https://github.com/CrocSwap/integer-mult-bounds/pull/1042) | jeremykothe2 | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#1043](https://github.com/CrocSwap/integer-mult-bounds/pull/1043) | aliromman | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1044](https://github.com/CrocSwap/integer-mult-bounds/pull/1044) | steph4n-gh | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1045](https://github.com/CrocSwap/integer-mult-bounds/pull/1045) | thakrarsagar | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1046](https://github.com/CrocSwap/integer-mult-bounds/pull/1046) | martinxxx9 | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1047](https://github.com/CrocSwap/integer-mult-bounds/pull/1047) | woklerx | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#1048](https://github.com/CrocSwap/integer-mult-bounds/pull/1048) | flemhhh | partially reviewed | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1049](https://github.com/CrocSwap/integer-mult-bounds/pull/1049) | thakrarsagar | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1050](https://github.com/CrocSwap/integer-mult-bounds/pull/1050) | jeremykothe2 | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1051](https://github.com/CrocSwap/integer-mult-bounds/pull/1051) | thakrarsagar | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1052](https://github.com/CrocSwap/integer-mult-bounds/pull/1052) | steph4n-gh | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1053](https://github.com/CrocSwap/integer-mult-bounds/pull/1053) | jeremykothe2 | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1054](https://github.com/CrocSwap/integer-mult-bounds/pull/1054) | aliromman | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1055](https://github.com/CrocSwap/integer-mult-bounds/pull/1055) | jeremykothe2 | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1056](https://github.com/CrocSwap/integer-mult-bounds/pull/1056) | rohanarun | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1057](https://github.com/CrocSwap/integer-mult-bounds/pull/1057) | bitplane | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1058](https://github.com/CrocSwap/integer-mult-bounds/pull/1058) | cbarber1 | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1059](https://github.com/CrocSwap/integer-mult-bounds/pull/1059) | thakrarsagar | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1060](https://github.com/CrocSwap/integer-mult-bounds/pull/1060) | aliromman | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1061](https://github.com/CrocSwap/integer-mult-bounds/pull/1061) | jeremykothe2 | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1062](https://github.com/CrocSwap/integer-mult-bounds/pull/1062) | thakrarsagar | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1063](https://github.com/CrocSwap/integer-mult-bounds/pull/1063) | rohanarun | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1064](https://github.com/CrocSwap/integer-mult-bounds/pull/1064) | aliromman | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1065](https://github.com/CrocSwap/integer-mult-bounds/pull/1065) | jeremykothe2 | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1066](https://github.com/CrocSwap/integer-mult-bounds/pull/1066) | woklerx | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1067](https://github.com/CrocSwap/integer-mult-bounds/pull/1067) | woklerx | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1068](https://github.com/CrocSwap/integer-mult-bounds/pull/1068) | jeremykothe2 | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1069](https://github.com/CrocSwap/integer-mult-bounds/pull/1069) | thakrarsagar | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1070](https://github.com/CrocSwap/integer-mult-bounds/pull/1070) | bbMisk | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1071](https://github.com/CrocSwap/integer-mult-bounds/pull/1071) | JosieElliston | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1072](https://github.com/CrocSwap/integer-mult-bounds/pull/1072) | davidNbreslauer | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1073](https://github.com/CrocSwap/integer-mult-bounds/pull/1073) | thakrarsagar | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1074](https://github.com/CrocSwap/integer-mult-bounds/pull/1074) | jeremykothe2 | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1075](https://github.com/CrocSwap/integer-mult-bounds/pull/1075) | RossRichardson | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1076](https://github.com/CrocSwap/integer-mult-bounds/pull/1076) | navinor | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1077](https://github.com/CrocSwap/integer-mult-bounds/pull/1077) | woklerx | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1078](https://github.com/CrocSwap/integer-mult-bounds/pull/1078) | bbMisk | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1079](https://github.com/CrocSwap/integer-mult-bounds/pull/1079) | bbMisk | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1080](https://github.com/CrocSwap/integer-mult-bounds/pull/1080) | steph4n-gh | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1081](https://github.com/CrocSwap/integer-mult-bounds/pull/1081) | steph4n-gh | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1082](https://github.com/CrocSwap/integer-mult-bounds/pull/1082) | rohanarun | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1083](https://github.com/CrocSwap/integer-mult-bounds/pull/1083) | bbMisk | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1084](https://github.com/CrocSwap/integer-mult-bounds/pull/1084) | navinor | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1085](https://github.com/CrocSwap/integer-mult-bounds/pull/1085) | bbMisk | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1086](https://github.com/CrocSwap/integer-mult-bounds/pull/1086) | Hope7Happiness | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1087](https://github.com/CrocSwap/integer-mult-bounds/pull/1087) | jeremykothe2 | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1088](https://github.com/CrocSwap/integer-mult-bounds/pull/1088) | martinxxx9 | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1089](https://github.com/CrocSwap/integer-mult-bounds/pull/1089) | martinxxx9 | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1090](https://github.com/CrocSwap/integer-mult-bounds/pull/1090) | 1337isnot1337 | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1091](https://github.com/CrocSwap/integer-mult-bounds/pull/1091) | JosieElliston | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1092](https://github.com/CrocSwap/integer-mult-bounds/pull/1092) | ToikY | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1093](https://github.com/CrocSwap/integer-mult-bounds/pull/1093) | woklerx | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1094](https://github.com/CrocSwap/integer-mult-bounds/pull/1094) | rohanarun | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1095](https://github.com/CrocSwap/integer-mult-bounds/pull/1095) | woklerx | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1096](https://github.com/CrocSwap/integer-mult-bounds/pull/1096) | woklerx | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1097](https://github.com/CrocSwap/integer-mult-bounds/pull/1097) | bitplane | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1098](https://github.com/CrocSwap/integer-mult-bounds/pull/1098) | adamgall | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1099](https://github.com/CrocSwap/integer-mult-bounds/pull/1099) | woklerx | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1100](https://github.com/CrocSwap/integer-mult-bounds/pull/1100) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1101](https://github.com/CrocSwap/integer-mult-bounds/pull/1101) | rcfc-jreed | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1102](https://github.com/CrocSwap/integer-mult-bounds/pull/1102) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1103](https://github.com/CrocSwap/integer-mult-bounds/pull/1103) | steph4n-gh | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1104](https://github.com/CrocSwap/integer-mult-bounds/pull/1104) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1105](https://github.com/CrocSwap/integer-mult-bounds/pull/1105) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1106](https://github.com/CrocSwap/integer-mult-bounds/pull/1106) | ToikY | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1107](https://github.com/CrocSwap/integer-mult-bounds/pull/1107) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1108](https://github.com/CrocSwap/integer-mult-bounds/pull/1108) | martinxxx9 | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1110](https://github.com/CrocSwap/integer-mult-bounds/pull/1110) | RossRichardson | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1111](https://github.com/CrocSwap/integer-mult-bounds/pull/1111) | seslly | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1112](https://github.com/CrocSwap/integer-mult-bounds/pull/1112) | Wronskode | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1113](https://github.com/CrocSwap/integer-mult-bounds/pull/1113) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1114](https://github.com/CrocSwap/integer-mult-bounds/pull/1114) | adamgall | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1115](https://github.com/CrocSwap/integer-mult-bounds/pull/1115) | martinxxx9 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1116](https://github.com/CrocSwap/integer-mult-bounds/pull/1116) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1117](https://github.com/CrocSwap/integer-mult-bounds/pull/1117) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1118](https://github.com/CrocSwap/integer-mult-bounds/pull/1118) | ToikY | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1119](https://github.com/CrocSwap/integer-mult-bounds/pull/1119) | steph4n-gh | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1120](https://github.com/CrocSwap/integer-mult-bounds/pull/1120) | aliromman | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1121](https://github.com/CrocSwap/integer-mult-bounds/pull/1121) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1122](https://github.com/CrocSwap/integer-mult-bounds/pull/1122) | bitplane | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1123](https://github.com/CrocSwap/integer-mult-bounds/pull/1123) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1124](https://github.com/CrocSwap/integer-mult-bounds/pull/1124) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1125](https://github.com/CrocSwap/integer-mult-bounds/pull/1125) | aliromman | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1126](https://github.com/CrocSwap/integer-mult-bounds/pull/1126) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1127](https://github.com/CrocSwap/integer-mult-bounds/pull/1127) | navinor | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1128](https://github.com/CrocSwap/integer-mult-bounds/pull/1128) | aliromman | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1129](https://github.com/CrocSwap/integer-mult-bounds/pull/1129) | aliromman | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1130](https://github.com/CrocSwap/integer-mult-bounds/pull/1130) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1131](https://github.com/CrocSwap/integer-mult-bounds/pull/1131) | chafreaky | partially reviewed | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1132](https://github.com/CrocSwap/integer-mult-bounds/pull/1132) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1133](https://github.com/CrocSwap/integer-mult-bounds/pull/1133) | thakrarsagar | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1134](https://github.com/CrocSwap/integer-mult-bounds/pull/1134) | aliromman | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1135](https://github.com/CrocSwap/integer-mult-bounds/pull/1135) | aliromman | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1136](https://github.com/CrocSwap/integer-mult-bounds/pull/1136) | aliromman | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1137](https://github.com/CrocSwap/integer-mult-bounds/pull/1137) | Wronskode | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1138](https://github.com/CrocSwap/integer-mult-bounds/pull/1138) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1139](https://github.com/CrocSwap/integer-mult-bounds/pull/1139) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1140](https://github.com/CrocSwap/integer-mult-bounds/pull/1140) | aliromman | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1141](https://github.com/CrocSwap/integer-mult-bounds/pull/1141) | aliromman | partially reviewed | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1142](https://github.com/CrocSwap/integer-mult-bounds/pull/1142) | martinxxx9 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1143](https://github.com/CrocSwap/integer-mult-bounds/pull/1143) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1144](https://github.com/CrocSwap/integer-mult-bounds/pull/1144) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1145](https://github.com/CrocSwap/integer-mult-bounds/pull/1145) | RossRichardson | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1147](https://github.com/CrocSwap/integer-mult-bounds/pull/1147) | RaphaelFakhri | partially reviewed | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1148](https://github.com/CrocSwap/integer-mult-bounds/pull/1148) | tomdif | partially reviewed | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1149](https://github.com/CrocSwap/integer-mult-bounds/pull/1149) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1150](https://github.com/CrocSwap/integer-mult-bounds/pull/1150) | rohanarun | partially reviewed | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1151](https://github.com/CrocSwap/integer-mult-bounds/pull/1151) | thakrarsagar | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1152](https://github.com/CrocSwap/integer-mult-bounds/pull/1152) | chafreaky | partially reviewed | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1153](https://github.com/CrocSwap/integer-mult-bounds/pull/1153) | Scratch-net | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1154](https://github.com/CrocSwap/integer-mult-bounds/pull/1154) | Dugongue | partially reviewed | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1155](https://github.com/CrocSwap/integer-mult-bounds/pull/1155) | navinor | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1156](https://github.com/CrocSwap/integer-mult-bounds/pull/1156) | thakrarsagar | partially reviewed | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1157](https://github.com/CrocSwap/integer-mult-bounds/pull/1157) | rohanarun | partially reviewed | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1158](https://github.com/CrocSwap/integer-mult-bounds/pull/1158) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1159](https://github.com/CrocSwap/integer-mult-bounds/pull/1159) | bitplane | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1160](https://github.com/CrocSwap/integer-mult-bounds/pull/1160) | Hope7Happiness | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1161](https://github.com/CrocSwap/integer-mult-bounds/pull/1161) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1162](https://github.com/CrocSwap/integer-mult-bounds/pull/1162) | brianross93 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#1164](https://github.com/CrocSwap/integer-mult-bounds/pull/1164) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1165](https://github.com/CrocSwap/integer-mult-bounds/pull/1165) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1168](https://github.com/CrocSwap/integer-mult-bounds/pull/1168) | thakrarsagar | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1169](https://github.com/CrocSwap/integer-mult-bounds/pull/1169) | rohanarun | partially reviewed | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1170](https://github.com/CrocSwap/integer-mult-bounds/pull/1170) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1171](https://github.com/CrocSwap/integer-mult-bounds/pull/1171) | 3xcalibur-tech | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1172](https://github.com/CrocSwap/integer-mult-bounds/pull/1172) | midhatn | partially reviewed | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1173](https://github.com/CrocSwap/integer-mult-bounds/pull/1173) | ToikY | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1174](https://github.com/CrocSwap/integer-mult-bounds/pull/1174) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1175](https://github.com/CrocSwap/integer-mult-bounds/pull/1175) | gvconly | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1176](https://github.com/CrocSwap/integer-mult-bounds/pull/1176) | Dugongue | partially reviewed | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1177](https://github.com/CrocSwap/integer-mult-bounds/pull/1177) | RossRichardson | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1178](https://github.com/CrocSwap/integer-mult-bounds/pull/1178) | rohanarun | partially reviewed | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1179](https://github.com/CrocSwap/integer-mult-bounds/pull/1179) | adamgall | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1180](https://github.com/CrocSwap/integer-mult-bounds/pull/1180) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1181](https://github.com/CrocSwap/integer-mult-bounds/pull/1181) | thakrarsagar | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1182](https://github.com/CrocSwap/integer-mult-bounds/pull/1182) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1183](https://github.com/CrocSwap/integer-mult-bounds/pull/1183) | rohanarun | partially reviewed | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1184](https://github.com/CrocSwap/integer-mult-bounds/pull/1184) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1185](https://github.com/CrocSwap/integer-mult-bounds/pull/1185) | Mister-Meeseeks | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1186](https://github.com/CrocSwap/integer-mult-bounds/pull/1186) | mdumitrean | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1187](https://github.com/CrocSwap/integer-mult-bounds/pull/1187) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1188](https://github.com/CrocSwap/integer-mult-bounds/pull/1188) | bitplane | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1189](https://github.com/CrocSwap/integer-mult-bounds/pull/1189) | mightyOil | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1190](https://github.com/CrocSwap/integer-mult-bounds/pull/1190) | adamgall | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1191](https://github.com/CrocSwap/integer-mult-bounds/pull/1191) | mightyOil | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1192](https://github.com/CrocSwap/integer-mult-bounds/pull/1192) | rohanarun | partially reviewed | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1193](https://github.com/CrocSwap/integer-mult-bounds/pull/1193) | jeremydiviney | partially reviewed | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1194](https://github.com/CrocSwap/integer-mult-bounds/pull/1194) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1195](https://github.com/CrocSwap/integer-mult-bounds/pull/1195) | mdumitrean | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1196](https://github.com/CrocSwap/integer-mult-bounds/pull/1196) | chafreaky | partially reviewed | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1197](https://github.com/CrocSwap/integer-mult-bounds/pull/1197) | mightyOil | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1198](https://github.com/CrocSwap/integer-mult-bounds/pull/1198) | Scratch-net | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1199](https://github.com/CrocSwap/integer-mult-bounds/pull/1199) | thakrarsagar | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1201](https://github.com/CrocSwap/integer-mult-bounds/pull/1201) | rohanarun | partially reviewed | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1203](https://github.com/CrocSwap/integer-mult-bounds/pull/1203) | mightyOil | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1204](https://github.com/CrocSwap/integer-mult-bounds/pull/1204) | GamingPuzzled | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#1205](https://github.com/CrocSwap/integer-mult-bounds/pull/1205) | adamgall | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1206](https://github.com/CrocSwap/integer-mult-bounds/pull/1206) | adamgall | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1207](https://github.com/CrocSwap/integer-mult-bounds/pull/1207) | rohanarun | partially reviewed | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1208](https://github.com/CrocSwap/integer-mult-bounds/pull/1208) | ToikY | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1209](https://github.com/CrocSwap/integer-mult-bounds/pull/1209) | akiva8201-dotcom | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1211](https://github.com/CrocSwap/integer-mult-bounds/pull/1211) | cbethin | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1212](https://github.com/CrocSwap/integer-mult-bounds/pull/1212) | burntout76 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1213](https://github.com/CrocSwap/integer-mult-bounds/pull/1213) | DavidAriasC | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1214](https://github.com/CrocSwap/integer-mult-bounds/pull/1214) | bbMisk | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1215](https://github.com/CrocSwap/integer-mult-bounds/pull/1215) | bbMisk | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1216](https://github.com/CrocSwap/integer-mult-bounds/pull/1216) | RossRichardson | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1217](https://github.com/CrocSwap/integer-mult-bounds/pull/1217) | bbMisk | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1218](https://github.com/CrocSwap/integer-mult-bounds/pull/1218) | rohanarun | partially reviewed | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1219](https://github.com/CrocSwap/integer-mult-bounds/pull/1219) | bbMisk | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1220](https://github.com/CrocSwap/integer-mult-bounds/pull/1220) | adamgall | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1221](https://github.com/CrocSwap/integer-mult-bounds/pull/1221) | bbMisk | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1222](https://github.com/CrocSwap/integer-mult-bounds/pull/1222) | bbMisk | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1223](https://github.com/CrocSwap/integer-mult-bounds/pull/1223) | zewelor | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1224](https://github.com/CrocSwap/integer-mult-bounds/pull/1224) | joaqcoo | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1225](https://github.com/CrocSwap/integer-mult-bounds/pull/1225) | rohanarun | partially reviewed | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1226](https://github.com/CrocSwap/integer-mult-bounds/pull/1226) | navinor | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1227](https://github.com/CrocSwap/integer-mult-bounds/pull/1227) | thakrarsagar | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1228](https://github.com/CrocSwap/integer-mult-bounds/pull/1228) | Mister-Meeseeks | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1229](https://github.com/CrocSwap/integer-mult-bounds/pull/1229) | bitplane | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1230](https://github.com/CrocSwap/integer-mult-bounds/pull/1230) | ToikY | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1231](https://github.com/CrocSwap/integer-mult-bounds/pull/1231) | Mister-Meeseeks | partially reviewed | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1232](https://github.com/CrocSwap/integer-mult-bounds/pull/1232) | Mister-Meeseeks | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1234](https://github.com/CrocSwap/integer-mult-bounds/pull/1234) | RichardHoekstra | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1235](https://github.com/CrocSwap/integer-mult-bounds/pull/1235) | RichardHoekstra | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1236](https://github.com/CrocSwap/integer-mult-bounds/pull/1236) | DavidAriasC | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1238](https://github.com/CrocSwap/integer-mult-bounds/pull/1238) | DreamingOfClouds | partially reviewed | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1239](https://github.com/CrocSwap/integer-mult-bounds/pull/1239) | GamingPuzzled | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#1242](https://github.com/CrocSwap/integer-mult-bounds/pull/1242) | bbMisk | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1243](https://github.com/CrocSwap/integer-mult-bounds/pull/1243) | bbMisk | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1244](https://github.com/CrocSwap/integer-mult-bounds/pull/1244) | bbMisk | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1245](https://github.com/CrocSwap/integer-mult-bounds/pull/1245) | bbMisk | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1246](https://github.com/CrocSwap/integer-mult-bounds/pull/1246) | bbMisk | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1247](https://github.com/CrocSwap/integer-mult-bounds/pull/1247) | bbMisk | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1248](https://github.com/CrocSwap/integer-mult-bounds/pull/1248) | mightyOil | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1249](https://github.com/CrocSwap/integer-mult-bounds/pull/1249) | bbMisk | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1250](https://github.com/CrocSwap/integer-mult-bounds/pull/1250) | bbMisk | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1252](https://github.com/CrocSwap/integer-mult-bounds/pull/1252) | Gonzalo-Mier | partially reviewed | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1253](https://github.com/CrocSwap/integer-mult-bounds/pull/1253) | mightyOil | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1254](https://github.com/CrocSwap/integer-mult-bounds/pull/1254) | mightyOil | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1255](https://github.com/CrocSwap/integer-mult-bounds/pull/1255) | bitplane | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1256](https://github.com/CrocSwap/integer-mult-bounds/pull/1256) | RossRichardson | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1257](https://github.com/CrocSwap/integer-mult-bounds/pull/1257) | bbMisk | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1259](https://github.com/CrocSwap/integer-mult-bounds/pull/1259) | thakrarsagar | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1261](https://github.com/CrocSwap/integer-mult-bounds/pull/1261) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1262](https://github.com/CrocSwap/integer-mult-bounds/pull/1262) | thakrarsagar | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1263](https://github.com/CrocSwap/integer-mult-bounds/pull/1263) | mightyOil | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1266](https://github.com/CrocSwap/integer-mult-bounds/pull/1266) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1270](https://github.com/CrocSwap/integer-mult-bounds/pull/1270) | mightyOil | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1271](https://github.com/CrocSwap/integer-mult-bounds/pull/1271) | mightyOil | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1273](https://github.com/CrocSwap/integer-mult-bounds/pull/1273) | theon199 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1274](https://github.com/CrocSwap/integer-mult-bounds/pull/1274) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1276](https://github.com/CrocSwap/integer-mult-bounds/pull/1276) | PatatePatatePatate | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1277](https://github.com/CrocSwap/integer-mult-bounds/pull/1277) | thakrarsagar | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1278](https://github.com/CrocSwap/integer-mult-bounds/pull/1278) | cbethin | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1281](https://github.com/CrocSwap/integer-mult-bounds/pull/1281) | mightyOil | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1282](https://github.com/CrocSwap/integer-mult-bounds/pull/1282) | bitplane | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1284](https://github.com/CrocSwap/integer-mult-bounds/pull/1284) | thakrarsagar | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1285](https://github.com/CrocSwap/integer-mult-bounds/pull/1285) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1286](https://github.com/CrocSwap/integer-mult-bounds/pull/1286) | rohanarun | partially reviewed | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1287](https://github.com/CrocSwap/integer-mult-bounds/pull/1287) | RossRichardson | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1288](https://github.com/CrocSwap/integer-mult-bounds/pull/1288) | Wronskode | partially reviewed | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1292](https://github.com/CrocSwap/integer-mult-bounds/pull/1292) | navinor | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1293](https://github.com/CrocSwap/integer-mult-bounds/pull/1293) | navinor | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1294](https://github.com/CrocSwap/integer-mult-bounds/pull/1294) | mightyOil | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1295](https://github.com/CrocSwap/integer-mult-bounds/pull/1295) | mightyOil | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1296](https://github.com/CrocSwap/integer-mult-bounds/pull/1296) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1297](https://github.com/CrocSwap/integer-mult-bounds/pull/1297) | rohanarun | partially reviewed | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1298](https://github.com/CrocSwap/integer-mult-bounds/pull/1298) | rtyu193-rgb | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1299](https://github.com/CrocSwap/integer-mult-bounds/pull/1299) | cbethin | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1300](https://github.com/CrocSwap/integer-mult-bounds/pull/1300) | mightyOil | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1302](https://github.com/CrocSwap/integer-mult-bounds/pull/1302) | theon199 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1303](https://github.com/CrocSwap/integer-mult-bounds/pull/1303) | mightyOil | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1304](https://github.com/CrocSwap/integer-mult-bounds/pull/1304) | commdata2338 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1306](https://github.com/CrocSwap/integer-mult-bounds/pull/1306) | commdata2338 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1307](https://github.com/CrocSwap/integer-mult-bounds/pull/1307) | commdata2338 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1308](https://github.com/CrocSwap/integer-mult-bounds/pull/1308) | mightyOil | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1309](https://github.com/CrocSwap/integer-mult-bounds/pull/1309) | bitplane | partially reviewed | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1310](https://github.com/CrocSwap/integer-mult-bounds/pull/1310) | mightyOil | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1311](https://github.com/CrocSwap/integer-mult-bounds/pull/1311) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1312](https://github.com/CrocSwap/integer-mult-bounds/pull/1312) | navinor | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1313](https://github.com/CrocSwap/integer-mult-bounds/pull/1313) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1318](https://github.com/CrocSwap/integer-mult-bounds/pull/1318) | RichardHoekstra | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1319](https://github.com/CrocSwap/integer-mult-bounds/pull/1319) | rohanarun | partially reviewed | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1320](https://github.com/CrocSwap/integer-mult-bounds/pull/1320) | Hope7Happiness | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1321](https://github.com/CrocSwap/integer-mult-bounds/pull/1321) | mightyOil | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1322](https://github.com/CrocSwap/integer-mult-bounds/pull/1322) | mightyOil | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1323](https://github.com/CrocSwap/integer-mult-bounds/pull/1323) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1325](https://github.com/CrocSwap/integer-mult-bounds/pull/1325) | mightyOil | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1326](https://github.com/CrocSwap/integer-mult-bounds/pull/1326) | applebees2 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1327](https://github.com/CrocSwap/integer-mult-bounds/pull/1327) | thakrarsagar | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1329](https://github.com/CrocSwap/integer-mult-bounds/pull/1329) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1331](https://github.com/CrocSwap/integer-mult-bounds/pull/1331) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1333](https://github.com/CrocSwap/integer-mult-bounds/pull/1333) | bitplane | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1334](https://github.com/CrocSwap/integer-mult-bounds/pull/1334) | thakrarsagar | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1337](https://github.com/CrocSwap/integer-mult-bounds/pull/1337) | mdumitrean | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1338](https://github.com/CrocSwap/integer-mult-bounds/pull/1338) | Wronskode | partially reviewed | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1340](https://github.com/CrocSwap/integer-mult-bounds/pull/1340) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1341](https://github.com/CrocSwap/integer-mult-bounds/pull/1341) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1342](https://github.com/CrocSwap/integer-mult-bounds/pull/1342) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1343](https://github.com/CrocSwap/integer-mult-bounds/pull/1343) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1344](https://github.com/CrocSwap/integer-mult-bounds/pull/1344) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1345](https://github.com/CrocSwap/integer-mult-bounds/pull/1345) | hipotures | partially reviewed | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1346](https://github.com/CrocSwap/integer-mult-bounds/pull/1346) | mythrilium | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1347](https://github.com/CrocSwap/integer-mult-bounds/pull/1347) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1348](https://github.com/CrocSwap/integer-mult-bounds/pull/1348) | navinor | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1349](https://github.com/CrocSwap/integer-mult-bounds/pull/1349) | thakrarsagar | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1350](https://github.com/CrocSwap/integer-mult-bounds/pull/1350) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1351](https://github.com/CrocSwap/integer-mult-bounds/pull/1351) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1353](https://github.com/CrocSwap/integer-mult-bounds/pull/1353) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1354](https://github.com/CrocSwap/integer-mult-bounds/pull/1354) | cbethin | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1358](https://github.com/CrocSwap/integer-mult-bounds/pull/1358) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1359](https://github.com/CrocSwap/integer-mult-bounds/pull/1359) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1361](https://github.com/CrocSwap/integer-mult-bounds/pull/1361) | thakrarsagar | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1363](https://github.com/CrocSwap/integer-mult-bounds/pull/1363) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1364](https://github.com/CrocSwap/integer-mult-bounds/pull/1364) | GamingPuzzled | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#1365](https://github.com/CrocSwap/integer-mult-bounds/pull/1365) | cheesegrader | partially reviewed | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1366](https://github.com/CrocSwap/integer-mult-bounds/pull/1366) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1367](https://github.com/CrocSwap/integer-mult-bounds/pull/1367) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1368](https://github.com/CrocSwap/integer-mult-bounds/pull/1368) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1369](https://github.com/CrocSwap/integer-mult-bounds/pull/1369) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1370](https://github.com/CrocSwap/integer-mult-bounds/pull/1370) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1371](https://github.com/CrocSwap/integer-mult-bounds/pull/1371) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1372](https://github.com/CrocSwap/integer-mult-bounds/pull/1372) | commdata2338 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1373](https://github.com/CrocSwap/integer-mult-bounds/pull/1373) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1374](https://github.com/CrocSwap/integer-mult-bounds/pull/1374) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1375](https://github.com/CrocSwap/integer-mult-bounds/pull/1375) | commdata2338 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1376](https://github.com/CrocSwap/integer-mult-bounds/pull/1376) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1377](https://github.com/CrocSwap/integer-mult-bounds/pull/1377) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1379](https://github.com/CrocSwap/integer-mult-bounds/pull/1379) | commdata2338 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1380](https://github.com/CrocSwap/integer-mult-bounds/pull/1380) | thakrarsagar | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1382](https://github.com/CrocSwap/integer-mult-bounds/pull/1382) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1383](https://github.com/CrocSwap/integer-mult-bounds/pull/1383) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1385](https://github.com/CrocSwap/integer-mult-bounds/pull/1385) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1386](https://github.com/CrocSwap/integer-mult-bounds/pull/1386) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1387](https://github.com/CrocSwap/integer-mult-bounds/pull/1387) | bitplane | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1388](https://github.com/CrocSwap/integer-mult-bounds/pull/1388) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1389](https://github.com/CrocSwap/integer-mult-bounds/pull/1389) | JosieElliston | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1390](https://github.com/CrocSwap/integer-mult-bounds/pull/1390) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1391](https://github.com/CrocSwap/integer-mult-bounds/pull/1391) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1392](https://github.com/CrocSwap/integer-mult-bounds/pull/1392) | brianross93 | partially reviewed | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1393](https://github.com/CrocSwap/integer-mult-bounds/pull/1393) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1397](https://github.com/CrocSwap/integer-mult-bounds/pull/1397) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1398](https://github.com/CrocSwap/integer-mult-bounds/pull/1398) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1399](https://github.com/CrocSwap/integer-mult-bounds/pull/1399) | JosieElliston | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1400](https://github.com/CrocSwap/integer-mult-bounds/pull/1400) | thakrarsagar | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1401](https://github.com/CrocSwap/integer-mult-bounds/pull/1401) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1402](https://github.com/CrocSwap/integer-mult-bounds/pull/1402) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1404](https://github.com/CrocSwap/integer-mult-bounds/pull/1404) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1405](https://github.com/CrocSwap/integer-mult-bounds/pull/1405) | TennisBowling | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1406](https://github.com/CrocSwap/integer-mult-bounds/pull/1406) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1407](https://github.com/CrocSwap/integer-mult-bounds/pull/1407) | pai-scaffolde | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#1408](https://github.com/CrocSwap/integer-mult-bounds/pull/1408) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1410](https://github.com/CrocSwap/integer-mult-bounds/pull/1410) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1413](https://github.com/CrocSwap/integer-mult-bounds/pull/1413) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1414](https://github.com/CrocSwap/integer-mult-bounds/pull/1414) | commdata2338 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1415](https://github.com/CrocSwap/integer-mult-bounds/pull/1415) | commdata2338 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1416](https://github.com/CrocSwap/integer-mult-bounds/pull/1416) | cbethin | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1417](https://github.com/CrocSwap/integer-mult-bounds/pull/1417) | aliromman | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1419](https://github.com/CrocSwap/integer-mult-bounds/pull/1419) | JosieElliston | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1420](https://github.com/CrocSwap/integer-mult-bounds/pull/1420) | bitplane | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1421](https://github.com/CrocSwap/integer-mult-bounds/pull/1421) | commdata2338 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1422](https://github.com/CrocSwap/integer-mult-bounds/pull/1422) | jeremydiviney | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1423](https://github.com/CrocSwap/integer-mult-bounds/pull/1423) | bbMisk | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1424](https://github.com/CrocSwap/integer-mult-bounds/pull/1424) | rohanarun | partially reviewed | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1425](https://github.com/CrocSwap/integer-mult-bounds/pull/1425) | JosieElliston | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1426](https://github.com/CrocSwap/integer-mult-bounds/pull/1426) | theon199 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1428](https://github.com/CrocSwap/integer-mult-bounds/pull/1428) | bbMisk | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1429](https://github.com/CrocSwap/integer-mult-bounds/pull/1429) | aliromman | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1430](https://github.com/CrocSwap/integer-mult-bounds/pull/1430) | bbMisk | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1431](https://github.com/CrocSwap/integer-mult-bounds/pull/1431) | bbMisk | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1432](https://github.com/CrocSwap/integer-mult-bounds/pull/1432) | bbMisk | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1433](https://github.com/CrocSwap/integer-mult-bounds/pull/1433) | thakrarsagar | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1435](https://github.com/CrocSwap/integer-mult-bounds/pull/1435) | woklerx | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1436](https://github.com/CrocSwap/integer-mult-bounds/pull/1436) | woklerx | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1437](https://github.com/CrocSwap/integer-mult-bounds/pull/1437) | woklerx | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1438](https://github.com/CrocSwap/integer-mult-bounds/pull/1438) | woklerx | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1439](https://github.com/CrocSwap/integer-mult-bounds/pull/1439) | woklerx | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1440](https://github.com/CrocSwap/integer-mult-bounds/pull/1440) | woklerx | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1441](https://github.com/CrocSwap/integer-mult-bounds/pull/1441) | woklerx | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1442](https://github.com/CrocSwap/integer-mult-bounds/pull/1442) | woklerx | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1443](https://github.com/CrocSwap/integer-mult-bounds/pull/1443) | woklerx | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1444](https://github.com/CrocSwap/integer-mult-bounds/pull/1444) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1445](https://github.com/CrocSwap/integer-mult-bounds/pull/1445) | woklerx | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1446](https://github.com/CrocSwap/integer-mult-bounds/pull/1446) | woklerx | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1447](https://github.com/CrocSwap/integer-mult-bounds/pull/1447) | woklerx | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1449](https://github.com/CrocSwap/integer-mult-bounds/pull/1449) | bbMisk | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1450](https://github.com/CrocSwap/integer-mult-bounds/pull/1450) | woklerx | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1451](https://github.com/CrocSwap/integer-mult-bounds/pull/1451) | woklerx | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1452](https://github.com/CrocSwap/integer-mult-bounds/pull/1452) | woklerx | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1453](https://github.com/CrocSwap/integer-mult-bounds/pull/1453) | aliromman | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1454](https://github.com/CrocSwap/integer-mult-bounds/pull/1454) | bbMisk | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1455](https://github.com/CrocSwap/integer-mult-bounds/pull/1455) | woklerx | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1456](https://github.com/CrocSwap/integer-mult-bounds/pull/1456) | woklerx | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1457](https://github.com/CrocSwap/integer-mult-bounds/pull/1457) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1458](https://github.com/CrocSwap/integer-mult-bounds/pull/1458) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1459](https://github.com/CrocSwap/integer-mult-bounds/pull/1459) | CubeJerry | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1460](https://github.com/CrocSwap/integer-mult-bounds/pull/1460) | bbMisk | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1461](https://github.com/CrocSwap/integer-mult-bounds/pull/1461) | CubeJerry | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1464](https://github.com/CrocSwap/integer-mult-bounds/pull/1464) | rohanarun | partially reviewed | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1465](https://github.com/CrocSwap/integer-mult-bounds/pull/1465) | aliromman | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1466](https://github.com/CrocSwap/integer-mult-bounds/pull/1466) | jmbarrancoidener | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1468](https://github.com/CrocSwap/integer-mult-bounds/pull/1468) | bitplane | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1469](https://github.com/CrocSwap/integer-mult-bounds/pull/1469) | JosieElliston | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1471](https://github.com/CrocSwap/integer-mult-bounds/pull/1471) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1473](https://github.com/CrocSwap/integer-mult-bounds/pull/1473) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1474](https://github.com/CrocSwap/integer-mult-bounds/pull/1474) | JosieElliston | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1475](https://github.com/CrocSwap/integer-mult-bounds/pull/1475) | thakrarsagar | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1477](https://github.com/CrocSwap/integer-mult-bounds/pull/1477) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1478](https://github.com/CrocSwap/integer-mult-bounds/pull/1478) | juper997 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1479](https://github.com/CrocSwap/integer-mult-bounds/pull/1479) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1480](https://github.com/CrocSwap/integer-mult-bounds/pull/1480) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1481](https://github.com/CrocSwap/integer-mult-bounds/pull/1481) | theon199 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1482](https://github.com/CrocSwap/integer-mult-bounds/pull/1482) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1483](https://github.com/CrocSwap/integer-mult-bounds/pull/1483) | CubeJerry | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1484](https://github.com/CrocSwap/integer-mult-bounds/pull/1484) | p-romeo | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1485](https://github.com/CrocSwap/integer-mult-bounds/pull/1485) | rohanarun | partially reviewed | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1487](https://github.com/CrocSwap/integer-mult-bounds/pull/1487) | ianlibanio | partially reviewed | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1488](https://github.com/CrocSwap/integer-mult-bounds/pull/1488) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1490](https://github.com/CrocSwap/integer-mult-bounds/pull/1490) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1491](https://github.com/CrocSwap/integer-mult-bounds/pull/1491) | commdata2338 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1494](https://github.com/CrocSwap/integer-mult-bounds/pull/1494) | cheesegrader | partially reviewed | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1495](https://github.com/CrocSwap/integer-mult-bounds/pull/1495) | commdata2338 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1496](https://github.com/CrocSwap/integer-mult-bounds/pull/1496) | commdata2338 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1497](https://github.com/CrocSwap/integer-mult-bounds/pull/1497) | an664 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1498](https://github.com/CrocSwap/integer-mult-bounds/pull/1498) | bitplane | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1499](https://github.com/CrocSwap/integer-mult-bounds/pull/1499) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1500](https://github.com/CrocSwap/integer-mult-bounds/pull/1500) | thakrarsagar | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1506](https://github.com/CrocSwap/integer-mult-bounds/pull/1506) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1508](https://github.com/CrocSwap/integer-mult-bounds/pull/1508) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1509](https://github.com/CrocSwap/integer-mult-bounds/pull/1509) | thakrarsagar | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1510](https://github.com/CrocSwap/integer-mult-bounds/pull/1510) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1511](https://github.com/CrocSwap/integer-mult-bounds/pull/1511) | an664 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1512](https://github.com/CrocSwap/integer-mult-bounds/pull/1512) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1513](https://github.com/CrocSwap/integer-mult-bounds/pull/1513) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1517](https://github.com/CrocSwap/integer-mult-bounds/pull/1517) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1518](https://github.com/CrocSwap/integer-mult-bounds/pull/1518) | hevlyo | partially reviewed | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1520](https://github.com/CrocSwap/integer-mult-bounds/pull/1520) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1521](https://github.com/CrocSwap/integer-mult-bounds/pull/1521) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1522](https://github.com/CrocSwap/integer-mult-bounds/pull/1522) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1523](https://github.com/CrocSwap/integer-mult-bounds/pull/1523) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1524](https://github.com/CrocSwap/integer-mult-bounds/pull/1524) | TennisBowling | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1526](https://github.com/CrocSwap/integer-mult-bounds/pull/1526) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1528](https://github.com/CrocSwap/integer-mult-bounds/pull/1528) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1529](https://github.com/CrocSwap/integer-mult-bounds/pull/1529) | higherbeing | partially reviewed | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1530](https://github.com/CrocSwap/integer-mult-bounds/pull/1530) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1531](https://github.com/CrocSwap/integer-mult-bounds/pull/1531) | navinor | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1532](https://github.com/CrocSwap/integer-mult-bounds/pull/1532) | theon199 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1533](https://github.com/CrocSwap/integer-mult-bounds/pull/1533) | CubeJerry | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1534](https://github.com/CrocSwap/integer-mult-bounds/pull/1534) | midhatn | partially reviewed | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1535](https://github.com/CrocSwap/integer-mult-bounds/pull/1535) | CubeJerry | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1536](https://github.com/CrocSwap/integer-mult-bounds/pull/1536) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1537](https://github.com/CrocSwap/integer-mult-bounds/pull/1537) | thakrarsagar | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1538](https://github.com/CrocSwap/integer-mult-bounds/pull/1538) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1541](https://github.com/CrocSwap/integer-mult-bounds/pull/1541) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1543](https://github.com/CrocSwap/integer-mult-bounds/pull/1543) | ToikY | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1546](https://github.com/CrocSwap/integer-mult-bounds/pull/1546) | an664 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1549](https://github.com/CrocSwap/integer-mult-bounds/pull/1549) | midhatn | partially reviewed | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1551](https://github.com/CrocSwap/integer-mult-bounds/pull/1551) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1552](https://github.com/CrocSwap/integer-mult-bounds/pull/1552) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1553](https://github.com/CrocSwap/integer-mult-bounds/pull/1553) | columbia-git | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1554](https://github.com/CrocSwap/integer-mult-bounds/pull/1554) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1556](https://github.com/CrocSwap/integer-mult-bounds/pull/1556) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1557](https://github.com/CrocSwap/integer-mult-bounds/pull/1557) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1558](https://github.com/CrocSwap/integer-mult-bounds/pull/1558) | yssite | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1559](https://github.com/CrocSwap/integer-mult-bounds/pull/1559) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1560](https://github.com/CrocSwap/integer-mult-bounds/pull/1560) | an664 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1562](https://github.com/CrocSwap/integer-mult-bounds/pull/1562) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1563](https://github.com/CrocSwap/integer-mult-bounds/pull/1563) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1564](https://github.com/CrocSwap/integer-mult-bounds/pull/1564) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1566](https://github.com/CrocSwap/integer-mult-bounds/pull/1566) | thakrarsagar | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1567](https://github.com/CrocSwap/integer-mult-bounds/pull/1567) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1568](https://github.com/CrocSwap/integer-mult-bounds/pull/1568) | JosieElliston | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1571](https://github.com/CrocSwap/integer-mult-bounds/pull/1571) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1572](https://github.com/CrocSwap/integer-mult-bounds/pull/1572) | Tuafo | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1573](https://github.com/CrocSwap/integer-mult-bounds/pull/1573) | steph4n-gh | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1574](https://github.com/CrocSwap/integer-mult-bounds/pull/1574) | rohanarun | partially reviewed | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1575](https://github.com/CrocSwap/integer-mult-bounds/pull/1575) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1576](https://github.com/CrocSwap/integer-mult-bounds/pull/1576) | navinor | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1577](https://github.com/CrocSwap/integer-mult-bounds/pull/1577) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1578](https://github.com/CrocSwap/integer-mult-bounds/pull/1578) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1580](https://github.com/CrocSwap/integer-mult-bounds/pull/1580) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1582](https://github.com/CrocSwap/integer-mult-bounds/pull/1582) | midhatn | partially reviewed | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1583](https://github.com/CrocSwap/integer-mult-bounds/pull/1583) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1584](https://github.com/CrocSwap/integer-mult-bounds/pull/1584) | thakrarsagar | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1586](https://github.com/CrocSwap/integer-mult-bounds/pull/1586) | dataisfire | partially reviewed | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1589](https://github.com/CrocSwap/integer-mult-bounds/pull/1589) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1590](https://github.com/CrocSwap/integer-mult-bounds/pull/1590) | DreamingOfClouds | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1591](https://github.com/CrocSwap/integer-mult-bounds/pull/1591) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1592](https://github.com/CrocSwap/integer-mult-bounds/pull/1592) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1595](https://github.com/CrocSwap/integer-mult-bounds/pull/1595) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1598](https://github.com/CrocSwap/integer-mult-bounds/pull/1598) | an664 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1600](https://github.com/CrocSwap/integer-mult-bounds/pull/1600) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1601](https://github.com/CrocSwap/integer-mult-bounds/pull/1601) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1602](https://github.com/CrocSwap/integer-mult-bounds/pull/1602) | ToikY | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1603](https://github.com/CrocSwap/integer-mult-bounds/pull/1603) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1604](https://github.com/CrocSwap/integer-mult-bounds/pull/1604) | Tuafo | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1605](https://github.com/CrocSwap/integer-mult-bounds/pull/1605) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1607](https://github.com/CrocSwap/integer-mult-bounds/pull/1607) | bbMisk | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1608](https://github.com/CrocSwap/integer-mult-bounds/pull/1608) | bbMisk | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1609](https://github.com/CrocSwap/integer-mult-bounds/pull/1609) | ToikY | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1610](https://github.com/CrocSwap/integer-mult-bounds/pull/1610) | an664 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1611](https://github.com/CrocSwap/integer-mult-bounds/pull/1611) | bbMisk | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1612](https://github.com/CrocSwap/integer-mult-bounds/pull/1612) | bbMisk | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1613](https://github.com/CrocSwap/integer-mult-bounds/pull/1613) | bbMisk | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1614](https://github.com/CrocSwap/integer-mult-bounds/pull/1614) | bbMisk | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1615](https://github.com/CrocSwap/integer-mult-bounds/pull/1615) | bbMisk | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1616](https://github.com/CrocSwap/integer-mult-bounds/pull/1616) | JosieElliston | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1617](https://github.com/CrocSwap/integer-mult-bounds/pull/1617) | bbMisk | partially reviewed | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1619](https://github.com/CrocSwap/integer-mult-bounds/pull/1619) | jackmgaller | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1623](https://github.com/CrocSwap/integer-mult-bounds/pull/1623) | navinor | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1624](https://github.com/CrocSwap/integer-mult-bounds/pull/1624) | an664 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1625](https://github.com/CrocSwap/integer-mult-bounds/pull/1625) | mdumitrean | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1626](https://github.com/CrocSwap/integer-mult-bounds/pull/1626) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1627](https://github.com/CrocSwap/integer-mult-bounds/pull/1627) | alephnan | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1628](https://github.com/CrocSwap/integer-mult-bounds/pull/1628) | Tuafo | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1629](https://github.com/CrocSwap/integer-mult-bounds/pull/1629) | rohanarun | partially reviewed | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1631](https://github.com/CrocSwap/integer-mult-bounds/pull/1631) | theon199 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1632](https://github.com/CrocSwap/integer-mult-bounds/pull/1632) | bbMisk | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1633](https://github.com/CrocSwap/integer-mult-bounds/pull/1633) | bbMisk | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1637](https://github.com/CrocSwap/integer-mult-bounds/pull/1637) | cbethin | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1638](https://github.com/CrocSwap/integer-mult-bounds/pull/1638) | ToikY | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1640](https://github.com/CrocSwap/integer-mult-bounds/pull/1640) | midhatn | partially reviewed | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1641](https://github.com/CrocSwap/integer-mult-bounds/pull/1641) | Dugongue | partially reviewed | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1642](https://github.com/CrocSwap/integer-mult-bounds/pull/1642) | theon199 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1643](https://github.com/CrocSwap/integer-mult-bounds/pull/1643) | antunishdPursuit | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1644](https://github.com/CrocSwap/integer-mult-bounds/pull/1644) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1646](https://github.com/CrocSwap/integer-mult-bounds/pull/1646) | JosieElliston | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1648](https://github.com/CrocSwap/integer-mult-bounds/pull/1648) | navinor | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1649](https://github.com/CrocSwap/integer-mult-bounds/pull/1649) | navinor | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1650](https://github.com/CrocSwap/integer-mult-bounds/pull/1650) | JosieElliston | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1651](https://github.com/CrocSwap/integer-mult-bounds/pull/1651) | RossRichardson | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1652](https://github.com/CrocSwap/integer-mult-bounds/pull/1652) | bitplane | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1654](https://github.com/CrocSwap/integer-mult-bounds/pull/1654) | JosieElliston | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1655](https://github.com/CrocSwap/integer-mult-bounds/pull/1655) | cbethin | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1656](https://github.com/CrocSwap/integer-mult-bounds/pull/1656) | antunishdPursuit | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1657](https://github.com/CrocSwap/integer-mult-bounds/pull/1657) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1658](https://github.com/CrocSwap/integer-mult-bounds/pull/1658) | theon199 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1661](https://github.com/CrocSwap/integer-mult-bounds/pull/1661) | midhatn | partially reviewed | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1662](https://github.com/CrocSwap/integer-mult-bounds/pull/1662) | ToikY | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1663](https://github.com/CrocSwap/integer-mult-bounds/pull/1663) | JosieElliston | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1664](https://github.com/CrocSwap/integer-mult-bounds/pull/1664) | an664 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1665](https://github.com/CrocSwap/integer-mult-bounds/pull/1665) | navinor | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1666](https://github.com/CrocSwap/integer-mult-bounds/pull/1666) | RossRichardson | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1668](https://github.com/CrocSwap/integer-mult-bounds/pull/1668) | JosieElliston | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1669](https://github.com/CrocSwap/integer-mult-bounds/pull/1669) | navinor | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1670](https://github.com/CrocSwap/integer-mult-bounds/pull/1670) | JosieElliston | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1671](https://github.com/CrocSwap/integer-mult-bounds/pull/1671) | bitplane | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1672](https://github.com/CrocSwap/integer-mult-bounds/pull/1672) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1673](https://github.com/CrocSwap/integer-mult-bounds/pull/1673) | Vlado-V | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1675](https://github.com/CrocSwap/integer-mult-bounds/pull/1675) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1676](https://github.com/CrocSwap/integer-mult-bounds/pull/1676) | an664 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1677](https://github.com/CrocSwap/integer-mult-bounds/pull/1677) | midhatn | partially reviewed | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1678](https://github.com/CrocSwap/integer-mult-bounds/pull/1678) | RossRichardson | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1679](https://github.com/CrocSwap/integer-mult-bounds/pull/1679) | Maximooch | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1680](https://github.com/CrocSwap/integer-mult-bounds/pull/1680) | ToikY | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1681](https://github.com/CrocSwap/integer-mult-bounds/pull/1681) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1682](https://github.com/CrocSwap/integer-mult-bounds/pull/1682) | RossRichardson | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1683](https://github.com/CrocSwap/integer-mult-bounds/pull/1683) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1684](https://github.com/CrocSwap/integer-mult-bounds/pull/1684) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1685](https://github.com/CrocSwap/integer-mult-bounds/pull/1685) | Maximooch | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1686](https://github.com/CrocSwap/integer-mult-bounds/pull/1686) | RossRichardson | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1688](https://github.com/CrocSwap/integer-mult-bounds/pull/1688) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1689](https://github.com/CrocSwap/integer-mult-bounds/pull/1689) | just-mn | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1690](https://github.com/CrocSwap/integer-mult-bounds/pull/1690) | navinor | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1692](https://github.com/CrocSwap/integer-mult-bounds/pull/1692) | midhatn | partially reviewed | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1696](https://github.com/CrocSwap/integer-mult-bounds/pull/1696) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1697](https://github.com/CrocSwap/integer-mult-bounds/pull/1697) | navinor | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1698](https://github.com/CrocSwap/integer-mult-bounds/pull/1698) | an664 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1699](https://github.com/CrocSwap/integer-mult-bounds/pull/1699) | chafreaky | partially reviewed | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1701](https://github.com/CrocSwap/integer-mult-bounds/pull/1701) | an664 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1702](https://github.com/CrocSwap/integer-mult-bounds/pull/1702) | SHIN09-git | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1703](https://github.com/CrocSwap/integer-mult-bounds/pull/1703) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1704](https://github.com/CrocSwap/integer-mult-bounds/pull/1704) | RossRichardson | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1705](https://github.com/CrocSwap/integer-mult-bounds/pull/1705) | navinor | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1706](https://github.com/CrocSwap/integer-mult-bounds/pull/1706) | rtyu193-rgb | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1707](https://github.com/CrocSwap/integer-mult-bounds/pull/1707) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1708](https://github.com/CrocSwap/integer-mult-bounds/pull/1708) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1709](https://github.com/CrocSwap/integer-mult-bounds/pull/1709) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1710](https://github.com/CrocSwap/integer-mult-bounds/pull/1710) | ToikY | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1711](https://github.com/CrocSwap/integer-mult-bounds/pull/1711) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1712](https://github.com/CrocSwap/integer-mult-bounds/pull/1712) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1714](https://github.com/CrocSwap/integer-mult-bounds/pull/1714) | alephnan | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1716](https://github.com/CrocSwap/integer-mult-bounds/pull/1716) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1717](https://github.com/CrocSwap/integer-mult-bounds/pull/1717) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1718](https://github.com/CrocSwap/integer-mult-bounds/pull/1718) | Pseudoataraxia | partially reviewed | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1719](https://github.com/CrocSwap/integer-mult-bounds/pull/1719) | aliromman | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1720](https://github.com/CrocSwap/integer-mult-bounds/pull/1720) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1721](https://github.com/CrocSwap/integer-mult-bounds/pull/1721) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1722](https://github.com/CrocSwap/integer-mult-bounds/pull/1722) | RossRichardson | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1724](https://github.com/CrocSwap/integer-mult-bounds/pull/1724) | midhatn | partially reviewed | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1725](https://github.com/CrocSwap/integer-mult-bounds/pull/1725) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1726](https://github.com/CrocSwap/integer-mult-bounds/pull/1726) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1729](https://github.com/CrocSwap/integer-mult-bounds/pull/1729) | jmbarrancoml | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1731](https://github.com/CrocSwap/integer-mult-bounds/pull/1731) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1732](https://github.com/CrocSwap/integer-mult-bounds/pull/1732) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1733](https://github.com/CrocSwap/integer-mult-bounds/pull/1733) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1734](https://github.com/CrocSwap/integer-mult-bounds/pull/1734) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1735](https://github.com/CrocSwap/integer-mult-bounds/pull/1735) | rtyu193-rgb | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1736](https://github.com/CrocSwap/integer-mult-bounds/pull/1736) | thakrarsagar | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1739](https://github.com/CrocSwap/integer-mult-bounds/pull/1739) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1741](https://github.com/CrocSwap/integer-mult-bounds/pull/1741) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1742](https://github.com/CrocSwap/integer-mult-bounds/pull/1742) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1744](https://github.com/CrocSwap/integer-mult-bounds/pull/1744) | Tuafo | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1745](https://github.com/CrocSwap/integer-mult-bounds/pull/1745) | 1337isnot1337 | partially reviewed | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1746](https://github.com/CrocSwap/integer-mult-bounds/pull/1746) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1747](https://github.com/CrocSwap/integer-mult-bounds/pull/1747) | RossRichardson | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1748](https://github.com/CrocSwap/integer-mult-bounds/pull/1748) | ToikY | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1749](https://github.com/CrocSwap/integer-mult-bounds/pull/1749) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1750](https://github.com/CrocSwap/integer-mult-bounds/pull/1750) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1752](https://github.com/CrocSwap/integer-mult-bounds/pull/1752) | thakrarsagar | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1754](https://github.com/CrocSwap/integer-mult-bounds/pull/1754) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1755](https://github.com/CrocSwap/integer-mult-bounds/pull/1755) | navinor | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1756](https://github.com/CrocSwap/integer-mult-bounds/pull/1756) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1757](https://github.com/CrocSwap/integer-mult-bounds/pull/1757) | jmbarrancoml | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1758](https://github.com/CrocSwap/integer-mult-bounds/pull/1758) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1761](https://github.com/CrocSwap/integer-mult-bounds/pull/1761) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1763](https://github.com/CrocSwap/integer-mult-bounds/pull/1763) | navinor | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1766](https://github.com/CrocSwap/integer-mult-bounds/pull/1766) | RossRichardson | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1767](https://github.com/CrocSwap/integer-mult-bounds/pull/1767) | thakrarsagar | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1768](https://github.com/CrocSwap/integer-mult-bounds/pull/1768) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1770](https://github.com/CrocSwap/integer-mult-bounds/pull/1770) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1772](https://github.com/CrocSwap/integer-mult-bounds/pull/1772) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1775](https://github.com/CrocSwap/integer-mult-bounds/pull/1775) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1777](https://github.com/CrocSwap/integer-mult-bounds/pull/1777) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1778](https://github.com/CrocSwap/integer-mult-bounds/pull/1778) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1779](https://github.com/CrocSwap/integer-mult-bounds/pull/1779) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1780](https://github.com/CrocSwap/integer-mult-bounds/pull/1780) | RossRichardson | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1781](https://github.com/CrocSwap/integer-mult-bounds/pull/1781) | thakrarsagar | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1782](https://github.com/CrocSwap/integer-mult-bounds/pull/1782) | navinor | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1783](https://github.com/CrocSwap/integer-mult-bounds/pull/1783) | JosieElliston | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1784](https://github.com/CrocSwap/integer-mult-bounds/pull/1784) | JosieElliston | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1786](https://github.com/CrocSwap/integer-mult-bounds/pull/1786) | chafreaky | partially reviewed | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1787](https://github.com/CrocSwap/integer-mult-bounds/pull/1787) | JosieElliston | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1788](https://github.com/CrocSwap/integer-mult-bounds/pull/1788) | JosieElliston | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1789](https://github.com/CrocSwap/integer-mult-bounds/pull/1789) | midhatn | partially reviewed | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1790](https://github.com/CrocSwap/integer-mult-bounds/pull/1790) | navinor | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1791](https://github.com/CrocSwap/integer-mult-bounds/pull/1791) | rtyu193-rgb | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1792](https://github.com/CrocSwap/integer-mult-bounds/pull/1792) | JosieElliston | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1793](https://github.com/CrocSwap/integer-mult-bounds/pull/1793) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1794](https://github.com/CrocSwap/integer-mult-bounds/pull/1794) | Maximooch | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1797](https://github.com/CrocSwap/integer-mult-bounds/pull/1797) | JosieElliston | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1799](https://github.com/CrocSwap/integer-mult-bounds/pull/1799) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1800](https://github.com/CrocSwap/integer-mult-bounds/pull/1800) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1801](https://github.com/CrocSwap/integer-mult-bounds/pull/1801) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1804](https://github.com/CrocSwap/integer-mult-bounds/pull/1804) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1805](https://github.com/CrocSwap/integer-mult-bounds/pull/1805) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1806](https://github.com/CrocSwap/integer-mult-bounds/pull/1806) | mtpsl | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1808](https://github.com/CrocSwap/integer-mult-bounds/pull/1808) | JosieElliston | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1810](https://github.com/CrocSwap/integer-mult-bounds/pull/1810) | RossRichardson | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1811](https://github.com/CrocSwap/integer-mult-bounds/pull/1811) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1812](https://github.com/CrocSwap/integer-mult-bounds/pull/1812) | nedveder | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1814](https://github.com/CrocSwap/integer-mult-bounds/pull/1814) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1815](https://github.com/CrocSwap/integer-mult-bounds/pull/1815) | jmbarrancoml | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1816](https://github.com/CrocSwap/integer-mult-bounds/pull/1816) | JosieElliston | partially reviewed | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1817](https://github.com/CrocSwap/integer-mult-bounds/pull/1817) | JosieElliston | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1819](https://github.com/CrocSwap/integer-mult-bounds/pull/1819) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1821](https://github.com/CrocSwap/integer-mult-bounds/pull/1821) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1822](https://github.com/CrocSwap/integer-mult-bounds/pull/1822) | navinor | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1823](https://github.com/CrocSwap/integer-mult-bounds/pull/1823) | navinor | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1824](https://github.com/CrocSwap/integer-mult-bounds/pull/1824) | JosieElliston | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1825](https://github.com/CrocSwap/integer-mult-bounds/pull/1825) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1826](https://github.com/CrocSwap/integer-mult-bounds/pull/1826) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1827](https://github.com/CrocSwap/integer-mult-bounds/pull/1827) | mightyOil | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1828](https://github.com/CrocSwap/integer-mult-bounds/pull/1828) | rohanarun | partially reviewed | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1829](https://github.com/CrocSwap/integer-mult-bounds/pull/1829) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1830](https://github.com/CrocSwap/integer-mult-bounds/pull/1830) | RossRichardson | partially reviewed | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1833](https://github.com/CrocSwap/integer-mult-bounds/pull/1833) | ToikY | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1834](https://github.com/CrocSwap/integer-mult-bounds/pull/1834) | navinor | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1837](https://github.com/CrocSwap/integer-mult-bounds/pull/1837) | navinor | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1838](https://github.com/CrocSwap/integer-mult-bounds/pull/1838) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1839](https://github.com/CrocSwap/integer-mult-bounds/pull/1839) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1841](https://github.com/CrocSwap/integer-mult-bounds/pull/1841) | woklerx | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1842](https://github.com/CrocSwap/integer-mult-bounds/pull/1842) | woklerx | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1843](https://github.com/CrocSwap/integer-mult-bounds/pull/1843) | woklerx | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1844](https://github.com/CrocSwap/integer-mult-bounds/pull/1844) | woklerx | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1845](https://github.com/CrocSwap/integer-mult-bounds/pull/1845) | woklerx | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1846](https://github.com/CrocSwap/integer-mult-bounds/pull/1846) | woklerx | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1847](https://github.com/CrocSwap/integer-mult-bounds/pull/1847) | woklerx | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1848](https://github.com/CrocSwap/integer-mult-bounds/pull/1848) | woklerx | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1849](https://github.com/CrocSwap/integer-mult-bounds/pull/1849) | woklerx | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1850](https://github.com/CrocSwap/integer-mult-bounds/pull/1850) | woklerx | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1851](https://github.com/CrocSwap/integer-mult-bounds/pull/1851) | woklerx | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1852](https://github.com/CrocSwap/integer-mult-bounds/pull/1852) | woklerx | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1853](https://github.com/CrocSwap/integer-mult-bounds/pull/1853) | woklerx | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1854](https://github.com/CrocSwap/integer-mult-bounds/pull/1854) | woklerx | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1855](https://github.com/CrocSwap/integer-mult-bounds/pull/1855) | woklerx | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1856](https://github.com/CrocSwap/integer-mult-bounds/pull/1856) | woklerx | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1857](https://github.com/CrocSwap/integer-mult-bounds/pull/1857) | woklerx | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1858](https://github.com/CrocSwap/integer-mult-bounds/pull/1858) | woklerx | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1859](https://github.com/CrocSwap/integer-mult-bounds/pull/1859) | woklerx | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1861](https://github.com/CrocSwap/integer-mult-bounds/pull/1861) | VictorLiwentao | partially reviewed | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1862](https://github.com/CrocSwap/integer-mult-bounds/pull/1862) | aliromman | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1863](https://github.com/CrocSwap/integer-mult-bounds/pull/1863) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1864](https://github.com/CrocSwap/integer-mult-bounds/pull/1864) | navinor | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1866](https://github.com/CrocSwap/integer-mult-bounds/pull/1866) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1867](https://github.com/CrocSwap/integer-mult-bounds/pull/1867) | jmbarrancoml | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1868](https://github.com/CrocSwap/integer-mult-bounds/pull/1868) | thakrarsagar | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1870](https://github.com/CrocSwap/integer-mult-bounds/pull/1870) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1872](https://github.com/CrocSwap/integer-mult-bounds/pull/1872) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1873](https://github.com/CrocSwap/integer-mult-bounds/pull/1873) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1874](https://github.com/CrocSwap/integer-mult-bounds/pull/1874) | mtpsl | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1875](https://github.com/CrocSwap/integer-mult-bounds/pull/1875) | rohanarun | partially reviewed | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1876](https://github.com/CrocSwap/integer-mult-bounds/pull/1876) | rohanarun | partially reviewed | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1877](https://github.com/CrocSwap/integer-mult-bounds/pull/1877) | chafreaky | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1878](https://github.com/CrocSwap/integer-mult-bounds/pull/1878) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1880](https://github.com/CrocSwap/integer-mult-bounds/pull/1880) | navinor | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1881](https://github.com/CrocSwap/integer-mult-bounds/pull/1881) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1882](https://github.com/CrocSwap/integer-mult-bounds/pull/1882) | waynenilsen | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1887](https://github.com/CrocSwap/integer-mult-bounds/pull/1887) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1888](https://github.com/CrocSwap/integer-mult-bounds/pull/1888) | RossRichardson | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1889](https://github.com/CrocSwap/integer-mult-bounds/pull/1889) | adamgall | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1891](https://github.com/CrocSwap/integer-mult-bounds/pull/1891) | woklerx | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1892](https://github.com/CrocSwap/integer-mult-bounds/pull/1892) | woklerx | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1893](https://github.com/CrocSwap/integer-mult-bounds/pull/1893) | woklerx | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1894](https://github.com/CrocSwap/integer-mult-bounds/pull/1894) | woklerx | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1895](https://github.com/CrocSwap/integer-mult-bounds/pull/1895) | woklerx | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1897](https://github.com/CrocSwap/integer-mult-bounds/pull/1897) | M6LI | partially reviewed | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1900](https://github.com/CrocSwap/integer-mult-bounds/pull/1900) | 1337isnot1337 | partially reviewed | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1902](https://github.com/CrocSwap/integer-mult-bounds/pull/1902) | bbMisk | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1904](https://github.com/CrocSwap/integer-mult-bounds/pull/1904) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1905](https://github.com/CrocSwap/integer-mult-bounds/pull/1905) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1906](https://github.com/CrocSwap/integer-mult-bounds/pull/1906) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1907](https://github.com/CrocSwap/integer-mult-bounds/pull/1907) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1908](https://github.com/CrocSwap/integer-mult-bounds/pull/1908) | adamgall | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1909](https://github.com/CrocSwap/integer-mult-bounds/pull/1909) | adamgall | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1910](https://github.com/CrocSwap/integer-mult-bounds/pull/1910) | adamgall | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1911](https://github.com/CrocSwap/integer-mult-bounds/pull/1911) | adamgall | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1912](https://github.com/CrocSwap/integer-mult-bounds/pull/1912) | adamgall | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1913](https://github.com/CrocSwap/integer-mult-bounds/pull/1913) | adamgall | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1914](https://github.com/CrocSwap/integer-mult-bounds/pull/1914) | bbMisk | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1915](https://github.com/CrocSwap/integer-mult-bounds/pull/1915) | adamgall | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1917](https://github.com/CrocSwap/integer-mult-bounds/pull/1917) | adamgall | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1918](https://github.com/CrocSwap/integer-mult-bounds/pull/1918) | adamgall | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1919](https://github.com/CrocSwap/integer-mult-bounds/pull/1919) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1920](https://github.com/CrocSwap/integer-mult-bounds/pull/1920) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1922](https://github.com/CrocSwap/integer-mult-bounds/pull/1922) | VictorLiwentao | partially reviewed | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1923](https://github.com/CrocSwap/integer-mult-bounds/pull/1923) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1924](https://github.com/CrocSwap/integer-mult-bounds/pull/1924) | ToikY | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1925](https://github.com/CrocSwap/integer-mult-bounds/pull/1925) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1926](https://github.com/CrocSwap/integer-mult-bounds/pull/1926) | Arham-Tahir64 | partially reviewed | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1928](https://github.com/CrocSwap/integer-mult-bounds/pull/1928) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1930](https://github.com/CrocSwap/integer-mult-bounds/pull/1930) | 1337isnot1337 | partially reviewed | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1932](https://github.com/CrocSwap/integer-mult-bounds/pull/1932) | thakrarsagar | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1934](https://github.com/CrocSwap/integer-mult-bounds/pull/1934) | RossRichardson | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1935](https://github.com/CrocSwap/integer-mult-bounds/pull/1935) | adamgall | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1936](https://github.com/CrocSwap/integer-mult-bounds/pull/1936) | adamgall | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1937](https://github.com/CrocSwap/integer-mult-bounds/pull/1937) | navinor | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1938](https://github.com/CrocSwap/integer-mult-bounds/pull/1938) | adamgall | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1939](https://github.com/CrocSwap/integer-mult-bounds/pull/1939) | jackmgaller | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1940](https://github.com/CrocSwap/integer-mult-bounds/pull/1940) | adamgall | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1941](https://github.com/CrocSwap/integer-mult-bounds/pull/1941) | adamgall | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1942](https://github.com/CrocSwap/integer-mult-bounds/pull/1942) | adamgall | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1943](https://github.com/CrocSwap/integer-mult-bounds/pull/1943) | adamgall | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1944](https://github.com/CrocSwap/integer-mult-bounds/pull/1944) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1945](https://github.com/CrocSwap/integer-mult-bounds/pull/1945) | arhamgarg | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1946](https://github.com/CrocSwap/integer-mult-bounds/pull/1946) | adamgall | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1948](https://github.com/CrocSwap/integer-mult-bounds/pull/1948) | adamgall | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1949](https://github.com/CrocSwap/integer-mult-bounds/pull/1949) | jmbarrancoml | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1951](https://github.com/CrocSwap/integer-mult-bounds/pull/1951) | adamgall | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1953](https://github.com/CrocSwap/integer-mult-bounds/pull/1953) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#1954](https://github.com/CrocSwap/integer-mult-bounds/pull/1954) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#1956](https://github.com/CrocSwap/integer-mult-bounds/pull/1956) | JosieElliston | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#1957](https://github.com/CrocSwap/integer-mult-bounds/pull/1957) | rohanarun | partially reviewed | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#1959](https://github.com/CrocSwap/integer-mult-bounds/pull/1959) | JosieElliston | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#1960](https://github.com/CrocSwap/integer-mult-bounds/pull/1960) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#1962](https://github.com/CrocSwap/integer-mult-bounds/pull/1962) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#1964](https://github.com/CrocSwap/integer-mult-bounds/pull/1964) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#1965](https://github.com/CrocSwap/integer-mult-bounds/pull/1965) | JosieElliston | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#1966](https://github.com/CrocSwap/integer-mult-bounds/pull/1966) | RossRichardson | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#1967](https://github.com/CrocSwap/integer-mult-bounds/pull/1967) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#1968](https://github.com/CrocSwap/integer-mult-bounds/pull/1968) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#1969](https://github.com/CrocSwap/integer-mult-bounds/pull/1969) | aliromman | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#1970](https://github.com/CrocSwap/integer-mult-bounds/pull/1970) | petalas | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#1973](https://github.com/CrocSwap/integer-mult-bounds/pull/1973) | DavidAriasC | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#1974](https://github.com/CrocSwap/integer-mult-bounds/pull/1974) | JosieElliston | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#1975](https://github.com/CrocSwap/integer-mult-bounds/pull/1975) | mtpsl | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#1977](https://github.com/CrocSwap/integer-mult-bounds/pull/1977) | JosieElliston | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#1979](https://github.com/CrocSwap/integer-mult-bounds/pull/1979) | lydakis | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#1981](https://github.com/CrocSwap/integer-mult-bounds/pull/1981) | petalas | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#1982](https://github.com/CrocSwap/integer-mult-bounds/pull/1982) | navinor | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#1983](https://github.com/CrocSwap/integer-mult-bounds/pull/1983) | cbethin | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#1984](https://github.com/CrocSwap/integer-mult-bounds/pull/1984) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#1988](https://github.com/CrocSwap/integer-mult-bounds/pull/1988) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#1989](https://github.com/CrocSwap/integer-mult-bounds/pull/1989) | RossRichardson | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#1990](https://github.com/CrocSwap/integer-mult-bounds/pull/1990) | ToikY | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#1991](https://github.com/CrocSwap/integer-mult-bounds/pull/1991) | chafreaky | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#1992](https://github.com/CrocSwap/integer-mult-bounds/pull/1992) | rohanarun | partially reviewed | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#1994](https://github.com/CrocSwap/integer-mult-bounds/pull/1994) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#1995](https://github.com/CrocSwap/integer-mult-bounds/pull/1995) | bitplane | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#1996](https://github.com/CrocSwap/integer-mult-bounds/pull/1996) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#1998](https://github.com/CrocSwap/integer-mult-bounds/pull/1998) | jmbarrancoml | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#2001](https://github.com/CrocSwap/integer-mult-bounds/pull/2001) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#2002](https://github.com/CrocSwap/integer-mult-bounds/pull/2002) | ianlibanio | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#2010](https://github.com/CrocSwap/integer-mult-bounds/pull/2010) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#2011](https://github.com/CrocSwap/integer-mult-bounds/pull/2011) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#2013](https://github.com/CrocSwap/integer-mult-bounds/pull/2013) | bitplane | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#2014](https://github.com/CrocSwap/integer-mult-bounds/pull/2014) | RossRichardson | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#2015](https://github.com/CrocSwap/integer-mult-bounds/pull/2015) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#2017](https://github.com/CrocSwap/integer-mult-bounds/pull/2017) | jmbarrancoml | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#2018](https://github.com/CrocSwap/integer-mult-bounds/pull/2018) | commdata2338 | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#2020](https://github.com/CrocSwap/integer-mult-bounds/pull/2020) | commdata2338 | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#2021](https://github.com/CrocSwap/integer-mult-bounds/pull/2021) | commdata2338 | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#2022](https://github.com/CrocSwap/integer-mult-bounds/pull/2022) | cbethin | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#2026](https://github.com/CrocSwap/integer-mult-bounds/pull/2026) | antunishdPursuit | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#2027](https://github.com/CrocSwap/integer-mult-bounds/pull/2027) | bitplane | incorporated | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) |
| [#2029](https://github.com/CrocSwap/integer-mult-bounds/pull/2029) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2031](https://github.com/CrocSwap/integer-mult-bounds/pull/2031) | DreamingOfClouds | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2033](https://github.com/CrocSwap/integer-mult-bounds/pull/2033) | ToikY | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2035](https://github.com/CrocSwap/integer-mult-bounds/pull/2035) | Tairitsu-Aya | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2037](https://github.com/CrocSwap/integer-mult-bounds/pull/2037) | commdata2338 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2039](https://github.com/CrocSwap/integer-mult-bounds/pull/2039) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2040](https://github.com/CrocSwap/integer-mult-bounds/pull/2040) | commdata2338 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2041](https://github.com/CrocSwap/integer-mult-bounds/pull/2041) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2042](https://github.com/CrocSwap/integer-mult-bounds/pull/2042) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2044](https://github.com/CrocSwap/integer-mult-bounds/pull/2044) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2045](https://github.com/CrocSwap/integer-mult-bounds/pull/2045) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2046](https://github.com/CrocSwap/integer-mult-bounds/pull/2046) | navinor | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2047](https://github.com/CrocSwap/integer-mult-bounds/pull/2047) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2048](https://github.com/CrocSwap/integer-mult-bounds/pull/2048) | commdata2338 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2050](https://github.com/CrocSwap/integer-mult-bounds/pull/2050) | RossRichardson | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2052](https://github.com/CrocSwap/integer-mult-bounds/pull/2052) | themilkman216 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2054](https://github.com/CrocSwap/integer-mult-bounds/pull/2054) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2055](https://github.com/CrocSwap/integer-mult-bounds/pull/2055) | antunishdPursuit | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2056](https://github.com/CrocSwap/integer-mult-bounds/pull/2056) | navinor | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2059](https://github.com/CrocSwap/integer-mult-bounds/pull/2059) | adamgall | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2060](https://github.com/CrocSwap/integer-mult-bounds/pull/2060) | adamgall | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2061](https://github.com/CrocSwap/integer-mult-bounds/pull/2061) | adamgall | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2062](https://github.com/CrocSwap/integer-mult-bounds/pull/2062) | adamgall | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2063](https://github.com/CrocSwap/integer-mult-bounds/pull/2063) | adamgall | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2064](https://github.com/CrocSwap/integer-mult-bounds/pull/2064) | adamgall | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2065](https://github.com/CrocSwap/integer-mult-bounds/pull/2065) | adamgall | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2066](https://github.com/CrocSwap/integer-mult-bounds/pull/2066) | adamgall | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2067](https://github.com/CrocSwap/integer-mult-bounds/pull/2067) | adamgall | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2068](https://github.com/CrocSwap/integer-mult-bounds/pull/2068) | theon199 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2069](https://github.com/CrocSwap/integer-mult-bounds/pull/2069) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2070](https://github.com/CrocSwap/integer-mult-bounds/pull/2070) | jmbarrancoml | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2071](https://github.com/CrocSwap/integer-mult-bounds/pull/2071) | adamgall | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2075](https://github.com/CrocSwap/integer-mult-bounds/pull/2075) | cbethin | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2076](https://github.com/CrocSwap/integer-mult-bounds/pull/2076) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2077](https://github.com/CrocSwap/integer-mult-bounds/pull/2077) | lydakis | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2078](https://github.com/CrocSwap/integer-mult-bounds/pull/2078) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2079](https://github.com/CrocSwap/integer-mult-bounds/pull/2079) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2081](https://github.com/CrocSwap/integer-mult-bounds/pull/2081) | Tairitsu-Aya | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2082](https://github.com/CrocSwap/integer-mult-bounds/pull/2082) | DavidAriasC | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2083](https://github.com/CrocSwap/integer-mult-bounds/pull/2083) | adamgall | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2084](https://github.com/CrocSwap/integer-mult-bounds/pull/2084) | adamgall | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2085](https://github.com/CrocSwap/integer-mult-bounds/pull/2085) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2086](https://github.com/CrocSwap/integer-mult-bounds/pull/2086) | adamgall | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2087](https://github.com/CrocSwap/integer-mult-bounds/pull/2087) | adamgall | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2088](https://github.com/CrocSwap/integer-mult-bounds/pull/2088) | adamgall | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2089](https://github.com/CrocSwap/integer-mult-bounds/pull/2089) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2090](https://github.com/CrocSwap/integer-mult-bounds/pull/2090) | adamgall | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2093](https://github.com/CrocSwap/integer-mult-bounds/pull/2093) | adamgall | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2096](https://github.com/CrocSwap/integer-mult-bounds/pull/2096) | adamgall | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2097](https://github.com/CrocSwap/integer-mult-bounds/pull/2097) | adamgall | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2098](https://github.com/CrocSwap/integer-mult-bounds/pull/2098) | navinor | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2099](https://github.com/CrocSwap/integer-mult-bounds/pull/2099) | navinor | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2100](https://github.com/CrocSwap/integer-mult-bounds/pull/2100) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2101](https://github.com/CrocSwap/integer-mult-bounds/pull/2101) | adamgall | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2103](https://github.com/CrocSwap/integer-mult-bounds/pull/2103) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2104](https://github.com/CrocSwap/integer-mult-bounds/pull/2104) | RossRichardson | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2105](https://github.com/CrocSwap/integer-mult-bounds/pull/2105) | theon199 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2108](https://github.com/CrocSwap/integer-mult-bounds/pull/2108) | jmbarrancoml | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2110](https://github.com/CrocSwap/integer-mult-bounds/pull/2110) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111) | DreamingOfClouds | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2112](https://github.com/CrocSwap/integer-mult-bounds/pull/2112) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2113](https://github.com/CrocSwap/integer-mult-bounds/pull/2113) | jeremydiviney | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2115](https://github.com/CrocSwap/integer-mult-bounds/pull/2115) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2116](https://github.com/CrocSwap/integer-mult-bounds/pull/2116) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2117](https://github.com/CrocSwap/integer-mult-bounds/pull/2117) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2118](https://github.com/CrocSwap/integer-mult-bounds/pull/2118) | 1337isnot1337 | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2120](https://github.com/CrocSwap/integer-mult-bounds/pull/2120) | petalas | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2122](https://github.com/CrocSwap/integer-mult-bounds/pull/2122) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2124](https://github.com/CrocSwap/integer-mult-bounds/pull/2124) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2125](https://github.com/CrocSwap/integer-mult-bounds/pull/2125) | DreamingOfClouds | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2126](https://github.com/CrocSwap/integer-mult-bounds/pull/2126) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2127](https://github.com/CrocSwap/integer-mult-bounds/pull/2127) | RossRichardson | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2128](https://github.com/CrocSwap/integer-mult-bounds/pull/2128) | navinor | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2129](https://github.com/CrocSwap/integer-mult-bounds/pull/2129) | petalas | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2130](https://github.com/CrocSwap/integer-mult-bounds/pull/2130) | navinor | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2132](https://github.com/CrocSwap/integer-mult-bounds/pull/2132) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2133](https://github.com/CrocSwap/integer-mult-bounds/pull/2133) | navinor | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2134](https://github.com/CrocSwap/integer-mult-bounds/pull/2134) | 1337isnot1337 | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2135](https://github.com/CrocSwap/integer-mult-bounds/pull/2135) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2136](https://github.com/CrocSwap/integer-mult-bounds/pull/2136) | Tairitsu-Aya | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2137](https://github.com/CrocSwap/integer-mult-bounds/pull/2137) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2139](https://github.com/CrocSwap/integer-mult-bounds/pull/2139) | jmbarrancoml | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2140](https://github.com/CrocSwap/integer-mult-bounds/pull/2140) | petalas | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2142](https://github.com/CrocSwap/integer-mult-bounds/pull/2142) | ianlibanio | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2145](https://github.com/CrocSwap/integer-mult-bounds/pull/2145) | navinor | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2146](https://github.com/CrocSwap/integer-mult-bounds/pull/2146) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2147](https://github.com/CrocSwap/integer-mult-bounds/pull/2147) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2148](https://github.com/CrocSwap/integer-mult-bounds/pull/2148) | petalas | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2150](https://github.com/CrocSwap/integer-mult-bounds/pull/2150) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2151](https://github.com/CrocSwap/integer-mult-bounds/pull/2151) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2152](https://github.com/CrocSwap/integer-mult-bounds/pull/2152) | DavidAriasC | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2153](https://github.com/CrocSwap/integer-mult-bounds/pull/2153) | commdata2338 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2154](https://github.com/CrocSwap/integer-mult-bounds/pull/2154) | commdata2338 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2156](https://github.com/CrocSwap/integer-mult-bounds/pull/2156) | Tairitsu-Aya | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2157](https://github.com/CrocSwap/integer-mult-bounds/pull/2157) | jmbarrancoml | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2158](https://github.com/CrocSwap/integer-mult-bounds/pull/2158) | navinor | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2159](https://github.com/CrocSwap/integer-mult-bounds/pull/2159) | RossRichardson | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2160](https://github.com/CrocSwap/integer-mult-bounds/pull/2160) | commdata2338 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2161](https://github.com/CrocSwap/integer-mult-bounds/pull/2161) | dataisfire | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2162](https://github.com/CrocSwap/integer-mult-bounds/pull/2162) | DreamingOfClouds | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2163](https://github.com/CrocSwap/integer-mult-bounds/pull/2163) | AgoraPluribusMichael | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2166](https://github.com/CrocSwap/integer-mult-bounds/pull/2166) | petalas | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2167](https://github.com/CrocSwap/integer-mult-bounds/pull/2167) | waynenilsen | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2168](https://github.com/CrocSwap/integer-mult-bounds/pull/2168) | dataisfire | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2169](https://github.com/CrocSwap/integer-mult-bounds/pull/2169) | philippeVV | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2171](https://github.com/CrocSwap/integer-mult-bounds/pull/2171) | jmbarrancoml | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2172](https://github.com/CrocSwap/integer-mult-bounds/pull/2172) | commdata2338 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2173](https://github.com/CrocSwap/integer-mult-bounds/pull/2173) | Gonzalo-Mier | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2174](https://github.com/CrocSwap/integer-mult-bounds/pull/2174) | commdata2338 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2175](https://github.com/CrocSwap/integer-mult-bounds/pull/2175) | petalas | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2176](https://github.com/CrocSwap/integer-mult-bounds/pull/2176) | RossRichardson | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2177](https://github.com/CrocSwap/integer-mult-bounds/pull/2177) | philippeVV | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2178](https://github.com/CrocSwap/integer-mult-bounds/pull/2178) | commdata2338 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2180](https://github.com/CrocSwap/integer-mult-bounds/pull/2180) | dataisfire | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2181](https://github.com/CrocSwap/integer-mult-bounds/pull/2181) | petalas | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2182](https://github.com/CrocSwap/integer-mult-bounds/pull/2182) | conorholds | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2183](https://github.com/CrocSwap/integer-mult-bounds/pull/2183) | petalas | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2184](https://github.com/CrocSwap/integer-mult-bounds/pull/2184) | dataisfire | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2186](https://github.com/CrocSwap/integer-mult-bounds/pull/2186) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2187](https://github.com/CrocSwap/integer-mult-bounds/pull/2187) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2188](https://github.com/CrocSwap/integer-mult-bounds/pull/2188) | commdata2338 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2189](https://github.com/CrocSwap/integer-mult-bounds/pull/2189) | commdata2338 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2190](https://github.com/CrocSwap/integer-mult-bounds/pull/2190) | commdata2338 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2191](https://github.com/CrocSwap/integer-mult-bounds/pull/2191) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2193](https://github.com/CrocSwap/integer-mult-bounds/pull/2193) | petalas | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2194](https://github.com/CrocSwap/integer-mult-bounds/pull/2194) | VictorLiwentao | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2195](https://github.com/CrocSwap/integer-mult-bounds/pull/2195) | jmbarrancoml | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2196](https://github.com/CrocSwap/integer-mult-bounds/pull/2196) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2197](https://github.com/CrocSwap/integer-mult-bounds/pull/2197) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2199](https://github.com/CrocSwap/integer-mult-bounds/pull/2199) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2201](https://github.com/CrocSwap/integer-mult-bounds/pull/2201) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2203](https://github.com/CrocSwap/integer-mult-bounds/pull/2203) | jeremydiviney | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2204](https://github.com/CrocSwap/integer-mult-bounds/pull/2204) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2206](https://github.com/CrocSwap/integer-mult-bounds/pull/2206) | petalas | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2207](https://github.com/CrocSwap/integer-mult-bounds/pull/2207) | jmbarrancoml | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2208](https://github.com/CrocSwap/integer-mult-bounds/pull/2208) | conorholds | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2210](https://github.com/CrocSwap/integer-mult-bounds/pull/2210) | VictorLiwentao | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2212](https://github.com/CrocSwap/integer-mult-bounds/pull/2212) | 1337isnot1337 | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2213](https://github.com/CrocSwap/integer-mult-bounds/pull/2213) | 1337isnot1337 | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2214](https://github.com/CrocSwap/integer-mult-bounds/pull/2214) | petalas | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2215](https://github.com/CrocSwap/integer-mult-bounds/pull/2215) | thakrarsagar | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2216](https://github.com/CrocSwap/integer-mult-bounds/pull/2216) | 1337isnot1337 | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2217](https://github.com/CrocSwap/integer-mult-bounds/pull/2217) | steph4n-gh | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2219](https://github.com/CrocSwap/integer-mult-bounds/pull/2219) | 1337isnot1337 | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2220](https://github.com/CrocSwap/integer-mult-bounds/pull/2220) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2222](https://github.com/CrocSwap/integer-mult-bounds/pull/2222) | 1337isnot1337 | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2224](https://github.com/CrocSwap/integer-mult-bounds/pull/2224) | 1337isnot1337 | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2225](https://github.com/CrocSwap/integer-mult-bounds/pull/2225) | 1337isnot1337 | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2226](https://github.com/CrocSwap/integer-mult-bounds/pull/2226) | 1337isnot1337 | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2227](https://github.com/CrocSwap/integer-mult-bounds/pull/2227) | conorholds | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2228](https://github.com/CrocSwap/integer-mult-bounds/pull/2228) | DreamingOfClouds | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2229](https://github.com/CrocSwap/integer-mult-bounds/pull/2229) | 1337isnot1337 | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2230](https://github.com/CrocSwap/integer-mult-bounds/pull/2230) | 1337isnot1337 | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2231](https://github.com/CrocSwap/integer-mult-bounds/pull/2231) | VictorLiwentao | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2232](https://github.com/CrocSwap/integer-mult-bounds/pull/2232) | 1337isnot1337 | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2233](https://github.com/CrocSwap/integer-mult-bounds/pull/2233) | 1337isnot1337 | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2234](https://github.com/CrocSwap/integer-mult-bounds/pull/2234) | jmbarrancoml | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2235](https://github.com/CrocSwap/integer-mult-bounds/pull/2235) | Dugongue | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2236](https://github.com/CrocSwap/integer-mult-bounds/pull/2236) | 1337isnot1337 | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2237](https://github.com/CrocSwap/integer-mult-bounds/pull/2237) | 1337isnot1337 | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2239](https://github.com/CrocSwap/integer-mult-bounds/pull/2239) | VictorLiwentao | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2240](https://github.com/CrocSwap/integer-mult-bounds/pull/2240) | 1337isnot1337 | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2241](https://github.com/CrocSwap/integer-mult-bounds/pull/2241) | 1337isnot1337 | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2244](https://github.com/CrocSwap/integer-mult-bounds/pull/2244) | DreamingOfClouds | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2246](https://github.com/CrocSwap/integer-mult-bounds/pull/2246) | 1337isnot1337 | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2247](https://github.com/CrocSwap/integer-mult-bounds/pull/2247) | 1337isnot1337 | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2248](https://github.com/CrocSwap/integer-mult-bounds/pull/2248) | 1337isnot1337 | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2249](https://github.com/CrocSwap/integer-mult-bounds/pull/2249) | 1337isnot1337 | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2250](https://github.com/CrocSwap/integer-mult-bounds/pull/2250) | jmbarrancoml | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2251](https://github.com/CrocSwap/integer-mult-bounds/pull/2251) | bitplane | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2252](https://github.com/CrocSwap/integer-mult-bounds/pull/2252) | cbethin | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2255](https://github.com/CrocSwap/integer-mult-bounds/pull/2255) | navinor | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2257](https://github.com/CrocSwap/integer-mult-bounds/pull/2257) | VictorLiwentao | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
