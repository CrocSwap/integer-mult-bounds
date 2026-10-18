# T37 execution-log coverage

The selected T37 archive contains 34 stage logs. The frozen native-stage
admission predicates read `native/STEPS.json`, check its eight stage names and
compare each exit code with zero. They do not inspect the eight native logs.
This package supplies a supplementary, read-only coverage check for the four
execution indexes and every corresponding log. It changes no selected files.

The exact result is limited to evidence admission. The replay below executes
the original three source statements at `final_binding.py:194-196`, with no
rewrites, against the archived native index. Each of the eight native-log
deletions leaves those predicates passing. The new check rejects all eight.
This is a component-level counterexample to log completeness. The complete
original final binder is not executed by this package, and no counterexample
to the mathematical construction is claimed.

## Reproduce

From the repository root, with Python 3.11 or newer and no third-party packages:

```sh
rtk proxy python3.11 -I -B research/t37-log-coverage-seed86/verify.py
```

Expected output:

```text
PASS_T37_LOG_COVERAGE_CONTROLS 34 logs; 80 rejections; 8 native omissions admitted by frozen slice
```

The verifier checks five immutable source/archive SHA-256 pins, derives the
stage order from the three actual producer programs, copies only the indexes
and logs into a temporary directory, and runs the complete declared controls.
It compares the canonical coverage and ordered control-name digests with
`CERTIFICATE.json`. Canonical JSON uses sorted keys and separators `,` and `:`.
The temporary directory is removed. The committed archive stays unchanged.
The source pins apply to immutable inputs, not to regenerated gzip containers.

Append `--out /new/path/receipt.json` to write the full report, including every
log digest and control name. Its parent must exist. Output is created only
after success, with exclusive creation; existing files are not overwritten.
Both ordinary and optimized Python execute all new checks. The original
native predicates are explicitly compiled with assertions enabled.

The public CLI controls exercise source drift, safe output handling, missing
logs, an escaping symlink, a minimal relocated checkout with spaces, and full
receipt equality between ordinary and optimized workers:

```sh
rtk proxy python3.11 -I -B research/t37-log-coverage-seed86/test_cli.py
```

Expected: `PASS_T37_LOG_CLI_CONTROLS` with receipt SHA-256
`e834d7037dee9071f14b0c0a3194c84c8f036d1160ca512f84d2a578992170c0`.
The test driver uses assertions and rejects optimized execution itself.

For a completed T37 replay directory:

```sh
rtk proxy python3.11 -I -B research/t37-log-coverage-seed86/audit.py --work /path/to/t37/replay
```

For the archived reuse mode, the success line is:

```text
PASS_T37_STAGE_LOG_COVERAGE 34 logs; 26 producer digests; 8 presence-only
```

The actual producer also supports a cold-baseline mode. That mode requires its
additional first stage and log, giving 35 logs and 27 producer digest checks.
The control suite exercises that branch with a synthetic log, explicitly not
with a cold supplier execution. `audit.py` checks the fixed T37 log contract;
it does not establish source identity, inspect the rest of the replay, or
substitute for `make frontier942-verify`.

## Coverage and limits

| Layer | Logs | Producer-recorded digests checked |
|---|---:|---:|
| Top-level T37, reused baseline | 13 | 13 |
| Native U8 | 8 | 0 |
| Discovery | 6 | 6 |
| Strict replay | 7 | 7 |
| Total | 34 | 26 |

All four ordered indexes must be complete and have integer zero exit codes.
Every expected log must be a regular file contained in the replay directory.
An empty log is valid; the actual `build-parent.log` is empty. There is no
heuristic success-text check.

The 80 negative controls cover every single-log omission, every changed log
with a producer-recorded digest, and five mutations of each index: omission
of its final stage, reversal, failure status 1, boolean false and floating zero.
The verifier restores and rechecks the original evidence after the mutations.
All 34 archived logs must be accounted for. This finite census is complete for
that declared class; arbitrary multi-file changes are outside the census.

The eight native logs have no producer-recorded digests. The checker records
their current hashes but does not claim to validate those bytes against an
earlier commitment. Eight native-content changes deliberately remain accepted
while changing the observed hashes. This positive limitation control prevents
claiming stronger coverage than the format supplies. A forged self-consistent
receipt is not authenticated execution. Archive integrity, receipt consistency,
fresh execution and mathematical proof are separate claims.

No new kappa, supplier improvement, cost reduction, or broad search result is
proposed. The selected conditional value remains
`1661960547713947/1000000000000000000`. The optimistic change to the complete
selected cost invoice is zero. The all-size/compiler, realization, hosting,
precision/tape, analytic and bit-interface assumptions remain. No full
supplier replay, invoice recomputation, Lean proof or Linux CI is claimed here.

## Sources and credit

The base is `2921874911956718fcaaaf9396fe8267b3cfa9f0`. The reviewed source
head is `1960cfa919a0945d0ca4cb14ea96237000037903`, PR942, integrated in
`3825dc0ea1317629864ebeb6929719cc4bbf525f`. `SOURCES.json` distinguishes the
five consumed inputs from historical context pins. Context pins describe the
base commit only; a later change to the moving selected pointer does not
invalidate this fixed archive audit.

Jonathan Capalbo supplied the T37 construction, producers and final binder.
Chafik Boukhalfa supplied the T21 construction, and Hao Yan supplied the T16
and independent owner-audit lineage. The native producer is retained through
the PR869/870 U8 work and Jeremy Kothe's PR799 X4 ancestry. Its notices retain
NewBArch, ColdWitness/icekylinx and the earlier factory, gauge and controller
credits. Douglas Colkitt supplied the maintainer coverage wrapper and archived
review. Lucas, @ljste, supplied the preceding ancestor audit. Stephen Shore,
@nightangelflowerwin-ops, supplied PR865's source-versioned coverage work, and
Adem Vessell supplied PR851's bridge controls. Their packages and notices
remain unchanged.

This scope extends the evidence-coverage idea from #865 to the current T37 log
inventory. It does not repeat #991's alternate owner schedule and payload
controls, #1006's bitmap owner audit, or the T37 arithmetic audits #1051/#1052.
The local `CLAIM.md` records the random assignment, coordination scan, rejected
candidates and fixed stopping rule.

Prepared for Sagar Thakrar with substantial OpenAI Codex assistance in design,
implementation, analysis and documentation. No independent human review is
claimed. New files are Apache-2.0 under the repository root license. The source
predicate slice is executed from the pinned original file; predecessor
copyright, license and AI-assistance notices remain in force.
