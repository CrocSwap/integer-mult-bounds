# Response-kernel entrance gauges: 132 paid helper-pair rewrites

**Conditional kappa: 71046520063283 / 100000000000000000 = 0.00071046520063283.**

Based on [PR249](https://github.com/CrocSwap/integer-mult-bounds/pull/249), pinned to `96495746c786d6d0339dbb38c7f553d4af3f88ed`. The baseline value is 0.000710392186446856. This is a new concrete helper basis change, not a sum of separately priced gains.

132 disjoint untouched helper pairs have equal complete target responses over F2 and compatible common entrance lines. Paid XOR basis changes and their inverses remove four old reads per pair, expose 132 new entrance gauges, and permit 220 fewer literal banks. All connectors, gates, charts, bank assignments and finite costs are charged. The actual pair cancellation is over F2; the odd-prime address field is separate.

## Reproduce

Requires Python 3.11+, SymPy 1.14.0, GNU g++ with C++17 and Boost headers. Linux: install `g++ libboost-dev`, then `python -m pip install -r requirements.txt`.

```
python verify.py --output ../cohort-replay
```

MinGW-w64 works on Windows. Specify `--cxx /path/to/g++` and, if needed, `--boost-include /path/to/boost-header-parent`. The output directory must be new and outside this package. Allow several minutes and a few GB of RAM. All mathematical checks added here are native C++; Python orchestrates them and runs the original upstream source emitter. No network, credentials, Lean or GPU is required.

Default verification checks every packaged hash, extracts pinned upstream sources, regenerates the baseline from source, compares the exact baseline transcript/states/frames and donor ownership, then compiles and runs seven native checkers. `--snapshots-only` explicitly skips upstream regeneration and checks the hash-pinned snapshots instead; its certificate records that weaker provenance mode.

The verifier rejects any changed native receipt field except elapsed time and runtime absolute paths. It also checks the exact new transcript hash. Expected receipts are comparison targets, never a substitute for execution. Generated native receipts may contain paths to your chosen output directory; they are not part of the upload package.

## Evidence

- 20,107 local F2 input columns forward/inverse, arbitrary independent dirt.
- Independent chronological frames, source/donor exclusion and COPY lifetimes.
- 232,320 independent pair/target prefix comparisons.
- 132 exact new projector charts and all 3,317,400 role/replica/stage assignments.
- All 23,627 five-stage global F2 columns and nonvacuous negative controls.
- Complete counted finite invoice: selector bill 626938189600; payload 95 bits below 104-bit guard.
- Exact rational recurrence pricing, all 47 strict outer inequalities, baseline regression, adjacent-grid rejection controls.

See PROOF.md, BANK-PROOF.md, FINITE-PROOF.md and REVIEW.md. Paths such as lead/ and temporal/ in proof notes refer to replay outputs. The component pricing receipt flags bank/finite obligations as outside *that checker*; the top verifier separately checks and composes the bank and finite receipts.

## Scope

Retains the public all-size compiler, common weighted chart, restored-row, routing, prime, precision/recovery and analytic interfaces. Their general theorems are not independently reproved here. The public eight-stage Python command is not claimed to have been replayed verbatim on the modified word: this package uses independently implemented native checks. No unconditional multiplication bound, practical speed benchmark, or Lean certification is claimed. No claim of the latest leaderboard record is made.

The upstream source archive, explicit pins and original notices are included for offline reproducibility. No binaries or machine-specific configuration are included.
