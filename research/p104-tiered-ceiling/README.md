# P104: tiered ceilings for words meeting the native-class hypotheses (incl. the frontier words): t0 = .0118103 at the junk count, t0 = .0151027 / .0151869 with no junk assumption (Lean, no kappa)

Authors: DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. **No kappa claim.** Everything here is a Lean statement with named hypotheses. Lean proves nothing about the extracted data's fidelity, the word files, or the checker scripts; those premises are listed in `NATIVES.md`.

## The three theorems
All three conclude `F(1 - t, invoice (caller 6 7) n 17) < 0` for `t` in `[t0, 1]`, i.e. kappa <= `t0` for any word meeting the hypotheses, on the 17-call invoice of the #7113 caller C(8|9).

| tag | theorem (module) | `t0` | junk assumption | extra |
|---|---|---|---|---|
| T1 | `CongestionNative.ceiling_native_J` (`CongestionNativeJ`) | .0118103 | `hJ : 4962 <= J.card` | covers only words with at least 4962 junk cells |
| T2a | `CongestionNative.ceiling_noHJ` (`JunkLawACeiling`) | .0151027 | none: `hJ` is derived from Law A | `hD : D <= 56`, which in Lean means rank M <= 56 (any spanning set of D arrival vectors) |
| T2b | `CongestionNative.ceiling_native_Z0` (`CongestionNativeZ`) | .0151869 | none | no junk count and no upper bound on owned mass; it still assumes `hmass : 56 <= ks.sum`, `hk`, `hmd`, `hmr`, `hY` and the rest of class K |

`JunkLawA` proves Law A in Lean (`maisBound`: sum over t of 1/(j_t+1) <= rank M, by Caro-Wei over all rankings, needs `hdiag`; with rank M <= D from `hspan`, the Lean theorem `lawA_96` states 96 <= J for `m : LawAModel K 104 D`, D <= 56, under all LawAModel premises incl. `hpart <= 48`; the general inequality J >= 2(P - D) is not stated in Lean). Its premises are the named fields of the structure `LawAModel` (`hspan`, `hdiag`, `hodd`, `hpart`); the register-machine facts behind `hspan` are not formalised.

## Hypotheses (generated from the Lean statements)
The lists below were extracted by script from the binders of the three theorems; the full text of every binder is in `PROVED.md`. All of them are hypotheses of the Lean statements. `hcong`, `hdist` and `J` in particular: `J` is an arbitrary finite set of cells, and Lean does not tie it to any word. In T2a, `hJdef : J = junkSet m.M` is not a naming link only: it forces `hcong` and `hdist` to hold on exactly the off-diagonal support of `m.M`. T1 and T2 hard-code 8-row decoder constants (`corrC <= 8 * cH`, `capC >= unLo / 48`), so decoders with 9 or more rows are outside the model.

Hypotheses (binders) of each theorem, extracted by script from the Lean statements. Names shared by all three are listed once.

- `ceiling_native_J` [T1]: `R`, `nR`, `dR`, `hmono`, `hd9`, `hmix`, `n`, `ks`, `mr st`, `E`, `J`, `distF`, `spF cstF`, `hk`, `hmass`, `hmd`, `hmr`, `hF`, `hY`, `hst`, `hEex`, `hcong`, `hdist`, `hJ`, `hspMono`, `hcstMono`, `hspTab`, `hcstTab`, `hspTabJ`, `hcstTabJ`
- `ceiling_noHJ` [T2 (needs hD, rank M <= 56)]: `m`, `hD`, `R`, `nR`, `dR`, `hmono`, `hd9`, `hmix`, `n`, `ks`, `mr st`, `E`, `J`, `distF`, `spF cstF`, `hk`, `hmass`, `hmd`, `hmr`, `hF`, `hY`, `hst`, `hEex`, `hcong`, `hdist`, `hJdef`, `hspMono`, `hcstMono`, `hspTabN`, `hcstTabN`
- `ceiling_native_Z0` [T2 (no junk count, no mass upper bound)]: `R`, `nR`, `dR`, `hmono`, `hd9`, `hmix`, `n`, `ks`, `mr st`, `E`, `J`, `distF`, `spF cstF`, `hk`, `hmass`, `hmd`, `hmr`, `hF`, `hY`, `hst`, `hEex`, `hcong`, `hdist`, `hspMono`, `hcstMono`, `hspTabN`, `hcstTabN`

- `ceiling_noHJ` relative to `ceiling_native_J`: removes `hJ`, `hspTab`, `hcstTab`, `hspTabJ`, `hcstTabJ`; adds `m`, `hD`, `hJdef`, `hspTabN`, `hcstTabN`
- `ceiling_native_Z0` relative to `ceiling_native_J`: removes `hJ`, `hspTab`, `hcstTab`, `hspTabJ`, `hcstTabJ`; adds `hspTabN`, `hcstTabN`

