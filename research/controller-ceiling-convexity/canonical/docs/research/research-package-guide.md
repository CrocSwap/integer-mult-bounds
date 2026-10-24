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

## Pin exact sources and declare live inputs

Every `SOURCES.json` `files` row records `path`, `usage`, `git_blob` and `sha256`.
`usage: "input"` marks a live input and `usage: "provenance"` binds through the
Git blob at the recorded commit. **Every `usage: "input"` row must also appear in
`VERIFY.json` `inputs`**, because declared inputs drive CI invalidation; the
metadata check (including `--check-only`) rejects an undeclared live pin and
names the path. `inputs` may list more than the live pins (a provenance-only
path can still be declared), never fewer.

A row without an explicit `pin` resolves as `base_commit:<path>`. A file vendored
from a pull-request head can instead carry `"pin": "head:<40-hex sha>:<path>"`,
whose bytes resolve at that commit rather than at the package base. Any other
pin form fails closed. Both forms preserve the exact path, including any LF or
CRLF characters in a Git filename; encode them as JSON escapes in the manifest.
The originating task catalogue
`docs/research/agent-task-catalog.json` must stay pinned at `base_commit`, so a
later catalogue revision cannot replace the card a package answers. Pins resolve
only against Git objects reachable in this repository (the base commit or an
explicit head sha); there is no `external` pin for bytes that are not a Git
object here. For such an input, record its source and a byte-equality check in
the verifier and explain the gap in the README.

Shared Git source readers ignore local replacement refs, including a custom
`GIT_REPLACE_REF_BASE` namespace. Otherwise Git can report the original blob ID
while returning a replacement's bytes, allowing locally generated pins to fail
in a clean checkout. The generator, metadata validator, HEAD input inventory,
committed-byte preflight and package exporter use the stored objects. Replacement
refs are left intact; the policy applies only to these Git subprocesses and does
not change the caller's environment or verifier subprocesses. This authenticates
source bytes, not publication ancestry or mathematical claims; the optional
source-history preflight below remains separate.

Regression controls use temporary Git repositories with blob and commit
replacements, the legacy batch fallback, newline paths, a custom replacement
namespace, forged live pins and an exported payload:

```sh
python3 -W error -B -m unittest discover -s tests -p 'test_research_git_replacements.py' -v
```

