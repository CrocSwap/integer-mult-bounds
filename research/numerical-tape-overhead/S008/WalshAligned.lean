import S008.ModularWalshExact
import Mathlib.Algebra.BigOperators.Intervals
import Mathlib.Data.Nat.Choose.Basic

/-! Common denominators of a Lagrange row and specialization to the existing Walsh token. -/
namespace Moonshot.AlignedWalsh

open Finset Moonshot.CompactSpecialization

/-- Absolute spacing on distinct labels. At the distinguished label the empty factor is one. -/
def spacing (i j : ℕ) : ℕ := if j = i then 1 else if j < i then i-j else j-i

private theorem factorial_prod (n : ℕ) : (∏ j ∈ range n, (j+1)) = n.factorial := by
  induction n with
  | zero => simp
  | succ n ih => rw [prod_range_succ, ih, Nat.factorial_succ, mul_comm]

private theorem lower_prod (i : ℕ) : (∏ j ∈ range i, spacing i j) = i.factorial := by
  calc
    _ = ∏ j ∈ range i, ((i-1-j)+1) := by
      apply prod_congr rfl
      intro j hj
      have h := mem_range.mp hj
      simp only [spacing, ite_eq_right (Nat.ne_of_lt h), ite_eq_left h]
      omega
    _ = ∏ j ∈ range i, (j+1) := prod_range_reflect (fun j => j+1) i
    _ = _ := factorial_prod i

theorem full_spacing_product (i u : ℕ) :
    (∏ j ∈ range (i+u+1), spacing i j) = i.factorial * u.factorial := by
  induction u with
  | zero =>
    simp only [Nat.add_zero, prod_range_succ, lower_prod, Nat.factorial_zero, mul_one]
    simp [spacing]
  | succ u ih =>
    rw [show i + (u+1) + 1 = (i+u+1)+1 by omega, prod_range_succ, ih, Nat.factorial_succ]
    have hi : i < i+u+1 := by omega
    have hsp : spacing i (i+u+1) = u+1 := by
      simp only [spacing, ite_eq_right (Nat.ne_of_gt hi), ite_eq_right (Nat.not_lt_of_ge (Nat.le_of_lt hi))]
      omega
    rw [hsp]
    ac_rfl

/-- The denominator of any actual subset row divides one factorial independent of the subset. -/
theorem subset_spacing_dvd_factorial {W i : ℕ} (hi : i < W) (J : Finset ℕ)
    (hJ : J ⊆ range W) : (∏ j ∈ J, spacing i j) ∣ (W-1).factorial := by
  have hfull := full_spacing_product i (W-1-i)
  rw [show i+(W-1-i)+1=W by omega] at hfull
  refine (prod_dvd_prod_of_subset J (range W) (spacing i) hJ).trans ?_
  rw [hfull]
  exact Nat.factorial_mul_factorial_dvd_factorial (by omega)

/-- The signed denominator in the monomial coefficients of a Lagrange row. -/
def orientedSpacing (i j : ℕ) : ℤ := if i < j then -(spacing i j : ℤ) else spacing i j

theorem oriented_spacing_eq (i j : ℕ) :
    orientedSpacing i j = if i = j then 1 else (i : ℤ) - j := by
  unfold orientedSpacing spacing
  split_ifs <;> omega

private theorem oriented_prod_abs (J : Finset ℕ) (i : ℕ) :
    (∏ j ∈ J, orientedSpacing i j).natAbs = ∏ j ∈ J, spacing i j := by
  induction J using Finset.induction_on with
  | empty => simp
  | @insert j J h ih =>
    rw [prod_insert h, Int.natAbs_mul, ih, prod_insert h]
    by_cases hij : i < j <;> simp [orientedSpacing, hij]

/-- The reduced denominator of each actual row coefficient divides (W-1)!. Its numerator
may be any integer, in particular a monomial coefficient of the product of the (W X-j). -/
theorem lagrange_den_dvd {W i : ℕ} (hi : i < W) (J : Finset ℕ) (hJ : J ⊆ range W) (p : ℤ) :
    ((p : ℚ) / ((∏ j ∈ J, orientedSpacing i j : ℤ) : ℚ)).den ∣ (W-1).factorial := by
  have h := Int.natCast_dvd.mp (Rat.den_dvd p (∏ j ∈ J, orientedSpacing i j))
  rw [Rat.divInt_eq_div, oriented_prod_abs] at h
  exact h.trans (subset_spacing_dvd_factorial hi J hJ)

