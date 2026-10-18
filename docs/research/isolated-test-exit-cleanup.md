# Stop isolated test solvers after ordinary module exit

The isolated test runner could finish a successful or failing module while its
ordinary child solvers continued running. A descendant that closes its inherited
stdout/stderr does not prevent `communicate()` from reaching EOF. Previously,
`run_one` then removed the exited leader from the active registry without
stopping its POSIX process group. Cancellation cleanup could no longer find it.

The repair calls the existing `stop_module` helper before releasing registry
ownership on POSIX. This sends group SIGKILL even when the module leader has
already exited. The helper's bounded leader wait and failure handling are
unchanged. Cleanup failure propagates instead of producing a passing receipt.
Windows behavior is unchanged.

## Reproduction and evidence

The regression invokes a copied production CLI with real unittest modules,
one child solver and one grandchild. A ready/release handshake holds all three
processes alive while the observer opens Linux pidfds. Their actual process
group IDs must equal the module leader's PID, ruling out deliberate detachment.
The observer then releases the module and checks its status, literal output and
termination of the retained process descriptors. PID reuse and unreaped zombies
cannot masquerade as running solvers.

All fixtures have bounded emergency lifetimes and independent teardown. A
solver survives up to 30 seconds without intervention; the lifetime assertion
checks before teardown, rather than accepting eventual self-exit.

| Test | Unchanged main | Repair |
| --- | --- | --- |
| Successful module stops child and grandchild | Fails, solvers survive | Passes |
| Failing module stops child and grandchild | Fails, solvers survive | Passes |
| Next queued module observes stopped solvers | Fails | Passes |
| Cleanup denial cannot produce PASS | Fails, cleanup never attempted | Passes |
| Explicitly joined child completion | Passes | Passes |
| Parent-only cleanup mutant is detected | Passes | Passes |

The parent-only mutation returns successfully without stopping descendants.
The observer must reject it. The cleanup-denial mutation raises an explicit
error, and the CLI must exit nonzero without its PASS summary. These controls
show that the test is observing lifetime rather than merely a call to cleanup.

Run from the repository root:

```sh
python3.12 -I -B tests/test_isolated_test_exit_cleanup.py -v
python3.12 -I -O -B tests/test_isolated_test_exit_cleanup.py -v
python3.12 -I -B tests/test_isolated_test_cancellation.py -v
python3.12 -I -B tests/test_isolated_test_runner.py -v
python3.12 -I -B tests/test_isolated_historical_completion.py -v
python3.12 -I -B -m unittest discover -s tests -p 'test_research_*.py'
python3.12 -B scripts/research_baseline.py
```

On Linux x86_64, WSL2 kernel 6.6.87.2, CPython 3.12.15, all six new tests,
seven cancellation tests, nine runner behavior tests, six historical-completion
tests and 144 research-workflow tests pass on refreshed main. The new tests also
pass under optimized CPython 3.13.5. Both unchanged baselines named below fail
four of the six new tests. Optimized and ordinary 3.12 runs retain the unittest
assertions. The selected baseline binding check passes; it is not a supplier
replay.

A complete run of `scripts/run_isolated_tests.py --workers 4` using the local
Python 3.12.15 environment attempted all 162 modules on refreshed main. It
returned failure for these twelve modules:

```text
test_combined_frame_source_pins.py  test_copied_fixed.py
test_copied_fixed_reversed.py      test_pair_assembly.py
test_pr_reconciliation.py         test_selected_ci_inputs.py
test_shared_point_digest.py       test_single_intersection_packing.py
test_skip_clones.py               test_skip_strips.py
test_skip_suffix.py               test_split_skip.py
```

Each of those twelve also fails on a fresh unchanged baseline worktree at
`a98b1ebcdd6f2fe25ffdd30cd7e753ebfe319797`. Eleven complete exception-message
lists agree exactly. The skip-clones wrapper has the same source-pin failure
but a run-specific private completion-receipt path/index in its command-error
message. The failures include historical source-pin drift, reconciliation
metadata disagreement and selected workflow-trigger expectations. In particular,
the batch932 accepted-successor check already rejects the baseline runner's
hash. This contribution does not rewrite historical acceptance pins or claim a
green complete suite. The other 150 module processes exited zero. The earlier
160-module run at the original base had the same twelve failing modules, also
reproduced on that unchanged base. These runs did not change tracked artifacts.

