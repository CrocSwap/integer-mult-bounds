/-
RankLaw (c) fix, lane LEAN-NEXT10, Nov 16. See RankLawC.md.

`rank_law` needs U ⊓ span(non-V targets) = ⊥. This file drops that hypothesis:
* `rank_law_gen`: with no U at all, V mix ⟺ no loss ∧ every V-ender row ∈ B ∧ B ⊓ N ≤ A
  (B = span V targets, N = span non-V targets, A = span V-ender rows).
* `rank_law_proj`: for any U ⊇ B and any linear π vanishing on B and injective on U ⊓ N,
  condition (ii) becomes "row ∈ U and π(row) = 0" (the (U ⊓ N)-component vanishes).
* `rank_law_indep`: if B ⊓ N = ⊥ (independent targets) the third clause disappears.
* `rank_law_of_gen`: the original `rank_law` is the case π = 0.

Build (imports the RankLaw olean, itself built on TokenCancel):
  lake env lean -o .lake/build/lib/lean/Nov15/TokenCancel.olean Nov15/TokenCancel.lean
  lake env lean -o .lake/build/lib/lean/Nov15/RankLaw.olean Nov15/RankLaw.lean
  lake env lean -o .lake/build/lib/lean/Nov15/RankLawC.olean Nov15/RankLawC.lean
-/
import Nov15.RankLaw

set_option linter.unusedSectionVars false

namespace RankLawC
open Submodule Module TokenCancel RankLaw

section Lat
variable {K M : Type*} [Field K] [AddCommGroup M] [Module K M]

/-- Cancellation without a complement: given A ⊔ N = B ⊔ N, A = B iff A ≤ B and B ⊓ N ≤ A. -/
theorem eq_iff_of_sup_eq (A B N : Submodule K M) (h : A ⊔ N = B ⊔ N) :
    A = B ↔ A ≤ B ∧ B ⊓ N ≤ A := by
  constructor
  · rintro rfl; exact ⟨le_rfl, inf_le_left⟩
  · rintro ⟨hAB, hBN⟩
    refine le_antisymm hAB fun b hb => ?_
    have : b ∈ A ⊔ N := h ▸ mem_sup_left hb
    obtain ⟨a, ha, n, hn, rfl⟩ := mem_sup.1 this
    have hnB : n ∈ B := by
      have := sub_mem hb (hAB ha); simpa using this
    exact add_mem ha (hBN ⟨hnB, hn⟩)