Every binder with its Lean type (T1 = `ceiling_native_J`, T2a = `ceiling_noHJ`, T2b = `ceiling_native_Z0`):

Hypotheses (binders) of each theorem, extracted by script from the Lean statements. Names shared by all three are listed once.

- `ceiling_native_J` [T1]: `R`, `nR`, `dR`, `hmono`, `hd9`, `hmix`, `n`, `ks`, `mr st`, `E`, `J`, `distF`, `spF cstF`, `hk`, `hmass`, `hmd`, `hmr`, `hF`, `hY`, `hst`, `hEex`, `hcong`, `hdist`, `hJ`, `hspMono`, `hcstMono`, `hspTab`, `hcstTab`, `hspTabJ`, `hcstTabJ`
- `ceiling_noHJ` [T2 (needs hD, rank M <= 56)]: `m`, `hD`, `R`, `nR`, `dR`, `hmono`, `hd9`, `hmix`, `n`, `ks`, `mr st`, `E`, `J`, `distF`, `spF cstF`, `hk`, `hmass`, `hmd`, `hmr`, `hF`, `hY`, `hst`, `hEex`, `hcong`, `hdist`, `hJdef`, `hspMono`, `hcstMono`, `hspTabN`, `hcstTabN`
- `ceiling_native_Z0` [T2 (no junk count, no mass upper bound)]: `R`, `nR`, `dR`, `hmono`, `hd9`, `hmix`, `n`, `ks`, `mr st`, `E`, `J`, `distF`, `spF cstF`, `hk`, `hmass`, `hmd`, `hmr`, `hF`, `hY`, `hst`, `hEex`, `hcong`, `hdist`, `hspMono`, `hcstMono`, `hspTabN`, `hcstTabN`

