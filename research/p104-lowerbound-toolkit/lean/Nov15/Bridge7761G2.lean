/-
Bridge7761G2 (lane LEAN-BRIDGE4, Nov 18).  #7761 charts as `Submodule (ZMod 2) V`, and the HSContract-shaped facts about
(ChA7761, ChB7761, piF, O7761) (Bridge7761G1): finrank of every chart = its packed height, π involution/injective, hsupp,
Ehi/Elo = 104 + 104 fields with the (1→9 | 0→8) height data, nonzero partner entries.
All checks are decide +kernel on O(1)-lookup packed data.  Kernel only.
-/
import Nov15.Bridge7761G1
import Nov15.Bridge7761Chart
import Nov15.Bridge7761D4

namespace Bridge7761
open Finset Module BankWireC BankFlagB BankNC0

def echB (B P : List ℕ) : Bool := decide (ech B P)
theorem len_chBasis : chBasis.length = 1099 := by decide +kernel
theorem len_chPiv : chPiv.length = 1099 := by decide +kernel
theorem ech_zip : (chBasis.zip chPiv).all (fun p => echB p.1 p.2) = true := by decide +kernel

theorem ech_get (c : ℕ) (hc : c < 1099) : ech (chBasis.getD c []) (chPiv.getD c []) := by
  have h1 : c < chBasis.length := by rw [len_chBasis]; exact hc
  have h2 : c < chPiv.length := by rw [len_chPiv]; exact hc
  have h3 : c < (chBasis.zip chPiv).length := by simp [List.length_zip]; omega
  have := List.all_eq_true.1 ech_zip _ (List.getElem_mem h3)
  rw [List.getElem_zip] at this
  simp only [echB, decide_eq_true_eq] at this
  rw [List.getD_eq_getElem _ _ h1, List.getD_eq_getElem _ _ h2]; exact this

def chartOf (c : ℕ) : Submodule (ZMod 2) V := cht (chBasis.getD c [])

theorem finrank_chartOf (c : ℕ) (hc : c < 1099) : (finrank (ZMod 2) (chartOf c) : ℤ) = hp c := by
  unfold chartOf; rw [finrank_cht (ech_get c hc)]
  have := hp_eq c; rw [Nat.mod_eq_of_lt hc] at this; unfold hgt at this; exact this

def ChA7761 (f : Fin 1262) : Submodule (ZMod 2) V := chartOf (sl FAK 11 f)
def ChB7761 (f : Fin 1262) : Submodule (ZMod 2) V := chartOf (sl FBK 11 f)
def piF (f : Fin 1262) : Fin 1262 := fin1262 (pip f)

