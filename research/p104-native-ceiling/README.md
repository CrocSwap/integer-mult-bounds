# P104: a conditional ceiling kappa <= .0136564 covering the current frontier words (Lean, no kappa)

Authors: DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. **No kappa claim.** Everything here is a Lean statement with named hypotheses. Lean proves nothing about the extracted data's fidelity, the word files, or the checker scripts; those premises are listed in `NATIVES.md`.

## What is in it
The import closure of `Nov15/CongestionNativeH.lean` (38 modules). 25 modules are the unchanged files of the previous Lean package (#7656), 13 are new:
`CongestionI3DualAlg`, `CongestionI3DualConst`, `CongestionI3DualSig`, `CongestionI3DualCertC0` to `C3`, `CongestionI3DualData`, `CongestionI3DualNumC` (two-sided I3: each public register's excess is telescoped end-anchored or start-anchored, so the premise "every public register ends at V" is replaced by "at most 5 mixed registers"; sigma certificates; rational cell data), `CongestionNativeTab` (outward-rounded rational tables), `CongestionNative` (`ceiling_native`: F(1-t) < 0 for t in [tC0, 1], tC0 = .0136564), `PathCut` (`path_cut`, `nested_needed`, `transported_card_le`) and `CongestionNativeH` (`ceiling_native'`: the hypotheses `hspMono`, `hcstMono`, `hdist` and `hcong` are derived from shape-DAG and per-cell-path hypotheses).

**The class-wide bound |J| >= 1936 (`hJ`) is a conjecture.** For the natives it is a computed value (|J| = 4962), not a bound; Lean takes it as a hypothesis. Equally, the natives' membership in the class is computed, not proved in Lean (`NATIVES.md`).

## Files
| file | content |
|---|---|
| PROVED.md | the main statements, copied by script from the Lean text (all hypotheses visible) |
| NATIVES.md | per word-level premise: the script that computes it, the words it ran on, the result |
| CHECK.txt | fresh compile table of all 38 modules (one at a time, 3.5 GB guard) and `#print axioms` |
| PR_BODY.md | draft PR description |
| LICENSE | Apache-2.0 |
| lean/ | Lean subproject; sources in `lean/Nov15/`, notes in the per-file `.md` where present |

## Pins and build
Toolchain `leanprover/lean4:v4.33.0-rc1` (`lean/lean-toolchain`); Mathlib commit `55b7917b472489c7c56a0fa6393af05cfd536599` (`lean/lakefile.toml`, `lean/lake-manifest.json`).
```
cd lean
lake exe cache get
lake build
```
CHECK.txt was produced file by file with `lean -j1 -o` in dependency order against an existing build of the pinned Mathlib, with a fresh output directory first on the search path. `lake build` itself was not run.

## Not included
All scripts that compute the word-level premises, the word files, and the working notes the per-file `.md` notes cite. Labels such as HC5 or AUD refer to those notes.
