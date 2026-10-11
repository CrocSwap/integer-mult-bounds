# Conditional κ = 0.001332077359286333

This finite construction combines the pinned PR493 R489 bit word with a new
whole-owner placement of PR484's gauge/kernel complex word. Pooling idle
families across the eight physical replicas removes all 66 complex bank
families. Every helper residual still occupies one complete physical family,
and each local invocation has 800 distinct owners.

The exact complex saving is
`b = 1333854156208409156010/10^24`; the bit saving is
`c = 391360506745414227149/250000000000000000000000`.
The resulting bound is
`κ = 1332077359286333/10^18 = 0.001332077359286333`.
It improves the whole-owner PR493 + PR484 pairing by about 0.532%.
The larger draft PR494 number uses the disputed cross-family split of PR448
and is not a comparison within this package's whole-owner scope.

Run from the committed repository package:

```sh
python3 -B research/r489-pooled-whole-complex/verify.py /absolute/fresh/output \
  --boost-include /path/to/boost/headers
```

Requirements: Python 3.11+, NumPy, SymPy, Bash, a C++17 compiler and genuine
Boost headers (`boost/multiprecision/cpp_int.hpp`). The release replays use
Python 3.14. Search additionally used SciPy, but verification performs no
optimization and needs no network.

The verifier reconstructs both pinned suppliers in full, rebuilds the new
serialized owner map, audits both reflected local programs and arbitrary dirty
restoration, checks all actual whole-family matrices and spectators, checks
complete idle remainders and mutation controls, and independently recomputes
the complete paid profiles, finite invoices, six bootstrap cutoffs and all 47
strict inequalities. Guarded exact simulations bound expanding integer
operations before they execute. Source files are checked before and after the
run; each subprocess exit is recorded. `EXACT-MATH.json` contains reproducible
mathematical results; runtime-dependent source/template hashes are bound
separately in each run's receipts.

`PROOF.md` gives the placement and serial execution argument.
`SOURCE.json` pins all 266 original supplier files. `MANIFEST.json` binds this
entire package. `EXPECTED.json` fixes the exact result. `NOTICE.md` preserves
provenance and AI disclosures. The original bit/complex packages and previously
published PRs are unchanged.

This remains conditional on the inherited all-size compiler, mutable-basis and
common-label interfaces, PR484's Lemma A realization, restored-row,
precision/tape and analytic-transfer contracts. It is a finite construction
with exact checks, not an unconditional multiplication theorem or Lean proof.
