# Large selected inventories in Windows sparse checkouts

The selected-source preflight could reject a valid sparse checkout on Windows
because it passed every omitted input to Git in one process command. This repair
batches calls to the existing sparse validator. It preserves the file checks,
sorted omission list, materialization advice, schema routing and exit codes.

## Reproduced failure

At canonical main `cef4b52f2a59009865bf8eabde1be3f159063703`, the selected
inventory contains 523 distinct paths. A cone checkout containing `scripts`,
`docs` and `certificates` omitted 503 of them. The resulting `git ls-files`
command was 38,351 characters long. On native Windows with CPython 3.12.0 and
Git 2.47.1.windows.1 it failed with `FileNotFoundError [WinError 206]`.
The validator caught the launch error and then reported
`Invalid selected file: notes/batched-bit-rows.tex`, although that file had a
regular stage-zero skip-worktree entry matching HEAD. Checking it alone passed.

Microsoft documents the process command limit as 32,767 characters including
the terminating null in
[CreateProcessW](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw).
The new batching uses a conservative 16,000 UTF-16-unit path-argument budget,
including Windows quoting and separators, leaving room for Git's fixed arguments.
An individually unlaunchable path remains an error; batching addresses the
aggregate inventory size, not arbitrary filesystem path limits.

Every batch still calls `choose_research_task.check_catalog_files`. Ordinary
deletions, nonregular entries, changed index blobs and Git failures retain that
validator's rejection behavior. A later failure raises before any omission
report is printed. As before, the checkout must remain stable during inspection;
this is not an atomic snapshot or a source-hash check.

## Evidence and reproduction

The new real-Git fixture contains 600 omitted files with spaces, literal
pathspec metacharacters and a supplementary Unicode character. Its unbatched
command exceeds the Windows limit. The fixture checks complete path coverage
in both index and HEAD inventories, successful CLI materialization and a final
zero-omission report. Controls change the final input's index blob, turn it into
an ordinary deletion, and fail a later Git inventory call. The command-size
failure is also simulated on other platforms while actual Git supplies the data.

Before the fix, the five new tests all failed on Windows (four failures and one
error), including the unmocked CLI. After the fix, all 14 sparse-baseline tests
passed normally and under `-O` on Windows; the same 14 passed on Ubuntu/WSL.
The existing small cone/non-cone, legacy/explicit manifest, omitted metadata and
maintenance-cleanup fixtures remain unchanged.

After materializing the current selected inputs, the preflight returned
`NO_SPARSE_SELECTED_OMISSIONS` and the unchanged selected baseline returned
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY` on Windows. This authenticates the
selected metadata closure; the full mathematical cold replay was not run.

All 6,136 tracked top-level `research/*/SOURCES.json` and `VERIFY.json` files
were read and their working bytes compared with their HEAD Git blob IDs. None
has an exact-path live pin, provenance pin or declared replay input for
`scripts/research_baseline_sparse.py`. Nested manifests and undeclared runtime
reads are outside this dependency check. The pinned chooser and baseline
implementations retain their bytes.

The broader Windows helper command (`PYTHONUTF8=1`, pattern
`test_research_*.py`) ran 362 tests: 322 passed, 22 skipped, and 18 had setup
errors. Twelve fixtures require newline-containing filenames unsupported by
Windows; six initially lacked the sparsely omitted descendant-bytecode fixture.
After materializing that package and its historical source objects, its native
rerun passed three methods but three still failed at historical-source resolution
through the fixture's alternate object store. All 18 affected methods passed on
Ubuntu/WSL (the six-case `test_research_overlap_local.py`,
`test_research_plan_explanations.py` and `test_research_descendant_source_roles.py`
modules). Those unchanged fixtures and their pins are outside this repair.
No clean full native Windows run or complete local Linux suite is claimed.

```sh
python -W error -B -m unittest discover -s tests -p 'test_research_baseline_sparse*.py' -v
python -W error -O -B -m unittest discover -s tests -p 'test_research_baseline_sparse*.py' -v
python -B scripts/research_baseline_sparse.py
```

Exit 2 means valid sparse omissions were found; exit 0 means no input is omitted.
Neither outcome authenticates the input bytes or proves a mathematical claim.
The subsequent `research_selected_baseline.py` and selected cold-replay command
retain their separate obligations.

## Task, overlap and attribution

Card: `portable-replay`, priority revision 7, chooser nonce
`1568f02fbdb6dc3102dbdeab4f3c4e6e`, scope key `831cc1a3c8f9ff01b197`.
Scope refined to the specific native Windows launch failure encountered during
selected-baseline orientation. The bounded success condition is a working large
inventory CLI with complete coverage and retained rejection controls. No
scientific package or selected-frontier file is changed; no new kappa is claimed.

The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4458#discussioncomment-19136447)
records the base, method and limits. Entry overlap covered 304 open PR bodies
and 4,003 Discussion records at 2026-10-23 02:22/02:23 UTC, with complete reported
pagination. Sparse local-note coverage was incomplete at entry. Targeted live
and closed-PR searches found the following distinct predecessors; these checks
do not establish novelty against every diff or unpublished investigation.

The submission refresh at 02:38/02:40 UTC covered 308 open PR bodies, 4,007
Discussion records and all 6,601 tracked in-scope local notes, with complete
reported coverage and no warnings. The exact command-size search found this
claim and the earlier fixture-maintenance handoff. Canonical main was fetched
again before submission and remained the same base commit.

- Douglas Colkitt and the credited Claude agent's preflight, published by
  Mister-Meeseeks in [#3725](https://github.com/CrocSwap/integer-mult-bounds/pull/3725).
- Arham-Tahir64's unchanged sparse/HEAD contract in
  [#3102](https://github.com/CrocSwap/integer-mult-bounds/pull/3102).
- lee-phys's inventory-format and schema-routing repair in
  [#4631](https://github.com/CrocSwap/integer-mult-bounds/pull/4631).
- Clear1nsight's fixture-maintenance repair in
  [#4857](https://github.com/CrocSwap/integer-mult-bounds/pull/4857).
- Mihir Srivastava's productive-helper baseline and generic startup guidance,
  [#4463](https://github.com/CrocSwap/integer-mult-bounds/pull/4463) and
  [#4906](https://github.com/CrocSwap/integer-mult-bounds/pull/4906).

**Open next question:** the preflight's materialization advice still emits one
directory command. If a future selected closure has enough distinct directories
to exceed a process limit, reproduce that directory-level case and provide
bounded materialization advice without changing the authenticated source set.
The present selected closure does not exhibit that second failure. The generic
validator itself also retains its existing behavior for callers other than this
preflight; no claim is made about all large catalogues or arbitrary Git tools.

Prepared by Mihir Srivastava with substantial OpenAI Codex assistance; no
subagents or independent human review. New work is Apache-2.0. Existing source
notices and frozen scientific evidence retain their attribution.
