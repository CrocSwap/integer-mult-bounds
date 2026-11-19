/-
Bridge7761O1 .  Chart-locality premises of `BankMed.bank_kappa_lt_banner_tiedS_loc` for #7761
(xin = xi, yout = yo of Bridge7761G3; DF.lq p = vecOf (DW4.lab p)):
  hin7761  : DF.lq p ∈ ChA7761 (xi p)                                  (104 live inputs; inSpanB over the packed chart tables)
  hout7761 : y ∈ ChB7761 (yo s) -> dot (DF.lq s) y = 0                 (B(yo s) has rank 8 and is killed by lab s: cht_ker)
Kernel only.
-/
import Nov15.Bridge7761R2
import Nov15.Bridge7761G3
import Nov15.BankTieC

namespace Bridge7761
open Finset Module BankWireC BankFlagB BankNC0

def hinB (p : ℕ) : Bool :=
  decide (sl FAK 11 (xField.getD p 0) < 1099) &&
    inSpanB (ubL (sl FAK 11 (xField.getD p 0))) (upL (sl FAK 11 (xField.getD p 0))) (DW4.lab p)

theorem hin_chk : (List.range 104).all hinB = true := by decide +kernel

theorem hin7761 (p : Fin 104) : DF.lq p ∈ ChA7761 (xi p) := by
  have h := List.all_eq_true.1 hin_chk p (List.mem_range.2 p.2)
  simp only [hinB, Bool.and_eq_true, decide_eq_true_eq] at h
  have hc := h.1
  have hmem := inSpanB_mem h.2
  rw [(ub_ok _ hc).1] at hmem
  unfold ChA7761 chartOf
  rw [xi_val]
  exact hmem

def houtB (s : ℕ) : Bool :=
  decide (sl FBK 11 (xField.getD s 0 + 112) < 1099) &&
  decide ((ubL (sl FBK 11 (xField.getD s 0 + 112))).length = 8) &&
  (List.range 9).any (fun i => (DW4.lab s).testBit i) &&
  (ubL (sl FBK 11 (xField.getD s 0 + 112))).all (fun b => par (DW4.lab s) b == 0)

theorem hout_chk : (List.range 104).all houtB = true := by decide +kernel

theorem dot_lq_eq_phi (a : ℕ) (y : V) : DecoderWall.dot (DF.vecOf a) y = phi a y := by
  rw [phi_apply]
  unfold DecoderWall.dot DF.vecOf
  rw [dotProduct]
  refine Finset.sum_congr rfl fun i _ => ?_
  by_cases h : a.testBit i <;> simp [h]

theorem hout7761 (s : Fin 104) : ∀ y ∈ ChB7761 (yo s), DecoderWall.dot (DF.lq s) y = 0 := by
  have h := List.all_eq_true.1 hout_chk s (List.mem_range.2 s.2)
  simp only [houtB, Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq, List.all_eq_true, List.any_eq_true,
    List.mem_range] at h
  obtain ⟨⟨⟨hc, h8⟩, ⟨i, hi9, hi⟩⟩, hk⟩ := h
  have hub := ub_ok _ hc
  have hech := ech_get _ hc
  intro y hy
  unfold ChB7761 chartOf at hy
  rw [yo_val] at hy
  unfold xf at hy
  have hk' : ∀ b ∈ chBasis.getD (sl FBK 11 (xField.getD s 0 + 112)) [], par (DW4.lab s) b = 0 := by
    rw [← hub.1]; exact hk
  have hker := cht_ker hech (by rw [← hub.1]; exact h8) (a := DW4.lab s) ⟨⟨i, hi9⟩, hi⟩ hk'
  rw [hker] at hy
  have h0 : phi (DW4.lab s) y = 0 := hy
  unfold DF.lq
  rw [dot_lq_eq_phi]; exact h0

end Bridge7761
#print axioms Bridge7761.hin7761
#print axioms Bridge7761.hout7761
