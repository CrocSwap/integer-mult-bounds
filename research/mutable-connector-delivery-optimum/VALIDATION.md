# Local validation and scope

Validated on 2026-10-14, CPython 3.12.12, macOS 26.5.2 arm64, standard library
only. Base/main: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Mathematical scope
was frozen by 09:44 UTC; the remaining session was used for source/overlap
checks, export validation and publication.

Executed from the isolated repository root:

```
python3.12 -I -B scripts/research_package.py --package research/mutable-connector-delivery-optimum
python3.12 -I -B scripts/research_package.py --package research/mutable-connector-delivery-optimum --check-only
make selected-record-check
git diff --check
```

Registered replay passed all three commands:

```
PASS_MUTABLE_CONNECTOR_DELIVERY_OPTIMUM tariffs=518 pilot=64->52 controls=6 no_new_kappa
PASS_INDEPENDENT_MUTABLE_DELIVERY tariffs=518 settled_states=67023 relaxed_states=184183 map_paths=16384 dirty_assignments_per_schedule=131072 schedules=2 no_new_kappa
Ran 6 tests ... OK
PASS_REGISTERED_RESEARCH_PACKAGE research/mutable-connector-delivery-optimum outcome=completed
```

The test suite's export contains only this package and its three exact live
source inputs. Both checkers pass there under `-I -O -B`, with all files and
directories made read-only and file hashes unchanged afterward. No Git history,
network or predecessor executable is required by the direct checkers. The
registered metadata runner separately validates historical Git provenance.

The six package test groups cover exact-price input aliases and bad shapes,
a nonadjacent optimum defeating a greedy adjacent-pair rule, an omitted
adapter whose delivered outputs pass while final connector restoration fails,
endpoint-neutral writes outside request intervals, a changed literal gate,
source/target aliasing, and read-only relocation. Seven on-disk mutations fail
under optimized Python: float/integer receipt alias, Boolean count alias,
missing scalar gate, duplicate JSON key, nonfinite JSON, source drift, missing
source. Six additional semantic word mutations are in the primary replay.

The first test draft accidentally replaced a gate by itself and correctly
failed its expected-rejection assertion. The test now changes its source from
bit 1 to bit 2; the registered replay above includes that actual mutation and
passes. This was a test-fixture correction, not a changed mathematical result.

The independent checker reproduces the exact tariff receipt digest without
importing the primary checker. Its scalar-identity quotient is an independent
necessary-condition oracle for the universal claim; the arbitrary-map proof
and explicit attaining word establish sufficiency. The 16,384 two-dimensional
map/path checks and complete 17-bit replays are separate positive evidence.
Both implementations have the same assisted author, not an independent human
reviewer. No Lean proof or full integer-multiplication theorem is asserted.

Selected-record integrity passes separately; selected source bytes and kappa
remain unchanged. No full selected cold replay, native/compiler/physical owner
admission, recursive profile, precision/tape admission, measured runtime or
analytic transfer is claimed. Hosted CI status is reported in the PR rather
than treated as part of these local checks.
