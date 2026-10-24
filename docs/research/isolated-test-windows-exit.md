# Windows ownership after isolated test modules exit

The isolated test runner could report a successful or failed module while its
ordinary child and grandchild solvers remained alive on Windows. When those
descendants inherited capture pipes, an already-exited module could also leave
the runner blocked. This closes the Windows follow-up to
[Nick Petalas's POSIX exit-cleanup result](isolated-test-exit-cleanup.md), scoped
to ordinary subprocess trees rather than adversarial process containment.

## Change and contract

Each Windows module now has a private supervisor that invokes the existing
`research_package.run_windows_command`. Its gated launcher joins a kill-on-close
Job Object before executing any test code. The supervisor preserves the test
command, environment, captured bytes and exit code, and the reused helper
terminates the job and waits for zero active members before normal return.
There is no second implementation of the native Job Object API.

The supervisor runs with isolated startup, no site initialization and a private
bytecode prefix. The actual test interpreter retains its original arguments,
environment and distinct cache namespace. Unittest completion receipts still
reject premature zero exits. Timeout/cancellation targets the live supervisor;
closing its non-inherited job handle also terminates its owned processes. A
`taskkill` rejection remains an error if the supervisor is still live; its
ordinary exit between polling and `taskkill` is accepted as completed cleanup.

The timeout still starts at actual launch, including supervisor/gate startup.
The healthy Windows deadline fixtures use three seconds instead of one to
allow those two additional interpreter startups. The blocked fixture still
uses the entire same budget, the next queued module receives a fresh budget,
and expiry still reports code 124. The unlimited default is unchanged.

Copies of the isolated runner on Windows must now include `research_package.py`
alongside it. Sandbox tests include that dependency explicitly. POSIX launches
retain their original direct module command and process-group cleanup.

The underlying ownership semantics follow Microsoft's
[Job Objects documentation](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects):
ordinary `CreateProcess` children join the job by default, and closing its final
kill-on-close handle terminates its members. WMI-created processes and other
external launch mechanisms are outside this claim.

## Reproduction and evidence

Native environment: Windows 11 build 26300, x64 CPython 3.12.0. The new fixture
copies the production CLI and existing job launcher, starts a real unittest
module/child/grandchild tree, and holds the three processes at a readiness
barrier while the observer opens native process handles. The same retained
identities are checked after the CLI returns. Teardown independently terminates
retained fixture processes, including deliberately uncontained mutants.

Before the repair, two tests failed because child/grandchild solvers survived
successful and failed module completion. The inherited-pipe fixture exceeded
its 15-second external bound despite a five-second module timeout. Joined
completion passed. The five-test baseline run took 24.860 seconds.

After the repair, the original five controls passed in 13.491 seconds. The
final six-case module also covers timeout, and the cancellation suite adds an
actual supervisor-only kill control. Removing the Windows supervisor restores
the observed leaks on both successful and failed module exits. These timings
describe bounded fixtures, not a speedup benchmark.

Commands from the repository root:

```sh
python -B -m unittest discover -s tests -p 'test_isolated_test_windows_exit.py' -v
python -O -B -m unittest discover -s tests -p 'test_isolated_test_windows_exit.py' -v
python -B -m unittest discover -s tests -p 'test_isolated_test_*.py' -v
python -B -m unittest discover -s tests -p 'test_isolated*.py' -v
```

The broader native run executed 57 tests in 143.426 seconds. All 50 focused
runner cases had their expected outcomes: 42 passed and eight POSIX-only cases
skipped. This covers cancellation, queued work, deadline failures, output-byte
preservation, premature exits, stale bytecode, concurrent private namespaces
and normal module results.

The seven historical-wrapper cases added two passes and five failing methods
(16 failed subtest/assertion outcomes). Each failure stops at the retained
`Unrecognized live source update: scripts/partial_swap/shared.py` check before
its intended assertion. The unchanged canonical-main source has SHA256
`5a0646a50b9f3e8ea55168620a78e8853b0ab810517cefc8cfb8696aedee278a`;
the historical wrapper's allowlist excludes that hash. A separate 16-file
export of unchanged main reproduced the same 16 failure headers and source
errors (seven tests, 17.074 seconds). The old acceptance pins are not relaxed.

The six native controls also passed under optimized Python (`-O`) in 14.892
seconds. On Ubuntu/WSL2 with CPython 3.12.3, all 50 focused cases had their
expected outcomes: 43 passed and seven Windows-only cases skipped, in 33.555
seconds. That includes the real POSIX exit, cancellation and capture-pipe tests.
The existing deliberately weakened cancellation control emits unclosed-pipe
ResourceWarnings; this is the separately documented teardown issue in the
predecessor, not a passing claim for warning-free cancellation.

## Task, source binding and attribution

Base: canonical main `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, priority
revision 7, selected conditional kappa 0.00302015. Card `portable-replay`, chooser
nonce `8fd33b1202dd34fd71d3e95ffb8161f5`. Scope status: refined to one native
environment failure. The initial selected-baseline orientation stopped at a
sparse-omitted `notes/batched-bit-rows.tex`; no selected baseline pass or
mathematical replay is claimed.

The [scoped claim and handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1472#discussioncomment-19126709)
takes the explicitly open Windows task in the existing investigation. Entry
overlap covered 445 open PR bodies and 3,600 Discussion records with reported
complete pagination. Sparse local notes were subsequently materialized; the
repeat searched all 5,860 in-scope tracked notes. Arbitrary code diffs, nested
package sources and all closed remote PR bodies were not exhaustively searched.
No matching open implementation was located; this is not proof of novelty.

Canonical main was fetched again at 2026-10-22T15:47:33Z and remained the same
commit. The selected record, priorities and reused native implementation were
unchanged. No selected source or frozen acceptance pin is modified.
The submission overlap refresh at 15:47:37Z/15:48:55Z covered 450 open PRs,
3,612 Discussion records and all 5,860 in-scope local notes, with complete
reported pagination and no coverage warnings. It found the predecessor handoff
and this claim, with no overlapping open implementation located.

Exact base-source SHA256 hashes:

| Source | SHA256 |
|---|---|
| `scripts/run_isolated_tests.py` | `ef5035e6216d39569da670f32b2717c870b23c418016fd134cc0a72649fb912a` |
| `scripts/research_package.py` (reused unchanged) | `3ff38a291677f9ebbbe54379d629208b17b7f526f73aee46d5f850ead768504e` |
| `tests/test_isolated_test_exit_cleanup.py` (reused fixture strings) | `267c8d94c1b5f07520e3254100599225f73943c6205bcb901fc1c6975658872d` |
| `tests/test_isolated_test_cancellation.py` | `014db7e16518254eb566c2ad2fa98d2f5dd4aea7525707530bc34e97ba9ed0d3` |

Credit Nick Petalas / #2906 for the POSIX exit-cleanup result and ready-tree
fixtures; ywz65 / #2469 for the registered runner's gated Job Object, #2625 for
cancellation and #2579 for completion receipts; Paul Romeo for the earlier
Linux observer and Windows handoff; Aaron Wang/navinor for isolated scheduling;
woklerx, Douglas Colkitt, Tekalign and the retained bytecode/timeout contributors.
Prepared for Mihir Srivastava (@mihir-s-05) with substantial OpenAI Codex
assistance, one agent. Apache-2.0. No independent human review is claimed.

## Open next questions and limits

Test modules must join proof-relevant children and propagate their failures.
Stopping unfinished work does not prove it passed. This is a verifier lifetime
repair, with no supplier, exponent or selected-frontier change. Hosted CI,
macOS, the complete historical suite and the selected cold replay are unrun.

The bounded next platform check is the same six native controls on the existing
Windows 3.14 review runner. A separate useful hardening question is abrupt
supervisor death before the gated launcher has joined its job: no test workload
can pass the gate before assignment, but a transient unassigned waiter can live
until its own 30-second gate timeout if both tree cleanup and ownership are
interrupted. This contribution does not claim that early-startup case, detached
external processes, denied native APIs or a hostile-process sandbox.

The source-pin mismatch in the historical wrapper needs its own exact-source
review before any successor is admitted. It is not repaired by this lifetime
change. Further cleanup work should retain the native-handle observations and
the uncontained-launch mutation, rather than counting zero exit codes alone.
