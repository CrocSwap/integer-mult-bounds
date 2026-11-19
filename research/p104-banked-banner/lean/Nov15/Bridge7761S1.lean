/-
Bridge7761S1 .  The BankWireD.Contract of #7761 (14 OUT + 14 IN flag rows) for `Net7761 hO`, conditional on hO only:
  conRO / conRI (Bridge7761S1D, bridgegen/gen7.py): the unique field of each counted row; okO / okI decide-checked on the counted rows
  (chart data: A = [v] / ⊥, B = ⊤ / ker φ_a on the field and its partner, partner entry ≠ 0); chartsO / chartsI turn that into the Submodule equalities
  (cht_single, cht_top, cht_ker, cht_nil); indegO / indegI from π injective.
Kernel only (decide +kernel on data; no sorry / native_decide / axioms).
-/
import Nov15.Bridge7761R5
import Nov15.Bridge7761G2
import Nov15.BankWireD
import Nov15.Bridge7761S1D

namespace Bridge7761
open Finset Module BankNC0 BankWireC BankFlagB BankWireD Submodule

def rowO (i : ℕ) : Fin 1262 := fin1262 (conRO.getD i 0)
def rowI (i : ℕ) : Fin 1262 := fin1262 (conRI.getD i 0)

def kerOk (a : ℕ) (B : List ℕ) : Bool :=
  decide (B.length = 8) && decide (0 < a ∧ a < 512) && B.all (fun b => par a b == 0)

def okO (i : ℕ) : Bool :=
  decide (conRO.getD i 0 < 1262) && decide (chBasis.getD (sl FAK 11 (conRO.getD i 0)) [] = [(OUT.getD i (0, 0)).1]) &&
  decide ((chBasis.getD (sl FBK 11 (conRO.getD i 0)) []).length = 9) &&
  decide (chBasis.getD (sl FAK 11 (pip (conRO.getD i 0))) [] = []) &&
  kerOk (OUT.getD i (0, 0)).2 (chBasis.getD (sl FBK 11 (pip (conRO.getD i 0))) []) &&
  decide (oov (conRO.getD i 0) ≠ 0) && decide (pip (conRO.getD i 0) ≠ conRO.getD i 0)

def okI (i : ℕ) : Bool :=
  decide (conRI.getD i 0 < 1262) && decide (chBasis.getD (sl FAK 11 (conRI.getD i 0)) [] = []) &&
  kerOk (IN.getD i (0, 0)).2 (chBasis.getD (sl FBK 11 (conRI.getD i 0)) []) &&
  decide (chBasis.getD (sl FAK 11 (pip (conRI.getD i 0))) [] = [(IN.getD i (0, 0)).1]) &&
  decide ((chBasis.getD (sl FBK 11 (pip (conRI.getD i 0))) []).length = 9) &&
  decide (oov (conRI.getD i 0) ≠ 0) && decide (pip (conRI.getD i 0) ≠ conRI.getD i 0)

theorem okO_all : ∀ i ∈ cntOUT, okO i = true := by decide +kernel
theorem okI_all : ∀ i ∈ cntIN, okI i = true := by decide +kernel
theorem injO_chk : ∀ i ∈ cntOUT, ∀ i' ∈ cntOUT, conRO.getD i 0 = conRO.getD i' 0 → i = i' := by decide +kernel
theorem injI_chk : ∀ i ∈ cntIN, ∀ i' ∈ cntIN, conRI.getD i 0 = conRI.getD i' 0 → i = i' := by decide +kernel
theorem bit9 : ∀ a < 512, 0 < a → ∃ i : Fin 9, a.testBit i = true := by decide +kernel

theorem val_f (f : ℕ) (hf : f < 1262) : (fin1262 f : ℕ) = f := Nat.mod_eq_of_lt hf
theorem pipv (f : ℕ) (hf : f < 1262) : (piF (fin1262 f) : ℕ) = pip f := by rw [piF_val, val_f f hf]

