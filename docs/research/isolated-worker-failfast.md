# Prompt isolated-worker failure propagation

On canonical `bee95ce88f9f19802f0613f92838895cd0e14a1f` (priority revision 7),
`run_isolated_tests.run_modules` observes `ThreadPoolExecutor.map` in input
order. An unexpected later worker exception stays hidden behind an earlier
unfinished module. Without a module deadline or external release, the controller
may never enter its existing process-group cleanup.

This repair changes observation order, while preserving the requested order and
exact bytes of ordinary result rows. It does not change a verifier, frozen
source, completion receipt or selected result. The earlier SIGTERM ownership
repair (#4975) and exited-leader/capture-pipe repair (#4779) remain distinct.

## Failure and repair

The first regression commit, `e112d761f`, adds two readiness-controlled cases.
Two real isolated modules each start an ordinary solver in their own process
group. After all four processes have live native exit observations, the later
worker raises a specific `OSError`: once from `communicate`, once from owned
group cleanup. The earlier module remains blocked until cancellation or a
three-second safety release.

On the unchanged runner, both cases wait for that release and fail. The initial
five-method regression ran in 10.297 seconds: two failures, three passes. Its
independent teardown prevents a failed control from leaving work behind. A
separate two-worker development fixture likewise changed from 4.033 seconds
with forced release to 0.198 seconds without release. These are local
observations, not portable latency guarantees.

The runner submits the same work to its existing executor and observes
`as_completed` futures inside the protected cancellation wait. Calling
`Future.result()` there immediately exposes an unexpected worker exception to
the existing controlling `except BaseException` path. Successful completion
still returns `[future.result() for future in futures]` in the original input
order. A nonzero unittest result remains an ordinary result row; other modules
continue as before.

`next(pending, None)` distinguishes exhaustion of the completion iterator from a
worker raising `StopIteration`. The latter, `SystemExit` and ordinary errors
retain their original exception objects. The inner `finally` disables
asynchronous SIGTERM raises before exceptional cleanup, as in #4975.

The existing registration lock, active-process set, queued-future cancellation,
worker join and temporary-directory cleanup remain in place. A worker already
launched when cancellation takes that lock is included in the owned snapshot;
a later launcher sees `stopping`. No claim is made that queued work cannot start
between the worker's failure and the controller observing it. This is process
ownership, not containment of a deliberately detached process session.

The retained controlling-exception fixture now injects through `submit` after
**two** futures have been submitted. With one worker, this keeps a real active
tree and a genuinely queued future in the test; merely failing the first
submission would make the queue assertion vacuous.

## Verification

Author environment: CPython 3.12.7, macOS 27.0 arm64. The final eight-method
regression runs normally and with an optimized outer interpreter, with warnings
as errors. It checks later pipe/cleanup failures, worker `StopIteration` and
`SystemExit`, the original exception identity, owned process exit before
teardown, an ordered-wait mutant, reversed completion with exact NUL-containing
stdout, and ordinary nonzero-result continuation. It also reuses the retained
KeyboardInterrupt/RuntimeError fixture with native exit handles, checking its
active tree and queued future on this machine. Native observations use kqueue
on macOS and pidfds on Linux; one event batch is not assumed to contain every
exit. Teardown does not re-signal a process-group ID after all retained member
handles have reported exit.

| Unittest pattern | Normal | Optimized |
| --- | --- | --- |
| `test_research_worker_failure_order.py` | 8 pass, 5.188 s | 8 pass, 5.344 s |
| `test_isolated_test_*.py` | 50 cases, 23 platform skips, 10.160 s | Same, 10.195 s |
| `test_research_posix_sigterm.py` | 11 pass, 12.251 s | 11 pass, 17.462 s |
| `test_research_isolated_test_posix_pipes.py` | 10 pass, 7.550 s | 10 pass, 7.598 s |

Reproduce each row using its pattern; repeat with `-O` before `-W`:

```sh
python3.12 -W error -B -m unittest discover -s tests -p 'test_research_worker_failure_order.py' -v
python3.12 -W error -B -m unittest discover -s tests -p 'test_isolated_test_*.py' -v
python3.12 -W error -B -m unittest discover -s tests -p 'test_research_posix_sigterm.py' -v
python3.12 -W error -B -m unittest discover -s tests -p 'test_research_isolated_test_posix_pipes.py' -v
```

The explicit CI plan selects three existing opt-in packages. The metadata checks
for `isolated-test-bytecode` and `isolated-descendant-bytecode` pass. Both
unchanged registered compatibility hooks also pass, including their source/cache
and mutation controls (6.552 and 25.087 seconds). No new helper import is
introduced into the standalone runner.

```sh
python3.12 -B scripts/research_package.py --package research/isolated-test-bytecode
python3.12 -B scripts/research_package.py --package research/isolated-descendant-bytecode
```

Two pre-existing source guards remain outside this repair:

- `test_isolated_historical_completion.py` has the same sixteen failing
  subtest keys on the patched checkout and an export of sixteen exact canonical
  source/config/test paths. Both fail at
  `Unrecognized live source update: scripts/partial_swap/shared.py` before the
  historical child runs. The exact-base seven-method run took 5.527 seconds;
  the broader patched `test_isolated*.py` run reports those same sixteen
  failures. Neither the live source nor its accepted hashes was changed.
- The selected `isolated-runner-successor` package rejects metadata with
  `working source drift: certificates/selected-result.json`. Its checker, first
  rejected input and metadata are byte-identical to the canonical base. The
  exact-base checker and current checker reproduce the same first rejection;
  its historical scientific commands were not run.

The baseline runner blob is `5295a8467b2b3d384178516a4091c09fe2cb2dfd`, SHA-256
`b3717c86e7e09184d1fe4bdb227d5d28a793fbaf60cfd138a9e33c161240d176`.
Complete archive CI, native Windows execution and mathematical acceptance are
not implied by these checks.

## Open next questions

The new pidfd cases need actual Linux execution; the existing hosted onboarding
pattern includes this new `test_research_*.py` file. Windows retains the same
executor observation logic and ownership supervisor, but native execution of
this change remains unrun locally. Historical source-guard reconciliation is a
separate maintainer decision requiring the source review that the guard demands;
weakening or repinning it is not part of a cancellation fix.

[Canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/1472#discussioncomment-19139343).
Credit Nick Petalas, Paul Romeo, yssite, ywz65, Mihir Srivastava, Douglas Colkitt
and the retained isolation, cancellation and source contributors, including
JoyboyBrian's #4779/#4975. Prepared by JoyboyBrian with substantial OpenAI Codex
assistance. Root agent review is not independent human or formal verification.
Apache-2.0.
