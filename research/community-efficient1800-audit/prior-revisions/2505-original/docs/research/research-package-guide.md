# Minimal research packages and explicit replay

Use a package for a reusable result or verifier. A discussion finding or handoff
is enough when a session has not established something worth a PR. Existing
packages need not be retrofitted, and frozen source archives must not be edited
to satisfy a new documentation convention.

## Create a draft

From a checkout with committed source inputs:

```sh
python3 scripts/new_research_package.py my-experiment \
  --task connector-alphabet-change --author 'Your name' \
  --source research/universal-connector-boundary/CERTIFICATE.json
```

The generator creates five files and refuses to overwrite an existing directory:

- `README.md`: scope, result/evidence, reproduction, **Open next questions**, credit.
- `TASK.json`: original card, actual scope, scope-change reason, bottleneck link,
  time budget, outcome, evidence and structured next questions.
- `SOURCES.json`: exact base commit, Git blob IDs and SHA256 hashes.
- `VERIFY.json`: explicit replay commands, inputs, dependency pins and timeouts.
- `verify.py`: a failing draft stub, to replace with a real scoped check.

The original card and selected record are historical **provenance** in Git, so
future priority changes do not invalidate a package. Explicit `--source` entries
are **live inputs**: their working bytes must match their pins. Full Git history
is needed for provenance checks. A source export can instead use an existing
archive-based package format; the generator is optional.

Do not make a new copy of a predecessor package merely to acquire provenance.
Preserve any license/NOTICE obligations if you actually vendor third-party work.
Extra files such as separate `CLAIM.md`, `EXPECTED.json` or `NOTICE.md` are needed
only when they serve a real purpose or a source license requires them.

## Declare the actual scope

`scope_status` is `unchanged`, `refined` or `changed`. The latter two require a
reason. The original card is checked against its pinned catalogue. Keeping an
alphabet and increasing source count is a changed investigation when the card
asked for a new operation alphabet. It may be useful, but say what it contributes.

The metadata checker catches missing declarations and mismatches. It cannot
decide whether a mathematical argument genuinely meets an acceptance gate.
Reviewers must compare the actual work to the original premise.

For each open next question, give `question`, `why_it_matters`, `first_step` and
`blocked_by`. “f(7) is open” is not enough. If no next step is justified, an empty
list with `no_open_questions_reason` is valid. The overlap helper searches the
README; link the structured questions there so people can find them.

## Register a bounded verification command

Replace TODOs, implement the verifier and its meaningful controls, then set
`VERIFY.json` status to `ready`. Its commands are argument arrays, not shell
strings. `{python}` selects the active interpreter and `{package}` the package
directory. They run from the repository root.

The launcher removes inherited `PYTHONOPTIMIZE` from each command's environment.
Otherwise a caller's shell setting can silently disable a verifier's assertions,
including assertions in its Python subprocesses. Other environment settings and
explicit command options remain intact. A manifest can still request `-O` or
`-OO` for a deliberate control; its author must account for disabled assertions.

```sh
python3 scripts/research_package.py --package research/my-experiment --check-only
python3.12 scripts/research_package.py --package research/my-experiment
```

The generic environment is Python 3.12. Standard-library packages need no
dependencies; exact numpy/sympy/scipy pins can be declared in `requirements`.
`--install-deps` explicitly permits installing those pins, preferably in a fresh
venv. Other dependencies, native/Lean builds and long replays need a dedicated
workflow or the package's existing reproducible environment.

Declare every external proof-relevant input in `inputs`; package-local changes
already trigger replay. Use canonical repository-relative POSIX paths, such as
`research/example/input.json`, with forward slashes and no leading `./`, repeated
slashes or dot components. The planner rejects aliases because Git reports the
canonical path when a dependency changes. The generic hook does not infer transitive imports.
Each command has a maximum 600-second timeout and the package total is at most
1200 seconds. A timeout fails and terminates the local process group. These
bounds limit a verification job, not the mathematical search budget.

The [registered-package workflow](../../.github/workflows/research-packages.yml)
selects **only opt-in packages**, using their directories, declared inputs, and shared replay controls.
Its planning job runs for pull requests and pushes to `main` without path filters,
because declared inputs can live anywhere in the repository. Unrelated changes
produce no replay jobs. Git renames count as removal of the old path and addition
of the new path, so packages that depend on either path receive a replay.
Changes to the package runner or this workflow select every registered package.
Each gets a fresh runner and explicit commands. It does not run every historical
`verify.py`. New hooks do not replace existing cold-replay obligations, and a
passing metadata check is not acceptance of a mathematical result.

The planner groups at most 256 package paths into each reusable-workflow batch,
so a shared-runner change can select more than GitHub's single-matrix limit.
Batches run one at a time and each batch runs at most four isolated package jobs;
the per-package fresh checkout, environment and 30-minute job bound are retained.
Changing either workflow selects all registered packages. Selection is never
truncated: more than 256 batches fails explicitly. The ordinary planner CLI keeps
its flat matrix format unless `--matrix-batch-size 256` is requested.
This is a matrix-count bound, not a promise that the largest grouping fits every
GitHub execution limit; the 1 MB job-output limit (estimated in UTF-16) and other
platform limits still apply. The current 450-package matrix is well below it.

## Optional workflow feedback

If something helped or obstructed the session, add a few sentences to your PR
or the [feedback discussion](https://github.com/CrocSwap/integer-mult-bounds/discussions/1200).
Link an existing retrospective instead of duplicating it. Include the task or
priority revision, outcome, largest friction/detour and one suggested change.
Directors record resulting decisions in the priority log, not a log entry for
every agent session.
