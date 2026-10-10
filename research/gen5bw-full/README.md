κ = 7.51154847341386e-4

# gen5bw-full: every stage re-derived fresh on the weighted gen5b word

**Conditional κ = 375577423670693 / (5·10¹⁷) = 7.51154847341386·10⁻⁴**, +1.43·10⁻⁸ (+0.0019%) over PR #305's
7.51140529238897·10⁻⁴ and +0.0105% over PR #275's 7.51075693834608·10⁻⁴.

PR #305 (eumemic) translated PR #300's 1,734 kernel entries and 87 second-descent gates onto George Lydakis' weighted
gen5b word (PR #275) by logical helper roles. This package is #305's package with every selection **re-derived on the
weighted word itself** by the same discovery scripts, plus a longer randomized packing search:

| stage | PR #305 (translated from #300) | this package (fresh on the weighted word) |
| --- | ---: | ---: |
| collective kernel entries (`discovery/coll`, `pack_restarts.py`, 450 restarts, seed 21) | 1,734, rank 2,196, φ −3,860 | **1,738** (920 pairs, 427 triples, 391 quadruples), rank **2,200**, φ **−3,880.5** |
| second constructed-frame descent (`descent4g`) | 87 gates | **90 gates** (delta {1: +39, 2: +153, 3: −81, 4: −51, 5: +27, 7: −48, 9: +24, 12: −24, 14: +24, 18: −39, 19: +39}) |
| early restorations | 440 | 440 (cut at record 757,373) |
| terminal sinks | 8 (R 15,424) | 8 (R 15,424) |
| weighted ADDs | 721,422 | 721,470 → 721,442 after the sinks |

The twin/collective census of the weighted word is identical to gen5b's (952 pairs, 2,104 triples, 3,807 quadruples
with a common cut and nondegenerate common entrance; plain greedy φ −3,799.13, 1,720 entries); the gain comes from the
packing search and from the descent being run on the actual kernel word. Transforms, checkers, the pins plumbing, the
bank tiling and #275's weighted virtual word and producer are unchanged from #305; `expected/kernel-pins.json` and
`MANIFEST.json` are regenerated; `discovery/build_restore_selection.py` and `build_sink_selection.py` run the second
descent before their screens as in #300.

```sh
python -m pip install -r research/gen5bw-full/requirements.txt    # sympy 1.14.0
python3 -B research/gen5bw-full/verify.py --output /tmp/gen5bw-full-verification   # about 7 minutes; not under -I
```

Prints `PASS_IMMUTABLE_GEN5_KERNEL_RESTORE_SINK_FIVE_STAGE_BANKED_CONSTRUCTION` with the pinned κ. Conditional finite
construction under the retained public all-size hypotheses, exactly as #275/#300/#305; no Lean build. #305's README and
PROOF are kept as `README-PR305.md`, `PROOF-PR305.md`. Prepared by Rohan Arun with Anthropic Claude assistance;
Apache-2.0; lineage in `NOTICE.md`.
