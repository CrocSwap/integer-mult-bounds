# Parallel CI without reducing verification coverage

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
