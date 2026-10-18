# Executed local validation

Windows, Python 3.14.5, standard library, 2026-10-13. Final commands ran
after code and proof finalization. Every process completed before commit;
there are no background writers modifying tracked receipts.

```text
python -I -O -B research/r439-donor-separation17/verify.py
PASS_DONOR_SEPARATION17 rows=23 functionals=6118 separated=4 controls=6

python -I -O -B research/r439-donor-separation17/independent.py
PASS_INDEPENDENT17 rows=23 zero_rows=4
representation_counts=[3,1,2,1,3,2,2,1,2,3,0,3,2,0,0,2,1,1,1,1,1,1,0]
dual_assignments=58320

python -I -O -B research/r439-donor-separation17/test_package.py
PASS_PACKAGE17 relocated=1 controls=6

python -B scripts/verify_selected_result.py
PASS selected record, exact kappa, original source inventory and proof supplement:
1661960547713947/1000000000000000000
```

The independent engine propagates all 11+12 integer basis columns through
the literal source blocks, without importing primary or predecessor code.
It enumerates every unused/entry/final choice per donor, pruning only positive
overshoot. Its finite positive cases are the other 19 rows; these demonstrate
that the checker does not simply reject every row. All four dual supplies
are also attained as maxima in the relaxed independent-donor choice domain.
The entire choice domain is stronger than the original order-restricted
domain, which is why a negative result transfers without an order search.

Mathematical controls reject a reversed functional, double-counted alternative
donor states, omission of the negative coordinate, a non-strict inequality,
a float weight and a changed source frame. Package controls reject a missing
source-pin entry, a changed immutable gzip, altered selected snapshot, float
and bool substitutions in the expected integer schema, and output overwrite.
The relocated replay runs without Git/network in a path containing spaces;
its workspace-local temporary directory is removed afterward.

The local Python launcher prints a location diagnostic before successful
runs. Pass status is based on exit code and the complete expected outputs.
No environment changes, installations or native toolchain attempts were made.
The staged whitespace check passes before commit. Native 5/9/11-stage replay,
H1-H5 supplier replay, full repository suite, hosted CI, Lean, physical tape
invoice and global assembly are outside this unchanged-circuit result.
