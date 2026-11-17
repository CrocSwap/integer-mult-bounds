# P104 Lean-only floors package (class-K floor, JB bridge, Lemma PG, R25 kill)

No kappa claim. Everything here is a Lean statement with named hypotheses; Lean proves nothing about the inputs (extracted rows, data, the realisation-to-core reduction).

## Summary of what is proved (full statements and exact hypotheses in `PROVED.md`)
- **Unconditional floor (class K only):** every class-K word has helper D0 >= 780 * 2 ln 2 >= 1,081.31 per call (`FloorD0.floor_D0_classK`; sole extra hypothesis H2, the extraction of the exported rows). It bounds the helper layer of class-K words only.
- **Conditional JB bounds:** the relaxed relay model gives 1,713.38 (joint) and 1,431.05 (beta) in JB units, and bounds helper D0 only through `V2Bridge`, with `hreal` and the born-at-0/end-at-V conditions (or the stated correction terms). The joint `IntFeasible` discharge uses `native_decide` and lives in the opt-in `NativeRoute` library.
- **Lemma PG** (`LemmaPG.lemmaPG`): rank bounds against I, T+, T- force X^2 = I when 2 != 0; `char_two_counterexample` shows 2 != 0 is needed.
- **R25 kill** (`R25Kill.kill_outer`): the 546 outer words die in the pinned d = 2 core model; the 84 middle words and the reduction to the core are not covered.
- Rebuild laws (rank law, hub settle, gauge, swap word) and support lemmas; 11 refuted prose statements plus the bridge counterexamples are in `FALSE.md`.

## Release notes
Authors: DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. No κ claim.

| file | content |
|---|---|
| PROVED.md | every theorem with its exact hypotheses and scope |
| FALSE.md | prose statements Lean refuted, with the proved fixes |
| CHECK.txt | compile log of every staged .lean file, with axioms |
| NOTICE.md, LICENSE | credit and Apache-2.0 |
| lean/ | Lean subproject; sources in `lean/Nov15/`, each .md states one file's model and hypotheses |
| lean/native/ | separate, optional: V2-FLOOR via `native_decide`. Depends on `Lean.ofReduceBool`. Kernel-only files never import it. |

## Pins
- Toolchain `leanprover/lean4:v4.33.0-rc1` (`lean/lean-toolchain`).
- Mathlib commit `55b7917b472489c7c56a0fa6393af05cfd536599` (`rev` in `lean/lakefile.toml`; `lean/lake-manifest.json` pins every transitive package).

## Build
```
cd lean
lake exe cache get      # prebuilt Mathlib oleans for the pinned commit
lake build              # kernel-only library Nov15 (default target)
lake build NativeRoute  # optional: the native_decide route (uses Lean.ofReduceBool)
```
Module names keep the prefix `Nov15.` so the files are byte-identical to where they were checked. Peak memory per file is at most 3.5 GB
(the V2FloorChk_* slices are split for that reason; the kernel `decide` checks run about 1 minute each).
The `lake` route was not run for CHECK.txt (it downloads Mathlib). CHECK.txt used `lean -o` file by file, in dependency order, with LEAN_PATH
set to the pinned Mathlib packages plus a fresh output directory.

## Data files
`FloorCertData`, `NativeFeasData`, `V2FloorData`, `V2FloorCost` and the `V2FloorChk_*` slices are generated Lean data (certificate rows, native point, pair lists).
Row and column names of the floor LP: `lean/Nov15/floorcert_index.txt`. Lean proves statements about this data; the extraction of it from a word is an input (hypothesis H2).

## Not included
MidCert*, DetLaw, TS, the 84-middle-word hand steps (MiddleWord), and all scripts.

## Open next questions
- Kernel-only discharge of `IntFeasible` (hyperplane cover, `decide +kernel`) to remove `native_decide` from the JB bounds; the beta native file is not compiled in CHECK.txt.
- The 84 middle words of the R25 kill, and the reduction of a general realisation to the pinned core.
- A statement of hypothesis `hreal` that follows from a checkable property of a word rather than from the r7-taint extraction.
