# Current-source imports in ordinary unittest descendants

The isolated unittest runner now passes a private per-module bytecode-cache
namespace and a no-write policy to ordinary environment-inheriting Python
children and grandchildren. A source-bound differential on an **existing test**
shows the previous runner passing with stale bytecode while the same current
source fails after only that cache is removed. The successor reports the
current-source failure in both cases. This repairs a verification-tooling
boundary; it does not establish a mathematical certificate bypass or a new κ.

## Exact result

The pinned test is
`SourceHistoryTests.test_real_cli_is_read_only_and_reports_no_pass_on_history_failure`
in `tests/test_research_source_history.py`. Its actual child command is:

```text
python -B <scratch>/scripts/check_research_commit.py --package research/fixture --check-source-history
```

That child imports `research_package.py`. PR2990 protects the unittest process
with `-X pycache_prefix`, but interpreter options are not inherited by this
child. `-B` prevents writes while still allowing cache reads.

The differential retains the original test body and child command. A subclass
only plants an artificial numeric disagreement in the test's disposable Git
fixture: compile the authenticated helper's original `len(fields) == 3`
Git-response parser, then change that one digit to `4` in equal-length current
source with the original timestamp. No repository source, proof, certificate,
input hash or production guard is modified by replay.

[RESULT.json](RESULT.json) records sixteen real CLI executions:

| Fixture | Pinned previous runner | Successor |
| --- | --- | --- |
| Original three-field source, timestamp / unchecked hash | Pass | Pass |
| Four-field current source, stale three-field timestamp cache | Pass | Fail |
| Four-field current source, stale three-field unchecked-hash cache | Pass | Fail |
| Same four-field source, only the cache removed, both modes | Fail | Fail |
| Stale unchecked-hash cache under an inherited external prefix | Pass | Fail |
| Checked-hash cache with changed current source | Fail | Fail |

Failures must come from the original test's `AssertionError: 1 != 0` and the
child's `missing or non-blob Git source` error, rather than early exit, timeout
or a missing completion receipt. Every run checks that source bytes/timestamps
and preexisting cache bytes are unchanged and that the owned completion/cache
directory has been removed. The scratch parser failure is deliberately benign;
no invalid mathematical certificate is supplied or accepted.

## Implementation and additional controls

`scripts/run_isolated_tests.py` gives each module a fresh environment copy with
`PYTHONPYCACHEPREFIX=<owned completion root>/<module>-descendant-pycache` and
`PYTHONDONTWRITEBYTECODE=1`. Its direct unittest and historical wrapper keep
their existing explicit `-X` namespaces. Descendants in one module share the
inherited namespace; different modules have distinct namespaces. No caller's
process environment is mutated. The existing process ownership, completion,
ordering and cleanup paths remain in use.

Eleven public-CLI groups in `tests/test_isolated_test_bytecode.py` retain the
original direct-import and historical-route controls and add ordinary children,
grandchildren, external caches, and a no-`-B` child with cache writes enabled in
the caller. An observer inside that child verifies no numeric-helper cache was
written before cleanup. Concurrent success/failure fixtures place markers in
both direct and inherited namespaces and check all four directories are distinct
and removed. The historical tooling adapter additionally admits the new runner
digest while retaining and executing its authenticated original source.
The registered-interpreter test's deliberately unprotected negative control
now explicitly removes an inherited cache prefix. Its failure assertion remains
unchanged; otherwise this repair would protect that control when the full
isolated test runner launches it.

## Reproduce

