# A conditional multiplication saving of 0.00385896148992

The complete P104 multiplier gives **κ ≥ 0.00385896148992** under the five assumptions of the selected framework. Its complex price changes sign between 0.00385932267587 and 0.00385932267588. The new ordinary BIT supplier supports 0.00385896149. [Complex circuit and application](complex/PROOF.md) · [Binary circuit and application](BIT-PROOF.md)

| Comparison | Earlier upper endpoint | Gain to the new conditional lower |
| --- | ---: | ---: |
| Previous contribution, PR 7756 | 0.00382063778177 | 0.00003832370815 |
| Concurrent contribution, PR 7774 | 0.00385068874155 | 0.00000827274837 |

The gain over PR 7756 is 15.70% larger than its preceding gain of 0.00003312268681. The new lower point is 1.00307% above PR 7756's upper endpoint. Nine of PR 7774's ten paid replacements work on the new graph. Two matching changes at their new senders remove another two paid transfers. The proof charges each replacement once. [PR 7756](https://github.com/CrocSwap/integer-mult-bounds/pull/7756) · [PR 7774](https://github.com/CrocSwap/integer-mult-bounds/pull/7774) · [Coordination and source history](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19721588)

## Reproduce

Use CPython 3.12 and its standard library from the repository root.

```sh
python3.12 -B scripts/research_package.py --package research/p104-dual-supplier-lift
```

The four registered checks reconstruct the two suppliers and verify the complete finite application. The first run checks 400 main fields and 864 independent helper returns, the 48-call schedule, ordinary work, and the price inequalities. It also checks the crossing with an independent integer-square-root calculation. The other three runs check the signed chart operators, their absolute phase and the main ports. [Commands](VERIFY.json) · [Computed receipts](complex/RESULT.json)

## Open next questions

- Can a second reviewer follow one changed paid transfer from its three-term source through its corrected returns? Start with peer edit 1 and its single-coefficient omission witness. [Edit proof](complex/PROOF.md#paid-restorations) · [Omission witnesses](complex/relays/OMISSIONS.json)
- Can an independent review trace the 24-bit scalar basis, the four bounded scale factors and the ordinary BIT bootstrap through the common precision tape? [Complex physical proof](complex/PROOF.md#physical-operator-and-ordinary-cost) · [Binary proof](BIT-PROOF.md) · [Structured questions](TASK.json)

## Credit

Ali Romman prepared the new binary supplier, native graph, closed caller and integration with substantial OpenAI Codex assistance. The graph uses published restorations by Clear1nsight and bank and compiler work by DreamingOfClouds. The detailed proofs credit the authors of the inherited circuits, chart engines and conditional framework. Independent scientific review is open. [Complex credits](complex/PROOF.md#credit) · [Binary credits](BIT-PROOF.md#attribution-and-remaining-work)
