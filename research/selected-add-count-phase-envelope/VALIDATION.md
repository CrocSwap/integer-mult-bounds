# Verification boundary

The registered replay executes the unchanged authenticated source, with a
nonretaining Tape observer. It checks the written proof in PROOF.md on finite
fixtures; it does not turn those fixtures into a universal source proof.
Normal replay is read-only. Only `verify.py --write` changes RESULT.json.

The package uses Python's standard library. The fixture set has 70 successful
ADD executions plus the successful escaping-callback counterexample.
Eight embedded controls check a one-cell-short actual quota, invalid positions,
coefficient and alias domain, omitted preparation, omitted marginals,
preparation-only pricing, and unnecessary addition of disjoint peaks. The
escaping callback separately refutes the omitted-release premise. Seven tests
also check literal expected peaks, direct array capture, a wrong-coefficient
implementation mutant on an origin input, module/observer restoration after
failure, Git-free relocation in normal and optimized modes, changed executable
source and typed receipt corruption. No assertion depends on Python `assert`.

An independent internal source audit and a separate observer using a list of
weak references reproduced all 70 receipts and the escaping receipt under
CPython 3.14. Extra callback widths one and 128 gave exact private callback
peaks six and 260. These were read-only internal corroboration, not retained
additional fixture coverage or independent human review.

## Code bounds and deviations

The new checker and tests use structured, nonrecursive control flow. There
are seven fixed imported modules, ten authenticated source inputs, at most
32 observed tapes, 2048 cells per tape, 4096 payload bits per fixture and
2,000,000 observer samples per fixture. Every numerical arena has capacity
64 Words. The fixture family and every external command are finite. CLI tests
have 30-second timeouts; registered commands have 120-second timeouts. The
loader and observer restore all altered module bindings in finally blocks,
including failed extraction and failed native execution. This is test-host
cleanup, not a proof of arbitrary native numerical rollback.

Rule 3, fixed allocation. Python objects, arithmetic, JSON and source compilation
allocate during replay. Fixed-capacity replacement would change the observed
source and expand the task into an interpreter implementation. Scope is this
bounded offline checker. Explicit fixture/tape/payload/sample/arena limits bound
live observed state; the full 70-fixture receipt is retained rather than an
unbounded event log. No asynchronous work or background workers run. Local
replays and resource-limit rejection checks verify those controls. A future
larger domain must first revise and justify its enforced limits. Python/runtime
allocator overhead is neither inspected nor included in the mathematical metric.

Rules 8 and 9, authenticated code loading and observation dispatch. The loader
executes only hash-authenticated module bytes and exactly one named Geometry
class and action definition from authenticated ASTs. Their unrelated imports
would require an entire selected caller, outside this component boundary.
Fixed import order and explicit scopes resolve all targets; the source hash and
inventory checks precede execution. The observer subclasses only three Tape
factory bindings and wraps only the known Layout.extents method. Source
tampering, module-restoration and wrong-endpoint controls exercise this boundary.
This deviation is restricted to the isolated verifier and should be removed if
the retained source gains an importable component API without changing bytes.

Rules 4 and 10. Formatting retains ordinary readable functions; the longest
function is the 61-line fixture orchestration, including its signature and
receipt fields. Phase invariants are a separate cohesive check. This is within
the roughly one-page review limit without compressed formatting. Ruff
E/F/I/B/UP checks and warnings-as-errors Python replays apply to the new code.
No shared diagnostic configuration or frozen
source is changed. The retained numerical/tape loops are existing scientific
inputs, not rewritten to enforce a different runtime policy.

The primitive's own failure cleanup, numerical/program/record backing, total
private A, physical capacity/reuse, stronger time contracts, recursive/outer
reserve, selected cold replay and formal-kernel proof are unrun obligations.
Hosted CI status is separate from local verification.

## Recorded local checks

Environment: macOS 27.0.1 arm64, CPython 3.12.15 for the registered hook and
workflow tests, CPython 3.14.8 for optimized direct replay, Ruff 0.17.1.
The machine's bare python3 is 3.9 and is not the declared replay environment.

- Python 3.12 package metadata/pin check and both registered commands pass.
- Python 3.14 `-I -O -B -W error verify.py` reproduces the same receipt.
- Ruff `check --select E,F,I,B,UP --target-version py312` passes; Ruff format
  checks pass for both new Python files.
- Python 3.12 `-W error -B -m unittest discover -s tests -p
  'test_research_*.py'` passes 144 tests, seven skipped. Expected child-failure
  traces in that suite are its rejection controls, not test failures.
- Refreshed canonical main `5a0dc2c0f4685b02bef7776bc196c7c1231cbac1` has no
  relevant source, priority, selected-record or replay-runner change from the
  scientific base. Final complete overlap at 10:42 UTC covers 493 open PRs,
  2116 closed/merged PRs and 1588 Discussion records, without warnings.
  Arbitrary diffs and unpublished work are not covered. All three predecessor
  PR heads remain the exact declared pins.

No full selected cold replay or hosted CI result is claimed.
