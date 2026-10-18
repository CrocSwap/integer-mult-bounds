# Verification receipt

Local date: October 13, 2026. CPython **3.12.14** and **3.14.7** on macOS
26.3.1 arm64; standard library only. No hosted CI success or independent human
review is asserted.

From the repository root:

```sh
python3 -B research/universal-connector-boundary/verify.py
python3.12 -B scripts/research_package.py --package research/mutable-source-shear-cost
python3.12 -B scripts/verify_selected_result.py
git diff --check
```

All pass. The first command is the card's unchanged working control:
`PASS_UNIVERSAL_CONNECTOR_BOUNDARY pairings=945 max_coverage=31 queries=74 leaves=182`.
The registered replay runs the primary and separate checkers in isolated,
optimized mode, then six package test groups. Primary/separate direct checks
also pass under CPython 3.14.7. Registered replay validates catalogue/base Git
provenance and all three live source pins before executing the declared checks.

* Exact short source-word census: 8421 words, restored counts 1/0/20/0.
* Two source-word representations: row images and column bit images.
* Exact five-direction pairing census: 945 words, maximum coverage 31/32.
* Two coverage methods: direct prefix differences and integer Walsh
  autocorrelation, agreeing on every sorted record and digest.
* Complete candidate map: 40 formal arbitrary incoming rows, both root and
  five-factor-expanded words and their literal inverse words.
* Separate dense matrix oracle: 3456 executions at L=1,2,3,4, every basis
  input and eight mixed dirty states per width, candidate and PR1340.
* Invoice: 2016 map leaves + 4 complete row XORs + 648 internal nodes +
  76 root instructions = 2744 tariff units; PR1340 = 2760.
* Seven primary semantic controls, a dense omitted-restoration control at
  every width, and eight on-disk corruptions across six package test groups.
* Relocation with read-only input files/directories, optimized execution,
  deterministic byte-identical export, and occupied-output preservation.
* Selected-record integrity passes at kappa
  836330098538459/500000000000000000; its evidence was not altered.

Main and PR1340 were rechecked before submission: main remained
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`; PR1340 remained
`f1dcab36fa63f8226f70dd07e26f44afb9d39b51`. Exact base, blob and SHA256 pins
are in SOURCES.json and PREDECESSOR.json. No pending executable is imported.

The initial complete overlap snapshot covered 831 open PRs (including drafts)
and 76 Discussion body/comment/reply records. Before submission it was refreshed
at 2026-10-13T23:28:41Z, covering **837 open PRs and 87 Discussion records**,
with complete pagination and no warnings. It also searched 327 local README,
TASK and ledger records. The direct overlapping PR1340 is explicitly credited;
PR1318 concerns complex four-valued phases, and the local dyadic-query-run
package concerns a different word/contract. This search does not inspect all
code diffs or establish novelty. Full coverage metadata and exact match heads
are in TASK.json. The claim is Discussion1352. One automatic permission-review
timeout during refresh was resolved by a successful read-only retry.

The sharp generic source-XOR minimum concerns exactly ten B queries and two
readouts per nonzero mask, not specialized operators, other alphabets or a
weighted global optimum. The exact algebraic proof is in PROOF.md. No selected
cold replay, native supplier/compiler run, physical hosting/frame/precision/tape
admission, outer analytic transfer, proof assistant or full multiplication
verification was attempted; no supplier instance or new kappa is claimed.
