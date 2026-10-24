# Reproducing the optional Lean appendix

The exact dependency snapshot in sources/ contains nine existing MathProof modules (148,970 bytes); it is publication provenance and is not a second active DAG or live project source.

Use Lean 4.33.0 and Mathlib commit db584cd6d46c92f209a44c0f1c829460d327499d. This differs from later integer-multiplication bootstraps using Lean 4.34.1: do not silently combine those environments.

In an isolated directory, make a Lake project with:

~~~lean
import Lake
open Lake DSL
package wordRamTransfer

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @
  "db584cd6d46c92f209a44c0f1c829460d327499d"

lean_lib Mathproof
~~~

Set lean-toolchain to leanprover/lean4:v4.33.0. Copy sources/Mathproof to the isolated project's Mathproof directory. Place the unchanged WordRAMLogWidthTransfer20261022.lean at Mathproof/Meta/WordRAMLogWidthTransfer20261022.lean. Preserve the hashes in DEPENDENCIES.json and AUDIT.json. Fetch the pinned Mathlib environment and cache in the usual Lake workflow, then build Mathproof.Meta.WordRAMLogWidthTransfer20261022.

A fresh axiom driver imports that module and runs #print axioms for each of:
- Mathproof.WordRAMLogWidthTransfer20261022.computesIn_on
- Mathproof.WordRAMLogWidthTransfer20261022.computesInOn_mono
- Mathproof.WordRAMLogWidthTransfer20261022.computesInOn_ofLax13
- Mathproof.WordRAMLogWidthTransfer20261022.polynomial_fitsWords
- Mathproof.WordRAMLogWidthTransfer20261022.compiled_polynomial_run

Accept only a successful compilation and axiom output without sorryAx or project axioms. The existing MathProof environment supplied the import artifacts for our local fresh appendix check. An isolated dependency-source rebuild is a separate reproducibility step; do not claim it was completed unless its log exists.

The imported source tree, manifest and the theorem appendix are optional formal provenance. The mathematical theorem and proof in MACHINE-INTERFACE.md do not require downloading Lean to review.
