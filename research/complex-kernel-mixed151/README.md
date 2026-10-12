# Paid complex kernel plus rank151 target-mixed bit supplier

Conditional kappa = 0.001274415506145115, 0.03005550944143967% above PR458.
This is a composition of unchanged PR458 complex and PR459 bit suppliers.

Submitted as a draft after exact composition checks and before full replay.
The pinned-report screen is not evidence of a fresh full supplier verification.

Reproduce from the repository root, choosing a fresh output outside research:

```sh
python -m pip install -r research/e8-r740-replica32/parent436/requirements.txt
python -B research/complex-kernel-mixed151/verify.py /absolute/new/output
```

The default runs both full upstream wrappers, then recomputes both exact
moments, six bootstrap steps and all47 strict outer inequalities and controls.
Requires Python3.11+, a C++17 compiler and Boost headers, plus pinned Python
dependencies. GitHub CI is separate from local verification.

For a numerical screen only:

```sh
python -B research/complex-kernel-mixed151/assemble.py /absolute/screen.json
```

The package includes the external shell path adapter used and verified for
PR456. It adjusts shell argument splitting for the old PR436 wrapper on paths
containing spaces without editing any pinned upstream source. Read PROOF.md
for scope and SOURCE.json / NOTICE.md for the exact provenance.

## Parent reconstruction metadata portability

The first full Python3.11 run passed the entire PR454 chain but PR458 stopped
at its absolute1e-12 comparison of two inherited floating-point discovery
estimates. The gain estimate differed by2.09e-12. These are explicitly
non-proof metadata in the pinned rebuild source. The external parent runner
normalizes only those two fields in a generated copy supplied to that rebuild;
all other JSON fields are checked unchanged, all pinned source files stay
unchanged, and the original exact reconstructed-word equality remains active.
A separate receipt retains both values, the source hashes and normalization
scope. The combined receipt binds it. No exact arithmetic check is relaxed.
