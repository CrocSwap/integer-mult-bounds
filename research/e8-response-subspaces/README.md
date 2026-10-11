# Synthesized response subspaces and two-sided dirty-bank normalization

**Conditional exponent saving: kappa = 101331088745971 / 100000000000000000 = 0.001013310887459710.**

The frozen comparison is PR399 at `b974e481efd2f771cda2dcdd71c91f133793558f`, claiming 0.001002661106042177. This construction improves that value by approximately **1.06215%**. The source sweep is frozen through PR399; no claim is made against later submissions.

The changed complex supplier synthesizes 26 entrance subspaces of dimensions 1, 2, 4 and 5, eliminates 119 helper response columns with 240 exact entrance shears, and packs the resulting mixed residual ranks into 748 banks per stage. Unlike the earlier odd rank-one orthogonal-complement route, an explicit two-sided Clifford normalization handles even and degenerate entrance spaces as well. Both boundary adapters are emitted and charged. The bit supplier is unchanged and remains above the complex bound.

This is a **finite conditional construction**, not an unconditional multiplication theorem or a Lean certificate. The inherited all-size compressed-window, arbitrary-correlated dirty-bank, recursive compiler, precision, fixed-tape/restored-row and analytic interfaces remain assumptions. See `PROOF.md`, `frames/PROOF.md`, and the bundled outer proof.

## Reproduce offline

Use Python 3.11 or later and a GCC/Clang C++17 compiler. The default changed-composition replay uses Python standard-library modules; bundled dependencies and Boost headers are required only for the optional unchanged bit replay. From any directory:

```sh
python -B verify.py /absolute/path/to/a-new-output-directory
```

Set `CXX` when required. Use `--replay-bit` and, if needed, `BOOST_INCLUDE` to freshly replay the unchanged bit component; the default checks its source-bound prior receipt. The output directory must be new and outside the package. Do not run Python with `-O`. Source dependencies are bundled; there is no network access or discovery search in the replay.

The runner reconstructs the exact candidate, checks all dirty columns and both local orientations, checks every new/reflected Clifford edge and all 13,312 residual address columns, emits and independently decodes the new bank template and cost invoice, then checks the exact moments and 47 outer inequalities. Unchanged local phase receipts are source-bound and expressly reused. This is verification of the changed composition, not a replay of other public PR pipelines.

`RESULT.json` in the output directory is the final replay receipt. The package manifest covers every uploaded file. Research notes retain bounded searches and sufficient identities that contribute no additional priced gain.