theorem kerOk_iff {a : ℕ} {B : List ℕ} (h : kerOk a B = true) :
    B.length = 8 ∧ (∃ i : Fin 9, a.testBit i = true) ∧ ∀ b ∈ B, par a b = 0 := by
  simp only [kerOk, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, beq_iff_eq] at h
  obtain ⟨⟨h8, h0, h1⟩, hk⟩ := h
  exact ⟨h8, bit9 a h1 h0, hk⟩

theorem chartsO (f v a : ℕ) (hf : f < 1262) (h1 : chBasis.getD (sl FAK 11 f) [] = [v])
    (h2 : (chBasis.getD (sl FBK 11 f) []).length = 9)
    (h3 : chBasis.getD (sl FAK 11 (pip f)) [] = [])
    (h4 : kerOk a (chBasis.getD (sl FBK 11 (pip f)) []) = true) :
    ChA7761 (fin1262 f) = span (ZMod 2) {vec v} ∧ ChB7761 (fin1262 f) = ⊤ ∧
    ChA7761 (piF (fin1262 f)) = ⊥ ∧ ChB7761 (piF (fin1262 f)) = LinearMap.ker (phi a) := by
  have hv := val_f f hf
  have hp := pipv f hf
  have hpl := (pi_inv f hf).1
  obtain ⟨h8, ha, hk⟩ := kerOk_iff h4
  refine ⟨?_, ?_, ?_, ?_⟩
  · unfold ChA7761 chartOf; rw [hv, h1, cht_single]
  · unfold ChB7761 chartOf; rw [hv]; exact cht_top (ech_get _ (fB_lt f hf)) h2
  · unfold ChA7761 chartOf; rw [hp, h3, cht_nil]
  · unfold ChB7761 chartOf; rw [hp]; exact cht_ker (ech_get _ (fB_lt _ hpl)) h8 ha hk

theorem chartsI (f v a : ℕ) (hf : f < 1262) (h1 : chBasis.getD (sl FAK 11 f) [] = [])
    (h2 : kerOk a (chBasis.getD (sl FBK 11 f) []) = true)
    (h3 : chBasis.getD (sl FAK 11 (pip f)) [] = [v])
    (h4 : (chBasis.getD (sl FBK 11 (pip f)) []).length = 9) :
    ChA7761 (fin1262 f) = ⊥ ∧ ChB7761 (fin1262 f) = LinearMap.ker (phi a) ∧
    ChA7761 (piF (fin1262 f)) = span (ZMod 2) {vec v} ∧ ChB7761 (piF (fin1262 f)) = ⊤ := by
  have hv := val_f f hf
  have hp := pipv f hf
  have hpl := (pi_inv f hf).1
  obtain ⟨h8, ha, hk⟩ := kerOk_iff h2
  refine ⟨?_, ?_, ?_, ?_⟩
  · unfold ChA7761 chartOf; rw [hv, h1, cht_nil]
  · unfold ChB7761 chartOf; rw [hv]; exact cht_ker (ech_get _ (fB_lt f hf)) h8 ha hk
  · unfold ChA7761 chartOf; rw [hp, h3, cht_single]
  · unfold ChB7761 chartOf; rw [hp]; exact cht_top (ech_get _ (fB_lt _ hpl)) h4

