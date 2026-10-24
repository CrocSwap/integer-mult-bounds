# POSIX isolated-module exit with inherited capture pipes

The isolated unittest runner now cleans an exited module's ordinary POSIX
process group before waiting for inherited capture pipes to close. A module
observed to have exited before its deadline keeps its actual exit code and must
still supply the successful-unittest completion receipt. Captured stdout and
stderr are drained from the original `Popen` object, without truncation or
replacement, and output remains in input-module order.

This deliberately changes one existing policy assertion: a successful module
whose ordinary descendants still hold capture pipes previously became timeout
124. It now succeeds after group cleanup and complete capture drainage. This
aligns with #2906's POSIX cleanup after already-closed capture pipes and #4683's
Windows owned-job cleanup. Test modules must still join proof-relevant work and
propagate its failure; the runner does not certify an unjoined solver's result.

## Reproduced failure

Base: canonical main `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision
7. On macOS 27.0 arm64, CPython 3.12.2, a disposable checkout used the exact
base runner and #2906's `MODULE`/`SOLVER` readiness fixture. The same module
spawned an ordinary child and grandchild, then completed successfully:

| Only changed fixture setting | Result after module release |
| --- | --- |
| Descendant stdout/stderr redirected to `DEVNULL` | Success, 0.067 s |
| Descendants inherit stdout/stderr | Unittest prints `OK`; runner rejects at its 3 s deadline, 2.649 s after release |

The second result contains `Module timeout after 3s: test_fixture.py; unittest
completion is not accepted`. With the default unlimited budget, the source
loop waits for the descendants' pipe EOF. The old `finally` cleanup cannot run
until that same EOF lets `communicate` return. The new no-deadline regression
uses a bounded outer watchdog and independently cleans the fixture on failure.

## Repair and scope

Only `scripts/run_isolated_tests.py:run_modules` changes production behavior.
`make verify-tests` invokes this CLI; direct callers use the same function. Historical
runner copies, registered-package replay, bytecode policy, Windows job ownership
and frozen scientific sources are unchanged.

After a capture poll times out, the existing cancellation and elapsed-deadline
branches retain priority. The leader is polled before the deadline clock is
checked, so time spent observing exit cannot admit a late completion. Before
that deadline, an exited POSIX leader triggers the existing
`stop_module`, followed by a bounded two-second capture drain. The original
return-code and completion-receipt checks then run. Group cleanup or drain
failure raises rather than reporting success; no captured-output truncation is
introduced. The two-second drain is cleanup time after an observed timely exit,
not a renewed execution budget for a running module.

The ownership domain is ordinary descendants remaining in the module's process
group. A descendant that detaches into another session and retains a pipe is
outside this contract. An unsuccessful drain is not proof that such a process
was contained. The runner's pre-existing deadline/cancellation handling of
escaped pipes is not expanded here.

## Validation

All tests below run small disposable modules; they do not execute historical
research suites. The new regression reuses #2906's readiness fixture and retains
native process identities before module release: macOS `kqueue` exit watches or
Linux pidfds. It checks child and grandchild termination independently of the
runner, including the deliberately weakened cleanup control.

The ten new cases cover unlimited successful completion with a queued module,
failed unittest status, zero exit without a completion receipt, joined work,
200,000 exact stdout bytes plus 100,000 binary stderr bytes across repeated
capture timeouts, real live-leader timeout, real SIGINT cancellation, omitted
group cleanup, and two deterministic deadline-order controls. Those controls
cover an already-elapsed budget and a scheduling pause inside exit observation
with a valid completion receipt. Moving the clock check before that observation
makes the latter control report success instead of timeout 124. The deadline
controls use a controlled clock; native lifecycle cases use real processes.
The old explicit timeout assertion is renamed and updated to the new policy.

Run from the repository root with Python 3.12:

```sh
python3.12 -B -m unittest discover -s tests -p 'test_isolated_test_*.py' -v
python3.12 -B -m unittest discover -s tests -p test_research_isolated_test_posix_pipes.py -v
python3.12 -O -B -m unittest discover -s tests -p test_research_isolated_test_posix_pipes.py -v
```

On this host, the focused coverage totals 60 tests: 37 passed and 23
platform-specific cases skipped. The final new module passes all ten cases in
normal and optimized modes. The new module
also passes through the actual `run_modules`
entry point with one worker and a 30-second module budget. These results are
local macOS evidence. Native Linux/Windows execution, hosted CI, a full repository
suite and mathematical verification are not claimed. Its final
`test_research_isolated_test_posix_pipes.py` name makes the existing registered
package workflow's `test_research_*.py` onboarding discovery execute these ten
cases, including the Linux pidfd cases on that workflow's Ubuntu host; this is
the selected CI route, not a claim of a completed hosted run.

The actual replay planner selects three existing packages because they declare
the changed runner as an input: `isolated-test-bytecode`,
`isolated-descendant-bytecode`, and `isolated-runner-successor`. The first two
pass their complete registered hooks in 6.313 s and 22.600 s respectively,
including the unchanged current-source differentials and rejection controls:

```sh
python3.12 -B scripts/research_package.py --package research/isolated-test-bytecode
python3.12 -B scripts/research_package.py --package research/isolated-descendant-bytecode
```

The last rejects at
`working source drift: certificates/selected-result.json`, before replay. Its
unchanged manifest pins SHA-256 `bb2eaa58…`, whereas the unchanged base already
contains `6fe0a099…`; it also pins runner `ef5035e6…`, which differs from the
base runner `c2ba0ce2…`. This historical admission obligation predates this
repair. Neither the frozen manifest nor acceptance lists are updated, and no
successful replay of that historical package is claimed.

## Sources, overlap and credit

The scoped offline search covered 299 open PRs at 2026-10-22 19:38 UTC, 3,695
Discussion records at 19:39 UTC, and all 6,319 in-scope local notes at the base.
It included `portable-replay`, `run_isolated_tests.py`, `inherited capture`,
`pipe EOF` and `POSIX`; offline staleness warnings remain. This is search
coverage, not a novelty proof. Both related predecessor PRs were live-checked
as merged at their original heads: #2906
`52b7b3f6cd3f12e34c2451c291a85fe9d1eff996` and #4683
`02d43658b948db1922a23369b1fa2ba9bc4f8f58`.

| Exact base source | SHA-256 |
| --- | --- |
| `scripts/run_isolated_tests.py` | `c2ba0ce2b58e3870f6963d4f0ef7f5053ad59d9257efe0eff94e8ef0e00f4313` |
| `tests/test_isolated_test_deadlines.py` | `c8c9175b119c6edb3a6b87ab2ee5270b5ab6f111998f6e73196695c72111c38f` |
| `tests/test_isolated_test_exit_cleanup.py` | `267c8d94c1b5f07520e3254100599225f73943c6205bcb901fc1c6975658872d` |

Canonical investigation:
<https://github.com/CrocSwap/integer-mult-bounds/discussions/1472#discussioncomment-19131480>.
Credit Nick Petalas (#2906), Mihir Srivastava (#4683), ywz65's cancellation and
completion work, Paul Romeo's process-observation fixtures, Aaron Wang/navinor,
Douglas Colkitt and retained contributors. Prepared by JoyboyBrian with
substantial OpenAI Codex assistance. Apache-2.0; no independent human review.

## Open next questions

- Corroborate these new capture-pipe cases on Linux with the retained pidfd
  observer. This host exercises the separate macOS observer.
- A stronger contract for deliberately detached descendants would require its
  own ownership design and failure policy; it is not inferred from group cleanup.
