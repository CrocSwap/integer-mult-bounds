/-
Bridge7761G3 .  The output spec of #7761 on the 104 live pairs, for `O7761` (Bridge7761G1):
xi t = xField t (input field), yo t = xField t + 112 (output field) :
  computes7761 : c t := oov (yo t) ≠ 0,  O (yo t)(xi t) = c t,  and O (yo s)(xi t) = 0 for ALL t ≠ s   (this is `BankTie.ComputesS`, BankTieC)
  c t = 1 for 96 pairs and 1/2 for 8 (cdist, decide).
Kernel only.
-/
import Nov15.Bridge7761G2

namespace Bridge7761
open Finset Module BankNC0

theorem len_xField : xField.length = 104 := by decide +kernel
theorem nd_xField : xField.Nodup := by decide +kernel
theorem xf_data : ∀ x ∈ xField, x < 112 ∧ oov (x + 112) ≠ 0 ∧ pip (x + 112) = x := by decide +kernel
theorem cdist : (xField.map (fun x => oov (x + 112))).count 1 = 96 ∧
    (xField.map (fun x => oov (x + 112))).count (1 / 2) = 8 := by decide +kernel

def xf (t : Fin 104) : ℕ := xField.getD t 0
theorem xf_mem (t : Fin 104) : xf t ∈ xField := by
  unfold xf; rw [List.getD_eq_getElem _ _ (by rw [len_xField]; exact t.2)]; exact List.getElem_mem _
theorem xf_inj : Function.Injective xf := fun a b h => by
  unfold xf at h
  have ha : (a : ℕ) < xField.length := by rw [len_xField]; exact a.2
  have hb : (b : ℕ) < xField.length := by rw [len_xField]; exact b.2
  rw [List.getD_eq_getElem _ _ ha, List.getD_eq_getElem _ _ hb] at h
  exact Fin.ext ((List.Nodup.getElem_inj_iff nd_xField).1 h)

def xi (t : Fin 104) : Fin 1262 := fin1262 (xf t)
def yo (t : Fin 104) : Fin 1262 := fin1262 (xf t + 112)
def cc (t : Fin 104) : ℚ := oov (xf t + 112)

theorem xf_lt (t : Fin 104) : xf t < 112 := (xf_data _ (xf_mem t)).1
theorem xi_val (t : Fin 104) : (xi t : ℕ) = xf t := Nat.mod_eq_of_lt (by have := xf_lt t; omega)
theorem yo_val (t : Fin 104) : (yo t : ℕ) = xf t + 112 := Nat.mod_eq_of_lt (by have := xf_lt t; omega)

theorem oo_yo (t : Fin 104) : oov (yo t) = oov (xf t + 112) := by
  unfold oov; rw [show (yo t : ℕ) = xf t + 112 from yo_val t]

theorem piF_yo (t : Fin 104) : piF (yo t) = xi t := by
  apply Fin.ext; rw [piF_val, yo_val, xi_val]; exact (xf_data _ (xf_mem t)).2.2

theorem computes7761 : (∀ t, cc t ≠ 0 ∧ O7761 (yo t) (xi t) = cc t) ∧
    ∀ t s, t ≠ s → O7761 (yo s) (xi t) = 0 := by
  refine ⟨fun t => ?_, fun t s hts => ?_⟩
  · have hd := xf_data _ (xf_mem t)
    refine ⟨hd.2.1, ?_⟩
    have := O_pi (yo t) (by rw [oo_yo]; exact hd.2.1) (by rw [← piF_val, piF_yo, xi_val, yo_val]; omega)
    rw [piF_yo] at this; rw [this]; unfold cc; rw [oo_yo]
  · by_contra hne
    rcases hsupp7761 _ _ hne with h | h
    · have := congrArg Fin.val h; rw [xi_val, yo_val] at this; have := xf_lt t; omega
    · rw [piF_yo] at h
      exact hts (xf_inj (by have := congrArg Fin.val h; rw [xi_val, xi_val] at this; exact this))

end Bridge7761
#print axioms Bridge7761.computes7761
