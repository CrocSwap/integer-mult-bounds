# Source-assisted complex word on PR168 v4 modules

This package applies the [PR184](https://github.com/CrocSwap/integer-mult-bounds/pull/184) source-parity local word and source-assisted frame flow to the PR168 v4 query modules. PR184 used the older PR168 snapshot `fd25adb7fbaa12ee761d02c733c54d1d2a7687ee`. The newer modules and a new choice of donor/recipient pairs give a much stronger complex supplier. The bit supplier starts with the face-diagonal bit word of [PR189](https://github.com/CrocSwap/integer-mult-bounds/pull/189) (chafreaky), then applies the 102-operation endpoint-frame descent recorded in `research/paired-cube-twin-local-168/bit/frame-descent.json`. Its priced saving is then passed through the two finite ordinary-leaf levels from [PR185](https://github.com/CrocSwap/integer-mult-bounds/pull/185), using the recurrence first applied to PR189 in [PR199](https://github.com/CrocSwap/integer-mult-bounds/pull/199).

## Complex supplier

| Quantity | PR184 (fd25adb7 modules) | PR191 (v4 modules) | PR193 and this version (v4 modules, new pairs) |
| --- | ---: | ---: | ---: |
| Physical auxiliaries `R` | 11,056 | 10,824 | 9,412 |
| Persistent roles `W` | 13,696 | 13,464 | 12,052 |
| Source-controlled erasures | 1,410 | 1,412 | 0 |
| Zero-fresh kernel reuses | 706 | 707 | 0 |
| Complex saving | 6.570752e-4 | 6.630702e-4 | 7.009184e-4 |

PR193 changed the donor/recipient pairs. PR184 matches donors to recipients with a plain maximum matching. Here `source_aligned_local_v4.py --avoid-parity-erasure` picks a full matching that avoids pairs which PR184's parity purification would erase. The flow then needs 1,412 fewer dirty births.

## Bit supplier and κ

The complex saving is 219037/312500000 = 0.0007009184, so the bit side binds. The descended physical profile retains R = 17,554, W = 21,074, deficit 1,936. PR184's exact pricing gives bit coarse saving `C = 1670897/2500000000` and initial effective saving `a_0 = 6679380665463285737/10^22`. Applying the exact recurrence `a_(j+1) = (1-C)C + C a_j` twice gives the ordinary leaf used by the unchanged assembly. The source word's Boolean operations and terminal sink writes are unchanged; the committed operation frames use the actual physical donor/gauge/recipient chain order.

| Version | Bit supplier | Binding side | κ |
| --- | --- | --- | ---: |
| PR191 | PR184 | complex | 6.626307e-4 |
| PR193 | PR184 | bit | 6.647872e-4 |
| PR194 baseline | PR189 | bit | 6.674324e-4 |
| PR199 | PR189 + finite leaf bootstrap | bit | 6.678525e-4 |
| this version | PR189 + 102 frame lowerings + depth-2 bootstrap | bit | **6.679123e-4** |

The result is κ = 6679123/10000000000 = 0.0006679123, an exact gain of 299/5000000000 over PR199 and 4799/10000000000 over PR194's 1668581/2500000000. The bit coarse saving is certified at PR189's finer 10^-18 precision as 167089706787281/250000000000000000 before PR184's 10^-10-grid pricing. Exact recurrence and assembly values are in `certificate.json`. PR197 claims a higher 0.000676080316519385 on another bit supplier, so this package does not claim the public record.

Run from the repository root with Python assertions enabled:

```sh
python3 -m pip install -r research/source-assisted/requirements-round13.txt
python3 -B research/source-assisted-v4/verify.py
```

The verifier checks `SOURCE.json`, regenerates the PR168 v4 complex cache with `scripts/paired_cube_producer.py`, and builds the source-parity word with `source_aligned_local_v4.py`. It then runs PR184's unchanged `complex_frame_flow.py` and `exact_complex_flow_lift.py`, this package's copy of PR184's contract checker, and `assemble.py`. It compares the canonical result with `certificate.json`. PR189's own `python3 -B research/paired-cube-twin-local-168/verify.py` regenerates the bit certificate that `assemble.py` reads; the workflow runs both. The finite leaf wrapper dependency and its proof inputs are source-pinned. Scratch files go to `.work/` inside this package, and the verifier deletes them at the end.

See [PROOF.md](PROOF.md) for the claim, the changes, and the scope.
