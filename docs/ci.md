# CI execution policy

The general artifact workflow is
[verify.yml](../.github/workflows/verify.yml). It verifies 16 Makefile groups
on Python 3.11, 3.13 and 3.14, the ranked-pair finite replay, the three
formal Lean packages and four historical package verifiers. Nothing in that
list was removed or thinned. What changed is *when* each job runs: a cheap
`plan` job first decides which of them the run's changed paths can reach.

## Why

Measured with the GitHub API on 2026-10-13/14 (details in the
[contribution PR](https://github.com/CrocSwap/integer-mult-bounds/pulls)):

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
  setup cannot help; the verification work itself is the cost.
- 23 of 30 recently updated pull requests only added a new
  `research/<package>/` directory. Only two groups depend on the whole
  tree (`clones` copies and hashes every tracked file; `tests` walks every
  research package), so the other 50 jobs of those runs re-verified a tree
  the pull request did not change.
- 25% of the queued runs had already been superseded by a newer push.

## What runs

1. **Planning.** For a pull request the checkout is GitHub's merge of the
   pull request into its base, and the planner diffs that merge against its
   first parent (`git diff --no-renames --name-status`). For a push to main
   it diffs `before..after`. Each changed path is classified with
   [.github/verify-groups.json](../.github/verify-groups.json):
   - a path in the manifest's `all` list (Makefile, `scripts/**`, the
     workflow, the manifest, and any `.gitattributes`, `.gitignore` or
     `.gitmodules` at any depth) runs everything;
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
   the whole tree and runs on every change (the `clones` group copies and
   hashes every tracked file; the `tests` group walks every research
   package), but a whole-tree match never counts as understanding a path:
   an otherwise undeclared path still runs everything.
2. **Verification.** Selected groups run exactly the commands they ran
   before, under `strace`, and the step also fails if a group read an input
   its declaration does not cover. Full runs are the same 48 Python
   combinations, the finite replay, the three formal packages and the four
   package verifiers as before.
3. **Summary.** `verify-summary` is one stable status: it fails if planning
   failed, if any job the plan selected did not succeed, or if any job
   failed or was cancelled; only jobs the planner skipped on purpose may be
   skipped.

## Expected effect

Measured by replaying the planner over the changed-file lists of the 60
most recently updated open pull requests (2026-10-15) with the recorded
manifest, using the Oct 14 per-job durations:

| | Runner-minutes per pull-request sync |
|---|---|
| Before (52 verify jobs plus the four package workflows) | 232 |
| After, mean over the 60 pull requests | 63 |
| After, a pull request that only adds a research package | 25 (`tests` and `clones` on three Pythons, plus the plan job) |

51 of the 60 pull requests select only the groups they reach; 9 run
everything, 6 of them because they edit the root `.gitattributes` and 3
because they change files under `scripts/`. At the Oct 14 arrival rate
(792 syncs and 133 main pushes a day) that is about 55,000 runner-minutes
a day including the scheduled full runs, against 86,400 available at 60
concurrent jobs. If the concurrency available to the repository stays at
the 30 to 38 jobs observed on the evening of Oct 14, the queue still
clears but with little headroom; that capacity question is outside this
change.

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

Regenerate a group's patterns locally with:

```sh
python3 -B scripts/trace_verify_inputs.py --group community --output build/community.json --check --suggest
```

The initial declarations were recorded locally on Python 3.14 (the
`gaussian` and `matrix` formal packages with their real Make targets; the
`historical` package's Python audits, with `formal/**` declared whole since
its Mathlib-backed build was not run locally). The first hosted runs on
3.11 and 3.13 are the check that nothing version-specific was missed; an
undeclared input fails that job with the exact pattern to add.

## Requesting the full matrix on a pull request

Fork pull requests cannot be targeted by **Run workflow** in this
repository. Add the `ci:full-verify` label instead: the label event starts a
full run on the pull request's merge commit, with its own concurrency group
so it is not cancelled by later pushes, and every later push to a labelled
pull request also runs everything. Remove and re-add the label to re-run.

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

## Known failures on main at the time of this change

Two tooling commits of 2026-10-14 changed sources that historical packages
pin by hash without updating the pins: d7d8bfcb (`scripts/exclusion_circuit.py`,
pinned by `research/skip-clones`) and 6178dede (`scripts/shared_point_circuit.py`,
pinned by `research/skip-strips`). The `clones` group and the
`test_skip_clones` module fail on that tree, while
`test_exclusion_embedding_masks` and `test_exclusion_support_masks` expect
the new bytes, so the `tests` group cannot pass in either state. This change
does not touch pins or frozen evidence. The input recordings for `clones`
and `tests` were made with the pinned versions of those two files
temporarily restored in a scratch checkout (the set of paths a group reads
does not depend on those bytes); both groups depend on the whole tree and
are declared `**`, so the recordings are not evidence that main passes.