/-- The (U ⊓ N)-component test: if B ≤ U, x ∈ U ⊓ (B ⊔ N), π vanishes on B and is injective on U ⊓ N,
then x ∈ B ⟺ π x = 0. -/
theorem mem_iff_proj {M' : Type*} [AddCommGroup M'] [Module K M'] (B N U : Submodule K M)
    (π : M →ₗ[K] M') (hBU : B ≤ U) (hπB : ∀ b ∈ B, π b = 0)
    (hπ : LinearMap.ker π ⊓ (U ⊓ N) = ⊥) (x : M) (hxU : x ∈ U) (hx : x ∈ B ⊔ N) :
    x ∈ B ↔ π x = 0 := by
  refine ⟨hπB x, fun h0 => ?_⟩
  obtain ⟨b, hb, n, hn, rfl⟩ := mem_sup.1 hx
  have hnU : n ∈ U := by
    have := sub_mem hxU (hBU hb); simpa using this
  have hπn : π n = 0 := by rw [map_add, hπB b hb, zero_add] at h0; exact h0
  have : n ∈ LinearMap.ker π ⊓ (U ⊓ N) := ⟨hπn, hnU, hn⟩
  rw [hπ, mem_bot] at this
  subst this; simpa using hb

end Lat

section Run
variable {K Reg C : Type*} [Field K] [Fintype Reg] [DecidableEq Reg] [DecidableEq C]
variable (z V : C)

/-- With no loss (and the RankLaw hypotheses), A ⊔ N = B ⊔ N. -/
theorem sup_eq_of_noloss (s : St K Reg C) (T : Finset Reg) (evs : List (Ev K Reg C))
    (hL : Legal z V s evs) (hN : ∀ e ∈ evs, NZ e) (hG : Good s T) (hS : Sp s = TS T)
    (Rf : Reg → Reg → K) (G1 : Finset Reg)
    (hNon : ∀ r ∉ G1, (run s evs).row r = Rf r)
    (hTgt : span K (Set.range Rf) = TS (tokRun T evs)) (hl : ¬ Loss s evs) :
    span K ((run s evs).row '' (G1 : Set Reg)) ⊔ span K (Rf '' (G1 : Set Reg)ᶜ) =
      span K (Rf '' (G1 : Set Reg)) ⊔ span K (Rf '' (G1 : Set Reg)ᶜ) := by
  set X := (run s evs).row with hXdef
  have hNim : X '' (G1 : Set Reg)ᶜ = Rf '' (G1 : Set Reg)ᶜ :=
    Set.image_congr (fun r hr => hNon r (by simpa using hr))
  have hfull := span_run z V s T evs hL hN hG hS hl
  rw [← hNim, ← span_range_split X G1, hNim, ← span_range_split Rf G1, hTgt]; exact hfull

/-- **RankLaw, general form (no U).** Same hypotheses as `RankLaw.rank_law` minus `hRU`/`hUN`.
B = span V targets, N = span non-V targets, A = span V-ender end rows. -/
theorem rank_law_gen (s : St K Reg C) (T : Finset Reg) (evs : List (Ev K Reg C))
    (hL : Legal z V s evs) (hN : ∀ e ∈ evs, NZ e) (hG : Good s T) (hS : Sp s = TS T)
    (Rf : Reg → Reg → K) (G1 : Finset Reg)
    (hNon : ∀ r ∉ G1, (run s evs).row r = Rf r)
    (hTgt : span K (Set.range Rf) = TS (tokRun T evs)) :
    VMix (run s evs).row Rf G1 ↔ ¬ Loss s evs ∧
      (∀ g ∈ G1, (run s evs).row g ∈ span K (Rf '' (G1 : Set Reg))) ∧
      span K (Rf '' (G1 : Set Reg)) ⊓ span K (Rf '' (G1 : Set Reg)ᶜ) ≤
        span K ((run s evs).row '' (G1 : Set Reg)) := by
  set X := (run s evs).row with hXdef
  have hNim : X '' (G1 : Set Reg)ᶜ = Rf '' (G1 : Set Reg)ᶜ :=
    Set.image_congr (fun r hr => hNon r (by simpa using hr))
  unfold VMix
  rw [vmixM_iff_span, range_restrict, range_restrict]
  have hAle : (∀ g ∈ G1, X g ∈ span K (Rf '' (G1 : Set Reg))) ↔
      span K (X '' (G1 : Set Reg)) ≤ span K (Rf '' (G1 : Set Reg)) :=
    ⟨fun h => span_le.2 (by rintro _ ⟨g, hg, rfl⟩; exact h g hg),
     fun h g hg => h (subset_span ⟨g, hg, rfl⟩)⟩
  constructor
  · intro hAB
    have hfull : Sp (run s evs) = TS (tokRun T evs) := by
      rw [← hTgt, Sp, ← hXdef, span_range_split X G1, span_range_split Rf G1, hAB, hNim]
    refine ⟨(full_rank_iff_noloss z V s T evs hL hN hG hS).1 hfull, hAle.2 hAB.le, ?_⟩
    rw [hAB]; exact inf_le_left
  · rintro ⟨hl, hB, hBN⟩
    have hsum := sup_eq_of_noloss z V s T evs hL hN hG hS Rf G1 hNon hTgt hl
    exact (eq_iff_of_sup_eq _ _ _ hsum).2 ⟨hAle.1 hB, hBN⟩

/-- **Corrected condition (ii) relative to an arbitrary U ⊇ V targets.** π is any linear map that
vanishes on the V targets and is injective on U ⊓ N (it reads the "(U ⊓ N)-component"). -/
theorem rank_law_proj {M' : Type*} [AddCommGroup M'] [Module K M']
    (s : St K Reg C) (T : Finset Reg) (evs : List (Ev K Reg C))
    (hL : Legal z V s evs) (hN : ∀ e ∈ evs, NZ e) (hG : Good s T) (hS : Sp s = TS T)
    (Rf : Reg → Reg → K) (G1 : Finset Reg) (U : Submodule K (Reg → K)) (π : (Reg → K) →ₗ[K] M')
    (hNon : ∀ r ∉ G1, (run s evs).row r = Rf r)
    (hTgt : span K (Set.range Rf) = TS (tokRun T evs))
    (hRU : ∀ g ∈ G1, Rf g ∈ U) (hπR : ∀ g ∈ G1, π (Rf g) = 0)
    (hπ : LinearMap.ker π ⊓ (U ⊓ span K (Rf '' (G1 : Set Reg)ᶜ)) = ⊥) :
    VMix (run s evs).row Rf G1 ↔ ¬ Loss s evs ∧
      (∀ g ∈ G1, (run s evs).row g ∈ U ∧ π ((run s evs).row g) = 0) ∧
      span K (Rf '' (G1 : Set Reg)) ⊓ span K (Rf '' (G1 : Set Reg)ᶜ) ≤
        span K ((run s evs).row '' (G1 : Set Reg)) := by
  set B := span K (Rf '' (G1 : Set Reg))
  have hBU : B ≤ U := span_le.2 (by rintro _ ⟨g, hg, rfl⟩; exact hRU g hg)
  have hπB : ∀ b ∈ B, π b = 0 := by
    intro b hb
    have : B ≤ LinearMap.ker π := span_le.2 (by rintro _ ⟨g, hg, rfl⟩; exact hπR g hg)
    exact this hb
  rw [rank_law_gen z V s T evs hL hN hG hS Rf G1 hNon hTgt]
  constructor
  · rintro ⟨hl, hB, h3⟩
    exact ⟨hl, fun g hg => ⟨hBU (hB g hg), hπB _ (hB g hg)⟩, h3⟩
  · rintro ⟨hl, hU, h3⟩
    have hsum := sup_eq_of_noloss z V s T evs hL hN hG hS Rf G1 hNon hTgt hl
    refine ⟨hl, fun g hg => ?_, h3⟩
    have hx : (run s evs).row g ∈ B ⊔ span K (Rf '' (G1 : Set Reg)ᶜ) :=
      hsum ▸ mem_sup_left (subset_span ⟨g, hg, rfl⟩)
    exact (mem_iff_proj B _ U π hBU hπB hπ _ (hU g hg).1 hx).2 (hU g hg).2

/-- Independent targets (B ⊓ N = ⊥; true on #7623, whose 1501 public target rows have rank 1501):
the third clause is vacuous, and (ii) is "every V-ender row lies in the span of the V targets". -/
theorem rank_law_indep (s : St K Reg C) (T : Finset Reg) (evs : List (Ev K Reg C))
    (hL : Legal z V s evs) (hN : ∀ e ∈ evs, NZ e) (hG : Good s T) (hS : Sp s = TS T)
    (Rf : Reg → Reg → K) (G1 : Finset Reg)
    (hNon : ∀ r ∉ G1, (run s evs).row r = Rf r)
    (hTgt : span K (Set.range Rf) = TS (tokRun T evs))
    (hBN : span K (Rf '' (G1 : Set Reg)) ⊓ span K (Rf '' (G1 : Set Reg)ᶜ) = ⊥) :
    VMix (run s evs).row Rf G1 ↔ ¬ Loss s evs ∧
      ∀ g ∈ G1, (run s evs).row g ∈ span K (Rf '' (G1 : Set Reg)) := by
  rw [rank_law_gen z V s T evs hL hN hG hS Rf G1 hNon hTgt, hBN]
  simp

/-- Consistency: the original `rank_law` (U ⊓ N = ⊥) is `rank_law_proj` with π = 0. -/
theorem rank_law_of_gen (s : St K Reg C) (T : Finset Reg) (evs : List (Ev K Reg C))
    (hL : Legal z V s evs) (hN : ∀ e ∈ evs, NZ e) (hG : Good s T) (hS : Sp s = TS T)
    (Rf : Reg → Reg → K) (G1 : Finset Reg) (U : Submodule K (Reg → K))
    (hNon : ∀ r ∉ G1, (run s evs).row r = Rf r)
    (hTgt : span K (Set.range Rf) = TS (tokRun T evs))
    (hRU : ∀ g ∈ G1, Rf g ∈ U)
    (hUN : U ⊓ span K (Rf '' (G1 : Set Reg)ᶜ) = ⊥) :
    VMix (run s evs).row Rf G1 ↔ ¬ Loss s evs ∧ ∀ g ∈ G1, (run s evs).row g ∈ U := by
  have hBU : span K (Rf '' (G1 : Set Reg)) ≤ U :=
    span_le.2 (by rintro _ ⟨g, hg, rfl⟩; exact hRU g hg)
  have hBN : span K (Rf '' (G1 : Set Reg)) ⊓ span K (Rf '' (G1 : Set Reg)ᶜ) = ⊥ :=
    eq_bot_iff.2 (fun x hx => hUN ▸ ⟨hBU hx.1, hx.2⟩)
  rw [rank_law_proj (M' := K) z V s T evs hL hN hG hS Rf G1 U 0 hNon hTgt hRU (by simp)
    (by simp [hUN]), hBN]
  simp

end Run
end RankLawC
