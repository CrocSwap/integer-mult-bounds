# Scoped negative result: a ninth total with fixed P112 coordinate readers

**Adding one total cannot lower the P112 complex coordinate decoder's
pairing-rank copy cost below 64 while retaining its original eight reader
columns.** This covers arbitrary real coefficients and an arbitrary
112-component source correction, including sources outside the coordinate
column space and mixed terms of pairing rank below eight. No new kappa is
claimed.

For the pinned 112 by 8 coordinate matrix X, the investigated mechanism is

    X X^T = sum_j x_j (x_j-a_j z)^T + (Xa) z^T,
    a in R^8, z in R^112.

The sum of the nine terms' binary label-pairing ranks is always at least
64. Equality is attained at z=0. This includes every exact nine-term
factorization retaining the original coordinate reader columns (up to
nonzero column rescalings), and the transposed family. See
[the precise theorem and proof](PROOF.md).

The existing coordinate cost 64 belongs to **Joel Pulikkan / GamingPuzzled's
PR620 and its predecessors**. **DreamingOfClouds' PR717 D1** identifies the
open mixed-rank problem and supplies the pinned geometry. This contribution
proves a new restricted obstruction inside that problem, using an
annihilator argument. It does not settle arbitrary nine-term decoders.

## Reproduce

From the repository root, with Python 3.10+ and no third-party dependencies:

```sh
python -B research/p112-single-lift/verify.py
```

Expected:

```text
PASS_P112_SINGLE_LIFT: 511 support certificates; 3272 sign cases; 128 conflicting kernels; 9 negative controls; copy cost >= 64
```

The separate implementation imports neither the main checker nor its
geometry module:

```sh
python -B research/p112-single-lift/independent_check.py
```

Expected: `PASS_P112_SINGLE_LIFT_INDEPENDENT`, with 511 integer minors,
3,272 set-rank replays, 128 incompatible kernels, and four arithmetic controls.
Both commands are read-only and work under `python -O -B` as well. The small
vendored NumPy model is retained as source evidence and is **not executed**
by either command.

To regenerate the exact certificate explicitly:

```sh
python -B research/p112-single-lift/verify.py --write /tmp/p112-single-lift.json
```

`--check PATH` compares all fields against a different certificate. JSON
equality is semantic; no compressed-container hash is used as mathematical
equality. Source inputs are pinned by exact SHA-256.

## What is certified

- The complete P112 root geometry, all 12,544 scalar and binary pairings,
  and entry-for-entry agreement with PR717's geometry snapshot.
- All 511 nonzero binary functionals: 503 rational support matrices have
  rank eight; the other eight have exactly the eight coordinate-axis
  kernels. Explicit original-row minors certify the lower ranks, and full
  zero-column checks certify the exceptional upper ranks.
- All 3,272 sign patterns modulo global sign. For two through seven active
  coordinates, the necessary binary system has full column rank. With all
  eight active, each of the 128 systems has rank 63 and one nonzero kernel
  vector. Each such vector forces incompatible correction values at 56
  ports. This last step is essential; the linear relaxation alone is too weak.
- Negative controls for roots, labels, the dual form, port coverage,
  omitted terms, compensation signs, false full-rank claims, treating a
  relaxation kernel as feasible, and erased constraints. Positive controls
  include a genuine rank-one ninth term, unequal coefficient magnitudes,
  rational corrections, the k=0/1 boundaries, and sharp cost 64.

The finite checks establish premises of the written proof. The theorem for
all real a,z follows from that argument; it is not inferred from the finite
diagnostic examples or from a failed search. No proof-assistant verification
or independent human review is claimed.

## Scope and accounting

The equality is to `2G` on every matrix entry. Arbitrary changes of the
eight reader columns, masked decoders with additional free corrections,
multiple added totals, other geometries, complex rather than real scalar
coefficients, and interacting delivery programs remain outside scope.

The interpretation as a physical copy lower bound inherits **PR446 Theorem
C's separate-total, drop-free gathering and copy-tree assumptions**. At the
base commit the ledger lists PR446 as unreviewed and PR620 as partially
reviewed; citing them does not upgrade their status. The algebraic cost
theorem is stated directly and does not require accepting the full physical
or multiplication construction.

Preparation, source access, frame changes, restoration and recursive-child
expenses were optimistically granted zero extra cost before attempting a
physical implementation. Even that relaxation does not reduce the copy-rank
sum. A different rank distribution or improvements to helper work and
hosting could still matter at unchanged copy rank. This is not a universal
bound on runtime, recursive moment, or kappa, and no supplier is constructed.

The selected conditional kappa at the exact base
`7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261` was
`1661202643272239/1000000000000000000` (#741 with #589 on #555). The selected
record, its suppliers, and `upstream/` are untouched. All-size/compiler,
common-label/mutable-source, hosting, precision/tape and analytic obligations
of that construction remain inherited.

## Files, provenance and coverage

`geometry.py` reconstructs the geometry exactly; `verify.py` proves the
finite premises and checks `RESULTS.json`; `independent_check.py` uses
fraction-free integer determinants and set elimination. The reference model
and its original notice are retained under `reference/`. Exact source pins
and the snapshot derivation are in [SOURCES.json](SOURCES.json).

Assignment seed **40** was drawn once from OS randomness. It selected the
initial coordinate pair `(1,7)` (zero-based); the successful pair proof
extended within the same single-lift mechanism to all supports. Seeded
traversal checks the full finite sign domain, without sampling or a timeout.
The stopping rule was complete coverage of 511 functionals and 3,272 sign
classes, followed by independent replay. There is no coefficient-magnitude
or correction-vector search cap: the proof handles those symbolically.

The [local sprint claim](CLAIM.md) records selection, related work and the
overlap review. The scope differs from PR717's eight-term/gauge and finite
flip-walk evidence, PR757/761's binary P111 factorizations, PR765's binary
tensor-code factors, and PR703/738/767/785/798/814's extension-ring units.
Their stronger or adjacent claims are not imported as new results here.

## Validation and final refresh

Both checkers passed on Windows/Python 3.12.0 normally and with optimization.
A clean, relocated Git archive passed on Python 3.11 with `-O -S -B`
(optimization on, site packages disabled), regenerating a byte-identical
certificate. Four additional packaging corruptions were rejected: altered
source bytes, an omitted sign case, a duplicated minor row, and a corrupted
kernel. The selected-record checker at the base commit and staged whitespace
checks passed. Exact validation details are in `VALIDATION.json`.

The final overlap refresh inspected 639 open PRs through #842. PR717's pinned
head was unchanged; all-state P112 searches still returned only #620/#717,
and no matching single-lift result was found. Main had advanced to
`f567884aeb8851b6e794af1184119a3bfbe1e631`, selecting Jeremy Kothe's #799
with conditional kappa `1661634653669567/1000000000000000000`. Its reviewed
read exchanges do not alter this research package or the pinned model.
The original base and source pins are retained.

The repository-wide suite and selected-supplier cold replay were not run:
this change only adds an isolated research package. A proposed scoped
workflow could not be pushed because the available GitHub token lacks
`workflow` permission; it was removed before submission, without changing
account permissions. The new package's checks have not run in hosted CI.
Local results do not imply success of the repository's existing CI checks.

Prepared for **Mihir Srivastava (@mihir-s-05)** with substantial **OpenAI
Codex assistance** in mathematics, implementation, verification and writing.
See [NOTICE.md](NOTICE.md); Apache-2.0.
