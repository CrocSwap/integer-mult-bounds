# Validation record

Executed on macOS arm64, 2026-10-14 Australia/Melbourne, with CPython 3.14.6
and 3.12.12. This is local evidence; no Linux run or GitHub CI result is claimed.

| Check | Observed result |
|---|---|
| `python3 -B -I research/chirp-symbolic-seed80/verify.py` | PASS; entire deterministic receipt matched |
| `python3 -B -I -O research/chirp-symbolic-seed80/verify.py` | PASS; checks remain active with assertions disabled |
| `python3 -B -I -O research/chirp-symbolic-seed80/test_verify.py` | Eight test groups pass |
| Same verifier and tests with `/opt/homebrew/bin/python3.12` | PASS; same receipt and eight test groups |
| Minimal package copied into an unrelated temporary directory containing spaces | Optimized isolated CLI passes; no Git checkout or external dependency is needed |
| Changed source bytes, incomplete source closure, changed receipt count | All rejected by the CLI |
| Existing destination passed to `--write` | Rejected; existing content preserved |
| `make selected-record-check` | PASS at the exact base; selected PR890 rational and bindings unchanged |
| Staged-files-only Git archive in a temporary path with spaces | Optimized verifier and all eight test groups pass |
| `git diff --cached --check` | PASS; all changes are additions within this package |
| Patch checked against refreshed main `018418fd789ce12a8c176279fe012138713ff53d` using a separate index | PASS; no target overlap or merge required |

The receipt is `EXPECTED.json`, SHA-256
`f245ccc40f5c0032a86cd4c1784f35bf092ed75de40409d8cc4377d53a81cceb`.
It contains 27 symbolic patterns, 587 state equalities, 8,605 small-state
transitions in 129 boxes, 21 wide transitions, 16 concrete rejecting controls,
and two accepted equivalent rewrites. Ten controls reject symbolically; six
require the exact initialization/representative layer. The tests evaluate the
polynomial engine against ordinary integer arithmetic on 625 expression/input
combinations, including negative inputs, and exercise explicit guard/modulus
rejection. Counts describe this declared domain only.

No production generator or selected supplier changed. Accordingly the full
repository `make verify`, selected supplier cold replay, and PR479's full
historical verifier were not rerun. The new package's exact checks and the
selected-record integrity check are the affected validation. This does not
establish PR479's outer cost row, numerical exponential, physical tape schedule,
or any new multiplication exponent.
