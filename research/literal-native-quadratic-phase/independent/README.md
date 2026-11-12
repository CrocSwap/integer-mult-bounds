# Independent review and replay

The lead independently wrote dense_check.py. It executes the exported graph
without the author CPU or packet oracle, and derives the current phase from
f-popcount(a0^a1^a2^a3^a5^a6)+2*popcount(a7) modulo4. Its source is copied
unchanged; SHA256 163b9042622825c3d97153508336fc4fd285ac0bd01910186ee6eafb7d9e777a.

The lead ran normal and optimized modes; receipts agree. The package-local
copy was additionally run once and matched the committed result exactly.
From the repository root:

```sh
python3 -I -W error -B research/literal-native-quadratic-phase/independent/dense_check.py research/literal-native-quadratic-phase/phase.py
python3 -I -W error -O -B research/literal-native-quadratic-phase/independent/dense_check.py research/literal-native-quadratic-phase/phase.py
```

Result: 16 cases, 7 accepts, 11,776 coefficients in complete fixture inputs,
6,428,358 transitions and three detected program mutations. The f=2,3,4
cases each deliberately supply only 300 coefficients: they validate staged
prefix arithmetic and public preservation on rejection, not full tensor
execution. Successful longer-to-shorter reuse preserves the physical dense
tape arrays and restores their heads/private cells.

native-phase-source-bindings.json records independent authentication of all
eight exact Git commit:path source bindings, including the published outer
phase predecessor. This authenticates source bytes, not mathematical scope.

The complementary peer accepts the universal phase/geometry, complete cost,
retirement and historical-storage theorem. Its unchanged files are under
peer/. It independently interprets the graph, derives exact head-movement
counts and detects a functionally correct but more expensive full-width
rewind. Program and final proof hashes are pinned in peer/REVIEW.md.
The package-local checker also passed after relocation:

```sh
python3 -I -W error -B research/literal-native-quadratic-phase/independent/peer/check.py research/literal-native-quadratic-phase
```
Independent AI review is not human or formal-kernel acceptance.
