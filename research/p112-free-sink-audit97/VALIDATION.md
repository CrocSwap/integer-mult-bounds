# Executed validation

Environment: Windows, CPython 3.14.5, standard library only. Commands run
from the isolated round-09 checkout at base
`2921874911956718fcaaaf9396fe8267b3cfa9f0` on 2026-10-13.

| Command | Result |
|---|---|
| `python -I -B research/p112-free-sink-audit97/verify.py --write` | Generated exact certificate |
| `python -I -O -B research/p112-free-sink-audit97/verify.py` | PASS, 28,560 alternatives, zero free, 112 self controls |
| `python -I -O -B research/p112-free-sink-audit97/independent.py` | PASS, 4,030 Fraction-checked minors; ranks 7:448, 8:28112 |
| `python -I -O -B research/p112-free-sink-audit97/test_package.py` | PASS, six mathematical and five package rejection controls |
| `python -I -B scripts/verify_selected_result.py` | PASS, selected kappa 1661960547713947/1000000000000000000 unchanged |
| `git diff --cached --check` | PASS before commit |

The independent checker shares the source-pin and geometry-literal readers.
Its code-space enumeration uses set closure rather than the producer's
greedy binary basis. Its Fraction determinant implementation does not call
the producer's modular row selection or integer Bareiss determinant. It
rechecks coverage for every target-deleted support and the rank-seven upper
bounds, rather than trusting only the final count.

The first prototype incorrectly expected every support to have rank eight;
exact generation exposed the eight omitted-coordinate patterns, leading to
the explicit rank-seven upper bounds. The first saved-receipt comparison
also caught numeric-vs-string histogram-key sorting; canonical JSON now
normalizes object keys before sorting. Both corrected paths passed the
reported optimized replays; neither failed attempt was recorded as a pass.

The mathematical controls reject missing/duplicate patterns, zero minors,
float determinant substitutions, a target used as its own witness source,
and a wrong rank-seven coordinate. Package controls reject missing/extra
source entries, wrong base, wrong digest, and a changed snapshot digest.
They execute with Python assertions disabled and leave no retained scratch.

Not run: NumPy original floating screen, native/full supplier, cold ancestry,
Linux CI or Lean. No solver or tool was installed. This is exact finite
evidence for the archived free-relaxation scope, not a full review of PR620.
