# Sharp rank-seven E8 support and equality after frame deletion

Every subset of the declared full E8 leading-one labels with binary rank at
most seven has at most **36 roots**. Exactly 5,440 rank-seven spaces attain
36 on full E8; exactly **448** survive unchanged on the actual fixed P112.
Thus deleting the frame does not improve this uniform capacity.

[PROOF.md](PROOF.md) proves the upper bound and complete equality criterion
by a signed character sum. Each nondegenerate perpendicular two-plane gives
exactly one extremal affine six-space. Fixed-P112 equality requires that space
to avoid the deleted frame. [RESULT.json](RESULT.json) records the full finite
section histogram, equality-support digest and a literal rank-seven witness.
The frame deletes 0/2/4/8 roots from 448/3584/1344/64 full equality supports.

The addition to PR3269's rank-five/six work is the rank-seven equality
classification and actual puncture count. This package does not claim a new
numerical capacity, historical caller exclusion, shortening threshold, decoder
floor, supplier or kappa. It uses the exact leading-one label convention,
not an arbitrary physical port encoding.

## Reproduce

Python 3.12+, standard library, from the repository root:

```sh
python3.12 -I -W error -B scripts/research_package.py --package research/e8-rank7-capacity
```

All direct commands also run in a Git-free exported tree:

```sh
python3.12 -I -W error -B research/e8-rank7-capacity/verify.py
python3.12 -I -W error -B research/e8-rank7-capacity/independent_check.py
python3.12 -I -O -W error -B research/e8-rank7-capacity/test_package.py
```

Both complete implementations check all 43,180 affine six-spaces. The primary
uses polar plane equations and reconstructs the canonical root/frame formula.
The independent implementation uses ordinary-dot RREF normals, reconstructs
roots and their integral coordinates separately and evaluates q from norms.
It shares source authentication, not the primary census or root functions.
Six boundary controls reject malformed source/schema/inventory controls,
including boolean schema one, and changed or linked live input. Four geometry
groups check the unique equality coset, degeneracy, actual witness and a
minus-type 40-point counterexample. Checks survive Python optimization.

The sole mathematical input is canonical-main geometry, pinned by SHA256 and
Git blob. No pending PR Git object or executable module is needed. Registered
replay checks historical task/selected provenance; direct replay authenticates
the live input and does not independently authenticate that history.
[CHECKS.json](CHECKS.json) records actual checks and limits.

## Research decision and limits

This bounded side result tests whether puncturing strengthens the rank-seven
support bound and supplies exact equality structure. The test finds surviving
maximizers. It stops here. It supplies no support-union geometry for multiple
pieces, scalar factorization, native realization, physical consumer or paid
invoice. Source authentication and finite replay do not establish supplier
admission or a complete multiplication theorem. No selected cold replay,
Lean, Docker or full historical census is run.

Separate Before Serializing Shared State kept the branch, package and cache
worker-owned, with short shared metadata/reservation locks. Prove It Works
required two actual implementations and the committed read-only Git-free
export. [ENGINEERING.md](ENGINEERING.md) records Power of Ten inspections and
bounded Python/source-loading deviations.

## Open next questions

Does a current decoder obligation require a 36-root rank-seven support while
excluding all 448 fixed-frame equality spaces? First pin that caller and its
extra support constraints, then apply the exact two-plane/coset criterion.
No such caller is established here. A capacity sum alone is insufficient to
infer an achievable union or a new shortening theorem. Structured context is
in [TASK.json](TASK.json).

## Sources and credit

Base `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
Nick Petalas's PR3269 at `ebe02d33157dc6c6d3b35df204e4a39242b7429e` supplies
the earlier signed quadratic support argument. Canonical PR3161/3162 geometry,
DreamingOfClouds/PR3154 at `708f0ad8928c383de8294aea3c126e9461d2066d`, joaqcoo
and the retained E8/P112 lineage keep their credit. Predecessors are unchanged.
Internal computational review is not human or proof-kernel approval.
Apache-2.0.
