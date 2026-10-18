# Executed validation

Windows, CPython 3.14, base `8bddbee377e2f3ce1f1247196c4b290d55767d20`.
All commands below were executed from the isolated round-02 repository.

- `python -I -B research/t37-bootstrap-depth-seed60/verify.py --write-certificate`
  generated the exact receipt successfully. The ordinary command without that
  flag then reproduced and matched it, with seven original levels, six candidate
  levels, 47 strict outer conditions, eleven negative and one positive controls.
- `python -I -B research/t37-bootstrap-depth-seed60/check_mutations.py` passed:
  deleted source pin, modified pinned source, and altered snapshot each reject;
  a scratch repository containing only the five immutable consumed inputs
  passes despite having no `certificates/selected-result.json`.
- `python -I -O -B research/t37-bootstrap-depth-seed60/verify.py` correctly
  exits nonzero before source-engine execution because assertions are required.
- `python -I -B scripts/verify_selected_result.py` passes the current selected
  record, exact kappa, source inventory and proof supplements. This one-time
  repository check is separate from the historical package replay.
- `make verify` could not start: `make` is not installed/available on PATH.

No GCC/Clang/Boost native replay, complete supplier/controller rebuild,
moment-engine rerun, hosted recursion, remote CI or full multiplication theorem
verification was performed. The unchanged moment brackets and completed
supplier admission remain inherited inputs. The all-size/compiler/physical/
hosting/precision/tape/analytic obligations are not discharged by this audit.

The interpreter emits an environment warning about locating its installed
Python executable, but the successful commands above terminate with exit code
zero and the recorded PASS lines. It is not counted as validation failure or
silently rewritten into a different runtime claim.
