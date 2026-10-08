# Indexed two-cycles with balanced multi-splits and coordinate flags

The frozen finite conditional witness has **κ = 261356445457/5000000000000000 = 5.22712890914e-5**, with bit saving **408390793141/7812500000000000**. This is about **0.8494742%** above the reported PR74 value at `3f78d8967c009153f2df5c6a6577b6ab1d37e2ca`, observed 2026-10-08. This is a historical pinned comparison, not a claim about the current community frontier. The complete pinned PR74 and PR79 recursive profiles are strictly excluded at the new accepted bit saving.

| Quantity | This witness |
|---|---:|
| h23 auxiliary roles | 26,834 |
| h25 auxiliary roles | 35,348 |
| Physical width W | 132,466,108 |
| Total recursive rank | 76,166,165,200 |
| Rank deficit | 1,846,900 |
| Largest child / parent dimension | 529 / 575 |
| Bit wire bits / row coefficient | 27 / 843 |

Additional reported comparisons observed on 2026-10-08: PR81 at `acae4964aef41c69f3c57e72a45e76afc4d4934d` reports κ=5.1915547765237e-5; PR82 at `3410b940aa26e5876202152dfa7c4f66451ee22c` reports κ=5.203279888519e-5. This frozen witness is about 0.4583459% above the reported PR82 value. These are metadata comparisons only; their foreign producers were not replayed. Exact rational ratios and authors are recorded in `reported-comparisons.json`.

Both axes use balanced coarse columns when `i+j<ng-1` and rows elsewhere, anchored point orders, PR74 node order followed by natural region execution, pending next-use scoring, future unit completion, and up to three single-exchange and three two-cycle passes. h23 uses split vector `[4,1,1]` and baseline output order; h25 uses `[1,4,1]` and late-use output order. Code 4 splits the first and middle eligible pairs, retaining strict contraction. Coordinate relabeling is cyclic shift one for h23 and the pinned PR74 permutation for h25. Every operation and frame raise is charged after relabeling.

```sh
make indexed-cycle-verify
make verify
```

The focused gate regenerates the parent and relabeled word bytes, replays every ordinary and arbitrary-dirty basis column in both orientations, reconstructs actual frame transitions, and regenerates the fixed-I+J/CRT profile. It composes every paid child, checks independent exact moment enclosures, excludes the next 10^-18 bit and κ grid points, and verifies all 47 strict inequalities and seven margins. Five actual-source audits exercise basis completion, both indexes, single exchanges and two-cycles. Physical/configuration/source mutations are rejected.

The [proof and scope](PROOF.md) states the algebra and inherited assumptions. The result remains conditional on the inherited ordered residual compiler, all-size recursion, finite scalar overhead, routing, prime selection, recovery, fixed-tape simulation and analytic transfer. Arithmetic cutoffs are not full operational thresholds. No full multiplication implementation, global optimum, practical speedup or complete formal multiplication theorem is asserted.

The engine and PR74 function extracts are byte-identical to the frozen 56-file R5 discovery bundle. The immutable PR79 construction archive contains its entire 250-file source/finite-input closure and arithmetic evidence. PR74 and PR78 contributor inputs retain original licenses and notices. `discovery-selection.json` preserves original provenance paths; executable verification uses repository-relative files only. `pin_indexed_cycle_sources.py` explicitly maintains the source closure; derived arithmetic and validation receipts are excluded to avoid circular inputs.

Source credits: @eumemic [#57](https://github.com/CrocSwap/integer-mult-bounds/pull/57) and [#69](https://github.com/CrocSwap/integer-mult-bounds/pull/69), reversible compilation and balanced coarse sums; @rohangar1 [#59](https://github.com/CrocSwap/integer-mult-bounds/pull/59), split recursion; @ikeboy [#62](https://github.com/CrocSwap/integer-mult-bounds/pull/62), interval strips and core-aware assembly; @DominikScholz [#63](https://github.com/CrocSwap/integer-mult-bounds/pull/63) and [#68](https://github.com/CrocSwap/integer-mult-bounds/pull/68), ranked composition and pending live controls; @rohanarun [#65](https://github.com/CrocSwap/integer-mult-bounds/pull/65), [#67](https://github.com/CrocSwap/integer-mult-bounds/pull/67) and [#78](https://github.com/CrocSwap/integer-mult-bounds/pull/78), exact refined assembly, profile-cost reclamation and coordinate-flag search; @alejandrozu [#70](https://github.com/CrocSwap/integer-mult-bounds/pull/70), carry exchanges; Thomas DiFiore (@tomdif) [#74](https://github.com/CrocSwap/integer-mult-bounds/pull/74), exact node order, coordinate relabeling and the selected h25 permutation; @chafreaky [#60](https://github.com/CrocSwap/integer-mult-bounds/pull/60), [#71](https://github.com/CrocSwap/integer-mult-bounds/pull/71), [#79](https://github.com/CrocSwap/integer-mult-bounds/pull/79) and this composition, ranked reclamation, anchored splits, future completion, integer scoring, exact indexes, two-cycles, output routing, search and certification.

Chafik Boukhalfa prepared this package with OpenAI Codex assistance. Original contributor, OpenAI/manuscript, Apache-2.0, and AI-assistance notices remain attached. In particular Avi Eisenberg's Claude assistance and the original contributors' OpenAI disclosures are retained verbatim in the archives. PR78 inspires the coordinate search; its published selected permutations are not claimed as the selected permutations here.
