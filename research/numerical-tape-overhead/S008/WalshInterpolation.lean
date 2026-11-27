import S008.WalshAligned
import Mathlib.Algebra.Polynomial.BigOperators
import Mathlib.Algebra.Polynomial.Eval.Coeff
import Mathlib.Algebra.Polynomial.Degree.Lemmas

/-! The actual monomial coefficients of the Lagrange correction, its full faulty-row
check/table/lift identity, and the unreduced table entry's original OAI scalar ticket. -/
namespace Moonshot.AlignedWalsh

open Finset Polynomial

noncomputable def intRowNumerator (W : ℕ) (J : Finset ℕ) (i : ℕ) : ℤ[X] :=
  ∏ j ∈ J.erase i, (C (W : ℤ) * X - C (j : ℤ))

def rowDivisor (J : Finset ℕ) (i : ℕ) : ℤ :=
  ∏ j ∈ J, orientedSpacing i j

noncomputable def rationalRow (W : ℕ) (J : Finset ℕ) (i : ℕ) : ℚ[X] :=
  C (rowDivisor J i : ℚ)⁻¹ * (intRowNumerator W J i).map (Int.castRingHom ℚ)

def node (W i : ℕ) : ℚ := i / (W : ℚ)

theorem rationalRow_coeff (W : ℕ) (J : Finset ℕ) (i r : ℕ) :
    (rationalRow W J i).coeff r =
      (((intRowNumerator W J i).coeff r : ℤ) : ℚ) / (rowDivisor J i : ℚ) := by
  simp [rationalRow, coeff_map, div_eq_mul_inv, mul_comm]

private theorem mappedNumerator_at {W : ℕ} (hW : 0 < W) (J : Finset ℕ) (i t : ℕ) :
    eval (node W t) ((intRowNumerator W J i).map (Int.castRingHom ℚ)) =
      ∏ j ∈ J.erase i, ((t : ℚ)-j) := by
  classical
  have hn : (W : ℚ) ≠ 0 := by exact_mod_cast (Nat.ne_of_gt hW)
  have hx : (W : ℚ) * (t / (W : ℚ)) = t := by field_simp
  simp [intRowNumerator, Polynomial.map_prod, Polynomial.eval_prod, node, hx]

private theorem rowDivisor_cast (J : Finset ℕ) (i : ℕ) :
    (rowDivisor J i : ℚ) = ∏ j ∈ J.erase i, ((i : ℚ)-j) := by
  classical
  have he := Finset.prod_erase J (f := orientedSpacing i) (a := i)
    (by simp [oriented_spacing_eq])
  unfold rowDivisor
  rw [← he]
  push_cast
  apply prod_congr rfl
  intro j hj
  simp [oriented_spacing_eq, Ne.symm (mem_erase.mp hj).1]

theorem rationalRow_eval {W : ℕ} (hW : 0 < W) (J : Finset ℕ) (i t : ℕ) (ht : t ∈ J) :
    (rationalRow W J i).eval (node W t) = if i = t then 1 else 0 := by
  classical
  rw [rationalRow, eval_mul, eval_C, mappedNumerator_at hW, rowDivisor_cast]
  split_ifs with he
  · subst t
    apply inv_mul_cancel₀
    apply prod_ne_zero_iff.mpr
    intro j hj
    exact sub_ne_zero.mpr (by exact_mod_cast (mem_erase.mp hj).1.symm)
  · have hz : (∏ j ∈ J.erase i, ((t : ℚ)-j)) = 0 := by
      exact prod_eq_zero (mem_erase.mpr ⟨Ne.symm he, ht⟩) (sub_self _)
    rw [hz, mul_zero]

private theorem intRow_natDegree (W : ℕ) (J : Finset ℕ) (i : ℕ) :
    (intRowNumerator W J i).natDegree ≤ (J.erase i).card := by
  classical
  unfold intRowNumerator
  calc
    _ ≤ ∑ j ∈ J.erase i, (C (W : ℤ) * X - C (j : ℤ)).natDegree := natDegree_prod_le _ _
    _ ≤ ∑ _j ∈ J.erase i, 1 := by
      apply sum_le_sum
      intro j hj
      apply (natDegree_sub_le _ _).trans
      apply max_le
      · exact (natDegree_C_mul_le _ _).trans (by simp)
      · simp
    _ = _ := by simp

