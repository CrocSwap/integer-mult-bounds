# Validation record

Author replays of `research/p104-third-anchor-clean-mixed-root` on CPython 3.12.10, Windows, using the
commands registered in `VERIFY.json`, run directly (no per-command cap). All exit 0.

| Run | Result | Wall time |
|---|---|---|
| `python -B verify.py --write-result` | all stages PASS; wrote `RESULT.json` | 8m03s |
| `python -B verify.py` (exact comparison with `RESULT.json`) | `PASS_THIRD_ANCHOR_CLEAN_MIXED_ROOT_COMPOSITION_KAPPA_003287014` | 19m12s |
| `python -O -B verify.py` | same marker | 11m34s |

Stages: regenerated native word, ownership, zero scratch and 799 columns; native absolute phases and 7,488
physical mixed contacts; both price engines, complete compiler, precision and outer ledger, and all controls.

Limits: author checks only. The five inherited framework assumptions remain (`native_all_columns`,
`owned_erasure`, `compiler`, `precision_tape`, `analytic_recovery`). Hosted CI had not been run when this record was
written. The shadow rows for owned labels 779-781 are zero in the transposed preparation but not at the forward
CLEAR (inherited `owned_erasure` obligation, as in PR6372); only the cache row 782 is declared zero scratch.
The verifier's `--build-only` mode is a development shortcut that exits 0 with a `_BUILD` marker and runs
neither the native phases nor the price; it is not registered in `VERIFY.json`.
