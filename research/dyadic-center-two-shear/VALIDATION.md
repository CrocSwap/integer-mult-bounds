# Executed validation

Environment: macOS Darwin 25.5.0 arm64; CPython 3.14.6; standard library only.
Starting base: `91a2094f2e022930069e8cfdc810a3ea1b81cd09`.
The source-pinned mathematical inputs are unchanged at refreshed main
`47481c89fd30a43f8f882eb4b391e89c29273fd0`.

Passed:

- `python3 -I -B research/dyadic-center-two-shear/verify.py`: complete deterministic
  receipt matches, including independent exact integer checks, source hashes,
  both complete scalar invoices, recurrence guard and actual primitive census.
- `python3 -I -B research/dyadic-center-two-shear/test_package.py`: **5 tests**,
  including optimized public replay from a minimal checkout without Git metadata,
  paths with spaces and an unrelated advanced selected pointer; corrupted source
  and base-snapshot rejection; an underpriced receipt rejected after fresh full
  replay without overwriting it; standalone optimized independent checker.
- `python3 -m unittest discover -s tests -p test_complex_centers.py`: **4 tests**.
- `python3 -m unittest discover -s tests -p test_disjoint_tensor.py`: **5 tests**.
- `make selected-record-check`: passes at the original PR799 base and again
  after rebase to main `47481c89fd30a43f8f882eb4b391e89c29273fd0` (PR890).
  All 21 pinned input files and the frozen base-selection snapshot match
  after rebase; the circuit verification inputs are byte-identical.
- Python compilation and `git diff --check`.

Exact coverage:

- 6,760,000 central matrix entries for each original/candidate h26 factor.
- Independent implementation: 6,777,536 candidate entries across h8/10/26;
  both central directions, all 5,226 independent h26 input columns.
- Complete signed invocations: h8 with 998 independent input columns per
  direction; h10 with 2,767 per direction; four dense dyadic h26 cases.
- Three-stage bank exchange with actual first/third dirty-bank reuse.
- Full side DAG/embedding, both side frame orientations, shared matching,
  all side/source/scatter/restoration charges and the conservative node ledger.
- Instrumented h26 invocation in each direction: baseline 734,858 additions
  and 52,080 halvings; candidate 728,376 additions and 53,000 halvings.
- 1,300 completed second-shear nominations, 602 admissible; independent final
  two-shear derivation, six primary and eight independent adverse controls.

An initial package run copied an older receipt while regeneration was still
finishing and correctly rejected the mismatch. The final receipt regeneration
and subsequent verification/package tests were sequenced; all five tests pass.
No mathematical witness or cost changed to resolve that packaging failure.

The written identity and cost polynomial cover general even h>=8; positivity
is proved for even h>=10. The h8 case is deliberately retained as a valid but
more expensive control. Finite execution is not a full formal theorem proof.

Not run or claimed: repository-wide `make verify`, selected cold replay,
selected supplier transport/global invoice/owner admission/outer assembly,
Lean, another OS/Python version or remote CI. The changed package has no
production-generator or selected-construction edits; the scoped checks above
cover its exact mathematical inputs and failure modes. All inherited compiler,
realization, hosting, tape, precision and analytic assumptions remain.