This extends the immutable-object policy of Nick Petalas's
[source-history preflight (PR3304)](https://github.com/CrocSwap/integer-mult-bounds/pull/3304)
to the shared source readers. The runner and scaffold retain Douglas Colkitt's
attribution, and the exporter retains Tekalign's. Added regression coverage and
reader policy prepared for roger-sato with substantial OpenAI Codex assistance;
Apache-2.0.

`original_card` in `TASK.json` must equal the full pinned catalogue card object.
Hand authors can print the exact object instead of copying it by hand:

```sh
python3 scripts/research_package.py --package research/my-experiment --print-card <task-id>
```

Paste the printed object verbatim as `original_card`; the checker reports every
key by which a copied card differs from its pin.

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

Each registered verification command also receives a fresh private Python
bytecode-cache namespace, removed after success, failure or timeout. This keeps
preexisting `.pyc` files from replacing source-authenticated modules: `-B`
disables cache writes but still permits cache reads. The runner replaces any
interpreter-level `-X pycache_prefix` with its own namespace; other interpreter
options and script arguments are preserved. This policy covers imports in that
registered interpreter, not separately launched child Python processes or direct
verifier calls. See the [source-binding reproduction and limits](bytecode-replay-isolation.md).

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
slashes or dot components. Each input must use its exact UTF-8 spelling in the
current `HEAD` tree. Validation and planning read that tree with NUL-delimited
Git output; neither filesystem case folding nor Unicode normalization defines
input identity. Untracked and staged-only inputs must be committed before they
can be validated. The index cannot override the spelling in `HEAD`.

Planning also permits exact paths reported by its Git diff, so deleted inputs
and both sides of case-only renames still select their consumers. Validation
continues to require a present file: remove or update obsolete declarations
before replaying the selected package. A stale missing declaration outside the
current diff fails planning rather than silently becoming irrelevant. Git
failures publish no matrix. These shared boundaries require a Git checkout with
a valid `HEAD`; direct standalone verifiers keep their own source-export
contracts. The generic hook does not infer transitive imports.

Existing components below the repository root must
also be free of symbolic links. The planner and metadata validator reject these
aliases because Git reports changes under the target's path. Declare that
target path instead. Missing inputs still participate in replay selection, so
deleting an input or its parent directory cannot suppress its consumer's replay.
The checkout must remain stable during planning, validation and execution; these
checks do not provide an atomic filesystem snapshot. The generic hook does not
infer transitive imports.

Each command has a maximum 600-second timeout and the package total is at most
1200 seconds. On POSIX, the launcher terminates the command's local process
group on every exit, including success, failure, timeout and interruption, so
background solver processes in that group cannot continue into another replay.
Verification commands must wait for all proof-relevant children and propagate
their failures before returning; cleanup is not evidence that unfinished checks
passed. Descendants that deliberately detach into another group/session are
outside this cleanup contract. On Windows, tree cleanup uses `taskkill` while
the leader is still running; cleanup after leader exit needs a separate native
lifetime mechanism and is not provided here. A timeout still fails. These
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

## Export committed bytes

Use the [committed package exporter](package-export.md) to snapshot one package
and its declared inputs with deterministic archive metadata and an offline
integrity check. Export is separate from mathematical verification and does
not infer transitive dependencies.

## Explain replay selection

```sh
python3 scripts/research_package.py --changed-since origin/main \
  --explain-plan /tmp/replay-reasons.json
```

The normal stdout matrix and `--github-output` fields stay unchanged. The
optional JSON sidecar names every selected package and all three independent
causes: changed files inside its directory, changed declared inputs, and changed
shared replay controls. It includes the resolved base/head, exact changed and
unmatched paths, and SHA256 of each selected working `VERIFY.json`. A removed
or renamed input is reported under its old spelling when that triggers a replay.
The all-zero base mode is labelled `all-tracked` with a null base.

Selection and explanation use one pass. A validation or sidecar-write failure
publishes no new stdout/GitHub matrix; a previous complete sidecar is left alone
on validation failure. Use the command exit status and base/head to distinguish
an old report. The sidecar is atomically replaced after complete serialization.
It explains selection from working manifests or authenticated unchanged sparse
HEAD manifests; it is not a claim that working manifests equal HEAD or that dependencies
were inferred transitively. Keep the checkout stable during planning. No verifier
runs and no mathematical acceptance follows from selection.

Regression command:

```sh
python3 -B -m unittest discover -s tests -p 'test_research_plan_explanations.py' -v
```
Tekalign, with substantial OpenAI Codex assistance; the existing selector and
its invalidation rules retain Douglas Colkitt and Charles Bethin's attribution.

## Check publication bytes

After committing a package and before publishing it, optionally compare its
working files and declared inputs with the exact commit:

```sh
python3 scripts/check_research_commit.py --package research/my-experiment
# For a different publication commit:
python3 scripts/check_research_commit.py --package research/my-experiment --ref COMMIT
```

Git attributes or clean filters can make a valid local source-hash receipt
describe different bytes from those committed, even when `git diff` is empty.
This read-only check compares raw bytes and reports missing, extra or changed
files. It includes tracked and nonignored untracked package files plus the
explicit `VERIFY.json` inputs, and rejects committed links/submodules.
Ignored runtime files and undeclared external dependencies are outside scope.

If a mismatch is intentional, use an explicitly documented source adapter;
otherwise correct the working bytes or publication commit and rerun the
affected verifier before regenerating its receipt. The preflight never changes
files or normalizes scientific evidence. Passing it does not run the verifier,
validate the mathematics, or establish equivalence to a hosted CI environment.

### Check declared source history before publication

A correct source pin can work locally because another research branch left its
commit in the shared object store. A clean hosted checkout may not contain that
unmerged commit. To reject that dependency before pushing, opt in to the
publication preflight's history check:

```sh
python3 -B scripts/check_research_commit.py --package research/my-experiment \
  --check-source-history
```

After the existing byte comparison, this reads `SOURCES.json` from the exact
publication commit. It requires the base commit and every supported explicit
`head:` source-pin commit to be ancestors of that publication. Separate local
branches and cached objects do not satisfy the check. Git replacement objects
and legacy grafts cannot supply the ancestry. A shallow repository fails with
a request for full history. The successful result lists the checked commit IDs
in `source_history_commits`; the default byte-only command is unchanged.

If a pending predecessor fails, retain its exact bytes, hashes and credit in
your own published history or a self-contained committed export, then bind the
package to that retained source. Do not weaken hash or mathematical assertions.
The repaired PR3234 and PR3227 provenance chains motivated this opt-in check.
An intentional external dependency can remain external, but this stricter
publication check will not pass it. Document and test its explicit fetch step
instead of treating the local object cache as evidence of cold availability.

This is a conservative check of **declared Git-history availability**, not full
metadata validation or a cold replay. Run the registered metadata and verifier
commands separately. It does not discover pins embedded in scripts or archives,
transitive imports, submodules, LFS payloads, dependencies or network services.
No source bytes, pins, Git refs or frozen evidence are changed. The new path
limits source metadata to 16 MiB, 100,000 rows and 256 distinct commits, with a
30-second timeout on each Git query. The checkout must remain stable.

Regression commands:

```sh
python3 -W error -B -m unittest discover -s tests -p 'test_research_source_history.py' -v
python3 -W error -B -m unittest discover -s tests -p 'test_research_commit_bytes.py' -v
```

The tests build synthetic Git histories and a bare object-only fixture, without
cloning the project or fetching remote objects. A valid side-commit pin passes
byte-only comparison but fails ancestry; exporting only the publication's
reachable objects confirms that the foreign commit is missing. Ancestor pins
pass the same cold object test. Replacement/graft, shallow-history, malformed
metadata, resource-limit, Git-failure and actual CLI controls remain active
under optimized Python. This is not a theorem or supplier-admission check.

Open next questions are explicit dependency declarations for script-embedded
Git references and separately fetched sources. Start with one actual replay's
source manifest and fetch command. Automatic import inference is not supplied
by this check and would need its own contract and failure controls.

The planner groups at most 256 package paths into each reusable-workflow batch,
so a shared-runner change can select more than GitHub's single-matrix limit.
Batches run one at a time and each batch runs at most four isolated package jobs;
the per-package fresh checkout, environment and 30-minute job bound are retained.
Changing either workflow selects all registered packages. Selection is never
truncated: more than 256 batches fails explicitly. The ordinary planner CLI keeps
its flat matrix format unless `--matrix-batch-size 256` is requested.
This is a matrix-count bound, not a promise that the largest grouping fits every
GitHub execution limit; the 1 MB job-output limit (estimated in UTF-16) and other
platform limits still apply. The submission measured 450 selected packages; later repository inventories may be larger.

## Optional workflow feedback

If something helped or obstructed the session, add a few sentences to your PR
or the [feedback discussion](https://github.com/CrocSwap/integer-mult-bounds/discussions/1200).
Link an existing retrospective instead of duplicating it. Include the task or
priority revision, outcome, largest friction/detour and one suggested change.
Directors record resulting decisions in the priority log, not a log entry for
every agent session.

## Planning in a sparse checkout

Replay selection inventories both committed `research/*/VERIFY.json` paths and
working manifests. Omitting a package directory from a sparse checkout must not
omit its declared input dependencies from the matrix. Absent manifests are read
from Git only when one stage-zero, regular, `skip-worktree` index entry has the
same mode and blob as HEAD. The planner reports the number of such declarations
on stderr; stdout and GitHub matrix formats stay unchanged.

An ordinary missing file, staged content/mode change, unmerged index entry,
symlink manifest or unreadable inventory still fails. Commit an intentional opt-in
removal before planning that deletion. Existing working edits and new local
manifests are read as before, and all declared input spelling checks still run.
A fully omitted `research/` directory is supported when its manifests satisfy
the same Git/index checks. The checkout must remain stable during planning.

This discovers declarations; it does **not** make sparse packages executable.
Materialize a selected package and its required inputs before actual validation
or replay. Partial clones may need Git's normal fetches for missing manifest
blobs. The fix needs only those declarations, not the full source packages.
Immutable inputs and upstream archives are unchanged.

At base `997e6a9ca7b4f95d50e366f61412fd640d72a88a`, HEAD contains 1,244 registered
manifests, while the contributor's sparse checkout initially materialized 18.
The earlier filesystem-only scan returned an 18-package global-trigger matrix.
The real sparse/full fixture and rejection controls can be reproduced with:

```sh
python3 -B -m unittest discover -s tests -p 'test_research_sparse_planning.py' -v
```

Tekalign, with substantial OpenAI Codex assistance. Apache-2.0. The exact
HEAD/index fallback premise follows Arham-Tahir64's PR3102 sparse-reference work;
this applies it to replay declarations. The original planner, canonical Git
spelling, symlink and inventory-error controls retain their predecessor credit.
