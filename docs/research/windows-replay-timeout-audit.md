# Native Windows replay timeout observation

This answers the Windows observer handoff in [discussion #1472](https://github.com/CrocSwap/integer-mult-bounds/discussions/1472).
The historical `tests/test_research_windows_process_tree.py` checks the frozen
pre-Job-Object launcher's native `taskkill /F /T` branch against a ready parent, child and
grandchild. All three process objects stop on timeout. Replacing tree cleanup
with a successful-looking parent-only kill is rejected because the retained
child and grandchild handles still report live processes.

This contributes missing native-platform coverage. It changes no production
launcher, mathematical source, selected result or supplier claim.

## Scope, sources and overlap

Task `portable-replay`, priority revision 4, selection nonce
`bee056178d0d10813b1e128c510250d8`, explicit verifier-engineering track override.
Scope status **changed**: this investigates missing native timeout coverage
rather than a compressed-payload comparison. Native child cleanup is a bounded
verification obligation; a leader-only check cannot establish it.

Base: canonical main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.

| Input at base | Git blob | SHA256 |
|---|---|---|
| `scripts/research_package.py` | `6733ec2f5700e6602d60dc95938c1ea1854980f0` | `b077068519d85bc04a7192d8bcd2fdbc1ce487ea2b7264ed7f437c439b0a16de` |
| `tests/test_research_process_tree.py` | `7073039625ccd0c6582ad066f475c70d05358980` | `5caef4430724a6895923bd0c0e3a58b381af9e7df9c2df943402a0f569f50638` |

Paul Romeo's merged #1484 supplies the Linux test and explicitly leaves a
Windows observer open. Open #2377, head
`5d444eee7dedd997c6094776fbb32ed19831e241`, handles already-exited leaders on
POSIX; it explicitly does not solve that Windows boundary. This test targets
ordinary descendants while the timed-out leader still exists. It is neither
a duplicate POSIX fix nor a Windows containment implementation.

The entry overlap snapshot covered 647 open PRs and 1,177 discussion records,
with complete reported pagination and no fetch warnings. Its PR snapshot was
2026-10-15T10:46:05Z and discussion snapshot 10:48:58Z. Arbitrary code diffs and
all closed PRs are outside the helper's coverage. The claim is in the existing
canonical discussion; no new reservation issue was created.

## Verification

On native Windows 11 build 26300, CPython 3.12.7 normal and `-O`, and CPython 3.14.5
normal, all three tests pass in each mode, with no skips. Each complete suite
took about five seconds. The three cases are successful joined completion,
real timeout tree termination, and rejection of parent-only termination.

```sh
python3.12 -B tests/test_research_windows_process_tree.py -v
python3.12 -O -B tests/test_research_windows_process_tree.py -v
python3.14 -B tests/test_research_windows_process_tree.py -v
```

On Windows use the corresponding installed interpreter path. Non-Windows
hosts intentionally skip this module; that skip is not native validation.

Readiness is established before the launcher's timeout clock starts. The
observer holds native process handles acquired while all three processes are
live, rather than reopening numeric PIDs after cleanup. It checks `taskkill`'s
return code and elapsed cleanup time as well as the process states, so the
fixture's 60-second fallback self-exit cannot be mistaken for successful cleanup.
Teardown uses only the fixture's retained handles and release marker.

The observer follows Microsoft's [process-handle wait contract](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitforsingleobject)
with `SYNCHRONIZE` access. Native execution needs permission to stop the test's
own processes; a sandbox-denied `taskkill` is an environment failure, not a
passing production cleanup result.

A separate AI agent reviewed the observer, readiness, mutation control and
teardown with no blocking finding. This is not human review. Hosted Windows CI,
detached processes, already-exited leader containment, and the selected
mathematical cold replay were not checked by this contribution.

## Open next questions

Native Windows already-exited-leader cleanup remains open in #2377. Reproduce
its ready-child/early-exit cases and design lifetime ownership that survives
leader exit; a late `taskkill` alone does not supply that contract. This test
does not resolve that separate boundary or guarantee hostile-process containment.

## Credit

Douglas Colkitt and retained contributors authored the launcher. Paul Romeo
authored the Linux fixture and Windows handoff; the tree shape and readiness
strategy are credited to that test. PR1298 and the earlier Windows replay audit
are retained predecessors. Prepared for ywz65 with substantial OpenAI Codex
assistance in implementation, verification and writing. Apache-2.0.

## Maintainer integration scope

The observer now loads the exact original runner from
`tests/historical/windows-taskkill-runner.py` (Git blob
`6733ec2f5700e6602d60dc95938c1ea1854980f0`). It remains a historical baseline
control, not coverage of the current Job Object implementation. Current Windows
cleanup is covered by `tests/test_research_windows_job.py`, contributed in #2469.
