# A post-reap numeric group signal can address a new group

The affected owner is `run_guarded_v3.py` in PR #6864 at `c8f7bd582ffc1301b851dde2364c60f1636aac8b`. Its exact source is retained as `run_guarded_v3.py.txt`. Lines 354–374 launch the direct child with `start_new_session=True`, monitor it with `Popen.poll()`, enter `process.wait()`, and then unconditionally call `killpg(process.pid, SIGKILL)` from `finally` before another wait.

Let q be that child's PID, session ID and initial group ID. The required invariant is that every numeric group signal performed by this owner addresses its original owned group, or establishes that group is absent. The following execution is compatible with an ordinary completed original case or the original optimized refusal; no scientific API or body is added.

1. The waiting entry and inner scientific path finish their local work and the direct GNU-time child exits. Its group has no remaining live members.
2. The runner consumes the child's wait. Its monitoring poll can do this earlier; the explicit wait before `finally` independently supplies a consuming boundary.
3. Once all task associations for the old PID object are detached, Linux removes q from namespace lookup. A held pidfd may keep the old object alive without preserving the numeric lookup reservation.
4. The runner is descheduled. An unrelated process with signal-permitting credentials is allocated q and successfully establishes its own session/group. Cyclic allocation permits number reuse; the selected source profile supplies no host-wide exclusion over all PID allocation.
5. The runner resumes and calls numeric `killpg(q, SIGKILL)`. Numeric lookup resolves the new group, so the signal can kill an unrelated process. The original cgroup guardian cannot undo this external signal.

The trace is existential, not a claim that every run recycles the number or that a particular workload did so. Even a rare permitted trace refutes the universal signalling-ownership invariant. No live reproduction, PID-reuse stress test or observed incident is claimed.

## Primary-source implications

In Linux v6.12, `kernel/pid.c:133–163` removes each numeric ID with `idr_remove` before deferred reference release; `346–367` reaches that removal after the last task association disappears. Allocation at `215–242` uses cyclic namespace allocation. `kernel/signal.c:1603–1617` resolves negative numeric group signalling with `find_vpid`. These source facts support steps 3–5. Exact raw-source hashes and URLs are in `SOURCES.json`.

The `WNOWAIT` path in `kernel/exit.c:1143–1169` reports the zombie's terminal information without the consuming state transition. This supports the proposed repair invariant, provided the actual parent retains exclusive wait ownership and auto-reaping is excluded by the selected launch chain. It does not by itself qualify the proposed Python implementation or prove every error path.

Official CPython v3.12.3 `Lib/subprocess.py:1973–2005` confirms that polling uses consuming `waitpid(..., WNOHANG)`. This is corroborating CPython 3.12 source, not a newly asserted current-host or exact selected patch-release association. The explicit wait-before-final-signal trace does not require selecting that patch release.

## What stays conditional

Keep the current native entry's `start_new_session=False`: changing it blindly would move scientific work out of the common runner's sampled and signalled group. The inspected cold-build control compares the child's inherited group with the actual parent's captured group, not with a fixed numeric group. Its failure protocol still requires outer termination and join. That narrow relational result does not establish a complete theorem over every helper/context body, group-changing path or instantaneous resource peak.

The current selected source therefore remains unsuitable for the required numeric signalling invariant. The finding is complete within this negative scope. Whole caller/source qualification and actual execution remain unestablished.
