# Validation record

Base `f567884aeb8851b6e794af1184119a3bfbe1e631`; Linux x86_64,
Python 3.12.14, GCC 14.2.0, Boost 1.83.0. Exact toolchain identification is
in `ENVIRONMENT.json`. All commands run from the repository root.

Completed initial checks:

- `python3 -I -B research/r439-block522-factor/verify.py`: all twelve exact
  integer columns, 4,096 Boolean inputs, 661 arbitrary dirty-input columns,
  both pinned geometry/interface replays, exported bill and precision bounds,
  eleven mathematical/record controls; committed receipt matches.
- The same verification under `-O`: PASS. New admission checks use explicit
  exceptions and remain active when assertions are disabled.
- `python3 -I -B research/r439-block522-factor/search.py --output /tmp/block522-candidate.json`
  followed by `cmp`: exactly reproduces all 12,000 trajectories' coverage
  counts and the selected candidate; 492 identity factorizations, seven
  33-ADD results. This is a deterministic replay, not another search domain.
- `python3 -I -B research/r439-block522-factor/test_package.py`: PASS after
  copying only the package and its ten pinned repository inputs to a fresh
  temporary root. The isolated optimized replay succeeds; changed source
  scatter, omitted checker pin, wrong candidate source, mathematically wrong
  candidate with a corrected count, falsified receipt and missing receipt
  are all rejected for the intended reason.
- `python3 -I -B research/r439-block522-factor/native.py --boost-include /workspace/.setup/boost/usr/include`:
  fresh native checker builds; both words pass chronological legality and
  883 / 1,327 / 1,549 formal columns at five/nine/eleven stages. Ninety-six
  distinct word/stage omitted-bridge controls reject. The additional KPAIRS=2
  replay equals the specialized five-stage checker in every non-timing field;
  its twelve repeated controls are not counted again.
- `python3 -I -B scripts/verify_selected_result.py`: PASS, selected exact
  kappa, original source inventory and proof supplement.
- Final native command without receipt-regeneration flags: PASS against the
  committed `NATIVE.json`; original and regenerated non-timing fields agree.
- Final upstream metadata refresh still reports the exact base head. Open
  arrivals through PR904 were inspected. Its certificate's single frame-522
  replacement saves one B ADD; the distinct whole-block ten-ADD reduction
  here and the absence of a combined replay are recorded in README.md.
- The published fork tree `504b4f3243158e6f2ba37f2e37807946726cc836`
  exactly matches the tested local tree before this claim/validation handoff
  update. A subsequent Git fetch of both upstream main and the published
  branch confirms the base and the published content. PR904's refreshed head
  `883a0bdf7792693e57c16be660824b57aacfbe05` has the identical inspected
  certificate. Publication metadata is separate from the finite checks.

`EXPECTED.json` and `NATIVE.json` are deterministic mathematical receipts,
excluding run times and temporary paths. The native programs retain their
original finite scope. No remote CI, full hosted rebuild, outer assembly,
Lean build, `make verify`, or selected-frontier cold replay is claimed. Only
a new isolated research package is added; no producer, selected construction,
or existing verification path is changed, so broad regenerating suites are
outside the affected checks.

The eleven in-verifier controls reject omitted/reordered/reversed ADDs,
reversed operands, self/foreign operands, stale cleanup, wrong frames, a
mutated copied source and an omitted ERASE. One control appends the same ADD
twice: it preserves the F2 endpoint but changes the integer lift and is
rejected by the integer-column check. This guards against accepting a
Boolean-only replacement without its precision-relevant integer contract.

The candidate's reversed positive matrix is not entrywise dominated by the
baseline; the full-stream replay is therefore essential evidence. Its lower
entry sum is used only as a search tie-break, never as a precision proof.
