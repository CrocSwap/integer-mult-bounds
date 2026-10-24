# PR review and integration ledger

The immutable starting snapshot contains **446 PRs**. Explicit later family rounds extend the current inventory to **4755**; unrelated arrivals remain outside the round.

[Machine-readable ledger](pr-ledger.json) · [Starting snapshot](../../research/pr-reconciliation-20261012/starting-snapshot.json)

The ledger separates historical review from integration. A prior snapshot or a mention in a note does not certify a contribution. “Partially reviewed” includes scoped review and triage with their original limitations; “changed since review” means the present head lacks matching recorded coverage. Archived incorporation preserves a historical implementation and attribution without making it the selected result.

| Disposition | Count |
|---|---:|
| incorporated | 2129 |
| partially reviewed | 2564 |
| superseded | 2 |
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
| [#116](https://github.com/CrocSwap/integer-mult-bounds/pull/116) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) · [record 4](../../research/pr116-evidence-reconciliation/PARENT-EVIDENCE.json) |
| [#117](https://github.com/CrocSwap/integer-mult-bounds/pull/117) | eumemic | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#118](https://github.com/CrocSwap/integer-mult-bounds/pull/118) | rohanarun | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#121](https://github.com/CrocSwap/integer-mult-bounds/pull/121) | Th0rgal | incorporated | [record 1](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 2](../../research/overnight-pr-review-20261009/dispositions.json) · [record 3](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
| [#122](https://github.com/CrocSwap/integer-mult-bounds/pull/122) | SovereignSteak | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 5](../../research/community-reconciliation92-audit/DISPOSITIONS.json) · [record 6](../../research/overnight-pr-review-20261009/dispositions.json) · [record 7](../../research/pr-reconciliation100-20261013/DISPOSITIONS.json) |
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
| [#148](https://github.com/CrocSwap/integer-mult-bounds/pull/148) | gupt1156 | partially reviewed | [record 1](../../research/overnight-pr-review-20261009/dispositions.json) · [record 2](../../research/pr148-source-retention/README.md) · [record 3](../../research/pr-reconciliation-20261012/content-comparison.json) |
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
| [#259](https://github.com/CrocSwap/integer-mult-bounds/pull/259) | Dugongue | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
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
| [#275](https://github.com/CrocSwap/integer-mult-bounds/pull/275) | lydakis | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 6](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#277](https://github.com/CrocSwap/integer-mult-bounds/pull/277) | hcg890 | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#278](https://github.com/CrocSwap/integer-mult-bounds/pull/278) | hcg890 | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#279](https://github.com/CrocSwap/integer-mult-bounds/pull/279) | rohanarun | incorporated | [record 1](../../docs/research/community-pr279-integration.json) · [record 2](../../research/community-batch970-audit/COMPANION-REVIEWS.json) · [record 3](../../research/community-efficient300-audit/PARENT-EVIDENCE.json) · [record 4](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) · [record 5](../../research/pr-reconciliation-20261012/content-comparison.json) |
| [#280](https://github.com/CrocSwap/integer-mult-bounds/pull/280) | utcorvusvolat-dotcom | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#281](https://github.com/CrocSwap/integer-mult-bounds/pull/281) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#282](https://github.com/CrocSwap/integer-mult-bounds/pull/282) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
| [#283](https://github.com/CrocSwap/integer-mult-bounds/pull/283) | Dugongue | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-reconciliation-next100-audit/DISPOSITIONS.json) |
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
| [#309](https://github.com/CrocSwap/integer-mult-bounds/pull/309) | Dugongue | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
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
| [#379](https://github.com/CrocSwap/integer-mult-bounds/pull/379) | eumemic | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-reconciliation-third100-audit/DISPOSITIONS.json) |
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
| [#455](https://github.com/CrocSwap/integer-mult-bounds/pull/455) | Dugongue | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#456](https://github.com/CrocSwap/integer-mult-bounds/pull/456) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#457](https://github.com/CrocSwap/integer-mult-bounds/pull/457) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#458](https://github.com/CrocSwap/integer-mult-bounds/pull/458) | chafreaky | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#459](https://github.com/CrocSwap/integer-mult-bounds/pull/459) | rohanarun | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#460](https://github.com/CrocSwap/integer-mult-bounds/pull/460) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#461](https://github.com/CrocSwap/integer-mult-bounds/pull/461) | Srikrishnabalaji | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#462](https://github.com/CrocSwap/integer-mult-bounds/pull/462) | rohanarun | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#463](https://github.com/CrocSwap/integer-mult-bounds/pull/463) | DreamingOfClouds | incorporated | [record 1](../../research/community-family533-audit/DISPOSITIONS.json) · [record 2](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#464](https://github.com/CrocSwap/integer-mult-bounds/pull/464) | ahrazzle | unreviewed | No exact-head review established; inspect contribution and dependencies. |
| [#465](https://github.com/CrocSwap/integer-mult-bounds/pull/465) | Srikrishnabalaji | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 3](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
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
| [#485](https://github.com/CrocSwap/integer-mult-bounds/pull/485) | DreamingOfClouds | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 4](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
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
| [#498](https://github.com/CrocSwap/integer-mult-bounds/pull/498) | Dugongue | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#499](https://github.com/CrocSwap/integer-mult-bounds/pull/499) | rosswaycaster | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 4](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
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
| [#620](https://github.com/CrocSwap/integer-mult-bounds/pull/620) | GamingPuzzled | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-k492-audit/DISPOSITIONS.json) |
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
| [#636](https://github.com/CrocSwap/integer-mult-bounds/pull/636) | vectorsss | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#637](https://github.com/CrocSwap/integer-mult-bounds/pull/637) | jeremykothe2 | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#638](https://github.com/CrocSwap/integer-mult-bounds/pull/638) | vectorsss | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#639](https://github.com/CrocSwap/integer-mult-bounds/pull/639) | vectorsss | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#640](https://github.com/CrocSwap/integer-mult-bounds/pull/640) | vectorsss | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#641](https://github.com/CrocSwap/integer-mult-bounds/pull/641) | jeremykothe2 | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#642](https://github.com/CrocSwap/integer-mult-bounds/pull/642) | vectorsss | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#643](https://github.com/CrocSwap/integer-mult-bounds/pull/643) | jeremykothe2 | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#644](https://github.com/CrocSwap/integer-mult-bounds/pull/644) | vectorsss | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#645](https://github.com/CrocSwap/integer-mult-bounds/pull/645) | icekylinx | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#646](https://github.com/CrocSwap/integer-mult-bounds/pull/646) | jeremydiviney | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#648](https://github.com/CrocSwap/integer-mult-bounds/pull/648) | jeremykothe2 | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#649](https://github.com/CrocSwap/integer-mult-bounds/pull/649) | jeremykothe2 | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#651](https://github.com/CrocSwap/integer-mult-bounds/pull/651) | higherbeing | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#652](https://github.com/CrocSwap/integer-mult-bounds/pull/652) | jeremykothe2 | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#653](https://github.com/CrocSwap/integer-mult-bounds/pull/653) | jaymosley07 | incorporated | [record 1](../../research/community-reconciliation-fourth100-audit/DISPOSITIONS.json) |
| [#654](https://github.com/CrocSwap/integer-mult-bounds/pull/654) | GamingPuzzled | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
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
| [#669](https://github.com/CrocSwap/integer-mult-bounds/pull/669) | the-missionary-company | partially reviewed | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 3](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#670](https://github.com/CrocSwap/integer-mult-bounds/pull/670) | yongjae321 | incorporated | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#671](https://github.com/CrocSwap/integer-mult-bounds/pull/671) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#672](https://github.com/CrocSwap/integer-mult-bounds/pull/672) | steph4n-gh | incorporated | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#673](https://github.com/CrocSwap/integer-mult-bounds/pull/673) | androolloyd | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#674](https://github.com/CrocSwap/integer-mult-bounds/pull/674) | x0hu | incorporated | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#675](https://github.com/CrocSwap/integer-mult-bounds/pull/675) | tekuuu | incorporated | [record 1](../../research/community-frontier741-audit/DISPOSITIONS.json) |
| [#676](https://github.com/CrocSwap/integer-mult-bounds/pull/676) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#677](https://github.com/CrocSwap/integer-mult-bounds/pull/677) | commdata2338 | incorporated | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#678](https://github.com/CrocSwap/integer-mult-bounds/pull/678) | 0x-chad | incorporated | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#679](https://github.com/CrocSwap/integer-mult-bounds/pull/679) | g-guthrie | incorporated | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#680](https://github.com/CrocSwap/integer-mult-bounds/pull/680) | littleBro | incorporated | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#681](https://github.com/CrocSwap/integer-mult-bounds/pull/681) | alluri-ritual | incorporated | [record 1](../../research/community-frontier741-audit/DISPOSITIONS.json) |
| [#682](https://github.com/CrocSwap/integer-mult-bounds/pull/682) | swbiggart | incorporated | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#683](https://github.com/CrocSwap/integer-mult-bounds/pull/683) | Mister-Meeseeks | incorporated | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#684](https://github.com/CrocSwap/integer-mult-bounds/pull/684) | ineffyble | incorporated | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#685](https://github.com/CrocSwap/integer-mult-bounds/pull/685) | chafreaky | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 4](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#686](https://github.com/CrocSwap/integer-mult-bounds/pull/686) | mikhailramalho | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#687](https://github.com/CrocSwap/integer-mult-bounds/pull/687) | cbethin | incorporated | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#688](https://github.com/CrocSwap/integer-mult-bounds/pull/688) | aliromman | incorporated | [record 1](../../research/community-frontier799-audit/DISPOSITIONS.json) |
| [#689](https://github.com/CrocSwap/integer-mult-bounds/pull/689) | dillona | incorporated | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#691](https://github.com/CrocSwap/integer-mult-bounds/pull/691) | mtpsl | incorporated | [record 1](../../research/community-frontier799-audit/DISPOSITIONS.json) |
| [#692](https://github.com/CrocSwap/integer-mult-bounds/pull/692) | Ambassators | incorporated | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#693](https://github.com/CrocSwap/integer-mult-bounds/pull/693) | thakrarsagar | incorporated | [record 1](../../research/community-pilot20-audit/DISPOSITIONS.json) |
| [#694](https://github.com/CrocSwap/integer-mult-bounds/pull/694) | g-guthrie | incorporated | [record 1](../../research/community-frontier799-audit/DISPOSITIONS.json) |
| [#695](https://github.com/CrocSwap/integer-mult-bounds/pull/695) | jsnider3 | incorporated | [record 1](../../research/community-frontier741-audit/DISPOSITIONS.json) |
| [#696](https://github.com/CrocSwap/integer-mult-bounds/pull/696) | thakrarsagar | incorporated | [record 1](../../research/community-frontier799-audit/DISPOSITIONS.json) |
| [#697](https://github.com/CrocSwap/integer-mult-bounds/pull/697) | swbiggart | partially reviewed | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2500-audit/DISPOSITIONS.json) |
| [#698](https://github.com/CrocSwap/integer-mult-bounds/pull/698) | thakrarsagar | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#699](https://github.com/CrocSwap/integer-mult-bounds/pull/699) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) |
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
| [#717](https://github.com/CrocSwap/integer-mult-bounds/pull/717) | DreamingOfClouds | partially reviewed | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) |
| [#718](https://github.com/CrocSwap/integer-mult-bounds/pull/718) | thakrarsagar | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#719](https://github.com/CrocSwap/integer-mult-bounds/pull/719) | thakrarsagar | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#720](https://github.com/CrocSwap/integer-mult-bounds/pull/720) | davidgovea | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
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
| [#732](https://github.com/CrocSwap/integer-mult-bounds/pull/732) | lukemansoor | partially reviewed | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
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
| [#746](https://github.com/CrocSwap/integer-mult-bounds/pull/746) | williamreidrichards | partially reviewed | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) |
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
| [#758](https://github.com/CrocSwap/integer-mult-bounds/pull/758) | Koroffstrogov | partially reviewed | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) |
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
| [#775](https://github.com/CrocSwap/integer-mult-bounds/pull/775) | at1as | partially reviewed | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) |
| [#776](https://github.com/CrocSwap/integer-mult-bounds/pull/776) | ntedvs | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#777](https://github.com/CrocSwap/integer-mult-bounds/pull/777) | tekuuu | incorporated | [record 1](../../research/community-frontier741-audit/DISPOSITIONS.json) · [record 2](../../research/community-frontier799-audit/DISPOSITIONS.json) |
| [#778](https://github.com/CrocSwap/integer-mult-bounds/pull/778) | merramil | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#779](https://github.com/CrocSwap/integer-mult-bounds/pull/779) | PeterCarp320 | partially reviewed | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) |
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
| [#790](https://github.com/CrocSwap/integer-mult-bounds/pull/790) | commdata2338 | partially reviewed | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) |
| [#791](https://github.com/CrocSwap/integer-mult-bounds/pull/791) | Curtis-D | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#792](https://github.com/CrocSwap/integer-mult-bounds/pull/792) | Ryan-Haines | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#793](https://github.com/CrocSwap/integer-mult-bounds/pull/793) | Varun-Mittal-1001 | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#794](https://github.com/CrocSwap/integer-mult-bounds/pull/794) | commdata2338 | partially reviewed | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) |
| [#795](https://github.com/CrocSwap/integer-mult-bounds/pull/795) | chafreaky | incorporated | [record 1](../../research/community-frontier799-audit/DISPOSITIONS.json) |
| [#796](https://github.com/CrocSwap/integer-mult-bounds/pull/796) | FanPUYen | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#797](https://github.com/CrocSwap/integer-mult-bounds/pull/797) | aliromman | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#798](https://github.com/CrocSwap/integer-mult-bounds/pull/798) | jonathanlam | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#799](https://github.com/CrocSwap/integer-mult-bounds/pull/799) | jeremykothe2 | incorporated | [record 1](../../research/community-frontier799-audit/DISPOSITIONS.json) |
| [#800](https://github.com/CrocSwap/integer-mult-bounds/pull/800) | jeremydiviney | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#801](https://github.com/CrocSwap/integer-mult-bounds/pull/801) | Rohansguliani | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#802](https://github.com/CrocSwap/integer-mult-bounds/pull/802) | Rohansguliani | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#803](https://github.com/CrocSwap/integer-mult-bounds/pull/803) | alephnan | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#805](https://github.com/CrocSwap/integer-mult-bounds/pull/805) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#806](https://github.com/CrocSwap/integer-mult-bounds/pull/806) | Rohansguliani | incorporated | [record 1](../../research/community-frontier799-audit/DISPOSITIONS.json) |
| [#807](https://github.com/CrocSwap/integer-mult-bounds/pull/807) | davidawad | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#808](https://github.com/CrocSwap/integer-mult-bounds/pull/808) | 4RchYMing | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#809](https://github.com/CrocSwap/integer-mult-bounds/pull/809) | Curtis-D | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#810](https://github.com/CrocSwap/integer-mult-bounds/pull/810) | jerrylin-23 | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#811](https://github.com/CrocSwap/integer-mult-bounds/pull/811) | Ryan-Haines | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#812](https://github.com/CrocSwap/integer-mult-bounds/pull/812) | ljste | incorporated | [record 1](../../research/community-frontier890-audit/DISPOSITIONS.json) |
| [#813](https://github.com/CrocSwap/integer-mult-bounds/pull/813) | bitplane | incorporated | [record 1](../../research/community-batch932-audit/DISPOSITIONS.json) |
| [#814](https://github.com/CrocSwap/integer-mult-bounds/pull/814) | shiftybitshiftr | incorporated | [record 1](../../research/community-efficient100-audit/DISPOSITIONS.json) |
| [#815](https://github.com/CrocSwap/integer-mult-bounds/pull/815) | Rohansguliani | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
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
| [#826](https://github.com/CrocSwap/integer-mult-bounds/pull/826) | Rohansguliani | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient200-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
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
| [#846](https://github.com/CrocSwap/integer-mult-bounds/pull/846) | Rohansguliani | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) |
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
| [#895](https://github.com/CrocSwap/integer-mult-bounds/pull/895) | DaysSky | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#896](https://github.com/CrocSwap/integer-mult-bounds/pull/896) | bitplane | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#897](https://github.com/CrocSwap/integer-mult-bounds/pull/897) | DaysSky | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#898](https://github.com/CrocSwap/integer-mult-bounds/pull/898) | CubeJerry | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#899](https://github.com/CrocSwap/integer-mult-bounds/pull/899) | DreamingOfClouds | partially reviewed | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient200-audit/DISPOSITIONS.json) |
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
| [#928](https://github.com/CrocSwap/integer-mult-bounds/pull/928) | rohanarun | superseded | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#929](https://github.com/CrocSwap/integer-mult-bounds/pull/929) | chafreaky | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#930](https://github.com/CrocSwap/integer-mult-bounds/pull/930) | RossRichardson | incorporated | [record 1](../../research/community-batch970-audit/DISPOSITIONS.json) |
| [#931](https://github.com/CrocSwap/integer-mult-bounds/pull/931) | RossRichardson | partially reviewed | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient200-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient2500-audit/DISPOSITIONS.json) |
| [#932](https://github.com/CrocSwap/integer-mult-bounds/pull/932) | RossRichardson | incorporated | [record 1](../../research/community-batch932-audit/DISPOSITIONS.json) |
| [#933](https://github.com/CrocSwap/integer-mult-bounds/pull/933) | ianlibanio | partially reviewed | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient200-audit/DISPOSITIONS.json) |
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
| [#962](https://github.com/CrocSwap/integer-mult-bounds/pull/962) | GamingPuzzled | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) |
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
| [#977](https://github.com/CrocSwap/integer-mult-bounds/pull/977) | chafreaky | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) |
| [#978](https://github.com/CrocSwap/integer-mult-bounds/pull/978) | franciscoyne001-svg | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#979](https://github.com/CrocSwap/integer-mult-bounds/pull/979) | DLamdata | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#980](https://github.com/CrocSwap/integer-mult-bounds/pull/980) | bitplane | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#981](https://github.com/CrocSwap/integer-mult-bounds/pull/981) | ToikY | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#982](https://github.com/CrocSwap/integer-mult-bounds/pull/982) | RossRichardson | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#984](https://github.com/CrocSwap/integer-mult-bounds/pull/984) | ToikY | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#985](https://github.com/CrocSwap/integer-mult-bounds/pull/985) | aliromman | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) |
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
| [#1007](https://github.com/CrocSwap/integer-mult-bounds/pull/1007) | RossRichardson | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient200-audit/DISPOSITIONS.json) |
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
| [#1025](https://github.com/CrocSwap/integer-mult-bounds/pull/1025) | chafreaky | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) |
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
| [#1038](https://github.com/CrocSwap/integer-mult-bounds/pull/1038) | aliromman | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) |
| [#1039](https://github.com/CrocSwap/integer-mult-bounds/pull/1039) | RossRichardson | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1040](https://github.com/CrocSwap/integer-mult-bounds/pull/1040) | woklerx | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#1041](https://github.com/CrocSwap/integer-mult-bounds/pull/1041) | thakrarsagar | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#1042](https://github.com/CrocSwap/integer-mult-bounds/pull/1042) | jeremykothe2 | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#1043](https://github.com/CrocSwap/integer-mult-bounds/pull/1043) | aliromman | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) |
| [#1044](https://github.com/CrocSwap/integer-mult-bounds/pull/1044) | steph4n-gh | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1045](https://github.com/CrocSwap/integer-mult-bounds/pull/1045) | thakrarsagar | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1046](https://github.com/CrocSwap/integer-mult-bounds/pull/1046) | martinxxx9 | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1047](https://github.com/CrocSwap/integer-mult-bounds/pull/1047) | woklerx | incorporated | [record 1](../../research/community-batch1047-audit/DISPOSITIONS.json) |
| [#1048](https://github.com/CrocSwap/integer-mult-bounds/pull/1048) | flemhhh | partially reviewed | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#1049](https://github.com/CrocSwap/integer-mult-bounds/pull/1049) | thakrarsagar | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1050](https://github.com/CrocSwap/integer-mult-bounds/pull/1050) | jeremykothe2 | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1051](https://github.com/CrocSwap/integer-mult-bounds/pull/1051) | thakrarsagar | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1052](https://github.com/CrocSwap/integer-mult-bounds/pull/1052) | steph4n-gh | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1053](https://github.com/CrocSwap/integer-mult-bounds/pull/1053) | jeremykothe2 | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1054](https://github.com/CrocSwap/integer-mult-bounds/pull/1054) | aliromman | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) |
| [#1055](https://github.com/CrocSwap/integer-mult-bounds/pull/1055) | jeremykothe2 | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1056](https://github.com/CrocSwap/integer-mult-bounds/pull/1056) | rohanarun | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1057](https://github.com/CrocSwap/integer-mult-bounds/pull/1057) | bitplane | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1058](https://github.com/CrocSwap/integer-mult-bounds/pull/1058) | cbarber1 | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1059](https://github.com/CrocSwap/integer-mult-bounds/pull/1059) | thakrarsagar | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1060](https://github.com/CrocSwap/integer-mult-bounds/pull/1060) | aliromman | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) |
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
| [#1075](https://github.com/CrocSwap/integer-mult-bounds/pull/1075) | RossRichardson | incorporated | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1076](https://github.com/CrocSwap/integer-mult-bounds/pull/1076) | navinor | incorporated | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1077](https://github.com/CrocSwap/integer-mult-bounds/pull/1077) | woklerx | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1078](https://github.com/CrocSwap/integer-mult-bounds/pull/1078) | bbMisk | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1079](https://github.com/CrocSwap/integer-mult-bounds/pull/1079) | bbMisk | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1080](https://github.com/CrocSwap/integer-mult-bounds/pull/1080) | steph4n-gh | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1081](https://github.com/CrocSwap/integer-mult-bounds/pull/1081) | steph4n-gh | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1082](https://github.com/CrocSwap/integer-mult-bounds/pull/1082) | rohanarun | incorporated | [record 1](../../research/community-batch1099-audit/DISPOSITIONS.json) |
| [#1083](https://github.com/CrocSwap/integer-mult-bounds/pull/1083) | bbMisk | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) |
| [#1084](https://github.com/CrocSwap/integer-mult-bounds/pull/1084) | navinor | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1085](https://github.com/CrocSwap/integer-mult-bounds/pull/1085) | bbMisk | incorporated | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) |
| [#1086](https://github.com/CrocSwap/integer-mult-bounds/pull/1086) | Hope7Happiness | partially reviewed | [record 1](../../research/community-efficient200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) |
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
| [#1104](https://github.com/CrocSwap/integer-mult-bounds/pull/1104) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1105](https://github.com/CrocSwap/integer-mult-bounds/pull/1105) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1106](https://github.com/CrocSwap/integer-mult-bounds/pull/1106) | ToikY | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1107](https://github.com/CrocSwap/integer-mult-bounds/pull/1107) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1108](https://github.com/CrocSwap/integer-mult-bounds/pull/1108) | martinxxx9 | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1110](https://github.com/CrocSwap/integer-mult-bounds/pull/1110) | RossRichardson | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1111](https://github.com/CrocSwap/integer-mult-bounds/pull/1111) | seslly | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1112](https://github.com/CrocSwap/integer-mult-bounds/pull/1112) | Wronskode | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1113](https://github.com/CrocSwap/integer-mult-bounds/pull/1113) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1114](https://github.com/CrocSwap/integer-mult-bounds/pull/1114) | adamgall | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1115](https://github.com/CrocSwap/integer-mult-bounds/pull/1115) | martinxxx9 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1116](https://github.com/CrocSwap/integer-mult-bounds/pull/1116) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1117](https://github.com/CrocSwap/integer-mult-bounds/pull/1117) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1118](https://github.com/CrocSwap/integer-mult-bounds/pull/1118) | ToikY | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1119](https://github.com/CrocSwap/integer-mult-bounds/pull/1119) | steph4n-gh | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1120](https://github.com/CrocSwap/integer-mult-bounds/pull/1120) | aliromman | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1121](https://github.com/CrocSwap/integer-mult-bounds/pull/1121) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1122](https://github.com/CrocSwap/integer-mult-bounds/pull/1122) | bitplane | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1123](https://github.com/CrocSwap/integer-mult-bounds/pull/1123) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1124](https://github.com/CrocSwap/integer-mult-bounds/pull/1124) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1125](https://github.com/CrocSwap/integer-mult-bounds/pull/1125) | aliromman | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1126](https://github.com/CrocSwap/integer-mult-bounds/pull/1126) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1127](https://github.com/CrocSwap/integer-mult-bounds/pull/1127) | navinor | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1128](https://github.com/CrocSwap/integer-mult-bounds/pull/1128) | aliromman | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1129](https://github.com/CrocSwap/integer-mult-bounds/pull/1129) | aliromman | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1130](https://github.com/CrocSwap/integer-mult-bounds/pull/1130) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1131](https://github.com/CrocSwap/integer-mult-bounds/pull/1131) | chafreaky | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1132](https://github.com/CrocSwap/integer-mult-bounds/pull/1132) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1133](https://github.com/CrocSwap/integer-mult-bounds/pull/1133) | thakrarsagar | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1134](https://github.com/CrocSwap/integer-mult-bounds/pull/1134) | aliromman | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1135](https://github.com/CrocSwap/integer-mult-bounds/pull/1135) | aliromman | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1136](https://github.com/CrocSwap/integer-mult-bounds/pull/1136) | aliromman | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1137](https://github.com/CrocSwap/integer-mult-bounds/pull/1137) | Wronskode | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1138](https://github.com/CrocSwap/integer-mult-bounds/pull/1138) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1139](https://github.com/CrocSwap/integer-mult-bounds/pull/1139) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1140](https://github.com/CrocSwap/integer-mult-bounds/pull/1140) | aliromman | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1141](https://github.com/CrocSwap/integer-mult-bounds/pull/1141) | aliromman | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1142](https://github.com/CrocSwap/integer-mult-bounds/pull/1142) | martinxxx9 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1143](https://github.com/CrocSwap/integer-mult-bounds/pull/1143) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1144](https://github.com/CrocSwap/integer-mult-bounds/pull/1144) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1145](https://github.com/CrocSwap/integer-mult-bounds/pull/1145) | RossRichardson | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1147](https://github.com/CrocSwap/integer-mult-bounds/pull/1147) | RaphaelFakhri | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1148](https://github.com/CrocSwap/integer-mult-bounds/pull/1148) | tomdif | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1149](https://github.com/CrocSwap/integer-mult-bounds/pull/1149) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1150](https://github.com/CrocSwap/integer-mult-bounds/pull/1150) | rohanarun | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1151](https://github.com/CrocSwap/integer-mult-bounds/pull/1151) | thakrarsagar | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1152](https://github.com/CrocSwap/integer-mult-bounds/pull/1152) | chafreaky | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1153](https://github.com/CrocSwap/integer-mult-bounds/pull/1153) | Scratch-net | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1154](https://github.com/CrocSwap/integer-mult-bounds/pull/1154) | Dugongue | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1155](https://github.com/CrocSwap/integer-mult-bounds/pull/1155) | navinor | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1400-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1156](https://github.com/CrocSwap/integer-mult-bounds/pull/1156) | thakrarsagar | partially reviewed | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1157](https://github.com/CrocSwap/integer-mult-bounds/pull/1157) | rohanarun | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1158](https://github.com/CrocSwap/integer-mult-bounds/pull/1158) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1159](https://github.com/CrocSwap/integer-mult-bounds/pull/1159) | bitplane | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1160](https://github.com/CrocSwap/integer-mult-bounds/pull/1160) | Hope7Happiness | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1161](https://github.com/CrocSwap/integer-mult-bounds/pull/1161) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1162](https://github.com/CrocSwap/integer-mult-bounds/pull/1162) | brianross93 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#1164](https://github.com/CrocSwap/integer-mult-bounds/pull/1164) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1165](https://github.com/CrocSwap/integer-mult-bounds/pull/1165) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1168](https://github.com/CrocSwap/integer-mult-bounds/pull/1168) | thakrarsagar | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1169](https://github.com/CrocSwap/integer-mult-bounds/pull/1169) | rohanarun | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1170](https://github.com/CrocSwap/integer-mult-bounds/pull/1170) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1171](https://github.com/CrocSwap/integer-mult-bounds/pull/1171) | 3xcalibur-tech | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1172](https://github.com/CrocSwap/integer-mult-bounds/pull/1172) | midhatn | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1173](https://github.com/CrocSwap/integer-mult-bounds/pull/1173) | ToikY | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1174](https://github.com/CrocSwap/integer-mult-bounds/pull/1174) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1175](https://github.com/CrocSwap/integer-mult-bounds/pull/1175) | gvconly | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1176](https://github.com/CrocSwap/integer-mult-bounds/pull/1176) | Dugongue | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1177](https://github.com/CrocSwap/integer-mult-bounds/pull/1177) | RossRichardson | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1178](https://github.com/CrocSwap/integer-mult-bounds/pull/1178) | rohanarun | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1179](https://github.com/CrocSwap/integer-mult-bounds/pull/1179) | adamgall | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1180](https://github.com/CrocSwap/integer-mult-bounds/pull/1180) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1181](https://github.com/CrocSwap/integer-mult-bounds/pull/1181) | thakrarsagar | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1182](https://github.com/CrocSwap/integer-mult-bounds/pull/1182) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1183](https://github.com/CrocSwap/integer-mult-bounds/pull/1183) | rohanarun | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1184](https://github.com/CrocSwap/integer-mult-bounds/pull/1184) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1185](https://github.com/CrocSwap/integer-mult-bounds/pull/1185) | Mister-Meeseeks | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1186](https://github.com/CrocSwap/integer-mult-bounds/pull/1186) | mdumitrean | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1187](https://github.com/CrocSwap/integer-mult-bounds/pull/1187) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1188](https://github.com/CrocSwap/integer-mult-bounds/pull/1188) | bitplane | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1189](https://github.com/CrocSwap/integer-mult-bounds/pull/1189) | mightyOil | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1190](https://github.com/CrocSwap/integer-mult-bounds/pull/1190) | adamgall | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1191](https://github.com/CrocSwap/integer-mult-bounds/pull/1191) | mightyOil | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1192](https://github.com/CrocSwap/integer-mult-bounds/pull/1192) | rohanarun | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1193](https://github.com/CrocSwap/integer-mult-bounds/pull/1193) | jeremydiviney | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1194](https://github.com/CrocSwap/integer-mult-bounds/pull/1194) | woklerx | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1195](https://github.com/CrocSwap/integer-mult-bounds/pull/1195) | mdumitrean | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1196](https://github.com/CrocSwap/integer-mult-bounds/pull/1196) | chafreaky | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1197](https://github.com/CrocSwap/integer-mult-bounds/pull/1197) | mightyOil | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1198](https://github.com/CrocSwap/integer-mult-bounds/pull/1198) | Scratch-net | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1199](https://github.com/CrocSwap/integer-mult-bounds/pull/1199) | thakrarsagar | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1201](https://github.com/CrocSwap/integer-mult-bounds/pull/1201) | rohanarun | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1203](https://github.com/CrocSwap/integer-mult-bounds/pull/1203) | mightyOil | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1204](https://github.com/CrocSwap/integer-mult-bounds/pull/1204) | GamingPuzzled | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#1205](https://github.com/CrocSwap/integer-mult-bounds/pull/1205) | adamgall | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1206](https://github.com/CrocSwap/integer-mult-bounds/pull/1206) | adamgall | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1207](https://github.com/CrocSwap/integer-mult-bounds/pull/1207) | rohanarun | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1208](https://github.com/CrocSwap/integer-mult-bounds/pull/1208) | ToikY | incorporated | [record 1](../../research/community-efficient300-audit/DISPOSITIONS.json) |
| [#1209](https://github.com/CrocSwap/integer-mult-bounds/pull/1209) | akiva8201-dotcom | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1211](https://github.com/CrocSwap/integer-mult-bounds/pull/1211) | cbethin | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1212](https://github.com/CrocSwap/integer-mult-bounds/pull/1212) | burntout76 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1213](https://github.com/CrocSwap/integer-mult-bounds/pull/1213) | DavidAriasC | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1214](https://github.com/CrocSwap/integer-mult-bounds/pull/1214) | bbMisk | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1215](https://github.com/CrocSwap/integer-mult-bounds/pull/1215) | bbMisk | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1216](https://github.com/CrocSwap/integer-mult-bounds/pull/1216) | RossRichardson | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1217](https://github.com/CrocSwap/integer-mult-bounds/pull/1217) | bbMisk | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1218](https://github.com/CrocSwap/integer-mult-bounds/pull/1218) | rohanarun | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1219](https://github.com/CrocSwap/integer-mult-bounds/pull/1219) | bbMisk | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1220](https://github.com/CrocSwap/integer-mult-bounds/pull/1220) | adamgall | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1221](https://github.com/CrocSwap/integer-mult-bounds/pull/1221) | bbMisk | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1222](https://github.com/CrocSwap/integer-mult-bounds/pull/1222) | bbMisk | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1223](https://github.com/CrocSwap/integer-mult-bounds/pull/1223) | zewelor | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1224](https://github.com/CrocSwap/integer-mult-bounds/pull/1224) | joaqcoo | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1225](https://github.com/CrocSwap/integer-mult-bounds/pull/1225) | rohanarun | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1226](https://github.com/CrocSwap/integer-mult-bounds/pull/1226) | navinor | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1227](https://github.com/CrocSwap/integer-mult-bounds/pull/1227) | thakrarsagar | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1228](https://github.com/CrocSwap/integer-mult-bounds/pull/1228) | Mister-Meeseeks | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1229](https://github.com/CrocSwap/integer-mult-bounds/pull/1229) | bitplane | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1230](https://github.com/CrocSwap/integer-mult-bounds/pull/1230) | ToikY | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1231](https://github.com/CrocSwap/integer-mult-bounds/pull/1231) | Mister-Meeseeks | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1232](https://github.com/CrocSwap/integer-mult-bounds/pull/1232) | Mister-Meeseeks | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1234](https://github.com/CrocSwap/integer-mult-bounds/pull/1234) | RichardHoekstra | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1235](https://github.com/CrocSwap/integer-mult-bounds/pull/1235) | RichardHoekstra | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1236](https://github.com/CrocSwap/integer-mult-bounds/pull/1236) | DavidAriasC | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1238](https://github.com/CrocSwap/integer-mult-bounds/pull/1238) | DreamingOfClouds | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1239](https://github.com/CrocSwap/integer-mult-bounds/pull/1239) | GamingPuzzled | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) |
| [#1242](https://github.com/CrocSwap/integer-mult-bounds/pull/1242) | bbMisk | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1243](https://github.com/CrocSwap/integer-mult-bounds/pull/1243) | bbMisk | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1244](https://github.com/CrocSwap/integer-mult-bounds/pull/1244) | bbMisk | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1245](https://github.com/CrocSwap/integer-mult-bounds/pull/1245) | bbMisk | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1246](https://github.com/CrocSwap/integer-mult-bounds/pull/1246) | bbMisk | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1247](https://github.com/CrocSwap/integer-mult-bounds/pull/1247) | bbMisk | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1248](https://github.com/CrocSwap/integer-mult-bounds/pull/1248) | mightyOil | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1249](https://github.com/CrocSwap/integer-mult-bounds/pull/1249) | bbMisk | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1250](https://github.com/CrocSwap/integer-mult-bounds/pull/1250) | bbMisk | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1252](https://github.com/CrocSwap/integer-mult-bounds/pull/1252) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1253](https://github.com/CrocSwap/integer-mult-bounds/pull/1253) | mightyOil | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1254](https://github.com/CrocSwap/integer-mult-bounds/pull/1254) | mightyOil | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1255](https://github.com/CrocSwap/integer-mult-bounds/pull/1255) | bitplane | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1256](https://github.com/CrocSwap/integer-mult-bounds/pull/1256) | RossRichardson | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1257](https://github.com/CrocSwap/integer-mult-bounds/pull/1257) | bbMisk | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1259](https://github.com/CrocSwap/integer-mult-bounds/pull/1259) | thakrarsagar | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1261](https://github.com/CrocSwap/integer-mult-bounds/pull/1261) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1262](https://github.com/CrocSwap/integer-mult-bounds/pull/1262) | thakrarsagar | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1263](https://github.com/CrocSwap/integer-mult-bounds/pull/1263) | mightyOil | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1266](https://github.com/CrocSwap/integer-mult-bounds/pull/1266) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1270](https://github.com/CrocSwap/integer-mult-bounds/pull/1270) | mightyOil | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1271](https://github.com/CrocSwap/integer-mult-bounds/pull/1271) | mightyOil | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1273](https://github.com/CrocSwap/integer-mult-bounds/pull/1273) | theon199 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1274](https://github.com/CrocSwap/integer-mult-bounds/pull/1274) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1276](https://github.com/CrocSwap/integer-mult-bounds/pull/1276) | PatatePatatePatate | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1277](https://github.com/CrocSwap/integer-mult-bounds/pull/1277) | thakrarsagar | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1278](https://github.com/CrocSwap/integer-mult-bounds/pull/1278) | cbethin | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1281](https://github.com/CrocSwap/integer-mult-bounds/pull/1281) | mightyOil | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1282](https://github.com/CrocSwap/integer-mult-bounds/pull/1282) | bitplane | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1284](https://github.com/CrocSwap/integer-mult-bounds/pull/1284) | thakrarsagar | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1285](https://github.com/CrocSwap/integer-mult-bounds/pull/1285) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1286](https://github.com/CrocSwap/integer-mult-bounds/pull/1286) | rohanarun | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1287](https://github.com/CrocSwap/integer-mult-bounds/pull/1287) | RossRichardson | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1288](https://github.com/CrocSwap/integer-mult-bounds/pull/1288) | Wronskode | partially reviewed | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1292](https://github.com/CrocSwap/integer-mult-bounds/pull/1292) | navinor | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1293](https://github.com/CrocSwap/integer-mult-bounds/pull/1293) | navinor | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1294](https://github.com/CrocSwap/integer-mult-bounds/pull/1294) | mightyOil | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1295](https://github.com/CrocSwap/integer-mult-bounds/pull/1295) | mightyOil | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1296](https://github.com/CrocSwap/integer-mult-bounds/pull/1296) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1297](https://github.com/CrocSwap/integer-mult-bounds/pull/1297) | rohanarun | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1298](https://github.com/CrocSwap/integer-mult-bounds/pull/1298) | rtyu193-rgb | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1299](https://github.com/CrocSwap/integer-mult-bounds/pull/1299) | cbethin | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1300](https://github.com/CrocSwap/integer-mult-bounds/pull/1300) | mightyOil | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1302](https://github.com/CrocSwap/integer-mult-bounds/pull/1302) | theon199 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1303](https://github.com/CrocSwap/integer-mult-bounds/pull/1303) | mightyOil | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1304](https://github.com/CrocSwap/integer-mult-bounds/pull/1304) | commdata2338 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1306](https://github.com/CrocSwap/integer-mult-bounds/pull/1306) | commdata2338 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1307](https://github.com/CrocSwap/integer-mult-bounds/pull/1307) | commdata2338 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1308](https://github.com/CrocSwap/integer-mult-bounds/pull/1308) | mightyOil | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1309](https://github.com/CrocSwap/integer-mult-bounds/pull/1309) | bitplane | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1310](https://github.com/CrocSwap/integer-mult-bounds/pull/1310) | mightyOil | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1311](https://github.com/CrocSwap/integer-mult-bounds/pull/1311) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1312](https://github.com/CrocSwap/integer-mult-bounds/pull/1312) | navinor | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1313](https://github.com/CrocSwap/integer-mult-bounds/pull/1313) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1318](https://github.com/CrocSwap/integer-mult-bounds/pull/1318) | RichardHoekstra | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1319](https://github.com/CrocSwap/integer-mult-bounds/pull/1319) | rohanarun | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient400-audit/DISPOSITIONS.json) |
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
| [#1337](https://github.com/CrocSwap/integer-mult-bounds/pull/1337) | mdumitrean | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1338](https://github.com/CrocSwap/integer-mult-bounds/pull/1338) | Wronskode | partially reviewed | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1340](https://github.com/CrocSwap/integer-mult-bounds/pull/1340) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1341](https://github.com/CrocSwap/integer-mult-bounds/pull/1341) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1342](https://github.com/CrocSwap/integer-mult-bounds/pull/1342) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1343](https://github.com/CrocSwap/integer-mult-bounds/pull/1343) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient400-audit/DISPOSITIONS.json) |
| [#1344](https://github.com/CrocSwap/integer-mult-bounds/pull/1344) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1345](https://github.com/CrocSwap/integer-mult-bounds/pull/1345) | hipotures | partially reviewed | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient500-audit/DISPOSITIONS.json) |
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
| [#1364](https://github.com/CrocSwap/integer-mult-bounds/pull/1364) | GamingPuzzled | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#1365](https://github.com/CrocSwap/integer-mult-bounds/pull/1365) | cheesegrader | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient500-audit/DISPOSITIONS.json) |
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
| [#1377](https://github.com/CrocSwap/integer-mult-bounds/pull/1377) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient500-audit/DISPOSITIONS.json) |
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
| [#1392](https://github.com/CrocSwap/integer-mult-bounds/pull/1392) | brianross93 | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient500-audit/DISPOSITIONS.json) |
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
| [#1407](https://github.com/CrocSwap/integer-mult-bounds/pull/1407) | pai-scaffolde | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) |
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
| [#1424](https://github.com/CrocSwap/integer-mult-bounds/pull/1424) | rohanarun | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient500-audit/DISPOSITIONS.json) |
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
| [#1444](https://github.com/CrocSwap/integer-mult-bounds/pull/1444) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient500-audit/DISPOSITIONS.json) |
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
| [#1458](https://github.com/CrocSwap/integer-mult-bounds/pull/1458) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1459](https://github.com/CrocSwap/integer-mult-bounds/pull/1459) | CubeJerry | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1460](https://github.com/CrocSwap/integer-mult-bounds/pull/1460) | bbMisk | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1461](https://github.com/CrocSwap/integer-mult-bounds/pull/1461) | CubeJerry | incorporated | [record 1](../../research/community-efficient500-audit/DISPOSITIONS.json) |
| [#1464](https://github.com/CrocSwap/integer-mult-bounds/pull/1464) | rohanarun | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient500-audit/DISPOSITIONS.json) |
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
| [#1479](https://github.com/CrocSwap/integer-mult-bounds/pull/1479) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1480](https://github.com/CrocSwap/integer-mult-bounds/pull/1480) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1481](https://github.com/CrocSwap/integer-mult-bounds/pull/1481) | theon199 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1482](https://github.com/CrocSwap/integer-mult-bounds/pull/1482) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1483](https://github.com/CrocSwap/integer-mult-bounds/pull/1483) | CubeJerry | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1484](https://github.com/CrocSwap/integer-mult-bounds/pull/1484) | p-romeo | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1485](https://github.com/CrocSwap/integer-mult-bounds/pull/1485) | rohanarun | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1487](https://github.com/CrocSwap/integer-mult-bounds/pull/1487) | ianlibanio | partially reviewed | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1488](https://github.com/CrocSwap/integer-mult-bounds/pull/1488) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1490](https://github.com/CrocSwap/integer-mult-bounds/pull/1490) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1491](https://github.com/CrocSwap/integer-mult-bounds/pull/1491) | commdata2338 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1494](https://github.com/CrocSwap/integer-mult-bounds/pull/1494) | cheesegrader | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) · [record 2](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1495](https://github.com/CrocSwap/integer-mult-bounds/pull/1495) | commdata2338 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1496](https://github.com/CrocSwap/integer-mult-bounds/pull/1496) | commdata2338 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1497](https://github.com/CrocSwap/integer-mult-bounds/pull/1497) | an664 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1498](https://github.com/CrocSwap/integer-mult-bounds/pull/1498) | bitplane | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1499](https://github.com/CrocSwap/integer-mult-bounds/pull/1499) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1500](https://github.com/CrocSwap/integer-mult-bounds/pull/1500) | thakrarsagar | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1506](https://github.com/CrocSwap/integer-mult-bounds/pull/1506) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1508](https://github.com/CrocSwap/integer-mult-bounds/pull/1508) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1509](https://github.com/CrocSwap/integer-mult-bounds/pull/1509) | thakrarsagar | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1510](https://github.com/CrocSwap/integer-mult-bounds/pull/1510) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1511](https://github.com/CrocSwap/integer-mult-bounds/pull/1511) | an664 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1512](https://github.com/CrocSwap/integer-mult-bounds/pull/1512) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1513](https://github.com/CrocSwap/integer-mult-bounds/pull/1513) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1517](https://github.com/CrocSwap/integer-mult-bounds/pull/1517) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1518](https://github.com/CrocSwap/integer-mult-bounds/pull/1518) | hevlyo | incorporated | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1520](https://github.com/CrocSwap/integer-mult-bounds/pull/1520) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1521](https://github.com/CrocSwap/integer-mult-bounds/pull/1521) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1522](https://github.com/CrocSwap/integer-mult-bounds/pull/1522) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1523](https://github.com/CrocSwap/integer-mult-bounds/pull/1523) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1524](https://github.com/CrocSwap/integer-mult-bounds/pull/1524) | TennisBowling | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1526](https://github.com/CrocSwap/integer-mult-bounds/pull/1526) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1528](https://github.com/CrocSwap/integer-mult-bounds/pull/1528) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1529](https://github.com/CrocSwap/integer-mult-bounds/pull/1529) | higherbeing | partially reviewed | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1530](https://github.com/CrocSwap/integer-mult-bounds/pull/1530) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1531](https://github.com/CrocSwap/integer-mult-bounds/pull/1531) | navinor | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1532](https://github.com/CrocSwap/integer-mult-bounds/pull/1532) | theon199 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1533](https://github.com/CrocSwap/integer-mult-bounds/pull/1533) | CubeJerry | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1534](https://github.com/CrocSwap/integer-mult-bounds/pull/1534) | midhatn | partially reviewed | [record 1](../../research/community-efficient2000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1535](https://github.com/CrocSwap/integer-mult-bounds/pull/1535) | CubeJerry | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1536](https://github.com/CrocSwap/integer-mult-bounds/pull/1536) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1537](https://github.com/CrocSwap/integer-mult-bounds/pull/1537) | thakrarsagar | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1538](https://github.com/CrocSwap/integer-mult-bounds/pull/1538) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1541](https://github.com/CrocSwap/integer-mult-bounds/pull/1541) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1543](https://github.com/CrocSwap/integer-mult-bounds/pull/1543) | ToikY | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1546](https://github.com/CrocSwap/integer-mult-bounds/pull/1546) | an664 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1549](https://github.com/CrocSwap/integer-mult-bounds/pull/1549) | midhatn | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient600-audit/DISPOSITIONS.json) |
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
| [#1574](https://github.com/CrocSwap/integer-mult-bounds/pull/1574) | rohanarun | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1575](https://github.com/CrocSwap/integer-mult-bounds/pull/1575) | bbMisk | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1576](https://github.com/CrocSwap/integer-mult-bounds/pull/1576) | navinor | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1577](https://github.com/CrocSwap/integer-mult-bounds/pull/1577) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1578](https://github.com/CrocSwap/integer-mult-bounds/pull/1578) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1580](https://github.com/CrocSwap/integer-mult-bounds/pull/1580) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1582](https://github.com/CrocSwap/integer-mult-bounds/pull/1582) | midhatn | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1583](https://github.com/CrocSwap/integer-mult-bounds/pull/1583) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1584](https://github.com/CrocSwap/integer-mult-bounds/pull/1584) | thakrarsagar | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1586](https://github.com/CrocSwap/integer-mult-bounds/pull/1586) | dataisfire | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1589](https://github.com/CrocSwap/integer-mult-bounds/pull/1589) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1590](https://github.com/CrocSwap/integer-mult-bounds/pull/1590) | DreamingOfClouds | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1591](https://github.com/CrocSwap/integer-mult-bounds/pull/1591) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1592](https://github.com/CrocSwap/integer-mult-bounds/pull/1592) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1595](https://github.com/CrocSwap/integer-mult-bounds/pull/1595) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1598](https://github.com/CrocSwap/integer-mult-bounds/pull/1598) | an664 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1600](https://github.com/CrocSwap/integer-mult-bounds/pull/1600) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient600-audit/DISPOSITIONS.json) |
| [#1601](https://github.com/CrocSwap/integer-mult-bounds/pull/1601) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient700-audit/DISPOSITIONS.json) |
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
| [#1617](https://github.com/CrocSwap/integer-mult-bounds/pull/1617) | bbMisk | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1619](https://github.com/CrocSwap/integer-mult-bounds/pull/1619) | jackmgaller | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1623](https://github.com/CrocSwap/integer-mult-bounds/pull/1623) | navinor | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1624](https://github.com/CrocSwap/integer-mult-bounds/pull/1624) | an664 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1625](https://github.com/CrocSwap/integer-mult-bounds/pull/1625) | mdumitrean | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1626](https://github.com/CrocSwap/integer-mult-bounds/pull/1626) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1627](https://github.com/CrocSwap/integer-mult-bounds/pull/1627) | alephnan | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1628](https://github.com/CrocSwap/integer-mult-bounds/pull/1628) | Tuafo | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1629](https://github.com/CrocSwap/integer-mult-bounds/pull/1629) | rohanarun | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1631](https://github.com/CrocSwap/integer-mult-bounds/pull/1631) | theon199 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1632](https://github.com/CrocSwap/integer-mult-bounds/pull/1632) | bbMisk | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1633](https://github.com/CrocSwap/integer-mult-bounds/pull/1633) | bbMisk | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1637](https://github.com/CrocSwap/integer-mult-bounds/pull/1637) | cbethin | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1638](https://github.com/CrocSwap/integer-mult-bounds/pull/1638) | ToikY | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1640](https://github.com/CrocSwap/integer-mult-bounds/pull/1640) | midhatn | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1641](https://github.com/CrocSwap/integer-mult-bounds/pull/1641) | Dugongue | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1642](https://github.com/CrocSwap/integer-mult-bounds/pull/1642) | theon199 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1643](https://github.com/CrocSwap/integer-mult-bounds/pull/1643) | antunishdPursuit | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1644](https://github.com/CrocSwap/integer-mult-bounds/pull/1644) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient700-audit/DISPOSITIONS.json) |
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
| [#1661](https://github.com/CrocSwap/integer-mult-bounds/pull/1661) | midhatn | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1662](https://github.com/CrocSwap/integer-mult-bounds/pull/1662) | ToikY | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1663](https://github.com/CrocSwap/integer-mult-bounds/pull/1663) | JosieElliston | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1664](https://github.com/CrocSwap/integer-mult-bounds/pull/1664) | an664 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1665](https://github.com/CrocSwap/integer-mult-bounds/pull/1665) | navinor | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1666](https://github.com/CrocSwap/integer-mult-bounds/pull/1666) | RossRichardson | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1668](https://github.com/CrocSwap/integer-mult-bounds/pull/1668) | JosieElliston | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1669](https://github.com/CrocSwap/integer-mult-bounds/pull/1669) | navinor | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1670](https://github.com/CrocSwap/integer-mult-bounds/pull/1670) | JosieElliston | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1671](https://github.com/CrocSwap/integer-mult-bounds/pull/1671) | bitplane | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1672](https://github.com/CrocSwap/integer-mult-bounds/pull/1672) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1673](https://github.com/CrocSwap/integer-mult-bounds/pull/1673) | Vlado-V | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1675](https://github.com/CrocSwap/integer-mult-bounds/pull/1675) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1676](https://github.com/CrocSwap/integer-mult-bounds/pull/1676) | an664 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1677](https://github.com/CrocSwap/integer-mult-bounds/pull/1677) | midhatn | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1678](https://github.com/CrocSwap/integer-mult-bounds/pull/1678) | RossRichardson | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1679](https://github.com/CrocSwap/integer-mult-bounds/pull/1679) | Maximooch | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1680](https://github.com/CrocSwap/integer-mult-bounds/pull/1680) | ToikY | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1681](https://github.com/CrocSwap/integer-mult-bounds/pull/1681) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1682](https://github.com/CrocSwap/integer-mult-bounds/pull/1682) | RossRichardson | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1683](https://github.com/CrocSwap/integer-mult-bounds/pull/1683) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1684](https://github.com/CrocSwap/integer-mult-bounds/pull/1684) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1685](https://github.com/CrocSwap/integer-mult-bounds/pull/1685) | Maximooch | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1686](https://github.com/CrocSwap/integer-mult-bounds/pull/1686) | RossRichardson | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1688](https://github.com/CrocSwap/integer-mult-bounds/pull/1688) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1689](https://github.com/CrocSwap/integer-mult-bounds/pull/1689) | just-mn | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1690](https://github.com/CrocSwap/integer-mult-bounds/pull/1690) | navinor | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1692](https://github.com/CrocSwap/integer-mult-bounds/pull/1692) | midhatn | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1696](https://github.com/CrocSwap/integer-mult-bounds/pull/1696) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1697](https://github.com/CrocSwap/integer-mult-bounds/pull/1697) | navinor | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1698](https://github.com/CrocSwap/integer-mult-bounds/pull/1698) | an664 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1699](https://github.com/CrocSwap/integer-mult-bounds/pull/1699) | chafreaky | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient700-audit/DISPOSITIONS.json) |
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
| [#1712](https://github.com/CrocSwap/integer-mult-bounds/pull/1712) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1714](https://github.com/CrocSwap/integer-mult-bounds/pull/1714) | alephnan | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1716](https://github.com/CrocSwap/integer-mult-bounds/pull/1716) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1717](https://github.com/CrocSwap/integer-mult-bounds/pull/1717) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1718](https://github.com/CrocSwap/integer-mult-bounds/pull/1718) | Pseudoataraxia | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1719](https://github.com/CrocSwap/integer-mult-bounds/pull/1719) | aliromman | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1720](https://github.com/CrocSwap/integer-mult-bounds/pull/1720) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1721](https://github.com/CrocSwap/integer-mult-bounds/pull/1721) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1722](https://github.com/CrocSwap/integer-mult-bounds/pull/1722) | RossRichardson | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1724](https://github.com/CrocSwap/integer-mult-bounds/pull/1724) | midhatn | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1725](https://github.com/CrocSwap/integer-mult-bounds/pull/1725) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1726](https://github.com/CrocSwap/integer-mult-bounds/pull/1726) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient700-audit/DISPOSITIONS.json) |
| [#1729](https://github.com/CrocSwap/integer-mult-bounds/pull/1729) | jmbarrancoml | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1731](https://github.com/CrocSwap/integer-mult-bounds/pull/1731) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1732](https://github.com/CrocSwap/integer-mult-bounds/pull/1732) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1733](https://github.com/CrocSwap/integer-mult-bounds/pull/1733) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1734](https://github.com/CrocSwap/integer-mult-bounds/pull/1734) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1735](https://github.com/CrocSwap/integer-mult-bounds/pull/1735) | rtyu193-rgb | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1736](https://github.com/CrocSwap/integer-mult-bounds/pull/1736) | thakrarsagar | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1739](https://github.com/CrocSwap/integer-mult-bounds/pull/1739) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1741](https://github.com/CrocSwap/integer-mult-bounds/pull/1741) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1742](https://github.com/CrocSwap/integer-mult-bounds/pull/1742) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1744](https://github.com/CrocSwap/integer-mult-bounds/pull/1744) | Tuafo | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1745](https://github.com/CrocSwap/integer-mult-bounds/pull/1745) | 1337isnot1337 | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1746](https://github.com/CrocSwap/integer-mult-bounds/pull/1746) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1747](https://github.com/CrocSwap/integer-mult-bounds/pull/1747) | RossRichardson | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1748](https://github.com/CrocSwap/integer-mult-bounds/pull/1748) | ToikY | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1749](https://github.com/CrocSwap/integer-mult-bounds/pull/1749) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1750](https://github.com/CrocSwap/integer-mult-bounds/pull/1750) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1752](https://github.com/CrocSwap/integer-mult-bounds/pull/1752) | thakrarsagar | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1754](https://github.com/CrocSwap/integer-mult-bounds/pull/1754) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1755](https://github.com/CrocSwap/integer-mult-bounds/pull/1755) | navinor | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1756](https://github.com/CrocSwap/integer-mult-bounds/pull/1756) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1757](https://github.com/CrocSwap/integer-mult-bounds/pull/1757) | jmbarrancoml | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1758](https://github.com/CrocSwap/integer-mult-bounds/pull/1758) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 7](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1761](https://github.com/CrocSwap/integer-mult-bounds/pull/1761) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1763](https://github.com/CrocSwap/integer-mult-bounds/pull/1763) | navinor | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient800-audit/DISPOSITIONS.json) |
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
| [#1786](https://github.com/CrocSwap/integer-mult-bounds/pull/1786) | chafreaky | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1787](https://github.com/CrocSwap/integer-mult-bounds/pull/1787) | JosieElliston | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1788](https://github.com/CrocSwap/integer-mult-bounds/pull/1788) | JosieElliston | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1789](https://github.com/CrocSwap/integer-mult-bounds/pull/1789) | midhatn | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1790](https://github.com/CrocSwap/integer-mult-bounds/pull/1790) | navinor | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1791](https://github.com/CrocSwap/integer-mult-bounds/pull/1791) | rtyu193-rgb | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1792](https://github.com/CrocSwap/integer-mult-bounds/pull/1792) | JosieElliston | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1793](https://github.com/CrocSwap/integer-mult-bounds/pull/1793) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1794](https://github.com/CrocSwap/integer-mult-bounds/pull/1794) | Maximooch | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1797](https://github.com/CrocSwap/integer-mult-bounds/pull/1797) | JosieElliston | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1799](https://github.com/CrocSwap/integer-mult-bounds/pull/1799) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1800](https://github.com/CrocSwap/integer-mult-bounds/pull/1800) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient800-audit/DISPOSITIONS.json) |
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
| [#1816](https://github.com/CrocSwap/integer-mult-bounds/pull/1816) | JosieElliston | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1817](https://github.com/CrocSwap/integer-mult-bounds/pull/1817) | JosieElliston | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1819](https://github.com/CrocSwap/integer-mult-bounds/pull/1819) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1821](https://github.com/CrocSwap/integer-mult-bounds/pull/1821) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1822](https://github.com/CrocSwap/integer-mult-bounds/pull/1822) | navinor | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1823](https://github.com/CrocSwap/integer-mult-bounds/pull/1823) | navinor | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1824](https://github.com/CrocSwap/integer-mult-bounds/pull/1824) | JosieElliston | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1825](https://github.com/CrocSwap/integer-mult-bounds/pull/1825) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1826](https://github.com/CrocSwap/integer-mult-bounds/pull/1826) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1827](https://github.com/CrocSwap/integer-mult-bounds/pull/1827) | mightyOil | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1828](https://github.com/CrocSwap/integer-mult-bounds/pull/1828) | rohanarun | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1829](https://github.com/CrocSwap/integer-mult-bounds/pull/1829) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1830](https://github.com/CrocSwap/integer-mult-bounds/pull/1830) | RossRichardson | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1833](https://github.com/CrocSwap/integer-mult-bounds/pull/1833) | ToikY | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1834](https://github.com/CrocSwap/integer-mult-bounds/pull/1834) | navinor | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1837](https://github.com/CrocSwap/integer-mult-bounds/pull/1837) | navinor | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1838](https://github.com/CrocSwap/integer-mult-bounds/pull/1838) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient800-audit/DISPOSITIONS.json) |
| [#1839](https://github.com/CrocSwap/integer-mult-bounds/pull/1839) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient800-audit/DISPOSITIONS.json) |
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
| [#1861](https://github.com/CrocSwap/integer-mult-bounds/pull/1861) | VictorLiwentao | partially reviewed | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient800-audit/DISPOSITIONS.json) |
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
| [#1875](https://github.com/CrocSwap/integer-mult-bounds/pull/1875) | rohanarun | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1876](https://github.com/CrocSwap/integer-mult-bounds/pull/1876) | rohanarun | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient900-audit/DISPOSITIONS.json) |
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
| [#1897](https://github.com/CrocSwap/integer-mult-bounds/pull/1897) | M6LI | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1900](https://github.com/CrocSwap/integer-mult-bounds/pull/1900) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1902](https://github.com/CrocSwap/integer-mult-bounds/pull/1902) | bbMisk | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1904](https://github.com/CrocSwap/integer-mult-bounds/pull/1904) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1905](https://github.com/CrocSwap/integer-mult-bounds/pull/1905) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient900-audit/DISPOSITIONS.json) |
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
| [#1922](https://github.com/CrocSwap/integer-mult-bounds/pull/1922) | VictorLiwentao | partially reviewed | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1923](https://github.com/CrocSwap/integer-mult-bounds/pull/1923) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1924](https://github.com/CrocSwap/integer-mult-bounds/pull/1924) | ToikY | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1925](https://github.com/CrocSwap/integer-mult-bounds/pull/1925) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1926](https://github.com/CrocSwap/integer-mult-bounds/pull/1926) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1928](https://github.com/CrocSwap/integer-mult-bounds/pull/1928) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient900-audit/DISPOSITIONS.json) |
| [#1930](https://github.com/CrocSwap/integer-mult-bounds/pull/1930) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2600-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient900-audit/DISPOSITIONS.json) |
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
| [#1957](https://github.com/CrocSwap/integer-mult-bounds/pull/1957) | rohanarun | partially reviewed | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) |
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
| [#1992](https://github.com/CrocSwap/integer-mult-bounds/pull/1992) | rohanarun | partially reviewed | [record 1](../../research/community-efficient1000-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) |
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
| [#2031](https://github.com/CrocSwap/integer-mult-bounds/pull/2031) | DreamingOfClouds | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) |
| [#2033](https://github.com/CrocSwap/integer-mult-bounds/pull/2033) | ToikY | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2035](https://github.com/CrocSwap/integer-mult-bounds/pull/2035) | Tairitsu-Aya | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2037](https://github.com/CrocSwap/integer-mult-bounds/pull/2037) | commdata2338 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2039](https://github.com/CrocSwap/integer-mult-bounds/pull/2039) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2040](https://github.com/CrocSwap/integer-mult-bounds/pull/2040) | commdata2338 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2041](https://github.com/CrocSwap/integer-mult-bounds/pull/2041) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2042](https://github.com/CrocSwap/integer-mult-bounds/pull/2042) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2044](https://github.com/CrocSwap/integer-mult-bounds/pull/2044) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2045](https://github.com/CrocSwap/integer-mult-bounds/pull/2045) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2046](https://github.com/CrocSwap/integer-mult-bounds/pull/2046) | navinor | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
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
| [#2077](https://github.com/CrocSwap/integer-mult-bounds/pull/2077) | lydakis | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) |
| [#2078](https://github.com/CrocSwap/integer-mult-bounds/pull/2078) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2079](https://github.com/CrocSwap/integer-mult-bounds/pull/2079) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2081](https://github.com/CrocSwap/integer-mult-bounds/pull/2081) | Tairitsu-Aya | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) |
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
| [#2101](https://github.com/CrocSwap/integer-mult-bounds/pull/2101) | adamgall | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) |
| [#2103](https://github.com/CrocSwap/integer-mult-bounds/pull/2103) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2104](https://github.com/CrocSwap/integer-mult-bounds/pull/2104) | RossRichardson | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2105](https://github.com/CrocSwap/integer-mult-bounds/pull/2105) | theon199 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2108](https://github.com/CrocSwap/integer-mult-bounds/pull/2108) | jmbarrancoml | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2110](https://github.com/CrocSwap/integer-mult-bounds/pull/2110) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111) | DreamingOfClouds | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) |
| [#2112](https://github.com/CrocSwap/integer-mult-bounds/pull/2112) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2113](https://github.com/CrocSwap/integer-mult-bounds/pull/2113) | jeremydiviney | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2115](https://github.com/CrocSwap/integer-mult-bounds/pull/2115) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2116](https://github.com/CrocSwap/integer-mult-bounds/pull/2116) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2117](https://github.com/CrocSwap/integer-mult-bounds/pull/2117) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2118](https://github.com/CrocSwap/integer-mult-bounds/pull/2118) | 1337isnot1337 | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) |
| [#2120](https://github.com/CrocSwap/integer-mult-bounds/pull/2120) | petalas | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2122](https://github.com/CrocSwap/integer-mult-bounds/pull/2122) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2124](https://github.com/CrocSwap/integer-mult-bounds/pull/2124) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2125](https://github.com/CrocSwap/integer-mult-bounds/pull/2125) | DreamingOfClouds | partially reviewed | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) |
| [#2126](https://github.com/CrocSwap/integer-mult-bounds/pull/2126) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2127](https://github.com/CrocSwap/integer-mult-bounds/pull/2127) | RossRichardson | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2128](https://github.com/CrocSwap/integer-mult-bounds/pull/2128) | navinor | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2129](https://github.com/CrocSwap/integer-mult-bounds/pull/2129) | petalas | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2130](https://github.com/CrocSwap/integer-mult-bounds/pull/2130) | navinor | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2132](https://github.com/CrocSwap/integer-mult-bounds/pull/2132) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2133](https://github.com/CrocSwap/integer-mult-bounds/pull/2133) | navinor | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2134](https://github.com/CrocSwap/integer-mult-bounds/pull/2134) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) · [record 2](../../research/community-efficient1100-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2135](https://github.com/CrocSwap/integer-mult-bounds/pull/2135) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1100-audit/DISPOSITIONS.json) |
| [#2136](https://github.com/CrocSwap/integer-mult-bounds/pull/2136) | Tairitsu-Aya | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2137](https://github.com/CrocSwap/integer-mult-bounds/pull/2137) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2139](https://github.com/CrocSwap/integer-mult-bounds/pull/2139) | jmbarrancoml | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2140](https://github.com/CrocSwap/integer-mult-bounds/pull/2140) | petalas | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2142](https://github.com/CrocSwap/integer-mult-bounds/pull/2142) | ianlibanio | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) |
| [#2145](https://github.com/CrocSwap/integer-mult-bounds/pull/2145) | navinor | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2146](https://github.com/CrocSwap/integer-mult-bounds/pull/2146) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2147](https://github.com/CrocSwap/integer-mult-bounds/pull/2147) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2148](https://github.com/CrocSwap/integer-mult-bounds/pull/2148) | petalas | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2150](https://github.com/CrocSwap/integer-mult-bounds/pull/2150) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2151](https://github.com/CrocSwap/integer-mult-bounds/pull/2151) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2152](https://github.com/CrocSwap/integer-mult-bounds/pull/2152) | DavidAriasC | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2153](https://github.com/CrocSwap/integer-mult-bounds/pull/2153) | commdata2338 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2154](https://github.com/CrocSwap/integer-mult-bounds/pull/2154) | commdata2338 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2156](https://github.com/CrocSwap/integer-mult-bounds/pull/2156) | Tairitsu-Aya | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2157](https://github.com/CrocSwap/integer-mult-bounds/pull/2157) | jmbarrancoml | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2158](https://github.com/CrocSwap/integer-mult-bounds/pull/2158) | navinor | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2159](https://github.com/CrocSwap/integer-mult-bounds/pull/2159) | RossRichardson | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2160](https://github.com/CrocSwap/integer-mult-bounds/pull/2160) | commdata2338 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2161](https://github.com/CrocSwap/integer-mult-bounds/pull/2161) | dataisfire | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2162](https://github.com/CrocSwap/integer-mult-bounds/pull/2162) | DreamingOfClouds | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1400-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2100-audit/DISPOSITIONS.json) |
| [#2163](https://github.com/CrocSwap/integer-mult-bounds/pull/2163) | AgoraPluribusMichael | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2166](https://github.com/CrocSwap/integer-mult-bounds/pull/2166) | petalas | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2167](https://github.com/CrocSwap/integer-mult-bounds/pull/2167) | waynenilsen | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) |
| [#2168](https://github.com/CrocSwap/integer-mult-bounds/pull/2168) | dataisfire | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2169](https://github.com/CrocSwap/integer-mult-bounds/pull/2169) | philippeVV | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2171](https://github.com/CrocSwap/integer-mult-bounds/pull/2171) | jmbarrancoml | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2172](https://github.com/CrocSwap/integer-mult-bounds/pull/2172) | commdata2338 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2173](https://github.com/CrocSwap/integer-mult-bounds/pull/2173) | Gonzalo-Mier | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2174](https://github.com/CrocSwap/integer-mult-bounds/pull/2174) | commdata2338 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2175](https://github.com/CrocSwap/integer-mult-bounds/pull/2175) | petalas | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2176](https://github.com/CrocSwap/integer-mult-bounds/pull/2176) | RossRichardson | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2177](https://github.com/CrocSwap/integer-mult-bounds/pull/2177) | philippeVV | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2178](https://github.com/CrocSwap/integer-mult-bounds/pull/2178) | commdata2338 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2180](https://github.com/CrocSwap/integer-mult-bounds/pull/2180) | dataisfire | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2181](https://github.com/CrocSwap/integer-mult-bounds/pull/2181) | petalas | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2182](https://github.com/CrocSwap/integer-mult-bounds/pull/2182) | conorholds | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2183](https://github.com/CrocSwap/integer-mult-bounds/pull/2183) | petalas | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2184](https://github.com/CrocSwap/integer-mult-bounds/pull/2184) | dataisfire | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2300-audit/DISPOSITIONS.json) |
| [#2186](https://github.com/CrocSwap/integer-mult-bounds/pull/2186) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2187](https://github.com/CrocSwap/integer-mult-bounds/pull/2187) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2188](https://github.com/CrocSwap/integer-mult-bounds/pull/2188) | commdata2338 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2189](https://github.com/CrocSwap/integer-mult-bounds/pull/2189) | commdata2338 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2190](https://github.com/CrocSwap/integer-mult-bounds/pull/2190) | commdata2338 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2191](https://github.com/CrocSwap/integer-mult-bounds/pull/2191) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2193](https://github.com/CrocSwap/integer-mult-bounds/pull/2193) | petalas | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2194](https://github.com/CrocSwap/integer-mult-bounds/pull/2194) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2195](https://github.com/CrocSwap/integer-mult-bounds/pull/2195) | jmbarrancoml | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2196](https://github.com/CrocSwap/integer-mult-bounds/pull/2196) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2197](https://github.com/CrocSwap/integer-mult-bounds/pull/2197) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2199](https://github.com/CrocSwap/integer-mult-bounds/pull/2199) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2201](https://github.com/CrocSwap/integer-mult-bounds/pull/2201) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2203](https://github.com/CrocSwap/integer-mult-bounds/pull/2203) | jeremydiviney | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2204](https://github.com/CrocSwap/integer-mult-bounds/pull/2204) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2206](https://github.com/CrocSwap/integer-mult-bounds/pull/2206) | petalas | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2207](https://github.com/CrocSwap/integer-mult-bounds/pull/2207) | jmbarrancoml | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2208](https://github.com/CrocSwap/integer-mult-bounds/pull/2208) | conorholds | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) |
| [#2210](https://github.com/CrocSwap/integer-mult-bounds/pull/2210) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2212](https://github.com/CrocSwap/integer-mult-bounds/pull/2212) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2213](https://github.com/CrocSwap/integer-mult-bounds/pull/2213) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2214](https://github.com/CrocSwap/integer-mult-bounds/pull/2214) | petalas | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2215](https://github.com/CrocSwap/integer-mult-bounds/pull/2215) | thakrarsagar | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2216](https://github.com/CrocSwap/integer-mult-bounds/pull/2216) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) · [record 2](../../research/community-efficient1200-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2217](https://github.com/CrocSwap/integer-mult-bounds/pull/2217) | steph4n-gh | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2219](https://github.com/CrocSwap/integer-mult-bounds/pull/2219) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2220](https://github.com/CrocSwap/integer-mult-bounds/pull/2220) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) |
| [#2222](https://github.com/CrocSwap/integer-mult-bounds/pull/2222) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2224](https://github.com/CrocSwap/integer-mult-bounds/pull/2224) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2225](https://github.com/CrocSwap/integer-mult-bounds/pull/2225) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2226](https://github.com/CrocSwap/integer-mult-bounds/pull/2226) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2227](https://github.com/CrocSwap/integer-mult-bounds/pull/2227) | conorholds | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2228](https://github.com/CrocSwap/integer-mult-bounds/pull/2228) | DreamingOfClouds | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2229](https://github.com/CrocSwap/integer-mult-bounds/pull/2229) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2230](https://github.com/CrocSwap/integer-mult-bounds/pull/2230) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2231](https://github.com/CrocSwap/integer-mult-bounds/pull/2231) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2232](https://github.com/CrocSwap/integer-mult-bounds/pull/2232) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2233](https://github.com/CrocSwap/integer-mult-bounds/pull/2233) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2234](https://github.com/CrocSwap/integer-mult-bounds/pull/2234) | jmbarrancoml | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2235](https://github.com/CrocSwap/integer-mult-bounds/pull/2235) | Dugongue | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2236](https://github.com/CrocSwap/integer-mult-bounds/pull/2236) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2237](https://github.com/CrocSwap/integer-mult-bounds/pull/2237) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2239](https://github.com/CrocSwap/integer-mult-bounds/pull/2239) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2240](https://github.com/CrocSwap/integer-mult-bounds/pull/2240) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2241](https://github.com/CrocSwap/integer-mult-bounds/pull/2241) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2244](https://github.com/CrocSwap/integer-mult-bounds/pull/2244) | DreamingOfClouds | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1400-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2246](https://github.com/CrocSwap/integer-mult-bounds/pull/2246) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2247](https://github.com/CrocSwap/integer-mult-bounds/pull/2247) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2248](https://github.com/CrocSwap/integer-mult-bounds/pull/2248) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2249](https://github.com/CrocSwap/integer-mult-bounds/pull/2249) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) · [record 2](../../research/community-efficient1200-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2250](https://github.com/CrocSwap/integer-mult-bounds/pull/2250) | jmbarrancoml | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2251](https://github.com/CrocSwap/integer-mult-bounds/pull/2251) | bitplane | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2252](https://github.com/CrocSwap/integer-mult-bounds/pull/2252) | cbethin | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) |
| [#2255](https://github.com/CrocSwap/integer-mult-bounds/pull/2255) | navinor | incorporated | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2257](https://github.com/CrocSwap/integer-mult-bounds/pull/2257) | VictorLiwentao | partially reviewed | [record 1](../../research/community-efficient1200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2258](https://github.com/CrocSwap/integer-mult-bounds/pull/2258) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2259](https://github.com/CrocSwap/integer-mult-bounds/pull/2259) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2260](https://github.com/CrocSwap/integer-mult-bounds/pull/2260) | Dugongue | partially reviewed | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) |
| [#2261](https://github.com/CrocSwap/integer-mult-bounds/pull/2261) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2263](https://github.com/CrocSwap/integer-mult-bounds/pull/2263) | VictorLiwentao | partially reviewed | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2265](https://github.com/CrocSwap/integer-mult-bounds/pull/2265) | DreamingOfClouds | partially reviewed | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1500-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2300-audit/DISPOSITIONS.json) |
| [#2266](https://github.com/CrocSwap/integer-mult-bounds/pull/2266) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2267](https://github.com/CrocSwap/integer-mult-bounds/pull/2267) | bitplane | partially reviewed | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) |
| [#2268](https://github.com/CrocSwap/integer-mult-bounds/pull/2268) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2269](https://github.com/CrocSwap/integer-mult-bounds/pull/2269) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) |
| [#2271](https://github.com/CrocSwap/integer-mult-bounds/pull/2271) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2272](https://github.com/CrocSwap/integer-mult-bounds/pull/2272) | navinor | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2273](https://github.com/CrocSwap/integer-mult-bounds/pull/2273) | navinor | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2274](https://github.com/CrocSwap/integer-mult-bounds/pull/2274) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2276](https://github.com/CrocSwap/integer-mult-bounds/pull/2276) | VictorLiwentao | partially reviewed | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2277](https://github.com/CrocSwap/integer-mult-bounds/pull/2277) | DreamingOfClouds | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2279](https://github.com/CrocSwap/integer-mult-bounds/pull/2279) | cbethin | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2280](https://github.com/CrocSwap/integer-mult-bounds/pull/2280) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2281](https://github.com/CrocSwap/integer-mult-bounds/pull/2281) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2300-audit/DISPOSITIONS.json) |
| [#2282](https://github.com/CrocSwap/integer-mult-bounds/pull/2282) | mason-hale | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2283](https://github.com/CrocSwap/integer-mult-bounds/pull/2283) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2284](https://github.com/CrocSwap/integer-mult-bounds/pull/2284) | Dugongue | partially reviewed | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) |
| [#2286](https://github.com/CrocSwap/integer-mult-bounds/pull/2286) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2287](https://github.com/CrocSwap/integer-mult-bounds/pull/2287) | jmbarrancoml | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2288](https://github.com/CrocSwap/integer-mult-bounds/pull/2288) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2300-audit/DISPOSITIONS.json) |
| [#2289](https://github.com/CrocSwap/integer-mult-bounds/pull/2289) | bitplane | partially reviewed | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) |
| [#2290](https://github.com/CrocSwap/integer-mult-bounds/pull/2290) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2293](https://github.com/CrocSwap/integer-mult-bounds/pull/2293) | navinor | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2294](https://github.com/CrocSwap/integer-mult-bounds/pull/2294) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2295](https://github.com/CrocSwap/integer-mult-bounds/pull/2295) | bitplane | partially reviewed | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) |
| [#2296](https://github.com/CrocSwap/integer-mult-bounds/pull/2296) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2297](https://github.com/CrocSwap/integer-mult-bounds/pull/2297) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2298](https://github.com/CrocSwap/integer-mult-bounds/pull/2298) | jmbarrancoml | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2301](https://github.com/CrocSwap/integer-mult-bounds/pull/2301) | navinor | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2302](https://github.com/CrocSwap/integer-mult-bounds/pull/2302) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2300-audit/DISPOSITIONS.json) |
| [#2303](https://github.com/CrocSwap/integer-mult-bounds/pull/2303) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2305](https://github.com/CrocSwap/integer-mult-bounds/pull/2305) | bitplane | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2306](https://github.com/CrocSwap/integer-mult-bounds/pull/2306) | CubeJerry | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2307](https://github.com/CrocSwap/integer-mult-bounds/pull/2307) | CubeJerry | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2308](https://github.com/CrocSwap/integer-mult-bounds/pull/2308) | 1337isnot1337 | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2309](https://github.com/CrocSwap/integer-mult-bounds/pull/2309) | Dugongue | partially reviewed | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2310](https://github.com/CrocSwap/integer-mult-bounds/pull/2310) | jmbarrancoml | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2311](https://github.com/CrocSwap/integer-mult-bounds/pull/2311) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2312](https://github.com/CrocSwap/integer-mult-bounds/pull/2312) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2300-audit/DISPOSITIONS.json) |
| [#2313](https://github.com/CrocSwap/integer-mult-bounds/pull/2313) | mason-hale | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2314](https://github.com/CrocSwap/integer-mult-bounds/pull/2314) | bitplane | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2315](https://github.com/CrocSwap/integer-mult-bounds/pull/2315) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2316](https://github.com/CrocSwap/integer-mult-bounds/pull/2316) | josecarlosgonzalezroque-design | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2317](https://github.com/CrocSwap/integer-mult-bounds/pull/2317) | navinor | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2318](https://github.com/CrocSwap/integer-mult-bounds/pull/2318) | navinor | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2320](https://github.com/CrocSwap/integer-mult-bounds/pull/2320) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2321](https://github.com/CrocSwap/integer-mult-bounds/pull/2321) | Hope7Happiness | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2322](https://github.com/CrocSwap/integer-mult-bounds/pull/2322) | Vlado-V | partially reviewed | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2323](https://github.com/CrocSwap/integer-mult-bounds/pull/2323) | bitplane | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2324](https://github.com/CrocSwap/integer-mult-bounds/pull/2324) | aakashthakkar | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2326](https://github.com/CrocSwap/integer-mult-bounds/pull/2326) | commdata2338 | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2327](https://github.com/CrocSwap/integer-mult-bounds/pull/2327) | AAAmirinu | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2328](https://github.com/CrocSwap/integer-mult-bounds/pull/2328) | commdata2338 | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2329](https://github.com/CrocSwap/integer-mult-bounds/pull/2329) | VictorLiwentao | partially reviewed | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2330](https://github.com/CrocSwap/integer-mult-bounds/pull/2330) | theon199 | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2332](https://github.com/CrocSwap/integer-mult-bounds/pull/2332) | commdata2338 | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2334](https://github.com/CrocSwap/integer-mult-bounds/pull/2334) | ROTl24 | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2335](https://github.com/CrocSwap/integer-mult-bounds/pull/2335) | navinor | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2336](https://github.com/CrocSwap/integer-mult-bounds/pull/2336) | antunishdPursuit | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2337](https://github.com/CrocSwap/integer-mult-bounds/pull/2337) | SHIN09-git | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2338](https://github.com/CrocSwap/integer-mult-bounds/pull/2338) | DreamingOfClouds | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2339](https://github.com/CrocSwap/integer-mult-bounds/pull/2339) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2340](https://github.com/CrocSwap/integer-mult-bounds/pull/2340) | navinor | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2341](https://github.com/CrocSwap/integer-mult-bounds/pull/2341) | bitplane | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2342](https://github.com/CrocSwap/integer-mult-bounds/pull/2342) | theon199 | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2343](https://github.com/CrocSwap/integer-mult-bounds/pull/2343) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2344](https://github.com/CrocSwap/integer-mult-bounds/pull/2344) | AAAmirinu | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2345](https://github.com/CrocSwap/integer-mult-bounds/pull/2345) | AAAmirinu | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2346](https://github.com/CrocSwap/integer-mult-bounds/pull/2346) | alephnan | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2348](https://github.com/CrocSwap/integer-mult-bounds/pull/2348) | VictorLiwentao | partially reviewed | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2349](https://github.com/CrocSwap/integer-mult-bounds/pull/2349) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 7](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2350](https://github.com/CrocSwap/integer-mult-bounds/pull/2350) | EdDiboi | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2351](https://github.com/CrocSwap/integer-mult-bounds/pull/2351) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2353](https://github.com/CrocSwap/integer-mult-bounds/pull/2353) | kumagi | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2354](https://github.com/CrocSwap/integer-mult-bounds/pull/2354) | kyzer1023 | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2355](https://github.com/CrocSwap/integer-mult-bounds/pull/2355) | bitplane | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2356](https://github.com/CrocSwap/integer-mult-bounds/pull/2356) | theon199 | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2357](https://github.com/CrocSwap/integer-mult-bounds/pull/2357) | VictorLiwentao | partially reviewed | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2358](https://github.com/CrocSwap/integer-mult-bounds/pull/2358) | AAAmirinu | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2359](https://github.com/CrocSwap/integer-mult-bounds/pull/2359) | AAAmirinu | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2360](https://github.com/CrocSwap/integer-mult-bounds/pull/2360) | jeremydiviney | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2361](https://github.com/CrocSwap/integer-mult-bounds/pull/2361) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) · [record 2](../../research/community-efficient1300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2363](https://github.com/CrocSwap/integer-mult-bounds/pull/2363) | mason-hale | partially reviewed | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2364](https://github.com/CrocSwap/integer-mult-bounds/pull/2364) | jmbarrancoml | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2365](https://github.com/CrocSwap/integer-mult-bounds/pull/2365) | jerrylin-23 | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2367](https://github.com/CrocSwap/integer-mult-bounds/pull/2367) | RossRichardson | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2368](https://github.com/CrocSwap/integer-mult-bounds/pull/2368) | starship-s | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2373](https://github.com/CrocSwap/integer-mult-bounds/pull/2373) | bitplane | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2374](https://github.com/CrocSwap/integer-mult-bounds/pull/2374) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2375](https://github.com/CrocSwap/integer-mult-bounds/pull/2375) | VictorLiwentao | partially reviewed | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2376](https://github.com/CrocSwap/integer-mult-bounds/pull/2376) | commdata2338 | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2377](https://github.com/CrocSwap/integer-mult-bounds/pull/2377) | yssite | incorporated | [record 1](../../research/community-efficient1300-audit/DISPOSITIONS.json) |
| [#2378](https://github.com/CrocSwap/integer-mult-bounds/pull/2378) | AAAmirinu | partially reviewed | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) |
| [#2379](https://github.com/CrocSwap/integer-mult-bounds/pull/2379) | navinor | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2381](https://github.com/CrocSwap/integer-mult-bounds/pull/2381) | jgilfoil | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2382](https://github.com/CrocSwap/integer-mult-bounds/pull/2382) | theon199 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2383](https://github.com/CrocSwap/integer-mult-bounds/pull/2383) | commdata2338 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2384](https://github.com/CrocSwap/integer-mult-bounds/pull/2384) | commdata2338 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2385](https://github.com/CrocSwap/integer-mult-bounds/pull/2385) | commdata2338 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2386](https://github.com/CrocSwap/integer-mult-bounds/pull/2386) | commdata2338 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2387](https://github.com/CrocSwap/integer-mult-bounds/pull/2387) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2388](https://github.com/CrocSwap/integer-mult-bounds/pull/2388) | commdata2338 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2389](https://github.com/CrocSwap/integer-mult-bounds/pull/2389) | commdata2338 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2390](https://github.com/CrocSwap/integer-mult-bounds/pull/2390) | commdata2338 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2391](https://github.com/CrocSwap/integer-mult-bounds/pull/2391) | navinor | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2392](https://github.com/CrocSwap/integer-mult-bounds/pull/2392) | commdata2338 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2393](https://github.com/CrocSwap/integer-mult-bounds/pull/2393) | commdata2338 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2394](https://github.com/CrocSwap/integer-mult-bounds/pull/2394) | commdata2338 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2395](https://github.com/CrocSwap/integer-mult-bounds/pull/2395) | commdata2338 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2396](https://github.com/CrocSwap/integer-mult-bounds/pull/2396) | navinor | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2397](https://github.com/CrocSwap/integer-mult-bounds/pull/2397) | commdata2338 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2398](https://github.com/CrocSwap/integer-mult-bounds/pull/2398) | commdata2338 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2399](https://github.com/CrocSwap/integer-mult-bounds/pull/2399) | commdata2338 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2400](https://github.com/CrocSwap/integer-mult-bounds/pull/2400) | commdata2338 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2402](https://github.com/CrocSwap/integer-mult-bounds/pull/2402) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2404](https://github.com/CrocSwap/integer-mult-bounds/pull/2404) | bitplane | partially reviewed | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) |
| [#2405](https://github.com/CrocSwap/integer-mult-bounds/pull/2405) | jmbarrancoml | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2406](https://github.com/CrocSwap/integer-mult-bounds/pull/2406) | jeremydiviney | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2407](https://github.com/CrocSwap/integer-mult-bounds/pull/2407) | RossRichardson | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2409](https://github.com/CrocSwap/integer-mult-bounds/pull/2409) | VictorLiwentao | partially reviewed | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2411](https://github.com/CrocSwap/integer-mult-bounds/pull/2411) | platypii | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) · [record 2](../../research/community-efficient1400-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2412](https://github.com/CrocSwap/integer-mult-bounds/pull/2412) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2413](https://github.com/CrocSwap/integer-mult-bounds/pull/2413) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2414](https://github.com/CrocSwap/integer-mult-bounds/pull/2414) | bitplane | partially reviewed | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) |
| [#2415](https://github.com/CrocSwap/integer-mult-bounds/pull/2415) | RossRichardson | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2416](https://github.com/CrocSwap/integer-mult-bounds/pull/2416) | ToikY | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2419](https://github.com/CrocSwap/integer-mult-bounds/pull/2419) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2420](https://github.com/CrocSwap/integer-mult-bounds/pull/2420) | RossRichardson | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2421](https://github.com/CrocSwap/integer-mult-bounds/pull/2421) | starship-s | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2422](https://github.com/CrocSwap/integer-mult-bounds/pull/2422) | bitplane | partially reviewed | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) |
| [#2423](https://github.com/CrocSwap/integer-mult-bounds/pull/2423) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2427](https://github.com/CrocSwap/integer-mult-bounds/pull/2427) | navinor | partially reviewed | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) |
| [#2428](https://github.com/CrocSwap/integer-mult-bounds/pull/2428) | navinor | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2429](https://github.com/CrocSwap/integer-mult-bounds/pull/2429) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2430](https://github.com/CrocSwap/integer-mult-bounds/pull/2430) | starship-s | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2431](https://github.com/CrocSwap/integer-mult-bounds/pull/2431) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2432](https://github.com/CrocSwap/integer-mult-bounds/pull/2432) | bitplane | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2433](https://github.com/CrocSwap/integer-mult-bounds/pull/2433) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2435](https://github.com/CrocSwap/integer-mult-bounds/pull/2435) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2437](https://github.com/CrocSwap/integer-mult-bounds/pull/2437) | RossRichardson | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2440](https://github.com/CrocSwap/integer-mult-bounds/pull/2440) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2441](https://github.com/CrocSwap/integer-mult-bounds/pull/2441) | bitplane | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2442](https://github.com/CrocSwap/integer-mult-bounds/pull/2442) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2443](https://github.com/CrocSwap/integer-mult-bounds/pull/2443) | starship-s | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2444](https://github.com/CrocSwap/integer-mult-bounds/pull/2444) | navinor | partially reviewed | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2445](https://github.com/CrocSwap/integer-mult-bounds/pull/2445) | RossRichardson | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2446](https://github.com/CrocSwap/integer-mult-bounds/pull/2446) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2447](https://github.com/CrocSwap/integer-mult-bounds/pull/2447) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2448](https://github.com/CrocSwap/integer-mult-bounds/pull/2448) | RossRichardson | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2449](https://github.com/CrocSwap/integer-mult-bounds/pull/2449) | jmbarrancoml | partially reviewed | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) |
| [#2450](https://github.com/CrocSwap/integer-mult-bounds/pull/2450) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2451](https://github.com/CrocSwap/integer-mult-bounds/pull/2451) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2452](https://github.com/CrocSwap/integer-mult-bounds/pull/2452) | ywz65 | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) · [record 2](../../research/community-efficient1400-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2453](https://github.com/CrocSwap/integer-mult-bounds/pull/2453) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2454](https://github.com/CrocSwap/integer-mult-bounds/pull/2454) | ywz65 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2455](https://github.com/CrocSwap/integer-mult-bounds/pull/2455) | ywz65 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2456](https://github.com/CrocSwap/integer-mult-bounds/pull/2456) | ywz65 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2457](https://github.com/CrocSwap/integer-mult-bounds/pull/2457) | ywz65 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2458](https://github.com/CrocSwap/integer-mult-bounds/pull/2458) | RossRichardson | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2459](https://github.com/CrocSwap/integer-mult-bounds/pull/2459) | ywz65 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2460](https://github.com/CrocSwap/integer-mult-bounds/pull/2460) | ywz65 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2461](https://github.com/CrocSwap/integer-mult-bounds/pull/2461) | ywz65 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2462](https://github.com/CrocSwap/integer-mult-bounds/pull/2462) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2464](https://github.com/CrocSwap/integer-mult-bounds/pull/2464) | navinor | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2465](https://github.com/CrocSwap/integer-mult-bounds/pull/2465) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2466](https://github.com/CrocSwap/integer-mult-bounds/pull/2466) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2467](https://github.com/CrocSwap/integer-mult-bounds/pull/2467) | ywz65 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2468](https://github.com/CrocSwap/integer-mult-bounds/pull/2468) | ywz65 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2469](https://github.com/CrocSwap/integer-mult-bounds/pull/2469) | ywz65 | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) · [record 2](../../research/community-efficient1400-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2470](https://github.com/CrocSwap/integer-mult-bounds/pull/2470) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2471](https://github.com/CrocSwap/integer-mult-bounds/pull/2471) | ywz65 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2472](https://github.com/CrocSwap/integer-mult-bounds/pull/2472) | RossRichardson | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2473](https://github.com/CrocSwap/integer-mult-bounds/pull/2473) | ywz65 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2474](https://github.com/CrocSwap/integer-mult-bounds/pull/2474) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2475](https://github.com/CrocSwap/integer-mult-bounds/pull/2475) | ywz65 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2476](https://github.com/CrocSwap/integer-mult-bounds/pull/2476) | ywz65 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2477](https://github.com/CrocSwap/integer-mult-bounds/pull/2477) | ywz65 | partially reviewed | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2478](https://github.com/CrocSwap/integer-mult-bounds/pull/2478) | mdumitrean | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2479](https://github.com/CrocSwap/integer-mult-bounds/pull/2479) | ywz65 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2480](https://github.com/CrocSwap/integer-mult-bounds/pull/2480) | RossRichardson | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2481](https://github.com/CrocSwap/integer-mult-bounds/pull/2481) | ywz65 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2482](https://github.com/CrocSwap/integer-mult-bounds/pull/2482) | mdumitrean | partially reviewed | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) |
| [#2483](https://github.com/CrocSwap/integer-mult-bounds/pull/2483) | ywz65 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2484](https://github.com/CrocSwap/integer-mult-bounds/pull/2484) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2485](https://github.com/CrocSwap/integer-mult-bounds/pull/2485) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2486](https://github.com/CrocSwap/integer-mult-bounds/pull/2486) | ywz65 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2487](https://github.com/CrocSwap/integer-mult-bounds/pull/2487) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2489](https://github.com/CrocSwap/integer-mult-bounds/pull/2489) | ywz65 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2490](https://github.com/CrocSwap/integer-mult-bounds/pull/2490) | ywz65 | incorporated | [record 1](../../research/community-efficient1400-audit/DISPOSITIONS.json) |
| [#2491](https://github.com/CrocSwap/integer-mult-bounds/pull/2491) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2492](https://github.com/CrocSwap/integer-mult-bounds/pull/2492) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2493](https://github.com/CrocSwap/integer-mult-bounds/pull/2493) | arhamgarg | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2494](https://github.com/CrocSwap/integer-mult-bounds/pull/2494) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2495](https://github.com/CrocSwap/integer-mult-bounds/pull/2495) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2496](https://github.com/CrocSwap/integer-mult-bounds/pull/2496) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2497](https://github.com/CrocSwap/integer-mult-bounds/pull/2497) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2498](https://github.com/CrocSwap/integer-mult-bounds/pull/2498) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2499](https://github.com/CrocSwap/integer-mult-bounds/pull/2499) | ywz65 | partially reviewed | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) |
| [#2500](https://github.com/CrocSwap/integer-mult-bounds/pull/2500) | RossRichardson | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2501](https://github.com/CrocSwap/integer-mult-bounds/pull/2501) | jmbarrancoml | partially reviewed | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) |
| [#2502](https://github.com/CrocSwap/integer-mult-bounds/pull/2502) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2503](https://github.com/CrocSwap/integer-mult-bounds/pull/2503) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2504](https://github.com/CrocSwap/integer-mult-bounds/pull/2504) | CubeJerry | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2505](https://github.com/CrocSwap/integer-mult-bounds/pull/2505) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2506](https://github.com/CrocSwap/integer-mult-bounds/pull/2506) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2507](https://github.com/CrocSwap/integer-mult-bounds/pull/2507) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2508](https://github.com/CrocSwap/integer-mult-bounds/pull/2508) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2509](https://github.com/CrocSwap/integer-mult-bounds/pull/2509) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2510](https://github.com/CrocSwap/integer-mult-bounds/pull/2510) | hikaru0706 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2511](https://github.com/CrocSwap/integer-mult-bounds/pull/2511) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2512](https://github.com/CrocSwap/integer-mult-bounds/pull/2512) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2513](https://github.com/CrocSwap/integer-mult-bounds/pull/2513) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2514](https://github.com/CrocSwap/integer-mult-bounds/pull/2514) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2515](https://github.com/CrocSwap/integer-mult-bounds/pull/2515) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2516](https://github.com/CrocSwap/integer-mult-bounds/pull/2516) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2517](https://github.com/CrocSwap/integer-mult-bounds/pull/2517) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2518](https://github.com/CrocSwap/integer-mult-bounds/pull/2518) | navinor | partially reviewed | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) |
| [#2519](https://github.com/CrocSwap/integer-mult-bounds/pull/2519) | RossRichardson | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2520](https://github.com/CrocSwap/integer-mult-bounds/pull/2520) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2521](https://github.com/CrocSwap/integer-mult-bounds/pull/2521) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2522](https://github.com/CrocSwap/integer-mult-bounds/pull/2522) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2523](https://github.com/CrocSwap/integer-mult-bounds/pull/2523) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2524](https://github.com/CrocSwap/integer-mult-bounds/pull/2524) | WilliamLawyer | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2525](https://github.com/CrocSwap/integer-mult-bounds/pull/2525) | ywz65 | partially reviewed | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) |
| [#2526](https://github.com/CrocSwap/integer-mult-bounds/pull/2526) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2527](https://github.com/CrocSwap/integer-mult-bounds/pull/2527) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2528](https://github.com/CrocSwap/integer-mult-bounds/pull/2528) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2529](https://github.com/CrocSwap/integer-mult-bounds/pull/2529) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2530](https://github.com/CrocSwap/integer-mult-bounds/pull/2530) | zxv | partially reviewed | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) |
| [#2531](https://github.com/CrocSwap/integer-mult-bounds/pull/2531) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2532](https://github.com/CrocSwap/integer-mult-bounds/pull/2532) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2533](https://github.com/CrocSwap/integer-mult-bounds/pull/2533) | ywz65 | partially reviewed | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) |
| [#2534](https://github.com/CrocSwap/integer-mult-bounds/pull/2534) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2535](https://github.com/CrocSwap/integer-mult-bounds/pull/2535) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2536](https://github.com/CrocSwap/integer-mult-bounds/pull/2536) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2537](https://github.com/CrocSwap/integer-mult-bounds/pull/2537) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2538](https://github.com/CrocSwap/integer-mult-bounds/pull/2538) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2539](https://github.com/CrocSwap/integer-mult-bounds/pull/2539) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2540](https://github.com/CrocSwap/integer-mult-bounds/pull/2540) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2541](https://github.com/CrocSwap/integer-mult-bounds/pull/2541) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2542](https://github.com/CrocSwap/integer-mult-bounds/pull/2542) | navinor | partially reviewed | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) |
| [#2543](https://github.com/CrocSwap/integer-mult-bounds/pull/2543) | RossRichardson | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2544](https://github.com/CrocSwap/integer-mult-bounds/pull/2544) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2545](https://github.com/CrocSwap/integer-mult-bounds/pull/2545) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2546](https://github.com/CrocSwap/integer-mult-bounds/pull/2546) | petalas | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2547](https://github.com/CrocSwap/integer-mult-bounds/pull/2547) | petalas | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2548](https://github.com/CrocSwap/integer-mult-bounds/pull/2548) | petalas | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2549](https://github.com/CrocSwap/integer-mult-bounds/pull/2549) | petalas | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2550](https://github.com/CrocSwap/integer-mult-bounds/pull/2550) | petalas | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2551](https://github.com/CrocSwap/integer-mult-bounds/pull/2551) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2552](https://github.com/CrocSwap/integer-mult-bounds/pull/2552) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2553](https://github.com/CrocSwap/integer-mult-bounds/pull/2553) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2554](https://github.com/CrocSwap/integer-mult-bounds/pull/2554) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2555](https://github.com/CrocSwap/integer-mult-bounds/pull/2555) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2556](https://github.com/CrocSwap/integer-mult-bounds/pull/2556) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2557](https://github.com/CrocSwap/integer-mult-bounds/pull/2557) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2558](https://github.com/CrocSwap/integer-mult-bounds/pull/2558) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2559](https://github.com/CrocSwap/integer-mult-bounds/pull/2559) | philippeVV | partially reviewed | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2560](https://github.com/CrocSwap/integer-mult-bounds/pull/2560) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2561](https://github.com/CrocSwap/integer-mult-bounds/pull/2561) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2562](https://github.com/CrocSwap/integer-mult-bounds/pull/2562) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2564](https://github.com/CrocSwap/integer-mult-bounds/pull/2564) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2565](https://github.com/CrocSwap/integer-mult-bounds/pull/2565) | petalas | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2566](https://github.com/CrocSwap/integer-mult-bounds/pull/2566) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2567](https://github.com/CrocSwap/integer-mult-bounds/pull/2567) | rtyu193-rgb | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2568](https://github.com/CrocSwap/integer-mult-bounds/pull/2568) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2569](https://github.com/CrocSwap/integer-mult-bounds/pull/2569) | jmbarrancoml | partially reviewed | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2100-audit/DISPOSITIONS.json) |
| [#2571](https://github.com/CrocSwap/integer-mult-bounds/pull/2571) | rohanarun | partially reviewed | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) |
| [#2572](https://github.com/CrocSwap/integer-mult-bounds/pull/2572) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2573](https://github.com/CrocSwap/integer-mult-bounds/pull/2573) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2574](https://github.com/CrocSwap/integer-mult-bounds/pull/2574) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2575](https://github.com/CrocSwap/integer-mult-bounds/pull/2575) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2577](https://github.com/CrocSwap/integer-mult-bounds/pull/2577) | starship-s | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2578](https://github.com/CrocSwap/integer-mult-bounds/pull/2578) | rtyu193-rgb | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2579](https://github.com/CrocSwap/integer-mult-bounds/pull/2579) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2580](https://github.com/CrocSwap/integer-mult-bounds/pull/2580) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2581](https://github.com/CrocSwap/integer-mult-bounds/pull/2581) | thakrarsagar | partially reviewed | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2582](https://github.com/CrocSwap/integer-mult-bounds/pull/2582) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2583](https://github.com/CrocSwap/integer-mult-bounds/pull/2583) | petalas | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2584](https://github.com/CrocSwap/integer-mult-bounds/pull/2584) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2585](https://github.com/CrocSwap/integer-mult-bounds/pull/2585) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2586](https://github.com/CrocSwap/integer-mult-bounds/pull/2586) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2587](https://github.com/CrocSwap/integer-mult-bounds/pull/2587) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2588](https://github.com/CrocSwap/integer-mult-bounds/pull/2588) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2589](https://github.com/CrocSwap/integer-mult-bounds/pull/2589) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2590](https://github.com/CrocSwap/integer-mult-bounds/pull/2590) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2591](https://github.com/CrocSwap/integer-mult-bounds/pull/2591) | ywz65 | incorporated | [record 1](../../research/community-efficient1500-audit/DISPOSITIONS.json) |
| [#2592](https://github.com/CrocSwap/integer-mult-bounds/pull/2592) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2593](https://github.com/CrocSwap/integer-mult-bounds/pull/2593) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2594](https://github.com/CrocSwap/integer-mult-bounds/pull/2594) | petalas | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2595](https://github.com/CrocSwap/integer-mult-bounds/pull/2595) | navinor | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2596](https://github.com/CrocSwap/integer-mult-bounds/pull/2596) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2597](https://github.com/CrocSwap/integer-mult-bounds/pull/2597) | ywz65 | partially reviewed | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2598](https://github.com/CrocSwap/integer-mult-bounds/pull/2598) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2599](https://github.com/CrocSwap/integer-mult-bounds/pull/2599) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2600](https://github.com/CrocSwap/integer-mult-bounds/pull/2600) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2601](https://github.com/CrocSwap/integer-mult-bounds/pull/2601) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2602](https://github.com/CrocSwap/integer-mult-bounds/pull/2602) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2603](https://github.com/CrocSwap/integer-mult-bounds/pull/2603) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2604](https://github.com/CrocSwap/integer-mult-bounds/pull/2604) | petalas | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2607](https://github.com/CrocSwap/integer-mult-bounds/pull/2607) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2613](https://github.com/CrocSwap/integer-mult-bounds/pull/2613) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2614](https://github.com/CrocSwap/integer-mult-bounds/pull/2614) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2618](https://github.com/CrocSwap/integer-mult-bounds/pull/2618) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2620](https://github.com/CrocSwap/integer-mult-bounds/pull/2620) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2621](https://github.com/CrocSwap/integer-mult-bounds/pull/2621) | themilkman216 | partially reviewed | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) |
| [#2622](https://github.com/CrocSwap/integer-mult-bounds/pull/2622) | ywz65 | partially reviewed | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2623](https://github.com/CrocSwap/integer-mult-bounds/pull/2623) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2624](https://github.com/CrocSwap/integer-mult-bounds/pull/2624) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2625](https://github.com/CrocSwap/integer-mult-bounds/pull/2625) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2626](https://github.com/CrocSwap/integer-mult-bounds/pull/2626) | petalas | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2627](https://github.com/CrocSwap/integer-mult-bounds/pull/2627) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2628](https://github.com/CrocSwap/integer-mult-bounds/pull/2628) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2629](https://github.com/CrocSwap/integer-mult-bounds/pull/2629) | ywz65 | partially reviewed | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2630](https://github.com/CrocSwap/integer-mult-bounds/pull/2630) | petalas | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2631](https://github.com/CrocSwap/integer-mult-bounds/pull/2631) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2632](https://github.com/CrocSwap/integer-mult-bounds/pull/2632) | commdata2338 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2633](https://github.com/CrocSwap/integer-mult-bounds/pull/2633) | commdata2338 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2634](https://github.com/CrocSwap/integer-mult-bounds/pull/2634) | navinor | partially reviewed | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2635](https://github.com/CrocSwap/integer-mult-bounds/pull/2635) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2636](https://github.com/CrocSwap/integer-mult-bounds/pull/2636) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2638](https://github.com/CrocSwap/integer-mult-bounds/pull/2638) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2639](https://github.com/CrocSwap/integer-mult-bounds/pull/2639) | DreamingOfClouds | partially reviewed | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2640](https://github.com/CrocSwap/integer-mult-bounds/pull/2640) | petalas | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2641](https://github.com/CrocSwap/integer-mult-bounds/pull/2641) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2643](https://github.com/CrocSwap/integer-mult-bounds/pull/2643) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2645](https://github.com/CrocSwap/integer-mult-bounds/pull/2645) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2651](https://github.com/CrocSwap/integer-mult-bounds/pull/2651) | commdata2338 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2652](https://github.com/CrocSwap/integer-mult-bounds/pull/2652) | commdata2338 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2653](https://github.com/CrocSwap/integer-mult-bounds/pull/2653) | commdata2338 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2654](https://github.com/CrocSwap/integer-mult-bounds/pull/2654) | commdata2338 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2655](https://github.com/CrocSwap/integer-mult-bounds/pull/2655) | commdata2338 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2656](https://github.com/CrocSwap/integer-mult-bounds/pull/2656) | commdata2338 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2658](https://github.com/CrocSwap/integer-mult-bounds/pull/2658) | commdata2338 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2659](https://github.com/CrocSwap/integer-mult-bounds/pull/2659) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2660](https://github.com/CrocSwap/integer-mult-bounds/pull/2660) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2661](https://github.com/CrocSwap/integer-mult-bounds/pull/2661) | commdata2338 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2662](https://github.com/CrocSwap/integer-mult-bounds/pull/2662) | commdata2338 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2663](https://github.com/CrocSwap/integer-mult-bounds/pull/2663) | petalas | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2664](https://github.com/CrocSwap/integer-mult-bounds/pull/2664) | commdata2338 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2665](https://github.com/CrocSwap/integer-mult-bounds/pull/2665) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2666](https://github.com/CrocSwap/integer-mult-bounds/pull/2666) | commdata2338 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2667](https://github.com/CrocSwap/integer-mult-bounds/pull/2667) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2668](https://github.com/CrocSwap/integer-mult-bounds/pull/2668) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2669](https://github.com/CrocSwap/integer-mult-bounds/pull/2669) | commdata2338 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2670](https://github.com/CrocSwap/integer-mult-bounds/pull/2670) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2671](https://github.com/CrocSwap/integer-mult-bounds/pull/2671) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2672](https://github.com/CrocSwap/integer-mult-bounds/pull/2672) | commdata2338 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2673](https://github.com/CrocSwap/integer-mult-bounds/pull/2673) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2674](https://github.com/CrocSwap/integer-mult-bounds/pull/2674) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2675](https://github.com/CrocSwap/integer-mult-bounds/pull/2675) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2676](https://github.com/CrocSwap/integer-mult-bounds/pull/2676) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2677](https://github.com/CrocSwap/integer-mult-bounds/pull/2677) | VictorLiwentao | partially reviewed | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2678](https://github.com/CrocSwap/integer-mult-bounds/pull/2678) | petalas | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2679](https://github.com/CrocSwap/integer-mult-bounds/pull/2679) | philippeVV | partially reviewed | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2680](https://github.com/CrocSwap/integer-mult-bounds/pull/2680) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2681](https://github.com/CrocSwap/integer-mult-bounds/pull/2681) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2682](https://github.com/CrocSwap/integer-mult-bounds/pull/2682) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2683](https://github.com/CrocSwap/integer-mult-bounds/pull/2683) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2685](https://github.com/CrocSwap/integer-mult-bounds/pull/2685) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2686](https://github.com/CrocSwap/integer-mult-bounds/pull/2686) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2687](https://github.com/CrocSwap/integer-mult-bounds/pull/2687) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2688](https://github.com/CrocSwap/integer-mult-bounds/pull/2688) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2689](https://github.com/CrocSwap/integer-mult-bounds/pull/2689) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2691](https://github.com/CrocSwap/integer-mult-bounds/pull/2691) | NicholasStone | partially reviewed | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2692](https://github.com/CrocSwap/integer-mult-bounds/pull/2692) | BigCactusLabs | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2693](https://github.com/CrocSwap/integer-mult-bounds/pull/2693) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2694](https://github.com/CrocSwap/integer-mult-bounds/pull/2694) | ywz65 | partially reviewed | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2695](https://github.com/CrocSwap/integer-mult-bounds/pull/2695) | hevlyo | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2696](https://github.com/CrocSwap/integer-mult-bounds/pull/2696) | mason-hale | partially reviewed | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2697](https://github.com/CrocSwap/integer-mult-bounds/pull/2697) | jmbarrancoml | partially reviewed | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2698](https://github.com/CrocSwap/integer-mult-bounds/pull/2698) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2699](https://github.com/CrocSwap/integer-mult-bounds/pull/2699) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2700](https://github.com/CrocSwap/integer-mult-bounds/pull/2700) | ywz65 | partially reviewed | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2701](https://github.com/CrocSwap/integer-mult-bounds/pull/2701) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2702](https://github.com/CrocSwap/integer-mult-bounds/pull/2702) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2704](https://github.com/CrocSwap/integer-mult-bounds/pull/2704) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2705](https://github.com/CrocSwap/integer-mult-bounds/pull/2705) | navinor | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2706](https://github.com/CrocSwap/integer-mult-bounds/pull/2706) | hevlyo | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2707](https://github.com/CrocSwap/integer-mult-bounds/pull/2707) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2708](https://github.com/CrocSwap/integer-mult-bounds/pull/2708) | petalas | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2709](https://github.com/CrocSwap/integer-mult-bounds/pull/2709) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2710](https://github.com/CrocSwap/integer-mult-bounds/pull/2710) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2711](https://github.com/CrocSwap/integer-mult-bounds/pull/2711) | ywz65 | partially reviewed | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2712](https://github.com/CrocSwap/integer-mult-bounds/pull/2712) | ywz65 | incorporated | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) |
| [#2713](https://github.com/CrocSwap/integer-mult-bounds/pull/2713) | petalas | partially reviewed | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) |
| [#2715](https://github.com/CrocSwap/integer-mult-bounds/pull/2715) | VictorLiwentao | partially reviewed | [record 1](../../research/community-efficient1600-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2716](https://github.com/CrocSwap/integer-mult-bounds/pull/2716) | ywz65 | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2717](https://github.com/CrocSwap/integer-mult-bounds/pull/2717) | navinor | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2718](https://github.com/CrocSwap/integer-mult-bounds/pull/2718) | ywz65 | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2719](https://github.com/CrocSwap/integer-mult-bounds/pull/2719) | ywz65 | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2720](https://github.com/CrocSwap/integer-mult-bounds/pull/2720) | petalas | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2722](https://github.com/CrocSwap/integer-mult-bounds/pull/2722) | petalas | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2723](https://github.com/CrocSwap/integer-mult-bounds/pull/2723) | ywz65 | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2724](https://github.com/CrocSwap/integer-mult-bounds/pull/2724) | DreamingOfClouds | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2725](https://github.com/CrocSwap/integer-mult-bounds/pull/2725) | flyingviper | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2726](https://github.com/CrocSwap/integer-mult-bounds/pull/2726) | ywz65 | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2728](https://github.com/CrocSwap/integer-mult-bounds/pull/2728) | ywz65 | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2729](https://github.com/CrocSwap/integer-mult-bounds/pull/2729) | petalas | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2730](https://github.com/CrocSwap/integer-mult-bounds/pull/2730) | ywz65 | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2731](https://github.com/CrocSwap/integer-mult-bounds/pull/2731) | starship-s | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2733](https://github.com/CrocSwap/integer-mult-bounds/pull/2733) | mdumitrean | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2734](https://github.com/CrocSwap/integer-mult-bounds/pull/2734) | petalas | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2735](https://github.com/CrocSwap/integer-mult-bounds/pull/2735) | ywz65 | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2736](https://github.com/CrocSwap/integer-mult-bounds/pull/2736) | petalas | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2737](https://github.com/CrocSwap/integer-mult-bounds/pull/2737) | navinor | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2738](https://github.com/CrocSwap/integer-mult-bounds/pull/2738) | DavidAriasC | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2740](https://github.com/CrocSwap/integer-mult-bounds/pull/2740) | cbethin | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2741](https://github.com/CrocSwap/integer-mult-bounds/pull/2741) | petalas | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2742](https://github.com/CrocSwap/integer-mult-bounds/pull/2742) | jmbarrancoml | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2743](https://github.com/CrocSwap/integer-mult-bounds/pull/2743) | petalas | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2744](https://github.com/CrocSwap/integer-mult-bounds/pull/2744) | flyingviper | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2745](https://github.com/CrocSwap/integer-mult-bounds/pull/2745) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2746](https://github.com/CrocSwap/integer-mult-bounds/pull/2746) | navinor | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2747](https://github.com/CrocSwap/integer-mult-bounds/pull/2747) | navinor | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2748](https://github.com/CrocSwap/integer-mult-bounds/pull/2748) | petalas | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2749](https://github.com/CrocSwap/integer-mult-bounds/pull/2749) | petalas | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2751](https://github.com/CrocSwap/integer-mult-bounds/pull/2751) | tekuuu | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2752](https://github.com/CrocSwap/integer-mult-bounds/pull/2752) | petalas | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2753](https://github.com/CrocSwap/integer-mult-bounds/pull/2753) | DavidAriasC | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2754](https://github.com/CrocSwap/integer-mult-bounds/pull/2754) | petalas | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2756](https://github.com/CrocSwap/integer-mult-bounds/pull/2756) | CubeJerry | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2757](https://github.com/CrocSwap/integer-mult-bounds/pull/2757) | flyingviper | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2758](https://github.com/CrocSwap/integer-mult-bounds/pull/2758) | petalas | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2759](https://github.com/CrocSwap/integer-mult-bounds/pull/2759) | petalas | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2760](https://github.com/CrocSwap/integer-mult-bounds/pull/2760) | petalas | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2761](https://github.com/CrocSwap/integer-mult-bounds/pull/2761) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2763](https://github.com/CrocSwap/integer-mult-bounds/pull/2763) | BigCactusLabs | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2764](https://github.com/CrocSwap/integer-mult-bounds/pull/2764) | VictorLiwentao | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2765](https://github.com/CrocSwap/integer-mult-bounds/pull/2765) | petalas | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2766](https://github.com/CrocSwap/integer-mult-bounds/pull/2766) | DavidAriasC | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2767](https://github.com/CrocSwap/integer-mult-bounds/pull/2767) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2768](https://github.com/CrocSwap/integer-mult-bounds/pull/2768) | tekuuu | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2769](https://github.com/CrocSwap/integer-mult-bounds/pull/2769) | jmbarrancoml | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2770](https://github.com/CrocSwap/integer-mult-bounds/pull/2770) | petalas | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2771](https://github.com/CrocSwap/integer-mult-bounds/pull/2771) | petalas | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2772](https://github.com/CrocSwap/integer-mult-bounds/pull/2772) | petalas | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2773](https://github.com/CrocSwap/integer-mult-bounds/pull/2773) | navinor | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2774](https://github.com/CrocSwap/integer-mult-bounds/pull/2774) | navinor | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2775](https://github.com/CrocSwap/integer-mult-bounds/pull/2775) | Dugongue | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) |
| [#2776](https://github.com/CrocSwap/integer-mult-bounds/pull/2776) | DavidAriasC | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2778](https://github.com/CrocSwap/integer-mult-bounds/pull/2778) | petalas | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2779](https://github.com/CrocSwap/integer-mult-bounds/pull/2779) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2780](https://github.com/CrocSwap/integer-mult-bounds/pull/2780) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) · [record 2](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2200-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2781](https://github.com/CrocSwap/integer-mult-bounds/pull/2781) | petalas | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2782](https://github.com/CrocSwap/integer-mult-bounds/pull/2782) | tekuuu | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2784](https://github.com/CrocSwap/integer-mult-bounds/pull/2784) | DreamingOfClouds | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2786](https://github.com/CrocSwap/integer-mult-bounds/pull/2786) | petalas | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2788](https://github.com/CrocSwap/integer-mult-bounds/pull/2788) | jeremydiviney | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2790](https://github.com/CrocSwap/integer-mult-bounds/pull/2790) | Dugongue | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2792](https://github.com/CrocSwap/integer-mult-bounds/pull/2792) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2793](https://github.com/CrocSwap/integer-mult-bounds/pull/2793) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2794](https://github.com/CrocSwap/integer-mult-bounds/pull/2794) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2795](https://github.com/CrocSwap/integer-mult-bounds/pull/2795) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2796](https://github.com/CrocSwap/integer-mult-bounds/pull/2796) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2797](https://github.com/CrocSwap/integer-mult-bounds/pull/2797) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2798](https://github.com/CrocSwap/integer-mult-bounds/pull/2798) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2799](https://github.com/CrocSwap/integer-mult-bounds/pull/2799) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2801](https://github.com/CrocSwap/integer-mult-bounds/pull/2801) | petalas | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2802](https://github.com/CrocSwap/integer-mult-bounds/pull/2802) | mdumitrean | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2803](https://github.com/CrocSwap/integer-mult-bounds/pull/2803) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2804](https://github.com/CrocSwap/integer-mult-bounds/pull/2804) | thakrarsagar | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2805](https://github.com/CrocSwap/integer-mult-bounds/pull/2805) | tekuuu | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2806](https://github.com/CrocSwap/integer-mult-bounds/pull/2806) | DreamingOfClouds | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2807](https://github.com/CrocSwap/integer-mult-bounds/pull/2807) | petalas | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2808](https://github.com/CrocSwap/integer-mult-bounds/pull/2808) | petalas | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2809](https://github.com/CrocSwap/integer-mult-bounds/pull/2809) | jmbarrancoml | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2810](https://github.com/CrocSwap/integer-mult-bounds/pull/2810) | RossRichardson | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2811](https://github.com/CrocSwap/integer-mult-bounds/pull/2811) | petalas | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2812](https://github.com/CrocSwap/integer-mult-bounds/pull/2812) | sandersdavid90-droid | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2813](https://github.com/CrocSwap/integer-mult-bounds/pull/2813) | petalas | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2814](https://github.com/CrocSwap/integer-mult-bounds/pull/2814) | tekuuu | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2815](https://github.com/CrocSwap/integer-mult-bounds/pull/2815) | petalas | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2816](https://github.com/CrocSwap/integer-mult-bounds/pull/2816) | DreamingOfClouds | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2817](https://github.com/CrocSwap/integer-mult-bounds/pull/2817) | VictorLiwentao | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2818](https://github.com/CrocSwap/integer-mult-bounds/pull/2818) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2819](https://github.com/CrocSwap/integer-mult-bounds/pull/2819) | DreamingOfClouds | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2820](https://github.com/CrocSwap/integer-mult-bounds/pull/2820) | Chrisbryan17 | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2821](https://github.com/CrocSwap/integer-mult-bounds/pull/2821) | RossRichardson | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2822](https://github.com/CrocSwap/integer-mult-bounds/pull/2822) | sandersdavid90-droid | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2823](https://github.com/CrocSwap/integer-mult-bounds/pull/2823) | mdumitrean | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2824](https://github.com/CrocSwap/integer-mult-bounds/pull/2824) | Dugongue | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2825](https://github.com/CrocSwap/integer-mult-bounds/pull/2825) | RossRichardson | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2826](https://github.com/CrocSwap/integer-mult-bounds/pull/2826) | DreamingOfClouds | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2827](https://github.com/CrocSwap/integer-mult-bounds/pull/2827) | Dugongue | partially reviewed | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2828](https://github.com/CrocSwap/integer-mult-bounds/pull/2828) | steph4n-gh | incorporated | [record 1](../../research/community-efficient1700-audit/DISPOSITIONS.json) |
| [#2829](https://github.com/CrocSwap/integer-mult-bounds/pull/2829) | cbethin | incorporated | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2830](https://github.com/CrocSwap/integer-mult-bounds/pull/2830) | DreamingOfClouds | incorporated | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2831](https://github.com/CrocSwap/integer-mult-bounds/pull/2831) | RossRichardson | incorporated | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2832](https://github.com/CrocSwap/integer-mult-bounds/pull/2832) | DreamingOfClouds | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) · [record 2](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2833](https://github.com/CrocSwap/integer-mult-bounds/pull/2833) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) |
| [#2834](https://github.com/CrocSwap/integer-mult-bounds/pull/2834) | steph4n-gh | incorporated | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2835](https://github.com/CrocSwap/integer-mult-bounds/pull/2835) | RossRichardson | incorporated | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2836](https://github.com/CrocSwap/integer-mult-bounds/pull/2836) | VictorLiwentao | partially reviewed | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2837](https://github.com/CrocSwap/integer-mult-bounds/pull/2837) | josecarlosgonzalezroque-design | incorporated | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2839](https://github.com/CrocSwap/integer-mult-bounds/pull/2839) | Dugongue | partially reviewed | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2840](https://github.com/CrocSwap/integer-mult-bounds/pull/2840) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2841](https://github.com/CrocSwap/integer-mult-bounds/pull/2841) | Lyy-iiis | incorporated | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2843](https://github.com/CrocSwap/integer-mult-bounds/pull/2843) | mdumitrean | partially reviewed | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2844](https://github.com/CrocSwap/integer-mult-bounds/pull/2844) | Chrisbryan17 | incorporated | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2845](https://github.com/CrocSwap/integer-mult-bounds/pull/2845) | RossRichardson | incorporated | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2846](https://github.com/CrocSwap/integer-mult-bounds/pull/2846) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2847](https://github.com/CrocSwap/integer-mult-bounds/pull/2847) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2848](https://github.com/CrocSwap/integer-mult-bounds/pull/2848) | Lyy-iiis | partially reviewed | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2849](https://github.com/CrocSwap/integer-mult-bounds/pull/2849) | Dugongue | partially reviewed | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2850](https://github.com/CrocSwap/integer-mult-bounds/pull/2850) | bitplane | incorporated | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2851](https://github.com/CrocSwap/integer-mult-bounds/pull/2851) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2852](https://github.com/CrocSwap/integer-mult-bounds/pull/2852) | dataisfire | partially reviewed | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 5](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 6](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2853](https://github.com/CrocSwap/integer-mult-bounds/pull/2853) | philippeVV | partially reviewed | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) |
| [#2854](https://github.com/CrocSwap/integer-mult-bounds/pull/2854) | DreamingOfClouds | incorporated | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2855](https://github.com/CrocSwap/integer-mult-bounds/pull/2855) | Dugongue | partially reviewed | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2856](https://github.com/CrocSwap/integer-mult-bounds/pull/2856) | mdumitrean | partially reviewed | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2300-audit/DISPOSITIONS.json) |
| [#2857](https://github.com/CrocSwap/integer-mult-bounds/pull/2857) | Lyy-iiis | partially reviewed | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2858](https://github.com/CrocSwap/integer-mult-bounds/pull/2858) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2859](https://github.com/CrocSwap/integer-mult-bounds/pull/2859) | antunishdPursuit | incorporated | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2860](https://github.com/CrocSwap/integer-mult-bounds/pull/2860) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2861](https://github.com/CrocSwap/integer-mult-bounds/pull/2861) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2862](https://github.com/CrocSwap/integer-mult-bounds/pull/2862) | DreamingOfClouds | partially reviewed | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2863](https://github.com/CrocSwap/integer-mult-bounds/pull/2863) | Dugongue | partially reviewed | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2864](https://github.com/CrocSwap/integer-mult-bounds/pull/2864) | DreamingOfClouds | partially reviewed | [record 1](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2865](https://github.com/CrocSwap/integer-mult-bounds/pull/2865) | thakrarsagar | partially reviewed | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2866](https://github.com/CrocSwap/integer-mult-bounds/pull/2866) | digitalis-p | partially reviewed | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2867](https://github.com/CrocSwap/integer-mult-bounds/pull/2867) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2868](https://github.com/CrocSwap/integer-mult-bounds/pull/2868) | VictorLiwentao | incorporated | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2869](https://github.com/CrocSwap/integer-mult-bounds/pull/2869) | navinor | incorporated | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2870](https://github.com/CrocSwap/integer-mult-bounds/pull/2870) | navinor | incorporated | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2871](https://github.com/CrocSwap/integer-mult-bounds/pull/2871) | Dugongue | partially reviewed | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2872](https://github.com/CrocSwap/integer-mult-bounds/pull/2872) | tekuuu | incorporated | [record 1](../../research/community-efficient1800-audit/DISPOSITIONS.json) |
| [#2873](https://github.com/CrocSwap/integer-mult-bounds/pull/2873) | DreamingOfClouds | partially reviewed | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2874](https://github.com/CrocSwap/integer-mult-bounds/pull/2874) | RossRichardson | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2875](https://github.com/CrocSwap/integer-mult-bounds/pull/2875) | digitalis-p | partially reviewed | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2876](https://github.com/CrocSwap/integer-mult-bounds/pull/2876) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2877](https://github.com/CrocSwap/integer-mult-bounds/pull/2877) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2878](https://github.com/CrocSwap/integer-mult-bounds/pull/2878) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2879](https://github.com/CrocSwap/integer-mult-bounds/pull/2879) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2880](https://github.com/CrocSwap/integer-mult-bounds/pull/2880) | DLamdata | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2881](https://github.com/CrocSwap/integer-mult-bounds/pull/2881) | RossRichardson | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2882](https://github.com/CrocSwap/integer-mult-bounds/pull/2882) | kumagi | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2883](https://github.com/CrocSwap/integer-mult-bounds/pull/2883) | VictorLiwentao | partially reviewed | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2885](https://github.com/CrocSwap/integer-mult-bounds/pull/2885) | kumagi | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2888](https://github.com/CrocSwap/integer-mult-bounds/pull/2888) | jwr404 | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2889](https://github.com/CrocSwap/integer-mult-bounds/pull/2889) | kumagi | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2890](https://github.com/CrocSwap/integer-mult-bounds/pull/2890) | navinor | partially reviewed | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2891](https://github.com/CrocSwap/integer-mult-bounds/pull/2891) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2892](https://github.com/CrocSwap/integer-mult-bounds/pull/2892) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2893](https://github.com/CrocSwap/integer-mult-bounds/pull/2893) | Arham-Tahir64 | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2894](https://github.com/CrocSwap/integer-mult-bounds/pull/2894) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2895](https://github.com/CrocSwap/integer-mult-bounds/pull/2895) | thakrarsagar | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2896](https://github.com/CrocSwap/integer-mult-bounds/pull/2896) | petalas | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2897](https://github.com/CrocSwap/integer-mult-bounds/pull/2897) | petalas | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2899](https://github.com/CrocSwap/integer-mult-bounds/pull/2899) | jmbarrancoml | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2900](https://github.com/CrocSwap/integer-mult-bounds/pull/2900) | petalas | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2901](https://github.com/CrocSwap/integer-mult-bounds/pull/2901) | navinor | partially reviewed | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2902](https://github.com/CrocSwap/integer-mult-bounds/pull/2902) | petalas | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2903](https://github.com/CrocSwap/integer-mult-bounds/pull/2903) | petalas | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2904](https://github.com/CrocSwap/integer-mult-bounds/pull/2904) | digitalis-p | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2905](https://github.com/CrocSwap/integer-mult-bounds/pull/2905) | petalas | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2906](https://github.com/CrocSwap/integer-mult-bounds/pull/2906) | petalas | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2907](https://github.com/CrocSwap/integer-mult-bounds/pull/2907) | DLamdata | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2908](https://github.com/CrocSwap/integer-mult-bounds/pull/2908) | jeremydiviney | partially reviewed | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2909](https://github.com/CrocSwap/integer-mult-bounds/pull/2909) | petalas | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2910](https://github.com/CrocSwap/integer-mult-bounds/pull/2910) | petalas | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2911](https://github.com/CrocSwap/integer-mult-bounds/pull/2911) | navinor | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2912](https://github.com/CrocSwap/integer-mult-bounds/pull/2912) | petalas | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2913](https://github.com/CrocSwap/integer-mult-bounds/pull/2913) | petalas | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2914](https://github.com/CrocSwap/integer-mult-bounds/pull/2914) | navinor | partially reviewed | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2915](https://github.com/CrocSwap/integer-mult-bounds/pull/2915) | jmbarrancoml | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2916](https://github.com/CrocSwap/integer-mult-bounds/pull/2916) | petalas | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2917](https://github.com/CrocSwap/integer-mult-bounds/pull/2917) | mason-hale | partially reviewed | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2918](https://github.com/CrocSwap/integer-mult-bounds/pull/2918) | RossRichardson | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2920](https://github.com/CrocSwap/integer-mult-bounds/pull/2920) | petalas | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2921](https://github.com/CrocSwap/integer-mult-bounds/pull/2921) | petalas | incorporated | [record 1](../../research/community-efficient1900-audit/DISPOSITIONS.json) |
| [#2922](https://github.com/CrocSwap/integer-mult-bounds/pull/2922) | petalas | partially reviewed | [record 1](../../research/community-efficient2200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2500-audit/DISPOSITIONS.json) |
| [#2923](https://github.com/CrocSwap/integer-mult-bounds/pull/2923) | petalas | partially reviewed | [record 1](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2924](https://github.com/CrocSwap/integer-mult-bounds/pull/2924) | Sudarsh3301 | partially reviewed | [record 1](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2925](https://github.com/CrocSwap/integer-mult-bounds/pull/2925) | petalas | partially reviewed | [record 1](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2927](https://github.com/CrocSwap/integer-mult-bounds/pull/2927) | petalas | partially reviewed | [record 1](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2928](https://github.com/CrocSwap/integer-mult-bounds/pull/2928) | petalas | incorporated | [record 1](../../research/community-efficient2200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2930](https://github.com/CrocSwap/integer-mult-bounds/pull/2930) | mdumitrean | partially reviewed | [record 1](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2931](https://github.com/CrocSwap/integer-mult-bounds/pull/2931) | hevlyo | partially reviewed | [record 1](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2932](https://github.com/CrocSwap/integer-mult-bounds/pull/2932) | ToikY | partially reviewed | [record 1](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2933](https://github.com/CrocSwap/integer-mult-bounds/pull/2933) | navinor | partially reviewed | [record 1](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2934](https://github.com/CrocSwap/integer-mult-bounds/pull/2934) | petalas | partially reviewed | [record 1](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2935](https://github.com/CrocSwap/integer-mult-bounds/pull/2935) | petalas | partially reviewed | [record 1](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2936](https://github.com/CrocSwap/integer-mult-bounds/pull/2936) | navinor | partially reviewed | [record 1](../../research/community-efficient2200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2938](https://github.com/CrocSwap/integer-mult-bounds/pull/2938) | petalas | partially reviewed | [record 1](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2939](https://github.com/CrocSwap/integer-mult-bounds/pull/2939) | petalas | partially reviewed | [record 1](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2940](https://github.com/CrocSwap/integer-mult-bounds/pull/2940) | petalas | partially reviewed | [record 1](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2941](https://github.com/CrocSwap/integer-mult-bounds/pull/2941) | petalas | partially reviewed | [record 1](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2942](https://github.com/CrocSwap/integer-mult-bounds/pull/2942) | mdumitrean | partially reviewed | [record 1](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2943](https://github.com/CrocSwap/integer-mult-bounds/pull/2943) | ToikY | partially reviewed | [record 1](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2944](https://github.com/CrocSwap/integer-mult-bounds/pull/2944) | petalas | partially reviewed | [record 1](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2945](https://github.com/CrocSwap/integer-mult-bounds/pull/2945) | petalas | incorporated | [record 1](../../research/community-efficient2200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2400-audit/DISPOSITIONS.json) · [record 3](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 4](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2947](https://github.com/CrocSwap/integer-mult-bounds/pull/2947) | petalas | partially reviewed | [record 1](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2948](https://github.com/CrocSwap/integer-mult-bounds/pull/2948) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2200-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2300-audit/DISPOSITIONS.json) |
| [#2949](https://github.com/CrocSwap/integer-mult-bounds/pull/2949) | petalas | partially reviewed | [record 1](../../research/community-efficient2200-audit/DISPOSITIONS.json) |
| [#2950](https://github.com/CrocSwap/integer-mult-bounds/pull/2950) | CubeJerry | partially reviewed | [record 1](../../research/community-efficient2300-audit/DISPOSITIONS.json) |
| [#2951](https://github.com/CrocSwap/integer-mult-bounds/pull/2951) | petalas | partially reviewed | [record 1](../../research/community-efficient2400-audit/DISPOSITIONS.json) |
| [#2952](https://github.com/CrocSwap/integer-mult-bounds/pull/2952) | tekuuu | partially reviewed | [record 1](../../research/community-efficient2400-audit/DISPOSITIONS.json) |
| [#2953](https://github.com/CrocSwap/integer-mult-bounds/pull/2953) | petalas | partially reviewed | [record 1](../../research/community-efficient2400-audit/DISPOSITIONS.json) |
| [#2956](https://github.com/CrocSwap/integer-mult-bounds/pull/2956) | Sudarsh3301 | partially reviewed | [record 1](../../research/community-efficient2500-audit/DISPOSITIONS.json) |
| [#2957](https://github.com/CrocSwap/integer-mult-bounds/pull/2957) | jeremykothe2 | partially reviewed | [record 1](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2958](https://github.com/CrocSwap/integer-mult-bounds/pull/2958) | petalas | incorporated | [record 1](../../research/community-efficient2500-audit/DISPOSITIONS.json) · [record 2](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2959](https://github.com/CrocSwap/integer-mult-bounds/pull/2959) | petalas | partially reviewed | [record 1](../../research/community-efficient2500-audit/DISPOSITIONS.json) |
| [#2960](https://github.com/CrocSwap/integer-mult-bounds/pull/2960) | RossRichardson | partially reviewed | [record 1](../../research/community-efficient2500-audit/DISPOSITIONS.json) |
| [#2961](https://github.com/CrocSwap/integer-mult-bounds/pull/2961) | navinor | partially reviewed | [record 1](../../research/community-efficient2600-audit/DISPOSITIONS.json) |
| [#2962](https://github.com/CrocSwap/integer-mult-bounds/pull/2962) | DreamingOfClouds | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2963](https://github.com/CrocSwap/integer-mult-bounds/pull/2963) | navinor | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2964](https://github.com/CrocSwap/integer-mult-bounds/pull/2964) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2965](https://github.com/CrocSwap/integer-mult-bounds/pull/2965) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2966](https://github.com/CrocSwap/integer-mult-bounds/pull/2966) | jeremykothe2 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2968](https://github.com/CrocSwap/integer-mult-bounds/pull/2968) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2969](https://github.com/CrocSwap/integer-mult-bounds/pull/2969) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2970](https://github.com/CrocSwap/integer-mult-bounds/pull/2970) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2971](https://github.com/CrocSwap/integer-mult-bounds/pull/2971) | CubeJerry | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2972](https://github.com/CrocSwap/integer-mult-bounds/pull/2972) | kumagi | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2973](https://github.com/CrocSwap/integer-mult-bounds/pull/2973) | NicholasStone | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2974](https://github.com/CrocSwap/integer-mult-bounds/pull/2974) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2975](https://github.com/CrocSwap/integer-mult-bounds/pull/2975) | tekuuu | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2977](https://github.com/CrocSwap/integer-mult-bounds/pull/2977) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2978](https://github.com/CrocSwap/integer-mult-bounds/pull/2978) | navinor | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2979](https://github.com/CrocSwap/integer-mult-bounds/pull/2979) | mdumitrean | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2980](https://github.com/CrocSwap/integer-mult-bounds/pull/2980) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2981](https://github.com/CrocSwap/integer-mult-bounds/pull/2981) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2982](https://github.com/CrocSwap/integer-mult-bounds/pull/2982) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2984](https://github.com/CrocSwap/integer-mult-bounds/pull/2984) | tekuuu | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2985](https://github.com/CrocSwap/integer-mult-bounds/pull/2985) | DreamingOfClouds | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2986](https://github.com/CrocSwap/integer-mult-bounds/pull/2986) | petalas | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2987](https://github.com/CrocSwap/integer-mult-bounds/pull/2987) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2989](https://github.com/CrocSwap/integer-mult-bounds/pull/2989) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2990](https://github.com/CrocSwap/integer-mult-bounds/pull/2990) | petalas | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2991](https://github.com/CrocSwap/integer-mult-bounds/pull/2991) | Arham-Tahir64 | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2992](https://github.com/CrocSwap/integer-mult-bounds/pull/2992) | Arham-Tahir64 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2993](https://github.com/CrocSwap/integer-mult-bounds/pull/2993) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2994](https://github.com/CrocSwap/integer-mult-bounds/pull/2994) | Arham-Tahir64 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2995](https://github.com/CrocSwap/integer-mult-bounds/pull/2995) | Arham-Tahir64 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2996](https://github.com/CrocSwap/integer-mult-bounds/pull/2996) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2997](https://github.com/CrocSwap/integer-mult-bounds/pull/2997) | Arham-Tahir64 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2998](https://github.com/CrocSwap/integer-mult-bounds/pull/2998) | Arham-Tahir64 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#2999](https://github.com/CrocSwap/integer-mult-bounds/pull/2999) | Arham-Tahir64 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3000](https://github.com/CrocSwap/integer-mult-bounds/pull/3000) | tekuuu | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3002](https://github.com/CrocSwap/integer-mult-bounds/pull/3002) | petalas | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3003](https://github.com/CrocSwap/integer-mult-bounds/pull/3003) | Arham-Tahir64 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3004](https://github.com/CrocSwap/integer-mult-bounds/pull/3004) | kumagi | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3005](https://github.com/CrocSwap/integer-mult-bounds/pull/3005) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3006](https://github.com/CrocSwap/integer-mult-bounds/pull/3006) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3007](https://github.com/CrocSwap/integer-mult-bounds/pull/3007) | petalas | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3008](https://github.com/CrocSwap/integer-mult-bounds/pull/3008) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3009](https://github.com/CrocSwap/integer-mult-bounds/pull/3009) | kumagi | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3010](https://github.com/CrocSwap/integer-mult-bounds/pull/3010) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3011](https://github.com/CrocSwap/integer-mult-bounds/pull/3011) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3012](https://github.com/CrocSwap/integer-mult-bounds/pull/3012) | navinor | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3013](https://github.com/CrocSwap/integer-mult-bounds/pull/3013) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3014](https://github.com/CrocSwap/integer-mult-bounds/pull/3014) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3015](https://github.com/CrocSwap/integer-mult-bounds/pull/3015) | jeremykothe2 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3016](https://github.com/CrocSwap/integer-mult-bounds/pull/3016) | petalas | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3017](https://github.com/CrocSwap/integer-mult-bounds/pull/3017) | tekuuu | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3018](https://github.com/CrocSwap/integer-mult-bounds/pull/3018) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3019](https://github.com/CrocSwap/integer-mult-bounds/pull/3019) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3020](https://github.com/CrocSwap/integer-mult-bounds/pull/3020) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3021](https://github.com/CrocSwap/integer-mult-bounds/pull/3021) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3022](https://github.com/CrocSwap/integer-mult-bounds/pull/3022) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3023](https://github.com/CrocSwap/integer-mult-bounds/pull/3023) | navinor | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3024](https://github.com/CrocSwap/integer-mult-bounds/pull/3024) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3025](https://github.com/CrocSwap/integer-mult-bounds/pull/3025) | tekuuu | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3026](https://github.com/CrocSwap/integer-mult-bounds/pull/3026) | flyingviper | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3027](https://github.com/CrocSwap/integer-mult-bounds/pull/3027) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3028](https://github.com/CrocSwap/integer-mult-bounds/pull/3028) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3029](https://github.com/CrocSwap/integer-mult-bounds/pull/3029) | DreamingOfClouds | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3030](https://github.com/CrocSwap/integer-mult-bounds/pull/3030) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3031](https://github.com/CrocSwap/integer-mult-bounds/pull/3031) | navinor | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3032](https://github.com/CrocSwap/integer-mult-bounds/pull/3032) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3033](https://github.com/CrocSwap/integer-mult-bounds/pull/3033) | tekuuu | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3034](https://github.com/CrocSwap/integer-mult-bounds/pull/3034) | navinor | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3035](https://github.com/CrocSwap/integer-mult-bounds/pull/3035) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3036](https://github.com/CrocSwap/integer-mult-bounds/pull/3036) | Arham-Tahir64 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3037](https://github.com/CrocSwap/integer-mult-bounds/pull/3037) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3038](https://github.com/CrocSwap/integer-mult-bounds/pull/3038) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3039](https://github.com/CrocSwap/integer-mult-bounds/pull/3039) | navinor | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3040](https://github.com/CrocSwap/integer-mult-bounds/pull/3040) | DreamingOfClouds | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3041](https://github.com/CrocSwap/integer-mult-bounds/pull/3041) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3042](https://github.com/CrocSwap/integer-mult-bounds/pull/3042) | dcharb78 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3043](https://github.com/CrocSwap/integer-mult-bounds/pull/3043) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3044](https://github.com/CrocSwap/integer-mult-bounds/pull/3044) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3045](https://github.com/CrocSwap/integer-mult-bounds/pull/3045) | DreamingOfClouds | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3046](https://github.com/CrocSwap/integer-mult-bounds/pull/3046) | Arham-Tahir64 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3047](https://github.com/CrocSwap/integer-mult-bounds/pull/3047) | navinor | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3048](https://github.com/CrocSwap/integer-mult-bounds/pull/3048) | flyingviper | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3049](https://github.com/CrocSwap/integer-mult-bounds/pull/3049) | DreamingOfClouds | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3050](https://github.com/CrocSwap/integer-mult-bounds/pull/3050) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3051](https://github.com/CrocSwap/integer-mult-bounds/pull/3051) | jeremydiviney | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3052](https://github.com/CrocSwap/integer-mult-bounds/pull/3052) | navinor | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3053](https://github.com/CrocSwap/integer-mult-bounds/pull/3053) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3054](https://github.com/CrocSwap/integer-mult-bounds/pull/3054) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3055](https://github.com/CrocSwap/integer-mult-bounds/pull/3055) | jmbarrancoml | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3056](https://github.com/CrocSwap/integer-mult-bounds/pull/3056) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3057](https://github.com/CrocSwap/integer-mult-bounds/pull/3057) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3058](https://github.com/CrocSwap/integer-mult-bounds/pull/3058) | conorholds | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3059](https://github.com/CrocSwap/integer-mult-bounds/pull/3059) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3060](https://github.com/CrocSwap/integer-mult-bounds/pull/3060) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3063](https://github.com/CrocSwap/integer-mult-bounds/pull/3063) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3064](https://github.com/CrocSwap/integer-mult-bounds/pull/3064) | dataisfire | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3065](https://github.com/CrocSwap/integer-mult-bounds/pull/3065) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3066](https://github.com/CrocSwap/integer-mult-bounds/pull/3066) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3067](https://github.com/CrocSwap/integer-mult-bounds/pull/3067) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3068](https://github.com/CrocSwap/integer-mult-bounds/pull/3068) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3069](https://github.com/CrocSwap/integer-mult-bounds/pull/3069) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3070](https://github.com/CrocSwap/integer-mult-bounds/pull/3070) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3071](https://github.com/CrocSwap/integer-mult-bounds/pull/3071) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3072](https://github.com/CrocSwap/integer-mult-bounds/pull/3072) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3073](https://github.com/CrocSwap/integer-mult-bounds/pull/3073) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3074](https://github.com/CrocSwap/integer-mult-bounds/pull/3074) | DreamingOfClouds | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3075](https://github.com/CrocSwap/integer-mult-bounds/pull/3075) | navinor | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3076](https://github.com/CrocSwap/integer-mult-bounds/pull/3076) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3077](https://github.com/CrocSwap/integer-mult-bounds/pull/3077) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3078](https://github.com/CrocSwap/integer-mult-bounds/pull/3078) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3079](https://github.com/CrocSwap/integer-mult-bounds/pull/3079) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3080](https://github.com/CrocSwap/integer-mult-bounds/pull/3080) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3081](https://github.com/CrocSwap/integer-mult-bounds/pull/3081) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3082](https://github.com/CrocSwap/integer-mult-bounds/pull/3082) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3083](https://github.com/CrocSwap/integer-mult-bounds/pull/3083) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3084](https://github.com/CrocSwap/integer-mult-bounds/pull/3084) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3085](https://github.com/CrocSwap/integer-mult-bounds/pull/3085) | navinor | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3086](https://github.com/CrocSwap/integer-mult-bounds/pull/3086) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3087](https://github.com/CrocSwap/integer-mult-bounds/pull/3087) | jmbarrancoml | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3088](https://github.com/CrocSwap/integer-mult-bounds/pull/3088) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3089](https://github.com/CrocSwap/integer-mult-bounds/pull/3089) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3090](https://github.com/CrocSwap/integer-mult-bounds/pull/3090) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3091](https://github.com/CrocSwap/integer-mult-bounds/pull/3091) | jmbarrancoml | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3092](https://github.com/CrocSwap/integer-mult-bounds/pull/3092) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3093](https://github.com/CrocSwap/integer-mult-bounds/pull/3093) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3094](https://github.com/CrocSwap/integer-mult-bounds/pull/3094) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3095](https://github.com/CrocSwap/integer-mult-bounds/pull/3095) | CubeJerry | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3096](https://github.com/CrocSwap/integer-mult-bounds/pull/3096) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3097](https://github.com/CrocSwap/integer-mult-bounds/pull/3097) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3098](https://github.com/CrocSwap/integer-mult-bounds/pull/3098) | jmbarrancoml | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3099](https://github.com/CrocSwap/integer-mult-bounds/pull/3099) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3100](https://github.com/CrocSwap/integer-mult-bounds/pull/3100) | josecarlosgonzalezroque-design | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3101](https://github.com/CrocSwap/integer-mult-bounds/pull/3101) | theon199 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3102](https://github.com/CrocSwap/integer-mult-bounds/pull/3102) | Arham-Tahir64 | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3103](https://github.com/CrocSwap/integer-mult-bounds/pull/3103) | Arham-Tahir64 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3104](https://github.com/CrocSwap/integer-mult-bounds/pull/3104) | Arham-Tahir64 | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3105](https://github.com/CrocSwap/integer-mult-bounds/pull/3105) | Arham-Tahir64 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3106](https://github.com/CrocSwap/integer-mult-bounds/pull/3106) | jmbarrancoml | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3107](https://github.com/CrocSwap/integer-mult-bounds/pull/3107) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3108](https://github.com/CrocSwap/integer-mult-bounds/pull/3108) | navinor | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3109](https://github.com/CrocSwap/integer-mult-bounds/pull/3109) | jmbarrancoml | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3110](https://github.com/CrocSwap/integer-mult-bounds/pull/3110) | navinor | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3111](https://github.com/CrocSwap/integer-mult-bounds/pull/3111) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3112](https://github.com/CrocSwap/integer-mult-bounds/pull/3112) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3113](https://github.com/CrocSwap/integer-mult-bounds/pull/3113) | navinor | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3114](https://github.com/CrocSwap/integer-mult-bounds/pull/3114) | mdumitrean | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3115](https://github.com/CrocSwap/integer-mult-bounds/pull/3115) | dataisfire | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3116](https://github.com/CrocSwap/integer-mult-bounds/pull/3116) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3117](https://github.com/CrocSwap/integer-mult-bounds/pull/3117) | CubeJerry | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3118](https://github.com/CrocSwap/integer-mult-bounds/pull/3118) | navinor | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3119](https://github.com/CrocSwap/integer-mult-bounds/pull/3119) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3120](https://github.com/CrocSwap/integer-mult-bounds/pull/3120) | navinor | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3121](https://github.com/CrocSwap/integer-mult-bounds/pull/3121) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3122](https://github.com/CrocSwap/integer-mult-bounds/pull/3122) | tekuuu | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3123](https://github.com/CrocSwap/integer-mult-bounds/pull/3123) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3124](https://github.com/CrocSwap/integer-mult-bounds/pull/3124) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3125](https://github.com/CrocSwap/integer-mult-bounds/pull/3125) | navinor | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3126](https://github.com/CrocSwap/integer-mult-bounds/pull/3126) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3127](https://github.com/CrocSwap/integer-mult-bounds/pull/3127) | tekuuu | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3128](https://github.com/CrocSwap/integer-mult-bounds/pull/3128) | theon199 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3129](https://github.com/CrocSwap/integer-mult-bounds/pull/3129) | tekuuu | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3130](https://github.com/CrocSwap/integer-mult-bounds/pull/3130) | tekuuu | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3131](https://github.com/CrocSwap/integer-mult-bounds/pull/3131) | jmbarrancoml | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3132](https://github.com/CrocSwap/integer-mult-bounds/pull/3132) | tekuuu | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3133](https://github.com/CrocSwap/integer-mult-bounds/pull/3133) | dcharb78 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3134](https://github.com/CrocSwap/integer-mult-bounds/pull/3134) | tekuuu | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3135](https://github.com/CrocSwap/integer-mult-bounds/pull/3135) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3136](https://github.com/CrocSwap/integer-mult-bounds/pull/3136) | Arham-Tahir64 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3137](https://github.com/CrocSwap/integer-mult-bounds/pull/3137) | Arham-Tahir64 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3138](https://github.com/CrocSwap/integer-mult-bounds/pull/3138) | tekuuu | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3139](https://github.com/CrocSwap/integer-mult-bounds/pull/3139) | tekuuu | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3140](https://github.com/CrocSwap/integer-mult-bounds/pull/3140) | tekuuu | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3141](https://github.com/CrocSwap/integer-mult-bounds/pull/3141) | tekuuu | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3142](https://github.com/CrocSwap/integer-mult-bounds/pull/3142) | tekuuu | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3143](https://github.com/CrocSwap/integer-mult-bounds/pull/3143) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3146](https://github.com/CrocSwap/integer-mult-bounds/pull/3146) | kumagi | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3147](https://github.com/CrocSwap/integer-mult-bounds/pull/3147) | dcharb78 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3148](https://github.com/CrocSwap/integer-mult-bounds/pull/3148) | jeremydiviney | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3150](https://github.com/CrocSwap/integer-mult-bounds/pull/3150) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3151](https://github.com/CrocSwap/integer-mult-bounds/pull/3151) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3152](https://github.com/CrocSwap/integer-mult-bounds/pull/3152) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3153](https://github.com/CrocSwap/integer-mult-bounds/pull/3153) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3154](https://github.com/CrocSwap/integer-mult-bounds/pull/3154) | DreamingOfClouds | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3157](https://github.com/CrocSwap/integer-mult-bounds/pull/3157) | rohanarun | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3158](https://github.com/CrocSwap/integer-mult-bounds/pull/3158) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3159](https://github.com/CrocSwap/integer-mult-bounds/pull/3159) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3160](https://github.com/CrocSwap/integer-mult-bounds/pull/3160) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3161](https://github.com/CrocSwap/integer-mult-bounds/pull/3161) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3162](https://github.com/CrocSwap/integer-mult-bounds/pull/3162) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3163](https://github.com/CrocSwap/integer-mult-bounds/pull/3163) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3164](https://github.com/CrocSwap/integer-mult-bounds/pull/3164) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3165](https://github.com/CrocSwap/integer-mult-bounds/pull/3165) | josecarlosgonzalezroque-design | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3166](https://github.com/CrocSwap/integer-mult-bounds/pull/3166) | conorholds | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3167](https://github.com/CrocSwap/integer-mult-bounds/pull/3167) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3168](https://github.com/CrocSwap/integer-mult-bounds/pull/3168) | Sudarsh3301 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3169](https://github.com/CrocSwap/integer-mult-bounds/pull/3169) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3170](https://github.com/CrocSwap/integer-mult-bounds/pull/3170) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3171](https://github.com/CrocSwap/integer-mult-bounds/pull/3171) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3172](https://github.com/CrocSwap/integer-mult-bounds/pull/3172) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3173](https://github.com/CrocSwap/integer-mult-bounds/pull/3173) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3174](https://github.com/CrocSwap/integer-mult-bounds/pull/3174) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3175](https://github.com/CrocSwap/integer-mult-bounds/pull/3175) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3176](https://github.com/CrocSwap/integer-mult-bounds/pull/3176) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3177](https://github.com/CrocSwap/integer-mult-bounds/pull/3177) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3179](https://github.com/CrocSwap/integer-mult-bounds/pull/3179) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3180](https://github.com/CrocSwap/integer-mult-bounds/pull/3180) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3181](https://github.com/CrocSwap/integer-mult-bounds/pull/3181) | dcharb78 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3182](https://github.com/CrocSwap/integer-mult-bounds/pull/3182) | dcharb78 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3183](https://github.com/CrocSwap/integer-mult-bounds/pull/3183) | dcharb78 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3184](https://github.com/CrocSwap/integer-mult-bounds/pull/3184) | rohanarun | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3185](https://github.com/CrocSwap/integer-mult-bounds/pull/3185) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3186](https://github.com/CrocSwap/integer-mult-bounds/pull/3186) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3187](https://github.com/CrocSwap/integer-mult-bounds/pull/3187) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3188](https://github.com/CrocSwap/integer-mult-bounds/pull/3188) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3189](https://github.com/CrocSwap/integer-mult-bounds/pull/3189) | tekuuu | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3190](https://github.com/CrocSwap/integer-mult-bounds/pull/3190) | rohanarun | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3191](https://github.com/CrocSwap/integer-mult-bounds/pull/3191) | DreamingOfClouds | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3192](https://github.com/CrocSwap/integer-mult-bounds/pull/3192) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3193](https://github.com/CrocSwap/integer-mult-bounds/pull/3193) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3194](https://github.com/CrocSwap/integer-mult-bounds/pull/3194) | jmbarrancoml | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3195](https://github.com/CrocSwap/integer-mult-bounds/pull/3195) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3196](https://github.com/CrocSwap/integer-mult-bounds/pull/3196) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3197](https://github.com/CrocSwap/integer-mult-bounds/pull/3197) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3198](https://github.com/CrocSwap/integer-mult-bounds/pull/3198) | rohanarun | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3199](https://github.com/CrocSwap/integer-mult-bounds/pull/3199) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3200](https://github.com/CrocSwap/integer-mult-bounds/pull/3200) | rohanarun | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3201](https://github.com/CrocSwap/integer-mult-bounds/pull/3201) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3202](https://github.com/CrocSwap/integer-mult-bounds/pull/3202) | 24kHandsome1201 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3203](https://github.com/CrocSwap/integer-mult-bounds/pull/3203) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3204](https://github.com/CrocSwap/integer-mult-bounds/pull/3204) | tekuuu | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3205](https://github.com/CrocSwap/integer-mult-bounds/pull/3205) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3206](https://github.com/CrocSwap/integer-mult-bounds/pull/3206) | theon199 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3207](https://github.com/CrocSwap/integer-mult-bounds/pull/3207) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3208](https://github.com/CrocSwap/integer-mult-bounds/pull/3208) | 24kHandsome1201 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3209](https://github.com/CrocSwap/integer-mult-bounds/pull/3209) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3210](https://github.com/CrocSwap/integer-mult-bounds/pull/3210) | commdata2338 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3211](https://github.com/CrocSwap/integer-mult-bounds/pull/3211) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3212](https://github.com/CrocSwap/integer-mult-bounds/pull/3212) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3213](https://github.com/CrocSwap/integer-mult-bounds/pull/3213) | commdata2338 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3214](https://github.com/CrocSwap/integer-mult-bounds/pull/3214) | commdata2338 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3215](https://github.com/CrocSwap/integer-mult-bounds/pull/3215) | commdata2338 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3216](https://github.com/CrocSwap/integer-mult-bounds/pull/3216) | commdata2338 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3217](https://github.com/CrocSwap/integer-mult-bounds/pull/3217) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3218](https://github.com/CrocSwap/integer-mult-bounds/pull/3218) | tekuuu | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3219](https://github.com/CrocSwap/integer-mult-bounds/pull/3219) | theon199 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3220](https://github.com/CrocSwap/integer-mult-bounds/pull/3220) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3221](https://github.com/CrocSwap/integer-mult-bounds/pull/3221) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3222](https://github.com/CrocSwap/integer-mult-bounds/pull/3222) | commdata2338 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3223](https://github.com/CrocSwap/integer-mult-bounds/pull/3223) | commdata2338 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3224](https://github.com/CrocSwap/integer-mult-bounds/pull/3224) | commdata2338 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3225](https://github.com/CrocSwap/integer-mult-bounds/pull/3225) | commdata2338 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3226](https://github.com/CrocSwap/integer-mult-bounds/pull/3226) | commdata2338 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3227](https://github.com/CrocSwap/integer-mult-bounds/pull/3227) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3228](https://github.com/CrocSwap/integer-mult-bounds/pull/3228) | theon199 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3229](https://github.com/CrocSwap/integer-mult-bounds/pull/3229) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3230](https://github.com/CrocSwap/integer-mult-bounds/pull/3230) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3231](https://github.com/CrocSwap/integer-mult-bounds/pull/3231) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3232](https://github.com/CrocSwap/integer-mult-bounds/pull/3232) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3233](https://github.com/CrocSwap/integer-mult-bounds/pull/3233) | commdata2338 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3234](https://github.com/CrocSwap/integer-mult-bounds/pull/3234) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3235](https://github.com/CrocSwap/integer-mult-bounds/pull/3235) | commdata2338 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3236](https://github.com/CrocSwap/integer-mult-bounds/pull/3236) | commdata2338 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3237](https://github.com/CrocSwap/integer-mult-bounds/pull/3237) | commdata2338 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3238](https://github.com/CrocSwap/integer-mult-bounds/pull/3238) | commdata2338 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3239](https://github.com/CrocSwap/integer-mult-bounds/pull/3239) | theon199 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3240](https://github.com/CrocSwap/integer-mult-bounds/pull/3240) | tekuuu | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3241](https://github.com/CrocSwap/integer-mult-bounds/pull/3241) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3242](https://github.com/CrocSwap/integer-mult-bounds/pull/3242) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3243](https://github.com/CrocSwap/integer-mult-bounds/pull/3243) | commdata2338 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3244](https://github.com/CrocSwap/integer-mult-bounds/pull/3244) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3245](https://github.com/CrocSwap/integer-mult-bounds/pull/3245) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3246](https://github.com/CrocSwap/integer-mult-bounds/pull/3246) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3247](https://github.com/CrocSwap/integer-mult-bounds/pull/3247) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3248](https://github.com/CrocSwap/integer-mult-bounds/pull/3248) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3249](https://github.com/CrocSwap/integer-mult-bounds/pull/3249) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3250](https://github.com/CrocSwap/integer-mult-bounds/pull/3250) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3251](https://github.com/CrocSwap/integer-mult-bounds/pull/3251) | rohanarun | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3252](https://github.com/CrocSwap/integer-mult-bounds/pull/3252) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3253](https://github.com/CrocSwap/integer-mult-bounds/pull/3253) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3254](https://github.com/CrocSwap/integer-mult-bounds/pull/3254) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3255](https://github.com/CrocSwap/integer-mult-bounds/pull/3255) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3256](https://github.com/CrocSwap/integer-mult-bounds/pull/3256) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3257](https://github.com/CrocSwap/integer-mult-bounds/pull/3257) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3258](https://github.com/CrocSwap/integer-mult-bounds/pull/3258) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3259](https://github.com/CrocSwap/integer-mult-bounds/pull/3259) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3260](https://github.com/CrocSwap/integer-mult-bounds/pull/3260) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3261](https://github.com/CrocSwap/integer-mult-bounds/pull/3261) | krzysztofwojt | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3262](https://github.com/CrocSwap/integer-mult-bounds/pull/3262) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3263](https://github.com/CrocSwap/integer-mult-bounds/pull/3263) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3264](https://github.com/CrocSwap/integer-mult-bounds/pull/3264) | tekuuu | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3265](https://github.com/CrocSwap/integer-mult-bounds/pull/3265) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3266](https://github.com/CrocSwap/integer-mult-bounds/pull/3266) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3267](https://github.com/CrocSwap/integer-mult-bounds/pull/3267) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3268](https://github.com/CrocSwap/integer-mult-bounds/pull/3268) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3269](https://github.com/CrocSwap/integer-mult-bounds/pull/3269) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3270](https://github.com/CrocSwap/integer-mult-bounds/pull/3270) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3271](https://github.com/CrocSwap/integer-mult-bounds/pull/3271) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3272](https://github.com/CrocSwap/integer-mult-bounds/pull/3272) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3273](https://github.com/CrocSwap/integer-mult-bounds/pull/3273) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3274](https://github.com/CrocSwap/integer-mult-bounds/pull/3274) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3275](https://github.com/CrocSwap/integer-mult-bounds/pull/3275) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3276](https://github.com/CrocSwap/integer-mult-bounds/pull/3276) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3277](https://github.com/CrocSwap/integer-mult-bounds/pull/3277) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3278](https://github.com/CrocSwap/integer-mult-bounds/pull/3278) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3279](https://github.com/CrocSwap/integer-mult-bounds/pull/3279) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3280](https://github.com/CrocSwap/integer-mult-bounds/pull/3280) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3281](https://github.com/CrocSwap/integer-mult-bounds/pull/3281) | krzysztofwojt | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3282](https://github.com/CrocSwap/integer-mult-bounds/pull/3282) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3283](https://github.com/CrocSwap/integer-mult-bounds/pull/3283) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3284](https://github.com/CrocSwap/integer-mult-bounds/pull/3284) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3285](https://github.com/CrocSwap/integer-mult-bounds/pull/3285) | Matarener | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3286](https://github.com/CrocSwap/integer-mult-bounds/pull/3286) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3287](https://github.com/CrocSwap/integer-mult-bounds/pull/3287) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3288](https://github.com/CrocSwap/integer-mult-bounds/pull/3288) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3289](https://github.com/CrocSwap/integer-mult-bounds/pull/3289) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3290](https://github.com/CrocSwap/integer-mult-bounds/pull/3290) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3291](https://github.com/CrocSwap/integer-mult-bounds/pull/3291) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3292](https://github.com/CrocSwap/integer-mult-bounds/pull/3292) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3293](https://github.com/CrocSwap/integer-mult-bounds/pull/3293) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3294](https://github.com/CrocSwap/integer-mult-bounds/pull/3294) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3295](https://github.com/CrocSwap/integer-mult-bounds/pull/3295) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3296](https://github.com/CrocSwap/integer-mult-bounds/pull/3296) | Matarener | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3297](https://github.com/CrocSwap/integer-mult-bounds/pull/3297) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3298](https://github.com/CrocSwap/integer-mult-bounds/pull/3298) | tekuuu | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3299](https://github.com/CrocSwap/integer-mult-bounds/pull/3299) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3300](https://github.com/CrocSwap/integer-mult-bounds/pull/3300) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3301](https://github.com/CrocSwap/integer-mult-bounds/pull/3301) | krzysztofwojt | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3302](https://github.com/CrocSwap/integer-mult-bounds/pull/3302) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3303](https://github.com/CrocSwap/integer-mult-bounds/pull/3303) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3304](https://github.com/CrocSwap/integer-mult-bounds/pull/3304) | petalas | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3305](https://github.com/CrocSwap/integer-mult-bounds/pull/3305) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3306](https://github.com/CrocSwap/integer-mult-bounds/pull/3306) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3307](https://github.com/CrocSwap/integer-mult-bounds/pull/3307) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3308](https://github.com/CrocSwap/integer-mult-bounds/pull/3308) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3309](https://github.com/CrocSwap/integer-mult-bounds/pull/3309) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3310](https://github.com/CrocSwap/integer-mult-bounds/pull/3310) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3311](https://github.com/CrocSwap/integer-mult-bounds/pull/3311) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3312](https://github.com/CrocSwap/integer-mult-bounds/pull/3312) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3313](https://github.com/CrocSwap/integer-mult-bounds/pull/3313) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3314](https://github.com/CrocSwap/integer-mult-bounds/pull/3314) | 1337isnot1337 | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3315](https://github.com/CrocSwap/integer-mult-bounds/pull/3315) | muatfannajm-dot | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3316](https://github.com/CrocSwap/integer-mult-bounds/pull/3316) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3317](https://github.com/CrocSwap/integer-mult-bounds/pull/3317) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3318](https://github.com/CrocSwap/integer-mult-bounds/pull/3318) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3319](https://github.com/CrocSwap/integer-mult-bounds/pull/3319) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3320](https://github.com/CrocSwap/integer-mult-bounds/pull/3320) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3321](https://github.com/CrocSwap/integer-mult-bounds/pull/3321) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3322](https://github.com/CrocSwap/integer-mult-bounds/pull/3322) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3323](https://github.com/CrocSwap/integer-mult-bounds/pull/3323) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3324](https://github.com/CrocSwap/integer-mult-bounds/pull/3324) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3325](https://github.com/CrocSwap/integer-mult-bounds/pull/3325) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3326](https://github.com/CrocSwap/integer-mult-bounds/pull/3326) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3327](https://github.com/CrocSwap/integer-mult-bounds/pull/3327) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3328](https://github.com/CrocSwap/integer-mult-bounds/pull/3328) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3329](https://github.com/CrocSwap/integer-mult-bounds/pull/3329) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3330](https://github.com/CrocSwap/integer-mult-bounds/pull/3330) | tekuuu | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3331](https://github.com/CrocSwap/integer-mult-bounds/pull/3331) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3332](https://github.com/CrocSwap/integer-mult-bounds/pull/3332) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3333](https://github.com/CrocSwap/integer-mult-bounds/pull/3333) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3334](https://github.com/CrocSwap/integer-mult-bounds/pull/3334) | krzysztofwojt | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3335](https://github.com/CrocSwap/integer-mult-bounds/pull/3335) | Matarener | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3336](https://github.com/CrocSwap/integer-mult-bounds/pull/3336) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3337](https://github.com/CrocSwap/integer-mult-bounds/pull/3337) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3338](https://github.com/CrocSwap/integer-mult-bounds/pull/3338) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3339](https://github.com/CrocSwap/integer-mult-bounds/pull/3339) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3340](https://github.com/CrocSwap/integer-mult-bounds/pull/3340) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3341](https://github.com/CrocSwap/integer-mult-bounds/pull/3341) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3342](https://github.com/CrocSwap/integer-mult-bounds/pull/3342) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3343](https://github.com/CrocSwap/integer-mult-bounds/pull/3343) | tekuuu | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3344](https://github.com/CrocSwap/integer-mult-bounds/pull/3344) | Matarener | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3345](https://github.com/CrocSwap/integer-mult-bounds/pull/3345) | Arham-Tahir64 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3346](https://github.com/CrocSwap/integer-mult-bounds/pull/3346) | hexapode | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3347](https://github.com/CrocSwap/integer-mult-bounds/pull/3347) | Arham-Tahir64 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3348](https://github.com/CrocSwap/integer-mult-bounds/pull/3348) | Arham-Tahir64 | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3349](https://github.com/CrocSwap/integer-mult-bounds/pull/3349) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3350](https://github.com/CrocSwap/integer-mult-bounds/pull/3350) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3351](https://github.com/CrocSwap/integer-mult-bounds/pull/3351) | Arham-Tahir64 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3352](https://github.com/CrocSwap/integer-mult-bounds/pull/3352) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3353](https://github.com/CrocSwap/integer-mult-bounds/pull/3353) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3354](https://github.com/CrocSwap/integer-mult-bounds/pull/3354) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3356](https://github.com/CrocSwap/integer-mult-bounds/pull/3356) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3357](https://github.com/CrocSwap/integer-mult-bounds/pull/3357) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3358](https://github.com/CrocSwap/integer-mult-bounds/pull/3358) | 1337isnot1337 | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3359](https://github.com/CrocSwap/integer-mult-bounds/pull/3359) | hexapode | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3360](https://github.com/CrocSwap/integer-mult-bounds/pull/3360) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3361](https://github.com/CrocSwap/integer-mult-bounds/pull/3361) | dataisfire | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3362](https://github.com/CrocSwap/integer-mult-bounds/pull/3362) | tekuuu | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3363](https://github.com/CrocSwap/integer-mult-bounds/pull/3363) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3364](https://github.com/CrocSwap/integer-mult-bounds/pull/3364) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3365](https://github.com/CrocSwap/integer-mult-bounds/pull/3365) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3366](https://github.com/CrocSwap/integer-mult-bounds/pull/3366) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3367](https://github.com/CrocSwap/integer-mult-bounds/pull/3367) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3368](https://github.com/CrocSwap/integer-mult-bounds/pull/3368) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3369](https://github.com/CrocSwap/integer-mult-bounds/pull/3369) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3370](https://github.com/CrocSwap/integer-mult-bounds/pull/3370) | tekuuu | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3371](https://github.com/CrocSwap/integer-mult-bounds/pull/3371) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3372](https://github.com/CrocSwap/integer-mult-bounds/pull/3372) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3373](https://github.com/CrocSwap/integer-mult-bounds/pull/3373) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3374](https://github.com/CrocSwap/integer-mult-bounds/pull/3374) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3375](https://github.com/CrocSwap/integer-mult-bounds/pull/3375) | hexapode | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3376](https://github.com/CrocSwap/integer-mult-bounds/pull/3376) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3377](https://github.com/CrocSwap/integer-mult-bounds/pull/3377) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3378](https://github.com/CrocSwap/integer-mult-bounds/pull/3378) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3379](https://github.com/CrocSwap/integer-mult-bounds/pull/3379) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3380](https://github.com/CrocSwap/integer-mult-bounds/pull/3380) | tekuuu | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3381](https://github.com/CrocSwap/integer-mult-bounds/pull/3381) | hexapode | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3382](https://github.com/CrocSwap/integer-mult-bounds/pull/3382) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3383](https://github.com/CrocSwap/integer-mult-bounds/pull/3383) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3384](https://github.com/CrocSwap/integer-mult-bounds/pull/3384) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3385](https://github.com/CrocSwap/integer-mult-bounds/pull/3385) | jmbarrancoml | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3386](https://github.com/CrocSwap/integer-mult-bounds/pull/3386) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3387](https://github.com/CrocSwap/integer-mult-bounds/pull/3387) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3388](https://github.com/CrocSwap/integer-mult-bounds/pull/3388) | hexapode | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3389](https://github.com/CrocSwap/integer-mult-bounds/pull/3389) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3390](https://github.com/CrocSwap/integer-mult-bounds/pull/3390) | hexapode | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3391](https://github.com/CrocSwap/integer-mult-bounds/pull/3391) | PellaML | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3392](https://github.com/CrocSwap/integer-mult-bounds/pull/3392) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3393](https://github.com/CrocSwap/integer-mult-bounds/pull/3393) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3394](https://github.com/CrocSwap/integer-mult-bounds/pull/3394) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3395](https://github.com/CrocSwap/integer-mult-bounds/pull/3395) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3396](https://github.com/CrocSwap/integer-mult-bounds/pull/3396) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3397](https://github.com/CrocSwap/integer-mult-bounds/pull/3397) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3398](https://github.com/CrocSwap/integer-mult-bounds/pull/3398) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3399](https://github.com/CrocSwap/integer-mult-bounds/pull/3399) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3400](https://github.com/CrocSwap/integer-mult-bounds/pull/3400) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3401](https://github.com/CrocSwap/integer-mult-bounds/pull/3401) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3402](https://github.com/CrocSwap/integer-mult-bounds/pull/3402) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3403](https://github.com/CrocSwap/integer-mult-bounds/pull/3403) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3404](https://github.com/CrocSwap/integer-mult-bounds/pull/3404) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3405](https://github.com/CrocSwap/integer-mult-bounds/pull/3405) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3406](https://github.com/CrocSwap/integer-mult-bounds/pull/3406) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3407](https://github.com/CrocSwap/integer-mult-bounds/pull/3407) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3408](https://github.com/CrocSwap/integer-mult-bounds/pull/3408) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3409](https://github.com/CrocSwap/integer-mult-bounds/pull/3409) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3410](https://github.com/CrocSwap/integer-mult-bounds/pull/3410) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3411](https://github.com/CrocSwap/integer-mult-bounds/pull/3411) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3412](https://github.com/CrocSwap/integer-mult-bounds/pull/3412) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3413](https://github.com/CrocSwap/integer-mult-bounds/pull/3413) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3414](https://github.com/CrocSwap/integer-mult-bounds/pull/3414) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3415](https://github.com/CrocSwap/integer-mult-bounds/pull/3415) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3416](https://github.com/CrocSwap/integer-mult-bounds/pull/3416) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3417](https://github.com/CrocSwap/integer-mult-bounds/pull/3417) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3418](https://github.com/CrocSwap/integer-mult-bounds/pull/3418) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3419](https://github.com/CrocSwap/integer-mult-bounds/pull/3419) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3420](https://github.com/CrocSwap/integer-mult-bounds/pull/3420) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3421](https://github.com/CrocSwap/integer-mult-bounds/pull/3421) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3422](https://github.com/CrocSwap/integer-mult-bounds/pull/3422) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3423](https://github.com/CrocSwap/integer-mult-bounds/pull/3423) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3424](https://github.com/CrocSwap/integer-mult-bounds/pull/3424) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3425](https://github.com/CrocSwap/integer-mult-bounds/pull/3425) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3426](https://github.com/CrocSwap/integer-mult-bounds/pull/3426) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3427](https://github.com/CrocSwap/integer-mult-bounds/pull/3427) | jmbarrancoml | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3428](https://github.com/CrocSwap/integer-mult-bounds/pull/3428) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3429](https://github.com/CrocSwap/integer-mult-bounds/pull/3429) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3430](https://github.com/CrocSwap/integer-mult-bounds/pull/3430) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3431](https://github.com/CrocSwap/integer-mult-bounds/pull/3431) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3432](https://github.com/CrocSwap/integer-mult-bounds/pull/3432) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3433](https://github.com/CrocSwap/integer-mult-bounds/pull/3433) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3434](https://github.com/CrocSwap/integer-mult-bounds/pull/3434) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3435](https://github.com/CrocSwap/integer-mult-bounds/pull/3435) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3436](https://github.com/CrocSwap/integer-mult-bounds/pull/3436) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3437](https://github.com/CrocSwap/integer-mult-bounds/pull/3437) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3438](https://github.com/CrocSwap/integer-mult-bounds/pull/3438) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3439](https://github.com/CrocSwap/integer-mult-bounds/pull/3439) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3440](https://github.com/CrocSwap/integer-mult-bounds/pull/3440) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3441](https://github.com/CrocSwap/integer-mult-bounds/pull/3441) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3442](https://github.com/CrocSwap/integer-mult-bounds/pull/3442) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3443](https://github.com/CrocSwap/integer-mult-bounds/pull/3443) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3444](https://github.com/CrocSwap/integer-mult-bounds/pull/3444) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3445](https://github.com/CrocSwap/integer-mult-bounds/pull/3445) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3446](https://github.com/CrocSwap/integer-mult-bounds/pull/3446) | kumagi | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3447](https://github.com/CrocSwap/integer-mult-bounds/pull/3447) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3448](https://github.com/CrocSwap/integer-mult-bounds/pull/3448) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3449](https://github.com/CrocSwap/integer-mult-bounds/pull/3449) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3450](https://github.com/CrocSwap/integer-mult-bounds/pull/3450) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3451](https://github.com/CrocSwap/integer-mult-bounds/pull/3451) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3452](https://github.com/CrocSwap/integer-mult-bounds/pull/3452) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3453](https://github.com/CrocSwap/integer-mult-bounds/pull/3453) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3454](https://github.com/CrocSwap/integer-mult-bounds/pull/3454) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3455](https://github.com/CrocSwap/integer-mult-bounds/pull/3455) | conorholds | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3456](https://github.com/CrocSwap/integer-mult-bounds/pull/3456) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3457](https://github.com/CrocSwap/integer-mult-bounds/pull/3457) | hexapode | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3458](https://github.com/CrocSwap/integer-mult-bounds/pull/3458) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3459](https://github.com/CrocSwap/integer-mult-bounds/pull/3459) | CubeJerry | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3460](https://github.com/CrocSwap/integer-mult-bounds/pull/3460) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3461](https://github.com/CrocSwap/integer-mult-bounds/pull/3461) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3462](https://github.com/CrocSwap/integer-mult-bounds/pull/3462) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3463](https://github.com/CrocSwap/integer-mult-bounds/pull/3463) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3464](https://github.com/CrocSwap/integer-mult-bounds/pull/3464) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3465](https://github.com/CrocSwap/integer-mult-bounds/pull/3465) | hexapode | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3466](https://github.com/CrocSwap/integer-mult-bounds/pull/3466) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3467](https://github.com/CrocSwap/integer-mult-bounds/pull/3467) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3468](https://github.com/CrocSwap/integer-mult-bounds/pull/3468) | hexapode | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3469](https://github.com/CrocSwap/integer-mult-bounds/pull/3469) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3470](https://github.com/CrocSwap/integer-mult-bounds/pull/3470) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3471](https://github.com/CrocSwap/integer-mult-bounds/pull/3471) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3472](https://github.com/CrocSwap/integer-mult-bounds/pull/3472) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3473](https://github.com/CrocSwap/integer-mult-bounds/pull/3473) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3474](https://github.com/CrocSwap/integer-mult-bounds/pull/3474) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3475](https://github.com/CrocSwap/integer-mult-bounds/pull/3475) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3476](https://github.com/CrocSwap/integer-mult-bounds/pull/3476) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3477](https://github.com/CrocSwap/integer-mult-bounds/pull/3477) | jmbarrancoml | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3478](https://github.com/CrocSwap/integer-mult-bounds/pull/3478) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3479](https://github.com/CrocSwap/integer-mult-bounds/pull/3479) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3480](https://github.com/CrocSwap/integer-mult-bounds/pull/3480) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3481](https://github.com/CrocSwap/integer-mult-bounds/pull/3481) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3482](https://github.com/CrocSwap/integer-mult-bounds/pull/3482) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3483](https://github.com/CrocSwap/integer-mult-bounds/pull/3483) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3484](https://github.com/CrocSwap/integer-mult-bounds/pull/3484) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3485](https://github.com/CrocSwap/integer-mult-bounds/pull/3485) | hexapode | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3486](https://github.com/CrocSwap/integer-mult-bounds/pull/3486) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3487](https://github.com/CrocSwap/integer-mult-bounds/pull/3487) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3488](https://github.com/CrocSwap/integer-mult-bounds/pull/3488) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3489](https://github.com/CrocSwap/integer-mult-bounds/pull/3489) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3490](https://github.com/CrocSwap/integer-mult-bounds/pull/3490) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3491](https://github.com/CrocSwap/integer-mult-bounds/pull/3491) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3492](https://github.com/CrocSwap/integer-mult-bounds/pull/3492) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3493](https://github.com/CrocSwap/integer-mult-bounds/pull/3493) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3494](https://github.com/CrocSwap/integer-mult-bounds/pull/3494) | hexapode | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3495](https://github.com/CrocSwap/integer-mult-bounds/pull/3495) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3496](https://github.com/CrocSwap/integer-mult-bounds/pull/3496) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3497](https://github.com/CrocSwap/integer-mult-bounds/pull/3497) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3498](https://github.com/CrocSwap/integer-mult-bounds/pull/3498) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3499](https://github.com/CrocSwap/integer-mult-bounds/pull/3499) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3500](https://github.com/CrocSwap/integer-mult-bounds/pull/3500) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3501](https://github.com/CrocSwap/integer-mult-bounds/pull/3501) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3502](https://github.com/CrocSwap/integer-mult-bounds/pull/3502) | kumagi | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3503](https://github.com/CrocSwap/integer-mult-bounds/pull/3503) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3504](https://github.com/CrocSwap/integer-mult-bounds/pull/3504) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3505](https://github.com/CrocSwap/integer-mult-bounds/pull/3505) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3506](https://github.com/CrocSwap/integer-mult-bounds/pull/3506) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3507](https://github.com/CrocSwap/integer-mult-bounds/pull/3507) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3508](https://github.com/CrocSwap/integer-mult-bounds/pull/3508) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3509](https://github.com/CrocSwap/integer-mult-bounds/pull/3509) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3510](https://github.com/CrocSwap/integer-mult-bounds/pull/3510) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3511](https://github.com/CrocSwap/integer-mult-bounds/pull/3511) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3512](https://github.com/CrocSwap/integer-mult-bounds/pull/3512) | jmbarrancoml | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3513](https://github.com/CrocSwap/integer-mult-bounds/pull/3513) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3514](https://github.com/CrocSwap/integer-mult-bounds/pull/3514) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3515](https://github.com/CrocSwap/integer-mult-bounds/pull/3515) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3516](https://github.com/CrocSwap/integer-mult-bounds/pull/3516) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3517](https://github.com/CrocSwap/integer-mult-bounds/pull/3517) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3518](https://github.com/CrocSwap/integer-mult-bounds/pull/3518) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3519](https://github.com/CrocSwap/integer-mult-bounds/pull/3519) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3520](https://github.com/CrocSwap/integer-mult-bounds/pull/3520) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3521](https://github.com/CrocSwap/integer-mult-bounds/pull/3521) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3522](https://github.com/CrocSwap/integer-mult-bounds/pull/3522) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3523](https://github.com/CrocSwap/integer-mult-bounds/pull/3523) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3524](https://github.com/CrocSwap/integer-mult-bounds/pull/3524) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3525](https://github.com/CrocSwap/integer-mult-bounds/pull/3525) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3526](https://github.com/CrocSwap/integer-mult-bounds/pull/3526) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3527](https://github.com/CrocSwap/integer-mult-bounds/pull/3527) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3528](https://github.com/CrocSwap/integer-mult-bounds/pull/3528) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3529](https://github.com/CrocSwap/integer-mult-bounds/pull/3529) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3530](https://github.com/CrocSwap/integer-mult-bounds/pull/3530) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3531](https://github.com/CrocSwap/integer-mult-bounds/pull/3531) | SovereignSteak | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3532](https://github.com/CrocSwap/integer-mult-bounds/pull/3532) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3533](https://github.com/CrocSwap/integer-mult-bounds/pull/3533) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3534](https://github.com/CrocSwap/integer-mult-bounds/pull/3534) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3535](https://github.com/CrocSwap/integer-mult-bounds/pull/3535) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3536](https://github.com/CrocSwap/integer-mult-bounds/pull/3536) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3537](https://github.com/CrocSwap/integer-mult-bounds/pull/3537) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3538](https://github.com/CrocSwap/integer-mult-bounds/pull/3538) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3539](https://github.com/CrocSwap/integer-mult-bounds/pull/3539) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3540](https://github.com/CrocSwap/integer-mult-bounds/pull/3540) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3541](https://github.com/CrocSwap/integer-mult-bounds/pull/3541) | SovereignSteak | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3542](https://github.com/CrocSwap/integer-mult-bounds/pull/3542) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3543](https://github.com/CrocSwap/integer-mult-bounds/pull/3543) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3544](https://github.com/CrocSwap/integer-mult-bounds/pull/3544) | jmbarrancoml | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3545](https://github.com/CrocSwap/integer-mult-bounds/pull/3545) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3546](https://github.com/CrocSwap/integer-mult-bounds/pull/3546) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3547](https://github.com/CrocSwap/integer-mult-bounds/pull/3547) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3548](https://github.com/CrocSwap/integer-mult-bounds/pull/3548) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3549](https://github.com/CrocSwap/integer-mult-bounds/pull/3549) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3550](https://github.com/CrocSwap/integer-mult-bounds/pull/3550) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3551](https://github.com/CrocSwap/integer-mult-bounds/pull/3551) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3552](https://github.com/CrocSwap/integer-mult-bounds/pull/3552) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3553](https://github.com/CrocSwap/integer-mult-bounds/pull/3553) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3554](https://github.com/CrocSwap/integer-mult-bounds/pull/3554) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3555](https://github.com/CrocSwap/integer-mult-bounds/pull/3555) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3556](https://github.com/CrocSwap/integer-mult-bounds/pull/3556) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3557](https://github.com/CrocSwap/integer-mult-bounds/pull/3557) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3558](https://github.com/CrocSwap/integer-mult-bounds/pull/3558) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3559](https://github.com/CrocSwap/integer-mult-bounds/pull/3559) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3560](https://github.com/CrocSwap/integer-mult-bounds/pull/3560) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3561](https://github.com/CrocSwap/integer-mult-bounds/pull/3561) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3562](https://github.com/CrocSwap/integer-mult-bounds/pull/3562) | jmbarrancoml | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3563](https://github.com/CrocSwap/integer-mult-bounds/pull/3563) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3564](https://github.com/CrocSwap/integer-mult-bounds/pull/3564) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3565](https://github.com/CrocSwap/integer-mult-bounds/pull/3565) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3566](https://github.com/CrocSwap/integer-mult-bounds/pull/3566) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3567](https://github.com/CrocSwap/integer-mult-bounds/pull/3567) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3568](https://github.com/CrocSwap/integer-mult-bounds/pull/3568) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3569](https://github.com/CrocSwap/integer-mult-bounds/pull/3569) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3570](https://github.com/CrocSwap/integer-mult-bounds/pull/3570) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3571](https://github.com/CrocSwap/integer-mult-bounds/pull/3571) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3572](https://github.com/CrocSwap/integer-mult-bounds/pull/3572) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3573](https://github.com/CrocSwap/integer-mult-bounds/pull/3573) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3574](https://github.com/CrocSwap/integer-mult-bounds/pull/3574) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3575](https://github.com/CrocSwap/integer-mult-bounds/pull/3575) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3576](https://github.com/CrocSwap/integer-mult-bounds/pull/3576) | kumagi | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3577](https://github.com/CrocSwap/integer-mult-bounds/pull/3577) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3578](https://github.com/CrocSwap/integer-mult-bounds/pull/3578) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3579](https://github.com/CrocSwap/integer-mult-bounds/pull/3579) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3580](https://github.com/CrocSwap/integer-mult-bounds/pull/3580) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3581](https://github.com/CrocSwap/integer-mult-bounds/pull/3581) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3582](https://github.com/CrocSwap/integer-mult-bounds/pull/3582) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3583](https://github.com/CrocSwap/integer-mult-bounds/pull/3583) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3584](https://github.com/CrocSwap/integer-mult-bounds/pull/3584) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3585](https://github.com/CrocSwap/integer-mult-bounds/pull/3585) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3586](https://github.com/CrocSwap/integer-mult-bounds/pull/3586) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3587](https://github.com/CrocSwap/integer-mult-bounds/pull/3587) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3588](https://github.com/CrocSwap/integer-mult-bounds/pull/3588) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3589](https://github.com/CrocSwap/integer-mult-bounds/pull/3589) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3590](https://github.com/CrocSwap/integer-mult-bounds/pull/3590) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3591](https://github.com/CrocSwap/integer-mult-bounds/pull/3591) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3592](https://github.com/CrocSwap/integer-mult-bounds/pull/3592) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3593](https://github.com/CrocSwap/integer-mult-bounds/pull/3593) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3594](https://github.com/CrocSwap/integer-mult-bounds/pull/3594) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3596](https://github.com/CrocSwap/integer-mult-bounds/pull/3596) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3597](https://github.com/CrocSwap/integer-mult-bounds/pull/3597) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3598](https://github.com/CrocSwap/integer-mult-bounds/pull/3598) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3599](https://github.com/CrocSwap/integer-mult-bounds/pull/3599) | jmbarrancoml | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3600](https://github.com/CrocSwap/integer-mult-bounds/pull/3600) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3601](https://github.com/CrocSwap/integer-mult-bounds/pull/3601) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3602](https://github.com/CrocSwap/integer-mult-bounds/pull/3602) | roger-sato | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3603](https://github.com/CrocSwap/integer-mult-bounds/pull/3603) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3604](https://github.com/CrocSwap/integer-mult-bounds/pull/3604) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3605](https://github.com/CrocSwap/integer-mult-bounds/pull/3605) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3607](https://github.com/CrocSwap/integer-mult-bounds/pull/3607) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3608](https://github.com/CrocSwap/integer-mult-bounds/pull/3608) | jmbarrancoml | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3609](https://github.com/CrocSwap/integer-mult-bounds/pull/3609) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3610](https://github.com/CrocSwap/integer-mult-bounds/pull/3610) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3611](https://github.com/CrocSwap/integer-mult-bounds/pull/3611) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3612](https://github.com/CrocSwap/integer-mult-bounds/pull/3612) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3613](https://github.com/CrocSwap/integer-mult-bounds/pull/3613) | roger-sato | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3614](https://github.com/CrocSwap/integer-mult-bounds/pull/3614) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3615](https://github.com/CrocSwap/integer-mult-bounds/pull/3615) | roger-sato | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3616](https://github.com/CrocSwap/integer-mult-bounds/pull/3616) | roger-sato | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3617](https://github.com/CrocSwap/integer-mult-bounds/pull/3617) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3618](https://github.com/CrocSwap/integer-mult-bounds/pull/3618) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3619](https://github.com/CrocSwap/integer-mult-bounds/pull/3619) | jmbarrancoml | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3620](https://github.com/CrocSwap/integer-mult-bounds/pull/3620) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3621](https://github.com/CrocSwap/integer-mult-bounds/pull/3621) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3623](https://github.com/CrocSwap/integer-mult-bounds/pull/3623) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3624](https://github.com/CrocSwap/integer-mult-bounds/pull/3624) | hexapode | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3625](https://github.com/CrocSwap/integer-mult-bounds/pull/3625) | Matarener | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3626](https://github.com/CrocSwap/integer-mult-bounds/pull/3626) | hexapode | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3627](https://github.com/CrocSwap/integer-mult-bounds/pull/3627) | jmbarrancoml | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3628](https://github.com/CrocSwap/integer-mult-bounds/pull/3628) | roger-sato | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3629](https://github.com/CrocSwap/integer-mult-bounds/pull/3629) | roger-sato | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3630](https://github.com/CrocSwap/integer-mult-bounds/pull/3630) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3631](https://github.com/CrocSwap/integer-mult-bounds/pull/3631) | roger-sato | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3632](https://github.com/CrocSwap/integer-mult-bounds/pull/3632) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3633](https://github.com/CrocSwap/integer-mult-bounds/pull/3633) | hexapode | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3634](https://github.com/CrocSwap/integer-mult-bounds/pull/3634) | roger-sato | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3635](https://github.com/CrocSwap/integer-mult-bounds/pull/3635) | roger-sato | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3636](https://github.com/CrocSwap/integer-mult-bounds/pull/3636) | roger-sato | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3637](https://github.com/CrocSwap/integer-mult-bounds/pull/3637) | roger-sato | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3638](https://github.com/CrocSwap/integer-mult-bounds/pull/3638) | zxv | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3639](https://github.com/CrocSwap/integer-mult-bounds/pull/3639) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3640](https://github.com/CrocSwap/integer-mult-bounds/pull/3640) | jmbarrancoml | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3641](https://github.com/CrocSwap/integer-mult-bounds/pull/3641) | roger-sato | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3642](https://github.com/CrocSwap/integer-mult-bounds/pull/3642) | roger-sato | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3643](https://github.com/CrocSwap/integer-mult-bounds/pull/3643) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3644](https://github.com/CrocSwap/integer-mult-bounds/pull/3644) | roger-sato | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3645](https://github.com/CrocSwap/integer-mult-bounds/pull/3645) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3646](https://github.com/CrocSwap/integer-mult-bounds/pull/3646) | roger-sato | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3647](https://github.com/CrocSwap/integer-mult-bounds/pull/3647) | ai-nanachi | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3648](https://github.com/CrocSwap/integer-mult-bounds/pull/3648) | roger-sato | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3649](https://github.com/CrocSwap/integer-mult-bounds/pull/3649) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3650](https://github.com/CrocSwap/integer-mult-bounds/pull/3650) | PellaML | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3651](https://github.com/CrocSwap/integer-mult-bounds/pull/3651) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3652](https://github.com/CrocSwap/integer-mult-bounds/pull/3652) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3653](https://github.com/CrocSwap/integer-mult-bounds/pull/3653) | rohanarun | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3654](https://github.com/CrocSwap/integer-mult-bounds/pull/3654) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3655](https://github.com/CrocSwap/integer-mult-bounds/pull/3655) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3656](https://github.com/CrocSwap/integer-mult-bounds/pull/3656) | Matarener | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3658](https://github.com/CrocSwap/integer-mult-bounds/pull/3658) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3659](https://github.com/CrocSwap/integer-mult-bounds/pull/3659) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3660](https://github.com/CrocSwap/integer-mult-bounds/pull/3660) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3661](https://github.com/CrocSwap/integer-mult-bounds/pull/3661) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3662](https://github.com/CrocSwap/integer-mult-bounds/pull/3662) | hevlyo | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3663](https://github.com/CrocSwap/integer-mult-bounds/pull/3663) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3665](https://github.com/CrocSwap/integer-mult-bounds/pull/3665) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3666](https://github.com/CrocSwap/integer-mult-bounds/pull/3666) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3667](https://github.com/CrocSwap/integer-mult-bounds/pull/3667) | Mainzu | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3668](https://github.com/CrocSwap/integer-mult-bounds/pull/3668) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3669](https://github.com/CrocSwap/integer-mult-bounds/pull/3669) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3670](https://github.com/CrocSwap/integer-mult-bounds/pull/3670) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3671](https://github.com/CrocSwap/integer-mult-bounds/pull/3671) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3672](https://github.com/CrocSwap/integer-mult-bounds/pull/3672) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3673](https://github.com/CrocSwap/integer-mult-bounds/pull/3673) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3674](https://github.com/CrocSwap/integer-mult-bounds/pull/3674) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3675](https://github.com/CrocSwap/integer-mult-bounds/pull/3675) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3676](https://github.com/CrocSwap/integer-mult-bounds/pull/3676) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3677](https://github.com/CrocSwap/integer-mult-bounds/pull/3677) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3678](https://github.com/CrocSwap/integer-mult-bounds/pull/3678) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3679](https://github.com/CrocSwap/integer-mult-bounds/pull/3679) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3680](https://github.com/CrocSwap/integer-mult-bounds/pull/3680) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3681](https://github.com/CrocSwap/integer-mult-bounds/pull/3681) | roger-sato | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3682](https://github.com/CrocSwap/integer-mult-bounds/pull/3682) | zxv | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3683](https://github.com/CrocSwap/integer-mult-bounds/pull/3683) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3684](https://github.com/CrocSwap/integer-mult-bounds/pull/3684) | flyingviper | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3685](https://github.com/CrocSwap/integer-mult-bounds/pull/3685) | flyingviper | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3686](https://github.com/CrocSwap/integer-mult-bounds/pull/3686) | roger-sato | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3687](https://github.com/CrocSwap/integer-mult-bounds/pull/3687) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3688](https://github.com/CrocSwap/integer-mult-bounds/pull/3688) | roger-sato | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3689](https://github.com/CrocSwap/integer-mult-bounds/pull/3689) | conorholds | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3690](https://github.com/CrocSwap/integer-mult-bounds/pull/3690) | zxv | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3691](https://github.com/CrocSwap/integer-mult-bounds/pull/3691) | zxv | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3692](https://github.com/CrocSwap/integer-mult-bounds/pull/3692) | roger-sato | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3693](https://github.com/CrocSwap/integer-mult-bounds/pull/3693) | roger-sato | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3694](https://github.com/CrocSwap/integer-mult-bounds/pull/3694) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3695](https://github.com/CrocSwap/integer-mult-bounds/pull/3695) | muatfannajm-dot | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3696](https://github.com/CrocSwap/integer-mult-bounds/pull/3696) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3697](https://github.com/CrocSwap/integer-mult-bounds/pull/3697) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3698](https://github.com/CrocSwap/integer-mult-bounds/pull/3698) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3699](https://github.com/CrocSwap/integer-mult-bounds/pull/3699) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3700](https://github.com/CrocSwap/integer-mult-bounds/pull/3700) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3701](https://github.com/CrocSwap/integer-mult-bounds/pull/3701) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3702](https://github.com/CrocSwap/integer-mult-bounds/pull/3702) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3703](https://github.com/CrocSwap/integer-mult-bounds/pull/3703) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3704](https://github.com/CrocSwap/integer-mult-bounds/pull/3704) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3705](https://github.com/CrocSwap/integer-mult-bounds/pull/3705) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3706](https://github.com/CrocSwap/integer-mult-bounds/pull/3706) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3707](https://github.com/CrocSwap/integer-mult-bounds/pull/3707) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3708](https://github.com/CrocSwap/integer-mult-bounds/pull/3708) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3709](https://github.com/CrocSwap/integer-mult-bounds/pull/3709) | jmbarrancoml | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3710](https://github.com/CrocSwap/integer-mult-bounds/pull/3710) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3711](https://github.com/CrocSwap/integer-mult-bounds/pull/3711) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3712](https://github.com/CrocSwap/integer-mult-bounds/pull/3712) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3713](https://github.com/CrocSwap/integer-mult-bounds/pull/3713) | Mainzu | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3714](https://github.com/CrocSwap/integer-mult-bounds/pull/3714) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3715](https://github.com/CrocSwap/integer-mult-bounds/pull/3715) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3716](https://github.com/CrocSwap/integer-mult-bounds/pull/3716) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3717](https://github.com/CrocSwap/integer-mult-bounds/pull/3717) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3718](https://github.com/CrocSwap/integer-mult-bounds/pull/3718) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3719](https://github.com/CrocSwap/integer-mult-bounds/pull/3719) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3720](https://github.com/CrocSwap/integer-mult-bounds/pull/3720) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3721](https://github.com/CrocSwap/integer-mult-bounds/pull/3721) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3722](https://github.com/CrocSwap/integer-mult-bounds/pull/3722) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3723](https://github.com/CrocSwap/integer-mult-bounds/pull/3723) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3724](https://github.com/CrocSwap/integer-mult-bounds/pull/3724) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3726](https://github.com/CrocSwap/integer-mult-bounds/pull/3726) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3727](https://github.com/CrocSwap/integer-mult-bounds/pull/3727) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3728](https://github.com/CrocSwap/integer-mult-bounds/pull/3728) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3729](https://github.com/CrocSwap/integer-mult-bounds/pull/3729) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3730](https://github.com/CrocSwap/integer-mult-bounds/pull/3730) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3731](https://github.com/CrocSwap/integer-mult-bounds/pull/3731) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3732](https://github.com/CrocSwap/integer-mult-bounds/pull/3732) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3733](https://github.com/CrocSwap/integer-mult-bounds/pull/3733) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3734](https://github.com/CrocSwap/integer-mult-bounds/pull/3734) | dataisfire | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3735](https://github.com/CrocSwap/integer-mult-bounds/pull/3735) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3736](https://github.com/CrocSwap/integer-mult-bounds/pull/3736) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3737](https://github.com/CrocSwap/integer-mult-bounds/pull/3737) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3738](https://github.com/CrocSwap/integer-mult-bounds/pull/3738) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3739](https://github.com/CrocSwap/integer-mult-bounds/pull/3739) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3740](https://github.com/CrocSwap/integer-mult-bounds/pull/3740) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3741](https://github.com/CrocSwap/integer-mult-bounds/pull/3741) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3742](https://github.com/CrocSwap/integer-mult-bounds/pull/3742) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3743](https://github.com/CrocSwap/integer-mult-bounds/pull/3743) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3744](https://github.com/CrocSwap/integer-mult-bounds/pull/3744) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3745](https://github.com/CrocSwap/integer-mult-bounds/pull/3745) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3746](https://github.com/CrocSwap/integer-mult-bounds/pull/3746) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3747](https://github.com/CrocSwap/integer-mult-bounds/pull/3747) | Arham-Tahir64 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3748](https://github.com/CrocSwap/integer-mult-bounds/pull/3748) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3749](https://github.com/CrocSwap/integer-mult-bounds/pull/3749) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3750](https://github.com/CrocSwap/integer-mult-bounds/pull/3750) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3751](https://github.com/CrocSwap/integer-mult-bounds/pull/3751) | Arham-Tahir64 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3752](https://github.com/CrocSwap/integer-mult-bounds/pull/3752) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3753](https://github.com/CrocSwap/integer-mult-bounds/pull/3753) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3754](https://github.com/CrocSwap/integer-mult-bounds/pull/3754) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3755](https://github.com/CrocSwap/integer-mult-bounds/pull/3755) | conorholds | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3756](https://github.com/CrocSwap/integer-mult-bounds/pull/3756) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3757](https://github.com/CrocSwap/integer-mult-bounds/pull/3757) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3758](https://github.com/CrocSwap/integer-mult-bounds/pull/3758) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3759](https://github.com/CrocSwap/integer-mult-bounds/pull/3759) | Arham-Tahir64 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3760](https://github.com/CrocSwap/integer-mult-bounds/pull/3760) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3761](https://github.com/CrocSwap/integer-mult-bounds/pull/3761) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3762](https://github.com/CrocSwap/integer-mult-bounds/pull/3762) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3763](https://github.com/CrocSwap/integer-mult-bounds/pull/3763) | jmbarrancoml | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3764](https://github.com/CrocSwap/integer-mult-bounds/pull/3764) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3765](https://github.com/CrocSwap/integer-mult-bounds/pull/3765) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3766](https://github.com/CrocSwap/integer-mult-bounds/pull/3766) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3767](https://github.com/CrocSwap/integer-mult-bounds/pull/3767) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3768](https://github.com/CrocSwap/integer-mult-bounds/pull/3768) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3769](https://github.com/CrocSwap/integer-mult-bounds/pull/3769) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3770](https://github.com/CrocSwap/integer-mult-bounds/pull/3770) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3771](https://github.com/CrocSwap/integer-mult-bounds/pull/3771) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3772](https://github.com/CrocSwap/integer-mult-bounds/pull/3772) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3773](https://github.com/CrocSwap/integer-mult-bounds/pull/3773) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3774](https://github.com/CrocSwap/integer-mult-bounds/pull/3774) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3775](https://github.com/CrocSwap/integer-mult-bounds/pull/3775) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3776](https://github.com/CrocSwap/integer-mult-bounds/pull/3776) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3777](https://github.com/CrocSwap/integer-mult-bounds/pull/3777) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3778](https://github.com/CrocSwap/integer-mult-bounds/pull/3778) | yzhouwang | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3779](https://github.com/CrocSwap/integer-mult-bounds/pull/3779) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3780](https://github.com/CrocSwap/integer-mult-bounds/pull/3780) | nightangelflowerwin-ops | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3781](https://github.com/CrocSwap/integer-mult-bounds/pull/3781) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3782](https://github.com/CrocSwap/integer-mult-bounds/pull/3782) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3783](https://github.com/CrocSwap/integer-mult-bounds/pull/3783) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3784](https://github.com/CrocSwap/integer-mult-bounds/pull/3784) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3785](https://github.com/CrocSwap/integer-mult-bounds/pull/3785) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3786](https://github.com/CrocSwap/integer-mult-bounds/pull/3786) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3787](https://github.com/CrocSwap/integer-mult-bounds/pull/3787) | jmbarrancoml | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3788](https://github.com/CrocSwap/integer-mult-bounds/pull/3788) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3789](https://github.com/CrocSwap/integer-mult-bounds/pull/3789) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3790](https://github.com/CrocSwap/integer-mult-bounds/pull/3790) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3791](https://github.com/CrocSwap/integer-mult-bounds/pull/3791) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3792](https://github.com/CrocSwap/integer-mult-bounds/pull/3792) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3793](https://github.com/CrocSwap/integer-mult-bounds/pull/3793) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3794](https://github.com/CrocSwap/integer-mult-bounds/pull/3794) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3795](https://github.com/CrocSwap/integer-mult-bounds/pull/3795) | hexapode | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3796](https://github.com/CrocSwap/integer-mult-bounds/pull/3796) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3797](https://github.com/CrocSwap/integer-mult-bounds/pull/3797) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3798](https://github.com/CrocSwap/integer-mult-bounds/pull/3798) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3799](https://github.com/CrocSwap/integer-mult-bounds/pull/3799) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3800](https://github.com/CrocSwap/integer-mult-bounds/pull/3800) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3801](https://github.com/CrocSwap/integer-mult-bounds/pull/3801) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3802](https://github.com/CrocSwap/integer-mult-bounds/pull/3802) | hexapode | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3803](https://github.com/CrocSwap/integer-mult-bounds/pull/3803) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3804](https://github.com/CrocSwap/integer-mult-bounds/pull/3804) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3805](https://github.com/CrocSwap/integer-mult-bounds/pull/3805) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3806](https://github.com/CrocSwap/integer-mult-bounds/pull/3806) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3807](https://github.com/CrocSwap/integer-mult-bounds/pull/3807) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3808](https://github.com/CrocSwap/integer-mult-bounds/pull/3808) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3809](https://github.com/CrocSwap/integer-mult-bounds/pull/3809) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3810](https://github.com/CrocSwap/integer-mult-bounds/pull/3810) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3811](https://github.com/CrocSwap/integer-mult-bounds/pull/3811) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3812](https://github.com/CrocSwap/integer-mult-bounds/pull/3812) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3813](https://github.com/CrocSwap/integer-mult-bounds/pull/3813) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3814](https://github.com/CrocSwap/integer-mult-bounds/pull/3814) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3815](https://github.com/CrocSwap/integer-mult-bounds/pull/3815) | ChaloupeMusic | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3816](https://github.com/CrocSwap/integer-mult-bounds/pull/3816) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3817](https://github.com/CrocSwap/integer-mult-bounds/pull/3817) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3818](https://github.com/CrocSwap/integer-mult-bounds/pull/3818) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3819](https://github.com/CrocSwap/integer-mult-bounds/pull/3819) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3820](https://github.com/CrocSwap/integer-mult-bounds/pull/3820) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3821](https://github.com/CrocSwap/integer-mult-bounds/pull/3821) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3822](https://github.com/CrocSwap/integer-mult-bounds/pull/3822) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3823](https://github.com/CrocSwap/integer-mult-bounds/pull/3823) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3824](https://github.com/CrocSwap/integer-mult-bounds/pull/3824) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3825](https://github.com/CrocSwap/integer-mult-bounds/pull/3825) | Matarener | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3826](https://github.com/CrocSwap/integer-mult-bounds/pull/3826) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3827](https://github.com/CrocSwap/integer-mult-bounds/pull/3827) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3828](https://github.com/CrocSwap/integer-mult-bounds/pull/3828) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3829](https://github.com/CrocSwap/integer-mult-bounds/pull/3829) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3830](https://github.com/CrocSwap/integer-mult-bounds/pull/3830) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3831](https://github.com/CrocSwap/integer-mult-bounds/pull/3831) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3832](https://github.com/CrocSwap/integer-mult-bounds/pull/3832) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3833](https://github.com/CrocSwap/integer-mult-bounds/pull/3833) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3834](https://github.com/CrocSwap/integer-mult-bounds/pull/3834) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3835](https://github.com/CrocSwap/integer-mult-bounds/pull/3835) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3836](https://github.com/CrocSwap/integer-mult-bounds/pull/3836) | Matarener | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3837](https://github.com/CrocSwap/integer-mult-bounds/pull/3837) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3838](https://github.com/CrocSwap/integer-mult-bounds/pull/3838) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3839](https://github.com/CrocSwap/integer-mult-bounds/pull/3839) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3840](https://github.com/CrocSwap/integer-mult-bounds/pull/3840) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3841](https://github.com/CrocSwap/integer-mult-bounds/pull/3841) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3842](https://github.com/CrocSwap/integer-mult-bounds/pull/3842) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3843](https://github.com/CrocSwap/integer-mult-bounds/pull/3843) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3844](https://github.com/CrocSwap/integer-mult-bounds/pull/3844) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3845](https://github.com/CrocSwap/integer-mult-bounds/pull/3845) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3846](https://github.com/CrocSwap/integer-mult-bounds/pull/3846) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3847](https://github.com/CrocSwap/integer-mult-bounds/pull/3847) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3848](https://github.com/CrocSwap/integer-mult-bounds/pull/3848) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3849](https://github.com/CrocSwap/integer-mult-bounds/pull/3849) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3850](https://github.com/CrocSwap/integer-mult-bounds/pull/3850) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3851](https://github.com/CrocSwap/integer-mult-bounds/pull/3851) | jmbarrancoml | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3852](https://github.com/CrocSwap/integer-mult-bounds/pull/3852) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3853](https://github.com/CrocSwap/integer-mult-bounds/pull/3853) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3854](https://github.com/CrocSwap/integer-mult-bounds/pull/3854) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3855](https://github.com/CrocSwap/integer-mult-bounds/pull/3855) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3856](https://github.com/CrocSwap/integer-mult-bounds/pull/3856) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3857](https://github.com/CrocSwap/integer-mult-bounds/pull/3857) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3858](https://github.com/CrocSwap/integer-mult-bounds/pull/3858) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3859](https://github.com/CrocSwap/integer-mult-bounds/pull/3859) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3860](https://github.com/CrocSwap/integer-mult-bounds/pull/3860) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3861](https://github.com/CrocSwap/integer-mult-bounds/pull/3861) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3862](https://github.com/CrocSwap/integer-mult-bounds/pull/3862) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3863](https://github.com/CrocSwap/integer-mult-bounds/pull/3863) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3864](https://github.com/CrocSwap/integer-mult-bounds/pull/3864) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3865](https://github.com/CrocSwap/integer-mult-bounds/pull/3865) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3866](https://github.com/CrocSwap/integer-mult-bounds/pull/3866) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3867](https://github.com/CrocSwap/integer-mult-bounds/pull/3867) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3868](https://github.com/CrocSwap/integer-mult-bounds/pull/3868) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3869](https://github.com/CrocSwap/integer-mult-bounds/pull/3869) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3870](https://github.com/CrocSwap/integer-mult-bounds/pull/3870) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3871](https://github.com/CrocSwap/integer-mult-bounds/pull/3871) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3872](https://github.com/CrocSwap/integer-mult-bounds/pull/3872) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3873](https://github.com/CrocSwap/integer-mult-bounds/pull/3873) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3874](https://github.com/CrocSwap/integer-mult-bounds/pull/3874) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3875](https://github.com/CrocSwap/integer-mult-bounds/pull/3875) | hexapode | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3876](https://github.com/CrocSwap/integer-mult-bounds/pull/3876) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3877](https://github.com/CrocSwap/integer-mult-bounds/pull/3877) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3878](https://github.com/CrocSwap/integer-mult-bounds/pull/3878) | jmbarrancoml | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3879](https://github.com/CrocSwap/integer-mult-bounds/pull/3879) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3880](https://github.com/CrocSwap/integer-mult-bounds/pull/3880) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3881](https://github.com/CrocSwap/integer-mult-bounds/pull/3881) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3882](https://github.com/CrocSwap/integer-mult-bounds/pull/3882) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3883](https://github.com/CrocSwap/integer-mult-bounds/pull/3883) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3884](https://github.com/CrocSwap/integer-mult-bounds/pull/3884) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3885](https://github.com/CrocSwap/integer-mult-bounds/pull/3885) | Clear1nsight | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3886](https://github.com/CrocSwap/integer-mult-bounds/pull/3886) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3887](https://github.com/CrocSwap/integer-mult-bounds/pull/3887) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3888](https://github.com/CrocSwap/integer-mult-bounds/pull/3888) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3889](https://github.com/CrocSwap/integer-mult-bounds/pull/3889) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3890](https://github.com/CrocSwap/integer-mult-bounds/pull/3890) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3926](https://github.com/CrocSwap/integer-mult-bounds/pull/3926) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3928](https://github.com/CrocSwap/integer-mult-bounds/pull/3928) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3929](https://github.com/CrocSwap/integer-mult-bounds/pull/3929) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3931](https://github.com/CrocSwap/integer-mult-bounds/pull/3931) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3932](https://github.com/CrocSwap/integer-mult-bounds/pull/3932) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3933](https://github.com/CrocSwap/integer-mult-bounds/pull/3933) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3935](https://github.com/CrocSwap/integer-mult-bounds/pull/3935) | jmbarrancoml | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3936](https://github.com/CrocSwap/integer-mult-bounds/pull/3936) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3937](https://github.com/CrocSwap/integer-mult-bounds/pull/3937) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3938](https://github.com/CrocSwap/integer-mult-bounds/pull/3938) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3940](https://github.com/CrocSwap/integer-mult-bounds/pull/3940) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3941](https://github.com/CrocSwap/integer-mult-bounds/pull/3941) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3942](https://github.com/CrocSwap/integer-mult-bounds/pull/3942) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3943](https://github.com/CrocSwap/integer-mult-bounds/pull/3943) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3944](https://github.com/CrocSwap/integer-mult-bounds/pull/3944) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3945](https://github.com/CrocSwap/integer-mult-bounds/pull/3945) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3946](https://github.com/CrocSwap/integer-mult-bounds/pull/3946) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3947](https://github.com/CrocSwap/integer-mult-bounds/pull/3947) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3948](https://github.com/CrocSwap/integer-mult-bounds/pull/3948) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3949](https://github.com/CrocSwap/integer-mult-bounds/pull/3949) | ChaloupeMusic | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3950](https://github.com/CrocSwap/integer-mult-bounds/pull/3950) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3951](https://github.com/CrocSwap/integer-mult-bounds/pull/3951) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3952](https://github.com/CrocSwap/integer-mult-bounds/pull/3952) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3953](https://github.com/CrocSwap/integer-mult-bounds/pull/3953) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3954](https://github.com/CrocSwap/integer-mult-bounds/pull/3954) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3956](https://github.com/CrocSwap/integer-mult-bounds/pull/3956) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3957](https://github.com/CrocSwap/integer-mult-bounds/pull/3957) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3960](https://github.com/CrocSwap/integer-mult-bounds/pull/3960) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3961](https://github.com/CrocSwap/integer-mult-bounds/pull/3961) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3962](https://github.com/CrocSwap/integer-mult-bounds/pull/3962) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3963](https://github.com/CrocSwap/integer-mult-bounds/pull/3963) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3964](https://github.com/CrocSwap/integer-mult-bounds/pull/3964) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3965](https://github.com/CrocSwap/integer-mult-bounds/pull/3965) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3966](https://github.com/CrocSwap/integer-mult-bounds/pull/3966) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3967](https://github.com/CrocSwap/integer-mult-bounds/pull/3967) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3968](https://github.com/CrocSwap/integer-mult-bounds/pull/3968) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3969](https://github.com/CrocSwap/integer-mult-bounds/pull/3969) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3970](https://github.com/CrocSwap/integer-mult-bounds/pull/3970) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3971](https://github.com/CrocSwap/integer-mult-bounds/pull/3971) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3972](https://github.com/CrocSwap/integer-mult-bounds/pull/3972) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3973](https://github.com/CrocSwap/integer-mult-bounds/pull/3973) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3974](https://github.com/CrocSwap/integer-mult-bounds/pull/3974) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3975](https://github.com/CrocSwap/integer-mult-bounds/pull/3975) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3976](https://github.com/CrocSwap/integer-mult-bounds/pull/3976) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3977](https://github.com/CrocSwap/integer-mult-bounds/pull/3977) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3978](https://github.com/CrocSwap/integer-mult-bounds/pull/3978) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3979](https://github.com/CrocSwap/integer-mult-bounds/pull/3979) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3980](https://github.com/CrocSwap/integer-mult-bounds/pull/3980) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3981](https://github.com/CrocSwap/integer-mult-bounds/pull/3981) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3982](https://github.com/CrocSwap/integer-mult-bounds/pull/3982) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3983](https://github.com/CrocSwap/integer-mult-bounds/pull/3983) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3984](https://github.com/CrocSwap/integer-mult-bounds/pull/3984) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3985](https://github.com/CrocSwap/integer-mult-bounds/pull/3985) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3986](https://github.com/CrocSwap/integer-mult-bounds/pull/3986) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3987](https://github.com/CrocSwap/integer-mult-bounds/pull/3987) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3988](https://github.com/CrocSwap/integer-mult-bounds/pull/3988) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3989](https://github.com/CrocSwap/integer-mult-bounds/pull/3989) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3990](https://github.com/CrocSwap/integer-mult-bounds/pull/3990) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3991](https://github.com/CrocSwap/integer-mult-bounds/pull/3991) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3992](https://github.com/CrocSwap/integer-mult-bounds/pull/3992) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3993](https://github.com/CrocSwap/integer-mult-bounds/pull/3993) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3994](https://github.com/CrocSwap/integer-mult-bounds/pull/3994) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3995](https://github.com/CrocSwap/integer-mult-bounds/pull/3995) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3996](https://github.com/CrocSwap/integer-mult-bounds/pull/3996) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3997](https://github.com/CrocSwap/integer-mult-bounds/pull/3997) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3998](https://github.com/CrocSwap/integer-mult-bounds/pull/3998) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#3999](https://github.com/CrocSwap/integer-mult-bounds/pull/3999) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4000](https://github.com/CrocSwap/integer-mult-bounds/pull/4000) | tekuuu | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4001](https://github.com/CrocSwap/integer-mult-bounds/pull/4001) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4002](https://github.com/CrocSwap/integer-mult-bounds/pull/4002) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4003](https://github.com/CrocSwap/integer-mult-bounds/pull/4003) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4004](https://github.com/CrocSwap/integer-mult-bounds/pull/4004) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4005](https://github.com/CrocSwap/integer-mult-bounds/pull/4005) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4006](https://github.com/CrocSwap/integer-mult-bounds/pull/4006) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4007](https://github.com/CrocSwap/integer-mult-bounds/pull/4007) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4008](https://github.com/CrocSwap/integer-mult-bounds/pull/4008) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4009](https://github.com/CrocSwap/integer-mult-bounds/pull/4009) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4010](https://github.com/CrocSwap/integer-mult-bounds/pull/4010) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4011](https://github.com/CrocSwap/integer-mult-bounds/pull/4011) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4012](https://github.com/CrocSwap/integer-mult-bounds/pull/4012) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4013](https://github.com/CrocSwap/integer-mult-bounds/pull/4013) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4014](https://github.com/CrocSwap/integer-mult-bounds/pull/4014) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4015](https://github.com/CrocSwap/integer-mult-bounds/pull/4015) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4016](https://github.com/CrocSwap/integer-mult-bounds/pull/4016) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4017](https://github.com/CrocSwap/integer-mult-bounds/pull/4017) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4018](https://github.com/CrocSwap/integer-mult-bounds/pull/4018) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4019](https://github.com/CrocSwap/integer-mult-bounds/pull/4019) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4020](https://github.com/CrocSwap/integer-mult-bounds/pull/4020) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4021](https://github.com/CrocSwap/integer-mult-bounds/pull/4021) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4022](https://github.com/CrocSwap/integer-mult-bounds/pull/4022) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4023](https://github.com/CrocSwap/integer-mult-bounds/pull/4023) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4024](https://github.com/CrocSwap/integer-mult-bounds/pull/4024) | tekuuu | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4025](https://github.com/CrocSwap/integer-mult-bounds/pull/4025) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4026](https://github.com/CrocSwap/integer-mult-bounds/pull/4026) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4027](https://github.com/CrocSwap/integer-mult-bounds/pull/4027) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4028](https://github.com/CrocSwap/integer-mult-bounds/pull/4028) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4029](https://github.com/CrocSwap/integer-mult-bounds/pull/4029) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4030](https://github.com/CrocSwap/integer-mult-bounds/pull/4030) | tekuuu | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4031](https://github.com/CrocSwap/integer-mult-bounds/pull/4031) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4032](https://github.com/CrocSwap/integer-mult-bounds/pull/4032) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4033](https://github.com/CrocSwap/integer-mult-bounds/pull/4033) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4034](https://github.com/CrocSwap/integer-mult-bounds/pull/4034) | Gonzalo-Mier | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4035](https://github.com/CrocSwap/integer-mult-bounds/pull/4035) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4036](https://github.com/CrocSwap/integer-mult-bounds/pull/4036) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4037](https://github.com/CrocSwap/integer-mult-bounds/pull/4037) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4039](https://github.com/CrocSwap/integer-mult-bounds/pull/4039) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4040](https://github.com/CrocSwap/integer-mult-bounds/pull/4040) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4041](https://github.com/CrocSwap/integer-mult-bounds/pull/4041) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4042](https://github.com/CrocSwap/integer-mult-bounds/pull/4042) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4043](https://github.com/CrocSwap/integer-mult-bounds/pull/4043) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4044](https://github.com/CrocSwap/integer-mult-bounds/pull/4044) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4045](https://github.com/CrocSwap/integer-mult-bounds/pull/4045) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4046](https://github.com/CrocSwap/integer-mult-bounds/pull/4046) | ChaloupeMusic | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4047](https://github.com/CrocSwap/integer-mult-bounds/pull/4047) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4048](https://github.com/CrocSwap/integer-mult-bounds/pull/4048) | tekuuu | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4049](https://github.com/CrocSwap/integer-mult-bounds/pull/4049) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4050](https://github.com/CrocSwap/integer-mult-bounds/pull/4050) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4051](https://github.com/CrocSwap/integer-mult-bounds/pull/4051) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4052](https://github.com/CrocSwap/integer-mult-bounds/pull/4052) | conorholds | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4053](https://github.com/CrocSwap/integer-mult-bounds/pull/4053) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4054](https://github.com/CrocSwap/integer-mult-bounds/pull/4054) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4055](https://github.com/CrocSwap/integer-mult-bounds/pull/4055) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4056](https://github.com/CrocSwap/integer-mult-bounds/pull/4056) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4057](https://github.com/CrocSwap/integer-mult-bounds/pull/4057) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4058](https://github.com/CrocSwap/integer-mult-bounds/pull/4058) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4059](https://github.com/CrocSwap/integer-mult-bounds/pull/4059) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4061](https://github.com/CrocSwap/integer-mult-bounds/pull/4061) | hevlyo | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4062](https://github.com/CrocSwap/integer-mult-bounds/pull/4062) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4063](https://github.com/CrocSwap/integer-mult-bounds/pull/4063) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4064](https://github.com/CrocSwap/integer-mult-bounds/pull/4064) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4066](https://github.com/CrocSwap/integer-mult-bounds/pull/4066) | hevlyo | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4067](https://github.com/CrocSwap/integer-mult-bounds/pull/4067) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4068](https://github.com/CrocSwap/integer-mult-bounds/pull/4068) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4069](https://github.com/CrocSwap/integer-mult-bounds/pull/4069) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4070](https://github.com/CrocSwap/integer-mult-bounds/pull/4070) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4071](https://github.com/CrocSwap/integer-mult-bounds/pull/4071) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4072](https://github.com/CrocSwap/integer-mult-bounds/pull/4072) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4073](https://github.com/CrocSwap/integer-mult-bounds/pull/4073) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4074](https://github.com/CrocSwap/integer-mult-bounds/pull/4074) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4075](https://github.com/CrocSwap/integer-mult-bounds/pull/4075) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4076](https://github.com/CrocSwap/integer-mult-bounds/pull/4076) | rohanarun | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4077](https://github.com/CrocSwap/integer-mult-bounds/pull/4077) | tekuuu | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4078](https://github.com/CrocSwap/integer-mult-bounds/pull/4078) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4079](https://github.com/CrocSwap/integer-mult-bounds/pull/4079) | nightangelflowerwin-ops | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4080](https://github.com/CrocSwap/integer-mult-bounds/pull/4080) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4081](https://github.com/CrocSwap/integer-mult-bounds/pull/4081) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4082](https://github.com/CrocSwap/integer-mult-bounds/pull/4082) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4083](https://github.com/CrocSwap/integer-mult-bounds/pull/4083) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4084](https://github.com/CrocSwap/integer-mult-bounds/pull/4084) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4085](https://github.com/CrocSwap/integer-mult-bounds/pull/4085) | zxv | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4086](https://github.com/CrocSwap/integer-mult-bounds/pull/4086) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4087](https://github.com/CrocSwap/integer-mult-bounds/pull/4087) | tekuuu | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4088](https://github.com/CrocSwap/integer-mult-bounds/pull/4088) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4089](https://github.com/CrocSwap/integer-mult-bounds/pull/4089) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4090](https://github.com/CrocSwap/integer-mult-bounds/pull/4090) | kumagi | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4091](https://github.com/CrocSwap/integer-mult-bounds/pull/4091) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4092](https://github.com/CrocSwap/integer-mult-bounds/pull/4092) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4093](https://github.com/CrocSwap/integer-mult-bounds/pull/4093) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4094](https://github.com/CrocSwap/integer-mult-bounds/pull/4094) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4095](https://github.com/CrocSwap/integer-mult-bounds/pull/4095) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4096](https://github.com/CrocSwap/integer-mult-bounds/pull/4096) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4097](https://github.com/CrocSwap/integer-mult-bounds/pull/4097) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4098](https://github.com/CrocSwap/integer-mult-bounds/pull/4098) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4099](https://github.com/CrocSwap/integer-mult-bounds/pull/4099) | VictorLiwentao | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4100](https://github.com/CrocSwap/integer-mult-bounds/pull/4100) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4101](https://github.com/CrocSwap/integer-mult-bounds/pull/4101) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4104](https://github.com/CrocSwap/integer-mult-bounds/pull/4104) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4105](https://github.com/CrocSwap/integer-mult-bounds/pull/4105) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4106](https://github.com/CrocSwap/integer-mult-bounds/pull/4106) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4107](https://github.com/CrocSwap/integer-mult-bounds/pull/4107) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4108](https://github.com/CrocSwap/integer-mult-bounds/pull/4108) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4109](https://github.com/CrocSwap/integer-mult-bounds/pull/4109) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4110](https://github.com/CrocSwap/integer-mult-bounds/pull/4110) | kumagi | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4112](https://github.com/CrocSwap/integer-mult-bounds/pull/4112) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4113](https://github.com/CrocSwap/integer-mult-bounds/pull/4113) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4114](https://github.com/CrocSwap/integer-mult-bounds/pull/4114) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4115](https://github.com/CrocSwap/integer-mult-bounds/pull/4115) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4116](https://github.com/CrocSwap/integer-mult-bounds/pull/4116) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4117](https://github.com/CrocSwap/integer-mult-bounds/pull/4117) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4118](https://github.com/CrocSwap/integer-mult-bounds/pull/4118) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4119](https://github.com/CrocSwap/integer-mult-bounds/pull/4119) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4120](https://github.com/CrocSwap/integer-mult-bounds/pull/4120) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4121](https://github.com/CrocSwap/integer-mult-bounds/pull/4121) | GamingPuzzled | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4122](https://github.com/CrocSwap/integer-mult-bounds/pull/4122) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4123](https://github.com/CrocSwap/integer-mult-bounds/pull/4123) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4124](https://github.com/CrocSwap/integer-mult-bounds/pull/4124) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4125](https://github.com/CrocSwap/integer-mult-bounds/pull/4125) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4126](https://github.com/CrocSwap/integer-mult-bounds/pull/4126) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4127](https://github.com/CrocSwap/integer-mult-bounds/pull/4127) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4128](https://github.com/CrocSwap/integer-mult-bounds/pull/4128) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4129](https://github.com/CrocSwap/integer-mult-bounds/pull/4129) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4130](https://github.com/CrocSwap/integer-mult-bounds/pull/4130) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4131](https://github.com/CrocSwap/integer-mult-bounds/pull/4131) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4132](https://github.com/CrocSwap/integer-mult-bounds/pull/4132) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4133](https://github.com/CrocSwap/integer-mult-bounds/pull/4133) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4134](https://github.com/CrocSwap/integer-mult-bounds/pull/4134) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4135](https://github.com/CrocSwap/integer-mult-bounds/pull/4135) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4136](https://github.com/CrocSwap/integer-mult-bounds/pull/4136) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4137](https://github.com/CrocSwap/integer-mult-bounds/pull/4137) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4138](https://github.com/CrocSwap/integer-mult-bounds/pull/4138) | unpaidmoon | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4139](https://github.com/CrocSwap/integer-mult-bounds/pull/4139) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4140](https://github.com/CrocSwap/integer-mult-bounds/pull/4140) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4141](https://github.com/CrocSwap/integer-mult-bounds/pull/4141) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4142](https://github.com/CrocSwap/integer-mult-bounds/pull/4142) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4143](https://github.com/CrocSwap/integer-mult-bounds/pull/4143) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4144](https://github.com/CrocSwap/integer-mult-bounds/pull/4144) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4145](https://github.com/CrocSwap/integer-mult-bounds/pull/4145) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4146](https://github.com/CrocSwap/integer-mult-bounds/pull/4146) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4147](https://github.com/CrocSwap/integer-mult-bounds/pull/4147) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4148](https://github.com/CrocSwap/integer-mult-bounds/pull/4148) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4149](https://github.com/CrocSwap/integer-mult-bounds/pull/4149) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4150](https://github.com/CrocSwap/integer-mult-bounds/pull/4150) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4151](https://github.com/CrocSwap/integer-mult-bounds/pull/4151) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4152](https://github.com/CrocSwap/integer-mult-bounds/pull/4152) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4153](https://github.com/CrocSwap/integer-mult-bounds/pull/4153) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4154](https://github.com/CrocSwap/integer-mult-bounds/pull/4154) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4155](https://github.com/CrocSwap/integer-mult-bounds/pull/4155) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4156](https://github.com/CrocSwap/integer-mult-bounds/pull/4156) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4157](https://github.com/CrocSwap/integer-mult-bounds/pull/4157) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4158](https://github.com/CrocSwap/integer-mult-bounds/pull/4158) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4159](https://github.com/CrocSwap/integer-mult-bounds/pull/4159) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4160](https://github.com/CrocSwap/integer-mult-bounds/pull/4160) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4161](https://github.com/CrocSwap/integer-mult-bounds/pull/4161) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4162](https://github.com/CrocSwap/integer-mult-bounds/pull/4162) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4163](https://github.com/CrocSwap/integer-mult-bounds/pull/4163) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4164](https://github.com/CrocSwap/integer-mult-bounds/pull/4164) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4165](https://github.com/CrocSwap/integer-mult-bounds/pull/4165) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4166](https://github.com/CrocSwap/integer-mult-bounds/pull/4166) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4167](https://github.com/CrocSwap/integer-mult-bounds/pull/4167) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4169](https://github.com/CrocSwap/integer-mult-bounds/pull/4169) | kumagi | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4170](https://github.com/CrocSwap/integer-mult-bounds/pull/4170) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4171](https://github.com/CrocSwap/integer-mult-bounds/pull/4171) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4172](https://github.com/CrocSwap/integer-mult-bounds/pull/4172) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4174](https://github.com/CrocSwap/integer-mult-bounds/pull/4174) | kumagi | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4176](https://github.com/CrocSwap/integer-mult-bounds/pull/4176) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4177](https://github.com/CrocSwap/integer-mult-bounds/pull/4177) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4178](https://github.com/CrocSwap/integer-mult-bounds/pull/4178) | jmbarrancoml | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4179](https://github.com/CrocSwap/integer-mult-bounds/pull/4179) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4180](https://github.com/CrocSwap/integer-mult-bounds/pull/4180) | yssite | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4181](https://github.com/CrocSwap/integer-mult-bounds/pull/4181) | rohanarun | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4183](https://github.com/CrocSwap/integer-mult-bounds/pull/4183) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4184](https://github.com/CrocSwap/integer-mult-bounds/pull/4184) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4185](https://github.com/CrocSwap/integer-mult-bounds/pull/4185) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4186](https://github.com/CrocSwap/integer-mult-bounds/pull/4186) | jmbarrancoml | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4187](https://github.com/CrocSwap/integer-mult-bounds/pull/4187) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4189](https://github.com/CrocSwap/integer-mult-bounds/pull/4189) | hevlyo | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4190](https://github.com/CrocSwap/integer-mult-bounds/pull/4190) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4192](https://github.com/CrocSwap/integer-mult-bounds/pull/4192) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4193](https://github.com/CrocSwap/integer-mult-bounds/pull/4193) | jmbarrancoml | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4194](https://github.com/CrocSwap/integer-mult-bounds/pull/4194) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4195](https://github.com/CrocSwap/integer-mult-bounds/pull/4195) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4197](https://github.com/CrocSwap/integer-mult-bounds/pull/4197) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4198](https://github.com/CrocSwap/integer-mult-bounds/pull/4198) | jmbarrancoml | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4200](https://github.com/CrocSwap/integer-mult-bounds/pull/4200) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4201](https://github.com/CrocSwap/integer-mult-bounds/pull/4201) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4203](https://github.com/CrocSwap/integer-mult-bounds/pull/4203) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4204](https://github.com/CrocSwap/integer-mult-bounds/pull/4204) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4205](https://github.com/CrocSwap/integer-mult-bounds/pull/4205) | jmbarrancoml | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4206](https://github.com/CrocSwap/integer-mult-bounds/pull/4206) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4207](https://github.com/CrocSwap/integer-mult-bounds/pull/4207) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4208](https://github.com/CrocSwap/integer-mult-bounds/pull/4208) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4209](https://github.com/CrocSwap/integer-mult-bounds/pull/4209) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4210](https://github.com/CrocSwap/integer-mult-bounds/pull/4210) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4211](https://github.com/CrocSwap/integer-mult-bounds/pull/4211) | brianross93 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4212](https://github.com/CrocSwap/integer-mult-bounds/pull/4212) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4214](https://github.com/CrocSwap/integer-mult-bounds/pull/4214) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4215](https://github.com/CrocSwap/integer-mult-bounds/pull/4215) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4216](https://github.com/CrocSwap/integer-mult-bounds/pull/4216) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4217](https://github.com/CrocSwap/integer-mult-bounds/pull/4217) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4218](https://github.com/CrocSwap/integer-mult-bounds/pull/4218) | thu-nmrc | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4219](https://github.com/CrocSwap/integer-mult-bounds/pull/4219) | conorholds | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4220](https://github.com/CrocSwap/integer-mult-bounds/pull/4220) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4221](https://github.com/CrocSwap/integer-mult-bounds/pull/4221) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4223](https://github.com/CrocSwap/integer-mult-bounds/pull/4223) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4225](https://github.com/CrocSwap/integer-mult-bounds/pull/4225) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4227](https://github.com/CrocSwap/integer-mult-bounds/pull/4227) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4228](https://github.com/CrocSwap/integer-mult-bounds/pull/4228) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4230](https://github.com/CrocSwap/integer-mult-bounds/pull/4230) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4231](https://github.com/CrocSwap/integer-mult-bounds/pull/4231) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4232](https://github.com/CrocSwap/integer-mult-bounds/pull/4232) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4233](https://github.com/CrocSwap/integer-mult-bounds/pull/4233) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4234](https://github.com/CrocSwap/integer-mult-bounds/pull/4234) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4235](https://github.com/CrocSwap/integer-mult-bounds/pull/4235) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4236](https://github.com/CrocSwap/integer-mult-bounds/pull/4236) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4237](https://github.com/CrocSwap/integer-mult-bounds/pull/4237) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4238](https://github.com/CrocSwap/integer-mult-bounds/pull/4238) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4239](https://github.com/CrocSwap/integer-mult-bounds/pull/4239) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4240](https://github.com/CrocSwap/integer-mult-bounds/pull/4240) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4241](https://github.com/CrocSwap/integer-mult-bounds/pull/4241) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4242](https://github.com/CrocSwap/integer-mult-bounds/pull/4242) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4243](https://github.com/CrocSwap/integer-mult-bounds/pull/4243) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4244](https://github.com/CrocSwap/integer-mult-bounds/pull/4244) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4245](https://github.com/CrocSwap/integer-mult-bounds/pull/4245) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4246](https://github.com/CrocSwap/integer-mult-bounds/pull/4246) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4247](https://github.com/CrocSwap/integer-mult-bounds/pull/4247) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4248](https://github.com/CrocSwap/integer-mult-bounds/pull/4248) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4249](https://github.com/CrocSwap/integer-mult-bounds/pull/4249) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4250](https://github.com/CrocSwap/integer-mult-bounds/pull/4250) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4251](https://github.com/CrocSwap/integer-mult-bounds/pull/4251) | flyingviper | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4252](https://github.com/CrocSwap/integer-mult-bounds/pull/4252) | flyingviper | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4253](https://github.com/CrocSwap/integer-mult-bounds/pull/4253) | jmbarrancoml | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4254](https://github.com/CrocSwap/integer-mult-bounds/pull/4254) | flyingviper | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4255](https://github.com/CrocSwap/integer-mult-bounds/pull/4255) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4256](https://github.com/CrocSwap/integer-mult-bounds/pull/4256) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4257](https://github.com/CrocSwap/integer-mult-bounds/pull/4257) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4258](https://github.com/CrocSwap/integer-mult-bounds/pull/4258) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4259](https://github.com/CrocSwap/integer-mult-bounds/pull/4259) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4260](https://github.com/CrocSwap/integer-mult-bounds/pull/4260) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4261](https://github.com/CrocSwap/integer-mult-bounds/pull/4261) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4262](https://github.com/CrocSwap/integer-mult-bounds/pull/4262) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4263](https://github.com/CrocSwap/integer-mult-bounds/pull/4263) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4264](https://github.com/CrocSwap/integer-mult-bounds/pull/4264) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4265](https://github.com/CrocSwap/integer-mult-bounds/pull/4265) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4266](https://github.com/CrocSwap/integer-mult-bounds/pull/4266) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4267](https://github.com/CrocSwap/integer-mult-bounds/pull/4267) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4268](https://github.com/CrocSwap/integer-mult-bounds/pull/4268) | jacobalansussman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4269](https://github.com/CrocSwap/integer-mult-bounds/pull/4269) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4270](https://github.com/CrocSwap/integer-mult-bounds/pull/4270) | RossRichardson | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4271](https://github.com/CrocSwap/integer-mult-bounds/pull/4271) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4272](https://github.com/CrocSwap/integer-mult-bounds/pull/4272) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4273](https://github.com/CrocSwap/integer-mult-bounds/pull/4273) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4274](https://github.com/CrocSwap/integer-mult-bounds/pull/4274) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4275](https://github.com/CrocSwap/integer-mult-bounds/pull/4275) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4276](https://github.com/CrocSwap/integer-mult-bounds/pull/4276) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4277](https://github.com/CrocSwap/integer-mult-bounds/pull/4277) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4278](https://github.com/CrocSwap/integer-mult-bounds/pull/4278) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4279](https://github.com/CrocSwap/integer-mult-bounds/pull/4279) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4280](https://github.com/CrocSwap/integer-mult-bounds/pull/4280) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4281](https://github.com/CrocSwap/integer-mult-bounds/pull/4281) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4282](https://github.com/CrocSwap/integer-mult-bounds/pull/4282) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4283](https://github.com/CrocSwap/integer-mult-bounds/pull/4283) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4284](https://github.com/CrocSwap/integer-mult-bounds/pull/4284) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4285](https://github.com/CrocSwap/integer-mult-bounds/pull/4285) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4286](https://github.com/CrocSwap/integer-mult-bounds/pull/4286) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4287](https://github.com/CrocSwap/integer-mult-bounds/pull/4287) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4288](https://github.com/CrocSwap/integer-mult-bounds/pull/4288) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4289](https://github.com/CrocSwap/integer-mult-bounds/pull/4289) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4290](https://github.com/CrocSwap/integer-mult-bounds/pull/4290) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4291](https://github.com/CrocSwap/integer-mult-bounds/pull/4291) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4292](https://github.com/CrocSwap/integer-mult-bounds/pull/4292) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4293](https://github.com/CrocSwap/integer-mult-bounds/pull/4293) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4294](https://github.com/CrocSwap/integer-mult-bounds/pull/4294) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4295](https://github.com/CrocSwap/integer-mult-bounds/pull/4295) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4296](https://github.com/CrocSwap/integer-mult-bounds/pull/4296) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4297](https://github.com/CrocSwap/integer-mult-bounds/pull/4297) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4298](https://github.com/CrocSwap/integer-mult-bounds/pull/4298) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4299](https://github.com/CrocSwap/integer-mult-bounds/pull/4299) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4300](https://github.com/CrocSwap/integer-mult-bounds/pull/4300) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4301](https://github.com/CrocSwap/integer-mult-bounds/pull/4301) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4302](https://github.com/CrocSwap/integer-mult-bounds/pull/4302) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4303](https://github.com/CrocSwap/integer-mult-bounds/pull/4303) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4304](https://github.com/CrocSwap/integer-mult-bounds/pull/4304) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4305](https://github.com/CrocSwap/integer-mult-bounds/pull/4305) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4306](https://github.com/CrocSwap/integer-mult-bounds/pull/4306) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4307](https://github.com/CrocSwap/integer-mult-bounds/pull/4307) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4308](https://github.com/CrocSwap/integer-mult-bounds/pull/4308) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4309](https://github.com/CrocSwap/integer-mult-bounds/pull/4309) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4310](https://github.com/CrocSwap/integer-mult-bounds/pull/4310) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4311](https://github.com/CrocSwap/integer-mult-bounds/pull/4311) | pinterbanget | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4312](https://github.com/CrocSwap/integer-mult-bounds/pull/4312) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4313](https://github.com/CrocSwap/integer-mult-bounds/pull/4313) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4314](https://github.com/CrocSwap/integer-mult-bounds/pull/4314) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4315](https://github.com/CrocSwap/integer-mult-bounds/pull/4315) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4316](https://github.com/CrocSwap/integer-mult-bounds/pull/4316) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4317](https://github.com/CrocSwap/integer-mult-bounds/pull/4317) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4318](https://github.com/CrocSwap/integer-mult-bounds/pull/4318) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4319](https://github.com/CrocSwap/integer-mult-bounds/pull/4319) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4320](https://github.com/CrocSwap/integer-mult-bounds/pull/4320) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4321](https://github.com/CrocSwap/integer-mult-bounds/pull/4321) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4322](https://github.com/CrocSwap/integer-mult-bounds/pull/4322) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4323](https://github.com/CrocSwap/integer-mult-bounds/pull/4323) | flyingviper | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4324](https://github.com/CrocSwap/integer-mult-bounds/pull/4324) | flyingviper | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4325](https://github.com/CrocSwap/integer-mult-bounds/pull/4325) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4326](https://github.com/CrocSwap/integer-mult-bounds/pull/4326) | ai-nanachi | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4327](https://github.com/CrocSwap/integer-mult-bounds/pull/4327) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4328](https://github.com/CrocSwap/integer-mult-bounds/pull/4328) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4329](https://github.com/CrocSwap/integer-mult-bounds/pull/4329) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4330](https://github.com/CrocSwap/integer-mult-bounds/pull/4330) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4331](https://github.com/CrocSwap/integer-mult-bounds/pull/4331) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4332](https://github.com/CrocSwap/integer-mult-bounds/pull/4332) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4334](https://github.com/CrocSwap/integer-mult-bounds/pull/4334) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4335](https://github.com/CrocSwap/integer-mult-bounds/pull/4335) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4336](https://github.com/CrocSwap/integer-mult-bounds/pull/4336) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4339](https://github.com/CrocSwap/integer-mult-bounds/pull/4339) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4340](https://github.com/CrocSwap/integer-mult-bounds/pull/4340) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4341](https://github.com/CrocSwap/integer-mult-bounds/pull/4341) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4342](https://github.com/CrocSwap/integer-mult-bounds/pull/4342) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4343](https://github.com/CrocSwap/integer-mult-bounds/pull/4343) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4344](https://github.com/CrocSwap/integer-mult-bounds/pull/4344) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4345](https://github.com/CrocSwap/integer-mult-bounds/pull/4345) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4347](https://github.com/CrocSwap/integer-mult-bounds/pull/4347) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4348](https://github.com/CrocSwap/integer-mult-bounds/pull/4348) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4349](https://github.com/CrocSwap/integer-mult-bounds/pull/4349) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4351](https://github.com/CrocSwap/integer-mult-bounds/pull/4351) | hevlyo | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4353](https://github.com/CrocSwap/integer-mult-bounds/pull/4353) | ToikY | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4354](https://github.com/CrocSwap/integer-mult-bounds/pull/4354) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4355](https://github.com/CrocSwap/integer-mult-bounds/pull/4355) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4356](https://github.com/CrocSwap/integer-mult-bounds/pull/4356) | Matarener | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4357](https://github.com/CrocSwap/integer-mult-bounds/pull/4357) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4358](https://github.com/CrocSwap/integer-mult-bounds/pull/4358) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4359](https://github.com/CrocSwap/integer-mult-bounds/pull/4359) | zxv | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4360](https://github.com/CrocSwap/integer-mult-bounds/pull/4360) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4361](https://github.com/CrocSwap/integer-mult-bounds/pull/4361) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4362](https://github.com/CrocSwap/integer-mult-bounds/pull/4362) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4363](https://github.com/CrocSwap/integer-mult-bounds/pull/4363) | rohanarun | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4364](https://github.com/CrocSwap/integer-mult-bounds/pull/4364) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4365](https://github.com/CrocSwap/integer-mult-bounds/pull/4365) | CubeJerry | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4366](https://github.com/CrocSwap/integer-mult-bounds/pull/4366) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4367](https://github.com/CrocSwap/integer-mult-bounds/pull/4367) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4368](https://github.com/CrocSwap/integer-mult-bounds/pull/4368) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4369](https://github.com/CrocSwap/integer-mult-bounds/pull/4369) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4370](https://github.com/CrocSwap/integer-mult-bounds/pull/4370) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4371](https://github.com/CrocSwap/integer-mult-bounds/pull/4371) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4372](https://github.com/CrocSwap/integer-mult-bounds/pull/4372) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4373](https://github.com/CrocSwap/integer-mult-bounds/pull/4373) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4374](https://github.com/CrocSwap/integer-mult-bounds/pull/4374) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4375](https://github.com/CrocSwap/integer-mult-bounds/pull/4375) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4376](https://github.com/CrocSwap/integer-mult-bounds/pull/4376) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4377](https://github.com/CrocSwap/integer-mult-bounds/pull/4377) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4378](https://github.com/CrocSwap/integer-mult-bounds/pull/4378) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4379](https://github.com/CrocSwap/integer-mult-bounds/pull/4379) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4380](https://github.com/CrocSwap/integer-mult-bounds/pull/4380) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4381](https://github.com/CrocSwap/integer-mult-bounds/pull/4381) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4382](https://github.com/CrocSwap/integer-mult-bounds/pull/4382) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4383](https://github.com/CrocSwap/integer-mult-bounds/pull/4383) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4384](https://github.com/CrocSwap/integer-mult-bounds/pull/4384) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4385](https://github.com/CrocSwap/integer-mult-bounds/pull/4385) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4386](https://github.com/CrocSwap/integer-mult-bounds/pull/4386) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4387](https://github.com/CrocSwap/integer-mult-bounds/pull/4387) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4388](https://github.com/CrocSwap/integer-mult-bounds/pull/4388) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4389](https://github.com/CrocSwap/integer-mult-bounds/pull/4389) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4390](https://github.com/CrocSwap/integer-mult-bounds/pull/4390) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4391](https://github.com/CrocSwap/integer-mult-bounds/pull/4391) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4392](https://github.com/CrocSwap/integer-mult-bounds/pull/4392) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4393](https://github.com/CrocSwap/integer-mult-bounds/pull/4393) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4394](https://github.com/CrocSwap/integer-mult-bounds/pull/4394) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4395](https://github.com/CrocSwap/integer-mult-bounds/pull/4395) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4396](https://github.com/CrocSwap/integer-mult-bounds/pull/4396) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4397](https://github.com/CrocSwap/integer-mult-bounds/pull/4397) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4398](https://github.com/CrocSwap/integer-mult-bounds/pull/4398) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4399](https://github.com/CrocSwap/integer-mult-bounds/pull/4399) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4400](https://github.com/CrocSwap/integer-mult-bounds/pull/4400) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4401](https://github.com/CrocSwap/integer-mult-bounds/pull/4401) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4402](https://github.com/CrocSwap/integer-mult-bounds/pull/4402) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4403](https://github.com/CrocSwap/integer-mult-bounds/pull/4403) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4404](https://github.com/CrocSwap/integer-mult-bounds/pull/4404) | pinterbanget | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4405](https://github.com/CrocSwap/integer-mult-bounds/pull/4405) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4406](https://github.com/CrocSwap/integer-mult-bounds/pull/4406) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4407](https://github.com/CrocSwap/integer-mult-bounds/pull/4407) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4408](https://github.com/CrocSwap/integer-mult-bounds/pull/4408) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4409](https://github.com/CrocSwap/integer-mult-bounds/pull/4409) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4410](https://github.com/CrocSwap/integer-mult-bounds/pull/4410) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4411](https://github.com/CrocSwap/integer-mult-bounds/pull/4411) | zxv | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4412](https://github.com/CrocSwap/integer-mult-bounds/pull/4412) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4413](https://github.com/CrocSwap/integer-mult-bounds/pull/4413) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4414](https://github.com/CrocSwap/integer-mult-bounds/pull/4414) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4415](https://github.com/CrocSwap/integer-mult-bounds/pull/4415) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4416](https://github.com/CrocSwap/integer-mult-bounds/pull/4416) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4417](https://github.com/CrocSwap/integer-mult-bounds/pull/4417) | Matarener | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4418](https://github.com/CrocSwap/integer-mult-bounds/pull/4418) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4419](https://github.com/CrocSwap/integer-mult-bounds/pull/4419) | lee-phys | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4420](https://github.com/CrocSwap/integer-mult-bounds/pull/4420) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4421](https://github.com/CrocSwap/integer-mult-bounds/pull/4421) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4422](https://github.com/CrocSwap/integer-mult-bounds/pull/4422) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4423](https://github.com/CrocSwap/integer-mult-bounds/pull/4423) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4424](https://github.com/CrocSwap/integer-mult-bounds/pull/4424) | Matarener | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4425](https://github.com/CrocSwap/integer-mult-bounds/pull/4425) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4426](https://github.com/CrocSwap/integer-mult-bounds/pull/4426) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4427](https://github.com/CrocSwap/integer-mult-bounds/pull/4427) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4428](https://github.com/CrocSwap/integer-mult-bounds/pull/4428) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4429](https://github.com/CrocSwap/integer-mult-bounds/pull/4429) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4430](https://github.com/CrocSwap/integer-mult-bounds/pull/4430) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4431](https://github.com/CrocSwap/integer-mult-bounds/pull/4431) | zxv | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4432](https://github.com/CrocSwap/integer-mult-bounds/pull/4432) | Matarener | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4433](https://github.com/CrocSwap/integer-mult-bounds/pull/4433) | zxv | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4434](https://github.com/CrocSwap/integer-mult-bounds/pull/4434) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4435](https://github.com/CrocSwap/integer-mult-bounds/pull/4435) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4436](https://github.com/CrocSwap/integer-mult-bounds/pull/4436) | zxv | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4437](https://github.com/CrocSwap/integer-mult-bounds/pull/4437) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4438](https://github.com/CrocSwap/integer-mult-bounds/pull/4438) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4439](https://github.com/CrocSwap/integer-mult-bounds/pull/4439) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4440](https://github.com/CrocSwap/integer-mult-bounds/pull/4440) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4441](https://github.com/CrocSwap/integer-mult-bounds/pull/4441) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4442](https://github.com/CrocSwap/integer-mult-bounds/pull/4442) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4446](https://github.com/CrocSwap/integer-mult-bounds/pull/4446) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4447](https://github.com/CrocSwap/integer-mult-bounds/pull/4447) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4448](https://github.com/CrocSwap/integer-mult-bounds/pull/4448) | mihir-s-05 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4449](https://github.com/CrocSwap/integer-mult-bounds/pull/4449) | mihir-s-05 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4450](https://github.com/CrocSwap/integer-mult-bounds/pull/4450) | mihir-s-05 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4451](https://github.com/CrocSwap/integer-mult-bounds/pull/4451) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4452](https://github.com/CrocSwap/integer-mult-bounds/pull/4452) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4453](https://github.com/CrocSwap/integer-mult-bounds/pull/4453) | zxv | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4454](https://github.com/CrocSwap/integer-mult-bounds/pull/4454) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4455](https://github.com/CrocSwap/integer-mult-bounds/pull/4455) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4456](https://github.com/CrocSwap/integer-mult-bounds/pull/4456) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4457](https://github.com/CrocSwap/integer-mult-bounds/pull/4457) | Matarener | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4459](https://github.com/CrocSwap/integer-mult-bounds/pull/4459) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4460](https://github.com/CrocSwap/integer-mult-bounds/pull/4460) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4462](https://github.com/CrocSwap/integer-mult-bounds/pull/4462) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4463](https://github.com/CrocSwap/integer-mult-bounds/pull/4463) | mihir-s-05 | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4464](https://github.com/CrocSwap/integer-mult-bounds/pull/4464) | mihir-s-05 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4465](https://github.com/CrocSwap/integer-mult-bounds/pull/4465) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4466](https://github.com/CrocSwap/integer-mult-bounds/pull/4466) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4467](https://github.com/CrocSwap/integer-mult-bounds/pull/4467) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4468](https://github.com/CrocSwap/integer-mult-bounds/pull/4468) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4469](https://github.com/CrocSwap/integer-mult-bounds/pull/4469) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4470](https://github.com/CrocSwap/integer-mult-bounds/pull/4470) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4471](https://github.com/CrocSwap/integer-mult-bounds/pull/4471) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4472](https://github.com/CrocSwap/integer-mult-bounds/pull/4472) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4473](https://github.com/CrocSwap/integer-mult-bounds/pull/4473) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4474](https://github.com/CrocSwap/integer-mult-bounds/pull/4474) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4475](https://github.com/CrocSwap/integer-mult-bounds/pull/4475) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4476](https://github.com/CrocSwap/integer-mult-bounds/pull/4476) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4477](https://github.com/CrocSwap/integer-mult-bounds/pull/4477) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4478](https://github.com/CrocSwap/integer-mult-bounds/pull/4478) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4479](https://github.com/CrocSwap/integer-mult-bounds/pull/4479) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4480](https://github.com/CrocSwap/integer-mult-bounds/pull/4480) | zxv | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4481](https://github.com/CrocSwap/integer-mult-bounds/pull/4481) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4482](https://github.com/CrocSwap/integer-mult-bounds/pull/4482) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4483](https://github.com/CrocSwap/integer-mult-bounds/pull/4483) | zxv | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4484](https://github.com/CrocSwap/integer-mult-bounds/pull/4484) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4485](https://github.com/CrocSwap/integer-mult-bounds/pull/4485) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4486](https://github.com/CrocSwap/integer-mult-bounds/pull/4486) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4487](https://github.com/CrocSwap/integer-mult-bounds/pull/4487) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4488](https://github.com/CrocSwap/integer-mult-bounds/pull/4488) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4489](https://github.com/CrocSwap/integer-mult-bounds/pull/4489) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4490](https://github.com/CrocSwap/integer-mult-bounds/pull/4490) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4491](https://github.com/CrocSwap/integer-mult-bounds/pull/4491) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4492](https://github.com/CrocSwap/integer-mult-bounds/pull/4492) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4493](https://github.com/CrocSwap/integer-mult-bounds/pull/4493) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4494](https://github.com/CrocSwap/integer-mult-bounds/pull/4494) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4495](https://github.com/CrocSwap/integer-mult-bounds/pull/4495) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4496](https://github.com/CrocSwap/integer-mult-bounds/pull/4496) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4497](https://github.com/CrocSwap/integer-mult-bounds/pull/4497) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4499](https://github.com/CrocSwap/integer-mult-bounds/pull/4499) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4501](https://github.com/CrocSwap/integer-mult-bounds/pull/4501) | mihir-s-05 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4502](https://github.com/CrocSwap/integer-mult-bounds/pull/4502) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4504](https://github.com/CrocSwap/integer-mult-bounds/pull/4504) | mihir-s-05 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4505](https://github.com/CrocSwap/integer-mult-bounds/pull/4505) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4506](https://github.com/CrocSwap/integer-mult-bounds/pull/4506) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4507](https://github.com/CrocSwap/integer-mult-bounds/pull/4507) | mihir-s-05 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4508](https://github.com/CrocSwap/integer-mult-bounds/pull/4508) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4509](https://github.com/CrocSwap/integer-mult-bounds/pull/4509) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4510](https://github.com/CrocSwap/integer-mult-bounds/pull/4510) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4511](https://github.com/CrocSwap/integer-mult-bounds/pull/4511) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4512](https://github.com/CrocSwap/integer-mult-bounds/pull/4512) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4513](https://github.com/CrocSwap/integer-mult-bounds/pull/4513) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4514](https://github.com/CrocSwap/integer-mult-bounds/pull/4514) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4515](https://github.com/CrocSwap/integer-mult-bounds/pull/4515) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4516](https://github.com/CrocSwap/integer-mult-bounds/pull/4516) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4517](https://github.com/CrocSwap/integer-mult-bounds/pull/4517) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4518](https://github.com/CrocSwap/integer-mult-bounds/pull/4518) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4519](https://github.com/CrocSwap/integer-mult-bounds/pull/4519) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4520](https://github.com/CrocSwap/integer-mult-bounds/pull/4520) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4521](https://github.com/CrocSwap/integer-mult-bounds/pull/4521) | dillona | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4522](https://github.com/CrocSwap/integer-mult-bounds/pull/4522) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4523](https://github.com/CrocSwap/integer-mult-bounds/pull/4523) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4524](https://github.com/CrocSwap/integer-mult-bounds/pull/4524) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4526](https://github.com/CrocSwap/integer-mult-bounds/pull/4526) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4527](https://github.com/CrocSwap/integer-mult-bounds/pull/4527) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4528](https://github.com/CrocSwap/integer-mult-bounds/pull/4528) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4529](https://github.com/CrocSwap/integer-mult-bounds/pull/4529) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4530](https://github.com/CrocSwap/integer-mult-bounds/pull/4530) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4531](https://github.com/CrocSwap/integer-mult-bounds/pull/4531) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4532](https://github.com/CrocSwap/integer-mult-bounds/pull/4532) | dillona | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4533](https://github.com/CrocSwap/integer-mult-bounds/pull/4533) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4534](https://github.com/CrocSwap/integer-mult-bounds/pull/4534) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4535](https://github.com/CrocSwap/integer-mult-bounds/pull/4535) | hexapode | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4536](https://github.com/CrocSwap/integer-mult-bounds/pull/4536) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4537](https://github.com/CrocSwap/integer-mult-bounds/pull/4537) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4538](https://github.com/CrocSwap/integer-mult-bounds/pull/4538) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4539](https://github.com/CrocSwap/integer-mult-bounds/pull/4539) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4540](https://github.com/CrocSwap/integer-mult-bounds/pull/4540) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4541](https://github.com/CrocSwap/integer-mult-bounds/pull/4541) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4542](https://github.com/CrocSwap/integer-mult-bounds/pull/4542) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4543](https://github.com/CrocSwap/integer-mult-bounds/pull/4543) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4544](https://github.com/CrocSwap/integer-mult-bounds/pull/4544) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4545](https://github.com/CrocSwap/integer-mult-bounds/pull/4545) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4546](https://github.com/CrocSwap/integer-mult-bounds/pull/4546) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4547](https://github.com/CrocSwap/integer-mult-bounds/pull/4547) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4549](https://github.com/CrocSwap/integer-mult-bounds/pull/4549) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4550](https://github.com/CrocSwap/integer-mult-bounds/pull/4550) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4551](https://github.com/CrocSwap/integer-mult-bounds/pull/4551) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4552](https://github.com/CrocSwap/integer-mult-bounds/pull/4552) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4553](https://github.com/CrocSwap/integer-mult-bounds/pull/4553) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4554](https://github.com/CrocSwap/integer-mult-bounds/pull/4554) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4555](https://github.com/CrocSwap/integer-mult-bounds/pull/4555) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4556](https://github.com/CrocSwap/integer-mult-bounds/pull/4556) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4557](https://github.com/CrocSwap/integer-mult-bounds/pull/4557) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4558](https://github.com/CrocSwap/integer-mult-bounds/pull/4558) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4559](https://github.com/CrocSwap/integer-mult-bounds/pull/4559) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4560](https://github.com/CrocSwap/integer-mult-bounds/pull/4560) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4561](https://github.com/CrocSwap/integer-mult-bounds/pull/4561) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4562](https://github.com/CrocSwap/integer-mult-bounds/pull/4562) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4563](https://github.com/CrocSwap/integer-mult-bounds/pull/4563) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4564](https://github.com/CrocSwap/integer-mult-bounds/pull/4564) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4565](https://github.com/CrocSwap/integer-mult-bounds/pull/4565) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4566](https://github.com/CrocSwap/integer-mult-bounds/pull/4566) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4567](https://github.com/CrocSwap/integer-mult-bounds/pull/4567) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4568](https://github.com/CrocSwap/integer-mult-bounds/pull/4568) | hexapode | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4569](https://github.com/CrocSwap/integer-mult-bounds/pull/4569) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4570](https://github.com/CrocSwap/integer-mult-bounds/pull/4570) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4579](https://github.com/CrocSwap/integer-mult-bounds/pull/4579) | mihir-s-05 | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4580](https://github.com/CrocSwap/integer-mult-bounds/pull/4580) | Matarener | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4581](https://github.com/CrocSwap/integer-mult-bounds/pull/4581) | mihir-s-05 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4582](https://github.com/CrocSwap/integer-mult-bounds/pull/4582) | mihir-s-05 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4583](https://github.com/CrocSwap/integer-mult-bounds/pull/4583) | mihir-s-05 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4584](https://github.com/CrocSwap/integer-mult-bounds/pull/4584) | mihir-s-05 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4585](https://github.com/CrocSwap/integer-mult-bounds/pull/4585) | mihir-s-05 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4586](https://github.com/CrocSwap/integer-mult-bounds/pull/4586) | mihir-s-05 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4587](https://github.com/CrocSwap/integer-mult-bounds/pull/4587) | mihir-s-05 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4588](https://github.com/CrocSwap/integer-mult-bounds/pull/4588) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4589](https://github.com/CrocSwap/integer-mult-bounds/pull/4589) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4590](https://github.com/CrocSwap/integer-mult-bounds/pull/4590) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4591](https://github.com/CrocSwap/integer-mult-bounds/pull/4591) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4592](https://github.com/CrocSwap/integer-mult-bounds/pull/4592) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4593](https://github.com/CrocSwap/integer-mult-bounds/pull/4593) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4594](https://github.com/CrocSwap/integer-mult-bounds/pull/4594) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4595](https://github.com/CrocSwap/integer-mult-bounds/pull/4595) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4597](https://github.com/CrocSwap/integer-mult-bounds/pull/4597) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4598](https://github.com/CrocSwap/integer-mult-bounds/pull/4598) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4599](https://github.com/CrocSwap/integer-mult-bounds/pull/4599) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4600](https://github.com/CrocSwap/integer-mult-bounds/pull/4600) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4601](https://github.com/CrocSwap/integer-mult-bounds/pull/4601) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4602](https://github.com/CrocSwap/integer-mult-bounds/pull/4602) | Matarener | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4603](https://github.com/CrocSwap/integer-mult-bounds/pull/4603) | Matarener | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4604](https://github.com/CrocSwap/integer-mult-bounds/pull/4604) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4605](https://github.com/CrocSwap/integer-mult-bounds/pull/4605) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4606](https://github.com/CrocSwap/integer-mult-bounds/pull/4606) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4607](https://github.com/CrocSwap/integer-mult-bounds/pull/4607) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4608](https://github.com/CrocSwap/integer-mult-bounds/pull/4608) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4609](https://github.com/CrocSwap/integer-mult-bounds/pull/4609) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4610](https://github.com/CrocSwap/integer-mult-bounds/pull/4610) | intqwq | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4612](https://github.com/CrocSwap/integer-mult-bounds/pull/4612) | Matarener | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4613](https://github.com/CrocSwap/integer-mult-bounds/pull/4613) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4614](https://github.com/CrocSwap/integer-mult-bounds/pull/4614) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4615](https://github.com/CrocSwap/integer-mult-bounds/pull/4615) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4616](https://github.com/CrocSwap/integer-mult-bounds/pull/4616) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4617](https://github.com/CrocSwap/integer-mult-bounds/pull/4617) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4618](https://github.com/CrocSwap/integer-mult-bounds/pull/4618) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4619](https://github.com/CrocSwap/integer-mult-bounds/pull/4619) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4620](https://github.com/CrocSwap/integer-mult-bounds/pull/4620) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4621](https://github.com/CrocSwap/integer-mult-bounds/pull/4621) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4622](https://github.com/CrocSwap/integer-mult-bounds/pull/4622) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4623](https://github.com/CrocSwap/integer-mult-bounds/pull/4623) | dillona | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4624](https://github.com/CrocSwap/integer-mult-bounds/pull/4624) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4625](https://github.com/CrocSwap/integer-mult-bounds/pull/4625) | pinterbanget | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4626](https://github.com/CrocSwap/integer-mult-bounds/pull/4626) | hexapode | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4627](https://github.com/CrocSwap/integer-mult-bounds/pull/4627) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4628](https://github.com/CrocSwap/integer-mult-bounds/pull/4628) | jacobalansussman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4630](https://github.com/CrocSwap/integer-mult-bounds/pull/4630) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4631](https://github.com/CrocSwap/integer-mult-bounds/pull/4631) | lee-phys | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4634](https://github.com/CrocSwap/integer-mult-bounds/pull/4634) | lee-phys | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4635](https://github.com/CrocSwap/integer-mult-bounds/pull/4635) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4636](https://github.com/CrocSwap/integer-mult-bounds/pull/4636) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4637](https://github.com/CrocSwap/integer-mult-bounds/pull/4637) | codyw912 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4638](https://github.com/CrocSwap/integer-mult-bounds/pull/4638) | codyw912 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4639](https://github.com/CrocSwap/integer-mult-bounds/pull/4639) | lm1909 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4640](https://github.com/CrocSwap/integer-mult-bounds/pull/4640) | lm1909 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4641](https://github.com/CrocSwap/integer-mult-bounds/pull/4641) | lm1909 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4642](https://github.com/CrocSwap/integer-mult-bounds/pull/4642) | lm1909 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4643](https://github.com/CrocSwap/integer-mult-bounds/pull/4643) | lm1909 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4644](https://github.com/CrocSwap/integer-mult-bounds/pull/4644) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4645](https://github.com/CrocSwap/integer-mult-bounds/pull/4645) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4646](https://github.com/CrocSwap/integer-mult-bounds/pull/4646) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4647](https://github.com/CrocSwap/integer-mult-bounds/pull/4647) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4648](https://github.com/CrocSwap/integer-mult-bounds/pull/4648) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4649](https://github.com/CrocSwap/integer-mult-bounds/pull/4649) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4650](https://github.com/CrocSwap/integer-mult-bounds/pull/4650) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4651](https://github.com/CrocSwap/integer-mult-bounds/pull/4651) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4652](https://github.com/CrocSwap/integer-mult-bounds/pull/4652) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4654](https://github.com/CrocSwap/integer-mult-bounds/pull/4654) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4655](https://github.com/CrocSwap/integer-mult-bounds/pull/4655) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4656](https://github.com/CrocSwap/integer-mult-bounds/pull/4656) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4657](https://github.com/CrocSwap/integer-mult-bounds/pull/4657) | ssafwann | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4658](https://github.com/CrocSwap/integer-mult-bounds/pull/4658) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4659](https://github.com/CrocSwap/integer-mult-bounds/pull/4659) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4660](https://github.com/CrocSwap/integer-mult-bounds/pull/4660) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4661](https://github.com/CrocSwap/integer-mult-bounds/pull/4661) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4662](https://github.com/CrocSwap/integer-mult-bounds/pull/4662) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4663](https://github.com/CrocSwap/integer-mult-bounds/pull/4663) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4664](https://github.com/CrocSwap/integer-mult-bounds/pull/4664) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4665](https://github.com/CrocSwap/integer-mult-bounds/pull/4665) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4666](https://github.com/CrocSwap/integer-mult-bounds/pull/4666) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4667](https://github.com/CrocSwap/integer-mult-bounds/pull/4667) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4668](https://github.com/CrocSwap/integer-mult-bounds/pull/4668) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4669](https://github.com/CrocSwap/integer-mult-bounds/pull/4669) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4670](https://github.com/CrocSwap/integer-mult-bounds/pull/4670) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4671](https://github.com/CrocSwap/integer-mult-bounds/pull/4671) | ssafwann | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4672](https://github.com/CrocSwap/integer-mult-bounds/pull/4672) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4673](https://github.com/CrocSwap/integer-mult-bounds/pull/4673) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4674](https://github.com/CrocSwap/integer-mult-bounds/pull/4674) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4676](https://github.com/CrocSwap/integer-mult-bounds/pull/4676) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4677](https://github.com/CrocSwap/integer-mult-bounds/pull/4677) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4678](https://github.com/CrocSwap/integer-mult-bounds/pull/4678) | ssafwann | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4679](https://github.com/CrocSwap/integer-mult-bounds/pull/4679) | mihir-s-05 | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4680](https://github.com/CrocSwap/integer-mult-bounds/pull/4680) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4683](https://github.com/CrocSwap/integer-mult-bounds/pull/4683) | mihir-s-05 | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4684](https://github.com/CrocSwap/integer-mult-bounds/pull/4684) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4685](https://github.com/CrocSwap/integer-mult-bounds/pull/4685) | mihir-s-05 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4686](https://github.com/CrocSwap/integer-mult-bounds/pull/4686) | mihir-s-05 | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4687](https://github.com/CrocSwap/integer-mult-bounds/pull/4687) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4688](https://github.com/CrocSwap/integer-mult-bounds/pull/4688) | lee-phys | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4689](https://github.com/CrocSwap/integer-mult-bounds/pull/4689) | mihir-s-05 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4690](https://github.com/CrocSwap/integer-mult-bounds/pull/4690) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4691](https://github.com/CrocSwap/integer-mult-bounds/pull/4691) | Matarener | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4692](https://github.com/CrocSwap/integer-mult-bounds/pull/4692) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4693](https://github.com/CrocSwap/integer-mult-bounds/pull/4693) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4695](https://github.com/CrocSwap/integer-mult-bounds/pull/4695) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4696](https://github.com/CrocSwap/integer-mult-bounds/pull/4696) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4697](https://github.com/CrocSwap/integer-mult-bounds/pull/4697) | Matarener | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4698](https://github.com/CrocSwap/integer-mult-bounds/pull/4698) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4699](https://github.com/CrocSwap/integer-mult-bounds/pull/4699) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4700](https://github.com/CrocSwap/integer-mult-bounds/pull/4700) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4701](https://github.com/CrocSwap/integer-mult-bounds/pull/4701) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4702](https://github.com/CrocSwap/integer-mult-bounds/pull/4702) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4703](https://github.com/CrocSwap/integer-mult-bounds/pull/4703) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4704](https://github.com/CrocSwap/integer-mult-bounds/pull/4704) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4705](https://github.com/CrocSwap/integer-mult-bounds/pull/4705) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4706](https://github.com/CrocSwap/integer-mult-bounds/pull/4706) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4707](https://github.com/CrocSwap/integer-mult-bounds/pull/4707) | Chrisbryan17 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4708](https://github.com/CrocSwap/integer-mult-bounds/pull/4708) | NicholasStone | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4710](https://github.com/CrocSwap/integer-mult-bounds/pull/4710) | Lyy-iiis | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4711](https://github.com/CrocSwap/integer-mult-bounds/pull/4711) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4712](https://github.com/CrocSwap/integer-mult-bounds/pull/4712) | intqwq | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4713](https://github.com/CrocSwap/integer-mult-bounds/pull/4713) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4714](https://github.com/CrocSwap/integer-mult-bounds/pull/4714) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4716](https://github.com/CrocSwap/integer-mult-bounds/pull/4716) | kumagi | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4717](https://github.com/CrocSwap/integer-mult-bounds/pull/4717) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4718](https://github.com/CrocSwap/integer-mult-bounds/pull/4718) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4719](https://github.com/CrocSwap/integer-mult-bounds/pull/4719) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4720](https://github.com/CrocSwap/integer-mult-bounds/pull/4720) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4724](https://github.com/CrocSwap/integer-mult-bounds/pull/4724) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4725](https://github.com/CrocSwap/integer-mult-bounds/pull/4725) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4726](https://github.com/CrocSwap/integer-mult-bounds/pull/4726) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4727](https://github.com/CrocSwap/integer-mult-bounds/pull/4727) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4728](https://github.com/CrocSwap/integer-mult-bounds/pull/4728) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4729](https://github.com/CrocSwap/integer-mult-bounds/pull/4729) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4730](https://github.com/CrocSwap/integer-mult-bounds/pull/4730) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4731](https://github.com/CrocSwap/integer-mult-bounds/pull/4731) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4732](https://github.com/CrocSwap/integer-mult-bounds/pull/4732) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4733](https://github.com/CrocSwap/integer-mult-bounds/pull/4733) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4734](https://github.com/CrocSwap/integer-mult-bounds/pull/4734) | codyw912 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4735](https://github.com/CrocSwap/integer-mult-bounds/pull/4735) | codyw912 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4736](https://github.com/CrocSwap/integer-mult-bounds/pull/4736) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4737](https://github.com/CrocSwap/integer-mult-bounds/pull/4737) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4738](https://github.com/CrocSwap/integer-mult-bounds/pull/4738) | JoyboyBrian | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4739](https://github.com/CrocSwap/integer-mult-bounds/pull/4739) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4740](https://github.com/CrocSwap/integer-mult-bounds/pull/4740) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4741](https://github.com/CrocSwap/integer-mult-bounds/pull/4741) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4742](https://github.com/CrocSwap/integer-mult-bounds/pull/4742) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4743](https://github.com/CrocSwap/integer-mult-bounds/pull/4743) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4745](https://github.com/CrocSwap/integer-mult-bounds/pull/4745) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4746](https://github.com/CrocSwap/integer-mult-bounds/pull/4746) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4747](https://github.com/CrocSwap/integer-mult-bounds/pull/4747) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4748](https://github.com/CrocSwap/integer-mult-bounds/pull/4748) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4749](https://github.com/CrocSwap/integer-mult-bounds/pull/4749) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4750](https://github.com/CrocSwap/integer-mult-bounds/pull/4750) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4751](https://github.com/CrocSwap/integer-mult-bounds/pull/4751) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4752](https://github.com/CrocSwap/integer-mult-bounds/pull/4752) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4753](https://github.com/CrocSwap/integer-mult-bounds/pull/4753) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4754](https://github.com/CrocSwap/integer-mult-bounds/pull/4754) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4755](https://github.com/CrocSwap/integer-mult-bounds/pull/4755) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4756](https://github.com/CrocSwap/integer-mult-bounds/pull/4756) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4757](https://github.com/CrocSwap/integer-mult-bounds/pull/4757) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4758](https://github.com/CrocSwap/integer-mult-bounds/pull/4758) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4759](https://github.com/CrocSwap/integer-mult-bounds/pull/4759) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4760](https://github.com/CrocSwap/integer-mult-bounds/pull/4760) | ai-nanachi | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4761](https://github.com/CrocSwap/integer-mult-bounds/pull/4761) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4762](https://github.com/CrocSwap/integer-mult-bounds/pull/4762) | MatShep | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4763](https://github.com/CrocSwap/integer-mult-bounds/pull/4763) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4764](https://github.com/CrocSwap/integer-mult-bounds/pull/4764) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4765](https://github.com/CrocSwap/integer-mult-bounds/pull/4765) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4766](https://github.com/CrocSwap/integer-mult-bounds/pull/4766) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4767](https://github.com/CrocSwap/integer-mult-bounds/pull/4767) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4768](https://github.com/CrocSwap/integer-mult-bounds/pull/4768) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4769](https://github.com/CrocSwap/integer-mult-bounds/pull/4769) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4770](https://github.com/CrocSwap/integer-mult-bounds/pull/4770) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4771](https://github.com/CrocSwap/integer-mult-bounds/pull/4771) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4772](https://github.com/CrocSwap/integer-mult-bounds/pull/4772) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4773](https://github.com/CrocSwap/integer-mult-bounds/pull/4773) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4774](https://github.com/CrocSwap/integer-mult-bounds/pull/4774) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4775](https://github.com/CrocSwap/integer-mult-bounds/pull/4775) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4776](https://github.com/CrocSwap/integer-mult-bounds/pull/4776) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4777](https://github.com/CrocSwap/integer-mult-bounds/pull/4777) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4778](https://github.com/CrocSwap/integer-mult-bounds/pull/4778) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4779](https://github.com/CrocSwap/integer-mult-bounds/pull/4779) | JoyboyBrian | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4780](https://github.com/CrocSwap/integer-mult-bounds/pull/4780) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4781](https://github.com/CrocSwap/integer-mult-bounds/pull/4781) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4782](https://github.com/CrocSwap/integer-mult-bounds/pull/4782) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4783](https://github.com/CrocSwap/integer-mult-bounds/pull/4783) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4784](https://github.com/CrocSwap/integer-mult-bounds/pull/4784) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4785](https://github.com/CrocSwap/integer-mult-bounds/pull/4785) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4786](https://github.com/CrocSwap/integer-mult-bounds/pull/4786) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4787](https://github.com/CrocSwap/integer-mult-bounds/pull/4787) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4788](https://github.com/CrocSwap/integer-mult-bounds/pull/4788) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4789](https://github.com/CrocSwap/integer-mult-bounds/pull/4789) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4790](https://github.com/CrocSwap/integer-mult-bounds/pull/4790) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4791](https://github.com/CrocSwap/integer-mult-bounds/pull/4791) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4792](https://github.com/CrocSwap/integer-mult-bounds/pull/4792) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4793](https://github.com/CrocSwap/integer-mult-bounds/pull/4793) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4794](https://github.com/CrocSwap/integer-mult-bounds/pull/4794) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4795](https://github.com/CrocSwap/integer-mult-bounds/pull/4795) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4796](https://github.com/CrocSwap/integer-mult-bounds/pull/4796) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4797](https://github.com/CrocSwap/integer-mult-bounds/pull/4797) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4798](https://github.com/CrocSwap/integer-mult-bounds/pull/4798) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4799](https://github.com/CrocSwap/integer-mult-bounds/pull/4799) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4800](https://github.com/CrocSwap/integer-mult-bounds/pull/4800) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4801](https://github.com/CrocSwap/integer-mult-bounds/pull/4801) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4802](https://github.com/CrocSwap/integer-mult-bounds/pull/4802) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4803](https://github.com/CrocSwap/integer-mult-bounds/pull/4803) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4804](https://github.com/CrocSwap/integer-mult-bounds/pull/4804) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4805](https://github.com/CrocSwap/integer-mult-bounds/pull/4805) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4806](https://github.com/CrocSwap/integer-mult-bounds/pull/4806) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4807](https://github.com/CrocSwap/integer-mult-bounds/pull/4807) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4808](https://github.com/CrocSwap/integer-mult-bounds/pull/4808) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4809](https://github.com/CrocSwap/integer-mult-bounds/pull/4809) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4810](https://github.com/CrocSwap/integer-mult-bounds/pull/4810) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4811](https://github.com/CrocSwap/integer-mult-bounds/pull/4811) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4812](https://github.com/CrocSwap/integer-mult-bounds/pull/4812) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4813](https://github.com/CrocSwap/integer-mult-bounds/pull/4813) | hexapode | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4814](https://github.com/CrocSwap/integer-mult-bounds/pull/4814) | ai-nanachi | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4815](https://github.com/CrocSwap/integer-mult-bounds/pull/4815) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4816](https://github.com/CrocSwap/integer-mult-bounds/pull/4816) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4817](https://github.com/CrocSwap/integer-mult-bounds/pull/4817) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4818](https://github.com/CrocSwap/integer-mult-bounds/pull/4818) | hexapode | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4819](https://github.com/CrocSwap/integer-mult-bounds/pull/4819) | hexapode | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4820](https://github.com/CrocSwap/integer-mult-bounds/pull/4820) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4821](https://github.com/CrocSwap/integer-mult-bounds/pull/4821) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4822](https://github.com/CrocSwap/integer-mult-bounds/pull/4822) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4823](https://github.com/CrocSwap/integer-mult-bounds/pull/4823) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4824](https://github.com/CrocSwap/integer-mult-bounds/pull/4824) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4825](https://github.com/CrocSwap/integer-mult-bounds/pull/4825) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4826](https://github.com/CrocSwap/integer-mult-bounds/pull/4826) | hexapode | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4827](https://github.com/CrocSwap/integer-mult-bounds/pull/4827) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4828](https://github.com/CrocSwap/integer-mult-bounds/pull/4828) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4829](https://github.com/CrocSwap/integer-mult-bounds/pull/4829) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4830](https://github.com/CrocSwap/integer-mult-bounds/pull/4830) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4831](https://github.com/CrocSwap/integer-mult-bounds/pull/4831) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4832](https://github.com/CrocSwap/integer-mult-bounds/pull/4832) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4833](https://github.com/CrocSwap/integer-mult-bounds/pull/4833) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4834](https://github.com/CrocSwap/integer-mult-bounds/pull/4834) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4835](https://github.com/CrocSwap/integer-mult-bounds/pull/4835) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4836](https://github.com/CrocSwap/integer-mult-bounds/pull/4836) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4837](https://github.com/CrocSwap/integer-mult-bounds/pull/4837) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4838](https://github.com/CrocSwap/integer-mult-bounds/pull/4838) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4839](https://github.com/CrocSwap/integer-mult-bounds/pull/4839) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4841](https://github.com/CrocSwap/integer-mult-bounds/pull/4841) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4842](https://github.com/CrocSwap/integer-mult-bounds/pull/4842) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4844](https://github.com/CrocSwap/integer-mult-bounds/pull/4844) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4845](https://github.com/CrocSwap/integer-mult-bounds/pull/4845) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4846](https://github.com/CrocSwap/integer-mult-bounds/pull/4846) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4847](https://github.com/CrocSwap/integer-mult-bounds/pull/4847) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4848](https://github.com/CrocSwap/integer-mult-bounds/pull/4848) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4849](https://github.com/CrocSwap/integer-mult-bounds/pull/4849) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4850](https://github.com/CrocSwap/integer-mult-bounds/pull/4850) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4851](https://github.com/CrocSwap/integer-mult-bounds/pull/4851) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4852](https://github.com/CrocSwap/integer-mult-bounds/pull/4852) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4854](https://github.com/CrocSwap/integer-mult-bounds/pull/4854) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4855](https://github.com/CrocSwap/integer-mult-bounds/pull/4855) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4856](https://github.com/CrocSwap/integer-mult-bounds/pull/4856) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4857](https://github.com/CrocSwap/integer-mult-bounds/pull/4857) | Clear1nsight | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4858](https://github.com/CrocSwap/integer-mult-bounds/pull/4858) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4859](https://github.com/CrocSwap/integer-mult-bounds/pull/4859) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4860](https://github.com/CrocSwap/integer-mult-bounds/pull/4860) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4861](https://github.com/CrocSwap/integer-mult-bounds/pull/4861) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4862](https://github.com/CrocSwap/integer-mult-bounds/pull/4862) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4863](https://github.com/CrocSwap/integer-mult-bounds/pull/4863) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4864](https://github.com/CrocSwap/integer-mult-bounds/pull/4864) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4865](https://github.com/CrocSwap/integer-mult-bounds/pull/4865) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4866](https://github.com/CrocSwap/integer-mult-bounds/pull/4866) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4867](https://github.com/CrocSwap/integer-mult-bounds/pull/4867) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4868](https://github.com/CrocSwap/integer-mult-bounds/pull/4868) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4869](https://github.com/CrocSwap/integer-mult-bounds/pull/4869) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4870](https://github.com/CrocSwap/integer-mult-bounds/pull/4870) | codyw912 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4871](https://github.com/CrocSwap/integer-mult-bounds/pull/4871) | codyw912 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4872](https://github.com/CrocSwap/integer-mult-bounds/pull/4872) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4873](https://github.com/CrocSwap/integer-mult-bounds/pull/4873) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4874](https://github.com/CrocSwap/integer-mult-bounds/pull/4874) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4875](https://github.com/CrocSwap/integer-mult-bounds/pull/4875) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4876](https://github.com/CrocSwap/integer-mult-bounds/pull/4876) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4877](https://github.com/CrocSwap/integer-mult-bounds/pull/4877) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4878](https://github.com/CrocSwap/integer-mult-bounds/pull/4878) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4879](https://github.com/CrocSwap/integer-mult-bounds/pull/4879) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4880](https://github.com/CrocSwap/integer-mult-bounds/pull/4880) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4881](https://github.com/CrocSwap/integer-mult-bounds/pull/4881) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4882](https://github.com/CrocSwap/integer-mult-bounds/pull/4882) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4883](https://github.com/CrocSwap/integer-mult-bounds/pull/4883) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4884](https://github.com/CrocSwap/integer-mult-bounds/pull/4884) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4885](https://github.com/CrocSwap/integer-mult-bounds/pull/4885) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4886](https://github.com/CrocSwap/integer-mult-bounds/pull/4886) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4887](https://github.com/CrocSwap/integer-mult-bounds/pull/4887) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4888](https://github.com/CrocSwap/integer-mult-bounds/pull/4888) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4889](https://github.com/CrocSwap/integer-mult-bounds/pull/4889) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4890](https://github.com/CrocSwap/integer-mult-bounds/pull/4890) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4891](https://github.com/CrocSwap/integer-mult-bounds/pull/4891) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4892](https://github.com/CrocSwap/integer-mult-bounds/pull/4892) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4893](https://github.com/CrocSwap/integer-mult-bounds/pull/4893) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4894](https://github.com/CrocSwap/integer-mult-bounds/pull/4894) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4895](https://github.com/CrocSwap/integer-mult-bounds/pull/4895) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4896](https://github.com/CrocSwap/integer-mult-bounds/pull/4896) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4897](https://github.com/CrocSwap/integer-mult-bounds/pull/4897) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4898](https://github.com/CrocSwap/integer-mult-bounds/pull/4898) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4899](https://github.com/CrocSwap/integer-mult-bounds/pull/4899) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4900](https://github.com/CrocSwap/integer-mult-bounds/pull/4900) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4901](https://github.com/CrocSwap/integer-mult-bounds/pull/4901) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4904](https://github.com/CrocSwap/integer-mult-bounds/pull/4904) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4905](https://github.com/CrocSwap/integer-mult-bounds/pull/4905) | mihir-s-05 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4906](https://github.com/CrocSwap/integer-mult-bounds/pull/4906) | mihir-s-05 | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4907](https://github.com/CrocSwap/integer-mult-bounds/pull/4907) | mihir-s-05 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4908](https://github.com/CrocSwap/integer-mult-bounds/pull/4908) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4909](https://github.com/CrocSwap/integer-mult-bounds/pull/4909) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4910](https://github.com/CrocSwap/integer-mult-bounds/pull/4910) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4911](https://github.com/CrocSwap/integer-mult-bounds/pull/4911) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4912](https://github.com/CrocSwap/integer-mult-bounds/pull/4912) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4913](https://github.com/CrocSwap/integer-mult-bounds/pull/4913) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4914](https://github.com/CrocSwap/integer-mult-bounds/pull/4914) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4915](https://github.com/CrocSwap/integer-mult-bounds/pull/4915) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4916](https://github.com/CrocSwap/integer-mult-bounds/pull/4916) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4917](https://github.com/CrocSwap/integer-mult-bounds/pull/4917) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4918](https://github.com/CrocSwap/integer-mult-bounds/pull/4918) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4919](https://github.com/CrocSwap/integer-mult-bounds/pull/4919) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4920](https://github.com/CrocSwap/integer-mult-bounds/pull/4920) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4921](https://github.com/CrocSwap/integer-mult-bounds/pull/4921) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4923](https://github.com/CrocSwap/integer-mult-bounds/pull/4923) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4924](https://github.com/CrocSwap/integer-mult-bounds/pull/4924) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4925](https://github.com/CrocSwap/integer-mult-bounds/pull/4925) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4926](https://github.com/CrocSwap/integer-mult-bounds/pull/4926) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4928](https://github.com/CrocSwap/integer-mult-bounds/pull/4928) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4929](https://github.com/CrocSwap/integer-mult-bounds/pull/4929) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4931](https://github.com/CrocSwap/integer-mult-bounds/pull/4931) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4932](https://github.com/CrocSwap/integer-mult-bounds/pull/4932) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4933](https://github.com/CrocSwap/integer-mult-bounds/pull/4933) | dillona | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4935](https://github.com/CrocSwap/integer-mult-bounds/pull/4935) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4936](https://github.com/CrocSwap/integer-mult-bounds/pull/4936) | mihir-s-05 | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4938](https://github.com/CrocSwap/integer-mult-bounds/pull/4938) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4939](https://github.com/CrocSwap/integer-mult-bounds/pull/4939) | mihir-s-05 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4940](https://github.com/CrocSwap/integer-mult-bounds/pull/4940) | SethBurkart123 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4942](https://github.com/CrocSwap/integer-mult-bounds/pull/4942) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4943](https://github.com/CrocSwap/integer-mult-bounds/pull/4943) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4944](https://github.com/CrocSwap/integer-mult-bounds/pull/4944) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4946](https://github.com/CrocSwap/integer-mult-bounds/pull/4946) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4947](https://github.com/CrocSwap/integer-mult-bounds/pull/4947) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4948](https://github.com/CrocSwap/integer-mult-bounds/pull/4948) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4949](https://github.com/CrocSwap/integer-mult-bounds/pull/4949) | mihir-s-05 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4950](https://github.com/CrocSwap/integer-mult-bounds/pull/4950) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4951](https://github.com/CrocSwap/integer-mult-bounds/pull/4951) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4952](https://github.com/CrocSwap/integer-mult-bounds/pull/4952) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4953](https://github.com/CrocSwap/integer-mult-bounds/pull/4953) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4954](https://github.com/CrocSwap/integer-mult-bounds/pull/4954) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4955](https://github.com/CrocSwap/integer-mult-bounds/pull/4955) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4956](https://github.com/CrocSwap/integer-mult-bounds/pull/4956) | mihir-s-05 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4957](https://github.com/CrocSwap/integer-mult-bounds/pull/4957) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4958](https://github.com/CrocSwap/integer-mult-bounds/pull/4958) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4959](https://github.com/CrocSwap/integer-mult-bounds/pull/4959) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4960](https://github.com/CrocSwap/integer-mult-bounds/pull/4960) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4961](https://github.com/CrocSwap/integer-mult-bounds/pull/4961) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4962](https://github.com/CrocSwap/integer-mult-bounds/pull/4962) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4963](https://github.com/CrocSwap/integer-mult-bounds/pull/4963) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4964](https://github.com/CrocSwap/integer-mult-bounds/pull/4964) | aliromman | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4965](https://github.com/CrocSwap/integer-mult-bounds/pull/4965) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4966](https://github.com/CrocSwap/integer-mult-bounds/pull/4966) | Lyy-iiis | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4967](https://github.com/CrocSwap/integer-mult-bounds/pull/4967) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4968](https://github.com/CrocSwap/integer-mult-bounds/pull/4968) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4969](https://github.com/CrocSwap/integer-mult-bounds/pull/4969) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4970](https://github.com/CrocSwap/integer-mult-bounds/pull/4970) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4971](https://github.com/CrocSwap/integer-mult-bounds/pull/4971) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4972](https://github.com/CrocSwap/integer-mult-bounds/pull/4972) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4973](https://github.com/CrocSwap/integer-mult-bounds/pull/4973) | jwr404 | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4974](https://github.com/CrocSwap/integer-mult-bounds/pull/4974) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4975](https://github.com/CrocSwap/integer-mult-bounds/pull/4975) | JoyboyBrian | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4976](https://github.com/CrocSwap/integer-mult-bounds/pull/4976) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4977](https://github.com/CrocSwap/integer-mult-bounds/pull/4977) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4978](https://github.com/CrocSwap/integer-mult-bounds/pull/4978) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4979](https://github.com/CrocSwap/integer-mult-bounds/pull/4979) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4980](https://github.com/CrocSwap/integer-mult-bounds/pull/4980) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4981](https://github.com/CrocSwap/integer-mult-bounds/pull/4981) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4982](https://github.com/CrocSwap/integer-mult-bounds/pull/4982) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4983](https://github.com/CrocSwap/integer-mult-bounds/pull/4983) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4984](https://github.com/CrocSwap/integer-mult-bounds/pull/4984) | Clear1nsight | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4986](https://github.com/CrocSwap/integer-mult-bounds/pull/4986) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4987](https://github.com/CrocSwap/integer-mult-bounds/pull/4987) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4988](https://github.com/CrocSwap/integer-mult-bounds/pull/4988) | 1337isnot1337 | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4989](https://github.com/CrocSwap/integer-mult-bounds/pull/4989) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4990](https://github.com/CrocSwap/integer-mult-bounds/pull/4990) | kumagi | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4991](https://github.com/CrocSwap/integer-mult-bounds/pull/4991) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4992](https://github.com/CrocSwap/integer-mult-bounds/pull/4992) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4994](https://github.com/CrocSwap/integer-mult-bounds/pull/4994) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4995](https://github.com/CrocSwap/integer-mult-bounds/pull/4995) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4996](https://github.com/CrocSwap/integer-mult-bounds/pull/4996) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4997](https://github.com/CrocSwap/integer-mult-bounds/pull/4997) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#4998](https://github.com/CrocSwap/integer-mult-bounds/pull/4998) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5000](https://github.com/CrocSwap/integer-mult-bounds/pull/5000) | SHIN09-git | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5001](https://github.com/CrocSwap/integer-mult-bounds/pull/5001) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5002](https://github.com/CrocSwap/integer-mult-bounds/pull/5002) | aliromman | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5003](https://github.com/CrocSwap/integer-mult-bounds/pull/5003) | krzysztofwojt | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5004](https://github.com/CrocSwap/integer-mult-bounds/pull/5004) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5005](https://github.com/CrocSwap/integer-mult-bounds/pull/5005) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5007](https://github.com/CrocSwap/integer-mult-bounds/pull/5007) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5014](https://github.com/CrocSwap/integer-mult-bounds/pull/5014) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5015](https://github.com/CrocSwap/integer-mult-bounds/pull/5015) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5016](https://github.com/CrocSwap/integer-mult-bounds/pull/5016) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5017](https://github.com/CrocSwap/integer-mult-bounds/pull/5017) | JoyboyBrian | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5018](https://github.com/CrocSwap/integer-mult-bounds/pull/5018) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5019](https://github.com/CrocSwap/integer-mult-bounds/pull/5019) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5020](https://github.com/CrocSwap/integer-mult-bounds/pull/5020) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5021](https://github.com/CrocSwap/integer-mult-bounds/pull/5021) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5022](https://github.com/CrocSwap/integer-mult-bounds/pull/5022) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5023](https://github.com/CrocSwap/integer-mult-bounds/pull/5023) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5024](https://github.com/CrocSwap/integer-mult-bounds/pull/5024) | krzysztofwojt | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5025](https://github.com/CrocSwap/integer-mult-bounds/pull/5025) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5026](https://github.com/CrocSwap/integer-mult-bounds/pull/5026) | thakrarsagar | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5027](https://github.com/CrocSwap/integer-mult-bounds/pull/5027) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5028](https://github.com/CrocSwap/integer-mult-bounds/pull/5028) | antunishdPursuit | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5029](https://github.com/CrocSwap/integer-mult-bounds/pull/5029) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5031](https://github.com/CrocSwap/integer-mult-bounds/pull/5031) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5033](https://github.com/CrocSwap/integer-mult-bounds/pull/5033) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5034](https://github.com/CrocSwap/integer-mult-bounds/pull/5034) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5035](https://github.com/CrocSwap/integer-mult-bounds/pull/5035) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5036](https://github.com/CrocSwap/integer-mult-bounds/pull/5036) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5037](https://github.com/CrocSwap/integer-mult-bounds/pull/5037) | Lyy-iiis | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5038](https://github.com/CrocSwap/integer-mult-bounds/pull/5038) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5039](https://github.com/CrocSwap/integer-mult-bounds/pull/5039) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5040](https://github.com/CrocSwap/integer-mult-bounds/pull/5040) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5041](https://github.com/CrocSwap/integer-mult-bounds/pull/5041) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5042](https://github.com/CrocSwap/integer-mult-bounds/pull/5042) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5043](https://github.com/CrocSwap/integer-mult-bounds/pull/5043) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5044](https://github.com/CrocSwap/integer-mult-bounds/pull/5044) | mihir-s-05 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5045](https://github.com/CrocSwap/integer-mult-bounds/pull/5045) | krzysztofwojt | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5046](https://github.com/CrocSwap/integer-mult-bounds/pull/5046) | mihir-s-05 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5047](https://github.com/CrocSwap/integer-mult-bounds/pull/5047) | mihir-s-05 | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5049](https://github.com/CrocSwap/integer-mult-bounds/pull/5049) | mihir-s-05 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5050](https://github.com/CrocSwap/integer-mult-bounds/pull/5050) | JoyboyBrian | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5051](https://github.com/CrocSwap/integer-mult-bounds/pull/5051) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5052](https://github.com/CrocSwap/integer-mult-bounds/pull/5052) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5053](https://github.com/CrocSwap/integer-mult-bounds/pull/5053) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5054](https://github.com/CrocSwap/integer-mult-bounds/pull/5054) | mihir-s-05 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5055](https://github.com/CrocSwap/integer-mult-bounds/pull/5055) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5056](https://github.com/CrocSwap/integer-mult-bounds/pull/5056) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5057](https://github.com/CrocSwap/integer-mult-bounds/pull/5057) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5058](https://github.com/CrocSwap/integer-mult-bounds/pull/5058) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5059](https://github.com/CrocSwap/integer-mult-bounds/pull/5059) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5060](https://github.com/CrocSwap/integer-mult-bounds/pull/5060) | Matarener | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5063](https://github.com/CrocSwap/integer-mult-bounds/pull/5063) | krzysztofwojt | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5065](https://github.com/CrocSwap/integer-mult-bounds/pull/5065) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5067](https://github.com/CrocSwap/integer-mult-bounds/pull/5067) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5068](https://github.com/CrocSwap/integer-mult-bounds/pull/5068) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5069](https://github.com/CrocSwap/integer-mult-bounds/pull/5069) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5070](https://github.com/CrocSwap/integer-mult-bounds/pull/5070) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5071](https://github.com/CrocSwap/integer-mult-bounds/pull/5071) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5072](https://github.com/CrocSwap/integer-mult-bounds/pull/5072) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5073](https://github.com/CrocSwap/integer-mult-bounds/pull/5073) | lee-phys | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5074](https://github.com/CrocSwap/integer-mult-bounds/pull/5074) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5075](https://github.com/CrocSwap/integer-mult-bounds/pull/5075) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5076](https://github.com/CrocSwap/integer-mult-bounds/pull/5076) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5077](https://github.com/CrocSwap/integer-mult-bounds/pull/5077) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5078](https://github.com/CrocSwap/integer-mult-bounds/pull/5078) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5079](https://github.com/CrocSwap/integer-mult-bounds/pull/5079) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5080](https://github.com/CrocSwap/integer-mult-bounds/pull/5080) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5081](https://github.com/CrocSwap/integer-mult-bounds/pull/5081) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5082](https://github.com/CrocSwap/integer-mult-bounds/pull/5082) | JoyboyBrian | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5083](https://github.com/CrocSwap/integer-mult-bounds/pull/5083) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5084](https://github.com/CrocSwap/integer-mult-bounds/pull/5084) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5085](https://github.com/CrocSwap/integer-mult-bounds/pull/5085) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5087](https://github.com/CrocSwap/integer-mult-bounds/pull/5087) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5089](https://github.com/CrocSwap/integer-mult-bounds/pull/5089) | lee-phys | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5090](https://github.com/CrocSwap/integer-mult-bounds/pull/5090) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5091](https://github.com/CrocSwap/integer-mult-bounds/pull/5091) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5092](https://github.com/CrocSwap/integer-mult-bounds/pull/5092) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5093](https://github.com/CrocSwap/integer-mult-bounds/pull/5093) | krzysztofwojt | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5095](https://github.com/CrocSwap/integer-mult-bounds/pull/5095) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5096](https://github.com/CrocSwap/integer-mult-bounds/pull/5096) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5097](https://github.com/CrocSwap/integer-mult-bounds/pull/5097) | krzysztofwojt | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5098](https://github.com/CrocSwap/integer-mult-bounds/pull/5098) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5099](https://github.com/CrocSwap/integer-mult-bounds/pull/5099) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5101](https://github.com/CrocSwap/integer-mult-bounds/pull/5101) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5102](https://github.com/CrocSwap/integer-mult-bounds/pull/5102) | JoyboyBrian | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5103](https://github.com/CrocSwap/integer-mult-bounds/pull/5103) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5104](https://github.com/CrocSwap/integer-mult-bounds/pull/5104) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5105](https://github.com/CrocSwap/integer-mult-bounds/pull/5105) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5106](https://github.com/CrocSwap/integer-mult-bounds/pull/5106) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5107](https://github.com/CrocSwap/integer-mult-bounds/pull/5107) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5108](https://github.com/CrocSwap/integer-mult-bounds/pull/5108) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5109](https://github.com/CrocSwap/integer-mult-bounds/pull/5109) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5110](https://github.com/CrocSwap/integer-mult-bounds/pull/5110) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5111](https://github.com/CrocSwap/integer-mult-bounds/pull/5111) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5112](https://github.com/CrocSwap/integer-mult-bounds/pull/5112) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5113](https://github.com/CrocSwap/integer-mult-bounds/pull/5113) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5114](https://github.com/CrocSwap/integer-mult-bounds/pull/5114) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5115](https://github.com/CrocSwap/integer-mult-bounds/pull/5115) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5116](https://github.com/CrocSwap/integer-mult-bounds/pull/5116) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5117](https://github.com/CrocSwap/integer-mult-bounds/pull/5117) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5118](https://github.com/CrocSwap/integer-mult-bounds/pull/5118) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5119](https://github.com/CrocSwap/integer-mult-bounds/pull/5119) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5120](https://github.com/CrocSwap/integer-mult-bounds/pull/5120) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5122](https://github.com/CrocSwap/integer-mult-bounds/pull/5122) | krzysztofwojt | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5123](https://github.com/CrocSwap/integer-mult-bounds/pull/5123) | JoyboyBrian | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5124](https://github.com/CrocSwap/integer-mult-bounds/pull/5124) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5126](https://github.com/CrocSwap/integer-mult-bounds/pull/5126) | dillona | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5128](https://github.com/CrocSwap/integer-mult-bounds/pull/5128) | krzysztofwojt | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5129](https://github.com/CrocSwap/integer-mult-bounds/pull/5129) | JoyboyBrian | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5130](https://github.com/CrocSwap/integer-mult-bounds/pull/5130) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5132](https://github.com/CrocSwap/integer-mult-bounds/pull/5132) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5133](https://github.com/CrocSwap/integer-mult-bounds/pull/5133) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5134](https://github.com/CrocSwap/integer-mult-bounds/pull/5134) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5135](https://github.com/CrocSwap/integer-mult-bounds/pull/5135) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5136](https://github.com/CrocSwap/integer-mult-bounds/pull/5136) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5137](https://github.com/CrocSwap/integer-mult-bounds/pull/5137) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5138](https://github.com/CrocSwap/integer-mult-bounds/pull/5138) | krzysztofwojt | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5139](https://github.com/CrocSwap/integer-mult-bounds/pull/5139) | lee-phys | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5140](https://github.com/CrocSwap/integer-mult-bounds/pull/5140) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5141](https://github.com/CrocSwap/integer-mult-bounds/pull/5141) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5143](https://github.com/CrocSwap/integer-mult-bounds/pull/5143) | krzysztofwojt | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5144](https://github.com/CrocSwap/integer-mult-bounds/pull/5144) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5145](https://github.com/CrocSwap/integer-mult-bounds/pull/5145) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5146](https://github.com/CrocSwap/integer-mult-bounds/pull/5146) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5147](https://github.com/CrocSwap/integer-mult-bounds/pull/5147) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5148](https://github.com/CrocSwap/integer-mult-bounds/pull/5148) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5149](https://github.com/CrocSwap/integer-mult-bounds/pull/5149) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5150](https://github.com/CrocSwap/integer-mult-bounds/pull/5150) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5151](https://github.com/CrocSwap/integer-mult-bounds/pull/5151) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5152](https://github.com/CrocSwap/integer-mult-bounds/pull/5152) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5153](https://github.com/CrocSwap/integer-mult-bounds/pull/5153) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5154](https://github.com/CrocSwap/integer-mult-bounds/pull/5154) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5155](https://github.com/CrocSwap/integer-mult-bounds/pull/5155) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5156](https://github.com/CrocSwap/integer-mult-bounds/pull/5156) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5157](https://github.com/CrocSwap/integer-mult-bounds/pull/5157) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5158](https://github.com/CrocSwap/integer-mult-bounds/pull/5158) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5159](https://github.com/CrocSwap/integer-mult-bounds/pull/5159) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5160](https://github.com/CrocSwap/integer-mult-bounds/pull/5160) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5161](https://github.com/CrocSwap/integer-mult-bounds/pull/5161) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5162](https://github.com/CrocSwap/integer-mult-bounds/pull/5162) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5163](https://github.com/CrocSwap/integer-mult-bounds/pull/5163) | lee-phys | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5164](https://github.com/CrocSwap/integer-mult-bounds/pull/5164) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5165](https://github.com/CrocSwap/integer-mult-bounds/pull/5165) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5166](https://github.com/CrocSwap/integer-mult-bounds/pull/5166) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5167](https://github.com/CrocSwap/integer-mult-bounds/pull/5167) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5168](https://github.com/CrocSwap/integer-mult-bounds/pull/5168) | krzysztofwojt | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5170](https://github.com/CrocSwap/integer-mult-bounds/pull/5170) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5171](https://github.com/CrocSwap/integer-mult-bounds/pull/5171) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5172](https://github.com/CrocSwap/integer-mult-bounds/pull/5172) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5173](https://github.com/CrocSwap/integer-mult-bounds/pull/5173) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5174](https://github.com/CrocSwap/integer-mult-bounds/pull/5174) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5175](https://github.com/CrocSwap/integer-mult-bounds/pull/5175) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5176](https://github.com/CrocSwap/integer-mult-bounds/pull/5176) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5177](https://github.com/CrocSwap/integer-mult-bounds/pull/5177) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5178](https://github.com/CrocSwap/integer-mult-bounds/pull/5178) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5179](https://github.com/CrocSwap/integer-mult-bounds/pull/5179) | thu-nmrc | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5180](https://github.com/CrocSwap/integer-mult-bounds/pull/5180) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5181](https://github.com/CrocSwap/integer-mult-bounds/pull/5181) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5182](https://github.com/CrocSwap/integer-mult-bounds/pull/5182) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5183](https://github.com/CrocSwap/integer-mult-bounds/pull/5183) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5184](https://github.com/CrocSwap/integer-mult-bounds/pull/5184) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5185](https://github.com/CrocSwap/integer-mult-bounds/pull/5185) | JoyboyBrian | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5186](https://github.com/CrocSwap/integer-mult-bounds/pull/5186) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5187](https://github.com/CrocSwap/integer-mult-bounds/pull/5187) | krzysztofwojt | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5188](https://github.com/CrocSwap/integer-mult-bounds/pull/5188) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5189](https://github.com/CrocSwap/integer-mult-bounds/pull/5189) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5190](https://github.com/CrocSwap/integer-mult-bounds/pull/5190) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5191](https://github.com/CrocSwap/integer-mult-bounds/pull/5191) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5193](https://github.com/CrocSwap/integer-mult-bounds/pull/5193) | krzysztofwojt | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5195](https://github.com/CrocSwap/integer-mult-bounds/pull/5195) | hevlyo | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5197](https://github.com/CrocSwap/integer-mult-bounds/pull/5197) | hevlyo | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5198](https://github.com/CrocSwap/integer-mult-bounds/pull/5198) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5199](https://github.com/CrocSwap/integer-mult-bounds/pull/5199) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5200](https://github.com/CrocSwap/integer-mult-bounds/pull/5200) | thu-nmrc | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5201](https://github.com/CrocSwap/integer-mult-bounds/pull/5201) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5202](https://github.com/CrocSwap/integer-mult-bounds/pull/5202) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5203](https://github.com/CrocSwap/integer-mult-bounds/pull/5203) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5204](https://github.com/CrocSwap/integer-mult-bounds/pull/5204) | krzysztofwojt | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5205](https://github.com/CrocSwap/integer-mult-bounds/pull/5205) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5206](https://github.com/CrocSwap/integer-mult-bounds/pull/5206) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5207](https://github.com/CrocSwap/integer-mult-bounds/pull/5207) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5208](https://github.com/CrocSwap/integer-mult-bounds/pull/5208) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5209](https://github.com/CrocSwap/integer-mult-bounds/pull/5209) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5210](https://github.com/CrocSwap/integer-mult-bounds/pull/5210) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5211](https://github.com/CrocSwap/integer-mult-bounds/pull/5211) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5212](https://github.com/CrocSwap/integer-mult-bounds/pull/5212) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5213](https://github.com/CrocSwap/integer-mult-bounds/pull/5213) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5214](https://github.com/CrocSwap/integer-mult-bounds/pull/5214) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5215](https://github.com/CrocSwap/integer-mult-bounds/pull/5215) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5216](https://github.com/CrocSwap/integer-mult-bounds/pull/5216) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5217](https://github.com/CrocSwap/integer-mult-bounds/pull/5217) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5218](https://github.com/CrocSwap/integer-mult-bounds/pull/5218) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5219](https://github.com/CrocSwap/integer-mult-bounds/pull/5219) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5220](https://github.com/CrocSwap/integer-mult-bounds/pull/5220) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5221](https://github.com/CrocSwap/integer-mult-bounds/pull/5221) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5222](https://github.com/CrocSwap/integer-mult-bounds/pull/5222) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5223](https://github.com/CrocSwap/integer-mult-bounds/pull/5223) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5224](https://github.com/CrocSwap/integer-mult-bounds/pull/5224) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5225](https://github.com/CrocSwap/integer-mult-bounds/pull/5225) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5226](https://github.com/CrocSwap/integer-mult-bounds/pull/5226) | DreamingOfClouds | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5227](https://github.com/CrocSwap/integer-mult-bounds/pull/5227) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5228](https://github.com/CrocSwap/integer-mult-bounds/pull/5228) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5229](https://github.com/CrocSwap/integer-mult-bounds/pull/5229) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5231](https://github.com/CrocSwap/integer-mult-bounds/pull/5231) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5232](https://github.com/CrocSwap/integer-mult-bounds/pull/5232) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5233](https://github.com/CrocSwap/integer-mult-bounds/pull/5233) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5234](https://github.com/CrocSwap/integer-mult-bounds/pull/5234) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5235](https://github.com/CrocSwap/integer-mult-bounds/pull/5235) | zxv | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5237](https://github.com/CrocSwap/integer-mult-bounds/pull/5237) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5238](https://github.com/CrocSwap/integer-mult-bounds/pull/5238) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5239](https://github.com/CrocSwap/integer-mult-bounds/pull/5239) | krzysztofwojt | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5240](https://github.com/CrocSwap/integer-mult-bounds/pull/5240) | apoursh | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5241](https://github.com/CrocSwap/integer-mult-bounds/pull/5241) | Clear1nsight | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5242](https://github.com/CrocSwap/integer-mult-bounds/pull/5242) | krzysztofwojt | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5243](https://github.com/CrocSwap/integer-mult-bounds/pull/5243) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5244](https://github.com/CrocSwap/integer-mult-bounds/pull/5244) | 1337isnot1337 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5245](https://github.com/CrocSwap/integer-mult-bounds/pull/5245) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5246](https://github.com/CrocSwap/integer-mult-bounds/pull/5246) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5247](https://github.com/CrocSwap/integer-mult-bounds/pull/5247) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5248](https://github.com/CrocSwap/integer-mult-bounds/pull/5248) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5249](https://github.com/CrocSwap/integer-mult-bounds/pull/5249) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5250](https://github.com/CrocSwap/integer-mult-bounds/pull/5250) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5251](https://github.com/CrocSwap/integer-mult-bounds/pull/5251) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5252](https://github.com/CrocSwap/integer-mult-bounds/pull/5252) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5253](https://github.com/CrocSwap/integer-mult-bounds/pull/5253) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5254](https://github.com/CrocSwap/integer-mult-bounds/pull/5254) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5255](https://github.com/CrocSwap/integer-mult-bounds/pull/5255) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5256](https://github.com/CrocSwap/integer-mult-bounds/pull/5256) | ssafwann | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5259](https://github.com/CrocSwap/integer-mult-bounds/pull/5259) | lee-phys | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5260](https://github.com/CrocSwap/integer-mult-bounds/pull/5260) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5262](https://github.com/CrocSwap/integer-mult-bounds/pull/5262) | krzysztofwojt | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5265](https://github.com/CrocSwap/integer-mult-bounds/pull/5265) | Chrisbryan17 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5267](https://github.com/CrocSwap/integer-mult-bounds/pull/5267) | ssafwann | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5268](https://github.com/CrocSwap/integer-mult-bounds/pull/5268) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5272](https://github.com/CrocSwap/integer-mult-bounds/pull/5272) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5273](https://github.com/CrocSwap/integer-mult-bounds/pull/5273) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5274](https://github.com/CrocSwap/integer-mult-bounds/pull/5274) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5275](https://github.com/CrocSwap/integer-mult-bounds/pull/5275) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5276](https://github.com/CrocSwap/integer-mult-bounds/pull/5276) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5277](https://github.com/CrocSwap/integer-mult-bounds/pull/5277) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5278](https://github.com/CrocSwap/integer-mult-bounds/pull/5278) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5279](https://github.com/CrocSwap/integer-mult-bounds/pull/5279) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5280](https://github.com/CrocSwap/integer-mult-bounds/pull/5280) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5281](https://github.com/CrocSwap/integer-mult-bounds/pull/5281) | unpaidmoon | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5282](https://github.com/CrocSwap/integer-mult-bounds/pull/5282) | Matarener | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5283](https://github.com/CrocSwap/integer-mult-bounds/pull/5283) | zxv | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5284](https://github.com/CrocSwap/integer-mult-bounds/pull/5284) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5285](https://github.com/CrocSwap/integer-mult-bounds/pull/5285) | Matarener | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5286](https://github.com/CrocSwap/integer-mult-bounds/pull/5286) | kumagi | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5287](https://github.com/CrocSwap/integer-mult-bounds/pull/5287) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5288](https://github.com/CrocSwap/integer-mult-bounds/pull/5288) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5292](https://github.com/CrocSwap/integer-mult-bounds/pull/5292) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5295](https://github.com/CrocSwap/integer-mult-bounds/pull/5295) | kumagi | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5296](https://github.com/CrocSwap/integer-mult-bounds/pull/5296) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5298](https://github.com/CrocSwap/integer-mult-bounds/pull/5298) | Matarener | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5299](https://github.com/CrocSwap/integer-mult-bounds/pull/5299) | Matarener | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5301](https://github.com/CrocSwap/integer-mult-bounds/pull/5301) | flyingviper | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5304](https://github.com/CrocSwap/integer-mult-bounds/pull/5304) | lee-phys | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5306](https://github.com/CrocSwap/integer-mult-bounds/pull/5306) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5307](https://github.com/CrocSwap/integer-mult-bounds/pull/5307) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5308](https://github.com/CrocSwap/integer-mult-bounds/pull/5308) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5309](https://github.com/CrocSwap/integer-mult-bounds/pull/5309) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5310](https://github.com/CrocSwap/integer-mult-bounds/pull/5310) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5311](https://github.com/CrocSwap/integer-mult-bounds/pull/5311) | aliromman | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5312](https://github.com/CrocSwap/integer-mult-bounds/pull/5312) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5313](https://github.com/CrocSwap/integer-mult-bounds/pull/5313) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5315](https://github.com/CrocSwap/integer-mult-bounds/pull/5315) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5316](https://github.com/CrocSwap/integer-mult-bounds/pull/5316) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5317](https://github.com/CrocSwap/integer-mult-bounds/pull/5317) | Matarener | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5318](https://github.com/CrocSwap/integer-mult-bounds/pull/5318) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5319](https://github.com/CrocSwap/integer-mult-bounds/pull/5319) | kumagi | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5320](https://github.com/CrocSwap/integer-mult-bounds/pull/5320) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5321](https://github.com/CrocSwap/integer-mult-bounds/pull/5321) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5322](https://github.com/CrocSwap/integer-mult-bounds/pull/5322) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5323](https://github.com/CrocSwap/integer-mult-bounds/pull/5323) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5324](https://github.com/CrocSwap/integer-mult-bounds/pull/5324) | flyingviper | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5325](https://github.com/CrocSwap/integer-mult-bounds/pull/5325) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5326](https://github.com/CrocSwap/integer-mult-bounds/pull/5326) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5327](https://github.com/CrocSwap/integer-mult-bounds/pull/5327) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5328](https://github.com/CrocSwap/integer-mult-bounds/pull/5328) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5329](https://github.com/CrocSwap/integer-mult-bounds/pull/5329) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5330](https://github.com/CrocSwap/integer-mult-bounds/pull/5330) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5331](https://github.com/CrocSwap/integer-mult-bounds/pull/5331) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5332](https://github.com/CrocSwap/integer-mult-bounds/pull/5332) | JoyboyBrian | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5333](https://github.com/CrocSwap/integer-mult-bounds/pull/5333) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5339](https://github.com/CrocSwap/integer-mult-bounds/pull/5339) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5340](https://github.com/CrocSwap/integer-mult-bounds/pull/5340) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5341](https://github.com/CrocSwap/integer-mult-bounds/pull/5341) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5342](https://github.com/CrocSwap/integer-mult-bounds/pull/5342) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5343](https://github.com/CrocSwap/integer-mult-bounds/pull/5343) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5344](https://github.com/CrocSwap/integer-mult-bounds/pull/5344) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5345](https://github.com/CrocSwap/integer-mult-bounds/pull/5345) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5346](https://github.com/CrocSwap/integer-mult-bounds/pull/5346) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5347](https://github.com/CrocSwap/integer-mult-bounds/pull/5347) | Matarener | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5348](https://github.com/CrocSwap/integer-mult-bounds/pull/5348) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5349](https://github.com/CrocSwap/integer-mult-bounds/pull/5349) | ahrazzle | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5350](https://github.com/CrocSwap/integer-mult-bounds/pull/5350) | ahrazzle | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5351](https://github.com/CrocSwap/integer-mult-bounds/pull/5351) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5352](https://github.com/CrocSwap/integer-mult-bounds/pull/5352) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5353](https://github.com/CrocSwap/integer-mult-bounds/pull/5353) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5356](https://github.com/CrocSwap/integer-mult-bounds/pull/5356) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5357](https://github.com/CrocSwap/integer-mult-bounds/pull/5357) | mihir-s-05 | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5358](https://github.com/CrocSwap/integer-mult-bounds/pull/5358) | mihir-s-05 | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5359](https://github.com/CrocSwap/integer-mult-bounds/pull/5359) | mihir-s-05 | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5360](https://github.com/CrocSwap/integer-mult-bounds/pull/5360) | mihir-s-05 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5361](https://github.com/CrocSwap/integer-mult-bounds/pull/5361) | flyingviper | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5362](https://github.com/CrocSwap/integer-mult-bounds/pull/5362) | mihir-s-05 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5363](https://github.com/CrocSwap/integer-mult-bounds/pull/5363) | mihir-s-05 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5364](https://github.com/CrocSwap/integer-mult-bounds/pull/5364) | mihir-s-05 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5365](https://github.com/CrocSwap/integer-mult-bounds/pull/5365) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5366](https://github.com/CrocSwap/integer-mult-bounds/pull/5366) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5367](https://github.com/CrocSwap/integer-mult-bounds/pull/5367) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5368](https://github.com/CrocSwap/integer-mult-bounds/pull/5368) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5369](https://github.com/CrocSwap/integer-mult-bounds/pull/5369) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5370](https://github.com/CrocSwap/integer-mult-bounds/pull/5370) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5371](https://github.com/CrocSwap/integer-mult-bounds/pull/5371) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5372](https://github.com/CrocSwap/integer-mult-bounds/pull/5372) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5373](https://github.com/CrocSwap/integer-mult-bounds/pull/5373) | flyingviper | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5374](https://github.com/CrocSwap/integer-mult-bounds/pull/5374) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5375](https://github.com/CrocSwap/integer-mult-bounds/pull/5375) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5376](https://github.com/CrocSwap/integer-mult-bounds/pull/5376) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5377](https://github.com/CrocSwap/integer-mult-bounds/pull/5377) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5378](https://github.com/CrocSwap/integer-mult-bounds/pull/5378) | aliromman | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5379](https://github.com/CrocSwap/integer-mult-bounds/pull/5379) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5380](https://github.com/CrocSwap/integer-mult-bounds/pull/5380) | zxv | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5382](https://github.com/CrocSwap/integer-mult-bounds/pull/5382) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5383](https://github.com/CrocSwap/integer-mult-bounds/pull/5383) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5384](https://github.com/CrocSwap/integer-mult-bounds/pull/5384) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5385](https://github.com/CrocSwap/integer-mult-bounds/pull/5385) | ahrazzle | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5386](https://github.com/CrocSwap/integer-mult-bounds/pull/5386) | ahrazzle | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5387](https://github.com/CrocSwap/integer-mult-bounds/pull/5387) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5388](https://github.com/CrocSwap/integer-mult-bounds/pull/5388) | dillona | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5389](https://github.com/CrocSwap/integer-mult-bounds/pull/5389) | aliromman | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5390](https://github.com/CrocSwap/integer-mult-bounds/pull/5390) | Dugongue | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5391](https://github.com/CrocSwap/integer-mult-bounds/pull/5391) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5392](https://github.com/CrocSwap/integer-mult-bounds/pull/5392) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5393](https://github.com/CrocSwap/integer-mult-bounds/pull/5393) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5394](https://github.com/CrocSwap/integer-mult-bounds/pull/5394) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5395](https://github.com/CrocSwap/integer-mult-bounds/pull/5395) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5396](https://github.com/CrocSwap/integer-mult-bounds/pull/5396) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5397](https://github.com/CrocSwap/integer-mult-bounds/pull/5397) | zxv | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5398](https://github.com/CrocSwap/integer-mult-bounds/pull/5398) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5399](https://github.com/CrocSwap/integer-mult-bounds/pull/5399) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5400](https://github.com/CrocSwap/integer-mult-bounds/pull/5400) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5401](https://github.com/CrocSwap/integer-mult-bounds/pull/5401) | zxv | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5402](https://github.com/CrocSwap/integer-mult-bounds/pull/5402) | dillona | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) · [record 2](../../docs/research/pr-intake-evidence/pr5413/PROOF-REVIEW.md) |
| [#5403](https://github.com/CrocSwap/integer-mult-bounds/pull/5403) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5404](https://github.com/CrocSwap/integer-mult-bounds/pull/5404) | zxv | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5405](https://github.com/CrocSwap/integer-mult-bounds/pull/5405) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5406](https://github.com/CrocSwap/integer-mult-bounds/pull/5406) | zxv | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5407](https://github.com/CrocSwap/integer-mult-bounds/pull/5407) | Clear1nsight | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) · [record 2](../../docs/research/pr-intake-evidence/pr5413/PROOF-REVIEW.md) |
| [#5408](https://github.com/CrocSwap/integer-mult-bounds/pull/5408) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5409](https://github.com/CrocSwap/integer-mult-bounds/pull/5409) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5410](https://github.com/CrocSwap/integer-mult-bounds/pull/5410) | jwr404 | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5411](https://github.com/CrocSwap/integer-mult-bounds/pull/5411) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5412](https://github.com/CrocSwap/integer-mult-bounds/pull/5412) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5413](https://github.com/CrocSwap/integer-mult-bounds/pull/5413) | Clear1nsight | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) · [record 2](../../docs/research/pr-intake-evidence/pr5413-promotion/PROMOTION.md) · [record 3](../../docs/research/pr-intake-evidence/pr5413/PROOF-REVIEW.md) |
| [#5414](https://github.com/CrocSwap/integer-mult-bounds/pull/5414) | Clear1nsight | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) · [record 2](../../docs/research/pr-intake-evidence/pr5413/PROOF-REVIEW.md) |
| [#5415](https://github.com/CrocSwap/integer-mult-bounds/pull/5415) | zxv | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5416](https://github.com/CrocSwap/integer-mult-bounds/pull/5416) | NicholasStone | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5417](https://github.com/CrocSwap/integer-mult-bounds/pull/5417) | jwr404 | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5418](https://github.com/CrocSwap/integer-mult-bounds/pull/5418) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5419](https://github.com/CrocSwap/integer-mult-bounds/pull/5419) | zxv | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5420](https://github.com/CrocSwap/integer-mult-bounds/pull/5420) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5421](https://github.com/CrocSwap/integer-mult-bounds/pull/5421) | aliromman | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5422](https://github.com/CrocSwap/integer-mult-bounds/pull/5422) | Matarener | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5423](https://github.com/CrocSwap/integer-mult-bounds/pull/5423) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5424](https://github.com/CrocSwap/integer-mult-bounds/pull/5424) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5425](https://github.com/CrocSwap/integer-mult-bounds/pull/5425) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5426](https://github.com/CrocSwap/integer-mult-bounds/pull/5426) | Matarener | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5427](https://github.com/CrocSwap/integer-mult-bounds/pull/5427) | Matarener | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5428](https://github.com/CrocSwap/integer-mult-bounds/pull/5428) | zxv | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5429](https://github.com/CrocSwap/integer-mult-bounds/pull/5429) | Clear1nsight | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5430](https://github.com/CrocSwap/integer-mult-bounds/pull/5430) | NicholasStone | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5432](https://github.com/CrocSwap/integer-mult-bounds/pull/5432) | hevlyo | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5433](https://github.com/CrocSwap/integer-mult-bounds/pull/5433) | Matarener | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5434](https://github.com/CrocSwap/integer-mult-bounds/pull/5434) | Matarener | incorporated | [record 1](../../docs/research/pr-intake-decisions.json) |
| [#5435](https://github.com/CrocSwap/integer-mult-bounds/pull/5435) | Matarener | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |
