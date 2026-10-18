# Validation receipt

Completed 2026-10-13 on macOS 27 arm64, CPython 3.14.4. Exact base and refreshed
main: `2921874911956718fcaaaf9396fe8267b3cfa9f0`.

- `python3 -I -B research/disjoint-frame-unions/test_unions.py`: **8 tests pass**,
  including five original historical tests inside the scoped adapter test.
  All three maps compare entry-for-entry and in iteration order at h26; all
  small generated and 88 seeded graph cases also match a separate BFS oracle.
- The same eight tests pass under `python3 -I -O -B`. This checks the new graph
  kernel and finite controls; it does not certify inherited assertion coverage.
- `python3 -I -B research/disjoint-frame-unions/test_replay.py`: **5 tests pass**.
  Under `-O`, four pass and the full-receipt test is explicitly skipped because
  full audit replay correctly refuses optimized Python. The refusal itself is
  tested in both modes.
- Five alternating fresh-process baseline/adapter pairs reproduce the complete
  certificate in all **10 runs**. Median wall times are **5.014369041 s** and
  **3.492928334 s**, a **1.435577419x** speedup. All samples and code/source
  manifest hashes are in BENCHMARK.json; none is excluded. No task-local test
  or other experiment ran concurrently with those benchmark processes.
- `PYTHONDONTWRITEBYTECODE=1 make verify-tests`: **661 tests in 96 isolated
  modules and 20 patch-application checks pass**, exit code zero. These tests
  use the default sources; the new optional package is tested separately above.
- `make selected-record-check`: passes, retaining
  `1661960547713947/1000000000000000000`.
- Minimal relocation: copied only the 40 pinned inherited files and this
  package into a temporary path containing spaces, then invoked the isolated
  adapter from `/tmp`. Full certificate comparison passes without Git or
  unrelated repository artifacts. RELOCATION.json preserves the result.
- Every inherited hash matches its base Git blob and the refreshed main blob.
  The benchmark's adapter and manifest hashes match the final executable files.
- A separate Codex worker reviewed the final implementation, wrapper, proof and
  tests read-only and found no actionable issues. This is AI review, not human
  peer review.
- `git diff --check` passes. Only `research/disjoint-frame-unions/` is added;
  all pre-existing source and certificate bytes remain unchanged.

The final PR overlap snapshot contained 737 open PRs through #1042. Newly
arrived #1029 (`ff4d7b9ac97a584275fe0653f226f4ce2ffc6086`) and #1041
(`9576c644a4cafd2cfac309689a19342451702f81`) concern U8 phase recipes; their
changed-file lists do not overlap this historical frame-union adapter.
No pinned coordination issue exists. Related #863/#981 change constructions,
and #950's central-factor verifier is credited separately in NOTICE.md.

Not run: full `make verify`, selected-supplier cold replay, Lean, or hosted Linux
CI. Those are not claimed by this additive historical-verifier contribution.
No new bound, all-size implementation, global optimality, or unconditional
multiplication theorem follows from these finite checks.
