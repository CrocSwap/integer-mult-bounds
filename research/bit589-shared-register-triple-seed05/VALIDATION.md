# Validation record

- Exact repository base: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
- Selected supplier: merged PR589 head `a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`;
  tuned word `v=111`, `R=439`, decoder constant 63.
- Transport/scoring source: open PR1345 head
  `b54a856aa79857d91cd5d65f8f7144e26c8c084f`, vendored bytes pinned in
  `SOURCES.json`.
- Local interpreter: CPython 3.14.7; the verifier uses only the standard
  library and is run without `-O` so upstream replay assertions remain active.

Command from the repository root:

```sh
python3 -I -B research/bit589-shared-register-triple-seed05/verify.py
```

Expected result:

```text
PASS_PR589_A_TRIPLE_TRANSPORT seed=5 ops=927,928,930 assignments=210 valid=164 ties=100 losses=64 incompatible=46 controls=3 no_new_kappa
```

The replay checks all 210 tuples in the fixed Cartesian product of three
individually legal PR1345 single-move option lists; all 164 tuples that pass
the chain-nesting scorer are replayed against the full 661-register map.
It does not certify all jointly enabled frames or alternative commutations. It also rechecks the
three controls named in the README and compares the entire generated result to
`RESULT.json`. Repository diff whitespace validation is `git diff --check`.
