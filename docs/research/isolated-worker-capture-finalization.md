# Capture ownership after isolated worker failures

The isolated-test supervisor killed and reaped an owner after an unexpected
`communicate()` error, but returned with both captured streams open. Its
existing communication-failure fixture closed those streams only during test
teardown. A pre-teardown assertion reproduces the failure on canonical main
`4c0a359d88f22f05189d51f48387750b801a45d4` on macOS.

The supervisor now retains successfully stopped owners until the worker pool
has shut down, then closes their captures. This ordering prevents concurrent
`communicate()` and stream closure. The original worker exception is preserved;
individual close failures are attached as cleanup notes, and closing the other
stream is still attempted. Failed process cleanup remains explicitly reported
and does not trigger a potentially blocking close of its active capture.

CPython's Windows `Popen._communicate` creates `stdout_thread` and
`stderr_thread`. They hold buffered-stream locks while reading, and remain alive
after a communication timeout. Owner exit alone therefore does not justify
closing either stream. The shared `close_captures` helper waits at most two
seconds in total for these readers; a still-live reader produces an explicit
cleanup diagnostic and its stream is left open. The helper also replaces the
existing direct closes after the module-timeout drainage attempt. That path
retains status 124 and captured output even when reader cleanup is incomplete.
This is bounded local finalization, not containment of escaped descendants.

## Scope and source lineage

The direct callers are `run_modules` and the runner CLI. Existing consumers are
the cancellation, completion-order, deadline, exited-pipe, bytecode and platform
lifetime tests; none needs a changed API. Frozen historical runners remain
unchanged. No selected record, mathematical artifact or supplier changes.

This builds on PR5017's completion-order fix at
`baab49ce64e6c170ad74432992a35a9c4a54be92` and the retained cancellation,
POSIX-group-cleanup and Windows Job Object implementation. Douglas Colkitt and
all predecessor notices retain their attribution. PR5047's Unicode command
transport is separate. The [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/1472#discussioncomment-19141160)
records this scope.

PR5046 reports a destructor-time Windows `Popen` ResourceWarning after its older
compatibility group. **This change does not identify or claim to fix that
warning's cause.** The confirmed open-stream failure is a separate local macOS
observation. Native Windows execution of this change remains unrun.

## Focused verification

The retained two-worker tests check capture closure before independent teardown
for `OSError`, `StopIteration` and `SystemExit`, while preserving process-exit,
completion-order and ordinary-output checks. The cancellation fixture also
checks closure before teardown on its supported native platforms.

The six new tests in `test_isolated_test_capture_finalization.py` use actual
`Popen` owners and cover:

- Failure after real communication has started, with original exception identity.
- A close error that must not mask that exception or prevent the other close.
- Process-cleanup denial, which must remain visible without blocking on a reader.
- A successfully reaped owner with a real buffered-pipe reader still blocked.
- That same reader at the timeout fallback, retaining status and output bytes.
- Rejection of an unbounded-close mutation using a four-second independent
  fixture release. Ordinary runs must return before that release.

The retained-reader fixture emulates the CPython reader ownership relation on
macOS using an actual pipe and reader thread. It is not native Windows evidence.
All resource assertions precede the fixture's independent process/pipe cleanup.
The helper's reader field names are bound to CPython's `subprocess` implementation;
other Python implementations require their own compatibility check.

Run from the repository root with Python 3.12, then repeat with `-O`:

```sh
python3.12 -W error -B -m unittest discover -s tests -p 'test_isolated_test_*.py' -v
python3.12 -W error -B -m unittest discover -s tests -p 'test_research_worker_failure_order.py' -v
python3.12 -W error -B -m unittest discover -s tests -p 'test_research_isolated_test_posix_pipes.py' -v
```

Local macOS 27.0 (26A428), CPython 3.12.7: the three commands above pass
normally and with `-O`: 56 tests (23 expected platform skips), eight tests and
ten tests respectively. The newly strengthened pre-teardown assertion fails on
the unchanged base and passes with the repair. No native Windows run, full
historical suite or scientific cold replay is claimed.

For a Git-free replay, export the committed runner and these five test modules:
`test_isolated_test_capture_finalization.py`,
`test_research_worker_failure_order.py`, `test_isolated_test_cancellation.py`
`test_research_isolated_test_posix_pipes.py` and its fixture dependency
`test_isolated_test_exit_cleanup.py`. Direct unittest discovery needs
no Git. Include `scripts/research_package.py` for native Windows owner launches.
A Git archive preserves these committed bytes. The research-package exporter
requires a `research/<slug>/VERIFY.json` and does not apply to this shared-tooling
change; no artificial scientific package is introduced for export.

## Open next questions

- Run the focused controls on native Windows CPython 3.12 and 3.14, including
  actual background-reader startup and the deliberately retained-pipe fixture.
- Independently identify PR5046's warning-producing allocation and fixture before
  connecting it to any cleanup repair.
- If another Python implementation is supported, establish its capture-reader
  ownership contract before claiming bounded finalization there.

Prepared by JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.
