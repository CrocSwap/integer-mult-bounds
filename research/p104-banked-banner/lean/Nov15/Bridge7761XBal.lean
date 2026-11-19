/-
Bridge7761XBal .  Data part (XB0 holds the model): for #7761's `Bridge7761.model` (1099 charts, 5746 banks, 1262 fields,
no owned registers):  W7761 : W = 0 (no owned registers), D_eq/A_eq reductions, X_of_flow_D.  PENDING (kernel memory): Flow, D = 56, A = 9721, Σc = 9665 (python-checked in PBAL/flowchk.py).
Long lists are checked chunk-wise (kernel recursion depth).  Kernel only.
-/
import Nov15.Bridge7761XB0
namespace Bridge7761
open Finset

theorem len_bS : bS.length = 5746 := by decide +kernel
theorem len_bT : bT.length = 5746 := by decide +kernel
theorem len_fA : fA.length = 1262 := by decide +kernel
theorem len_fB : fB.length = 1262 := by decide +kernel

theorem lt_bS0 : ∀ x ∈ bS0, x < 1099 := by decide +kernel
theorem lt_bS1 : ∀ x ∈ bS1, x < 1099 := by decide +kernel
theorem lt_bS2 : ∀ x ∈ bS2, x < 1099 := by decide +kernel
theorem lt_bS3 : ∀ x ∈ bS3, x < 1099 := by decide +kernel
theorem lt_bT0 : ∀ x ∈ bT0, x < 1099 := by decide +kernel
theorem lt_bT1 : ∀ x ∈ bT1, x < 1099 := by decide +kernel
theorem lt_bT2 : ∀ x ∈ bT2, x < 1099 := by decide +kernel
theorem lt_bT3 : ∀ x ∈ bT3, x < 1099 := by decide +kernel
theorem lt_fA : ∀ x ∈ fA, x < 1099 := by decide +kernel
theorem lt_fB : ∀ x ∈ fB, x < 1099 := by decide +kernel

theorem lt_bS : ∀ x ∈ bS, x < 1099 := by
  intro x hx
  simp only [bS, List.mem_append] at hx
  rcases hx with ((h | h) | h) | h
  exacts [lt_bS0 x h, lt_bS1 x h, lt_bS2 x h, lt_bS3 x h]
theorem lt_bT : ∀ x ∈ bT, x < 1099 := by
  intro x hx
  simp only [bT, List.mem_append] at hx
  rcases hx with ((h | h) | h) | h
  exacts [lt_bT0 x h, lt_bT1 x h, lt_bT2 x h, lt_bT3 x h]

theorem W7761 : model.W = 0 := by simp [XBal.Model.W]

/-- bank height change (data level). -/
def dl (i : ℕ) : ℤ := hgt (bT.getD i 0 % 1099) - hgt (bS.getD i 0 % 1099)

theorem sum5746 (g : ℕ → ℤ) : ∑ i ∈ range 5746, g i =
    (∑ i ∈ range 1500, g i) + (∑ i ∈ range 1500, g (1500 + i)) + (∑ i ∈ range 1500, g (3000 + i)) +
    (∑ i ∈ range 1246, g (4500 + i)) := by
  rw [show (5746 : ℕ) = 4500 + 1246 from rfl, Finset.sum_range_add,
    show (4500 : ℕ) = 3000 + 1500 from rfl, Finset.sum_range_add,
    show (3000 : ℕ) = 1500 + 1500 from rfl, Finset.sum_range_add]

theorem D_eq : model.D = ∑ i ∈ range 5746, max (-(dl i)) 0 :=
  Fin.sum_univ_eq_sum_range (fun i => max (-(dl i)) 0) 5746
theorem A_eq : model.A = ∑ i ∈ range 5746, max (dl i) 0 :=
  Fin.sum_univ_eq_sum_range (fun i => max (dl i) 0) 5746

/-- reduction: with Flow and the three data sums, X = 112.  The sums D = 56, A = 9721 are NOT kernel-checked here:
random-access list sums over 5746 banks exceed the 3.5 GB guard (~9 KB kernel memory per list step). -/
theorem X_of_flow_D (hF : model.Flow) (hD : model.D = 56) : model.X = 2 * 56 := by
  rw [XBal.Model.X_eq model hF, W7761, hD]; norm_num

end Bridge7761
