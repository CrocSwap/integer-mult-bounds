# Executed validation

Executed on 2026-10-13 with Windows / CPython 3.14, in the isolated
round-16 worktree at base `2921874911956718fcaaaf9396fe8267b3cfa9f0`.

| Command from repository root | Result |
| --- | --- |
| `python -B research/nine-stage-prefix-audit-seed70/verify.py --write` | PASS; initial exact receipt recording |
| `python -I -O -B research/nine-stage-prefix-audit-seed70/verify.py` | PASS; complete deterministic receipt comparison with assertions disabled in the new verifier |
| `python -B research/nine-stage-prefix-audit-seed70/verify.py` | PASS; ordinary replay of the saved receipt |
| `python -B scripts/verify_selected_result.py` | PASS; unchanged selected record, exact kappa, source inventory and proof supplement |
| `make verify` | Unavailable: this Windows environment reports `make` is not recognized |
| `git diff --cached --check` | PASS for the ten new package files |

The receipt binds exactly five required consumed files by SHA-256. Text
pins normalize CRLF to LF; the gzip word pin uses exact bytes. Removing
a pin cannot disable verification. The source exporter executes in a
separate isolated Python process without optimization, so its inherited
assertions remain enabled under an optimized parent. Its temporary output
is inside the owned package and its resolved parent is checked before
automatic cleanup. An initial default-Windows-temp permission failure
was resolved by this local scratch placement; it was not a mathematical
failure or a reason to weaken a source check.

All 27,234 source records are reconstructed by the original exporter.
Deleting their 2,911 MOVEs yields exactly the independently expanded
24,305 ADDs and nine COPY/ERASE pairs. The complete schedule checks all
220,905 scalar events and all 4,839 independent Boolean input columns,
including 3,951 distinct helper columns. The positive scalar replay and
three-coefficient model are separately maintained and compared at every
local event. Bridge monotonicity covers each individual port update.
The independent schedule matches the actual consumed recipe, and its
coarse result equals evaluation of the actual pinned prefix expression.

All 23 rejection controls pass: two false endpoint/local precision
shortcuts, the omission of arbitrary helper dirt, each of eighteen
bridge shears, a missing source pin and a corrupted word digest. The
zero-helper positive maximum is
`73031471119030478673328582981162819048`, strictly below the required
arbitrary-helper maximum. The eighteen bridge controls replay the
complete Boolean program, not only an eight-by-eight surrogate.

This is finite scalar audit evidence. Native compilation, hosted CI,
the full repository suite, physical cover/hosting replay, outer error
reassembly and all-size theorem closure were not run or established.
Production still uses its existing 192-bit charge. Only the new package
is changed; selected and predecessor files are unchanged.
