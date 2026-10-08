# Aligned frame composition

The frozen conditional finite witness certifies **κ = 52789616935221/1000000000000000000 = 5.2789616935221e-5**, with bit saving **10558480765231/200000000000000000**. This is about **2^(-14.2093862772)** and **37.2695587404% above the original PR36 κ=384569/10^10**. Exact fractions are authoritative; decimals and percentages are displays. It is approximately **0.01415763596% above reported PR74** at `428b5c167686b42a83f1abf7003c6d17aec561ea`. The reported external construction is a working baseline, not independently producer-replayed here.

| Quantity | This witness |
|---|---:|
| h23 / h25 auxiliary roles | 26,387 / 34,772 |
| Physical width W | 130,417,912 |
| Total recursive rank | 74,988,452,500 |
| Rank deficit | 1,846,900 |
| Largest child / parent dimension | 529 / 575 |
| Bit wire bits / row coefficient | 27 / 843 |

The selected vectors `['first6',1,1]` and `['first9',1,1,2]` use six/nine anchored pairs, depth-coarse word `hhh`, PR74 node order and its updated coordinate maps. h23 uses baseline output order, identity oracle pricing and zero three-cycle passes. h25 uses late output order, coordinate-aware prices and three passes (60 accepted three-cycles). Future-compatible completion, exact retired/pending indexes and next-use prices remain enabled; bounded single/two-cycle exchange passes remain three.

```sh
make aligned-composition-verify
make verify
make formal-historical-verify
```

The focused gate regenerates both pre-permutation and final words byte-for-byte, reconstructs dense scalar supports, replays all ordinary and arbitrary-dirty basis columns in both orientations, computes fresh actual-frame CRT profiles and checks the complete paid child list. Two independent rational moment enclosures, 47 strict inequalities, seven margins, next-grid rejection and adverse controls are retained. The additive Lean module proves 197 rational arithmetic theorems and exposes its external physical/analytic/all-size hypotheses.

The [proof](PROOF.md) supplies general compatibility arguments, finite evidence and exact scope. Expert review should focus on the inherited all-size framed/residual compiler and fixed-tape implementation; analytic/prime/precision/recovery transfer; and the finite-profile interface plus Lean's external real-log/exp hypotheses. Arithmetic cutoffs are not full operational thresholds and no practical speedup is asserted.

The complete immutable PR88 construction and original contributor archives are retained. The 59,045-pair finite search has two equivalent winners and does not prove global optimality. Discovery paths are provenance only; executable verification uses repository-relative inputs.

Source credits: @eumemic [#57](https://github.com/CrocSwap/integer-mult-bounds/pull/57) and [#69](https://github.com/CrocSwap/integer-mult-bounds/pull/69), reversible compilation and balanced coarse sums; @rohangar1 [#59](https://github.com/CrocSwap/integer-mult-bounds/pull/59), split recursion; @ikeboy [#62](https://github.com/CrocSwap/integer-mult-bounds/pull/62), interval strips and core-aware assembly; @DominikScholz [#63](https://github.com/CrocSwap/integer-mult-bounds/pull/63) and [#68](https://github.com/CrocSwap/integer-mult-bounds/pull/68), ranked composition and pending live controls; @rohanarun [#65](https://github.com/CrocSwap/integer-mult-bounds/pull/65), [#67](https://github.com/CrocSwap/integer-mult-bounds/pull/67) [#78](https://github.com/CrocSwap/integer-mult-bounds/pull/78) and [#82](https://github.com/CrocSwap/integer-mult-bounds/pull/82), exact refined assembly, profile-cost reclamation, coordinate-flag search and coordinate-aware pricing; @alejandrozu [#70](https://github.com/CrocSwap/integer-mult-bounds/pull/70), carry exchanges; Thomas DiFiore (@tomdif) [#74](https://github.com/CrocSwap/integer-mult-bounds/pull/74), aligned firstK partition, multi-pair anchoring, depth-dependent coarse sums, original rank-first order and coordinate relabeling; @chafreaky [#60](https://github.com/CrocSwap/integer-mult-bounds/pull/60), [#71](https://github.com/CrocSwap/integer-mult-bounds/pull/71), [#79](https://github.com/CrocSwap/integer-mult-bounds/pull/79) [#84](https://github.com/CrocSwap/integer-mult-bounds/pull/84), [#88](https://github.com/CrocSwap/integer-mult-bounds/pull/88) and this composition, rank-preserving tie orders, three-donor cycles, ranked reclamation, anchored splits, future completion, integer scoring, exact indexes, two-cycles, output routing, search and certification.

Chafik Boukhalfa prepared this package with OpenAI Codex assistance. Original contributor, OpenAI/manuscript, Apache-2.0, and AI-assistance notices remain attached. In particular Avi Eisenberg's Claude assistance and the original contributors' OpenAI disclosures are retained verbatim in the archives. PR78 inspires coordinate-flag search; the selected maps here come from the pinned updated PR74 source.
