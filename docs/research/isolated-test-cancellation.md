# Cancellation of concurrent isolated test modules

The isolated runner used a ThreadPoolExecutor context around subprocess.run.
When the controlling thread raised KeyboardInterrupt, context cleanup waited
for every submitted module, including queued modules that had not started.
A blocked test could therefore prevent cancellation indefinitely.

The same native Windows fixture was run against current main and the repair.
It starts one real unittest interpreter, an ordinary child solver and a queued
second module, then raises a specific exception in the controlling thread.
The old runner returned only after the fixture's five-second emergency release
(5.172 seconds in the recorded run), and the queued module started. The repair
returned before release (1.875 seconds) with both process handles signalled
and no queued start. These timings describe this witness, not a speed benchmark.
The fixture always releases/reaps its own processes even when a control fails.

The repair registers each launch under the same lock used to stop new launches.
On a controlling exception it attempts to stop every captured active tree,
cancels pending futures, joins worker threads and rethrows the original exception.
Native termination commands and leader waits are bounded. Cleanup failure falls
back to killing the parent and adds a diagnostic to the controlling exception.
Workers periodically check cancellation while collecting output, so a surviving
solver holding a pipe cannot keep the worker pool waiting for EOF. Captured
output is discarded on cancellation; no verification success is reported.
Successful execution retains one interpreter per module, the same discovery command and
environment, concurrent scheduling and input-ordered stdout/stderr bytes.
The private cancelled-worker result is discarded with the controlling exception;
it cannot become a passing module receipt.

## Validation

Native Windows / Python 3.12.14:

```
python3.12 -I -O -B tests/test_isolated_test_cancellation.py -v
python3.12 -I -O -B tests/test_isolated_test_runner.py -v
```

Six focused tests and all four existing behavior tests pass. The new
tests cover KeyboardInterrupt, a different controlling exception, and a
parent-only termination mutant which must be detected because its solver
survives until emergency release. Injected cleanup denial preserves the original
exception with a diagnostic and returns while the surviving fixture processes
remain observable; teardown then releases them. A native-command timeout control
checks the bounded parent fallback. A 200,000-byte stdout fixture with delayed
completion checks byte preservation across repeated communicate timeouts.
The two unmodified-main cancellation fixtures fail as expected. The six focused
tests also pass natively under optimized Python 3.14.5.
Assertions in the tests use unittest methods, so optimized execution retains
their checks. Windows observers hold process handles rather than trusting PID
reuse; Linux observers distinguish zombies from running processes.

Native termination needed a context permitted to invoke Windows taskkill.
The restricted sandbox's taskkill attempt did not terminate the tree; the
fixture caught that failure and cleaned up via its emergency release. This
observation prompted the bounded cleanup and failure-diagnostic controls. Native
runs then passed. Linux support is implemented using an owned process session
and killpg, but Linux execution was not available for this validation.

A follow-up review found that an unexpected `communicate()` exception inside
one worker removed its still-live child from the registry before outer cleanup.
The registry now releases a process only after normal communication completion
or the explicit cancellation return. A real sleeping module/solver fixture
injects `OSError` in the worker, checks that the original exception survives,
and observes termination of both processes before emergency release. All seven
focused tests pass on native Windows Python 3.12.14.

## Scope and previous work

This handles active module leaders and their ordinary child processes when
the controlling thread unwinds with an exception. It is not a hostile-process
sandbox, SIGTERM handler, or guarantee for descendants that deliberately escape
the session/tree. On Windows, descendants already orphaned after their module
leader exits are outside taskkill's live-tree ownership; complete lifetime
containment would need a native ownership primitive. Termination must be
permitted by the host. Verification modules still own propagation of their
proof-relevant solver failures.

PR2377 and ywz65's earlier PR2469 repair the distinct registered research-package
runner; PR2498 repairs the parallel snapshot runner. PR2579 handles premature
zero exits in this isolated runner by requiring a completion receipt. That
pending change is not imported: receipt validation and cancellation are separate
obligations and will require resolving their shared run_one edit when combined.
No mathematical source, selected result, acceptance assertion or CI invalidation
rule changes here.

Canonical start/pivot base is 0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2,
priority revision 4. Picker nonce c77df70cf2fac1b309310ab4bf670f66 selected
incumbent-optimization. The prescribed scalar-to-moment fixture passed
PASS_R439_BSECTION_STARS. Same-frame and dirty-workspace barrier proposals were
discarded because main already proves them. The changed scope follows this
independently reproduced cancellation defect instead of submitting a duplicate
mathematical result. The active replay/overlap work informed the bounded tooling
pivot; it is verification engineering, not a paid-profile improvement.

Final overlap combined the paginated cache (804 open PRs at 16:13:42 UTC and
1239 Discussion records at 15:22:22 UTC on 2026-10-15) with a live REST page of
the newest 100 open PRs, numbers 2504 through 2613. The nearby isolated-runner
match was PR2579's distinct completion receipt. Discussion freshness remains
bounded by quota availability; this is not a novelty certificate.

Credit the retained isolated scheduler and its assertion-environment guard,
the research-package process-tree fixture lineage, and the parallel-runner
cancellation work. Prepared by ywz65 with OpenAI Codex assistance; Apache-2.0.

## Open next questions

Can native Windows ownership cover orphaned module descendants at normal exit
and cancellation? First adapt the already reviewed gated Job Object mechanism
from PR2469 to the isolated runner's captured pipes and thread registry; do not
infer that a late taskkill of an exited leader provides that guarantee.
