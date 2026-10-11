# Conditional κ = 0.001343518018117309

This finite construction combines the pinned PR493 R489 bit word with a
frame-only retiming of PR484's gauge/kernel complex word and PR496's pooled
whole-owner placement. The 4,107 scalar gates keep their payloads and order;
411 A frames and 504 B frames change. Fixed entrances, centres, boundaries
and cleanup remain exact. Every helper residual occupies one physical family,
each invocation has 800 distinct owners, and no bank families are needed.

The exact complex saving is
`b = 1345325487149526878087/10^24`; the bit saving is
`c = 391360506745414227149/250000000000000000000000`.
The resulting bound is
`κ = 1343518018117309/10^18 = 0.001343518018117309`.
It improves the frozen whole-owner PR496 result by about 0.859%.
The larger draft PR494 number uses the disputed cross-family split of PR448
and is not a comparison within this package's whole-owner scope.

Run from the committed repository package:

```sh
python3 -B research/r489-pooled-retimed-complex/verify.py /absolute/fresh/output \
  --boost-include /path/to/boost/headers
```

Requirements: Python 3.14, NumPy, SymPy, Bash, a C++17 compiler and genuine
Boost headers (`boost/multiprecision/cpp_int.hpp`). The release replays use
Python 3.14; inherited source receipts compare gzip byte hashes, so other
Python minor versions are not covered by this release. Search additionally used SciPy, but verification performs no
optimization and needs no network.

The verifier reconstructs both pinned suppliers in full, applies the frozen
retiming map to the fresh word, rebuilds all changed scalar programs and exact
Gaussian recipes with the unchanged upstream tools, then rebuilds the
serialized owner map, audits both reflected local programs and arbitrary dirty
restoration, checks all actual whole-family matrices and spectators, checks
complete idle remainders and mutation controls, and independently recomputes
the complete paid profiles, finite invoices, six bootstrap cutoffs and all 47
strict inequalities. Guarded exact simulations bound expanding integer
operations before they execute. Source files are checked before and after the
run; each subprocess exit is recorded. `EXACT-MATH.json` contains reproducible
mathematical results; runtime-dependent source/template hashes are bound
separately in each run's receipts.

`PROOF.md` gives the retiming, placement and serial execution argument.
The independent frame reviewer checks both 25,082-event ledgers, all fixed
scalar payloads, raw-to-canonical orthogonality and 12 targeted rejection
controls. Fresh source mutation suites and all 14 Lemma G necessity controls also run.
A derivative adapter nominates an available nonnested frame for control M8;
its two transition ranks are recomputed, preserving the same total charge.
All other source mutation code and the pinned source files stay unchanged.
`SOURCE.json` pins all 266 original supplier files. `MANIFEST.json` binds this
entire package. `EXPECTED.json` fixes the exact result. `NOTICE.md` preserves
provenance and AI disclosures. The original bit/complex packages and previously
published PRs are unchanged.

This remains conditional on the inherited all-size compiler, mutable-basis and
common-label interfaces, PR484's Lemma A realization, restored-row,
precision/tape and analytic-transfer contracts. It is a finite construction
with exact checks, not an unconditional multiplication theorem or Lean proof.
