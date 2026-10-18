# Decoder floors, case (c): the B-locus of the A2 family (completes #2784's m ≥ 10 claim: P112 ≥ 64, #968 P104 ≥ 56, E8 ≥ 72; no κ claim)

**Status: research note. Exact finite computations plus a written proof; not a SAT/DRAT result. No κ claim, no supplier word.**
Only `research/a2-family-b-locus/` is added; nothing existing is changed. It closes the one item #2784 left open for its Claim M.

Labels: **PROVEN** (written argument), **CHECKED** (exact script in `checks/`, re-run by `verify.sh`), **RECORDED** (log shipped and hash-pinned; `verify.sh` re-runs and compares it).

## Claims box (scope is part of the claim)

Setting: exactly that of #2784 (and #2338 / #2724): a unit `E8`, `P112` (E8 minus an orthogonal frame), `P104` (#968's unit), a rank-9 iff-pattern realisation `M` in the **A2 family** of #2784 §2, the dense pairing table `B` (F2-rank 9),
cost `Σ_j rank_F2 B[R_j, A_j]`, characteristic 0, and a decoder `M = P Qᵀ` with `m ≥ 10` terms whose factors lie in the realisation's two 9-dimensional spaces (`P = A X̂`, `Q = B Ŷ`).

| # | Statement | Scope | Status |
|---|---|---|---|
| **B1** | Members on the **B-locus** `γ₂ = γ₃` are of B-form: `M = D₁ G + 1_X βᵀ`, `supp β ⊆ X`, a rank-one change of the 3×3 triangle block only (§1) | A2 family, B-locus | PROVEN (from #2784 §2 / CONJB Theorem G(a)) |
| **B2** | **On the B-locus every such decoder with `m ≥ 10` costs ≥ 64 (P112), ≥ 72 (E8); for P104 (all 28 triangle representatives) ≥ 58 when the decoder still has ≥ 10 terms after merging parallel terms, otherwise Theorem F's 56** (§2) | the A2-family members with `γ₂ = γ₃`, `m ≥ 10`, factors in the two 9-dimensional spaces, dense `B` | PROVEN from CHECKED facts (a)–(e) (`checks/bcheck.py`) |
| **M′** | With #2784 (off the locus 68 / 64 / 77; Theorem F for `m = 9`): **Claim M holds on the whole A2 family**: every decoder of every A2-family member with `m ≥ 9` terms and factors in the spaces costs **P112 ≥ 64, #968 P104 ≥ 56, E8 ≥ 72** (on the B-locus P104 is ≥ 58 for decoders whose terms stay ≥ 10 after merging parallel terms; otherwise Theorem F's 56 applies, so the combined P104 bound stays 56) | same scope, any `m ≥ 9` | PROVEN, from B2 + #2784 Claim M + Theorem F |

The transposed family (triangle on the column side) follows by the same proof with rows and columns exchanged (`G`, `B` symmetric).

**Scope, stated exactly.** These are floors for decoders whose realisation `N` is a member of the A2 family and whose factors lie in that realisation's spaces. By the universality of the factors-in-spaces normal form, this is the whole of the stated class for that `N`; **nothing is claimed for other rank-9 realisations, for decoders with factors outside the spaces, for non-iff patterns or for `B` of rank ≥ 10.** **Tightness of 64 / 72 on the B-locus is not claimed and was not checked** (the tie decoders of #2784 are off the locus). The earlier relaxation values 62 / 70 for P112 / E8 were slack (§3), not decoders; for P104 the value 58 (proved when the terms stay ≥ 10 after merging) equals the relaxation value. **Out-of-space `m ≥ 10`** (decoders whose factors leave `col M` / `row M`, #2784 README §7.3) **stays OPEN.**

## 1. B-locus members (PROVEN)

On `γ₂ = γ₃`, after a change of basis of `K⁹`: `a_u = (r_u, 0)`, `b_s = (r_s, 0)` off `X`, and `a_{u_i} = (λ_i r_i, 1)`, `b_{u_i} = (r_i, β_i)` with `λ_i ≠ 0` (#2784 §2, CONJB Theorem G(a)).
So `M = D₁ G + 1_X βᵀ` with `supp β ⊆ X`: **B-form**, a rank-one change of the triangle block only. The triangle `X` is pairwise non-orthogonal, so the biclique condition holds. This is why the B-locus is the exceptional case in #2784: its merged-kill fact lets two merged column classes be co-killed only there.

## 2. Theorem (PROVEN from CHECKED facts (a)–(e))

Write `x̂_j = (x_j, a_j)`, `ŷ_j = (y_j, b_j)`; `Σ_j x̂_j ŷ_jᵀ = I₉`, hence `Σ_j x_j y_jᵀ = I₈`. After merging (#2784 §7.1) the `x̂_j` are pairwise non-parallel, the `ŷ_j` are pairwise non-parallel, and `m′ ≥ 9`; `m′ = 9` is #2784's Theorem F, so `m′ ≥ 10`.
Let `J* = {j : x_j ≠ 0 ≠ y_j}`. A term outside `J*` has `x_j = 0` (then `x̂ ∥ e₉`: at most one, `T_r`) or `y_j = 0` (`ŷ ∥ e₉`: at most one, `T_c`). `Σ_{J*} x_j y_jᵀ = I₈`.

**Restriction bound.** Off `X` rows and columns are Gram, so `R_j∖X = supp(R x_j)∖X` and `A_j∖X = supp(R y_j)∖X`, and `cost_j ≥ c′_j := rank B[supp(Rx_j)∖X, supp(Ry_j)∖X]`. The pairs `(x_j, y_j)`, `j ∈ J*`, form an *inside decoder* of `G` on `L∖X` (X deleted on both sides).

**CHECKED facts** (`checks/bcheck.py`, UNIT = P112 | P104 | E8; P104 for each of the 28 triangle orbit representatives of #2784):

* (a) labels of `L∖X` span `F₂⁹`; the deficient classes of `G` on `L∖X` (11 / 19 / 3 for P112 / P104 / E8) have 1-dimensional nullspaces with pairwise distinct normals, so one direction kills at most one class and the class table is exact;
* (b) every term with `x, y ≠ 0` has `c′ ≥ 7`;
* (c) class-level relaxation of inside decoders on `L∖X` with `m″` terms (each class direction once per side), `m″ = 9`: **66 / 63 / 75**;
* (d) (the key new input) the square (`m″ = 8`) lower bound with `X` deleted on both sides, `Q_XX`, by the `opt3u` duality branch-and-bound (complete, all candidate spaces 1-dimensional): **62 / 56 / 70**;
* (e) (S): `r(O_{u_i}∖(E6 ∪ X))` spans `r_i^⊥` and `B[X, s] = e_i` there; `rank{r₁, r₂, r₃} = 2`.

**Cases.**

1. *Merging inside `J*`* (two `J*` terms with parallel `x` or parallel `y` in `K⁸`). Merge to a decoder with `m″ ≥ 8` non-parallel terms (cost ≥ `Q_XX`, or ≥ (c) if `m″ ≥ 9`). A group `g` merged into one term has `Σ_g c′_j ≥ 7|g| ≥ c̃ + (7|g| − 9)`, since `c̃ ≤ 9 = rank B`; a cancelled group pays ≥ 14. So `Σ_{J*} ≥ Q_XX + 5 = 67 / 61 / 75`.
2. *No merging, `|J*| ≥ 9`*: cost ≥ (c) = **66 / 63 / 75**.
3. *No merging, `|J*| = 8`*: then `m′ = 10` and `T_r`, `T_c` are distinct terms; `y_r ≠ 0` (else `ŷ_r ∥ e₉ ∥ ŷ_c`). `T_r` has `p = a_r 1_X`, `R = X`; `y_r` lies on at most one line `⟨r_i⟩`, so by (e) `A_r` contains `s_i ∈ O_{u_i}∖(E6 ∪ X)` with `B[X, s_i] = e_i` for two values of `i`: `cost(T_r) ≥ 2`. Total `≥ Q_XX + 2 =` **64 / 58 / 72**. ∎

The minimum over the cases is the floor for decoders with `m′ ≥ 10` after merging: **P112 64, P104 58, E8 72** (a decoder that merges down to 9 terms is covered by Theorem F: 64 / 56 / 72, so for P104 the unconditional bound is 56) (`bcheck.py` prints `FLOOR B-locus m>=10`). Only Case 3 is at the floor; whether it is attained was not checked.

## 3. Why the relaxation values 62 / 70 (P112 / E8) are not decoders (PROVEN from CHECKED (e))

The class-level relaxation with an `e₉` row (`R = X`) and an `e₉` column (`A = supp β ⊆ X`) has optimum **62 / 58 / 70** (P112 / P104 / E8) at `m = 10`, `|supp β| = 1` (`checks/relax.py`; recorded in `evidence/logs/relax_*.log.txt`). Its optimal configuration uses
three cost-7 terms whose row normals are `∝ r₁, r₂, r₃`, inside a decoder of 8 `J*` terms. That is impossible: the 8 `x_j` of a square inside decoder form a basis of `K⁸` (`Σ x_j y_jᵀ = I₈`), but `r₁, r₂, r₃` span only 2 dimensions ((e), `rank = 2`).
The relaxation ignores this and, for `m′ = 9`, even returns 54 (P112) where #2784 Case II(a) proves 64: it ignores duality entirely. For P104 the relaxation value 58 coincides with the proven bound, so nothing is slack there. The floors of §2 are not contradicted by the relaxation; no constructive attempt is needed.

## 4. Files

* `checks/bcheck.py` (facts (a)–(e), floor line), `checks/relax.py` (the relaxation optimum and configuration), `checks/qxx.py` and `checks/inrelax.py` (auxiliary: partial punctures of `Q_XX`, and the inside relaxation alone; re-run by `verify.sh` step 3 and compared with the recorded logs `evidence/logs/qxx_*`, `inrelax_*`: P112 `Q_XX` with `(|Z_r|,|Z_c|) = (1,1)` 63, `(2,2)`, `(3,0)`, `(3,1)`, `(3,3)` 62).
* `checks/a2lib.py, a2cls.py, opt3u.py, iib.py, setup9.py, cert2.py, lib.py, lib2.py, common2.py, frames.py, frames_data.py, manifest_check.py`, `data/p104_frames.json`: **vendored unchanged from #2784** (`research/a2-family-decoder-floors/`) so that this package is self-contained; see `NOTICE.md`, `SOURCES.json`.
* `evidence/logs/`: recorded outputs (`bcheck_*`, the 28 `b104_*`, `relax_*`, `qxx_*`), compared by `verify.sh` with the re-run output.

## 5. Verification

`bash research/a2-family-b-locus/verify.sh /fresh/dir` (Python ≥ 3.11, `numpy`, `networkx`; `PYTHON=` to choose the interpreter). Steps: manifest; `bcheck.py` on P112, E8 and the 28 P104 representatives (6 processes at a time, each under `timeout 1200`), outputs compared byte-for-byte with the recorded logs;
`relax.py` on the three units; the partial punctures of `Q_XX` and `inrelax.py`. `Q_XX` itself (fact (d)) is re-run inside every `bcheck.py` call, i.e. for P112, E8 and all 28 P104 representatives. Wall time is about two minutes. No SAT solver.
