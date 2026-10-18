# Ordered branch filters in the selected replay guard

The selected replay's CI guard could report complete trigger coverage for
`branches: [main, '!main']`. Its branch check only required a literal `main`
entry. GitHub applies matching patterns in order, so the later negative pattern
excludes main. The same false pass occurred with `[main, '!m*']`, for both
`push` and `pull_request`.

The correction in [check_selected_ci_inputs.py](../../scripts/check_selected_ci_inputs.py)
also evaluates the branch list with its existing ordered `triggers` matcher.
The explicit `main` requirement and supported glob grammar are retained.
`[main, '!m*', main]` includes main again. Unsupported branch globs are reported
through the existing coverage-error path. Trigger failures remain advisory
unless the caller requests `--require-triggers`.

The current `frontier1094.yml` uses `[main]` and passes. This result repairs a
false pass on edited workflows; it does not establish a missed hosted run.

## Task, sources and overlap

This is one bounded verifier-engineering contribution from canonical main
`f0cf35964766b21a67c5e3b52e4a7daa4ca92a13`, priority revision 5. Task picker nonce
`e5e3cd7f4b9abf66cbf27a7f5f819c6e` suggested `portable-replay` and a canonical
payload audit. Scope changed to a distinct reproduced failure at the selected
replay's trigger boundary. The known integer-parsing, paired-traversal and
fail-closed inventory work is separate. The stop rule is this branch check and
its regressions, without a general YAML parser or workflow-execution audit.

The canonical claim and subsequent result are in
[Discussion #2926](https://github.com/CrocSwap/integer-mult-bounds/discussions/2926).
The nearest predecessor is Sagar Thakrar's
[PR #1361](https://github.com/CrocSwap/integer-mult-bounds/pull/1361), which
introduced the guard and its 21 tests. Credit Douglas Colkitt's selected-record
checks and replay chain, and the retained supplier authors.

The exact predecessor guard at the base above has SHA256
`ac9b8a1ce5d1fb107cff608571b7457957f7cc5361ea422d1589ee143631fbd5`
and Git blob `eb7c8e723df90946fc61ec5b7a28b51249a7ef9d`.
Its original test module has SHA256
`c97d91ca9048a2bc328550b475f31e412fcdd2816faf8fb49cb2c876aca0541f`.

The overlap search used `branch filter`, `event_paths` and `selected CI inputs`,
including closed PR bodies. Its initial complete snapshots covered 489 open PRs,
1,604 Discussion records and 2,130 closed PRs on 2026-10-16. It identified
#1361 as the predecessor. Search coverage does not establish novelty outside
the searched bodies, comments and local package notes.

GitHub's primary specification is
[Workflow syntax for GitHub Actions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#onpushbranchestagsbranches-ignoretags-ignore).
The order rule applies to push branch filters and pull-request base branches.

## Evidence and reproduction

The final regression module rejects the unmodified predecessor guard. Its
`Globs` group has 18 failing subtests and its `BranchFilterCLI` group has four.
The original 21 tests pass on the base. With the correction, all 24 tests pass.

The new tests exercise both event types and inline/block branch lists. They
cover literal and wildcard exclusions, later re-inclusion, unrelated exclusions,
empty filters, unsupported syntax and the retained explicit-main restriction.
Eight subprocess invocations exercise the actual CLI against a complete small
repository fixture. That fixture authenticates a certificate, source inventory
and proof before checking workflow coverage. The assertions check exit codes
and result/error messages, including advisory behavior.

A separate local probe temporarily changed the actual selected workflow,
restoring its exact bytes afterward. With `[main, '!main']`, the original
`--require-triggers` command returned exit 0 and `PASS_SELECTED_CI_INPUTS`.
The corrected command returns exit 1 and names the excluded event. This passes
for both events in normal and optimized Python execution. The restored
workflow returns exit 0.

Run from the repository root with the standard library:

```sh
python3.12 -W error -B -m unittest discover -s tests -p test_selected_ci_inputs.py -v
python3.14 -I -O -B -m unittest discover -s tests -p test_selected_ci_inputs.py -v
python3.12 -I -B scripts/check_selected_ci_inputs.py --require-triggers
python3.12 -I -B scripts/verify_selected_result.py
```

Local environment was macOS 27.0.1, arm64. The focused module passed on CPython
3.9.6, 3.12.15 and 3.14.8; Python 3.12 also passed with warnings treated as errors.
Five related modules passed on Python 3.12, totaling 40 tests:
`test_selected_result.py`, `test_selected_proof_binding.py`,
`test_selected_inventory_links.py`, `test_replay_coverage.py` and
`test_frontier_replay_coverage.py`. These checks authenticate source metadata
and test replay bookkeeping; they do not execute the selected construction.
The generic `make verify-tests` runner discovers the changed test module.

## Scope and engineering checks

Only branch inclusion changes. The guard remains a limited static reader.
Job conditions, shell execution, event delivery, concurrent file edits and
arbitrary-input resource hardening are outside this result. Hosted execution,
Linux/Windows execution and the complete `make frontier1094-verify` replay
were not run. This is no supplier admission, new kappa or multiplication proof.

The changed parser function is 50 lines. New test methods are at most 25 lines,
and every child command has a 30-second timeout. Existing explicit exceptions
enforce the branch decision under optimized execution. Temporary fixtures clean
up through unittest's registered cleanup path. No new recursive traversal,
dynamic dispatch or source execution mechanism is introduced.

The Python parser and cached glob matcher retain their existing input-sized
allocation and traversal behavior. A fixed-memory or arbitrary-input capacity
rewrite would exceed this branch-order repair. Its compensating boundary is
the existing repository-workflow contract; a future general parser would need
explicit document/pattern limits and bounded cache storage. Tests use fixed
tables and small fixtures. Ruff's E4/E7/E9/F checks pass; the broader local Ruff
configuration reports the same pre-existing style diagnostics as on the base,
with no additional diagnostics. Repository-wide style changes are deferred.

## Open next questions

Can a future workflow-reader audit compare the other supported trigger forms
against a primary-source oracle? First enumerate its declared supported forms
and test one concrete mismatch. Full YAML parsing, dynamic job conditions and
shell-command analysis require separate contracts. None is implied by this
branch-filter correction.
