# CI verification

## Current selected-family replay: #5413 with #5407 and #5414

The [selected record](../certificates/selected-result.json) binds conditional
κ = 0.003027288235, the [promotion and scope](research/pr-intake-evidence/pr5413-promotion/PROMOTION.md),
[explicit source closure](../certificates/frontier5413-source.json),
[review validation](research/pr-intake-evidence/pr5413-promotion/VALIDATION.json), and
[integration receipt](research/pr-intake-evidence/pr5413-promotion/INTEGRATION.json).

`make frontier5413-verify` authenticates the selected source manifest, derives
the certificate from frozen numerical evidence, and exports the complete
three-package execution closure. It replays #5407's five-stage provider audit,
#5413's eight-stage admission, and #5414's independent companion screen serially.
The exported inputs are checked again afterward. Source-bound #4610/#5241 and
earlier BIT/native/compiler/tape/analytic foundation coverage is explicitly
reused; its historical suites are not rerun.

Each package runs under an external sampled 1 GiB aggregate descendant-memory
guard, with timeouts of 660 seconds for the provider and primary packages and
120 seconds for the companion. On macOS the replay uses the reviewed RLIMIT_AS
adapter; on Linux it invokes the unmodified package wrappers. The recorded
successful local macOS replay does not establish a hosted Linux pass.

The [frontier5413 workflow](../.github/workflows/frontier5413.yml) is manual-only,
uses Python 3.12 on Ubuntu, materializes the declared source closure, and uploads
receipts and logs. Its status is separate from local validation and recorded in
the integration receipt. Routine donor PRs do not launch this selected replay.

`make selected-record-check` verifies metadata and source/proof hashes. It does
not execute the operators or prove the five inherited framework assumptions.
The finite checks do not establish the full integer multiplication theorem,
and the uniform word remains unmaterialized.

## Historical selected-family replay: #4610 with #5241

The historical [selected record](../certificates/checkpoints/frontier4610.json) binds conditional
κ = 0.0030217758, the [review](research/pr-intake-evidence/pr4610/PROOF-REVIEW.md),
[explicit source closure](../certificates/frontier4610-source.json),
[review validation](research/pr-intake-evidence/pr4610/VALIDATION.json), and
[integration receipt](research/pr-intake-evidence/pr4610/INTEGRATION.json).

`make frontier4610-verify` authenticates 585 source pins and exports exactly
82 reviewed inputs into a fresh directory. The old selected record is explicitly
remapped from `certificates/checkpoints/frontier4470.json`; frozen source packages
are unchanged. The eleven admission stages run serially under a sampled 1 GiB
descendant-memory limit and a 660-second timeout. The source-bound #4470 foundation
is reused explicitly. This is not a full historical cold replay. No Lean, Docker
or optimization search is part of this target.

The [frontier4610 workflow](../.github/workflows/frontier4610.yml) is manual-only,
uses Python 3.12 on Ubuntu, and uploads receipts and logs. Its sparse checkout
materializes only the source manifest's declared files. Git history authenticates
the frozen canonical inputs; mathematical replay reads the exported files.
The integration receipt distinguishes local success from hosted status: no Linux
pass is claimed until the dedicated hosted replay has actually completed.

