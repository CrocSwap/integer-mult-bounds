# Integrated validation

Base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
The enlargement pins the published root snapshot
`976c169857b2ba212dff06349058351a3557b3e7` by exact source SHA256s.
Environment: CPython 3.12, standard library only.

Executed:

```
python3 -B scripts/research_package.py --package research/p104-uncovered-pivot-root
```

All eight registered commands passed and the runner ended with
`PASS_REGISTERED_RESEARCH_PACKAGE`. These are the two base checkers normally
and with optimized Python, the full 90-case enlargement checker, and the three
independent geometry/price/derivative checks. Timeouts sum to 1,200 seconds;
none required an extension or dependency install.

The enlargement checker also passed with `-I -O -B` in a separate copy.
Normal and optimized receipts are byte-identical, SHA256
`2a816a92bc5ecb9e58b395a95fe078b6775fef619572efe764fa80da2bda8eee`.
The final enlargement verifier SHA256 is
`33ca1a98714b28ee8c2a01853000a9319405056d9bf058a55ce5578985955f34`.
The independent geometry reviewer separately passed normal/optimized modes;
its portable path adaptation passed in the registered integrated replay.

Evidence checked:

- 110 roots, 220 literal polynomial operator identities and 3,300 transport
  nullspaces, with seven retained-source hashes and five rejection controls.
- Independent minimal-mask accounting: 4,298 top-k identities, 840 independently
  coded transport systems, four source hashes, complete signed histograms and
  exact rational crossing/derivative signs.
- All 90 enlarged masks: 1,620 prefix/projector commutations and 1,986,278
  positive-capacity relaxed job supports, every committed integer-price
  inequality, and every complete margin/derivative bound.
- Independent direct-nullspace review: all 1,048,572 nonempty subsets across
  four cases, including the weakest certificate and the largest enlargement;
  separately inverted prefixes and a positive-exponential interval engine.
- Independent all-90 price review: every target/native/thin invoice and integer
  objective, plus all 23,592,870 possible subset tariff inequalities.
- Independent all-90 no-reentry bounds through kappa=.01.

The maximal enlarged-mask margin upper bound is
`-0.210890121535325573`, at (7,8); the maximal uniform derivative upper bound
on [0,.01] is `-166817.003849584388739881`.

The team lead independently reviewed the root endpoint, arbitrary-D stage
factorization, carrier proof, cover majorization, and exact row-space cache.
Separate workers audited the enlargement geometry and prices. Their scoped
reviews and replay receipts are under `enlargement/independent/`.

These are exact finite checks and proof reviews, not formal proof-kernel
verification, a native-word replay, compiler admission, or a new kappa.
