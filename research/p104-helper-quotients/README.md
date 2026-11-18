# Removing paid transfers and helper returns together

The 16-stage signed P104 application gives **conditional κ ≥ 0.00376154487703**. This lower bound exceeds the upper endpoint of PR #7708 by **0.00002115478655 (0.56558%)**. The preceding gain over #7704 was 0.00001034832006. The new increment is 2.04 times as large. The selected #7000 reference at the pinned main commit is 0.00363005817. [Predecessor](https://github.com/CrocSwap/integer-mult-bounds/pull/7708) · [Selected scientific review](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/docs/research/pr-intake-evidence/pr7000-application/PROOF-REVIEW.md)

| Quantity | PR #7708 | This construction |
| --- | ---: | ---: |
| Independent native helpers per call | 1,101 | 1,068 |
| Paid native transfers per call | 6,121 | 6,054 |
| Local scalar terms per call | 177,531 | 175,927 |
| Numerical storage locations per call | 9,128 | 8,995 |
| Paid jobs across 16 calls | 101,488 | 100,416 |
| Productive jobs across 16 calls | 21,152 | 20,624 |
| Paid rank mass | 271,568 | 268,368 |
| Productive rank mass | 272,896 | 269,696 |
| Charged scalar services | 124,542,464 | 123,312,128 |
| Directed raw crossing | (0.00374039009047, 0.00374039009048) | (0.00376154487711, 0.00376154487712) |

At each step, give up one independent helper and impose a linear relation among inputs at the same chart. Several receiver banks already contain that linear form. Each receiver can now reconstruct one paid return from its other banks. For example, giving up the rank-nine return for helper 264 removes three paid transfers of ranks two, four and three. The signed bill benefits because, for every exponent strictly between zero and one, the three separate jobs cost more than the single lost target. [Worked example and general proof](PROOF.md) · [33 explicit restrictions](QUOTIENTS.json)

The verifier checks all 67 receiver identities on independent inputs before each restriction. It also checks all 1,468 final rows, all 1,468 input columns, 2,962 phased chart pairs, 104 main ports and 1,664 port-stage contacts. The forward execution uses the actual compact graph, including its integer divisions, guarded storage, typed transfers and resets. At #7708’s upper endpoint, the new productive-minus-paid margin lies between 7.41141029282 and 7.41141029283. [Relation and reverse-column receipt](results/witness.json) · [Complete price and physical receipt](results/application.json)

## Reproduce

Run the five registered checks from the repository root with Python 3.12 and its standard library.

```sh
python3.12 -B scripts/research_package.py --package research/p104-helper-quotients
```

To obtain the exact compact graph, run the constructor. The SHA-256 of its output is `16e99893a2c669467ce74f214e8eb5150402f0267aaa8d67aad5d870aa4d5c18`. The program folds the supplied nine-swap word, applies the role-1256 contraction and replays all 46 parent cuts. The parent graph must match the published SHA-256 `db10e4ca7154b454f86bf404bc34b3a16d02de6cc008d5227e4eef2654cb0778`.

```sh
python3.12 -I -B research/p104-helper-quotients/quotient.py > /tmp/p104-helper-quotients.json
```

## Scope

The result inherits five scientific interfaces from #7000. They cover the native operator family, owned erasure, compilation, precision on tape and analytic recovery. Independent scientific review, a materialized full multiplier and practical finite-size runtime remain open. [Selected assumptions](vendor/selected-claim.json) · [Compiler gates](results/application.json)

## Open next questions

- Can a two-dimensional restriction remove a paid return that either constraint alone leaves necessary? Start with two surviving helpers at one entrance chart. Account for both lost targets.
- Can an independent implementation recover the three relations for helper 264 and the first transposed restriction, for helper 559? Check the compact endpoint map and the full price after both orientations. [Review handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19710820)

Ali Romman prepared the new construction and software with substantial OpenAI Codex assistance. The package retains the supplier notices and source pins. New work uses Apache-2.0. [Attribution](NOTICE) · [Source pins](SOURCE-PINS.json)
