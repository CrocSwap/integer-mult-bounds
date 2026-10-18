# Eight smaller endpoints on the k8 circuit

The frozen conditional value is **κ = 0.001673414377866467**, a **0.072845%** increase over 0.001672196274581061.

This package composes four rank-seven helper endpoint pairs with the R480 k8 + seven-slot supplier, then repacks its whole helpers. See `CLAIM.json` for the frozen conditional κ and comparison, `PROOF.md` for the argument, and `evidence/RESULT.json` for strict verification. This is an incremental construction improvement, not a large new-geometry breakthrough.

The change is 42 B-frame annotations, eight early-cleanup frames, and eight helper endpoints. Scalar instructions and their order are unchanged. The local helper-width sum falls from 3730 to 3722. All 704 exact scalar columns, both orientations, 2904 directed phase edges, 32 endpoint mutation controls, and the inherited global admission checks are verified.

PR1030 supplied the first endpoint-pair lead. We transported that pair to the current k8 circuit, screened all 16 groups with smaller forced endpoint spaces, and combined four favorable groups. The discovery also checked seven immediate source aliases and 6497 algebraically permissible source-read placements; none fitted the tested frame constraints. These negative results are limited to those searches.

The new construction changes the old fixed-profile/fixed-width packing family. The previous packing ceiling therefore does not cover it. Discovery LP values are relaxed search estimates; only the frozen, strictly admitted value in `CLAIM.json` is an achieved result.

## Reproduce

Use Python 3.11+ and the upstream native phase backend dependencies, including a C++ compiler and Boost headers. Set `CPLUS_INCLUDE_PATH` to your Boost include directory if needed. No optimization solver is required for verification.

`BASE` is the final raw k8 + seven-slot `FULL-WORD.json.gz` produced by the documented `research/k8-coordinated-owners/verify.py` rebuild. Its decompressed hash is pinned in `RECIPE.json`.

```sh
python -B research/k8-eight-ends/verify.py \
  --base "$BASE" \
  --work /tmp/k8-eight-ends-fresh
```

The output directory must not exist. To reuse an explicitly supplied completed native replay, add `--native-from /path/to/completed/native`. The verifier checks all five native step receipts and the complete proof-relevant artifact identities, then reruns exact local and global admission. It does not trust a saved status string alone.

The verifier copies upstream admission code without edits. Frozen `PLAN.json.gz` (expanded verbatim for admission), `OWNERS.json.gz`, and `SPEC.json` remain fixed during verification. `SOURCE-PINS.json` authenticates the source dependencies and `MANIFEST.json` authenticates this package.

## Research record

`discovery/END-GROUP-SCREEN.json` and `END-COMBINATIONS.json` record finite endpoint refits and floating-point packing relaxations. `SEARCH.json` records the completed owner searches, and their full traces are retained in compressed form. A feasible optimizer incumbent is a nomination, never an admission result or an optimality proof.

The exploratory scripts require NumPy/SciPy and `K8_BASE_WORD` set to the pinned baseline raw word. They retain their source census and relaxed endpoint search separately from the verifier. They are not needed to reproduce the frozen witness.

See `NOTICE.md` for upstream credit. All inherited conditional assumptions remain in force.
