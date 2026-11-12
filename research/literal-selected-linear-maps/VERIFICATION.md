# Verification receipt guide

Science frozen and independently accepted:

- linear.py SHA256 `d56704082b82e37d4a360b8aad7e0af63499f4160c6bbcfd338804453c46fa33`.
- PROOF.md SHA256 `217b6bbe9271aa5d5c0f0999a231d7386c7ba3fc432a88e3796d70ca283eb322`.
- Right table+alphabet `40c12281a92857287c13fd55d551ab3e574392656a174812e07625764eb7ae6c`.
- Left table+alphabet `5f1a916d1a4c39195522754c44b8facd2fbe237161943440fa6aa25c3b287496`.

## Author evidence

`source_gate.py` prints PASS_SELECTED_LINEAR_SOURCE_GATE. It checks fourteen
retained source byte/Git-blob pins, recomputes the actual current native recipe
and compares both source matrix row lists. This portable check is distinct
from root's actual commit:path authentication below.

`check.py` prints PASS_LITERAL_SELECTED_LINEAR_BASE. It checks all 512 scalar
matrix addresses, ten complete actual m9,f1 successful packets and six
malformed controls. Success shapes vary r/P/S/w. Two packets append an opaque
sixth Gamma code with a 2,049-bit represented cutoff, plus trailing symbols;
only the first-five prefix is parsed. Inputs include translated/negative
origins, arbitrary raw bits and protected exteriors.

`check_big.py` prints PASS_ACTUAL_BOTH_SELECTED_LINEAR_F2. Its second author
interpreter is C4's dense CPU adapted to 27 tapes; that reuse is disclosed.
It executes both actual m9,f2 arrays in full, with 262,144 addresses and
524,288 bits each. Direct matrix-coordinate XOR provides the oracle. The
right and left costs are 1,230,072,483 and 1,726,632,151 instructions, and f1
counts match the reference CPU. Three altered programs fail the oracle:
first-column-only (despite complete clean retirement), reversed controls,
and changed final-commit bits.

`check_reuse.py` prints PASS_SELECTED_LINEAR_SAME_OWNER_REUSE. Each fixed map
runs on a longer then shorter field on the same actual objects, preserving
old history and opaque public tails. The smaller call has the same price as
a fresh small call. No failure-time retry is inferred.

`check_cost.py` prints PASS_EXACT_SELECTED_LINEAR_COST. The independently
summed helper/geometry/full-work formula agrees with fourteen complete
physical receipts. Fifty-six larger parameter checks are exact arithmetic
only: no huge payload execution is claimed. The universal inequalities are
proved in PROOF.md rather than inferred from these finite points.

Normal and optimized author executions produced byte-identical scientific
receipts for all five scripts. The C++ compiler flags for the author runner
are `-std=c++17 -O2`; external timeouts/watchdogs are verification controls,
not part of the unbounded tape-program semantics.

## Separate root review

The unchanged files in independent/ are a separate root agent's work:
REVIEW.md, dense_check.py, literal_dense_runner.cpp, RESULT.json,
RESULT-OPTIMIZED.json and SOURCE-BINDINGS.json. Their copies match the originals
byte-for-byte. The review covers the complete source, universal proof,
physical lifecycle, inherited premises and complete cost/history bill.

The root CPU was written separately from the author CPU. The expected map is
computed by inversion of the nine-bit truth table at each OUTPUT column and
reconstruction of its source address; it does not execute the CNOT word.
Fourteen complete actual m9 packets, including both full f2 fields, four
malformed controls, two grow/shrink/regrow sequences and three program mutants
are checked. The ordinary eighteen packets total 3,076,553,809 transitions.
The exact full instruction formula and DATA's V+1 reads, V writes and 4V
moves are checked. Normal/optimized receipts agree. SOURCE-BINDINGS.json
records all fourteen actual Git commit:path/blob/byte bindings, not just a
self-declared local checksum comparison.

Portable review commands, from the package directory:

```sh
python -I -W error -B independent/dense_check.py linear.py
python -I -W error -O -B independent/dense_check.py linear.py
```

Both require a C++17 compiler named `c++` and compile the independent runner
in a temporary directory. VERIFY.json records explicit normal/optimized
commands and their timeouts as a standalone replay manifest. TASK/SOURCES
use standalone provenance; no compatibility with canonical
research_package.py, hosted CI acceptance or a new shared workflow is claimed.

## Practical limits

Finite traces are implementation evidence. Universal conclusions rest on
the reviewed algebra/loop/cost invariants. No complete MOVE, old-codec bridge,
free strided layout, numerical/C admission, source caller, faster nonleaf
rate or foundational assumption is supplied. No new kappa is claimed.
