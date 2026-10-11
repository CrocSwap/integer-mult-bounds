# Multi-cut response-kernel condensation

**Conditional kappa = 142205877210807 / 200000000000000000 = 0.000711029386054035.**

This builds on pinned PR249 (`96495746c786d6d0339dbb38c7f553d4af3f88ed`) and extends the earlier 132-pair kernel construction. It raises the previous delivered 0.00071046520063283 by approximately 0.0794%. This is a modest checked exponent gain, not a claim of a huge jump or the latest leaderboard record.

The new mechanism selects simultaneous zero-response helper directions, shares donor lifts, repairs singular common frames with explicit nondegenerate subframes, and places compatible basis changes at four actual cuts. The result has 518 pivot entrances, removes 1344 raw rank units and 27772 initial reads, and pays every added basis gate and inverse. Complete bank stock is 867175.

## Reproduce

Requires Python 3.11+, SymPy 1.14.0, GNU g++ with C++17 and Boost headers. Install `g++ libboost-dev` on Linux, then:

```
python -m pip install -r requirements.txt
python verify.py --output ../multicut-replay
```

MinGW-w64 is supported on Windows. Use `--cxx /path/to/g++` and optionally `--boost-include /path/to/boost-header-parent`. The output directory must be new and outside the package. Allow several minutes and a few GB of RAM. No network, credentials, Lean or GPU is required. New mathematical computation is C++; Python orchestrates it and runs the original upstream emitter.

The default verifier checks hashes, regenerates pinned upstream data, compiles seven native checkers, emits the new word from the frozen candidate selection, and rechecks its complete semantics, geometry, bank assignment, finite invoice and exact exponent. It requires all 20107 local input columns in both directions, 23627 five-stage global columns, 911680 per-cut kernel equalities, all 3317400 bank assignments, exact chart identities, nonvacuous controls and all 47 strict outer inequalities. The bank label and mathematical receipts must match exactly; only elapsed time and runtime paths are excluded from comparisons.

`--snapshots-only` explicitly skips upstream source regeneration and records that weaker provenance mode in its certificate. It still executes all seven native checkers. Discovery scans are not rerun: inputs/candidates.json.gz is the complete frozen final witness, including actual cut positions.

## Scope and source handling

Retains the public all-size compiler, common weighted chart, restored-row, routing, prime, precision/recovery, complex symbolic correctness and analytic interfaces. These foundations are not independently reproved. The actual cancellation is over F2 payload; odd-prime address geometry is separate. This is not an unconditional multiplication theorem, practical benchmark or Lean certificate. The public eight-stage Python command is not claimed to be replayed verbatim on the modified word.

See PROOF.md, KERNEL-PROOF.md, BANK-PROOF.md, COPY-PROOF.md, FINITE-PROOF.md and REVIEW.md. Paths under lead/ or banks/ in research-derived proof notes identify the original evidence roles; the executable package uses code/, inputs/ and expected/. Native output logs can contain your chosen output path; they are not upload files.

Original public sources, licenses and attributions are preserved in vendor/. No personal byline, binaries or local machine configuration is included.