theorem rationalRow_card (W : ℕ) (J : Finset ℕ) (i : ℕ) (hi : i ∈ J) :
    (rationalRow W J i).natDegree < J.card := by
  calc
    _ ≤ ((intRowNumerator W J i).map (Int.castRingHom ℚ)).natDegree := natDegree_C_mul_le _ _
    _ ≤ (intRowNumerator W J i).natDegree := natDegree_map_le
    _ ≤ (J.erase i).card := intRow_natDegree W J i
    _ < _ := card_erase_lt_of_mem hi

theorem check_row_on_node {W : ℕ} (hW : 0 < W) (J : Finset ℕ) {i t : ℕ}
    (hi : i ∈ J) (ht : t ∈ J) :
    (∑ r ∈ range J.card, (rationalRow W J i).coeff r * (node W t)^r) =
      if i = t then 1 else 0 := by
  rw [← Polynomial.eval_eq_sum_range' (rationalRow_card W J i hi)]
  exact rationalRow_eval hW J i t ht

/-- Entry of the actual factorized inverse-gap column table on its active rank. -/
noncomputable def repairEntry (W : ℕ) (J : Finset ℕ) (g : ℕ → ℤ) (r s : ℕ) : ℚ :=
  ∑ i ∈ J, (rationalRow W J i).coeff r * (g i : ℚ)⁻¹ * (rationalRow W J i).coeff s

theorem actual_entry_den_dvd {W G : ℕ} (J : Finset ℕ) (hJ : J ⊆ range W)
    (g : ℕ → ℤ) (hg : ∀ i ∈ J, (g i).natAbs ∣ G) (hn : ∀ i ∈ J, g i ≠ 0) (r s : ℕ) :
    (repairEntry W J g r s).den ∣ (W-1).factorial^2 * G := by
  simpa only [repairEntry, rationalRow_coeff, rowDivisor] using
    repair_entry_den_dvd J hJ (fun i ↦ (intRowNumerator W J i).coeff r)
      (fun i ↦ (intRowNumerator W J i).coeff s) g hg hn

private theorem entry_on_node {W : ℕ} (hW : 0 < W) (J : Finset ℕ) (g : ℕ → ℤ)
    (r : ℕ) {t : ℕ} (ht : t ∈ J) :
    (∑ s ∈ range J.card, repairEntry W J g r s * (node W t)^s) =
      (rationalRow W J t).coeff r * (g t : ℚ)⁻¹ := by
  classical
  simp_rw [repairEntry, Finset.sum_mul]
  rw [Finset.sum_comm]
  calc
    _ = ∑ i ∈ J, ((rationalRow W J i).coeff r * (g i : ℚ)⁻¹) *
        (if i = t then 1 else 0) := by
      apply sum_congr rfl
      intro i hi
      rw [← check_row_on_node hW J hi ht, Finset.mul_sum]
      exact sum_congr rfl (fun s hs ↦ by ring)
    _ = _ := by simp [mul_ite, ht]

theorem check_congruence {W : ℕ} (hW : 0 < W) (J : Finset ℕ) (g : ℕ → ℤ)
    {i j : ℕ} (hi : i ∈ J) (hj : j ∈ J) :
    (∑ r ∈ range J.card, (node W i)^r *
      (∑ s ∈ range J.card, repairEntry W J g r s * (node W j)^s)) =
      if i = j then (g i : ℚ)⁻¹ else 0 := by
  classical
  simp_rw [entry_on_node hW J g _ hj]
  calc
    _ = (∑ r ∈ range J.card, (rationalRow W J j).coeff r * (node W i)^r) *
        (g j : ℚ)⁻¹ := by
      rw [Finset.sum_mul]
      exact sum_congr rfl (fun r hr ↦ by ring)
    _ = (if j = i then 1 else 0) * (g j : ℚ)⁻¹ := by rw [check_row_on_node hW J hj hi]
    _ = _ := by by_cases h : i = j <;> simp [h, eq_comm]

/-- All active faulty seed values are recovered after the check, table and transposed lift. -/
theorem actual_repair_lift {W : ℕ} (hW : 0 < W) (J : Finset ℕ) (g : ℕ → ℤ)
    (hn : ∀ j ∈ J, g j ≠ 0) (x : ℕ → ℚ) {i : ℕ} (hi : i ∈ J) :
    (∑ r ∈ range J.card, (node W i)^r * (∑ s ∈ range J.card, repairEntry W J g r s *
      (∑ j ∈ J, (node W j)^s * ((g j : ℚ) * x j)))) = x i := by
  classical
  have hright (r : ℕ) :
      (∑ s ∈ range J.card, repairEntry W J g r s *
        (∑ j ∈ J, (node W j)^s * ((g j : ℚ) * x j))) =
        (∑ j ∈ J, (rationalRow W J j).coeff r * x j) := by
    simp_rw [Finset.mul_sum]
    rw [sum_comm]
    apply sum_congr rfl
    intro j hj
    calc
      _ = (∑ s ∈ range J.card, repairEntry W J g r s * (node W j)^s) *
          ((g j : ℚ) * x j) := by
        rw [Finset.sum_mul]
        exact sum_congr rfl (fun s hs ↦ by ring)
      _ = _ := by
        rw [entry_on_node hW J g _ hj]
        have hgj : (g j : ℚ) ≠ 0 := by exact_mod_cast (hn j hj)
        field_simp
  simp_rw [hright, Finset.mul_sum]
  rw [sum_comm]
  calc
    _ = ∑ j ∈ J, (if j = i then 1 else 0) * x j := by
      apply sum_congr rfl
      intro j hj
      rw [← check_row_on_node hW J hj hi, Finset.sum_mul]
      exact sum_congr rfl (fun r hr ↦ by ring)
    _ = _ := by simp [ite_mul, hi]

theorem rowDivisor_dvd {W : ℕ} {i : ℕ} (hi : i < W) (J : Finset ℕ) (hJ : J ⊆ range W) :
    rowDivisor J i ∣ ((W-1).factorial : ℤ) := by
  have ha : (rowDivisor J i).natAbs = ∏ j ∈ J, spacing i j := by
    classical
    clear hJ
    unfold rowDivisor
    induction J using Finset.induction_on with
    | empty => simp
    | @insert j J hj ih =>
      rw [prod_insert hj, Int.natAbs_mul, ih, prod_insert hj]
      by_cases h : i < j <;> simp [orientedSpacing, h]
  apply Int.natAbs_dvd_natAbs.mp
  simpa [ha] using subset_spacing_dvd_factorial hi J hJ

private theorem rowDivisor_nonzeroQ (J : Finset ℕ) (i : ℕ) : (rowDivisor J i : ℚ) ≠ 0 := by
  rw [rowDivisor_cast]
  apply prod_ne_zero_iff.mpr
  intro j hj
  exact sub_ne_zero.mpr (by exact_mod_cast (Ne.symm (mem_erase.mp hj).1))

noncomputable def scaledRowInt (W : ℕ) (J : Finset ℕ) (i r : ℕ) : ℤ :=
  (((W-1).factorial : ℤ) / rowDivisor J i) * (intRowNumerator W J i).coeff r

theorem scaled_row_exact {W : ℕ} (J : Finset ℕ) (hJ : J ⊆ range W)
    {i : ℕ} (hi : i ∈ J) (r : ℕ) :
    (scaledRowInt W J i r : ℚ) = ((W-1).factorial : ℚ) * (rationalRow W J i).coeff r := by
  rw [scaledRowInt, Int.cast_mul, Int.cast_div (rowDivisor_dvd (mem_range.mp (hJ hi)) J hJ)
    (rowDivisor_nonzeroQ J i), rationalRow_coeff, Int.cast_natCast]
  ring

/-- The integer emitted by the frequency-dependent compiler with unreduced denominator F²G. -/
noncomputable def scaledRepairNum (W G : ℕ) (J : Finset ℕ) (g : ℕ → ℤ) (r s : ℕ) : ℤ :=
  ∑ i ∈ J, scaledRowInt W J i r * scaledRowInt W J i s * ((G : ℤ) / g i)

theorem scaled_repair_exact {W G : ℕ} (J : Finset ℕ) (hJ : J ⊆ range W)
    (g : ℕ → ℤ) (hg : ∀ i ∈ J, (g i).natAbs ∣ G) (hn : ∀ i ∈ J, g i ≠ 0) (r s : ℕ) :
    (scaledRepairNum W G J g r s : ℚ) =
      (((W-1).factorial : ℚ)^2 * G) * repairEntry W J g r s := by
  classical
  rw [scaledRepairNum, repairEntry, Int.cast_sum, Finset.mul_sum]
  apply sum_congr rfl
  intro i hi
  have hp : g i ∣ (G : ℤ) := Int.natAbs_dvd_natAbs.mp (by simpa using hg i hi)
  have hni : (g i : ℚ) ≠ 0 := by exact_mod_cast hn i hi
  rw [Int.cast_mul, Int.cast_mul, scaled_row_exact J hJ hi r, scaled_row_exact J hJ hi s,
    Int.cast_div hp hni, Int.cast_natCast]
  ring

open Moonshot.CompactSpecialization

/-- The unreduced scalar supplies the original OAI rational ticket for this table entry. -/
theorem actual_repair_token {W G U e : ℕ} (J : Finset ℕ) (hJ : J ⊆ range W)
    (g : ℕ → ℤ) (hg : ∀ i ∈ J, (g i).natAbs ∣ G) (hn : ∀ i ∈ J, g i ≠ 0)
    (hG : 0 < G) (hU : (W-1).factorial^2 * G ∣ U) (r s x : ℕ) :
    let C := (W-1).factorial^2 * G
    let M := modulus U e
    let N := scaledRepairNum W G J g r s
    let z := (((N : ZMod M) * x).val)
    let Y := (z + shortCorrection C z * M)/C
    Y < M ∧ SourceTicket M (repairEntry W J g r s * x) (Y : ZMod M) := by
  dsimp only
  have hC : 0 < (W - 1).factorial ^ 2 * G := by positivity
  obtain ⟨hl, _, ht⟩ := aligned_scalar_token (e := e) hC hU (scaledRepairNum W G J g r s) x
  refine ⟨hl, ?_⟩
  convert ht using 1
  rw [scaled_repair_exact J hJ g hg hn r s]
  push_cast
  have hF : (((W-1).factorial : ℕ) : ℚ) ≠ 0 := by exact_mod_cast (Nat.factorial_ne_zero _)
  have hG' : (G : ℚ) ≠ 0 := by exact_mod_cast (Nat.ne_of_gt hG)
  field_simp


/-- The full two-predictor frequency output agrees with the scalar target on *every* seed.
The set J is built from actual nonzero integer discrepancies, including all outside-window
coincidences where the predictor already has the correct value. -/
theorem corrected_predictor_all_seeds {W : ℕ} (hW : 0 < W) (p : ℕ → ℤ) (z : ℤ)
    (x : ℕ → ℚ) {i : ℕ} (hi : i < W) :
    let J := (range W).filter (fun j ↦ p j ≠ z)
    let g := fun j ↦ p j - z
    let Z := ∑ r ∈ range J.card, (node W i)^r *
      (∑ s ∈ range J.card, repairEntry W J g r s *
        (∑ j ∈ J, (node W j)^s * ((g j : ℚ) * x j)))
    (p i : ℚ) * x i - (p i : ℚ) * Z + (z : ℚ) * Z = (z : ℚ) * x i := by
  classical
  let J := (range W).filter (fun j ↦ p j ≠ z)
  let g := fun j ↦ p j - z
  change (p i : ℚ) * x i - (p i : ℚ) * _ + (z : ℚ) * _ = (z : ℚ) * x i
  by_cases h : p i = z
  · rw [h]
    ring
  · have hm : i ∈ J := mem_filter.mpr ⟨mem_range.mpr hi, h⟩
    have hn (j : ℕ) (hj : j ∈ J) : g j ≠ 0 := sub_ne_zero.mpr (mem_filter.mp hj).2
    have hl := actual_repair_lift hW J g hn x hm
    change (p i : ℚ) * x i - (p i : ℚ) * _ + (z : ℚ) * _ = (z : ℚ) * x i
    rw [hl]
    ring

end Moonshot.AlignedWalsh
