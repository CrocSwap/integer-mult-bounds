# Attribution

Ali Romman supplied `#8042`, `#8057`, and `#8055`; SYLforge supplied `#8052` (the retimed K7 binary circuit setting `BINARY_C = 4391986206293/2^50`); ToikY supplied `#8073` (`0.003898219753506`) and `#8076` (`CHILD_TARIFF = 2401/1024`, contraction `2400/2401`, geometric sum `2401`, entry `+5` / terminal `+3m` clock bounds); Clear1nsight supplied `#8081`/`#8084` (`eta = 1/256` and the 25-bit setup lemma) and `#8089` (`kappa = 0.0039` with full `256/255` reserve); floration supplied `#8088` (`w5669_shortcut5.json.gz`, 5 chart-3 relay shortcuts and 44 chart-3 re-encodings), `#8090` (`0.003900826966095`), and `#8094` (27-bit 5-stage `0.003900857267786`).

This package contributes:
1. Five additional exact pure-identity chart-3 relay shortcuts (`104494..104498`) unlocked by `#8088`'s 44 chart-3 re-encodings, producing `w5664_shortcut10.json.gz` (`5664` moves, independently checked via 3-prime forward/transpose equivalence, 25M-term exact `literal_grid`, and 2,961-pair Clifford catalogue).
2. A 3-type `(1, 2, 3)` Gaussian producer with weights `(1, 45, 2025)` on `w5664`, lifting `GAUSSIAN_C` to `17166573920/2^42 = 0.003903227006958` while keeping `actual_roles = 1,002,096 < 2^20` and `grade_count = 72 < 2^8`.
3. The exact periodic-integral `(1 - delta)` matched-interval suffix theorem paired with `#8076`'s `2401/1024` child tariff while **retaining the full `256/255` summation reserve** (no `#8082` reserve drop), lowering `ORDINARY_DEBIT` to `1418665/2^20` (`< #8094`'s `1420718/2^20`).
4. A 6-stage `eta = 1/256` schedule reaching the exact sharp `w = 2^38` fixed datum ceiling (`H < 2^28`, [`SETUP-28BIT.md`](SETUP-28BIT.md)), achieving conditional **`kappa = 0.003900862325217`** (`complete_log2_C = 171,810,078,109`, `G = 52,270`) and strictly beating `#8073`, `#8076`, `#8088`, `#8089`, `#8090`, and `#8094` at every matched tier.

The archived source and notices retain their original license.
