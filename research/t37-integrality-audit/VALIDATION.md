# Verification and handoff

Validated locally on Windows with CPython 3.14.5. Both commands passed
normally and with optimized Python; no third-party library is required:

```sh
python -I -B research/t37-integrality-audit/verify.py
python -I -O -B research/t37-integrality-audit/verify.py
python -I -B research/t37-integrality-audit/independent_check.py
python -I -O -B research/t37-integrality-audit/independent_check.py
```

The primary checker reproduces the complete committed JSON receipt. The
separately written checker uses the other pinned rational engine, DP bin
enumeration, synchronous Bellman-Ford and direct moment differences. It
checks the same 37 witnesses and 1,591 edges, with ten additional rejection
controls. Its review found no substantive mathematical defect in the
primary argument. Both checks are AI-assisted; this is not human peer review.

Exact reported uniform penalty interval:

```
291373150447864129539126 / 10^24
    <= delta(2) <=
291373150447864129539127 / 10^24.
```

All 37 residue certificates have witness upper bound minus certified lower
bound at most **2/10^24** in this receipt (the checker permits at most
10/10^24). The T29 witness attains the exact symbolic uniform constant.

Only this additive research package is changed. Existing selected-supplier
replays and the repository-wide regenerating `make verify` suite were not
rerun: no supplier, generator, selected record or upstream source changed.
This package's two complete replays are the affected checks.

Immediately before packaging, Curiosity Bot refreshed PR metadata for T37
and integrality. PR942 was closed/incorporated; PR962 remained an independent
T37 construction; PR974 concerned interface budgets and bit-binding
headroom. Those are credited or distinguished in the claim. No overlapping
quantitative integer-residue certificate appeared in those queries. This is
a scoped overlap check, not a claim to have inspected every open PR.

The intended submission is one **research audit / scoped arithmetic result**,
with no new kappa and no request to change the selected frontier. Reviewers
can inspect the short slack-lattice proof, the T29 sharpness witness, and
the exact edge inequalities without rebuilding a physical supplier.
