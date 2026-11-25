# Local replay

Scientific commit: the package as committed on this branch (pins: `INPUTS.json`, `source/wide/ASSEMBLY.json`).

Environment: CPython 3.12.15 (uv build, `cpython-3.12-linux-x86_64-gnu`), Linux x86-64, 16 cores, 62 GiB RAM. Modes run with `python3.12 -IB research/p104-k7-31bit-wide-datum/verify.py <mode>` directly in the worktree. No network wrapping; pinning is by `INPUTS.json` and `source/wide/ASSEMBLY.json` hashes.

| Mode | Exit | Wall s | Peak RSS GiB |
| --- | ---: | ---: | ---: |
| `inputs` | 0 | 0.10 | 0.02 |
| `price` | 0 | 57.28 | 1.28 |
| `calendar` | 0 | 1268.79 | 30.70 |
| `raw` | 0 | 71.49 | 0.49 |
| `exterior` | 0 | 89.35 | 0.92 |
| `nested` | 0 | 114.58 | 2.29 |
| `product` | 0 | 84.12 | 0.19 |
| `setup` | 0 | 59.60 | 0.33 |
| `census` | 0 | 23.78 | 0.44 |

All nine modes (including `inputs`) passed once at this head. The `calendar` mode is the heavyweight: `check_stage_seam.py` replays the 31-bit six-stage literal seam at stage 6 and materials the stage-6 scanned field `2^(9·H_6)`. It peaked at about 32 GiB RSS (30.7 GiB) and needs about 22 minutes here. The 30-bit predecessor (#8099) logged price 24.4 s (0.75 GiB), calendar 295.3 s (15.62 GiB), raw 28.6 s (0.49 GiB), exterior 34.3 s (0.92 GiB), nested 45.2 s (2.29 GiB), product 32.0 s (0.19 GiB), setup 23.7 s (0.33 GiB), census 9.8 s (0.44 GiB).

The `calendar` figure above is the exact full-mode peak (the seam process alone peaked at ~26.4 GiB inside the mode). A later run of `census` and every other mode stayed in the low single-digit GiB.