private theorem sum_den_dvd {ι : Type*} (J : Finset ι) (v : ι → ℚ) (D : ℕ)
    (h : ∀ i ∈ J, (v i).den ∣ D) : (∑ i ∈ J, v i).den ∣ D := by
  classical
  induction J using Finset.induction_on with
  | empty => simp
  | @insert i J hi ih =>
    rw [sum_insert hi]
    exact (Rat.add_den_dvd_lcm _ _).trans (Nat.lcm_dvd (h i (mem_insert_self ..))
      (ih (fun j hj => h j (mem_insert_of_mem hj))))

/-- A modulus numerator F²G simultaneously clears the full two-sided inverse table. -/
theorem repair_entry_den_dvd {W G : ℕ} (J : Finset ℕ) (hJ : J ⊆ range W)
    (p q g : ℕ → ℤ) (hg : ∀ i ∈ J, (g i).natAbs ∣ G) (hn : ∀ i ∈ J, g i ≠ 0) :
    let row (u : ℕ → ℤ) (i : ℕ) : ℚ :=
      (u i : ℚ) / ((∏ j ∈ J, orientedSpacing i j : ℤ) : ℚ)
    (∑ i ∈ J, row p i * (g i : ℚ)⁻¹ * row q i).den ∣ (W-1).factorial^2 * G := by
  dsimp only
  apply sum_den_dvd
  intro i hi
  have hw := mem_range.mp (hJ hi)
  have hq := lagrange_den_dvd hw J hJ (q i)
  have hp := lagrange_den_dvd hw J hJ (p i)
  have hgi : (g i : ℚ)⁻¹.den ∣ G := by simpa [Rat.inv_intCast_den, hn i hi] using hg i hi
  apply (Rat.mul_den_dvd _ _).trans
  apply (Nat.mul_dvd_mul (Rat.mul_den_dvd _ _) dvd_rfl).trans
  convert Nat.mul_dvd_mul (Nat.mul_dvd_mul hp hgi) hq using 1
  ring

/-- The actual single short subtraction, including the zero branch. -/
def shortCorrection (b z : ℕ) : ℕ := if z % b = 0 then 0 else b - z % b

theorem correction_eq_short {U e b : ℕ} (hb : 0 < b) (hd : b ∣ U) (z : ℕ) :
    correction (modulus U e) b z = shortCorrection b z := by
  let _ : NeZero b := ⟨Nat.ne_of_gt hb⟩
  have hU : (U : ZMod b) = 0 := (ZMod.natCast_eq_zero_iff ..).2 hd
  have hM : ((modulus U e : ℕ) : ZMod b) = 1 := by simp [modulus, hU]
  rw [correction, hM, ZMod.inv_one, mul_one, ZMod.neg_val']
  rw [ZMod.val_natCast, shortCorrection]
  split_ifs with hr
  · simp [hr]
  · exact Nat.mod_eq_of_lt (Nat.sub_lt hb (Nat.pos_of_ne_zero hr))

/-- The short subtraction and one exact quotient are the canonical source rational scalar. -/
theorem aligned_scalar_token {U e b : ℕ} (hb : 0 < b) (hd : b ∣ U) (a : ℤ) (x : ℕ) :
    let M := modulus U e
    let z := (((a : ZMod M) * x).val)
    let y := (z + shortCorrection b z * M)/b
    y < M ∧ (b : ZMod M) * (y : ZMod M) = (a : ZMod M) * (x : ZMod M) ∧
      SourceTicket M (((a : ℚ)*x)/b) (y : ZMod M) := by
  dsimp only
  rw [← correction_eq_short (e := e) hb hd]
  exact scalar_spec (e := e) (t := 1) hb (by simpa using hd) a x

end Moonshot.AlignedWalsh