theorem fA_lt (i : ℕ) (hi : i < 1262) : sl FAK 11 i < 1099 := by
  rw [← pack_fA, pkw_get 11 fA lt_fA', List.getD_eq_getElem _ _ (by rw [len_fA]; exact hi)]
  exact lt_fA _ (List.getElem_mem _)
theorem fB_lt (i : ℕ) (hi : i < 1262) : sl FBK 11 i < 1099 := by
  rw [← pack_fB, pkw_get 11 fB lt_fB', List.getD_eq_getElem _ _ (by rw [len_fB]; exact hi)]
  exact lt_fB _ (List.getElem_mem _)

theorem finrank_A (f : Fin 1262) : (finrank (ZMod 2) (ChA7761 f) : ℤ) = hp (sl FAK 11 f) :=
  finrank_chartOf _ (fA_lt f f.2)
theorem finrank_B (f : Fin 1262) : (finrank (ZMod 2) (ChB7761 f) : ℤ) = hp (sl FBK 11 f) :=
  finrank_chartOf _ (fB_lt f f.2)

theorem pi_inv : ∀ i < 1262, pip i < 1262 ∧ pip (pip i) = i := by decide +kernel

theorem piF_val (f : Fin 1262) : (piF f : ℕ) = pip f := by
  show pip f % 1262 = pip f; exact Nat.mod_eq_of_lt (pi_inv f f.2).1
theorem piF_piF (f : Fin 1262) : piF (piF f) = f := by
  apply Fin.ext; rw [piF_val, piF_val, (pi_inv f f.2).2]
theorem piF_inj : Function.Injective piF := fun a b h => by
  rw [← piF_piF a, h, piF_piF]

theorem hsupp7761 (f g : Fin 1262) (h : O7761 f g ≠ 0) : g = f ∨ g = piF f := by
  unfold O7761 funcMat at h
  by_cases hg : g = f
  · exact Or.inl hg
  · rw [if_neg hg] at h
    right
    by_cases hp' : pOpt f = some g
    · unfold pOpt at hp'
      by_cases ho : oov f ≠ 0
      · rw [if_pos ho] at hp'; exact (Option.some.inj hp').symm
      · rw [if_neg ho] at hp'; exact absurd hp' (by simp)
    · rw [if_neg hp'] at h; exact absurd rfl h

theorem hs_hi : ∀ e ∈ hsEhi, e < 1262 ∧ oov e ≠ 0 ∧ pip e ≠ e ∧
    hp (sl FAK 11 e) = 1 ∧ hp (sl FBK 11 e) = 9 ∧ hp (sl FAK 11 (pip e)) = 0 ∧ hp (sl FBK 11 (pip e)) = 8 := by
  decide +kernel
theorem hs_lo : ∀ e ∈ hsElo, e < 1262 ∧ oov e ≠ 0 ∧ pip e ≠ e ∧
    hp (sl FAK 11 e) = 0 ∧ hp (sl FBK 11 e) = 8 ∧ hp (sl FAK 11 (pip e)) = 1 ∧ hp (sl FBK 11 (pip e)) = 9 := by
  decide +kernel

theorem nd_hi : (hsEhi.map fin1262).Nodup := by decide +kernel
theorem nd_lo : (hsElo.map fin1262).Nodup := by decide +kernel
theorem len_hi : hsEhi.length = 104 := by decide +kernel
theorem len_lo : hsElo.length = 104 := by decide +kernel

def Ehi7761 : Finset (Fin 1262) := (hsEhi.map fin1262).toFinset
def Elo7761 : Finset (Fin 1262) := (hsElo.map fin1262).toFinset

theorem Ehi_card : Ehi7761.card = 104 := by
  unfold Ehi7761; rw [List.toFinset_card_of_nodup nd_hi, List.length_map, len_hi]
theorem Elo_card : Elo7761.card = 104 := by
  unfold Elo7761; rw [List.toFinset_card_of_nodup nd_lo, List.length_map, len_lo]

theorem mem_hi {e : Fin 1262} (h : e ∈ Ehi7761) : (e : ℕ) ∈ hsEhi := by
  unfold Ehi7761 at h; simp only [List.mem_toFinset, List.mem_map] at h
  obtain ⟨x, hx, rfl⟩ := h
  have := (hs_hi x hx).1
  show x % 1262 ∈ hsEhi; rwa [Nat.mod_eq_of_lt this]
theorem mem_lo {e : Fin 1262} (h : e ∈ Elo7761) : (e : ℕ) ∈ hsElo := by
  unfold Elo7761 at h; simp only [List.mem_toFinset, List.mem_map] at h
  obtain ⟨x, hx, rfl⟩ := h
  have := (hs_lo x hx).1
  show x % 1262 ∈ hsElo; rwa [Nat.mod_eq_of_lt this]

theorem O_pi (e : Fin 1262) (ho : oov e ≠ 0) (hne : pip e ≠ e) : O7761 e (piF e) = oov e := by
  have hne' : piF e ≠ e := fun h => hne (by rw [← piF_val, h])
  unfold O7761 funcMat
  rw [if_neg hne', if_pos]
  unfold pOpt; rw [if_pos ho]; rfl

theorem hi_h7761 : ∀ e ∈ Ehi7761, finrank (ZMod 2) (ChA7761 e) = 1 ∧ finrank (ZMod 2) (ChB7761 e) = 9 ∧
    finrank (ZMod 2) (ChA7761 (piF e)) = 0 ∧ finrank (ZMod 2) (ChB7761 (piF e)) = 8 := by
  intro e he
  obtain ⟨h0, h1, h2, h3, h4, h5, h6⟩ := hs_hi _ (mem_hi he)
  have a1 := finrank_A e; have a2 := finrank_B e; have a3 := finrank_A (piF e); have a4 := finrank_B (piF e)
  rw [piF_val] at a3 a4
  rw [h3] at a1; rw [h4] at a2; rw [h5] at a3; rw [h6] at a4
  refine ⟨?_, ?_, ?_, ?_⟩ <;> omega
theorem lo_h7761 : ∀ e ∈ Elo7761, finrank (ZMod 2) (ChA7761 e) = 0 ∧ finrank (ZMod 2) (ChB7761 e) = 8 ∧
    finrank (ZMod 2) (ChA7761 (piF e)) = 1 ∧ finrank (ZMod 2) (ChB7761 (piF e)) = 9 := by
  intro e he
  obtain ⟨h0, h1, h2, h3, h4, h5, h6⟩ := hs_lo _ (mem_lo he)
  have a1 := finrank_A e; have a2 := finrank_B e; have a3 := finrank_A (piF e); have a4 := finrank_B (piF e)
  rw [piF_val] at a3 a4
  rw [h3] at a1; rw [h4] at a2; rw [h5] at a3; rw [h6] at a4
  refine ⟨?_, ?_, ?_, ?_⟩ <;> omega

theorem nz_hi7761 : ∀ e ∈ Ehi7761, O7761 e (piF e) ≠ 0 := fun e he => by
  obtain ⟨_, h1, h2, _⟩ := hs_hi _ (mem_hi he); rw [O_pi e h1 h2]; exact h1
theorem nz_lo7761 : ∀ e ∈ Elo7761, O7761 e (piF e) ≠ 0 := fun e he => by
  obtain ⟨_, h1, h2, _⟩ := hs_lo _ (mem_lo he); rw [O_pi e h1 h2]; exact h1

end Bridge7761
#print axioms Bridge7761.hi_h7761
#print axioms Bridge7761.lo_h7761
#print axioms Bridge7761.nz_lo7761
#print axioms Bridge7761.hsupp7761
