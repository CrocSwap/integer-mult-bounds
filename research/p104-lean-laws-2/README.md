# Lean-only release, part 2: kernel-only V2-FLOOR cover, native beta, structural laws and spec-break lemmas

Authors: DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. No κ claim. Everything here is a Lean statement with named hypotheses; Lean proves nothing about the inputs (extracted rows, data, the realisation-to-core reduction).
This is the second Lean-only package. It follows the first one (floors and bridge, PR #7632) and uses the same toolchain, Mathlib pin and module prefix.

## Summary (full statements and exact hypotheses in `PROVED.md`)
- **Kernel-only V2-FLOOR cover** (no `native_decide`): `V2Floor.v2floor_joint_kernel` (cost ≥ 987754236107 / 2^30 = 919.92, θ = 79793/2^20, 2,625 pairs) and `V2Floor.v2floor_beta_kernel` (cost ≥ 877.28, θ = 1, 1,822 pairs),
  by a hyperplane cover checked with `decide +kernel` in 536 generated files, plus the Gaussian count lemma (`V2Floor.gaussian_count`). It is a floor for the JB relay LP, numerically below the native-route values, and not a helper-D0 bound.
- **Native beta** (opt-in `NativeRoute`): `V2FloorNativeBeta.v2floor_beta_native`, 1,431.05, depends on `Lean.ofReduceBool`.
- **Structural laws** in the TokenCancel op model: Lemma TC and its timed/departure forms, charge certificate, stay-removability, whole-floor counting lemmas with the Port lemma and the Y-side theorem, free-endpoint collapse, spread identity, fusion obstruction.
- **Spec-break lemmas** over a field: Lemmas TS, UR, INV, SPLIT, COV, and the budget closures, scoped exactly as the audits state (see PROVED.md §4).
- `FALSE.md`: seven prose statements Lean refuted or tightened (with counterexample theorem names where one exists).

| file | content |
|---|---|
| PROVED.md | every theorem with its exact hypotheses and scope |
| FALSE.md | prose statements Lean refuted or tightened, with the proved fixes |
| CHECK.txt | compile table, axioms, and the full build log of the V2FloorKernel files |
| SCRUB.txt | privacy grep (expected empty) |
| SHIPPED.txt | files that the first package already contains (byte-identical; skip them if you overlay) |
| NOTICE.md, LICENSE | credit and Apache-2.0 |
| lean/ | Lean subproject; sources in `lean/Nov15/`, each new .md states one file's model and hypotheses |
| lean/native/ | separate, optional: `V2FloorNativeBeta` via `native_decide` (depends on `Lean.ofReduceBool`); kernel-only files never import it |

## Pins
- Toolchain `leanprover/lean4:v4.33.0-rc1` (`lean/lean-toolchain`).
- Mathlib commit `55b7917b472489c7c56a0fa6393af05cfd536599` (`rev` in `lean/lakefile.toml`; `lean/lake-manifest.json` pins every transitive package).

## Build
```
cd lean
lake exe cache get      # prebuilt Mathlib oleans for the pinned commit
lake build              # kernel-only library Nov15 (default target; about 620 modules, roughly an hour)
lake build NativeRoute  # optional: the native_decide route (uses Lean.ofReduceBool)
```
Module names keep the prefix `Nov15.` so the files are byte-identical to where they were checked. Peak memory per file is at most 3.5 GB (each generated check file is one slice; a kernel `decide` declaration is a separate kernel run).
The `lake` route was not run for CHECK.txt (it downloads Mathlib). CHECK.txt used `lean -o` file by file, in dependency order, with LEAN_PATH set to the pinned Mathlib packages plus an output directory; see its METHOD block for which files were recompiled in this round
and which results come from the earlier full build.

## Data files
`V2FloorKernelData_{j,b}` and the `V2FloorKernel{Base*,E_*,F_*}` slices are generated Lean (certificate rows, check chunks). Lean re-derives every row; the certificate file the rows came from is not trusted and is not shipped.

## Not included
All scripts and generators, the MidCert files, and the 84-middle-word steps (as in the first package). The numeric scans quoted in the notes (e.g. 30.8M census checks, 71,604 scanned states) are data outside Lean.
