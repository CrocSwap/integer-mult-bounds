# Source-bound complete-price oracle (local review draft)

This package contains the pure Python standard-library oracle, schema, synthetic contract controls, immutable three-profile calibration, and two actual independently evidenced admission views. No producer is imported or replayed by the consumer. `policy.json` is reviewer-maintained trusted input; the oracle proves compatibility with the pinned evidence, not the physical truth of arbitrary prose.

The #5383 view `joined-v5` has label FUNDED_CONDITIONAL at 151333/50000000 = .00302666. The #5387 view `joined-5387-v4` has label FUNDED_CONDITIONAL at 605334953/200000000000 = .003026674765. Both have 64148 paid / 10800 productive, but different words, physical proofs, scalar charges, precision constants, compiler savings and heights. The #5387 view is freshly physically checked; the rejected ordering-only transfer is not used.

All results retain exactly native_all_columns, owned_erasure, compiler, precision_tape, analytic_recovery. This local draft has no publication/hosted-CI or selected transition. The frozen #4610/#5377 calibration imports retain their previously established statuses and source pins independently.

Run from this package directory:

```sh
python3 -B test_oracle.py
python3 -B calibrate.py
python3 -B check_join.py joined-v5
python3 -B check_join.py joined-5387-v4
```

These are compatibility, exact rational comparison and immutable evidence checks, completing in under one second. They do not repeat any native, root, compiler, phase or cold scientific replay. `CONTRACT.md` explains API usage and the trust boundary. Every SHA-addressed raw artifact retains its exact bytes; `origins.json` records its source path. The separate upstream independently implemented engine and producer receipts remain credited in those frozen artifacts.

The only admitted compiler tuple is power1024/cutoff20/floor21/u1/5/theta63/64/logpower1000. The two reserve/tested/height points have individual exact receipts. This does not certify the suggested27tuplegrid or a global optimum across changed words and physical allocations. Positive necessary screens always remain MODEL_ONLY.

Ali Romman owns the eight-relation construction; Dugongue owns the #5387 successor. Preserve Cao Yifan, Cinna Davis, zxv, Jacob Alan Sussman, ToikY, ordinary-BIT contributors and every retained source notice. New adapter and review by Chris R / Clear1nsight with substantial OpenAI Codex assistance. Root owns publication of this local draft.
