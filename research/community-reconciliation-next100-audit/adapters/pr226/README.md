# PR226 arithmetic-module portability repair

Original source is unchanged and retained under its reviewed Git head. The repaired
copy imports Mathlib.Data.Rat.Defs instead of the absent Mathlib.Data.Rat.Basic and
removes two rfl tactics after rw already closes the goal. Appended #print axioms
commands inspect all 11 declarations. No theorem statement or witness constant changes.

Use the pinned Lean/Mathlib environment in ENVIRONMENT.json, then run
`lake env lean --root=/path/to/adapter /path/to/adapter/SchonhageTensorMatchFixed.lean`.
The accepted declarations establish finite arithmetic only, not full network correctness,
the analytic reduction or a current frontier. No sorry axiom appears in the audit.