theorem okO_elim (i : ℕ) (h : okO i = true) :
    conRO.getD i 0 < 1262 ∧ ChA7761 (rowO i) = span (ZMod 2) {vec (OUT.getD i (0, 0)).1} ∧ ChB7761 (rowO i) = ⊤ ∧
    ChA7761 (piF (rowO i)) = ⊥ ∧ ChB7761 (piF (rowO i)) = LinearMap.ker (phi (OUT.getD i (0, 0)).2) ∧
    O7761 (rowO i) (piF (rowO i)) ≠ 0 := by
  simp only [okO, Bool.and_eq_true, decide_eq_true_eq] at h
  obtain ⟨⟨⟨⟨⟨⟨hf, h1⟩, h2⟩, h3⟩, h4⟩, h5⟩, h6⟩ := h
  have := chartsO _ _ _ hf h1 h2 h3 h4
  refine ⟨hf, this.1, this.2.1, this.2.2.1, this.2.2.2, ?_⟩
  have hv := val_f _ hf
  show O7761 (fin1262 (conRO.getD i 0)) (piF (fin1262 (conRO.getD i 0))) ≠ 0
  rw [O_pi _ (by rw [hv]; exact h5) (by rw [hv]; exact h6)]
  rw [hv]; exact h5

theorem okI_elim (i : ℕ) (h : okI i = true) :
    conRI.getD i 0 < 1262 ∧ ChA7761 (rowI i) = ⊥ ∧ ChB7761 (rowI i) = LinearMap.ker (phi (IN.getD i (0, 0)).2) ∧
    ChA7761 (piF (rowI i)) = span (ZMod 2) {vec (IN.getD i (0, 0)).1} ∧ ChB7761 (piF (rowI i)) = ⊤ ∧
    O7761 (rowI i) (piF (rowI i)) ≠ 0 := by
  simp only [okI, Bool.and_eq_true, decide_eq_true_eq] at h
  obtain ⟨⟨⟨⟨⟨⟨hf, h1⟩, h2⟩, h3⟩, h4⟩, h5⟩, h6⟩ := h
  have := chartsI _ _ _ hf h1 h2 h3 h4
  refine ⟨hf, this.1, this.2.1, this.2.2.1, this.2.2.2, ?_⟩
  have hv := val_f _ hf
  show O7761 (fin1262 (conRI.getD i 0)) (piF (fin1262 (conRI.getD i 0))) ≠ 0
  rw [O_pi _ (by rw [hv]; exact h5) (by rw [hv]; exact h6)]
  rw [hv]; exact h5

noncomputable def Con7761 (hO : ∀ f, outVec Recipe7761 (ofld7761 f) (oref7761 f) = O7761 f) :
    BankWireD.Contract (Net7761 hO) where
  π := piF
  rowO := rowO
  rowI := rowI
  hsupp := fun f g h => hsupp7761 f g h
  injO := fun i hi i' hi' h => by
    rw [out_cnt] at hi hi'
    have a := (okO_elim i (okO_all i hi)).1
    have b := (okO_elim i' (okO_all i' hi')).1
    have h' := congrArg Fin.val h
    unfold rowO at h'
    rw [val_f _ a, val_f _ b] at h'
    exact injO_chk i hi i' hi' h'
  injI := fun i hi i' hi' h => by
    rw [in_cnt] at hi hi'
    have a := (okI_elim i (okI_all i hi)).1
    have b := (okI_elim i' (okI_all i' hi')).1
    have h' := congrArg Fin.val h
    unfold rowI at h'
    rw [val_f _ a, val_f _ b] at h'
    exact injI_chk i hi i' hi' h'
  chartO := fun i hi => by
    rw [out_cnt] at hi
    obtain ⟨-, a, b, c, d, -⟩ := okO_elim i (okO_all i hi)
    exact ⟨a, b, c, d⟩
  chartI := fun i hi => by
    rw [in_cnt] at hi
    obtain ⟨-, a, b, c, d, -⟩ := okI_elim i (okI_all i hi)
    exact ⟨a, b, c, d⟩
  nzO := fun i hi => by
    rw [out_cnt] at hi
    exact (okO_elim i (okO_all i hi)).2.2.2.2.2
  nzI := fun i hi => by
    rw [in_cnt] at hi
    exact (okI_elim i (okI_all i hi)).2.2.2.2.2
  indegO := fun c _ e _ r _ h => piF_inj h
  indegI := fun c _ e _ r _ h => piF_inj h

end Bridge7761
#print axioms Bridge7761.Con7761
