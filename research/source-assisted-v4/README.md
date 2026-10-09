# Source-assisted complex word on PR168 v4 modules

This package applies the [PR184](https://github.com/CrocSwap/integer-mult-bounds/pull/184) source-parity local word and source-assisted frame flow to the PR168 v4 query modules. PR184 used the older PR168 snapshot `fd25adb7fbaa12ee761d02c733c54d1d2a7687ee`. The newer modules give a stronger complex supplier, and the complex side binds.

| Quantity | PR184 (fd25adb7 modules) | This package (v4 modules) |
| --- | ---: | ---: |
| Physical auxiliaries `R` | 11,056 | 10,824 |
| Persistent roles `W` | 13,696 | 13,464 |
| Source-controlled erasures | 1,410 | 1,412 |
| Zero-fresh kernel reuses | 706 | 707 |
| Complex saving | 6.570752e-4 | 6.630702e-4 |
| κ | 6.566436e-4 | **6.626307e-4** |

The bit supplier, finite bridge and 47-constraint assembly are PR184's, unchanged. The result is κ = 6626307/10^10 = 0.0006626307, about 0.1126% above PR186 (0.000661885549259598). The exact values are in `certificate.json`.

Run from the repository root with Python assertions enabled:

```sh
python3 -m pip install -r research/source-assisted/requirements-round13.txt
python3 -B research/source-assisted-v4/verify.py
```

The verifier checks `SOURCE.json`, regenerates the PR168 v4 complex cache with `scripts/paired_cube_producer.py`, and builds the source-parity word with `source_aligned_local_v4.py`. It then runs PR184's unchanged `complex_frame_flow.py` and `exact_complex_flow_lift.py`, this package's copy of PR184's contract checker, and PR184's unchanged `assemble_profiles.py`. It compares the canonical result with `certificate.json`. Scratch files go to `.work/` inside this package, and the verifier deletes them at the end.

See [PROOF.md](PROOF.md) for the claim, the changes, and the scope.
