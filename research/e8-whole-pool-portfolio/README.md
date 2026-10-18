# Whole-residual replica pooling and complete-program portfolios

This finite research artifact gives conditional **kappa = 0.001266541949425315**, exactly
`253308389885063/200000000000000000`, in the repository's retained multiplication framework.
It improves the whole-residual PR451 baseline `0.001265931727546219` by **0.04820338%**.
The complex supplier binds. This is not a claim to exceed PR453's larger posted number:
PR451's trace obstruction defeats the cross-family splitting derivation used for that number.

Two different construction changes are included:

1. **Pool whole residuals across all eight replicas.** Each helper stays in one physical
   array family. Global integer allocation removes per-replica fragmentation while respecting
   every physical axis and idle window. This improves both supplier inventories; the complex
   improvement raises the final kappa.
2. **Choose an entire equivalent implementation at each invocation.** Five reverse calls
   at stage 5, replicas 0 through 4, use rank147 instead of rank149. The extra residual coordinates
   and their storage are charged. This improves the bit supplier's reserve; it does not increase
   the final kappa further while the complex supplier binds.

Target-label mixing and two partial-prefix recoveries are also composed into the bit word.
Those are credited ports of prior techniques, not claimed as a third new mechanism.

## Reproduce offline

Requirements: Python 3.11 or newer, SymPy, a C++17 compiler, and Boost headers. No network,
SciPy, optimizer, Lean installation, or prebuilt native executable is required at replay.
On Linux/macOS set `CXX` if needed; on Windows use a g++/clang++ toolchain. If Boost is not in
its normal include path, set `BOOST_INCLUDE` to the directory containing `boost/`.
Do not use Python optimization (`-O`), because assertions are executable checks.

From this directory:

```sh
python -B verify.py /absolute/path/to/a-new-output-directory
```

The output directory must not already exist and must be outside this source directory.
The verifier checks `MANIFEST.json`, compiles the three native checkers, reconstructs both
complete local words, verifies changed columns/frames, emits both global schedules, rejects
adverse controls, and recomputes the rational moments and all 47 strict outer constraints.
`RESULT.json` and `RECEIPT.json` appear in that output directory only on success.

`EXPECTED.json` is the frozen exact invoice. `VALIDATION.json` and `REPLAY-MANIFEST.json`
record the fresh replay before documentation was added; the final manifest also covers
these documents. No executable or input used by that replay is changed afterward.

## Evidence and limits

The checks include both 980-column local programs, their eleven-stage orientation checks,
exact frame/prime witnesses, 74,720 columns of the heterogeneous unbanked controller,
65,120 whole bit helper occurrences, 49,280 whole complex helper occurrences, actual
family/axis collision checks, all 89-dimensional complex data-phase recipes, 19 bit
routing mutants and 10 complex routing mutants. Both moment engines and all 47 strict
assembly inequalities are used. The bit coefficient bound conservatively charges every
one of the 88 calls, not an unproved replica-independence shortcut.

This is **conditional finite evidence**, not an unconditional multiplication theorem,
Lean certificate, literature-wide novelty claim, or optimality certificate. Retained
all-size compiler, arbitrary-correlated dirty hosting, target-label, compressed-window,
restored-work, common-grid/tape, precision, and analytic interfaces remain explicit
assumptions. Source-bound inherited complex Clifford evidence is retained; we did not
rerun every unchanged upstream pipeline.

See `PROOF.md`, `RESEARCH.md`, `PROVENANCE.md`, and the detailed notes under `proofs/`.