- `ceiling_noHJ` relative to `ceiling_native_J`: removes `hJ`, `hspTab`, `hcstTab`, `hspTabJ`, `hcstTabJ`; adds `m`, `hD`, `hJdef`, `hspTabN`, `hcstTabN`
- `ceiling_native_Z0` relative to `ceiling_native_J`: removes `hJ`, `hspTab`, `hcstTab`, `hspTabJ`, `hcstTabJ`; adds `hspTabN`, `hcstTabN`
| hypothesis | in | Lean type |
|---|---|---|
| `R` | T1, T2a, T2b | `Finset ι` |
| `nR` | T1, T2a, T2b | `ι → ℕ` |
| `dR` | T1, T2a, T2b | `ι → ℕ → ℕ` |
| `hmono` | T1, T2a, T2b | `∀ r ∈ R, ∀ i < nR r, dR r i ≤ dR r (i + 1)` |
| `hd9` | T1, T2a, T2b | `∀ r ∈ R, dR r (nR r) ≤ 9` |
| `hmix` | T1, T2a, T2b | `(R.filter fun r => Mixed dR nR r).card ≤ 5` |
| `n` | T1, T2a, T2b | `Inv` |
| `ks` | T1, T2a, T2b | `List ℕ` |
| `mr st` | T1, T2a, T2b | `ℕ` |
| `E` | T1, T2a, T2b | `ℝ → ℝ` |
| `J` | T1, T2a, T2b | `Finset (ℕ × ℕ)` |
| `distF` | T1, T2a, T2b | `ℝ → ℕ × ℕ → ℝ` |
| `spF cstF` | T1, T2a, T2b | `ℝ → ℝ` |
| `hk` | T1, T2a, T2b | `∀ k ∈ ks, 1 ≤ k ∧ k ≤ 9` |
| `hmass` | T1, T2a, T2b | `56 ≤ ks.sum` |
| `hmd` | T1, T2a, T2b | `8 ≤ ks.length` |
| `hmr` | T1, T2a, T2b | `8 ≤ mr` |
| `hF` | T1, T2a, T2b | `∀ s, 0 ≤ s → s ≤ 1 → Finv s n ≤ -400 * (8 : ℝ) ^ s - dprice ks s - mr - E s` |
| `hY` | T1, T2a, T2b | `104 ≤ st + (ks.length + mr)` |
| `hst` | T1, T2a, T2b | `∀ s, 0 ≤ s → s ≤ 1 → (2 - (2 : ℝ) ^ s) * st ≤ E s` |
| `hEex` | T1, T2a, T2b | `∀ s, 0 ≤ s → s ≤ 1 → ∑ r ∈ R, ex (gs s) (lev dR r) (nR r) ≤ E s` |
| `hcong` | T1, T2a, T2b | `∀ s, 9 / 10 ≤ s → s ≤ 1 - ((tJ0 : ℚ) : ℝ) → ∑ p ∈ J, min (distF s p) (capC s) - corrC cstF s ≤ ∑ r ∈ R, ∑ i ∈ range (nR r), c2 (gs s) (lev dR r i) (lev dR r (i + 1)) + Omega ks mr s (differs between theorems; see PROVED.md)` |
| `hdist` | T1, T2a, T2b | `∀ s, 9 / 10 ≤ s → s ≤ 1 - ((tJ0 : ℚ) : ℝ) → ∀ p ∈ J, spF (1 - s) ≤ distF s p (differs between theorems; see PROVED.md)` |
| `hJ` | T1 | `4962 ≤ J.card` |
| `hspMono` | T1, T2a, T2b | `MonotoneOn spF (Set.Icc ((tJ0 : ℚ) : ℝ) (1 / 10)) (differs between theorems; see PROVED.md)` |
| `hcstMono` | T1, T2a, T2b | `MonotoneOn cstF (Set.Icc ((tJ0 : ℚ) : ℝ) (1 / 10)) (differs between theorems; see PROVED.md)` |
| `hspTab` | T1 | `((spFloC0 : ℚ) : ℝ) ≤ spF ((tC0 : ℚ) : ℝ) ∧ ((spFloC1 : ℚ) : ℝ) ≤ spF ((tC1 : ℚ) : ℝ) ∧ ((spFloC2 : ℚ) : ℝ) ≤ spF ((tC2 : ℚ) : ℝ) ∧ ((spFloC3 : ℚ) : ℝ) ≤ spF ((tC3 : ℚ) : ℝ)` |
| `hcstTab` | T1 | `cstF ((tC1 : ℚ) : ℝ) ≤ ((cHC0 : ℚ) : ℝ) ∧ cstF ((tC2 : ℚ) : ℝ) ≤ ((cHC1 : ℚ) : ℝ) ∧ cstF ((tC3 : ℚ) : ℝ) ≤ ((cHC2 : ℚ) : ℝ) ∧ cstF (1 / 10) ≤ ((cHC3 : ℚ) : ℝ)` |
| `hspTabJ` | T1 | `((spFloJ0 : ℚ) : ℝ) ≤ spF ((tJ0 : ℚ) : ℝ) ∧ ((spFloJ1 : ℚ) : ℝ) ≤ spF ((tJ1 : ℚ) : ℝ) ∧ ((spFloJ2 : ℚ) : ℝ) ≤ spF ((tJ2 : ℚ) : ℝ)` |
| `hcstTabJ` | T1 | `cstF ((tJ1 : ℚ) : ℝ) ≤ ((cHJ0 : ℚ) : ℝ) ∧ cstF ((tJ2 : ℚ) : ℝ) ≤ ((cHJ1 : ℚ) : ℝ) ∧ cstF ((tC0 : ℚ) : ℝ) ≤ ((cHJ2 : ℚ) : ℝ)` |
| `m` | T2a | `JunkLawA.LawAModel K 104 D` |
| `hD` | T2a | `D ≤ 56` |
| `hJdef` | T2a | `J = JunkLawA.junkSet m.M` |
| `hspTabN` | T2a, T2b | `((spFloN0 : ℚ) : ℝ) ≤ spF ((tN0 : ℚ) : ℝ) ∧ ((spFloN1 : ℚ) : ℝ) ≤ spF ((tN1 : ℚ) : ℝ) ∧ ((spFloN2 : ℚ) : ℝ) ≤ spF ((tN2 : ℚ) : ℝ) ∧ ((spFloN3 : ℚ) : ℝ) ≤ spF ((tN3 : ℚ) : ℝ) ∧ ((spFloN4 : ℚ) : ℝ) ≤ spF ((tN4 : ℚ) : ℝ) (differs between theorems; see PROVED.md)` |
| `hcstTabN` | T2a, T2b | `cstF ((tN1 : ℚ) : ℝ) ≤ ((cHN0 : ℚ) : ℝ) ∧ cstF ((tN2 : ℚ) : ℝ) ≤ ((cHN1 : ℚ) : ℝ) ∧ cstF ((tN3 : ℚ) : ℝ) ≤ ((cHN2 : ℚ) : ℝ) ∧ cstF ((tN4 : ℚ) : ℝ) ≤ ((cHN3 : ℚ) : ℝ) ∧ cstF ((tN5 : ℚ) : ℝ) ≤ ((cHN4 : ℚ) : ℝ) (differs between theorems; see PROVED.md)` |

## Files
| file | content |
|---|---|
| PROVED.md | the main statements, copied by script from the Lean text (all hypotheses visible) |
| NATIVES.md | table premise x word (st1, #7637, x1t2a, #7660 word) -> result and script |
| CHECK.txt | fresh compile table of the 66 modules (one at a time, 3.5 GB guard), with one stated exception, and `#print axioms` |
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
All scripts that compute the word-level premises and the table entries, the word files, and the working notes that the per-file `.md` notes cite. Labels such as HC5 or JL1 refer to those notes.
