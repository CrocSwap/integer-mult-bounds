# Nonfield coefficients do not escape the one-relation paid-rank floor

This scoped mathematical proof is produced by Nick Petalas. For every nonzero
commutative coefficient ring R, a formal word with normalized rank-one scalar
projectors and at most one rational relation among its paid rank-one address
frames has disjoint target assignments and

    sum_w rank_Q(C_w) <= number of paid factors.

This answers Open next question 2 of Josie Elliston's
[PR6044](https://github.com/CrocSwap/integer-mult-bounds/pull/6044) for the stated
commutative-ring class. It includes Z/2^e, arbitrary composite moduli,
nilpotents, zero divisors and any finite number of restored dirty registers.
The [proof](PROOF.md) uses PR6044's every-field theorem as a cited premise.
It does not recheck that theorem or rerun its scientific executable.

The new specialization theorem permits projectors without a global normalized
outer product. It is enough that one residue field sees only rank-zero and
rank-one projectors, and that the surviving frames have at most one relation.
The bound then counts only surviving factors. If every residue qualifies,
take their minimum. A Z/6 example has two nonzero ring factors but only one
active factor in each residue and attains that sharper floor. A second
example attains the ordinary rank-two floor over Z/4. The written construction
attains the general k-factor bound over every nonzero commutative ring.

## Evidence and reproduction

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/nonfield-one-relation
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/nonfield-one-relation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/nonfield-one-relation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/nonfield-one-relation --check-source-history
```

A reviewer may substitute their CPython 3.12 path. The direct verifier works
from a Git-free export. Expected marker: `PASS_NONFIELD_ONE_RELATION`.
Normal verification writes no files. Optional `--emit-to EXTERNAL_NEW_FILE`
creates a generated receipt containing all six source hashes and every result;
`--check-receipt FILE` recomputes and checks its canonical bytes. Creation
refuses overwrites and paths inside the package. No receipt is hand-written.

The exact finite evidence checks the new composite-ring setting:

- Enumerate every two-by-two matrix over Z/m for m=4,6,8,9,10,12. Retain
  exactly 864 idempotents with zero determinant among 42,945 matrices. Compare the full
  residue-rank histogram with the classical prime-power/CRT formula.
- Multiply every two-factor word on those projectors for m=4,6,8,9, using
  independent frames A=diag(1,0), B=diag(0,1). Also multiply every three-factor
  word over Z/4 with frames A,B,A, which have one relation. Compare every
  coefficient after specialization on 45,821 words, and check disjoint assignment and the
  sharper active-factor bound at all 85 diagonal monomial endpoints.
- Check the Z/6 partial-projector example, its glued endpoint, its rejection
  as a global monomial before gluing, and the sharp rank-two Z/4 example.
- Nine rejection controls cover the zero ring, a map that is not a residue
  quotient, failed idempotence, rank-two fibers, excess relations, nonunit
  coefficients, off-diagonal endpoints, nonmonomial diagonal entries and
  reduction of rational address labels modulo the characteristic.

These finite checks corroborate the written extension. They do not prove
PR6044's universal field theorem or replace its review.

## Limits and implementation

Claim type: scoped written algebraic proof using a credited theorem, with
exact finite corroboration. No new kappa, physical supplier, selected-frontier
change or discharge of the five selected assumptions is claimed. No predecessor
scientific replay, Lean, Docker or selected cold replay is required or run.
Independent human and formal proof-kernel review are unclaimed.

The new verifier has no recursion, network, subprocesses or dynamic code
loading. The matrix census visits at most 12^4 matrices per modulus; stored
projector lists have at most 325 entries. Words have at most three factors,
formal supports at most eight labels and assignment searches at most 27
possibilities. Functions are below 60 lines. Explicit exceptions keep all
checks active under optimized Python. Python managed allocation is a deviation
from fixed allocation, bounded here by these fixed finite domains and one-MiB
source/receipt limits. A larger or externally parametrized replay would need
new capacities or a fixed-storage runtime. Warning-strict normal and optimized execution provide
the available diagnostics. No shared configuration or predecessor code changes.

## Open next questions

1. Can a surviving frame list with exactly two relations beat the rank floor
   over a commutative ring? First seek such a field word, since the present
   specialization transfers every qualifying field obstruction. A shorter
   field endpoint and a complete native tariff remain missing.
2. Can a noncommutative coefficient ring evade this particular specialization
   argument? First specify a ring, a paid alphabet and a diagonal endpoint.
   The residue field and scalar rank-one decomposition used here need not
   exist. No saving follows merely from that failure.

Structured first steps and blockers are in [TASK.json](TASK.json).

## Credit

Credit Josie Elliston / PR6044 for the every-field one-relation theorem and
its explicit nonfield question. Credit Hanson Sun / PR1454, woklerx / PR1456,
theon199, Ali Romman / PR468, eumemic / PR288 and huxint / PR203 for the
retained register-model and one-relation lineage. Maximal-ideal reduction,
rank-one idempotent factorization over fields, CRT and prime-power projector
counts are classical. No general literature-priority claim is made.
[SOURCES.json](SOURCES.json) pins the predecessor statement and historical
orientation sources; no predecessor executable is imported. New files are
under Apache-2.0.
