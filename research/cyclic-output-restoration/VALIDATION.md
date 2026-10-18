# Local verification and handoff

Research base: `dadfea6e8a78ff6ba901705f87532a71c6f5bbb8`.
Refreshed submission base: `b84ba67156a01f9c2cb34fe1e3cb1dcdeab00d9c`.
The rebase changes no package code, certificate, source bytes or selected record.
Environment: macOS arm64; CPython 3.12.12 (registered runner), 3.14.6 and 3.9.6.
Final mathematical implementation and certificate verified on 2026-10-13 UTC.

- Registered Python 3.12 replay passes: complete boundary and reader census,
  all recursive maps, literal inverses, both invoices, source pins, ten
  mathematical controls and seven package test groups.
- The final code also passes the seven test groups on Python 3.12 and 3.9,
  including isolated optimized replay, exact certificate regeneration and
  five on-disk corruptions. The final direct Python 3.9 replay passes.
- Python 3.14 optimized certificate export is byte-identical to the committed
  JSON. Both forward and arbitrary-input inverse matrices are checked against
  independently constructed block formulas.
- Complete finite coverage: 66,420 boundary schedules (120 admitted), 100 price
  comparisons; 19,683 ternary admission matrices (27 admitted); 192 recursive
  cases, 3,744 basis columns and 157,704 forward primitive occurrences. The
  frozen five-child and depth-three witnesses are additional complete cases.
  The general optimal-boundary argument is written in README, not inferred
  from those finite counts.
- Full final echo: eager 588 signed ADDs, output-frame word 504; 21 registers
  in both. Complete boundary cost 15→8 triple rotations per batch, with both
  passes charged. Existing six-ADD rotations from the PR1145 line are used
  in both schedules; the initial two-SWAP upper price is not used in the result.
- Final marker: `PASS_CYCLIC_OUTPUT_RESTORATION schedules=66420 admission=27/19683 cases=192 saved_rotations=14 saved_primitives=84 no_new_kappa`.
- Source hashes: three retained predecessor notes authenticate by both Git
  blob ID and SHA256. Six historical base-context pins pass the registered
  metadata checker. Selected record verification and all five
  `test_selected_result.py` tests pass; selected evidence is unchanged.
- Whitespace checks pass. Only this scoped package is added; no global
  regeneration, upstream changes or frontier edits.

The input tests exposed a Boolean/integer memoization-key collision during
implementation; the planner now uses a type-sensitive cache and rejects
Boolean prices/counts even after the integer key has been populated. This
changed no admitted positive-integer certificate result.

The deep witness raises address travel and intermediate coefficient bounds;
the small witness also raises its coefficient bound. Full compiler/admission,
precision/rounding, tape/hosting and analytic transfer are not established.
No full selected cold replay, formal proof-assistant compilation, independent
human review or hosted CI pass is claimed. CI status is separate from these
local checks. There is no new kappa or total runtime claim.
