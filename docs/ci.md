# CI execution policy

The general artifact workflow is
[verify.yml](../.github/workflows/verify.yml). It verifies 16 Makefile groups
on Python 3.11, 3.13 and 3.14, the ranked-pair finite replay, the three
formal Lean packages and four historical package verifiers. Nothing in that
list was removed or thinned. What changed is *when* each job runs: a cheap
`plan` job first decides which of them the run's changed paths can reach.

## Why

Observed with the GitHub API on 2026-10-13/14; the downloaded timings are
local investigation evidence, not a retained performance certificate:

- The repository had about 4,700 queued runs and 20 to 22 hours of queue
  wait, growing since 2026-10-13 06:00 UTC.
- The runner concurrency available to the repository fell from more than
  134 jobs on 2026-10-13 morning to 60 on 2026-10-14 evening and 30 to 38
  at 22:30 UTC. That is outside the repository's control.
- Demand was about 222,000 runner-minutes per day against 86,400 per day
  at 60 concurrent jobs. `verify.yml` accounted for 86% of the minutes:
  52 jobs and about 207 runner-minutes per run, 925 runs a day.
- A verify job spends 3.6 of its 3.9 minutes inside `make verify-<group>`;
  checkout and interpreter setup are 0.3 minutes. Merging jobs or caching
  setup addresses only a small part of that cost.
- 23 of 30 recently updated pull requests only added a new
  `research/<package>/` directory. Only two groups depend on the whole
  tree (`clones` copies and hashes every tracked file; `tests` walks every
  research package). Most remaining jobs re-verified inputs the pull request
  did not change. The historical formal job's complete dependency recording
  also allows selection without losing its external source checks.
- 25% of the queued runs had already been superseded by a newer push.

## What runs

1. **Planning.** For a pull request the checkout is GitHub's merge of the
   pull request into its base, and the planner diffs that merge against its
   first parent (`git diff --no-renames --name-status`). For a push to main
   it diffs `before..after`. Each changed path is classified with
   [.github/verify-groups.json](../.github/verify-groups.json):
   - a path in the manifest's `all` list (Makefile, `scripts/**`, the
     workflow, the manifest, and the root `.gitattributes` or `.gitignore`)
     runs everything; `.gitmodules` at any depth also runs everything;
   - a nested `.gitattributes` or `.gitignore` selects every group whose
     declared inputs overlap its affected subtree;
   - a path matching a group's declared inputs selects that group, on every
     Python version;
   - a path in `skip_safe` (research packages, documentation prose, other
     workflow files, top-level prose) selects nothing; a declared group
     input always takes precedence over `skip_safe`;
   - any other path is *unclassified* and runs everything. Silence has to be
     declared; it is never assumed.
   Scheduled and manually dispatched runs, pull requests carrying the
   `ci:full-verify` label, any run whose diff cannot be computed (force
   push, missing parent), any change to a symbolic link, any tracked path
   that `.gitignore` would ignore, and any entry added to or removed from
   the repository root run everything. A group declared `**` depends on
   the whole tree and runs on every change (`clones` and `tests`), but a whole-tree
   match never counts as understanding a path:
   an otherwise undeclared path still runs everything.
2. **Verification.** Selected groups retain their checks, using the
   authenticated historical adapters described below where source pins
   require them. They run under `strace`, and the step also fails if a group read an input
   its declaration does not cover. Full runs are the same 48 Python
   combinations, the finite replay, the three formal packages and the four
   package verifiers as before.
3. **Summary.** `verify-summary` is one stable status: it fails if planning
   failed, if any job the plan selected did not succeed, or if any job
   failed or was cancelled; only jobs the planner skipped on purpose may be
   skipped.

## Estimated effect

Estimated by replaying the planner over the changed-file lists of the 60
most recently updated open pull requests (2026-10-15) with the audited
manifest, using the Oct 14 per-job durations. These are workload estimates,
not measured hosted durations of the new workflow; they exclude added tracing,
historical-copy and summary-job overhead:

| | Runner-minutes per pull-request sync |
|---|---|
| Before (52 verify jobs plus the four package workflows) | 232 |
| After, mean over the 60 pull requests | 63 |
| After, a pull request that only adds a research package | 25 (`tests` and `clones` on three Pythons, plus the plan job) |

