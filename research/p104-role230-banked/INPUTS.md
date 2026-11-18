# Exact source capsule and replay checks

`peer/` contains the original scientific dependencies of #7674 at `26b6c469aa6c4aa04322ce25a22150f90e5fb14e`. The refreshed head `28b2af322a1fab01b3734365988930920f9dda48` authenticates those same blobs. `peer/source/` carries the one original K372 gzip, the exact source edit and actual caller gzip. `peer/PIVOTS.json` is the only executable pivot list. [Manifest](ASSETS.json) · [Peer source pins](peer/SOURCE-PINS.json)

`data/CONTACTS.json` carries the source-anchored role-230 replacements. Both banked graphs are rebuilt in scratch and checked by their decoded canonical hashes and compressed transport hashes. The retained [wire result](evidence/WIRE-RESULT.json) identifies every completed saved-signal check, the exact output digests and the deterministic control results. No second copy of the scientific graph source is needed for the native stage.

The frozen phase producer/checker and the directed price evaluator and its helper live in `engines/frozen/`. Where a subprocess imports an original #7674 module, it uses those exact local bytes and the vendored peer path. `SOURCES.json` is for upstream Git provenance. `ASSETS.json` authenticates transitive proof inputs inside an unpacked source capsule. Output artifacts and caches are placed in scratch. The source, comparator pivot set and literal caller have independent pins.

| Executed scope | Required replay and controls | Observed resource use |
|---|---|---:|
| Exact wire graph | Prove all fifteen saved signals, both full exact wire directions and the actual dependency closure. Reject a same-price wrong scalar, nonlocal donor and cocharted cycle. | 40.80 s wall, 318,652 KiB |
| Actual paired 16-call application | Complete signed bills, directed prices, outer predicates, exact paired grid and normalized bank dispatcher. Reject an extra paid rank-one fee. | 25.47 s wall, 238,228 KiB |
| Independent stored graph cost audit | Recount exact matched source/caller pre-products, positive private extent, complete copies, staging, phase and `q` movement budgets. | 3.85 s CPU, 117,652 KiB |
| Independent rational price | Recheck both crossing brackets, negative interval derivative, the improvement at the baseline upper, and a single-fee sign reversal. | 0.53 s wall |
| Native phases and dense tapes | Fresh signed Pauli and phase comparison on all 3,030 ordered pairs, 19 complete forward and adjoint literal column pairs, 104 main boundaries and two full held-array runs. Both actual first-prime fault variants alter 53 distinct public roles each. The second prime uses the unmodified paired graph. | 145.13 s CPU combined, 612,540 KiB peak |

`paired` runs the exact graph, caller, complete resource and independent price scopes within 280 seconds. `native` rematerializes the identical graph hashes and executes the full native checks within 400 seconds. The measured materialization cost is 18.92 seconds wall. The two registered commands allocate 680 seconds total and at most 2 GiB address space per command. They use Linux CPython 3.12 and the standard library, write to fresh isolated scratch, check all local assets before and after each replay, and read back both exact scientific graph hashes. [VERIFY.json](VERIFY.json)

```sh
python3.12 -I -B verify.py integrity
python3.12 -I -B verify.py paired --out /path/to/new-paired-directory
python3.12 -I -B verify.py native --out /path/to/new-native-directory
```

Omit `--out` to use temporary cleanup. In the repository run `python3.12 -B scripts/research_package.py --package research/p104-role230-banked`. The upstream source provenance check uses the task catalogue and selected record at pinned canonical main. The standalone checks use the archived package-relative files.

The release branch carries ToikY's unchanged CI bridge at `0eabc624a9bc9ed2847719efd63390db4d297df4` as repository workflow context. The banked package has its own registered scopes and targets the two exact #7674 graph hashes above.
