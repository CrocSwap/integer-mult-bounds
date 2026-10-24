# Windows Python 3.14 lifetime-control replay

The six existing native Windows lifetime controls from
[PR #4683](https://github.com/CrocSwap/integer-mult-bounds/pull/4683) pass on
**CPython 3.14.9 x64, Windows 11 build 26300**, both normally and with the outer
unittest interpreter optimized. This supplies the specific Python 3.14 execution
evidence requested in that PR's **Open next questions** and
[Discussion #1472](https://github.com/CrocSwap/integer-mult-bounds/discussions/1472#discussioncomment-19126709).
The implementation and tests are unchanged. This is additional environment
coverage of existing controls, not independent test design or human review.

## Result and exact scope

Canonical main at execution:
`624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.
The runs were serial on 2026-10-22, from 23:24:13 to 23:24:48 UTC.

| Invocation | Outcome | Unittest duration | Whole invocation |
|---|---|---:|---:|
| Normal outer interpreter, `-B -W error` | 6 passed, no skips | 17.350 s | 17.821106 s |
| Optimized outer interpreter, `-O -B -W error` | 6 passed, no skips | 16.817 s | 17.370000 s |

These are execution durations, not a speedup comparison. Each invocation had
a 120-second external timeout; the existing fixtures retain their own shorter
readiness, execution and cleanup bounds.

The six controls cover:

1. A failed unittest's child and grandchild stop, with failure/output preserved.
2. Inherited capture pipes do not turn successful completion into a timeout.
3. Joined work retains successful completion and literal output.
4. A successful unittest's child and grandchild stop.
5. A real module timeout remains a failure and stops the owned tree.
6. Removing the Windows supervisor is detected for both successful and failed
   modules: the same retained-handle assertion observes surviving solvers.

The observer opens native process handles while all three fixture processes
are alive at a readiness barrier. It checks those identities before teardown
releases or independently stops the fixtures. This avoids mistaking a reused
PID or eventual emergency self-exit for successful cleanup.

`-O` and `-W error` apply to the outer unittest interpreter. They are **not**
claims that every descendant executes with those options. The existing test
launches its CLI without `-O`, and the production runner removes inherited
`PYTHONOPTIMIZE` before executing test modules. That assertion-preserving
policy and the isolated supervisor/gate arguments remain unchanged.

## Evidence and reproduction

[REPLAY.json](REPLAY.json) records exact commands, platform/build, GIL status,
runtime package/executable/DLL SHA-256 hashes, four consumed repository source
SHA-256 and Git blob identities, log hashes, environment handling and times.
All four source files matched committed main before execution and remained
byte-identical after both runs. Raw captures are
[normal stderr](normal.stderr.txt) and [optimized stderr](optimized.stderr.txt);
both stdout captures are empty and retained. The directory's attributes preserve
their exact Windows line endings. Unittest prints its success summary on stderr.

The workspace-local interpreter was the CPython team's
[NuGet `python` 3.14.9 x64 package](https://www.nuget.org/packages/python/3.14.9),
used via its `tools/python.exe`; no system interpreter or PATH was changed.
The [Python Windows documentation](https://docs.python.org/3.14/using/windows.html#the-nuget-org-packages)
describes this distribution for build/CI use. The exact downloaded package
SHA-256 is
`7cd9d07aec975212344dc6f7e45019378cf6775dd564181e269010a1eddaaec7`.

From the repository root, set `py314` to that package's executable and run:

```powershell
$py314 = 'C:\path\to\python.3.14.9\tools\python.exe'
& $py314 -B -W error -m unittest discover -s tests -p test_isolated_test_windows_exit.py -v
& $py314 -O -B -W error -m unittest discover -s tests -p test_isolated_test_windows_exit.py -v
```

The recorded launches removed `PYTHONOPTIMIZE`, `PYTHONPATH`, `PYTHONHOME`,
`PYTHONPYCACHEPREFIX` and `PYTHONWARNINGS` from each child environment and set
`PYTHONDONTWRITEBYTECODE=1`. The remaining environment was inherited; the
receipt does not claim a hermetic machine image. Use a fresh source checkout
with the recorded hashes. Runtime and timing strings need not match on another
machine; all six tests must execute and pass, including the mutant rejection.

This replays current main, rather than claiming the complete old PR tree is
identical. #4683's head was
`02d43658b948db1922a23369b1fa2ba9bc4f8f58`. Its full
`scripts/research_package.py` blob differs from current main; a separate
`ast.dump(..., include_attributes=False)` comparison found its
`run_windows_command` definition and `_WINDOWS_GATE` assignment identical to
the tested main versions. This comparison is limited to those two nodes and
is not a whole-runner review.

## Task, coordination and attribution

The live handoff was selected before retrieving the `portable-replay` card
(nonce `2941c600bffe1f98f2667f09cc9ccd1c`, scope key
`91a9a2afec282c926282`). Scope is **refined** to the named interpreter gap,
within the card's interpreter/version variation. The advance claim is
[here](https://github.com/CrocSwap/integer-mult-bounds/discussions/1472#discussioncomment-19134438).

Entry overlap covered 424 open PR bodies and 3,949 Discussion records, with
complete reported remote pagination. The closest related open work,
[PR #4779](https://github.com/CrocSwap/integer-mult-bounds/pull/4779), changes
the POSIX inherited-pipe boundary; it does not perform this Windows six-control
Python 3.14 replay. #2452's Python 3.14 Windows observer concerns the earlier
registered-runner live-leader timeout case. Neither is a substitute for this
isolated-module exited-leader handoff.

At the final checkpoint, canonical main was unchanged (fetch completed at
2026-10-22T23:28:46Z); the guidance, selected record and four consumed sources
had no upstream delta. Refreshed overlap covered 425 open PRs at 23:30:09Z and
3,957 Discussion records at 23:31:36Z, with complete reported pagination.
The local scan covered 5,570 of 6,319 tracked note paths; 749 remained omitted
after bounding sparse materialization. Relevant scripts, tests and lifecycle
notes were read directly. The two additional local Python 3.14 hits concerned
different scientific replay packages. Arbitrary diffs, omitted notes,
historical versions and unpublished work remain coverage limitations; these
searches do not establish novelty.

The prescribed current selected-baseline orientation stopped at sparse-omitted
`certificates/checkpoints/frontier4359.json`. That metadata check is not part of
these four source files; no selected-baseline pass or mathematical replay is
claimed.

Credit Mihir Srivastava / #4683 for the Windows caller repair and six controls;
Nick Petalas / #2906 for the POSIX exit-cleanup result and ready-tree fixtures;
ywz65 / #2469 for gated Job Object ownership, #2625 for cancellation and #2579
for completion receipts; Paul Romeo / #1484 for the earlier observer/handoff;
Aaron Wang/navinor, woklerx, Douglas Colkitt, Tekalign and retained contributors.
Prepared for Mihir Srivastava (@mihir-s-05) with substantial OpenAI Codex
assistance, one agent. Apache-2.0. The same account authored #4683; this is not
a claim of independent authorship.

## Open next questions and limitations

This closes only the requested six-control execution gap for this one standard,
GIL-enabled CPython 3.14.9 x64 distribution and Windows build. Other 3.14 patch
versions, free-threaded Python, ARM64, different Windows policies, all other test
modules and hosted Windows CI were not exercised. No native implementation was
changed, and no new test or broader regression coverage is claimed.

The useful remaining lifetime question is abrupt supervisor death **before**
Job Object assignment. A bounded first step is a fault-injected pause at that
boundary, with a retained handle observing the unassigned gate waiter's exit
and an explicit assertion that workload execution never starts. The gate's
existing 30-second wait limits that experiment, but these six tests do not
observe that early-startup window. External launch mechanisms and hostile
containment also remain outside the ordinary-subprocess contract.

Proof-relevant child work must still be joined and its failure propagated;
cleanup does not validate unfinished work. Historical source-pin failures,
selected cold replay, native/all-size mathematical obligations and the full
multiplication theorem were not audited. The selected conditional
`kappa = 60403/20000000` is unchanged.
