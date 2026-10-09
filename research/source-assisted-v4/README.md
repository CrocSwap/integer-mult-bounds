# Source-assisted complex word on PR168 v4 modules

This package applies the [PR184](https://github.com/CrocSwap/integer-mult-bounds/pull/184) source-parity local word and source-assisted frame flow to the PR168 v4 query modules. PR184 used the older PR168 snapshot `fd25adb7fbaa12ee761d02c733c54d1d2a7687ee`. The newer modules and a new choice of donor/recipient pairs give a much stronger complex supplier.

| Quantity | PR184 (fd25adb7 modules) | PR191 (v4 modules) | This version (v4 modules, new pairs) |
| --- | ---: | ---: | ---: |
| Physical auxiliaries `R` | 11,056 | 10,824 | 9,412 |
| Persistent roles `W` | 13,696 | 13,464 | 12,052 |
| Source-controlled erasures | 1,410 | 1,412 | 0 |
| Zero-fresh kernel reuses | 706 | 707 | 0 |
| Complex saving | 6.570752e-4 | 6.630702e-4 | 7.009184e-4 |
| κ | 6.566436e-4 | 6.626307e-4 | **6.647872e-4** |

This version changes one more input: the donor/recipient pairs. PR184 matches donors to recipients with a plain maximum matching. Here `source_aligned_local_v4.py --avoid-parity-erasure` picks a full matching that avoids pairs which PR184's parity purification would erase. The flow then needs 1,412 fewer dirty births, and the complex saving rises to 7.009184e-4.

The complex supplier no longer binds. PR184's effective bit saving, 6.652294768530547e-4, now limits κ. The result is κ = 103873/156250000 = 0.0006647872, about 0.438% above PR186 (0.000661885549259598) and 0.325% above PR191. The bit supplier, finite bridge and 47-constraint assembly are PR184's, unchanged. The exact values are in `certificate.json`.

Run from the repository root with Python assertions enabled:

```sh
python3 -m pip install -r research/source-assisted/requirements-round13.txt
python3 -B research/source-assisted-v4/verify.py
```

The verifier checks `SOURCE.json`, regenerates the PR168 v4 complex cache with `scripts/paired_cube_producer.py`, and builds the source-parity word with `source_aligned_local_v4.py`. It then runs PR184's unchanged `complex_frame_flow.py` and `exact_complex_flow_lift.py`, this package's copy of PR184's contract checker, and PR184's unchanged `assemble_profiles.py`. It compares the canonical result with `certificate.json`. Scratch files go to `.work/` inside this package, and the verifier deletes them at the end.

See [PROOF.md](PROOF.md) for the claim, the changes, and the scope.