Use a full-history checkout, Git, CPython 3.12 and a writable temporary directory;
no third-party Python packages are needed. Source commits, Git blobs and SHA256
pins are in [SOURCES.json](SOURCES.json). Canonical scientific base is
`6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6. The original
runner is provenance; the manifest also declares the evolving live runner and
regressions for replay selection.

The `research_package.py` source row is historical provenance: `verify.py`
loads that helper from the exact base-commit Git blob and checks its original
SHA256 before copying it into the differential fixture. Its base, blob and
SHA256 are unchanged. The original manifest is retained at commit
`20ecf2891d80b5acf18d980b2164fb44ea7faa90` (blob
`5e2d5560769ca754175472d123829a8586bb4ddc`). Classifying this row as a live
byte pin incorrectly prevented compatible changes to the current helper.
`VERIFY.json` still declares the current helper as an input for replay
selection, and its unchanged third command runs the eight current-helper
bytecode regressions. The sixteen-run historical differential, all three
registered commands, verifier and `RESULT.json` are retained unchanged.
This metadata correction was prepared for roger-sato with substantial OpenAI
Codex assistance; Arham Tahir's original work and source credit are retained.

The `tests/test_research_source_history.py` row likewise authenticates the
original test copied by `pinned_sources()` from the exact base-commit Git blob;
the verifier does not import the live test file. Its original commit, blob and
SHA256 remain unchanged. Classifying that row as provenance permits the live
test's disposable Git fixtures to disable automatic maintenance, preventing
detached writers from racing temporary-directory cleanup. `VERIFY.json` still
declares the current test as a planner and publication input. The original
sixteen-run differential, verifier, commands and result remain unchanged.
Regression controls require the historical replay to pass even when a live
test copy cannot import, retain rejection of original pin corruption, and
confirm live changes still select replay and fail uncommitted-byte checks.
This fixture repair was prepared by Clear1nsight with substantial OpenAI
Codex assistance; it changes no source-history validation or research claim.

```sh
python3.12 -B scripts/research_package.py --package research/isolated-descendant-bytecode --check-only
python3.12 -B scripts/research_package.py --package research/isolated-descendant-bytecode
python3.12 -W error -B -m unittest discover -s tests -p 'test_isolated*.py' -v
python3.12 -W error -B -m unittest discover -s tests -p 'test_historical_check.py' -v
```

The primary marker is `PASS_ISOLATED_DESCENDANT_BYTECODE` inside the JSON result;
the registered replay also prints `PASS_REGISTERED_RESEARCH_PACKAGE`.
Exact local commands, interpreter versions, outcomes and the final upstream
checkpoint are recorded in [TASK.json](TASK.json).

## Limits and remaining obligations

This covers normal default imports in environment-inheriting descendants of the
isolated unittest runner. A child using `-I` or `-E`, an explicit `-X` prefix,
a replacement environment or a custom loader retains its own policy. A public
CLI control deliberately demonstrates the remaining `-I` stale-cache gap and
its cache-removed failure. The change does not rewrite descendant commands,
force an interpreter, authenticate arbitrary descendants or prevent tests from
explicitly writing/reusing bytecode. Standalone bytecode, already loaded
modules and concurrent source mutation are outside scope.

No runtime speedup is claimed. Fresh imports may add startup cost. No native
Windows/Linux execution, repository-wide suite, selected cold replay, supplier
admission, hosted-CI success or full multiplication theorem follows from local
macOS tests. Native process-lifetime skips and exact verification results are
reported in TASK rather than inferred from successful import tests.

The historical regression suite has a preexisting stale allowlist for
`docs/ci-verification.md` at the pinned main: its actual SHA256 is
`a3711fe12d560fac7726c530b9c8c622182f3d4f231a876c163616e49bd911bc`.
The original main's `authenticated_input` rejects it too. Main also omitted its
newer deadline-enabled runner digest; this change admits only its own complete
successor digest. The unrelated document-pin repair remains open, and a full
historical-suite pass is not claimed.

## Open next questions

Which concrete test launches a Python child with `-I`/`-E` but lacks an explicit
fresh cache boundary? Pin one caller and helper, reproduce a benign numeric
mismatch, and add explicit arguments at that caller. This matters because the
inherited policy is intentionally ignored there. A named caller and its own
source-bound regression are required before expanding this repair; there is no
justification for another general descendant census here.

## Credit and coordination

Nick Petalas owns PR2990's direct unittest/historical cache boundary and explicit
next-test handoff in [Discussion2988](https://github.com/CrocSwap/integer-mult-bounds/discussions/2988).
His source-history checker/test is retained at `77cb5ea616b647c6d451fbf1e113e1e338df6210`.
PR2553 and the frame-closure-child-isolation package retain their earlier
registered-interpreter and explicit child-adapter credit; the latter's caller
uses `-I` and is outside this inherited-environment repair. Douglas Colkitt and
all credited isolated-runner, completion, concurrency and lifecycle contributors
retain their predecessor work. No preceding result is counted as new here.

This closes one ordinary-child implication left by those predecessors. The
entry overlap helper completely paginated 257 open PRs and 2,181 Discussion,
comment and reply records and searched 3,738 local records. Arbitrary diffs,
closed PR bodies and unpublished work were outside that entry snapshot; final
freshness is in TASK. The exporter consumer handoff had an active claim, so the
verifier-engineering picker was refined to this unclaimed explicit handoff.

Arham Tahir, with substantial OpenAI Codex assistance. New work Apache-2.0;
original source notices retained. Author-checked; no independent human or
subagent review claimed. Selected frontier and frozen packages are unchanged.
