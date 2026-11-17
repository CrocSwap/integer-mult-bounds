/-
WHOLEFLOOR R3: slack-rank decomposition I_C = F_stay ⊕ E_BL ⊕ K_C, dim K_C ≤ σ_C.
Lane LEAN-NEXT22, Nov 16. See WFCount.md.
-/
import Nov15.WFCount

set_option linter.unusedSectionVars false

namespace WFSlack
open Submodule Module

section Alg
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]

/-- Abstract slack decomposition: `F, E ≤ I` independent, `I` spanned by at most `g` vectors.
Then `I = F ⊕ E ⊕ Kc` with `dim Kc = dim I - dim F - dim E ≤ g - dim F - dim E`. -/
theorem slack_decomp (I F E : Submodule K V) [FiniteDimensional K I]
    (hF : F ≤ I) (hE : E ≤ I) (hFE : Disjoint F E) :
    ∃ Kc : Submodule K V, Kc ≤ I ∧ Disjoint (F ⊔ E) Kc ∧ F ⊔ E ⊔ Kc = I ∧
      finrank K Kc + (finrank K F + finrank K E) = finrank K I := by
  have hle : F ⊔ E ≤ I := sup_le hF hE
  obtain ⟨B, hB⟩ := Submodule.exists_isCompl ((F ⊔ E).comap I.subtype)
  refine ⟨B.map I.subtype, ?_, ?_, ?_, ?_⟩
  · rintro _ ⟨y, _, rfl⟩; exact y.2
  · rw [Submodule.disjoint_def]
    rintro x hx ⟨y, hy, rfl⟩
    have hyA : y ∈ (F ⊔ E).comap I.subtype := hx
    have : y = 0 := by
      have := Submodule.disjoint_def.1 hB.disjoint y hyA hy
      exact this
    simp [this]
  · apply le_antisymm
    · exact sup_le hle (by rintro _ ⟨y, _, rfl⟩; exact y.2)
    · intro x hx
      have hx' : (⟨x, hx⟩ : I) ∈ (⊤ : Submodule K I) := trivial
      rw [← hB.sup_eq_top] at hx'
      obtain ⟨a, ha, b, hb, hab⟩ := Submodule.mem_sup.1 hx'
      have : x = a.1 + b.1 := by
        have := congrArg Subtype.val hab; simpa using this.symm
      rw [this]
      have ha' : a.1 ∈ F ⊔ E := ha
      exact add_mem (Submodule.mem_sup_left ha') (Submodule.mem_sup_right (Submodule.mem_map_of_mem hb))
  · have h1 := Submodule.finrank_add_eq_of_isCompl hB
    have h2 : finrank K B = finrank K (B.map I.subtype) :=
      LinearEquiv.finrank_eq (Submodule.equivMapOfInjective I.subtype I.injective_subtype B)
    have h3 : finrank K ((F ⊔ E).comap I.subtype) = finrank K ↥(F ⊔ E) :=
      LinearEquiv.finrank_eq (Submodule.comapSubtypeEquivOfLe hle)
    haveI : FiniteDimensional K F := Submodule.finiteDimensional_of_le hF
    haveI : FiniteDimensional K E := Submodule.finiteDimensional_of_le hE
    have h4 : finrank K ↥(F ⊔ E) = finrank K F + finrank K E := by
      have := Submodule.finrank_sup_add_finrank_inf_eq F E
      rw [hFE.eq_bot] at this
      simpa using this
    omega

end Alg

section Model
open TokenCancel WFCount
variable {K Reg C : Type*} [Field K] [DecidableEq Reg] [DecidableEq C] [Preorder C] [Fintype Reg]

/-- **Slack-rank lemma, model form (WHOLEFLOOR R3 §2).** Region `D` (one chart or any chart set).
`I` = span of the generators (births in `D` and rows at entries into `D`); by CS every row ever in
`D` is in `I`. `F` = any subspace of the final rows of registers ending in `D`, `E` ≤ span of the
birth rows in `D`; they are assumed independent. If `#generators ≤ dim F + dim E + σ` then
`I = F ⊕ E ⊕ Kc` with `dim Kc ≤ σ`. (The paper's identity `#gens = dim(F ⊕ E) + s_C + o_C` is a
counting fact about passers, NOT formalized here; it enters as `hcount`.) -/
theorem slack_rank_model (Own : Reg → Prop) (D : Set C)
    (evs : List (Ev K Reg C)) (hL : LegalW Own start evs)
    (F E : Submodule K (Reg → K))
    (hFfin : F ≤ span K {v | ∃ r c, (run start evs).loc r = some c ∧ c ∈ D ∧
        v = (run start evs).row r})
    (hE : E ≤ span K {v | ∃ i c, Ev.born i c ∈ evs ∧ c ∈ D ∧ v = Pi.single i 1})
    (hFE : Disjoint F E) (σ : ℕ)
    (hcount : (gens (fun c0 c => c0 ∉ D ∧ c ∈ D) (fun c => c ∈ D) start evs).length ≤
        finrank K F + finrank K E + σ) :
    ∃ Kc : Submodule K (Reg → K),
      Kc ≤ gspan (gens (fun c0 c => c0 ∉ D ∧ c ∈ D) (fun c => c ∈ D) start evs) ∧
      Disjoint (F ⊔ E) Kc ∧
      F ⊔ E ⊔ Kc = gspan (gens (fun c0 c => c0 ∉ D ∧ c ∈ D) (fun c => c ∈ D) start evs) ∧
      finrank K Kc ≤ σ := by
  set P : C → C → Prop := fun c0 c => c0 ∉ D ∧ c ∈ D with hPdef
  set B : C → Prop := fun c => c ∈ D with hBdef
  set L := gens P B start evs with hLdef
  have hcov : Cov D (gspan L) (run start evs) :=
    CS_run Own D P B (fun c0 c h0 hc => ⟨h0, hc⟩) (fun c hc => hc) evs hL
  have hFI : F ≤ gspan L := by
    refine hFfin.trans ?_
    rw [Submodule.span_le]
    rintro _ ⟨r, c, hl, hc, rfl⟩
    exact hcov r c hl hc
  have hBs : span K {v | ∃ i c, Ev.born i c ∈ evs ∧ c ∈ D ∧ v = Pi.single i 1} ≤ gspan L := by
    rw [Submodule.span_le]
    rintro _ ⟨i, c, hm, hc, rfl⟩
    obtain ⟨g, hg, hr⟩ := born_mem_gens P B i c hc evs start hm
    exact Submodule.subset_span ⟨g, hg, hr⟩
  have hEI : E ≤ gspan L := hE.trans hBs
  obtain ⟨Kc, hKI, hdis, hsup, hdim⟩ := slack_decomp (gspan L) F E hFI hEI hFE
  have hsp : gspan L = span K {v | v ∈ L.map Gen.row} := by
    unfold gspan; congr 1; ext v; simp
  have h2 : finrank K ↥(gspan L) ≤ L.length := by
    rw [hsp]; simpa using finrank_span_list_le (K := K) (L.map Gen.row)
  exact ⟨Kc, hKI, hdis, hsup, by omega⟩

end Model

end WFSlack

#print axioms WFSlack.slack_decomp
#print axioms WFSlack.slack_rank_model
