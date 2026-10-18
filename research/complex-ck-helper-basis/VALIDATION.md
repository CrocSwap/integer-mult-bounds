# Local validation

Linux x86_64, CPython 3.13.5; base
`66849e1475c930fd7732b1a0067ffee7e1e95f60`.

- Full certificate generation: PASS; both complete emitted scalar programs,
  all 716 arbitrary live columns, frame incidence and wrapper ordering.
- Independent primitive block replay: PASS in both orientations, all 716 live
  columns plus one arbitrary incoming coefficient-work column.
- New semantic mutations: 6/6 rejected. Retained native mutations: 25/25
  rejected. These are rejection controls, not additional unittest test cases.
- `PYTHONOPTIMIZE=2 python3 -I -O -B .../verify.py --out <fresh-dir>`:
  PASS, exact committed certificate match. Retained subprocess assertions stay
  enabled. No optimized false PASS is accepted.
- Focused mathematical and packaging unittest suite under isolated optimized
  Python: **11 passed, 0 failed, 0 skipped**. `TEST_SKIP_LOG` is empty (0 lines,
  no skip reasons). Includes all 128,524 pair/sign prices by a separate census,
  27,776 pair/target/orientation dense maps, source corruption rejection,
  gzip-container portability and dirty private work clearing.
- `make selected-record-check`: PASS; selected result unchanged.
- Staged whitespace, Python syntax and package-relative documentation links:
  PASS before local commit.

The initial discovery run completed mathematical checks but encountered a
report-packaging KeyError (`negative_controls` versus the retained receipt's
`negative_controls_rejected`). This was corrected, then complete certificate
generation and the independent optimized replay passed. No failed or skipped
check is counted as a pass.

No repository-wide `make verify`, full selected cold regeneration, global
owner/invoice/assembly regeneration, remote CI or Lean was run. Only the new
research package is changed.

Initial read-only overlap review covered 585 open PRs through #764, the review
ledger and open issues. Final refresh reaches #773 and credits #769's distinct
CK coefficient reuse. The relevant #749/#750/#719/#696/#734 heads remain pinned
in the overlap snapshots; upstream main remains at the exact base.
No independent human review is claimed.