The [historical #4470 workflow](../.github/workflows/frontier4470.yml) is now
manual-only and checks out its last selected checkpoint. Neither workflow runs
per donor PR. Routine queue intake must not launch historical supplier suites.

`make selected-record-check` verifies hashes and the exact selected κ.
`python3 -B scripts/research_selected_baseline.py` compares the raw certificate's
budget stages. Neither is an operator replay or a proof of the five inherited
framework assumptions. The finite checks do not establish the full integer
multiplication theorem, and do not materialize the uniform word.

## Historical selected-family replay through #1094

Start with the [selected record](../certificates/selected-result.json). Its
`reproduce`, `review`, `source_manifest` and `validation` fields identify the
replay command, scoped assessment, source bindings and integration evidence.
At that checkpoint, the selected composition is #589 with #1094, documented in
[the review](research/community-batch1099-review.md),
[the source manifest](../research/community-frontier1094-audit/SELECTED-SOURCE.json)
and [the integration receipt](research/community-batch1099-integration.json).

The public cold replay is `make frontier1094-verify`. The configured
[frontier1094 workflow](../.github/workflows/frontier1094.yml) runs on Ubuntu
24.04 with Python 3.12, C++17, Boost and the pinned bit package's Python
requirements. It checks the selected and historical #1042 records, then runs
`python -B scripts/verify_frontier1094.py --work "$RUNNER_TEMP/frontier1094"`
in a fresh output directory. It requires tracked files to remain unchanged
and uploads replay receipts and logs. Selected-input path filters control
push and pull-request runs; manual dispatch is also available.

`make selected-record-check` checks metadata and source/proof hashes, not the
operators. The cold replay checks the finite construction and composition;
it does not discharge the inherited all-size/compiler, realization, hosting,
precision/tape, analytic or bit-interface assumptions.

The integration receipt records successful local macOS execution and leaves
hosted Linux CI pending **at that review checkpoint**. This is dated evidence,
not the latest hosted status. Consult the
[workflow runs](https://github.com/CrocSwap/integer-mult-bounds/actions/workflows/frontier1094.yml)
and check the exact tested head, inputs and logs before claiming hosted
coverage. A workflow file, a generic matrix pass or a successful historical
#626 run does not establish execution of the selected #1094 construction.

## Historical selected-family replay through #626

At this historical checkpoint, the #543 + #626 composition used
`.github/workflows/frontier626.yml`.
Its [completed Linux run](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/38317651752)
passed on 2026-10-13 at commit `ed49217ad6244f1d3bfe4588f122fa861849739c`.
The [preserved artifact reconciliation](../research/selected626-linux-reconciliation/README.md)
checks source equality to the sprint base, all six replay stages and exact
mathematical assembly agreement, with explicit limits for omitted payloads.
The older queued integration receipt is retained as historical evidence.

## Historical selected-family replay through #588

`.github/workflows/frontier588.yml` provides one complete cold check of #543
with #588 on Ubuntu 24.04 and Python 3.12. It installs NumPy, SymPy, SciPy,
C++17 and Boost, checks the selected record and review evidence, rebuilds both
finite suppliers and their exact composition, and uploads the execution
receipts and logs. It triggers on changes to the selected dependency packages,
entry points and selection metadata, or by manual dispatch.

The shared complex foundation is rebuilt once inside that command. Every
changed provider, phase program and owner assignment is still checked. No
cached proof result replaces execution. The workflow uses the repository's
pinned checkout and Python-setup actions, read-only permissions and a fresh
output directory.

The 23 workflows imported with the frozen family through #588 retain their
original replay jobs under manual dispatch. This keeps historical checks
available without automatically launching every numerical predecessor on
each new family change. The existing generic verification matrix remains
separate. Its passing status does not substitute for the selected-family run.

Local replay has passed. The [integration receipt](research/community-family588-integration.json)
records Linux CI status separately; a workflow file alone does not establish
cross-platform success or prove the retained all-size theorem assumptions.

## Historical matrix split

The remainder documents the earlier generic suite and its original timings.
Its counts and checkpoint-specific Lean statements are historical.

The previous release's [successful Linux run](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/37799621548)
took 15–16 minutes per Python version before the new PR #49 producer replays.
The Python 3.13 log shows these major sequential costs:

| Operation | Approximate elapsed time |
|---|---:|
| Partial-swap producer regeneration | 202 seconds |
| Historical ternary audit | 156 seconds |
| Unit-test collection | 180 seconds |
| Prime-field network certificate | 83 seconds |
| Endpoint-gauge producer regeneration | 54 seconds |

The workflow now distributes each Python version across eleven independent
checkouts:

| Make target | Coverage |
|---|---|
| `verify-community` | PR #39 and follow-up arithmetic, reversed/fixed producers, PR #48 and #49 complete replays |
| `verify-producers` | Copied-center, structured-bulk, endpoint-gauge and partial-swap producers and certificates |
| `verify-certificates` | Remaining exact arithmetic, historical constructions and research audits |
| `verify-ternary` | Complex-compression and ternary checkpoint audits and patches |
| `verify-research` | 28 recovered historical audits and their regenerated certificates |
| `verify-tests` | All current and recovered tests, isolated by module and all 20 historical patch-application checks |

| `verify-strips` | Full skip-prefix and dual-suffix producers, exact profiles and controls |
| `verify-clones` | Original-envelope clones and split-pair producer replays |
| `verify-positive` | Positive-frame rebuild and bounded-minor exact profiler with sufficient primes |
| `verify-joint` | Full PR57/60 compiler words, profiles, controls and independent arithmetic |
| `verify-pair` | PR62 plain and stacked witnesses and independent PR61 refinement check |

Every group runs on **all three** Python versions (3.11, 3.13 and 3.14).
All three pinned Lean packages remain separate jobs. No producer replay, negative
control, historical result or Python version is dropped. Every arithmetic job
also requires `git diff --exit-code` on its entire tracked checkout, so a
regenerated artifact cannot silently diverge from its recorded certificate.

At the original five-group split, `make -n verify` expands to the same multiset of
**94 leaf commands**, including identical multiplicities for duplicate checks.
That split changed scheduling rather than mathematics or certificate inputs.
The subsequent research reconciliation adds 28 audit commands (122 total leaf
commands) and additional tests; it does not remove any existing check.
The complete old run remains useful as a comparison; the new workflow must
pass independently in clean checkouts.

Local `make verify` invokes the eleven groups sequentially. Do not launch them
concurrently in the same worktree: one group can read certificates another
group regenerates. CI avoids that race by using a separate runner and checkout
for each group. Directly invoking a group works from a fresh checkout; the
pinned certificates are inputs, and upstream producers are checked in their
own required jobs.

This trades more concurrent runners and checkout overhead for a shorter
critical path, without relying on a cache of successful mathematical results.
The baseline timings suggest a roughly 5–7 minute critical path if runners
are available; measure actual runs before treating that as a guarantee.

The current matrix has 33 arithmetic jobs (eleven groups × three Python
versions) plus three Lean jobs. PR61's package builds on Lean 4.31 and checks
169 distinct declarations and eleven Python tools. Its concrete input is bound
to the selected finite profile; the full multiplication theorem is not formalized.

Contributed research packages reuse module names. `run_isolated_tests.py` runs
every test file in a fresh interpreter so import state cannot select another
package's graph or verifier. No test files are omitted. The enlarged-frame job
installs Boost headers if needed and repeats its sufficient-prime proof on every
run; the diagnostic three-prime profiler is not used as the exact certificate.

### Bound an isolated test module

For a local or CI run with a known per-module budget:

```sh
python3 scripts/run_isolated_tests.py --workers 4 --module-timeout 600
```

The optional timeout is a finite positive number of seconds, measured from each
module's actual process launch. Waiting for a worker does not consume it.
Omitting the option preserves the unlimited default. On expiry the module
returns failure code 124 with captured diagnostics; even a completion receipt
cannot turn a timeout into success. Other modules continue, and the final CLI
exit remains nonzero. No test or assertion is skipped to meet the deadline.

The runner stops the owned process group on POSIX. On Windows a private
supervisor reuses `research_package.py`'s gated Job Object and waits for its
ordinary descendants to stop even when the test module has already exited.
Timeout/cancellation targets the live supervisor; closing its job handle also
terminates the owned descendants. Copies of the runner on Windows must include
`research_package.py` in the same scripts directory. Test modules must still
join proof-relevant children and propagate their failures: cleanup does not
validate unfinished work. After cleanup, capture has a bounded drain
so an inherited pipe cannot impose an unlimited EOF wait. Cleanup failures
propagate through the existing cancellation path instead of becoming a pass.
This is a failure bound, not a speedup or a new mathematical result.

The [Windows exit-cleanup evidence](research/isolated-test-windows-exit.md)
records the caller-specific native-handle controls and remaining limits.

Regression command: `python3 -B -m unittest discover -s tests -p 'test_isolated*.py'`.
The deadline controls exercise hung imports, partial output, child cleanup,
queue waiting, ordinary success/failure, premature zero exits and invalid
budgets. Tekalign, with substantial OpenAI Codex assistance; Apache-2.0.
