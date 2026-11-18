# Role-230 rank redistribution on the fifteen-pivot banked caller

The role-230 correction gives **conditional κ ≥ 0.0037261023899** on Ali Romman's frozen fifteen-pivot banked graph from [#7674](https://github.com/CrocSwap/integer-mult-bounds/pull/7674). The lower point exceeds the matched #7674 upper endpoint `0.00372604555572` by **0.00000005683418**. The candidate retains all fifteen pivot witnesses, all 1,501 public operators, the literal 16-stage caller, and 15,290 numerical private homes per native invocation. Both graphs use the same complete exact common-root and physical bank contract under the five selected assumptions. [Proof](PROOF.md) · [Independent price](evidence/INDEPENDENT-PRICE.json)

| Identity | SHA-256 or exact commit |
|---|---|
| #7674 refreshed head | `28b2af322a1fab01b3734365988930920f9dda48` |
| #7674 scientific source | `26b6c469aa6c4aa04322ce25a22150f90e5fb14e` |
| Shared #7669 source word | `ee251f6005d2a92b887c5b804bd7aac05989d278b2c9ccb3c3091b50d533b08d` |
| Reconstructed #7674 baseline graph | `d81ec9f47740852a4bf7bd83100feff5cb66b70e1973466e1609bbac8af75098` |
| Reconstructed recharted graph | `1f082936ada08b5138b7d13e33368bd21c6f46632c5319a348e2f2a8e0021150` |
| Shared caller after decompression | `62d94fb992acab0a71c3d12f22be4ce63f4f65e5cbe3f420b93aa1393ffa8dcf` |

The role-230 graph changes source MOVE keys 97471 and 102393. The two rank-three paid edges become a rank-four and a rank-two edge. Across sixteen invocations, the full paid deltas are `{2:+16,3:−32,4:+16}`. All target ranks, 101,824 paid positions, 21,152 productive outputs and rank-mass surplus 1,328 are preserved. The child raw crossing is `(0.0037261023900, 0.0037261023901)`. Its six additional scalar terms per native invocation and all complete-view stock and movement costs enter the paired bill. [Wire result](evidence/WIRE-RESULT.json) · [Full invoices](evidence/INVOICES.json) · [Provider cost](evidence/PROVIDER-RESULT.json)

## Reproduction

Use Linux CPython 3.12 and the standard library. The package carries one copy each of the frozen #7674 source word inputs, caller and pivot list. Both banked graphs are rebuilt in scratch. SHA-256 and Git blob bindings identify each module and input. [Exact pivots](peer/PIVOTS.json) · [Asset manifest](ASSETS.json)

```sh
python3.12 -I -B verify.py integrity
python3.12 -I -B verify.py paired --out /path/to/new-paired-directory
python3.12 -I -B verify.py native --out /path/to/new-native-directory
```

`paired` checks fifteen saved signals, both exact wire directions, complete caller prices, physical costs and all 54 strict and four functional outer predicates. `native` checks the 3,025 forward ordered-chart pairs, five additional pivot directions, 104 main boundaries, and both whole banked tapes at two primes. It includes all 512 forward and adjoint columns for 19 changed or unbound pairs. Both stages run rejecting controls using the actual frozen graph. The registered schedule allocates 680 seconds. [Replay checklist](INPUTS.md) · [Native evidence](evidence/NATIVE-RESULT.json)

The two optional saved-witness controls reproduce an endpoint-preserving sign error at the third pivot (residual −8) and a missing chart-912 reader correction (output change 1/12). [Controls and standalone replay](witness-controls/README.md)

## Open next questions

- Can some of the banked snapshots share backing? Start from each literal donor's last read, then prove safe reuse through both forwarded child returns and the retained same-owner public installations. [Banked predecessor proof](https://github.com/aliromman/integer-mult-bounds/blob/26b6c469aa6c4aa04322ce25a22150f90e5fb14e/research/p104-banked-transfer-pivots/PROOF.md)
- A separately rounded supplier needs an exact reachable congruence or its own charged error proof. A one-tick residual in the chart-912 saved row at slot 97471 gives a nonintegral `−1/3` pre-product at row 101174. [Exact-root proof](PROOF.md#exact-common-root-and-bank-costs)

## Credit

The source hierarchy, scoped contribution and the separate ToikY CI bridge are recorded in [NOTICE](NOTICE). Ali Romman supplied the fifteen-pivot banked baseline and the common-grid context used here. SYLforge supplied the exact #7669 caller and source word with DreamingOfClouds and the contributors recorded in the preserved notices. The distinct change in this package is the one source-pinned role-230 transfer, its exact compatibility with the unchanged pivots and the matched accounting and verification. Clear1nsight prepared it with substantial OpenAI Codex assistance. [Pinned predecessor](peer/NOTICE) · [Parent provenance](peer/source/7669-CREDITS.md)
