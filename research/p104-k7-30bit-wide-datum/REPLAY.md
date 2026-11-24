# Local replay

Scientific commit: the package as committed on this branch (pins: `INPUTS.json`, `source/wide/ASSEMBLY.json`).

Environment: CPython 3.12.14 (uv build), Linux x86-64, 32 cores. Each mode ran with `python3.12 -IB research/p104-k7-30bit-wide-datum/verify.py <mode>` inside a bubblewrap sandbox. The sandbox had no network, a read-only root, and write access only to the scratch directory, with `TMPDIR` set to scratch.

| Mode | Exit | Wall s | Peak RSS GiB |
| --- | ---: | ---: | ---: |
| `inputs` | 0 | 0.0 | 0.02 |
| `price` | 0 | 24.4 | 0.75 |
| `calendar` | 0 | 295.3 | 15.62 |
| `raw` | 0 | 28.6 | 0.49 |
| `exterior` | 0 | 34.3 | 0.92 |
| `nested` | 0 | 45.2 | 2.29 |
| `product` | 0 | 32.0 | 0.19 |
| `setup` | 0 | 23.7 | 0.33 |
| `census` | 0 | 9.8 | 0.44 |

The `calendar` peak comes from `check_stage_seam.verify_stage` at stage 6. It materializes the 30-bit scanned field `2^2147520000` and the compiled field `2^(round(9·(2^30−1)))`.

Before the new layer was added, the unchanged #8098 package (`research/p104-10shortcut-child-tariff`) passed all of its modes in the same sandbox: price, calendar, raw, exterior, nested, product, setup and census.

Registered runner: `python3.12 -IB scripts/research_package.py --package research/p104-k7-30bit-wide-datum`, run in the same sandbox, printed `PASS_REGISTERED_RESEARCH_PACKAGE research/p104-k7-30bit-wide-datum outcome=completed`. It took 479.3 s wall time with 15.6 GiB peak RSS.
