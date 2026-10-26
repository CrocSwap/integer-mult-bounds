# Windows ownership in the shared Git blob reader

The shared `git_blobs` reader now uses the gated Job Object owner and launch
status channel from [PR5463](https://github.com/CrocSwap/integer-mult-bounds/pull/5463)
and [PR5524](https://github.com/CrocSwap/integer-mult-bounds/pull/5524) on Windows.
Previously, a descendant retaining a pipe could survive the Git leader or keep
a response blocked after the direct-child timeout. The reader now stops the
owned job before closing buffered pipes on success, timeout, generator close
and consumer failure. The requested executable's native launch errors remain
exceptions; only a successfully launched command exiting 129 can trigger the
existing compatibility retry.

This is an author-checked tooling integration. It makes no mathematical,
selected-frontier, general subprocess, or independent-review claim.

## Task and source boundaries

- Task: `portable-replay`, verifier engineering, chosen from the production
  adoption handoff in [Discussion1166](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166)
  and PR5524's **Open next questions**. The retrieved catalogue card had nonce
  `0f543fba2362863680106573ad15451a`, scope key `91a9a2afec282c926282`,
  and priority revision 7.
- **Changed scope:** integrate the existing native owner at one shared process
  factory and exercise its consumers, rather than compare compressed replays.
  This addresses the predecessor's explicit adoption gap without opening a
  new construction family.
- Started from canonical main `5e0052ca0aa3036a3afa8b0438927377c8d97d53`;
  refreshed to `df0137efd35e11b4445734bf612bdd4c7ebc330c` before submission.
  Priority revision 7 and the relevant shared reader/predecessors were unchanged.
  The initial selected orientation returned
  `PASS_RESEARCH_BASELINE_BINDINGS_ONLY` for frontier5413. The refresh selected
  frontier5599; no cold mathematical replay of either selection is claimed.
- Direct sources: PR5463 head `991da9010925914ec64a5293286edb10a7910218`
  and PR5524 head `b11f5ab7df36fbde44e9f2de3498e3e77f2eb4ee`.
  `scripts/research_windows_git.py` combines PR5524's
  `vendor/owned_pipe.py` and `spawn_checked.py`; its wrapper uses the same-module
  owner instead of accepting an owner module parameter. Frozen packages remain
  unchanged. [PR5461](https://github.com/CrocSwap/integer-mult-bounds/pull/5461)
  is the predecessor diagnosis, not a new audit result here.
- Milestone: shared-tool integration with bounded native regression evidence.
  Success means descendant termination observed **before fixture teardown**,
  exact binary/source-pin behavior, preserved launch exceptions and fallback,
  and existing consumer checks. A direct-child replacement must fail all six
  lifetime cases. No cost-law, supplier-restoration or kappa claim applies.
- Overlap: read the start/handoff discussions and active discussion listing;
  targeted live PR searches for `5524` and `Windows Git` found the predecessor
  work, but no equivalent shared integration. The offline helper covered only
  3 of 7,611 local tracked records in the initial sparse checkout and had no
  refreshed remote cache. The canonical investigation thread could not be
  fetched. These checks are partial coverage, not proof of novelty.

## Integration contract

`_git_blob_popen` is the launch boundary. POSIX retains its existing `Popen`
session and process-group behavior. Windows lazily imports the companion module,
including when the reader is loaded by file path under isolated Python. Protocol
fixtures patch this boundary; installed-Git and native ownership fixtures retain
the real factory. The scaffold check still observes two metadata calls and one
blob stream; its optional benchmark also counts the Git launch inside the native
gate. No timing improvement is claimed. Standalone copies of `research_package.py` that read blobs on
Windows must include `research_windows_git.py` beside it. Temporary CLI fixtures
have been updated accordingly.

Two existing fixture assumptions needed Windows fixes: the historical object
store's `alternates` file now uses literal LF instead of translated CRLF, and
the sparse nonregular-manifest test creates its Git symlink-mode entry directly
without requiring filesystem symlink privilege. The tested predicates remain
the same.

The native helper creates the job and event, starts an isolated Python gate,
assigns that gate to the job, and only then releases it to launch the requested
argv. A separate bounded JSON status file preserves launch diagnostics without
touching Git's binary stdout. Job termination is idempotent and synchronized.
The per-response timer still excludes time spent in the consumer. Startup has a
separate ten-second report deadline, and cleanup retains the predecessor's
ten-second accounting bound.

The planner treats the companion module as a shared control, so a helper-only
change selects all registered packages, including omitted sparse manifests.
`git_source_rows`, separate `git()` metadata calls and the registered verifier
process runner are outside this change.

## Reproduction and evidence

Host: Windows 11 build 26300, CPython 3.12.10, Git for Windows 2.53.0.windows.3.
Use Python 3.12 and installed Git from the repository root. Windows process
creation and a writable temporary directory are required. Warnings were errors.

```sh
python -W error -B -m unittest discover -s tests -p 'test_research_git_*.py' -v
python -W error -O -B tests/test_research_git_windows.py -v
python -W error -B -m unittest discover -s tests -p 'test_research_export_*.py' -v
python -W error -B tests/test_research_commit_bytes.py -v
python -W error -B tests/test_research_source_history.py -v
python -W error -B tests/test_research_scaffold_batch.py -v
python -W error -B tests/test_research_sparse_planning.py -v
python -W error -B tests/test_research_head_pin_paths.py -v
python -W error -B tests/test_research_onboarding.py -v
python -W error -B tests/test_research_package_diagnostics.py -v
python -W error -B tests/test_research_replay_selection.py -v
python -W error -B tests/test_research_input_paths.py -v
python -W error -B tests/test_research_symlink_inputs.py -v
python -W error -B tests/test_research_descendant_source_roles.py -v
git diff --check
```

All listed commands passed. The final results were:

| Check | Tests run | Skipped on this host |
|---|---:|---:|
| Git reader suites, including five native Windows tests | 67 | 8 |
| Native Windows tests under `-O` | 5 | 0 |
| Export suites | 26 | 0 |
| Commit bytes / source history | 11 / 13 | 0 |
| Scaffold / sparse planning / head-pin paths | 3 / 11 / 3 | 0 / 0 / 2 |
| Onboarding / diagnostics | 27 / 16 | 0 |
| Replay selection / input paths / symlink inputs | 9 / 5 / 14 | 1 / 0 / 5 |
| Descendant source-role compatibility | 10 | 0 |

The source-role fixture requires its historical objects in the local Git store;
these were materialized before the successful run in this partial clone. The
optional timing benchmark was not run. The scaffold regression verifies the
three-call budget and exact generated pins instead.

The native regression retains process handles rather than relying on PID lookup.
Its six lifecycle cases are success, header stall, payload stall, terminator
stall, early close and consumer error. A four-second rescue guard bounds broken
implementations; any use of that guard fails the test. The direct-child mutation
is required to produce six failures and no fixture errors. Launch comparisons
check exception type and all five native error fields. The launched-exit control
checks 0, 1, 7 and 129; only 129 retries, returning two exact 80,000-byte blobs.
Unicode argv/environment/cwd and unmodified binary stdout have a separate case.

Before integration, the unchanged PR5524 native verifier passed its 25 named
case groups on this host. That is predecessor evidence, not a substitute for
the shared-reader checks above.

## Open next questions and limits

1. Run the shared consumer and POSIX descendant suites on Linux/macOS. This
   session has a native Windows host only; POSIX cases and unsupported filename
   cases skip. Windows filesystem-symlink tests also skip without the privilege;
   junction tests and the Git-index symlink-mode check do run.
2. Review the adopted adapter and repeat native checks on another Windows/Python
   version and under restrictive enclosing jobs. Hard owner death during setup,
   abrupt parent termination and job-policy denial are not newly certified here.
3. The helper supports the reader's nonempty string argv, binary streams and
   context-manager usage. It does not implement general `Popen` options. Launch
   timing does not bound all Windows process-creation or filesystem operations.
   The status file is a trusted local control channel, not a security boundary.
   Installed older Git was not available; the launched-129 fixture exercises the
   retry with actual current Git serving the resulting blobs.

## Attribution

Credit Mihir Srivastava for the PR5463 owner and PR5524 launch diagnostics;
ywz65 for the gated Job Object lifecycle (PR2469) and retained native-handle
observer (PR2452); Brian / JoyboyBrian for response deadlines (PR4738) and POSIX
lifetime controls (PR5185); Nick Petalas for the blob/compatibility reader
(PR2752); and Douglas Colkitt for the package runner. Arham Tahir, Woklerx,
yssite, Paul Romeo, Tekalign and the retained source/fixture lineage keep their
credit. The predecessor `NOTICE` and `vendor/NOTICE` remain intact.

Integration and regressions prepared for josecarlosgonzalezroque-design with
substantial OpenAI Codex assistance, one agent. Apache-2.0. No independent human
or separate-agent review has been performed by this session.
