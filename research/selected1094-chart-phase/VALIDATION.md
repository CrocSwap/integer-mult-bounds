# Validation record

2026-10-13, Linux x86-64, CPython 3.14.4 and system CPython 3.12.3.
Standard library only. All three registered commands pass under isolated,
optimized execution; the predecessor ASTs are explicitly compiled with
`optimize=0` so their assertions remain active.

```sh
/usr/bin/python3.12 scripts/research_package.py --package research/selected1094-chart-phase
python3 -I -O -B research/selected1094-chart-phase/verify.py
python3 -I -O -B research/selected1094-chart-phase/production_check.py
python3 -I -O -B research/selected1094-chart-phase/test_package.py
python3 -B scripts/verify_selected_result.py
```

The complete mathematical receipt agrees across versions:

```text
34f3fc87deac2e04323d140b490133f7ebe2788c66143c926b5e266126993269
```

The complete isolated production-predicate receipt also agrees:

```text
0f1fc10c00dfbedeebc2c96353c18bdc2a7fff9a40abbd789397e21b395bf1cb
```

A fresh minimal directory held the package and only its eight declared external
inputs, with every file and directory made read-only. All three commands passed
from an unrelated working directory on Python 3.14; all 20 files in that input
closure were unchanged. The mathematical receipt equals the complete committed
EXPECTED object. The final documentation-only validation note was added after
this replay. The registered Python 3.12 hook passes metadata validation, the
mathematical verifier, the source-predicate companion and all eight tests.

Evidence covers 69,120 helper roles, 10,002 complete charts, 53,300,658 Gram
entries, 10,008 chart/width signatures and 5,348,224 exact kernel coefficients.
The orthogonal census checks 23,817 matrices and 2,996,852 coefficient equations.
Six mathematical controls and two unmodified-source predicate controls reject.
The source C-only evaluator checks 512 full input columns. The eight package
tests include all columns/fibers of a small operator, inverse and square
identities, independent unpruned enumeration through dimension four, a valid
nonpermutation rebase, and actual optimized subprocess corruption tests.

All eight input pins and two provenance pins match the named Git objects and
SHA-256 digests. The selected-record check passes. No scientific input changes
between experimental base `49b3157d1d89adcef16df8be98445451672be5ba` and submission
base `dadfea6e8a78ff6ba901705f87532a71c6f5bbb8`.

Final overlap at 21:05 UTC covered all 844 open PRs through #1247, nine Discussion
threads plus their comments (16 records), and 324 local README/TASK/ledger
records. Remote pagination was complete, with no refresh warnings. Terms:
`orthogonal rebase`, `weight modulo`, `weight mod4`, `phase refinement`,
`spectator chart`, `chart phase`. The relevant PR702/712/1149/1209 heads stayed
unchanged. A historical PR407 entrance-frame match is a different construction.
This is bounded overlap evidence, not a novelty certificate.

The cross-environment checks caught two harness issues, both corrected before
submission. A disposable copied receipt now has its own writable mode before
mutation when the source package is read-only. Receipt fingerprints hash exact
extracted source segments instead of version-dependent `ast.dump` formatting;
the executed ASTs and source predicates are unchanged. A local executable named
`python3.12` resolved to Python 3.14 and was correctly rejected by the hook;
the successful 3.12 run used `/usr/bin/python3.12` explicitly. Initial failures
were not counted as passing checks.

The full supplier cold replay, historical global suites, other Clifford gate
types, local wrapper/native execution, invoice/precision/tape checks and a Lean
build were not run. The extracted source-predicate check inherits its supplied
context; it is not a complete admission-driver replay. Hosted PR CI is separate
and no hosted success is implied by these local results.
