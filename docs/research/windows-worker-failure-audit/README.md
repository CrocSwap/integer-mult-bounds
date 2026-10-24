# Native Windows audit of PR5017 worker failures

PR5017's changed failure-observation loop promptly cleans up ordinary owned
Windows processes in this bounded probe. Its new ordinary-failure regression,
however, fails on Windows because the fixture uses text-mode `print` and the
assertion requires LF-only bytes. The captured output is correctly preserved
as CRLF. This is a test portability defect, not evidence that ordinary failures
cancel other modules.

Audited PR: [JoyboyBrian's #5017](https://github.com/CrocSwap/integer-mult-bounds/pull/5017),
exact head `baab49ce64e6c170ad74432992a35a9c4a54be92`.
Contribution base: canonical main `f259dabc7d70e0db8d6d36bfda888f008bbfecc1`,
priority revision 7. Environment: CPython 3.12.0 x64, Windows 11 build 26300.
No production implementation or predecessor test is changed by this note.

## Evidence

| Check | Observed result |
| --- | --- |
| Unchanged `test_research_worker_failure_order.py` | 1 pass, 1 failure, 6 intentional POSIX-only skips; 3.386 s |
| Native probe, normal and optimized outer Python | Three exception cases and one ordered-wait negative control pass in each mode |
| Existing `test_isolated_test_*.py`, normal outer Python | 42 pass, 8 platform skips; 63.713 s; post-summary destructor warning described below |
| Binary-output fixture repair, normal and optimized outer Python | 2 pass, 6 intentional POSIX-only skips in each mode; 1.800 / 1.809 s |

The independently written [probe](probe.py) starts two actual Windows owners,
two unittest modules, and two ordinary solver children. After both trees are
ready, it opens six native handles while all processes are alive, then injects
one exact `OSError`, `StopIteration`, or `SystemExit` into the later worker's
`communicate` call. The earlier module remains blocked. Each exception reaches
the controller unchanged; all six retained handles report exit before the
probe's independent teardown. No fallback release is needed.

The negative control replaces `as_completed` with input-order iteration. The
same probe then needs its six-second safety release. This demonstrates that the
fixture distinguishes delayed observation; timing values are local evidence,
not a latency promise. Each positive case observes six process identities,
and the control observes six more, for 24 per interpreter mode.

`normal.json` and `optimized.json` contain the final source-authenticated probe
results. `-O` applies to the outer probe, whose checks use explicit exceptions;
the runner retains its existing assertion-preserving child policy. This does
not claim optimized execution of every descendant. The authenticating wrapper
checks every exported source both before and after execution. A changed-source
control is recorded in `REPLAY.json`.

The [compatibility transcript](compatibility-transcript.txt) ends with
`OK (skipped=8)` and exit code zero, followed by a `Popen.__del__` warning that
a subprocess was still running. This warning occurred under `-W error` during
destruction and did not change unittest's exit status. It was not traced to a
particular fixture; no warning-free compatibility claim or general absence of
leaks follows from that run. The native probe's assertions concern its own six
retained process handles and run before its teardown.

## Reproduce the discrepancy and probe

[SOURCES.json](SOURCES.json) binds ten exact files by commit, Git blob and
SHA-256. Three come from the pending PR; the other seven match both that PR
and the canonical base byte-for-byte. This is a minimal import/test closure,
not an execution of every file in the PR or its complete CI plan. Scientific
packages, historical overlays and the selected cold replay are outside it.

From a clone containing the contribution, fetch the exact pending source if
needed, then export into a new directory without changing the checkout:

```powershell
git fetch --no-tags https://github.com/JoyboyBrian/integer-mult-bounds.git baab49ce64e6c170ad74432992a35a9c4a54be92
$note = 'docs/research/windows-worker-failure-audit'
python -B "$note/export_inputs.py" --repo . --output ../worker-audit-export
python -W error -B "$note/probe.py" ../worker-audit-export
python -O -W error -B "$note/probe.py" ../worker-audit-export
Push-Location ../worker-audit-export
python -W error -B -m unittest discover -s tests -p test_research_worker_failure_order.py -v
python -W error -B -m unittest discover -s tests -p 'test_isolated_test_*.py' -v
Pop-Location
```

The unchanged first unittest command is expected to fail on this Windows host:

```text
AssertionError: b'earlier module completed\r\n' != b'earlier module completed\n'
```

The output-order test with explicit NUL-containing binary writes passes.
[fixture-output.patch](fixture-output.patch) changes only the other fixture's
import and write: `sys.stdout.buffer.write(...)` replaces `print(...)`, with
an explicit flush. It leaves the exact-byte assertion and production runner
unchanged. This suggested patch was tested in a disposable copy, then the
original file was restored and authenticated. It is offered for the owner of
PR5017 to incorporate; this contribution does not modify that PR or silently
apply the patch during the native probe. The two `fixture-fix-*.stderr.txt`
files retain the byte-exact repaired-test captures.

`original-transcript.txt` and `compatibility-transcript.txt` are PowerShell
`Tee-Object` console transcripts, not raw child stdout/stderr captures. No
output normalization is used inside the assertions. Raw or canonical file
identities, commands and environment details are recorded in `REPLAY.json`.

## Scope, coordination and attribution

This takes the explicit native Windows gap from
[PR5017's canonical finding](https://github.com/CrocSwap/integer-mult-bounds/discussions/1472#discussioncomment-19139343).
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1472#discussioncomment-19140253)
refines `portable-replay` to this interpreter/platform and exact pending change.
The verifier-engineering override uses the available native Windows host;
chooser nonce `00be257651f70b46816d54d90ddc3508`. Success/stop test: one concrete
portability discrepancy and bounded native cleanup corroboration. No broader
implementation campaign or new mathematical result is claimed.

Entry overlap covered 323 open PR bodies and 4,134 Discussion records with
reported complete pagination. The local follow-up covered all 6,710 tracked
README/TASK/ledger records at the pinned base. The closest work is PR5017's
POSIX failure-order check, #4683's Windows lifetime implementation and #4905's
Python 3.14 replay of its six older controls. None replaces this later-worker
Windows observation. The concurrent
[Unicode command-transport claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1472#discussioncomment-19140347)
changes JSON argument expansion; that launch-size boundary is separate from
this pinned worker-failure audit. Final freshness and coverage are in `REPLAY.json`;
arbitrary diffs, historical versions and unpublished work remain outside the
search, which is not proof of novelty.

Credit JoyboyBrian for #5017's failure-order repair, question and existing
regressions, plus #4779/#4975; Nick Petalas for the original runner and readiness
fixtures; Mihir Srivastava/#4683 for the Windows caller and native-handle
observer; ywz65 for the gated Job Object and retained receipt/cancellation
lineage; Paul Romeo, yssite, Douglas Colkitt and other retained contributors.
The probe reuses credited fixtures and the handle observer. This account also
authored #4683, so it is not independent authorship of that machinery.
Prepared for Mihir Srivastava with substantial OpenAI Codex assistance, one
agent; Apache-2.0. This is author-checked execution evidence and test design,
not independent human review or maintainer acceptance.

## Open next questions

The owner of PR5017 can apply the two-line binary-output fixture repair and
repeat its normal/optimized tests on Windows and POSIX. This audit does not
apply or validate a future revised PR head. The post-summary compatibility
warning needs a fixture-by-fixture reproduction before assigning it to a
runner leak or changing cleanup code. The native later-worker probe can also
be considered for Windows CI after review.

Other Python/Windows versions, early Job Object assignment failure, hostile
process escape, physical/scientific replay and the pending PR's unrelated
historical source-guard failures remain untested here. The selected metadata
orientation passed `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`; it is not a cold
replay. The selected conditional `kappa = 60403/20000000` remains unchanged.
