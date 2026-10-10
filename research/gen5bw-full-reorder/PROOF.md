# gen5bw-full-reorder — verification chain

**Conditional κ = 375736057005951 / (5·10¹⁷) = 7.51472114011902·10⁻⁴**, +1.32·10⁻⁸ over PR #306's
7.51458925311258·10⁻⁴, +3.32·10⁻⁷ over PR #305, +3.96·10⁻⁷ over PR #275.

This is PR #306's package (eumemic's #305 composition on George Lydakis' weighted gen5b word, plus chafreaky's two
reorder stages) with the kernel, second-descent, restoration and sink selections replaced by the ones re-derived on
the weighted word in PR #307 (`gen5bw-full`), and the two reorder selections re-screened on that word by #306's own
`discovery/build_reorder_selection.py`:

| stage | #306 | this package |
| --- | ---: | ---: |
| collective kernel entries (450-restart packing, `discovery/coll/pack_restarts.py`) | 1,734, rank 2,196, φ −3,860 | **1,738**, rank **2,200**, φ **−3,880.5** |
| second constructed-frame descent | 87 gates | **90 gates** |
| early restorations / terminal sinks | 440 / 8 | 440 / 8 (R 15,424) |
| reorder (#299/#306 stage, screened on this word) | 237 moves, φ −495.07 | 234 moves, delta {2: +234, 3: −214, 4: −22, 5: +2, 6: −20, 8: +20, 21: −212, 22: +212}, φ −493.29 |
| reorder2 (screen re-run on the reordered word) | 2 moves, φ −1.18 | 2 moves, delta {2: +2, 3: −2, 4: −2, 5: +2}, φ −1.18 |
| κ | 7.51458925311258·10⁻⁴ | **7.51472114011902·10⁻⁴** |

Transforms, checkers, the pins plumbing, bank tiling, #275's weighted virtual word and producer are byte-identical to
#306; the six selection files, `expected/kernel-pins.json` and `MANIFEST.json` are the changed inputs, every changed
count a recomputed pin. The twin/collective census of the weighted word is identical to gen5b's; the gain over #306 is
the packing search and the descent run on the actual kernel word (as in #307), carried through the reorder stages.

```sh
python -m pip install -r research/gen5bw-full-reorder/requirements.txt    # sympy 1.14.0
python3 -B research/gen5bw-full-reorder/verify.py --output /tmp/gen5bw-full-reorder-verification   # about 7 minutes; not under -I
```

Prints `PASS_IMMUTABLE_GEN5_KERNEL_RESTORE_SINK_FIVE_STAGE_BANKED_CONSTRUCTION` with the pinned κ (14 fresh stages,
14 omitted-stage controls). Conditional finite construction under the retained public all-size hypotheses, exactly as
#275/#305/#306; no Lean build. #306's and #305's README/PROOF are kept as `README-PR306.md`, `PROOF-PR306.md`,
`README-PR305.md`, `PROOF-PR305.md`. Prepared by Rohan Arun with Anthropic Claude assistance; Apache-2.0; lineage in
`NOTICE.md`.
