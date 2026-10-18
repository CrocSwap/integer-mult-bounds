# Validation record

Verification and packaging began by 2026-10-13 19:52:45 UTC, ahead of the
20:07:19 verification deadline. The cycle's hard finish is 20:17:19 UTC.
Host: macOS 26.5.2, arm64. CPython 3.11.15 and 3.14.8, standard library only.

Both interpreters passed normal and optimized isolated verifier runs:

```sh
rtk proxy python3.11 -I -B research/reader-restoration-cuts-seed53/verify.py
rtk proxy python3.11 -I -O -B research/reader-restoration-cuts-seed53/verify.py
rtk proxy python3 -I -B research/reader-restoration-cuts-seed53/verify.py
rtk proxy python3 -I -O -B research/reader-restoration-cuts-seed53/verify.py
```

Expected `PASS_READER_RESTORATION_CUTS restoration=5->1 forced_cut=5 exhaustive=2851 seeded=160`.

- 1,555 exhaustive scalar batches, all lengths zero through four, signs ±1 and
  readers -1,0,1. 11,311 partitions replayed independently.
- 1,296 exhaustive two-coordinate two-child batches, signs ±1 and readers
  -1,0,1 in each coordinate. Prices `[2,5]`, nonempty restoration overhead 3.
  2,592 partitions replayed independently.
- 160 deterministic seed-53 batches, lengths five through eight, dimensions
  one through three, reader values -3 through 3, positive prices one through
  nine, overhead zero through three, and declared mandatory cuts. Every cut
  mask satisfying those cuts was tested, 5,264 partitions in total.
- All D/W basis columns and every selected cut are checked. Exact equality,
  no floating-point tolerances or sampled input vectors in this oracle.
- The five-reader construction and its literal inverse pass. The scalar
  instruction invoice is recounted and included in the certificate.
- Four mathematical controls distinguish final equality from intermediate
  legality, remove the cancellation, reorder a reader, and require child-two
  observation. Nine invalid planner inputs are rejected.
- PR1155's original certificate reproduces with its unchanged checker. Its
  Batch implementation confirms five-versus-one restoration multiplication
  counts and equality for real and imaginary basis inputs plus `W=7-3i`.

On both interpreters, the package test passes in optimized isolated subprocesses:

```sh
rtk proxy python3.11 -I -O -B research/reader-restoration-cuts-seed53/test_package.py
rtk proxy python3 -I -O -B research/reader-restoration-cuts-seed53/test_package.py
```

This relocates the package, regenerates and compares every parsed certificate
field, checks the public planner CLI, and rejects four independent file
corruptions plus an unknown CLI field. The corruption cases alter the saved
cost, pinned source, cancelling reader and emitted planner cost. No shell,
network or repository-wide source is needed by the relocated checker.

Certificate SHA256:
`3968403e53ec0937bd9ee1203de402b3d40810e7b489ad4ff31960ddc69face1`.
JSON serialization is deterministic. The retained PR1155 certificate differs
from its upstream bytes only by an appended final LF, as declared in SOURCES.json;
its parsed fields and original verifier are unchanged.

Repository guard checks:

```sh
rtk proxy python3 -B scripts/verify_selected_result.py
rtk proxy python3 -B -m unittest discover -s tests -p 'test_selected*.py'
rtk git diff --check
```

Selected integrity passes at unchanged conditional kappa
`836330098538459/500000000000000000`; all 25 selected tests pass. No pre-existing
tracked file is changed. New material is confined to this research directory.

At the first completed result, the live queue through PR1184 was checked again.
PR1155, PR1164 and accepted PR1088 retained the exact heads in SOURCES.json and
had no review or comment correcting the read-free condition. No matching planner
or correction appeared. The claim remains in its original scope, with no pivot.

Not run: the complete selected cold replay, full historical repository suite,
Linux execution, hosted CI, proof-assistant formalization or independent human
review. This package does not alter the selected construction, so a cold replay
is not the applicable verification target. Supplier admission and the remaining
physical and analytic interfaces are not established by these finite checks.