51 of the 60 pull requests select only the groups they reach; 9 run
everything, 6 of them because they edit the root `.gitattributes` and 3
because they change files under `scripts/`. The mean estimated workload is
27% of the old workload. Actual queue recovery depends on runner capacity,
new arrivals, trace overhead and the historical replay copies. No queue-drain
time or hosted speedup is established by this model.

## How the declared inputs are known to be complete

The manifest is recorded, not guessed.
[scripts/trace_verify_inputs.py](../scripts/trace_verify_inputs.py) runs a
group's exact CI command under `strace` and records every tracked file it
opened, every directory it listed, every path whose existence it probed and
every whole-tree Git query it made (`git ls-files`, `git status`, ...).
`--check` fails when a recorded input is not covered by the group's patterns.

Pattern semantics are small on purpose:

| Pattern | Matches |
|---|---|
| `path/to/file` | any change to that file |
| `dir/**` (`**` alone: the whole tree) | any change at or below `dir` |
| `dir/*` (`*`: the repository root) | an entry added to or removed from the listed directory; editing an existing entry is covered by its own read |
| `dir/` | the directory was only checked for existence (path resolution, `mkdir -p`, `os.path.isdir`); only creating or removing it matters |

An added path changes the listing of its deepest ancestor that already
existed in the base tree, and a deleted path the listing of its deepest
surviving ancestor; the planner computes that from `git ls-tree` of both
trees, so adding `research/new-package/verify.py` changes the listing of
`research`, not of the root, and creates only `research/new-package`.
Listing and existence are recorded separately because they differ in
practice: every Python process resolves its script path through
`research`, which proves nothing about that directory's entries, while a
glob or a directory walk does. GNU make lists the repository root before every
rule, so a new or removed entry directly at the root always verifies
everything.

Every verification job, selected or full, runs under the tracer and fails
on undeclared inputs, on every Python version. A change that makes a
verifier read a new input therefore fails until the declaration is updated,
and the scheduled full runs re-validate the whole manifest against main
four times a day. The Lean builds of the formal packages run under the
tracer too; their project trees are declared whole because Lake reads them
densely.

Rechecking a saved recording with `--from-recording` requires its matching
group, current recording schema and explicit verification status. A failed
or incomplete recording cannot establish successful input coverage. Reuse
checks the saved observations; it does not rerun the verifier.

Regenerate a group's patterns locally with:

```sh
python3 -B scripts/trace_verify_inputs.py --group community --output build/community.json --check --suggest
```

The initial declarations were recorded locally on Python 3.14, including the
`gaussian` and `matrix` formal packages with their real Make targets. The
initial `historical` recording stopped before its source audits because
compiled Mathlib dependencies were unavailable. Those audits read notes,
certificates and upstream paper sources outside `formal/`; a declaration of
`formal/**` alone was insufficient. The pre-push audit fetched the pinned
Mathlib cache and successfully traced the complete `make formal-historical-verify`
target, including ranked-pair and machine-transfer compilation. Its 145 files,
43 directory listings, 3 directory-existence checks and 86 probes are covered
by 21 declared patterns. All three Lean project source trees stay declared
whole; external notes, certificates and upstream sections are explicit inputs.
The alternative `research/formal/` project discovery path is covered too.
No whole-tree Git access was observed in that complete recording. The first hosted runs on
3.11 and 3.13 are the check that nothing version-specific was missed; an
undeclared input fails that job with the exact pattern to add.

## Requesting the full matrix on a pull request

Fork pull requests cannot be targeted by **Run workflow** in this
repository. Add the `ci:full-verify` label instead: the label event starts a
full run on the pull request's merge commit, with its own concurrency group
so it is not cancelled by later pushes, and every later push to a labelled
pull request also runs everything. Remove and re-add the label to re-run.
Other label events follow the ordinary change-based plan and honor any existing
full-verification label; they cannot publish an empty successful replacement
for a real verification run.

## Required checks

The stable gate is `verify-summary`. On 2026-10-15 the GitHub branch API reported
`main` unprotected with no required status checks, and the repository ruleset
list was empty. If maintainers enable required checks, use this gate rather
than individual matrix or retired package-workflow check names. Selected-out
matrix combinations do not publish those former check names. This change does
not alter repository protection settings.

## Pushes and the schedule

