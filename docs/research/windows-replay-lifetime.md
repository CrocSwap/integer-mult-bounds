# Native Windows replay lifetime

Prepared for ywz65 with substantial OpenAI Codex assistance. Apache-2.0.

## Result and boundary

On Windows, `run_command` now assigns a gated launcher to a kill-on-close Job
Object before releasing it to start the verification command. Ordinary Windows
`CreateProcess` descendants inherit membership. At success, error, timeout or
interrupted wait, the runner terminates the job, waits until its accounting
reports zero active processes, reaps the launcher and closes its handles. It
preserves a nonzero command exit as an error. If assignment fails, the gate stays
closed and the verification command never starts.

The gate interpreter uses `-I -S`, preventing environment/site startup hooks
from running before job assignment. The requested verifier keeps its original
argument vector and environment, including its own intended startup behavior.

This closes the already-exited command-leader gap: a late `taskkill /T` cannot
reconstruct that leader's former tree. Job membership persists after the leader
exits. Job handles are noninheritable, and breakaway is not enabled. An external
job policy that disallows assignment fails closed. The helper uses CPython's
Windows `Popen._handle`; native validation covers CPython 3.12 and 3.14 below.

The command must still join proof-relevant children and propagate their errors.
Stopping an abandoned solver does not validate its output. This is ordinary
subprocess lifecycle management, not a hostile-code sandbox or a proof of
crash-atomic filesystem output. Job accounting can reach zero shortly before
retained process handles become signaled; the independent observer allows a
bounded one-second completion interval. No changed mathematical certificate,
supplier, exponent or measured speedup is claimed. POSIX behavior is unchanged.

## Sources, task and novelty

- Canonical main: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
  Original implementation: `scripts/research_package.py` at that commit.
- [PR2377](https://github.com/CrocSwap/integer-mult-bounds/pull/2377), yssite,
  head `5d444eee7dedd997c6094776fbb32ed19831e241`, repairs the analogous POSIX
  boundary and explicitly hands off native Windows cleanup after leader exit.
  Its pending implementation is not imported.
- [PR2452](https://github.com/CrocSwap/integer-mult-bounds/pull/2452), ywz65,
  head `5208ab2780550273b1d8933ff584ce7581fb242d`, independently observes the
  baseline Windows timeout with a live leader. This result adds the lifetime
  primitive and tests the previously excluded early-exit boundary.
- Credit Douglas Colkitt and retained contributors for the replay launcher,
  Paul Romeo for the original process-tree fixture, and yssite for PR2377's
  lifetime diagnosis and explicit Windows handoff.
- Card `portable-replay`, scope key `831cc1a3c8f9ff01b197`, selection nonce
  `f10ab1eb080d36fe03979d29f44e0af6`. The scoped override follows the live
  Windows handoff instead of another compressed-artifact comparison.

The implementation follows Microsoft's [Job Objects contract](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects),
[assignment API](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-assignprocesstojobobject),
[termination API](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-terminatejobobject),
and [basic accounting layout](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_accounting_information).
These OS contracts justify inherited ownership; the finite fixture checks the
implementation on the recorded native environment.

## Reproduction and evidence

Native Windows 11, build 10.0.26300, CPython 3.12.7 and 3.14.5; standard library
only. Set `TEMP` and `TMP` to a writable local directory when the host sandbox
does not provide one. Use an environment permitted to terminate its own fixture
processes. From the repository root:

```text
python3.12 -B tests/test_research_windows_job.py -v
python3.12 -O -B tests/test_research_windows_job.py -v
python3.14 -B tests/test_research_windows_job.py -v
python3.12 -B -m unittest discover -s tests -p "test_research_*.py" -v
python3.12 -B scripts/research_baseline.py
git diff --check
```

Eight native tests cover normal leader exit, exit 7, timeout, controlled wait
interruption, fully joined success, a parent-only cleanup mutant at three exit
boundaries, assignment denial before the command can run, and startup-hook
isolation with a flag-removal mutant and verifier-environment positive control. The fixture
retains handles to a ready parent/child/grandchild before permitting exit; PID
reuse cannot count as termination. Cleanup uses only those fixture handles.
The parent-only mutant must fail the independent live-descendant observation.

Full research unittest discovery passed 72 tests with three Linux-only skips
before the focused startup-hook review correction; all eight final native tests
pass, including with Python optimization enabled. Exact original
baseline replay against the new normal/error observer fails as expected for
both exit codes, detecting retained live descendants; fixture teardown reaps
them. Python 3.14 is an additional native portability check, not the registered
package replay environment, which remains Python 3.12.

Full mathematical supplier/cold replays and hosted CI are not established by
these checks. The existing CI planner still selects all registered packages
when the shared runner changes.

## Open next questions

Run the same native fixture on supported CI Windows versions and on hosts with
restrictive enclosing jobs. First retain the assignment-denial control: the
verification command must never run outside ownership. Porting away from the
CPython process-handle attribute would require a separately validated launch
mechanism that preserves the pre-spawn gate. Neither is a prerequisite for a
mathematical supplier claim, and no such claim follows here.

## Maintainer integration scope

The Job Object implementation is composed with current main without reverting
later Git compatibility, source-pin diagnostics, cache isolation, POSIX lifetime
cleanup, or replay-inventory fixes. #2452 remains an explicitly frozen historical
baseline test; the eight current Job Object controls are separate. Native CI
evidence for this composed source is recorded in `docs/research/pr-intake-evidence/windows-and-new-archives-20261016.json`.
