# Lean-only release, part 3 (combined): premise narrowing, ceilings, word structure, spec-break kills

Authors: DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. **No κ claim.** Everything here is a Lean statement with named hypotheses; Lean proves nothing about the extracted data's fidelity, the compiler, or the checker scripts.
This is the third Lean-only package. It follows the floors/bridge package (#7632) and the structural-laws package (#7634) and uses the same toolchain, Mathlib pin and module prefix (`Nov15.`). It is unregistered, like the other Lean packages: it is not wired into any build or verifier of the repository.

## What is in it
**A. Premise narrowing for #7620.** Our #7623/#7630 κ is conditional on #7620's premises. Six Lean files shrink what is merely assumed:
`ClearCert` (every CLEAR is lossless; checker sound and complete), `OwnedAscent` (owned ascent is priced symmetrically, earns no credit, and relaxed-class floors imply strict-class floors),
`NativeColumns` (exact rows ⇔ all columns), `CensusComplete` (+ `CensusData`: the 981-pair census is a DELTA census; all used pairs are correct if the census and #7623's used pairs are),
`OwnedSkeleton` (+ `OwnedSkeletonData`: E1, E2, E3-flat for the real owned skeleton), `OwnedTree` (+ `OwnedTreeData`, `OwnedTreeCheck`: E3-tree for every depth and call-site set under atomic calls).
`PREMISES.md` lists, premise by premise, what is now a kernel fact and what is still assumed.

**B. Caller-tied ceiling.** `CallerCost` (caller cost closed form, reproduction of the #7113 caller invoice, single crossing, composition) and `JointCeiling`
(ceiling κ ≤ .0419448764 conditional on named hypotheses; kernel-checked 2|2 bound t ≥ 141/4096 and 1|1 bound t ≥ 176/4096; the earlier .0336 is withdrawn).

**C. SWAP-NULL law.** `SwapNull.lean`: the swap gadget, hub-undoability iff both helpers end in V or both are born in G0, zero cost change in exactly those cases, and a witness that cost-changing swaps cannot be undone (see PROVED.md §C).

**D. Whole-word and restricted-class ceilings.** `WholeFloor*` (model, slack rank, pricing, the nesting rule, kernel interval cover) with `NumCertK*` (kernel interval arithmetic), `FloorK22*` (class K(S22)), `CongestionI3*` (the I3 congestion bound and rank-8, C = 56 junk count), with the supporting `FloorCert*` (780-stop LP certificate), `DescentPrice`, `FloorD0`, `JunkLB2`. Results: κ ≤ .0204110965 over legal (nested) words, hypotheses Theorem Y, `Indep`, `hF`, `Priced`; κ ≤ .0060197405 for class K(S22); κ ≤ .0183952347 and .0134769139 for the restricted class M_V, with I3, the flag-DP minima, rank-8 C = 56 and public provenance as hypotheses. The M_V ceilings are not floors on the native class: no known native lies in M_V.

**E. Word structure.** `Shadow` (twin invoice has the same net), `Annihilator` (served ports ≤ descending owned rank), `Delivery` (two contacts, three-hop cost, direct-read capacity), `DesignLaws` (port/chart laws, rank-feed, XCLOSE), `SharedCourier` (shared-snapshot courier), `PsiLaw` (span law and exposed reads), `WordDuality` (legal words dualise; the invoice and roots are unchanged), `PlaneLaws` (SPLIT for any n, QUARTER exact partition; counts on E7 only), with `HubSettle`, `RankLaw`, `RankLawC`, `FrameSep`.

**F. Spec-break kills.** `SpecTSUR`, `SpecTS`, `SpecINV`, `SpecGC`, `SpecRankP`, `SpecRankP2`, `SpecLemmaU`, `SpecLemmaU2`, `Spec6`, `PadLift`, `Spec0Sym` (+ `Spec0K0Core`), `CallerBorrow`: rank, Gram and involution lemmas used by the kill arguments, with their model hypotheses stated. `Spec0K0_ABCEDF_s0` to `s6` are PARTIAL: radical certificates for 60 of the 68 targets of one class; 8 targets are not certified.

**G. Smaller lemmas.** `LemmaW` (borrow lemma W), `SmallRoots` (+ Defs, Data, A22Corners; kernel checks of three small-caller roots).

Labels such as R3, RB4 and AUDIT5 in the per-file notes refer to internal working notes that are not part of this package.

| file | content |
|---|---|
| PREMISES.md | per premise: kernel FACT vs still ASSUMED |
| PROVED.md | every theorem with its exact hypotheses |
| FALSE.md | prose statements Lean refuted or corrected |
| CHECK.txt | compile table (one file at a time, 3.5 GB guard) and axioms |
| SHIPPED.txt | files already in #7632/#7634 (byte-identical) |
| PR_BODY.md | draft PR description |
| NOTICE.md, LICENSE | credit and Apache-2.0 |
| lean/ | Lean subproject; sources in `lean/Nov15/`, one `.md` per theorem file |

## Pins
- Toolchain `leanprover/lean4:v4.33.0-rc1` (`lean/lean-toolchain`).
- Mathlib commit `55b7917b472489c7c56a0fa6393af05cfd536599` (`rev` in `lean/lakefile.toml`; `lean/lake-manifest.json` pins every transitive package).

## Build
```
cd lean
lake exe cache get      # prebuilt Mathlib oleans for the pinned commit
lake build              # library Nov15 (default target; every module in lean/Nov15)
```
Peak memory per file is at most 3.5 GB (the guard; the chunked data files are split for this) (CHECK.txt). The `lake build` route was not run for CHECK.txt (it downloads Mathlib); CHECK.txt used `lean -o` file by file in dependency order against an existing build of the pinned commit.

## Data files
`CensusData`, `OwnedSkeletonData`, `OwnedTreeData` are generated Lean (lists extracted from the #7630 word and affected-pair files, and a copy of the #7113 caller). Lean re-checks everything derived from them; the extraction itself (a script) is not shipped and its fidelity rests on reading.
The rational-cell data inside `JointCeiling.lean` is inline; the scripts that produced it are not shipped.

## Not included
All scripts and generators (the Singular, python and LP tooling that produced the data files and certificates), the source data files (word, certificates, pair lists), and the internal working notes the per-file `.md` notes cite. Generated Lean data files are included; their fidelity to the sources rests on reading.