The cancellation suite's parent-only fault control emits two unclosed-pipe
ResourceWarnings on both baseline and repair. That pre-existing cancellation
resource issue is not a normal-exit regression. The new test file passes the
configured Ruff check. Both touched Python files pass an isolated correctness
check with `--select E4,E7,E9,F,B,PLE`. An all-rules inspection is not a clean lint
gate for the inherited untyped runner; its existing import-order,
explicit-`check` and broad cleanup-exception diagnostics remain unchanged.

## Task boundary, sources and overlap

Initial base: `b2024b853ae33de489756de8e4dde011dabebeaa`.
Publication base and canonical-main checkpoint at 09:39 UTC on 2026-10-16:
`a98b1ebcdd6f2fe25ffdd30cd7e753ebfe319797`, priority revision 5. Upstream
incorporated PR2579 during this session. The original checkpoint was preserved,
the same seven-line repair applied cleanly to refreshed main, and all affected
completion, cancellation and historical-overlay checks were rerun. Guidance,
priority revision and selected record were unchanged.
Chooser nonce `74864336139e29f33377ef5a4d21bd84` selected verifier engineering.
This changes the `portable-replay` card's proposed canonical-comparison method
to a POSIX verification-process lifetime repair. The initial comparison defect
was already covered by PR2040, so it was not repeated. Preventing completed
checks from leaking solvers protects verification resources, not the supplier's
paid profile or multiplication exponent.

Exact publication-base source hashes:

- `scripts/run_isolated_tests.py`:
  `6f353dae3f922d78f62bedddcb50cfe2b500b4195a888cec5ffac2367b1a4f88`.
- `tests/test_isolated_test_cancellation.py`:
  `014db7e16518254eb566c2ad2fa98d2f5dd4aea7525707530bc34e97ba9ed0d3`.

The original baseline runner hash was
`331743571ea29a63a0e819d421e8adc6f04831f11333aa1f7f1292933ccc82d4`.

The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1472#discussioncomment-18968635)
records the object, method and two-hour expiry. The entry overlap snapshot
covered 489 open PRs, 2,110 closed PRs and 1,575 Discussion records, with reported
complete pagination at 09:24 through 09:25 UTC on 2026-10-16. The pre-submission
refresh covered 487 open PRs, 2,112 closed PRs and 1,577 Discussion records at
09:38 through 09:39 UTC, with complete reported pagination and no warnings.
Searches do not prove novelty. Relevant predecessors are:

- Aaron Wang/navinor's isolated concurrent scheduler.
- woklerx's PR1852 assertion-environment hardening, head
  `2b7dc6cf68f650dd2cd8898924d31a02f1a6e9c7`.
- ywz65's PR2625 cancellation/registration repair, head
  `2158a3675e11d59d7a8706e8cb0f16acd875df64`.
- ywz65's PR2579 unittest-completion receipts, inspected head
  `808942baa87f048b5d8a7cca47a04d8ca4fbe038`, incorporated during the refresh.
  Its current-main integration retains cancellation and the historical overlay.
  That checks whether unittest completed; this repair checks ordinary descendant
  lifetime after module exit. Its completion-token checks remain intact.
- PR2377 and PR2469 cover the separate registered-package runner. Their
  implementations are not imported here.

This is a verifier repair, not mathematical verification. Test modules must
still wait for proof-relevant children and propagate their failures. Killing
unfinished work does not establish that it passed. POSIX SIGKILL is requested
before returning the module result or scheduling another module on that worker;
the operating system determines actual signal-completion latency. Detached
sessions/groups, denied termination, native Windows exited-leader containment,
macOS execution, hosted CI and the complete selected cold replay are not
established. No selected record, source archive or mathematical input changes.

The new tests use bounded readiness loops, at most three pidfds and four
processes per fixture, with unconditional teardown. The existing runner still
has no per-module runtime/output-size cap and retains its 101-line coordinating
function. Adding limits or refactoring its shared synchronization would change
the broader execution contract and is deferred. The repair adds no new loop,
cache, dependency or recursive call.

## Open next questions

Can Windows module descendants receive lifetime ownership through a gated Job
Object? First adapt the reviewed registered-runner mechanism to the isolated
runner's captured streams and registry, then observe success, failure and
cancellation with native process handles. Native Windows execution and a
caller-specific ownership design are required. A late `taskkill` against an
exited leader is not evidence of containment.

Separately, can cancellation close discarded capture pipes without changing
its exception/cleanup ordering? Start with the existing parent-only fault
control and require warning-free teardown while retaining the survivor
observation. This normal-exit repair does not resolve that pre-existing issue.
