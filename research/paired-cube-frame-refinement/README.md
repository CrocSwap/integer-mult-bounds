# Fixed frame refinement above PR168

Conditional bound: `kappa = 13118356069/20000000000000 = 0.00065591780345`.
This is a small 0.0043305% improvement over PR168 at
`4a3c769e5c5430e7114c4d3e099ff34664677f17` (0.0006558894), and about
1.075% above PR176 at `96dc228f426252c969c99d3c4c1eb97cc44b7184`.
No global optimum is claimed.

The only physical change is 64 operation frames in the frozen PR168 complex
word. The DAG, coefficients, 2,310 compensated reuse pairs, 47 terminal sinks,
bit supplier, scalar-work guard, full orthogonal-group cardinality, router
charge and row reserves are retained. Complex saving is
`13126968687/20000000000000 = 0.00065634843435`.
There are 11,015 physical auxiliary roles and 13,655 persistent roles; the
rank deficit remains 1,320 and the largest child remains 20.

Run the read-only selected gate with Python 3.11 or later:

```
python3 -B research/paired-cube-frame-refinement/verify.py
```

The gate regenerates the pinned source DAG and word, checks the unchanged
PR168 complete supplier/assembly, runs its physical and terminal-sink gates
on the new frames, and compares the resulting complete histogram with the
independent PR176 terminal checker. PR176's unchanged packed-column executor
checks every source, target and dirty column under both signs. Ten inherited
physical/sink/formal corruption controls remain enabled. The exact retained
assembly checks all 47 strict inequalities and seven margins. The adjacent
10^-14 complex point fails the same conservative rational moment enclosure;
this concerns that fixed enclosure and parameter choice only.

Validation status: full repository `make -j1 verify` and the packaged verifier
passed on frozen research commit `2c4a380126640abfcdce398ced255d1dd5d1d007`
on 2026-10-09, in 3340.2324075698853 seconds. The run completed 79 isolated
test modules, 20 patch checks and the package's ten corruption controls, with
no source drift. All 48 research-head GitHub CI checks passed. See
validation.json for the source-bound receipt and evidence hashes. Finite
verification does not establish the inherited all-size interfaces. See PROOF.md
and NOTICE.