Every push (main, other branches, tags) runs the groups its own diff
reaches, with no cancellation and no shared concurrency group, so each
pushed change is verified for what it touched; a push whose previous
commit is unavailable (new branch, tag, force push) verifies everything. The scheduled full run every six hours
re-establishes whole-tree verification independently of any selection and
re-checks the manifest; manual dispatch does the same on demand. A schedule
is an audit, not a guarantee: a transient bad commit reverted before the
next schedule is caught by its own push run, not by the schedule.

## Superseded runs

A newer revision of a pull request cancels that pull request's queued or
running automatic run. Runs created before this policy keep their old
definition; [ci-cancel-superseded.yml](../.github/workflows/ci-cancel-superseded.yml)
is a manually dispatched, report-only-by-default maintenance workflow that
cancels, through the API and without checking out any pull-request code,
pull-request runs that a newer commit of the same pull request has
superseded. It never touches pushes, scheduled or manual runs, runs that
share the newest head commit (re-runs, label-requested runs) or runs whose
pull request it cannot identify unambiguously, and it inspects one
created-at window per dispatch because the API lists at most 1000 runs.
Cancellation API failures make the maintenance workflow fail and identify the
affected run IDs; a dry run never sends cancellation requests.

## Trust boundary

A pull request runs its own copy of the workflow, planner and manifest with
a read-only token and no secrets, exactly as before. "Changing the planner
runs everything" guards against mistakes, not against a hostile pull
request; pushes to main and scheduled runs, which execute reviewed code
only, remain the trust anchor.

## Dependency caching

Only `formal/lean/.lake/packages` is cached, with an exact key derived from
the runner image, architecture, Lean toolchain, Lake manifest and Lake
configuration. Successful non-PR runs on `main` populate the cache; pull
requests restore it. Project compilation, source checks and theorem axiom
audits still run on cache hits. The cache contains dependency sources and
builds, never verification results, regenerated certificates or replay
receipts.

## Earlier verification speedups

The following contributions are merged, but their accelerated
implementations remain opt-in and are not used by the matrix:

