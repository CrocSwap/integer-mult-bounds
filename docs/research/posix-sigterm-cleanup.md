# SIGTERM and owned verification processes

On canonical `b91956876e5b4122fd89179f1b57557ff8378f15` (priority revision 7),
SIGTERM sent to a POSIX verification owner exits that process without executing
Python `finally` blocks. Its module and ordinary solver can remain running in
the separate process group the owner created. Timeout and KeyboardInterrupt
cleanup do not cover this path.

A real readiness-controlled `research_package.run_command` reproduction on
macOS 27 arm64 / CPython 3.12.2 observes both processes through kqueue before
sending the signal. The owner exits `-15`; neither observed process has exited
after the owner is gone. Independent fixture teardown then kills the leaked
group. The new regression's initial eight-method version fails with six failure
reports on the unchanged runners, covering both owners, their launch windows
and repeated cancellation. Custom/ignored handlers, normal completion and
worker-thread calls already pass on that baseline.

This is a cancellation repair, separate from #4779's completed-leader/captured
pipe repair, #2906's closed-pipe ownership cleanup and #4683's Windows Job Object
ownership. It changes no scientific result or source pin.

## Behavior and callers

The two self-contained runners temporarily handle **default SIGTERM on the
main thread** while their public operation owns work:

- `research_package.run_command`, used by `run_python_replay`, the registered
  `run_package` commands and its optional dependency-install command;
- `run_isolated_tests.run_modules`, used by its CLI and imported callers.

A handled termination normally raises `SystemExit(143)` after the existing
owned-group cleanup. An observing parent therefore receives positive status
143 instead of the baseline's signal return code `-15`; shells conventionally
report both as 143. No verification PASS is produced. The previous signal
handler is restored on normal return, cancellation and other exceptions.

An existing custom handler or `SIG_IGN` is left untouched. Calls from a worker
thread do not install a process-wide signal handler; the application retains
responsibility for its signal policy. Windows retains its existing ownership
implementation. SIGKILL and deliberately detached process sessions remain
outside this cooperative termination contract.

If another exception has already entered cleanup, the first SIGTERM is deferred
and that original exception remains the reported failure. This avoids replacing
the cause of failure or interrupting the remaining process groups. A first
SIGTERM during otherwise successful completion cleanup instead yields 143 after
cleanup. Repeated SIGTERM does not interrupt cleanup.

## Launch and failure boundaries

The handlers record a pending request at every stage, but raise asynchronously
only inside a wait protected by an inner `finally`. That `finally` disables
asynchronous raises before the outer failure/cleanup path begins.

For registered commands, `Popen` may have spawned its child before returning
the handle to the caller. A signal in that interval only records the request;
the handle is assigned inside the outer cleanup region before cancellation is
raised. The actual `process.wait` remains the interruptible wait.

For isolated tests, `Popen` runs only in executor workers. The existing lock
covers launch through registration in `active`. A main-thread cancellation
must acquire that same lock before taking the cleanup snapshot, so a launch
already in progress is registered before cancellation proceeds. Results still
use the original `pool.map` order; explicit iteration gives each `next` its
protected interruptible interval. The original exception cleanup, pending-work
cancellation and worker join remain in place.

The handlers remain local to their runner files. Existing compatibility checks
copy `run_isolated_tests.py` alone into an owned fixture; a new helper import
would break that established standalone boundary.

## Verification

The final regression contains eleven methods and twenty real-process fixtures.
On macOS / CPython 3.12.2, normal and optimized runs pass in 13.742 s and
13.660 s. The optimized invocation also launches the actual owner interpreter
with `-O`; success does not rely on assertions enabled in that owner.

The fixtures cover both owners, Popen returning after a signal, isolated queued
work, repeated SIGTERM, first SIGTERM during ordinary completion cleanup,
handler restoration, custom and ignored handlers, and worker-thread calls.
An exceptional-cleanup fixture keeps two isolated process groups (four observed
processes) active, raises an ordinary worker error, then sends the first SIGTERM
from the first cleanup call. All groups terminate and the original error is
retained. The corresponding registered-command fixture also passes.

Lifetime assertions use native kqueue registrations on macOS and retained pidfds
on Linux. They must observe process exit **before** fixture teardown. A weakened
cleanup that kills only the leader is rejected by this oracle for both owners;
test teardown is not counted as successful production cleanup. Native Linux
execution awaits hosted CI; no Windows execution is claimed for these POSIX
controls.

```sh
python3.12 -B -m unittest discover -s tests -p 'test_research_posix_sigterm.py' -v
python3.12 -O -B -m unittest discover -s tests -p 'test_research_posix_sigterm.py' -v
python3.12 -B -m unittest discover -s tests -p 'test_isolated_test_*.py' -v
python3.12 -B -m unittest discover -s tests -p 'test_research_isolated_test_posix_pipes.py' -v
python3.12 -B -m unittest discover -s tests -p 'test_research_bytecode_isolation.py' -v
python3.12 -B -m unittest discover -s tests -p 'test_research_process_tree.py' -v
python3.12 -B -m unittest discover -s tests -p 'test_research_onboarding.py' -v
python3.12 -B scripts/research_package.py --package research/isolated-test-bytecode
python3.12 -B scripts/research_package.py --package research/isolated-descendant-bytecode
```

The five existing focused unittest invocations pass 71 of 101 cases, with 30
platform skips. The two unchanged registered compatibility hooks also pass
(7.995 s and 24.085 s), retaining their source/cache differentials and mutation
controls. Repeating the isolated, registered-bytecode and onboarding unittest
groups with `-O` passes 61 of 84 cases, with 23 platform skips. No dependency,
historical scientific replay or frozen input is changed.
The existing Ubuntu onboarding pattern `test_research_*.py` includes the new
regression without a workflow change.

The shared `research_package.py` control change makes the actual CI planner
select all **2,851 opted-in packages** at this base. That selection is not local
verification of those packages. Only the two named compatibility hooks were
replayed. The separately inspected `isolated-runner-successor` metadata still
rejects its historical `certificates/selected-result.json` pin before replay;
its package and acceptance pins remain unchanged. Full archive CI and
mathematical acceptance are unclaimed.

The unchanged baseline source SHA-256 values are:

| Source | SHA-256 |
| --- | --- |
| `scripts/research_package.py` | `b63018ac0e30259569f1490219844ce2ae67331c5c8b2213868eb643033990b6` |
| `scripts/run_isolated_tests.py` | `f8b51fe5f3d444ee6fe47b1744eff7e99ba9386aa485befa94700aadcb8dd00d` |

## Open next questions

Native Linux execution should corroborate the new pidfd lifetime controls through
the existing onboarding job. Applications invoking these APIs from worker
threads or installing custom signal handlers retain their own cancellation
policy; extending that contract would require an explicit owner interface.
Detached-session containment and uncatchable-signal guarantees are separate
problems, not claims of this patch.

Coordination: [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/1472#discussioncomment-19138316).
Credit Paul Romeo, yssite, ywz65, Nick Petalas, Mihir Srivastava, Douglas Colkitt
and retained lifecycle/source contributors. Prepared by JoyboyBrian with
substantial OpenAI Codex assistance. Author-process agent review is not
independent human or formal verification. Apache-2.0.
