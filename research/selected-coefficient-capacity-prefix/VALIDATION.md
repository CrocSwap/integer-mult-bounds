# Validation

Validated on macOS with CPython3.12.12 and CPython3.14.6. This is exact finite
corroboration plus two written AI source audits, not human or formal-kernel
verification. All scientific runtime files remain byte-identical to INPUTS.json.

- The registered replay passed under CPython3.12.12 with `-I -Werror -B`.
  It ran the complete primary checker, eight optimized controls and the separate
  optimized witness. Nine successful closed coefficient fixtures and three
  actual underbudget failures observed 977,159 pending allocation requests.
- The separate ordinary/optimized witness distinguishes the source extension's
  exact extra index capacities10 and11; its demand11 is observed before rejection.
- A Git-free 0444/0555 export passed all three commands under CPython3.14.6
  with `-I -O -Werror -B`, empty PATH, cwd `/private/tmp`. All28 exported files
  remained byte-identical across that replay. No Git import or external package
  was available to the scientific commands. TASK freshness and this validation
  record are updated after replay; scientific inputs/checkers are unchanged.
- An initial read-only control replay exposed copied file permissions in the
  *test's disposable mutation copy*. The control now makes only that temporary
  copy writable. Final normal/optimized checks pass, and the failed temporary
  path was absent afterward. The original read-only export was unchanged.
- The canonical refresh advanced main to `808e0e985a84cf59df69b118d05c406c921c0196`
  at 2026-10-16T01:07:42.753458+00:00. Guidance/priority/selected record were
  unchanged. The generic runner gained duplicate-dependency validation,
  normalization of omitted requirements and display encoding handling. We
  inspected that diff and ran its current `run_package` against this unchanged
  isolated package; all three registered checks passed. The frozen scientific
  base and vendor pins were intentionally retained; no rebase or repin occurred.

`verify.py` compares the complete typed RESULT.json; no ordinary command
regenerates a receipt. Actual source quota failures and changed-code defects
are distinguished from observation-budget failures. Source rollback restores
entry state in the three tested quota cases; arbitrary exception safety is
not claimed. The half-extension witness tests a naked subroutine and uses
explicit cleanup on its underbudget path.

Finite fixtures do not exhaust source programs, all prime powers, arbitrary
widths or selected-catalogue membership. The all-parameter resource result
rests on PROOF.md and INDEPENDENT.md. Full Consumer.apply/GL64 execution,
complete physical/recursive reserve, selected cold replay, supplier adoption
and new kappa were not claimed. Hosted CI and publication are separate gates.
