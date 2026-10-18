# Replay planning must reject incomplete inventories

The opt-in research planner could report success after silently omitting
unreadable package directories. At main
`afc158a25ef3e0bd80de81d1eb5339f0dace118e`, removing directory access from
`research/` produced `{"include": []}`. Removing access only from the first
of two registered packages produced a matrix containing just the second.
Both commands exited zero and appended the incomplete matrix to GitHub output,
even when the runner itself changed and every registered package was required.

`Path.glob("*/VERIFY.json")` suppressed the directory scan errors. Opening an
unreadable manifest already failed correctly. The change replaces globbing
with one explicit, shallow directory scan and a direct `lstat` of each possible
manifest. An absent opt-in or a regular nonpackage file is skipped. Other
scan, lookup and read failures propagate through the existing CLI error path
before a matrix is printed or GitHub output is appended. A dangling manifest
symlink is still encountered and rejected when opened.

## Evidence and replay

Run from the repository root, with standard-library Python:

```sh
python3.12 -B tests/test_research_replay_selection.py
python3.12 -I -O -Werror -B tests/test_research_replay_selection.py
python3.12 -B -m unittest discover -s tests -p 'test_research_*.py'
```

Before the fix, the new regressions failed on both real directory-permission
cases and an injected inventory-scan error. After the fix, all nine focused
tests pass on CPython 3.12.15 and optimized CPython 3.14.8, on macOS arm64.
The CLI controls check exit status 1, empty stdout, unchanged existing GitHub
output, and recovery to the exact two-package matrix after permissions return.
Unreadable-manifest and unregistered-entry controls also pass. Real permission
tests skip on Windows and when running as root; the injected scan failure
can test the planner there without relying on permission bits.

The research workflow suite passes 147 tests with seven platform skips. A
comparison against the original planner on this readable checkout gives
identical sorted selections for the runner change, an unrelated README change,
a package-local change and a shared fixture change, respectively 1101, 0, 1
and 54 packages. The selected source-binding baseline passes. A separate
internal reviewer ran the focused tests and found no actionable issue.

Ruff 0.17.1 with `E,F,B` reports no new diagnostics relative to the base.
The two existing files retain 73 line-length diagnostics and one `zip` diagnostic
outside the edited lines. Warning-as-error compilation of the changed Python
sources passes. Native Windows execution and hosted CI were not run locally.

## Task, scope and limits

Priority revision 5; original picker nonce
`3989aec3b1e0ee49e2f6fd8e69d9bf8b`. The complex-mechanisms suggestions led
to a live P104 overlap check. Adjacent endpoint and precision obligations were
already covered, so the session changed scope to `portable-replay` in verifier
engineering. The specific question changed from mathematical completion to
whether filesystem access failures can silently remove required verification.
The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2955)
records the pivot, overlap coverage and bounded stop rule.

This is a planner correction. It does not independently verify the mathematics
of selected packages, infer undeclared dependencies, or protect against files
changing during a scan. It changes no selected result, frozen source or proof
receipt. The selected cold replay and all historical package replays were not
run for this discovery-only change.

Build the Lever and Prove It Works shaped the retained regression commands.
Test Behavior, Not Implementation required the real CLI and literal matrices.
Power of Ten shaped the shallow scan, scoped iterator cleanup and explicit
failure propagation. The changed planner is 27 lines with no recursion.
Managed allocation remains a runtime deviation: the finite directory snapshot
and manifest input lists bound each loop, but their sizes are not capped before
allocation. A capacity-controlled scanner would need a separate resource
contract. Existing replay commands retain their time limits; new CLI subprocesses
have ten-second timeouts. No new dependency, dispatch layer or suppression is
introduced.

## Open next questions

No further construction or verification campaign follows from this fix.
Other inventory consumers need their own concrete omission reproduction before
receiving the same treatment. Concurrent filesystem mutation remains outside
this planner's snapshot contract.

Nick Petalas. Credit Douglas Colkitt for the registered runner and Charles
Bethin for the replay-selection tests and workflow dependency checks. Related
strict-payload and selected-record inventory fixes are separate predecessors
of this failure class. Substantial AI assistance was used for diagnosis,
implementation, testing and writing; no independent human review is claimed.
Apache-2.0.
