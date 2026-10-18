# Require unittest completion before reporting an isolated module passed

ywz65, with OpenAI Codex assistance. 2026-10-15. Apache-2.0.

`scripts/run_isolated_tests.py` now requires both a successful child exit and a
completion token written after unittest returns a successful result. A process
that exits with status zero during discovery or execution no longer earns the
parent's `PASS all ... test modules` summary.

## Reproduced missing coverage

At canonical main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, copy the real runner
into a small checkout with one ordinary passing test module and this second one:

```python
def load_tests(loader, tests, pattern):
    raise SystemExit(0)
```

The original runner exits zero and prints `PASS all 2 test modules in isolated
interpreters`, although only the first module finishes a unittest run. The
repaired runner exits nonzero, identifies the incomplete child and lists the
second module as failed. Ordinary import-time `SystemExit(0)` was already caught
by unittest's loader; the witness specifically uses its `load_tests` hook.
An `os._exit(0)` during test execution is a second abrupt-exit control.

## Implementation and retained behavior

Each child still gets a fresh interpreter and the same unittest discovery
arguments. Its bootstrap captures the private completion-file path, restores
the normal discovery `sys.argv`, and calls `unittest.main(..., exit=False)`.
Only a returned successful result writes the token. Fresh, distinct temporary
paths prevent another ordinary child or an earlier run from supplying it.
The parent combines this token with the process exit code before reporting
success. Temporary receipts are removed after all workers return.

Completed zero-test suites and all-skipped suites keep their existing behavior;
this change checks completion, not a new minimum test count. Normal failures,
per-module import isolation, concurrency, ordered captured output and assertion
checks under optimized parents are retained. This is a premature-termination
guard, not a sandbox against hostile test code deliberately forging the token.

## Evidence and source credit

```sh
python3 -I -O -B -m unittest discover -s tests -p test_isolated_test_runner.py -v
```

All eight end-to-end tests passed on Windows with Python 3.12.14 and 3.14.5,
using writable workspace `TEMP`/`TMP`. They cover both premature exits, the exact
child discovery arguments, completed empty/skipped suites, ordinary failure
reporting, scheduling concurrency and preserved assertions. The original
false-pass witness was also rerun directly against the repaired script.
No full selected-frontier replay or runtime improvement is claimed.

The original isolated runner and
[PR #921's concurrent scheduler](https://github.com/CrocSwap/integer-mult-bounds/pull/921)
remain the foundation. The inherited assertion protection was added by
`woklerx` in `2b7dc6cf`; this patch addresses a different completion condition.
No frozen scientific input, selected result or mathematical claim changes.

Task picker nonce `e66045b995aeca544f688ebefbad2e68` selected verifier engineering
at priority revision 4. Its prescribed baseline binding check passed. The scope
changed from `portable-replay` artifact comparison to the concrete execution
coverage failure above; this distinction is recorded rather than claiming a
compression or interpreter mismatch. Entry overlap covered 768 open PRs and
1,231 Discussion records with complete pagination, plus local notes. It did not
search every code diff or unpublished investigation.

## Open next questions

A separate runner that treats process exit as evidence of verifier completion
needs its own source-bound premature-exit witness before adopting this protocol.
This patch does not establish a cross-repository process-attestation scheme or
require receipt files for unrelated command-line programs.

## Maintainer integration

Integration retains the newer process-group cancellation and authenticated
`skip-clones-tests` overlay. The private receipt is forwarded to the actual
unittest process inside that overlay; the wrapper checks it and still checks
all copied inputs for mutation before returning success. A wrapper's zero exit
alone is insufficient. Additional tests exercise passing and premature-exit
modules through the real wrapper and unchanged source-authentication gates.
Native process-lifetime tests remain platform-specific; macOS skips are recorded
in the integration receipt, not reported as Linux verification.