- Sagar Thakrar's [#1041](https://github.com/CrocSwap/integer-mult-bounds/pull/1041)
  parallel phase recipes, [#1059](https://github.com/CrocSwap/integer-mult-bounds/pull/1059)
  parallel U8 layer-end controls, and
  [#1151](https://github.com/CrocSwap/integer-mult-bounds/pull/1151)
  frontier1042 layer-end controls. Their equivalence checks are separate from
  adopting them in the selected cold replay.
- Sagar's [#1433](https://github.com/CrocSwap/integer-mult-bounds/pull/1433)
  packed omission replay and [#1584](https://github.com/CrocSwap/integer-mult-bounds/pull/1584)
  finite-bit transition cache are also opt-in.
- Josie Elliston's
  [selected-chain phase comparison](../research/frontier1042-phase-fastpath/README.md)
  documents the remaining integration points in pinned scripts.

This CI change leaves those sources and their attribution intact. It does
not alter pinned verifiers, frozen evidence, the selected result or
mathematical claims.

## Validation

Local validation uses Linux, Python 3.14.4, strace 6.x and actionlint 1.7.12:

```sh
actionlint .github/workflows/*.yml
python3 -B -m unittest discover -s tests -p 'test_plan_verify_groups.py' -v
python3 -B -m unittest discover -s tests -p 'test_trace_verify_inputs.py' -v
python3 -B -m unittest discover -s tests -p 'test_cancel_superseded_runs.py' -v
python3 -B scripts/check_selected_ci_inputs.py
python3 -B -m unittest discover -s tests -p test_selected_ci_inputs.py -v
git diff --check
```

The planner tests assert that the manifest's verification groups are
exactly the Makefile's `verify-*` targets, that a full plan is the fixed
48-pair universe without duplicates, and that a pull request adding only a
new research package selects exactly the whole-tree groups, on every
Python version. Hosted execution and the first scheduled tracer run are not
claimed by local checks.

## Historical source compatibility repair

At the investigation base `0fdd7d82`, the exclusion-circuit optimizations in
`d8029ee05` and `d7d8bfcb` change a script pinned by `research/skip-clones` and
`research/split-skip`. The shared-point optimization in `6178dede` also changes
a script pinned by `research/split-skip`. The clone certificate tests and the
clones CI group therefore fail. Reverting the optimizations would instead
break their new source-bound equivalence tests. An earlier version of this
note incorrectly named `skip-strips` as the shared-point pin's consumer;
its unchanged verifier passes.

The repair extends the existing `scripts/replay_historical_check.py` adapter.
It authenticates exact predecessor blobs from commit
`0b1cccf86e2f5132ed286a26ef0a681a495740ea` against the unchanged historical
source manifests before copying the current tracked tree. Only the declared
historical inputs are replaced inside the temporary tree. The live optimized
scripts, frozen certificates, manifests and selected result remain unchanged.
All tracked bytes in the replay copy are checked again on exit.

After merging current main, the exclusion and shared-point inputs come from
Wentao Li's retained research baselines, with the same authenticated bytes as
the reference snapshots above. The adapter also retains main's checks that
each baseline is tracked and that live helpers match an explicitly accepted
successor, including the newer shared-point initialization and frame cache.
Unknown live source changes reject before a replay tree is created.

Main's partial-swap digest/initialization changes also affect both historical
clone manifests. Their additional `scripts/partial_swap/shared.py` input is
restored from `research/partial-swap-digest/baseline.py`, which matches the
original `0b1cccf86e2f5132ed286a26ef0a681a495740ea` bytes. The accepted live
digests come from Wentao Li's retained digest and initialization packages;
their live optimization tests continue to use the current implementation.

The subsequent sparse-fusion optimization is handled the same way: split-skip
uses `research/sparse-fusion-orbits-production/baseline.py` for its original
`scripts/audit_sparse_fusion.py` pin and accepts only the retained production
successor. The optimized live checker stays unchanged.

The clones group now runs:

```sh
python3 -B scripts/replay_historical_check.py skip-clones
python3 -B scripts/replay_historical_check.py split-skip
```

The first command retains the complete clone native producer, certificate
regeneration and unit tests. The final command retains the split-skip native
producer (with the original Makefile arguments), witness,
independent arithmetic and unit tests, now with all five historical inputs
authenticated. The producer runs inside the replay copy because its inherited
skip-strips source check also pins the original partial-swap helper.
The original source-bound Makefile targets remain frozen; use these adapters
to replay those checkpoints against a modern checkout.

`make verify-tests` retains main's isolated runner dispatch to `skip-clones-tests`.
`test_skip_clones.py` also uses this isolated context during direct unittest
discovery. Only this historical module sees the predecessor script; the
optimization tests still exercise the current production code. When already
running inside the historical replay, it uses that tree without nesting a
second copy. Scratch trees live under ignored `build/` and are removed on
exit, avoiding multi-GB allocations in memory-backed `/tmp`.

Regression controls reject corrupt replacement bytes, missing or changed pins,
duplicate replacement paths, untracked replacements, and modifications to a
replay copy. Both groups retain their conservative whole-tree input declaration.
The earlier workload estimates predate the additional isolated clone replay;
its copying overhead and hosted execution still require measurement.

Local repair validation on Linux x86_64 / Python 3.14.4 passed:

```sh
python3 -B scripts/trace_verify_inputs.py --group clones --check --output build/verify-trace/pin-repair-clones.json
python3 -B scripts/trace_verify_inputs.py --group tests --check --output build/verify-trace/pin-repair-tests.json
python3 -B scripts/verify_selected_result.py
python3 -B scripts/check_selected_ci_inputs.py
```

Run the groups sequentially in an isolated worktree. The clones run includes
both native reconstructions, all 4,073,300 fixed-basis data pairs, the historical
witnesses and 21 package tests. The tests group passes all 129 discovered test
modules (including the live optimization controls) and all 20 patch-application
checks. Both traced input-coverage audits pass, tracked artifacts remain
unchanged, and temporary historical trees are removed. The recordings and logs
under `build/` are local-only evidence; hosted execution and Python 3.11/3.13
execution of this repair are not claimed.

The pre-push audit also ran the complete historical formal target on Linux
x86_64 / Python 3.14.4, Lean 4.21.0 and the pinned Mathlib revision
`308445d7985027f538e281e18df29ca16ede2ba3`:

```sh
(cd formal/lean && lake exe cache get)
python3 -B scripts/trace_verify_inputs.py --group formal-historical --command 'make formal-historical-verify' --check --output build/verify-trace/push-audit-formal-historical.json
python3 -B scripts/trace_verify_inputs.py --group formal-historical --from-recording build/verify-trace/push-audit-formal-historical.json --check
```

The run passed 45 ranked-pair theorem audits, 298 machine-transfer declaration
audits, the main Lean build, 386 project axiom audits, source/literal consistency
checks and the paired-circuit reconstruction. The narrowed manifest covers the
successful complete recording. These are the existing scoped formal checks,
not a formal verification of the full multiplication theorem. Tracked artifacts
remain unchanged; the log and recording under `build/` are local-only evidence.

The final staged audit fixes passed the complete test group again, including
all **130 test modules**, all 20 patch-application checks and the traced
input-coverage audit:

```sh
python3 -B scripts/trace_verify_inputs.py --group tests --check --output build/verify-trace/push-audit-tests.json
git diff --exit-code
```

The added module tests cancellation boundaries without making live API writes.
Regression controls also cover unrelated label events, failed/incompatible
saved recordings, all 17 formal source references and both nearer Lean project
discovery paths. Independent review found no remaining input gap in the final
formal declaration. Scratch replay trees were removed and tracked artifacts
remained unchanged. Hosted execution and other Python versions remain unrun.

## Conflict-resolution validation

The conflict refresh merges PR head
`91669e2a3316751ceba6330d19b09fdf5e6b95aa` with canonical main
`ab4fcd39c74effa88d464ed1d80ec832f6020e51`. It keeps main's authenticated
research baselines, accepted-live-source checks and isolated test-runner
dispatch, alongside the PR's traced CI selection and temporary-tree cleanup.
The partial-swap and sparse-fusion additions above cover the newer source
optimizations without editing their implementations or frozen manifests.

On Linux x86_64 / Python 3.14.4, the complete traced clones group passed both
native reconstructions, all 4,073,300 data pairs, 21 package tests, the copied
artifact integrity gates and declared-input coverage. The six focused CI
modules passed 120 tests; the three updated upstream compatibility modules
passed another 21. Workflow lint (actionlint 1.7.12), selected-record checks,
selected CI input checks and the PR diff whitespace check also passed.

```sh
python3 -B scripts/trace_verify_inputs.py --group clones --check --output build/verify-trace/pr2361-updated-base-clones.json
for module in historical_check plan_verify_groups trace_verify_inputs cancel_superseded_runs selected_ci_inputs isolated_test_runner disjoint_tensor_support_masks exclusion_embedding_masks exclusion_support_masks; do
  python3 -B -m unittest discover -s tests -p "test_${module}.py" -v || exit
done
```

The full `tests` group was also run on the initial merge with main
`c3c94c2ea2ebcd5d69d1e51b5fe8a36bf79819f5`: all 139 modules executed, but ten
failed, so the subsequent patch-application checks were not reached. Updated
main fixed the disjoint-tensor and two exclusion compatibility modules; their
reruns are included above. The other seven failures were independently
reproduced in an untouched worktree at `ab4fcd39c`:

- `test_copied_fixed.py`, `test_copied_fixed_reversed.py`,
  `test_pair_assembly.py`, `test_skip_strips.py` and `test_skip_suffix.py`
  reject the updated live `scripts/partial_swap/shared.py` source pin.
- `test_shared_point_digest.py` still expects the earlier production digest.
- `test_split_skip.py` encounters a tuple-shape mismatch with the live helper.

These existing upstream failures are not suppressed. The full tests group was
not rerun after the base refresh, and this resolution does not claim a green
full suite. Logs and recordings under `build/pr2361-*.log` and
`build/verify-trace/pr2361-*.json` are local-only evidence, including the
untouched-upstream reproduction in `build/pr2361-upstream-failures.log`.
Tracked artifacts did not drift. The selected cold replay and Python 3.11/3.13
were not rerun; the selected record, supplier sources and frozen evidence are
unchanged by this PR.

## Attribution

This CI maintenance work is by Sagar Thakrar with substantial Claude Fable 5.1
and OpenAI Codex assistance, including independent pre-push code reviews.
It builds on Dennis's authenticated historical replay adapter and retains the
source credits listed in
[historical-ci-inputs/README.md](../scripts/historical-ci-inputs/README.md).
The optimized circuit implementations and their source-bound controls remain
Wentao Li's contributions. The earlier optional speedups listed above remain
opt-in. All new maintenance code is under the repository's Apache-2.0 license.
