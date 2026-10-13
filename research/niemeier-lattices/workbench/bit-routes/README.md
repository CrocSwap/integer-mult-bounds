# Bit routes and spinor continuation

These finite experiments investigate Niemeier and D16 spinor suppliers. They include exact kernel ranks, scoped implementation obstructions, and unsuccessful bounded searches. They do **not** certify an improved κ.

From `research/niemeier-lattices`, with NumPy and SymPy installed:

```sh
python3 workbench/bit-routes/verify_portable.py
python3 -I -O workbench/bit-routes/verify_portable.py
```

The verifier copies the package into a temporary directory, regenerates the E8² and D16 coordinate arrays, runs 18 generators, and compares 19 saved receipts. JSON comparisons exclude only the historical `seconds` timing field in `MOD4-RANK.json`; the factor NPZ is compared by array contents. Saved checkout receipts are never regeneration targets.

The same verifier covers this directory and `../continuation/section-search` and `../continuation/spinor-routes`. A top-level verifier can reuse its own isolated copy with `replay(isolated_package, frozen_package, optimized=True)`.

[REPLAY.txt](REPLAY.txt) gives the dependency and result scopes. In particular, `NEIGHBOR-CUBICS.json` preserves an early sampled lower bound; its mixed rank 678 is superseded by the final exact rank 679 in `CUBIC-RELATIONS.json`. The small clique searches retain their bounded scope. [The spinor proofs](../continuation/spinor-routes/PROOF.txt) concern specified implementations, not all possible factorizations or circuits.

Direct execution of an individual generator is a regeneration operation that writes beside the script. Use a copy for those commands. `PR589.json` is a historical context snapshot, not a regenerated mathematical receipt.

Both commands passed on 2026-10-12 with Python 3.14.8, NumPy 2.5.4, and SymPy 1.14.0. The normal run took approximately 83 seconds of generator time; the `-I -O` run reported 83.47 seconds including the temporary copy and comparisons. Runtime depends on the machine.
