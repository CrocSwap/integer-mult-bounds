# Executed validation

2026-10-13, base `f567884aeb8851b6e794af1184119a3bfbe1e631`.
Python 3.14.6; macOS 26.5.2 arm64; Apple Clang 17.0.0;
Boost 1.87.0 headers downloaded into temporary storage from
`https://archives.boost.io/release/1.87.0/source/boost_1_87_0.tar.bz2`,
archive SHA256 `af57be25cb4c4f4b413ed692fe378affb4352ea50fbe294a11ef548f4d527d89`.
No installed system dependency or upstream source was modified.

Executed checks:

- `python3 -I -B research/r439-frame519-seed02/search.py`: complete domain,
  minima 16+16, 8,192 states and 49,152 state/destination pairs. A second
  regeneration matched the exact candidate bytes (SHA256
  `dbc98e37719ff3a034c164a44a141346146ddd70f0276766e5ee7554ff515821`).
- `python3 -I -B research/r439-frame519-seed02/verify.py`: passed. Separate
  integer subset-sum/Bellman optimum replay, exact integer factor/product
  maps, 4,096 Boolean inputs, 661 symbolic dirty-input columns, identical
  frame paths, pinned owning lattice/frame/interface check, exact record
  invoice and all 11 mutation controls. Optimized `python3 -O -I -B` also passed.
- `BOOST_INCLUDE=/private/tmp/boost_1_87_0 python3 -I -B research/r439-frame519-seed02/native.py`:
  unchanged native legality and full 883/1,327/1,549-column replays passed
  for both base and candidate; original five-stage and parameterized
  five-stage receipts agree field for field after path/time normalization.
  All 96 distinct per-word omitted-bridge controls were rejected, plus the
  even-coefficient, self-add and bad-COPY-rank controls on the actual stream.
- External certificate corruption (reverse bound 1,031,082 changed to
  1,031,083) failed with `certificate mismatch`; an expected xcheck source
  hash changed to zero failed with `source pin mismatch`. Both files were
  restored exactly after their controls.
- `python3 -I -B scripts/verify_selected_result.py`: selected record, source
  inventory and proof supplement passed. The initial exploratory import had
  produced a Python cache in the selected package; moving that generated
  cache to temporary storage restored its exact inventory. All subsequent
  checks used `-B`.
- Whitespace and tracked-source preservation checks passed before submission.
- Final upstream fetch still reports the exact experimental base. Final PR
  metadata refresh identified PR904's partial interval overlap; its pinned
  certificate was inspected and credited in the README.

One native harness run caught a JSON representation mismatch in the new
wrapper: the unchanged checker's integer-key map is an array of pairs.
Correcting the wrapper to compare that representation allowed the complete
replay to finish. This was a harness exception, not a mathematical failure.

`make verify` and the selected construction's cold replay were not run:
they regenerate and replay unrelated historical/selected constructions.
This self-contained circuit contribution runs the affected checks above and
does not change any selected supplier input or bound. No fresh global hosting,
outer assembly, remote CI, all-size theorem or Lean pass is claimed.

All deterministic mathematical receipt fields are retained in
`CERTIFICATE.json` and `NATIVE-CERTIFICATE.json`; only native elapsed seconds
and temporary stream paths are removed. `native.py --work PATH` preserves
the regenerated word, raw records, compiled checkers, complete local native
receipts and environment file for inspection.
