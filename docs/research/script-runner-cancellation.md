# Direct script runner cancellation

`scripts/run_parallel.py::run_all` now stops its active ordinary process trees
when the controlling thread raises, prevents queued launches after cancellation
starts, and preserves the original exception if cleanup also fails. A normal
nonzero script exit still contributes its label to the returned failure list;
it does not cancel the other scripts. Complete output blocks retain their
existing completion order and text-decoding behavior.

## Reproduced problem and repair

At canonical main `b4560d9e7216f72b73c5aa940ac099c05e33ccf9`, the pool context
manager waited for all submitted `subprocess.run` calls on interruption. A
real script and child solver fixture forced release after five seconds: the
old runner returned only after that release (5.266 seconds), and queued work
could start before shutdown finished. The regression rejects that outcome.

Each worker now registers its process under the same lock used to set the
stop flag. Cancellation snapshots this registry, attempts every owned stop,
then cancels queued futures. `communicate` polls every 0.2 seconds so a failed
stop or retained output pipe cannot indefinitely block pool shutdown. Native
cleanup uses a separate POSIX process group or Windows `taskkill /F /T`, with
a five-second utility timeout and a two-second parent wait. Cleanup failures
become notes on the original exception; they are not reported as successful
process termination. Bounds are per process, not a constant for the whole pool.

Review found a second edge: an unexpected `communicate` error must leave the
failed worker's process registered. An unconditional `finally` removal leaked
the live script and solver in an actual regression. A completion flag now
removes only completed workers or workers whose cancellation snapshot has
already been taken. Command-iterator and launch errors also enter the same
cleanup path.

The process-ownership and bounded-stop pattern, plus the native lifetime
observer and initial cancellation fixtures, are adapted from
[PR2625](https://github.com/CrocSwap/integer-mult-bounds/pull/2625) at
`4219e25b095e7edb59076c777c5a4a17e066bc89`. That contribution targets the separate
unittest-module scheduler. This patch integrates the pattern into the direct
script API, adds its command-production/launch/output-failure controls, and
retains independent submission from current main. It does not claim a new
process-termination algorithm. The output-error finding was also handed back
to PR2625 for correction there without another contribution count.

## Validation and limits

```sh
python3 -I -O -B -m unittest discover -s tests -p test_script_cancellation.py -v
python3 -I -B -m unittest discover -s tests -p test_parallel_verification.py -k worker_failure -v
python3 -I -B -m unittest discover -s tests -p test_parallel_verification.py -k invalid_environment -v
```

Nine focused tests pass on native Windows with CPython 3.12.14 and 3.14.5.
They cover interruption, another controlling exception, command-iterator
failure, worker launch failure, output-read failure with a live child,
parent-only cleanup as a rejected mutant, denied cleanup, bounded native
utility timeout, and intact 200,000-character output plus failure labels.
Actual process handles verify script and solver termination. The two existing
direct-runner regressions also pass. POSIX code is reviewed but not executed
in this Windows validation; hosted CI is not claimed.

The full neighboring snapshot-test module was attempted but its three
make-dependent cases failed because `make` was unavailable, followed by the
known unmodified snapshot cleanup error. Those are not reported as passing
or fixed here. Sandbox process restrictions also denied the first native
tree-stop checks; the reported native successes use the ordinary user process
context and kill only fixture-owned processes.

Windows tree termination requires a still-active parent PID. Descendants
already orphaned before cancellation, deliberately escaped POSIX groups,
external services, and repeated interruption during cleanup remain outside
this ownership contract. A cleanup failure can leave processes alive and is
reported explicitly. The fixture that replaces `communicate` before its
normal reader setup owns the resulting pipe and closes it after checking
termination. This is not a proof that arbitrary external I/O libraries can
always be cancelled or that every pipe failure is recoverable.

## Assignment and overlap

The original picker nonce was `057cad22699fa91fd2f81df9ec3d5073`, priority 5,
adversarial audit. `research_baseline.py` passed its binding-only first step.
Scope changed after checking that the examined selected stock and compiler
questions were already covered. The reproduced long-running runner failure
affects the reliability of research verification itself; no mathematical
result, supplier admission, or selected exponent changes.

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/pull/2625#issuecomment-6197406515).
The overlap cache covered 833 open PRs at 2026-10-15 16:47:56 UTC and 1,239
Discussion/comment/reply records at 15:22:22 UTC, with complete pagination at
those timestamps. Discussion freshness is bounded because the broad refresh
hit the API quota. Final targeted PR checks supplement this snapshot; no
metadata search establishes absolute novelty. PR2495 concerns assertion
environments, PR2498 the snapshot runner, and PR2625 the unittest runner.
None repairs this direct-script entry point at the checked heads.

The final refresh advanced main to
`1884c509efc004524786e9b7cfcc4aca572316d5`, incorporating the efficient1100
research review. Its guidance, selected record and runner inputs are unchanged.
This branch was fast-forwarded to that submission base; the reproduced
predecessor boundary remains pinned above.

## Open next questions

Run these native lifetime controls on Linux before claiming tested POSIX
behavior. A stronger Windows orphan guarantee would require a separate job
object ownership design; it is not inferred from `taskkill`. The scoped
decision is to complete this repair and stop, with no dependent mechanism
expansion or scientific cost claim.

Prepared for ywz65 with substantial OpenAI Codex assistance, including a
separate agent review. No independent human review is claimed. Apache-2.0;
the original script retains eumemic's PR154 attribution.
