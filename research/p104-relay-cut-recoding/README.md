# Recoding cuts on the role-1256 relay

The 16-stage signed P104 application gives **conditional $\kappa\ge 0.00374039009039$**. The lower bound exceeds the upper endpoint of the #7704 parent by **0.00001034832006** (0.27743%). The preceding #7674 contribution gained 0.0000041662072 over its own parent. The present increment is 2.48 times that gain. The selected #7000 reference on the pinned main branch is 0.00363005817. Scientific admission of the new construction requires independent review. [Parent and its tighter bracket](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19708867) · [Previous contribution](https://github.com/CrocSwap/integer-mult-bounds/pull/7674) · [Selected review](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/docs/research/pr-intake-evidence/pr7000-application/PROOF-REVIEW.md)

| Quantity | Role-1256 graph | This graph |
| --- | ---: | ---: |
| Paid transfers per native invocation | 6,143 | 6,121 |
| Paid jobs across the full caller | 101,840 | 101,488 |
| Productive jobs across the full caller | 21,152 | 21,152 |
| Paid rank mass | 271,568 | 271,568 |
| Productive rank mass | 272,896 | 272,896 |
| Local scalar terms per invocation | 172,414 | 177,531 |
| Numerical homes per invocation | 9,150 | 9,128 |
| Charged scalar services across the full caller | 122,001,408 | 124,542,464 |
| Directed raw crossing | (0.00373004177032, 0.00373004177033) | (0.00374039009047, 0.00374039009048) |

## Construction

Start with SYLforge's nine-swap word and Clear1nsight's contracted role-1256 relay. The certificate gives 22 paid-edge eliminations, 21 grouped reroutes and three reroutes that construct a signal from banks at two different charts. Six of the 24 reroutes change two incoming signals together. The last five eliminations use the recoded graph. The sequence uses the banked pivot method of #7674 and the grouped hub method of DreamingOfClouds, who applied it to the 1,502-owner chart-595 graph in #7705. Each of the 46 witnesses here applies to the 1,501-owner relay graph at its position in the sequence. [Source word](https://github.com/CrocSwap/integer-mult-bounds/pull/7700) · [Role-1256 relay](https://github.com/CrocSwap/integer-mult-bounds/pull/7704) · [Grouped hubs](https://github.com/CrocSwap/integer-mult-bounds/pull/7705) · [Ordered witnesses](CUTS.json)

A short example starts with cut 40. It sends the sum of two existing banks from chart 722 to chart 778. Chart 778 already holds the missing summand. This changes two rank-two jobs into jobs of ranks three and one. Cut 42 replaces those two jobs by one rank-four job. Another example, cut 38, uses a receiver correction with determinant five. It recovers the desired signal exactly, including division by five, on the checked integer grid. [Proof and examples](PROOF.md) · [Even-numbered cut receipts](results/witness-1.json)

## Verification and cost

The replay reconstructs the parent from its raw chronological word and its published relay contract. It checks the rational identity for each cut on independent inputs and the fully phased operator for each of 3,023 ordered native or helper chart pairs. For the 54 distinct pairs rerouted at surviving paid slots it also checks all 512 forward and all 512 adjoint columns. The 104 main-port adapters and 1,664 port-stage bindings pass the exact signed contact check. The forward sweep verifies all 1,501 public rows with 9,280,471 exact coefficient products. A separate reverse sweep compares all 1,501 parent and candidate columns. [Replay manifest](VERIFY.json) · [Reverse-column receipt](results/witness-0.json)

Across all 16 stages, the changes to the paid histogram at ranks one through seven are $(-288,+48,-368,+96,+80,+48,+32)$. All target counts agree with the parent. The integer concave-tariff test certifies a strict cost decrease for every power $r^t$ with $0<t<1$. Two directed power evaluations bracket the new crossing. The compiler consumes the stricter interior value 0.00374039009046. All 54 strict and four functional outer inequalities pass. The same physical replay charges the increased number of local terms, typed transfers and full resets. Finite-size runtime and a materialized full multiplier remain open. [Full signed invoice, physical costs and outer gates](results/application.json)

## Reproduce

Use Python 3.12 with the standard library. Run the eight registered commands from the repository root.

```sh
python3.12 -B scripts/research_package.py --package research/p104-relay-cut-recoding
```

To inspect the complete candidate graph independently, run the constructor from the repository root. It writes canonical JSON to standard output. Its SHA-256 is `db10e4ca7154b454f86bf404bc34b3a16d02de6cc008d5227e4eef2654cb0778`. The reconstructed parent must first match `8e7b755bd2d2d387bc3d3adfe48100985adf74775ca5acbb143170a3d16b5ccf` under the parent serializer.

```sh
python3.12 -I -B research/p104-relay-cut-recoding/recoding.py > /tmp/p104-relay-cut-graph.json
```

## Open next questions

- Can one receiver solve for two independent missing signals at once? Start with two directions at an actual middle chart. Check the rank of the receiver's $2\times2$ system and direct every surviving dependency to an available bank. A complete, cheaper invoice is still required.
- Can an independent implementation reproduce cuts 38 and 40 from the pinned parent? Compare every public row, then join the final graph to the charged physical schedule and the signed caller. This would address the new work that needs scientific review.

Ali Romman prepared this work with substantial OpenAI Codex assistance. The source manifests bind each reused file and preserve the original notices. New work uses Apache-2.0. [Attribution](NOTICE) · [External source pins](SOURCE-PINS.json) · [Canonical inputs](SOURCES.json) · [Coordination](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19709868)
